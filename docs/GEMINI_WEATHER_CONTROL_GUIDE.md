# 🌤️ Gemini Game Master - Weather Control System

## Tổng quan

Gemini Game Master có khả năng thay đổi thời tiết mỗi 15 phút dựa trên trạng thái game thực tế. Hệ thống này tự động phân tích tình hình và đưa ra quyết định thời tiết phù hợp để tối ưu trải nghiệm người chơi.

## Cách thức hoạt động

### 1. Thu thập dữ liệu (mỗi 15 phút)
- **Số người chơi hoạt động**: Active players trong 15 phút qua
- **Sức khỏe kinh tế**: Economic health score
- **Thời tiết hiện tại**: Current weather và thời gian còn lại
- **Mức độ hài lòng**: Weather satisfaction score
- **Thời gian trong ngày**: Hour của ngày (0-23)

### 2. Phân tích và quyết định
Gemini sử dụng logic thông minh để chọn thời tiết:

#### Ban ngày (6h-18h)
- **Nhiều người chơi (>10)**:
  - Kinh tế yếu → `sunny` (tăng thu nhập)
  - Không hài lòng thời tiết → `cloudy`/`rainy` (cân bằng)
  - Tình hình tốt → `windy` (thử thách nhẹ)
- **Ít người chơi (≤10)**:
  - → `sunny` (khuyến khích tham gia)

#### Ban đêm (19h-5h)
- **Có người chơi đêm (>5)**:
  - Kinh tế tốt → `storm` (thử thách thú vị)
  - Kinh tế yếu → `rainy` (cân bằng)
- **Ít người chơi (≤5)**:
  - → `cloudy` (thời tiết nhẹ nhàng)

### 3. Thời gian duy trì
- **>15 players**: 15 phút (thay đổi nhanh)
- **5-15 players**: 30 phút (trung bình)
- **<5 players**: 60 phút (ổn định lâu)

## Các loại thời tiết

| Thời tiết | Growth | Price | Quality | Satisfaction | Phù hợp cho |
|-----------|--------|-------|---------|--------------|-------------|
| `sunny` | 1.3x | 1.2x | 1.0x | 80% | Tăng thu nhập nhanh |
| `cloudy` | 1.0x | 1.0x | 1.1x | 70% | Cân bằng chung |
| `rainy` | 1.1x | 0.9x | 1.4x | 60% | Tăng chất lượng |
| `windy` | 1.2x | 1.1x | 0.9x | 50% | Thu hoạch nhanh |
| `foggy` | 0.8x | 1.3x | 0.8x | 40% | Giá cao, khó trồng |
| `storm` | 0.7x | 1.5x | 1.2x | 30% | Rủi ro cao, lợi nhuận cao |
| `drought` | 0.6x | 1.4x | 0.7x | 20% | Thử thách khó |

## Tích hợp với WeatherCog

### Methods mới trong WeatherCog

#### `set_weather(weather_type, duration_minutes, source)`
```python
# Gemini Game Master set weather
success = await weather_cog.set_weather(
    weather_type="sunny",
    duration_minutes=60,
    source="Gemini Game Master"
)
```

#### `get_current_weather_info()`
```python
# Lấy thông tin chi tiết cho Gemini
weather_info = await weather_cog.get_current_weather_info()
# Returns: {
#   'current_weather': 'sunny',
#   'duration_remaining_minutes': 45,
#   'weather_effects': {...},
#   'satisfaction_score': 0.8
# }
```

### Thông báo tự động
Khi Gemini thay đổi thời tiết, hệ thống tự động:
- Gửi thông báo đến tất cả guilds có weather notification
- Hiển thị hiệu ứng mới và thời gian kéo dài
- Ghi log quyết định và lý do

## Ví dụ thực tế

### Scenario 1: Sáng sớm, ít người chơi
```
⏰ 08:00 | 🌤️ SUNNY | 👥 8 players | ⏱️ 30min
💡 Ít người chơi → chọn thời tiết dễ chơi để khuyến khích tham gia
📊 Growth: 1.3x | Price: 1.2x | Quality: 1.0x
```

### Scenario 2: Giờ cao điểm, nhiều người chơi
```
⏰ 20:00 | 🌤️ STORM | 👥 25 players | ⏱️ 15min
💡 Ban đêm + có người chơi → tạo thử thách thú vị
📊 Growth: 0.7x | Price: 1.5x | Quality: 1.2x
```

### Scenario 3: Đêm khuya, ít người
```
⏰ 02:00 | 🌤️ CLOUDY | 👥 3 players | ⏱️ 60min
💡 Ban đêm + ít người → thời tiết nhẹ nhàng
📊 Growth: 1.0x | Price: 1.0x | Quality: 1.1x
```

## Lợi ích

### 1. Tự động hóa hoàn toàn
- Không cần admin can thiệp thủ công
- Phản ứng real-time với tình hình game
- Chạy 24/7 không gián đoạn

### 2. Tối ưu trải nghiệm
- Khuyến khích người chơi khi ít người online
- Tạo thử thách khi game đông đúc
- Cân bằng kinh tế game tự động

### 3. Đa dạng gameplay
- 7 loại thời tiết khác nhau
- Hiệu ứng đặc biệt cho từng loại
- Pattern thông minh theo thời gian

### 4. Token optimization
- Sử dụng Smart Cache để giảm API calls
- Context Caching cho prompt tối ưu
- Tiết kiệm 80% token usage

## Cấu hình

### Game Master Config
```json
{
  "weather_control": {
    "enabled": true,
    "min_change_interval": 15,
    "max_change_interval": 60,
    "satisfaction_threshold": 0.6,
    "priority_weather_control": true
  }
}
```

### Weather Effects Config
Cấu hình trong `config.py`:
```python
WEATHER_EFFECTS = {
    'sunny': {
        'growth_rate': 1.3,
        'sell_price': 1.2,
        'quality_bonus': 1.0
    },
    # ... other weather types
}
```

## Monitoring

### Commands để theo dõi
- `!gm_status` - Trạng thái Game Master
- `!gm_decisions` - Quyết định gần đây
- `!weather_stats` - Thống kê thời tiết
- `!gm_tokens` - Token usage stats

### Logs
```
🌤️ Gemini Game Master set weather: sunny for 1h
🎮 Executing Game Master decision: weather_control
✅ Weather change notification sent to 3 guilds
```

## Demo & Testing

Chạy simulation 24h:
```bash
python ai/gemini_weather_demo.py
```

Kết quả lưu trong `cache/gemini_weather_simulation.json` với:
- Lịch trình thời tiết chi tiết
- Reasoning cho từng quyết định
- Thống kê phân bố thời tiết

## Kết luận

Hệ thống Weather Control của Gemini Game Master mang lại:
- **Automation**: Tự động thay đổi thời tiết mỗi 15 phút
- **Intelligence**: Quyết định thông minh dựa trên game state
- **Balance**: Tối ưu trải nghiệm cho mọi thời điểm
- **Efficiency**: Tiết kiệm token với Smart Cache

Đây là bước tiến quan trọng trong việc tạo ra một game Discord farming bot thực sự tự động và thông minh. 