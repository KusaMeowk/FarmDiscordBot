# 🤖 AI Engine Documentation

## Tổng quan

Bot Nông Trại được trang bị một hệ thống AI Engine thông minh để quản lý và phân bố các sự kiện và thời tiết một cách tự động và thích ứng. AI Engine bao gồm 3 thành phần chính hoạt động cùng nhau để tạo ra trải nghiệm game động và hấp dẫn.

## Kiến trúc AI Engine

```
🧠 Game Master AI (Bộ não chính)
    ├── 📊 Phân tích trạng thái game
    ├── 🎯 Ra quyết định thông minh  
    └── ⚖️ Cân bằng game balance

🎭 Event Manager AI (Quản lý sự kiện)
    ├── 🎪 Tạo sự kiện contextual
    ├── 🎲 Quản lý độ hiếm
    └── 📈 Theo dõi impact

🌤️ Weather Predictor AI (Dự báo thời tiết)
    ├── 🔮 Dự báo thời tiết thông minh
    ├── 🌊 Quản lý weather patterns
    └── 🎯 Tối ưu trải nghiệm người chơi
```

## 🧠 Game Master AI

### Nhiệm vụ chính
- **Phân tích Game State**: Thu thập và phân tích dữ liệu thời gian thực về người chơi
- **Quyết định thông minh**: Sử dụng AI để quyết định khi nào trigger events/weather changes
- **Cân bằng Game**: Đảm bảo game không quá dễ hoặc quá khó

### Personality Traits
Game Master AI có tính cách có thể tùy chỉnh:

```python
personality_traits = {
    'benevolence': 0.7,      # Mức độ giúp đỡ người chơi (70%)
    'mischief': 0.3,         # Mức độ tạo thách thức (30%)  
    'unpredictability': 0.5,  # Mức độ bất ngờ (50%)
    'balance_focus': 0.8,     # Ưu tiên cân bằng (80%)
    'player_retention': 0.9   # Ưu tiên giữ chân người chơi (90%)
}
```

### Game State Analysis
AI phân tích các yếu tố sau để ra quyết định:

- **Active Players**: Số lượng người chơi hoạt động
- **Economy**: Tổng tiền trong lưu thông, cân bằng kinh tế
- **Activity Level**: Mức độ tích cực tham gia của người chơi
- **Player Satisfaction**: Độ hài lòng ước tính của người chơi
- **Weather History**: Lịch sử thời tiết để tránh pattern nhàm chán
- **Event History**: Thời gian và tần suất các sự kiện

### Decision Factors

#### Event Decisions
1. **Boredom Factor** (Yếu tố nhàm chán)
   - Tính toán dựa trên activity level và thời gian từ event cuối
   - Trigger: > 70% → Tạo sự kiện excitement

2. **Economy Imbalance** (Mất cân bằng kinh tế)
   - So sánh tiền bình quân với target (5000 coins/player)
   - Trigger: > 60% → Tạo sự kiện cân bằng

3. **Weather Stagnation** (Thời tiết trì trệ)
   - Phát hiện khi thời tiết ổn định quá lâu
   - Trigger: > 50% → Tạo weather event

4. **Random Surprise** (Bất ngờ ngẫu nhiên)
   - Factor ngẫu nhiên để tạo unpredictability
   - Trigger: > 90% → Tạo surprise event

#### Weather Decisions
1. **Player Frustration** (Người chơi frustrated)
   - Phát hiện khi satisfaction thấp + thời tiết xấu
   - Action: Cải thiện thời tiết

2. **Too Easy** (Quá dễ dàng)
   - Phát hiện khi satisfaction cao + thời tiết tốt quá lâu
   - Action: Thêm thách thức

3. **Pattern Break** (Phá vỡ pattern)
   - Tránh thời tiết quá predictable
   - Action: Thay đổi weather pattern

## 🎭 Event Manager AI

### Nhiệm vụ chính
- **Contextual Event Generation**: Tạo sự kiện phù hợp với tình huống
- **Dynamic Content**: Sử dụng template + AI để tạo nội dung đa dạng
- **Rarity Management**: Quản lý độ hiếm và impact của events

### Event Types

#### 1. Economy Boost Events
- **Trigger**: Economy imbalance, player frustration
- **Effects**: Tăng giá bán, bonus coins
- **Examples**: "Thị trường sôi động", "Xuất khẩu nông sản"

#### 2. Productivity Events  
- **Trigger**: Low activity, boredom
- **Effects**: Tăng tốc độ phát triển, bonus sản lượng
- **Examples**: "Phép màu tăng trưởng", "Năng lượng thiên nhiên"

#### 3. Challenge Events
- **Trigger**: Game too easy, high satisfaction
- **Effects**: Giảm hiệu suất, tăng difficulty
- **Examples**: "Sâu bệnh", "Hạn hán"

#### 4. Special Events
- **Trigger**: Random surprises, milestones
- **Effects**: Multi-bonus, unique rewards
- **Examples**: "Lễ hội thu hoạch", "Quà tặng thiên thần"

### Rarity System
- **Common** (70%): Events thường ngày, impact nhẹ
- **Rare** (20%): Events đặc biệt, impact vừa
- **Epic** (8%): Events mạnh mẽ, impact lớn  
- **Legendary** (2%): Events siêu hiếm, impact khổng lồ

### AI Content Generation
Event Manager sử dụng template system với AI để tạo nội dung đa dạng:

```python
name_template = "{emotion} Thị trường {type}"
# AI fills: emotion="Tuyệt vời", type="sôi động"
# Result: "Tuyệt vời Thị trường sôi động"
```

## 🌤️ Weather Predictor AI

### Nhiệm vụ chính
- **Pattern Recognition**: Nhận diện và tạo weather patterns thông minh
- **Adaptive Prediction**: Dự báo thích ứng với game state
- **Player Experience Optimization**: Tối ưu trải nghiệm thời tiết

### Weather Types
1. **☀️ Sunny** (30% base): +20% crop effects, tốt cho tomato/corn
2. **☁️ Cloudy** (40% base): Neutral, tốt cho wheat
3. **🌧️ Rainy** (20% base): +10% effects, tốt cho carrot/wheat
4. **⛈️ Stormy** (8% base): -30% effects, khó khăn cho tất cả
5. **🌈 Perfect** (2% base): +50% effects, tốt cho tất cả

### Weather Patterns

#### 1. Stable Growth Pattern
- **Sequence**: Sunny → Cloudy → Sunny → Cloudy
- **Trigger**: Low frustration, stable economy
- **Purpose**: Giúp người chơi phát triển ổn định

#### 2. Challenging Cycle Pattern  
- **Sequence**: Cloudy → Rainy → Stormy → Sunny
- **Trigger**: High satisfaction, strong economy
- **Purpose**: Tăng độ khó khi người chơi quá mạnh

#### 3. Recovery Boost Pattern
- **Sequence**: Perfect → Sunny → Sunny → Cloudy  
- **Trigger**: High frustration, low activity
- **Purpose**: Hỗ trợ khi người chơi gặp khó khăn

#### 4. Surprise Mix Pattern
- **Sequence**: Stormy → Perfect → Rainy → Sunny
- **Trigger**: Boredom detected, random events
- **Purpose**: Tạo excitement và unpredictability

### AI Prediction Logic
Weather AI sử dụng context-aware prediction:

```python
# Modify probabilities based on game state
if weather_type == 'sunny' and context['frustration'] > 0.6:
    base_prob *= 2.0  # Help frustrated players
elif weather_type == 'stormy' and context['satisfaction'] > 0.8:
    base_prob *= 1.5  # Challenge satisfied players
```

## 🎮 AI Integration với Game Systems

### Events Integration
AI-generated events được tích hợp seamlessly với EventsCog:

```python
# AI tạo SmartEvent
smart_event = await event_manager.generate_contextual_event(game_state, ai_decision)

# Convert sang format EventsCog
event_data = {
    'name': smart_event.name,
    'description': smart_event.description,
    'effect_type': smart_event.effect_type,
    'effect_value': smart_event.effect_value,
    'duration': smart_event.duration_hours * 3600
}

# Trigger event
await events_cog.start_event(event_data)
```

### Weather Integration
AI predictions được sử dụng để guide weather patterns và notifications.

### Database Integration
AI sử dụng dữ liệu thực từ database:
- **Player count**: `SELECT COUNT(DISTINCT user_id) FROM users`
- **Total money**: `SELECT SUM(coins) FROM users`
- **Activity level**: Ratio của users có crops vs total users
- **Average level**: Based on `land_slots` as progression proxy

## 🛠️ Admin Commands

### Basic Commands
- `f!ai` - Hiển thị menu AI commands
- `f!ai status` - Trạng thái hệ thống AI
- `f!ai toggle` - Bật/tắt AI Engine
- `f!ai reset` - Reset tất cả AI state

### Monitoring Commands  
- `f!ai report` - Báo cáo toàn diện về hoạt động AI
- `f!ai analytics` - Phân tích chi tiết performance
- `f!ai force` - Buộc AI thực hiện analysis ngay

### Sample AI Status Output
```
🤖 AI Engine Status

🟢 System Status: Hoạt động
🕐 Last Decision: 15 phút trước  
🔄 Background Tasks: 🟢 Running

📊 Game State:
Players: 12
Satisfaction: 67%
Activity: 45%
```

## ⚙️ Configuration & Tuning

### Task Intervals
- **AI Decision Task**: 30 phút (có thể điều chỉnh)
- **Weather Task**: 45 phút
- **Event Duration**: 1-24 giờ tùy loại

### AI Personality Tuning
Có thể điều chỉnh personality traits để thay đổi behavior:

```python
# More helpful AI
self.personality_traits['benevolence'] = 0.9
self.personality_traits['mischief'] = 0.1

# More chaotic AI  
self.personality_traits['unpredictability'] = 0.8
self.personality_traits['mischief'] = 0.6
```

### Threshold Tuning
Các threshold triggers có thể điều chỉnh:

```python
# More frequent events
if factors['boredom_factor'] > 0.5:  # Default: 0.7

# More economy interventions  
elif factors['economy_imbalance'] > 0.4:  # Default: 0.6
```

## 📊 Analytics & Monitoring

### Game Master Analytics
- Game state history và trends
- Decision frequency và accuracy
- Player satisfaction tracking
- Economic balance monitoring

### Event Manager Analytics  
- Event generation rate và distribution
- Rarity distribution statistics
- Average event duration
- Event impact measurement

### Weather Predictor Analytics
- Prediction accuracy rate
- Weather pattern effectiveness
- Pattern duration statistics  
- Weather stability metrics

## 🚀 Future Enhancements

### Machine Learning Integration
- Player behavior prediction
- Adaptive personality traits
- Outcome-based learning

### Advanced Analytics
- A/B testing different AI strategies
- Player retention correlation
- Economic impact analysis

### Enhanced Weather Control
- Real-time weather API override
- Seasonal weather patterns
- Climate change simulation

### Smart Notifications
- Personalized event recommendations
- Optimal timing analysis
- Multi-channel notifications

## 🔧 Technical Implementation

### Background Tasks
AI Engine chạy các background tasks:

```python
@tasks.loop(minutes=30)
async def ai_decision_task(self):
    # Analyze game state
    # Make decisions  
    # Execute actions
    
@tasks.loop(minutes=45)  
async def ai_weather_task(self):
    # Weather prediction
    # Pattern management
    # History updates
```

### Error Handling
Comprehensive error handling với fallbacks:

```python
try:
    # AI logic
except Exception as e:
    logger.error(f"AI Error: {e}")
    return fallback_decision()
```

### Performance Optimization
- Async operations cho database calls
- Caching cho expensive calculations  
- Rate limiting cho AI decisions
- Memory management cho history data

## 📝 Best Practices

### AI Tuning
1. **Monitor player feedback** - Điều chỉnh based on player reactions
2. **Balance unpredictability** - Đủ surprise nhưng không chaos
3. **Respect player agency** - AI support, không override player choices
4. **Gradual changes** - Tránh sudden dramatic shifts

### Performance
1. **Efficient queries** - Optimize database calls
2. **Reasonable intervals** - Không quá frequent tasks
3. **Fallback mechanisms** - Always có backup plans
4. **Logging** - Comprehensive logging cho debugging

### Game Design
1. **Player-centric** - AI serves player experience
2. **Transparent reasoning** - Show AI reasoning khi appropriate  
3. **Configurable** - Allow admins to tune behavior
4. **Reversible** - Có thể undo/modify AI decisions

---

## 🎯 Kết luận

AI Engine của Bot Nông Trại tạo ra một trải nghiệm game dynamic, adaptive và engaging. Bằng cách phân tích real-time data và sử dụng intelligent decision making, AI đảm bảo game luôn fresh, challenging và enjoyable cho người chơi ở mọi skill level.

Hệ thống được thiết kế để:
- **Học hỏi** từ player behavior  
- **Thích ứng** với changing conditions
- **Cân bằng** game difficulty
- **Tạo surprise** và memorable moments
- **Duy trì engagement** lâu dài

AI Engine là một step quan trọng trong việc tạo ra một farming game Discord bot truly intelligent và responsive với community needs. 