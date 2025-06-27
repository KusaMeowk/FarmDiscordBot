import random
from datetime import datetime, timedelta
from typing import Optional
import config

def calculate_yield_range(crop_type: str, weather_modifier: float = 1.0, event_modifier: float = 1.0) -> tuple[int, int]:
    """Calculate modified yield range (min, max) after applying all buffs/debuffs"""
    crop_config = config.CROPS.get(crop_type, {})
    base_min = crop_config.get('yield_min', 1)
    base_max = crop_config.get('yield_max', 1)
    
    # Tính toán combined modifier từ thời tiết và sự kiện
    combined_modifier = weather_modifier * event_modifier
    
    # Áp dụng modifier vào cả min và max
    modified_min = max(1, int(base_min * combined_modifier))
    modified_max = max(modified_min, int(base_max * combined_modifier))
    
    return modified_min, modified_max

def calculate_crop_yield(crop_type: str, weather_modifier: float = 1.0, event_modifier: float = 1.0) -> int:
    """Calculate crop yield based on type and modifiers using the new range system"""
    # Sử dụng range mới để tính yield
    min_yield, max_yield = calculate_yield_range(crop_type, weather_modifier, event_modifier)
    
    # Random trong range đã được modified
    final_yield = random.randint(min_yield, max_yield)
    
    return final_yield

def calculate_crop_price(crop_type: str, weather_modifier: float = 1.0) -> int:
    """Calculate crop selling price with weather effects"""
    crop_config = config.CROPS.get(crop_type, {})
    base_price = crop_config.get('sell_price', 10)
    
    # Weather can affect price slightly
    price_modifier = 0.8 + (weather_modifier * 0.4)  # Range: 0.8 - 1.2
    final_price = int(base_price * price_modifier)
    
    return max(1, final_price)

def calculate_growth_time(crop_type: str, weather_modifier: float = 1.0, event_modifier: float = 1.0, user_id: int = None) -> int:
    """Calculate actual growth time with modifiers"""
    crop_config = config.CROPS.get(crop_type, {})
    base_time = crop_config.get('growth_time', 300)
    
    # Combined modifier calculation
    combined_modifier = weather_modifier * event_modifier
    
    # Apply modifier logic correctly:
    # Higher modifier (>1.0) = bonus = faster growth = shorter time
    # Lower modifier (<1.0) = penalty = slower growth = longer time
    final_time = int(base_time / combined_modifier)
    
    # 🎀 Apply maid growth speed buff
    if user_id:
        try:
            from features.maid_helper import maid_helper
            final_time = maid_helper.apply_growth_speed_buff(user_id, final_time)
        except ImportError:
            pass  # Fallback if maid system not available
    
    return max(60, final_time)  # Minimum 1 minute

def is_crop_ready(plant_time: datetime, crop_type: str, weather_modifier: float = 1.0, event_modifier: float = 1.0, user_id: int = None) -> bool:
    """Check if crop is ready for harvest"""
    # 🔧 FIX: Sử dụng base growth time để tránh double modifier khi restart
    crop_config = config.CROPS.get(crop_type, {})
    base_growth_time = crop_config.get('growth_time', 300)
    
    # 🎀 Apply maid growth speed buff chỉ một lần
    if user_id:
        try:
            from features.maid_helper import maid_helper
            base_growth_time = maid_helper.apply_growth_speed_buff(user_id, base_growth_time)
        except ImportError:
            pass
    
    # Apply weather/event modifiers sau khi đã có maid buff
    combined_modifier = weather_modifier * event_modifier
    final_growth_time = int(base_growth_time / combined_modifier)
    final_growth_time = max(60, final_growth_time)  # Minimum 1 minute
    
    elapsed_time = (datetime.now() - plant_time).total_seconds()
    return elapsed_time >= final_growth_time

def get_crop_growth_progress(plant_time: datetime, crop_type: str, weather_modifier: float = 1.0, event_modifier: float = 1.0, user_id: int = None) -> float:
    """Get crop growth progress as percentage (0.0 - 1.0)"""
    # 🔧 FIX: Sử dụng logic tương tự như is_crop_ready
    crop_config = config.CROPS.get(crop_type, {})
    base_growth_time = crop_config.get('growth_time', 300)
    
    # 🎀 Apply maid growth speed buff chỉ một lần
    if user_id:
        try:
            from features.maid_helper import maid_helper
            base_growth_time = maid_helper.apply_growth_speed_buff(user_id, base_growth_time)
        except ImportError:
            pass
    
    # Apply weather/event modifiers sau khi đã có maid buff
    combined_modifier = weather_modifier * event_modifier
    final_growth_time = int(base_growth_time / combined_modifier)
    final_growth_time = max(60, final_growth_time)
    
    elapsed_time = (datetime.now() - plant_time).total_seconds()
    return min(elapsed_time / final_growth_time, 1.0)

def format_time_remaining(plant_time: datetime, crop_type: str, weather_modifier: float = 1.0, event_modifier: float = 1.0, user_id: int = None) -> str:
    """Format remaining time for crop growth"""
    # 🔧 FIX: Sử dụng logic tương tự như is_crop_ready
    crop_config = config.CROPS.get(crop_type, {})
    base_growth_time = crop_config.get('growth_time', 300)
    
    # 🎀 Apply maid growth speed buff chỉ một lần
    if user_id:
        try:
            from features.maid_helper import maid_helper
            base_growth_time = maid_helper.apply_growth_speed_buff(user_id, base_growth_time)
        except ImportError:
            pass
    
    # Apply weather/event modifiers sau khi đã có maid buff
    combined_modifier = weather_modifier * event_modifier
    final_growth_time = int(base_growth_time / combined_modifier)
    final_growth_time = max(60, final_growth_time)
    
    elapsed_time = (datetime.now() - plant_time).total_seconds()
    remaining_time = max(0, final_growth_time - elapsed_time)
    
    if remaining_time <= 0:
        return "Sẵn sàng thu hoạch!"
    
    hours = int(remaining_time // 3600)
    minutes = int((remaining_time % 3600) // 60)
    seconds = int(remaining_time % 60)
    
    if hours > 0:
        return f"{hours}h {minutes}p {seconds}s"
    elif minutes > 0:
        return f"{minutes}p {seconds}s"
    else:
        return f"{seconds}s"

def calculate_daily_reward(streak: int) -> int:
    """Calculate daily login reward based on streak"""
    base_reward = config.DAILY_REWARD_BASE
    streak_bonus = min(streak * 10, config.MAX_DAILY_STREAK * 10)
    
    return base_reward + streak_bonus

def calculate_land_expansion_cost(current_slots: int) -> Optional[int]:
    """Calculate cost for next land expansion"""
    expansion_level = current_slots - config.INITIAL_LAND_SLOTS
    
    if expansion_level >= len(config.LAND_COSTS):
        return None  # Max expansion reached
    
    return config.LAND_COSTS[expansion_level]

def get_weather_from_description(description: str) -> str:
    """Convert weather description to simplified weather type"""
    description = description.lower()
    
    if any(word in description for word in ['clear', 'sunny', 'sun']):
        return 'sunny'
    elif any(word in description for word in ['rain', 'drizzle', 'shower']):
        return 'rainy'
    elif any(word in description for word in ['storm', 'thunder']):
        return 'stormy'
    elif any(word in description for word in ['cloud', 'overcast']):
        return 'cloudy'
    else:
        return 'cloudy'  # Default

def generate_seasonal_event() -> dict:
    """Generate seasonal event based on current date"""
    now = datetime.now()
    month = now.month
    
    events = {
        3: {  # March - Spring
            'name': '🌸 Lễ hội mùa xuân',
            'description': 'Mùa xuân đã đến! Tất cả cây trồng sinh trưởng nhanh hơn 20%',
            'growth_bonus': 1.2,
            'duration_days': 7
        },
        6: {  # June - Summer
            'name': '☀️ Mùa hè nắng nóng',
            'description': 'Mùa hè nắng nóng! Cây trồng cần nhiều nước hơn nhưng cho sản lượng cao',
            'yield_bonus': 1.3,
            'duration_days': 10
        },
        9: {  # September - Autumn
            'name': '🍂 Mùa thu thu hoạch',
            'description': 'Mùa thu đến rồi! Giá bán nông sản tăng 15%',
            'price_bonus': 1.15,
            'duration_days': 14
        },
        12: {  # December - Winter
            'name': '❄️ Lễ hội mùa đông',
            'description': 'Mùa đông lạnh giá! Nhận thêm coins từ điểm danh hàng ngày',
            'daily_bonus': 1.5,
            'duration_days': 21
        }
    }
    
    return events.get(month, {})

def format_number(number: int) -> str:
    """Format large numbers with K, M, B suffixes"""
    if number >= 1_000_000_000:
        return f"{number / 1_000_000_000:.1f}B"
    elif number >= 1_000_000:
        return f"{number / 1_000_000:.1f}M"
    elif number >= 1_000:
        return f"{number / 1_000:.1f}K"
    else:
        return str(number)

def get_crop_emoji_by_growth(growth_progress: float) -> str:
    """Get emoji representing crop growth stage"""
    if growth_progress >= 1.0:
        return "✨"  # Ready to harvest
    elif growth_progress >= 0.75:
        return "🌾"  # Almost ready
    elif growth_progress >= 0.5:
        return "🌿"  # Growing well
    elif growth_progress >= 0.25:
        return "🌱"  # Young plant
    else:
        return "🌰"  # Just planted

def validate_plot_index(plot_index: int, max_slots: int) -> bool:
    """Validate if plot index is valid"""
    return 0 <= plot_index < max_slots

def get_random_weather_event() -> dict:
    """Generate random weather events for variety"""
    events = [
        {
            'name': '🌪️ Gió lớn',
            'description': 'Gió lớn đang thổi, cây trồng có thể bị ảnh hưởng',
            'growth_modifier': 0.8,
            'chance': 0.1
        },
        {
            'name': '🦋 Bướm thụ phấn',
            'description': 'Đàn bướm đang giúp thụ phấn, tăng sản lượng!',
            'yield_modifier': 1.2,
            'chance': 0.15
        },
        {
            'name': '🐛 Sâu bệnh',
            'description': 'Có sâu bệnh xuất hiện, cần chú ý bảo vệ cây trồng',
            'yield_modifier': 0.9,
            'chance': 0.05
        }
    ]
    
    for event in events:
        if random.random() < event['chance']:
            return event
    
    return {}  # No event 