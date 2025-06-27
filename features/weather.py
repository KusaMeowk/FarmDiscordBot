import discord
from discord.ext import commands, tasks
import asyncio
import aiosqlite
from datetime import datetime, timedelta
from typing import Dict, Any
import logging

import config
from utils.embeds import EmbedBuilder
from utils.state_manager import StateManager

logger = logging.getLogger(__name__)

class WeatherCog(commands.Cog):
    """Cog quản lý thời tiết game - điều khiển bởi Gemini Game Master"""
    
    def __init__(self, bot):
        self.bot = bot
        self.current_weather = None  # Thời tiết hiện tại từ Gemini Game Master
        self.next_weather_change = None  # Thời điểm thay đổi thời tiết tiếp theo
        self.weather_change_duration = 3600  # 1 giờ = 3600 giây (default)
        
        # State Manager cho persistence
        self.state_manager = None  # Sẽ được khởi tạo trong setup_hook
        
        # Chỉ giữ market notification task
        self.market_notification_task.start()
    
    async def setup_hook(self):
        """Setup state manager và load weather state"""
        try:
            self.state_manager = StateManager(self.bot.db)
            await self._load_weather_state()
            logger.info("✅ Weather Cog initialized successfully")
        except Exception as e:
            logger.error(f"❌ Error initializing Weather Cog: {e}", exc_info=True)
    
    async def _load_weather_state(self):
        """Load weather state từ database"""
        try:
            if not self.state_manager:
                return
                
            state = await self.state_manager.load_weather_state()
            if state:
                # Handle current_weather - ensure it's a string
                current_weather_data = state.get('current_weather', {})
                
                if isinstance(current_weather_data, dict):
                    # Check if it's nested structure (from Gemini)
                    if 'type' in current_weather_data:
                        self.current_weather = current_weather_data.get('type', 'sunny')
                    elif 'current_weather' in current_weather_data:
                        nested_weather = current_weather_data['current_weather']
                        if isinstance(nested_weather, dict) and 'type' in nested_weather:
                            self.current_weather = nested_weather['type']
                        else:
                            self.current_weather = str(nested_weather) if nested_weather else 'sunny'
                    else:
                        # Unknown dict structure, default to sunny
                        self.current_weather = 'sunny'
                elif isinstance(current_weather_data, str):
                    self.current_weather = current_weather_data
                else:
                    self.current_weather = 'sunny'
                
                # Validate weather type
                valid_weather_types = ['sunny', 'rainy', 'storm', 'stormy', 'drought', 'cloudy', 'windy', 'foggy']
                if self.current_weather not in valid_weather_types:
                    logger.warning(f"Invalid weather type loaded: {self.current_weather}, defaulting to sunny")
                    self.current_weather = 'sunny'
                
                # Map 'stormy' to 'storm' for consistency
                if self.current_weather == 'stormy':
                    self.current_weather = 'storm'
                
                # Parse next_weather_change
                next_change_str = state.get('next_weather_change')
                if next_change_str:
                    try:
                        # Check if it's already a datetime object
                        if isinstance(next_change_str, datetime):
                            self.next_weather_change = next_change_str
                        elif isinstance(next_change_str, str):
                            self.next_weather_change = datetime.fromisoformat(next_change_str)
                        else:
                            logger.warning(f"Invalid next_weather_change type: {type(next_change_str)}")
                            self.next_weather_change = None
                    except (ValueError, TypeError) as e:
                        logger.warning(f"Error parsing next_weather_change: {e}")
                        self.next_weather_change = None
                        
            logger.info(f"✅ Loaded weather state: {self.current_weather}")
        except Exception as e:
            logger.error(f"❌ Error loading weather state: {e}", exc_info=True)
    
    async def _save_weather_state(self):
        """Save weather state to database"""
        try:
            if not self.state_manager:
                return
                
            # Prepare current weather data
            current_weather_data = {
                'current_weather': self.current_weather,
                'last_updated': datetime.now().isoformat()
            }
            
            await self.state_manager.save_weather_state(
                next_weather_change=self.next_weather_change,
                current_weather=current_weather_data
            )
            logger.info(f"✅ Saved weather state: {self.current_weather}")
        except Exception as e:
            logger.error(f"❌ Error saving weather state: {e}", exc_info=True)
    
    def get_weather_effects(self, weather_type: str) -> dict:
        """Lấy hiệu ứng thời tiết lên cây trồng"""
        try:
            if not hasattr(config, 'WEATHER_EFFECTS'):
                logger.error("WEATHER_EFFECTS not found in config")
                return {'growth_modifier': 1.0, 'yield_modifier': 1.0}
            
            effects = config.WEATHER_EFFECTS.get(weather_type, config.WEATHER_EFFECTS.get('cloudy', {}))
            
            # Validate return value
            if not isinstance(effects, dict):
                logger.error(f"Weather effects not dict for {weather_type}: {type(effects)}")
                return {'growth_modifier': 1.0, 'yield_modifier': 1.0}
            
            if 'growth_modifier' not in effects or 'yield_modifier' not in effects:
                logger.error(f"Missing modifiers in weather effects for {weather_type}: {effects}")
                return {'growth_modifier': 1.0, 'yield_modifier': 1.0}
            
            return effects
        except Exception as e:
            logger.error(f"Error getting weather effects for {weather_type}: {e}", exc_info=True)
            return {'growth_modifier': 1.0, 'yield_modifier': 1.0}
    
    async def set_weather(self, weather_type: str, duration_minutes: int = 60, source: str = "Gemini Game Master"):
        """Set weather trực tiếp - dành cho Gemini Game Master"""
        try:
            # Validate weather type
            valid_weather_types = ['sunny', 'rainy', 'storm', 'drought', 'cloudy', 'windy', 'foggy']
            if weather_type not in valid_weather_types:
                logger.warning(f"Invalid weather type: {weather_type}")
                return False
            
            # Store old weather for notification
            old_weather = self.current_weather or 'unknown'
            
            # Set new weather
            self.current_weather = weather_type
            self.next_weather_change = datetime.now() + timedelta(minutes=duration_minutes)
            
            # Save state to database
            await self._save_weather_state()
            
            logger.info(f"🌤️ {source} set weather to {weather_type} for {duration_minutes} minutes")
            
            # Send notification to all guilds
            await self._notify_weather_change_from_source(old_weather, weather_type, duration_minutes, source)
            
            return True
            
        except Exception as e:
            logger.error(f"Error setting weather: {e}")
            return False
    
    async def get_current_weather_info(self) -> Dict[str, Any]:
        """Lấy thông tin thời tiết hiện tại cho Gemini Game Master"""
        try:
            current_time = datetime.now()
            
            # Calculate remaining time
            remaining_minutes = 0
            if self.next_weather_change:
                remaining_delta = self.next_weather_change - current_time
                remaining_minutes = max(0, int(remaining_delta.total_seconds() / 60))
            
            return {
                'current_weather': self.current_weather or 'sunny',
                'duration_remaining_minutes': remaining_minutes,
                'next_change_time': self.next_weather_change,
                'weather_effects': self.get_weather_effects(self.current_weather or 'sunny'),
                'satisfaction_score': self._calculate_weather_satisfaction(),
                'last_change_time': current_time - timedelta(minutes=self.weather_change_duration//60 - remaining_minutes) if remaining_minutes > 0 else None
            }
            
        except Exception as e:
            logger.error(f"Error getting weather info: {e}")
            return {
                'current_weather': 'sunny',
                'duration_remaining_minutes': 0,
                'weather_effects': self.get_weather_effects('sunny'),
                'satisfaction_score': 0.5
            }
    
    def _calculate_weather_satisfaction(self) -> float:
        """Tính toán mức độ hài lòng với thời tiết hiện tại"""
        try:
            weather = self.current_weather or 'sunny'
            
            # Base satisfaction scores for different weather types
            satisfaction_scores = {
                'sunny': 0.8,      # High satisfaction
                'cloudy': 0.7,     # Good satisfaction  
                'rainy': 0.6,      # Moderate satisfaction
                'windy': 0.5,      # Neutral
                'foggy': 0.4,      # Low satisfaction
                'storm': 0.3,      # Very low satisfaction
                'drought': 0.2     # Extremely low satisfaction
            }
            
            return satisfaction_scores.get(weather, 0.5)
            
        except Exception:
            return 0.5
    
    async def _notify_weather_change_from_source(self, old_weather: str, new_weather: str, duration_minutes: int, source: str):
        """Gửi thông báo thay đổi thời tiết từ nguồn cụ thể"""
        try:
            # Create notification embed
            embed = EmbedBuilder.create_base_embed(
                title=f"🌤️ {source} đã thay đổi thời tiết!",
                description=f"Thời tiết đã được thay đổi từ **{old_weather}** thành **{new_weather}**",
                color=0x87CEEB  # Sky blue
            )
            
            # Weather effects
            effects = self.get_weather_effects(new_weather)
            embed.add_field(
                name="📊 Hiệu ứng mới",
                value=f"• Tăng trưởng: {effects['growth_modifier']:.1%}\n"
                      f"• Sản lượng: {effects['yield_modifier']:.1%}",
                inline=True
            )
            
            # Duration info
            embed.add_field(
                name="⏰ Thời gian",
                value=f"Kéo dài: **{duration_minutes} phút**\n"
                      f"Kết thúc: <t:{int((datetime.now() + timedelta(minutes=duration_minutes)).timestamp())}:R>",
                inline=True
            )
            
            # Source info
            embed.add_field(
                name="🤖 Nguồn",
                value=f"Thay đổi bởi: **{source}**\n"
                      f"Thời gian: <t:{int(datetime.now().timestamp())}:f>",
                inline=False
            )
            
            embed.set_footer(text=f"Thời tiết mới: {new_weather} • Hãy tận dụng hiệu ứng!")
            
            # Send to all guilds with weather notifications enabled
            all_guilds = self.bot.guilds
            notification_count = 0
            
            for guild in all_guilds:
                try:
                    # Tìm channel chung để gửi thông báo
                    for channel in guild.text_channels:
                        if channel.permissions_for(guild.me).send_messages:
                            await channel.send(embed=embed)
                            notification_count += 1
                            break
                            
                except Exception as e:
                    logger.warning(f"Could not send weather notification to guild {guild.name}: {e}")
            
            logger.info(f"🌤️ Weather change notification sent to {notification_count} guilds")
            
        except Exception as e:
            logger.error(f"Error sending weather change notification: {e}")
    
    @commands.command(name='weather', aliases=['thoitiet'])
    async def weather(self, ctx):
        """Xem thời tiết hiện tại trong game được điều khiển bởi Gemini AI
        
        Sử dụng: f!weather
        """
        # Lấy thời tiết hiện tại từ Gemini Game Master
        current_weather = self.current_weather or 'sunny'
        
        # Tạo embed thời tiết game
        embed = self.create_game_weather_embed(current_weather)
        
        # Thêm thông tin thời gian thay đổi tiếp theo
        if self.next_weather_change:
            time_remaining = self.next_weather_change - datetime.now()
            
            if time_remaining.total_seconds() > 0:
                hours = int(time_remaining.total_seconds() // 3600)
                minutes = int((time_remaining.total_seconds() % 3600) // 60)
                
                embed.add_field(
                    name="⏰ Thời tiết tiếp theo",
                    value=f"Sau {hours}h {minutes}m\n({self.next_weather_change.strftime('%H:%M %d/%m')})",
                    inline=True
                )
            else:
                embed.add_field(
                    name="⏰ Thời tiết tiếp theo", 
                    value="🔄 Đang cập nhật...",
                    inline=True
                )
        else:
            embed.add_field(
                name="⏰ Chu kỳ thời tiết",
                value="🤖 Gemini AI đang điều khiển",
                inline=True
            )
        
        # Thêm thông tin về Gemini Game Master
        embed.add_field(
            name="🧠 Điều khiển bởi",
            value="🤖 **Gemini Game Master**\nThời tiết thông minh dựa trên game state",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    def create_game_weather_embed(self, weather_type: str) -> discord.Embed:
        """Tạo embed thời tiết game (không dùng API)"""
        # Weather mapping
        weather_info = {
            'sunny': {'emoji': '☀️', 'name': 'Nắng', 'temp': '28°C', 'humidity': '65%'},
            'rainy': {'emoji': '🌧️', 'name': 'Mưa', 'temp': '24°C', 'humidity': '85%'},
            'cloudy': {'emoji': '☁️', 'name': 'Nhiều mây', 'temp': '26°C', 'humidity': '75%'},
            'windy': {'emoji': '💨', 'name': 'Gió', 'temp': '25°C', 'humidity': '70%'},
            'storm': {'emoji': '⛈️', 'name': 'Bão', 'temp': '22°C', 'humidity': '90%'},
            'foggy': {'emoji': '🌫️', 'name': 'Sương mù', 'temp': '20°C', 'humidity': '95%'},
            'drought': {'emoji': '🔥', 'name': 'Hạn hán', 'temp': '35°C', 'humidity': '40%'}
        }
        
        info = weather_info.get(weather_type, weather_info['sunny'])
        
        embed = EmbedBuilder.create_base_embed(
            f"{info['emoji']} Thời tiết hiện tại",
            f"Điều kiện thời tiết đang ảnh hưởng đến nông trại của bạn",
            color=0x34495e
        )
        
        embed.add_field(
            name="🌡️ Nhiệt độ",
            value=info['temp'],
            inline=True
        )
        
        embed.add_field(
            name="🌤️ Thời tiết",
            value=info['name'],
            inline=True
        )
        
        embed.add_field(
            name="💧 Độ ẩm",
            value=info['humidity'],
            inline=True
        )
        
        # Weather effects từ config
        effects = self.get_weather_effects(weather_type)
        
        embed.add_field(
            name="📈 Hiệu ứng lên cây trồng",
            value=f"Tốc độ sinh trưởng: {effects['growth_modifier']:.1%}\nSản lượng: {effects['yield_modifier']:.1%}",
            inline=False
        )
        
        # Farming tips
        tips = {
            'sunny': "☀️ Thời tiết tuyệt vời cho việc trồng trọt! Cây sẽ phát triển nhanh hơn.",
            'rainy': "🌧️ Mưa rất tốt cho cây trồng! Sản lượng sẽ cao hơn bình thường.",
            'cloudy': "☁️ Thời tiết bình thường, không có hiệu ứng đặc biệt.",
            'windy': "💨 Gió nhẹ giúp cây thông thoáng, phát triển ổn định.",
            'storm': "⛈️ Thời tiết xấu! Cây trồng có thể bị ảnh hưởng tiêu cực.",
            'foggy': "🌫️ Sương mù làm giảm ánh sáng, cây phát triển chậm.",
            'drought': "🔥 Hạn hán nghiêm trọng! Cây cần được chăm sóc đặc biệt."
        }
        
        tip = tips.get(weather_type, "🌤️ Thời tiết ổn định.")
        
        embed.add_field(
            name="💡 Lời khuyên",
            value=tip,
            inline=False
        )
        
        return embed
    
    @commands.command(name='forecast', aliases=['dubao'])
    async def forecast(self, ctx):
        """Xem dự báo ảnh hưởng thời tiết game
        
        Sử dụng: f!forecast
        """
        embed = EmbedBuilder.create_base_embed(
            "📊 Hệ thống thời tiết Gemini Game Master",
            "Các điều kiện thời tiết khác nhau sẽ ảnh hưởng đến cây trồng của bạn",
            color=0x34495e
        )
        
        # Hiển thị tất cả weather types có trong game
        weather_info = []
        weather_names = {
            'sunny': '☀️ Nắng',
            'rainy': '🌧️ Mưa', 
            'cloudy': '☁️ Có mây',
            'windy': '💨 Gió',
            'storm': '⛈️ Bão',
            'foggy': '🌫️ Sương mù',
            'drought': '🔥 Hạn hán'
        }
        
        for weather_type in weather_names.keys():
            effects = self.get_weather_effects(weather_type)
            name = weather_names[weather_type]
            growth = f"{effects['growth_modifier']:.1%}"
            yield_mod = f"{effects['yield_modifier']:.1%}"
            
            weather_info.append(f"**{name}**\nTốc độ: {growth} | Sản lượng: {yield_mod}")
        
        embed.add_field(
            name="🌤️ Các loại thời tiết",
            value="\n\n".join(weather_info),
            inline=False
        )
        
        embed.add_field(
            name="🤖 Hệ thống AI",
            value="• Gemini Game Master điều khiển thời tiết thông minh\n"
                  "• Phân tích game state mỗi 15 phút\n"
                  "• Thay đổi thời tiết dựa trên hoạt động người chơi\n"
                  "• Tránh lặp lại để tạo đa dạng",
            inline=False
        )
        
        embed.add_field(
            name="📝 Giải thích",
            value="• Tốc độ > 100%: Cây phát triển nhanh hơn\n"
                  "• Sản lượng > 100%: Thu hoạch nhiều hơn\n"
                  "• Thời tiết thay đổi theo logic AI thông minh",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    async def get_current_weather_modifier(self) -> tuple:
        """Lấy modifier thời tiết hiện tại cho tính toán game"""
        try:
            weather_type = self.current_weather or 'sunny'
            effects = self.get_weather_effects(weather_type)
            
            # Đảm bảo effects là dict và có đủ keys
            if not isinstance(effects, dict):
                logger.warning(f"Weather effects không phải dict: {type(effects)}")
                effects = config.WEATHER_EFFECTS['sunny']
            
            growth_modifier = effects.get('growth_modifier', 1.0)
            yield_modifier = effects.get('yield_modifier', 1.0)
            
            return growth_modifier, yield_modifier
        except Exception as e:
            logger.error(f"Error getting weather modifier: {e}", exc_info=True)
            # Return default values on error
            return 1.0, 1.0
    
    @tasks.loop(minutes=15)  # Check market changes every 15 minutes
    async def market_notification_task(self):
        """Task để kiểm tra thay đổi market và gửi thông báo"""
        try:
            # Get current weather modifier (returns tuple)
            growth_mod, yield_mod = await self.get_current_weather_modifier()
            
            # Validate modifiers
            if not isinstance(growth_mod, (int, float)) or not isinstance(yield_mod, (int, float)):
                logger.error(f"Invalid weather modifiers: growth={type(growth_mod)}, yield={type(yield_mod)}")
                return
            
            # Calculate market modifier based on weather
            weather_modifier = (growth_mod + yield_mod) / 2
            
            # Log for monitoring
            logger.info(f"Market check - Current weather: {self.current_weather}, Growth: {growth_mod:.2f}, Yield: {yield_mod:.2f}, Overall modifier: {weather_modifier:.2f}")
            
        except Exception as e:
            logger.error(f"Error in market notification task: {e}", exc_info=True)
    
    @market_notification_task.before_loop
    async def before_market_task(self):
        """Wait for bot to be ready before starting task"""
        await self.bot.wait_until_ready()
    
    def cog_unload(self):
        """Clean up when cog is unloaded"""
        self.market_notification_task.cancel()

async def setup(bot):
    await bot.add_cog(WeatherCog(bot))
