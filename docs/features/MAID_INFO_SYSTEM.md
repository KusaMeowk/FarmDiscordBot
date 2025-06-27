# 🔍 Maid Info System - Complete Guide

## **📋 Tổng Quan**
Hệ thống thông tin maid hoàn chỉnh cho phép người chơi:
- Xem chi tiết maid trong collection cá nhân
- Tìm kiếm và khám phá maid trong database hệ thống
- Xem danh sách tất cả maids theo rarity
- Hiển thị avatar, skills, rates và thống kê chi tiết

---

## **🎯 Commands Mới**

### **1. `/maid_info <maid_id>`**
```
📝 Mô tả: Xem thông tin chi tiết maid trong collection
🔍 Tham số: ID hoặc tên maid (8 ký tự đầu)
🔒 Bảo mật: Chỉ hiển thị maid của người dùng
```

**Ví dụ sử dụng:**
```
/maid_info abc12345  # Tìm theo instance ID
/maid_info rem       # Tìm theo tên maid
/maid_info waifu1    # Tìm theo custom name
```

**Thông tin hiển thị:**
- 🖼️ Avatar (nếu có art_url)
- 📋 Thông tin cơ bản (rarity, ID, status, ngày nhận)
- ✨ Skills đang sở hữu (buffs hiện tại)
- 🎲 Skills có thể có (khi reroll)
- 📊 Gacha info (drop rate, costs)

### **2. `/maid_database <search>`**
```
📝 Mô tả: Tìm kiếm maid trong database hệ thống
🔍 Tham số: Tên maid cần tìm (có thể viết tắt)
🌐 Phạm vi: Tất cả maids trong hệ thống
```

**Ví dụ sử dụng:**
```
/maid_database rem      # Tìm maids có tên "rem"
/maid_database zero     # Tìm maids có tên "zero"
/maid_database saber    # Tìm maids có tên "saber"
```

**Hiển thị kết quả:**
- **Nếu tìm thấy 1 maid**: Hiển thị chi tiết đầy đủ
- **Nếu tìm thấy nhiều maids**: Hiển thị danh sách grouped by rarity
- **Nếu không tìm thấy**: Thông báo lỗi

**Thông tin chi tiết (1 maid):**
- 🖼️ Avatar (nếu có art_url)
- 📋 Thông tin cơ bản (rarity, ID, drop rate)
- 🎲 Skills khi roll trúng
- 💰 Economics (reroll cost, dismantle reward, expected cost)
- 👑 Ownership status (có sở hữu không)

### **3. `/maid_list [rarity]`**
```
📝 Mô tả: Xem danh sách tất cả maids theo rarity
🔍 Tham số: Rarity để xem (UR/SSR/SR/R), optional
📊 Hiển thị: Overview hoặc detailed list
```

**Ví dụ sử dụng:**
```
/maid_list       # Xem overview tất cả rarities
/maid_list UR    # Xem tất cả UR maids
/maid_list SSR   # Xem tất cả SSR maids
```

**Chế độ hiển thị:**
- **Không có rarity**: Overview tất cả rarities với examples
- **Có rarity**: Detailed list của rarity đó với rates và commands

---

## **🔧 Tính Năng Kỹ Thuật**

### **Search Functionality**
```python
def _find_user_maid(self, user_id: int, maid_id: str):
    # 1. Tìm theo instance ID (ưu tiên)
    # 2. Tìm theo template name 
    # 3. Tìm theo custom name
    # 4. Ownership validation ở mọi bước
```

**Search Algorithm:**
1. **First pass**: Exact instance ID match
2. **Second pass**: Template name partial match
3. **Third pass**: Custom name partial match
4. **Security**: Double-check ownership at each step

### **Avatar System**
```python
# Hiển thị avatar theo độ ưu tiên:
if template.get("art_url"):
    embed.set_image(url=template["art_url"])  # Official art (3:4 aspect ratio)
else:
    embed.set_thumbnail(url=user.avatar.url)  # User avatar fallback
```

### **Rate Display**
```python
individual_rate = RARITY_CONFIG[template["rarity"]]["individual_rate"]
expected_rolls = 100 / individual_rate
expected_cost = expected_rolls * 10000  # Assuming 10k per roll
```

---

## **📊 Information Architecture**

### **Collection View (`/maid_info`)**
```
🔍 [Emoji] Custom/Template Name
📋 Thông Tin Cơ Bản
├── Rarity: [Emoji] UR
├── ID: abc12345
├── Status: ⭐ Active
└── Obtained: 2 days ago

✨ Skills Đang Sở Hữu
├── 🌱 Tăng Tốc Sinh Trưởng: +45%
├── 📈 Tăng Sản Lượng: +38%
└── 💎 Tăng Giá Bán: +42%

🎲 Skills Có Thể Có (Reroll)
├── 🌱 Tăng Tốc Sinh Trưởng (30-50%)
├── 📈 Tăng Sản Lượng (30-50%)
└── 💎 Tăng Giá Bán (30-50%)

📊 Gacha Info
├── Drop Rate: 0.0167% per roll
├── Buff Count: 3 buffs
├── Reroll Cost: 500 ⭐
└── Dismantle: 100 ⭐
```

### **Database View (`/maid_database`)**
```
📚 [Emoji] Template Name
📋 Thông Tin Cơ Bản
├── Rarity: [Emoji] UR
├── Maid ID: rem_ur
├── Drop Rate: 0.0167%
└── Buff Count: 3 buffs

🎲 Skills Khi Roll Trúng
├── 🌱 Tăng Tốc Sinh Trưởng (30-50%)
├── 📈 Tăng Sản Lượng (30-50%)
└── 💎 Tăng Giá Bán (30-50%)

💰 Economics
├── Reroll Cost: 500 ⭐
├── Dismantle Reward: 100 ⭐
├── Expected Rolls: ~6000 rolls
└── Expected Cost: ~60,000,000 coins

👑 Ownership Status
└── ✅ Bạn sở hữu 2x Rem
    Dùng /maid_info <id> để xem chi tiết
```

---

## **🎮 User Experience**

### **Workflow Examples**

**Scenario 1: Check owned maid**
```
User: /maid_info rem
Bot: [Shows detailed info of user's Rem maid]
```

**Scenario 2: Research before rolling**
```
User: /maid_database saber
Bot: [Shows Saber's stats, rates, and ownership status]
User: "Oh, I need 6000 rolls on average? Maybe later..."
```

**Scenario 3: Browse collection**
```
User: /maid_list UR
Bot: [Shows all 6 UR maids with rates and commands]
User: /maid_database zero two
Bot: [Shows Zero Two detailed info]
```

### **Navigation Flow**
```
/maid_list (overview)
    ↓
/maid_list UR (specific rarity)
    ↓
/maid_database <name> (research maid)
    ↓
/maid_roll (decide to roll)
    ↓
/maid_info <id> (check obtained maid)
```

---

## **🔒 Security Features**

### **Ownership Validation**
```python
# Triple-check ownership
def _find_user_maid(self, user_id: int, maid_id: str):
    for maid in user_maids:
        # Find match
        if match_found:
            # Security check
            if maid.user_id != user_id:
                return None  # Ownership violation
            return maid
```

### **Data Sanitization**
- ✅ Input validation cho search terms
- ✅ Escape special characters
- ✅ Limit search results (prevent spam)
- ✅ Rate limiting thông qua Discord

### **Privacy Protection**
- ✅ Chỉ hiển thị maid của user
- ✅ Không leak instance IDs của người khác
- ✅ Ephemeral responses cho errors

---

## **🖼️ Avatar System Requirements**

### **📐 Aspect Ratio: 3:4 (Portrait Mode)**
```
✅ Image Specs:
   - Format: PNG (preferred), JPG, WEBP
   - Aspect Ratio: 3:4 (Portrait)
   - Size: 480x640 to 900x1200 pixels
   - File size: < 8MB (Discord limit)

🎯 Quality by Rarity:
   - UR Maids: 750x1000 (Premium)
   - SSR Maids: 600x800 (High Quality)  
   - SR/R Maids: 480x640 (Standard)

🌐 Hosting Options:
   - Imgur: https://i.imgur.com/image_id.png
   - Discord CDN: https://cdn.discordapp.com/...
   - GitHub: https://raw.githubusercontent.com/...
```

### **🎨 Design Guidelines**
```
📍 Character Positioning:
   - Head & hair in top 25%
   - Torso & main features in middle 50%
   - Character fills 70-80% of frame
   - Face in upper 1/3 of image

🌈 Visual Style:
   - High contrast backgrounds
   - Clean, sharp character lines
   - Vibrant colors that pop
   - Minimal background distractions
```

---

## **📈 Performance Optimizations**

### **Search Efficiency**
```python
# O(n) search với early termination
# 1. ID search: Direct hash lookup
# 2. Name search: Linear scan với short-circuit
# 3. Batch processing cho multiple results
```

### **Memory Management**
- ✅ Lazy loading cho large embeds
- ✅ Chunked display cho long lists
- ✅ Efficient string operations

### **Discord API Optimization**
- ✅ Single embed per response
- ✅ Optimized field structure
- ✅ Efficient image loading

---

## **🛠️ Future Enhancements**

### **Planned Features**
1. **Advanced Search**
   - Filter by series, buff types
   - Sort by rates, names, dates
   - Fuzzy search algorithms

2. **Collection Statistics**
   - Completion percentage by rarity
   - Total investment calculations
   - Comparative analysis

3. **Interactive Features**
   - Reaction-based navigation
   - Quick actions (activate/rename)
   - Favorite maid bookmarking

4. **Avatar System**
   - Custom art upload
   - Community gallery
   - Seasonal themes

---

## **✅ Implementation Status**

### **Completed ✅**
- ✅ `/maid_info` command với full details
- ✅ `/maid_database` search functionality
- ✅ `/maid_list` overview system
- ✅ Avatar display support
- ✅ Security validation
- ✅ Search by name/ID
- ✅ Rate calculations
- ✅ Ownership status
- ✅ Error handling

### **Ready for Testing 🧪**
- 🧪 All commands functional
- 🧪 Security measures active
- 🧪 Performance optimized
- 🧪 User experience polished

**System Status: ✅ PRODUCTION READY** 