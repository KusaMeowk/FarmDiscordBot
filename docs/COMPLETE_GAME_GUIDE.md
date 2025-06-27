# 🌾 **FARM BOT - HƯỚNG DẪN TOÀN DIỆN**

Chào mừng bạn đến với **Farm Bot** - trò chơi farming simulation hoàn chỉnh trên Discord! Xây dựng trang trại, nuôi gia súc, gacha maid, và trở thành nông dân giàu có nhất!

---

## 🎯 **GIỚI THIỆU GAME**

### **Về Farm Bot**
- **Thể loại**: Idle Farming Simulation Game
- **Nền tảng**: Discord Bot  
- **Prefix lệnh**: `f!`
- **Mục tiêu**: Xây dựng đế chế nông nghiệp thông qua trồng trọt, chăn nuôi và kinh doanh

### **Điểm Nổi Bật**
- 🌾 **Hệ thống farming hoàn chỉnh** với 10+ loại cây trồng
- 🐟🐄 **Chăn nuôi đa dạng** (ao cá + chuồng trại)
- 🎀 **Maid Collection System** với gacha và buff system
- 🎰 **Casino & Games** (Blackjack, Roulette, Slots)
- 🌤️ **Thời tiết động** ảnh hưởng sản xuất
- 🎪 **Sự kiện đặc biệt** với buff/debuff
- 🤖 **AI Game Master** tự động điều chỉnh kinh tế
- 📈 **Market động** với giá cả biến đổi
- 🏆 **Leaderboard & Competition**

---

## 🚀 **HƯỚNG DẪN BẮT ĐẦU**

### **1. Đăng Ký Tài Khoản**
```bash
f!register
f!r
```
- Tạo tài khoản mới với 1000 coins khởi điểm
- Mở khóa tất cả tính năng cơ bản

### **2. Xem Profile**
```bash
f!profile
f!p
```
- Xem thông tin cá nhân, tiền bạc, tài sản
- Kiểm tra streak điểm danh và achievements

### **3. Nhận Phần Thưởng Hàng Ngày**
```bash
f!daily
f!d
```
- Điểm danh hàng ngày nhận coins
- Streak càng dài, phần thưởng càng lớn

### **4. Xem Hướng Dẫn**
```bash
f!help
f!shortcuts
```
- Danh sách đầy đủ các lệnh
- Hướng dẫn sử dụng từng tính năng

---

## 🌾 **HỆ THỐNG FARMING**

### **Cơ Bản Farming**

#### **Xem Trang Trại**
```bash
f!farm
f!f
```
- Xem layout trang trại với grid 4x4
- Trạng thái từng ô đất (trống/đang trồng/chín)
- Sử dụng nút ⬅️ ➡️ để chuyển trang

#### **Mua Hạt Giống**
```bash
f!shop seeds
f!buy <hạt_giống> <số_lượng>
```
- Mua hạt giống từ shop
- Ví dụ: `f!buy carrot 10`

#### **Trồng Cây**
```bash
f!plant <loại_cây> <ô>           # Trồng ô đơn lẻ
f!plant <loại_cây> 1,3,5,7       # Trồng nhiều ô cụ thể  
f!plant <loại_cây> all           # Trồng tất cả ô trống
```
**Ví dụ:**
- `f!plant carrot 1` - Trồng cà rốt ở ô 1
- `f!plant tomato all` - Trồng cà chua tất cả ô trống

#### **Thu Hoạch**
```bash
f!harvest <ô>                    # Thu hoạch ô cụ thể
f!harvest 1,3,5,7                # Thu hoạch nhiều ô
f!harvest all                    # Thu hoạch tất cả
```
- Thu hoạch khi cây đã chín (✨)
- Nông sản sẽ vào kho inventory

#### **Bán Nông Sản**
```bash
f!sell <cây> <số_lượng>          # Bán số lượng cụ thể
f!sell <cây> all                 # Bán toàn bộ
```
**Ví dụ:**
- `f!sell carrot 5` - Bán 5 cà rốt
- `f!sell tomato all` - Bán toàn bộ cà chua

### **Loại Cây Trồng**

| **Tier** | **Cây** | **Giá** | **Thời Gian** | **Lợi Nhuận** |
|----------|---------|---------|---------------|---------------|
| **Tier 1** | 🥕 Cà rốt | 10→20 | 5 phút | 100% |
| | 🍅 Cà chua | 15→35 | 10 phút | 133% |
| | 🌾 Lúa mì | 25→55 | 15 phút | 120% |
| **Tier 2** | 🥔 Khoai tây | 40→90 | 25 phút | 125% |
| | 🌽 Ngô | 60→140 | 35 phút | 133% |
| | 🥬 Rau cải | 80→180 | 45 phút | 125% |
| **Tier 3** | 🍓 Dâu tây | 120→280 | 60 phút | 133% |
| | 🥦 Súp lơ | 150→350 | 75 phút | 133% |
| | 🍇 Nho | 200→480 | 90 phút | 140% |

**Tips:**
- Tier 1: Lợi nhuận nhanh, vòng quay ngắn
- Tier 2: Cân bằng thời gian và lợi nhuận  
- Tier 3: Đầu tư lâu dài, lợi nhuận cao

---

## 🐟🐄 **HỆ THỐNG CHĂN NUÔI**

### **Ao Cá (Pond System)**

#### **Quản Lý Ao Cá**
```bash
f!pond                           # Xem trạng thái ao
f!pond buy <loại_cá> [số_lượng]  # Mua cá
f!pond harvest [ô]               # Thu hoạch cá chín
f!pond upgrade                   # Nâng cấp ao (tăng ô)
```

#### **Loại Cá Nuôi**
| **Tier** | **Loài** | **Giá** | **Thời Gian** | **ROI** |
|----------|----------|---------|---------------|---------|
| **Tier 1** | 🐟 Cá Vàng | 50→80 | 30 phút | 60% |
| | 🐠 Cá Nhiệt Đới | 80→130 | 45 phút | 62% |
| | 🦈 Cá Mập Nhỏ | 120→200 | 60 phút | 67% |
| **Tier 2** | 🐙 Bạch Tuộc | 200→350 | 90 phút | 75% |
| | 🦑 Mực Ống | 300→520 | 120 phút | 73% |
| | 🦀 Cua Hoàng Gia | 500→850 | 150 phút | 70% |
| **Tier 3** | 🐋 Cá Voi Nhỏ | 800→1400 | 180 phút | 75% |
| | 🦞 Tôm Hùm | 1000→1800 | 210 phút | 80% |
| | 🦞 Tôm Hùm Huyền Thoại | 1500→2800 | 240 phút | 87% |

### **Chuồng Trại (Barn System)**

#### **Quản Lý Chuồng Trại**
```bash
f!barn                           # Xem trạng thái chuồng
f!barn buy <loại_gia_súc>        # Mua gia súc
f!barn harvest [ô]               # Thu hoạch thịt
f!barn collect [ô]               # Thu thập sản phẩm
f!barn upgrade                   # Nâng cấp chuồng
```

#### **Loại Gia Súc**
| **Loài** | **Giá** | **Thời Gian** | **Sản Phẩm** | **Chu Kỳ** |
|----------|---------|---------------|--------------|------------|
| 🐔 **Gà Mái** | 80→130 | 45 phút | 🥚 Trứng Gà (15🪙) | 30 phút |
| 🐑 **Cừu Non** | 150→250 | 90 phút | 🧶 Len Cừu (40🪙) | 6 giờ |
| 🐄 **Bò Sữa** | 300→500 | 120 phút | 🥛 Sữa Tươi (30🪙) | 2 giờ |
| 🦆 **Vịt Trời** | 200→350 | 90 phút | 🥚 Trứng Vịt (20🪙) | 45 phút |
| 🐷 **Heo Con** | 100→160 | 60 phút | 🥩 Thịt Heo (50🪙) | 4 giờ |

**Double Revenue:**
- **Thu hoạch thịt** (1 lần): Bán gia súc trưởng thành
- **Thu thập sản phẩm** (định kỳ): Sữa, trứng, len...

### **Tổng Quan Chăn Nuôi**
```bash
f!livestock                      # Tổng quan pond + barn
f!harvestall                     # Thu hoạch tất cả
f!collectall                     # Thu thập tất cả sản phẩm
```

---

## 🎀 **MAID COLLECTION SYSTEM**

### **Gacha System**
```bash
f!maid_gacha                     # Gacha 1 lần (10,000 coins)
f!maid_gacha10                   # Gacha 10 lần (90,000 coins)
f!maid_pity                      # Xem pity counter
```

#### **Tỷ Lệ Gacha**
- **R (Common)**: 70% - Basic buffs
- **SR (Rare)**: 25% - Good buffs  
- **SSR (Super Rare)**: 4.5% - Strong buffs
- **UR (Ultra Rare)**: 0.5% - Legendary buffs

### **Quản Lý Collection**
```bash
f!maid_collection               # Xem tất cả maid
f!mc                           # Shortcut
f!maid_active                  # Xem maid đang active
f!minfo <maid_name>            # Thông tin chi tiết maid
```

### **Buff System**
Maid cung cấp các loại buff:
- 🌾 **Yield Boost**: Tăng sản lượng thu hoạch
- 💰 **Sell Price**: Tăng giá bán nông sản  
- ⚡ **Growth Speed**: Giảm thời gian trồng trọt
- 🍀 **Lucky Find**: Tăng chance tìm rare items

### **Maid Management**
```bash
f!maid_equip <tên_maid>         # Trang bị maid (buff)
f!maid_rename <tên_cũ> <tên_mới> # Đổi tên maid
f!maid_dismantle <tên_maid>     # Tách maid → stardust
f!maid_dismantle_all           # Tách tất cả maid thấp
```

### **Reroll System**
```bash
f!maid_reroll <tên_maid>        # Reroll buff (tốn stardust)
f!maid_reroll_cost <tên_maid>   # Xem giá reroll
f!maid_stardust                # Xem số stardust hiện tại
```

**Maid Trading:**
```bash
f!maid_trade @user              # Mở giao dịch maid
```
- Trade maid với người chơi khác
- Đổi maid + coins + stardust

---

## 🎰 **CASINO & GAMES**

### **Blackjack**
```bash
f!blackjack <tiền_cược>         # Chơi Blackjack
f!bj <tiền_cược>               # Shortcut
```
**Luật chơi:**
- Mục tiêu: Đạt 21 điểm hoặc gần nhất
- A = 1 hoặc 11, J/Q/K = 10
- Blackjack trả 3:2, thắng thường 1:1
- House edge: 2%

**Giới hạn cược:**
- Tối thiểu: 1,000 coins
- Tối đa: 1,000,000 coins
- Cooldown: 3 giây

### **Other Casino Games** (Coming Soon)
- 🎰 **Slots Machine**
- 🎲 **Dice Games**  
- 🃏 **Poker**
- 🎯 **Roulette**

---

## 🌤️ **HỆ THỐNG THỜI TIẾT**

### **Xem Thời Tiết**
```bash
f!weather                       # Thời tiết hiện tại
f!forecast                      # Dự báo 3 ngày
f!aiweather                     # AI weather control
```

### **Loại Thời Tiết**
| **Thời Tiết** | **Farm Effect** | **Price Effect** | **Livestock** |
|---------------|-----------------|------------------|---------------|
| ☀️ **Sunny** | Growth +20% | Market +15% | Normal |
| 🌧️ **Rainy** | Growth +10% | Market +10% | Fish +30% |
| ☁️ **Cloudy** | Normal | Normal | Animal -5% |
| ⛈️ **Stormy** | Growth -30% | Market -25% | All -15% |
| 🌈 **Perfect** | Growth +25% | Market +25% | All +10% |

**Tips:**
- Trồng nhiều cây khi **Sunny/Perfect**
- Tránh trồng khi **Stormy**
- Bán nông sản khi giá cao

---

## 🎪 **HỆ THỐNG SỰ KIỆN**

### **Xem Sự Kiện**
```bash
f!event                         # Sự kiện hiện tại
f!events                        # Lịch sử sự kiện
f!claim_event                   # Claim phần thưởng
```

### **Loại Sự Kiện**

#### **Buff Events** (Tích cực)
- 🌱 **Mùa màng bội thu**: +50% yield tất cả cây
- 🎉 **Lễ hội nông dân**: +30% exp, giảm 50% giá hạt giống
- 🌟 **Phúc lành từ trời**: +25% tốc độ growth
- 💰 **Boom kinh tế**: +40% giá bán nông sản

#### **Debuff Events** (Thử thách)
- 🌧️ **Mưa acid**: -50% yield tất cả cây
- 🐛 **Dịch sâu bệnh**: -50% tốc độ growth
- 📉 **Khủng hoảng kinh tế**: -30% giá bán  
- 💸 **Lạm phát hạt giống**: +100% giá mua hạt giống

**Event Duration**: 2-6 giờ
**Frequency**: 1-3 events/ngày

---

## 💰 **HỆ THỐNG KINH TẾ**

### **Market & Pricing**
```bash
f!market                        # Thị trường chi tiết
f!farmmarket                    # Giá nông sản đơn giản
f!trends                        # Xu hướng giá cả
```

### **AI Economic Manager**
- **Tự động điều chỉnh** giá cả dựa trên supply/demand
- **Dynamic pricing** theo thời tiết và sự kiện
- **Anti-inflation** system bảo vệ kinh tế game
- **Market cycle** 4-6 giờ

### **Shop System**
```bash
f!shop                          # Shop tổng hợp
f!shop seeds                    # Hạt giống
f!shop tools                    # Công cụ nông nghiệp
f!shop special                  # Vật phẩm đặc biệt
```

### **Transfer System**
```bash
f!transfer @user <số_tiền>      # Chuyển tiền
```

---

## 🏆 **LEADERBOARD & RANKINGS**

### **Xem Leaderboard**
```bash
f!leaderboard                   # Top players by money
f!rank                          # Ranking cá nhân
f!compare @user                 # So sánh với user khác
```

### **Ranking Categories**
- 💰 **Richest Players**: Top tiền bạc
- 🌾 **Best Farmers**: Top sản lượng nông nghiệp  
- 🎰 **Casino Kings**: Top thắng casino
- 📅 **Streak Masters**: Top streak điểm danh
- 🎀 **Maid Collectors**: Top collection maid

---

## 🤖 **AI GAME MASTER**

### **AI Controls**
```bash
f!gamemaster                    # Trạng thái AI Game Master
f!ai                           # Shortcut AI commands
```

### **AI Features**
- **Economic Management**: Tự động điều chỉnh giá market
- **Weather Control**: AI quyết định thời tiết logic
- **Event Scheduling**: Tự động tạo sự kiện cân bằng
- **Balance Monitoring**: Phát hiện và fix economic imbalance
- **Player Behavior Analysis**: Optimize game experience

**AI Notifications:**
Game Master sẽ thông báo các thay đổi quan trọng:
- Market price adjustments
- Weather pattern changes  
- Special events triggered
- Economic balance updates

---

## 📱 **SHORTCUTS & QOL**

### **Command Shortcuts**
| **Full Command** | **Shortcut** | **Description** |
|------------------|--------------|-----------------|
| `f!profile` | `f!p` | Profile |
| `f!farm` | `f!f` | Farm view |
| `f!plant` | `f!pl` | Plant crops |
| `f!harvest` | `f!h` | Harvest |
| `f!sell` | `f!s` | Sell crops |
| `f!daily` | `f!d` | Daily rewards |
| `f!market` | `f!m` | Market view |
| `f!weather` | `f!w` | Weather |
| `f!maid_collection` | `f!mc` | Maid collection |
| `f!livestock` | `f!li` | Livestock overview |

### **Nút Tương Tác**
- **🔄 Harvest All**: Thu hoạch tất cả cây chín
- **⬅️ ➡️**: Chuyển trang farm
- **💰 Sell All**: Bán tất cả loại nông sản
- **♻️ Refresh**: Cập nhật trạng thái

### **Help System**
```bash
f!help                          # Hướng dẫn tổng quầnn
f!help <command>                # Hướng dẫn lệnh cụ thể
f!shortcuts                     # Danh sách shortcuts
```

---

## 💡 **TIPS & STRATEGIES**

### **Early Game (0-10k coins)**
1. **Tập trung Tier 1 crops**: Cà rốt, cà chua cho vòng quay nhanh
2. **Điểm danh hàng ngày**: Streak tăng income passive
3. **Mua ít pond slots**: Bắt đầu nuôi cá Tier 1
4. **Tránh casino**: Rủi ro cao với capital thấp

### **Mid Game (10k-100k coins)**
1. **Đa dạng hóa**: Mix Tier 1-2 crops và livestock
2. **Upgrade facilities**: Tăng pond/barn slots
3. **Maid gacha**: Bắt đầu gacha cho buff system
4. **Weather trading**: Mua thấp bán cao theo thời tiết

### **Late Game (100k+ coins)**
1. **Tier 3 focus**: Đầu tư vào cây/livestock lợi nhuận cao
2. **Maid collection**: Thu thập maid UR/SSR cho buff mạnh
3. **Casino investment**: Chơi casino với capital lớn
4. **Market manipulation**: Tận dụng AI economic cycles

### **Advanced Tips**
- **Combo planting**: Trồng mixed Tier cho optimize thời gian
- **Weather prediction**: Theo dõi forecast để plan production
- **Event preparation**: Chuẩn bị inventory cho debuff events
- **Maid synergy**: Combine multiple maid buffs hiệu quả

---

## 🐛 **TROUBLESHOOTING**

### **Common Issues**
- **"Bạn chưa đăng ký"**: Dùng `f!register` để tạo account
- **"Không đủ tiền"**: Kiểm tra balance với `f!profile`  
- **"Ô đất không hợp lệ"**: Đảm bảo số ô trong giới hạn
- **"Chưa chín"**: Đợi đủ thời gian growth hoặc check `f!farm`

### **Performance Issues**
- **Bot lag**: Bot có thể bận, thử lại sau 30 giây
- **Commands không response**: Check bot online status
- **Database issues**: Report admin nếu persistent

### **Get Help**
- Dùng `f!help` cho hướng dẫn cơ bản
- Tag admin nếu gặp bug
- Report issues trong support channel

---

## 🎊 **KẾT LUẬN**

**Farm Bot** là một ecosystem gaming hoàn chỉnh với depth và replayability cao. Từ một nông dân khiêm tốn, bạn có thể xây dựng đế chế nông nghiệp, thu thập army of maids, và trở thành tỷ phú trong thế giới Discord!

**Key Success Factors:**
- ⏰ **Patience**: Idle game rewards long-term planning
- 📊 **Strategy**: Smart resource allocation và timing
- 🎯 **Focus**: Specialize trong area mạnh nhất của bạn
- 🤝 **Community**: Trade và compete với players khác

**Ready to start farming?** 
Gõ `f!register` và bắt đầu cuộc phiêu lưu nông nghiệp của bạn ngay hôm nay!

---

*Document Version: 1.0 | Last Updated: 2024*
*Tạo bởi Farm Bot Development Team*

**🌾 Happy Farming! 🌾** 