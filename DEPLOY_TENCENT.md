小麦病虫害识别系统 - 腾讯云部署指南
================================

目录
1. 购买服务器
2. 连接服务器
3. 安装运行环境
4. 安装配置 MySQL
5. 上传项目代码
6. 配置环境变量
7. 部署后端 (Flask)
8. 构建前端 (Vue)
9. 配置 Nginx + HTTPS
10. 域名绑定
11. 启动服务
================================

1. 购买服务器
-----------
1.1 打开 https://buy.cloud.tencent.com/lighthouse
1.2 选择配置:
    - 地域: 选离你最近的 (默认即可)
    - 镜像: 选 "系统镜像" -> "CentOS 8.2" 或 "Ubuntu 22.04"
    - 套餐: 2核2GB (最低配置够用)
    - 时长: 按月或按年
1.3 下单付款，等待服务器创建完成
1.4 在控制台重置密码，复制公网 IP

2. 连接服务器
-----------
Windows 用 PowerShell 或 CMD:

   ssh root@你的服务器IP

输入密码即可登录 (Linux 下输入密码不可见，正常敲完回车)

3. 安装运行环境
-----------
以下命令一行一行复制粘贴执行：

3.1 更新系统
   apt update && apt upgrade -y    (Ubuntu)
   或
   yum update -y                   (CentOS)

3.2 安装 Python 3 + pip
   apt install -y python3 python3-pip python3-venv   (Ubuntu)
   或
   yum install -y python3 python3-pip                (CentOS)

   验证:
   python3 --version
   pip3 --version

3.3 安装 Node.js (用于构建前端)
   curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
   apt install -y nodejs          (Ubuntu)
   或
   curl -fsSL https://rpm.nodesource.com/setup_20.x | bash -
   yum install -y nodejs          (CentOS)

   验证:
   node --version
   npm --version

3.4 安装 Nginx (Web 服务器)
   apt install -y nginx           (Ubuntu)
   或
   yum install -y nginx           (CentOS)

   启动 Nginx:
   systemctl start nginx
   systemctl enable nginx

   验证: 浏览器访问 http://你的服务器IP, 看到 Nginx 欢迎页就对了

3.5 安装 Git (拉取代码用)
   apt install -y git             (Ubuntu)
   或
   yum install -y git             (CentOS)

4. 安装配置 MySQL
-----------
4.1 安装 MySQL
   apt install -y mysql-server    (Ubuntu)
   或
   yum install -y mysql-server    (CentOS)

4.2 启动 MySQL
   systemctl start mysqld
   systemctl enable mysqld

4.3 设置 root 密码
   先查临时密码 (CentOS):
   grep "temporary password" /var/log/mysqld.log

   然后执行安全配置:
   mysql_secure_installation

   或者手动设置:
   mysql -u root -p
   ALTER USER "root"@"localhost" IDENTIFIED BY "你的密码";
   FLUSH PRIVILEGES;
   EXIT;

4.4 创建数据库
   mysql -u root -p
   CREATE DATABASE wheat_disease CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   EXIT;

   验证: mysql -u root -p -e "SHOW DATABASES;" | grep wheat

5. 上传项目代码
-----------
5.1 在服务器上创建项目目录
   mkdir -p /app/wheat_disease
   cd /app/wheat_disease

5.2 从本地上传代码
   在本机 PowerShell 中执行:

   scp -r D:\桌面\软件工程\wheat_disease_system\* root@你的服务器IP:/app/wheat_disease/

   输入密码等待传输完成 (如果文件大可能需要几分钟)

   回到服务器验证:
   cd /app/wheat_disease && ls -la

6. 配置环境变量
-----------
cd /app/wheat_disease

6.1 复制环境变量文件:
   cp .env.example .env

6.2 编辑 .env:
   nano .env

   填入以下内容 (用你的实际值替换):

   SECRET_KEY=这里填一个随机字符串，随便打30个字符
   DATABASE_URL=mysql+pymysql://root:你的MySQL密码@localhost/wheat_disease
   FLASK_ENV=production
   PORT=5000
   ALLOWED_ORIGINS=
   JWT_EXPIRATION_HOURS=24
   MODEL_PATH=/app/wheat_disease/model/model/cnn_model.pth
   LABEL_PATH=/app/wheat_disease/model/model/labels.json

   保存退出: Ctrl+X, 按 Y, 回车

7. 部署后端 (Flask)
-----------
cd /app/wheat_disease

7.1 创建虚拟环境
   python3 -m venv venv
   source venv/bin/activate

7.2 安装 Python 依赖
   pip install --upgrade pip
   pip install -r requirements.txt

   如果 torch 安装太慢，可以换国内源:
   pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

7.3 测试后端是否能启动
   python3 app.py

   看到 "[INFO] 数据库表已就绪" 和 "[INFO] 服务启动" 就说明成功了
   按 Ctrl+C 停掉

7.4 安装 supervisor 来管理进程 (保证服务一直在运行)
   apt install -y supervisor     (Ubuntu)
   或
   yum install -y supervisor     (CentOS)

   创建配置文件:
   nano /etc/supervisor/conf.d/wheat.conf

   填入:

   [program:wheat]
   command=/app/wheat_disease/venv/bin/python /app/wheat_disease/app.py
   directory=/app/wheat_disease
   user=root
   autostart=true
   autorestart=true
   stderr_logfile=/var/log/wheat.err.log
   stdout_logfile=/var/log/wheat.out.log

   保存退出 (Ctrl+X, Y, 回车)

   启动:
   supervisorctl reread
   supervisorctl update
   supervisorctl start wheat

   查看状态:
   supervisorctl status

   看到 "RUNNING" 就对了

   测试后端是否工作:
   curl http://localhost:5000/api/health

   应该返回: {"status":"ok","time":"..."}

8. 构建前端 (Vue)
-----------
cd /app/wheat_disease/wheat-frontend

8.1 创建生产环境变量文件:
   nano .env.production

   填入:
   VITE_API_URL=/api

   保存退出

8.2 安装依赖并构建
   npm install
   npm run build

   看到 "built in xx s" 就成功了
   构建产物在 dist/ 目录里

   验证:
   ls -la dist/

9. 配置 Nginx + HTTPS
-----------
9.1 创建 Nginx 配置文件:
   nano /etc/nginx/sites-available/wheat.conf    (Ubuntu)
   或
   nano /etc/nginx/conf.d/wheat.conf             (CentOS)

   填入:

   server {
       listen 80;
       server_name 你的域名.com;

       client_max_body_size 20M;

       location /api/ {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }

       location /uploads/ {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }

       location / {
           root /app/wheat_disease/wheat-frontend/dist;
           index index.html;
           try_files $uri $uri/ /index.html;
       }
   }

   保存退出

9.2 启用配置
   ln -s /etc/nginx/sites-available/wheat.conf /etc/nginx/sites-enabled/   (Ubuntu)
   或  CentOS 不用这一步，直接在 conf.d 下已经生效

   测试配置:
   nginx -t

   重载 Nginx:
   systemctl reload nginx

9.3 配置 HTTPS (腾讯云免费证书)

   方法 A: 使用 certbot (推荐)
   apt install -y certbot python3-certbot-nginx
   certbot --nginx -d 你的域名.com

   一路按提示操作，会自动配置 HTTPS

   方法 B: 使用腾讯云免费证书
   - 打开 https://console.cloud.tencent.com/ssl
   - 点击 "申请免费证书"
   - 填写域名，验证通过后下载
   - 选择 "Nginx" 格式下载证书文件
   - 上传到服务器:
     scp 本地证书路径 root@服务器IP:/etc/nginx/ssl/
   - 修改 Nginx 配置添加 HTTPS:
     server {
         listen 443 ssl;
         server_name 你的域名.com;

         ssl_certificate /etc/nginx/ssl/你的证书文件.crt;
         ssl_certificate_key /etc/nginx/ssl/你的私钥文件.key;

         ... 其余配置跟上面一样 ...
     }

   然后重载 Nginx:
   systemctl reload nginx

10. 域名绑定
----------
10.1 打开 https://console.cloud.tencent.com/cns (DNS 解析)
10.2 添加记录:
     记录类型: A
     主机记录: @ (根域名) 或 www (www 域名)
     记录值: 你的服务器公网 IP
10.3 等待解析生效 (一般几分钟)

11. 初始化数据
-----------
登录服务器执行:

   cd /app/wheat_disease
   source venv/bin/activate
   python3 init_data.py

   看到 "已添加所有病虫害防治信息" 就完成了

12. 验证部署
-----------
打开浏览器访问:

   http://你的域名.com

应该看到:
- 登录页面能正常显示
- 注册账号后能登录
- 上传图片能识别
- 识别记录能显示

如果遇到 502 或 504 错误:
   systemctl status nginx          # 检查 Nginx
   supervisorctl status wheat      # 检查后端
   tail -f /var/log/wheat.err.log  # 查看错误日志

常用维护命令:
   supervisorctl restart wheat     # 重启后端
   nginx -t && systemctl reload nginx  # 重载 Nginx
   tail -f /var/log/nginx/access.log   # 查看 Nginx 日志
