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
    "UR": {
        "buff_count": 2,
        "buff_range": (30, 50),    # % buff power
        "total_rate": 0.1,         # 0.1% total rate cho UR
        "maid_count": 6,           # 6 UR maids
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
        "UR": 100,      # Tách UR = 100 bụi sao
        "SSR": 50,      # Tách SSR = 50 bụi sao  
        "SR": 25,       # Tách SR = 25 bụi sao
        "R": 10,        # Tách R = 10 bụi sao
    },
    "reroll_costs": {
        "UR": 80,       # Reroll UR maid = 80 bụi sao
        "SSR": 40,      # Reroll SSR maid = 40 bụi sao
        "SR": 20,       # Reroll SR maid = 20 bụi sao
        "R": 8          # Reroll R maid = 8 bụi sao
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
        "art_url": "art/maids_cropped/rem-ur.jpg",  # Placeholder - replace with actual
        "series": "Re:Zero"
    },
    "saber_ur": {
        "name": "Saber",
        "full_name": "Artoria Pendragon the King of Knights",
        "rarity": "UR",
        "description": "Vua của các hiệp sĩ với thanh kiếm thiêng liêng Excalibur",
        "emoji": "⚔️",
        "possible_buffs": ["growth_speed", "yield_boost", "sell_price"],
        "art_url": "art/maids_cropped/saber-ur.jpg",  # Replace with actual Saber image
        "series": "Fate/Stay Night"
    },
    "rias_ur": {
        "name": "Rias",
        "full_name": "Rias Gremory the Devil Princess",
        "rarity": "UR",
        "description": "Công chúa quỷ với sức mạnh hủy diệt và trái tim nhân hậu",
        "emoji": "👹",
        "possible_buffs": ["sell_price", "seed_discount", "yield_boost"],
        "art_url": "art/maids_cropped/rias-ur.jpg"
    },
    "emilia_ur": {
        "name": "Emilia",
        "full_name": "Emilia the Half-Elf Princess",
        "rarity": "UR",
        "description": "Công chúa bán elf với ma thuật băng và trái tim trong sáng",
        "emoji": "❄️",
        "possible_buffs": ["growth_speed", "seed_discount", "yield_boost"],
        "art_url": "art/maids_cropped/emilia-ur.jpg"
    },
    "yoshino_ur": {
        "name": "Yoshino",
        "full_name": "Yoshino the Gentle Spirit",
        "rarity": "UR",
        "description": "Linh hồn hiền lành với sức mạnh băng giá và con thỏ Yoshinon",
        "emoji": "🐰",
        "possible_buffs": ["growth_speed", "yield_boost", "seed_discount"],
        "art_url": "art/maids_cropped/yoshino-ur.jpg"
    },
    "kurumi_ur": {
        "name": "Kurumi",
        "full_name": "Kurumi Tokisaki the Nightmare",
        "rarity": "UR",
        "description": "Linh hồn thời gian với khả năng thao túng thời gian tuyệt đối",
        "emoji": "🕰️",
        "possible_buffs": ["growth_speed", "sell_price", "yield_boost"],
        "art_url": "art/maids_cropped/kurumi-ur.jpg"
    },

    # SSR Maids (10 maids - 1 buff each)
    "mikasa_ssr": {
        "name": "Mikasa",
        "full_name": "Mikasa Ackerman the Strongest Soldier",
        "rarity": "SSR",
        "description": "Chiến binh mạnh nhất nhân loại với tốc độ và sức mạnh kinh hoàng",
        "emoji": "⚡",
        "possible_buffs": ["growth_speed"],
        "art_url": "art/maids_cropped/mikasa-ssr.jpg"
    },
    "asuna_ssr": {
        "name": "Asuna",
        "full_name": "Asuna Yuuki the Lightning Flash",
        "rarity": "SSR",
        "description": "Tia chớp của SAO với kỹ năng đấu kiếm tuyệt vời",
        "emoji": "💫",
        "possible_buffs": ["growth_speed"],
        "art_url": "art/maids_cropped/asuna-ssr.jpg"
    },
    "zero_two_ssr": {
        "name": "Zero Two",
        "full_name": "Zero Two the Darling in the FranXX",
        "rarity": "SSR",
        "description": "Cô gái lai oni với đôi sừng đáng yêu và tính cách nổi loạn",
        "emoji": "🦋",
        "possible_buffs": ["yield_boost"],
        "art_url": "art/maids_cropped/zero-two-ssr.jpg"
    },
    "violet_ssr": {
        "name": "Violet",
        "full_name": "Violet Evergarden the Auto Memory Doll",
        "rarity": "SSR",
        "description": "Búp bê ký ức tự động với khả năng viết thư tuyệt vời",
        "emoji": "📝",
        "possible_buffs": ["sell_price"],
        "art_url": "art/maids_cropped/violet-ssr.jpg"
    },
    "kurisu_ssr": {
        "name": "Kurisu",
        "full_name": "Kurisu Makise the Genius Scientist",
        "rarity": "SSR",
        "description": "Nhà khoa học thiên tài chuyên về thời gian du hành",
        "emoji": "🧪",
        "possible_buffs": ["seed_discount"],
        "art_url": "art/maids_cropped/kurisu-ssr.jpg"
    },
    "makima_ssr": {
        "name": "Makima",
        "full_name": "Makima the Control Devil",
        "rarity": "SSR",
        "description": "Quỷ kiểm soát với sức mạnh thao túng tuyệt đối",
        "emoji": "👁️",
        "possible_buffs": ["sell_price"],
        "art_url": "art/maids_cropped/makima-ssr.jpg"
    },
    "yor_ssr": {
        "name": "Yor",
        "full_name": "Yor Forger the Thorn Princess",
        "rarity": "SSR",
        "description": "Công chúa gai với kỹ năng ám sát đỉnh cao",
        "emoji": "🌹",
        "possible_buffs": ["growth_speed"],
        "art_url": "art/maids_cropped/yor-ssr.jpg"
    },
    "kaguya_ssr": {
        "name": "Kaguya",
        "full_name": "Kaguya Shinomiya the Ice Princess",
        "rarity": "SSR",
        "description": "Công chúa băng giá với trí tuệ và kiêu hãnh tuyệt đối",
        "emoji": "🏰",
        "possible_buffs": ["seed_discount"],
        "art_url": "art/maids_cropped/kaguya-ssr.jpg"
    },
    "tatsumaki_ssr": {
        "name": "Tatsumaki",
        "full_name": "Tatsumaki the Tornado of Terror",
        "rarity": "SSR",
        "description": "Siêu anh hùng esper với sức mạnh tâm linh khủng khiếp",
        "emoji": "🌪️",
        "possible_buffs": ["yield_boost"],
        "art_url": "art/maids_cropped/tatsumaki-ssr.jpg"
    },
    "megumin_ssr": {
        "name": "Megumin",
        "full_name": "Megumin the Explosion Wizard",
        "rarity": "SSR",
        "description": "Phù thủy nổ chuyên về ma pháp explosion duy nhất",
        "emoji": "💥",
        "possible_buffs": ["yield_boost"],
        "art_url": "art/maids_cropped/megumin-ssr.jpg"
    },

    # SR Maids (15 maids - 1 buff each)
    "usagi_sr": {
        "name": "Usagi",
        "full_name": "Usagi Tsukino Sailor Moon",
        "rarity": "SR",
        "description": "Chiến binh Sailor Moon bảo vệ tình yêu và công lý",
        "emoji": "🌙",
        "possible_buffs": ["growth_speed"],
        "art_url": "art/maids_cropped/usagi-sr.jpg"
    },
    "hinata_sr": {
        "name": "Hinata",
        "full_name": "Hinata Hyuga the Byakugan Princess",
        "rarity": "SR",
        "description": "Công chúa Byakugan với tính cách nhút nhát nhưng mạnh mẽ",
        "emoji": "👁️‍🗨️",
        "possible_buffs": ["seed_discount"],
        "art_url": "art/maids_cropped/hinata-sr.jpg"
    },
    "nezuko_sr": {
        "name": "Nezuko",
        "full_name": "Nezuko Kamado the Demon Sister",
        "rarity": "SR",
        "description": "Cô em gái quỷ với khả năng thu nhỏ và tình yêu thương",
        "emoji": "🎋",
        "possible_buffs": ["yield_boost"],
        "art_url": "art/maids_cropped/nezuko-sr.jpg"
    },
    "mai_sr": {
        "name": "Mai",
        "full_name": "Sakurajima Mai the Bunny Girl Senpai",
        "rarity": "SR",
        "description": "Nữ diễn viên nổi tiếng với hiện tượng không gian lạ",
        "emoji": "🐰",
        "possible_buffs": ["sell_price"],
        "art_url": "art/maids_cropped/mai-sr.jpg"
    },
    "hitagi_sr": {
        "name": "Hitagi",
        "full_name": "Hitagi Senjougahara the Tsundere Queen",
        "rarity": "SR",
        "description": "Nữ hoàng tsundere với lời nói sắc bén như dao",
        "emoji": "✂️",
        "possible_buffs": ["sell_price"],
        "art_url": "art/maids_cropped/hitagi-sr.jpg"
    },
    "erza_sr": {
        "name": "Erza",
        "full_name": "Erza Scarlet the Titania",
        "rarity": "SR",
        "description": "Nữ hoàng tiên nữ với ma pháp thay đổi áo giáp",
        "emoji": "🛡️",
        "possible_buffs": ["growth_speed"],
        "art_url": "art/maids_cropped/erza-sr.jpg"
    },
    "nami_sr": {
        "name": "Nami",
        "full_name": "Nami the Cat Burglar Navigator",
        "rarity": "SR",
        "description": "Hàng hải của băng Mũ Rơm với tài năng định hướng",
        "emoji": "🗺️",
        "possible_buffs": ["seed_discount"],
        "art_url": "art/maids_cropped/nami-sr.jpg"
    },
    "robin_sr": {
        "name": "Robin",
        "full_name": "Nico Robin the Devil Child",
        "rarity": "SR",
        "description": "Khảo cổ học gia với trái ác quỷ Hana Hana",
        "emoji": "🌸",
        "possible_buffs": ["yield_boost"],
        "art_url": "art/maids_cropped/robin-sr.jpg"
    },
    "komi_sr": {
        "name": "Komi",
        "full_name": "Shoko Komi the Communication Goddess",
        "rarity": "SR",
        "description": "Nữ thần giao tiếp với vẻ đẹp tuyệt trần nhưng sợ nói chuyện",
        "emoji": "📱",
        "possible_buffs": ["sell_price"],
        "art_url": "art/maids_cropped/komi-sr.jpg"
    },
    "chihiro_sr": {
        "name": "Chihiro",
        "full_name": "Chihiro Ogino the Spirited Girl",
        "rarity": "SR",
        "description": "Cô bé dũng cảm trong thế giới thần linh",
        "emoji": "🐲",
        "possible_buffs": ["growth_speed"],
        "art_url": "art/maids_cropped/chihiro-sr.jpg"
    },
    "rei_sr": {
        "name": "Rei",
        "full_name": "Rei Ayanami the First Child",
        "rarity": "SR",
        "description": "Pilot Eva đầu tiên với tính cách lạnh lùng bí ẩn",
        "emoji": "🤖",
        "possible_buffs": ["seed_discount"],
        "art_url": "art/maids_cropped/rei-sr.jpg"
    },
    "asuka_sr": {
        "name": "Asuka",
        "full_name": "Asuka Langley Soryu the Second Child",
        "rarity": "SR",
        "description": "Pilot Eva thứ hai với tính cách mạnh mẽ và kiêu hãnh",
        "emoji": "🔥",
        "possible_buffs": ["yield_boost"],
        "art_url": "art/maids_cropped/asuka-sr.jpg"
    },
    "shinobu_sr": {
        "name": "Shinobu",
        "full_name": "Shinobu Kocho the Insect Hashira",
        "rarity": "SR",
        "description": "Trụ côn trùng với nụ cười dịu dàng và độc tính chết người",
        "emoji": "🦋",
        "possible_buffs": ["sell_price"],
        "art_url": "art/maids_cropped/shinobu-sr.jpg"
    },
    "mitsuri_sr": {
        "name": "Mitsuri",
        "full_name": "Mitsuri Kanroji the Love Hashira",
        "rarity": "SR",
        "description": "Trụ tình yêu với sức mạnh khổng lồ và trái tim nhân hậu",
        "emoji": "💗",
        "possible_buffs": ["yield_boost"],
        "art_url": "art/maids_cropped/mitsuri-sr.jpg"
    },
    "power_sr": {
        "name": "Power",
        "full_name": "Power the Blood Devil",
        "rarity": "SR",
        "description": "Quỷ máu với tính cách ích kỷ nhưng đáng yêu",
        "emoji": "🩸",
        "possible_buffs": ["growth_speed"],
        "art_url": "art/maids_cropped/power-sr.jpg"
    },

    # R Maids (19 maids - 1 buff each)
    "android18_r": {
        "name": "Android 18",
        "full_name": "Android 18 the Infinite Energy",
        "rarity": "R",
        "description": "Cyborg với năng lượng vô hạn và sức mạnh khủng khiếp",
        "emoji": "🤖",
        "possible_buffs": ["growth_speed"],
        "art_url": "art/maids_cropped/android18-r.jpg"
    },
    "rukia_r": {
        "name": "Rukia",
        "full_name": "Rukia Kuchiki the Soul Reaper",
        "rarity": "R",
        "description": "Thần chết với Zanpakuto băng tuyết Sode no Shirayuki",
        "emoji": "❄️",
        "possible_buffs": ["seed_discount"],
        "art_url": "art/maids_cropped/rukia-r.jpg"
    },
    "venus_r": {
        "name": "Venus",
        "full_name": "Sailor Venus the Guardian of Love",
        "rarity": "R",
        "description": "Chiến binh Sailor Venus bảo vệ tình yêu và vẻ đẹp",
        "emoji": "💛",
        "possible_buffs": ["yield_boost"],
        "art_url": "art/maids_cropped/venus-r.jpg"
    },
    "tohru_r": {
        "name": "Tohru",
        "full_name": "Tohru Honda the Kind Heart",
        "rarity": "R",
        "description": "Cô gái với trái tim nhân hậu và khả năng chữa lành",
        "emoji": "🌻",
        "possible_buffs": ["sell_price"],
        "art_url": "art/maids_cropped/tohru-r.jpg"
    },
    "kagome_r": {
        "name": "Kagome",
        "full_name": "Kagome Higurashi the Time Traveler",
        "rarity": "R",
        "description": "Nữ sinh du hành thời gian với mũi tên thiêng liêng",
        "emoji": "🏹",
        "possible_buffs": ["growth_speed"],
        "art_url": "art/maids_cropped/kagome-r.jpg"
    },
    "yuno_r": {
        "name": "Yuno",
        "full_name": "Yuno Gasai the Yandere Queen",
        "rarity": "R",
        "description": "Nữ hoàng yandere với tình yêu ám ảnh và dao găm",
        "emoji": "🔪",
        "possible_buffs": ["sell_price"],
        "art_url": "art/maids_cropped/yuno-r.jpg"
    },
    "holo_r": {
        "name": "Holo",
        "full_name": "Holo the Wise Wolf",
        "rarity": "R",
        "description": "Sói thông thái của thu hoạch với kiến thức kinh tế",
        "emoji": "🐺",
        "possible_buffs": ["seed_discount"],
        "art_url": "art/maids_cropped/holo-r.jpg"
    },
    "vivi_r": {
        "name": "Vivi",
        "full_name": "Nefertari Vivi the Desert Princess",
        "rarity": "R",
        "description": "Công chúa sa mạc với trái tim vì dân tộc",
        "emoji": "🏜️",
        "possible_buffs": ["yield_boost"],
        "art_url": "art/maids_cropped/vivi-r.jpg"
    },
    "revy_r": {
        "name": "Revy",
        "full_name": "Revy the Two Hand",
        "rarity": "R",
        "description": "Tay súng lừng danh với đôi súng lục Beretta",
        "emoji": "🔫",
        "possible_buffs": ["growth_speed"],
        "art_url": "art/maids_cropped/revy-r.jpg"
    },
    "jolyne_r": {
        "name": "Jolyne",
        "full_name": "Jolyne Cujoh the Stone Free",
        "rarity": "R",
        "description": "Con gái của Jotaro với Stand Stone Free",
        "emoji": "🕷️",
        "possible_buffs": ["sell_price"],
        "art_url": "art/maids_cropped/jolyne-r.jpg"
    },
    "nobara_r": {
        "name": "Nobara",
        "full_name": "Nobara Kugisaki the Straw Doll",
        "rarity": "R",
        "description": "Phù thủy búp bê rơm với búa và đinh thép",
        "emoji": "🔨",
        "possible_buffs": ["yield_boost"],
        "art_url": "art/maids_cropped/nobara-r.jpg"
    },
    "mio_r": {
        "name": "Mio",
        "full_name": "Mio Akiyama the Bass Guitarist",
        "rarity": "R",
        "description": "Tay bass shycore với mái tóc đen dài",
        "emoji": "🎸",
        "possible_buffs": ["seed_discount"],
        "art_url": "art/maids_cropped/mio-r.jpg"
    },
    "sheryl_r": {
        "name": "Sheryl",
        "full_name": "Sheryl Nome the Galactic Fairy",
        "rarity": "R",
        "description": "Nàng tiên thiên hà với giọng hát mê hoặc",
        "emoji": "🎤",
        "possible_buffs": ["sell_price"],
        "art_url": "art/maids_cropped/sheryl-r.jpg"
    },
    "lina_r": {
        "name": "Lina",
        "full_name": "Lina Inverse the Dragon Spooker",
        "rarity": "R",
        "description": "Phù thủy hủy diệt với Dragon Slave tuyệt đỉnh",
        "emoji": "🐲",
        "possible_buffs": ["growth_speed"],
        "art_url": "art/maids_cropped/lina-r.jpg"
    },
    "kagura_r": {
        "name": "Kagura",
        "full_name": "Kagura shikigami",
        "rarity": "R",
        "description": "Shikigami xinh xắn, đáng yêu",
        "emoji": "☂️",
        "possible_buffs": ["yield_boost"],
        "art_url": "art/maids_cropped/kagura-r.jpg"
    },
    "motoko_r": {
        "name": "Motoko",
        "full_name": "Motoko Kusanagi the Major",
        "rarity": "R",
        "description": "Thiếu tá cyborg trong thế giới công nghệ cao",
        "emoji": "🔬",
        "possible_buffs": ["seed_discount"],
        "art_url": "art/maids_cropped/motoko-r.jpg"
    },
    "yoruichi_r": {
        "name": "Yoruichi",
        "full_name": "Yoruichi Shihouin the Flash Goddess",
        "rarity": "R",
        "description": "Nữ thần tốc độ với khả năng biến hình mèo",
        "emoji": "🐱",
        "possible_buffs": ["growth_speed"],
        "art_url": "art/maids_cropped/yoruichi-r.jpg"
    },
    "esdeath_r": {
        "name": "Esdeath",
        "full_name": "Esdeath the Ice Queen General",
        "rarity": "R",
        "description": "Nữ tướng băng giá với sức mạnh tuyệt đối",
        "emoji": "🧊",
        "possible_buffs": ["sell_price"],
        "art_url": "art/maids_cropped/esdeath-r.jpg"
    },
    "tsunade_r": {
        "name": "Tsunade",
        "full_name": "Tsunade Senju the Legendary Sannin",
        "rarity": "R",
        "description": "Một trong ba Sannin huyền thoại với sức mạnh khủng khiếp",
        "emoji": "👑",
        "possible_buffs": ["yield_boost"],
        "art_url": "art/maids_cropped/tsunade-r.jpg"
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

# Emoji cho rarity
RARITY_EMOJIS = {
    "UR": "💎",
    "SSR": "🌟", 
    "SR": "⭐",
    "R": "✨"
} 