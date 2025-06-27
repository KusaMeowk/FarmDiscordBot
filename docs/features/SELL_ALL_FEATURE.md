# 💰 Tính Năng Bán Tất Cả (Sell All)

## 📝 Tổng Quan

Tính năng mới **Sell All** cho phép người chơi bán toàn bộ nông sản cùng loại trong inventory chỉ với một lệnh duy nhất, tiết kiệm thời gian và thuận tiện hơn.

## 🎯 Cách Sử Dụng

### Lệnh Cơ Bản
```
f!sell <loại_cây> all
```

### Ví Dụ Thực Tế
```bash
# Bán toàn bộ cà rót
f!sell carrot all

# Bán toàn bộ cà chua  
f!sell tomato all

# Bán toàn bộ lúa mì
f!sell wheat all

# Bán toàn bộ ngô
f!sell corn all
```

### So Sánh Với Lệnh Cũ
```bash
# Cách cũ - phải biết số lượng chính xác
f!sell carrot 25

# Cách mới - tự động bán hết
f!sell carrot all
```

## ✨ Tính Năng

### 🎯 Tự Động Phát Hiện Số Lượng
- Bot tự động tìm số lượng nông sản có sẵn trong inventory
- Không cần biết chính xác có bao nhiêu để bán

### 📊 Thông Báo Chi Tiết
Khi bán thành công, bot sẽ hiển thị:
- Số lượng đã bán (với chú thích "toàn bộ" nếu bán hết)
- Giá bán per unit với weather bonuses
- Tổng tiền thu được
- Số dư mới

### 🛡️ Xử Lý Lỗi Thông Minh
- Thông báo rõ ràng nếu không có nông sản để bán
- Hỗ trợ cả chữ thường và chữ hoa: `all`, `ALL`, `All`

## 🔧 Tương Thích

### Aliases Hỗ Trợ
```bash
f!sell carrot all    # Lệnh chính
f!ban carrot all     # Alias tiếng Việt
```

### Từ Khóa Hỗ Trợ
- `all` - Bán toàn bộ (khuyến nghị)
- `ALL` - Cũng hoạt động
- `All` - Cũng hoạt động

### Backward Compatibility
Lệnh cũ vẫn hoạt động bình thường:
```bash
f!sell carrot 5      # Vẫn bán được 5 cà rót
f!sell tomato 10     # Vẫn bán được 10 cà chua
```

## 🎨 UI/UX Improvements

### Thông Báo Thành Công
```
💰 Bán thành công!
Đã bán 25 🥕 Cà rót (toàn bộ)

💱 Chi tiết giá
💵 Giá bán: 20 coins/cây
📊 Giá gốc: 18 coins/cây  
📈 Bonus: +11.1%

⚡ Phân Tích Giá
🌤️ Thời tiết tốt: +10%
📈 Xu hướng thị trường: +5%

💰 Kết quả
Tổng thu: 500 coins
Số dư mới: 1,250 coins
```

### Hướng Dẫn Cập Nhật
Tất cả UI hints đã được cập nhật:
- Farm command: `f!sell <loại_cây> <số_lượng>` hoặc `f!sell <loại_cây> all`
- Market footers: Bao gồm cả `f!sell <cây> all` option
- Weather embeds: Hướng dẫn sell all trong footer

## 🚀 Lợi Ích

### Cho Người Chơi
1. **Tiết Kiệm Thời Gian**: Không cần đếm inventory
2. **Thuận Tiện**: Một lệnh bán hết
3. **Ít Lỗi**: Không lo nhập sai số lượng
4. **Hiệu Quả**: Đặc biệt hữu ích với inventory lớn

### Cho Game Experience
1. **User-Friendly**: Giảm friction trong gameplay
2. **Quality of Life**: Improvement đáng kể
3. **Competitive**: Tăng tốc độ trading
4. **Professional**: Bot cảm thấy polished hơn

## 🔍 Technical Details

### Implementation
- Modified `FarmCog.sell()` method để accept `quantity` parameter linh hoạt
- Special flag `quantity = -1` để handle "all" logic
- Backward compatible với existing commands

### Error Handling
```python
# Handle "all" keyword
if isinstance(quantity, str) and quantity.lower() == "all":
    quantity = -1  # Special flag for "all"
elif isinstance(quantity, str):
    try:
        quantity = int(quantity)
    except ValueError:
        await ctx.send("❌ Số lượng phải là số hoặc 'all'!")
        return
```

### Database Impact
- Không thay đổi database schema
- Sử dụng existing `use_item()` và `update_user()` methods
- Hoàn toàn backward compatible

## 📚 Examples

### Scenario: Thu Hoạch Và Bán Hết
```bash
# 1. Thu hoạch tất cả
f!harvest all

# 2. Kiểm tra inventory  
f!farm

# 3. Bán toàn bộ từng loại
f!sell carrot all
f!sell tomato all  
f!sell wheat all
f!sell corn all
```

### Scenario: Quick Cash
```bash
# Bán nhanh toàn bộ cà rót để có tiền mua hạt giống
f!sell carrot all

# Mua hạt giống mới
f!buy tomato 10
```

## 🎯 Kết Luận

Tính năng **Sell All** là một quality-of-life improvement quan trọng, giúp game trở nên user-friendly và professional hơn. Nó giữ được tính đơn giản của syntax hiện tại trong khi thêm convenience cho power users.

**Command Summary:**
- `f!sell <crop> <number>` - Bán số lượng cụ thể
- `f!sell <crop> all` - Bán toàn bộ loại cây đó
- Aliases: `f!ban` cũng hoạt động tương tự

🎉 **Happy farming and trading!** 🎉 