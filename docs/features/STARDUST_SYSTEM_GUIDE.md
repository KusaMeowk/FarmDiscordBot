# Hướng Dẫn Hệ Thống Stardust

## 🌟 Tổng Quan

Hệ thống **Stardust** (Bụi Sao) cho phép người chơi:
- **Tách maid** không cần thiết thành bụi sao
- **Reroll buffs** của maid quan trọng bằng bụi sao
- **Tối ưu hóa** collection maid với buffs tốt hơn

## ⭐ Cơ Chế Hoạt Động

### 💥 Dismantle Rewards
Khi tách maid, bạn nhận được bụi sao theo rarity:

| Rarity | Dismantle Reward |
|--------|------------------|
| **UR** | 100 ⭐ bụi sao   |
| **SSR**| 50 ⭐ bụi sao    |
| **SR** | 25 ⭐ bụi sao    |
| **R**  | 10 ⭐ bụi sao    |

### 🎲 Reroll Costs
Chi phí để reroll buffs của maid:

| Rarity | Reroll Cost |
|--------|-------------|
| **UR** | 80 ⭐ bụi sao |
| **SSR**| 40 ⭐ bụi sao |
| **SR** | 20 ⭐ bụi sao |
| **R**  | 8 ⭐ bụi sao  |

### 💰 Economics (Tỷ lệ 1.25x)
- **Mọi rarity** đều có tỷ lệ Reward/Cost = 1.25x
- **Luôn có lời** khi tách maid để reroll
- **Khuyến khích** trade duplicate maids

## 🔄 Workflow Thực Tế

### Scenario 1: Tối Ưu Main Maid
```
1. Có 1 UR Saber với buffs kém (growth_speed +25%, sell_price +30%)
2. Tách 2 SSR duplicate (2×50⭐ = 100⭐)
3. Reroll UR Saber (80⭐)
4. Nhận buffs mới (growth_speed +45%, sell_price +48%)
5. Còn dư 20⭐ cho lần sau
```

### Scenario 2: Trade Cross-Rarity
```
1. Tách 5 R duplicate (5×10⭐ = 50⭐)
2. Reroll 1 SSR (40⭐)
3. Còn dư 10⭐
4. Hoặc reroll 2 SR (2×20⭐ = 40⭐)
```

### Scenario 3: Farming Strategy
```
1. Gacha để collect maids
2. Tách tất cả duplicate
3. Tích lũy stardust
4. Reroll các main maid để có perfect buffs
```

## 🤖 Discord Commands

### `/maid_stardust`
- **Mục đích**: Xem số bụi sao hiện có
- **Hiển thị**: Stardust amount + bảng giá reroll/dismantle
- **Usage**: `/maid_stardust`

### `/maid_dismantle <maid_id>`
- **Mục đích**: Tách maid thành bụi sao
- **Safety**: Có confirmation view
- **Hạn chế**: Không thể tách maid đang active
- **Usage**: `/maid_dismantle abc12345`

### `/maid_reroll <maid_id>`
- **Mục đích**: Reroll buffs của maid
- **Safety**: Có confirmation view + preview buffs cũ
- **Kết quả**: Buffs hoàn toàn mới & random
- **Usage**: `/maid_reroll def67890`

## 🎯 Ví Dụ Sử Dụng

### Bước 1: Kiểm tra stardust
```
/maid_stardust
```
**Output:**
```
⭐ Bụi Sao: 75 bụi sao

🔄 Reroll Costs:        💥 Dismantle Rewards:
UR: 80 ⭐               UR: 100 ⭐
SSR: 40 ⭐              SSR: 50 ⭐
SR: 20 ⭐               SR: 25 ⭐
R: 8 ⭐                 R: 10 ⭐
```

### Bước 2: Tách maid duplicate
```
/maid_dismantle abc12345
```
**Confirmation:**
```
💥 Xác Nhận Dismantle
🗑️ Maid bị xóa: SSR ⚡ Mikasa Ackerman
⭐ Nhận được: 50 bụi sao
⚠️ Cảnh báo: Hành động không thể hoàn tác!
[✅ Xác Nhận] [❌ Hủy]
```

### Bước 3: Reroll main maid
```
/maid_reroll def67890
```
**Confirmation:**
```
🎲 Xác Nhận Reroll
🎯 Maid: UR 💙 Rem the Devoted Maid
💰 Chi phí: 80 bụi sao

✨ Buffs hiện tại:
🌱 Tăng Tốc Sinh Trưởng: +32%
💎 Tăng Giá Bán: +28%

⚠️ Lưu ý: Buffs sẽ được random lại hoàn toàn!
[🎲 Reroll] [❌ Hủy]
```

### Kết quả sau reroll:
```
🎲 Reroll Thành Công!
Rem the Devoted Maid đã có buffs mới!

✨ Buffs Mới:
📈 Tăng Sản Lượng: +47%
💎 Tăng Giá Bán: +44%

💫 Stardust Còn Lại: 45 bụi sao
```

## 📊 Database Schema

### UserStardust Table
```sql
CREATE TABLE user_stardust (
    user_id INTEGER PRIMARY KEY,
    stardust_amount INTEGER DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### UserStardust Class Methods
```python
def add_stardust(self, amount: int) -> None:
    """Thêm stardust"""
    self.stardust_amount += amount

def spend_stardust(self, amount: int) -> bool:
    """Tiêu stardust (trả về True nếu đủ)"""
    if self.stardust_amount >= amount:
        self.stardust_amount -= amount
        return True
    return False
```

## 🔐 Security Features

### 1. **Ownership Validation**
- Chỉ có thể dismantle/reroll maid của chính mình
- Dùng `_find_user_maid()` để verify ownership

### 2. **Confirmation Views**
- Tất cả operations đều có confirmation UI
- Preview chi tiết trước khi execute
- Timeout 300 seconds

### 3. **Active Maid Protection**
- Không thể dismantle maid đang active
- Phải equip maid khác trước

### 4. **Transaction Safety**
- Check stardust trước khi reroll
- Update database atomically
- Rollback nếu có lỗi

## 🎮 Strategic Tips

### 💡 Khi Nào Nên Dismantle?
- ✅ Maid duplicate không dùng
- ✅ Maid với buffs kém
- ✅ Lower rarity khi có higher rarity tương tự
- ❌ Maid đang active
- ❌ Maid duy nhất của rarity cao

### 💡 Khi Nào Nên Reroll?
- ✅ Main maid với buffs thấp (<35%)
- ✅ Khi có đủ stardust dư
- ✅ Buffs không phù hợp strategy
- ❌ Buffs đã tốt (>45%)
- ❌ Khi stardust ít

### 💡 Stardust Management
- 🎯 **Priority**: UR > SSR > SR > R
- 💰 **Reserve**: Luôn giữ 80⭐ cho UR reroll
- 📈 **ROI**: Reroll maids dùng thường xuyên
- 🔄 **Cycling**: Dismantle → Accumulate → Reroll

## 🚀 Future Enhancements

### Potential Features
- **Stardust Shop**: Mua items đặc biệt
- **Bulk Operations**: Dismantle nhiều maid cùng lúc
- **Reroll Preview**: Xem trước buff ranges
- **Stardust Events**: Double rewards periods
- **Achievement System**: Rewards cho milestones

### Balance Considerations
- **Rate Adjustments**: Có thể điều chỉnh costs/rewards
- **Rarity Scaling**: Buffs cap khác nhau theo rarity
- **Economic Events**: Seasonal promotions

## 📋 Implementation Status

### ✅ Completed
- [x] Stardust configuration system
- [x] UserStardust model & database
- [x] Discord commands (/maid_stardust, /maid_dismantle, /maid_reroll)
- [x] Confirmation views với safety
- [x] Ownership validation
- [x] Economic balance (1.25x ratio)

### 🚀 Ready for Use
Hệ thống stardust đã hoàn chỉnh và sẵn sàng sử dụng trong production! 