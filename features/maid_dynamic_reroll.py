"""
Dynamic Maid Reroll Cost System
Chi phí reroll thay đổi theo nhiều yếu tố: rarity, số lần reroll, chất lượng buffs hiện tại
"""
import math
from typing import List, Dict, Tuple
from datetime import datetime, timedelta
from database.models import UserMaid, MaidBuff

class DynamicRerollCostCalculator:
    """Tính toán chi phí reroll động"""
    
    # Base costs theo rarity (giống như cũ)
    BASE_COSTS = {
        "UR": 80,
        "SSR": 40, 
        "SR": 20,
        "R": 8
    }
    
    # Buff ranges để tính chất lượng
    BUFF_RANGES = {
        "UR": (30, 50),
        "SSR": (20, 35),
        "SR": (15, 25), 
        "R": (5, 15)
    }
    
    @classmethod
    def calculate_reroll_cost(cls, maid: UserMaid, maid_template: Dict, reroll_history: List = None) -> Tuple[int, Dict]:
        """
        Tính chi phí reroll động
        
        Args:
            maid: UserMaid instance
            maid_template: Maid template từ config
            reroll_history: Lịch sử reroll của maid này
            
        Returns:
            Tuple[int, Dict]: (final_cost, breakdown_details)
        """
        rarity = maid_template["rarity"]
        base_cost = cls.BASE_COSTS[rarity]
        
        # 1. Base cost
        multipliers = {
            "base_cost": base_cost,
            "reroll_count_multiplier": 1.0,
            "quality_multiplier": 1.0,
            "time_multiplier": 1.0,
            "rarity_scaling": 1.0
        }
        
        # 2. Reroll count multiplier
        reroll_count = len(reroll_history) if reroll_history else 0
        multipliers["reroll_count_multiplier"] = cls._get_reroll_count_multiplier(reroll_count)
        
        # 3. Current buff quality multiplier  
        multipliers["quality_multiplier"] = cls._get_quality_multiplier(maid.buff_values, rarity)
        
        # 4. Time-based scaling (recent rerolls cost more)
        multipliers["time_multiplier"] = cls._get_time_multiplier(reroll_history)
        
        # 5. Rarity scaling (UR gets more expensive faster)
        multipliers["rarity_scaling"] = cls._get_rarity_scaling(rarity, reroll_count)
        
        # Calculate final cost
        final_multiplier = (
            multipliers["reroll_count_multiplier"] * 
            multipliers["quality_multiplier"] * 
            multipliers["time_multiplier"] * 
            multipliers["rarity_scaling"]
        )
        
        final_cost = int(base_cost * final_multiplier)
        
        # Cap maximum cost
        max_cost = base_cost * 5  # Không quá 5x base cost
        final_cost = min(final_cost, max_cost)
        
        # Minimum cost (ít nhất 50% base cost)
        min_cost = int(base_cost * 0.5)
        final_cost = max(final_cost, min_cost)
        
        breakdown = {
            **multipliers,
            "final_multiplier": final_multiplier,
            "final_cost": final_cost,
            "original_cost": base_cost,
            "savings_penalty": final_cost - base_cost
        }
        
        return final_cost, breakdown
    
    @classmethod
    def _get_reroll_count_multiplier(cls, reroll_count: int) -> float:
        """Chi phí tăng theo số lần reroll"""
        if reroll_count == 0:
            return 1.0      # Lần đầu: 100%
        elif reroll_count <= 2:
            return 1.2      # Lần 2-3: +20%
        elif reroll_count <= 5:
            return 1.5      # Lần 4-6: +50%
        elif reroll_count <= 10:
            return 2.0      # Lần 7-11: +100%
        else:
            return 3.0      # Lần 12+: +200%
    
    @classmethod
    def _get_quality_multiplier(cls, current_buffs: List[MaidBuff], rarity: str) -> float:
        """Chi phí tăng nếu buffs hiện tại đã tốt"""
        if not current_buffs:
            return 0.8  # Không có buffs -> giảm giá
        
        min_range, max_range = cls.BUFF_RANGES[rarity]
        
        # Tính quality score trung bình
        avg_buff_value = sum(buff.value for buff in current_buffs) / len(current_buffs)
        quality_percentage = (avg_buff_value - min_range) / (max_range - min_range)
        quality_percentage = max(0, min(1, quality_percentage))  # Clamp 0-1
        
        if quality_percentage >= 0.9:      # 90%+ của max range
            return 2.0      # +100% cost (gần perfect, đắt để reroll)
        elif quality_percentage >= 0.75:   # 75-90% của max range
            return 1.5      # +50% cost (khá tốt)
        elif quality_percentage >= 0.5:    # 50-75% của max range  
            return 1.1      # +10% cost (trung bình)
        elif quality_percentage >= 0.25:   # 25-50% của max range
            return 0.9      # -10% cost (hơi kém)
        else:
            return 0.7      # -30% cost (buffs rất kém, khuyến khích reroll)
    
    @classmethod
    def _get_time_multiplier(cls, reroll_history: List) -> float:
        """Recent rerolls cost more (cooling down system)"""
        if not reroll_history:
            return 1.0
        
        now = datetime.now()
        recent_rerolls = 0
        
        # Đếm số lần reroll trong 24h qua
        for reroll_time in reroll_history[-10:]:  # Check 10 lần gần nhất
            if isinstance(reroll_time, str):
                reroll_time = datetime.fromisoformat(reroll_time)
            
            if now - reroll_time < timedelta(hours=24):
                recent_rerolls += 1
        
        if recent_rerolls >= 3:
            return 1.8      # 3+ rerolls trong 24h: +80%
        elif recent_rerolls >= 2:  
            return 1.4      # 2 rerolls trong 24h: +40%
        elif recent_rerolls >= 1:
            return 1.2      # 1 reroll trong 24h: +20%
        else:
            return 1.0      # Không có recent rerolls
    
    @classmethod  
    def _get_rarity_scaling(cls, rarity: str, reroll_count: int) -> float:
        """UR maids get more expensive faster than lower rarities"""
        base_scaling = {
            "UR": 1.1,      # UR tăng nhanh nhất
            "SSR": 1.05,    # SSR tăng vừa phải
            "SR": 1.02,     # SR tăng ít
            "R": 1.0        # R không tăng thêm
        }
        
        scaling_factor = base_scaling.get(rarity, 1.0)
        return scaling_factor ** min(reroll_count, 10)  # Cap at 10 để tránh quá đắt

    @classmethod
    def format_cost_breakdown(cls, breakdown: Dict) -> str:
        """Format breakdown thành text đẹp cho Discord"""
        lines = [
            f"💰 **Chi Phí Reroll Breakdown:**",
            f"├─ Base Cost: `{breakdown['base_cost']:,}` ⭐",
            f"├─ Reroll Count: `×{breakdown['reroll_count_multiplier']:.1f}`",
            f"├─ Buff Quality: `×{breakdown['quality_multiplier']:.1f}`", 
            f"├─ Time Penalty: `×{breakdown['time_multiplier']:.1f}`",
            f"├─ Rarity Scaling: `×{breakdown['rarity_scaling']:.1f}`",
            f"├─ Total Multiplier: `×{breakdown['final_multiplier']:.1f}`",
            f"└─ **Final Cost: `{breakdown['final_cost']:,}` ⭐**"
        ]
        
        if breakdown['savings_penalty'] > 0:
            lines.append(f"📈 *+{breakdown['savings_penalty']:,} so với base cost*")
        elif breakdown['savings_penalty'] < 0:
            lines.append(f"📉 *{breakdown['savings_penalty']:,} so với base cost*")
        
        return "\n".join(lines)

# Export alias for compatibility
DynamicRerollCostSystem = DynamicRerollCostCalculator

class MaidRerollHistory:
    """Quản lý lịch sử reroll của maid"""
    
    def __init__(self, db_path: str = "farm_bot.db"):
        self.db_path = db_path
        self.init_tables()
    
    def init_tables(self):
        """Tạo bảng lưu lịch sử reroll"""
        import sqlite3
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS maid_reroll_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    maid_instance_id TEXT NOT NULL,
                    old_buffs TEXT NOT NULL,
                    new_buffs TEXT NOT NULL,
                    stardust_cost INTEGER NOT NULL,
                    reroll_time TEXT NOT NULL,
                    FOREIGN KEY (maid_instance_id) REFERENCES user_maids(instance_id)
                )
            ''')
            
            # Index cho performance
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_reroll_history_maid 
                ON maid_reroll_history(maid_instance_id)
            ''')
            
            conn.commit()
    
    def add_reroll_record(self, user_id: int, maid_instance_id: str, 
                         old_buffs: List[MaidBuff], new_buffs: List[MaidBuff], 
                         cost: int) -> bool:
        """Thêm record reroll mới"""
        import sqlite3
        import json
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO maid_reroll_history 
                    (user_id, maid_instance_id, old_buffs, new_buffs, stardust_cost, reroll_time)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    user_id,
                    maid_instance_id, 
                    json.dumps([buff.to_dict() for buff in old_buffs]),
                    json.dumps([buff.to_dict() for buff in new_buffs]),
                    cost,
                    datetime.now().isoformat()
                ))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error adding reroll record: {e}")
            return False
    
    def get_maid_reroll_history(self, maid_instance_id: str) -> List[Dict]:
        """Lấy lịch sử reroll của maid"""
        import sqlite3
        import json
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT old_buffs, new_buffs, stardust_cost, reroll_time
                    FROM maid_reroll_history 
                    WHERE maid_instance_id = ?
                    ORDER BY reroll_time ASC
                ''', (maid_instance_id,))
                
                results = []
                for row in cursor.fetchall():
                    results.append({
                        'old_buffs': json.loads(row[0]),
                        'new_buffs': json.loads(row[1]), 
                        'cost': row[2],
                        'time': row[3]
                    })
                
                return results
        except Exception as e:
            print(f"Error getting reroll history: {e}")
            return []
    
    def get_reroll_times(self, maid_instance_id: str) -> List[str]:
        """Lấy danh sách thời gian reroll (cho time multiplier)"""
        import sqlite3
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT reroll_time FROM maid_reroll_history 
                    WHERE maid_instance_id = ?
                    ORDER BY reroll_time DESC
                ''', (maid_instance_id,))
                
                return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error getting reroll times: {e}")
            return []

# Global instances
dynamic_cost_calculator = DynamicRerollCostCalculator()
reroll_history_manager = MaidRerollHistory() 