"""
Maid System Cooldown Manager
Xử lý cooldown cho gacha và các actions khác
"""
import time
from typing import Dict, Tuple
from datetime import datetime, timedelta

class CooldownManager:
    """Persistent cooldown manager cho maid system"""
    
    def __init__(self):
        # user_id -> last_action_time
        self.cooldowns: Dict[int, datetime] = {}
    
    def check_cooldown(self, user_id: int, cooldown_seconds: float = 3.0) -> Tuple[bool, float]:
        """
        Kiểm tra xem user có thể thực hiện action không
        
        Args:
            user_id: ID của user
            cooldown_seconds: Thời gian cooldown cần check (default 3s)
        
        Returns:
            Tuple[bool, float]: (can_proceed, remaining_seconds)
        """
        if user_id not in self.cooldowns:
            return True, 0.0
        
        last_action = self.cooldowns[user_id]
        now = datetime.now()
        elapsed = (now - last_action).total_seconds()
        
        if elapsed >= cooldown_seconds:
            return True, 0.0
        else:
            remaining = cooldown_seconds - elapsed
            return False, remaining
    
    def set_cooldown(self, user_id: int, cooldown_seconds: float):
        """
        Set cooldown cho user
        
        Args:
            user_id: ID của user
            cooldown_seconds: Thời gian cooldown (giây)
        """
        self.cooldowns[user_id] = datetime.now()
    
    def get_remaining_time(self, user_id: int, cooldown_seconds: float) -> float:
        """
        Lấy thời gian cooldown còn lại
        
        Args:
            user_id: ID của user
            cooldown_seconds: Thời gian cooldown tổng cộng
            
        Returns:
            float: Số giây còn lại, 0 nếu không còn cooldown
        """
        if user_id not in self.cooldowns:
            return 0.0
        
        last_action = self.cooldowns[user_id]
        now = datetime.now()
        elapsed = (now - last_action).total_seconds()
        
        remaining = cooldown_seconds - elapsed
        return max(0.0, remaining)
    
    def clear_cooldown(self, user_id: int):
        """Xóa cooldown cho user (admin use)"""
        if user_id in self.cooldowns:
            del self.cooldowns[user_id]
    
    def clear_all_cooldowns(self):
        """Xóa tất cả cooldowns (admin use)"""
        self.cooldowns.clear()

# Global instance
cooldown_manager = CooldownManager() 