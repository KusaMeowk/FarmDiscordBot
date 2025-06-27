# ⏰ Maid Equip Cooldown System

## 📋 Tổng Quan

Hệ thống cooldown 10 giờ cho maid equip nhằm:
- ✅ **Tránh spam**: Ngăn chặn việc thay đổi maid liên tục
- ✅ **Game balance**: Tạo strategic thinking khi chọn maid
- ✅ **Encourage planning**: Người chơi phải cân nhắc kỹ trước khi equip

---

## 🎯 **Tính Năng Chính**

### **⏰ Cooldown Duration**
- **Thời gian**: 10 giờ kể từ lần equip cuối
- **Scope**: Áp dụng cho tất cả maid equip operations
- **Reset**: Tự động reset sau 10 giờ

### **🛡️ Protection Logic**
- Check cooldown trước mỗi lần equip
- Block equip nếu còn trong cooldown
- Hiển thị thời gian còn lại chính xác

### **📊 Database Schema**
```sql
CREATE TABLE maid_equip_cooldown_v2 (
    user_id INTEGER PRIMARY KEY,
    last_equip_time TEXT NOT NULL,
    cooldown_until TEXT NOT NULL
)
```

---

## 🎮 **Commands**

### **`f!mequip <id>` - Trang bị maid (với cooldown)**
```
📝 Mô tả: Trang bị maid với 10 giờ cooldown
🔒 Ràng buộc: Phải đợi 10 giờ giữa các lần equip
⏰ Cooldown: 10 giờ
```

**Workflow:**
1. Check registration
2. **Check 10-hour cooldown** ← NEW
3. Find target maid
4. Deactivate current maid
5. Activate new maid
6. **Set new 10-hour cooldown** ← NEW
7. Show success message with cooldown warning

**Success Output:**
```
✅ Trang bị thành công!
Đã trang bị 🌟 Rem

✨ Buffs được kích hoạt
🌱 Growth Speed: +25.0%

⏰ Cooldown
Bạn sẽ phải đợi 10 giờ để thay đổi maid khác!
```

**Cooldown Block:**
```
⏰ Equip Cooldown
Bạn cần đợi 8 giờ 45 phút nữa mới có thể thay đổi maid!

💡 Tại sao có cooldown?
Để tránh spam change maid và tạo balance cho game.

🎯 Tip
Hãy cân nhắc kỹ trước khi equip maid để tránh phải đợi lâu!
```

### **`f!mcooldown` - Xem cooldown status**
```
📝 Mô tả: Kiểm tra thời gian cooldown còn lại
🎯 Output: Ready/Cooldown với thời gian chính xác
⚡ Shortcut: f!mcooldown
```

**Ready State:**
```
✅ Sẵn sàng equip!
Bạn có thể trang bị maid mới bất cứ lúc nào!

🎯 Lưu ý
Sau khi equip, bạn sẽ phải đợi 10 giờ để thay đổi lại!
```

**Cooldown State:**
```
⏰ Đang trong cooldown
Bạn cần đợi 3 giờ 22 phút nữa để thay đổi maid!

💡 Mẹo
Dùng thời gian này để farm và tận dụng buffs của maid hiện tại!
```

---

## 🔧 **Technical Implementation**

### **Helper Functions**

#### **`check_equip_cooldown(user_id)`**
```python
async def check_equip_cooldown(self, user_id: int) -> tuple[bool, str]:
    """
    Check if user can equip maid
    
    Returns:
        tuple[bool, str]: (can_equip, time_remaining_text)
    """
```

**Logic:**
1. Query cooldown table
2. Compare current time vs cooldown_until
3. Calculate time remaining
4. Format human-readable text

#### **`set_equip_cooldown(user_id)`**
```python
async def set_equip_cooldown(self, user_id: int):
    """Set 10-hour cooldown after successful equip"""
```

**Logic:**
1. Calculate cooldown_until = now + 10 hours
2. INSERT OR REPLACE into cooldown table
3. Save both last_equip_time and cooldown_until

### **Time Calculation**
```python
# Calculate remaining time
time_remaining = cooldown_until - now
hours = int(time_remaining.total_seconds() // 3600)
minutes = int((time_remaining.total_seconds() % 3600) // 60)

# Format display
if hours > 0:
    time_text = f"{hours} giờ {minutes} phút"
else:
    time_text = f"{minutes} phút"
```

---

## 🎮 **User Experience**

### **Strategic Planning**
```
Scenario: User có 3 maids
- Rem (Growth Speed +30%) - For farming
- Asuna (Seed Discount +25%) - For shopping  
- Zero Two (Yield Boost +35%) - For harvesting

Decision: Chọn maid nào để maximize efficiency?
```

### **Workflow Optimization**
```
Best Practice:
1. Plan ahead: Xem schedule farming/shopping
2. Choose optimal maid: Dựa trên activity chính
3. Use cooldown time: Farm/shop/harvest effectively
4. Check f!mcooldown: Trước khi có plan mới
```

### **Common Scenarios**

#### **Farming Day (8-10 hours)**
```
Choice: Growth Speed maid
Reason: Giảm thời gian grow crops
Duration: Perfect cho 10-hour cooldown
```

#### **Shopping Spree**
```
Choice: Seed Discount maid  
Reason: Tiết kiệm coins khi mua seeds
Plan: Mua seeds cho vài ngày
```

#### **Harvest Season**
```
Choice: Yield Boost maid
Reason: Maximize crops từ harvest
Timing: Khi có nhiều crops ready
```

---

## 🚀 **Benefits**

### **For Game Balance**
- ✅ **Prevents abuse**: Không thể switch maid constantly
- ✅ **Strategic depth**: Phải plan ahead
- ✅ **Resource management**: Maid choice becomes important

### **For User Experience**  
- ✅ **Clear feedback**: Hiển thị time remaining rõ ràng
- ✅ **Helpful tips**: Guidance về cách optimize
- ✅ **Fair system**: Áp dụng cho tất cả users

### **For Technical Stability**
- ✅ **Reduced database calls**: Ít thay đổi maid
- ✅ **Cleaner logs**: Ít spam equip operations
- ✅ **Better performance**: Stable maid assignments

---

## 📊 **Implementation Notes**

### **Database Considerations**
- Primary key trên user_id (1 cooldown per user)
- Store both timestamps để debug/admin
- Auto-cleanup old records có thể implement sau

### **Edge Cases Handled**
- ✅ First-time equip: No cooldown restriction
- ✅ Cooldown expired: Auto-allow equip
- ✅ Database error: Graceful fallback
- ✅ Time calculation: Accurate to minutes

### **Future Enhancements**
- 🔮 Premium users: Reduced cooldown (5 hours)
- 🔮 Special events: Temporary cooldown reduction
- 🔮 Admin commands: Force reset cooldown
- 🔮 Analytics: Track equip patterns

---

## 🎯 **Usage Examples**

### **Normal Flow**
```bash
# Check current status
f!mcooldown
> ✅ Sẵn sàng equip!

# Equip new maid
f!mequip abc12345
> ✅ Trang bị thành công! 
> ⏰ Cooldown: 10 giờ

# Try to equip again immediately
f!mequip def67890
> ⏰ Cooldown: 9 giờ 59 phút

# Check status after some time
f!mcooldown  
> ⏰ Đang trong cooldown: 7 giờ 30 phút
```

### **Planning Workflow**
```bash
# Morning: Plan for day
f!mcooldown
> Ready → Choose farming maid

f!mequip farm_maid_id
> Success → Farm for day

# Evening: Still in cooldown
f!mcooldown  
> 2 giờ 15 phút → Wait or continue farming

# Next morning: Ready again
f!mcooldown
> Ready → Switch to shopping maid
```

---

**✅ Hệ thống Maid Equip Cooldown đã được implement thành công với đầy đủ tính năng bảo vệ, user feedback và strategic depth!** 🎯 