# 🎀 Hệ Thống Maid - Gacha & Buffs

## 📝 Tổng Quan

Hệ thống Maid là một tính năng gacha cho phép người chơi:
- Roll để nhận các maid với buffs khác nhau
- Trang bị maid để nhận buffs cho farming
- Quản lý collection và trade maids
- Sử dụng stardust để reroll buffs

## 🎰 Gacha System

### Commands Cơ Bản
- `/maid_gacha` - Roll 1 lần (10,000 coins)
- `/maid_gacha10` - Roll 10 lần (90,000 coins, giảm 10%)
- `/maid_pity` - Xem tỷ lệ gacha rates

### ⚠️ Không Có Pity System
- **Mỗi lần roll đều độc lập** với tỷ lệ cố định
- **Không có guaranteed UR** sau số lần roll nhất định
- **Pure RNG system** - may mắn là chìa khóa!

### Tỷ Lệ Drop
- **UR**: 0.001% (2 buffs, 30-50% power) - **CỰC HIẾM!**
- **SSR**: 5.999% (1 buff, 20-35% power)  
- **SR**: 14% (1 buff, 15-25% power)
- **R**: 80% (1 buff, 5-15% power)

## 👑 Management Commands

### Collection & Equipment
- `/maid_collection [page]` - Xem collection maids
- `/maid_equip <id>` - Trang bị maid (chỉ 1 active tại 1 thời điểm)
- `/maid_active` - Xem maid đang active và buffs
- `/maid_rename <id> <name>` - Đổi tên maid

### Stardust System
- `/maid_stardust` - Xem số bụi sao và giá reroll
- `/maid_dismantle <id>` - Tách maid thành bụi sao
- `/maid_reroll <id>` - Reroll buffs bằng bụi sao

### Statistics
- `/maid_stats` - Xem thống kê gacha cá nhân

## ✨ Buff Types

### 🌱 Growth Speed
- **Tác dụng**: Giảm thời gian trồng cây
- **Áp dụng**: Khi plant seeds trong farm
- **Range**: 5% - 50% tùy rarity

### 💰 Seed Discount  
- **Tác dụng**: Giảm giá mua hạt giống
- **Áp dụng**: Khi mua seeds trong shop
- **Range**: 10% - 40% tùy rarity

### 📈 Yield Boost
- **Tác dụng**: Tăng sản lượng nông sản
- **Áp dụng**: Khi harvest crops
- **Range**: 15% - 75% tùy rarity

### 💎 Sell Price
- **Tác dụng**: Tăng giá bán nông sản  
- **Áp dụng**: Khi sell crops
- **Range**: 10% - 50% tùy rarity

## ⭐ Stardust Economy

### Dismantle Rewards
- **UR**: 100 bụi sao
- **SSR**: 50 bụi sao
- **SR**: 25 bụi sao
- **R**: 10 bụi sao

### Reroll Costs
- **UR**: 80 bụi sao
- **SSR**: 40 bụi sao
- **SR**: 20 bụi sao
- **R**: 8 bụi sao

## 📊 Anime Maids Collection

### UR Tier (6 Maids - 2 Buffs Each)
- **💙 Rem** - Devoted Maid (Re:Zero)
- **⚔️ Saber** - King of Knights (Fate)  
- **👹 Rias** - Devil Princess (High School DxD)
- **❄️ Emilia** - Half-Elf Princess (Re:Zero)
- **🐰 Yoshino** - Gentle Spirit (Date A Live)
- **🕰️ Kurumi** - Nightmare (Date A Live)

### SSR Tier (10 Maids - 1 Buff Each)
- **⚡ Mikasa** - Strongest Soldier (Attack on Titan)
- **💫 Asuna** - Lightning Flash (SAO)
- **🦋 Zero Two** - Darling (FranXX)
- **📝 Violet** - Auto Memory Doll (Violet Evergarden)
- **🧪 Kurisu** - Genius Scientist (Steins;Gate)
- **👁️ Makima** - Control Devil (Chainsaw Man)
- **🌹 Yor** - Thorn Princess (Spy x Family)
- **🏰 Kaguya** - Ice Princess (Kaguya-sama)
- **🌪️ Tatsumaki** - Tornado of Terror (One Punch Man)
- **💥 Megumin** - Explosion Wizard (KonoSuba)

### SR Tier (15 Maids - 1 Buff Each)
- **🌙 Usagi** - Sailor Moon, **👁️‍🗨️ Hinata** - Byakugan Princess (Naruto)
- **🎋 Nezuko** - Demon Sister (Demon Slayer), **🐰 Mai** - Bunny Girl Senpai
- **✂️ Hitagi** - Tsundere Queen (Monogatari), **🛡️ Erza** - Titania (Fairy Tail)
- **🗺️ Nami** - Navigator (One Piece), **🌸 Robin** - Devil Child (One Piece)
- **📱 Komi** - Communication Goddess, **🐲 Chihiro** - Spirited Girl
- **🤖 Rei** - First Child (Evangelion), **🔥 Asuka** - Second Child (Evangelion)
- **🦋 Shinobu** - Insect Hashira (Demon Slayer), **💗 Mitsuri** - Love Hashira
- **🩸 Power** - Blood Devil (Chainsaw Man)

### R Tier (19 Maids - 1 Buff Each)
Includes popular characters like Android 18, Rukia, Sailor Venus, Tohru Honda, Kagome, Yuno Gasai, Holo, Nefertari Vivi, Revy, Jolyne Cujoh, Nobara, Mio Akiyama, và nhiều nhân vật khác từ các anime nổi tiếng.

## 🔧 Integration với Game Systems

### Farm System
```python
from features.maid_helper import maid_helper

# Apply buffs khi farming
growth_time = maid_helper.apply_growth_speed_buff(user_id, base_time)
yield_amount = maid_helper.apply_yield_boost_buff(user_id, base_yield)
```

### Shop System  
```python
# Apply discount khi mua seeds
seed_price = maid_helper.apply_seed_discount_buff(user_id, base_price)
```

### Market System
```python  
# Apply price boost khi bán crops
sell_price = maid_helper.apply_sell_price_buff(user_id, base_price)
```

## 🗄️ Database Schema

### Tables Created
- `user_maids` - Maid instances của users
- `gacha_history` - Lịch sử gacha rolls
- `user_gacha_pity` - Pity tracking
- `user_stardust` - Stardust của users
- `maid_trades` - Trade history (future feature)

### Key Models
- `UserMaid` - Instance cụ thể của maid với buffs
- `MaidBuff` - Individual buff với type và value
- `GachaHistory` - Record gacha attempts
- `UserStardust` - Stardust balance

## 🚀 Usage Examples

### Basic Gacha Flow
1. User dùng `/maid_gacha` với 10k coins
2. System random rarity dựa theo drop rates
3. Generate buffs random cho maid
4. Lưu vào database với unique instance ID
5. Show results với embed

### Equipment Flow  
1. User dùng `/maid_equip <id>`
2. System deactivate all current maids
3. Activate selected maid
4. Buffs automatically apply to farming

### Stardust Flow
1. User dùng `/maid_dismantle <id>` 
2. System confirm với button interaction
3. Delete maid và add stardust to user
4. User có thể `/maid_reroll <id>` với stardust

## ⚡ Performance Notes

- Maid buffs được cache trong active session
- Database queries optimized với indexes
- Pagination cho collection views
- Rate limiting cho gacha commands

## 🔮 Future Features

- **Trade System**: User trade maids với nhau
- **Seasonal Maids**: Limited time special maids
- **Maid Fusion**: Combine maids để upgrade
- **Maid Levels**: Level up system cho stronger buffs

---

**Created**: Hệ thống Maid hoàn chỉnh với gacha, buffs, stardust, và integration sẵn sàng để deploy! 