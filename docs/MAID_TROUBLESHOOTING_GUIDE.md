# 🚨 Maid System Troubleshooting Guide

## Vấn đề: "Thiếu tham số" khi dùng `f2!mg`

### ✅ Xác nhận Commands hoạt động
Commands đã được kiểm tra và hoạt động bình thường:
- ✅ `maid_gacha`: aliases=['mg'] 
- ✅ `maid_collection`: aliases=['mc']
- ✅ `maid_active`: aliases=['ma']

---

## 🔍 Nguyên nhân có thể

### 1. **CHƯA ĐĂNG KÝ** (Nguyên nhân phổ biến nhất)
Maid system yêu cầu phải đăng ký tài khoản trước.

**Kiểm tra**: Sử dụng `f2!profile` để xem có tài khoản không

**Giải pháp**: 
```bash
f2!register    # Đăng ký tài khoản mới
```

### 2. **BOT CHƯA RESTART** 
Sau khi cập nhật PREFIX, bot cần restart để load config mới.

**Kiểm tra**: Sử dụng `f2!help` để xem có hoạt động không

**Giải pháp**: Restart bot hoặc đợi admin restart

### 3. **CONFLICT VỚI CÁC COMMAND KHÁC**
Có thể `mg` bị conflict với command khác.

**Kiểm tra**: Thử lệnh đầy đủ `f2!maid_gacha`

**Giải pháp**: Sử dụng lệnh đầy đủ thay vì shortcut

---

## 🛠️ Các bước kiểm tra tuần tự

### Bước 1: Kiểm tra đăng ký
```bash
f2!profile
```
**Kết quả mong đợi**: Hiển thị thông tin tài khoản và tiền  
**Nếu lỗi**: `f2!register` để đăng ký

### Bước 2: Kiểm tra tiền
```bash
f2!profile
```
**Yêu cầu**: Ít nhất 10,000 coins để roll gacha  
**Nếu thiếu**: `f2!daily` để nhận tiền hàng ngày

### Bước 3: Test lệnh đầy đủ
```bash
f2!maid_gacha
```
**Kết quả mong đợi**: Roll gacha thành công  
**Nếu hoạt động**: Shortcut `f2!mg` cũng sẽ hoạt động

### Bước 4: Test shortcut
```bash
f2!mg
```
**Kết quả mong đợi**: Tương tự `f2!maid_gacha`

---

## 📊 Commands khả dụng

### ✅ Commands đã verified hoạt động:
- `f2!maid_gacha` / `f2!mg` - Roll gacha 1 lần
- `f2!maid_collection` / `f2!mc` - Xem collection
- `f2!maid_active` / `f2!ma` - Xem maid active

### 🔄 Commands cần test:
- `f2!maid_gacha10` - Roll 10 lần (90k coins)
- `f2!maid_equip <id>` - Trang bị maid
- `f2!maid_info <id>` - Chi tiết maid

---

## 🎯 Hướng dẫn bắt đầu (Step by Step)

### Lần đầu sử dụng Maid System:

**1. Đăng ký tài khoản**
```bash
f2!register
```

**2. Kiểm tra tiền**
```bash
f2!profile
```

**3. Nhận daily để có tiền**
```bash
f2!daily
```

**4. Roll gacha đầu tiên**
```bash
f2!mg
# hoặc f2!maid_gacha
```

**5. Xem maid đã có**
```bash
f2!mc
# hoặc f2!maid_collection
```

**6. Trang bị maid**
```bash
f2!maid_equip <8_ký_tự_đầu_ID>
```

**7. Kiểm tra maid active**
```bash
f2!ma
# hoặc f2!maid_active
```

---

## 🚨 Error Messages & Solutions

### "❌ Thiếu tham số. Sử dụng f2!help để xem hướng dẫn."
- **Nguyên nhân**: Command không nhận diện được hoặc missing registration
- **Giải pháp**: Đăng ký với `f2!register` và thử lại

### "❌ Bạn chưa đăng ký! Dùng lệnh farm để bắt đầu."
- **Nguyên nhân**: Chưa có tài khoản trong database
- **Giải pháp**: `f2!register`

### "❌ Không đủ tiền! Cần 10,000 coins"
- **Nguyên nhân**: Không đủ tiền roll gacha
- **Giải pháp**: `f2!daily`, `f2!farm`, hoặc `f2!sell`

### "⏰ Vui lòng đợi X.Xs trước khi roll tiếp!"
- **Nguyên nhân**: Cooldown system (3 giây giữa các roll)
- **Giải pháp**: Đợi cooldown hết

---

## 🔧 Advanced Troubleshooting

### Nếu tất cả bước trên vẫn không hoạt động:

**1. Kiểm tra bot permissions**
- Bot cần quyền Send Messages
- Bot cần quyền Use Slash Commands

**2. Thử slash commands**
```bash
/maid_gacha    # Thay vì f2!mg
```

**3. Kiểm tra logs**
- Admin có thể check bot logs để tìm lỗi cụ thể

**4. Force reload**
- Admin có thể reload maid cog: `f2!admin reload features.maid`

---

## ✅ Verification Checklist

Để đảm bảo maid system hoạt động:

- [ ] Đã đăng ký tài khoản (`f2!register`)
- [ ] Có ít nhất 10,000 coins
- [ ] Bot đã restart sau khi update PREFIX
- [ ] Lệnh `f2!help` hoạt động bình thường
- [ ] Không có conflict với commands khác
- [ ] Bot có đủ permissions trong channel

---

**📞 Nếu vẫn gặp vấn đề sau khi làm theo hướng dẫn này, vui lòng liên hệ admin với thông tin:**
- Lệnh đã thử
- Error message chính xác
- Kết quả của `f2!profile`
- Có đã thử `f2!register` chưa 