"""
State Admin Commands - Admin commands để quản lý bot state
"""

import discord
from discord.ext import commands
from datetime import datetime, timedelta
from utils.embeds import EmbedBuilder
from utils.state_manager import StateManager
import json

class StateAdminCog(commands.Cog):
    """Admin commands để quản lý bot state"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='state_status', aliases=['trangthai'])
    @commands.has_permissions(administrator=True)
    async def state_status(self, ctx):
        """Xem trạng thái hiện tại của hệ thống (Admin only)
        
        Sử dụng: f!state_status
        """
        try:
            state_manager = StateManager(self.bot.db)
            all_states = await state_manager.get_all_states()
            
            embed = EmbedBuilder.create_base_embed(
                "🔧 Trạng thái hệ thống",
                "Thông tin về trạng thái persistence các module",
                color=0x3498db
            )
            
            # Weather System Status
            weather_state = all_states.get('weather_cycle', {})
            if weather_state:
                next_change = weather_state.get('next_weather_change')
                current_weather = weather_state.get('current_weather', {})
                
                if next_change:
                    time_remaining = next_change - datetime.now()
                    hours = int(time_remaining.total_seconds() // 3600)
                    minutes = int((time_remaining.total_seconds() % 3600) // 60)
                    next_change_str = f"Sau {hours}h {minutes}m"
                else:
                    next_change_str = "Chưa đặt"
                
                weather_type = current_weather.get('type', 'Chưa xác định')
                
                embed.add_field(
                    name="🌤️ Weather System",
                    value=f"Trạng thái: ✅ Đã lưu\n"
                          f"Thời tiết hiện tại: {weather_type}\n"
                          f"Thay đổi tiếp theo: {next_change_str}",
                    inline=True
                )
            else:
                embed.add_field(
                    name="🌤️ Weather System", 
                    value="Trạng thái: ❌ Chưa có dữ liệu",
                    inline=True
                )
            
            # Event System Status
            event_state = all_states.get('event_system', {})
            if event_state:
                current_event = event_state.get('current_event')
                event_end_time = event_state.get('event_end_time')
                
                if current_event:
                    event_name = current_event.get('data', {}).get('name', 'Unknown')
                    
                    if event_end_time:
                        time_remaining = event_end_time - datetime.now()
                        hours = int(time_remaining.total_seconds() // 3600)
                        minutes = int((time_remaining.total_seconds() % 3600) // 60)
                        end_time_str = f"Kết thúc sau {hours}h {minutes}m"
                    else:
                        end_time_str = "Chưa xác định"
                    
                    embed.add_field(
                        name="🎪 Event System",
                        value=f"Trạng thái: ✅ Có sự kiện\n"
                              f"Sự kiện: {event_name}\n"
                              f"{end_time_str}",
                        inline=True
                    )
                else:
                    embed.add_field(
                        name="🎪 Event System",
                        value="Trạng thái: ✅ Không có sự kiện",
                        inline=True
                    )
            else:
                embed.add_field(
                    name="🎪 Event System",
                    value="Trạng thái: ❌ Chưa có dữ liệu", 
                    inline=True
                )
            
            # System Uptime
            system_uptime = all_states.get('system_uptime')
            if system_uptime:
                total_seconds = int(system_uptime.total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                uptime_str = f"{hours}h {minutes}m"
            else:
                uptime_str = "Chưa xác định"
            
            embed.add_field(
                name="⏱️ System Info",
                value=f"Uptime: {uptime_str}\n"
                      f"Database: ✅ Kết nối\n"
                      f"State Manager: ✅ Hoạt động",
                inline=False
            )
            
            embed.set_footer(text="Dữ liệu được lưu tự động, bảo đảm không mất khi restart")
            embed.timestamp = datetime.now()
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            embed = EmbedBuilder.create_error_embed(
                f"Lỗi khi lấy trạng thái hệ thống: {e}"
            )
            await ctx.send(embed=embed)
    
    @commands.command(name='reset_weather_state', aliases=['reset_thoitiet'])
    @commands.has_permissions(administrator=True)
    async def reset_weather_state(self, ctx):
        """Reset trạng thái weather system (Admin only)
        
        Sử dụng: f!reset_weather_state
        """
        try:
            # Get weather cog
            weather_cog = self.bot.get_cog('WeatherCog')
            if not weather_cog:
                await ctx.send("❌ Weather module không được tải!")
                return
            
            # Reset state
            weather_cog.next_weather_change = datetime.now() + timedelta(seconds=weather_cog.weather_change_duration)
            weather_cog.current_weather = None
            
            # Save new state
            await weather_cog._save_weather_state()
            
            embed = EmbedBuilder.create_success_embed(
                "🔄 Weather state đã được reset!",
                f"Chu kỳ thời tiết mới sẽ bắt đầu sau {weather_cog.weather_change_duration // 60} phút."
            )
            await ctx.send(embed=embed)
            
        except Exception as e:
            embed = EmbedBuilder.create_error_embed(
                f"Lỗi khi reset weather state: {e}"
            )
            await ctx.send(embed=embed)
    
    @commands.command(name='clear_event_state', aliases=['clear_sukien'])
    @commands.has_permissions(administrator=True)
    async def clear_event_state(self, ctx):
        """Xóa sự kiện hiện tại (Admin only)
        
        Sử dụng: f!clear_event_state
        """
        try:
            # Get events cog
            events_cog = self.bot.get_cog('EventsCog')
            if not events_cog:
                await ctx.send("❌ Events module không được tải!")
                return
            
            # Clear current event
            current_event_name = "None"
            if events_cog.current_event:
                current_event_name = events_cog.current_event.get('data', {}).get('name', 'Unknown')
            
            events_cog.current_event = None
            events_cog.event_end_time = None
            
            # Save cleared state
            await events_cog._save_event_state()
            
            embed = EmbedBuilder.create_success_embed(
                "🗑️ Event state đã được xóa!",
                f"Sự kiện '{current_event_name}' đã được kết thúc sớm."
            )
            await ctx.send(embed=embed)
            
        except Exception as e:
            embed = EmbedBuilder.create_error_embed(
                f"Lỗi khi clear event state: {e}"
            )
            await ctx.send(embed=embed)
    
    @commands.command(name='force_weather_change', aliases=['force_thoitiet'])
    @commands.has_permissions(administrator=True) 
    async def force_weather_change(self, ctx):
        """Ép buộc thay đổi thời tiết ngay lập tức (Admin only)
        
        Sử dụng: f!force_weather_change
        """
        try:
            # Get weather cog
            weather_cog = self.bot.get_cog('WeatherCog')
            if not weather_cog:
                await ctx.send("❌ Weather module không được tải!")
                return
            
            # Force weather change
            old_weather_type = None
            if weather_cog.current_weather:
                old_weather_type = weather_cog.current_weather.get('type', 'unknown')
            
            # Apply new AI weather
            prediction = await weather_cog.apply_ai_weather()
            
            if prediction:
                new_weather_type = prediction['weather']
                
                # Set next change time
                weather_cog.next_weather_change = datetime.now() + timedelta(seconds=weather_cog.weather_change_duration)
                
                # Save state
                await weather_cog._save_weather_state()
                
                embed = EmbedBuilder.create_success_embed(
                    "⚡ Thời tiết đã được thay đổi ép buộc!",
                    f"Từ: {old_weather_type or 'Unknown'}\n"
                    f"Sang: {new_weather_type}\n"
                    f"Lý do AI: {prediction.get('reasoning', 'Không có')}"
                )
                
                # Notify all servers
                await weather_cog._notify_ai_weather_change(old_weather_type, new_weather_type, prediction)
                
            else:
                embed = EmbedBuilder.create_error_embed(
                    "❌ Không thể thay đổi thời tiết. AI prediction thất bại."
                )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            embed = EmbedBuilder.create_error_embed(
                f"Lỗi khi force weather change: {e}"
            )
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(StateAdminCog(bot)) 