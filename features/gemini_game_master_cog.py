from datetime import datetime
import discord
from discord.ext import commands
from utils.enhanced_logging import get_bot_logger

logger = get_bot_logger()

class GeminiGameMasterCog(commands.Cog):
    def __init__(self, game_master):
        self.game_master = game_master

    @commands.command(name='status')
    @commands.has_permissions(administrator=True)
    async def status(self, ctx):
        """Xem trạng thái Game Master với token optimization stats"""
        try:
            status = await self.game_master.get_status()
            token_stats = await self.game_master.get_token_optimization_stats()
            
            embed = discord.Embed(
                title="🎮 Gemini Game Master Status",
                color=0x00ff00 if status['enabled'] else 0xff0000,
                timestamp=datetime.now()
            )
            
            # Basic status
            embed.add_field(
                name="📊 Status",
                value=f"**Enabled:** {'✅' if status['enabled'] else '❌'}\n"
                      f"**Emergency Mode:** {'🚨 ON' if status['emergency_mode'] else '⭕ OFF'}\n"
                      f"**Decisions Today:** {status['decisions_today']}/20\n"
                      f"**Last Analysis:** {status['last_analysis']}",
                inline=True
            )
            
            # Token optimization stats
            embed.add_field(
                name="💾 Token Optimization",
                value=f"**Cache Hit Rate:** {token_stats['cache_hit_rate']:.1%}\n"
                      f"**Tokens Saved:** {token_stats['total_tokens_saved']:,}\n"
                      f"**Cost Saved:** ${token_stats['estimated_cost_saved']:.3f}\n"
                      f"**Context Caching:** {'✅' if token_stats['context_caching_enabled'] else '❌'}",
                inline=True
            )
            
            # Performance
            embed.add_field(
                name="⚡ Performance",
                value=f"**Total Tokens Used:** {token_stats['total_tokens_used']:,}\n"
                      f"**Avg per Decision:** {token_stats['total_tokens_used'] // max(1, status['decisions_today']):.0f}\n"
                      f"**Efficiency:** {(token_stats['total_tokens_saved'] / max(1, token_stats['total_tokens_used']) * 100):.1f}%",
                inline=True
            )
            
            # Recent decisions
            recent = status.get('recent_decisions', [])
            if recent:
                recent_text = "\n".join([
                    f"• {d['action_type']} ({d['confidence']:.0%}) - {d['reasoning'][:50]}..."
                    for d in recent[-3:]
                ])
                embed.add_field(
                    name="🕒 Recent Decisions",
                    value=recent_text,
                    inline=False
                )
            
            embed.set_footer(text="Game Master với AI-powered token optimization")
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in status command: {e}")
            await ctx.send("❌ Lỗi khi lấy trạng thái Game Master")

    @commands.command(name='tokens')
    @commands.has_permissions(administrator=True)
    async def token_stats(self, ctx):
        """Xem thống kê chi tiết về token optimization"""
        try:
            token_stats = await self.game_master.get_token_optimization_stats()
            cache_stats = token_stats.get('smart_cache_stats', {})
            
            embed = discord.Embed(
                title="💾 Token Optimization Statistics",
                color=0x3498db,
                timestamp=datetime.now()
            )
            
            # Overall token usage
            embed.add_field(
                name="📊 Token Usage",
                value=f"**Total Used:** {token_stats['total_tokens_used']:,} tokens\n"
                      f"**Total Saved:** {token_stats['total_tokens_saved']:,} tokens\n"
                      f"**Efficiency:** {(token_stats['total_tokens_saved'] / max(1, token_stats['total_tokens_used']) * 100):.1f}%\n"
                      f"**Est. Cost:** ${(token_stats['total_tokens_used'] * 0.30) / 1000000:.3f}",
                inline=True
            )
            
            # Cache performance
            embed.add_field(
                name="🎯 Cache Performance",
                value=f"**Hit Rate:** {token_stats['cache_hit_rate']:.1%}\n"
                      f"**Hits:** {cache_stats.get('cache_hits', 0)}\n"
                      f"**Misses:** {cache_stats.get('cache_misses', 0)}\n"
                      f"**Cached Decisions:** {cache_stats.get('cached_decisions', 0)}",
                inline=True
            )
            
            # Cost savings
            embed.add_field(
                name="💰 Cost Savings",
                value=f"**Saved Today:** ${token_stats['estimated_cost_saved']:.3f}\n"
                      f"**Saved per Month:** ${token_stats['estimated_cost_saved'] * 30:.2f}\n"
                      f"**Context Caching:** {'✅ Active' if token_stats['context_caching_enabled'] else '❌ Disabled'}\n"
                      f"**Smart Cache:** {'✅ Active' if cache_stats else '❌ Disabled'}",
                inline=True
            )
            
            # Token breakdown
            daily_tokens = token_stats['total_tokens_used']
            monthly_tokens = daily_tokens * 30
            yearly_tokens = daily_tokens * 365
            
            embed.add_field(
                name="📈 Projections",
                value=f"**Daily:** {daily_tokens:,} tokens (${(daily_tokens * 0.30) / 1000000:.3f})\n"
                      f"**Monthly:** {monthly_tokens:,} tokens (${(monthly_tokens * 0.30) / 1000000:.2f})\n"
                      f"**Yearly:** {yearly_tokens:,} tokens (${(yearly_tokens * 0.30) / 1000000:.2f})\n"
                      f"**Rate Limit:** {'✅ Safe' if daily_tokens < 800000 else '⚠️ High'}",
                inline=False
            )
            
            embed.set_footer(text="Token optimization giúp tiết kiệm chi phí API đáng kể!")
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in token_stats command: {e}")
            await ctx.send("❌ Lỗi khi lấy thống kê token")

    @commands.command(name='cache')
    @commands.has_permissions(administrator=True)
    async def cache_info(self, ctx, action: str = "info"):
        """Quản lý cache system (info/clear/stats)"""
        try:
            if action.lower() == "clear":
                if self.game_master.smart_cache:
                    await self.game_master.smart_cache.clear_cache()
                    await ctx.send("🗑️ Cache đã được xóa!")
                else:
                    await ctx.send("❌ Smart cache không khả dụng")
                    
            elif action.lower() == "stats":
                await self.token_stats(ctx)
                
            else:  # info
                if not self.game_master.smart_cache:
                    await ctx.send("❌ Smart cache không khả dụng")
                    return
                
                cache_stats = self.game_master.smart_cache.get_stats()
                
                embed = discord.Embed(
                    title="💾 Smart Cache Information",
                    color=0x9b59b6,
                    timestamp=datetime.now()
                )
                
                embed.add_field(
                    name="📊 Cache Stats",
                    value=f"**Cached Decisions:** {cache_stats.get('cached_decisions', 0)}\n"
                          f"**Hit Rate:** {cache_stats.get('hit_rate', 'N/A')}\n"
                          f"**Tokens Saved:** {cache_stats.get('tokens_saved', 0):,}\n"
                          f"**Cost Saved:** {cache_stats.get('cost_saved', '$0.00')}",
                    inline=True
                )
                
                embed.add_field(
                    name="⚙️ Settings",
                    value=f"**Similarity Threshold:** 80%\n"
                          f"**Max Age:** 14 days\n"
                          f"**Min Success Rate:** 60%\n"
                          f"**Auto Cleanup:** ✅ Enabled",
                    inline=True
                )
                
                embed.add_field(
                    name="🔍 How It Works",
                    value="Cache tự động lưu decisions cho game states tương tự\n"
                          "Khi gặp tình huống giống nhau, tái sử dụng decision cũ\n"
                          "Tiết kiệm ~2500 tokens mỗi lần cache hit\n"
                          "Tự động expire sau 14 ngày để đảm bảo freshness",
                    inline=False
                )
                
                await ctx.send(embed=embed)
                
        except Exception as e:
            logger.error(f"Error in cache_info command: {e}")
            await ctx.send("❌ Lỗi khi xử lý cache command")

    @commands.command(name='force_weather', aliases=['fw'])
    @commands.has_permissions(administrator=True)
    async def force_weather(self, ctx, weather_type: str = None, duration: int = 60):
        """🌤️ Buộc Gemini thay đổi thời tiết ngay lập tức
        
        Sử dụng: f!force_weather <loại_thời_tiết> [thời_gian_phút]
        Ví dụ: f!force_weather sunny 120
        
        Loại thời tiết có sẵn:
        • sunny - Nắng (tăng tốc độ sinh trưởng)
        • rainy - Mưa (tăng sản lượng)
        • cloudy - Có mây (bình thường)
        • windy - Có gió (tăng sinh trưởng nhẹ)
        • storm - Bão (giảm hiệu suất)
        • foggy - Sương mù (giảm năng suất)
        • drought - Hạn hán (giảm mạnh hiệu suất)
        """
        try:
            # Validate weather type
            valid_weather = ["sunny", "rainy", "cloudy", "windy", "storm", "foggy", "drought"]
            
            if not weather_type:
                weather_list = "\n".join([f"• `{w}` - {self._get_weather_description(w)}" for w in valid_weather])
                embed = discord.Embed(
                    title="🌤️ Danh Sách Thời Tiết",
                    description=f"**Sử dụng:** `f!force_weather <loại> [phút]`\n\n{weather_list}",
                    color=0x87CEEB
                )
                await ctx.send(embed=embed)
                return
            
            if weather_type.lower() not in valid_weather:
                await ctx.send(f"❌ Loại thời tiết không hợp lệ! Sử dụng: {', '.join(valid_weather)}")
                return
            
            if not (15 <= duration <= 360):  # 15 phút đến 6 giờ
                await ctx.send("❌ Thời gian phải từ 15-360 phút (6 giờ)!")
                return
            
            # Create forced weather decision
            weather_type = weather_type.lower()
            
            embed = discord.Embed(
                title="⚡ Admin Override - Thay Đổi Thời Tiết",
                description=f"**Admin:** {ctx.author.mention}\n"
                           f"**Thời tiết mới:** {weather_type.title()} {self._get_weather_emoji(weather_type)}\n"
                           f"**Thời gian:** {duration} phút\n"
                           f"**Lý do:** Admin force command",
                color=0xFFD700
            )
            
            # Execute weather change through Game Master
            success = await self._execute_admin_weather_change(weather_type, duration)
            
            if success:
                embed.add_field(
                    name="✅ Thành Công",
                    value=f"Thời tiết đã được thay đổi thành **{weather_type}** trong {duration} phút!",
                    inline=False
                )
                embed.color = 0x00FF00
                
                # Notify all channels about admin weather change
                await self._notify_admin_weather_change(ctx.bot, weather_type, duration, ctx.author)
            else:
                embed.add_field(
                    name="❌ Thất Bại",
                    value="Không thể thay đổi thời tiết. Vui lòng kiểm tra logs.",
                    inline=False
                )
                embed.color = 0xFF0000
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in force_weather command: {e}")
            await ctx.send(f"❌ Lỗi khi thay đổi thời tiết: {str(e)}")

    @commands.command(name='force_event', aliases=['fe'])
    @commands.has_permissions(administrator=True)
    async def force_event(self, ctx, event_type: str = None, duration: int = 120):
        """🎉 Buộc Gemini tạo event mới ngay lập tức
        
        Sử dụng: f!force_event <loại_event> [thời_gian_phút]
        Ví dụ: f!force_event harvest_bonus 180
        
        Loại event có sẵn:
        • harvest_bonus - Tăng 50% sản lượng thu hoạch
        • double_exp - Tăng gấp đôi exp từ hoạt động
        • market_boost - Tăng 30% giá bán nông sản
        • rain_blessing - Tất cả cây tưới nước tự động
        • golden_hour - Tăng 25% tốc độ sinh trưởng
        • lucky_day - Tăng chance drop item hiếm
        • speed_growth - Tăng 40% tốc độ lớn
        • mega_yield - Tăng 100% sản lượng (hiếm)
        """
        try:
            # Validate event type
            valid_events = [
                "harvest_bonus", "double_exp", "market_boost", "rain_blessing",
                "golden_hour", "lucky_day", "speed_growth", "mega_yield"
            ]
            
            if not event_type:
                event_list = "\n".join([f"• `{e}` - {self._get_event_description(e)}" for e in valid_events])
                embed = discord.Embed(
                    title="🎉 Danh Sách Event",
                    description=f"**Sử dụng:** `f!force_event <loại> [phút]`\n\n{event_list}",
                    color=0xFF6B6B
                )
                await ctx.send(embed=embed)
                return
            
            if event_type.lower() not in valid_events:
                await ctx.send(f"❌ Loại event không hợp lệ! Sử dụng: {', '.join(valid_events)}")
                return
            
            if not (30 <= duration <= 720):  # 30 phút đến 12 giờ
                await ctx.send("❌ Thời gian phải từ 30-720 phút (12 giờ)!")
                return
            
            # Create forced event decision
            event_type = event_type.lower()
            
            embed = discord.Embed(
                title="⚡ Admin Override - Tạo Event Mới",
                description=f"**Admin:** {ctx.author.mention}\n"
                           f"**Event:** {event_type.replace('_', ' ').title()} {self._get_event_emoji(event_type)}\n"
                           f"**Thời gian:** {duration} phút\n"
                           f"**Lý do:** Admin force command",
                color=0xFF6B6B
            )
            
            # Execute event creation through Game Master
            success = await self._execute_admin_event_creation(event_type, duration)
            
            if success:
                embed.add_field(
                    name="✅ Thành Công",
                    value=f"Event **{event_type.replace('_', ' ').title()}** đã được tạo trong {duration} phút!",
                    inline=False
                )
                embed.color = 0x00FF00
                
                # Notify all channels about admin event
                await self._notify_admin_event_creation(ctx.bot, event_type, duration, ctx.author)
            else:
                embed.add_field(
                    name="❌ Thất Bại", 
                    value="Không thể tạo event. Vui lòng kiểm tra logs.",
                    inline=False
                )
                embed.color = 0xFF0000
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in force_event command: {e}")
            await ctx.send(f"❌ Lỗi khi tạo event: {str(e)}")

    @commands.command(name='emergency', aliases=['em'])
    @commands.has_permissions(administrator=True)
    async def emergency_mode(self, ctx):
        """🚨 Bật/tắt chế độ khẩn cấp của Gemini Game Master
        
        Chế độ khẩn cấp:
        • Phân tích mỗi 5 phút thay vì 15 phút
        • Cho phép 20 quyết định/giờ thay vì 8
        • Ưu tiên can thiệp economic và balance issues
        """
        try:
            # Toggle emergency mode
            self.game_master.toggle_emergency_mode()
            
            is_emergency = self.game_master.emergency_mode
            
            embed = discord.Embed(
                title="🚨 Chế Độ Khẩn Cấp",
                description=f"**Admin:** {ctx.author.mention}\n"
                           f"**Trạng thái:** {'🚨 KÍCH HOẠT' if is_emergency else '✅ TẮT'}",
                color=0xFF0000 if is_emergency else 0x00FF00
            )
            
            if is_emergency:
                embed.add_field(
                    name="⚡ Chế Độ Khẩn Cấp ACTIVE",
                    value="• Phân tích mỗi **5 phút**\n"
                          "• Tối đa **20 quyết định/giờ**\n"
                          "• Ưu tiên can thiệp **critical issues**\n"
                          "• Tự động phát hiện và xử lý **emergency situations**",
                    inline=False
                )
            else:
                embed.add_field(
                    name="✅ Chế Độ Bình Thường",
                    value="• Phân tích mỗi **15 phút**\n"
                          "• Tối đa **8 quyết định/giờ**\n"
                          "• Hoạt động **standard mode**\n"
                          "• Cân bằng game theo **normal parameters**",
                    inline=False
                )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in emergency_mode command: {e}")
            await ctx.send(f"❌ Lỗi khi chuyển đổi emergency mode: {str(e)}")

    @commands.command(name='analyze', aliases=['an'])
    @commands.has_permissions(administrator=True)
    async def force_analysis(self, ctx):
        """🔍 Buộc Gemini phân tích và ra quyết định ngay lập tức
        
        Bỏ qua cooldown 15 phút và ép buộc Game Master phân tích tình hình game,
        sau đó đưa ra quyết định can thiệp nếu cần thiết.
        """
        try:
            embed = discord.Embed(
                title="🔍 Force Analysis Initiated",
                description=f"**Admin:** {ctx.author.mention}\n"
                           f"**Thời gian:** {datetime.now().strftime('%H:%M:%S')}\n"
                           f"**Trạng thái:** Đang phân tích...",
                color=0xFFB347
            )
            
            initial_msg = await ctx.send(embed=embed)
            
            # Execute force analysis
            decision = await self.game_master.force_analysis(ctx.bot)
            
            # Update embed with results
            if decision:
                embed.title = "✅ Analysis Completed - Action Taken"
                embed.color = 0x00FF00
                embed.add_field(
                    name="🎯 Quyết Định AI",
                    value=f"**Action:** {decision.action_type.replace('_', ' ').title()}\n"
                          f"**Confidence:** {decision.confidence:.1%}\n"
                          f"**Priority:** {decision.priority.upper()}\n"
                          f"**Reasoning:** {decision.reasoning[:100]}...",
                    inline=False
                )
                
                if hasattr(decision, 'parameters') and decision.parameters:
                    params = []
                    for key, value in decision.parameters.items():
                        if key not in ['duration_hours']:
                            params.append(f"• {key}: {value}")
                    
                    if params:
                        embed.add_field(
                            name="⚙️ Parameters",
                            value="\n".join(params[:5]),  # Limit to 5 params
                            inline=True
                        )
            else:
                embed.title = "ℹ️ Analysis Completed - No Action Needed"
                embed.color = 0x3498DB
                embed.add_field(
                    name="📊 Kết Quả",
                    value="Game đang ở trạng thái cân bằng.\n"
                          "Không cần can thiệp tại thời điểm này.",
                    inline=False
                )
            
            embed.set_footer(text=f"Analysis completed at {datetime.now().strftime('%H:%M:%S')}")
            await initial_msg.edit(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in force_analysis command: {e}")
            await ctx.send(f"❌ Lỗi khi force analysis: {str(e)}")

    # Helper methods for admin commands
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
        return emojis.get(weather_type, "🌤️")
    
    def _get_weather_description(self, weather_type: str) -> str:
        """Get description for weather type"""
        descriptions = {
            "sunny": "Nắng (tăng tốc độ sinh trưởng)",
            "rainy": "Mưa (tăng sản lượng)",
            "cloudy": "Có mây (bình thường)",
            "windy": "Có gió (tăng sinh trưởng nhẹ)",
            "storm": "Bão (giảm hiệu suất)",
            "foggy": "Sương mù (giảm năng suất)",
            "drought": "Hạn hán (giảm mạnh hiệu suất)"
        }
        return descriptions.get(weather_type, "Không rõ")
    
    def _get_event_emoji(self, event_type: str) -> str:
        """Get emoji for event type"""
        emojis = {
            "harvest_bonus": "🌾",
            "double_exp": "⭐",
            "market_boost": "💰",
            "rain_blessing": "💧",
            "golden_hour": "✨",
            "lucky_day": "🍀",
            "speed_growth": "⚡",
            "mega_yield": "💎"
        }
        return emojis.get(event_type, "🎉")
    
    def _get_event_description(self, event_type: str) -> str:
        """Get description for event type"""
        descriptions = {
            "harvest_bonus": "Tăng 50% sản lượng thu hoạch",
            "double_exp": "Tăng gấp đôi exp từ hoạt động",
            "market_boost": "Tăng 30% giá bán nông sản",
            "rain_blessing": "Tất cả cây tưới nước tự động",
            "golden_hour": "Tăng 25% tốc độ sinh trưởng",
            "lucky_day": "Tăng chance drop item hiếm",
            "speed_growth": "Tăng 40% tốc độ lớn",
            "mega_yield": "Tăng 100% sản lượng (hiếm)"
        }
        return descriptions.get(event_type, "Event đặc biệt")
    
    async def _execute_admin_weather_change(self, weather_type: str, duration_minutes: int) -> bool:
        """Execute admin-forced weather change"""
        try:
            # Get weather cog and change weather
            weather_cog = self.game_master.bot.get_cog('WeatherCog') if hasattr(self.game_master, 'bot') else None
            
            if weather_cog:
                duration_hours = duration_minutes / 60
                success = await weather_cog.set_weather(weather_type, duration_hours)
                logger.info(f"Admin forced weather change: {weather_type} for {duration_minutes} minutes")
                return success
            else:
                logger.error("WeatherCog not found for admin weather change")
                return False
                
        except Exception as e:
            logger.error(f"Error executing admin weather change: {e}")
            return False
    
    async def _execute_admin_event_creation(self, event_type: str, duration_minutes: int) -> bool:
        """Execute admin-forced event creation"""
        try:
            # Get events cog and create event
            events_cog = self.game_master.bot.get_cog('EventsCog') if hasattr(self.game_master, 'bot') else None
            
            if events_cog:
                duration_hours = duration_minutes / 60
                success = await events_cog.create_admin_event(event_type, duration_hours)
                logger.info(f"Admin forced event creation: {event_type} for {duration_minutes} minutes")
                return success
            else:
                logger.error("EventsCog not found for admin event creation")
                return False
                
        except Exception as e:
            logger.error(f"Error executing admin event creation: {e}")
            return False
    
    async def _notify_admin_weather_change(self, bot, weather_type: str, duration_minutes: int, admin_user):
        """Notify all channels about admin weather change"""
        # Implementation would depend on notification system
        pass
    
    async def _notify_admin_event_creation(self, bot, event_type: str, duration_minutes: int, admin_user):
        """Helper to create and send admin event notification"""
        # (Implementation details omitted for brevity)
        pass

async def setup(bot):
    """Setup function to add the cog to the bot"""
    # This assumes you have a 'game_master' instance available on the bot
    # If not, you'll need to initialize it here or in the bot's setup_hook
    if hasattr(bot, 'game_master'):
        await bot.add_cog(GeminiGameMasterCog(bot.game_master))
        logger.info("✅ GeminiGameMasterCog loaded")
    else:
        logger.error("❌ Cannot load GeminiGameMasterCog: 'game_master' instance not found on bot.") 