import os
import torch
from torch import nn, optim
from torchvision import datasets, transforms, models
from torch.cuda.amp import autocast, GradScaler
from torch.optim.lr_scheduler import CosineAnnealingLR
from tqdm import tqdm
import matplotlib.pyplot as plt
import json

# ===== 参数 =====
data_dir = r'D:\桌面\软件工程\wheat_disease_system\model\data'
batch_size = 32
epochs = 30
lr = 1e-4
save_path = 'model'
model_path = os.path.join(save_path, 'cnn_model2.pth')
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# ===== SE模块 =====
class SEBlock(nn.Module):
    def __init__(self, c, r=16):
        super().__init__()
        self.pool = nn.AdaptiveAvgPool2d(1)
        self.fc = nn.Sequential(
            nn.Linear(c, c//r),
            nn.ReLU(),
            nn.Linear(c//r, c),
            nn.Sigmoid()
        )
    def forward(self, x):
        b,c,_,_ = x.size()
        y = self.pool(x).view(b,c)
        y = self.fc(y).view(b,c,1,1)
        return x * y

# ===== 模型 =====
class ResNet50_SE(nn.Module):
    def __init__(self, num_classes):
        super().__init__()
        base = models.resnet50(pretrained=True)

        self.backbone = nn.Sequential(
            base.conv1, base.bn1, base.relu, base.maxpool,
            base.layer1, base.layer2, base.layer3, base.layer4
        )

        self.se = SEBlock(2048)
        self.pool = nn.AdaptiveAvgPool2d(1)

        self.head = nn.Sequential(
            nn.Linear(2048, 256),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(256, num_classes)
        )

    def forward(self, x):
        x = self.backbone(x)
        x = self.se(x)
        x = self.pool(x)
        x = torch.flatten(x, 1)
        return self.head(x)

# ===== 主函数 =====
def main():

    transforms_dict = {
        'train': transforms.Compose([
            transforms.Resize((160,160)),
            transforms.RandomHorizontalFlip(),
            transforms.RandomRotation(10),
            transforms.ToTensor()
        ]),
        'valid': transforms.Compose([
            transforms.Resize((160,160)),
            transforms.ToTensor()
        ])
    }

    datasets_dict = {
        x: datasets.ImageFolder(os.path.join(data_dir,x), transforms_dict[x])
        for x in ['train','valid']
    }

    loaders = {
        x: torch.utils.data.DataLoader(
            datasets_dict[x],
            batch_size=batch_size,
            shuffle=True,
            num_workers=2
        )
        for x in ['train','valid']
    }

    classes = datasets_dict['train'].classes
    num_classes = len(classes)

    model = ResNet50_SE(num_classes).to(device)

    # ⭐ 关键：解冻 layer3 + layer4
    for name, p in model.named_parameters():
        if "layer3" in name or "layer4" in name or "se" in name or "head" in name:
            p.requires_grad = True
        else:
            p.requires_grad = False

    criterion = nn.CrossEntropyLoss(label_smoothing=0.1)

    optimizer = optim.Adam(
        filter(lambda p: p.requires_grad, model.parameters()),
        lr=lr,
        weight_decay=1e-4
    )

    scheduler = CosineAnnealingLR(optimizer, T_max=epochs)
    scaler = GradScaler()

    # ===== 记录 =====
    train_loss_list, val_loss_list = [], []
    train_acc_list, val_acc_list = [], []

    best_acc = 0
    patience = 5
    trigger = 0

    for epoch in range(epochs):
        print(f"\nEpoch {epoch+1}/{epochs}")

        # ===== 训练 =====
        model.train()
        total, correct, loss_sum = 0,0,0

        for x,y in tqdm(loaders['train']):
            x,y = x.to(device), y.to(device)

            optimizer.zero_grad()

            with autocast():
                out = model(x)
                loss = criterion(out,y)

            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()

            loss_sum += loss.item()
            _,pred = torch.max(out,1)
            correct += (pred==y).sum().item()
            total += y.size(0)

        train_loss = loss_sum/len(loaders['train'])
        train_acc = correct/total

        # ===== 验证 =====
        model.eval()
        total, correct, loss_sum = 0,0,0

        with torch.no_grad():
            for x,y in loaders['valid']:
                x,y = x.to(device), y.to(device)
                out = model(x)
                loss = criterion(out,y)

                loss_sum += loss.item()
                _,pred = torch.max(out,1)
                correct += (pred==y).sum().item()
                total += y.size(0)

        val_loss = loss_sum/len(loaders['valid'])
        val_acc = correct/total

        scheduler.step()

        print(f"Train Acc: {train_acc:.2%} | Val Acc: {val_acc:.2%}")

        train_loss_list.append(train_loss)
        val_loss_list.append(val_loss)
        train_acc_list.append(train_acc)
        val_acc_list.append(val_acc)

        # ===== 保存最优 =====
        if val_acc > best_acc:
            best_acc = val_acc
            torch.save(model, model_path)
            trigger = 0
            print("✔ 保存最优模型")
        else:
            trigger += 1

        # ===== 早停 =====
        if trigger >= patience:
            print("⛔ Early Stopping")
            break

    # ===== 画图 =====
    plt.figure()
    plt.plot(train_acc_list, label="训练准确率")
    plt.plot(val_acc_list, label="验证准确率")
    plt.legend()
    plt.title("准确率")

    plt.savefig("accuracy_curve.png", dpi=300)  # ⭐ 保存到当前文件夹
    plt.show()

    plt.figure()
    plt.plot(train_loss_list,label="训练损失")
    plt.plot(val_loss_list,label="验证损失")
    plt.legend()
    plt.title("模型损失")
    plt.show()

    # 保存标签
    os.makedirs(save_path, exist_ok=True)
    with open(os.path.join(save_path,'labels.json'),'w') as f:
        json.dump(classes,f)

if __name__ == '__main__':
    main()