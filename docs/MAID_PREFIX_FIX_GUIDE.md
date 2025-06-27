# 🚨 HOTFIX: Maid System PREFIX Fix Guide

## Vấn đề đã giải quyết
✅ **Lỗi "Thiếu tham số" với maid commands**  
✅ **Cập nhật PREFIX từ `f!` → `f2!`**  
✅ **Maid system hoạt động bình thường**

---

## 🔧 Thay đổi đã thực hiện

### 1. PREFIX Update
- **File**: `config.py`
- **Thay đổi**: `PREFIX = os.getenv('PREFIX', 'f2!')`
- **Kết quả**: Tất cả commands giờ sử dụng `f2!` thay vì `f!`

### 2. Dynamic Error Messages
- **File**: `bot.py` 
- **Thay đổi**: Error message sử dụng `{config.PREFIX}` thay vì hardcoded `f!`
- **Kết quả**: Thông báo lỗi hiển thị đúng prefix `f2!help`

### 3. Help System Update
- **File**: `features/help_system.py`
- **Thay đổi**: Documentation đã cập nhật để sử dụng `f2!`
- **Kết quả**: `f2!help` hiển thị đúng hướng dẫn

---

## 🎀 Cách sử dụng Maid System

### ⚡ Lệnh cơ bản (Quick Start)
```bash
f2!maid_gacha         # Roll gacha 1 lần (10,000 coins)
f2!mg                 # Shortcut cho maid_gacha

f2!maid_collection    # Xem collection maid của bạn  
f2!mc                 # Shortcut cho collection

f2!maid_equip <id>    # Trang bị maid (8 ký tự đầu của ID)
f2!me <id>            # Shortcut cho equip

f2!maid_active        # Xem maid đang active và buffs
f2!ma                 # Shortcut cho active
```

### 🎰 Gacha System
```bash
f2!maid_gacha         # Roll 1 lần (10,000 coins)
f2!maid_gacha10       # Roll 10 lần (90,000 coins - giảm 10%)
f2!maid_pity          # Xem tỷ lệ gacha rates
f2!maid_stats         # Xem thống kê gacha của bạn
```

### 📚 Collection Management
```bash
f2!maid_collection [page]    # Xem collection (có pagination)
f2!maid_info <id>           # Xem chi tiết maid
f2!maid_equip <id>          # Trang bị maid
f2!maid_active              # Xem maid đang active
f2!maid_rename <id> <name>  # Đổi tên maid
```

### 🔍 Database & Discovery
```bash
f2!maid_database <search>   # Tìm kiếm maid trong database
f2!maid_list [rarity]       # Danh sách maids theo rarity (UR/SSR/SR/R)
```

### ⭐ Advanced Features
```bash
f2!maid_stardust           # Xem số bụi sao hiện có
f2!maid_dismantle <id>     # Tách maid thành bụi sao
f2!maid_reroll <id>        # Reroll buffs của maid
f2!maid_reroll_cost <id>   # Xem chi phí reroll
```

---

## 🎯 Shortcuts (Viết tắt)

| Lệnh đầy đủ | Shortcut | Mô tả |
|------------|----------|-------|
| `f2!maid_gacha` | `f2!mg` | Roll gacha 1 lần |
| `f2!maid_gacha10` | `f2!mg10` | Roll gacha 10 lần |
| `f2!maid_collection` | `f2!mc` | Xem collection |
| `f2!maid_equip` | `f2!me` | Trang bị maid |
| `f2!maid_active` | `f2!ma` | Xem maid active |

---

## 🚀 Ví dụ sử dụng

### Scenario 1: Bắt đầu với Maid System
```bash
# 1. Kiểm tra tiền
f2!profile

# 2. Roll gacha lần đầu
f2!maid_gacha
# hoặc dùng shortcut: f2!mg

# 3. Xem collection
f2!maid_collection
# hoặc: f2!mc

# 4. Trang bị maid đầu tiên
f2!maid_equip 12ab34cd
# hoặc: f2!me 12ab34cd

# 5. Kiểm tra maid active
f2!maid_active
# hoặc: f2!ma
```

### Scenario 2: Quản lý Collection
```bash
# Xem tất cả maids
f2!maid_list

# Xem chỉ UR maids
f2!maid_list UR

# Tìm kiếm maid cụ thể
f2!maid_database asuka

# Xem chi tiết maid
f2!maid_info 12ab34cd
```

### Scenario 3: Advanced Operations
```bash
# Kiểm tra stardust
f2!maid_stardust

# Tách maid không cần
f2!maid_dismantle 12ab34cd

# Reroll buffs
f2!maid_reroll 12ab34cd

# Đổi tên maid
f2!maid_rename 12ab34cd "Waifu của tôi"
```

---

## 🔧 Environment Setup (Nếu cần)

Nếu bạn muốn tùy chỉnh PREFIX, tạo file `.env`:

```env
# Discord Bot Configuration
DISCORD_TOKEN=your_discord_bot_token_here
PREFIX=f2!
OWNER_ID=your_discord_user_id_here

# Database Configuration  
DATABASE_PATH=farm_bot.db
```

---

## ✅ Verification Checklist

- [x] Bot sử dụng prefix `f2!` thay vì `f!`
- [x] Error messages hiển thị `f2!help` đúng
- [x] Maid commands hoạt động với `f2!maid_*`
- [x] Shortcuts hoạt động (`f2!mg`, `f2!mc`, etc.)
- [x] Help system cập nhật prefix mới
- [x] Tất cả text commands tương thích

---

## 🆘 Troubleshooting

### "Command not found"
- **Nguyên nhân**: Đang dùng prefix cũ `f!`
- **Giải pháp**: Sử dụng `f2!` thay vì `f!`

### "Thiếu tham số" 
- **Nguyên nhân**: Command cần thêm tham số
- **Giải pháp**: Sử dụng `f2!help <command>` để xem hướng dẫn

### Maid command không hoạt động
- **Kiểm tra**: Đảm bảo đã register với `f2!register`
- **Kiểm tra**: Có đủ tiền để roll gacha (10,000 coins)
- **Thử**: Slash commands `/maid_gacha` nếu text commands có vấn đề

---

**🎉 Maid System đã sẵn sàng với PREFIX mới `f2!`!** 