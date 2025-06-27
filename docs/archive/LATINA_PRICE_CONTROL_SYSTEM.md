# 💰 Latina AI Price Control System

## 🎯 Tổng Quan

Hệ thống điều chỉnh giá của **Latina AI** cho phép trí tuệ nhân tạo tự động điều chỉnh giá bán nông sản và giá hạt giống mỗi giờ để cân bằng kinh tế game.

## ✨ Tính Năng Chính

### 🤖 AI Price Adjustment
- **Tự động phân tích** kinh tế game mỗi giờ
- **Điều chỉnh giá** từng loại cây hoặc toàn bộ thị trường
- **Thời gian hiệu lực** từ 1-24 giờ (mặc định 1 giờ)
- **Persistence** - Lưu trong cache, không mất khi restart bot
- **Auto-expiration** - Tự động hết hạn và reset về giá gốc

### 💎 Khả Năng Điều Chỉnh
- **Giá bán nông sản**: 0.1x đến 10x (±90% đến +900%)
- **Giá hạt giống**: 0.1x đến 10x (±90% đến +900%)
- **Cây cụ thể** hoặc **toàn bộ thị trường**
- **Lý do AI** - Mọi điều chỉnh đều có giải thích rõ ràng

## 🎮 Lệnh Discord

### 📊 Xem Trạng Thái
```bash
f!gemini status        # Tình trạng tổng quát của Latina
f!gemini prices        # Danh sách điều chỉnh giá hiện tại
f!market              # Thị trường với giá đã điều chỉnh
```

### 🔧 Quản Lý (Admin)
```bash
f!gemini toggle       # Bật/tắt Latina AI
f!gemini analyze      # Yêu cầu phân tích ngay lập tức
f!gemini history      # Lịch sử quyết định
```

## 🛠️ Technical Implementation

### 🔗 Core Components

#### 1. **PricingCoordinator** (`utils/pricing.py`)
```python
# Apply AI price adjustment
pricing_coordinator.apply_ai_price_adjustment(
    crop_type="carrot",           # Loại cây hoặc "all"
    sell_price_modifier=1.2,      # +20% giá bán
    seed_price_modifier=0.8,      # -20% giá hạt giống  
    reasoning="AI explanation",    # Lý do điều chỉnh
    duration_hours=1              # Thời gian hiệu lực
)

# Get current AI modifiers
sell_mod, seed_mod = pricing_coordinator.get_ai_price_modifier("carrot")

# Get final price with all modifiers
final_price, modifiers = pricing_coordinator.calculate_final_price("carrot", bot)
```

#### 2. **GeminiEconomicManagerV2** (`ai/gemini_manager_v2.py`)
```python
# AI decision for price adjustment
decision = GeminiDecision(
    action_type='PRICE_ADJUSTMENT',
    parameters={
        'crop_type': 'carrot',
        'sell_price_modifier': 1.15,
        'seed_price_modifier': 0.9,
        'duration_hours': 1
    },
    reasoning="Market analysis shows carrot oversupply..."
)
```

### 📁 Data Persistence

#### Cache File: `cache/ai_price_adjustments.json`
```json
{
  "carrot": {
    "sell_price_modifier": 1.2,
    "seed_price_modifier": 0.8,
    "reasoning": "Điều chỉnh cà rốt để khuyến khích sản xuất",
    "timestamp": "2025-01-21T20:30:00",
    "expires_at": "2025-01-21T21:30:00",
    "duration_hours": 1
  }
}
```

## 🔄 AI Decision Process

### 📈 Hourly Analysis Cycle
1. **Thu thập dữ liệu**:
   - Tổng người chơi và hoạt động
   - Phân bổ tiền tệ
   - Tình trạng thời tiết
   - Sự kiện hiện tại

2. **Phân tích AI**:
   - Economic health score
   - Money distribution balance  
   - Market supply/demand
   - Player activity patterns

3. **Quyết định điều chỉnh**:
   - Loại cây cần điều chỉnh
   - Mức độ thay đổi giá
   - Thời gian hiệu lực
   - Lý do cụ thể

4. **Thực thi và thông báo**:
   - Apply vào pricing system
   - Gửi notification Discord
   - Lưu vào cache
   - Log activity

### 🎯 AI Decision Criteria

#### Tăng Giá Bán (Sell Price ↑)
- **Supply thấp**: Ít người trồng loại cây đó
- **Economic boost**: Cần kích thích hoạt động
- **Premium crops**: Cây high-value cần premium pricing

#### Giảm Giá Bán (Sell Price ↓)  
- **Oversupply**: Quá nhiều người trồng
- **Market balance**: Cần cân bằng lạm phát
- **Accessibility**: Giúp người chơi mới tiếp cận

#### Giảm Giá Hạt Giống (Seed Cost ↓)
- **Khuyến khích sản xuất**: Boost farming activity  
- **New player support**: Giúp người mới bắt đầu
- **Economic stimulus**: Tăng lưu thông tiền tệ

#### Tăng Giá Hạt Giống (Seed Cost ↑)
- **Control inflation**: Hạn chế lạm phát
- **Resource scarcity**: Tạo độ khan hiếm
- **Premium balance**: Cân bằng cây đắt tiền

## 📊 Example Scenarios

### 🌟 Scenario 1: Economic Stimulus
```json
{
  "action_type": "PRICE_ADJUSTMENT", 
  "parameters": {
    "crop_type": "all",
    "sell_price_modifier": 1.1,
    "seed_price_modifier": 0.9,
    "duration_hours": 2
  },
  "reasoning": "Economic health score thấp (0.65), cần kích thích tổng thể"
}
```

### 🎯 Scenario 2: Crop-Specific Balance
```json
{
  "action_type": "PRICE_ADJUSTMENT",
  "parameters": {
    "crop_type": "wheat", 
    "sell_price_modifier": 0.85,
    "seed_price_modifier": 1.15,
    "duration_hours": 1
  },
  "reasoning": "Lúa mì oversupply (70% farmers), cần giảm incentive"
}
```

### 💎 Scenario 3: Premium Crop Focus
```json
{
  "action_type": "PRICE_ADJUSTMENT",
  "parameters": {
    "crop_type": "strawberry",
    "sell_price_modifier": 1.25, 
    "seed_price_modifier": 0.8,
    "duration_hours": 3
  },
  "reasoning": "Dâu tây ít người trồng, tăng giá để khuyến khích"
}
```

## 🔔 Discord Notifications

### 💖 Price Adjustment Embed
```
💰 Latina đã điều chỉnh giá Cà rốt!

🥕 Sản phẩm: Cà rốt
💰 Giá bán: 📈 +20.0% (1.20x)  
🌱 Giá hạt giống: 📉 -20.0% (0.80x)

🌸 Lý do của mình:
Phân tích cho thấy cà rốt đang thiếu nguồn cung...

📊 Độ tin cậy: 85%
⏰ Thời gian hiệu lực: 1 giờ
🎯 Ưu tiên: MEDIUM

Latina AI Economic Manager • f!market để xem giá mới
```

## ⚡ Performance & Safety

### 🛡️ Safety Limits
- **Price bounds**: 0.1x - 10x (never break economy)
- **Duration limits**: 1-24 hours max
- **Auto-expiration**: Always returns to base price
- **Validation**: Check crop existence before apply

### 📈 Performance
- **Cache persistence**: O(1) lookup for active adjustments
- **Memory efficient**: Only store active adjustments
- **Auto-cleanup**: Expired adjustments removed automatically
- **JSON serialization**: Fast save/load with proper datetime handling

### 🔄 Integration
- **Weather system**: Works with weather price modifiers
- **Event system**: Combines with event bonuses
- **Market display**: Seamlessly integrated with `f!market`
- **Shop system**: Auto-applies to seed purchases

## 🎉 Benefits

### 👥 For Players
- **Dynamic economy**: Prices always changing and interesting
- **Smart balancing**: AI prevents economic stagnation  
- **Clear reasoning**: Always know WHY prices changed
- **Fair system**: No human bias, pure data-driven

### 🎮 For Admins
- **Hands-off management**: AI handles daily price balancing
- **Full transparency**: Complete logging and reasoning
- **Manual override**: Can disable or force analyze anytime
- **Rich monitoring**: Detailed status and history commands

### 🚀 For Game Health
- **Economic stability**: Automatic inflation/deflation control
- **Player engagement**: Dynamic pricing encourages activity
- **Market diversity**: Promotes growing different crops
- **Long-term balance**: Sustained healthy economy

---

## 🎀 Conclusion

Latina AI Price Control System mang lại **economic intelligence** cho Discord farming bot, tự động duy trì cân bằng thị trường mà không cần can thiệp thủ công. Hệ thống kết hợp **AI decision making**, **persistent caching**, và **transparent communication** để tạo ra trải nghiệm kinh tế phong phú và công bằng cho tất cả người chơi.

**Latina đã sẵn sàng quản lý kinh tế trang trại của bạn! 💖** 