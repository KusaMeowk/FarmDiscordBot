# 🌱 HƯỚNG DẪN TRỒNG CÂY HÀNG LOẠT

## 🎯 Tính năng mới: Bulk Planting

Lệnh `f!plant` đã được nâng cấp để hỗ trợ trồng nhiều ô cùng lúc!

## 📖 Cách sử dụng

### 1. Trồng ô đơn lẻ (như cũ)
```
f!plant carrot 1
f!plant tomato 3
f!plant wheat 5
```

### 2. Trồng nhiều ô cụ thể
```
f!plant carrot 1,2,3,4
f!plant tomato 1,3,5,7
f!plant corn 2,4,6
f!plant wheat 1,2,3,4,5,6,7,8
```

### 3. Trồng tất cả ô trống
```
f!plant carrot all
f!plant tomato all
f!plant wheat all
```

## 🎮 Ví dụ thực tế

### Scenario 1: Setup nông trại mới
```bash
# Mua hạt giống trước
f!buy carrot_seed 10
f!buy tomato_seed 5

# Trồng toàn bộ nông trại với cà rót
f!plant carrot all

# Sau khi thu hoạch, trồng cà chua ở một số ô
f!plant tomato 1,3,5
```

### Scenario 2: Farming hiệu quả
```bash
# Mua đủ hạt cho tất cả ô
f!buy wheat_seed 8

# Trồng tất cả ô bằng lúa mì (lợi nhuận cao)
f!plant wheat all

# Thu hoạch tất cả sau 30 phút
f!harvest all

# Repeat cycle
f!plant wheat all
```

### Scenario 3: Mixed farming
```bash
# Trồng cà rót ở ô lẻ
f!plant carrot 1,3,5,7

# Trồng cà chua ở ô chẵn  
f!plant tomato 2,4,6,8

# Harvesting theo từng loại
f!harvest 1,3,5,7    # Thu hoạch cà rót
f!harvest 2,4,6,8    # Thu hoạch cà chua
```

## ✨ Tính năng thông minh

### ✅ Validation tự động
- Kiểm tra ô đất có trống không
- Kiểm tra đủ hạt giống không
- Báo lỗi rõ ràng nếu có vấn đề

### ✅ Batch processing
- Trồng nhiều ô trong 1 lệnh
- Tiết kiệm thời gian và clicks
- Xử lý lỗi graceful

### ✅ Smart feedback
- Hiển thị số ô đã trồng
- Hiển thị hạt giống còn lại
- Tips sử dụng phù hợp

## 🎯 Lợi ích

### ⚡ Hiệu quả
- **Trước**: `f!plant carrot 1` → `f!plant carrot 2` → `f!plant carrot 3` → `f!plant carrot 4`
- **Sau**: `f!plant carrot 1,2,3,4` hoặc `f!plant carrot all`

### 🧠 Thông minh
- Tự động skip ô đã có cây
- Kiểm tra hạt giống trước khi trồng
- Feedback chi tiết về kết quả

### 🎮 User-friendly
- Nhiều cách sử dụng linh hoạt
- Error messages rõ ràng
- Tips hướng dẫn trong embed

## 🔗 Kết hợp với các lệnh khác

### Workflow hoàn chỉnh
```bash
# 1. Xem nông trại hiện tại
f!farm

# 2. Mua hạt giống cần thiết
f!shop
f!buy carrot_seed 8

# 3. Trồng hàng loạt
f!plant carrot all

# 4. Đợi cây chín và thu hoạch
f!harvest all

# 5. Bán nông sản
f!market              # Xem giá
f!sell carrot 20      # Bán với giá tốt
```

### Power user tips
```bash
# Combo hiệu quả: Trồng - Thu hoạch - Trồng tiếp
f!plant wheat all
# Đợi 30 phút...
f!harvest all
f!sell wheat all
f!plant wheat all

# Mixed strategy: Diversify risks
f!plant carrot 1,2,3,4    # Fast crops (5 min)
f!plant wheat 5,6,7,8     # Slow crops (30 min) 
```

## 🎉 Kết luận

Tính năng bulk planting giúp:
- ⚡ **Tiết kiệm thời gian** đáng kể
- 🎯 **Tăng hiệu quả** farming
- 🧠 **Chiến lược** linh hoạt hơn
- 🎮 **Trải nghiệm** mượt mà hơn

**Happy farming!** 🌾💰 