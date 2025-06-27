# Farm Pagination System Implementation

## 📋 Tổng Quan

Hệ thống phân trang nông trại được triển khai để hiển thị tất cả các ô đất của người chơi thông qua các trang với navigation buttons, thay vì giới hạn chỉ hiển thị 5 ô đầu tiên.

## 🎯 Vấn Đề Được Giải Quyết

**Trước khi có pagination:**
- Chỉ hiển thị được 5 ô đất đầu tiên
- Người chơi có 8+ ô đất không thể xem hết
- Không có cách nào để xem các ô đất phía sau

**Sau khi có pagination:**
- Hiển thị 8 ô đất mỗi trang (2 hàng x 4 cột)
- Navigation với nút ◀️ ▶️ để chuyển trang
- Hiển thị đầy đủ thông tin về trang hiện tại
- User experience tốt hơn với visual improvements

## 🛠️ Technical Implementation

### 1. **FarmView Updates** (`features/farm.py`)

#### New Properties
```python
class FarmView(discord.ui.View):
    def __init__(self, bot, user_id, page=0):
        self.current_page = page
        self.plots_per_page = 8  # 8 ô đất mỗi trang
```

#### Navigation Buttons
```python
@discord.ui.button(label="◀️", style=discord.ButtonStyle.grey)
async def previous_page(self, interaction, button):
    # Logic chuyển về trang trước
    
@discord.ui.button(label="▶️", style=discord.ButtonStyle.grey)  
async def next_page(self, interaction, button):
    # Logic chuyển đến trang sau
```

#### Smart Button States
- Nút ◀️ bị disabled khi ở trang đầu tiên
- Nút ▶️ bị disabled khi ở trang cuối cùng
- Auto-update states khi chuyển trang

### 2. **Paginated Embed Creation** (`utils/embeds.py`)

#### New Method: `create_farm_embed_paginated()`
```python
def create_farm_embed_paginated(user, crops, page=0, plots_per_page=8):
    # Calculate page boundaries
    start_plot = page * plots_per_page
    end_plot = min(start_plot + plots_per_page, user.land_slots)
    
    # Create page-specific grid
    # Show only crops for current page
    # Add navigation info
```

#### Enhanced Visual Display
- **Grid Layout**: 2 hàng x 4 cột mỗi trang
- **Plot Numbers**: Hiển thị số thứ tự ô đất chính xác
- **Symbols**: 
  - ⬜ = Ô trống
  - 🌱 = Cây non (< 33% thời gian)
  - 🌿 = Cây phát triển (33-66% thời gian)  
  - 🌾 = Cây gần chín (66-100% thời gian)
  - ✨ = Sẵn sàng thu hoạch

#### Page Information
```
🌾 Nông trại của {username}
Trang 1/3 • Ô 1-8/20
```

### 3. **Enhanced Farm Command** (`features/farm.py`)

#### New Syntax
```python
@commands.command(name='farm')
async def farm(self, ctx, page: int = 1):
    # Optional page parameter
    # Auto-validation và clamping
    # Set button states correctly
```

#### Page Validation
- Clamp page number giữa 1 và max_pages
- Convert 1-based input thành 0-based internal index
- Handle edge cases gracefully

## 📊 Pagination Logic

### Page Calculations
```python
# Với 20 ô đất và 8 ô/trang:
total_pages = (20 - 1) // 8 + 1  # = 3 trang
# Trang 0: ô 0-7   (hiển thị 1-8)
# Trang 1: ô 8-15  (hiển thị 9-16) 
# Trang 2: ô 16-19 (hiển thị 17-20)
```

### Button State Logic
```python
prev_disabled = (current_page == 0)
next_disabled = (current_page >= max_pages - 1)
```

## 🎮 User Experience Flow

### Initial Load
1. User gõ `f!farm` hoặc `f!farm 2`
2. Validate page number
3. Create paginated embed cho trang được yêu cầu
4. Set button states appropriately
5. Display với navigation buttons

### Navigation
1. User click ◀️ hoặc ▶️
2. Check if navigation is valid
3. Update current_page
4. Refresh embed với data mới
5. Update button states
6. Maintain interaction context

### Visual Feedback
- Disabled buttons cho invalid navigation
- Clear page indicators trong embed title
- Range information (Ô 1-8/20)
- Navigation instructions khi có nhiều trang

## 🎯 Benefits Achieved

### User Experience
- **Complete Visibility**: Xem được tất cả ô đất
- **Intuitive Navigation**: Nút mũi tên quen thuộc
- **Clear Information**: Biết rõ đang ở trang nào
- **Mobile Friendly**: Hoạt động tốt trên điện thoại

### Technical Benefits  
- **Scalable**: Hỗ trợ unlimited số ô đất
- **Performance**: Chỉ load data cần thiết mỗi trang
- **Maintainable**: Code organization tốt
- **Extensible**: Dễ dàng thêm features mới

### Backward Compatibility
- ✅ Lệnh `f!farm` cũ vẫn hoạt động (mặc định trang 1)
- ✅ Tất cả buttons cũ vẫn hoạt động bình thường
- ✅ Harvest all button hoạt động trên tất cả ô đất
- ✅ Không breaking changes với existing users

## 📚 Usage Examples

### Basic Usage
```
f!farm           # Xem trang 1
f!farm 2         # Xem trang 2 trực tiếp
```

### Navigation trong Discord
1. Gõ `f!farm` để mở nông trại
2. Click ▶️ để chuyển sang trang sau
3. Click ◀️ để quay lại trang trước
4. Click 🔄 để refresh trang hiện tại
5. Click ✨ để thu hoạch tất cả (all pages)

### Visual Example
```
🌾 Nông trại của NTR
Trang 1/3 • Ô 1-8/20

🗺️ Bản đồ nông trại
✨  🌾  ⬜  🌱
 1   2   3   4 

🌿  ⬜  ✨  🌱  
 5   6   7   8

🌱 Trạng thái cây trồng
Ô 1: Cà rốt - ✅ Có thể thu hoạch
Ô 2: Cà chua - ⏰ 2p 30s
Ô 4: Khoai tây - ⏰ 5p 15s

📊 Tổng quan       💰 Số dư
Tổng cây: 12/20    15,350 coins
Sẵn sàng: 3

🔄 Điều hướng
Sử dụng các nút ◀️ ▶️ để xem tất cả 20 ô đất

[◀️] [🔄 Cập nhật] [▶️] [🌱 Trồng cây] [✨ Thu hoạch tất cả]
```

## 🧪 Testing

### Test Cases Covered
- ✅ User với ít hơn 8 ô đất (1 trang)
- ✅ User với đúng 8 ô đất (1 trang)  
- ✅ User với 9-16 ô đất (2 trang)
- ✅ User với 20+ ô đất (3+ trang)
- ✅ Navigation boundaries (first/last page)
- ✅ Button state management
- ✅ Page parameter validation
- ✅ Harvest all functionality across pages

### Edge Cases Handled
- Invalid page numbers → Auto-clamp
- Empty farms → Graceful display
- Single page farms → Hide navigation
- Button spam → Proper error messages
- Interaction timeouts → Handled by Discord

## 🎉 Status: ✅ HOÀN THÀNH

Farm Pagination System đã được triển khai đầy đủ với:
- ✅ Navigation buttons hoạt động hoàn hảo
- ✅ Visual improvements đáng kể
- ✅ Backward compatibility 100%
- ✅ User experience tối ưu
- ✅ Scalable architecture
- ✅ Comprehensive testing

Người chơi giờ đây có thể xem và quản lý tất cả các ô đất của mình một cách dễ dàng và trực quan! 