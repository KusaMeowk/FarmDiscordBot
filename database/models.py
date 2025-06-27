from datetime import datetime
from typing import Optional, List, Dict, Any
import json

class User:
    def __init__(self, user_id: int, username: str, money: int = 1000, 
                 land_slots: int = 4, last_daily: Optional[datetime] = None,
                 daily_streak: int = 0, joined_date: Optional[datetime] = None):
        self.user_id = user_id
        self.username = username
        self.money = money
        self.land_slots = land_slots
        self.last_daily = last_daily
        self.daily_streak = daily_streak
        self.joined_date = joined_date or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'user_id': self.user_id,
            'username': self.username,
            'money': self.money,
            'land_slots': self.land_slots,
            'last_daily': self.last_daily.isoformat() if self.last_daily else None,
            'daily_streak': self.daily_streak,
            'joined_date': self.joined_date.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        return cls(
            user_id=data['user_id'],
            username=data['username'],
            money=data['money'],
            land_slots=data['land_slots'],
            last_daily=datetime.fromisoformat(data['last_daily']) if data['last_daily'] else None,
            daily_streak=data['daily_streak'],
            joined_date=datetime.fromisoformat(data['joined_date'])
        )

class Crop:
    def __init__(self, crop_id: int, user_id: int, crop_type: str, 
                 plot_index: int, plant_time: datetime, growth_stage: int = 0,
                 buffs_applied: Optional[str] = None):
        self.crop_id = crop_id
        self.user_id = user_id
        self.crop_type = crop_type
        self.plot_index = plot_index
        self.plant_time = plant_time
        self.growth_stage = growth_stage
        self.buffs_applied = buffs_applied or ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'crop_id': self.crop_id,
            'user_id': self.user_id,
            'crop_type': self.crop_type,
            'plot_index': self.plot_index,
            'plant_time': self.plant_time.isoformat(),
            'growth_stage': self.growth_stage,
            'buffs_applied': self.buffs_applied
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Crop':
        return cls(
            crop_id=data['crop_id'],
            user_id=data['user_id'],
            crop_type=data['crop_type'],
            plot_index=data['plot_index'],
            plant_time=datetime.fromisoformat(data['plant_time']),
            growth_stage=data['growth_stage'],
            buffs_applied=data['buffs_applied']
        )

class InventoryItem:
    def __init__(self, user_id: int, item_type: str, item_id: str, quantity: int):
        self.user_id = user_id
        self.item_type = item_type  # 'seed', 'tool', 'buff', 'crop'
        self.item_id = item_id
        self.quantity = quantity
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'user_id': self.user_id,
            'item_type': self.item_type,
            'item_id': self.item_id,
            'quantity': self.quantity
        }

class SeasonalEvent:
    def __init__(self, event_id: str, name: str, description: str,
                 start_date: datetime, end_date: datetime, 
                 rewards: Dict[str, Any], is_active: bool = False):
        self.event_id = event_id
        self.name = name
        self.description = description
        self.start_date = start_date
        self.end_date = end_date
        self.rewards = rewards
        self.is_active = is_active

class WeatherNotification:
    def __init__(self, guild_id: int, channel_id: int, enabled: bool = True,
                 last_weather: str = None, city: str = "Ho Chi Minh City"):
        self.guild_id = guild_id
        self.channel_id = channel_id
        self.enabled = enabled
        self.last_weather = last_weather
        self.city = city
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'guild_id': self.guild_id,
            'channel_id': self.channel_id,
            'enabled': self.enabled,
            'last_weather': self.last_weather,
            'city': self.city
        }

class MarketNotification:
    def __init__(self, guild_id: int, channel_id: int, enabled: bool = True,
                 last_market_modifier: float = 1.0, threshold: float = 0.1):
        self.guild_id = guild_id
        self.channel_id = channel_id
        self.enabled = enabled
        self.last_market_modifier = last_market_modifier
        self.threshold = threshold  # Minimum change to trigger notification
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'guild_id': self.guild_id,
            'channel_id': self.channel_id,
            'enabled': self.enabled,
            'last_market_modifier': self.last_market_modifier,
            'threshold': self.threshold
        }

class AINotification:
    def __init__(self, guild_id: int, channel_id: int, enabled: bool = True,
                 event_notifications: bool = True, weather_notifications: bool = True,
                 economic_notifications: bool = True):
        self.guild_id = guild_id
        self.channel_id = channel_id
        self.enabled = enabled
        self.event_notifications = event_notifications
        self.weather_notifications = weather_notifications
        self.economic_notifications = economic_notifications
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'guild_id': self.guild_id,
            'channel_id': self.channel_id,
            'enabled': self.enabled,
            'event_notifications': self.event_notifications,
            'weather_notifications': self.weather_notifications,
            'economic_notifications': self.economic_notifications
        }

class EventClaim:
    """Model để tracking việc user đã claim event reward"""
    def __init__(self, user_id: int, event_id: str, claimed_at: datetime):
        self.user_id = user_id
        self.event_id = event_id
        self.claimed_at = claimed_at

class BotState:
    """Model để lưu trạng thái hệ thống (weather cycle, events, etc.)"""
    def __init__(self, state_key: str, state_data: Dict[str, Any], 
                 updated_at: Optional[datetime] = None):
        self.state_key = state_key
        self.state_data = state_data
        self.updated_at = updated_at or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'state_key': self.state_key,
            'state_data': json.dumps(self.state_data, default=str),
            'updated_at': self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BotState':
        return cls(
            state_key=data['state_key'],
            state_data=json.loads(data['state_data']),
            updated_at=datetime.fromisoformat(data['updated_at'])
        )
    
    def get_state_value(self, key: str, default=None):
        """Lấy giá trị từ state_data"""
        return self.state_data.get(key, default)
    
    def set_state_value(self, key: str, value: Any):
        """Set giá trị vào state_data"""
        self.state_data[key] = value
        self.updated_at = datetime.now()
    
    def update_multiple(self, updates: Dict[str, Any]):
        """Update nhiều giá trị cùng lúc"""
        self.state_data.update(updates)
        self.updated_at = datetime.now()

class Species:
    """Model định nghĩa loài cá/thú"""
    def __init__(self, species_id: str, name: str, species_type: str, tier: int,
                 buy_price: int, sell_price: int, growth_time: int, 
                 special_ability: str = "", emoji: str = "🐟"):
        self.species_id = species_id
        self.name = name
        self.species_type = species_type  # 'fish' hoặc 'animal'
        self.tier = tier
        self.buy_price = buy_price
        self.sell_price = sell_price
        self.growth_time = growth_time  # seconds
        self.special_ability = special_ability
        self.emoji = emoji
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'species_id': self.species_id,
            'name': self.name,
            'species_type': self.species_type,
            'tier': self.tier,
            'buy_price': self.buy_price,
            'sell_price': self.sell_price,
            'growth_time': self.growth_time,
            'special_ability': self.special_ability,
            'emoji': self.emoji
        }

class UserLivestock:
    """Model cá/thú của user"""
    def __init__(self, livestock_id: int, user_id: int, species_id: str,
                 facility_type: str, facility_slot: int, birth_time: datetime,
                 is_adult: bool = False, last_product_time: Optional[datetime] = None):
        self.livestock_id = livestock_id
        self.user_id = user_id
        self.species_id = species_id
        self.facility_type = facility_type  # 'pond' hoặc 'barn'
        self.facility_slot = facility_slot
        self.birth_time = birth_time
        self.is_adult = is_adult
        self.last_product_time = last_product_time
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'livestock_id': self.livestock_id,
            'user_id': self.user_id,
            'species_id': self.species_id,
            'facility_type': self.facility_type,
            'facility_slot': self.facility_slot,
            'birth_time': self.birth_time.isoformat(),
            'is_adult': self.is_adult,
            'last_product_time': self.last_product_time.isoformat() if self.last_product_time else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserLivestock':
        return cls(
            livestock_id=data['livestock_id'],
            user_id=data['user_id'],
            species_id=data['species_id'],
            facility_type=data['facility_type'],
            facility_slot=data['facility_slot'],
            birth_time=datetime.fromisoformat(data['birth_time']),
            is_adult=data['is_adult'],
            last_product_time=datetime.fromisoformat(data['last_product_time']) if data['last_product_time'] else None
        )

class UserFacilities:
    """Model cơ sở hạ tầng của user"""
    def __init__(self, user_id: int, pond_slots: int = 2, barn_slots: int = 2,
                 pond_level: int = 1, barn_level: int = 1):
        self.user_id = user_id
        self.pond_slots = pond_slots
        self.barn_slots = barn_slots
        self.pond_level = pond_level
        self.barn_level = barn_level
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'user_id': self.user_id,
            'pond_slots': self.pond_slots,
            'barn_slots': self.barn_slots,
            'pond_level': self.pond_level,
            'barn_level': self.barn_level
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserFacilities':
        return cls(
            user_id=data['user_id'],
            pond_slots=data['pond_slots'],
            barn_slots=data['barn_slots'],
            pond_level=data['pond_level'],
            barn_level=data['barn_level']
        )

class LivestockProduct:
    """Model sản phẩm từ thú nuôi"""
    def __init__(self, species_id: str, product_name: str, product_emoji: str,
                 production_time: int, sell_price: int):
        self.species_id = species_id
        self.product_name = product_name
        self.product_emoji = product_emoji
        self.production_time = production_time  # seconds
        self.sell_price = sell_price
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'species_id': self.species_id,
            'product_name': self.product_name,
            'product_emoji': self.product_emoji,
            'production_time': self.production_time,
            'sell_price': self.sell_price
        }

class MaidBuff:
    """Model cho buff của maid"""
    def __init__(self, buff_type: str, value: float, description: str = ""):
        self.buff_type = buff_type  # growth_speed, seed_discount, yield_boost, sell_price
        self.value = value          # % buff value
        self.description = description
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'buff_type': self.buff_type,
            'value': self.value,
            'description': self.description
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MaidBuff':
        return cls(
            buff_type=data['buff_type'],
            value=data['value'],
            description=data.get('description', '')
        )

class Maid:
    """Model cho maid template"""
    def __init__(self, maid_id: str, name: str, rarity: str, description: str,
                 emoji: str, possible_buffs: List[str], art_url: str = ""):
        self.maid_id = maid_id
        self.name = name
        self.rarity = rarity        # UR, SSR, SR, R
        self.description = description
        self.emoji = emoji
        self.possible_buffs = possible_buffs  # List of possible buff types
        self.art_url = art_url
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'maid_id': self.maid_id,
            'name': self.name,
            'rarity': self.rarity,
            'description': self.description,
            'emoji': self.emoji,
            'possible_buffs': self.possible_buffs,
            'art_url': self.art_url
        }

class UserMaid:
    """Model cho maid instance của user"""
    def __init__(self, instance_id: str, user_id: int, maid_id: str, 
                 custom_name: Optional[str] = None, obtained_at: Optional[datetime] = None,
                 is_active: bool = False, buff_values: List[MaidBuff] = None):
        self.instance_id = instance_id
        self.user_id = user_id
        self.maid_id = maid_id
        self.custom_name = custom_name
        self.obtained_at = obtained_at or datetime.now()
        self.is_active = is_active
        self.buff_values = buff_values or []
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'instance_id': self.instance_id,
            'user_id': self.user_id,
            'maid_id': self.maid_id,
            'custom_name': self.custom_name,
            'obtained_at': self.obtained_at.isoformat(),
            'is_active': self.is_active,
            'buff_values': [buff.to_dict() for buff in self.buff_values]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserMaid':
        return cls(
            instance_id=data['instance_id'],
            user_id=data['user_id'],
            maid_id=data['maid_id'],
            custom_name=data.get('custom_name'),
            obtained_at=datetime.fromisoformat(data['obtained_at']),
            is_active=data['is_active'],
            buff_values=[MaidBuff.from_dict(buff) for buff in data['buff_values']]
        )

class GachaHistory:
    """Model cho lịch sử gacha"""
    def __init__(self, user_id: int, roll_type: str, cost: int, 
                 results: List[str], created_at: Optional[datetime] = None):
        self.user_id = user_id
        self.roll_type = roll_type  # 'single' or 'ten'
        self.cost = cost
        self.results = results      # List of maid_ids obtained
        self.created_at = created_at or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'user_id': self.user_id,
            'roll_type': self.roll_type,
            'cost': self.cost,
            'results': json.dumps(self.results),
            'created_at': self.created_at.isoformat()
        }

class UserGachaPity:
    """Model cho hệ thống pity gacha"""
    def __init__(self, user_id: int, rolls_without_ur: int = 0, 
                 in_pity_mode: bool = False, pity_rolls_remaining: int = 0,
                 last_roll_time: Optional[datetime] = None):
        self.user_id = user_id
        self.rolls_without_ur = rolls_without_ur
        self.in_pity_mode = in_pity_mode
        self.pity_rolls_remaining = pity_rolls_remaining
        self.last_roll_time = last_roll_time
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'user_id': self.user_id,
            'rolls_without_ur': self.rolls_without_ur,
            'in_pity_mode': self.in_pity_mode,
            'pity_rolls_remaining': self.pity_rolls_remaining,
            'last_roll_time': self.last_roll_time.isoformat() if self.last_roll_time else None
        }

class MaidTrade:
    """Model cho hệ thống trade maid"""
    def __init__(self, trade_id: str, from_user_id: int, to_user_id: int,
                 maid_instance_id: str, trade_status: str = 'pending',
                 created_at: Optional[datetime] = None, completed_at: Optional[datetime] = None):
        self.trade_id = trade_id
        self.from_user_id = from_user_id
        self.to_user_id = to_user_id
        self.maid_instance_id = maid_instance_id
        self.trade_status = trade_status  # pending, accepted, cancelled
        self.created_at = created_at or datetime.now()
        self.completed_at = completed_at
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'trade_id': self.trade_id,
            'from_user_id': self.from_user_id,
            'to_user_id': self.to_user_id,
            'maid_instance_id': self.maid_instance_id,
            'trade_status': self.trade_status,
            'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

class UserStardust:
    """Model cho bụi sao của user"""
    def __init__(self, user_id: int, stardust_amount: int = 0, 
                 last_updated: Optional[datetime] = None):
        self.user_id = user_id
        self.stardust_amount = stardust_amount
        self.last_updated = last_updated or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'user_id': self.user_id,
            'stardust_amount': self.stardust_amount,
            'last_updated': self.last_updated.isoformat()
        }
    
    def add_stardust(self, amount: int):
        """Thêm bụi sao"""
        self.stardust_amount += amount
        self.last_updated = datetime.now()
    
    def spend_stardust(self, amount: int) -> bool:
        """Tiêu bụi sao, return True nếu đủ"""
        if self.stardust_amount >= amount:
            self.stardust_amount -= amount
            self.last_updated = datetime.now()
            return True
        return False 