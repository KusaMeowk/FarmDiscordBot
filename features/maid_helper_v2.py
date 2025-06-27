"""
Maid System Helper V2 - Integration với game systems
"""
import aiosqlite
import json
from typing import Dict, Optional, Tuple
from database.database import Database
from utils.enhanced_logging import get_bot_logger

logger = get_bot_logger()

class MaidHelperV2:
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db if hasattr(bot, 'db') else Database('farm_bot.db')
    
    async def get_user_maid_buffs(self, user_id: int) -> Dict[str, float]:
        """
        Lấy tất cả buff hiện tại của user từ maid active
        
        Returns:
            Dict với key là buff_type và value là % buff
            VD: {"growth_speed": 25.5, "yield_boost": 15.0}
        """
        buffs = {
            "growth_speed": 0.0,
            "seed_discount": 0.0,
            "yield_boost": 0.0,
            "sell_price": 0.0
        }
        
        try:
            # Lấy maid active từ database
            cursor = await self.db.connection.execute('''
                SELECT buff_values FROM user_maids_v2 
                WHERE user_id = ? AND is_active = 1
            ''', (user_id,))
            result = await cursor.fetchone()
            
            if result:
                buff_data = json.loads(result[0])
                for buff in buff_data:
                    if buff["type"] in buffs:
                        buffs[buff["type"]] += buff["value"]
            
        except Exception as e:
            logger.warning(f"Error getting maid buffs for user {user_id}: {e}")
        
        return buffs
    
    async def apply_growth_speed_buff(self, user_id: int, base_growth_time: int) -> int:
        """
        Apply growth speed buff (giảm thời gian trồng cây)
        
        Args:
            user_id: ID của user
            base_growth_time: Thời gian sinh trưởng gốc (seconds)
            
        Returns:
            Thời gian sinh trưởng sau khi apply buff
        """
        buffs = await self.get_user_maid_buffs(user_id)
        growth_speed_buff = buffs.get("growth_speed", 0.0)
        
        # Cap buff để tránh exploit
        growth_speed_buff = max(0.0, min(growth_speed_buff, 80.0))  # Max 80% reduction
        
        if growth_speed_buff > 0:
            # Giảm thời gian theo % buff
            reduction = growth_speed_buff / 100.0
            new_time = int(base_growth_time * (1 - reduction))
            final_time = max(new_time, 60)  # Tối thiểu 1 phút
            
            logger.info(f"Applied growth speed buff for user {user_id}: {base_growth_time}s -> {final_time}s ({growth_speed_buff}% reduction)")
            return final_time
        
        return base_growth_time
    
    async def apply_seed_discount_buff(self, user_id: int, base_seed_price: int) -> int:
        """
        Apply seed discount buff (giảm giá hạt giống)
        
        Args:
            user_id: ID của user
            base_seed_price: Giá hạt giống gốc
            
        Returns:
            Giá hạt giống sau khi apply buff
        """
        buffs = await self.get_user_maid_buffs(user_id)
        seed_discount_buff = buffs.get("seed_discount", 0.0)
        
        # Cap buff để tránh exploit
        seed_discount_buff = max(0.0, min(seed_discount_buff, 90.0))  # Max 90% discount
        
        if seed_discount_buff > 0:
            # Giảm giá theo % buff
            discount = seed_discount_buff / 100.0
            new_price = int(base_seed_price * (1 - discount))
            final_price = max(new_price, 1)  # Tối thiểu 1 coin
            
            logger.info(f"Applied seed discount buff for user {user_id}: {base_seed_price} -> {final_price} ({seed_discount_buff}% discount)")
            return final_price
        
        return base_seed_price
    
    async def apply_yield_boost_buff(self, user_id: int, base_yield: int) -> int:
        """
        Apply yield boost buff (tăng sản lượng)
        
        Args:
            user_id: ID của user
            base_yield: Sản lượng gốc
            
        Returns:
            Sản lượng sau khi apply buff
        """
        buffs = await self.get_user_maid_buffs(user_id)
        yield_boost_buff = buffs.get("yield_boost", 0.0)
        
        # Cap buff để tránh exploit
        yield_boost_buff = max(0.0, min(yield_boost_buff, 200.0))  # Max 200% increase
        
        if yield_boost_buff > 0:
            # Tăng sản lượng theo % buff
            boost = yield_boost_buff / 100.0
            new_yield = int(base_yield * (1 + boost))
            
            logger.info(f"Applied yield boost buff for user {user_id}: {base_yield} -> {new_yield} ({yield_boost_buff}% boost)")
            return new_yield
        
        return base_yield
    
    async def apply_sell_price_buff(self, user_id: int, base_sell_price: int) -> int:
        """
        Apply sell price buff (tăng giá bán)
        
        Args:
            user_id: ID của user
            base_sell_price: Giá bán gốc
            
        Returns:
            Giá bán sau khi apply buff
        """
        buffs = await self.get_user_maid_buffs(user_id)
        sell_price_buff = buffs.get("sell_price", 0.0)
        
        # Cap buff để tránh exploit
        sell_price_buff = max(0.0, min(sell_price_buff, 150.0))  # Max 150% increase
        
        if sell_price_buff > 0:
            # Tăng giá bán theo % buff
            boost = sell_price_buff / 100.0
            new_price = int(base_sell_price * (1 + boost))
            
            logger.info(f"Applied sell price buff for user {user_id}: {base_sell_price} -> {new_price} ({sell_price_buff}% boost)")
            return new_price
        
        return base_sell_price
    
    async def get_active_maid_info(self, user_id: int) -> Optional[Dict]:
        """
        Lấy thông tin maid active để hiển thị
        
        Returns:
            Dict chứa thông tin maid hoặc None nếu không có
        """
        try:
            cursor = await self.db.connection.execute('''
                SELECT maid_id, custom_name, buff_values, instance_id
                FROM user_maids_v2 
                WHERE user_id = ? AND is_active = 1
            ''', (user_id,))
            result = await cursor.fetchone()
            
            if result:
                from features.maid_system_v2 import MAID_TEMPLATES
                
                maid_id = result[0]
                custom_name = result[1]
                buff_values = json.loads(result[2])
                instance_id = result[3]
                
                template = MAID_TEMPLATES.get(maid_id)
                if not template:
                    return None
                
                return {
                    "maid_id": maid_id,
                    "name": custom_name or template["name"],
                    "emoji": template["emoji"],
                    "rarity": template["rarity"],
                    "instance_id": instance_id,
                    "buffs": buff_values
                }
            
        except Exception as e:
            logger.warning(f"Error getting active maid info for user {user_id}: {e}")
        
        return None
    
    async def get_buff_summary_text(self, user_id: int) -> str:
        """
        Tạo text summary ngắn gọn về buffs hiện tại
        
        Returns:
            String mô tả buffs hoặc empty string nếu không có
        """
        buffs = await self.get_user_maid_buffs(user_id)
        active_buffs = [(k, v) for k, v in buffs.items() if v > 0]
        
        if not active_buffs:
            return ""
        
        buff_names = {
            "growth_speed": "🌱 Tăng tốc",
            "seed_discount": "💰 Giảm giá seed",
            "yield_boost": "📈 Tăng yield", 
            "sell_price": "💎 Tăng giá bán"
        }
        
        buff_texts = [f"{buff_names[k]} +{v:.1f}%" for k, v in active_buffs]
        return " • ".join(buff_texts)
    
    async def calculate_all_farm_modifiers(self, user_id: int, 
                                   base_growth_time: int, 
                                   base_seed_price: int,
                                   base_yield: int, 
                                   base_sell_price: int) -> Dict[str, int]:
        """
        Tính toán tất cả modifiers cùng lúc để tối ưu performance
        
        Returns:
            Dict chứa tất cả giá trị đã modify
        """
        return {
            "growth_time": await self.apply_growth_speed_buff(user_id, base_growth_time),
            "seed_price": await self.apply_seed_discount_buff(user_id, base_seed_price),
            "yield": await self.apply_yield_boost_buff(user_id, base_yield),
            "sell_price": await self.apply_sell_price_buff(user_id, base_sell_price)
        }
    
    async def has_active_maid(self, user_id: int) -> bool:
        """Kiểm tra user có maid active không"""
        try:
            cursor = await self.db.connection.execute('''
                SELECT 1 FROM user_maids_v2 
                WHERE user_id = ? AND is_active = 1 LIMIT 1
            ''', (user_id,))
            result = await cursor.fetchone()
            return result is not None
        except:
            return False
    
    async def get_buff_display_embed_field(self, user_id: int) -> Optional[Tuple[str, str, bool]]:
        """
        Tạo field cho embed hiển thị buff summary
        
        Returns:
            Tuple (name, value, inline) để add vào embed hoặc None
        """
        maid_info = await self.get_active_maid_info(user_id)
        if not maid_info:
            return None
        
        buff_summary = await self.get_buff_summary_text(user_id)
        if not buff_summary:
            return None
        
        return (
            f"✨ {maid_info['emoji']} {maid_info['name']} Buffs",
            buff_summary,
            False
        )

# Global instance để import từ các modules khác
maid_helper = None

def init_maid_helper(bot):
    """Khởi tạo global maid helper"""
    global maid_helper
    maid_helper = MaidHelperV2(bot)
    return maid_helper

def get_maid_helper():
    """Lấy global maid helper instance"""
    return maid_helper 