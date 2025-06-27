# 🔄 Hệ Thống Trade Maid

Hệ thống Trade Maid cho phép người dùng giao dịch maid, tiền và stardust với nhau một cách an toàn.

## 📋 Tính Năng Chính

### ✨ Các Loại Trade
- **Maid**: Trade maid theo ID, rarity hoặc tên
- **Coins**: Trade tiền tệ trong game  
- **Stardust**: Trade stardust để reroll maid

### 🔒 Bảo Mật
- Chỉ 1 giao dịch đồng thời per kênh
- Timeout 1 phút nếu không xác nhận
- Validation tài sản trước khi thực hiện
- Transaction atomic (rollback nếu lỗi)

## 🎮 Cách Sử Dụng

### 1. Bắt Đầu Trade
```
f!trade @user
```
- Mention user bạn muốn trade
- Tạo phiên giao dịch mới trong kênh
- Chỉ 2 người được mention mới có thể tham gia

### 2. Thêm Items Vào Trade

#### Thêm Maid Theo ID
```
f!trade add -m <maid_id>
```
**Ví dụ:** `f!trade add -m abc123ef`

#### Thêm Tiền
```
f!trade add -c <số tiền>
```
**Ví dụ:** `f!trade add -c 50000`

#### Thêm Stardust
```
f!trade add -st <số stardust>
```
**Ví dụ:** `f!trade add -st 100`

#### Thêm Maid Theo Rarity
```
f!trade add -r <rarity>
```
**Ví dụ:** `f!trade add -r UR` (thêm tất cả maid UR)

**Rarity hợp lệ:** UR, SSR, SR, R

#### Thêm Maid Theo Tên
```
f!trade add -n <tên>
```
**Ví dụ:** `f!trade add -n rem` (thêm tất cả maid có tên chứa "rem")

### 3. Xác Nhận Trade
```
f!trade confirm
```
- Cả 2 người phải confirm
- Trade được thực hiện khi cả 2 đã confirm

### 4. Hủy Trade
```
f!trade cancel
```
- Bất kỳ ai trong 2 người đều có thể hủy
- Trade sẽ bị hủy ngay lập tức

### 5. Xem Trạng Thái
```
f!trade status
```
- Xem những gì mỗi người đang offer
- Kiểm tra trạng thái confirm

## 📊 Hiển Thị Trade

Khi trade đang diễn ra, hệ thống sẽ hiển thị:

```
🔄 Trade Status - ID: abc12345
User1 ⬌ User2

📦 User1 offers: ⏳ Chờ xác nhận
• Maids (3):
  • Rem UR (abc123ef)
  • Saber SSR (def456gh)
  • Android 18 R (ghi789jk)

💰 Coins: 50,000
⭐ Stardust: 100

📦 User2 offers: ✅ Đã xác nhận
• Maids (1):
  • Kurumi UR (xyz987wv)

💰 Coins: 25,000

⏰ Thời gian còn lại: 45 giây
```

## ⚠️ Lưu Ý Quan Trọng

### Giới Hạn
- **Chỉ 1 trade per kênh**: Không thể có 2 trade đồng thời trong cùng kênh
- **Timeout 1 phút**: Trade tự động hủy nếu không confirm trong 1 phút
- **Validate tài sản**: Kiểm tra đủ tiền/stardust trước khi trade

### An Toàn
- **Transaction atomic**: Nếu có lỗi, toàn bộ trade sẽ rollback
- **Maid ownership**: Chỉ trade được maid của chính mình
- **Realtime validation**: Kiểm tra tài sản trước khi execute

### Tự Động Hủy
Trade sẽ tự động hủy khi:
- Hết thời gian 1 phút
- Một trong 2 người cancel
- User không đủ tài sản khi execute
- Có lỗi trong quá trình thực hiện

## 🎯 Ví Dụ Trade Hoàn Chính

```
1. f!trade @friend
   → Bắt đầu trade với @friend

2. f!trade add -r UR
   → Thêm tất cả maid UR vào offer

3. f!trade add -c 100000
   → Thêm 100k coins

4. f!trade add -st 50
   → Thêm 50 stardust

5. (@friend) f!trade add -m def456gh
   → Friend thêm 1 maid specific

6. (@friend) f!trade add -c 50000
   → Friend thêm 50k coins

7. f!trade confirm
   → Confirm trade từ phía mình

8. (@friend) f!trade confirm
   → Friend confirm → Trade hoàn thành!
```

## 🗄️ Database

Trade history được lưu trong bảng `trade_history`:
- Trade ID
- User IDs
- Offers details
- Completion timestamp
- Channel ID

## 🔧 Commands Reference

| Command | Mô Tả | Ví Dụ |
|---------|-------|-------|
| `f!trade @user` | Bắt đầu trade | `f!trade @john` |
| `f!trade add -m <id>` | Thêm maid | `f!trade add -m abc123` |
| `f!trade add -c <money>` | Thêm tiền | `f!trade add -c 50000` |
| `f!trade add -st <dust>` | Thêm stardust | `f!trade add -st 100` |
| `f!trade add -r <rarity>` | Thêm theo rarity | `f!trade add -r UR` |
| `f!trade add -n <name>` | Thêm theo tên | `f!trade add -n rem` |
| `f!trade confirm` | Xác nhận trade | `f!trade confirm` |
| `f!trade cancel` | Hủy trade | `f!trade cancel` |
| `f!trade status` | Xem trạng thái | `f!trade status` |

---
*Hệ thống trade an toàn và tiện lợi cho community maid collectors! 🎀* 