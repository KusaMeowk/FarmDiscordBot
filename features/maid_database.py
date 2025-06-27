import aiosqlite
import json
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple
from database.models import UserMaid, MaidBuff, GachaHistory, UserGachaPity, MaidTrade, UserStardust
from utils.enhanced_logging import get_database_logger

logger = get_database_logger()

class MaidDatabase:
    """Quản lý các bảng database liên quan đến maid system, sử dụng chung connection"""
    
    def __init__(self, db_connection: aiosqlite.Connection):
        """
        Khởi tạo MaidDatabase với một connection aiosqlite đã có.
        """
        self.conn = db_connection
    
    async def init_tables(self):
        """Khởi tạo bất đồng bộ các bảng cho hệ thống Maid"""
        # Bảng user_maids
        await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS user_maids (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                maid_id TEXT NOT NULL,
                instance_id TEXT NOT NULL UNIQUE,
                custom_name TEXT,
                obtained_at TEXT NOT NULL,
                is_active BOOLEAN DEFAULT 0,
                buff_values TEXT NOT NULL
            )
        ''')
        
        # (Các bảng khác tương tự)
        await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS gacha_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                roll_type TEXT NOT NULL,
                cost INTEGER NOT NULL,
                results TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        ''')
        
        await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS user_stardust (
                user_id INTEGER PRIMARY KEY,
                stardust_amount INTEGER DEFAULT 0,
                last_updated TEXT NOT NULL
            )
        ''')

        await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS maid_trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trade_id TEXT NOT NULL UNIQUE,
                from_user_id INTEGER NOT NULL,
                to_user_id INTEGER NOT NULL,
                maid_instance_id TEXT NOT NULL,
                trade_status TEXT DEFAULT 'pending',
                created_at TEXT NOT NULL,
                completed_at TEXT
            )
        ''')
        
        await self.conn.commit()
        logger.info("🎀 Maid tables initialized successfully.")

    async def add_user_maid(self, user_maid: UserMaid) -> bool:
        """Thêm maid mới cho user"""
        try:
            await self.conn.execute('''
                INSERT INTO user_maids 
                (user_id, maid_id, instance_id, custom_name, obtained_at, is_active, buff_values)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_maid.user_id,
                user_maid.maid_id,
                user_maid.instance_id,
                user_maid.custom_name,
                user_maid.obtained_at.isoformat(),
                user_maid.is_active,
                json.dumps([buff.to_dict() for buff in user_maid.buff_values])
            ))
            await self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error adding user maid: {e}", exc_info=True)
            return False

    async def get_user_maids(self, user_id: int) -> List[UserMaid]:
        """Lấy tất cả maids của user"""
        try:
            cursor = await self.conn.execute('''
                SELECT instance_id, user_id, maid_id, custom_name, obtained_at, is_active, buff_values
                FROM user_maids WHERE user_id = ?
                ORDER BY obtained_at DESC
            ''', (user_id,))
            
            rows = await cursor.fetchall()
            maids = []
            for row in rows:
                # Use index access instead of dict access for compatibility
                buff_data = json.loads(row[6])  # buff_values is at index 6
                buffs = [MaidBuff.from_dict(buff) for buff in buff_data]
                
                maid = UserMaid(
                    instance_id=row[0],
                    user_id=row[1],
                    maid_id=row[2],
                    custom_name=row[3],
                    obtained_at=datetime.fromisoformat(row[4]),
                    is_active=bool(row[5]),
                    buff_values=buffs
                )
                maids.append(maid)
            
            return maids
        except Exception as e:
            logger.error(f"Error getting user maids for {user_id}: {e}", exc_info=True)
            return []

    async def get_active_maid(self, user_id: int) -> Optional[UserMaid]:
        """Lấy maid đang active của user"""
        try:
            cursor = await self.conn.execute('''
                SELECT instance_id, user_id, maid_id, custom_name, obtained_at, is_active, buff_values
                FROM user_maids WHERE user_id = ? AND is_active = 1
                LIMIT 1
            ''', (user_id,))
            
            row = await cursor.fetchone()
            if row:
                # Use index access instead of dict access for compatibility
                buff_data = json.loads(row[6])  # buff_values is at index 6
                buffs = [MaidBuff.from_dict(buff) for buff in buff_data]
                
                return UserMaid(
                    instance_id=row[0],
                    user_id=row[1],
                    maid_id=row[2],
                    custom_name=row[3],
                    obtained_at=datetime.fromisoformat(row[4]),
                    is_active=bool(row[5]),
                    buff_values=buffs
                )
            return None
        except Exception as e:
            logger.error(f"Error getting active maid for {user_id}: {e}", exc_info=True)
            return None

    async def set_active_maid(self, user_id: int, instance_id: str) -> bool:
        """Set maid làm active (chỉ 1 maid active tại 1 thời điểm)"""
        try:
            # Validate ownership first
            cursor = await self.conn.execute("SELECT 1 FROM user_maids WHERE instance_id = ? AND user_id = ?", (instance_id, user_id))
            result = await cursor.fetchone()
            if result is None:
                logger.warning(f"Security warning: User {user_id} tried to activate maid {instance_id} they don't own")
                return False
            
            # Deactivate all current maids for this user
            await self.conn.execute("UPDATE user_maids SET is_active = 0 WHERE user_id = ?", (user_id,))
            
            # Activate the selected maid
            cursor = await self.conn.execute("UPDATE user_maids SET is_active = 1 WHERE user_id = ? AND instance_id = ?", (user_id, instance_id))
            
            await self.conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error setting active maid for {user_id}: {e}", exc_info=True)
            return False
    
    # (Các hàm khác được chuyển đổi tương tự sang async)
    async def rename_maid(self, user_id: int, instance_id: str, new_name: str) -> bool:
        try:
            cursor = await self.conn.execute('''
                UPDATE user_maids SET custom_name = ?
                WHERE user_id = ? AND instance_id = ?
            ''', (new_name, user_id, instance_id))
            await self.conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error renaming maid {instance_id}: {e}", exc_info=True)
            return False

    async def delete_maid(self, user_id: int, instance_id: str) -> bool:
        try:
            cursor = await self.conn.execute('''
                DELETE FROM user_maids 
                WHERE user_id = ? AND instance_id = ?
            ''', (user_id, instance_id))
            await self.conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error deleting maid {instance_id}: {e}", exc_info=True)
            return False

    async def update_maid_buffs(self, user_id: int, instance_id: str, new_buffs: List[MaidBuff]) -> bool:
        try:
            buff_json = json.dumps([buff.to_dict() for buff in new_buffs])
            cursor = await self.conn.execute('''
                UPDATE user_maids SET buff_values = ?
                WHERE user_id = ? AND instance_id = ?
            ''', (buff_json, user_id, instance_id))
            await self.conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error updating buffs for maid {instance_id}: {e}", exc_info=True)
            return False

    async def add_gacha_history(self, history: GachaHistory) -> bool:
        try:
            await self.conn.execute('''
                INSERT INTO gacha_history (user_id, roll_type, cost, results, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                history.user_id,
                history.roll_type,
                history.cost,
                json.dumps(history.results),
                history.created_at.isoformat()
            ))
            await self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error adding gacha history for user {history.user_id}: {e}", exc_info=True)
            return False

    async def get_user_stardust(self, user_id: int) -> Optional[UserStardust]:
        try:
            cursor = await self.conn.execute('SELECT user_id, stardust_amount, last_updated FROM user_stardust WHERE user_id = ?', (user_id,))
            row = await cursor.fetchone()
            if row:
                return UserStardust(
                    user_id=row[0],      # user_id at index 0
                    stardust_amount=row[1],  # stardust_amount at index 1  
                    last_updated=datetime.fromisoformat(row[2])  # last_updated at index 2
                )
            return None
        except Exception as e:
            logger.error(f"Error getting stardust for user {user_id}: {e}", exc_info=True)
            return None

    async def update_user_stardust(self, stardust: UserStardust) -> bool:
        try:
            await self.conn.execute('''
                INSERT OR REPLACE INTO user_stardust (user_id, stardust_amount, last_updated)
                VALUES (?, ?, ?)
            ''', (stardust.user_id, stardust.stardust_amount, stardust.last_updated.isoformat()))
            await self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error updating stardust for user {stardust.user_id}: {e}", exc_info=True)
            return False

    async def get_user_gacha_history(self, user_id: int) -> List[GachaHistory]:
        try:
            cursor = await self.conn.execute('SELECT user_id, roll_type, cost, results, created_at FROM gacha_history WHERE user_id = ?', (user_id,))
            rows = await cursor.fetchall()
            return [GachaHistory(
                user_id=row[0],        # user_id at index 0
                roll_type=row[1],      # roll_type at index 1
                cost=row[2],           # cost at index 2
                results=json.loads(row[3]),  # results at index 3
                created_at=datetime.fromisoformat(row[4])  # created_at at index 4
            ) for row in rows]
        except Exception as e:
            logger.error(f"Error getting gacha history for user {user_id}: {e}", exc_info=True)
            return []

    # ======================
    # TRADE OPERATIONS
    # ======================
    
    async def create_trade(self, trade: MaidTrade) -> bool:
        """Tạo trade mới"""
        try:
            await self.conn.execute('''
                INSERT INTO maid_trades 
                (trade_id, from_user_id, to_user_id, maid_instance_id, trade_status, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                trade.trade_id,
                trade.from_user_id,
                trade.to_user_id,
                trade.maid_instance_id,
                trade.trade_status,
                trade.created_at.isoformat()
            ))
            await self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error creating trade: {e}", exc_info=True)
            return False
    
    async def get_user_trades(self, user_id: int, status: str = None) -> List[MaidTrade]:
        """Lấy danh sách trade của user"""
        try:
            if status:
                cursor = await self.conn.execute('''
                    SELECT trade_id, from_user_id, to_user_id, maid_instance_id, 
                           trade_status, created_at, completed_at
                    FROM maid_trades 
                    WHERE (from_user_id = ? OR to_user_id = ?) AND trade_status = ?
                    ORDER BY created_at DESC
                ''', (user_id, user_id, status))
            else:
                cursor = await self.conn.execute('''
                    SELECT trade_id, from_user_id, to_user_id, maid_instance_id, 
                           trade_status, created_at, completed_at
                    FROM maid_trades 
                    WHERE from_user_id = ? OR to_user_id = ?
                    ORDER BY created_at DESC
                ''', (user_id, user_id))
            
            trades = []
            rows = await cursor.fetchall()
            for row in rows:
                trade = MaidTrade(
                    trade_id=row[0],           # trade_id at index 0
                    from_user_id=row[1],      # from_user_id at index 1
                    to_user_id=row[2],        # to_user_id at index 2
                    maid_instance_id=row[3],  # maid_instance_id at index 3
                    trade_status=row[4],      # trade_status at index 4
                    created_at=datetime.fromisoformat(row[5]),    # created_at at index 5
                    completed_at=datetime.fromisoformat(row[6]) if row[6] else None  # completed_at at index 6
                )
                trades.append(trade)
            
            return trades
        except Exception as e:
            logger.error(f"Error getting user trades for {user_id}: {e}", exc_info=True)
            return []
    
    async def update_trade_status(self, trade_id: str, status: str) -> bool:
        """Cập nhật trạng thái trade"""
        try:
            cursor = await self.conn.execute('''
                UPDATE maid_trades 
                SET trade_status = ?, completed_at = ?
                WHERE trade_id = ?
            ''', (status, datetime.now().isoformat(), trade_id))
            await self.conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error updating trade status for {trade_id}: {e}", exc_info=True)
            return False
    
    async def transfer_maid_ownership(self, instance_id: str, new_user_id: int) -> bool:
        """Chuyển quyền sở hữu maid (dùng cho trade)"""
        try:
            cursor = await self.conn.execute('''
                UPDATE user_maids 
                SET user_id = ?, is_active = 0
                WHERE instance_id = ?
            ''', (new_user_id, instance_id))
            await self.conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error transferring maid ownership for {instance_id}: {e}", exc_info=True)
            return False
    
    # ======================
    # STATISTICS
    # ======================
    
    async def get_user_maid_stats(self, user_id: int) -> Dict[str, Any]:
        """Lấy thống kê maid của user"""
        try:
            cursor = await self.conn.execute('SELECT COUNT(*) FROM user_maids WHERE user_id = ?', (user_id,))
            result = await cursor.fetchone()
            total_maids = result[0] if result else 0
            
            cursor = await self.conn.execute('''
                SELECT maid_id FROM user_maids WHERE user_id = ?
            ''', (user_id,))
            
            rarity_count = {"UR": 0, "SSR": 0, "SR": 0, "R": 0}
            rows = await cursor.fetchall()
            for row in rows:
                maid_id = row[0]  # maid_id at index 0
                # Determine rarity from maid_id
                # This assumes MAID_TEMPLATES is accessible
                # If not, you might need to pass it or handle differently
                try:
                    from features.maid_config import MAID_TEMPLATES
                    template = MAID_TEMPLATES.get(maid_id)
                    if template:
                        rarity = template["rarity"]
                        if rarity in rarity_count:
                            rarity_count[rarity] += 1
                except:
                    # Fallback logic if templates not available
                    rarity_count["R"] += 1
            
            cursor = await self.conn.execute('''
                SELECT SUM(cost) FROM gacha_history WHERE user_id = ?
            ''', (user_id,))
            result = await cursor.fetchone()
            total_spent = result[0] if result and result[0] else 0
            
            cursor = await self.conn.execute('''
                SELECT COUNT(*) FROM gacha_history WHERE user_id = ?
            ''', (user_id,))
            result = await cursor.fetchone()
            total_rolls = result[0] if result else 0
            
            return {
                "total_maids": total_maids,
                "rarity_count": rarity_count, 
                "total_spent": total_spent,
                "total_rolls": total_rolls
            }
        except Exception as e:
            logger.error(f"Error getting user maid stats for {user_id}: {e}", exc_info=True)
            return {"total_maids": 0, "rarity_count": {"UR": 0, "SSR": 0, "SR": 0, "R": 0}, 
                    "total_spent": 0, "total_rolls": 0} 