"""
Maid System Helper Functions
Để integrate maid buffs vào các hệ thống game hiện tại
"""
from typing import Dict, Optional, Tuple
from database.database import Database
from features.maid_database import MaidDatabase
from features.maid_config import MAID_TEMPLATES
from features.maid_monitoring import maid_monitor

class MaidBuffHelper:
    def __init__(self, db_path: str = "farm_bot.db"):
        self.db_path = db_path  # ⭐ Missing line!
        try:
            self.db = Database('farm_bot.db')
            self.maid_db = MaidDatabase(db_path)
        except Exception:
            # Fallback for testing environment
            self.db = None
            self.maid_db = None
    
    def get_user_maid_buffs(self, user_id: int) -> Dict[str, float]:
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
            # 🎀 Direct implementation - exactly like working inline test
            import sqlite3
            import json
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT maid_id, buff_values 
                FROM user_maids_v2 
                WHERE user_id = ? AND is_active = 1
            """, (user_id,))
            
            result = cursor.fetchone()
            if not result:
                conn.close()
                return buffs
            
            maid_id, buff_values_json = result
            
            if buff_values_json:
                try:
                    buff_list = json.loads(buff_values_json)
                    
                    for buff_data in buff_list:
                        buff_type = buff_data.get('type') or buff_data.get('buff_type')
                        buff_value = float(buff_data.get('value', 0.0))
                        
                        if buff_type and buff_type in buffs:
                            buffs[buff_type] += buff_value
                        
                except Exception as e:
                    pass  # Silent fail for now
            
            conn.close()
            
        except Exception as e:
            # Show the actual error instead of hiding it
            print(f"❌ maid_helper error for user {user_id}: {e}")
            import traceback
            traceback.print_exc()
            
            # Fallback to old system if V2 fails
            try:
                if self.maid_db:
                    active_maid = self.maid_db.get_active_maid(user_id)
                    if active_maid and hasattr(active_maid, 'buff_values'):
                        buff_values = active_maid.buff_values
                        if not hasattr(buff_values, '__await__'):
                            for buff in buff_values:
                                if hasattr(buff, 'buff_type') and buff.buff_type in buffs:
                                    buffs[buff.buff_type] += buff.value
            except Exception as fallback_error:
                print(f"❌ Fallback error: {fallback_error}")
        
        return buffs
    
    def apply_growth_speed_buff(self, user_id: int, base_growth_time: int) -> int:
        """
        Apply growth speed buff (giảm thời gian trồng cây)
        
        Args:
            user_id: ID của user
            base_growth_time: Thời gian sinh trưởng gốc (seconds)
            
        Returns:
            Thời gian sinh trưởng sau khi apply buff
        """
        buffs = self.get_user_maid_buffs(user_id)
        growth_speed_buff = buffs.get("growth_speed", 0.0)
        
        # 🛡️ Cap buff để tránh exploit
        growth_speed_buff = max(0.0, min(growth_speed_buff, 80.0))  # Max 80% reduction
        
        if growth_speed_buff > 0:
            # Giảm thời gian theo % buff
            reduction = growth_speed_buff / 100.0
            new_time = int(base_growth_time * (1 - reduction))
            final_time = max(new_time, 60)  # Tối thiểu 1 phút
            
            # 📊 Log usage for monitoring
            maid_monitor.log_buff_usage(
                user_id, "growth_speed", growth_speed_buff,
                base_growth_time, final_time, "crop_growth"
            )
            
            return final_time
        
        return base_growth_time
    
    def apply_seed_discount_buff(self, user_id: int, base_seed_price: int) -> int:
        """
        Apply seed discount buff (giảm giá hạt giống)
        
        Args:
            user_id: ID của user
            base_seed_price: Giá hạt giống gốc
            
        Returns:
            Giá hạt giống sau khi apply buff
        """
        buffs = self.get_user_maid_buffs(user_id)
        seed_discount_buff = buffs.get("seed_discount", 0.0)
        
        # 🛡️ Cap buff để tránh exploit
        seed_discount_buff = max(0.0, min(seed_discount_buff, 90.0))  # Max 90% discount
        
        if seed_discount_buff > 0:
            # Giảm giá theo % buff
            discount = seed_discount_buff / 100.0
            new_price = int(base_seed_price * (1 - discount))
            return max(new_price, 1)  # Tối thiểu 1 coin
        
        return base_seed_price
    
    def apply_yield_boost_buff(self, user_id: int, base_yield: int) -> int:
        """
        Apply yield boost buff (tăng sản lượng)
        
        Args:
            user_id: ID của user
            base_yield: Sản lượng gốc
            
        Returns:
            Sản lượng sau khi apply buff
        """
        buffs = self.get_user_maid_buffs(user_id)
        yield_boost_buff = buffs.get("yield_boost", 0.0)
        
        # 🛡️ Cap buff để tránh exploit
        yield_boost_buff = max(0.0, min(yield_boost_buff, 200.0))  # Max 200% increase
        
        if yield_boost_buff > 0:
            # Tăng sản lượng theo % buff
            boost = yield_boost_buff / 100.0
            new_yield = int(base_yield * (1 + boost))
            return new_yield
        
        return base_yield
    
    def apply_sell_price_buff(self, user_id: int, base_sell_price: int) -> int:
        """
        Apply sell price buff (tăng giá bán)
        
        Args:
            user_id: ID của user
            base_sell_price: Giá bán gốc
            
        Returns:
            Giá bán sau khi apply buff
        """
        buffs = self.get_user_maid_buffs(user_id)
        sell_price_buff = buffs.get("sell_price", 0.0)
        
        # 🛡️ Cap buff để tránh exploit
        sell_price_buff = max(0.0, min(sell_price_buff, 150.0))  # Max 150% increase
        
        if sell_price_buff > 0:
            # Tăng giá bán theo % buff
            boost = sell_price_buff / 100.0
            new_price = int(base_sell_price * (1 + boost))
            return new_price
        
        return base_sell_price
    
    def get_active_maid_info(self, user_id: int) -> Optional[Dict]:
        """
        Lấy thông tin maid active để hiển thị
        
        Returns:
            Dict chứa thông tin maid hoặc None nếu không có
        """
        try:
            active_maid = self.maid_db.get_active_maid(user_id)
            if not active_maid:
                return None
            
            template = MAID_TEMPLATES.get(active_maid.maid_id)
            if not template:
                return None
            
            # Handle buff_values safely
            buffs_info = []
            try:
                buff_values = active_maid.buff_values
                if not hasattr(buff_values, '__await__'):
                    buffs_info = [
                        {
                            "type": buff.buff_type,
                            "value": buff.value,
                            "description": getattr(buff, 'description', '')
                        }
                        for buff in buff_values
                        if hasattr(buff, 'buff_type')
                    ]
            except (AttributeError, TypeError):
                pass
            
            return {
                "name": active_maid.custom_name or template["name"],
                "full_name": template.get("full_name", template["name"]),
                "emoji": template["emoji"],
                "rarity": template["rarity"],
                "buffs": buffs_info
            }
        except Exception:
            return None
    
    def get_buff_summary_text(self, user_id: int) -> str:
        """
        Tạo text summary ngắn gọn về buffs hiện tại
        
        Returns:
            String mô tả buffs hoặc empty string nếu không có
        """
        buffs = self.get_user_maid_buffs(user_id)
        active_buffs = [(k, v) for k, v in buffs.items() if v > 0]
        
        if not active_buffs:
            return ""
        
        from features.maid_config import BUFF_TYPES
        
        buff_texts = []
        for buff_type, value in active_buffs:
            if buff_type in BUFF_TYPES:
                emoji = BUFF_TYPES[buff_type]["emoji"]
                buff_texts.append(f"{emoji}+{value}%")
        
        return " ".join(buff_texts)
    
    def calculate_all_farm_modifiers(self, user_id: int, 
                                   base_growth_time: int, 
                                   base_seed_price: int,
                                   base_yield: int, 
                                   base_sell_price: int) -> Dict[str, int]:
        """
        Tính toán tất cả modifiers cho farming trong 1 lần call
        
        Returns:
            Dict chứa tất cả giá trị đã được modified
        """
        return {
            "growth_time": self.apply_growth_speed_buff(user_id, base_growth_time),
            "seed_price": self.apply_seed_discount_buff(user_id, base_seed_price),
            "yield": self.apply_yield_boost_buff(user_id, base_yield),
            "sell_price": self.apply_sell_price_buff(user_id, base_sell_price)
        }

# Global instance để sử dụng trong các cogs khác
maid_helper = MaidBuffHelper() 