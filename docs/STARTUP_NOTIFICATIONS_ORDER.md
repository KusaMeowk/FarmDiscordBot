# 🌅 Thứ Tự Thông Báo Khởi Động Bot

## 📋 Tổng Quan

Khi bot khởi động, các thông báo sẽ được gửi theo thứ tự ưu tiên để đảm bảo trải nghiệm người dùng tốt nhất.

## 🕐 Timeline Thông Báo

### **1. Thông Báo Latina AI (Đầu tiên - 2 giây)**
- **Thời gian**: 2 giây sau khi bot ready
- **Nguồn**: `features/gemini_economic_cog.py` → `_send_startup_notification()`
- **Mục đích**: Giới thiệu Latina AI Economic Manager ĐẦU TIÊN

```python
🎀 Latina AI Economic Manager đã thức dậy!
Xin chào mọi người! Mình là Latina, trợ lý AI kinh tế...
```

### **2. Thông Báo Farm Bot (Sau đó - 6 giây)**
- **Thời gian**: 6 giây sau khi bot ready
- **Nguồn**: `bot.py` → `_send_farm_bot_notification_later()`
- **Mục đích**: Thông báo hệ thống hoàn tất khởi động

```python
🌅 Farm Bot đã sẵn sàng!
Bot nông trại hoàn tất khởi động! 🌞
Tất cả hệ thống đã được kích hoạt...
```

## 🎯 Channel Selection Logic

### **Thứ Tự Ưu Tiên Channel:**
1. `general` - Channel chính của server
2. `announce`/`announcements` - Channel thông báo
3. `bot`/`notification` - Channel dành cho bot
4. `farm`/`farming` - Channel game-specific
5. **Fallback**: Channel đầu tiên có permission `send_messages`

### **Permission Requirements:**
- Bot phải có quyền `send_messages` trong channel
- Channel phải là text channel
- Channel phải trong cùng guild

## 🔧 Implementation Details

### **Wake-up Notification (bot.py)**
```python
async def _send_wake_up_notification(self):
    # Gửi ngay lập tức
    embed = EmbedBuilder.create_base_embed(
        title="🌅 Farm Bot đã thức dậy!",
        color=0xFFD700  # Màu vàng buổi sáng
    )
    
    # Gửi tới tất cả guilds
    for guild in self.guilds:
        target_channel = await self._find_best_notification_channel(guild)
        await target_channel.send(embed=embed)
        await asyncio.sleep(0.5)  # Rate limit protection
    
    # Delay buffer
    await asyncio.sleep(2)
```

### **Latina AI Notification (gemini_economic_cog.py)**
```python
async def _send_startup_notification(self):
    # Delay để thông báo thức dậy gửi trước
    await asyncio.sleep(8)
    
    embed = EmbedBuilder.create_base_embed(
        title="🎀 Latina AI Economic Manager đã thức dậy!",
        color=0xff69b4  # Màu hồng của Latina
    )
    
    # Gửi tới tất cả guilds
    ...
```

## 📊 Notification Content

### **🎀 Latina AI Notification (FIRST)**
- **Title**: "🎀 Latina AI Economic Manager đã thức dậy!"
- **Description**: Giới thiệu Latina AI
- **Fields**:
  - 🌸 Tính năng tự động của Latina
  - 💝 Lệnh tương tác với Latina
- **Color**: `0xff69b4` (Hồng)
- **Footer**: Latina sẽ bắt đầu làm việc
- **Priority**: HIGHEST (sent first)

### **🌅 Farm Bot Notification (SECOND)**
- **Title**: "🌅 Farm Bot đã sẵn sàng!"
- **Description**: Hệ thống hoàn tất khởi động
- **Fields**:
  - 🎮 Hệ thống đã sẵn sàng
  - ⚡ Lệnh cơ bản
  - 🤖 AI Systems Active
- **Color**: `0xFFD700` (Vàng)
- **Footer**: Thời gian hoàn tất khởi động
- **Priority**: SECONDARY (sent after Latina)

## 🛡️ Rate Limiting & Error Handling

### **Rate Limit Protection:**
- Delay 0.5 giây giữa các guild (wake-up)
- Delay 1 giây giữa các guild (Latina)
- Tổng thời gian gửi: ~2-5 giây tùy số guild

### **Error Handling:**
- Bỏ qua guild không có channel phù hợp
- Log warning cho các lỗi gửi thông báo
- Không crash bot nếu có lỗi notification

### **Fallback Logic:**
- Nếu không tìm thấy channel priority → dùng channel đầu tiên
- Nếu không có permission → bỏ qua guild đó
- Nếu lỗi embed → log error nhưng tiếp tục

## 🎨 Visual Timeline

```
0s    Bot ready, status set
2s    🎀 Latina AI notification sent (ĐẦU TIÊN)
3s    Rate limit delay between guilds
6s    🌅 Farm Bot ready notification sent (SAU ĐÓ)
7s    Rate limit delay between guilds
8s    All startup notifications completed
```

## 🔄 Future Enhancements

### **Có thể thêm:**
- Game Master startup notification (nếu cần)
- Weather system ready notification
- Database health check notification
- Custom guild-specific startup messages

### **Tối ưu hóa:**
- Parallel sending to multiple guilds
- Custom delay settings per notification type
- User preference for notification types
- Channel-specific notification routing

---

**Kết quả**: Thông báo "Thức dậy" sẽ luôn được gửi đầu tiên, tạo trải nghiệm khởi động nhất quán và thân thiện cho users! 🌅✨ 