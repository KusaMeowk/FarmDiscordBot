from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import config
from database.models import Species, UserLivestock, UserFacilities, LivestockProduct

def get_livestock_growth_time_with_modifiers(species_id: str, growth_modifier: float = 1.0, 
                                           event_growth_modifier: float = 1.0) -> int:
    """Calculate actual growth time with weather and event modifiers"""
    # Get base species info
    all_species = {**config.FISH_SPECIES, **config.ANIMAL_SPECIES}
    
    if species_id not in all_species:
        return 3600  # Default 1 hour
    
    base_time = all_species[species_id]['growth_time']
    
    # Apply modifiers (lower modifier = faster growth)
    modified_time = int(base_time / growth_modifier / event_growth_modifier)
    
    # Minimum 5 minutes
    return max(modified_time, 300)

def calculate_livestock_maturity(livestock: UserLivestock, growth_modifier: float = 1.0,
                               event_growth_modifier: float = 1.0) -> Tuple[bool, float]:
    """
    Calculate if livestock is mature and growth percentage
    Returns: (is_mature, growth_percentage)
    """
    now = datetime.now()
    age = (now - livestock.birth_time).total_seconds()
    
    # 🔧 FIX: Lấy base growth time từ config để tránh double modifier
    all_species = {**config.FISH_SPECIES, **config.ANIMAL_SPECIES}
    
    if livestock.species_id not in all_species:
        base_growth_time = 3600  # Default 1 hour
    else:
        base_growth_time = all_species[livestock.species_id]['growth_time']
    
    # Apply modifiers chỉ một lần
    combined_modifier = growth_modifier * event_growth_modifier
    required_time = int(base_growth_time / combined_modifier)
    required_time = max(required_time, 300)  # Minimum 5 minutes
    
    growth_percentage = min(age / required_time * 100, 100)
    is_mature = age >= required_time
    
    return is_mature, growth_percentage

def get_livestock_display_info(livestock: UserLivestock, species: Species, 
                             growth_modifier: float = 1.0, 
                             event_growth_modifier: float = 1.0) -> Dict:
    """Get formatted display information for livestock"""
    is_mature, growth_percentage = calculate_livestock_maturity(
        livestock, growth_modifier, event_growth_modifier
    )
    
    # Calculate time remaining if not mature
    time_remaining = ""
    if not is_mature:
        now = datetime.now()
        age = (now - livestock.birth_time).total_seconds()
        
        # 🔧 FIX: Sử dụng base growth time để tính chính xác
        all_species = {**config.FISH_SPECIES, **config.ANIMAL_SPECIES}
        if livestock.species_id in all_species:
            base_growth_time = all_species[livestock.species_id]['growth_time']
        else:
            base_growth_time = 3600  # Default
        
        combined_modifier = growth_modifier * event_growth_modifier
        required_time = int(base_growth_time / combined_modifier)
        required_time = max(required_time, 300)
        
        remaining_seconds = required_time - age
        
        if remaining_seconds > 0:
            hours = int(remaining_seconds // 3600)
            minutes = int((remaining_seconds % 3600) // 60)
            if hours > 0:
                time_remaining = f"{hours}h {minutes}m"
            else:
                time_remaining = f"{minutes}m"
    
    # Status display
    if is_mature:
        status = "🟢 Trưởng thành"
        if livestock.species_id in config.ANIMAL_SPECIES:
            # Check if can produce
            can_produce = can_collect_product(livestock)
            if can_produce:
                status += " (Có thể thu hoạch)"
    else:
        status = f"🟡 Đang lớn ({growth_percentage:.1f}%)"
    
    return {
        'name': species.name,
        'emoji': species.emoji,
        'status': status,
        'time_remaining': time_remaining,
        'is_mature': is_mature,
        'growth_percentage': growth_percentage,
        'tier': species.tier,
        'special_ability': species.special_ability
    }

def can_collect_product(livestock: UserLivestock) -> bool:
    """Check if livestock can produce products"""
    # Only animals produce products
    if livestock.species_id not in config.ANIMAL_SPECIES:
        return False
    
    # Must be adult
    if not livestock.is_adult:
        return False
    
    # Check if species has products
    if livestock.species_id not in config.LIVESTOCK_PRODUCTS:
        return False
    
    # Check production cooldown
    if livestock.last_product_time:
        product_config = config.LIVESTOCK_PRODUCTS[livestock.species_id]
        production_time = product_config['production_time']
        
        next_production = livestock.last_product_time + timedelta(seconds=production_time)
        return datetime.now() >= next_production
    
    return True

def get_product_ready_time(livestock: UserLivestock) -> Optional[str]:
    """Get time until next product is ready"""
    if livestock.species_id not in config.LIVESTOCK_PRODUCTS:
        return None
    
    if not livestock.last_product_time:
        return "Sẵn sàng"
    
    product_config = config.LIVESTOCK_PRODUCTS[livestock.species_id]
    production_time = product_config['production_time']
    
    next_production = livestock.last_product_time + timedelta(seconds=production_time)
    now = datetime.now()
    
    if now >= next_production:
        return "Sẵn sàng"
    
    remaining = (next_production - now).total_seconds()
    hours = int(remaining // 3600)
    minutes = int((remaining % 3600) // 60)
    
    if hours > 0:
        return f"{hours}h {minutes}m"
    else:
        return f"{minutes}m"

def calculate_facility_expansion_cost(facility_type: str, current_level: int) -> Optional[int]:
    """Calculate cost to expand facility to next level"""
    costs = config.POND_UPGRADE_COSTS if facility_type == 'pond' else config.BARN_UPGRADE_COSTS
    
    next_level = current_level + 1
    return costs.get(next_level, None)  # Return None if max level reached

def get_facility_max_slots(facility_type: str, level: int) -> int:
    """Get maximum slots for facility at given level"""
    base_slots = config.INITIAL_POND_SLOTS if facility_type == 'pond' else config.INITIAL_BARN_SLOTS
    return base_slots + (level - 1) * 2  # +2 slots per level

def format_livestock_value(species: Species) -> str:
    """Format livestock buy/sell prices for display"""
    profit = species.sell_price - species.buy_price
    profit_percent = (profit / species.buy_price) * 100
    
    return f"💰 Mua: {species.buy_price:,}🪙 | Bán: {species.sell_price:,}🪙 (Lời: {profit_percent:.1f}%)"

def get_species_by_tier(species_type: str, tier: int) -> List[Dict]:
    """Get all species of specific type and tier"""
    all_species = config.FISH_SPECIES if species_type == 'fish' else config.ANIMAL_SPECIES
    
    return [
        {
            'id': species_id,
            'data': species_data
        }
        for species_id, species_data in all_species.items()
        if species_data['tier'] == tier
    ]

def get_livestock_weather_modifier(weather: str, species_type: str) -> float:
    """Get weather modifier for livestock growth"""
    # Weather affects livestock similar to crops but less severely
    weather_effects = {
        'sunny': 1.1,    # Slightly faster growth
        'rainy': 1.0,    # Normal growth  
        'cloudy': 0.95,  # Slightly slower
        'stormy': 0.85   # Slower growth
    }
    
    return weather_effects.get(weather, 1.0)

def validate_facility_slot(user_facilities: UserFacilities, facility_type: str, slot: int) -> bool:
    """Validate if facility slot is valid"""
    max_slots = user_facilities.pond_slots if facility_type == 'pond' else user_facilities.barn_slots
    return 0 <= slot < max_slots

def get_available_species_for_purchase(user_money: int, species_type: str) -> List[Dict]:
    """Get species that user can afford"""
    all_species = config.FISH_SPECIES if species_type == 'fish' else config.ANIMAL_SPECIES
    
    affordable_species = []
    for species_id, species_data in all_species.items():
        if species_data['buy_price'] <= user_money:
            affordable_species.append({
                'id': species_id,
                'data': species_data
            })
    
    # Sort by tier and price
    affordable_species.sort(key=lambda x: (x['data']['tier'], x['data']['buy_price']))
    return affordable_species

def calculate_livestock_value(base_price: int, weather_modifier: float = 1.0, event_modifier: float = 1.0) -> int:
    """Calculate livestock value with weather and event modifiers"""
    return int(base_price * weather_modifier * event_modifier)

def get_weather_modifier(bot, species_type: str) -> float:
    """Get current weather modifier for livestock"""
    try:
        weather_cog = bot.get_cog('WeatherCog')
        if weather_cog:
            current_weather, modifier = weather_cog.get_current_weather_modifier()
            return get_livestock_weather_modifier(current_weather, species_type)
    except:
        pass
    return 1.0

def is_livestock_mature_simple(birth_time: datetime, growth_time: int, modifier: float = 1.0) -> bool:
    """Calculate if livestock is mature based on birth time and growth time (simple version)"""
    elapsed = (datetime.now() - birth_time).total_seconds()
    adjusted_growth_time = growth_time / modifier
    return elapsed >= adjusted_growth_time 