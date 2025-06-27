# Maid System Configuration
"""
🖼️ AVATAR REQUIREMENTS - 3:4 Aspect Ratio (Portrait Mode):
- UR Maids: 750x1000 pixels (Premium quality)
- SSR Maids: 600x800 pixels (High quality)  
- SR/R Maids: 480x640 pixels (Standard quality)
- Format: PNG preferred, JPG/WEBP acceptable
- File size: < 8MB (Discord limit)
- Hosting: Imgur recommended (https://i.imgur.com/image_id.png)
"""
import random
from typing import Dict, List, Any

# Gacha Configuration
GACHA_CONFIG = {
    "single_roll_cost": 10000,      # 10k coins/roll
    "ten_roll_cost": 90000,         # 90k coins/10 rolls (10% discount)
    "pity_threshold": None,         # No pity system
    "guaranteed_ur_rolls": None     # No pity system
}

# Rarity Configuration với Individual Maid Rates
RARITY_CONFIG = {
    "GR": {
        "buff_count": 3,
        "buff_range": (50, 70),    # % buff power - HIGHEST tier
        "total_rate": 0.01,        # 0.01% total rate cho GR (rarest)
        "maid_count": 2,           # 2 GR maids (Jalter + Kotori)
        "individual_rate": 0.01/2, # 0.005% per GR maid (exclusive trong limited banner)
        "color": 0xDC143C          # Màu đỏ tươi
    },
    "UR": {
        "buff_count": 2,
        "buff_range": (35, 50),    # % buff power - REDUCED from 50-70
        "total_rate": 0.1,         # 0.1% total rate cho UR
        "maid_count": 6,           # 6 UR maids (excluding Jalter - now GR)
        "individual_rate": 0.1/6,  # 0.0167% per UR maid
        "color": 0xFF6B9D          # Màu hồng
    },
    "SSR": {
        "buff_count": 1,
        "buff_range": (20, 35),
        "total_rate": 5.9,         # 5.9% total rate cho SSR
        "maid_count": 10,          # 10 SSR maids
        "individual_rate": 5.9/10, # 0.59% per SSR maid
        "color": 0xFFD700          # Màu vàng
    },
    "SR": {
        "buff_count": 1,
        "buff_range": (15, 25),
        "total_rate": 24.0,        # 24% total rate cho SR
        "maid_count": 15,          # 15 SR maids
        "individual_rate": 24.0/15, # 1.6% per SR maid
        "color": 0xC0C0C0          # Màu bạc
    },
    "R": {
        "buff_count": 1,
        "buff_range": (5, 15),
        "total_rate": 70.0,        # 70% total rate cho R
        "maid_count": 19,          # 19 R maids
        "individual_rate": 70.0/19, # 3.68% per R maid
        "color": 0xCD7F32          # Màu đồng
    }
}

# Stardust Configuration
STARDUST_CONFIG = {
    "dismantle_rewards": {
        "GR": 200,      # Tách GR = 200 bụi sao (highest reward)
        "UR": 100,      # Tách UR = 100 bụi sao
        "SSR": 50,      # Tách SSR = 50 bụi sao  
        "SR": 25,       # Tách SR = 25 bụi sao
        "R": 10,        # Tách R = 10 bụi sao
    },
    "reroll_costs": {
        "GR": 150,      # Reroll GR maid = 150 bụi sao (premium cost)
        "UR": 80,       # Reroll UR maid = 80 bụi sao
        "SSR": 40,      # Reroll SSR maid = 40 bụi sao
        "SR": 20,       # Reroll SR maid = 20 bụi sao
        "R": 8          # Reroll R maid = 8 bụi sao
    }
}

# Multi-Banner Configuration  
BANNER_CONFIGS = {
    "jalter": {
        "banner_name": "Dragon Witch Festival",
        "featured_character": "jalter_gr",
        "single_roll_cost": 12000,
        "ten_roll_cost": 108000,
        "banner_description": "🔥 Dragon Witch Jeanne d'Arc Alter ra mắt! Ghost Rare debut + Rate-up featured!",
        "background_color": 0xFF4500,  # Màu cam đỏ cho theme rồng lửa
        "theme_emoji": "🔥"
    },
    "kotori": {
        "banner_name": "Spirit Sister Festival", 
        "featured_character": "kotori_gr",
        "single_roll_cost": 12000,
        "ten_roll_cost": 108000,
        "banner_description": "🍡 Date A Live - Kotori Itsuka cô em gái đáng yêu ra mắt!",
        "background_color": 0xDC143C,  # Màu đỏ tươi cho Kotori
        "theme_emoji": "🍡"
    }
}

# Active Banner State (Admin có thể thay đổi)
ACTIVE_BANNER_CONFIG = {
    "enabled": False,               # Banner có đang active không
    "current_banner": "kotori",     # Banner hiện tại: "jalter" hoặc "kotori"
    "start_time": None,             # Thời gian bắt đầu
    "end_time": None                # Thời gian kết thúc
}

# Legacy config để backward compatibility
LIMITED_BANNER_CONFIG = {
    "enabled": False,
    "banner_name": "Spirit Sister Festival",
    "single_roll_cost": 12000,
    "ten_roll_cost": 108000,
    "featured_rate_up": 2.0,
    "ur_rate_boost": 0.1,
    "ssr_rate_boost": 2.0,
    "banner_description": "🍡 Date A Live - Kotori Itsuka cô em gái đáng yêu ra mắt!",
    "background_color": 0xDC143C,
    "start_time": None,
    "end_time": None
}

# Limited Banner Rates (khi enabled)
LIMITED_RARITY_CONFIG = {
    "GR": {
        "total_rate": 0.05,        # 0.05% Ghost Rare rate trong limited banner  
        "featured_rate": 0.05,     # 100% của GR rate cho featured (Jalter)
        "other_rate": 0.0,         # Không có GR khác
        "color": 0x8B00FF          # Màu tím ma quái
    },
    "UR": {
        "total_rate": 0.15,        # Giảm từ 0.2% xuống 0.15% (để nhường chỗ cho GR)
        "featured_rate": 0.0,      # Không có UR featured nữa
        "other_rate": 0.15,        # Tất cả cho UR thường (exclude limited-only)
        "color": 0xFF1493          # Deep pink cho limited UR
    },
    "SSR": {
        "total_rate": 7.9,         # Tăng từ 5.9% lên 7.9%
        "featured_rate": 0.0,      # Không có SSR featured
        "other_rate": 7.9,         # Tất cả cho SSR thường
        "color": 0xFFD700
    },
    "SR": {
        "total_rate": 22.1,        # Điều chỉnh để cân bằng tổng = 100%
        "featured_rate": 0.0,
        "other_rate": 22.1,
        "color": 0xC0C0C0
    },
    "R": {
        "total_rate": 69.8,        # Điều chỉnh để cân bằng tổng = 100%
        "featured_rate": 0.0,
        "other_rate": 69.8,
        "color": 0xCD7F32
    }
}

# Buff Types
BUFF_TYPES = {
    "growth_speed": {
        "name": "🌱 Tăng Tốc Sinh Trưởng",
        "description": "Giảm thời gian trồng cây",
        "emoji": "🌱"
    },
    "seed_discount": {
        "name": "💰 Giảm Giá Hạt Giống", 
        "description": "Giảm giá mua hạt giống",
        "emoji": "💰"
    },
    "yield_boost": {
        "name": "📈 Tăng Sản Lượng",
        "description": "Tăng số lượng nông sản thu hoạch",
        "emoji": "📈"
    },
    "sell_price": {
        "name": "💎 Tăng Giá Bán",
        "description": "Tăng giá bán nông sản",
        "emoji": "💎"
    }
}

# Sample Maid Data
MAID_TEMPLATES = {
    # UR Maids (6 maids - 2 buffs each)
    "rem_ur": {
        "name": "Rem",
        "full_name": "Rem the Devoted Maid",
        "rarity": "UR", 
        "description": "Cô hầu gái tận tâm với sức mạnh oni và tình yêu bất diệt",
        "emoji": "💙",
        "possible_buffs": ["yield_boost", "sell_price", "growth_speed"],
        "art_url": "https://media.discordapp.net/attachments/1173415199043239947/1387927655201902732/Rem.jpg?ex=685f1fdb&is=685dce5b&hm=5d9f9d72ffb6288db68c4c02595ac20c275913d5daf15508cbc9a21f54e7e3aa&=&format=webp&width=570&height=856",  # Placeholder - replace with actual
        "series": "Re:Zero"
    },
    "saber_ur": {
        "name": "Saber",
        "full_name": "Artoria Pendragon the King of Knights",
        "rarity": "UR",
        "description": "Vua của các hiệp sĩ với thanh kiếm thiêng liêng Excalibur",
        "emoji": "⚔️",
        "possible_buffs": ["growth_speed", "yield_boost", "sell_price"],
        "art_url": "https://media.discordapp.net/attachments/1173415199043239947/1387927656179302542/Saber_Artoria.jpg?ex=685f1fdb&is=685dce5b&hm=f8244bbca19a19c8da6704978c08ca667b66c4bb5ad88908a8bae8e2c6343712&=&format=webp&width=592&height=856",  # Replace with actual Saber image
        "series": "Fate/Stay Night"
    },
    "rias_ur": {
        "name": "Rias",
        "full_name": "Rias Gremory the Devil Princess",
        "rarity": "UR",
        "description": "Công chúa quỷ với sức mạnh hủy diệt và trái tim nhân hậu",
        "emoji": "👹",
        "possible_buffs": ["sell_price", "seed_discount", "yield_boost"],
        "art_url": "https://media.discordapp.net/attachments/1173415199043239947/1387927655843627128/Rias_Gremory.jpg?ex=685f1fdb&is=685dce5b&hm=4822615d7728d1fa765f8272d1a4e0b6166991c96d93e73324c2ccb282accaac&=&format=webp&width=650&height=856"
    },
    "emilia_ur": {
        "name": "Emilia",
        "full_name": "Emilia the Half-Elf Princess",
        "rarity": "UR",
        "description": "Công chúa bán elf với ma thuật băng và trái tim trong sáng",
        "emoji": "❄️",
        "possible_buffs": ["growth_speed", "seed_discount", "yield_boost"],
        "art_url": "https://media.discordapp.net/attachments/1173415199043239947/1387927653926965310/Emilia.jpg?ex=685f1fdb&is=685dce5b&hm=a96f2881766ae4d8fbb125559c1f6b8f6351108044c231053d530eafd8c9ea0d&=&format=webp&width=586&height=855"
    },
    "yoshino_ur": {
        "name": "Yoshino",
        "full_name": "Yoshino the Gentle Spirit",
        "rarity": "UR",
        "description": "Linh hồn hiền lành với sức mạnh băng giá và con thỏ Yoshinon",
        "emoji": "🐰",
        "possible_buffs": ["growth_speed", "yield_boost", "seed_discount"],
        "art_url": "https://media.discordapp.net/attachments/1173415199043239947/1387927656594542652/Yoshino.jpg?ex=685f1fdb&is=685dce5b&hm=0efe8cc3a6c503e70c2fd24ecdfe33f12c57f54427ebba9b48a7b6315f423da1&=&format=webp&width=570&height=856"
    },
    "kurumi_ur": {
        "name": "Kurumi",
        "full_name": "Kurumi Tokisaki the Nightmare",
        "rarity": "UR",
        "description": "Linh hồn thời gian với khả năng thao túng thời gian tuyệt đối",
        "emoji": "🕰️",
        "possible_buffs": ["growth_speed", "sell_price", "yield_boost"],
        "art_url": "https://media.discordapp.net/attachments/1173415199043239947/1387927654522687599/Kurumi_Tokisaki.jpg?ex=685f1fdb&is=685dce5b&hm=d885172efab97e155ed641648cba3e73f2dab8546de6a8ba98910c3d5bec0edc&=&format=webp&width=602&height=855",
        "series": "Date A Live"
    },
    "jalter_gr": {
        "name": "Jeanne d'Arc Alter",
        "full_name": "Jeanne d'Arc Alter the Dragon Witch",
        "rarity": "GR",
        "description": "Phiên bản tà ác của thánh nữ Orleans với quyền năng rồng và lửa địa ngục - GHOST RARE",
        "emoji": "🔥",
        "possible_buffs": ["sell_price", "yield_boost", "growth_speed"],  # 3 buffs for GR
        "art_url": "https://media.discordapp.net/attachments/1173415199043239947/1387683466820452415/Jeanne_dArc_Alter.jpg?ex=685ee530&is=685d93b0&hm=5cf04653e003b4e7ca5cf75b4e545cc5e92cd023b7fee3adef43d6886c569c9d&=&format=webp",
        "series": "Fate/Grand Order",
        "limited_only": True,  # 🌟 LIMITED BANNER ONLY
        "banner_featured": False  # Không featured mặc định
    },
    "kotori_gr": {
        "name": "Kotori",
        "full_name": "Kotori Itsuka the Spirit Sister",
        "rarity": "GR",
        "description": "Cô em gái đáng yêu với quyền năng của Ifrit - GHOST RARE",
        "emoji": "🍡",
        "possible_buffs": ["growth_speed", "yield_boost", "sell_price"],  # 3 buffs for GR
        "art_url": "https://media.discordapp.net/attachments/1173415199043239947/1387683467172646933/Kotori_itsuka.jpg?ex=685e3c70&is=685ceaf0&hm=59f11fcec933090af2d036675c33e6538e35d6cbcca8b908c444ba0f4beb047c&=&format=webp&width=600&height=855",
        "series": "Date A Live",
        "limited_only": True,  # 🌟 LIMITED BANNER ONLY
        "banner_featured": True  # Featured mặc định cho Kotori
    },

    # SSR Maids (10 maids - 1 buff each)
    "mikasa_ssr": {
        "name": "Mikasa",
        "full_name": "Mikasa Ackerman the Strongest Soldier",
        "rarity": "SSR",
        "description": "Chiến binh mạnh nhất nhân loại với tốc độ và sức mạnh kinh hoàng",
        "emoji": "⚡",
        "possible_buffs": ["growth_speed"],
        "art_url": "https://media.discordapp.net/attachments/1173415199043239947/1386870505033961602/Mikasa_Ackerman.jpg?ex=685b474f&is=6859f5cf&hm=5a8e69c2c5117d05e1c91ae44fecee4674fb7b8e0012468e35509cd08532684e&=&format=webp&width=481&height=856"
    },
    "asuna_ssr": {
        "name": "Asuna",
        "full_name": "Asuna Yuuki the Lightning Flash",
        "rarity": "SSR",
        "description": "Tia chớp của SAO với kỹ năng đấu kiếm tuyệt vời",
        "emoji": "💫",
        "possible_buffs": ["growth_speed"],
        "art_url": "https://media.discordapp.net/attachments/1173415199043239947/1386870453884158023/Asuna_Yuuki.jpg?ex=685b4743&is=6859f5c3&hm=c39ab7d30ad414bc142d37a3c6adaa8c357baafcaced5f02fcef343bb4364680&=&format=webp&width=685&height=856"
    },
    "zero_two_ssr": {
        "name": "Zero Two",
        "full_name": "Zero Two the Darling in the FranXX",
        "rarity": "SSR",
        "description": "Cô gái lai oni với đôi sừng đáng yêu và tính cách nổi loạn",
        "emoji": "🦋",
        "possible_buffs": ["yield_boost"],
        "art_url": "https://media.discordapp.net/attachments/1173415199043239947/1386870685028188272/Zero_Two.jpg?ex=685b477a&is=6859f5fa&hm=4a48df6f3048964db7a68ca1784a6da0516920f048ca5908456f8aaf9dcbf3d3&=&format=webp&width=510&height=856"
    },
    "violet_ssr": {
        "name": "Violet",
        "full_name": "Violet Evergarden the Auto Memory Doll",
        "rarity": "SSR",
        "description": "Búp bê ký ức tự động với khả năng viết thư tuyệt vời",
        "emoji": "📝",
        "possible_buffs": ["sell_price"],
        "art_url": "https://media.discordapp.net/attachments/1173415199043239947/1386870682943492097/Violet_Evergarden.webp?ex=685b4779&is=6859f5f9&hm=8437d50d2c31a39f59ebcb18a5420ae2e1fd4a7b8eaddaf161c137f0fd98a460&=&format=webp&width=662&height=856"
    },
    "kurisu_ssr": {
        "name": "Kurisu",
        "full_name": "Kurisu Makise the Genius Scientist",
        "rarity": "SSR",
        "description": "Nhà khoa học thiên tài chuyên về thời gian du hành",
        "emoji": "🧪",
        "possible_buffs": ["seed_discount"],
        "art_url": "https://media.discordapp.net/attachments/1173415199043239947/1386870502621970523/Kurisu_Makise.jpg?ex=685b474e&is=6859f5ce&hm=b3e950cae954510ab16df8e0377c8275441e8f7607a5c99afa2261181d16fce2&=&format=webp&width=685&height=856"
    },
    "makima_ssr": {
        "name": "Makima",
        "full_name": "Makima the Control Devil",
        "rarity": "SSR",
        "description": "Quỷ kiểm soát với sức mạnh thao túng tuyệt đối",
        "emoji": "👁️",
        "possible_buffs": ["sell_price"],
        "art_url": "https://media.discordapp.net/attachments/1173415199043239947/1386870504115277864/Makima.webp?ex=685b474e&is=6859f5ce&hm=202b238fe62b8c9a152e1d05a424074e11143ecb3baf90168101e451b221662b&=&format=webp&width=482&height=856"
    },
    "yor_ssr": {
        "name": "Yor",
        "full_name": "Yor Forger the Thorn Princess",
        "rarity": "SSR",
        "description": "Công chúa gai với kỹ năng ám sát đỉnh cao",
        "emoji": "🌹",
        "possible_buffs": ["growth_speed"],
        "art_url": "https://media.discordapp.net/attachments/1294342075541753936/1387128548661268672/Yor_Forger.jpg?ex=685c37a1&is=685ae621&hm=21bf3ee1df7401b13cbc0763754055d4ee00e5a8c6375d73dcbabbad9b5b75a6&=&format=webp&width=734&height=960"
    },
    "kaguya_ssr": {
        "name": "Kaguya",
        "full_name": "Kaguya Shinomiya the Ice Princess",
        "rarity": "SSR",
        "description": "Công chúa băng giá với trí tuệ và kiêu hãnh tuyệt đối",
        "emoji": "🏰",
        "possible_buffs": ["seed_discount"],
        "art_url": "https://media.discordapp.net/attachments/1173415199043239947/1386870502274109582/Kaguya_Shinomiya.jpg?ex=685b474e&is=6859f5ce&hm=0ca3c68c511d38cb53030004d5318642f1f863323c8ef6d1d2d942c97bf09503&=&format=webp&width=584&height=856"
    },
    "tatsumaki_ssr": {
        "name": "Tatsumaki",
        "full_name": "Tatsumaki the Tornado of Terror",
        "rarity": "SSR",
        "description": "Siêu anh hùng esper với sức mạnh tâm linh khủng khiếp",
        "emoji": "🌪️",
        "possible_buffs": ["yield_boost"],
        "art_url": "https://media.discordapp.net/attachments/1294342075541753936/1387122701797294272/Tatsumaki.jpg?ex=685c322f&is=685ae0af&hm=7c9a35f9348c5b2ed0b2eb4e64ea458cdfbdcf248fff8d38b6e89726219ac8b2&=&format=webp&width=657&height=960"
    },
    "megumin_ssr": {
        "name": "Megumin",
        "full_name": "Megumin the Explosion Wizard",
        "rarity": "SSR",
        "description": "Phù thủy nổ chuyên về ma pháp explosion duy nhất",
        "emoji": "💥",
        "possible_buffs": ["yield_boost"],
        "art_url": "https://media.discordapp.net/attachments/1173415199043239947/1386870504681504881/Megumin.jpeg?ex=685b474f&is=6859f5cf&hm=348c79d84a58eaeedf3f5bdde555ece71262e394244e36f9dde123aa30c55811&=&format=webp&width=619&height=856"
    },

    # SR Maids (15 maids - 1 buff each)
    "usagi_sr": {
        "name": "Usagi",
        "full_name": "Usagi Tsukino Sailor Moon",
        "rarity": "SR",
        "description": "Chiến binh Sailor Moon bảo vệ tình yêu và công lý",
        "emoji": "🌙",
        "possible_buffs": ["growth_speed"],
        "art_url": "https://media.discordapp.net/attachments/1173415199043239947/1386870682356547685/Usagi_Tsukino.jpg?ex=685b4779&is=6859f5f9&hm=25a41ab796cfbe6286f405b06d7834ca3c9ccbdd66072895cc5c5c18c51cb5ae&=&format=webp&width=605&height=855"
    },
    "hinata_sr": {
        "name": "Hinata",
        "full_name": "Hinata Hyuga the Byakugan Princess",
        "rarity": "SR",
        "description": "Công chúa Byakugan với tính cách nhút nhát nhưng mạnh mẽ",
        "emoji": "👁️‍🗨️",
        "possible_buffs": ["seed_discount"],
        "art_url": "https://media.discordapp.net/attachments/1173415199043239947/1386872902799986869/Hinata_Hyuga.webp?ex=685b498a&is=6859f80a&hm=b2cc07a5c27d2355b240a9cdf4a7fab9a5d91c3d14f23b1c35bdc9f097ffdefb&=&format=webp"
    },
    "nezuko_sr": {
        "name": "Nezuko",
        "full_name": "Nezuko Kamado the Demon Sister",
        "rarity": "SR",
        "description": "Cô em gái quỷ với khả năng thu nhỏ và tình yêu thương",
        "emoji": "🎋",
        "possible_buffs": ["yield_boost"],
        "art_url": "https://media.discordapp.net/attachments/1173415199043239947/1386870549367492688/Nezuko_Kamado.jpg?ex=685b4759&is=6859f5d9&hm=ef93fa83e226f4f5aa7e643b21361e994b865fc66df40ed4dc8660fb609c09f4&=&format=webp&width=606&height=856"
    },
    "mai_sr": {
        "name": "Mai",
        "full_name": "Sakurajima Mai the Bunny Girl Senpai",
        "rarity": "SR",
        "description": "Nữ diễn viên nổi tiếng với hiện tượng không gian lạ",
        "emoji": "🐰",
        "possible_buffs": ["sell_price"],
        "art_url": "https://media.discordapp.net/attachments/1173415199043239947/1386870609094381588/Sakurajima_Mai.webp?ex=685b4768&is=6859f5e8&hm=0d5e2162bd282df358fee1d80603f90b3d4ad9f2fed17ce5cc8bb8701ed0ff3d&=&format=webp&width=481&height=856"
    },
    "hitagi_sr": {
        "name": "Hitagi",
        "full_name": "Hitagi Senjougahara the Tsundere Queen",
        "rarity": "SR",
        "description": "Nữ hoàng tsundere với lời nói sắc bén như dao",
        "emoji": "✂️",
        "possible_buffs": ["sell_price"],
        "art_url": "https://media.discordapp.net/attachments/1173415199043239947/1386870455855485140/Hitagi_Senjougahara.jpg?ex=685b4743&is=6859f5c3&hm=ffe10fd2acc286b2e8aca8a6b63839d56b4fafb297d2dc3a2636225a7efc1405&=&format=webp&width=634&height=856"
    },
    "erza_sr": {
        "name": "Erza",
        "full_name": "Erza Scarlet the Titania",
        "rarity": "SR",
        "description": "Nữ hoàng tiên nữ với ma pháp thay đổi áo giáp",
        "emoji": "🛡️",
        "possible_buffs": ["growth_speed"],
        "art_url": "https://media.discordapp.net/attachments/1173415199043239947/1386870455192784986/Erza_Scarlet.jpg?ex=685b4743&is=6859f5c3&hm=1b477aef71d431f6e2a986bea06fb0bb5492617eef09385956420cb54d3d9da6&=&format=webp&width=481&height=856"
    },
    "nami_sr": {
        "name": "Nami",
        "full_name": "Nami the Cat Burglar Navigator",
        "rarity": "SR",
        "description": "Hàng hải của băng Mũ Rơm với tài năng định hướng",
        "emoji": "🗺️",
        "possible_buffs": ["seed_discount"],
        "art_url": "https://media.discordapp.net/attachments/1173415199043239947/1386870548860113018/Nami.jpg?ex=685b4759&is=6859f5d9&hm=23b0595536171a4d897a867ad98142d4675c15f720ff61f57841b08c3d02969f&=&format=webp"
    },
    "robin_sr": {
        "name": "Robin",
        "full_name": "Nico Robin the Devil Child",
        "rarity": "SR",
        "description": "Khảo cổ học gia với trái ác quỷ Hana Hana",
        "emoji": "🌸",
        "possible_buffs": ["yield_boost"],
        "art_url": "https://media.discordapp.net/attachments/1173415199043239947/1386870549619281950/Nico_Robin.jpg?ex=685b4759&is=6859f5d9&hm=3db0a455064b73f280c5e1511524bb8b5e727c569454d15ac721c9f81e53c643&=&format=webp"
    },
    "komi_sr": {
        "name": "Komi",
        "full_name": "Shoko Komi the Communication Goddess",
        "rarity": "SR",
        "description": "Nữ thần giao tiếp với vẻ đẹp tuyệt trần nhưng sợ nói chuyện",
        "emoji": "📱",
        "possible_buffs": ["sell_price"],
        "art_url": "https://media.discordapp.net/attachments/1173415199043239947/1386870610214387813/Shoko_Komi.webp?ex=685b4768&is=6859f5e8&hm=7d1d718809933bcac2cd6f0be2e997967682e2ef294e060c4c9822d7b40341be&=&format=webp&width=577&height=856"
    },
    "chihiro_sr": {
        "name": "Chihiro",
        "full_name": "Chihiro Ogino the Spirited Girl",
        "rarity": "SR",
        "description": "Cô bé dũng cảm trong thế giới thần linh",
        "emoji": "🐲",
        "possible_buffs": ["growth_speed"],
        "art_url": "https://media.discordapp.net/attachments/1173415199043239947/1386870454349730003/Chihiro_Ogino.jpg?ex=685b4743&is=6859f5c3&hm=3441b4bef47ae1b4bfe8917091fe3bb52323d34a0a40404fb292434394b15c04&=&format=webp&width=602&height=855"
    },
    "rei_sr": {
        "name": "Rei",
        "full_name": "Rei Ayanami the First Child",
        "rarity": "SR",
        "description": "Pilot Eva đầu tiên với tính cách lạnh lùng bí ẩn",
        "emoji": "🤖",
        "possible_buffs": ["seed_discount"],
        "art_url": "https://media.discordapp.net/attachments/1294342075541753936/1387125073885921301/76ac0aa7aea76205fcaece3a021ca457.jpg?ex=685c3465&is=685ae2e5&hm=3a9e235e27803124f5419579a950417e5f5432ce0198a4034a1091be88fa5747&=&format=webp&width=591&height=960"
    },
    "asuka_sr": {
        "name": "Asuka",
        "full_name": "Asuka Langley Soryu the Second Child",
        "rarity": "SR",
        "description": "Pilot Eva thứ hai với tính cách mạnh mẽ và kiêu hãnh",
        "emoji": "🔥",
        "possible_buffs": ["yield_boost"],
        "art_url": "https://media.discordapp.net/attachments/1294342075541753936/1387127701969834135/Asuka_Langley_.jpg?ex=685c36d7&is=685ae557&hm=88449a725a0e7c3e30faa791c3816927a62fb52b009994aef711f71f632d8940&=&format=webp&width=677&height=960"
    },
    "shinobu_sr": {
        "name": "Shinobu",
        "full_name": "Shinobu Kocho the Insect Hashira",
        "rarity": "SR",
        "description": "Trụ côn trùng với nụ cười dịu dàng và độc tính chết người",
        "emoji": "🦋",
        "possible_buffs": ["sell_price"],
        "art_url": "https://media.discordapp.net/attachments/1173415199043239947/1386870609895493753/Shinobu_Kocho.jpg?ex=685b4768&is=6859f5e8&hm=42cf5c066caab7ffd9ba5e77a5f6fef630641b3edefe9eb52a714868dc95e5fc&=&format=webp&width=583&height=856"
    },
    "mitsuri_sr": {
        "name": "Mitsuri",
        "full_name": "Mitsuri Kanroji the Love Hashira",
        "rarity": "SR",
        "description": "Trụ tình yêu với sức mạnh khổng lồ và trái tim nhân hậu",
        "emoji": "💗",
        "possible_buffs": ["yield_boost"],
        "art_url": "https://media.discordapp.net/attachments/1173415199043239947/1386870547979436042/Mitsuri_Kanroji.webp?ex=685b4759&is=6859f5d9&hm=4dc66db2477b2644cdadf1337ddddacda9f21ce336be516d652752a598eaa8f2&=&format=webp&width=478&height=856"
    },
    "power_sr": {
        "name": "Power",
        "full_name": "Power the Blood Devil",
        "rarity": "SR",
        "description": "Quỷ máu với tính cách ích kỷ nhưng đáng yêu",
        "emoji": "🩸",
        "possible_buffs": ["growth_speed"],
        "art_url": "https://media.discordapp.net/attachments/1173415199043239947/1386870550357475399/Power.jpg?ex=685b475a&is=6859f5da&hm=5ec3c3712b0bcee58ecf33a1fdf8e8a7cee6214829aeb17a26782e6a562d1c87&=&format=webp&width=605&height=856"
    },

    # R Maids (19 maids - 1 buff each)
    "android18_r": {
        "name": "Android 18",
        "full_name": "Android 18 the Infinite Energy",
        "rarity": "R",
        "description": "Cyborg với năng lượng vô hạn và sức mạnh khủng khiếp",
        "emoji": "🤖",
        "possible_buffs": ["growth_speed"],
        "art_url": "https://media.discordapp.net/attachments/1173415199043239947/1386870453204947004/Android_18.jpg?ex=685b4742&is=6859f5c2&hm=4094cb5e34a9e87d4fdc424486c2bcd52b4c6867147e2f339957a5985412e466&=&format=webp&width=605&height=856"
    },
    "rukia_r": {
        "name": "Rukia",
        "full_name": "Rukia Kuchiki the Soul Reaper",
        "rarity": "R",
        "description": "Thần chết với Zanpakuto băng tuyết Sode no Shirayuki",
        "emoji": "❄️",
        "possible_buffs": ["seed_discount"],
        "art_url": "https://media.discordapp.net/attachments/1173415199043239947/1386870608045805649/Rukia_Kuchiki.webp?ex=685b4767&is=6859f5e7&hm=032641179dc877d83c01003137799b15dbd042ed7e190d643bb0c3f183eb21eb&=&format=webp&width=685&height=856"
    },
    "venus_r": {
        "name": "Venus",
        "full_name": "Sailor Venus the Guardian of Love",
        "rarity": "R",
        "description": "Chiến binh Sailor Venus bảo vệ tình yêu và vẻ đẹp",
        "emoji": "💛",
        "possible_buffs": ["yield_boost"],
        "art_url": "https://media.discordapp.net/attachments/1173415199043239947/1386870608729739455/Sailor_Venus.avif?ex=685b4767&is=6859f5e7&hm=08ce4a8269845288fb564d777e483a428330423dfd1c495f76c18e5929d548e4&=&format=webp&quality=lossless"
    },
    "tohru_r": {
        "name": "Tohru",
        "full_name": "Tohru Honda the Kind Heart",
        "rarity": "R",
        "description": "Cô gái với trái tim nhân hậu và khả năng chữa lành",
        "emoji": "🌻",
        "possible_buffs": ["sell_price"],
        "art_url": "https://media.discordapp.net/attachments/1173415199043239947/1386870681827807262/Tohru_Honda.jpg?ex=685b4779&is=6859f5f9&hm=166f88be6af4efb151531a6657334eadbf75a9de2c50619d1fd921ae935b09d4&=&format=webp"
    },
    "kagome_r": {
        "name": "Kagome",
        "full_name": "Kagome Higurashi the Time Traveler",
        "rarity": "R",
        "description": "Nữ sinh du hành thời gian với mũi tên thiêng liêng",
        "emoji": "🏹",
        "possible_buffs": ["growth_speed"],
        "art_url": "https://media.discordapp.net/attachments/1173415199043239947/1386870501317677086/Kagome_Higurashi.webp?ex=685b474e&is=6859f5ce&hm=fae8ac9c853aa536bbf3e91c1bab7d959d919c016034230fcac7fd5dfa555ab8&=&format=webp"
    },
    "yuno_r": {
        "name": "Yuno",
        "full_name": "Yuno Gasai the Yandere Queen",
        "rarity": "R",
        "description": "Nữ hoàng yandere với tình yêu ám ảnh và dao găm",
        "emoji": "🔪",
        "possible_buffs": ["sell_price"],
        "art_url": "https://media.discordapp.net/attachments/1173415199043239947/1386870684743106630/Yuno_Gasai.jpg?ex=685b477a&is=6859f5fa&hm=e15cd883fa7b1d855d4277d390ed103343492655700c832a1c3bf414fa4db8c7&=&format=webp&width=481&height=856"
    },
    "holo_r": {
        "name": "Holo",
        "full_name": "Holo the Wise Wolf",
        "rarity": "R",
        "description": "Sói thông thái của thu hoạch với kiến thức kinh tế",
        "emoji": "🐺",
        "possible_buffs": ["seed_discount"],
        "art_url": "https://media.discordapp.net/attachments/1173415199043239947/1387124618124333157/Holo.jpg?ex=685c33f8&is=685ae278&hm=7f82d0712d57b8122912a7ccba0e9e142fddba1db0496b626e3b8f6ea7599fef&=&format=webp&width=576&height=960"
    },
    "vivi_r": {
        "name": "Vivi",
        "full_name": "Nefertari Vivi the Desert Princess",
        "rarity": "R",
        "description": "Công chúa sa mạc với trái tim vì dân tộc",
        "emoji": "🏜️",
        "possible_buffs": ["yield_boost"],
        "art_url": "https://media.discordapp.net/attachments/1173415199043239947/1386870549128675348/Nefertari_Vivi.jpg?ex=685b4759&is=6859f5d9&hm=45175bee6f4c94a76f92be3515238e908c0417aa8b645d12e1f96a4610f168ed&=&format=webp&width=642&height=856"
    },
    "revy_r": {
        "name": "Revy",
        "full_name": "Revy the Two Hand",
        "rarity": "R",
        "description": "Tay súng lừng danh với đôi súng lục Beretta",
        "emoji": "🔫",
        "possible_buffs": ["growth_speed"],
        "art_url": "https://media.discordapp.net/attachments/1173415199043239947/1386870607160938576/Revy.webp?ex=685b4767&is=6859f5e7&hm=91d95db1b81aa369ca2cc2c54132d215bc3966b138c30080b8ba8da63af44ccc&=&format=webp"
    },
    "jolyne_r": {
        "name": "Jolyne",
        "full_name": "Jolyne Cujoh the Stone Free",
        "rarity": "R",
        "description": "Con gái của Jotaro với Stand Stone Free",
        "emoji": "🕷️",
        "possible_buffs": ["sell_price"],
        "art_url": "https://media.discordapp.net/attachments/1173415199043239947/1386870456388157470/Jolyne_Cujoh.jpg?ex=685b4743&is=6859f5c3&hm=1d5ef9bd0cd198e03460de93873f1c7b840fc41ba66db5afd25f5ece4a4c8e46&=&format=webp"
    },
    "nobara_r": {
        "name": "Nobara",
        "full_name": "Nobara Kugisaki the Straw Doll",
        "rarity": "R",
        "description": "Phù thủy búp bê rơm với búa và đinh thép",
        "emoji": "🔨",
        "possible_buffs": ["yield_boost"],
        "art_url": "https://media.discordapp.net/attachments/1173415199043239947/1386870549904621661/Nobara_Kugisaki.jpg?ex=685b4759&is=6859f5d9&hm=48b705bda7a7fe6da8aa6cad09703d2b8332df5de5b1ba4969f1464dc482b4b6&=&format=webp&width=605&height=856"
    },
    "mio_r": {
        "name": "Mio",
        "full_name": "Mio Akiyama the Bass Guitarist",
        "rarity": "R",
        "description": "Tay bass shycore với mái tóc đen dài",
        "emoji": "🎸",
        "possible_buffs": ["seed_discount"],
        "art_url": "https://media.discordapp.net/attachments/1173415199043239947/1386870505306325062/Mio_Akiyama.jpg?ex=685b474f&is=6859f5cf&hm=9b357f58ccde0040cc101aabcd1f7f06007e5746233823dceb6cf143362e4d75&=&format=webp&width=481&height=855"
    },
    "sheryl_r": {
        "name": "Sheryl",
        "full_name": "Sheryl Nome the Galactic Fairy",
        "rarity": "R",
        "description": "Nàng tiên thiên hà với giọng hát mê hoặc",
        "emoji": "🎤",
        "possible_buffs": ["sell_price"],
        "art_url": "https://media.discordapp.net/attachments/1173415199043239947/1386870609392304180/Sheryl_Nome.webp?ex=685b4768&is=6859f5e8&hm=e8028f09c1e9007fe359f2139ad3de85d3e6322d5ac35a6ca00512ce988a134b&=&format=webp"
    },
    "lina_r": {
        "name": "Lina",
        "full_name": "Lina Inverse the Dragon Spooker",
        "rarity": "R",
        "description": "Phù thủy hủy diệt với Dragon Slave tuyệt đỉnh",
        "emoji": "🐲",
        "possible_buffs": ["growth_speed"],
        "art_url": "https://media.discordapp.net/attachments/1173415199043239947/1386870503813283991/Lina_Inverse.jpg?ex=685b474e&is=6859f5ce&hm=f50892be26b9295caaac0561b50a2fe855f6d72ed9de53aa86e041c63f033d44&=&format=webp&width=564&height=856"
    },
    "kagura_r": {
        "name": "Kagura",
        "full_name": "Kagura shikigami",
        "rarity": "R",
        "description": "Shikigami xinh xắn, đáng yêu",
        "emoji": "☂️",
        "possible_buffs": ["yield_boost"],
        "art_url": "https://media.discordapp.net/attachments/1173415199043239947/1386870501976047626/Kagura.png?ex=685b474e&is=6859f5ce&hm=3f2995224caa79ff0a22270bf6f895620db13e8e39a7d94176203637a381f196&=&format=webp&quality=lossless"
    },
    "motoko_r": {
        "name": "Motoko",
        "full_name": "Motoko Kusanagi the Major",
        "rarity": "R",
        "description": "Thiếu tá cyborg trong thế giới công nghệ cao",
        "emoji": "🔬",
        "possible_buffs": ["seed_discount"],
        "art_url": "https://media.discordapp.net/attachments/1173415199043239947/1386870548629295135/Motoko_Kusanagi.jpg?ex=685b4759&is=6859f5d9&hm=4f1c780232bf0cb2356891eefe5560d20c813b9a1f9af49b99be32496d81db60&=&format=webp&width=590&height=856"
    },
    "yoruichi_r": {
        "name": "Yoruichi",
        "full_name": "Yoruichi Shihouin the Flash Goddess",
        "rarity": "R",
        "description": "Nữ thần tốc độ với khả năng biến hình mèo",
        "emoji": "🐱",
        "possible_buffs": ["growth_speed"],
        "art_url": "https://media.discordapp.net/attachments/1173415199043239947/1386870683908313088/Yoruichi_Shihouin.jpeg?ex=685b4779&is=6859f5f9&hm=4db365b6bbca1db03794b6da709af9d9a272554195f10c56e21540a82dfa15f6&=&format=webp&width=595&height=855"
    },
    "esdeath_r": {
        "name": "Esdeath",
        "full_name": "Esdeath the Ice Queen General",
        "rarity": "R",
        "description": "Nữ tướng băng giá với sức mạnh tuyệt đối",
        "emoji": "🧊",
        "possible_buffs": ["sell_price"],
        "art_url": "https://media.discordapp.net/attachments/1173415199043239947/1387124577724797011/Esdeath.jpg?ex=685c33ee&is=685ae26e&hm=7703de348911c92ae0bd67087e02000d1d8c887afaeedf79e2d2e7ffe69f8781&=&format=webp&width=657&height=960"
    },
    "tsunade_r": {
        "name": "Tsunade",
        "full_name": "Tsunade Senju the Legendary Sannin",
        "rarity": "R",
        "description": "Một trong ba Sannin huyền thoại với sức mạnh khủng khiếp",
        "emoji": "👑",
        "possible_buffs": ["yield_boost"],
        "art_url": "https://media.discordapp.net/attachments/1173415199043239947/1386870682037518416/Tsunade_Senju.jpg?ex=685b4779&is=6859f5f9&hm=30867deac805b7eb23d318c1282a960de9fdbd7a89f79dd1543b27bc7f35d85e&=&format=webp"
    }
}

def get_random_maid_by_individual_rates() -> str:
    """
    🎯 NEW: Roll một maid cụ thể dựa trên individual rates
    Mỗi maid có rate riêng = total_rate / maid_count của rarity đó
    
    Returns:
        maid_id của maid được roll
    """
    # Tạo weighted list của tất cả maids
    weighted_maids = []
    
    for maid_id, template in MAID_TEMPLATES.items():
        rarity = template["rarity"]
        individual_rate = RARITY_CONFIG[rarity]["individual_rate"]
        
        # Thêm vào list với weight = individual_rate (chuyển % thành decimal)
        weighted_maids.append((maid_id, individual_rate))
    
    # Tính total weight
    total_weight = sum(weight for _, weight in weighted_maids)
    
    # Random selection
    rand = random.random() * total_weight
    current_weight = 0
    
    for maid_id, weight in weighted_maids:
        current_weight += weight
        if rand <= current_weight:
            return maid_id
    
    # Fallback - return random R maid nếu có lỗi
    r_maids = [maid_id for maid_id, template in MAID_TEMPLATES.items() 
               if template["rarity"] == "R"]
    return random.choice(r_maids) if r_maids else "tsunade_r"

def get_all_maid_rates() -> Dict[str, float]:
    """
    📊 Lấy tất cả individual rates của từng maid
    
    Returns:
        Dict với key = maid_id, value = individual_rate
    """
    rates = {}
    for maid_id, template in MAID_TEMPLATES.items():
        rarity = template["rarity"]
        individual_rate = RARITY_CONFIG[rarity]["individual_rate"]
        rates[maid_id] = individual_rate
    
    return rates

def get_rarity_by_rate() -> str:
    """🔄 LEGACY: Random rarity dựa theo total rates (for backwards compatibility)"""
    rand = random.uniform(0, 100)
    
    if rand <= RARITY_CONFIG["UR"]["total_rate"]:
        return "UR"
    elif rand <= RARITY_CONFIG["UR"]["total_rate"] + RARITY_CONFIG["SSR"]["total_rate"]:
        return "SSR"
    elif rand <= (RARITY_CONFIG["UR"]["total_rate"] + 
                  RARITY_CONFIG["SSR"]["total_rate"] + 
                  RARITY_CONFIG["SR"]["total_rate"]):
        return "SR"
    else:
        return "R"

def get_maids_by_rarity(rarity: str) -> List[str]:
    """🔄 LEGACY: Lấy danh sách maid_id theo rarity"""
    return [maid_id for maid_id, data in MAID_TEMPLATES.items() 
            if data["rarity"] == rarity]

def generate_random_buffs(maid_id: str) -> List[Dict[str, Any]]:
    """Generate random buffs cho maid với validation"""
    template = MAID_TEMPLATES[maid_id]
    rarity = template["rarity"]
    rarity_config = RARITY_CONFIG[rarity]
    
    # Số lượng buff
    buff_count = rarity_config["buff_count"]
    
    # Chọn random buff types
    available_buffs = template["possible_buffs"]
    selected_buffs = random.sample(available_buffs, min(buff_count, len(available_buffs)))
    
    # 🛡️ Buff caps per type để tránh overpowered
    BUFF_CAPS = {
        "growth_speed": 80.0,      # Max 80% faster growth
        "seed_discount": 90.0,     # Max 90% discount
        "yield_boost": 200.0,      # Max 200% more yield
        "sell_price": 150.0        # Max 150% sell price
    }
    
    # Generate random values
    buffs = []
    for buff_type in selected_buffs:
        min_val, max_val = rarity_config["buff_range"]
        
        # 🛡️ Apply caps
        if buff_type in BUFF_CAPS:
            max_val = min(max_val, BUFF_CAPS[buff_type])
        
        value = round(random.uniform(min_val, max_val), 1)
        
        # 🛡️ Ensure positive values
        value = max(0.1, value)
        
        buffs.append({
            "buff_type": buff_type,
            "value": value,
            "description": f"{BUFF_TYPES[buff_type]['name']}: +{value}%"
        })
    
    return buffs

# UI Configuration
UI_CONFIG = {
    "maids_per_page": 6,        # Số maid hiển thị mỗi page
    "trades_per_page": 5,       # Số trade hiển thị mỗi page
    "history_per_page": 10,     # Số lịch sử hiển thị mỗi page
}

# Legacy Maid ID Mapping (for backwards compatibility)
LEGACY_MAID_MAPPING = {
    "jalter_ur": "jalter_gr",  # Old Jalter UR → New Jalter GR
    # Add more legacy mappings as needed
}

# Emoji cho rarity
RARITY_EMOJIS = {
    "GR": "👻",    # Ghost emoji cho Ghost Rare
    "UR": "💎",
    "SSR": "🌟", 
    "SR": "⭐",
    "R": "✨"
}

def get_regular_gacha_pool() -> Dict[str, Dict]:
    """🎯 Lấy pool gacha thường (exclude limited-only characters)"""
    regular_pool = {}
    for maid_id, template in MAID_TEMPLATES.items():
        # Exclude limited-only characters khỏi gacha thường
        if not template.get("limited_only", False):
            regular_pool[maid_id] = template
    return regular_pool

def get_limited_banner_pool() -> Dict[str, Dict]:
    """🌟 Lấy pool limited banner (include ALL characters)"""
    return MAID_TEMPLATES.copy()  # Limited banner có access tất cả characters

def get_featured_characters() -> List[str]:
    """⭐ Lấy danh sách featured characters trong limited banner"""
    featured = []
    for maid_id, template in MAID_TEMPLATES.items():
        if template.get("banner_featured", False):
            featured.append(maid_id)
    return featured

def get_random_maid_regular_gacha() -> str:
    """🎰 Roll maid từ regular gacha pool (exclude limited-only)"""
    regular_pool = get_regular_gacha_pool()
    
    # Tạo weighted list exclude limited characters
    weighted_maids = []
    for maid_id, template in regular_pool.items():
        rarity = template["rarity"]
        individual_rate = RARITY_CONFIG[rarity]["individual_rate"]
        weighted_maids.append((maid_id, individual_rate))
    
    # Random selection
    total_weight = sum(weight for _, weight in weighted_maids)
    rand = random.random() * total_weight
    current_weight = 0
    
    for maid_id, weight in weighted_maids:
        current_weight += weight
        if rand <= current_weight:
            return maid_id
    
    # Fallback
    regular_r_maids = [maid_id for maid_id, template in regular_pool.items() 
                       if template["rarity"] == "R"]
    return random.choice(regular_r_maids) if regular_r_maids else "tsunade_r"

def get_random_maid_limited_banner() -> str:
    """🌟 Roll maid từ limited banner với rate-up và featured"""
    if not LIMITED_BANNER_CONFIG["enabled"]:
        return get_random_maid_regular_gacha()  # Fallback to regular nếu banner tắt
    
    featured_chars = get_featured_characters()
    rand = random.uniform(0, 100)
    
    # Determine rarity với limited rates
    if rand <= LIMITED_RARITY_CONFIG["GR"]["total_rate"]:
        # GR tier - GHOST RARE!
        featured_grs = [maid_id for maid_id in featured_chars 
                       if MAID_TEMPLATES[maid_id]["rarity"] == "GR"]
        if featured_grs:
            return random.choice(featured_grs)
        
        # Fallback to UR if no GR available (shouldn't happen)
        regular_urs = [maid_id for maid_id, template in MAID_TEMPLATES.items() 
                       if template["rarity"] == "UR" and not template.get("limited_only", False)]
        return random.choice(regular_urs) if regular_urs else "rem_ur"
        
    elif rand <= LIMITED_RARITY_CONFIG["GR"]["total_rate"] + LIMITED_RARITY_CONFIG["UR"]["total_rate"]:
        # UR tier (no featured URs anymore, all Jalter moved to GR)
        regular_urs = [maid_id for maid_id, template in MAID_TEMPLATES.items() 
                       if template["rarity"] == "UR" and not template.get("limited_only", False)]
        return random.choice(regular_urs) if regular_urs else "rem_ur"
        
    elif rand <= (LIMITED_RARITY_CONFIG["GR"]["total_rate"] + 
                  LIMITED_RARITY_CONFIG["UR"]["total_rate"] + 
                  LIMITED_RARITY_CONFIG["SSR"]["total_rate"]):
        # SSR tier
        ssrs = [maid_id for maid_id, template in MAID_TEMPLATES.items() 
                if template["rarity"] == "SSR"]
        return random.choice(ssrs) if ssrs else "mikasa_ssr"
        
    elif rand <= (LIMITED_RARITY_CONFIG["GR"]["total_rate"] + 
                  LIMITED_RARITY_CONFIG["UR"]["total_rate"] + 
                  LIMITED_RARITY_CONFIG["SSR"]["total_rate"] + 
                  LIMITED_RARITY_CONFIG["SR"]["total_rate"]):
        # SR tier
        srs = [maid_id for maid_id, template in MAID_TEMPLATES.items() 
               if template["rarity"] == "SR"]
        return random.choice(srs) if srs else "usagi_sr"
    else:
        # R tier
        rs = [maid_id for maid_id, template in MAID_TEMPLATES.items() 
              if template["rarity"] == "R"]
        return random.choice(rs) if rs else "tsunade_r"

def is_limited_banner_active() -> bool:
    """🕐 Check xem limited banner có đang active không"""
    return LIMITED_BANNER_CONFIG["enabled"]

def get_limited_banner_info() -> Dict:
    """ℹ️ Lấy thông tin limited banner hiện tại"""
    return {
        "enabled": LIMITED_BANNER_CONFIG["enabled"],
        "banner_name": LIMITED_BANNER_CONFIG["banner_name"],
        "description": LIMITED_BANNER_CONFIG["banner_description"],
        "featured_characters": get_featured_characters(),
        "single_cost": LIMITED_BANNER_CONFIG["single_roll_cost"],
        "ten_cost": LIMITED_BANNER_CONFIG["ten_roll_cost"],
        "ur_rate": LIMITED_RARITY_CONFIG["UR"]["total_rate"],
        "featured_rate": LIMITED_RARITY_CONFIG["UR"]["featured_rate"]
    }

def get_maid_template_safe(maid_id: str) -> Dict:
    """🛡️ Safely get maid template with legacy support"""
    # Check if maid_id exists directly
    if maid_id in MAID_TEMPLATES:
        return MAID_TEMPLATES[maid_id]
    
    # Check legacy mapping
    if maid_id in LEGACY_MAID_MAPPING:
        new_maid_id = LEGACY_MAID_MAPPING[maid_id]
        if new_maid_id in MAID_TEMPLATES:
            return MAID_TEMPLATES[new_maid_id]
    
    # Return None if not found
    return None 

# 🎪 MULTI-BANNER SYSTEM FUNCTIONS
def get_current_banner() -> str:
    """🎯 Lấy banner hiện tại đang active"""
    return ACTIVE_BANNER_CONFIG.get("current_banner", "kotori")

def set_active_banner(banner_id: str) -> bool:
    """🎯 Set banner active (admin command)"""
    if banner_id not in BANNER_CONFIGS:
        return False
    
    # Update active banner config
    ACTIVE_BANNER_CONFIG["current_banner"] = banner_id
    ACTIVE_BANNER_CONFIG["enabled"] = True
    
    # Update legacy config để backward compatibility
    banner_config = BANNER_CONFIGS[banner_id]
    LIMITED_BANNER_CONFIG.update({
        "enabled": True,
        "banner_name": banner_config["banner_name"],
        "single_roll_cost": banner_config["single_roll_cost"],
        "ten_roll_cost": banner_config["ten_roll_cost"],
        "banner_description": banner_config["banner_description"],
        "background_color": banner_config["background_color"]
    })
    
    # Update featured characters
    featured_char = banner_config["featured_character"]
    for maid_id, template in MAID_TEMPLATES.items():
        # Reset tất cả featured flags
        if "banner_featured" in template:
            template["banner_featured"] = False
        
        # Set featured cho character được chọn
        if maid_id == featured_char:
            template["banner_featured"] = True
    
    return True

def disable_active_banner() -> bool:
    """🚫 Tắt banner hiện tại"""
    ACTIVE_BANNER_CONFIG["enabled"] = False
    LIMITED_BANNER_CONFIG["enabled"] = False
    
    # Reset tất cả featured flags
    for maid_id, template in MAID_TEMPLATES.items():
        if "banner_featured" in template:
            template["banner_featured"] = False
    
    return True

def get_banner_info(banner_id: str = None) -> Dict:
    """ℹ️ Lấy thông tin banner theo ID hoặc current banner"""
    if banner_id is None:
        banner_id = get_current_banner()
    
    if banner_id not in BANNER_CONFIGS:
        return None
    
    banner_config = BANNER_CONFIGS[banner_id]
    featured_char = banner_config["featured_character"]
    
    return {
        "banner_id": banner_id,
        "banner_name": banner_config["banner_name"],
        "description": banner_config["banner_description"],
        "featured_character": featured_char,
        "featured_name": MAID_TEMPLATES[featured_char]["name"],
        "featured_emoji": MAID_TEMPLATES[featured_char]["emoji"],
        "single_cost": banner_config["single_roll_cost"],
        "ten_cost": banner_config["ten_roll_cost"],
        "background_color": banner_config["background_color"],
        "theme_emoji": banner_config["theme_emoji"],
        "enabled": ACTIVE_BANNER_CONFIG["enabled"] and get_current_banner() == banner_id
    }

def get_all_banner_list() -> List[Dict]:
    """📋 Lấy danh sách tất cả banners available"""
    banners = []
    for banner_id in BANNER_CONFIGS:
        banner_info = get_banner_info(banner_id)
        if banner_info:
            banners.append(banner_info)
    return banners

def get_random_maid_multi_banner() -> str:
    """🎰 Roll maid từ multi-banner system"""
    if not ACTIVE_BANNER_CONFIG["enabled"]:
        return get_random_maid_regular_gacha()
    
    current_banner = get_current_banner()
    banner_config = BANNER_CONFIGS[current_banner]
    featured_char = banner_config["featured_character"]
    
    # GR featured = 0.05% rate (exclusive)
    rand = random.uniform(0, 100)
    
    if rand <= LIMITED_RARITY_CONFIG["GR"]["total_rate"]:
        # GHOST RARE! Featured character only
        return featured_char
        
    elif rand <= LIMITED_RARITY_CONFIG["GR"]["total_rate"] + LIMITED_RARITY_CONFIG["UR"]["total_rate"]:
        # UR tier (exclude limited-only characters)
        regular_urs = [maid_id for maid_id, template in MAID_TEMPLATES.items() 
                       if template["rarity"] == "UR" and not template.get("limited_only", False)]
        return random.choice(regular_urs) if regular_urs else "rem_ur"
        
    elif rand <= (LIMITED_RARITY_CONFIG["GR"]["total_rate"] + 
                  LIMITED_RARITY_CONFIG["UR"]["total_rate"] + 
                  LIMITED_RARITY_CONFIG["SSR"]["total_rate"]):
        # SSR tier
        ssrs = [maid_id for maid_id, template in MAID_TEMPLATES.items() 
                if template["rarity"] == "SSR"]
        return random.choice(ssrs) if ssrs else "mikasa_ssr"
        
    elif rand <= (LIMITED_RARITY_CONFIG["GR"]["total_rate"] + 
                  LIMITED_RARITY_CONFIG["UR"]["total_rate"] + 
                  LIMITED_RARITY_CONFIG["SSR"]["total_rate"] + 
                  LIMITED_RARITY_CONFIG["SR"]["total_rate"]):
        # SR tier
        srs = [maid_id for maid_id, template in MAID_TEMPLATES.items() 
               if template["rarity"] == "SR"]
        return random.choice(srs) if srs else "usagi_sr"
    else:
        # R tier
        rs = [maid_id for maid_id, template in MAID_TEMPLATES.items() 
              if template["rarity"] == "R"]
        return random.choice(rs) if rs else "tsunade_r"