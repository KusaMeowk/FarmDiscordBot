# 🤖 HƯỚNG DẪN AI NOTIFICATIONS

## 📋 Tổng quan

Hệ thống AI Notifications cho phép admin server thiết lập thông báo tự động khi AI Engine tạo events hoặc thay đổi weather.

## 🚀 Thiết lập ban đầu

### 1. Setup thông báo AI tại channel hiện tại:
```
f!ai setupnotify
```

### 2. Setup thông báo AI tại channel cụ thể:
```
f!ai setupnotify <channel_id>
```

### 3. Setup với options cụ thể:
```
f!ai setupnotify <channel_id> <event_notifications> <weather_notifications>

# Ví dụ:
f!ai setupnotify 123456789 True False  # Chỉ event notifications
f!ai setupnotify 123456789 False True # Chỉ weather notifications
```

## 📊 Quản lý thông báo

### Kiểm tra trạng thái:
```
f!ai notifystatus
```

### Bật/tắt tất cả thông báo:
```
f!ai togglenotify          # Toggle trạng thái hiện tại
f!ai togglenotify True     # Bật
f!ai togglenotify False    # Tắt
```

### Bật/tắt thông báo events:
```
f!ai toggleevent           # Toggle
f!ai toggleevent True      # Bật event notifications
f!ai toggleevent False     # Tắt event notifications
```

### Bật/tắt thông báo weather:
```
f!ai toggleweather         # Toggle
f!ai toggleweather True    # Bật weather notifications  
f!ai toggleweather False   # Tắt weather notifications
```

## 🔔 Loại thông báo

### 🎪 AI Event Notifications
Thông báo khi AI Game Master tạo event mới:
- **Tiêu đề**: "🤖 AI Event Generated"
- **Nội dung**: Tên event, mô tả, AI reasoning, rarity, duration
- **Trigger**: Mỗi 30 phút (nếu AI quyết định tạo event)

### 🌤️ AI Weather Notifications  
Thông báo khi AI Weather Predictor thay đổi thời tiết:
- **Tiêu đề**: "🌤️ AI Weather Change" 
- **Nội dung**: Thời tiết mới, độ tin cậy, AI reasoning, duration
- **Trigger**: Mỗi 45 phút (nếu AI quyết định thay đổi weather)

## 🛡️ Permissions

### Cần permissions để setup:
- `manage_channels` - Để sử dụng setup và toggle commands
- Không cần permission đặc biệt để xem status

### Channel requirements:
- Channel phải trong cùng server
- Bot phải có permission `send_messages` trong channel đó

## 📝 Ví dụ sử dụng

### Setup hoàn chỉnh:
```bash
# 1. Setup AI notifications tại channel hiện tại
f!ai setupnotify

# 2. Kiểm tra trạng thái
f!ai notifystatus

# 3. Tạm tắt weather notifications nếu không cần
f!ai toggleweather False

# 4. Kiểm tra lại
f!ai notifystatus
```

### Quản lý hàng ngày:
```bash
# Xem trạng thái AI và notifications
f!ai status
f!ai notifystatus

# Tạm tắt thông báo khi maintenance
f!ai togglenotify False

# Bật lại sau maintenance
f!ai togglenotify True
```

## 🔄 Workflow AI Notifications

### AI Event Flow:
1. **AI Decision Task** (mỗi 30 phút)
2. **Game Master AI** phân tích game state
3. **Generate contextual event** nếu cần thiết
4. **Trigger event** trong EventsCog
5. **Send notification** đến tất cả channels đã setup

### AI Weather Flow:
1. **AI Weather Task** (mỗi 45 phút)  
2. **Weather Predictor AI** phân tích conditions
3. **Apply weather prediction** nếu cần thiết
4. **Send notification** đến tất cả channels đã setup

## 📊 Database Storage

Thông tin notifications được lưu trong database table:
```sql
ai_notifications (
    guild_id INTEGER PRIMARY KEY,
    channel_id INTEGER NOT NULL,
    enabled BOOLEAN DEFAULT 1,
    event_notifications BOOLEAN DEFAULT 1,
    weather_notifications BOOLEAN DEFAULT 1
)
```

## 🎯 Best Practices

### Setup recommendations:
- **Setup 1 channel** dành riêng cho AI notifications
- **Tên channel** gợi ý: `#ai-notifications`, `#bot-logs`, `#farm-ai`
- **Permissions**: Chỉ cho admins xem để tránh spam users

### Management tips:
- **Monitor frequency**: Kiểm tra `f!ai status` định kỳ
- **Adjust settings**: Tắt weather notifications nếu quá nhiều
- **Channel maintenance**: Đảm bảo channel luôn accessible

## ❓ Troubleshooting

### Không nhận được thông báo:
1. Kiểm tra `f!ai notifystatus` - enabled?
2. Kiểm tra `f!ai status` - AI system hoạt động?
3. Kiểm tra bot permissions trong channel
4. Kiểm tra channel có tồn tại không

### Quá nhiều thông báo:
1. Tắt weather notifications: `f!ai toggleweather False`
2. Hoặc tắt hẳn: `f!ai togglenotify False`
3. Setup channel riêng cho AI thay vì channel chung

### Setup mới không hoạt động:
1. Restart bot để reload database
2. Kiểm tra channel_id có đúng không
3. Test với channel khác

---

**Hệ thống AI Notifications giúp admin theo dõi và hiểu cách AI Engine điều chỉnh game balance real-time!** 🤖✨ 