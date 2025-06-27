# 🎀 Maid System - Commands Comprehensive Guide

## 📋 Tổng Quan
Hệ thống Maid hoàn chỉnh với 50 nhân vật anime, gacha system, buff system, stardust economy và management tools. Hỗ trợ cả shortcuts và full commands.

---

## 🎰 **GACHA COMMANDS**

### **`f2!mg` / `f2!maid_gacha`**
```
📝 Mô tả: Roll gacha 1 maid
💰 Chi phí: 10,000 coins
🎯 Output: 1 maid ngẫu nhiên với buffs random
⚡ Shortcut: f2!mg
```

### **`f2!mg10` / `f2!maid_gacha10`**
```
📝 Mô tả: Roll gacha 10 maids cùng lúc
💰 Chi phí: 90,000 coins (tiết kiệm 10,000 coins)
🎯 Output: 10 maids với pagination view
⚡ Shortcut: f2!mg10
💡 Tip: Better value, recommended cho bulk rolling
```

---

## 👑 **MANAGEMENT COMMANDS**

### **`f2!ma` / `f2!maid_active`**
```
📝 Mô tả: Xem maid đang active và tất cả buffs
🎯 Output: Active maid info + buff breakdown + farm impact
⚡ Shortcut: f2!ma
📊 Hiển thị: Name, rarity, buffs, instance ID
```

### **`f2!mc` / `f2!maid_collection`**
```
📝 Mô tả: Xem collection tất cả maids với filters
🎯 Pagination: 5 maids per page với navigation buttons
⚡ Shortcut: f2!mc
🔍 Filters:
   • f2!mc -r <rarity>     # Filter theo UR/SSR/SR/R
   • f2!mc -n <name>       # Filter theo tên maid
   • f2!mc -r UR -n Rem    # Combine filters
📊 Hiển thị: Instance ID, name, buffs, status (active/inactive)
```

### **`f2!mequip` / `f2!maid_equip`**
```
📝 Mô tả: Trang bị maid để nhận buffs
🎯 Input: Instance ID (8 ký tự đầu)
⚡ Shortcut: f2!mequip <id>
🔧 Logic: Unequip maid cũ → Equip maid mới → Apply buffs
💡 Tip: Chỉ 1 maid active tại 1 thời điểm
```

---

## ⭐ **STARDUST COMMANDS**

### **`f2!mstar` / `f2!maid_stardust`**
```
📝 Mô tả: Xem số stardust hiện có và economics
📊 Hiển thị:
   • Current stardust amount
   • Reroll costs by rarity
   • Dismantle rewards by rarity
   • Economic ratios (1.25x profit margin)
⚡ Shortcut: f2!mstar
```

### **`f2!mdis` / `f2!maid_dismantle`**
```
📝 Mô tả: Tách 1 maid thành stardust
🎯 Input: Instance ID (8 ký tự đầu)
⚡ Shortcut: f2!mdis <id>
🛡️ Safety: Confirmation dialog với preview rewards
❌ Restriction: Không thể tách maid đang active
💰 Rewards: UR=100⭐, SSR=50⭐, SR=25⭐, R=10⭐
```

### **`f2!mdisall` / `f2!maid_dismantle_all`** ⭐ **NEW**
```
📝 Mô tả: Tách nhiều maid cùng lúc theo filter
🔍 Filters:
   • f2!mdisall -r R          # Tách tất cả R maids
   • f2!mdisall -n Rem        # Tách tất cả Rem maids
   • f2!mdisall               # Tách tất cả (trừ active)
⚡ Shortcut: f2!mdisall
🛡️ Safety: 
   • Preview total rewards by rarity
   • Confirmation dialog with breakdown
   • Auto-exclude active maid
   • Single database transaction
💡 Use Cases:
   • Cleanup R maids: f2!mdisall -r R
   • Remove duplicates: f2!mdisall -n "duplicate name"
   • Mass stardust farming before big rerolls
```

### **`f2!mreroll` / `f2!maid_reroll`**
```
📝 Mô tả: Reroll buffs của maid với dynamic cost
🎯 Input: Instance ID (8 ký tự đầu)
⚡ Shortcut: f2!mreroll <id>
🎲 Logic: 
   • Hoàn toàn random new buffs trong rarity range
   • UR: 2 buffs (30-50%), SSR/SR/R: 1 buff
   • Dynamic cost based on current buff quality
🛡️ Safety: Confirmation dialog với old vs preview
💰 Cost: Base cost × quality multiplier (0.7x - 2.0x)
```

---

## 🔍 **INFORMATION COMMANDS**

### **`f2!maid_info`**
```
📝 Mô tả: Xem thông tin chi tiết maid trong collection
🎯 Input: Instance ID hoặc tên maid
🔒 Security: Chỉ hiển thị maid của chính user
📊 Hiển thị:
   • Avatar (nếu có art_url)
   • Basic info (rarity, ID, status, ngày nhận)
   • Current buffs (đang sở hữu)
   • Possible buffs (khi reroll)
   • Gacha info (drop rate, costs)
💡 Tip: Dùng để research maid trước khi reroll
```

### **`f2!maid_database`**
```
📝 Mô tả: Tìm kiếm maid trong database hệ thống
🎯 Input: Tên maid (có thể viết tắt)
🌐 Scope: Tất cả 50 maids trong hệ thống
📊 Output:
   • Single result: Chi tiết đầy đủ với avatar
   • Multiple results: Grouped by rarity với rates
🔍 Examples:
   • f2!maid_database rem      # Tìm tất cả maids có "rem"
   • f2!maid_database zero     # Tìm Zero Two
   • f2!maid_database saber    # Tìm Saber variants
```

### **`f2!maid_list`**
```
📝 Mô tả: Xem danh sách tất cả maids theo rarity
🎯 Input: Rarity (optional) - UR/SSR/SR/R
📊 Modes:
   • No rarity: Overview tất cả 50 maids
   • With rarity: Detailed list của rarity đó
🌟 Hiển thị:
   • Total rates, individual rates
   • Examples và complete lists
   • Direct commands để research thêm
```

### **`f2!maid_reroll_cost`**
```
📝 Mô tả: Preview chi phí reroll dynamic trước khi reroll
🎯 Input: Instance ID
📊 Hiển thị:
   • Current buffs quality analysis
   • Dynamic cost breakdown
   • Multipliers explanation
   • Base cost vs final cost
💡 Tip: Dùng để plan stardust usage efficiently
```

### **`f2!maid_stats`**
```
📝 Mô tả: Xem thống kê gacha personal
📊 Hiển thị:
   • Total rolls, money spent
   • Maids by rarity breakdown
   • Drop rates achieved vs expected
   • Collection completion percentage
   • Stardust earned/spent tracking
```

---

## 🎯 **FILTER SYSTEM GUIDE**

### **Collection Filters (`f2!mc`)**
```bash
# By Rarity
f2!mc -r UR          # Chỉ UR maids
f2!mc -r SSR         # Chỉ SSR maids
f2!mc -r SR          # Chỉ SR maids  
f2!mc -r R           # Chỉ R maids

# By Name
f2!mc -n Rem         # Tất cả maids có tên "Rem"
f2!mc -n Android     # Tất cả Android variants
f2!mc -n "Zero Two"  # Multi-word names

# Combined
f2!mc -r UR -n Saber # UR Saber variants only
```

### **Bulk Dismantle Filters (`f2!mdisall`)**
```bash
# Strategic Cleanup
f2!mdisall -r R                # Tách tất cả R maids
f2!mdisall -r SR              # Tách tất cả SR maids
f2!mdisall -n Rukia           # Tách duplicates của Rukia
f2!mdisall -n "Android 18"    # Tách Android 18 duplicates

# Mass Operations
f2!mdisall                    # Tách tất cả (except active)

# Example Workflow
f2!mc -r R                    # Preview R maids
f2!mdisall -r R              # Confirm và tách tất cả R
f2!mstar                     # Check stardust received
f2!mreroll <ur_maid_id>      # Reroll main UR maid
```

---

## 💰 **ECONOMICS & STRATEGY**

### **Stardust Economics**
```
Profit Margin: 1.25x trên tất cả rarities
• UR: 100⭐ reward / 80⭐ cost = 1.25x
• SSR: 50⭐ reward / 40⭐ cost = 1.25x  
• SR: 25⭐ reward / 20⭐ cost = 1.25x
• R: 10⭐ reward / 8⭐ cost = 1.25x

Strategy: Luôn profitable để tách duplicates cho stardust
```

### **Dynamic Reroll Costs**
```
Cost Multipliers based on current buff quality:
• 90%+ quality: 2.0x cost (expensive để reroll good buffs)
• 75-90%: 1.5x cost (moderate cost)
• 50-75%: 1.1x cost (slight premium)
• 25-50%: 0.9x cost (small discount)
• <25%: 0.7x cost (big discount để encourage reroll)
```

### **Optimal Workflows**
```
Beginner Flow:
1. f2!mg (roll singles để explore)
2. f2!mc (review collection)
3. f2!mequip <best_id> (equip best maid)
4. f2!ma (verify buffs active)

Advanced Flow:
1. f2!mg10 (bulk rolling)
2. f2!mc -r UR (check URs first)
3. f2!mequip <best_ur> (equip best UR)
4. f2!mdisall -r R (cleanup R maids)
5. f2!mreroll <main_maid> (optimize main)

Collection Management:
1. f2!mc -n <name> (find duplicates)
2. f2!mdisall -n <name> (tách duplicates)
3. f2!mstar (check stardust)
4. f2!mreroll <keeper> (improve keeper)
```

---

## 🎮 **INTEGRATION WITH GAME SYSTEMS**

### **Buff Applications**
```
🌱 Growth Speed: Farming system (reduce plant time)
💰 Seed Discount: Shop system (reduce seed prices)  
📈 Yield Boost: Farming system (increase harvest)
💎 Sell Price: Market system (increase sell value)

All buffs automatically apply khi có maid active
View impact với f2!ma command
```

### **Commands Connectivity**
```
Gacha → Collection → Equipment → Active → Benefits
f2!mg → f2!mc → f2!mequip → f2!ma → Game buffs

Cleanup → Stardust → Optimization → Better buffs
f2!mdisall → f2!mstar → f2!mreroll → Improved farming
```

---

## ⚡ **QUICK REFERENCE**

### **Essential Commands (Daily Use)**
```
f2!mg                 # Quick single roll
f2!mc                 # Check collection
f2!ma                 # Verify active maid
f2!mstar              # Check stardust
```

### **Management Commands (Weekly)**
```
f2!mdisall -r R       # Cleanup R maids
f2!mc -r UR           # Review UR collection  
f2!mreroll <id>       # Optimize main maid
```

### **Research Commands (As Needed)**
```
f2!maid_database <name>   # Research specific maid
f2!maid_list UR          # Browse UR options
f2!maid_info <id>        # Deep dive maid details
```

**Hệ thống Maid System hiện tại đã hoàn thiện với 20+ commands, filter system, bulk operations, dynamic economics và seamless integration với game systems!** 🎯 