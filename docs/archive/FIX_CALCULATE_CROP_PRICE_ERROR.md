# Sửa Lỗi: "calculate_crop_price is not defined"

## 🐛 Mô Tả Lỗi

**Vị trí:** `features/weather.py` - Dòng 924, 925
```
"calculate_crop_price" is not defined Pylance(reportUndefinedVariable)
```

**Nguyên nhân:** Function `calculate_crop_price` được sử dụng trong `market_notification_task()` nhưng không được import đúng cách.

## 🔍 Phân Tích Root Cause

### Import Pattern Sai
```python
# Trong market_notification_task():
for notification in notifications:
    # Calculate current market modifier
    from utils.helpers import calculate_crop_price  # ❌ Import inside function
```

### Vấn đề:
1. **Late Import**: Import bên trong function có thể gây lỗi và không theo best practice
2. **Missing Global Import**: Function đã có sẵn trong `utils.helpers` nhưng không được import ở đầu file
3. **Inconsistent**: Các helper functions khác đã được import ở đầu file

## ✅ Giải Pháp Đã Áp Dụng

### 1. Thêm Import Ở Đầu File
```python
# OLD:
from utils.helpers import get_weather_from_description

# NEW:
from utils.helpers import get_weather_from_description, calculate_crop_price
```

### 2. Xóa Import Bên Trong Function
```python
# OLD:
for notification in notifications:
    # Calculate current market modifier
    from utils.helpers import calculate_crop_price  # ❌
    
    # Get weather modifier

# NEW:
for notification in notifications:
    # Calculate current market modifier
    
    # Get weather modifier
```

## 🔧 Technical Details

### Function Đã Có Sẵn
`calculate_crop_price` đã được implement trong `utils/helpers.py`:
```python
def calculate_crop_price(crop_type: str, weather_modifier: float = 1.0) -> int:
    """Calculate crop selling price with weather effects"""
    crop_config = config.CROPS.get(crop_type, {})
    base_price = crop_config.get('sell_price', 10)
    
    # Weather can affect price slightly
    price_modifier = 0.8 + (weather_modifier * 0.4)  # Range: 0.8 - 1.2
    final_price = int(base_price * price_modifier)
    
    return max(1, final_price)
```

### Cách Sử Dụng Trong Weather.py
Function được dùng trong `_create_market_change_notification()`:
```python
for crop_id in sample_crops:
    if crop_id in config.CROPS:
        crop_config = config.CROPS[crop_id]
        old_price = calculate_crop_price(crop_id, old_modifier)
        new_price = calculate_crop_price(crop_id, new_modifier)
        # ...
```

## 🧪 Testing & Verification

### 1. Syntax Check
```bash
python -m py_compile features/weather.py
# ✅ No errors
```

### 2. Bot Startup
```bash
python bot.py
# ✅ No "calculate_crop_price is not defined" errors
# ✅ All extensions load successfully
```

### 3. Import Verification
- `calculate_crop_price` giờ đã available globally trong `weather.py`
- Function hoạt động bình thường trong market notifications
- Không còn runtime errors

## 📋 Best Practices Implemented

1. **Consistent Imports**: Tất cả helper functions được import ở đầu file
2. **Early Import**: Import functions khi module load, không phải runtime
3. **Clean Code**: Loại bỏ redundant imports bên trong functions
4. **Maintainable**: Dễ track dependencies và debug

## 🔄 Impact & Benefits

### ✅ Đã Sửa:
- Lỗi Pylance/IDE warnings
- Runtime errors khi market notifications trigger
- Code consistency và readability

### 📈 Improved:
- Import pattern theo Python best practices
- Module load performance (import một lần)
- Code maintainability

### 🛡️ Risk Mitigation:
- Không breaking changes
- Backward compatible
- Function behavior không thay đổi

## 📝 Summary

**Lỗi đơn giản:** Import function chưa đúng cách
**Giải pháp nhanh:** Thêm vào import statement đầu file
**Kết quả:** Bot hoạt động bình thường, không còn errors

Đây là lỗi import pattern phổ biến, dễ sửa và không ảnh hưởng đến functionality của bot. 