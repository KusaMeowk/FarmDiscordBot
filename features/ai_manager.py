import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
import random
import asyncio
from typing import Optional, Dict, List
import config
from database.database import Database
from utils.embeds import EmbedBuilder
from utils.enhanced_logging import get_bot_logger
from utils.task_cleanup import TaskCleanupManager
from ai.game_master import GameMasterAI, AIDecision
from ai.event_manager import EventManagerAI, SmartEvent
from ai.weather_predictor import WeatherPredictorAI, WeatherPrediction

logger = get_bot_logger()

class AICog(commands.Cog):
    """
    AI Manager Cog - Coordinates all AI systems
    
    This cog manages the Game Master AI, Event Manager AI, and Weather Predictor AI
    to create an intelligent, adaptive game experience.
    """
    
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
        
        # AI Components
        self.game_master = GameMasterAI()
        self.event_manager = EventManagerAI(database=bot.db)
        self.weather_predictor = WeatherPredictorAI()
        
        # AI State
        self.ai_enabled = True
        self.last_ai_decision_time = None
        self.ai_decision_interval = 30  # minutes
        
        # Load AI state
        asyncio.create_task(self._load_ai_state())
        
        # Start AI tasks
        self.ai_decision_task.start()
        self.ai_weather_task.start()
        
    def cog_unload(self):
        """Clean up when cog is unloaded"""
        # Use TaskCleanupManager for safe cleanup
        TaskCleanupManager.safe_cancel_task(
            getattr(self, 'ai_decision_task', None), 
            'ai_decision_task'
        )
        
        TaskCleanupManager.safe_cancel_task(
            getattr(self, 'ai_weather_task', None), 
            'ai_weather_task'
        )
        
        logger.info("🧹 AI Manager cleanup completed")
        
    async def _load_ai_state(self):
        """Load AI state từ database"""
        try:
            # Load Event Manager state
            await self.event_manager.load_ai_state()
            logger.info("🤖 AI Manager state loaded successfully")
        except Exception as e:
            logger.error(f"Error loading AI Manager state: {e}")
    
    async def _save_ai_state(self):
        """Save AI state vào database"""
        try:
            # Save Event Manager state
            await self.event_manager.save_ai_state()
        except Exception as e:
            logger.error(f"Error saving AI Manager state: {e}")
    
    @tasks.loop(minutes=30)
    async def ai_decision_task(self):
        """Main AI decision loop - runs every 30 minutes"""
        if not self.ai_enabled:
            return
            
        try:
            logger.info("🤖 AI Decision Task: Starting analysis...")
            
            # Analyze game state
            game_state = await self.game_master.analyze_game_state(self.bot)
            
            # Make event decision
            event_decision = await self.game_master.make_event_decision(self.bot)
            if event_decision:
                await self._execute_event_decision(event_decision, game_state)
            
            # Make weather decision
            weather_decision = await self.game_master.make_weather_decision(self.bot)
            if weather_decision:
                await self._execute_weather_decision(weather_decision, game_state)
            
            self.last_ai_decision_time = datetime.now()
            logger.info("🤖 AI Decision Task: Analysis complete")
            
        except Exception as e:
            logger.error(f"Critical error in AI decision task: {e}")
            # Don't reraise - let task continue running
            # Store error for diagnostics
            self.last_error = {
                'type': 'ai_decision_task',
                'error': str(e),
                'timestamp': datetime.now()
            }
    
    @tasks.loop(minutes=45)
    async def ai_weather_task(self):
        """AI Weather management task - runs every 45 minutes"""
        if not self.ai_enabled:
            return
            
        try:
            # Get current weather
            weather_cog = self.bot.get_cog('WeatherCog')
            if not weather_cog:
                return
            
            weather_data = await weather_cog.fetch_weather_data()
            current_weather = weather_data.get('weather', [{}])[0].get('main', 'clouds').lower()
            
            # Get game state
            game_state = await self.game_master.analyze_game_state(self.bot)
            
            # Predict next weather
            prediction = await self.weather_predictor.predict_next_weather(game_state, current_weather)
            
            # Update weather history
            self.weather_predictor.update_history(current_weather)
            
            # Log AI weather decision
            logger.info(f"🌤️ AI Weather: Predicted {prediction.weather_type} "
                       f"(Confidence: {prediction.probability:.1%}) - {prediction.ai_reasoning}")
            
        except Exception as e:
            logger.error(f"Error in AI weather task: {e}")
    
    async def _execute_event_decision(self, ai_decision, game_state):
        """Execute AI event decision"""
        try:
            # Check if we should trigger new event (cooldown logic)
            if not self.event_manager.should_trigger_new_event(game_state):
                return
                
            # Generate contextual event
            smart_event = await self.event_manager.generate_contextual_event(game_state, ai_decision)
            if not smart_event:
                return
            
            # Convert to events cog format
            events_cog = self.bot.get_cog('EventsCog')
            if not events_cog:
                logger.error("EventsCog not found")
                return
            
            # Create event data in expected format
            event_data = {
                'name': smart_event.name,
                'description': smart_event.description,
                'effect_type': smart_event.effect_type,
                'effect_value': smart_event.effect_value,
                'duration': smart_event.duration_hours * 3600,  # Convert to seconds
                'ai_generated': True,
                'ai_reasoning': smart_event.ai_reasoning,
                'rarity': smart_event.rarity
            }
            
            # Trigger the event
            await events_cog.start_event(event_data)
            
            # Update event manager history
            self.event_manager.event_history.append(smart_event)
            self.event_manager.last_event_time = datetime.now()
            
            # Save AI state to persist the event trigger time
            await self._save_ai_state()
            
            # Notify about AI decision
            await self._notify_ai_event(smart_event, ai_decision)
            
            logger.info(f"🤖 AI Event: Triggered '{smart_event.name}' - {smart_event.ai_reasoning}")
            
        except Exception as e:
            logger.error(f"Error executing event decision: {e}")
    
    async def _execute_weather_decision(self, ai_decision, game_state):
        """Execute AI weather decision"""
        try:
            # Get WeatherCog to apply AI weather
            weather_cog = self.bot.get_cog('WeatherCog')
            if not weather_cog:
                logger.error("WeatherCog not found")
                return
            
            # Apply AI weather prediction
            weather_prediction = await weather_cog.apply_ai_weather()
            
            if weather_prediction:
                # Notify about weather change
                await self._notify_ai_weather(weather_prediction, ai_decision)
                logger.info(f"🌤️ AI Weather: Applied '{weather_prediction['weather']}' - {weather_prediction.get('reasoning', '')}")
            else:
                logger.warning("Failed to apply AI weather prediction")
            
        except Exception as e:
            logger.error(f"Error executing weather decision: {e}")
    
    async def _notify_ai_weather(self, weather_prediction: dict, ai_decision):
        """Notify about AI-generated weather changes"""
        try:
            # Get configured AI notifications from database
            ai_notifications = await self.bot.db.get_all_ai_notifications()
            
            for notification in ai_notifications:
                # Skip if weather notifications are disabled
                if not notification.weather_notifications:
                    continue
                
                guild = self.bot.get_guild(notification.guild_id)
                if not guild:
                    continue
                
                channel = guild.get_channel(notification.channel_id)
                if not channel:
                    continue
                
                # Weather info
                weather_emojis = {
                    'sunny': '☀️',
                    'cloudy': '☁️',
                    'rainy': '🌧️',
                    'stormy': '⛈️',
                    'perfect': '🌟'
                }
                
                weather_names = {
                    'sunny': 'Nắng',
                    'cloudy': 'Có mây',
                    'rainy': 'Mưa',
                    'stormy': 'Bão',
                    'perfect': 'Hoàn hảo'
                }
                
                weather_emoji = weather_emojis.get(weather_prediction['weather'], '🌤️')
                weather_name = weather_names.get(weather_prediction['weather'], weather_prediction['weather'])
                
                embed = EmbedBuilder.create_base_embed(
                    title="🌤️ AI Weather Change",
                    description=f"Weather Predictor AI đã điều chỉnh thời tiết!",
                    color=0x3498DB
                )
                embed.add_field(
                    name=f"{weather_emoji} Thời Tiết Mới",
                    value=f"**{weather_name}**\n⏰ Thời gian: {weather_prediction['duration']//3600}h",
                    inline=True
                )
                embed.add_field(
                    name="📊 Độ Tin Cậy",
                    value=f"{weather_prediction.get('confidence', 0.5):.1%}",
                    inline=True
                )
                if weather_prediction.get('reasoning'):
                    embed.add_field(
                        name="🧠 AI Reasoning",
                        value=weather_prediction['reasoning'][:100] + "..." if len(weather_prediction['reasoning']) > 100 else weather_prediction['reasoning'],
                        inline=False
                    )
                embed.set_footer(text="AI Weather Predictor đang phân tích và điều chỉnh game balance")
                
                try:
                    await channel.send(embed=embed)
                except discord.Forbidden:
                    logger.warning(f"No permission to send AI weather notification in guild {guild.name}")
                except Exception as e:
                    logger.error(f"Error sending AI weather notification to {guild.name}: {e}")
                    
        except Exception as e:
            logger.error(f"Error in AI weather notification: {e}")
    
    async def _notify_ai_event(self, smart_event: SmartEvent, ai_decision):
        """Notify about AI-generated events"""
        try:
            # Get configured AI notifications from database
            ai_notifications = await self.bot.db.get_all_ai_notifications()
            
            for notification in ai_notifications:
                # Skip if event notifications are disabled
                if not notification.event_notifications:
                    continue
                
                guild = self.bot.get_guild(notification.guild_id)
                if not guild:
                    continue
                
                channel = guild.get_channel(notification.channel_id)
                if not channel:
                    continue
                
                embed = EmbedBuilder.create_base_embed(
                    title="Update Event",
                    description=f"Sự kiện mới!",
                    color=0x9B59B6
                )
                embed.add_field(
                    name=f"{smart_event.name}",
                    value=smart_event.description,
                    inline=False
                )
                embed.add_field(
                    name="🧠 AI Reasoning",
                    value=smart_event.ai_reasoning,
                    inline=True
                )
                embed.add_field(
                    name="💎 Rarity",
                    value=smart_event.rarity.title(),
                    inline=True
                )
                embed.add_field(
                    name="⏰ Duration",
                    value=f"{smart_event.duration_hours} giờ",
                    inline=True
                )
                embed.set_footer(text="AI Engine đang học và thích ứng với hành vi người chơi")
                
                try:
                    await channel.send(embed=embed)
                except discord.Forbidden:
                    logger.warning(f"No permission to send AI notification in guild {guild.name}")
                except Exception as e:
                    logger.error(f"Error sending AI notification to {guild.name}: {e}")
                    
        except Exception as e:
            logger.error(f"Error in AI notification: {e}")
    
    # Admin Commands
    @commands.group(name='ai', invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def ai_commands(self, ctx):
        """AI management commands"""
        embed = EmbedBuilder.create_base_embed(
            title="🤖 AI Engine Commands",
            description="Quản lý hệ thống AI của bot",
            color=0x9B59B6
        )
        embed.add_field(
            name="📊 Monitoring",
            value="`f!ai status` - Trạng thái AI\n`f!ai report` - Báo cáo chi tiết\n`f!ai analytics` - Phân tích dữ liệu",
            inline=False
        )
        embed.add_field(
            name="⚙️ Control",
            value="`f!ai toggle` - Bật/tắt AI\n`f!ai reset` - Reset AI state\n`f!ai force` - Force AI decision",
            inline=False
        )
        embed.add_field(
            name="🔔 Notifications",
            value="`f!ai setupnotify` - Setup thông báo\n`f!ai notifystatus` - Trạng thái thông báo\n`f!ai togglenotify` - Bật/tắt thông báo",
            inline=False
        )
        await ctx.send(embed=embed)
    
    @ai_commands.command(name='status')
    @commands.has_permissions(administrator=True)
    async def ai_status(self, ctx):
        """Show AI system status"""
        embed = EmbedBuilder.create_base_embed(
            title="🤖 AI Engine Status",
            description="Trạng thái hệ thống AI hiện tại",
            color=0x9B59B6 if self.ai_enabled else 0xE74C3C
        )
        
        # System status
        status_emoji = "🟢" if self.ai_enabled else "🔴"
        embed.add_field(
            name=f"{status_emoji} System Status",
            value=f"{'Hoạt động' if self.ai_enabled else 'Tạm dừng'}",
            inline=True
        )
        
        # Last decision time
        if self.last_ai_decision_time:
            time_diff = datetime.now() - self.last_ai_decision_time
            minutes_ago = int(time_diff.total_seconds() / 60)
            embed.add_field(
                name="🕐 Last Decision",
                value=f"{minutes_ago} phút trước",
                inline=True
            )
        
        # Task status
        task_status = "🟢 Running" if not self.ai_decision_task.is_being_cancelled() else "🔴 Stopped"
        embed.add_field(
            name="🔄 Background Tasks",
            value=task_status,
            inline=True
        )
        
        # Current AI state
        game_state = self.game_master.game_state
        if game_state:
            embed.add_field(
                name="📊 Game State",
                value=f"Players: {game_state.active_players}\nSatisfaction: {game_state.player_satisfaction:.1%}\nActivity: {game_state.recent_activity_level:.1%}",
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    @ai_commands.command(name='report')
    @commands.has_permissions(administrator=True)
    async def ai_report(self, ctx):
        """Generate comprehensive AI report"""
        try:
            # Generate reports from all AI components
            game_master_report = self.game_master.get_ai_report()
            weather_report = self.weather_predictor.get_ai_weather_report()
            event_analytics = self.event_manager.get_event_analytics()
            
            # Create comprehensive embed
            embed = EmbedBuilder.create_base_embed(
                title="🧠 Comprehensive AI Report",
                description="Báo cáo chi tiết về hoạt động của AI Engine",
                color=0x9B59B6
            )
            
            # Game Master section
            embed.add_field(
                name="🎮 Game Master AI",
                value=game_master_report[:1000] + "..." if len(game_master_report) > 1000 else game_master_report,
                inline=False
            )
            
            # Event Manager section  
            embed.add_field(
                name="🎭 Event Manager AI",
                value=f"Events Generated: {event_analytics.get('total_events_generated', 0)}\nActive Events: {event_analytics.get('active_events', 0)}",
                inline=True
            )
            
            # Weather Predictor section
            embed.add_field(
                name="🌤️ Weather AI",
                value=f"Prediction Accuracy: {self.weather_predictor.prediction_accuracy:.1%}\nPattern: {self.weather_predictor.current_pattern.name if self.weather_predictor.current_pattern else 'Standalone'}",
                inline=True
            )
            
            await ctx.send(embed=embed)
            
            # Send detailed weather report in separate message
            await ctx.send(f"```{weather_report}```")
            
        except Exception as e:
            await ctx.send(f"❌ Lỗi tạo báo cáo: {e}")
    
    @ai_commands.command(name='toggle')
    @commands.has_permissions(administrator=True)
    async def ai_toggle(self, ctx):
        """Toggle AI system on/off"""
        self.ai_enabled = not self.ai_enabled
        status = "bật" if self.ai_enabled else "tắt"
        emoji = "🟢" if self.ai_enabled else "🔴"
        
        embed = EmbedBuilder.create_base_embed(
            title=f"{emoji} AI Engine {status.title()}",
            description=f"Hệ thống AI đã được {status}",
            color=0x2ECC71 if self.ai_enabled else 0xE74C3C
        )
        await ctx.send(embed=embed)
    
    @ai_commands.command(name='force')
    @commands.has_permissions(administrator=True)
    async def ai_force_decision(self, ctx):
        """Force AI to make a decision now"""
        if not self.ai_enabled:
            await ctx.send("❌ AI Engine đang tắt!")
            return
        
        embed = EmbedBuilder.create_base_embed(
            title="🤖 Forcing AI Decision...",
            description="Đang buộc AI thực hiện phân tích và quyết định...",
            color=0xF39C12
        )
        message = await ctx.send(embed=embed)
        
        try:
            # Force AI analysis
            await self.ai_decision_task()
            
            embed.title = "✅ AI Decision Completed"
            embed.description = "AI đã hoàn thành phân tích và thực hiện quyết định!"
            embed.color = 0x2ECC71
            await message.edit(embed=embed)
            
        except Exception as e:
            embed.title = "❌ AI Decision Failed"
            embed.description = f"Lỗi: {e}"
            embed.color = 0xE74C3C
            await message.edit(embed=embed)
    
    @ai_commands.command(name='reset')
    @commands.has_permissions(administrator=True)
    async def ai_reset(self, ctx):
        """Reset AI state"""
        # Reset all AI components
        self.game_master = GameMasterAI()
        self.event_manager = EventManagerAI(database=self.bot.db)
        self.weather_predictor = WeatherPredictorAI()
        self.last_ai_decision_time = None
        
        embed = EmbedBuilder.create_base_embed(
            title="🔄 AI Engine Reset",
            description="Tất cả thành phần AI đã được reset về trạng thái ban đầu",
            color=0xF39C12
        )
        await ctx.send(embed=embed)
    
    @ai_commands.command(name='analytics')
    @commands.has_permissions(administrator=True)
    async def ai_analytics(self, ctx):
        """Show detailed AI analytics"""
        try:
            event_analytics = self.event_manager.get_event_analytics()
            weather_analytics = self.weather_predictor.get_weather_analytics()
            
            embed = EmbedBuilder.create_base_embed(
                title="📊 AI Analytics Dashboard",
                description="Phân tích chi tiết về hiệu suất AI",
                color=0x3498DB
            )
            
            # Event analytics
            if event_analytics.get('total_events_generated', 0) > 0:
                embed.add_field(
                    name="🎭 Event Analytics",
                    value=f"Total Events: {event_analytics['total_events_generated']}\nAvg Duration: {event_analytics.get('average_event_duration', 0):.1f}h",
                    inline=True
                )
            
            # Weather analytics
            if weather_analytics.get('weather_history_length', 0) > 0:
                embed.add_field(
                    name="🌤️ Weather Analytics",
                    value=f"History Length: {weather_analytics['weather_history_length']}\nStability: {weather_analytics.get('weather_stability', 0):.1%}",
                    inline=True
                )
            
            # System performance
            uptime = datetime.now() - self.bot.start_time if hasattr(self.bot, 'start_time') else timedelta(0)
            embed.add_field(
                name="⚡ Performance",
                value=f"Uptime: {int(uptime.total_seconds() / 3600)}h\nDecision Interval: {self.ai_decision_interval}min",
                inline=True
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Lỗi tạo analytics: {e}")
    
    @ai_commands.command(name='setupnotify', aliases=['setup_notifications'])
    @commands.has_permissions(manage_channels=True)
    async def setup_ai_notifications(self, ctx, channel_id: int = None, 
                                   event_notifications: bool = True, weather_notifications: bool = True):
        """Setup AI notifications cho server
        
        Sử dụng:
        - f!ai setupnotify - Setup tại channel hiện tại
        - f!ai setupnotify <channel_id> - Setup tại channel cụ thể
        - f!ai setupnotify <channel_id> True False - Chỉ event notifications
        """
        if channel_id is None:
            channel_id = ctx.channel.id
            channel = ctx.channel
        else:
            channel = self.bot.get_channel(channel_id)
            if not channel:
                await ctx.send("❌ Không tìm thấy channel!")
                return
            
            # Check if channel is in same guild
            if channel.guild.id != ctx.guild.id:
                await ctx.send("❌ Channel phải trong cùng server!")
                return
        
        try:
            await self.bot.db.set_ai_notification(
                ctx.guild.id, 
                channel_id, 
                event_notifications, 
                weather_notifications
            )
            
            embed = EmbedBuilder.create_base_embed(
                title="🤖 AI Notifications Setup",
                description="Đã thiết lập thông báo AI thành công!",
                color=0x2ECC71
            )
            embed.add_field(
                name="📍 Channel",
                value=f"<#{channel_id}>",
                inline=True
            )
            embed.add_field(
                name="🎪 Event Notifications",
                value="✅ Bật" if event_notifications else "❌ Tắt",
                inline=True
            )
            embed.add_field(
                name="🌤️ Weather Notifications", 
                value="✅ Bật" if weather_notifications else "❌ Tắt",
                inline=True
            )
            embed.add_field(
                name="💡 Quản lý",
                value="`f!ai togglenotify` - Bật/tắt notifications\n"
                      "`f!ai notifystatus` - Xem trạng thái\n"
                      "`f!ai toggleevent` - Bật/tắt event notifications\n"
                      "`f!ai toggleweather` - Bật/tắt weather notifications",
                inline=False
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Lỗi khi setup: {e}")
    
    @ai_commands.command(name='notifystatus', aliases=['notification_status'])
    async def ai_notification_status(self, ctx):
        """Kiểm tra trạng thái AI notifications"""
        notification = await self.bot.db.get_ai_notification(ctx.guild.id)
        
        embed = EmbedBuilder.create_base_embed(
            title="🤖 AI Notification Status",
            description="Trạng thái thông báo AI cho server này",
            color=0x3498DB
        )
        
        if notification:
            channel = self.bot.get_channel(notification.channel_id)
            channel_text = f"<#{notification.channel_id}>" if channel else f"ID: {notification.channel_id} (không tìm thấy)"
            
            status_emoji = "🟢" if notification.enabled else "🔴"
            event_emoji = "🟢" if notification.event_notifications else "🔴"
            weather_emoji = "🟢" if notification.weather_notifications else "🔴"
            
            embed.add_field(
                name=f"{status_emoji} Trạng thái tổng",
                value="Hoạt động" if notification.enabled else "Tạm dừng",
                inline=True
            )
            embed.add_field(
                name="📍 Channel",
                value=channel_text,
                inline=True
            )
            embed.add_field(
                name="Settings",
                value=f"{event_emoji} Events\n{weather_emoji} Weather",
                inline=True
            )
        else:
            embed.add_field(
                name="❌ Chưa thiết lập",
                value="Sử dụng `f!ai setupnotify` để thiết lập thông báo",
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    @ai_commands.command(name='togglenotify', aliases=['toggle_notifications'])
    @commands.has_permissions(manage_channels=True)
    async def toggle_ai_notifications(self, ctx, enabled: bool = None):
        """Bật/tắt AI notifications"""
        notification = await self.bot.db.get_ai_notification(ctx.guild.id)
        
        if not notification:
            await ctx.send("❌ Chưa thiết lập AI notifications! Sử dụng `f!ai setupnotify` trước.")
            return
        
        if enabled is None:
            enabled = not notification.enabled
        
        await self.bot.db.toggle_ai_notification(ctx.guild.id, enabled)
        
        status = "bật" if enabled else "tắt"
        emoji = "🟢" if enabled else "🔴"
        
        embed = EmbedBuilder.create_base_embed(
            title=f"{emoji} AI Notifications {status.title()}",
            description=f"Thông báo AI đã được {status}",
            color=0x2ECC71 if enabled else 0xE74C3C
        )
        await ctx.send(embed=embed)
    
    @ai_commands.command(name='toggleevent', aliases=['toggle_event_notifications'])
    @commands.has_permissions(manage_channels=True)
    async def toggle_ai_event_notifications(self, ctx, enabled: bool = None):
        """Bật/tắt AI event notifications"""
        notification = await self.bot.db.get_ai_notification(ctx.guild.id)
        
        if not notification:
            await ctx.send("❌ Chưa thiết lập AI notifications! Sử dụng `f!ai setupnotify` trước.")
            return
        
        if enabled is None:
            enabled = not notification.event_notifications
        
        await self.bot.db.toggle_ai_event_notification(ctx.guild.id, enabled)
        
        status = "bật" if enabled else "tắt"
        emoji = "🎪" if enabled else "❌"
        
        embed = EmbedBuilder.create_base_embed(
            title=f"{emoji} AI Event Notifications {status.title()}",
            description=f"Thông báo AI events đã được {status}",
            color=0x2ECC71 if enabled else 0xE74C3C
        )
        await ctx.send(embed=embed)
    
    @ai_commands.command(name='toggleweather', aliases=['toggle_weather_notifications'])
    @commands.has_permissions(manage_channels=True) 
    async def toggle_ai_weather_notifications(self, ctx, enabled: bool = None):
        """Bật/tắt AI weather notifications"""
        notification = await self.bot.db.get_ai_notification(ctx.guild.id)
        
        if not notification:
            await ctx.send("❌ Chưa thiết lập AI notifications! Sử dụng `f!ai setupnotify` trước.")
            return
        
        if enabled is None:
            enabled = not notification.weather_notifications
        
        await self.bot.db.toggle_ai_weather_notification(ctx.guild.id, enabled)
        
        status = "bật" if enabled else "tắt"
        emoji = "🌤️" if enabled else "❌"
        
        embed = EmbedBuilder.create_base_embed(
            title=f"{emoji} AI Weather Notifications {status.title()}",
            description=f"Thông báo AI weather đã được {status}",
            color=0x2ECC71 if enabled else 0xE74C3C
        )
        await ctx.send(embed=embed)
    
    # Wait for bot to be ready
    @ai_decision_task.before_loop
    async def before_ai_task(self):
        await self.bot.wait_until_ready()
        
    @ai_weather_task.before_loop
    async def before_weather_task(self):
        await self.bot.wait_until_ready()

    @ai_decision_task.error
    async def ai_decision_task_error(self, error):
        """Handle AI decision task errors"""
        logger.error(f"AI decision task crashed: {error}")
        # Task will automatically restart due to @tasks.loop
        await asyncio.sleep(60)  # Wait 1 minute before restart

async def setup(bot):
    await bot.add_cog(AICog(bot))
