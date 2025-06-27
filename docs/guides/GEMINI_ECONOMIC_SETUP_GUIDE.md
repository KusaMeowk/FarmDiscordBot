# Hướng dẫn Setup Gemini Economic Manager

## 🤖 Tổng quan

Gemini Economic Manager V2 là hệ thống AI tiên tiến thay thế AI local để quản lý và cân bằng kinh tế game nông trại. Hệ thống này sử dụng Google Gemini API để phân tích dữ liệu game và đưa ra quyết định thông minh mỗi giờ.

## 🎯 Tính năng chính

### ✨ Tính năng mới
- **Multiple API Keys**: Hỗ trợ nhiều API key với rotation tự động
- **Cache System**: Cache dữ liệu kinh tế, thời tiết, người chơi
- **Smart Decision Cache**: Tái sử dụng quyết định để tiết kiệm token
- **Hourly Analysis**: Phân tích và quyết định mỗi giờ
- **Economic Balance**: Cân bằng kinh tế game tự động
- **Smart Decisions**: 4 loại quyết định: Weather, Events, Pricing, No Action

### 🔧 Cách hoạt động
1. **Thu thập dữ liệu** từ database và cache mỗi 30 phút
2. **Phân tích** bằng Gemini AI mỗi giờ
3. **Đưa ra quyết định** dựa trên:
   - Số lượng người chơi và hoạt động
   - Phân bổ tiền trong game
   - Tình trạng lạm phát
   - Thời tiết hiện tại
   - Lịch sử quyết định
4. **Thực thi quyết định** tự động
5. **Thông báo** tới Discord channels

## 📝 Setup Instructions

### 1. Chuẩn bị API Keys

**Tạo Google Gemini API Keys:**
1. Truy cập [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Tạo ít nhất 2-3 API keys để dự phòng
3. Copy các API keys này

### 2. Cấu hình API Keys

**Chỉnh sửa file `ai/gemini_config.json`:**

```json
{
  "gemini_apis": {
    "primary": {
      "api_key": "YOUR_PRIMARY_GEMINI_API_KEY_HERE",
      "model": "gemini-pro",
      "url": "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent",
      "daily_limit": 1000,
      "current_usage": 0,
      "last_reset": "2025-06-21T00:00:00",
      "enabled": true,
      "priority": 1
    },
    "secondary": {
      "api_key": "YOUR_SECONDARY_GEMINI_API_KEY_HERE",
      "model": "gemini-pro",
      "url": "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent",
      "daily_limit": 1000,
      "current_usage": 0,
      "last_reset": "2025-06-21T00:00:00",
      "enabled": true,
      "priority": 2
    },
    "backup": {
      "api_key": "YOUR_BACKUP_GEMINI_API_KEY_HERE",
      "model": "gemini-pro",
      "url": "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent",
      "daily_limit": 1000,
      "current_usage": 0,
      "last_reset": "2025-06-21T00:00:00",
      "enabled": true,
      "priority": 3
    }
  }
}
```

### 3. Environment Variables (Tùy chọn)

**Thêm vào file `.env`:**
```
GEMINI_API_KEY=your_primary_gemini_api_key_here
```

### 4. Khởi động bot

```bash
python start_bot.py
```

Gemini Economic Manager sẽ tự động load và bắt đầu hoạt động.

## 🎮 Sử dụng Commands

### Admin Commands

**Xem trạng thái:**
```
f!gemini status
```
- Hiển thị trạng thái hệ thống
- Dữ liệu kinh tế hiện tại  
- Thời tiết và API status
- Quyết định gần đây

**Phân tích ngay:**
```
f!gemini analyze  
```
- Buộc phân tích kinh tế ngay lập tức
- Bỏ qua cooldown 1 giờ
- Hiển thị quyết định và thực thi

**Lịch sử quyết định:**
```
f!gemini history [limit]
```
- Xem 10 quyết định gần nhất (mặc định)
- Hiển thị loại quyết định, thời gian, độ tin cậy

**Thống kê cache:**
```
f!gemini cache
```
- Xem hit rate và tokens đã tiết kiệm
- Thống kê hiệu quả cache system
- Ước tính cost savings

**Bật/tắt hệ thống:**
```
f!gemini toggle [true/false]
```
- Bật/tắt Gemini Economic Manager
- Dừng/khởi động analysis task

**Setup thông báo:**
```
f!gemini setup [#channel]
```
- Setup channel nhận thông báo quyết định Gemini
- Mặc định là channel hiện tại nếu không chỉ định

## 📊 Loại quyết định

### 🌤️ WEATHER_CHANGE
Thay đổi thời tiết để cân bằng kinh tế:
- **sunny**: Boost growth và yield
- **rainy**: Tăng yield, bình thường growth  
- **cloudy**: Cân bằng
- **stormy**: Giảm cả growth và yield

### 🎯 EVENT_TRIGGER  
Kích hoạt sự kiện đặc biệt:
- **Yield Bonus**: Tăng sản lượng cây trồng
- **Price Bonus**: Tăng giá bán 
- **Growth Speed**: Tăng tốc độ phát triển
- **Tax Events**: Thuế để giảm lạm phát

### 💰 PRICE_ADJUSTMENT
Điều chỉnh giá cả thị trường:
- **Market modifier**: Thay đổi hệ số giá
- **Crop-specific**: Điều chỉnh từng loại cây
- **Inflation control**: Kiểm soát lạm phát

### ⏸️ NO_ACTION
Không can thiệp khi:
- Kinh tế ổn định
- Các chỉ số trong ngưỡng an toàn
- Quyết định gần đây vẫn có hiệu lực

## 🔧 Cấu hình nâng cao

### Economic Thresholds

Chỉnh sửa trong `ai/gemini_config.json`:

```json
"economic_balance_config": {
  "analysis_interval_hours": 1,
  "enable_auto_intervention": true,
  "inflation_warning_threshold": 0.08,
  "inflation_critical_threshold": 0.15,
  "activity_low_threshold": 0.3,
  "money_concentration_max": 0.7,
  "health_score_minimum": 0.4
}
```

### Cache Settings

```json
"cache_settings": {
  "economic_data_cache_minutes": 30,
  "weather_cache_minutes": 15,
  "player_stats_cache_minutes": 60,
  "decision_cooldown_minutes": 60
}
```

### API Rotation

```json
"rotation_settings": {
  "enable_auto_rotation": true,
  "rotation_threshold": 0.8,
  "fallback_on_error": true,
  "max_retries_per_key": 3,
  "retry_delay_seconds": 5
}
```

## 📈 Monitoring

### Alerts tự động
Hệ thống sẽ tự động tạo cảnh báo khi:
- **Lạm phát cao** (>15% = critical, >8% = warning)
- **Hoạt động thấp** (<30% users active)
- **Tập trung tiền** (>70% tiền ở top 10% players)

### Health Score
Điểm health kinh tế (0-1) dựa trên:
- **Activity factor** (40%): Tỷ lệ người chơi hoạt động
- **Inflation factor** (30%): Mức độ lạm phát
- **Distribution factor** (30%): Phân bổ tiền công bằng

### Logs
Theo dõi logs để monitoring:
```
[16:07:14] 🤖 Gemini: Starting hourly economic analysis...
[16:07:14] 🤖 Gemini Decision: WEATHER_CHANGE - Reasoning...
[16:07:14] 🌤️ Gemini Weather Change: rainy for 2h - Economic boost needed
```

## 🚨 Troubleshooting

### API Key Issues
```
❌ No available Gemini API keys
```
**Solutions:**
1. Kiểm tra `ai/gemini_config.json` có API keys đúng
2. Verify API keys trên Google AI Studio
3. Kiểm tra daily limits chưa vượt

### Decision Không thực thi
```
❌ Failed to execute Gemini decision
```
**Solutions:**
1. Kiểm tra WeatherCog và EventsCog đã load
2. Verify database connection
3. Check permissions của bot

### Cache Issues
```
📊 Using cached economic data
```
- Bình thường, cache tránh spam API
- Force refresh bằng `f!gemini analyze`

### Task Not Running
```
🔴 Task analysis đã được dừng
```
**Solutions:**
1. `f!gemini toggle true` để restart
2. Restart bot nếu cần
3. Check logs để tìm lỗi

## 💡 Tips & Best Practices

### 1. Multiple API Keys
- Setup 2-3 API keys để đảm bảo uptime
- Set priority khác nhau cho rotation thông minh
- Monitor usage để tránh hit limits

### 2. Smart Cache System
- **Automatic Token Saving**: Cache tự động lưu decisions cho situations tương tự
- **Pattern Matching**: Hệ thống so sánh activity level, health score, weather
- **Fresh Data**: Cache expires sau 7 ngày để đảm bảo decisions up-to-date
- **High Efficiency**: Hit rate thường 40-60% sau vài ngày hoạt động

### 3. Timing
- Gemini phân tích mỗi giờ (configurable)
- Cache refresh mỗi 30 phút để optimize performance
- Cooldown prevents spam decisions

### 4. Notifications
- Setup notification channel để theo dõi decisions
- Monitor health score và alerts
- Review history để hiểu pattern

### 5. Economic Balance
- Gemini tự động adjust dựa trên data
- Manual analyze khi cần intervention ngay
- Review config thresholds theo gameplay cần thiết

## 🔮 Future Updates

Planned features:
- **Seasonal Analysis**: Long-term economic trends
- **Player Behavior Learning**: Machine learning cho prediction tốt hơn  
- **Advanced Events**: Complex multi-stage events
- **Economic Forecasting**: Predict future economic state
- **Integration với market data**: Real-time pricing adjustments

---

**🤖 Gemini Economic Manager V2** - Intelligent economic balance for farming game Discord bot.

*Developed by the farming bot team. For support, use the Discord commands or check logs.* 