import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import uuid
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any

from database.database import Database
from utils.embeds import EmbedBuilder
from utils.registration import require_registration
from utils.enhanced_logging import get_bot_logger

logger = get_bot_logger()

class TradeOffer:
    """Class để quản lý một giao dịch trade"""
    def __init__(self, channel_id: int, user1_id: int, user2_id: int):
        self.trade_id = str(uuid.uuid4())[:8]
        self.channel_id = channel_id
        self.user1_id = user1_id
        self.user2_id = user2_id
        self.created_at = datetime.now()
        self.expires_at = datetime.now() + timedelta(minutes=10)
        
        # Trade offers từ mỗi user
        self.user1_offer = {
            "maids": [],
            "money": 0,
            "stardust": 0,
            "confirmed": False
        }
        self.user2_offer = {
            "maids": [],
            "money": 0,
            "stardust": 0,
            "confirmed": False
        }
        
    def get_user_offer(self, user_id: int):
        """Lấy offer của user"""
        if user_id == self.user1_id:
            return self.user1_offer
        elif user_id == self.user2_id:
            return self.user2_offer
        return None
    
    def is_participant(self, user_id: int) -> bool:
        """Kiểm tra user có phải participant không"""
        return user_id in [self.user1_id, self.user2_id]
    
    def is_expired(self) -> bool:
        """Kiểm tra trade đã hết hạn chưa"""
        return datetime.now() > self.expires_at
    
    def both_confirmed(self) -> bool:
        """Kiểm tra cả 2 user đã confirm chưa"""
        return self.user1_offer["confirmed"] and self.user2_offer["confirmed"]

class TradeConfirmationView(discord.ui.View):
    def __init__(self, requester_id: int, target_id: int, trading_cog):
        super().__init__(timeout=30.0)  # 30 seconds timeout
        self.requester_id = requester_id
        self.target_id = target_id
        self.trading_cog = trading_cog
    
    @discord.ui.button(label="✅ Đồng ý trade", style=discord.ButtonStyle.success)
    async def accept_trade(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Chỉ user được mời mới có thể accept
        if interaction.user.id != self.target_id:
            await interaction.response.send_message("❌ Chỉ người được mời mới có thể phản hồi!", ephemeral=True)
            return
        
        # Disable all buttons
        for item in self.children:
            item.disabled = True
        
        # Update embed to show accepted
        embed = discord.Embed(
            title="✅ Lời Mời Được Chấp Nhận!",
            description=f"**{interaction.user.display_name}** đã đồng ý trade!\n\n"
                       f"Đang tạo phòng trade...",
            color=0x00FF00
        )
        
        await interaction.response.edit_message(embed=embed, view=self)
        
        # Tạo trade mới
        await self.trading_cog.create_trade_room(interaction, self.requester_id, self.target_id)
        
        # Stop the view
        self.stop()
    
    @discord.ui.button(label="❌ Từ chối", style=discord.ButtonStyle.danger)
    async def decline_trade(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Chỉ user được mời mới có thể decline
        if interaction.user.id != self.target_id:
            await interaction.response.send_message("❌ Chỉ người được mời mới có thể phản hồi!", ephemeral=True)
            return
        
        # Disable all buttons
        for item in self.children:
            item.disabled = True
        
        # Update embed to show declined
        embed = discord.Embed(
            title="❌ Lời Mời Bị Từ Chối",
            description=f"**{interaction.user.display_name}** đã từ chối trade.",
            color=0xFF0000
        )
        
        await interaction.response.edit_message(embed=embed, view=self)
        self.stop()
    
    async def on_timeout(self):
        # Disable all buttons when timeout
        for item in self.children:
            item.disabled = True
        
        # Update embed to show timeout
        embed = discord.Embed(
            title="⏰ Lời Mời Đã Hết Hạn",
            description="Lời mời trade đã hết hạn và bị hủy.",
            color=0x808080
        )
        
        # Try to update the message
        try:
            await self.message.edit(embed=embed, view=self)
        except:
            pass  # Message might be deleted

class MaidTrading(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
        self.active_trades: Dict[int, TradeOffer] = {}  # channel_id -> TradeOffer
        
    async def cog_load(self):
        """Khởi tạo khi load cog"""
        logger.info("MaidTrading cog loaded")
        self._tables_initialized = False
    
    async def init_trade_tables(self):
        """Tạo bảng trade history"""
        try:
            if not hasattr(self.bot, 'db') or not self.bot.db:
                logger.warning("Database not available, skipping table creation")
                return
            
            connection = await self.bot.db.get_connection()
            
            # Trade history table
            await connection.execute('''
                CREATE TABLE IF NOT EXISTS trade_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    trade_id TEXT NOT NULL,
                    user1_id INTEGER NOT NULL,
                    user2_id INTEGER NOT NULL,
                    user1_offer TEXT NOT NULL,
                    user2_offer TEXT NOT NULL,
                    completed_at TEXT NOT NULL,
                    channel_id INTEGER NOT NULL
                )
            ''')
            
            await connection.commit()
            logger.info("✅ Trade tables created successfully")
            
        except Exception as e:
            logger.error(f"Error creating trade tables: {e}")
    
    async def ensure_tables_ready(self):
        """Ensure tables are created when called from commands"""
        if not self._tables_initialized and hasattr(self.bot, 'db') and self.bot.db:
            try:
                await self.init_trade_tables()
                self._tables_initialized = True
            except Exception as e:
                logger.error(f"Error initializing trade tables: {e}")
    
    async def get_user_maids(self, user_id: int) -> List[Dict]:
        """Lấy danh sách maid của user"""
        try:
            connection = await self.bot.db.get_connection()
            cursor = await connection.execute('''
                SELECT instance_id, maid_id, custom_name, buff_values, is_active
                FROM user_maids_v2 WHERE user_id = ?
            ''', (user_id,))
            rows = await cursor.fetchall()
            
            maids = []
            for row in rows:
                maid_data = {
                    'instance_id': row[0],
                    'maid_id': row[1],
                    'custom_name': row[2],
                    'buff_values': json.loads(row[3]),
                    'is_active': bool(row[4])
                }
                maids.append(maid_data)
            
            return maids
        except Exception as e:
            logger.error(f"Error getting user maids: {e}")
            return []
    
    async def get_user_stats(self, user_id: int) -> Dict:
        """Lấy stats của user (money, stardust)"""
        try:
            connection = await self.bot.db.get_connection()
            
            # Get money
            cursor = await connection.execute('SELECT money FROM users WHERE user_id = ?', (user_id,))
            money_row = await cursor.fetchone()
            money = money_row[0] if money_row else 0
            
            # Get stardust
            cursor = await connection.execute('SELECT stardust_amount FROM user_stardust_v2 WHERE user_id = ?', (user_id,))
            stardust_row = await cursor.fetchone()
            stardust = stardust_row[0] if stardust_row else 0
            
            return {"money": money, "stardust": stardust}
        except Exception as e:
            logger.error(f"Error getting user stats: {e}")
            return {"money": 0, "stardust": 0}
    
    def cleanup_expired_trades(self):
        """Dọn dẹp các trade đã hết hạn"""
        expired_channels = []
        for channel_id, trade in self.active_trades.items():
            if trade.is_expired():
                expired_channels.append(channel_id)
        
        for channel_id in expired_channels:
            del self.active_trades[channel_id]
    
    @commands.hybrid_group(name="trade", description="🔄 Hệ thống trade maid", invoke_without_command=True)
    async def trade_group(self, ctx, user: Optional[discord.Member] = None):
        """Group command cho trade system"""
        # Check registration if user is provided
        if user:
            # Simple registration check
            try:
                await self.bot.db.get_user(ctx.author.id)
            except:
                embed = EmbedBuilder.create_error_embed("❌ Bạn chưa đăng ký! Sử dụng `f!register` để bắt đầu.")
                await ctx.send(embed=embed)
                return
            await self.trade_start(ctx, user)
        else:
            embed = discord.Embed(
                title="🔄 Hệ Thống Trade Maid",
                description="**Cách sử dụng:**\n"
                           f"• `{ctx.prefix}trade @user` - Bắt đầu trade\n"
                           f"• `{ctx.prefix}trade add -m <maid_id>` - Thêm maid\n"
                           f"• `{ctx.prefix}trade add -c <số tiền>` - Thêm tiền\n"
                           f"• `{ctx.prefix}trade add -st <stardust>` - Thêm stardust\n"
                           f"• `{ctx.prefix}trade add -r <rarity>` - Thêm maid theo rarity\n"
                           f"• `{ctx.prefix}trade add -n <name>` - Thêm maid theo tên\n"
                           f"• `{ctx.prefix}trade confirm` - Xác nhận trade\n"
                           f"• `{ctx.prefix}trade cancel` - Hủy trade\n"
                           f"• `{ctx.prefix}trade status` - Xem trạng thái",
                color=0x00AAFF
            )
            await ctx.send(embed=embed)
    
    async def trade_start(self, ctx, user: discord.Member):
        """Bắt đầu một giao dịch trade"""
        await self.ensure_tables_ready()
        self.cleanup_expired_trades()
        
        # Kiểm tra không trade với chính mình
        if user.id == ctx.author.id:
            embed = EmbedBuilder.create_error_embed("❌ Bạn không thể trade với chính mình!")
            await ctx.send(embed=embed)
            return
        
        # Kiểm tra user được mention có phải là bot không
        if user.bot:
            embed = EmbedBuilder.create_error_embed("❌ Không thể trade với bot!")
            await ctx.send(embed=embed)
            return
        
        # Kiểm tra channel đã có trade chưa
        if ctx.channel.id in self.active_trades:
            embed = EmbedBuilder.create_error_embed("❌ Kênh này đang có giao dịch trade khác! Hãy đợi hoặc chuyển sang kênh khác.")
            await ctx.send(embed=embed)
            return
        
        # Tạo embed hỏi xác nhận
        embed = discord.Embed(
            title="🔄 Lời Mời Trade Maid",
            description=f"**{ctx.author.display_name}** muốn trade với **{user.display_name}**\n\n"
                       f"💫 **{user.display_name}**, bạn có đồng ý trade không?",
            color=0xFFAA00
        )
        
        embed.add_field(
            name="⏰ Thời gian",
            value="Lời mời sẽ hết hạn sau **30 giây**",
            inline=False
        )
        
        # Tạo view với buttons
        view = TradeConfirmationView(ctx.author.id, user.id, self)
        
        await ctx.send(f"{user.mention}", embed=embed, view=view)
    
    async def create_trade_room(self, interaction: discord.Interaction, user1_id: int, user2_id: int):
        """Tạo phòng trade sau khi đối phương đồng ý"""
        await self.ensure_tables_ready()
        self.cleanup_expired_trades()
        
        # Kiểm tra channel đã có trade chưa (double check)
        if interaction.channel.id in self.active_trades:
            embed = EmbedBuilder.create_error_embed("❌ Kênh này đang có giao dịch trade khác!")
            await interaction.followup.send(embed=embed)
            return
        
        # Tạo trade mới
        trade = TradeOffer(interaction.channel.id, user1_id, user2_id)
        self.active_trades[interaction.channel.id] = trade
        
        # Lấy thông tin users
        user1 = self.bot.get_user(user1_id)
        user2 = self.bot.get_user(user2_id)
        
        # Nếu get_user không có, thử fetch từ Discord API
        if not user1:
            try:
                user1 = await self.bot.fetch_user(user1_id)
            except:
                user1 = None
                
        if not user2:
            try:
                user2 = await self.bot.fetch_user(user2_id)
            except:
                user2 = None
        
        # Ưu tiên username (global name) > display_name > fallback
        if user1:
            user1_name = user1.global_name or user1.display_name or user1.name
        else:
            user1_name = f"User {user1_id}"
            
        if user2:
            user2_name = user2.global_name or user2.display_name or user2.name
        else:
            user2_name = f"User {user2_id}"
        
        # Tạo embed thông báo trade
        embed = discord.Embed(
            title="🔄 Giao Dịch Trade Maid", 
            description=f"**{user1_name}** ⬌ **{user2_name}**\n\n"
                       f"🆔 Trade ID: `{trade.trade_id}`\n\n"
                       f"**Cách sử dụng:**\n"
                       f"• `f!trade add -m <maid_id>` - Thêm maid\n"
                       f"• `f!trade add -c <số tiền>` - Thêm tiền\n"
                       f"• `f!trade add -st <stardust>` - Thêm stardust\n"
                       f"• `f!trade add -r <rate>` - Thêm maid theo rarity\n"
                       f"• `f!trade add -n <name>` - Thêm maid theo tên\n"
                       f"• `f!trade confirm` - Xác nhận trade\n"
                       f"• `f!trade cancel` - Hủy trade",
            color=0x00FF00
        )
        
        embed.add_field(
            name=f"📦 {user1_name} offers:",
            value="*Chưa có gì*",
            inline=True
        )
        embed.add_field(
            name=f"📦 {user2_name} offers:",
            value="*Chưa có gì*",
            inline=True
        )
        
        await interaction.followup.send(embed=embed)
        
        # Không có timeout ngay lập tức - chỉ timeout khi có người đầu tiên confirm
    
    async def _timeout_waiting_for_second_confirm(self, ctx, trade_id: str):
        """Timeout chờ người thứ 2 confirm sau khi người đầu tiên đã confirm"""
        await asyncio.sleep(60)  # 1 phút
        
        if ctx.channel.id in self.active_trades:
            trade = self.active_trades[ctx.channel.id]
            if trade.trade_id == trade_id and not trade.both_confirmed():
                # Có đúng 1 người confirm và timeout
                del self.active_trades[ctx.channel.id]
                embed = EmbedBuilder.create_error_embed(f"⏰ Trade `{trade.trade_id}` đã hết thời gian chờ xác nhận và bị hủy!")
                try:
                    await ctx.send(embed=embed)
                except:
                    # Channel might be deleted or bot has no permission
                    pass
    
    async def _cleanup_trade_after_timeout_ctx(self, channel, trade_id: str):
        """Cleanup trade sau timeout với channel object (deprecated - không dùng nữa)"""
        pass
    

    
    @trade_group.command(name="add", description="➕ Thêm items vào trade")
    async def trade_add(self, ctx, *, args: str):
        """Thêm items vào trade hiện tại"""
        await self.ensure_tables_ready()
        
        # Check registration
        try:
            await self.bot.db.get_user(ctx.author.id)
        except:
            embed = EmbedBuilder.create_error_embed("❌ Bạn chưa đăng ký! Sử dụng `f!register` để bắt đầu.")
            await ctx.send(embed=embed)
            return
        
        # Kiểm tra có trade trong channel không
        if ctx.channel.id not in self.active_trades:
            embed = EmbedBuilder.create_error_embed("❌ Không có giao dịch trade nào trong kênh này!")
            await ctx.send(embed=embed)
            return
        
        trade = self.active_trades[ctx.channel.id]
        
        # Kiểm tra user có phải participant không
        if not trade.is_participant(ctx.author.id):
            embed = EmbedBuilder.create_error_embed("❌ Bạn không phải là người tham gia trade này!")
            await ctx.send(embed=embed)
            return
        
        # Kiểm tra trade đã hết hạn chưa
        if trade.is_expired():
            del self.active_trades[ctx.channel.id]
            embed = EmbedBuilder.create_error_embed("⏰ Trade đã hết hạn!")
            await ctx.send(embed=embed)
            return
        
        # Parse arguments
        parts = args.strip().split()
        if len(parts) < 2:
            embed = EmbedBuilder.create_error_embed("❌ Cú pháp không đúng! Sử dụng: `f!trade add -m <maid_id>` hoặc `-c <money>` hoặc `-st <stardust>` hoặc `-r <rarity>` hoặc `-n <name>`")
            await ctx.send(embed=embed)
            return
        
        flag = parts[0]
        value = " ".join(parts[1:])
        
        user_offer = trade.get_user_offer(ctx.author.id)
        user_stats = await self.get_user_stats(ctx.author.id)
        
        if flag == "-m":
            # Thêm maid theo ID
            maid_id = value
            user_maids = await self.get_user_maids(ctx.author.id)
            
            # DEBUG: Log tất cả maid IDs để debug
            logger.info(f"DEBUG: Looking for maid_id '{maid_id}'")
            logger.info(f"DEBUG: Found {len(user_maids)} maids for user")
            for maid in user_maids:
                logger.info(f"DEBUG: Maid - ID: {maid['instance_id']}, Maid_ID: {maid['maid_id']}")
            
            # Tìm maid (support 8 ký tự đầu hoặc full ID)
            found_maid = None
            for maid in user_maids:
                if (maid['instance_id'] == maid_id or 
                    maid['instance_id'].startswith(maid_id.lower())):
                    found_maid = maid
                    break
            
            if not found_maid:
                embed = EmbedBuilder.create_error_embed(f"❌ Không tìm thấy maid với ID `{maid_id}`!")
                # DEBUG: Thêm gợi ý với instance IDs thật
                debug_text = "\n💡 Instance IDs của bạn:\n"
                for i, maid in enumerate(user_maids[:5]):  # Show first 5
                    debug_text += f"• {maid['instance_id'][:8]} - {maid['maid_id']}\n"
                if len(user_maids) > 5:
                    debug_text += f"... và {len(user_maids) - 5} maid khác"
                embed.add_field(name="🔍 Debug Info", value=debug_text, inline=False)
                await ctx.send(embed=embed)
                return
            
            # Kiểm tra đã thêm chưa (support 8 ký tự đầu)
            if any(m['instance_id'].startswith(maid_id.lower()) for m in user_offer['maids']):
                embed = EmbedBuilder.create_error_embed(f"❌ Maid `{maid_id}` đã được thêm vào trade!")
                await ctx.send(embed=embed)
                return
            
            user_offer['maids'].append(found_maid)
            embed = EmbedBuilder.create_success_embed("Thành công", f"✅ Đã thêm maid **{found_maid['maid_id']}** (`{maid_id}`) vào trade!")
            
        elif flag == "-c":
            # Thêm tiền
            try:
                amount = int(value)
                if amount <= 0:
                    embed = EmbedBuilder.create_error_embed("❌ Số tiền phải lớn hơn 0!")
                    await ctx.send(embed=embed)
                    return
                
                if amount > user_stats['money']:
                    embed = EmbedBuilder.create_error_embed(f"❌ Bạn không đủ tiền! Hiện có: {user_stats['money']:,} coins")
                    await ctx.send(embed=embed)
                    return
                
                user_offer['money'] += amount
                embed = EmbedBuilder.create_success_embed("Thành công", f"✅ Đã thêm **{amount:,}** coins vào trade!")
                
            except ValueError:
                embed = EmbedBuilder.create_error_embed("❌ Số tiền không hợp lệ!")
                await ctx.send(embed=embed)
                return
        
        elif flag == "-st":
            # Thêm stardust
            try:
                amount = int(value)
                if amount <= 0:
                    embed = EmbedBuilder.create_error_embed("❌ Số stardust phải lớn hơn 0!")
                    await ctx.send(embed=embed)
                    return
                
                if amount > user_stats['stardust']:
                    embed = EmbedBuilder.create_error_embed(f"❌ Bạn không đủ stardust! Hiện có: {user_stats['stardust']:,}")
                    await ctx.send(embed=embed)
                    return
                
                user_offer['stardust'] += amount
                embed = EmbedBuilder.create_success_embed("Thành công", f"✅ Đã thêm **{amount:,}** stardust vào trade!")
                
            except ValueError:
                embed = EmbedBuilder.create_error_embed("❌ Số stardust không hợp lệ!")
                await ctx.send(embed=embed)
                return
        
        elif flag == "-r":
            # Thêm maid theo rarity
            rarity = value.upper()
            if rarity not in ["UR", "SSR", "SR", "R"]:
                embed = EmbedBuilder.create_error_embed("❌ Rarity không hợp lệ! Sử dụng: UR, SSR, SR, R")
                await ctx.send(embed=embed)
                return
            
            user_maids = await self.get_user_maids(ctx.author.id)
            added_count = 0
            
            for maid in user_maids:
                if maid['maid_id'].endswith(f"_{rarity.lower()}"):
                    # Kiểm tra chưa thêm
                    if not any(m['instance_id'] == maid['instance_id'] for m in user_offer['maids']):
                        user_offer['maids'].append(maid)
                        added_count += 1
            
            if added_count == 0:
                embed = EmbedBuilder.create_error_embed(f"❌ Không tìm thấy maid {rarity} nào chưa được thêm!")
                await ctx.send(embed=embed)
                return
            
            embed = EmbedBuilder.create_success_embed("Thành công", f"✅ Đã thêm **{added_count}** maid {rarity} vào trade!")
        
        elif flag == "-n":
            # Thêm maid theo tên
            name = value.lower()
            user_maids = await self.get_user_maids(ctx.author.id)
            added_count = 0
            
            for maid in user_maids:
                maid_name = maid['maid_id'].split('_')[0].lower()
                if name in maid_name:
                    # Kiểm tra chưa thêm
                    if not any(m['instance_id'] == maid['instance_id'] for m in user_offer['maids']):
                        user_offer['maids'].append(maid)
                        added_count += 1
            
            if added_count == 0:
                embed = EmbedBuilder.create_error_embed(f"❌ Không tìm thấy maid có tên chứa '{value}' nào chưa được thêm!")
                await ctx.send(embed=embed)
                return
            
            embed = EmbedBuilder.create_success_embed("Thành công", f"✅ Đã thêm **{added_count}** maid có tên chứa '{value}' vào trade!")
        
        else:
            embed = EmbedBuilder.create_error_embed("❌ Flag không hợp lệ! Sử dụng: `-m`, `-c`, `-st`, `-r`, `-n`")
            await ctx.send(embed=embed)
            return
        
        # Reset confirmation
        user_offer['confirmed'] = False
        trade.user1_offer['confirmed'] = False
        trade.user2_offer['confirmed'] = False
        
        await ctx.send(embed=embed)
        
        # Gửi updated trade embed
        await self.send_trade_status(ctx, trade)
    
    async def send_trade_status(self, ctx, trade: TradeOffer):
        """Gửi trạng thái hiện tại của trade"""
        user1 = self.bot.get_user(trade.user1_id)
        user2 = self.bot.get_user(trade.user2_id)
        
        # Nếu get_user không có, thử fetch từ Discord API
        if not user1:
            try:
                user1 = await self.bot.fetch_user(trade.user1_id)
            except:
                user1 = None
                
        if not user2:
            try:
                user2 = await self.bot.fetch_user(trade.user2_id)
            except:
                user2 = None
        
        # Ưu tiên username (global name) > display_name > fallback
        if user1:
            user1_name = user1.global_name or user1.display_name or user1.name
        else:
            user1_name = f"User {trade.user1_id}"
            
        if user2:
            user2_name = user2.global_name or user2.display_name or user2.name
        else:
            user2_name = f"User {trade.user2_id}"
        
        # Debug log
        logger.info(f"Trade Status: User1={user1_name} (ID: {trade.user1_id}), User2={user2_name} (ID: {trade.user2_id})")
        
        embed = discord.Embed(
            title=f"🔄 Trade Status - ID: {trade.trade_id}",
            description=f"**{user1_name}** ⬌ **{user2_name}**",
            color=0x00FF00 if trade.both_confirmed() else 0xFFAA00
        )
        
        # User 1 offer
        offer1_text = self.format_offer(trade.user1_offer)
        status1 = "✅ Đã xác nhận" if trade.user1_offer['confirmed'] else "⏳ Chờ xác nhận"
        embed.add_field(
            name=f"📦 {user1_name} offers: {status1}",
            value=offer1_text or "*Chưa có gì*",
            inline=False
        )
        
        # User 2 offer
        offer2_text = self.format_offer(trade.user2_offer)
        status2 = "✅ Đã xác nhận" if trade.user2_offer['confirmed'] else "⏳ Chờ xác nhận"
        embed.add_field(
            name=f"📦 {user2_name} offers: {status2}",
            value=offer2_text or "*Chưa có gì*",
            inline=False
        )
        
        if trade.both_confirmed():
            embed.add_field(
                name="🎉 Trade hoàn thành!",
                value="Giao dịch đã được thực hiện thành công!",
                inline=False
            )
        else:
            # Kiểm tra xem có ai đã confirm chưa
            confirmed_count = sum([trade.user1_offer['confirmed'], trade.user2_offer['confirmed']])
            if confirmed_count == 1:
                embed.add_field(
                    name="⏰ Chờ xác nhận:",
                    value="Người còn lại có **1 phút** để xác nhận trade!",
                    inline=False
                )
            elif confirmed_count == 0:
                embed.add_field(
                    name="💡 Trạng thái:",
                    value="Cả 2 người chưa xác nhận. Không có giới hạn thời gian.",
                    inline=False
                )
        
        await ctx.send(embed=embed)
    
    def format_offer(self, offer: Dict) -> str:
        """Format offer thành text"""
        items = []
        
        if offer['maids']:
            maid_list = []
            for maid in offer['maids'][:5]:  # Hiển thị tối đa 5 maid
                name = maid['maid_id'].replace('_', ' ').title()
                maid_list.append(f"• {name} (`{maid['instance_id']}`)")
            
            if len(offer['maids']) > 5:
                maid_list.append(f"• ... và {len(offer['maids']) - 5} maid khác")
            
            items.append(f"**Maids ({len(offer['maids'])}):**\n" + "\n".join(maid_list))
        
        if offer['money'] > 0:
            items.append(f"**💰 Coins:** {offer['money']:,}")
        
        if offer['stardust'] > 0:
            items.append(f"**⭐ Stardust:** {offer['stardust']:,}")
        
        return "\n\n".join(items) if items else ""
    
    @trade_group.command(name="confirm", description="✅ Xác nhận trade")
    async def trade_confirm(self, ctx):
        """Xác nhận trade"""
        await self.ensure_tables_ready()
        
        # Check registration
        try:
            await self.bot.db.get_user(ctx.author.id)
        except:
            embed = EmbedBuilder.create_error_embed("❌ Bạn chưa đăng ký! Sử dụng `f!register` để bắt đầu.")
            await ctx.send(embed=embed)
            return
        
        if ctx.channel.id not in self.active_trades:
            embed = EmbedBuilder.create_error_embed("❌ Không có giao dịch trade nào trong kênh này!")
            await ctx.send(embed=embed)
            return
        
        trade = self.active_trades[ctx.channel.id]
        
        if not trade.is_participant(ctx.author.id):
            embed = EmbedBuilder.create_error_embed("❌ Bạn không phải là người tham gia trade này!")
            await ctx.send(embed=embed)
            return
        
        if trade.is_expired():
            del self.active_trades[ctx.channel.id]
            embed = EmbedBuilder.create_error_embed("⏰ Trade đã hết hạn!")
            await ctx.send(embed=embed)
            return
        
        user_offer = trade.get_user_offer(ctx.author.id)
        
        # Kiểm tra có ai đã confirm trước chưa
        first_to_confirm = not (trade.user1_offer['confirmed'] or trade.user2_offer['confirmed'])
        
        user_offer['confirmed'] = True
        
        if first_to_confirm:
            # Người đầu tiên confirm - bắt đầu timeout cho người còn lại
            embed = EmbedBuilder.create_success_embed("Thành công", f"✅ **{ctx.author.display_name}** đã xác nhận trade!\n⏰ Đối phương có **1 phút** để xác nhận.")
            await ctx.send(embed=embed)
            
            # Bắt đầu timeout 1 phút cho người còn lại
            asyncio.create_task(self._timeout_waiting_for_second_confirm(ctx, trade.trade_id))
        else:
            # Người thứ 2 confirm - thực hiện trade ngay
            embed = EmbedBuilder.create_success_embed("Thành công", f"✅ **{ctx.author.display_name}** đã xác nhận trade!")
            await ctx.send(embed=embed)
        
        # Kiểm tra cả 2 đã confirm chưa
        if trade.both_confirmed():
            await self.execute_trade(ctx, trade)
        else:
            await self.send_trade_status(ctx, trade)
    
    async def execute_trade(self, ctx, trade: TradeOffer):
        """Thực hiện trade"""
        try:
            connection = await self.bot.db.get_connection()
            
            # Validate lại tài sản trước khi trade
            user1_stats = await self.get_user_stats(trade.user1_id)
            user2_stats = await self.get_user_stats(trade.user2_id)
            
            # Kiểm tra user 1
            if (trade.user1_offer['money'] > user1_stats['money'] or 
                trade.user1_offer['stardust'] > user1_stats['stardust']):
                embed = EmbedBuilder.create_error_embed("❌ User 1 không đủ tài sản để thực hiện trade!")
                await ctx.send(embed=embed)
                return
            
            # Kiểm tra user 2  
            if (trade.user2_offer['money'] > user2_stats['money'] or 
                trade.user2_offer['stardust'] > user2_stats['stardust']):
                embed = EmbedBuilder.create_error_embed("❌ User 2 không đủ tài sản để thực hiện trade!")
                await ctx.send(embed=embed)
                return
            
            # 🛡️ SAFETY: Begin atomic transaction  
            await connection.execute('BEGIN TRANSACTION')
            
            # 🔐 VALIDATION: Verify maid ownership before transfer
            for maid in trade.user1_offer['maids']:
                cursor = await connection.execute(
                    'SELECT user_id FROM user_maids_v2 WHERE instance_id = ?', 
                    (maid['instance_id'],)
                )
                row = await cursor.fetchone()
                if not row or row[0] != trade.user1_id:
                    await connection.execute('ROLLBACK')
                    logger.warning(f"🚨 SECURITY: User {trade.user1_id} tried to trade maid {maid['instance_id']} they don't own!")
                    embed = EmbedBuilder.create_error_embed("❌ Phát hiện maid không thuộc sở hữu! Trade bị hủy.")
                    await ctx.send(embed=embed)
                    return
                    
            for maid in trade.user2_offer['maids']:
                cursor = await connection.execute(
                    'SELECT user_id FROM user_maids_v2 WHERE instance_id = ?', 
                    (maid['instance_id'],)
                )
                row = await cursor.fetchone()
                if not row or row[0] != trade.user2_id:
                    await connection.execute('ROLLBACK')
                    logger.warning(f"🚨 SECURITY: User {trade.user2_id} tried to trade maid {maid['instance_id']} they don't own!")
                    embed = EmbedBuilder.create_error_embed("❌ Phát hiện maid không thuộc sở hữu! Trade bị hủy.")
                    await ctx.send(embed=embed)
                    return
            
            # Transfer money (with validation)
            if trade.user1_offer['money'] > 0:
                cursor = await connection.execute('UPDATE users SET money = money - ? WHERE user_id = ? AND money >= ?',
                                                (trade.user1_offer['money'], trade.user1_id, trade.user1_offer['money']))
                if cursor.rowcount == 0:
                    await connection.execute('ROLLBACK')
                    embed = EmbedBuilder.create_error_embed("❌ User 1 không đủ tiền! Trade bị hủy.")
                    await ctx.send(embed=embed)
                    return
                await connection.execute('UPDATE users SET money = money + ? WHERE user_id = ?',
                                       (trade.user1_offer['money'], trade.user2_id))
            
            if trade.user2_offer['money'] > 0:
                cursor = await connection.execute('UPDATE users SET money = money - ? WHERE user_id = ? AND money >= ?',
                                                (trade.user2_offer['money'], trade.user2_id, trade.user2_offer['money']))
                if cursor.rowcount == 0:
                    await connection.execute('ROLLBACK')
                    embed = EmbedBuilder.create_error_embed("❌ User 2 không đủ tiền! Trade bị hủy.")
                    await ctx.send(embed=embed)
                    return
                await connection.execute('UPDATE users SET money = money + ? WHERE user_id = ?',
                                       (trade.user2_offer['money'], trade.user1_id))
            
            # Transfer stardust (with validation)
            if trade.user1_offer['stardust'] > 0:
                cursor = await connection.execute('UPDATE user_stardust_v2 SET stardust_amount = stardust_amount - ? WHERE user_id = ? AND stardust_amount >= ?',
                                                (trade.user1_offer['stardust'], trade.user1_id, trade.user1_offer['stardust']))
                if cursor.rowcount == 0:
                    await connection.execute('ROLLBACK')
                    embed = EmbedBuilder.create_error_embed("❌ User 1 không đủ stardust! Trade bị hủy.")
                    await ctx.send(embed=embed)
                    return
                await connection.execute('''INSERT OR REPLACE INTO user_stardust_v2 
                                           (user_id, stardust_amount, last_updated) 
                                           VALUES (?, COALESCE((SELECT stardust_amount FROM user_stardust_v2 WHERE user_id = ?), 0) + ?, ?)''',
                                       (trade.user2_id, trade.user2_id, trade.user1_offer['stardust'], datetime.now().isoformat()))
            
            if trade.user2_offer['stardust'] > 0:
                cursor = await connection.execute('UPDATE user_stardust_v2 SET stardust_amount = stardust_amount - ? WHERE user_id = ? AND stardust_amount >= ?',
                                                (trade.user2_offer['stardust'], trade.user2_id, trade.user2_offer['stardust']))
                if cursor.rowcount == 0:
                    await connection.execute('ROLLBACK')
                    embed = EmbedBuilder.create_error_embed("❌ User 2 không đủ stardust! Trade bị hủy.")
                    await ctx.send(embed=embed)
                    return
                await connection.execute('''INSERT OR REPLACE INTO user_stardust_v2 
                                           (user_id, stardust_amount, last_updated) 
                                           VALUES (?, COALESCE((SELECT stardust_amount FROM user_stardust_v2 WHERE user_id = ?), 0) + ?, ?)''',
                                       (trade.user1_id, trade.user1_id, trade.user2_offer['stardust'], datetime.now().isoformat()))
            
            # Transfer maids (validated ownership above)
            for maid in trade.user1_offer['maids']:
                cursor = await connection.execute('UPDATE user_maids_v2 SET user_id = ?, is_active = 0 WHERE instance_id = ? AND user_id = ?',
                                                (trade.user2_id, maid['instance_id'], trade.user1_id))
                if cursor.rowcount == 0:
                    await connection.execute('ROLLBACK')
                    logger.error(f"❌ Failed to transfer maid {maid['instance_id']} from user {trade.user1_id}")
                    embed = EmbedBuilder.create_error_embed("❌ Lỗi transfer maid! Trade bị hủy.")
                    await ctx.send(embed=embed)
                    return
            
            for maid in trade.user2_offer['maids']:
                cursor = await connection.execute('UPDATE user_maids_v2 SET user_id = ?, is_active = 0 WHERE instance_id = ? AND user_id = ?',
                                                (trade.user1_id, maid['instance_id'], trade.user2_id))
                if cursor.rowcount == 0:
                    await connection.execute('ROLLBACK')
                    logger.error(f"❌ Failed to transfer maid {maid['instance_id']} from user {trade.user2_id}")
                    embed = EmbedBuilder.create_error_embed("❌ Lỗi transfer maid! Trade bị hủy.")
                    await ctx.send(embed=embed)
                    return
            
            # Save trade history
            await connection.execute('''INSERT INTO trade_history 
                                       (trade_id, user1_id, user2_id, user1_offer, user2_offer, completed_at, channel_id)
                                       VALUES (?, ?, ?, ?, ?, ?, ?)''',
                                    (trade.trade_id, trade.user1_id, trade.user2_id,
                                     json.dumps(trade.user1_offer, default=str),
                                     json.dumps(trade.user2_offer, default=str),
                                     datetime.now().isoformat(), trade.channel_id))
            
            await connection.commit()
            
            # Xóa trade khỏi memory
            del self.active_trades[ctx.channel.id]
            
            # Thông báo thành công
            user1 = self.bot.get_user(trade.user1_id)
            user2 = self.bot.get_user(trade.user2_id)
            
            # Nếu get_user không có, thử fetch từ Discord API
            if not user1:
                try:
                    user1 = await self.bot.fetch_user(trade.user1_id)
                except:
                    user1 = None
                    
            if not user2:
                try:
                    user2 = await self.bot.fetch_user(trade.user2_id)
                except:
                    user2 = None
            
            # Ưu tiên username (global name) > display_name > fallback
            if user1:
                user1_name = user1.global_name or user1.display_name or user1.name
            else:
                user1_name = f"User {trade.user1_id}"
                
            if user2:
                user2_name = user2.global_name or user2.display_name or user2.name
            else:
                user2_name = f"User {trade.user2_id}"
            
            embed = discord.Embed(
                title="🎉 Trade Hoàn Thành!",
                description=f"Giao dịch giữa **{user1_name}** và **{user2_name}** đã thành công!",
                color=0x00FF00
            )
            
            embed.add_field(
                name=f"📦 {user1_name} nhận được:",
                value=self.format_offer(trade.user2_offer) or "*Không có gì*",
                inline=True
            )
            
            embed.add_field(
                name=f"📦 {user2_name} nhận được:",
                value=self.format_offer(trade.user1_offer) or "*Không có gì*",
                inline=True
            )
            
            embed.add_field(
                name="📝 Trade ID:",
                value=f"`{trade.trade_id}`",
                inline=False
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error executing trade: {e}")
            # 🛡️ SAFETY: Always rollback on any error
            try:
                await connection.execute('ROLLBACK')
            except:
                pass  # Connection might be closed
            embed = EmbedBuilder.create_error_embed(f"❌ Có lỗi xảy ra khi thực hiện trade! Trade đã được rollback.")
            await ctx.send(embed=embed)
            
            # Cleanup trade from memory on error
            if ctx.channel.id in self.active_trades:
                del self.active_trades[ctx.channel.id]
    
    @trade_group.command(name="cancel", description="❌ Hủy trade hiện tại")
    async def trade_cancel(self, ctx):
        """Hủy trade"""
        if ctx.channel.id not in self.active_trades:
            embed = EmbedBuilder.create_error_embed("❌ Không có giao dịch trade nào trong kênh này!")
            await ctx.send(embed=embed)
            return
        
        trade = self.active_trades[ctx.channel.id]
        
        if not trade.is_participant(ctx.author.id):
            embed = EmbedBuilder.create_error_embed("❌ Bạn không phải là người tham gia trade này!")
            await ctx.send(embed=embed)
            return
        
        del self.active_trades[ctx.channel.id]
        embed = EmbedBuilder.create_success_embed("Thành công", f"❌ **{ctx.author.display_name}** đã hủy trade `{trade.trade_id}`!")
        await ctx.send(embed=embed)
    
    @trade_group.command(name="status", description="📋 Xem trạng thái trade hiện tại")
    async def trade_status(self, ctx):
        """Xem trạng thái trade hiện tại"""
        if ctx.channel.id not in self.active_trades:
            embed = EmbedBuilder.create_error_embed("❌ Không có giao dịch trade nào trong kênh này!")
            await ctx.send(embed=embed)
            return
        
        trade = self.active_trades[ctx.channel.id]
        await self.send_trade_status(ctx, trade)

async def setup(bot):
    await bot.add_cog(MaidTrading(bot))