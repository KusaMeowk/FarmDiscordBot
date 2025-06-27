#!/usr/bin/env python3
"""
Gemini Economic Cog - Tích hợp Gemini Manager vào Discord bot
"""

import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
import json
import asyncio
from typing import Optional, Dict, List
from utils.embeds import EmbedBuilder
from utils.enhanced_logging import get_bot_logger
from utils.task_cleanup import TaskCleanupManager

# Optional imports with fallbacks
try:
    from ai.gemini_manager_v2 import GeminiEconomicManagerV2, GeminiDecision
    GEMINI_MANAGER_AVAILABLE = True
except ImportError:
    GEMINI_MANAGER_AVAILABLE = False
    # Fallback stub
    class GeminiEconomicManagerV2:
        def __init__(self, **kwargs):
            pass
        async def initialize(self):
            pass
        async def analyze_and_decide(self, bot):
            return None
    
    class GeminiDecision:
        def __init__(self):
            self.action_type = "NO_ACTION"

logger = get_bot_logger()

class GeminiEconomicCog(commands.Cog):
    """
    Gemini Economic Management Cog
    Thay thế AI local bằng Gemini để cân bằng kinh tế game
    """
    
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
        
        # Check dependencies
        if not GEMINI_MANAGER_AVAILABLE:
            logger.warning("⚠️ Gemini Manager not available - missing dependencies")
            logger.warning("   Run: pip install aiofiles google-generativeai")
        
        # Gemini Manager
        self.gemini_manager = GeminiEconomicManagerV2(database=bot.db)
        
        # State tracking - disabled by default if dependencies missing
        self.enabled = GEMINI_MANAGER_AVAILABLE
        self.last_analysis_time = None
        self.analysis_interval_hours = 1
        self.decision_history = []
        
        # Notification settings
        self.notification_channels = {}  # guild_id -> channel_id
        
        # Schedule initialization if dependencies available
        if GEMINI_MANAGER_AVAILABLE:
            # Auto-enable Gemini after bot startup
            self.enabled = True  # Auto-enable by default
            asyncio.create_task(self._initialize_gemini())
        else:
            logger.info("🔒 Gemini Economic Cog loaded but disabled (missing dependencies)")
        
    async def _initialize_gemini(self):
        """Khởi tạo Gemini Manager"""
        try:
            await self.gemini_manager.initialize()
            logger.info("🤖 Latina Economic Cog initialized")
            
            # Auto-start analysis task after bot is ready
            if self.enabled and not self.gemini_analysis_task.is_running():
                await self.bot.wait_until_ready()  # Wait for bot to be ready
                self.gemini_analysis_task.start()
                logger.info("🚀 Latina Economic Analysis auto-started!")
                
                # Send startup notification to setup channels
                await self._send_startup_notification()
            
        except Exception as e:
            logger.error(f"Error initializing Gemini Manager: {e}")
    
    async def _send_startup_notification(self):
        """Gửi thông báo Gemini đã khởi động"""
        try:
            # Delay ngắn để đảm bảo tất cả guild đã load
            await asyncio.sleep(2)  # Giảm delay để Latina gửi đầu tiên
            
            embed = EmbedBuilder.create_base_embed(
                title="🎀 Latina AI Economic Manager đã thức dậy!",
                description="Xin chào mọi người! Mình là **Latina**, trợ lý AI kinh tế của trang trại. Mình đã sẵn sàng quản lý kinh tế game rồi nhé! 💖",
                color=0xff69b4
            )
            
            embed.add_field(
                name="🌸 Latina sẽ tự động giúp các bạn:",
                value="• 📊 Phân tích kinh tế game mỗi giờ\n"
                      "• 🌤️ Thay đổi thời tiết khi cần thiết\n"
                      "• 🎉 Tạo sự kiện vui vẻ để cân bằng\n"
                      "• 💰 Điều chỉnh giá cả thị trường hợp lý",
                inline=False
            )
            
            embed.add_field(
                name="💝 Lệnh để tương tác với Latina:",
                value="`f!gemini status` - Xem tình trạng của mình\n"
                      "`f!gemini toggle` - Bật/tắt hoạt động\n"
                      "`f!gemini setup` - Setup thông báo cute",
                inline=False
            )
            
            embed.set_footer(text="Latina sẽ bắt đầu làm việc trong vài phút nữa... ✨ • Hôm nay lúc 8:29 SA")
            
            # Gửi tới tất cả guild với channel đầu tiên available
            for guild in self.bot.guilds:
                try:
                    # Tìm channel đầu tiên có thể gửi
                    target_channel = None
                    
                    # Thử general, announcement, hoặc channel đầu tiên
                    for channel in guild.text_channels:
                        if channel.permissions_for(guild.me).send_messages:
                            if any(name in channel.name.lower() for name in ['general', 'announce', 'bot', 'notification']):
                                target_channel = channel
                                break
                    
                    # Nếu không tìm thấy, dùng channel đầu tiên có permission
                    if not target_channel:
                        for channel in guild.text_channels:
                            if channel.permissions_for(guild.me).send_messages:
                                target_channel = channel
                                break
                    
                    if target_channel:
                        await target_channel.send(embed=embed)
                        logger.info(f"📢 Gemini startup notification sent to {guild.name} #{target_channel.name}")
                        
                        # Delay giữa các guild để tránh rate limit
                        await asyncio.sleep(1)
                        
                except Exception as e:
                    logger.warning(f"Could not send startup notification to guild {guild.name}: {e}")
                    
        except Exception as e:
            logger.error(f"Error sending startup notification: {e}")
    
    def cog_unload(self):
        """Cleanup khi unload cog"""
        try:
            # Stop task trước khi cleanup
            if hasattr(self, 'gemini_analysis_task') and self.gemini_analysis_task:
                if self.gemini_analysis_task.is_running():
                    self.gemini_analysis_task.cancel()
                    
            # Use TaskCleanupManager for safe cleanup
            TaskCleanupManager.safe_cancel_task(
                getattr(self, 'gemini_analysis_task', None), 
                'gemini_analysis_task'
            )
            
            # Safe cache cleanup
            if hasattr(self, 'smart_cache') and self.smart_cache:
                try:
                    loop = TaskCleanupManager.safe_get_loop()
                    if loop and not loop.is_closed():
                        loop.create_task(self.smart_cache.cleanup_old())
                except Exception:
                    pass  # Ignore cleanup errors during shutdown
                    
        except Exception as e:
            logger.error(f"Error during cog unload: {e}")
        
        logger.info("🧹 Latina Economic Cog unloaded")
    
    @tasks.loop(minutes=60)  # Chạy mỗi giờ
    async def gemini_analysis_task(self):
        """Task chính - phân tích và quyết định mỗi giờ"""
        if not self.enabled:
            return
            
        try:
            logger.info("🤖 Latina: Starting hourly economic analysis...")
            
            # Kiểm tra manager có sẵn sàng
            if not hasattr(self, 'gemini_manager') or not self.gemini_manager:
                logger.warning("Latina manager not available for analysis")
                return
            
            # Phân tích và quyết định
            decision = await self.gemini_manager.analyze_and_decide(self.bot)
            
            if decision:
                # Thực thi quyết định
                success = await self.gemini_manager.execute_decision(decision, self.bot)
                
                if success:
                    # Lưu vào history
                    self.decision_history.append(decision)
                    self.last_analysis_time = datetime.now()
                    
                    # Thông báo
                    await self._notify_decision(decision)
                    
                    logger.info(f"🤖 Latina Decision executed: {decision.action_type}")
                else:
                    logger.error("❌ Failed to execute Latina decision")
            else:
                logger.info("🤖 Latina: No decision made this cycle")
                
        except asyncio.CancelledError:
            logger.info("🤖 Latina analysis task cancelled")
            raise  # Re-raise để task được cancel đúng cách
        except Exception as e:
            logger.error(f"Error in Latina analysis task: {e}")
            # Không raise exception để task tiếp tục chạy
    
    async def _notify_decision(self, decision: GeminiDecision):
        """Thông báo quyết định Gemini tới các channel đã setup"""
        if not self.notification_channels:
            return
            
        try:
            embed = EmbedBuilder.create_base_embed(
                title="🎀 Latina đã đưa ra quyết định!",
                description=f"**Hành động của mình:** {self._get_action_name(decision.action_type)}\n"
                           f"**Lý do:** {decision.reasoning[:200]}{'...' if len(decision.reasoning) > 200 else ''}\n"
                           f"**Độ tin cậy:** {decision.confidence:.1%}\n"
                           f"**Thời gian:** {decision.duration_hours} giờ",
                color=self._get_priority_color(decision.priority)
            )
            
            # Add thông tin chi tiết
            if decision.parameters:
                params_text = ""
                for key, value in decision.parameters.items():
                    if key == 'weather_type':
                        params_text += f"🌤️ **Thời tiết:** {value}\n"
                    elif key == 'event_name':
                        params_text += f"🎯 **Sự kiện:** {value}\n"
                    elif key == 'effect_value':
                        params_text += f"📊 **Hiệu ứng:** {value}x\n"
                
                if params_text:
                    embed.add_field(name="📋 Chi tiết", value=params_text, inline=False)
            
            embed.add_field(
                name="🎯 Tác động dự kiến", 
                value=decision.expected_impact[:100] if decision.expected_impact else "Không xác định",
                inline=False
            )
            
            embed.set_footer(text=f"Ưu tiên: {decision.priority.upper()} • Latina • {decision.timestamp.strftime('%H:%M:%S')}")
            
            # Gửi tới tất cả channels
            for guild_id, channel_id in self.notification_channels.items():
                try:
                    channel = self.bot.get_channel(channel_id)
                    if channel:
                        await channel.send(embed=embed)
                except Exception as e:
                    logger.error(f"Error sending notification to {channel_id}: {e}")
                    
        except Exception as e:
            logger.error(f"Error creating notification: {e}")
    
    def _get_action_name(self, action_type: str) -> str:
        """Chuyển đổi action type thành tên tiếng Việt"""
        names = {
            'WEATHER_CHANGE': '🌤️ Thay đổi thời tiết',
            'EVENT_TRIGGER': '🎉 Tạo sự kiện vui',
            'PRICE_ADJUSTMENT': '💰 Điều chỉnh giá cả',
            'NO_ACTION': '⏸️ Không can thiệp'
        }
        return names.get(action_type, action_type)
    
    def _get_priority_color(self, priority: str) -> int:
        """Màu embed theo mức độ ưu tiên"""
        colors = {
            'low': 0x95a5a6,      # Grey
            'medium': 0xf39c12,   # Orange  
            'high': 0xe74c3c,     # Red
            'critical': 0x8e44ad  # Purple
        }
        return colors.get(priority, 0x3498db)  # Default blue
    
    # ==================== DISCORD COMMANDS ====================
    
    @commands.group(name='gemini', invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def gemini_commands(self, ctx):
        """Nhóm lệnh quản lý Gemini Economic Manager"""
        embed = EmbedBuilder.create_base_embed(
            title="🎀 Latina AI Economic Manager",
            description="Xin chào! Mình là **Latina**, trợ lý AI quản lý kinh tế trang trại của các bạn! 💖",
            color=0xff69b4
        )
        
        embed.add_field(
            name="💝 Lệnh tương tác với Latina:",
            value="`f!gemini status` - Xem tình trạng hiện tại\n"
                  "`f!gemini analyze` - Nhờ mình phân tích ngay\n"
                  "`f!gemini history` - Xem lịch sử quyết định\n"
                  "`f!gemini prices` - Xem điều chỉnh giá hiện tại\n"
                  "`f!gemini cache` - Thống kê bộ nhớ\n"
                  "`f!gemini toggle` - Bật/tắt hoạt động\n"
                  "`f!gemini setup <channel>` - Setup thông báo cute",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @gemini_commands.command(name='status')
    @commands.has_permissions(administrator=True)
    async def gemini_status(self, ctx):
        """Xem trạng thái Gemini Manager"""
        try:
            # Check dependencies first
            if not GEMINI_MANAGER_AVAILABLE:
                embed = EmbedBuilder.create_base_embed(
                    title="🎀 Trạng thái Latina Economic Manager",
                    description="❌ **Mình không thể hoạt động vì thiếu dependencies**",
                    color=0xe74c3c
                )
                
                embed.add_field(
                    name="🔧 Cài đặt required",
                    value="```bash\npip install aiofiles>=0.8.0\npip install google-generativeai>=0.3.0\n```\n"
                          "Hoặc chạy: `install_gemini_deps.bat`",
                    inline=False
                )
                
                embed.add_field(
                    name="📋 Sau khi cài đặt",
                    value="1. Restart bot\n2. Chạy `f!gemini status`\n3. Enable với `f!gemini toggle on`",
                    inline=False
                )
                
                await ctx.send(embed=embed)
                return
            
            # Collect current data
            economic_data = await self.gemini_manager.collect_economic_data(self.bot)
            weather_data = await self.gemini_manager.collect_weather_data(self.bot)
            
            embed = EmbedBuilder.create_base_embed(
                title="🎀 Trạng thái Latina Economic Manager",
                color=0xff69b4 if self.enabled else 0xe74c3c
            )
            
            # System status
            status_icon = "🟢" if self.enabled else "🔴"
            embed.add_field(
                name=f"{status_icon} Tình trạng của Latina",
                value=f"**Hoạt động:** {'Đang làm việc' if self.enabled else 'Đang nghỉ'}\n"
                      f"**Chu kỳ phân tích:** {self.analysis_interval_hours} giờ\n"
                      f"**Lần phân tích cuối:** {self.last_analysis_time.strftime('%H:%M %d/%m') if self.last_analysis_time else 'Chưa có'}",
                inline=True
            )
            
            # Economic data
            embed.add_field(
                name="📊 Dữ liệu mình theo dõi",
                value=f"**Người chơi:** {economic_data['total_players']}\n"
                      f"**Hoạt động:** {economic_data['activity_rate']:.1%}\n"
                      f"**Sức khỏe kinh tế:** {economic_data['economic_health_score']:.2f}/1.0",
                inline=True
            )
            
            # Weather info
            embed.add_field(
                name="🌤️ Thời tiết",
                value=f"**Hiện tại:** {weather_data['current_weather']}\n"
                      f"**Hệ số:** {weather_data['modifier']}x",
                inline=True
            )
            
            # Recent decisions
            if self.decision_history:
                recent = self.decision_history[-3:]  # 3 quyết định gần nhất
                decisions_text = ""
                for d in recent:
                    decisions_text += f"• {self._get_action_name(d.action_type)} ({d.timestamp.strftime('%H:%M')})\n"
                
                embed.add_field(
                    name="📈 Quyết định gần đây",
                    value=decisions_text or "Chưa có quyết định",
                    inline=False
                )
            
            # API status
            try:
                api_status_data = self.gemini_manager.get_api_status()
                api_status = f"🟢 {api_status_data.get('available_clients', 0)} clients ready"
            except Exception as e:
                logger.error(f"Error getting API status: {e}")
                api_status = "🔴 Lỗi API"
            
            embed.add_field(
                name="🔑 API Status",
                value=api_status,
                inline=True
            )
            
            # Cache statistics
            cache_stats = self.gemini_manager.smart_cache.get_stats()
            embed.add_field(
                name="💾 Cache Stats",
                value=f"**Hit Rate:** {cache_stats['hit_rate']}\n"
                      f"**Tokens Saved:** {cache_stats['tokens_saved']}\n"
                      f"**Cost Saved:** {cache_stats['cost_saved']}",
                inline=True
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in gemini status: {e}")
            await ctx.send("❌ Lỗi khi lấy trạng thái Gemini")
    
    @gemini_commands.command(name='analyze')
    @commands.has_permissions(administrator=True)
    async def force_analysis(self, ctx):
        """Buộc phân tích kinh tế ngay lập tức"""
        try:
            await ctx.send("🎀 Để mình phân tích kinh tế cho các bạn ngay nhé...")
            
            decision = await self.gemini_manager.analyze_and_decide(self.bot)
            
            if decision:
                success = await self.gemini_manager.execute_decision(decision, self.bot)
                
                embed = EmbedBuilder.create_base_embed(
                    title="✅ Mình đã phân tích xong rồi!",
                    description=f"**Quyết định của mình:** {self._get_action_name(decision.action_type)}\n"
                               f"**Lý do:** {decision.reasoning[:150]}...\n"
                               f"**Độ tin cậy:** {decision.confidence:.1%}",
                    color=0xff69b4 if success else 0xe74c3c
                )
                
                if success:
                    self.decision_history.append(decision)
                    embed.add_field(name="🎯 Trạng thái", value="Thực hiện thành công!", inline=False)
                else:
                    embed.add_field(name="❌ Trạng thái", value="Có lỗi trong quá trình thực hiện", inline=False)
                
                await ctx.send(embed=embed)
            else:
                await ctx.send("❌ Mình không thể phân tích được - có vấn đề với API keys")
                
        except Exception as e:
            logger.error(f"Error in force analysis: {e}")
            await ctx.send("❌ Có lỗi trong quá trình mình phân tích")
    
    @gemini_commands.command(name='history')
    @commands.has_permissions(administrator=True)
    async def decision_history(self, ctx, limit: int = 10):
        """Xem lịch sử quyết định Gemini"""
        try:
            if not self.decision_history:
                await ctx.send("📋 Mình chưa có quyết định nào cả")
                return
            
            # Get recent decisions
            recent_decisions = self.decision_history[-limit:]
            
            embed = EmbedBuilder.create_base_embed(
                title=f"📋 Lịch sử quyết định của Latina ({len(recent_decisions)}/{len(self.decision_history)})",
                color=0xff69b4
            )
            
            for i, decision in enumerate(reversed(recent_decisions)):
                embed.add_field(
                    name=f"{i+1}. {self._get_action_name(decision.action_type)}",
                    value=f"**Thời gian:** {decision.timestamp.strftime('%H:%M %d/%m')}\n"
                          f"**Tin cậy:** {decision.confidence:.1%}\n"
                          f"**Lý do:** {decision.reasoning[:80]}...",
                    inline=True
                )
                
                if i >= 8:  # Limit fields
                    break
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error showing history: {e}")
            await ctx.send("❌ Lỗi khi hiển thị lịch sử")
    
    @gemini_commands.command(name='toggle')
    @commands.has_permissions(administrator=True)
    async def toggle_gemini(self, ctx, enabled: bool = None):
        """Bật/tắt Gemini Economic Manager"""
        try:
            if enabled is None:
                self.enabled = not self.enabled
            else:
                self.enabled = enabled
            
            status = "🟢 BẬT" if self.enabled else "🔴 TẮT"
            
            embed = EmbedBuilder.create_base_embed(
                title="🎀 Latina Economic Manager",
                description=f"Trạng thái của mình đã chuyển thành: **{status}**",
                color=0xff69b4 if self.enabled else 0xe74c3c
            )
            
            # Safe task start/stop
            try:
                if self.enabled and not self.gemini_analysis_task.is_running():
                    self.gemini_analysis_task.start()
                    embed.add_field(name="🚀", value="Mình đã bắt đầu làm việc rồi!", inline=False)
                elif not self.enabled and self.gemini_analysis_task.is_running():
                    self.gemini_analysis_task.cancel()
                    embed.add_field(name="⏹️", value="Mình tạm nghỉ một chút nhé!", inline=False)
            except Exception as task_error:
                logger.error(f"Error managing analysis task: {task_error}")
                embed.add_field(name="⚠️", value="Có lỗi gì đó rồi, kiểm tra logs nhé", inline=False)
            
            # Note about auto-restart
            if not self.enabled:
                embed.add_field(
                    name="ℹ️ Lưu ý", 
                    value="Mình sẽ tự động làm việc lại khi bot restart nhé!",
                    inline=False
                )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error toggling Gemini: {e}")
            await ctx.send("❌ Lỗi khi chuyển đổi trạng thái")
    
    @gemini_commands.command(name='setup')
    @commands.has_permissions(manage_channels=True)
    async def setup_notifications(self, ctx, channel: discord.TextChannel = None):
        """Setup channel nhận thông báo Gemini"""
        try:
            target_channel = channel or ctx.channel
            guild_id = ctx.guild.id
            
            self.notification_channels[guild_id] = target_channel.id
            
            embed = EmbedBuilder.create_base_embed(
                title="✅ Thiết lập thông báo Gemini",
                description=f"Channel {target_channel.mention} sẽ nhận thông báo về các quyết định Gemini",
                color=0x27ae60
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error setting up notifications: {e}")
            await ctx.send("❌ Lỗi khi thiết lập thông báo")
    
    @gemini_commands.command(name='cache')
    @commands.has_permissions(administrator=True)
    async def cache_statistics(self, ctx):
        """Xem thống kê cache chi tiết"""
        try:
            cache_stats = self.gemini_manager.smart_cache.get_stats()
            
            embed = EmbedBuilder.create_base_embed(
                title="💾 Cache Statistics - Token Savings",
                color=0x3498db
            )
            
            embed.add_field(
                name="📊 Performance",
                value=f"**Hit Rate:** {cache_stats['hit_rate']}\n"
                      f"**Cache Hits:** {cache_stats['cache_hits']}\n"
                      f"**Cache Misses:** {cache_stats['cache_misses']}\n"
                      f"**Cached Decisions:** {cache_stats['cached_decisions']}",
                inline=True
            )
            
            embed.add_field(
                name="💰 Savings",
                value=f"**Tokens Saved:** {cache_stats['tokens_saved']:,}\n"
                      f"**Est. Cost Saved:** {cache_stats['cost_saved']}\n"
                      f"**API Calls Avoided:** {cache_stats['cache_hits']}",
                inline=True
            )
            
            # Show some recent cached patterns
            embed.add_field(
                name="🔍 Cache Info",
                value="Cache automatically saves decisions for similar game states\n"
                      "This reduces API calls and speeds up responses\n"
                      "Cached decisions expire after 7 days for freshness",
                inline=False
            )
            
            embed.set_footer(text="Cache helps save tokens and improve response time!")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error showing cache stats: {e}")
            await ctx.send("❌ Lỗi khi hiển thị thống kê cache")
    
    @gemini_commands.command(name='prices')
    @commands.has_permissions(administrator=True)
    async def price_adjustments(self, ctx):
        """Xem các điều chỉnh giá hiện tại của Latina"""
        try:
            from utils.pricing import pricing_coordinator
            
            # Get active AI price adjustments
            active_adjustments = pricing_coordinator.get_active_ai_adjustments()
            
            embed = EmbedBuilder.create_base_embed(
                title="💰 Điều Chỉnh Giá Của Latina",
                description="Danh sách các điều chỉnh giá hiện tại mà mình đang áp dụng! 💖",
                color=0xff69b4
            )
            
            if not active_adjustments:
                embed.add_field(
                    name="📝 Tình trạng",
                    value="Hiện tại mình không điều chỉnh giá cây nào cả!\nTất cả giá đang ở mức bình thường 🌟",
                    inline=False
                )
            else:
                # Group adjustments by type
                increasing_crops = []
                decreasing_crops = []
                stable_crops = []
                
                for crop_type, adjustment in active_adjustments.items():
                    sell_change = (adjustment['sell_modifier'] - 1.0) * 100
                    seed_change = (adjustment['seed_modifier'] - 1.0) * 100
                    
                    crop_info = {
                        'name': adjustment['crop_name'],
                        'sell_change': sell_change,
                        'seed_change': seed_change,
                        'time_remaining': adjustment['time_remaining_minutes'],
                        'reasoning': adjustment['reasoning']
                    }
                    
                    if sell_change > 5:
                        increasing_crops.append(crop_info)
                    elif sell_change < -5:
                        decreasing_crops.append(crop_info)
                    else:
                        stable_crops.append(crop_info)
                
                # Display increasing prices
                if increasing_crops:
                    increase_text = ""
                    for crop in increasing_crops[:5]:  # Limit to 5
                        increase_text += f"📈 **{crop['name']}**\n"
                        increase_text += f"   💰 Bán: +{crop['sell_change']:.1f}% | 🌱 Hạt: {crop['seed_change']:+.1f}%\n"
                        increase_text += f"   ⏰ Còn {crop['time_remaining']} phút\n\n"
                    
                    embed.add_field(
                        name="📈 Giá Tăng",
                        value=increase_text,
                        inline=True
                    )
                
                # Display decreasing prices
                if decreasing_crops:
                    decrease_text = ""
                    for crop in decreasing_crops[:5]:  # Limit to 5
                        decrease_text += f"📉 **{crop['name']}**\n"
                        decrease_text += f"   💰 Bán: {crop['sell_change']:.1f}% | 🌱 Hạt: {crop['seed_change']:+.1f}%\n"
                        decrease_text += f"   ⏰ Còn {crop['time_remaining']} phút\n\n"
                    
                    embed.add_field(
                        name="📉 Giá Giảm",
                        value=decrease_text,
                        inline=True
                    )
                
                # Display stable adjustments
                if stable_crops:
                    stable_text = ""
                    for crop in stable_crops[:3]:  # Limit to 3
                        stable_text += f"➡️ **{crop['name']}** (±{abs(crop['sell_change']):.1f}%)\n"
                    
                    embed.add_field(
                        name="➡️ Điều Chỉnh Nhẹ",
                        value=stable_text,
                        inline=True
                    )
                
                # Show total count
                embed.add_field(
                    name="📊 Thống Kê",
                    value=f"**Tổng số cây được điều chỉnh:** {len(active_adjustments)}\n"
                          f"**Cây tăng giá:** {len(increasing_crops)}\n"
                          f"**Cây giảm giá:** {len(decreasing_crops)}\n"
                          f"**Điều chỉnh nhẹ:** {len(stable_crops)}",
                    inline=False
                )
                
                # Show most recent reasoning
                if active_adjustments:
                    latest_crop = list(active_adjustments.values())[0]
                    embed.add_field(
                        name="🌸 Lý do gần nhất của mình",
                        value=latest_crop['reasoning'][:200] + ("..." if len(latest_crop['reasoning']) > 200 else ""),
                        inline=False
                    )
            
            embed.set_footer(text="f!market để xem giá hiện tại • Latina AI Economic Manager")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Lỗi khi lấy thông tin điều chỉnh giá: {e}")
    
    @gemini_analysis_task.before_loop
    async def before_analysis_task(self):
        """Đợi bot ready trước khi start task"""
        try:
            await self.bot.wait_until_ready()
            logger.info("🤖 Gemini analysis task ready to start")
        except Exception as e:
            logger.error(f"Error in before_analysis_task: {e}")
    
    @gemini_analysis_task.error
    async def analysis_task_error(self, error):
        """Handle lỗi trong analysis task"""
        if isinstance(error, asyncio.CancelledError):
            logger.info("🤖 Gemini analysis task was cancelled")
        else:
            logger.error(f"Gemini analysis task error: {error}")
            # Restart task nếu có lỗi (trừ khi đang shutdown)
            if self.enabled and not self.bot.is_closed():
                try:
                    await asyncio.sleep(300)  # Đợi 5 phút trước khi restart
                    if self.enabled and not self.gemini_analysis_task.is_running():
                        self.gemini_analysis_task.restart()
                        logger.info("🤖 Gemini analysis task restarted after error")
                except Exception as restart_error:
                    logger.error(f"Failed to restart analysis task: {restart_error}")

# Setup function for bot
async def setup(bot):
    await bot.add_cog(GeminiEconomicCog(bot)) 