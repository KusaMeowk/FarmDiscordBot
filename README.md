# 🌾 Bot Discord Game Nông Trại

> **Bot Discord game nông trại hoàn chỉnh với AI thông minh và kinh tế cân bằng**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Discord.py](https://img.shields.io/badge/discord.py-2.3+-blue.svg)](https://discordpy.readthedocs.io/)
[![Gemini AI](https://img.shields.io/badge/AI-Google%20Gemini-green.svg)](https://ai.google.dev/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🎯 Tổng Quan

Bot Discord game nông trại với các tính năng:
- **🌾 14 loại cây trồng** từ cơ bản đến huyền thoại
- **🐟 Hệ thống chăn nuôi** với ao cá và chuồng gia súc
- **🤖 AI Gemini** điều chỉnh kinh tế thời gian thực
- **🌤️ Thời tiết thông minh** ảnh hưởng sinh trưởng
- **🎪 Events** theo mùa với phần thưởng đặc biệt
- **📊 Leaderboard** và thành tích
- **💰 Kinh tế cân bằng** tự động

## ⚡ Cài Đặt Nhanh

### Ubuntu Server (Khuyến nghị)
```bash
# 1. Clone repository
git clone <repo-url>
cd BotNôngTrại

# 2. Chạy script tự động
chmod +x ubuntu_setup.sh
bash ubuntu_setup.sh

# 3. Cấu hình API keys
sudo -u farmbot nano /home/farmbot/bot/.env

# 4. Start service
sudo systemctl start farmbot
```

### Cài đặt thủ công
```bash
# 1. Install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Setup environment
cp env_template.txt .env
# Edit .env với Discord token và Gemini API key

# 3. Run bot
python bot.py
```

## 📋 Yêu Cầu

### Bắt buộc
- **Python 3.8+**
- **Discord Bot Token** ([Tạo tại đây](https://discord.com/developers/applications))
- **Gemini API Key** ([Tạo tại đây](https://aistudio.google.com/app/apikey))

### Tùy chọn
- **Weather API Key** ([OpenWeatherMap](https://openweathermap.org/api))
- **Ubuntu Server** cho production deployment

### System Requirements
- **2GB RAM** minimum (4GB khuyến nghị)
- **1GB storage** trống
- **Internet connection** ổn định

## 🎮 Commands Chính

| Command | Mô tả |
|---------|-------|
| `f!help` | Xem hướng dẫn đầy đủ |
| `f!profile` | Thông tin cá nhân |
| `f!farm` | Quản lý nông trại |
| `f!shop` | Cửa hàng mua bán |
| `f!weather` | Xem thời tiết hiện tại |
| `f!daily` | Điểm danh hàng ngày |
| `f!leaderboard` | Bảng xếp hạng |
| `f!pond` | Quản lý ao cá |
| `f!barn` | Quản lý chuồng gia súc |

## 🏗️ Kiến Trúc

```
BotNôngTrại/
├── bot.py                    # Bot chính
├── config.py                # Cấu hình game
├── requirements.txt         # Dependencies
├── ubuntu_setup.sh          # Auto-setup script
├── docs/                    # Documentation
│   ├── README.md           # Tài liệu chính
│   ├── SETUP.md            # Hướng dẫn cài đặt
│   ├── ARCHITECTURE.md     # Kiến trúc hệ thống
│   └── UBUNTU_DEPLOYMENT_GUIDE.md
├── database/               # Database layer
├── features/               # Game features (cogs)
├── ai/                     # AI systems
├── utils/                  # Utilities
└── memory-bank/            # AI memory system
```

## 🤖 Tính Năng AI

### Gemini Economic Manager
- **Multi-API System**: Failover với backup keys
- **Hourly Analysis**: AI phân tích game state
- **4 Decision Types**: Weather, Events, Pricing, No Action
- **Real-time Balancing**: Điều chỉnh kinh tế tự động

### Weather AI
- **Smart Cycles**: 30min-8h tùy game state  
- **Pattern Recognition**: Optimal timing
- **Game Impact**: Ảnh hưởng growth và yield

## 🚀 Production Deployment

### Auto-Restart với Systemd
```bash
# Service status
sudo systemctl status farmbot

# View logs
sudo journalctl -u farmbot -f

# Restart service
sudo systemctl restart farmbot
```

### Database Backup
- **Automatic**: Daily backup lúc 3:00 AM
- **Manual**: `sudo -u farmbot /home/farmbot/backup_bot.sh`
- **Retention**: Giữ 7 backup gần nhất

### Monitoring
- **Uptime**: 99%+ với auto-restart
- **Memory**: <256MB steady state
- **Response**: <500ms average
- **API Quota**: Smart rotation prevents limits

## 🔧 Troubleshooting

### Bot không start
```bash
# Check service
sudo systemctl status farmbot

# Check logs
sudo journalctl -u farmbot --no-pager

# Common fixes:
# 1. Verify .env file
# 2. Check API keys
# 3. Database permissions
```

### Database locked
```bash
sudo systemctl stop farmbot
sleep 10
sudo systemctl start farmbot
```

### Memory issues
```bash
# Check usage
free -h

# Add swap if needed
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

## 📊 Game Balance

### Economic Metrics
- **Money circulation**: Total trong hệ thống
- **Inflation rate**: Stability over time
- **Player activity**: Engagement tracking
- **Market balance**: Supply/demand

### Security Features
- **Anti-cheat**: Secure event claiming
- **Rate limiting**: Prevent spam
- **Input validation**: Sanitize inputs
- **Atomic transactions**: Database safety

## 📚 Documentation

- **[📖 Full Documentation](docs/DOCUMENTATION.md)** - Tài liệu đầy đủ
- **[🛠️ Setup Guide](docs/SETUP.md)** - Hướng dẫn cài đặt
- **[🏗️ Architecture](docs/ARCHITECTURE.md)** - Kiến trúc hệ thống
- **[🚀 Ubuntu Deployment](docs/UBUNTU_DEPLOYMENT_GUIDE.md)** - Triển khai server

### Features Documentation
- **[🐟 Livestock System](docs/features/LIVESTOCK_SYSTEM_COMPLETE.md)**
- **[🌾 Premium Crops](docs/features/PREMIUM_CROPS_SYSTEM.md)**
- **[📱 Shortcuts & Help](docs/features/SHORTCUTS_AND_HELP_SYSTEM.md)**

### Guides
- **[🤖 Gemini Integration](docs/guides/GEMINI_INTEGRATION_GUIDE.md)**
- **[💰 Economic Setup](docs/guides/GEMINI_ECONOMIC_SETUP_GUIDE.md)**
- **[📡 Gemini SDK](docs/guides/GEMINI_SDK_UPDATE.md)**

## 🤝 Contributing

### Development Setup
```bash
# Clone repo
git clone <repo-url>
cd BotNôngTrại

# Create branch
git checkout -b feature/new-feature

# Install dev dependencies
pip install -r requirements.txt

# Make changes and test
python bot.py

# Submit PR
```

### Code Standards
- **Python PEP 8** style guidelines
- **Type hints** cho functions
- **Docstrings** cho documentation
- **Error handling** comprehensive

## 📝 Changelog

### Version 2.0 (Current)
- ✅ Gemini AI integration hoàn chỉnh
- ✅ Multi-API failover system
- ✅ Livestock system complete (ao cá + chuồng gia súc)
- ✅ Security hardening (event exploit fixed)
- ✅ Production deployment ready
- ✅ Ubuntu auto-setup script
- ✅ Comprehensive documentation

### Version 1.x
- Basic farming system
- Weather integration
- Event system
- Market functionality

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](../../issues)
- **Discord**: [Support Server](#)
- **Email**: [Support Email](#)

---

**Made with ❤️ by [Your Name]**

*Bot nông trại Discord với AI thông minh cho cộng đồng gaming Việt Nam* 