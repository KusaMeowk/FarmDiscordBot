import aiosqlite
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import config
from .models import User, Crop, InventoryItem, WeatherNotification, MarketNotification, AINotification, EventClaim, BotState, Species, UserLivestock, UserFacilities, LivestockProduct
from utils.enhanced_logging import get_database_logger, log_error

logger = get_database_logger()

class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection = None
        self._connection_pool = {}  # Simple connection pooling
        self._pool_size = 5
        self._query_cache = {}  # Cache for expensive queries
        self._cache_expiry = timedelta(minutes=5)
    
    async def get_connection(self):
        """Get a database connection from pool or create new one"""
        try:
            # Try to reuse existing connection - check if connection exists and is not closed
            if self.connection:
                try:
                    # Test the connection by executing a simple query
                    await self.connection.execute('SELECT 1')
                    return self.connection
                except:
                    # Connection is closed or invalid, need to recreate
                    self.connection = None
            
            # Create new connection
            self.connection = await aiosqlite.connect(self.db_path)
            self.connection.row_factory = aiosqlite.Row  # Enable dict-like access
            return self.connection
        except Exception as e:
            print(f"Database connection error: {e}")
            # Fallback: create temporary connection
            return await aiosqlite.connect(self.db_path)
    
    async def ensure_connection(self):
        """Ensure database connection is alive, reconnect if needed"""
        if self.connection is None:
            await self.init_db()
            return
            
        try:
            # Test connection
            await self.connection.execute('SELECT 1')
        except Exception as e:
            logger.warning("🔄 Database connection lost, reconnecting...")
            await self._reconnect()
    
    async def _reconnect(self):
        """Reconnect to database with retry logic"""
        self._connection_attempts += 1
        
        if self._connection_attempts > self._max_retries:
            log_error(logger, f"❌ Database connection failed after {self._max_retries} attempts")
            raise Exception("Database connection failed permanently")
        
        try:
            if self.connection:
                await self.connection.close()
                
            self.connection = await aiosqlite.connect(self.db_path)
            await self._create_tables()
            logger.info(f"✅ Database reconnected (attempt {self._connection_attempts})")
            self._connection_attempts = 0  # Reset on successful connection
            
        except Exception as e:
            log_error(logger, f"❌ Reconnection attempt {self._connection_attempts} failed", e)
            raise
    
    async def init_db(self):
        """Initialize database and create tables"""
        self.connection = await aiosqlite.connect(self.db_path)
        await self._create_tables()
        logger.info("Database initialized")
    
    async def close(self):
        """Close database connection"""
        if self.connection:
            await self.connection.close()
    
    async def table_exists(self, table_name: str) -> bool:
        """Check if table exists"""
        try:
            cursor = await self.connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                (table_name,)
            )
            row = await cursor.fetchone()
            return row is not None
        except Exception:
            return False
    
    async def get_all_users(self) -> List[dict]:
        """Get all users as dictionaries"""
        try:
            cursor = await self.connection.execute('SELECT * FROM users')
            rows = await cursor.fetchall()
            
            # Get column names
            description = cursor.description
            columns = [desc[0] for desc in description]
            
            # Convert to dictionaries
            users = []
            for row in rows:
                user_dict = dict(zip(columns, row))
                users.append(user_dict)
            
            return users
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            return []
    
    async def _create_tables(self):
        """Create all database tables"""
        
        # Users table
        await self.connection.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT NOT NULL,
                money INTEGER DEFAULT 1000,
                land_slots INTEGER DEFAULT 4,
                last_daily TEXT,
                daily_streak INTEGER DEFAULT 0,
                joined_date TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Crops table
        await self.connection.execute('''
            CREATE TABLE IF NOT EXISTS crops (
                crop_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                crop_type TEXT NOT NULL,
                plot_index INTEGER NOT NULL,
                plant_time TEXT NOT NULL,
                growth_stage INTEGER DEFAULT 0,
                buffs_applied TEXT DEFAULT '',
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                UNIQUE(user_id, plot_index)
            )
        ''')
        
        # Inventory table
        await self.connection.execute('''
            CREATE TABLE IF NOT EXISTS inventory (
                user_id INTEGER NOT NULL,
                item_type TEXT NOT NULL,
                item_id TEXT NOT NULL,
                quantity INTEGER DEFAULT 0,
                PRIMARY KEY (user_id, item_type, item_id),
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Seasonal events table
        await self.connection.execute('''
            CREATE TABLE IF NOT EXISTS seasonal_events (
                event_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                rewards TEXT,
                is_active INTEGER DEFAULT 0
            )
        ''')
        
        # Weather notifications table
        await self.connection.execute('''
            CREATE TABLE IF NOT EXISTS weather_notifications (
                guild_id INTEGER PRIMARY KEY,
                channel_id INTEGER NOT NULL,
                enabled BOOLEAN DEFAULT 1,
                last_weather TEXT,
                city TEXT DEFAULT 'Ho Chi Minh City'
            )
        ''')
        
        # Market notifications table
        await self.connection.execute('''
            CREATE TABLE IF NOT EXISTS market_notifications (
                guild_id INTEGER PRIMARY KEY,
                channel_id INTEGER NOT NULL,
                enabled BOOLEAN DEFAULT 1,
                last_market_modifier REAL DEFAULT 1.0,
                threshold REAL DEFAULT 0.1
            )
        ''')
        
        # AI notifications table
        await self.connection.execute('''
            CREATE TABLE IF NOT EXISTS ai_notifications (
                guild_id INTEGER PRIMARY KEY,
                channel_id INTEGER NOT NULL,
                enabled BOOLEAN DEFAULT 1,
                event_notifications BOOLEAN DEFAULT 1,
                weather_notifications BOOLEAN DEFAULT 1,
                economic_notifications BOOLEAN DEFAULT 1
            )
        ''')
        
        # Event claims table để tracking user đã claim event reward
        await self.connection.execute('''
            CREATE TABLE IF NOT EXISTS event_claims (
                user_id INTEGER NOT NULL,
                event_id TEXT NOT NULL,
                claimed_at TEXT NOT NULL,
                PRIMARY KEY (user_id, event_id),
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Bot state table để lưu trạng thái hệ thống
        await self.connection.execute('''
            CREATE TABLE IF NOT EXISTS bot_states (
                state_key TEXT PRIMARY KEY,
                state_data TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')
        
        # Species table - định nghĩa loài cá/thú
        await self.connection.execute('''
            CREATE TABLE IF NOT EXISTS species (
                species_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                species_type TEXT NOT NULL,
                tier INTEGER NOT NULL,
                buy_price INTEGER NOT NULL,
                sell_price INTEGER NOT NULL,
                growth_time INTEGER NOT NULL,
                special_ability TEXT DEFAULT '',
                emoji TEXT DEFAULT '🐟'
            )
        ''')
        
        # User livestock table - cá/thú của user
        await self.connection.execute('''
            CREATE TABLE IF NOT EXISTS user_livestock (
                livestock_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                species_id TEXT NOT NULL,
                facility_type TEXT NOT NULL,
                facility_slot INTEGER NOT NULL,
                birth_time TEXT NOT NULL,
                is_adult BOOLEAN DEFAULT FALSE,
                last_product_time TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                FOREIGN KEY (species_id) REFERENCES species (species_id),
                UNIQUE(user_id, facility_type, facility_slot)
            )
        ''')
        
        # User facilities table - cơ sở hạ tầng
        await self.connection.execute('''
            CREATE TABLE IF NOT EXISTS user_facilities (
                user_id INTEGER PRIMARY KEY,
                pond_slots INTEGER DEFAULT 2,
                barn_slots INTEGER DEFAULT 2,
                pond_level INTEGER DEFAULT 1,
                barn_level INTEGER DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Livestock products table - sản phẩm từ thú nuôi
        await self.connection.execute('''
            CREATE TABLE IF NOT EXISTS livestock_products (
                species_id TEXT PRIMARY KEY,
                product_name TEXT NOT NULL,
                product_emoji TEXT NOT NULL,
                production_time INTEGER NOT NULL,
                sell_price INTEGER NOT NULL,
                FOREIGN KEY (species_id) REFERENCES species (species_id)
            )
        ''')
        
        await self.connection.commit()
        
        # Migration: Add economic_notifications column if missing
        try:
            await self.connection.execute('''
                ALTER TABLE ai_notifications 
                ADD COLUMN economic_notifications BOOLEAN DEFAULT 1
            ''')
            await self.connection.commit()
            logger.info("✅ Added economic_notifications column to ai_notifications table")
        except Exception:
            # Column might already exist, ignore error
            pass
    
    # User methods
    async def get_user(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        cursor = await self.connection.execute(
            'SELECT * FROM users WHERE user_id = ?', (user_id,)
        )
        row = await cursor.fetchone()
        
        if row:
            return User(
                user_id=row[0],
                username=row[1],
                money=row[2],
                land_slots=row[3],
                last_daily=datetime.fromisoformat(row[4]) if row[4] else None,
                daily_streak=row[5],
                joined_date=datetime.fromisoformat(row[6])
            )
        return None
    
    async def create_user(self, user_id: int, username: str) -> User:
        """Create new user"""
        user = User(user_id, username)
        
        await self.connection.execute('''
            INSERT OR REPLACE INTO users 
            (user_id, username, money, land_slots, daily_streak, joined_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user.user_id, user.username, user.money, user.land_slots,
              user.daily_streak, user.joined_date.isoformat()))
        
        await self.connection.commit()
        return user
    
    async def update_user(self, user: User):
        """Update user data"""
        await self.connection.execute('''
            UPDATE users SET username = ?, money = ?, land_slots = ?,
            last_daily = ?, daily_streak = ? WHERE user_id = ?
        ''', (user.username, user.money, user.land_slots,
              user.last_daily.isoformat() if user.last_daily else None,
              user.daily_streak, user.user_id))
        
        await self.connection.commit()
    
    async def get_top_users(self, limit: int = 10) -> List[User]:
        """Get top users by money"""
        cursor = await self.connection.execute(
            'SELECT * FROM users ORDER BY money DESC LIMIT ?', (limit,)
        )
        rows = await cursor.fetchall()
        
        users = []
        for row in rows:
            users.append(User(
                user_id=row[0],
                username=row[1],
                money=row[2],
                land_slots=row[3],
                last_daily=datetime.fromisoformat(row[4]) if row[4] else None,
                daily_streak=row[5],
                joined_date=datetime.fromisoformat(row[6])
            ))
        
        return users
    
    # Crop methods
    async def plant_crop(self, user_id: int, crop_type: str, plot_index: int, plant_time: datetime):
        """Plant a crop on user's land with error handling"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    INSERT INTO crops (user_id, crop_type, plant_time, plot_index, growth_stage, buffs_applied)
                    VALUES (?, ?, ?, ?, 0, ?)
                ''', (user_id, crop_type, plant_time, plot_index, '{}'))
                await db.commit()
        except aiosqlite.IntegrityError as e:
            print(f"Database integrity error in plant_crop: {e}")
            raise Exception("Không thể trồng cây. Có thể ô đất đã được sử dụng.")
        except Exception as e:
            print(f"Database error in plant_crop: {e}")
            raise Exception("Lỗi cơ sở dữ liệu khi trồng cây.")
    
    async def get_user_crops(self, user_id: int) -> List[Crop]:
        """Get all crops for a user"""
        cursor = await self.connection.execute(
            'SELECT * FROM crops WHERE user_id = ?', (user_id,)
        )
        rows = await cursor.fetchall()
        
        crops = []
        for row in rows:
            crops.append(Crop(
                crop_id=row[0],
                user_id=row[1],
                crop_type=row[2],
                plot_index=row[3],
                plant_time=datetime.fromisoformat(row[4]),
                growth_stage=row[5],
                buffs_applied=row[6]
            ))
        
        return crops
    
    async def get_user_crops_optimized(self, user_id: int) -> List[Crop]:
        """Optimized version of get_user_crops with caching"""
        cache_key = f"user_crops_{user_id}"
        
        # Check cache first
        if cache_key in self._query_cache:
            cached_data, timestamp = self._query_cache[cache_key]
            if datetime.now() - timestamp < self._cache_expiry:
                return cached_data
        
        # Query database
        crops = await self.get_user_crops(user_id)
        
        # Cache result
        self._query_cache[cache_key] = (crops, datetime.now())
        
        # Cleanup old cache entries
        if len(self._query_cache) > 100:
            self._cleanup_query_cache()
        
        return crops
    
    def _cleanup_query_cache(self):
        """Remove expired cache entries"""
        current_time = datetime.now()
        expired_keys = []
        
        for key, (data, timestamp) in self._query_cache.items():
            if current_time - timestamp > self._cache_expiry:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self._query_cache[key]
    
    def invalidate_user_cache(self, user_id: int):
        """Invalidate cached data for a specific user"""
        keys_to_remove = [key for key in self._query_cache if f"_{user_id}" in key]
        for key in keys_to_remove:
            del self._query_cache[key]
    
    async def harvest_crop(self, crop_id: int):
        """Harvest a crop with error handling"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Start transaction
                async with db.execute('BEGIN'):
                    await db.execute('DELETE FROM crops WHERE crop_id = ?', (crop_id,))
                    await db.commit()
        except Exception as e:
            print(f"Database error in harvest_crop: {e}")
            raise Exception("Lỗi cơ sở dữ liệu khi thu hoạch.")
    
    # Inventory methods
    async def add_item(self, user_id: int, item_type: str, item_id: str, quantity: int):
        """Add item to inventory"""
        await self.connection.execute('''
            INSERT OR REPLACE INTO inventory (user_id, item_type, item_id, quantity)
            VALUES (?, ?, ?, COALESCE((SELECT quantity FROM inventory 
                    WHERE user_id = ? AND item_type = ? AND item_id = ?), 0) + ?)
        ''', (user_id, item_type, item_id, user_id, item_type, item_id, quantity))
        
        await self.connection.commit()
    
    async def get_user_inventory(self, user_id: int) -> List[InventoryItem]:
        """Get user's inventory"""
        cursor = await self.connection.execute(
            'SELECT * FROM inventory WHERE user_id = ? AND quantity > 0', (user_id,)
        )
        rows = await cursor.fetchall()
        
        items = []
        for row in rows:
            items.append(InventoryItem(
                user_id=row[0],
                item_type=row[1],
                item_id=row[2],
                quantity=row[3]
            ))
        
        return items
    
    async def use_item(self, user_id: int, item_type: str, item_id: str, quantity: int = 1) -> bool:
        """Use item from inventory with atomic transaction"""
        try:
            # Start transaction
            await self.connection.execute('BEGIN IMMEDIATE')
            
            # Atomic update with check
            cursor = await self.connection.execute('''
                UPDATE inventory 
                SET quantity = quantity - ? 
                WHERE user_id = ? AND item_type = ? AND item_id = ? 
                AND quantity >= ?
                RETURNING quantity
            ''', (quantity, user_id, item_type, item_id, quantity))
            
            result = await cursor.fetchone()
            
            if not result:
                # Not enough items or item doesn't exist
                await self.connection.execute('ROLLBACK')
                return False
            
            new_quantity = result[0]
            
            # Remove item if quantity is 0
            if new_quantity <= 0:
                await self.connection.execute(
                    'DELETE FROM inventory WHERE user_id = ? AND item_type = ? AND item_id = ?',
                    (user_id, item_type, item_id)
                )
            
            await self.connection.commit()
            return True
            
        except Exception as e:
            await self.connection.execute('ROLLBACK')
            log_error(logger, "❌ Error using item from inventory", e)
            return False
    
    # Additional methods for leaderboard
    async def get_top_users_by_money(self, limit: int = 10) -> List[User]:
        """Get top users by money"""
        cursor = await self.connection.execute(
            'SELECT * FROM users ORDER BY money DESC LIMIT ?', (limit,)
        )
        rows = await cursor.fetchall()
        
        users = []
        for row in rows:
            users.append(User(
                user_id=row[0],
                username=row[1],
                money=row[2],
                land_slots=row[3],
                last_daily=datetime.fromisoformat(row[4]) if row[4] else None,
                daily_streak=row[5],
                joined_date=datetime.fromisoformat(row[6])
            ))
        
        return users
    
    async def get_top_users_by_streak(self, limit: int = 10) -> List[User]:
        """Get top users by daily streak"""
        cursor = await self.connection.execute(
            'SELECT * FROM users ORDER BY daily_streak DESC LIMIT ?', (limit,)
        )
        rows = await cursor.fetchall()
        
        users = []
        for row in rows:
            users.append(User(
                user_id=row[0],
                username=row[1],
                money=row[2],
                land_slots=row[3],
                last_daily=datetime.fromisoformat(row[4]) if row[4] else None,
                daily_streak=row[5],
                joined_date=datetime.fromisoformat(row[6])
            ))
        
        return users
    
    async def get_top_users_by_land(self, limit: int = 10) -> List[User]:
        """Get top users by land slots"""
        cursor = await self.connection.execute(
            'SELECT * FROM users ORDER BY land_slots DESC LIMIT ?', (limit,)
        )
        rows = await cursor.fetchall()
        
        users = []
        for row in rows:
            users.append(User(
                user_id=row[0],
                username=row[1],
                money=row[2],
                land_slots=row[3],
                last_daily=datetime.fromisoformat(row[4]) if row[4] else None,
                daily_streak=row[5],
                joined_date=datetime.fromisoformat(row[6])
            ))
        
        return users
    
    # Weather notification methods
    async def set_weather_notification(self, guild_id: int, channel_id: int, city: str = "Ho Chi Minh City"):
        """Set up weather notification for a guild"""
        await self.connection.execute('''
            INSERT OR REPLACE INTO weather_notifications 
            (guild_id, channel_id, enabled, city)
            VALUES (?, ?, 1, ?)
        ''', (guild_id, channel_id, city))
        
        await self.connection.commit()
    
    async def get_weather_notification(self, guild_id: int) -> Optional[WeatherNotification]:
        """Get weather notification settings for a guild"""
        
        cursor = await self.connection.execute(
            'SELECT * FROM weather_notifications WHERE guild_id = ?', (guild_id,)
        )
        row = await cursor.fetchone()
        
        if row:
            return WeatherNotification(
                guild_id=row[0],
                channel_id=row[1],
                enabled=bool(row[2]),
                last_weather=row[3],
                city=row[4]
            )
        return None
    
    async def update_weather_notification(self, guild_id: int, last_weather: str):
        """Update last weather for a guild"""
        await self.connection.execute(
            'UPDATE weather_notifications SET last_weather = ? WHERE guild_id = ?',
            (last_weather, guild_id)
        )
        await self.connection.commit()
    
    async def toggle_weather_notification(self, guild_id: int, enabled: bool):
        """Enable/disable weather notifications for a guild"""
        await self.connection.execute(
            'UPDATE weather_notifications SET enabled = ? WHERE guild_id = ?',
            (enabled, guild_id)
        )
        await self.connection.commit()
    
    async def get_all_weather_notifications(self) -> List[WeatherNotification]:
        """Get all enabled weather notifications"""
        
        cursor = await self.connection.execute(
            'SELECT * FROM weather_notifications WHERE enabled = 1'
        )
        rows = await cursor.fetchall()
        
        notifications = []
        for row in rows:
            notifications.append(WeatherNotification(
                guild_id=row[0],
                channel_id=row[1],
                enabled=bool(row[2]),
                last_weather=row[3],
                city=row[4]
            ))
        
        return notifications
    
    # Market notification methods
    async def set_market_notification(self, guild_id: int, channel_id: int, threshold: float = 0.1):
        """Set up market notification for a guild"""
        await self.connection.execute('''
            INSERT OR REPLACE INTO market_notifications 
            (guild_id, channel_id, enabled, threshold)
            VALUES (?, ?, 1, ?)
        ''', (guild_id, channel_id, threshold))
        
        await self.connection.commit()
    
    async def get_market_notification(self, guild_id: int) -> Optional[MarketNotification]:
        """Get market notification settings for a guild"""
        
        cursor = await self.connection.execute(
            'SELECT * FROM market_notifications WHERE guild_id = ?', (guild_id,)
        )
        row = await cursor.fetchone()
        
        if row:
            return MarketNotification(
                guild_id=row[0],
                channel_id=row[1],
                enabled=bool(row[2]),
                last_market_modifier=row[3],
                threshold=row[4]
            )
        return None
    
    async def update_market_notification(self, guild_id: int, last_market_modifier: float):
        """Update last market modifier for a guild"""
        await self.connection.execute(
            'UPDATE market_notifications SET last_market_modifier = ? WHERE guild_id = ?',
            (last_market_modifier, guild_id)
        )
        await self.connection.commit()
    
    async def toggle_market_notification(self, guild_id: int, enabled: bool):
        """Enable/disable market notifications for a guild"""
        await self.connection.execute(
            'UPDATE market_notifications SET enabled = ? WHERE guild_id = ?',
            (enabled, guild_id)
        )
        await self.connection.commit()
    
    async def get_all_market_notifications(self) -> List[MarketNotification]:
        """Get all enabled market notifications"""
        
        cursor = await self.connection.execute(
            'SELECT * FROM market_notifications WHERE enabled = 1'
        )
        rows = await cursor.fetchall()
        
        notifications = []
        for row in rows:
            notifications.append(MarketNotification(
                guild_id=row[0],
                channel_id=row[1],
                enabled=bool(row[2]),
                last_market_modifier=row[3],
                threshold=row[4]
            ))
        
        return notifications
    
    # AI notification methods
    async def set_ai_notification(self, guild_id: int, channel_id: int, 
                                  event_notifications: bool = True, weather_notifications: bool = True,
                                  economic_notifications: bool = True):
        """Set up AI notification for a guild"""
        await self.connection.execute('''
            INSERT OR REPLACE INTO ai_notifications 
            (guild_id, channel_id, enabled, event_notifications, weather_notifications, economic_notifications)
            VALUES (?, ?, 1, ?, ?, ?)
        ''', (guild_id, channel_id, event_notifications, weather_notifications, economic_notifications))
        
        await self.connection.commit()
    
    async def get_ai_notification(self, guild_id: int) -> Optional[AINotification]:
        """Get AI notification settings for a guild"""
        
        cursor = await self.connection.execute(
            'SELECT * FROM ai_notifications WHERE guild_id = ?', (guild_id,)
        )
        row = await cursor.fetchone()
        
        if row:
            return AINotification(
                guild_id=row[0],
                channel_id=row[1],
                enabled=bool(row[2]),
                event_notifications=bool(row[3]),
                weather_notifications=bool(row[4]),
                economic_notifications=bool(row[5]) if len(row) > 5 else True
            )
        return None
    
    async def toggle_ai_notification(self, guild_id: int, enabled: bool):
        """Enable/disable AI notifications for a guild"""
        await self.connection.execute(
            'UPDATE ai_notifications SET enabled = ? WHERE guild_id = ?',
            (enabled, guild_id)
        )
        await self.connection.commit()
    
    async def toggle_ai_event_notification(self, guild_id: int, enabled: bool):
        """Enable/disable AI event notifications for a guild"""
        await self.connection.execute(
            'UPDATE ai_notifications SET event_notifications = ? WHERE guild_id = ?',
            (enabled, guild_id)
        )
        await self.connection.commit()
    
    async def toggle_ai_weather_notification(self, guild_id: int, enabled: bool):
        """Enable/disable AI weather notifications for a guild"""
        await self.connection.execute(
            'UPDATE ai_notifications SET weather_notifications = ? WHERE guild_id = ?',
            (enabled, guild_id)
        )
        await self.connection.commit()
    
    async def toggle_ai_economic_notification(self, guild_id: int, enabled: bool):
        """Enable/disable AI economic notifications for a guild"""
        await self.connection.execute(
            'UPDATE ai_notifications SET economic_notifications = ? WHERE guild_id = ?',
            (enabled, guild_id)
        )
        await self.connection.commit()
    
    async def get_all_ai_notifications(self) -> List[AINotification]:
        """Get all enabled AI notifications"""
        
        cursor = await self.connection.execute(
            'SELECT * FROM ai_notifications WHERE enabled = 1'
        )
        rows = await cursor.fetchall()
        
        notifications = []
        for row in rows:
            notifications.append(AINotification(
                guild_id=row[0],
                channel_id=row[1],
                enabled=bool(row[2]),
                event_notifications=bool(row[3]),
                weather_notifications=bool(row[4]),
                economic_notifications=bool(row[5]) if len(row) > 5 else True
            ))
        
        return notifications
    
    async def update_user_money(self, user_id: int, amount: int):
        """Update user money with transaction safety"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute('BEGIN'):
                    # Get current money
                    async with db.execute('SELECT money FROM users WHERE user_id = ?', (user_id,)) as cursor:
                        row = await cursor.fetchone()
                        if not row:
                            raise Exception("User not found")
                        
                        current_money = row[0]
                        new_money = current_money + amount
                        
                        if new_money < 0:
                            raise Exception("Insufficient funds")
                        
                        # Update money
                        await db.execute('UPDATE users SET money = ? WHERE user_id = ?', (new_money, user_id))
                        await db.commit()
                        
                        return new_money
        except Exception as e:
            print(f"Database error in update_user_money: {e}")
            raise Exception("Lỗi cơ sở dữ liệu khi cập nhật tiền.")
    
    async def execute_transaction(self, operations: list):
        """Execute multiple operations in a single transaction"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute('BEGIN'):
                    for operation in operations:
                        query = operation['query']
                        params = operation.get('params', ())
                        await db.execute(query, params)
                    await db.commit()
        except Exception as e:
            print(f"Transaction error: {e}")
            raise Exception("Lỗi thực hiện giao dịch cơ sở dữ liệu.")
    
    async def buy_seeds_transaction(self, user_id: int, seed_type: str, quantity: int, total_cost: int):
        """Buy seeds with transaction safety - deduct money and add seeds atomically"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute('BEGIN'):
                    # Check current money
                    async with db.execute('SELECT money FROM users WHERE user_id = ?', (user_id,)) as cursor:
                        row = await cursor.fetchone()
                        if not row:
                            raise Exception("User not found")
                        
                        current_money = row[0]
                        if current_money < total_cost:
                            raise Exception("Insufficient funds")
                        
                        new_money = current_money - total_cost
                    
                    # Update money
                    await db.execute('UPDATE users SET money = ? WHERE user_id = ?', (new_money, user_id))
                    
                    # Add seeds to inventory
                    # Check if item already exists
                    async with db.execute('''
                        SELECT quantity FROM inventory 
                        WHERE user_id = ? AND item_type = ? AND item_id = ?
                    ''', (user_id, 'seed', seed_type)) as cursor:
                        row = await cursor.fetchone()
                        
                        if row:
                            # Update existing
                            new_quantity = row[0] + quantity
                            await db.execute('''
                                UPDATE inventory 
                                SET quantity = ? 
                                WHERE user_id = ? AND item_type = ? AND item_id = ?
                            ''', (new_quantity, user_id, 'seed', seed_type))
                        else:
                            # Insert new
                            await db.execute('''
                                INSERT INTO inventory (user_id, item_type, item_id, quantity)
                                VALUES (?, ?, ?, ?)
                            ''', (user_id, 'seed', seed_type, quantity))
                    
                    await db.commit()
                    return new_money
                    
        except Exception as e:
            print(f"Buy seeds transaction error: {e}")
            raise Exception("Lỗi khi mua hạt giống.")
    
    async def sell_crops_transaction(self, user_id: int, crop_type: str, quantity: int, total_earnings: int):
        """Sell crops with transaction safety - remove crops and add money atomically"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute('BEGIN'):
                    # Check current crop quantity
                    async with db.execute('''
                        SELECT quantity FROM inventory 
                        WHERE user_id = ? AND item_type = ? AND item_id = ?
                    ''', (user_id, 'crop', crop_type)) as cursor:
                        row = await cursor.fetchone()
                        if not row or row[0] < quantity:
                            raise Exception("Insufficient crops")
                        
                        new_quantity = row[0] - quantity
                    
                    # Update crop quantity
                    if new_quantity > 0:
                        await db.execute('''
                            UPDATE inventory 
                            SET quantity = ? 
                            WHERE user_id = ? AND item_type = ? AND item_id = ?
                        ''', (new_quantity, user_id, 'crop', crop_type))
                    else:
                        await db.execute('''
                            DELETE FROM inventory 
                            WHERE user_id = ? AND item_type = ? AND item_id = ?
                        ''', (user_id, 'crop', crop_type))
                    
                    # Add money
                    async with db.execute('SELECT money FROM users WHERE user_id = ?', (user_id,)) as cursor:
                        row = await cursor.fetchone()
                        if not row:
                            raise Exception("User not found")
                        
                        new_money = row[0] + total_earnings
                    
                    await db.execute('UPDATE users SET money = ? WHERE user_id = ?', (new_money, user_id))
                    
                    await db.commit()
                    return new_money
                    
        except Exception as e:
            print(f"Sell crops transaction error: {e}")
            raise Exception("Lỗi khi bán nông sản.") 
    
    # Event claim methods
    async def has_claimed_event(self, user_id: int, event_id: str) -> bool:
        """Check if user has already claimed reward for this event"""
        cursor = await self.connection.execute(
            'SELECT 1 FROM event_claims WHERE user_id = ? AND event_id = ?', 
            (user_id, event_id)
        )
        row = await cursor.fetchone()
        return row is not None
    
    async def record_event_claim(self, user_id: int, event_id: str):
        """Record that user has claimed reward for this event"""
        await self.connection.execute('''
            INSERT OR REPLACE INTO event_claims (user_id, event_id, claimed_at)
            VALUES (?, ?, ?)
        ''', (user_id, event_id, datetime.now().isoformat()))
        
        await self.connection.commit()
    
    async def get_user_event_claims(self, user_id: int) -> List[str]:
        """Get list of event IDs that user has claimed"""
        cursor = await self.connection.execute(
            'SELECT event_id FROM event_claims WHERE user_id = ?', (user_id,)
        )
        rows = await cursor.fetchall()
        return [row[0] for row in rows]
    
    # Bot State methods
    async def get_bot_state(self, state_key: str) -> Optional[BotState]:
        """Get bot state by key"""
        cursor = await self.connection.execute(
            'SELECT * FROM bot_states WHERE state_key = ?', (state_key,)
        )
        row = await cursor.fetchone()
        
        if row:
            return BotState.from_dict({
                'state_key': row[0],
                'state_data': row[1],
                'updated_at': row[2]
            })
        return None
    
    async def save_bot_state(self, bot_state: BotState):
        """Save bot state to database"""
        try:
            await self.connection.execute('''
                INSERT OR REPLACE INTO bot_states (state_key, state_data, updated_at)
                VALUES (?, ?, ?)
            ''', (bot_state.state_key, bot_state.to_dict()['state_data'], 
                  bot_state.updated_at.isoformat()))
            
            await self.connection.commit()
            
        except Exception as e:
            log_error(logger, f"Error saving bot state {bot_state.state_key}", e)
            raise Exception("Lỗi lưu trạng thái hệ thống")
    
    async def update_bot_state(self, state_key: str, updates: Dict[str, Any]):
        """Update specific values in bot state"""
        try:
            # Get existing state or create new one
            bot_state = await self.get_bot_state(state_key)
            if not bot_state:
                bot_state = BotState(state_key, {})
            
            # Update values
            bot_state.update_multiple(updates)
            
            # Save back to database
            await self.save_bot_state(bot_state)
            
            return bot_state
            
        except Exception as e:
            log_error(logger, f"Error updating bot state {state_key}", e)
            raise Exception("Lỗi cập nhật trạng thái hệ thống")
    
    async def get_bot_state_value(self, state_key: str, value_key: str, default=None):
        """Get specific value from bot state"""
        bot_state = await self.get_bot_state(state_key)
        if bot_state:
            return bot_state.get_state_value(value_key, default)
        return default
    
    async def set_bot_state_value(self, state_key: str, value_key: str, value: Any):
        """Set specific value in bot state"""
        await self.update_bot_state(state_key, {value_key: value})
    
    async def delete_bot_state(self, state_key: str):
        """Delete bot state"""
        try:
            await self.connection.execute(
                'DELETE FROM bot_states WHERE state_key = ?', (state_key,)
            )
            await self.connection.commit()
        except Exception as e:
            log_error(logger, f"Error deleting bot state {state_key}", e)
            raise Exception("Lỗi xóa trạng thái hệ thống")
    
    # ==================== LIVESTOCK METHODS ====================
    
    # Species methods
    async def get_species(self, species_id: str) -> Optional[Species]:
        """Get species by ID"""
        cursor = await self.connection.execute(
            'SELECT * FROM species WHERE species_id = ?', (species_id,)
        )
        row = await cursor.fetchone()
        
        if row:
            return Species(
                species_id=row[0],
                name=row[1],
                species_type=row[2],
                tier=row[3],
                buy_price=row[4],
                sell_price=row[5],
                growth_time=row[6],
                special_ability=row[7],
                emoji=row[8]
            )
        return None
    
    async def get_all_species(self, species_type: str = None) -> List[Species]:
        """Get all species, optionally filtered by type"""
        if species_type:
            cursor = await self.connection.execute(
                'SELECT * FROM species WHERE species_type = ? ORDER BY tier, buy_price', 
                (species_type,)
            )
        else:
            cursor = await self.connection.execute(
                'SELECT * FROM species ORDER BY species_type, tier, buy_price'
            )
        
        rows = await cursor.fetchall()
        species_list = []
        
        for row in rows:
            species_list.append(Species(
                species_id=row[0],
                name=row[1],
                species_type=row[2],
                tier=row[3],
                buy_price=row[4],
                sell_price=row[5],
                growth_time=row[6],
                special_ability=row[7],
                emoji=row[8]
            ))
        
        return species_list
    
    async def add_species(self, species: Species):
        """Add new species to database"""
        await self.connection.execute('''
            INSERT OR REPLACE INTO species 
            (species_id, name, species_type, tier, buy_price, sell_price, 
             growth_time, special_ability, emoji)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            species.species_id, species.name, species.species_type, species.tier,
            species.buy_price, species.sell_price, species.growth_time,
            species.special_ability, species.emoji
        ))
        await self.connection.commit()
    
    # User facilities methods
    async def get_user_facilities(self, user_id: int) -> UserFacilities:
        """Get user facilities, create default if not exists"""
        cursor = await self.connection.execute(
            'SELECT * FROM user_facilities WHERE user_id = ?', (user_id,)
        )
        row = await cursor.fetchone()
        
        if row:
            return UserFacilities(
                user_id=row[0],
                pond_slots=row[1],
                barn_slots=row[2],
                pond_level=row[3],
                barn_level=row[4]
            )
        else:
            # Create default facilities
            facilities = UserFacilities(user_id=user_id)
            await self.connection.execute('''
                INSERT INTO user_facilities (user_id, pond_slots, barn_slots, pond_level, barn_level)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, facilities.pond_slots, facilities.barn_slots, 
                  facilities.pond_level, facilities.barn_level))
            await self.connection.commit()
            return facilities
    
    async def create_user_facilities(self, user_id: int):
        """Create default user facilities"""
        facilities = UserFacilities(user_id=user_id)
        await self.connection.execute('''
            INSERT INTO user_facilities (user_id, pond_slots, barn_slots, pond_level, barn_level)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, facilities.pond_slots, facilities.barn_slots, 
              facilities.pond_level, facilities.barn_level))
        await self.connection.commit()
        return facilities

    async def update_user_facilities(self, facilities: UserFacilities):
        """Update user facilities"""
        await self.connection.execute('''
            UPDATE user_facilities 
            SET pond_slots = ?, barn_slots = ?, pond_level = ?, barn_level = ?
            WHERE user_id = ?
        ''', (facilities.pond_slots, facilities.barn_slots, 
              facilities.pond_level, facilities.barn_level, facilities.user_id))
        await self.connection.commit()
    
    # User livestock methods
    async def add_livestock(self, user_id: int, species_id: str, facility_type: str, 
                           facility_slot: int, birth_time: datetime) -> int:
        """Add livestock to user facility, returns livestock_id"""
        cursor = await self.connection.execute('''
            INSERT INTO user_livestock 
            (user_id, species_id, facility_type, facility_slot, birth_time)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, species_id, facility_type, facility_slot, birth_time.isoformat()))
        await self.connection.commit()
        return cursor.lastrowid
    
    async def get_user_livestock(self, user_id: int, facility_type: str = None) -> List[UserLivestock]:
        """Get user livestock, optionally filtered by facility type"""
        if facility_type:
            cursor = await self.connection.execute(
                'SELECT * FROM user_livestock WHERE user_id = ? AND facility_type = ? ORDER BY facility_slot',
                (user_id, facility_type)
            )
        else:
            cursor = await self.connection.execute(
                'SELECT * FROM user_livestock WHERE user_id = ? ORDER BY facility_type, facility_slot',
                (user_id,)
            )
        
        rows = await cursor.fetchall()
        livestock_list = []
        
        for row in rows:
            livestock_list.append(UserLivestock(
                livestock_id=row[0],
                user_id=row[1],
                species_id=row[2],
                facility_type=row[3],
                facility_slot=row[4],
                birth_time=datetime.fromisoformat(row[5]),
                is_adult=bool(row[6]),
                last_product_time=datetime.fromisoformat(row[7]) if row[7] else None
            ))
        
        return livestock_list
    
    async def get_livestock_by_slot(self, user_id: int, facility_type: str, facility_slot: int) -> Optional[UserLivestock]:
        """Get livestock in specific slot"""
        cursor = await self.connection.execute(
            'SELECT * FROM user_livestock WHERE user_id = ? AND facility_type = ? AND facility_slot = ?',
            (user_id, facility_type, facility_slot)
        )
        row = await cursor.fetchone()
        
        if row:
            return UserLivestock(
                livestock_id=row[0],
                user_id=row[1],
                species_id=row[2],
                facility_type=row[3],
                facility_slot=row[4],
                birth_time=datetime.fromisoformat(row[5]),
                is_adult=bool(row[6]),
                last_product_time=datetime.fromisoformat(row[7]) if row[7] else None
            )
        return None
    
    async def update_livestock(self, livestock: UserLivestock):
        """Update livestock"""
        await self.connection.execute('''
            UPDATE user_livestock 
            SET is_adult = ?, last_product_time = ?
            WHERE livestock_id = ?
        ''', (livestock.is_adult, 
              livestock.last_product_time.isoformat() if livestock.last_product_time else None,
              livestock.livestock_id))
        await self.connection.commit()
    
    async def remove_livestock(self, livestock_id: int):
        """Remove livestock (for harvesting/selling)"""
        await self.connection.execute(
            'DELETE FROM user_livestock WHERE livestock_id = ?', (livestock_id,)
        )
        await self.connection.commit()
    
    async def get_empty_facility_slots(self, user_id: int, facility_type: str) -> List[int]:
        """Get list of empty slots in facility"""
        facilities = await self.get_user_facilities(user_id)
        max_slots = facilities.pond_slots if facility_type == 'pond' else facilities.barn_slots
        
        # Get occupied slots
        cursor = await self.connection.execute(
            'SELECT facility_slot FROM user_livestock WHERE user_id = ? AND facility_type = ?',
            (user_id, facility_type)
        )
        occupied_slots = [row[0] for row in await cursor.fetchall()]
        
        # Return empty slots
        return [slot for slot in range(max_slots) if slot not in occupied_slots]
    
    # Livestock products methods
    async def get_livestock_product(self, species_id: str) -> Optional[LivestockProduct]:
        """Get product info for species"""
        cursor = await self.connection.execute(
            'SELECT * FROM livestock_products WHERE species_id = ?', (species_id,)
        )
        row = await cursor.fetchone()
        
        if row:
            return LivestockProduct(
                species_id=row[0],
                product_name=row[1],
                product_emoji=row[2],
                production_time=row[3],
                sell_price=row[4]
            )
        return None
    
    async def add_livestock_product(self, product: LivestockProduct):
        """Add livestock product definition"""
        await self.connection.execute('''
            INSERT OR REPLACE INTO livestock_products 
            (species_id, product_name, product_emoji, production_time, sell_price)
            VALUES (?, ?, ?, ?, ?)
        ''', (product.species_id, product.product_name, product.product_emoji,
              product.production_time, product.sell_price))
        await self.connection.commit() 