import os
import torch
from torch import nn, optim
from torchvision import datasets, transforms, models
from torch.cuda.amp import autocast, GradScaler
from tqdm import tqdm
import json
import torch
print(torch.__version__)
print(torch.version.cuda)
# ======= 参数配置 =======
data_dir = r'D:\桌面\软件工程\wheat_disease_system\model\data'
batch_size = 32
epochs = 30
learning_rate = 1e-5
save_path = 'model'
model_save_path = os.path.join(save_path, 'cnn_model.pth')
label_save_path = os.path.join(save_path, 'labels.json')
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(torch.cuda.is_available())

def main():
    # ======= 图像增强与数据加载 =======
    data_transforms = {
        'train': transforms.Compose([
            transforms.Resize((160, 160)),
            transforms.RandomHorizontalFlip(),
            transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
            transforms.RandomRotation(15),
            transforms.ToTensor()
        ]),
        'valid': transforms.Compose([
            transforms.Resize((160, 160)),
            transforms.ToTensor()
        ])
    }

    image_datasets = {
        x: datasets.ImageFolder(os.path.join(data_dir, x), data_transforms[x])
        for x in ['train', 'valid']
    }
    dataloaders = {
        x: torch.utils.data.DataLoader(
            image_datasets[x],
            batch_size=batch_size,
            shuffle=True,
            num_workers=4,
            pin_memory=True
        )
        for x in ['train', 'valid']
    }
    class_names = image_datasets['train'].classes
    num_classes = len(class_names)

    print(f'📂 类别总数：{num_classes}')
    print(f'📂 类别列表：{class_names}')

    # ======= 模型构建 =======
    model = models.resnet50(pretrained=True)
    for name, param in model.named_parameters():
        if "layer4" in name or "fc" in name:
            param.requires_grad = True
        else:
            param.requires_grad = False
    model.fc = nn.Sequential(
        nn.Linear(model.fc.in_features, 256),
        nn.ReLU(),
        nn.Dropout(0.4),
        nn.Linear(256, num_classes)
    )
    model = model.to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(filter(lambda p: p.requires_grad, model.parameters()), lr=learning_rate)
    scaler = GradScaler()

    # ======= 训练循环 =======
    for epoch in range(epochs):
        print(f'\n Epoch {epoch + 1}/{epochs}')
        model.train()
        running_loss = 0.0
        train_loader = tqdm(dataloaders['train'], desc='Training', unit='batch')

        for batch_idx, (inputs, labels) in enumerate(train_loader):
            inputs, labels = inputs.to(device), labels.to(device)

            optimizer.zero_grad()
            with autocast(enabled=device.type == 'cuda'):
                outputs = model(inputs)
                loss = criterion(outputs, labels)

            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()

            running_loss += loss.item()
            percent = (batch_idx + 1) / len(train_loader) * 100
            train_loader.set_postfix({
                'loss': f'{loss.item():.4f}',
                'progress': f'{percent:.1f}%'
            })

        avg_loss = running_loss / len(train_loader)
        print(f'✅ 平均训练损失：{avg_loss:.4f}')

        # 验证
        model.eval()
        correct, total = 0, 0
        with torch.no_grad():
            for inputs, labels in dataloaders['valid']:
                inputs, labels = inputs.to(device), labels.to(device)
                outputs = model(inputs)
                _, preds = torch.max(outputs, 1)
                correct += (preds == labels).sum().item()
                total += labels.size(0)
        acc = correct / total
        print(f'📊 验证准确率：{acc:.2%}')

    # ======= 保存模型与标签 =======
    os.makedirs(save_path, exist_ok=True)
    torch.save(model, model_save_path)
    print(f'✅ 模型保存至：{model_save_path}')

    with open(label_save_path, 'w', encoding='utf-8') as f:
        json.dump(class_names, f, ensure_ascii=False)
    print(f'✅ 标签保存至：{label_save_path}')


if __name__ == '__main__':
    main()
