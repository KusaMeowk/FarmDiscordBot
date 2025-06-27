# 🚀 HƯỚNG DẪN SETUP BOT NÔNG TRẠI

## ⚡ Quick Start

### 1. Tạo file `.env`
```bash
# Sao chép template
cp .env.example .env

# Hoặc tạo file .env với nội dung:
DISCORD_TOKEN=your_discord_bot_token_here
PREFIX=f!
OWNER_ID=your_discord_user_id_here
WEATHER_API_KEY=your_openweathermap_api_key_here
DATABASE_PATH=farm_bot.db
```

### 2. Cài đặt Python packages
```bash
pip install -r requirements.txt
```

### 3. Chạy bot
```bash
python bot.py
```

## 🔧 Cấu hình chi tiết

### Discord Bot Token
1. Truy cập [Discord Developer Portal](https://discord.com/developers/applications)
2. Tạo "New Application"
3. Vào tab "Bot" → "Reset Token" 
4. Copy token vào `DISCORD_TOKEN`

⚠️ **LƯU Ý**: KHÔNG chia sẻ token với ai!

### Owner ID (Tùy chọn)
- ID Discord của bạn để có quyền admin commands
- Nhấp chuột phải vào tên mình trong Discord → "Copy User ID"

### Weather API Key (Tùy chọn)
- Đăng ký tại [OpenWeatherMap](https://openweathermap.org/api)
- Free plan: 900 calls/day
- Bot hoạt động với mock data nếu không có API key

## 🐛 Troubleshooting

### Lỗi thường gặp

#### `DISCORD_TOKEN not found`
- Kiểm tra file `.env` có tồn tại
- Đảm bảo token được copy đúng (không có space)

#### `Module not found`
```bash
pip install --upgrade -r requirements.txt
```

#### `Database locked`
- Tắt bot và chạy lại
- Xóa file `farm_bot.db` và restart

#### Bot không phản hồi
- Kiểm tra bot có online trong Discord
- Đảm bảo bot có permission "Send Messages"

### Performance Issues

#### Memory leak
- Bot tự động cleanup cache mỗi 30 phút
- Restart bot nếu RAM usage > 500MB

#### Database slow
- SQLite file có thể lớn sau thời gian dài
- Backup và recreate database định kỳ

## 📊 Monitoring

### Health Check
```bash
# Kiểm tra bot status
f!ai status

# Weather API usage  
f!apistats

# Database info
f!profile
```

### Logs quan trọng
- `🤖 AI Decision Task` - AI hoạt động bình thường
- `Database reconnected` - Connection recovery
- `Weather API error` - API limit hoặc network issue

## 🚨 Critical Safeguards Implemented

### 1. Database Protection
✅ Atomic transactions để tránh race conditions
✅ Connection recovery với retry logic
✅ SQL injection prevention (parameterized queries)

### 2. Memory Management  
✅ Weather cache size limit (100 cities)
✅ Automatic cache cleanup mỗi 30 phút
✅ Task error recovery

### 3. API Rate Limiting
✅ Weather API: 900 calls/day limit
✅ Fallback to cached/mock data
✅ Daily counter reset tự động

### 4. Bulk Operation Limits
✅ Maximum 50 plots for "plant all"
✅ Maximum 20 plots for manual bulk
✅ Input validation cho tất cả commands

### 5. Error Handling
✅ Task crash recovery
✅ Graceful degradation
✅ Detailed error logging

## 🎯 Production Deployment

### System Requirements
- Python 3.8+
- RAM: 256MB minimum, 512MB recommended  
- Storage: 100MB minimum
- Network: Stable internet connection

### Security Checklist
- [ ] `.env` file not in git repository
- [ ] Database file permissions restricted
- [ ] Bot token regenerated for production
- [ ] Log files properly rotated
- [ ] Regular database backups

### Scaling Considerations
- Single server: Handles ~1000 concurrent users
- Multi-server: Cần migrate to PostgreSQL
- High traffic: Consider Redis caching layer

Tất cả critical issues đã được fix! Bot sẵn sàng production. 