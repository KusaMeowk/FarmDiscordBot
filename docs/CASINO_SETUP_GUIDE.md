# 🎰 HƯỚNG DẪN SETUP HỆ THỐNG CASINO BLACKJACK

## 📋 Tổng quan
Hệ thống Casino Blackjack đã được tích hợp vào Farm Bot với các tính năng:
- ✅ **Blackjack game** với logic đầy đủ 
- ✅ **Custom emoji** cho các lá bài
- ✅ **Discord UI** với buttons tương tác
- ✅ **Economy integration** với hệ thống tiền tệ
- ✅ **Anti-spam** và cooldown system

## 🎯 Các bước triển khai

### Bước 1: Chuẩn bị ảnh emoji
1. **Tạo thư mục**: `card_images/` trong root project
2. **Chuẩn bị 53 file ảnh** với format:
   ```
   2_spades.png, 3_spades.png, ..., A_spades.png    (13 lá)
   2_hearts.png, 3_hearts.png, ..., A_hearts.png    (13 lá)  
   2_diamonds.png, 3_diamonds.png, ..., A_diamonds.png (13 lá)
   2_clubs.png, 3_clubs.png, ..., A_clubs.png       (13 lá)
   card_back.png                                      (1 lá)
   ```

3. **Yêu cầu ảnh**:
   - Format: PNG, JPG, GIF, WEBP
   - Kích thước: 128x128 pixels (recommended)
   - Dung lượng: Dưới 256KB mỗi file
   - Tên file: Đúng format `<rank>_<suit>.<extension>`

### Bước 2: Upload emoji lên Discord
1. **Chỉnh sửa `upload_casino_emojis.py`**:
   ```python
   BOT_TOKEN = "YOUR_ACTUAL_BOT_TOKEN"
   GUILD_ID = 1234567890  # Your Discord Server ID
   ```

2. **Lấy Bot Token**:
   - Vào [Discord Developer Portal](https://discord.com/developers/applications)
   - Chọn bot application
   - Tab "Bot" → Copy Token

3. **Lấy Guild ID**:
   - Bật Developer Mode trong Discord
   - Right-click server → Copy ID

4. **Chạy script upload**:
   ```bash
   python upload_casino_emojis.py
   ```

5. **Kiểm tra kết quả**:
   - Script sẽ tự động cập nhật `config.py`
   - Emoji IDs sẽ được thêm vào `CARD_EMOJIS`

### Bước 3: Cấu hình Casino
Các setting trong `config.py`:
```python
CASINO_CONFIG = {
    "min_bet": 10,        # Cược tối thiểu
    "max_bet": 10000,     # Cược tối đa  
    "house_edge": 0.02,   # House edge 2%
    "blackjack_payout": 1.5,  # Blackjack trả 3:2
    "cooldown": 3         # Cooldown 3 giây giữa game
}
```

### Bước 4: Test hệ thống
1. **Khởi động bot**: `python bot.py`
2. **Test commands**:
   ```
   f!bj              # Hiển thị hướng dẫn
   f!bj 100          # Chơi với 100 coins
   f!blackjack 500   # Chơi với 500 coins
   f!casino          # Shortcut info
   ```

## 🎮 Cách chơi Blackjack

### Luật cơ bản
- **Mục tiêu**: Đạt tổng điểm gần 21 nhất mà không vượt quá
- **Giá trị bài**: 
  - A = 1 hoặc 11 (tự động tính tối ưu)
  - J, Q, K = 10
  - Các số = giá trị thực

### Gameplay
1. **Đặt cược**: `f!bj <số_tiền>`
2. **Nhận bài**: Player và dealer mỗi người 2 lá
3. **Hành động**:
   - 🎯 **Hit**: Rút thêm bài
   - 🛑 **Stand**: Dừng lại
   - 🔄 **Chơi lại**: Game mới với cùng mức cược

### Tỷ lệ trả
- **Blackjack** (21 với 2 lá đầu): 3:2 (150%)
- **Thắng thường**: 1:1 (100%)  
- **Hòa**: Trả lại tiền cược
- **Thua**: Mất tiền cược

## 🔧 Troubleshooting

### Lỗi "Casino system không có sẵn"
- Kiểm tra file `features/casino.py` tồn tại
- Kiểm tra `bot.py` đã load `'features.casino'`
- Restart bot

### Emoji hiển thị text thay vì ảnh
- Kiểm tra emoji đã upload thành công
- Kiểm tra `config.py` có emoji IDs
- Bot phải có quyền Use External Emojis

### Game không phản hồi buttons
- Kiểm tra bot có quyền Send Messages
- Kiểm tra message interaction permissions
- User phải là người bắt đầu game

### Database errors
- Kiểm tra user đã đăng ký: `f!register`
- Kiểm tra database connection
- Check bot permissions

## 📊 Features nâng cao (có thể thêm)

### Casino Stats
```python
# Thêm vào User model
casino_wins: int = 0
casino_losses: int = 0  
casino_total_bet: int = 0
casino_biggest_win: int = 0
```

### Leaderboard Casino
```
f!casino_leaders     # Top casino winners
f!casino_stats       # Personal casino stats
```

### Additional Games
- **Slots** (máy đánh bạc)
- **Roulette** (roulette)
- **Poker** (poker 5 lá)
- **Coin Flip** (xúc xắc)

### VIP System
- **High roller rooms** (bàn cược cao)
- **Daily casino bonus** (chips miễn phí)
- **Casino achievements** (thành tựu)

## 🎰 Commands Reference

| Command | Shortcut | Description |
|---------|----------|-------------|
| `f!blackjack [bet]` | `f!bj [bet]` | Chơi Blackjack |
| `f!casino` | `f!casino` | Thông tin casino |

### Examples
```bash
f!bj                 # Hiển thị hướng dẫn
f!bj 100             # Cược 100 coins  
f!blackjack 1000     # Cược 1000 coins
f!casino             # Thông tin casino
```

## 🔒 Security & Balance

### Anti-cheat measures
- Server-side validation
- Immutable game state  
- Rate limiting
- Database integrity

### Economic balance
- House edge 2%
- Bet limits (10-10,000)
- Cooldown system
- Integration với economy

## 🎉 Kết luận
Hệ thống Casino Blackjack đã sẵn sàng! Với visual đẹp mắt từ custom emoji và gameplay mượt mà, người chơi sẽ có trải nghiệm casino tuyệt vời ngay trong Discord.

**Chơi có trách nhiệm!** 🎰 