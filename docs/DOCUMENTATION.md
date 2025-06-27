# 📚 BOT DISCORD GAME NÔNG TRẠI - DOCUMENTATION

## 📖 Mục Lục

1. [Tổng Quan Dự Án](#tổng-quan-dự-án)
2. [Kiến Trúc Hệ Thống](#kiến-trúc-hệ-thống)
3. [Tính Năng Chính](#tính-năng-chính)
4. [Hệ Thống AI & Gemini](#hệ-thống-ai--gemini)
5. [Hướng Dẫn Cài Đặt](#hướng-dẫn-cài-đặt)
6. [Triển Khai Production](#triển-khai-production)
7. [Troubleshooting](#troubleshooting)

---

## 🎯 Tổng Quan Dự Án

### Mục tiêu
Bot Discord game nông trại hoàn chỉnh với AI thông minh, hệ thống kinh tế cân bằng và trải nghiệm người chơi phong phú.

### Tính năng cốt lõi
- **🌾 Hệ thống nông trại**: 14 loại cây trồng từ cơ bản đến huyền thoại
- **🐟 Chăn nuôi**: Ao cá và chuồng gia súc với 20+ loài
- **🏪 Shop & Market**: Mua bán vật phẩm với AI điều chỉnh giá
- **🌤️ Thời tiết AI**: Chu kỳ thời tiết thông minh ảnh hưởng sinh trưởng
- **🎪 Sự kiện**: Events theo mùa với phần thưởng đặc biệt
- **📊 Leaderboard**: Xếp hạng và thành tích
- **💰 Kinh tế cân bằng**: AI Gemini điều chỉnh realtime

### Công nghệ
- **Python 3.8+** với discord.py 2.3+
- **SQLite** database với async operations
- **Google Gemini AI** cho decision making
- **Weather API** integration
- **Discord Components** (buttons, selects, embeds)

---

## 🏗️ Kiến Trúc Hệ Thống

### Cấu trúc thư mục
```
BotNôngTrại/
├── bot.py                 # Bot chính
├── config.py             # Cấu hình game
├── requirements.txt      # Dependencies
├── ubuntu_setup.sh       # Auto-setup script
│
├── database/             # Database layer
│   ├── database.py       # Database manager
│   └── models.py         # Data models
│
├── features/             # Game features (cogs)
│   ├── farm.py          # Farming system
│   ├── shop.py          # Shop system
│   ├── weather.py       # Weather system
│   ├── events.py        # Event system
│   ├── pond.py          # Fish farming
│   ├── barn.py          # Animal farming
│   ├── gemini_economic_cog.py  # AI economic manager
│   └── ...
│
├── ai/                  # AI systems
│   ├── gemini_client.py     # Gemini API client
│   ├── gemini_manager_v2.py # Multi-API manager
│   └── weather_predictor.py # Weather AI
│
├── utils/               # Utilities
│   ├── embeds.py        # Discord embed builder
│   ├── helpers.py       # Helper functions
│   ├── enhanced_logging.py # Logging system
│   └── state_manager.py # State persistence
│
└── memory-bank/         # AI memory system
    ├── projectbrief.md
    ├── activeContext.md
    └── ...
```

### Component Flow
```
Discord User Input
       ↓
    Bot.py (Command Router)
       ↓
    Feature Cogs (farm.py, shop.py, etc.)
       ↓
    Database Layer (database.py)
       ↓
    AI Systems (Gemini Economic Manager)
       ↓
    External APIs (Weather, Gemini)
```

---

## 🎮 Tính Năng Chính

### 🌾 Hệ Thống Nông Trại
- **14 loại cây**: Từ cà rốt (5 phút) đến thanh long (6 giờ)
- **Tiến hóa theo tier**: Basic → Premium → Exotic → Legendary → Mythical
- **Yield system**: Random từ 1-4 sản phẩm mỗi lần thu hoạch
- **Pagination**: 8 plots per page cho UX tốt hơn

### 🐟 Chăn Nuôi
- **Pond System**: 6 loại cá với khả năng đặc biệt
- **Barn System**: 5 loại gia súc với sản phẩm khác nhau
- **Facility Upgrades**: Mở rộng từ level 1-6
- **Production Cycles**: Thu hoạch sản phẩm định kỳ

### 🌤️ Thời Tiết AI
- **4 loại thời tiết**: Sunny (tăng growth), Rainy (tăng yield), Cloudy (neutral), Stormy (giảm)
- **AI Cycle**: Tự động thay đổi mỗi 1 giờ dựa trên game state
- **Smart Patterns**: Recovery boosts, challenge cycles, stability periods

### 🎪 Events Hệ Thống
- **Seasonal Events**: Theo mùa với themed rewards
- **Dynamic Events**: AI tạo events để cân bằng kinh tế
- **Anti-Exploit**: Secure claim system với database tracking

### 💰 Kinh tế AI
- **Gemini Integration**: Multi-API với failover
- **Hourly Analysis**: AI phân tích và điều chỉnh
- **4 Decision Types**: Weather, Events, Pricing, No Action
- **Health Monitoring**: Economic health score (0-1)

---

## 🤖 Hệ Thống AI & Gemini

### Gemini Economic Manager V2
**Multi-API System**:
- Primary, Secondary, Backup API keys
- Auto-rotation khi hit quota
- Fallback mechanism

**Decision Engine**:
```python
{
  "decision_type": "weather_change|event_trigger|price_adjustment|no_action",
  "reasoning": "AI explanation",
  "confidence": 0.85,
  "parameters": {...}
}
```

**Real-time Analysis**:
- Player activity levels
- Money distribution & inflation
- Market volatility
- Engagement metrics

### Weather Predictor AI
- **Game State Analysis**: Player satisfaction, economy health
- **Pattern Recognition**: Optimal timing cho weather changes
- **Predictive Logic**: 30min-8h cycles tùy game state

### Cache System
- **Economic Snapshots**: 30-minute intervals
- **Smart Caching**: Reduce API calls, improve performance
- **Data Persistence**: State maintained across restarts

---

## 🛠️ Hướng Dẫn Cài Đặt

### Cài đặt nhanh (Ubuntu)
```bash
# 1. Clone repository
git clone <repo-url>
cd BotNôngTrại

# 2. Chạy auto-setup
chmod +x ubuntu_setup.sh
bash ubuntu_setup.sh

# 3. Cấu hình API keys
sudo -u farmbot nano /home/farmbot/bot/.env

# 4. Start service
sudo systemctl start farmbot
```

### Cài đặt thủ công
```bash
# 1. Install Python dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Create .env file
cp env_template.txt .env
# Edit .env với Discord token, Gemini API key

# 3. Run bot
python bot.py
```

### Environment Variables
```bash
# Required
DISCORD_TOKEN=your_discord_bot_token
GEMINI_API_KEY=your_gemini_api_key

# Optional
WEATHER_API_KEY=your_weather_api_key
OWNER_ID=your_discord_user_id
PREFIX=f!

# Production
ENVIRONMENT=production
LOG_LEVEL=INFO
```

---

## 🚀 Triển Khai Production

### System Requirements
- **Ubuntu 20.04+** (khuyến nghị 22.04 LTS)
- **2GB RAM** minimum (4GB recommended)
- **Python 3.8+**
- **1GB storage** free space
- **Stable internet** connection

### Production Features
✅ **Auto-restart** với systemd service  
✅ **Database backup** hàng ngày  
✅ **Comprehensive logging** với journald  
✅ **Security hardening** với dedicated user  
✅ **Memory monitoring** với psutil  
✅ **Multi-API failover** cho high availability  

### Monitoring Commands
```bash
# Service status
sudo systemctl status farmbot

# Real-time logs
sudo journalctl -u farmbot -f

# Restart service
sudo systemctl restart farmbot

# Manual backup
sudo -u farmbot /home/farmbot/backup_bot.sh
```

### Performance Metrics
- **Response time**: <500ms average
- **Uptime**: 99%+ với auto-restart
- **Memory usage**: <256MB steady state
- **API quota**: Smart rotation prevents limits

---

## 🔧 Troubleshooting

### Common Issues

#### Bot không start
```bash
# Check service status
sudo systemctl status farmbot

# Check logs
sudo journalctl -u farmbot --no-pager

# Solutions:
# 1. Verify .env file exists và có đúng permissions
# 2. Check API keys validity
# 3. Ensure database file readable
```

#### Database locked
```bash
# Stop service
sudo systemctl stop farmbot
sleep 10
sudo systemctl start farmbot
```

#### Memory issues
```bash
# Check memory usage
free -h
ps aux | grep python

# Add swap if needed
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

#### API quota exceeded
- **Gemini**: Auto-rotation to backup keys
- **Weather**: Fallback to cached/mock data
- **Rate limiting**: Built-in throttling

### Error Patterns

#### Discord.py errors
- **Type conversion**: Manual string→int conversion
- **Permission errors**: Check bot permissions trong server
- **Connection issues**: Auto-reconnect với retry logic

#### Database errors
- **Connection pool**: Max 10 concurrent connections
- **Atomic transactions**: Prevent race conditions
- **Backup recovery**: Restore từ daily backups

#### AI errors
- **API failures**: Graceful degradation to cached decisions
- **Invalid responses**: JSON parsing với error handling
- **Quota management**: Multi-key rotation system

---

## 📊 Game Balance

### Economic Health Metrics
- **Money circulation**: Total money in system
- **Inflation rate**: Price stability over time
- **Player activity**: Engagement và retention
- **Market balance**: Supply/demand equilibrium

### AI Balancing
- **Dynamic pricing**: Tự động điều chỉnh crop prices
- **Event generation**: Targeted events để correct imbalances
- **Weather control**: Optimize growth patterns
- **Alert system**: Early warning cho economic issues

### Security Features
- **Anti-cheat**: Secure event claiming
- **Rate limiting**: Prevent spam và abuse
- **Input validation**: Sanitize all user inputs
- **Transaction safety**: Atomic database operations

---

## 🎯 Best Practices

### Development
- **Modular design**: Mỗi feature = separate cog
- **Error handling**: Comprehensive try-catch blocks
- **Logging**: Detailed logs cho debugging
- **Testing**: Unit tests cho critical components

### Production
- **Security first**: Dedicated user, secure permissions
- **Monitoring**: Real-time status tracking
- **Backups**: Automated daily database backups
- **Updates**: Zero-downtime deployment process

### Performance
- **Async operations**: Non-blocking database calls
- **Caching**: Smart cache cho expensive operations
- **Resource limits**: Prevent memory leaks
- **API optimization**: Minimize external calls

---

## 🤝 Contributing

### Code Standards
- **Python PEP 8**: Follow style guidelines
- **Type hints**: Use typing annotations
- **Documentation**: Docstrings cho functions
- **Git**: Meaningful commit messages

### Feature Development
1. **Create branch**: `feature/new-feature-name`
2. **Develop**: Follow existing patterns
3. **Test**: Ensure no regressions
4. **Document**: Update relevant .md files
5. **PR**: Submit for review

---

## 📝 Changelog

### Version 2.0 (Current)
- ✅ Gemini AI integration hoàn chỉnh
- ✅ Multi-API failover system
- ✅ Livestock system complete
- ✅ Security hardening (event exploit fixed)
- ✅ Production deployment ready
- ✅ Comprehensive documentation

### Version 1.x
- Basic farming system
- Weather integration
- Event system
- Market functionality

---

*Tài liệu này được cập nhật thường xuyên. Phiên bản cuối: $(date)* 