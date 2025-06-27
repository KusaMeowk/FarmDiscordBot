# 🚀 HƯỚNG DẪN TRIỂN KHAI BOT NÔNG TRẠI LÊN UBUNTU SERVER

## 📋 Yêu Cầu Hệ Thống

### ✅ Hệ điều hành
- **Ubuntu 20.04 LTS** hoặc mới hơn (khuyến nghị 22.04 LTS)
- **2GB RAM** tối thiểu (4GB khuyến nghị cho production)
- **1GB storage** trống
- **Kết nối internet** ổn định

### ✅ Software cần thiết
- **Python 3.8+** (Ubuntu 22.04 có sẵn Python 3.10)
- **pip** package manager
- **git** để clone repository
- **systemd** để chạy service (có sẵn trên Ubuntu)

## 🛠️ BƯỚC 1: Chuẩn Bị Hệ Thống

### 1.1 Cập nhật hệ thống
```bash
sudo apt update && sudo apt upgrade -y
```

### 1.2 Cài đặt Python và các tools cần thiết
```bash
# Cài đặt Python và pip
sudo apt install python3 python3-pip python3-venv python3-dev -y

# Cài đặt git
sudo apt install git -y

# Cài đặt build tools (cần cho một số Python packages)
sudo apt install build-essential -y

# Cài đặt supervisor cho process management
sudo apt install supervisor -y
```

### 1.3 Tạo user riêng cho bot (bảo mật)
```bash
# Tạo user mới
sudo adduser farmbot --disabled-password --gecos ""

# Thêm user vào group sudo (nếu cần admin access)
sudo usermod -aG sudo farmbot

# Chuyển sang user farmbot
sudo su - farmbot
```

## 🛠️ BƯỚC 2: Cài Đặt Bot

### 2.1 Clone repository
```bash
# Tạo thư mục cho bot
mkdir -p ~/bot && cd ~/bot

# Clone repository (thay thế URL bằng repo thực tế)
git clone https://github.com/username/BotNongTrai.git .

# Hoặc upload code từ máy local
# scp -r BotNôngTrại/ farmbot@your-server-ip:~/bot/
```

### 2.2 Tạo Python virtual environment
```bash
# Tạo virtual environment
python3 -m venv venv

# Kích hoạt virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

### 2.3 Cài đặt dependencies
```bash
# Cài đặt tất cả packages
pip install -r requirements.txt

# Kiểm tra cài đặt
python -c "import discord; print('Discord.py:', discord.__version__)"
python -c "import google.genai; print('Gemini SDK: OK')"
```

## 🛠️ BƯỚC 3: Cấu Hình Bot

### 3.1 Tạo file .env
```bash
# Tạo file .env từ template
cp .env.example .env

# Chỉnh sửa file .env
nano .env
```

### 3.2 Nội dung file .env
```bash
# Discord Bot Configuration
DISCORD_TOKEN=your_discord_bot_token_here
PREFIX=f!
OWNER_ID=your_discord_user_id

# Database
DATABASE_PATH=/home/farmbot/bot/farm_bot.db

# Weather API (Optional)
WEATHER_API_KEY=your_openweathermap_api_key

# Gemini AI (Required cho AI features)
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_API_KEY_2=backup_key_optional
GEMINI_API_KEY_3=third_backup_optional

# Production Settings
ENVIRONMENT=production
LOG_LEVEL=INFO
LOG_FILE=/home/farmbot/bot/logs/bot.log
```

### 3.3 Tạo thư mục logs
```bash
mkdir -p ~/bot/logs
mkdir -p ~/bot/cache
```

### 3.4 Thiết lập quyền files
```bash
chmod 600 .env                    # Bảo mật file .env
chmod +x bot.py start_bot.py     # Executable scripts
chmod 755 ~/bot                   # Thư mục bot readable
```

## 🛠️ BƯỚC 4: Test Bot

### 4.1 Test chạy thủ công
```bash
# Kích hoạt virtual environment
source ~/bot/venv/bin/activate

# Chạy bot
cd ~/bot
python bot.py
```

**Kiểm tra output:**
- ✅ `🤖 Bot ready for farming!`
- ✅ `✅ Database connected successfully`
- ✅ `🎯 Successfully loaded X/X extensions`

### 4.2 Test commands cơ bản
Trong Discord server test:
```
f!help
f!profile
f!farm
f!weather
```

**Ctrl+C** để dừng bot sau khi test thành công.

## 🛠️ BƯỚC 5: Cấu Hình Service (Auto-Start)

### 5.1 Tạo systemd service file
```bash
sudo nano /etc/systemd/system/farmbot.service
```

### 5.2 Nội dung service file
```ini
[Unit]
Description=Farm Bot Discord Game
After=network.target
Wants=network.target

[Service]
Type=simple
User=farmbot
Group=farmbot
WorkingDirectory=/home/farmbot/bot
Environment=PATH=/home/farmbot/bot/venv/bin
ExecStart=/home/farmbot/bot/venv/bin/python /home/farmbot/bot/bot.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# Security settings
NoNewPrivileges=yes
PrivateTmp=yes
ProtectSystem=strict
ReadWritePaths=/home/farmbot/bot

[Install]
WantedBy=multi-user.target
```

### 5.3 Kích hoạt service
```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service (auto-start on boot)
sudo systemctl enable farmbot

# Start service
sudo systemctl start farmbot

# Check status
sudo systemctl status farmbot
```

## 🛠️ BƯỚC 6: Giám Sát & Maintenance

### 6.1 Kiểm tra logs
```bash
# Xem logs real-time
sudo journalctl -u farmbot -f

# Xem logs của hôm nay
sudo journalctl -u farmbot --since today

# Xem logs bot file
tail -f ~/bot/logs/bot.log
```

### 6.2 Quản lý service
```bash
# Restart bot
sudo systemctl restart farmbot

# Stop bot
sudo systemctl stop farmbot

# Check status
sudo systemctl status farmbot

# Disable auto-start
sudo systemctl disable farmbot
```

### 6.3 Backup database định kỳ
```bash
# Tạo script backup
nano ~/backup_bot.sh
```

**Nội dung script:**
```bash
#!/bin/bash
BACKUP_DIR="/home/farmbot/backups"
DB_PATH="/home/farmbot/bot/farm_bot.db"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
cp $DB_PATH $BACKUP_DIR/farm_bot_$DATE.db

# Giữ chỉ 7 backup gần nhất
ls -t $BACKUP_DIR/farm_bot_*.db | tail -n +8 | xargs rm -f

echo "Backup completed: farm_bot_$DATE.db"
```

```bash
# Chmod executable
chmod +x ~/backup_bot.sh

# Thêm vào crontab (backup hàng ngày lúc 3:00 AM)
crontab -e
```

**Thêm dòng:**
```
0 3 * * * /home/farmbot/backup_bot.sh >> /home/farmbot/backup.log 2>&1
```

## 🛠️ BƯỚC 7: Cập Nhật Bot

### 7.1 Cập nhật code
```bash
cd ~/bot
sudo systemctl stop farmbot

# Backup trước khi update
cp farm_bot.db farm_bot.db.backup

# Pull latest code
git pull origin main

# Update dependencies nếu cần
source venv/bin/activate
pip install -r requirements.txt --upgrade

# Restart service
sudo systemctl start farmbot
```

## 🔧 TROUBLESHOOTING

### ❌ Service không start
```bash
# Check service status
sudo systemctl status farmbot

# Check logs
sudo journalctl -u farmbot --no-pager

# Common fixes:
# 1. Check file permissions
# 2. Verify .env file exists
# 3. Check Python path trong service file
```

### ❌ Permission denied errors
```bash
# Fix owner
sudo chown -R farmbot:farmbot /home/farmbot/bot

# Fix permissions
chmod 755 /home/farmbot/bot
chmod 600 /home/farmbot/bot/.env
```

### ❌ Database locked
```bash
# Stop service
sudo systemctl stop farmbot

# Wait 10 seconds
sleep 10

# Start service
sudo systemctl start farmbot
```

### ❌ Memory issues
```bash
# Check memory usage
free -h
ps aux | grep python

# Add swap if needed (2GB)
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

## 🔒 BẢO MẬT

### ✅ Security Checklist
- [ ] Bot chạy với user riêng (không phải root)
- [ ] File .env có quyền 600 (chỉ owner đọc được)
- [ ] Database backup định kỳ
- [ ] UFW firewall enabled (chỉ mở port cần thiết)
- [ ] SSH key authentication (tắt password login)
- [ ] Fail2ban cài đặt để chống brute force

### 🔥 Firewall setup (Optional)
```bash
# Enable UFW
sudo ufw enable

# Allow SSH (thay 22 bằng port SSH của bạn)
sudo ufw allow 22

# Deny all other incoming
sudo ufw default deny incoming
sudo ufw default allow outgoing
```

## ✅ KẾT LUẬN

Bot của bạn giờ đây đã:
- ✅ **Chạy tự động** khi server khởi động
- ✅ **Tự restart** khi có lỗi
- ✅ **Backup database** định kỳ
- ✅ **Logs đầy đủ** để debug
- ✅ **Bảo mật** với user riêng
- ✅ **Sẵn sàng production** với 99% uptime

**Commands quan trọng để nhớ:**
```bash
# Check bot status
sudo systemctl status farmbot

# View logs
sudo journalctl -u farmbot -f

# Restart bot
sudo systemctl restart farmbot

# Manual backup
~/backup_bot.sh
```

🎉 **Bot nông trại của bạn đã sẵn sàng phục vụ cộng đồng!** 