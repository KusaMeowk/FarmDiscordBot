# 🎀 Maid System V2 - Hướng Dẫn Hoàn Chỉnh

## 🚀 Tổng Quan

Maid System V2 là phiên bản **hoàn toàn mới** của hệ thống maid với:
- ✅ **Architecture mới**: Sử dụng database riêng biệt (`user_maids_v2`)
- ✅ **Commands đơn giản**: Prefix ngắn gọn, dễ nhớ
- ✅ **Zero conflicts**: Không xung đột với hệ thống cũ
- ✅ **Full features**: Gacha, collection, buffs, stardust, reroll
- ✅ **Integration sẵn sàng**: Tích hợp buff vào farm/shop/market

---

## 🎯 Commands Mới

### **Gacha Commands**
```bash
f2!mg          # 🎰 Gacha 1 maid (10,000 coins)
f2!mg10        # 🎰 Gacha 10 maids (90,000 coins, tiết kiệm 10%)
```

### **Management Commands**
```bash
f2!ma          # 👑 Xem maid đang active và buffs
f2!mc [page]   # 📚 Xem collection maids (có pagination)
f2!me <id>     # 🎯 Trang bị maid (dùng instance ID hoặc tên)
```

### **Stardust Commands**
```bash
f2!mstar       # ⭐ Xem stardust và bảng giá
f2!mdis <id>   # 💥 Tách maid thành stardust (có confirm button)
f2!mreroll <id> # 🎲 Reroll buffs maid (có confirm button)
```

---

## 🎰 Gacha System

### **Rates (Tỷ lệ drop)**
- **UR**: 0.1% (2 buffs, 30-50% power) - 6 maids
- **SSR**: 5.9% (1 buff, 20-35% power) - 10 maids  
- **SR**: 24% (1 buff, 15-25% power) - 15 maids
- **R**: 70% (1 buff, 5-15% power) - 19 maids

### **Gacha Pricing**
- **Single roll**: 10,000 coins
- **10-roll**: 90,000 coins (tiết kiệm 10,000 coins)
- **No pity system**: Mỗi roll độc lập, pure RNG

### **Example Gacha Flow**
```
1. User: f2!mg
2. Bot deducts 10,000 coins
3. System rolls random maid theo rates
4. Generate random buffs cho maid đó
5. Save vào database với unique instance ID
6. Show result embed với avatar và buffs
```

---

## ✨ Buff System

### **4 Loại Buffs**
1. **🌱 Growth Speed**: Giảm thời gian trồng cây (5-50%)
2. **💰 Seed Discount**: Giảm giá mua hạt giống (10-40%)  
3. **📈 Yield Boost**: Tăng sản lượng thu hoạch (15-75%)
4. **💎 Sell Price**: Tăng giá bán nông sản (10-50%)

### **Buff Ranges by Rarity**
- **UR**: 30-50% per buff (2 buffs)
- **SSR**: 20-35% per buff (1 buff)
- **SR**: 15-25% per buff (1 buff)  
- **R**: 5-15% per buff (1 buff)

### **Integration với Game Systems**
Buffs tự động apply khi có maid active:
- **Farm**: Growth time reduction, yield boost
- **Shop**: Seed price discount
- **Market**: Sell price boost

---

## ⭐ Stardust Economy

### **Dismantle Rewards (Tách maid)**
- **UR**: 100 ⭐ stardust
- **SSR**: 50 ⭐ stardust
- **SR**: 25 ⭐ stardust  
- **R**: 10 ⭐ stardust

### **Reroll Costs (Reroll buffs)**
- **UR**: 80 ⭐ stardust
- **SSR**: 40 ⭐ stardust
- **SR**: 20 ⭐ stardust
- **R**: 8 ⭐ stardust

### **Economics (1.25x ratio)**
- Tách maid luôn cho nhiều stardust hơn cost reroll
- Khuyến khích tách duplicate để reroll main maids
- Sustainable economy không bị inflation

---

## 🗄️ Database Schema

### **Tables Created (V2)**
```sql
-- V2 tables không conflict với old system
user_maids_v2          -- Maid instances của users
gacha_history_v2       -- Lịch sử gacha rolls  
user_stardust_v2       -- Stardust balance
maid_reroll_history_v2 -- History reroll cho tracking
```

### **Key Features**
- **Separate tables**: Không ảnh hưởng data cũ
- **UUID instance IDs**: Unique cho mỗi maid copy
- **Async operations**: Performance tối ưu
- **Proper indexing**: Fast queries

---

## 📚 Maid Collection (50 Maids)

### **UR Tier (6 maids - 2 buffs each)**
- 💙 **Rem** - Devoted Maid (Re:Zero)
- ⚔️ **Saber** - King of Knights (Fate)
- 👹 **Rias** - Devil Princess (High School DxD)  
- ❄️ **Emilia** - Half-Elf Princess (Re:Zero)
- 🐰 **Yoshino** - Gentle Spirit (Date A Live)
- 🕰️ **Kurumi** - Nightmare (Date A Live)

### **SSR Tier (10 maids - 1 buff each)**
- ⚡ **Mikasa** - Strongest Soldier (Attack on Titan)
- 💫 **Asuna** - Lightning Flash (SAO)
- 🦋 **Zero Two** - Darling (FranXX)
- 📝 **Violet** - Auto Memory Doll (Violet Evergarden)
- 🧪 **Kurisu** - Genius Scientist (Steins;Gate)
- 👁️ **Makima** - Control Devil (Chainsaw Man)
- 🌹 **Yor** - Thorn Princess (Spy x Family)
- 🏰 **Kaguya** - Ice Princess (Kaguya-sama)
- 🌪️ **Tatsumaki** - Tornado of Terror (One Punch Man)
- 💥 **Megumin** - Explosion Wizard (KonoSuba)

### **SR Tier (15 maids - 1 buff each)**
Bao gồm: Usagi, Hinata, Nezuko, Mai, Hitagi, Erza, Nami, Robin, Komi, Chihiro, Rei, Asuka, Shinobu, Mitsuri, Power

### **R Tier (19 maids - 1 buff each)**  
Bao gồm: Android 18, Rukia, Venus, Tohru, Kagome, Yuno, Holo, Vivi, Revy, Jolyne, Nobara, Mio, Sheryl, Lina, Kagura, Esdeath, Motoko, Tsunade, Yoruichi

---

## 🎮 Workflow Examples

### **Basic Gacha → Equipment Flow**
```bash
1. f2!mg                    # Roll 1 maid
2. f2!mc                    # Check collection  
3. f2!me abc12345          # Equip maid by instance ID
4. f2!ma                   # Verify active maid và buffs
```

### **Stardust Management Flow**
```bash
1. f2!mc                   # Find duplicate hoặc weak maids
2. f2!mdis abc12345       # Dismantle maid → stardust
3. f2!mstar               # Check stardust balance
4. f2!mreroll def67890    # Reroll buffs của main maid
```

### **10-Roll Gacha Flow**
```bash
1. f2!mg10                 # Roll 10 maids (better value)
2. f2!mc                   # Review new collection
3. f2!me <best_maid_id>   # Equip maid với best buffs
4. f2!mdis <duplicate_ids> # Tách duplicates → stardust
```

---

## 🔧 Integration Setup

### **Buff Helper Usage**
```python
from features.maid_helper_v2 import get_maid_helper

# Apply buffs trong farm system
maid_helper = get_maid_helper()
modified_growth_time = await maid_helper.apply_growth_speed_buff(user_id, base_time)
modified_seed_price = await maid_helper.apply_seed_discount_buff(user_id, base_price)
modified_yield = await maid_helper.apply_yield_boost_buff(user_id, base_yield)
modified_sell_price = await maid_helper.apply_sell_price_buff(user_id, base_price)
```

### **Display Integration**
```python
# Thêm buff info vào farm/profile embeds
buff_field = await maid_helper.get_buff_display_embed_field(user_id)
if buff_field:
    embed.add_field(buff_field[0], buff_field[1], buff_field[2])
```

---

## 🚨 Migration & Compatibility

### **Old vs New System**
- **Old system**: Tables `user_maids`, `gacha_history`, etc.
- **New system**: Tables `user_maids_v2`, `gacha_history_v2`, etc.
- **Zero conflict**: Có thể chạy song song

### **Admin Commands**
```bash
f2!disable_old_maid    # Disable old maid system
f2!enable_old_maid     # Re-enable old maid system  
f2!maid_status         # Check status của both systems
```

### **Migration Strategy**
1. Deploy V2 system song song với old system
2. Test V2 thoroughly
3. Migrate user data nếu cần (optional)
4. Disable old system khi V2 stable
5. Remove old code sau khi confirmed working

---

## ✅ Features Completed

### **🎰 Gacha System**
- ✅ Single roll (f2!mg) 
- ✅ 10-roll với discount (f2!mg10)
- ✅ Proper rates và random generation
- ✅ History tracking
- ✅ Cost deduction

### **👑 Management System**  
- ✅ Active maid viewing (f2!ma)
- ✅ Collection viewing với pagination (f2!mc)
- ✅ Maid equipment (f2!me)
- ✅ Instance ID search
- ✅ Name-based search

### **⭐ Stardust System**
- ✅ Stardust viewing (f2!mstar)
- ✅ Maid dismantling với confirm (f2!mdis)
- ✅ Buff rerolling với confirm (f2!mreroll)
- ✅ Economics balancing
- ✅ History tracking

### **🔧 Integration System**
- ✅ Buff helper V2 
- ✅ Growth speed buffs
- ✅ Seed discount buffs
- ✅ Yield boost buffs  
- ✅ Sell price buffs
- ✅ Display integration ready

### **🗄️ Database System**
- ✅ V2 tables design
- ✅ Async operations
- ✅ Proper schema
- ✅ No conflicts với old system

---

## 🎯 Kết Luận

Maid System V2 là **complete rewrite** với:
- **Architecture tốt hơn**: Async/await, proper database design
- **UX tốt hơn**: Simple commands, clear feedback  
- **Performance tốt hơn**: Optimized queries, minimal conflicts
- **Integration ready**: Sẵn sàng integrate với farm/shop/market
- **Maintainable**: Clean code, proper documentation

**Ready for production deployment!** 🚀

---

## 📞 Commands Quick Reference

| Command | Description | Cost |
|---------|-------------|------|
| `f2!mg` | Gacha 1 maid | 10,000 coins |
| `f2!mg10` | Gacha 10 maids | 90,000 coins |
| `f2!ma` | Xem active maid | Free |
| `f2!mc [page]` | Xem collection | Free |
| `f2!me <id>` | Trang bị maid | Free |
| `f2!mstar` | Xem stardust | Free |
| `f2!mdis <id>` | Tách maid | Free (earn ⭐) |
| `f2!mreroll <id>` | Reroll buffs | Costs ⭐ | 