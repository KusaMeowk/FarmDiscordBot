"""
Admin Commands for Farm Bot
Các lệnh admin để điều khiển Gemini Game Master và các hệ thống khác
"""

import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
import config
from utils.embeds import EmbedBuilder
from utils.enhanced_logging import get_bot_logger
import json

logger = get_bot_logger()

class AdminCog(commands.Cog):
    """Admin commands cho Farm Bot"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.group(name='admin', invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def admin_group(self, ctx):
        """🔧 Nhóm lệnh admin cho Farm Bot
        
        Các lệnh admin có sẵn:
        • f!admin gemini - Điều khiển Gemini Game Master
        • f!admin weather - Điều khiển thời tiết
        • f!admin event - Điều khiển events
        • f!admin economy - Điều khiển kinh tế
        • f!admin stats - Thống kê hệ thống
        """
        embed = EmbedBuilder.create_base_embed(
            title="🔧 Admin Panel - Farm Bot",
            description=f"**Admin:** {ctx.author.mention}\n"
                       f"**Server:** {ctx.guild.name}\n"
                       f"**Thời gian:** {datetime.now().strftime('%H:%M:%S')}",
            color=0xFF0000
        )
        
        embed.add_field(
            name="🎮 Gemini Game Master",
            value="`f!admin gemini status` - Trạng thái AI\n"
                  "`f!admin gemini analyze` - Ép phân tích\n"
                  "`f!admin gemini emergency` - Chế độ khẩn cấp\n"
                  "`f!admin gemini toggle` - Bật/tắt AI",
            inline=True
        )
        
        embed.add_field(
            name="🌤️ Weather Control",
            value="`f!admin weather <type> [minutes]` - Thay đổi thời tiết\n"
                  "`f!admin weather list` - Xem danh sách\n"
                  "`f!admin weather current` - Thời tiết hiện tại",
            inline=True
        )
        
        embed.add_field(
            name="🎉 Event Control",
            value="`f!admin event <type> [minutes]` - Tạo event\n"
                  "`f!admin event list` - Xem danh sách\n"
                  "`f!admin event current` - Event hiện tại",
            inline=True
        )
        
        embed.add_field(
            name="💰 Economy Control",
            value="`f!admin economy addmoney` - Thêm tiền cho user\n"
                  "`f!admin economy setmoney` - Đặt tiền cho user\n"
                  "`f!admin economy checkmoney` - Kiểm tra tiền user",
            inline=True
        )
        
        embed.add_field(
            name="📊 System Stats",
            value="`f!admin stats users` - Thống kê users\n"
                  "`f!admin stats game` - Thống kê game\n"
                  "`f!admin stats performance` - Hiệu suất",
            inline=True
        )
        
        embed.add_field(
            name="⚡ Quick Actions",
            value="`f!afw <weather> [minutes]` - Admin weather change\n"
                  "`f!afe <event> [minutes]` - Admin force event\n"
                  "`f!addmoney @user <amount>` - Nhanh thêm tiền\n"
                  "`f!aanalyze` - Admin analysis\n"
                  "`f!aemergency` - Admin emergency mode",
            inline=True
        )
        
        embed.set_footer(text="⚠️ Chỉ admin mới có thể sử dụng các lệnh này")
        await ctx.send(embed=embed)
    
    # ==================== GEMINI GAME MASTER CONTROLS ====================
    
    @admin_group.group(name='gemini', invoke_without_command=True)
    async def gemini_admin(self, ctx):
        """🤖 Điều khiển Gemini Game Master"""
        embed = EmbedBuilder.create_base_embed(
            title="🤖 Gemini Game Master Controls",
            description="Điều khiển AI quản lý tự động game",
            color=0x9B59B6
        )
        
        embed.add_field(
            name="📊 Commands",
            value="`f!admin gemini status` - Trạng thái AI\n"
                  "`f!admin gemini analyze` - Force analysis\n"
                  "`f!admin gemini emergency` - Emergency mode\n"
                  "`f!admin gemini toggle` - Bật/tắt\n"
                  "`f!admin gemini history` - Lịch sử quyết định",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @gemini_admin.command(name='status')
    async def gemini_status(self, ctx):
        """📊 Xem trạng thái Gemini Game Master"""
        try:
            # Get Game Master cog
            gm_cog = self.bot.get_cog('GeminiGameMasterCog')
            if not gm_cog:
                await ctx.send("❌ Gemini Game Master không khả dụng!")
                return
            
            # Call the existing status command
            await gm_cog.status(ctx)
            
        except Exception as e:
            logger.error(f"Error in gemini status: {e}")
            await ctx.send(f"❌ Lỗi: {str(e)}")
    
    @gemini_admin.command(name='analyze')
    async def gemini_analyze(self, ctx):
        """🔍 Ép buộc Gemini phân tích ngay lập tức"""
        try:
            # Get Game Master cog
            gm_cog = self.bot.get_cog('GeminiGameMasterCog')
            if not gm_cog:
                await ctx.send("❌ Gemini Game Master không khả dụng!")
                return
            
            # Call the existing force_analysis command
            await gm_cog.force_analysis(ctx)
            
        except Exception as e:
            logger.error(f"Error in gemini analyze: {e}")
            await ctx.send(f"❌ Lỗi: {str(e)}")
    
    @gemini_admin.command(name='emergency')
    async def gemini_emergency(self, ctx):
        """🚨 Chuyển đổi chế độ khẩn cấp"""
        try:
            # Get Game Master cog
            gm_cog = self.bot.get_cog('GeminiGameMasterCog')
            if not gm_cog:
                await ctx.send("❌ Gemini Game Master không khả dụng!")
                return
            
            # Call the existing emergency_mode command
            await gm_cog.emergency_mode(ctx)
            
        except Exception as e:
            logger.error(f"Error in gemini emergency: {e}")
            await ctx.send(f"❌ Lỗi: {str(e)}")
    
    # ==================== WEATHER CONTROLS ====================
    
    @admin_group.group(name='weather', invoke_without_command=True)
    async def weather_admin(self, ctx, weather_type: str = None, duration: int = 60):
        """🌤️ Điều khiển thời tiết
        
        Sử dụng: f!admin weather <loại> [phút]
        """
        if not weather_type:
            await self.weather_list(ctx)
            return
            
        # Get Game Master cog and execute weather change
        gm_cog = self.bot.get_cog('GeminiGameMasterCog')
        if not gm_cog:
            await ctx.send("❌ Gemini Game Master không khả dụng!")
            return
        
        await gm_cog.force_weather(ctx, weather_type, duration)
    
    @weather_admin.command(name='list')
    async def weather_list(self, ctx):
        """📋 Danh sách loại thời tiết"""
        weather_types = [
            ("sunny", "☀️", "Nắng - Tăng tốc độ sinh trưởng"),
            ("rainy", "🌧️", "Mưa - Tăng sản lượng"), 
            ("cloudy", "☁️", "Có mây - Bình thường"),
            ("windy", "💨", "Có gió - Tăng sinh trưởng nhẹ"),
            ("storm", "⛈️", "Bão - Giảm hiệu suất"),
            ("foggy", "🌫️", "Sương mù - Giảm năng suất"),
            ("drought", "🔥", "Hạn hán - Giảm mạnh hiệu suất")
        ]
        
        embed = EmbedBuilder.create_base_embed(
            title="🌤️ Danh Sách Thời Tiết",
            description="**Sử dụng:** `f!admin weather <loại> [phút]`",
            color=0x87CEEB
        )
        
        weather_list = "\n".join([f"{emoji} **{wtype}** - {desc}" for wtype, emoji, desc in weather_types])
        embed.add_field(
            name="🌈 Các Loại Thời Tiết",
            value=weather_list,
            inline=False
        )
        
        embed.add_field(
            name="⏰ Thời Gian",
            value="• **Tối thiểu:** 15 phút\n• **Tối đa:** 360 phút (6 giờ)\n• **Mặc định:** 60 phút",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @weather_admin.command(name='current')
    async def weather_current(self, ctx):
        """🌡️ Xem thời tiết hiện tại"""
        try:
            weather_cog = self.bot.get_cog('WeatherCog')
            if not weather_cog:
                await ctx.send("❌ Weather system không khả dụng!")
                return
            
            # Get current weather info
            if hasattr(weather_cog, 'current_weather'):
                current = weather_cog.current_weather
                weather_type = current.get('type', 'unknown') if isinstance(current, dict) else current
                
                embed = EmbedBuilder.create_base_embed(
                    title="🌡️ Thời Tiết Hiện Tại",
                    description=f"**Loại:** {weather_type.title()}\n"
                               f"**Emoji:** {self._get_weather_emoji(weather_type)}",
                    color=0x87CEEB
                )
                
                await ctx.send(embed=embed)
            else:
                await ctx.send("❌ Không thể lấy thông tin thời tiết hiện tại!")
                
        except Exception as e:
            logger.error(f"Error getting current weather: {e}")
            await ctx.send(f"❌ Lỗi: {str(e)}")
    
    # ==================== EVENT CONTROLS ====================
    
    @admin_group.group(name='event', invoke_without_command=True)
    async def event_admin(self, ctx, event_type: str = None, duration: int = 120):
        """🎉 Điều khiển events
        
        Sử dụng: f!admin event <loại> [phút]
        """
        if not event_type:
            await self.event_list(ctx)
            return
            
        # Get Game Master cog and execute event creation
        gm_cog = self.bot.get_cog('GeminiGameMasterCog')
        if not gm_cog:
            await ctx.send("❌ Gemini Game Master không khả dụng!")
            return
        
        await gm_cog.force_event(ctx, event_type, duration)
    
    @event_admin.command(name='list')
    async def event_list(self, ctx):
        """📋 Danh sách loại event"""
        event_types = [
            ("harvest_bonus", "🌾", "Tăng 50% sản lượng thu hoạch"),
            ("double_exp", "⭐", "Tăng gấp đôi exp từ hoạt động"),
            ("market_boost", "💰", "Tăng 30% giá bán nông sản"),
            ("rain_blessing", "💧", "Tất cả cây tưới nước tự động"),
            ("golden_hour", "✨", "Tăng 25% tốc độ sinh trưởng"),
            ("lucky_day", "🍀", "Tăng chance drop item hiếm"),
            ("speed_growth", "⚡", "Tăng 40% tốc độ lớn"),
            ("mega_yield", "💎", "Tăng 100% sản lượng (hiếm)")
        ]
        
        embed = EmbedBuilder.create_base_embed(
            title="🎉 Danh Sách Event",
            description="**Sử dụng:** `f!admin event <loại> [phút]`",
            color=0xFF6B6B
        )
        
        event_list = "\n".join([f"{emoji} **{etype}** - {desc}" for etype, emoji, desc in event_types])
        embed.add_field(
            name="🎊 Các Loại Event",
            value=event_list,
            inline=False
        )
        
        embed.add_field(
            name="⏰ Thời Gian",
            value="• **Tối thiểu:** 30 phút\n• **Tối đa:** 720 phút (12 giờ)\n• **Mặc định:** 120 phút",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @event_admin.command(name='current')
    async def event_current(self, ctx):
        """🎪 Xem event hiện tại"""
        try:
            events_cog = self.bot.get_cog('EventsCog')
            if not events_cog:
                await ctx.send("❌ Events system không khả dụng!")
                return
            
            # Get current events info
            if hasattr(events_cog, 'get_active_events'):
                active_events = await events_cog.get_active_events()
                
                if active_events:
                    embed = EmbedBuilder.create_base_embed(
                        title="🎪 Event Hiện Tại",
                        description="Các event đang diễn ra:",
                        color=0xFF6B6B
                    )
                    
                    for event in active_events[:5]:  # Limit to 5 events
                        embed.add_field(
                            name=f"🎉 {event.get('name', 'Unknown Event')}",
                            value=f"**Loại:** {event.get('type', 'unknown')}\n"
                                  f"**Còn lại:** {event.get('time_remaining', 'N/A')}",
                            inline=True
                        )
                    
                    await ctx.send(embed=embed)
                else:
                    await ctx.send("ℹ️ Hiện tại không có event nào đang diễn ra.")
            else:
                await ctx.send("❌ Không thể lấy thông tin event hiện tại!")
                
        except Exception as e:
            logger.error(f"Error getting current events: {e}")
            await ctx.send(f"❌ Lỗi: {str(e)}")
    
    # ==================== ECONOMY CONTROLS ====================
    
    @admin_group.group(name='economy', invoke_without_command=True)
    async def economy_admin(self, ctx):
        """💰 Điều khiển kinh tế game"""
        embed = EmbedBuilder.create_base_embed(
            title="💰 Economy Controls",
            description="Điều khiển hệ thống kinh tế game",
            color=0xFFD700
        )
        
        embed.add_field(
            name="💸 Money Commands",
            value="`f!admin economy addmoney <@user> <amount>` - Thêm tiền cho user\n"
                  "`f!admin economy setmoney <@user> <amount>` - Đặt tiền cho user\n"
                  "`f!admin economy checkmoney <@user>` - Kiểm tra tiền của user",
            inline=False
        )
        
        embed.add_field(
            name="📊 Analysis Commands", 
            value="`f!admin economy inflation` - Kiểm tra lạm phát\n"
                  "`f!admin economy balance` - Cân bằng tiền tệ\n"
                  "`f!admin economy stats` - Thống kê kinh tế",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @economy_admin.command(name='addmoney')
    async def add_money(self, ctx, user_input: str = None, amount_str: str = None):
        """💰 Thêm tiền cho user
        
        Sử dụng: f!admin economy addmoney @user <số_tiền>
        Ví dụ: f!admin economy addmoney @Latina 10000
        Hỗ trợ: 1k = 1,000, 1m = 1,000,000
        """
        try:
            # Check if arguments provided
            if not user_input or not amount_str:
                embed = EmbedBuilder.create_base_embed(
                    title="💰 Add Money - Admin Command",
                    description=(
                        f"**Cách dùng:** `{config.PREFIX}admin economy addmoney @user <số_tiền>`\n"
                        f"**Ví dụ:** `{config.PREFIX}admin economy addmoney @Latina 10000`\n\n"
                        f"**Hỗ trợ format:**\n"
                        f"• `1000` = 1,000 coins\n"
                        f"• `1k` = 1,000 coins\n"
                        f"• `1m` = 1,000,000 coins\n"
                        f"• `2.5k` = 2,500 coins"
                    ),
                    color=0xFFD700
                )
                await ctx.send(embed=embed)
                return
            
            # Parse amount with k, m support
            amount = self._parse_amount(amount_str)
            if amount is None:
                await ctx.send("❌ **Số tiền không hợp lệ!** Ví dụ: `10000`, `5k`, `1.5m`")
                return
            
            if amount <= 0:
                await ctx.send("❌ **Số tiền phải lớn hơn 0!**")
                return
            
            # Find target user
            target_user = await self._find_user(ctx, user_input)
            if not target_user:
                await ctx.send(f"❌ **Không tìm thấy user** `{user_input}`!\n"
                             f"💡 Thử: `{config.PREFIX}admin economy addmoney @username 10000`")
                return
            
            if target_user.bot:
                await ctx.send("❌ **Không thể thêm tiền cho bot!**")
                return
            
            # Check if user is registered
            user = await self.bot.db.get_user(target_user.id)
            if not user:
                await ctx.send(f"❌ **{target_user.display_name} chưa đăng ký!**\n"
                             f"Họ cần dùng `{config.PREFIX}register` trước.")
                return
            
            # Get current money before update
            current_money = user.money
            
            # Add money to user
            new_balance = await self.bot.db.update_user_money(target_user.id, amount)
            
            # Create success embed
            embed = EmbedBuilder.create_base_embed(
                title="💰 Admin - Thêm Tiền Thành Công!",
                description=f"**Admin:** {ctx.author.mention}\n"
                           f"**Target:** {target_user.mention}",
                color=0x00FF00
            )
            
            embed.add_field(
                name="💸 Thông Tin Giao Dịch",
                value=f"**Số tiền thêm:** `+{amount:,}` coins\n"
                      f"**Số dư trước:** `{current_money:,}` coins\n"
                      f"**Số dư sau:** `{new_balance:,}` coins",
                inline=False
            )
            
            embed.add_field(
                name="📝 Chi Tiết",
                value=f"**Thời gian:** {datetime.now().strftime('%H:%M:%S %d/%m/%Y')}\n"
                      f"**User ID:** {target_user.id}",
                inline=False
            )
            
            embed.set_footer(text="⚠️ Lệnh chỉ dành cho Admin")
            
            await ctx.send(embed=embed)
            
            # Log the action
            logger.info(f"Admin {ctx.author.id} added {amount:,} coins to user {target_user.id}")
            
            # Send notification to target user if they're in the same server
            try:
                await target_user.send(
                    f"🎉 **Bạn nhận được {amount:,} coins từ admin {ctx.author.display_name}!**\n"
                    f"Số dư hiện tại: `{new_balance:,}` coins"
                )
            except:
                # If DM fails, it's okay - they'll see it in their profile
                pass
                
        except Exception as e:
            logger.error(f"Error in add_money command: {e}")
            await ctx.send(f"❌ **Lỗi:** {str(e)}")
    
    @economy_admin.command(name='setmoney')
    async def set_money(self, ctx, user_input: str = None, amount_str: str = None):
        """💰 Đặt số tiền cho user
        
        Sử dụng: f!admin economy setmoney @user <số_tiền>
        Ví dụ: f!admin economy setmoney @Latina 50000
        """
        try:
            if not user_input or not amount_str:
                embed = EmbedBuilder.create_base_embed(
                    title="💰 Set Money - Admin Command",
                    description=(
                        f"**Cách dùng:** `{config.PREFIX}admin economy setmoney @user <số_tiền>`\n"
                        f"**Ví dụ:** `{config.PREFIX}admin economy setmoney @Latina 50000`\n\n"
                        f"⚠️ **Lưu ý:** Lệnh này sẽ thay thế hoàn toàn số tiền hiện tại!"
                    ),
                    color=0xFF6B6B
                )
                await ctx.send(embed=embed)
                return
            
            # Parse amount
            amount = self._parse_amount(amount_str)
            if amount is None:
                await ctx.send("❌ **Số tiền không hợp lệ!**")
                return
            
            if amount < 0:
                await ctx.send("❌ **Số tiền không thể âm!**")
                return
            
            # Find target user
            target_user = await self._find_user(ctx, user_input)
            if not target_user:
                await ctx.send(f"❌ **Không tìm thấy user** `{user_input}`!")
                return
            
            if target_user.bot:
                await ctx.send("❌ **Không thể đặt tiền cho bot!**")
                return
            
            # Check if user is registered
            user = await self.bot.db.get_user(target_user.id)
            if not user:
                await ctx.send(f"❌ **{target_user.display_name} chưa đăng ký!**")
                return
            
            # Get current money
            current_money = user.money
            
            # Set new money amount
            user.money = amount
            await self.bot.db.update_user(user)
            
            # Create success embed
            embed = EmbedBuilder.create_base_embed(
                title="💰 Admin - Đặt Tiền Thành Công!",
                description=f"**Admin:** {ctx.author.mention}\n"
                           f"**Target:** {target_user.mention}",
                color=0xFF6B6B
            )
            
            embed.add_field(
                name="💸 Thông Tin Thay Đổi",
                value=f"**Số dư cũ:** `{current_money:,}` coins\n"
                      f"**Số dư mới:** `{amount:,}` coins\n"
                      f"**Thay đổi:** `{amount - current_money:+,}` coins",
                inline=False
            )
            
            await ctx.send(embed=embed)
            
            # Log the action  
            logger.info(f"Admin {ctx.author.id} set money for user {target_user.id} to {amount:,} coins")
            
        except Exception as e:
            logger.error(f"Error in set_money command: {e}")
            await ctx.send(f"❌ **Lỗi:** {str(e)}")
    
    @economy_admin.command(name='checkmoney')
    async def check_money(self, ctx, user_input: str = None):
        """💰 Kiểm tra tiền của user
        
        Sử dụng: f!admin economy checkmoney @user
        """
        try:
            if not user_input:
                await ctx.send("❌ **Cần chỉ định user!** Ví dụ: `f!admin economy checkmoney @Latina`")
                return
            
            # Find target user
            target_user = await self._find_user(ctx, user_input)
            if not target_user:
                await ctx.send(f"❌ **Không tìm thấy user** `{user_input}`!")
                return
            
            # Check if user is registered
            user = await self.bot.db.get_user(target_user.id)
            if not user:
                await ctx.send(f"❌ **{target_user.display_name} chưa đăng ký!**")
                return
            
            # Create info embed
            embed = EmbedBuilder.create_base_embed(
                title="💰 Thông Tin Tiền Tệ",
                description=f"**User:** {target_user.mention}",
                color=0x3498DB
            )
            
            embed.add_field(
                name="💵 Số Dư Hiện Tại",
                value=f"`{user.money:,}` coins",
                inline=False
            )
            
            embed.add_field(
                name="📊 Thông Tin Khác",
                value=f"**User ID:** {target_user.id}\n"
                      f"**Ngày tham gia:** {user.joined_date.strftime('%d/%m/%Y')}\n"
                      f"**Daily streak:** {user.daily_streak} ngày",
                inline=False
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in check_money command: {e}")
            await ctx.send(f"❌ **Lỗi:** {str(e)}")

    # ==================== HELPER METHODS ====================
    
    def _get_weather_emoji(self, weather_type: str) -> str:
        """Get emoji for weather type"""
        emojis = {
            "sunny": "☀️",
            "rainy": "🌧️", 
            "cloudy": "☁️",
            "windy": "💨",
            "storm": "⛈️",
            "foggy": "🌫️",
            "drought": "🔥"
        }
        return emojis.get(weather_type.lower(), "🌤️")
    
    def _parse_amount(self, amount_str: str) -> int:
        """Parse số tiền với hỗ trợ k, m"""
        try:
            amount_str = amount_str.lower().replace(',', '').replace('.', '')
            
            # Handle suffixes
            if amount_str.endswith('k'):
                amount = int(float(amount_str[:-1]) * 1000)
            elif amount_str.endswith('m'):
                amount = int(float(amount_str[:-1]) * 1000000)
            else:
                amount = int(amount_str)
            
            return amount if amount > 0 else None
                
        except (ValueError, TypeError):
            return None
    
    async def _find_user(self, ctx, user_input: str):
        """Tìm user theo mention, ID hoặc username"""
        try:
            # Try mention first
            if user_input.startswith('<@') and user_input.endswith('>'):
                user_id = int(user_input[2:-1].replace('!', ''))
                return ctx.bot.get_user(user_id) or await ctx.bot.fetch_user(user_id)
            
            # Try user ID
            if user_input.isdigit():
                user_id = int(user_input)
                return ctx.bot.get_user(user_id) or await ctx.bot.fetch_user(user_id)
            
            # Try username in guild
            for member in ctx.guild.members:
                if member.name.lower() == user_input.lower() or member.display_name.lower() == user_input.lower():
                    return member
            
            return None
            
        except (ValueError, discord.NotFound):
            return None

    # ==================== QUICK COMMANDS ====================
    
    @commands.command(name='afw', hidden=True)
    @commands.has_permissions(administrator=True)
    async def quick_weather(self, ctx, weather_type: str, duration: int = 60):
        """🌤️ Admin quick weather change"""
        await self.weather_admin(ctx, weather_type, duration)
    
    @commands.command(name='afe', hidden=True)
    @commands.has_permissions(administrator=True)
    async def quick_event(self, ctx, event_type: str, duration: int = 120):
        """🎉 Admin Force Event (quick event creation)"""
        await self.event_admin(ctx, event_type, duration)
    
    @commands.command(name='aanalyze', hidden=True)
    @commands.has_permissions(administrator=True)
    async def quick_analyze(self, ctx):
        """🔍 Admin Analysis (quick shortcut)"""
        await self.gemini_analyze(ctx)
    
    @commands.command(name='aemergency', hidden=True)
    @commands.has_permissions(administrator=True)
    async def quick_emergency(self, ctx):
        """🚨 Admin Emergency (shortcut for f!admin gemini emergency)"""
        gm_cog = self.bot.get_cog('GeminiGameMasterCog')
        if gm_cog:
            await gm_cog.emergency_mode(ctx)
    
    @commands.command(name='addmoney', hidden=True)
    @commands.has_permissions(administrator=True)
    async def quick_addmoney(self, ctx, user_input: str = None, amount_str: str = None):
        """💰 Quick shortcut cho f!admin economy addmoney"""
        await self.add_money(ctx, user_input, amount_str)

    @commands.command(name='maidreload', hidden=True)
    @commands.has_permissions(administrator=True)
    async def reload_maid(self, ctx):
        """🔄 Reload maid system V2"""
        try:
            # Unload if loaded
            if 'features.maid_system_v2' in self.bot.extensions:
                await self.bot.unload_extension('features.maid_system_v2')
                await ctx.send("🔄 Unloaded maid system...")
                
            # Load the extension
            await self.bot.load_extension('features.maid_system_v2')
            await ctx.send("✅ Maid system V2 reloaded thành công!")
            
        except Exception as e:
            await ctx.send(f"❌ Lỗi reload maid system: {str(e)}")
            import traceback
            traceback.print_exc()

    @commands.command(name='maidload', hidden=True)
    @commands.has_permissions(administrator=True)
    async def manual_load_maid(self, ctx):
        """🎎 Manual load maid system V2"""
        try:
            # Check if already loaded
            if 'features.maid_system_v2' in self.bot.extensions:
                await ctx.send("✅ Maid system đã được load rồi!")
                return
                
            # Try to load the extension
            await self.bot.load_extension('features.maid_system_v2')
            await ctx.send("✅ Maid system V2 loaded thành công!")
            
        except Exception as e:
            await ctx.send(f"❌ Lỗi load maid system: {str(e)}")
            import traceback
            traceback.print_exc()

    @app_commands.command(name="debug_maid_integration", description="🔧 Admin: Test maid integration với farm/shop")
    @app_commands.describe(user="User để test integration")
    async def debug_maid_integration(self, interaction: discord.Interaction, user: discord.Member = None):
        """
        [ADMIN] Command để test xem buff của maid có được áp dụng đúng vào
        hệ thống farm và shop không.
        """
        if not await self.is_admin(interaction.user.id):
            await interaction.response.send_message("❌ Không có quyền admin!", ephemeral=True)
            return
        
        target_user = user or interaction.user
        user_id = target_user.id
        
        from features.maid_helper import maid_helper
        from features.maid_display_integration import maid_display
        from features.maid_config import BUFF_TYPES
        import config
        
        embed = create_embed(
            title="🔧 Maid Integration Debug",
            description=f"Testing cho user: {target_user.display_name}",
            color=0x9932CC
        )
        
        # 1. Test maid active status
        active_maid_info = maid_helper.get_active_maid_info(user_id)
        if active_maid_info:
            embed.add_field(
                name="👑 Active Maid",
                value=f"{active_maid_info['emoji']} {active_maid_info['name']} ({active_maid_info['rarity']})",
                inline=True
            )
        else:
            embed.add_field(
                name="👑 Active Maid", 
                value="❌ Không có maid active",
                inline=True
            )
        
        # 2. Test buffs
        buffs = maid_helper.get_user_maid_buffs(user_id)
        buff_text = []
        for buff_type, value in buffs.items():
            if value > 0:
                emoji = BUFF_TYPES[buff_type]["emoji"]
                buff_text.append(f"{emoji} {buff_type}: +{value}%")
        
        embed.add_field(
            name="✨ Current Buffs",
            value="\n".join(buff_text) if buff_text else "Không có buffs",
            inline=False
        )
        
        # 3. Test integration với crops
        carrot_config = config.CROPS["carrot"]
        base_time = carrot_config["growth_time"]
        base_price = carrot_config["price"]
        base_yield = 2
        base_sell = carrot_config["sell_price"]
        
        # Apply buffs
        final_time = maid_helper.apply_growth_speed_buff(user_id, base_time)
        final_seed_price = maid_helper.apply_seed_discount_buff(user_id, base_price)
        final_yield = maid_helper.apply_yield_boost_buff(user_id, base_yield)
        final_sell_price = maid_helper.apply_sell_price_buff(user_id, base_sell)
        
        integration_text = [
            f"🌱 Growth: {base_time//60}m → {final_time//60}m",
            f"💰 Seed Cost: {base_price} → {final_seed_price} coins",
            f"📈 Yield: {base_yield} → {final_yield} crops",
            f"💎 Sell Price: {base_sell} → {final_sell_price} coins"
        ]
        
        embed.add_field(
            name="🧪 Integration Test (Carrot)",
            value="\n".join(integration_text),
            inline=False
        )
        
        # 4. Test display functions
        display_text = [
            f"Farm Footer: {maid_display.get_farm_embed_footer(user_id)}",
            f"Shop Footer: {maid_display.get_shop_embed_footer(user_id)}",
            f"Active Indicator: {maid_display.format_maid_active_indicator(user_id)}"
        ]
        
        embed.add_field(
            name="🎨 Display Functions",
            value="\n".join(display_text),
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @commands.command(name='testmanualbuff')
    @commands.is_owner()
    async def test_manual_buff(self, ctx):
        """Manual test buff parsing"""
        try:
            import sqlite3
            import json
            
            user_id = ctx.author.id
            
            # Manual database query - exactly like maid_helper
            conn = sqlite3.connect("farm_bot.db")
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT maid_id, buff_values 
                FROM user_maids_v2 
                WHERE user_id = ? AND is_active = 1
            """, (user_id,))
            
            result = cursor.fetchone()
            
            embed = EmbedBuilder.create_base_embed("🔧 Manual Buff Test", color=0xffa500)
            
            if not result:
                embed.add_field(name="❌ No Result", value="No active maid found", inline=False)
                conn.close()
                await ctx.send(embed=embed)
                return
            
            maid_id, buff_values_json = result
            
            embed.add_field(
                name="📋 Raw Query Result", 
                value=f"Maid ID: {maid_id}\nBuff JSON: ```{buff_values_json}```", 
                inline=False
            )
            
            # Test parsing
            buffs_result = {
                "growth_speed": 0.0,
                "seed_discount": 0.0,
                "yield_boost": 0.0,
                "sell_price": 0.0
            }
            
            parse_log = []
            
            if buff_values_json:
                try:
                    buff_list = json.loads(buff_values_json)
                    parse_log.append(f"✅ JSON parsed: {buff_list}")
                    
                    for i, buff_data in enumerate(buff_list):
                        parse_log.append(f"Processing buff {i}: {buff_data}")
                        
                        buff_type = buff_data.get('type') or buff_data.get('buff_type')
                        buff_value = buff_data.get('value', 0.0)
                        
                        parse_log.append(f"  Type: {buff_type}, Value: {buff_value}")
                        
                        if buff_type and buff_type in buffs_result:
                            buffs_result[buff_type] += buff_value
                            parse_log.append(f"  ✅ Applied {buff_type}: {buff_value}")
                        else:
                            parse_log.append(f"  ❌ Skipped {buff_type}: not in valid types")
                            
                except Exception as e:
                    parse_log.append(f"❌ Parse error: {e}")
            
            embed.add_field(
                name="🔍 Parse Log",
                value="```" + "\n".join(parse_log) + "```",
                inline=False
            )
            
            embed.add_field(
                name="📊 Final Buffs",
                value=f"```json\n{json.dumps(buffs_result, indent=2)}```",
                inline=False
            )
            
            # Test apply function
            test_price = 10
            if buffs_result["seed_discount"] > 0:
                discount = buffs_result["seed_discount"] / 100.0
                final_price = int(test_price * (1 - discount))
                embed.add_field(
                    name="💰 Test Apply",
                    value=f"Test price: {test_price} → {final_price} (-{buffs_result['seed_discount']}%)",
                    inline=False
                )
            
            conn.close()
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Error: {e}")
            import traceback
            await ctx.send(f"```{traceback.format_exc()}```")

    @commands.command(name='testmaidbuffs')
    @commands.is_owner()
    async def test_maid_buffs(self, ctx):
        """Test maid buffs functionality"""
        try:
            from features.maid_helper import maid_helper
            import config
            import sqlite3
            import json
            
            user_id = ctx.author.id
            
            embed = EmbedBuilder.create_base_embed("🧪 Test Maid Buffs", color=0xff69b4)
            
            # Add user info
            embed.add_field(
                name="👤 User Info",
                value=f"Discord ID: {user_id}\nUser: {ctx.author.mention}",
                inline=False
            )
            
            # Check V2 database directly
            try:
                conn = sqlite3.connect("farm_bot.db")
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT instance_id, maid_id, buff_values, is_active
                    FROM user_maids_v2 
                    WHERE user_id = ?
                """, (user_id,))
                
                all_maids = cursor.fetchall()
                
                if all_maids:
                    db_info = f"Total maids: {len(all_maids)}\n"
                    for maid in all_maids:
                        instance_id, maid_id, buff_values, is_active = maid
                        status = "🟢 ACTIVE" if is_active else "⚫ Inactive"
                        db_info += f"{status} {maid_id[:8]}...\n"
                        if is_active and buff_values:
                            buffs = json.loads(buff_values)
                            for buff in buffs:
                                # V2 uses 'type' instead of 'buff_type'
                                buff_type = buff.get('type') or buff.get('buff_type', 'unknown')
                                buff_value = buff.get('value', 0)
                                db_info += f"  • {buff_type}: +{buff_value}%\n"
                else:
                    db_info = "❌ No maids found in V2 database"
                
                embed.add_field(
                    name="🗄️ Database Check",
                    value=f"```\n{db_info}```",
                    inline=False
                )
                
                conn.close()
                
            except Exception as e:
                embed.add_field(
                    name="🗄️ Database Check",
                    value=f"❌ Error: {e}",
                    inline=False
                )
            
            # Test get buffs
            buffs = maid_helper.get_user_maid_buffs(user_id)
            
            embed.add_field(
                name="📊 Helper Buffs",
                value=f"```json\n{json.dumps(buffs, indent=2)}```" if buffs else "Không có buffs",
                inline=False
            )
            
            # Test seed price changes
            test_results = []
            for crop_id, crop_data in list(config.CROPS.items())[:4]:
                base_price = crop_data['price']
                final_price = maid_helper.apply_seed_discount_buff(user_id, base_price)
                discount = base_price - final_price
                discount_percent = (discount / base_price) * 100 if discount > 0 else 0
                
                test_results.append(
                    f"🌱 {crop_data['name']}: {base_price} -> {final_price} (-{discount_percent:.1f}%)"
                )
            
            embed.add_field(
                name="💰 Seed Price Tests",
                value="\n".join(test_results),
                inline=False
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Test error: {e}")
            import traceback
            await ctx.send(f"```\n{traceback.format_exc()}```")

    @commands.command(name='debugmaiddb')
    @commands.is_owner()
    async def debug_maid_db(self, ctx):
        """Debug raw database for maid buffs"""
        try:
            import sqlite3
            user_id = ctx.author.id
            
            conn = sqlite3.connect("farm_bot.db")
            cursor = conn.cursor()
            
            # Get raw data
            cursor.execute("""
                SELECT instance_id, maid_id, buff_values, is_active
                FROM user_maids_v2 
                WHERE user_id = ?
            """, (user_id,))
            
            results = cursor.fetchall()
            
            embed = EmbedBuilder.create_base_embed("🔍 Raw Maid Database", color=0x00ff00)
            
            if results:
                for i, (instance_id, maid_id, buff_values, is_active) in enumerate(results):
                    status = "🟢 ACTIVE" if is_active else "⚫ Inactive"
                    embed.add_field(
                        name=f"{status} Maid {i+1}",
                        value=f"**ID:** {maid_id}\n**Instance:** {instance_id[:8]}...\n**Raw Buffs:** ```{buff_values}```",
                        inline=False
                    )
            else:
                embed.add_field(
                    name="❌ No Data",
                    value="No maids found in user_maids_v2 table",
                    inline=False
                )
            
            conn.close()
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Error: {e}")
            import traceback
            await ctx.send(f"```{traceback.format_exc()}```")

    @commands.command(name='quicktest')
    @commands.is_owner()
    async def quick_test(self, ctx):
        """Quick test command"""
        await ctx.send("🤖 Bot is working!")
        
        # Test maid buffs quickly
        try:
            import sqlite3
            user_id = ctx.author.id
            
            conn = sqlite3.connect("farm_bot.db")
            cursor = conn.cursor()
            
            cursor.execute("SELECT maid_id, buff_values FROM user_maids_v2 WHERE user_id = ? AND is_active = 1", (user_id,))
            result = cursor.fetchone()
            
            if result:
                maid_id, buff_json = result
                await ctx.send(f"Found maid: {maid_id}\nBuffs: `{buff_json}`")
                
                # Try parse
                import json
                try:
                    buffs = json.loads(buff_json)
                    for buff in buffs:
                        buff_type = buff.get('type', 'unknown')
                        buff_value = buff.get('value', 0)
                        await ctx.send(f"Buff: {buff_type} = {buff_value}%")
                except Exception as e:
                    await ctx.send(f"Parse error: {e}")
            else:
                await ctx.send("No active maid found")
                
            conn.close()
            
        except Exception as e:
            await ctx.send(f"Error: {e}")

    @commands.command(name='reloadhelper')
    @commands.is_owner() 
    async def reload_helper(self, ctx):
        """Reload maid_helper module"""
        try:
            import importlib
            from features import maid_helper
            
            # Force reload
            importlib.reload(maid_helper)
            
            await ctx.send("✅ maid_helper reloaded!")
            
            # Test immediately
            user_id = ctx.author.id
            helper = maid_helper.maid_helper
            buffs = helper.get_user_maid_buffs(user_id)
            
            await ctx.send(f"📊 Buffs after reload: ```json\n{buffs}```")
            
            # Test seed discount
            if buffs.get("seed_discount", 0) > 0:
                test_price = 10
                final_price = helper.apply_seed_discount_buff(user_id, test_price)
                await ctx.send(f"💰 Test: {test_price} → {final_price} coins")
            
        except Exception as e:
            await ctx.send(f"❌ Reload error: {e}")

    @commands.command(name='debughelper')
    @commands.is_owner()
    async def debug_helper(self, ctx):
        """Debug maid_helper with error display"""
        try:
            from features.maid_helper import maid_helper
            user_id = ctx.author.id
            
            await ctx.send("🔍 Calling maid_helper.get_user_maid_buffs()...")
            
            # This should trigger the error and print to console
            buffs = maid_helper.get_user_maid_buffs(user_id)
            
            await ctx.send(f"📊 Result: ```json\n{buffs}```")
            
            # Try individual buff functions
            test_seed_price = 10
            discounted = maid_helper.apply_seed_discount_buff(user_id, test_seed_price)
            
            await ctx.send(f"💰 Seed discount test: {test_seed_price} → {discounted}")
            
        except Exception as e:
            await ctx.send(f"❌ Command error: {e}")
            import traceback
            await ctx.send(f"```{traceback.format_exc()}```")

    @commands.command(name='inlinetest')
    @commands.is_owner()
    async def inline_test(self, ctx):
        """Inline test - bypass maid_helper completely"""
        try:
            import sqlite3
            import json
            
            user_id = ctx.author.id
            
            # Direct implementation - exactly like maid_helper should do
            buffs = {
                "growth_speed": 0.0,
                "seed_discount": 0.0,
                "yield_boost": 0.0,
                "sell_price": 0.0
            }
            
            await ctx.send("🔍 Step 1: Connecting to database...")
            
            conn = sqlite3.connect("farm_bot.db")
            cursor = conn.cursor()
            
            await ctx.send("🔍 Step 2: Querying active maid...")
            
            cursor.execute("""
                SELECT maid_id, buff_values 
                FROM user_maids_v2 
                WHERE user_id = ? AND is_active = 1
            """, (user_id,))
            
            result = cursor.fetchone()
            
            if not result:
                await ctx.send("❌ No active maid found")
                conn.close()
                return
            
            maid_id, buff_values_json = result
            await ctx.send(f"✅ Found maid: {maid_id}")
            await ctx.send(f"📄 Raw JSON: `{buff_values_json}`")
            
            await ctx.send("🔍 Step 3: Parsing JSON...")
            
            if buff_values_json:
                try:
                    buff_list = json.loads(buff_values_json)
                    await ctx.send(f"✅ Parsed: `{buff_list}`")
                    
                    await ctx.send("🔍 Step 4: Processing buffs...")
                    
                    for i, buff_data in enumerate(buff_list):
                        await ctx.send(f"Processing buff {i}: `{buff_data}`")
                        
                        buff_type = buff_data.get('type') or buff_data.get('buff_type')
                        buff_value = float(buff_data.get('value', 0.0))
                        
                        await ctx.send(f"Type: `{buff_type}`, Value: `{buff_value}`")
                        await ctx.send(f"Valid types: `{list(buffs.keys())}`")
                        await ctx.send(f"In valid types? `{buff_type in buffs}`")
                        
                        if buff_type and buff_type in buffs:
                            old_value = buffs[buff_type]
                            buffs[buff_type] += buff_value
                            await ctx.send(f"✅ APPLIED: {buff_type}: {old_value} → {buffs[buff_type]}")
                        else:
                            await ctx.send(f"❌ SKIPPED: {buff_type}")
                            
                except Exception as e:
                    await ctx.send(f"❌ JSON Parse Error: {e}")
            
            await ctx.send(f"🔍 Step 5: Final result:")
            await ctx.send(f"```json\n{json.dumps(buffs, indent=2)}```")
            
            # Test apply
            if buffs["seed_discount"] > 0:
                test_price = 10
                discount = buffs["seed_discount"] / 100.0
                final_price = int(test_price * (1 - discount))
                await ctx.send(f"💰 Test apply: {test_price} → {final_price} (-{buffs['seed_discount']}%)")
            
            conn.close()
            
        except Exception as e:
            await ctx.send(f"❌ Error: {e}")
            import traceback
            await ctx.send(f"```{traceback.format_exc()}```")

    @commands.command(name='finaltest')
    async def final_test(self, ctx):
        """🔄 Force reload và test maid buffs ngay lập tức"""
        user_id = ctx.author.id
        
        # Force reload modules
        import importlib
        from features import maid_helper
        importlib.reload(maid_helper)
        
        # Import fresh instance
        helper = maid_helper.MaidBuffHelper()
        
        # Test buffs
        buffs = helper.get_user_maid_buffs(user_id)
        
        # Test seed discount application
        base_price = 10
        if buffs.get('seed_discount', 0) > 0:
            discount_price = helper.apply_seed_discount_buff(user_id, base_price)
            await ctx.send(f"✅ **THÀNH CÔNG!**\n🎀 Seed Discount: {buffs['seed_discount']}%\n💰 Giá: {base_price} → {discount_price}")
        else:
            await ctx.send(f"❌ **VẪN LỖI**: buffs = {buffs}")

    @commands.command(name='checksheryls')
    async def check_sheryl_buffs(self, ctx):
        """🔍 Kiểm tra buff của Sheryl maid"""
        user_id = ctx.author.id
        
        import sqlite3
        import json
        
        conn = sqlite3.connect("farm_bot.db")
        cursor = conn.cursor()
        
        # Get Sheryl maid info
        cursor.execute("""
            SELECT maid_id, buff_values 
            FROM user_maids_v2 
            WHERE user_id = ? AND is_active = 1
        """, (user_id,))
        
        result = cursor.fetchone()
        if not result:
            await ctx.send("❌ Không tìm thấy maid active!")
            conn.close()
            return
        
        maid_id, buff_values_json = result
        
        await ctx.send(f"**🎀 Sheryl Maid Info:**\n"
                      f"📋 Maid ID: `{maid_id}`\n"
                      f"🎯 Raw Buffs: `{buff_values_json}`")
        
        if buff_values_json:
            try:
                buff_list = json.loads(buff_values_json)
                
                buff_details = []
                has_sell_price = False
                
                for buff_data in buff_list:
                    buff_type = buff_data.get('type') or buff_data.get('buff_type')
                    buff_value = buff_data.get('value', 0.0)
                    buff_details.append(f"• {buff_type}: {buff_value}%")
                    
                    if buff_type == 'sell_price':
                        has_sell_price = True
                
                await ctx.send(f"**🔍 Parsed Buffs:**\n" + "\n".join(buff_details))
                
                if not has_sell_price:
                    await ctx.send("❌ **ISSUE FOUND**: Sheryl không có buff `sell_price`!\n"
                                  "✅ **GIẢI PHÁP**: Sheryl chỉ có buff tăng giá bán ở special tier, không phải basic buff")
                else:
                    await ctx.send("✅ Sheryl có sell_price buff!")
                    
            except Exception as e:
                await ctx.send(f"❌ Parse error: {e}")
        
        conn.close()

    @commands.command(name='testsellbuff')
    async def test_sell_buff(self, ctx):
        """🔍 Test sell_price buff trực tiếp"""
        user_id = ctx.author.id
        
        # Test sell price buff với wheat
        from features.maid_helper import maid_helper
        
        # Test 1: Get buffs
        buffs = maid_helper.get_user_maid_buffs(user_id)
        await ctx.send(f"**🎀 Maid Buffs:**\n`{buffs}`")
        
        # Test 2: Apply sell buff to wheat price
        wheat_base_price = 200  # From config
        buffed_price = maid_helper.apply_sell_price_buff(user_id, wheat_base_price)
        
        await ctx.send(f"**💰 Sell Price Test:**\n"
                      f"🌾 Wheat base: {wheat_base_price} coins\n"
                      f"🎀 With Sheryl buff: {buffed_price} coins\n"
                      f"📈 Difference: +{buffed_price - wheat_base_price} coins ({((buffed_price/wheat_base_price - 1) * 100):.1f}%)")
        
        # Test 3: Check if sell command imports properly
        try:
            from utils.pricing import pricing_coordinator
            final_price, modifiers = pricing_coordinator.calculate_final_price('wheat', ctx.bot)
            
            await ctx.send(f"**🔍 Pricing System:**\n"
                          f"💵 Final price: {final_price} coins\n"
                          f"📊 Modifiers: `{modifiers}`\n"
                          f"⚠️ **NOTE**: Sell command should apply maid buff AFTER this price!")
            
        except Exception as e:
            await ctx.send(f"❌ Pricing error: {e}")

    @commands.command(name='testyieldbuff')
    async def test_yield_buff(self, ctx):
        """🔍 Test yield boost buff của Sheryl"""
        user_id = ctx.author.id
        
        from features.maid_helper import maid_helper
        
        # Test 1: Check buffs
        buffs = maid_helper.get_user_maid_buffs(user_id)
        await ctx.send(f"**🎀 Maid Buffs:**\n`{buffs}`")
        
        # Test 2: Apply yield buff
        base_yield = 3  # Example base yield
        buffed_yield = maid_helper.apply_yield_boost_buff(user_id, base_yield)
        
        await ctx.send(f"**📈 Yield Boost Test:**\n"
                      f"🌾 Base yield: {base_yield} items\n"
                      f"🎀 With Sheryl buff: {buffed_yield} items\n"
                      f"📈 Difference: +{buffed_yield - base_yield} items")
        
        # Test 3: Check if Sheryl has yield_boost
        yield_boost = buffs.get('yield_boost', 0.0)
        if yield_boost > 0:
            await ctx.send(f"✅ **Sheryl có yield_boost**: {yield_boost}%")
        else:
            await ctx.send(f"❌ **Sheryl KHÔNG có yield_boost buff!**\n"
                          f"🔍 **Lý do**: Sheryl (rarity R) chỉ có `sell_price` buff\n"
                          f"💡 **Cần**: Maid có `yield_boost` buff như Zero Two, Mitsuri, Venus, v.v.")

    @commands.group(name="banner", description="🌟 Quản lý Multi-Banner System")
    @commands.has_permissions(administrator=True)
    async def banner(self, ctx):
        """Group command cho Multi-Banner management"""
        if ctx.invoked_subcommand is None:
            embed = EmbedBuilder.create_base_embed(
                title="🌟 Multi-Banner Admin Commands",
                description="Quản lý hệ thống Multi-Banner",
                color=0xFF4500
            )
            
            embed.add_field(
                name="🎯 Banner Commands",
                value="`f!banner set <banner_id>` - Set banner active\n"
                      "`f!banner disable` - Tắt banner\n"
                      "`f!banner list` - Danh sách banners",
                inline=False
            )
            
            embed.add_field(
                name="ℹ️ Information Commands",
                value="`f!banner status` - Xem trạng thái\n"
                      "`f!banner config` - Xem cấu hình\n"
                      "`f!banner info <banner_id>` - Chi tiết banner",
                inline=False
            )
            
            embed.add_field(
                name="🎪 Available Banners",
                value="• **jalter** - Dragon Witch Festival 🔥\n"
                      "• **kotori** - Spirit Sister Festival 🍡",
                inline=False
            )
            
            embed.set_footer(text="⚠️ Chỉ admin mới có thể sử dụng")
            await ctx.send(embed=embed)
    
    @banner.command(name="set", description="🎯 Set banner active")
    @commands.has_permissions(administrator=True)
    async def banner_set(self, ctx, banner_id: str = None):
        """Set banner active theo ID"""
        if not banner_id:
            embed = EmbedBuilder.create_base_embed(
                title="❌ Thiếu Banner ID",
                description="Vui lòng chỉ định banner_id để set active.\n\n"
                           "**Available banners:**\n"
                           "• `jalter` - Dragon Witch Festival 🔥\n"
                           "• `kotori` - Spirit Sister Festival 🍡\n\n"
                           "**Sử dụng:** `f!banner set <banner_id>`",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            return
        
        try:
            from features.maid_config_backup import (
                set_active_banner, get_banner_info, 
                BANNER_CONFIGS, get_current_banner
            )
            
            # Validate banner ID
            if banner_id not in BANNER_CONFIGS:
                embed = EmbedBuilder.create_base_embed(
                    title="❌ Banner ID không hợp lệ",
                    description=f"Banner `{banner_id}` không tồn tại.\n\n"
                               "**Available banners:**\n"
                               "• `jalter` - Dragon Witch Festival 🔥\n"
                               "• `kotori` - Spirit Sister Festival 🍡",
                    color=0xFF0000
                )
                await ctx.send(embed=embed)
                return
            
            # Check if already active
            current_banner = get_current_banner()
            if current_banner == banner_id and get_banner_info(banner_id)["enabled"]:
                embed = EmbedBuilder.create_base_embed(
                    title="⚠️ Banner đã được set",
                    description=f"Banner `{banner_id}` đã đang active!",
                    color=0xFFFF00
                )
                await ctx.send(embed=embed)
                return
            
            # Set banner active
            success = set_active_banner(banner_id)
            if not success:
                embed = EmbedBuilder.create_base_embed(
                    title="❌ Lỗi khi set banner",
                    description="Không thể set banner active. Vui lòng thử lại.",
                    color=0xFF0000
                )
                await ctx.send(embed=embed)
                return
            
            # Get banner info và create success embed
            banner_info = get_banner_info(banner_id)
            embed = EmbedBuilder.create_base_embed(
                title=f"🟢 {banner_info['banner_name']} Active!",
                description=f"{banner_info['description']}",
                color=banner_info['background_color']
            )
            
            embed.add_field(
                name="🎮 Commands available",
                value="`f!2mg` - Single roll (12,000 coins)\n"
                      "`f!2mg10` - 10-roll (108,000 coins)\n"
                      "`f!2mbanner` - Xem thông tin banner",
                inline=False
            )
            
            embed.add_field(
                name=f"⭐ Featured Character",
                value=f"{banner_info['featured_emoji']} **{banner_info['featured_name']}** (GHOST RARE)",
                inline=True
            )
            
            embed.add_field(
                name="📊 Rate Boost",
                value="GR: 0% → 0.05% (NEW!)\nUR: 0.1% → 0.15%\nSSR: 5.9% → 7.9%",
                inline=True
            )
            
            embed.set_footer(text=f"Banner {banner_id} đã được set active!")
            await ctx.send(embed=embed)
            
        except Exception as e:
            embed = EmbedBuilder.create_base_embed(
                title="❌ Lỗi khi set banner",
                description=f"Đã xảy ra lỗi: {str(e)}",
                color=0xFF0000
            )
            await ctx.send(embed=embed)

    @banner.command(name="enable", description="🟢 Bật Limited Banner (DEPRECATED)")
    @commands.has_permissions(administrator=True)
    async def banner_enable(self, ctx):
        """Bật Limited Banner Event"""
        try:
            # Import limited banner config
            from features.maid_config_backup import LIMITED_BANNER_CONFIG
            
            if LIMITED_BANNER_CONFIG["enabled"]:
                embed = EmbedBuilder.create_base_embed(
                    title="⚠️ Limited Banner đã được bật",
                    description="Limited Banner hiện đang hoạt động!",
                    color=0xFFFF00
                )
                await ctx.send(embed=embed)
                return
            
            # Enable banner
            LIMITED_BANNER_CONFIG["enabled"] = True
            LIMITED_BANNER_CONFIG["start_time"] = datetime.now().isoformat()
            # Banner sẽ chạy vô thời hạn cho đến khi admin disable
            
            embed = EmbedBuilder.create_base_embed(
                title="🟢 Limited Banner đã được bật!",
                description=f"**{LIMITED_BANNER_CONFIG['banner_name']}**\n{LIMITED_BANNER_CONFIG['banner_description']}",
                color=0x00FF00
            )
            
            embed.add_field(
                name="🎮 Commands có sẵn",
                value="`f!2mg` - Single roll (12,000 coins)\n"
                      "`f!2mg10` - 10-roll (108,000 coins)\n"
                      "`f!2mbanner` - Xem thông tin banner",
                inline=False
            )
            
            embed.add_field(
                name="⭐ Featured Characters",
                value="👻 Jeanne d'Arc Alter (GHOST RARE)",
                inline=True
            )
            
            embed.add_field(
                name="📊 Rate Boost",
                value="GR: 0% → 0.05% (NEW!)\nUR: 0.1% → 0.15%\nSSR: 5.9% → 7.9%",
                inline=True
            )
            
            embed.set_footer(text="Limited Banner Event đã bắt đầu!")
            await ctx.send(embed=embed)
            
        except Exception as e:
            embed = EmbedBuilder.create_base_embed(
                title="❌ Lỗi khi bật Limited Banner",
                description=f"Đã xảy ra lỗi: {str(e)}",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
    
    @banner.command(name="disable", description="🔴 Tắt Banner")
    @commands.has_permissions(administrator=True)
    async def banner_disable(self, ctx):
        """Tắt Multi-Banner Event"""
        try:
            from features.maid_config_backup import (
                disable_active_banner, get_current_banner, 
                get_banner_info, ACTIVE_BANNER_CONFIG
            )
            
            if not ACTIVE_BANNER_CONFIG["enabled"]:
                embed = EmbedBuilder.create_base_embed(
                    title="⚠️ Banner đã được tắt",
                    description="Hiện không có banner nào đang hoạt động!",
                    color=0xFFFF00
                )
                await ctx.send(embed=embed)
                return
            
            # Get current banner info trước khi disable
            current_banner = get_current_banner()
            banner_info = get_banner_info(current_banner)
            
            # Disable banner
            success = disable_active_banner()
            if not success:
                embed = EmbedBuilder.create_base_embed(
                    title="❌ Lỗi khi tắt banner",
                    description="Không thể tắt banner. Vui lòng thử lại.",
                    color=0xFF0000
                )
                await ctx.send(embed=embed)
                return
            
            embed = EmbedBuilder.create_base_embed(
                title="🔴 Banner đã được tắt!",
                description=f"**{banner_info['banner_name']}** đã kết thúc.",
                color=0xFF0000
            )
            
            embed.add_field(
                name="ℹ️ Thông báo",
                value="• Commands `f!2mg` và `f!2mg10` sẽ không hoạt động\n"
                      "• GR characters chỉ có thể có được khi banner active\n"
                      "• Maids đã có vẫn được giữ nguyên",
                inline=False
            )
            
            embed.add_field(
                name="🎯 Để bật lại",
                value="Sử dụng `f!banner set <banner_id>` để bật banner khác",
                inline=False
            )
            
            embed.set_footer(text="Multi-Banner System đã được tắt!")
            await ctx.send(embed=embed)
            
        except Exception as e:
            embed = EmbedBuilder.create_base_embed(
                title="❌ Lỗi khi tắt banner",
                description=f"Đã xảy ra lỗi: {str(e)}",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
    
    @banner.command(name="list", description="📋 Danh sách banners")
    @commands.has_permissions(administrator=True)
    async def banner_list(self, ctx):
        """Hiển thị danh sách tất cả banners"""
        try:
            from features.maid_config_backup import get_all_banner_list, get_current_banner, ACTIVE_BANNER_CONFIG
            
            banners = get_all_banner_list()
            current_banner = get_current_banner()
            
            embed = EmbedBuilder.create_base_embed(
                title="📋 Danh Sách Multi-Banner",
                description="Tất cả banners có sẵn trong hệ thống",
                color=0x9B59B6
            )
            
            for banner in banners:
                status = "🟢 **ACTIVE**" if (banner["enabled"] and banner["banner_id"] == current_banner) else "🔴 Inactive"
                
                embed.add_field(
                    name=f"{banner['theme_emoji']} {banner['banner_name']}",
                    value=f"**ID:** `{banner['banner_id']}`\n"
                          f"**Status:** {status}\n"
                          f"**Featured:** {banner['featured_emoji']} {banner['featured_name']}\n"
                          f"**Cost:** {banner['single_cost']:,} / {banner['ten_cost']:,}",
                    inline=True
                )
            
            embed.add_field(
                name="🎯 Cách sử dụng",
                value=f"• `f!banner set <banner_id>` - Set banner active\n"
                      f"• `f!banner info <banner_id>` - Chi tiết banner\n"
                      f"• `f!banner disable` - Tắt banner",
                inline=False
            )
            
            embed.set_footer(text=f"Hiện tại: {ACTIVE_BANNER_CONFIG['enabled'] and 'Active' or 'Disabled'}")
            await ctx.send(embed=embed)
            
        except Exception as e:
            embed = EmbedBuilder.create_base_embed(
                title="❌ Lỗi khi lấy danh sách",
                description=f"Đã xảy ra lỗi: {str(e)}",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
    
    @banner.command(name="info", description="ℹ️ Chi tiết banner")
    @commands.has_permissions(administrator=True)
    async def banner_info(self, ctx, banner_id: str = None):
        """Xem chi tiết banner theo ID"""
        if not banner_id:
            embed = EmbedBuilder.create_base_embed(
                title="❌ Thiếu Banner ID",
                description="Vui lòng chỉ định banner_id.\n\n"
                           "**Available banners:**\n"
                           "• `jalter` - Dragon Witch Festival 🔥\n"
                           "• `kotori` - Spirit Sister Festival 🍡\n\n"
                           "**Sử dụng:** `f!banner info <banner_id>`",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            return
        
        try:
            from features.maid_config_backup import get_banner_info, BANNER_CONFIGS
            
            if banner_id not in BANNER_CONFIGS:
                embed = EmbedBuilder.create_base_embed(
                    title="❌ Banner không tồn tại",
                    description=f"Banner `{banner_id}` không tồn tại.",
                    color=0xFF0000
                )
                await ctx.send(embed=embed)
                return
            
            banner_info = get_banner_info(banner_id)
            status = "🟢 **ACTIVE**" if banner_info["enabled"] else "🔴 **INACTIVE**"
            
            embed = EmbedBuilder.create_base_embed(
                title=f"{banner_info['theme_emoji']} {banner_info['banner_name']}",
                description=f"{banner_info['description']}\n\n**Status:** {status}",
                color=banner_info['background_color']
            )
            
            embed.add_field(
                name="⭐ Featured Character",
                value=f"{banner_info['featured_emoji']} **{banner_info['featured_name']}**\n"
                      f"Rarity: **GHOST RARE (GR)**\n"
                      f"Rate: **0.05%** (exclusive trong banner)",
                inline=True
            )
            
            embed.add_field(
                name="💰 Pricing",
                value=f"Single Roll: **{banner_info['single_cost']:,}** coins\n"
                      f"10-Roll: **{banner_info['ten_cost']:,}** coins\n"
                      f"Discount: **10%** cho 10-roll",
                inline=True
            )
            
            embed.add_field(
                name="📊 Rate Boosts",
                value="**GR:** 0% → 0.05% (NEW!)\n"
                      "**UR:** 0.1% → 0.15%\n"
                      "**SSR:** 5.9% → 7.9%\n"
                      "**SR:** 24% → 22.1%\n"
                      "**R:** 70% → 69.8%",
                inline=False
            )
            
            embed.add_field(
                name="🎯 Commands",
                value=f"`f!banner set {banner_id}` - Set banner này active\n"
                      f"`f!2mg` - Roll khi banner active\n"
                      f"`f!2mg10` - 10-roll khi banner active",
                inline=False
            )
            
            embed.set_footer(text=f"Banner ID: {banner_id}")
            await ctx.send(embed=embed)
            
        except Exception as e:
            embed = EmbedBuilder.create_base_embed(
                title="❌ Lỗi khi lấy thông tin",
                description=f"Đã xảy ra lỗi: {str(e)}",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
    
    @banner.command(name="status", description="ℹ️ Xem trạng thái Banner System")
    @commands.has_permissions(administrator=True)
    async def banner_status(self, ctx):
        """Xem trạng thái Limited Banner"""
        try:
            from features.maid_config_backup import LIMITED_BANNER_CONFIG, get_featured_characters, MAID_TEMPLATES
            
            status = "🟢 **ACTIVE**" if LIMITED_BANNER_CONFIG["enabled"] else "🔴 **INACTIVE**"
            color = 0x00FF00 if LIMITED_BANNER_CONFIG["enabled"] else 0xFF0000
            
            embed = EmbedBuilder.create_base_embed(
                title="🌟 Limited Banner Status",
                description=f"Trạng thái: {status}",
                color=color
            )
            
            embed.add_field(
                name="📝 Banner Info",
                value=f"**Tên**: {LIMITED_BANNER_CONFIG['banner_name']}\n"
                      f"**Mô tả**: {LIMITED_BANNER_CONFIG['banner_description']}",
                inline=False
            )
            
            # Featured characters
            featured_chars = get_featured_characters()
            if featured_chars:
                featured_list = []
                for maid_id in featured_chars:
                    template = MAID_TEMPLATES[maid_id]
                    limited_badge = " (LIMITED)" if template.get("limited_only", False) else ""
                    featured_list.append(f"• {template['emoji']} {template['name']}{limited_badge}")
                
                embed.add_field(
                    name="⭐ Featured Characters",
                    value="\n".join(featured_list),
                    inline=True
                )
            
            # Costs và rates
            embed.add_field(
                name="💰 Pricing",
                value=f"Single: {LIMITED_BANNER_CONFIG['single_roll_cost']:,}\n"
                      f"10-roll: {LIMITED_BANNER_CONFIG['ten_roll_cost']:,}",
                inline=True
            )
            
            # Timing
            timing_text = ""
            if LIMITED_BANNER_CONFIG["start_time"]:
                timing_text += f"**Started**: {LIMITED_BANNER_CONFIG['start_time'][:19]}\n"
            if LIMITED_BANNER_CONFIG["end_time"]:
                timing_text += f"**Ended**: {LIMITED_BANNER_CONFIG['end_time'][:19]}\n"
            
            if timing_text:
                embed.add_field(name="🕐 Timing", value=timing_text, inline=False)
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            embed = EmbedBuilder.create_base_embed(
                title="❌ Lỗi khi xem status",
                description=f"Đã xảy ra lỗi: {str(e)}",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
    
    @banner.command(name="config", description="⚙️ Xem cấu hình Limited Banner")
    @commands.has_permissions(administrator=True)
    async def banner_config(self, ctx):
        """Xem cấu hình chi tiết Limited Banner"""
        try:
            from features.maid_config_backup import LIMITED_BANNER_CONFIG, LIMITED_RARITY_CONFIG
            
            embed = EmbedBuilder.create_base_embed(
                title="⚙️ Limited Banner Configuration",
                description="Cấu hình chi tiết hệ thống Limited Banner",
                color=0x0099FF
            )
            
            # Banner settings
            embed.add_field(
                name="🌟 Banner Settings",
                value=f"**Enabled**: {LIMITED_BANNER_CONFIG['enabled']}\n"
                      f"**Name**: {LIMITED_BANNER_CONFIG['banner_name']}\n"
                      f"**Single Cost**: {LIMITED_BANNER_CONFIG['single_roll_cost']:,}\n"
                      f"**10-roll Cost**: {LIMITED_BANNER_CONFIG['ten_roll_cost']:,}",
                inline=False
            )
            
            # Rate configuration
            rate_text = ""
            for rarity, config in LIMITED_RARITY_CONFIG.items():
                rate_text += f"**{rarity}**: {config['total_rate']}%"
                if config['featured_rate'] > 0:
                    rate_text += f" (Featured: {config['featured_rate']}%)"
                rate_text += "\n"
            
            embed.add_field(
                name="📊 Rates",
                value=rate_text,
                inline=True
            )
            
            # Comparison with regular gacha
            embed.add_field(
                name="🔄 vs Regular Gacha",
                value="**GR**: 0% → 0.05% (NEW!)\n"
                      "**UR**: 0.1% → 0.15% (+50%)\n"
                      "**SSR**: 5.9% → 7.9% (+33%)\n"
                      "**SR**: 24% → 22.1% (-8%)\n"
                      "**R**: 70% → 69.8% (-0.2%)",
                inline=True
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            embed = EmbedBuilder.create_base_embed(
                title="❌ Lỗi khi xem config",
                description=f"Đã xảy ra lỗi: {str(e)}",
                color=0xFF0000
            )
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(AdminCog(bot)) 