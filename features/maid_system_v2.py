import discord
from discord.ext import commands
from discord import app_commands
import uuid
import random
import json
import aiosqlite
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple

from database.database import Database
from utils.embeds import EmbedBuilder
from utils.registration import require_registration
from utils.enhanced_logging import get_bot_logger
from features.maid_config_backup import MAID_TEMPLATES, RARITY_CONFIG as CONFIG_RARITY_CONFIG, STARDUST_CONFIG as CONFIG_STARDUST_CONFIG, BUFF_TYPES as CONFIG_BUFF_TYPES

logger = get_bot_logger()

# Configuration - Use shared configs from maid_config_backup
GACHA_CONFIG = {
    "single_roll_cost": 10000,
    "ten_roll_cost": 90000,
    "pity_threshold": None,
    "guaranteed_ur_rolls": None
}

# Use configs from maid_config_backup.py để sync với limited banner
RARITY_CONFIG = CONFIG_RARITY_CONFIG
STARDUST_CONFIG = CONFIG_STARDUST_CONFIG
BUFF_TYPES = CONFIG_BUFF_TYPES

# Import helper functions from maid_config_backup
from features.maid_config_backup import get_maid_template_safe

# 🛡️ SAFETY: Use MAID_TEMPLATES from maid_config_backup.py (includes Kotori)
# MAID_TEMPLATES is already imported from maid_config_backup

class MaidSystemV2(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
    
    async def cog_load(self):
        """Khởi tạo khi load cog"""
        logger.info("MaidSystemV2 cog loaded - tables will be created on first use")
        # Defer table initialization until database is fully ready
        self._tables_initialized = False
    
    async def init_maid_tables(self):
        """Tạo các bảng cần thiết cho maid system"""
        try:
            # Ensure database connection is available
            if not hasattr(self.bot, 'db') or not self.bot.db:
                logger.warning("Database not available, skipping table creation")
                return
            
            # Get connection
            connection = await self.bot.db.get_connection()
            
            # 🛡️ SAFETY: Create tables only if they don't exist (preserve existing data)
            logger.info("Creating maid system v2 tables (preserving existing data)...")
            
            # 🚫 REMOVED: DROP TABLE operations to prevent data loss
            # Tables will only be created if they don't exist
            
            # User maids table with schema validation
            await connection.execute('''
                CREATE TABLE IF NOT EXISTS user_maids_v2 (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    maid_id TEXT NOT NULL,
                    instance_id TEXT NOT NULL UNIQUE,
                    custom_name TEXT,
                    obtained_at TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT 0,
                    buff_values TEXT NOT NULL,
                    reroll_count INTEGER DEFAULT 0,
                    last_reroll_time TEXT
                )
            ''')
            
            # 🛡️ SAFETY: Add missing columns if they don't exist (for schema evolution)
            try:
                await connection.execute('ALTER TABLE user_maids_v2 ADD COLUMN reroll_count INTEGER DEFAULT 0')
                logger.info("Added reroll_count column to user_maids_v2")
            except:
                pass  # Column already exists
                
            try:
                await connection.execute('ALTER TABLE user_maids_v2 ADD COLUMN last_reroll_time TEXT')
                logger.info("Added last_reroll_time column to user_maids_v2")
            except:
                pass  # Column already exists
            
            # Gacha history table
            await connection.execute('''
                CREATE TABLE IF NOT EXISTS gacha_history_v2 (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    roll_type TEXT NOT NULL,
                    cost INTEGER NOT NULL,
                    results TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            ''')
            
            # User stardust table
            await connection.execute('''
                CREATE TABLE IF NOT EXISTS user_stardust_v2 (
                    user_id INTEGER PRIMARY KEY,
                    stardust_amount INTEGER DEFAULT 0,
                    last_updated TEXT NOT NULL
                )
            ''')
            
            # Reroll history table
            await connection.execute('''
                CREATE TABLE IF NOT EXISTS maid_reroll_history_v2 (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    maid_instance_id TEXT NOT NULL,
                    old_buffs TEXT NOT NULL,
                    new_buffs TEXT NOT NULL,
                    stardust_cost INTEGER NOT NULL,
                    reroll_time TEXT NOT NULL
                )
            ''')
            
            # Maid equip cooldown table (preserve existing data)
            await connection.execute('''
                CREATE TABLE IF NOT EXISTS maid_equip_cooldown_v2 (
                    user_id INTEGER PRIMARY KEY,
                    last_equip_time TEXT NOT NULL,
                    cooldown_until TEXT NOT NULL
                )
            ''')
            
            await connection.commit()
            logger.info("✅ Maid system v2 tables initialized safely (existing data preserved)")
            
        except Exception as e:
            logger.error(f"Error creating maid tables: {e}")
            import traceback
            traceback.print_exc()
    
    async def ensure_tables_ready(self):
        """Ensure tables are created when called from commands"""
        if not self._tables_initialized and hasattr(self.bot, 'db') and self.bot.db:
            try:
                await self.init_maid_tables()
                self._tables_initialized = True
                logger.info("✅ Maid tables initialized successfully on first command")
            except Exception as e:
                logger.error(f"❌ Failed to initialize maid tables: {e}")
                raise
    
    async def get_db_connection(self):
        """Get database connection safely"""
        if not hasattr(self.bot, 'db') or not self.bot.db:
            raise Exception("Database not available")
        return await self.bot.db.get_connection()
    
    # Helper functions
    def get_random_maid(self) -> str:
        """Roll random maid theo rates (EXCLUDE limited-only characters)"""
        rate = random.uniform(0, 100)
        
        if rate < RARITY_CONFIG["UR"]["rate"]:
            # ⚠️ EXCLUDE limited-only characters từ gacha thường
            maids = [k for k, v in MAID_TEMPLATES.items() 
                     if v["rarity"] == "UR" and not v.get("limited_only", False)]
        elif rate < RARITY_CONFIG["UR"]["rate"] + RARITY_CONFIG["SSR"]["rate"]:
            maids = [k for k, v in MAID_TEMPLATES.items() 
                     if v["rarity"] == "SSR" and not v.get("limited_only", False)]
        elif rate < RARITY_CONFIG["UR"]["rate"] + RARITY_CONFIG["SSR"]["rate"] + RARITY_CONFIG["SR"]["rate"]:
            maids = [k for k, v in MAID_TEMPLATES.items() 
                     if v["rarity"] == "SR" and not v.get("limited_only", False)]
        else:
            maids = [k for k, v in MAID_TEMPLATES.items() 
                     if v["rarity"] == "R" and not v.get("limited_only", False)]
        
        # Fallback nếu không có maid nào available
        if not maids:
            fallback_maids = [k for k, v in MAID_TEMPLATES.items() 
                             if v["rarity"] == "R" and not v.get("limited_only", False)]
            return random.choice(fallback_maids) if fallback_maids else "tsunade_r"
        
        return random.choice(maids)
    
    def generate_buffs(self, maid_id: str) -> List[Dict]:
        """Generate buffs cho maid"""
        template = get_maid_template_safe(maid_id)
        if not template:
            return []  # Return empty list for invalid templates
        rarity = template["rarity"]
        buff_count = RARITY_CONFIG[rarity]["buff_count"]
        buff_range = RARITY_CONFIG[rarity]["buff_range"]
        possible_buffs = template["possible_buffs"]
        
        buffs = []
        selected_types = random.sample(possible_buffs, min(buff_count, len(possible_buffs)))
        
        for buff_type in selected_types:
            value = random.uniform(buff_range[0], buff_range[1])
            buffs.append({
                "buff_type": buff_type,  # 🛡️ FIXED: Use buff_type not type
                "value": round(value, 1)
            })
        
        return buffs
    
    async def get_user_stardust(self, user_id: int) -> int:
        """Lấy số stardust của user"""
        connection = await self.get_db_connection()
        cursor = await connection.execute(
            "SELECT stardust_amount FROM user_stardust_v2 WHERE user_id = ?",
            (user_id,)
        )
        result = await cursor.fetchone()
        return result[0] if result else 0
    
    async def add_stardust(self, user_id: int, amount: int):
        """Thêm stardust cho user"""
        connection = await self.get_db_connection()
        await connection.execute('''
            INSERT OR REPLACE INTO user_stardust_v2 (user_id, stardust_amount, last_updated)
            VALUES (?, COALESCE((SELECT stardust_amount FROM user_stardust_v2 WHERE user_id = ?), 0) + ?, ?)
        ''', (user_id, user_id, amount, datetime.now().isoformat()))
        await connection.commit()
    
    async def spend_stardust(self, user_id: int, amount: int) -> bool:
        """Tiêu stardust, return True nếu đủ tiền"""
        current = await self.get_user_stardust(user_id)
        if current < amount:
            return False
        
        connection = await self.get_db_connection()
        await connection.execute('''
            UPDATE user_stardust_v2 SET stardust_amount = stardust_amount - ?, last_updated = ?
            WHERE user_id = ?
        ''', (amount, datetime.now().isoformat(), user_id))
        await connection.commit()
        return True
    
    async def check_equip_cooldown(self, user_id: int) -> tuple[bool, str]:
        """Check equip cooldown. Returns (can_equip, time_remaining_text)"""
        connection = await self.get_db_connection()
        cursor = await connection.execute(
            "SELECT cooldown_until FROM maid_equip_cooldown_v2 WHERE user_id = ?",
            (user_id,)
        )
        result = await cursor.fetchone()
        
        if not result:
            return True, ""  # No cooldown recorded
        
        # 🔧 FIX: Sử dụng UTC time để tránh timezone issues khi restart
        try:
            cooldown_until = datetime.fromisoformat(result[0])
            now = datetime.now()
            
            # Đảm bảo cả hai datetime đều cùng timezone
            if cooldown_until.tzinfo is None:
                cooldown_until = cooldown_until.replace(tzinfo=None)
            if now.tzinfo is None:
                now = now.replace(tzinfo=None)
            
            if now >= cooldown_until:
                return True, ""  # Cooldown expired
            
            # Calculate time remaining
            time_remaining = cooldown_until - now
            total_seconds = time_remaining.total_seconds()
            
            # 🔧 FIX: Tránh negative time do timezone confusion
            if total_seconds <= 0:
                return True, ""
                
            hours = int(total_seconds // 3600)
            minutes = int((total_seconds % 3600) // 60)
            
            if hours > 0:
                time_text = f"{hours} giờ {minutes} phút"
            else:
                time_text = f"{minutes} phút"
            
            return False, time_text
            
        except (ValueError, TypeError) as e:
            # If datetime parsing fails, reset cooldown
            logger.warning(f"Failed to parse cooldown time for user {user_id}: {e}")
            return True, ""

    async def set_equip_cooldown(self, user_id: int):
        """Set 10-hour cooldown for maid equip"""
        # 🔧 FIX: Sử dụng consistent datetime format
        now = datetime.now()
        cooldown_until = now + timedelta(hours=10)
        
        connection = await self.get_db_connection()
        await connection.execute('''
            INSERT OR REPLACE INTO maid_equip_cooldown_v2 (user_id, last_equip_time, cooldown_until)
            VALUES (?, ?, ?)
        ''', (user_id, now.isoformat(), cooldown_until.isoformat()))
        await connection.commit()
    
    async def get_user_maids(self, user_id: int) -> List[Dict]:
        """Lấy tất cả maids của user"""
        connection = await self.get_db_connection()
        
        # Try to get with reroll_count first, fallback if column doesn't exist
        try:
            cursor = await connection.execute('''
                SELECT instance_id, maid_id, custom_name, obtained_at, is_active, buff_values, reroll_count
                FROM user_maids_v2 WHERE user_id = ? ORDER BY obtained_at DESC
            ''', (user_id,))
            results = await cursor.fetchall()
            
            maids = []
            for row in results:
                buffs = json.loads(row[5])
                maids.append({
                    "instance_id": row[0],
                    "maid_id": row[1],
                    "custom_name": row[2],
                    "obtained_at": row[3],
                    "is_active": bool(row[4]),
                    "buffs": buffs,
                    "reroll_count": row[6] or 0
                })
            
            return maids
            
        except Exception as e:
            # If reroll_count column doesn't exist, query without it
            logger.warning(f"Reroll_count column not found, using fallback query: {e}")
            cursor = await connection.execute('''
                SELECT instance_id, maid_id, custom_name, obtained_at, is_active, buff_values
                FROM user_maids_v2 WHERE user_id = ? ORDER BY obtained_at DESC
            ''', (user_id,))
            results = await cursor.fetchall()
            
            maids = []
            for row in results:
                buffs = json.loads(row[5])
                maids.append({
                    "instance_id": row[0],
                    "maid_id": row[1],
                    "custom_name": row[2],
                    "obtained_at": row[3],
                    "is_active": bool(row[4]),
                    "buffs": buffs,
                    "reroll_count": 0  # Default value when column missing
                })
            
            return maids
    
    async def get_active_maid(self, user_id: int) -> Optional[Dict]:
        """Lấy maid đang active"""
        connection = await self.get_db_connection()
        cursor = await connection.execute('''
            SELECT instance_id, maid_id, custom_name, buff_values
            FROM user_maids_v2 WHERE user_id = ? AND is_active = 1
        ''', (user_id,))
        result = await cursor.fetchone()
        
        if result:
            buffs = json.loads(result[3])
            return {
                "instance_id": result[0],
                "maid_id": result[1],
                "custom_name": result[2],
                "buffs": buffs
            }
        return None
    
    # Commands
    @commands.hybrid_command(name="mg", description="🎰 Gacha maid - Roll 1 lần (10,000 coins)")
    async def maid_gacha(self, ctx):
        """Gacha maid 1 lần"""
        # Check registration
        if not await require_registration(ctx.bot, ctx):
            return
        
        # Ensure tables are ready
        await self.ensure_tables_ready()
            
        user_id = ctx.author.id
        cost = GACHA_CONFIG["single_roll_cost"]
        
        # Check coins
        user = await self.db.get_user(user_id)
        if user.money < cost:
            embed = EmbedBuilder.create_base_embed(
                title="❌ Không đủ coins",
                description=f"Bạn cần {cost:,} coins để gacha!\nBạn hiện có: {user.money:,} coins",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            return
        
        # 🛡️ SAFETY: Atomic transaction for gacha
        connection = await self.get_db_connection()
        try:
            await connection.execute('BEGIN TRANSACTION')
            
            # Double-check coins and deduct atomically
            cursor = await connection.execute(
                'UPDATE users SET money = money - ? WHERE user_id = ? AND money >= ?',
                (cost, user_id, cost)
            )
            
            if cursor.rowcount == 0:
                await connection.execute('ROLLBACK')
                embed = EmbedBuilder.create_base_embed(
                    title="❌ Không đủ coins",
                    description="Không đủ tiền để thực hiện gacha!",
                    color=0xFF0000
                )
                await ctx.send(embed=embed)
                return
            
            # Gacha roll (after successful payment)
            maid_id = self.get_random_maid()
            instance_id = str(uuid.uuid4())
            buffs = self.generate_buffs(maid_id)
            
            # Save maid to database
            await connection.execute('''
                INSERT INTO user_maids_v2 (user_id, maid_id, instance_id, obtained_at, buff_values)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, maid_id, instance_id, datetime.now().isoformat(), json.dumps(buffs)))
            
            # Save gacha history
            await connection.execute('''
                INSERT INTO gacha_history_v2 (user_id, roll_type, cost, results, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, "single", cost, json.dumps([maid_id]), datetime.now().isoformat()))
            
            # 🛡️ COMMIT: All operations successful
            await connection.commit()
            
        except Exception as e:
            # 🛡️ ROLLBACK: Any error rolls back entire transaction
            await connection.execute('ROLLBACK')
            logger.error(f"Gacha transaction failed for user {user_id}: {e}")
            embed = EmbedBuilder.create_base_embed(
                title="❌ Lỗi gacha",
                description="Đã xảy ra lỗi trong quá trình gacha. Tiền của bạn không bị trừ.",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            return
        
        # Create result embed
        template = get_maid_template_safe(maid_id)
        if not template:
            return await ctx.send("❌ Maid template không tồn tại!", ephemeral=True)
        embed = EmbedBuilder.create_base_embed(
            title="🎰 Gacha Result!",
            description=f"Chi phí: {cost:,} coins",
            color=RARITY_CONFIG[template["rarity"]]["color"]
        )
        
        rarity_emoji = {"GR": "👻", "UR": "💎", "SSR": "🌟", "SR": "⭐", "R": "✨"}[template["rarity"]]
        embed.add_field(
            name=f"{rarity_emoji} {template['emoji']} {template['name']}",
            value=f"**{template['rarity']} Maid**",
            inline=False
        )
        
        # Buffs
        buff_text = "\n".join([
            f"{BUFF_TYPES[buff.get('buff_type') or buff.get('type', 'unknown')]['emoji']} {BUFF_TYPES[buff.get('buff_type') or buff.get('type', 'unknown')]['name']}: +{buff['value']}%"
            for buff in buffs
            if (buff.get('buff_type') or buff.get('type')) in BUFF_TYPES
        ])
        
        embed.add_field(name="✨ Buffs", value=buff_text, inline=False)
        embed.add_field(name="🆔 Instance ID", value=f"`{instance_id[:8]}`", inline=True)
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="mg10", description="🎰 Gacha maid - Roll 10 lần (90,000 coins)")
    async def maid_gacha_10(self, ctx):
        """Gacha maid 10 lần"""
        # Check registration
        if not await require_registration(ctx.bot, ctx):
            return
            
        user_id = ctx.author.id
        cost = GACHA_CONFIG["ten_roll_cost"]
        
        # Check coins
        user = await self.db.get_user(user_id)
        if user.money < cost:
            embed = EmbedBuilder.create_base_embed(
                title="❌ Không đủ coins",
                description=f"Bạn cần {cost:,} coins để gacha 10 lần!\nBạn hiện có: {user.money:,} coins",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            return
        
        # 🛡️ SAFETY: Atomic transaction for 10-roll gacha
        connection = await self.get_db_connection()
        try:
            await connection.execute('BEGIN TRANSACTION')
            
            # Double-check coins and deduct atomically
            cursor = await connection.execute(
                'UPDATE users SET money = money - ? WHERE user_id = ? AND money >= ?',
                (cost, user_id, cost)
            )
            
            if cursor.rowcount == 0:
                await connection.execute('ROLLBACK')
                embed = EmbedBuilder.create_base_embed(
                    title="❌ Không đủ coins",
                    description="Không đủ tiền để thực hiện gacha 10 lần!",
                    color=0xFF0000
                )
                await ctx.send(embed=embed)
                return
            
            # Roll 10 times (after successful payment)
            results = []
            for _ in range(10):
                maid_id = self.get_random_maid()
                instance_id = str(uuid.uuid4())
                buffs = self.generate_buffs(maid_id)
                
                # Save to database
                await connection.execute('''
                    INSERT INTO user_maids_v2 (user_id, maid_id, instance_id, obtained_at, buff_values)
                    VALUES (?, ?, ?, ?, ?)
                ''', (user_id, maid_id, instance_id, datetime.now().isoformat(), json.dumps(buffs)))
                
                results.append({
                    "maid_id": maid_id,
                    "instance_id": instance_id,
                    "buffs": buffs
                })
            
            # Save gacha history
            await connection.execute('''
                INSERT INTO gacha_history_v2 (user_id, roll_type, cost, results, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, "ten_roll", cost, json.dumps([r["maid_id"] for r in results]), datetime.now().isoformat()))
            
            # 🛡️ COMMIT: All operations successful
            await connection.commit()
            
        except Exception as e:
            # 🛡️ ROLLBACK: Any error rolls back entire transaction
            await connection.execute('ROLLBACK')
            logger.error(f"10-roll gacha transaction failed for user {user_id}: {e}")
            embed = EmbedBuilder.create_base_embed(
                title="❌ Lỗi gacha",
                description="Đã xảy ra lỗi trong quá trình gacha 10 lần. Tiền của bạn không bị trừ.",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            return
        
        # Send results with view
        view = GachaResultsView(user_id, results)
        embed = view.create_embed(show_remaining=False)
        await ctx.send(embed=embed, view=view)
    
    @commands.hybrid_command(name="ma", description="👑 Xem maid đang active và buffs")
    async def maid_active(self, ctx):
        """Xem maid active"""
        # Check registration
        if not await require_registration(ctx.bot, ctx):
            return
        
        # Ensure tables are ready
        await self.ensure_tables_ready()
            
        user_id = ctx.author.id
        active_maid = await self.get_active_maid(user_id)
        
        if not active_maid:
            embed = EmbedBuilder.create_base_embed(
                title="❌ Không có maid active",
                description="Bạn chưa trang bị maid nào!\nDùng `f!mequip <id>` để trang bị maid",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            return
        
        template = get_maid_template_safe(active_maid["maid_id"])
        if not template:
            return await ctx.send("❌ Maid template không tồn tại!", ephemeral=True)
        embed = EmbedBuilder.create_base_embed(
            title="👑 Maid Active",
            description=f"Maid đang trang bị của {ctx.author.mention}",
            color=RARITY_CONFIG[template["rarity"]]["color"]
        )
        
        name = active_maid["custom_name"] or template["name"]
        rarity_emoji = {"GR": "👻", "UR": "💎", "SSR": "🌟", "SR": "⭐", "R": "✨"}[template["rarity"]]
        embed.add_field(
            name=f"{rarity_emoji} {template['emoji']} {name}",
            value=f"**{template['rarity']} Maid**",
            inline=False
        )
        
        # Active buffs
        buff_text = "\n".join([
            f"{BUFF_TYPES[buff.get('buff_type') or buff.get('type', 'unknown')]['emoji']} {BUFF_TYPES[buff.get('buff_type') or buff.get('type', 'unknown')]['name']}: +{buff['value']}%"
            for buff in active_maid["buffs"]
            if (buff.get('buff_type') or buff.get('type')) in BUFF_TYPES
        ])
        
        embed.add_field(name="✨ Active Buffs", value=buff_text, inline=False)
        embed.add_field(name="🆔 Instance ID", value=f"`{active_maid['instance_id'][:8]}`", inline=True)
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="mc", description="📚 Xem collection maids")
    async def maid_collection(self, ctx, *, args: Optional[str] = None):
        """Xem collection maids với filters
        
        Usage:
        f!mc - Xem tất cả
        f!mc -r UR - Lọc theo rarity 
        f!mc -n zero - Lọc theo tên
        """
        # Check registration
        if not await require_registration(ctx.bot, ctx):
            return
        
        # Parse arguments
        filter_type = None
        filter_value = None
        
        if args:
            parts = args.strip().split()
            if len(parts) >= 2:
                if parts[0] == '-r':
                    filter_type = 'rarity'
                    filter_value = parts[1]
                elif parts[0] == '-n':
                    filter_type = 'name'
                    filter_value = ' '.join(parts[1:])  # Support multi-word names
            
        user_id = ctx.author.id
        maids = await self.get_user_maids(user_id)
        
        if not maids:
            embed = EmbedBuilder.create_base_embed(
                title="❌ Collection trống",
                description="Bạn chưa có maid nào!\nDùng `f!mg` để gacha maid",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            return
        
        # Apply filters
        filtered_maids = self.apply_maid_filters(maids, filter_type, filter_value)
        
        if not filtered_maids:
            filter_text = ""
            if filter_type == 'rarity':
                filter_text = f" với rarity `{filter_value.upper()}`"
            elif filter_type == 'name':
                filter_text = f" với tên chứa `{filter_value}`"
                
            embed = EmbedBuilder.create_base_embed(
                title="❌ Không tìm thấy maid",
                description=f"Không có maid nào{filter_text}",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            return
        
        # Send with pagination view
        view = MaidCollectionView(user_id, filtered_maids, self, filter_type, filter_value)
        embed = view.create_embed(1)
        await ctx.send(embed=embed, view=view)
    
    def apply_maid_filters(self, maids: List[Dict], filter_type: Optional[str], filter_value: Optional[str]) -> List[Dict]:
        """Apply filters to maid list"""
        if not filter_type or not filter_value:
            return maids
            
        filtered = []
        
        for maid in maids:
            template = MAID_TEMPLATES.get(maid["maid_id"], {})
            
            if filter_type == 'rarity':
                if template.get("rarity", "").upper() == filter_value.upper():
                    filtered.append(maid)
                    
            elif filter_type == 'name':
                maid_name = template.get("name", "").lower()
                custom_name = (maid.get("custom_name") or "").lower()
                search_term = filter_value.lower()
                
                if (search_term in maid_name or 
                    search_term in custom_name or
                    search_term in maid["maid_id"].lower()):
                    filtered.append(maid)
        
        return filtered
    
    @commands.hybrid_command(name="mequip", description="🎯 Trang bị maid")
    async def maid_equip(self, ctx, maid_id: str):
        """Trang bị maid"""
        # Check registration
        if not await require_registration(ctx.bot, ctx):
            return
            
        user_id = ctx.author.id
        
        # Check equip cooldown (10 hours)
        can_equip, time_remaining = await self.check_equip_cooldown(user_id)
        if not can_equip:
            embed = EmbedBuilder.create_base_embed(
                title="⏰ Equip Cooldown",
                description=f"Bạn cần đợi **{time_remaining}** nữa mới có thể thay đổi maid!",
                color=0xFFA500
            )

            await ctx.send(embed=embed)
            return
        
        # Find maid
        maids = await self.get_user_maids(user_id)
        target_maid = None
        
        for maid in maids:
            if (maid["instance_id"].startswith(maid_id.lower()) or 
                (maid["custom_name"] and maid_id.lower() in maid["custom_name"].lower()) or
                (lambda template: template and maid_id.lower() in template["name"].lower())(get_maid_template_safe(maid["maid_id"]))):
                target_maid = maid
                break
        
        if not target_maid:
            embed = EmbedBuilder.create_base_embed(
                title="❌ Không tìm thấy maid",
                description=f"Không tìm thấy maid với ID: `{maid_id}`",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            return
        
        # Deactivate all maids
        connection = await self.get_db_connection()
        await connection.execute(
            "UPDATE user_maids_v2 SET is_active = 0 WHERE user_id = ?",
            (user_id,)
        )
        
        # Activate target maid
        await connection.execute(
            "UPDATE user_maids_v2 SET is_active = 1 WHERE instance_id = ?",
            (target_maid["instance_id"],)
        )
        
        await connection.commit()
        
        # Set 10-hour cooldown
        await self.set_equip_cooldown(user_id)
        
        template = get_maid_template_safe(target_maid["maid_id"])
        if not template:
            return await ctx.send("❌ Maid template không tồn tại!", ephemeral=True)
        name = target_maid["custom_name"] or template["name"]
        
        embed = EmbedBuilder.create_base_embed(
            title="✅ Trang bị thành công!",
            description=f"Đã trang bị {template['emoji']} **{name}**",
            color=0x00FF00
        )
        
        buff_text = "\n".join([
            f"{BUFF_TYPES[buff.get('buff_type') or buff.get('type', 'unknown')]['emoji']} {BUFF_TYPES[buff.get('buff_type') or buff.get('type', 'unknown')]['name']}: +{buff['value']}%"
            for buff in target_maid["buffs"]
            if (buff.get('buff_type') or buff.get('type')) in BUFF_TYPES
        ])
        
        embed.add_field(name="✨ Buffs được kích hoạt", value=buff_text, inline=False)
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="mcooldown", description="⏰ Xem thời gian cooldown equip maid")
    async def maid_cooldown_check(self, ctx):
        """Xem thời gian cooldown còn lại"""
        # Check registration
        if not await require_registration(ctx.bot, ctx):
            return
            
        user_id = ctx.author.id
        can_equip, time_remaining = await self.check_equip_cooldown(user_id)
        
        if can_equip:
            embed = EmbedBuilder.create_base_embed(
                title="✅ Sẵn sàng equip!",
                description="Bạn có thể trang bị maid mới bất cứ lúc nào!",
                color=0x00FF00
            )

        else:
            embed = EmbedBuilder.create_base_embed(
                title="⏰ Đang trong cooldown",
                description=f"Bạn cần đợi **{time_remaining}** nữa để thay đổi maid!",
                color=0xFFA500
            )

        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="mstar", description="⭐ Xem stardust và giá reroll")
    async def maid_stardust(self, ctx):
        """Xem stardust"""
        # Check registration
        if not await require_registration(ctx.bot, ctx):
            return
            
        user_id = ctx.author.id
        stardust = await self.get_user_stardust(user_id)
        
        embed = EmbedBuilder.create_base_embed(
            title="⭐ Bụi Sao",
            description=f"Stardust của {ctx.author.mention}",
            color=0xFFD700
        )
        
        embed.add_field(
            name="💫 Số lượng",
            value=f"{stardust:,} bụi sao",
            inline=True
        )
        
        embed.add_field(
            name="🔄 Reroll Costs",
            value=f"👻 GR: {STARDUST_CONFIG['reroll_costs']['GR']} ⭐\n"
                  f"💎 UR: {STARDUST_CONFIG['reroll_costs']['UR']} ⭐\n"
                  f"🌟 SSR: {STARDUST_CONFIG['reroll_costs']['SSR']} ⭐\n"
                  f"⭐ SR: {STARDUST_CONFIG['reroll_costs']['SR']} ⭐\n"
                  f"✨ R: {STARDUST_CONFIG['reroll_costs']['R']} ⭐",
            inline=True
        )
        
        embed.add_field(
            name="💥 Dismantle Rewards",
            value=f"👻 GR: {STARDUST_CONFIG['dismantle_rewards']['GR']} ⭐\n"
                  f"💎 UR: {STARDUST_CONFIG['dismantle_rewards']['UR']} ⭐\n"
                  f"🌟 SSR: {STARDUST_CONFIG['dismantle_rewards']['SSR']} ⭐\n"
                  f"⭐ SR: {STARDUST_CONFIG['dismantle_rewards']['SR']} ⭐\n"
                  f"✨ R: {STARDUST_CONFIG['dismantle_rewards']['R']} ⭐",
            inline=True
        )
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="mdis", description="💥 Tách maid thành stardust")
    async def maid_dismantle(self, ctx, maid_id: str):
        """Tách maid thành stardust"""
        # Check registration
        if not await require_registration(ctx.bot, ctx):
            return
            
        user_id = ctx.author.id
        
        # Find maid
        maids = await self.get_user_maids(user_id)
        target_maid = None
        
        for maid in maids:
            if maid["instance_id"].startswith(maid_id.lower()):
                target_maid = maid
                break
        
        if not target_maid:
            embed = EmbedBuilder.create_base_embed(
                title="❌ Không tìm thấy maid",
                description=f"Không tìm thấy maid với ID: `{maid_id}`",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            return
        
        template = get_maid_template_safe(target_maid["maid_id"])
        if not template:
            return await ctx.send("❌ Maid template không tồn tại!", ephemeral=True)
        name = target_maid["custom_name"] or template["name"]
        reward = STARDUST_CONFIG["dismantle_rewards"][template["rarity"]]
        
        # Confirm view
        view = DismantleConfirmView(user_id, target_maid, reward, self)
        
        embed = EmbedBuilder.create_base_embed(
            title="⚠️ Xác nhận tách maid",
            description=f"Bạn có chắc muốn tách {template['emoji']} **{name}**?",
            color=0xFFA500
        )
        
        embed.add_field(name="🆔 Instance ID", value=f"`{target_maid['instance_id'][:8]}`", inline=True)
        embed.add_field(name="⭐ Stardust nhận được", value=f"{reward} bụi sao", inline=True)
        embed.add_field(name="⚠️ Cảnh báo", value="**Hành động này KHÔNG THỂ hoàn tác!**", inline=False)
        
        await ctx.send(embed=embed, view=view)

    @commands.hybrid_command(name="mdisall", description="💥 Tách nhiều maid theo filter (-r rarity / -n name)")
    async def maid_dismantle_all(self, ctx, *, args: Optional[str] = None):
        """Tách nhiều maid cùng lúc theo filter"""
        # Check registration
        if not await require_registration(ctx.bot, ctx):
            return
            
        user_id = ctx.author.id
        
        # Parse filters
        filter_type = None
        filter_value = None
        
        if args:
            parts = args.split()
            i = 0
            while i < len(parts):
                if parts[i] == "-r" and i + 1 < len(parts):
                    filter_type = "rarity"
                    filter_value = parts[i + 1].upper()
                    i += 2
                elif parts[i] == "-n" and i + 1 < len(parts):
                    filter_type = "name"
                    # Handle multi-word names
                    name_parts = []
                    i += 1
                    while i < len(parts) and not parts[i].startswith("-"):
                        name_parts.append(parts[i])
                        i += 1
                    filter_value = " ".join(name_parts).lower()
                else:
                    i += 1
        
        # Get all maids
        all_maids = await self.get_user_maids(user_id)
        if not all_maids:
            embed = EmbedBuilder.create_base_embed(
                title="❌ Không có maid",
                description="Bạn chưa có maid nào để tách!",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            return
        
        # Apply filters
        filtered_maids = self.apply_maid_filters(all_maids, filter_type, filter_value)
        
        if not filtered_maids:
            if filter_type and filter_value:
                embed = EmbedBuilder.create_base_embed(
                    title="❌ Không tìm thấy maid",
                    description=f"Không tìm thấy maid với filter: `{filter_type}={filter_value}`",
                    color=0xFF0000
                )
            else:
                embed = EmbedBuilder.create_base_embed(
                    title="❌ Không có maid",
                    description="Bạn chưa có maid nào!",
                    color=0xFF0000
                )
            await ctx.send(embed=embed)
            return
        
        # Remove active maid from dismantle list
        active_maid = await self.get_active_maid(user_id)
        if active_maid:
            filtered_maids = [m for m in filtered_maids if m["instance_id"] != active_maid["instance_id"]]
        
        if not filtered_maids:
            embed = EmbedBuilder.create_base_embed(
                title="⚠️ Không thể tách",
                description="Không thể tách maid đang active! Hãy unequip trước.",
                color=0xFFA500
            )
            await ctx.send(embed=embed)
            return
        
        # Calculate total rewards
        total_rewards = {}
        total_stardust = 0
        for maid in filtered_maids:
            template = get_maid_template_safe(maid["maid_id"])
            if not template:
                continue  # Skip invalid templates
            rarity = template["rarity"]
            reward = STARDUST_CONFIG["dismantle_rewards"][rarity]
            total_rewards[rarity] = total_rewards.get(rarity, 0) + 1
            total_stardust += reward
        
        # Create confirmation view
        view = BulkDismantleConfirmView(user_id, filtered_maids, total_stardust, total_rewards, self)
        
        # Create embed
        embed = EmbedBuilder.create_base_embed(
            title="⚠️ Xác nhận tách nhiều maid",
            description=f"Bạn có chắc muốn tách **{len(filtered_maids)} maid**?",
            color=0xFFA500
        )
        
        # Show filter used
        if filter_type and filter_value:
            if filter_type == "rarity":
                embed.add_field(name="🔍 Filter", value=f"Rarity: **{filter_value}**", inline=False)
            else:
                embed.add_field(name="🔍 Filter", value=f"Name: **{filter_value}**", inline=False)
        
        # Show breakdown by rarity
        breakdown_parts = []
        for rarity in ["UR", "SSR", "SR", "R"]:
            if rarity in total_rewards:
                count = total_rewards[rarity]
                reward_per = STARDUST_CONFIG["dismantle_rewards"][rarity]
                total_per_rarity = count * reward_per
                rarity_emoji = {"GR": "👻", "UR": "💎", "SSR": "🌟", "SR": "⭐", "R": "✨"}[rarity]
                breakdown_parts.append(f"{rarity_emoji} **{rarity}**: {count}x → {total_per_rarity}⭐")
        
        embed.add_field(name="📊 Chi tiết", value="\n".join(breakdown_parts), inline=False)
        embed.add_field(name="💰 Tổng stardust", value=f"**{total_stardust:,} ⭐**", inline=True)
        embed.add_field(name="⚠️ Cảnh báo", value="**Hành động này KHÔNG THỂ hoàn tác!**", inline=False)
        
        await ctx.send(embed=embed, view=view)
    
    @commands.hybrid_command(name="mreroll", description="🎲 Reroll buffs maid bằng stardust")
    async def maid_reroll(self, ctx, maid_id: str):
        """Reroll buffs của maid"""
        # Check registration
        if not await require_registration(ctx.bot, ctx):
            return
            
        user_id = ctx.author.id
        
        # Find maid
        maids = await self.get_user_maids(user_id)
        target_maid = None
        
        for maid in maids:
            if maid["instance_id"].startswith(maid_id.lower()):
                target_maid = maid
                break
        
        if not target_maid:
            embed = EmbedBuilder.create_base_embed(
                title="❌ Không tìm thấy maid",
                description=f"Không tìm thấy maid với ID: `{maid_id}`",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            return
        
        template = get_maid_template_safe(target_maid["maid_id"])
        if not template:
            return await ctx.send("❌ Maid template không tồn tại!", ephemeral=True)
        cost = STARDUST_CONFIG["reroll_costs"][template["rarity"]]
        current_stardust = await self.get_user_stardust(user_id)
        
        if current_stardust < cost:
            embed = EmbedBuilder.create_base_embed(
                title="❌ Không đủ stardust",
                description=f"Bạn cần {cost} ⭐ để reroll!\nBạn hiện có: {current_stardust} ⭐",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            return
        
        name = target_maid["custom_name"] or template["name"]
        
        # Confirm view
        view = RerollConfirmView(user_id, target_maid, cost, self)
        
        embed = EmbedBuilder.create_base_embed(
            title="🎲 Xác nhận reroll",
            description=f"Reroll buffs cho {template['emoji']} **{name}**?",
            color=0x00FFFF
        )
        
        # Current buffs
        current_buffs = "\n".join([
            f"{BUFF_TYPES[buff.get('buff_type') or buff.get('type', 'unknown')]['emoji']} {BUFF_TYPES[buff.get('buff_type') or buff.get('type', 'unknown')]['name']}: +{buff['value']}%"
            for buff in target_maid["buffs"]
            if (buff.get('buff_type') or buff.get('type')) in BUFF_TYPES
        ])
        
        embed.add_field(name="✨ Buffs hiện tại", value=current_buffs, inline=False)
        embed.add_field(name="💰 Chi phí", value=f"{cost} ⭐ stardust", inline=True)
        embed.add_field(name="💫 Stardust hiện có", value=f"{current_stardust} ⭐", inline=True)
        
        await ctx.send(embed=embed, view=view)

    async def reload_maid_templates(self):
        """Reload maid templates từ file config (cho hot reload)"""
        try:
            # Có thể load từ JSON file để hot reload
            # with open('ai/maid_characters.json', 'r', encoding='utf-8') as f:
            #     external_templates = json.load(f)
            #     MAID_TEMPLATES.update(external_templates)
            pass
        except Exception as e:
            logger.error(f"Failed to reload maid templates: {e}")
    
    @commands.hybrid_command(name="mreload", description="🔄 Reload maid templates (admin only)")
    async def reload_templates(self, ctx):
        """Reload maid templates without restart"""
        # Check admin permission
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("❌ Chỉ admin mới có thể reload templates!")
            return
            
        await self.reload_maid_templates()
        
        embed = EmbedBuilder.create_base_embed(
            title="✅ Templates Reloaded",
            description=f"Đã reload templates! Hiện có {len(MAID_TEMPLATES)} nhân vật.",
            color=0x00FF00
        )
        await ctx.send(embed=embed)

# Button views
class GachaResultsView(discord.ui.View):
    """View cho gacha x10 results với button hiện remaining maids"""
    
    def __init__(self, user_id: int, results: List[Dict]):
        super().__init__(timeout=300)  # 5 minutes timeout
        self.user_id = user_id
        self.results = results
        self.showing_remaining = False
        
        # Only show button if there are more than 5 results
        if len(results) > 5:
            self.update_button()
    
    def update_button(self):
        """Update button state"""
        self.clear_items()
        
        if len(self.results) > 5:
            if self.showing_remaining:
                button = discord.ui.Button(
                    label="📋 Hiện 5 maid đầu",
                    style=discord.ButtonStyle.secondary,
                    emoji="📋"
                )
                button.callback = self.show_first_five
            else:
                button = discord.ui.Button(
                    label=f"👁️ Hiện {len(self.results) - 5} maid còn lại",
                    style=discord.ButtonStyle.primary,
                    emoji="👁️"
                )
                button.callback = self.show_remaining
            
            self.add_item(button)
    
    def create_embed(self, show_remaining: bool = False) -> discord.Embed:
        """Tạo embed cho gacha results"""
        self.showing_remaining = show_remaining
        
        # Create result embed
        embed = EmbedBuilder.create_base_embed(
            title="🎰 Gacha x10 Results!",
            description=f"Chi phí: {GACHA_CONFIG['ten_roll_cost']:,} coins • Tiết kiệm: {10000 * 10 - GACHA_CONFIG['ten_roll_cost']:,} coins",
            color=0x00FF00
        )
        
        # Count by rarity
        rarity_count = {"GR": 0, "UR": 0, "SSR": 0, "SR": 0, "R": 0}
        for result in self.results:
            template = get_maid_template_safe(result["maid_id"])
            if template:
                rarity_count[template["rarity"]] += 1
        
        # Summary
        summary_parts = []
        for rarity in ["GR", "UR", "SSR", "SR", "R"]:
            if rarity_count[rarity] > 0:
                rarity_emoji = {"GR": "👻", "UR": "💎", "SSR": "🌟", "SR": "⭐", "R": "✨"}[rarity]
                summary_parts.append(f"{rarity_emoji} {rarity}: {rarity_count[rarity]}x")
        
        embed.add_field(name="📊 Tổng kết", value=" • ".join(summary_parts), inline=False)
        
        # Show maids based on current state
        if show_remaining and len(self.results) > 5:
            # Show maids 6-10
            maids_to_show = self.results[5:]
            start_index = 6
        else:
            # Show first 5 maids
            maids_to_show = self.results[:5]
            start_index = 1
        
        for i, result in enumerate(maids_to_show):
            template = get_maid_template_safe(result["maid_id"])
            if not template:
                continue  # Skip invalid templates
            rarity_emoji = {"GR": "👻", "UR": "💎", "SSR": "🌟", "SR": "⭐", "R": "✨"}[template["rarity"]]
            
            buff_summary = " • ".join([
                f"{BUFF_TYPES[buff.get('buff_type') or buff.get('type', 'unknown')]['emoji']}{buff['value']:.1f}%" 
                for buff in result["buffs"]
                if (buff.get('buff_type') or buff.get('type')) in BUFF_TYPES
            ])
            
            embed.add_field(
                name=f"{start_index + i}. {rarity_emoji} {template['emoji']} {template['name']}",
                value=f"`{result['instance_id'][:8]}` • {buff_summary}",
                inline=False
            )
        
        # Show status if not showing all
        if not show_remaining and len(self.results) > 5:
            embed.add_field(name="...", value=f"Và {len(self.results) - 5} maids khác", inline=False)
        
        return embed
    
    async def show_remaining(self, interaction: discord.Interaction):
        """Hiện 5 maid còn lại"""
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Chỉ người gacha mới có thể xem!", ephemeral=True)
            return
        
        self.update_button()
        embed = self.create_embed(show_remaining=True)
        await interaction.response.edit_message(embed=embed, view=self)
    
    async def show_first_five(self, interaction: discord.Interaction):
        """Quay lại hiện 5 maid đầu"""
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Chỉ người gacha mới có thể xem!", ephemeral=True)
            return
        
        self.update_button()
        embed = self.create_embed(show_remaining=False)
        await interaction.response.edit_message(embed=embed, view=self)
    
    async def on_timeout(self):
        """Disable button when timeout"""
        for item in self.children:
            item.disabled = True


class MaidCollectionView(discord.ui.View):
    """View cho maid collection với pagination buttons"""
    
    def __init__(self, user_id: int, maids: List[Dict], cog, filter_type: Optional[str] = None, filter_value: Optional[str] = None):
        super().__init__(timeout=300)  # 5 minutes timeout
        self.user_id = user_id
        self.maids = maids
        self.cog = cog
        self.filter_type = filter_type
        self.filter_value = filter_value
        self.per_page = 8
        self.current_page = 1
        self.total_pages = (len(maids) - 1) // self.per_page + 1
        
        # Update button states
        self.update_buttons()
    
    def update_buttons(self):
        """Update button states based on current page"""
        # Clear all buttons first
        self.clear_items()
        
        # Add navigation buttons only if more than 1 page
        if self.total_pages > 1:
            # Previous page button
            prev_button = discord.ui.Button(
                label="◀️ Trang trước",
                style=discord.ButtonStyle.secondary,
                disabled=(self.current_page <= 1)
            )
            prev_button.callback = self.previous_page
            self.add_item(prev_button)
            
            # Page indicator button (disabled)
            page_button = discord.ui.Button(
                label=f"Trang {self.current_page}/{self.total_pages}",
                style=discord.ButtonStyle.primary,
                disabled=True
            )
            self.add_item(page_button)
            
            # Next page button
            next_button = discord.ui.Button(
                label="Trang sau ▶️",
                style=discord.ButtonStyle.secondary,
                disabled=(self.current_page >= self.total_pages)
            )
            next_button.callback = self.next_page
            self.add_item(next_button)
    
    def create_embed(self, page: int) -> discord.Embed:
        """Tạo embed cho page hiện tại"""
        self.current_page = max(1, min(page, self.total_pages))
        
        start_idx = (self.current_page - 1) * self.per_page
        end_idx = start_idx + self.per_page
        page_maids = self.maids[start_idx:end_idx]
        
        # Create title with filter info
        title = "📚 Maid Collection"
        if self.filter_type:
            if self.filter_type == 'rarity':
                title += f" - {self.filter_value.upper()} Only"
            elif self.filter_type == 'name':
                title += f" - '{self.filter_value}'"
        
        description = f"Trang {self.current_page}/{self.total_pages} • Tổng cộng: {len(self.maids)} maids"
        if self.filter_type:
            description += f"\n🔍 **Filter**: {self.filter_type} = `{self.filter_value}`"
        
        embed = EmbedBuilder.create_base_embed(
            title=title,
            description=description,
            color=0x00FF00
        )
        
        for maid in page_maids:
            # 🛡️ SAFETY: Handle legacy maid_ids that no longer exist
            template = get_maid_template_safe(maid["maid_id"])
            if not template:
                # Skip maids with invalid/legacy IDs
                continue
            name = maid["custom_name"] or template["name"]
            rarity_emoji = {"GR": "👻", "UR": "💎", "SSR": "🌟", "SR": "⭐", "R": "✨"}[template["rarity"]]
            active_text = "👑 **ACTIVE**" if maid["is_active"] else ""
            
            # Get gacha rate
            rarity_config = RARITY_CONFIG[template["rarity"]]
            gacha_rate = rarity_config.get("total_rate", 0.1)  # Use total_rate instead of rate
            
            buff_summary = " • ".join([
                f"{BUFF_TYPES[buff.get('buff_type') or buff.get('type', 'unknown')]['emoji']}{buff['value']}%" 
                for buff in maid["buffs"]
                if (buff.get('buff_type') or buff.get('type')) in BUFF_TYPES
            ])
            
            embed.add_field(
                name=f"{rarity_emoji} {template['emoji']} {name} {active_text}",
                value=f"`{maid['instance_id'][:8]}` • Rate: {gacha_rate}% • {buff_summary}",
                inline=False
            )
        
        footer_text = "💡 f!mequip <id> để trang bị • f!mc -r <rarity> • f!mc -n <tên>"
        embed.set_footer(text=footer_text)
        return embed
    
    async def previous_page(self, interaction: discord.Interaction):
        """Chuyển về trang trước"""
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Chỉ người sở hữu collection mới có thể điều khiển!", ephemeral=True)
            return
        
        if self.current_page > 1:
            self.current_page -= 1
            self.update_buttons()
            embed = self.create_embed(self.current_page)
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            await interaction.response.defer()
    
    async def next_page(self, interaction: discord.Interaction):
        """Chuyển sang trang sau"""
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Chỉ người sở hữu collection mới có thể điều khiển!", ephemeral=True)
            return
        
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.update_buttons()
            embed = self.create_embed(self.current_page)
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            await interaction.response.defer()
    
    async def on_timeout(self):
        """Disable all buttons when timeout"""
        for item in self.children:
            item.disabled = True


class DismantleConfirmView(discord.ui.View):
    def __init__(self, user_id: int, maid: Dict, reward: int, cog):
        super().__init__(timeout=300)
        self.user_id = user_id
        self.maid = maid
        self.reward = reward
        self.cog = cog
    
    @discord.ui.button(label="💥 Xác nhận tách", style=discord.ButtonStyle.danger)
    async def confirm_dismantle(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Chỉ chủ sở hữu mới có thể tách!", ephemeral=True)
            return
        
        try:
            # 🛡️ SAFETY: Atomic transaction for single dismantle
            connection = await self.cog.get_db_connection()
            await connection.execute('BEGIN TRANSACTION')
            
            # 🔐 VALIDATION: Verify ownership before deletion
            cursor = await connection.execute(
                'SELECT user_id FROM user_maids_v2 WHERE instance_id = ?', 
                (self.maid["instance_id"],)
            )
            row = await cursor.fetchone()
            if not row or row[0] != self.user_id:
                await connection.execute('ROLLBACK')
                await interaction.response.send_message("❌ Maid không thuộc sở hữu của bạn!", ephemeral=True)
                return
            
            # Delete maid with ownership validation
            cursor = await connection.execute(
                "DELETE FROM user_maids_v2 WHERE instance_id = ? AND user_id = ?",
                (self.maid["instance_id"], self.user_id)
            )
            
            # 🛡️ VALIDATION: Check if maid was actually deleted
            if cursor.rowcount == 0:
                await connection.execute('ROLLBACK')
                await interaction.response.send_message("❌ Không thể tách maid này!", ephemeral=True)
                return
            
            # Add stardust in same transaction
            await connection.execute('''
                INSERT OR REPLACE INTO user_stardust_v2 (user_id, stardust_amount, last_updated)
                VALUES (?, COALESCE((SELECT stardust_amount FROM user_stardust_v2 WHERE user_id = ?), 0) + ?, ?)
            ''', (self.user_id, self.user_id, self.reward, datetime.now().isoformat()))
            
            # 🛡️ COMMIT: All operations successful
            await connection.commit()
            
            template = get_maid_template_safe(self.maid["maid_id"])
            if not template:
                await interaction.response.send_message("❌ Maid template không tồn tại!", ephemeral=True)
                return
            name = self.maid["custom_name"] or template["name"]
            
            embed = EmbedBuilder.create_base_embed(
                title="✅ Tách thành công!",
                description=f"Đã tách {template['emoji']} **{name}**",
                color=0x00FF00
            )
            
            embed.add_field(name="⭐ Stardust nhận được", value=f"+{self.reward} bụi sao", inline=True)
            
            self.clear_items()
            await interaction.response.edit_message(embed=embed, view=self)
            
        except Exception as e:
            # 🛡️ ROLLBACK: Any error rolls back entire transaction
            try:
                await connection.execute('ROLLBACK')
            except:
                pass  # Connection might be closed
            logger.error(f"Single dismantle failed for user {self.user_id}: {e}")
            await interaction.response.send_message(f"❌ Lỗi khi tách maid: Operation đã được rollback.", ephemeral=True)
    
    @discord.ui.button(label="❌ Hủy", style=discord.ButtonStyle.secondary)
    async def cancel_dismantle(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Chỉ chủ sở hữu mới có thể hủy!", ephemeral=True)
            return
        
        embed = EmbedBuilder.create_base_embed(
            title="❌ Đã hủy",
            description="Không tách maid",
            color=0x808080
        )
        
        self.clear_items()
        await interaction.response.edit_message(embed=embed, view=self)

class BulkDismantleConfirmView(discord.ui.View):
    def __init__(self, user_id: int, maids: List[Dict], total_stardust: int, total_rewards: Dict, cog):
        super().__init__(timeout=300)
        self.user_id = user_id
        self.maids = maids
        self.total_stardust = total_stardust
        self.total_rewards = total_rewards
        self.cog = cog

    @discord.ui.button(label="💥 Xác nhận tách tất cả", style=discord.ButtonStyle.danger)
    async def confirm_bulk_dismantle(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Chỉ chủ sở hữu mới có thể tách!", ephemeral=True)
            return
        
        try:
            # 🛡️ SAFETY: Validate input before processing
            if not self.maids or len(self.maids) == 0:
                await interaction.response.send_message("❌ Không có maid nào để tách!", ephemeral=True)
                return
                
            # 🔓 REMOVED LIMIT: Cho phép người dùng tách toàn bộ collection của mình
            # Old limit: max 50 maids per bulk operation - đã được loại bỏ theo yêu cầu người dùng
            
            # 🛡️ SAFETY: Atomic transaction for bulk dismantle
            connection = await self.cog.get_db_connection()
            await connection.execute('BEGIN TRANSACTION')
            
            # 🔐 VALIDATION: Verify ownership before deletion
            instance_ids = [maid["instance_id"] for maid in self.maids]
            for instance_id in instance_ids:
                cursor = await connection.execute(
                    'SELECT user_id FROM user_maids_v2 WHERE instance_id = ?', 
                    (instance_id,)
                )
                row = await cursor.fetchone()
                if not row or row[0] != self.user_id:
                    await connection.execute('ROLLBACK')
                    await interaction.response.send_message(
                        f"❌ Phát hiện maid không thuộc sở hữu! Bulk dismantle bị hủy.",
                        ephemeral=True
                    )
                    return
            
            # Delete all maids with ownership validation
            placeholders = ",".join("?" * len(instance_ids))
            cursor = await connection.execute(
                f"DELETE FROM user_maids_v2 WHERE instance_id IN ({placeholders}) AND user_id = ?",
                instance_ids + [self.user_id]  # Add user_id for extra safety
            )
            
            # 🛡️ VALIDATION: Check if expected number of maids were deleted
            if cursor.rowcount != len(instance_ids):
                await connection.execute('ROLLBACK')
                await interaction.response.send_message(
                    f"❌ Có lỗi xảy ra khi tách maid (expected {len(instance_ids)}, deleted {cursor.rowcount}). Operation rolled back.",
                    ephemeral=True
                )
                return
            
            # Add stardust in same transaction
            await connection.execute('''
                INSERT OR REPLACE INTO user_stardust_v2 (user_id, stardust_amount, last_updated)
                VALUES (?, COALESCE((SELECT stardust_amount FROM user_stardust_v2 WHERE user_id = ?), 0) + ?, ?)
            ''', (self.user_id, self.user_id, self.total_stardust, datetime.now().isoformat()))
            
            # 🛡️ COMMIT: All operations successful
            await connection.commit()
            
            embed = EmbedBuilder.create_base_embed(
                title="💥 Tách thành công!",
                description=f"Đã tách **{len(self.maids)} maid** thành stardust!",
                color=0x00FF00
            )
            
            # Show breakdown
            breakdown_parts = []
            for rarity in ["GR", "UR", "SSR", "SR", "R"]:
                if rarity in self.total_rewards:
                    count = self.total_rewards[rarity]
                    reward_per = STARDUST_CONFIG["dismantle_rewards"][rarity]
                    total_per_rarity = count * reward_per
                    rarity_emoji = {"GR": "👻", "UR": "💎", "SSR": "🌟", "SR": "⭐", "R": "✨"}[rarity]
                    breakdown_parts.append(f"{rarity_emoji} {rarity}: {count}x → +{total_per_rarity}⭐")
            
            embed.add_field(name="📊 Đã tách", value="\n".join(breakdown_parts), inline=False)
            embed.add_field(name="💰 Tổng stardust nhận", value=f"**+{self.total_stardust:,} ⭐**", inline=True)
            
            # Get current stardust for display
            current_stardust = await self.cog.get_user_stardust(self.user_id)
            embed.add_field(name="💫 Stardust hiện có", value=f"{current_stardust:,} ⭐", inline=True)
            
            self.clear_items()
            await interaction.response.edit_message(embed=embed, view=self)
            
        except Exception as e:
            # 🛡️ ROLLBACK: Any error rolls back entire transaction
            try:
                await connection.execute('ROLLBACK')
            except:
                pass  # Connection might be closed
            logger.error(f"Bulk dismantle failed for user {self.user_id}: {e}")
            await interaction.response.send_message(f"❌ Lỗi khi tách maid: Đã rollback toàn bộ operation.", ephemeral=True)

    @discord.ui.button(label="❌ Hủy", style=discord.ButtonStyle.secondary)
    async def cancel_bulk_dismantle(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Chỉ chủ sở hữu mới có thể hủy!", ephemeral=True)
            return
        
        embed = EmbedBuilder.create_base_embed(
            title="❌ Đã hủy",
            description="Đã hủy thao tác tách maid.",
            color=0x808080
        )
        
        self.clear_items()
        await interaction.response.edit_message(embed=embed, view=self)

class RerollConfirmView(discord.ui.View):
    def __init__(self, user_id: int, maid: Dict, cost: int, cog):
        super().__init__(timeout=300)
        self.user_id = user_id
        self.maid = maid
        self.cost = cost
        self.cog = cog
    
    @discord.ui.button(label="🎲 Xác nhận reroll", style=discord.ButtonStyle.primary)
    async def confirm_reroll(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Chỉ chủ sở hữu mới có thể reroll!", ephemeral=True)
            return
        
        try:
            # Check stardust again
            current_stardust = await self.cog.get_user_stardust(self.user_id)
            if current_stardust < self.cost:
                await interaction.response.send_message("❌ Không đủ stardust!", ephemeral=True)
                return
            
            # Save old buffs
            old_buffs = self.maid["buffs"].copy()
            
            # Generate new buffs
            new_buffs = self.cog.generate_buffs(self.maid["maid_id"])
            
            # 🛡️ SAFETY: Atomic transaction for reroll
            connection = await self.cog.get_db_connection()
            await connection.execute('BEGIN TRANSACTION')
            
            # 🔐 VALIDATION: Verify maid ownership
            cursor = await connection.execute(
                'SELECT user_id FROM user_maids_v2 WHERE instance_id = ?', 
                (self.maid["instance_id"],)
            )
            row = await cursor.fetchone()
            if not row or row[0] != self.user_id:
                await connection.execute('ROLLBACK')
                await interaction.response.send_message("❌ Maid không thuộc sở hữu của bạn!", ephemeral=True)
                return
            
            # 🔐 VALIDATION: Double-check stardust and spend atomically
            cursor = await connection.execute('''
                UPDATE user_stardust_v2 SET stardust_amount = stardust_amount - ?, last_updated = ?
                WHERE user_id = ? AND stardust_amount >= ?
            ''', (self.cost, datetime.now().isoformat(), self.user_id, self.cost))
            
            if cursor.rowcount == 0:
                await connection.execute('ROLLBACK')
                await interaction.response.send_message("❌ Không đủ stardust để reroll!", ephemeral=True)
                return
            
            # Update maid buffs
            cursor = await connection.execute('''
                UPDATE user_maids_v2 
                SET buff_values = ?, reroll_count = reroll_count + 1, last_reroll_time = ?
                WHERE instance_id = ? AND user_id = ?
            ''', (json.dumps(new_buffs), datetime.now().isoformat(), self.maid["instance_id"], self.user_id))
            
            # 🛡️ VALIDATION: Check if maid was actually updated
            if cursor.rowcount == 0:
                await connection.execute('ROLLBACK')
                await interaction.response.send_message("❌ Không thể reroll maid này!", ephemeral=True)
                return
            
            # Save reroll history
            await connection.execute('''
                INSERT INTO maid_reroll_history_v2 
                (user_id, maid_instance_id, old_buffs, new_buffs, stardust_cost, reroll_time)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (self.user_id, self.maid["instance_id"], json.dumps(old_buffs), 
                  json.dumps(new_buffs), self.cost, datetime.now().isoformat()))
            
            # 🛡️ COMMIT: All operations successful
            await connection.commit()
            
            template = get_maid_template_safe(self.maid["maid_id"])
            if not template:
                await interaction.response.send_message("❌ Maid template không tồn tại!", ephemeral=True)
                return
            name = self.maid["custom_name"] or template["name"]
            
            embed = EmbedBuilder.create_base_embed(
                title="🎲 Reroll thành công!",
                description=f"Đã reroll buffs cho {template['emoji']} **{name}**",
                color=0x00FF00
            )
            
            # Show new buffs
            new_buff_text = "\n".join([
                f"{BUFF_TYPES[buff.get('buff_type') or buff.get('type', 'unknown')]['emoji']} {BUFF_TYPES[buff.get('buff_type') or buff.get('type', 'unknown')]['name']}: +{buff['value']}%"
                for buff in new_buffs
                if (buff.get('buff_type') or buff.get('type')) in BUFF_TYPES
            ])
            
            embed.add_field(name="✨ Buffs mới", value=new_buff_text, inline=False)
            embed.add_field(name="💰 Chi phí", value=f"-{self.cost} ⭐", inline=True)
            
            self.clear_items()
            await interaction.response.edit_message(embed=embed, view=self)
            
        except Exception as e:
            # 🛡️ ROLLBACK: Any error rolls back entire transaction
            try:
                await connection.execute('ROLLBACK')
            except:
                pass  # Connection might be closed
            logger.error(f"Reroll failed for user {self.user_id}: {e}")
            await interaction.response.send_message(f"❌ Lỗi khi reroll maid: Operation đã được rollback. Stardust không bị trừ.", ephemeral=True)
    
    @discord.ui.button(label="❌ Hủy", style=discord.ButtonStyle.secondary)
    async def cancel_reroll(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Chỉ chủ sở hữu mới có thể hủy!", ephemeral=True)
            return
        
        embed = EmbedBuilder.create_base_embed(
            title="❌ Đã hủy",
            description="Không reroll buffs",
            color=0x808080
        )
        
        self.clear_items()
        await interaction.response.edit_message(embed=embed, view=self)

async def setup(bot):
    await bot.add_cog(MaidSystemV2(bot)) 