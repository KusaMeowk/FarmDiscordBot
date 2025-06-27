import os
from dotenv import load_dotenv
import sys

load_dotenv()

# Discord Configuration
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
if not DISCORD_TOKEN:
    print("❌ DISCORD_TOKEN không được tìm thấy trong environment variables!")
    print("Vui lòng tạo file .env và thêm DISCORD_TOKEN=your_token_here")
    sys.exit(1)

PREFIX = os.getenv('PREFIX', 'f!')

OWNER_ID_STR = os.getenv('OWNER_ID', '0')
try:
    OWNER_ID = int(OWNER_ID_STR)
except ValueError:
    print(f"⚠️ OWNER_ID không hợp lệ: '{OWNER_ID_STR}'. Sử dụng 0 mặc định.")
    OWNER_ID = 0

# Database Configuration  
DATABASE_PATH = os.getenv('DATABASE_PATH', 'farm_bot.db')

# Weather API Configuration
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
WEATHER_API_URL = "http://api.openweathermap.org/data/2.5/weather"

# Game Configuration
INITIAL_MONEY = 1000
INITIAL_LAND_SLOTS = 4

# Daily Rewards Configuration
DAILY_BASE_REWARD = 100
DAILY_STREAK_BONUS = 50
DAILY_MAX_STREAK_BONUS = 1000
MAX_DAILY_STREAK = 30

# Crop Configuration
CROPS = {
    'carrot': {
        'name': '🥕 Cà rốt',
        'price': 10,
        'sell_price': 18,  # Tăng từ 12 → 18 (50% tăng)
        'growth_time': 300,  # 5 phút (giây)
        'yield_min': 1,
        'yield_max': 4  # Tăng từ 3 → 4
    },
    'tomato': {
        'name': '🍅 Cà chua', 
        'price': 25,
        'sell_price': 45,  # Tăng từ 30 → 45 (50% tăng)
        'growth_time': 600,  # 10 phút
        'yield_min': 1,  # Giảm từ 2 → 1
        'yield_max': 4   # Tăng từ 3 → 4
    },
    'corn': {
        'name': '🌽 Ngô',
        'price': 50,
        'sell_price': 100,  # Tăng từ 60 → 100 (67% tăng)
        'growth_time': 1200,  # 20 phút
        'yield_min': 1,  # Giảm từ 3 → 1  
        'yield_max': 4   # Tăng từ 3 → 4
    },
    'wheat': {
        'name': '🌾 Lúa mì',
        'price': 100,
        'sell_price': 200,  # Tăng từ 120 → 200 (67% tăng)
        'growth_time': 1800,  # 30 phút
        'yield_min': 1,  # Giảm từ 4 → 1
        'yield_max': 4   # Tăng từ 3 → 4
    },
    # === PREMIUM CROPS - Tier 2 ===
    'potato': {
        'name': '🥔 Khoai tây',
        'price': 200,
        'sell_price': 380,  # 1.9x ratio
        'growth_time': 2700,  # 45 phút
        'yield_min': 1,
        'yield_max': 4
    },
    'cabbage': {
        'name': '🥬 Bắp cải',
        'price': 350,
        'sell_price': 700,  # 2x ratio
        'growth_time': 3600,  # 1 giờ
        'yield_min': 1,
        'yield_max': 4
    },
    'eggplant': {
        'name': '🍆 Cà tím',
        'price': 500,
        'sell_price': 950,  # 1.9x ratio
        'growth_time': 4500,  # 1.25 giờ
        'yield_min': 1,
        'yield_max': 4
    },
    # === EXOTIC CROPS - Tier 3 ===
    'pumpkin': {
        'name': '🎃 Bí ngô',
        'price': 750,
        'sell_price': 1500,  # 2x ratio
        'growth_time': 5400,  # 1.5 giờ
        'yield_min': 1,
        'yield_max': 4
    },
    'grape': {
        'name': '🍇 Nho',
        'price': 1200,
        'sell_price': 2280,  # 1.9x ratio
        'growth_time': 7200,  # 2 giờ
        'yield_min': 1,
        'yield_max': 4
    },
    'strawberry': {
        'name': '🍓 Dâu tây',
        'price': 1800,
        'sell_price': 3600,  # 2x ratio
        'growth_time': 9000,  # 2.5 giờ
        'yield_min': 1,
        'yield_max': 4
    },
    # === LEGENDARY CROPS - Tier 4 ===
    'pineapple': {
        'name': '🍍 Dứa',
        'price': 2500,
        'sell_price': 4750,  # 1.9x ratio
        'growth_time': 10800,  # 3 giờ
        'yield_min': 1,
        'yield_max': 3
    },
    'watermelon': {
        'name': '🍉 Dưa hấu',
        'price': 3500,
        'sell_price': 7000,  # 2x ratio
        'growth_time': 14400,  # 4 giờ
        'yield_min': 1,
        'yield_max': 4
    },
    'avocado': {
        'name': '🥑 Bơ',
        'price': 5000,
        'sell_price': 9500,  # 1.9x ratio
        'growth_time': 18000,  # 5 giờ
        'yield_min': 1,
        'yield_max': 3
    },
    # === MYTHICAL CROPS - Tier 5 ===
    'dragon_fruit': {
        'name': '🐲 Thanh long',
        'price': 7500,
        'sell_price': 15000,  # 2x ratio
        'growth_time': 21600,  # 6 giờ
        'yield_min': 1,
        'yield_max': 4
    }
}

# Land Expansion Costs
LAND_COSTS = [500, 1000, 2500, 5000, 10000, 20000, 50000, 100000]

# Livestock Facility Upgrade Costs
POND_UPGRADE_COSTS = {
    2: 1000,   # Level 1 → 2
    3: 2500,   # Level 2 → 3
    4: 5000,   # Level 3 → 4
    5: 10000,  # Level 4 → 5
    6: 20000   # Level 5 → 6
}

BARN_UPGRADE_COSTS = {
    2: 1500,   # Level 1 → 2
    3: 3500,   # Level 2 → 3
    4: 7500,   # Level 3 → 4
    5: 15000,  # Level 4 → 5
    6: 30000   # Level 5 → 6
}

# Weather Effects
WEATHER_EFFECTS = {
    'sunny': {'growth_modifier': 1.2, 'yield_modifier': 1.1},      # Nắng - tốt cho phát triển
    'rainy': {'growth_modifier': 1.0, 'yield_modifier': 1.3},      # Mưa - tốt cho sản lượng
    'cloudy': {'growth_modifier': 0.9, 'yield_modifier': 1.0},     # Mây - trung bình
    'windy': {'growth_modifier': 1.1, 'yield_modifier': 0.95},     # Gió - tốt cho phát triển, hơi giảm sản lượng
    'storm': {'growth_modifier': 0.7, 'yield_modifier': 0.8},      # Bão - xấu cho cả hai
    'foggy': {'growth_modifier': 0.8, 'yield_modifier': 0.9},      # Sương mù - hạn chế ánh sáng
    'drought': {'growth_modifier': 0.6, 'yield_modifier': 0.7}     # Hạn hán - rất xấu
}

# ==================== LIVESTOCK CONFIGURATION ====================

# Fish Species Configuration
FISH_SPECIES = {
    # Tier 1 - Cá Cơ Bản
    'goldfish': {
        'name': '🐟 Cá Vàng',
        'tier': 1,
        'buy_price': 50,
        'sell_price': 80,
        'growth_time': 1800,  # 30 phút
        'special_ability': 'Dễ nuôi, ít bệnh',
        'emoji': '🐟'
    },
    'tropical_fish': {
        'name': '🐠 Cá Nhiệt Đới',
        'tier': 1,
        'buy_price': 80,
        'sell_price': 130,
        'growth_time': 2700,  # 45 phút
        'special_ability': 'Màu sắc đẹp, giá cao hơn',
        'emoji': '🐠'
    },
    'baby_shark': {
        'name': '🦈 Cá Mập Nhỏ',
        'tier': 1,
        'buy_price': 200,
        'sell_price': 350,
        'growth_time': 5400,  # 1.5 giờ
        'special_ability': 'Cần ao lớn, lợi nhuận cao',
        'emoji': '🦈'
    },
    
    # Tier 2 - Cá Cao Cấp
    'octopus': {
        'name': '🐙 Bạch Tuộc',
        'tier': 2,
        'buy_price': 300,
        'sell_price': 500,
        'growth_time': 7200,  # 2 giờ
        'special_ability': 'Cần nước sạch, bonus trí tuệ',
        'emoji': '🐙'
    },
    'squid': {
        'name': '🦑 Mực Ống',
        'tier': 2,
        'buy_price': 400,
        'sell_price': 700,
        'growth_time': 9000,  # 2.5 giờ
        'special_ability': 'Sản phẩm đặc biệt (mực khô)',
        'emoji': '🦑'
    },
    'pufferfish': {
        'name': '🐡 Cá Nóc',
        'tier': 2,
        'buy_price': 500,
        'sell_price': 900,
        'growth_time': 10800,  # 3 giờ
        'special_ability': 'Nguy hiểm nhưng giá trị cao',
        'emoji': '🐡'
    },
    
    # Tier 3 - Cá Huyền Thoại
    'baby_whale': {
        'name': '🐋 Cá Voi Nhỏ',
        'tier': 3,
        'buy_price': 1000,
        'sell_price': 2000,
        'growth_time': 21600,  # 6 giờ
        'special_ability': 'Cần ao khổng lồ, siêu lợi nhuận',
        'emoji': '🐋'
    },
    'seal': {
        'name': '🦭 Hải Cẩu',
        'tier': 3,
        'buy_price': 800,
        'sell_price': 1400,
        'growth_time': 14400,  # 4 giờ
        'special_ability': 'Có thể biểu diễn, thu nhập thêm',
        'emoji': '🦭'
    },
    'dolphin': {
        'name': '🐬 Cá Heo',
        'tier': 3,
        'buy_price': 1200,
        'sell_price': 2200,
        'growth_time': 18000,  # 5 giờ
        'special_ability': 'Thông minh, tăng EXP cho player',
        'emoji': '🐬'
    },
    'lobster': {
        'name': '🦞 Tôm Hùm',
        'tier': 3,
        'buy_price': 1500,
        'sell_price': 3000,
        'growth_time': 28800,  # 8 giờ
        'special_ability': 'Rare drop, cao cấp nhất',
        'emoji': '🦞'
    }
}

# Animal Species Configuration
ANIMAL_SPECIES = {
    # Tier 1 - Gia Súc Cơ Bản
    'pig': {
        'name': '🐷 Heo Con',
        'tier': 1,
        'buy_price': 150,
        'sell_price': 300,
        'growth_time': 7200,  # 2 giờ
        'special_ability': 'Sản xuất thịt heo',
        'emoji': '🐷'
    },
    'cow': {
        'name': '🐄 Bò Sữa',
        'tier': 1,
        'buy_price': 400,
        'sell_price': 700,
        'growth_time': 14400,  # 4 giờ
        'special_ability': 'Sản xuất sữa tươi',
        'emoji': '🐄'
    },
    'sheep': {
        'name': '🐑 Cừu Non',
        'tier': 1,
        'buy_price': 250,
        'sell_price': 450,
        'growth_time': 10800,  # 3 giờ
        'special_ability': 'Sản xuất len cừu',
        'emoji': '🐑'
    },
    
    # Tier 2 - Gia Cầm
    'chicken': {
        'name': '🐔 Gà Mái',
        'tier': 2,
        'buy_price': 100,
        'sell_price': 180,
        'growth_time': 3600,  # 1 giờ
        'special_ability': 'Sản xuất trứng gà',
        'emoji': '🐔'
    },
    'duck': {
        'name': '🦆 Vịt Trời',
        'tier': 2,
        'buy_price': 120,
        'sell_price': 220,
        'growth_time': 5400,  # 1.5 giờ
        'special_ability': 'Sản xuất trứng vịt',
        'emoji': '🦆'
    },
    'swan': {
        'name': '🦢 Thiên Nga',
        'tier': 2,
        'buy_price': 800,
        'sell_price': 1500,
        'growth_time': 21600,  # 6 giờ
        'special_ability': 'Trang trí, tăng giá trị trang trại',
        'emoji': '🦢'
    },
    
    # Tier 3 - Thú Cưng Cao Cấp
    'koala': {
        'name': '🐨 Gấu Koala',
        'tier': 3,
        'buy_price': 1000,
        'sell_price': 2000,
        'growth_time': 28800,  # 8 giờ
        'special_ability': 'Giảm stress cho player',
        'emoji': '🐨'
    },
    'elephant': {
        'name': '🐘 Voi Nhỏ',
        'tier': 3,
        'buy_price': 2000,
        'sell_price': 4000,
        'growth_time': 43200,  # 12 giờ
        'special_ability': 'Giúp làm việc, tăng hiệu suất',
        'emoji': '🐘'
    },
    'rhino': {
        'name': '🦏 Tê Giác',
        'tier': 3,
        'buy_price': 1500,
        'sell_price': 3000,
        'growth_time': 36000,  # 10 giờ
        'special_ability': 'Bảo vệ trang trại khỏi thiên tai',
        'emoji': '🦏'
    },
    'giraffe': {
        'name': '🦒 Hươu Cao Cổ',
        'tier': 3,
        'buy_price': 3000,
        'sell_price': 6000,
        'growth_time': 54000,  # 15 giờ
        'special_ability': 'Rare, prestige symbol',
        'emoji': '🦒'
    }
}

# Livestock Products Configuration
LIVESTOCK_PRODUCTS = {
    # Animal products
    'pig': {
        'product_name': 'Thịt Heo',
        'product_emoji': '🥩',
        'production_time': 14400,  # 4 giờ
        'sell_price': 50
    },
    'cow': {
        'product_name': 'Sữa Tươi',
        'product_emoji': '🥛',
        'production_time': 7200,  # 2 giờ
        'sell_price': 30
    },
    'sheep': {
        'product_name': 'Len Cừu',
        'product_emoji': '🧶',
        'production_time': 21600,  # 6 giờ
        'sell_price': 40
    },
    'chicken': {
        'product_name': 'Trứng Gà',
        'product_emoji': '🥚',
        'production_time': 1800,  # 30 phút
        'sell_price': 15
    },
    'duck': {
        'product_name': 'Trứng Vịt',
        'product_emoji': '🥚',
        'production_time': 2700,  # 45 phút
        'sell_price': 20
    }
}

# Legacy Facility Expansion Costs (for max slots calculation)
POND_EXPANSION_COSTS = [300, 600, 1200, 2500, 5000, 10000]  # Per level
BARN_EXPANSION_COSTS = [400, 800, 1600, 3200, 6400, 12800]  # Per level

# Initial Facility Configuration
INITIAL_POND_SLOTS = 2
INITIAL_BARN_SLOTS = 2

# Casino & Blackjack Configuration
CASINO_CONFIG = {
    "min_bet": 1000,
    "max_bet": 1000000,
    "house_edge": 0.02,  # 2% house edge
    "blackjack_payout": 1.5,  # 3:2 payout
    "cooldown": 3  # 3 seconds between games
}

# Emoji mapping for playing cards - Application Emojis uploaded!
CARD_EMOJIS = {
    # Spades (♠)
    "2_spades": 1186320677838883390,
    "3_spades": 1186320770483012348,
    "4_spades": 1186320843796406963,
    "5_spades": 1186320958450042,
    "6_spades": 1186321013408442323,
    "7_spades": 1186321073506486549,
    "8_spades": 1186321230965665499,
    "9_spades": 1186321280439662660,
    "10_spades": 1186321341773888256,
    "J_spades": 1186321444764422,
    "Q_spades": 1186321471268890318,
    "K_spades": 1186321506305014,
    "A_spades": 1186321070788070469,
    
    # Hearts (♥)
    "2_hearts": 1186321343658472,
    "3_hearts": 1186321458458176,
    "4_hearts": 1186321502730954966,
    "5_hearts": 1186321562640414390,
    "6_hearts": 1186321600925990,
    "7_hearts": 1186321649484934779,
    "8_hearts": 1186321707242537364,
    "9_hearts": 1186321757109555866,
    "10_hearts": 1186321864450159,
    "J_hearts": 1186321913056494779,
    "Q_hearts": 1186321946635966,
    "K_hearts": 1186321978183771770,
    "A_hearts": 1186321072333854404,
    
    # Diamonds (♦)
    "2_diamonds": 1186322065953586473,
    "3_diamonds": 1186322083198234071,
    "4_diamonds": 1186322110638244998,
    "5_diamonds": 1186322143038240608,
    "6_diamonds": 1186322168953382536,
    "7_diamonds": 1186322197918564927,
    "8_diamonds": 1186322227015254956,
    "9_diamonds": 1186322256845118,
    "10_diamonds": 1186322298855321,
    "J_diamonds": 1186322326446772752,
    "Q_diamonds": 1186322354788208,
    "K_diamonds": 1186322377268034671,
    "A_diamonds": 1186322394496906553,
    
    # Clubs (♣)
    "2_clubs": 1186322417946896303,
    "3_clubs": 1186322443539420647,
    "4_clubs": 1186322468330256003,
    "5_clubs": 1186322503856348390,
    "6_clubs": 1186322522971444,
    "7_clubs": 1186322555394176003,
    "8_clubs": 1186322580359046647,
    "9_clubs": 1186322605414390,
    "10_clubs": 1186322662297762,
    "J_clubs": 1186322686525014390,
    "Q_clubs": 1186322709895014310,
    "K_clubs": 1186322736460814390,
    "A_clubs": 1186322760285014930,
    
    # Special cards
    "card_back": 1186322044778607507,  # Back_cards từ hình ảnh
    "empty_slot": "⬜"  # Slot trống
} 