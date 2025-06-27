"""
Livestock Overview System
Unified view của tất cả livestock (pond + barn)
"""

import discord
from discord.ext import commands
from datetime import datetime, timedelta
import asyncio
from typing import Optional, List, Dict

import config
from database.database import Database
from database.models import Species, UserLivestock, UserFacilities
from utils.embeds import EmbedBuilder
from utils.livestock_helpers import (
    calculate_livestock_maturity, get_livestock_display_info,
    get_livestock_weather_modifier, can_collect_product, 
    get_product_ready_time
)

class LivestockCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database(config.DATABASE_PATH)
    
    async def cog_load(self):
        """Initialize database connection when cog loads"""
        await self.db.init_db()
    
    async def cog_unload(self):
        """Close database connection when cog unloads"""
        await self.db.close()
    
    def get_current_modifiers(self):
        """Get current weather and event modifiers"""
        # Get weather modifier
        weather_cog = self.bot.get_cog('WeatherCog')
        weather_modifier = 1.0
        current_weather = "sunny"
        
        if weather_cog and hasattr(weather_cog, 'current_weather'):
            current_weather = weather_cog.current_weather
            weather_modifier = get_livestock_weather_modifier(current_weather, 'fish')  # Average
        
        # Get event modifier
        events_cog = self.bot.get_cog('EventsCog')
        event_growth_modifier = 1.0
        
        if events_cog:
            event_growth_modifier = events_cog.get_current_growth_modifier()
        
        return weather_modifier, event_growth_modifier, current_weather
    
    @commands.command(name='livestock', aliases=['thucung', 'overview'])
    async def livestock_overview(self, ctx):
        """🐟🐄 Tổng quan chăn nuôi - Xem tổng quan tất cả ao cá và chuồng trại
        
        Hiển thị thông tin tổng hợp về:
        • Trạng thái ao cá và chuồng trại
        • Số lượng động vật trưởng thành
        • Sản phẩm sẵn sàng thu thập
        • Tổng giá trị ước tính
        
        Sử dụng: f!livestock
        """
        user_id = ctx.author.id
        
        try:
            # Get user and facilities
            user = await self.db.get_user(user_id)
            if not user:
                await ctx.send(embed=EmbedBuilder.create_error_embed("❌ Bạn chưa đăng ký! Sử dụng `f!register` để bắt đầu."))
                return
            
            facilities = await self.db.get_user_facilities(user_id)
            
            # Get all livestock
            pond_livestock = await self.db.get_user_livestock(user_id, 'pond')
            barn_livestock = await self.db.get_user_livestock(user_id, 'barn')
            
            # Get modifiers
            weather_modifier, event_growth_modifier, current_weather = self.get_current_modifiers()
            
            # Create main embed
            embed = EmbedBuilder.create_base_embed(
                title=f"🐟🐄 Tổng Quan Chăn Nuôi - {ctx.author.display_name}",
                description=f"**Thời tiết:** {current_weather.title()} (×{weather_modifier:.1f})\n"
                           f"**Modifier sự kiện:** ×{event_growth_modifier:.1f}"
            )
            
            # === POND SECTION ===
            pond_info = self._get_facility_summary(
                pond_livestock, facilities.pond_slots, facilities.pond_level,
                weather_modifier, event_growth_modifier, 'pond'
            )
            
            embed.add_field(
                name="🐟 **AO CÁ**",
                value=f"**Cấp độ:** {facilities.pond_level}/6 | **Ô:** {pond_info['occupied']}/{facilities.pond_slots}\n"
                      f"**Trưởng thành:** {pond_info['mature']}/{pond_info['total']}\n"
                      f"**Giá trị ước tính:** {pond_info['estimated_value']:,}🪙",
                inline=False
            )
            
            # === BARN SECTION ===
            barn_info = self._get_facility_summary(
                barn_livestock, facilities.barn_slots, facilities.barn_level,
                weather_modifier, event_growth_modifier, 'barn'
            )
            
            embed.add_field(
                name="🐄 **CHUỒNG TRẠI**",
                value=f"**Cấp độ:** {facilities.barn_level}/6 | **Ô:** {barn_info['occupied']}/{facilities.barn_slots}\n"
                      f"**Trưởng thành:** {barn_info['mature']}/{barn_info['total']}\n"
                      f"**Sản phẩm sẵn sàng:** {barn_info['products_ready']}\n"
                      f"**Giá trị ước tính:** {barn_info['estimated_value']:,}🪙",
                inline=False
            )
            
            # === TOTAL SUMMARY ===
            total_livestock = pond_info['total'] + barn_info['total']
            total_mature = pond_info['mature'] + barn_info['mature']
            total_value = pond_info['estimated_value'] + barn_info['estimated_value']
            
            embed.add_field(
                name="📊 **TỔNG KẾT**",
                value=f"**Tổng số:** {total_livestock} con\n"
                      f"**Sẵn sàng thu hoạch:** {total_mature} con\n"
                      f"**Tổng giá trị:** {total_value:,}🪙\n"
                      f"**Sản phẩm chờ thu thập:** {barn_info['products_ready']}",
                inline=False
            )
            
            # Add quick action buttons info
            embed.add_field(
                name="⚡ **HÀNH ĐỘNG NHANH**",
                value="`f!pond` - Quản lý ao cá\n"
                      "`f!barn` - Quản lý chuồng trại\n"
                      "`f!harvestall` - Thu hoạch tất cả\n"
                      "`f!collectall` - Thu thập tất cả sản phẩm",
                inline=False
            )
            
            # Color coding based on status
            if total_mature > 0 or barn_info['products_ready'] > 0:
                embed.color = 0x00ff00  # Green - có thể thu hoạch
            elif total_livestock > 0:
                embed.color = 0xffff00  # Yellow - đang nuôi
            else:
                embed.color = 0xff0000  # Red - trống
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(embed=EmbedBuilder.create_error_embed(f"❌ Lỗi hiển thị tổng quan: {str(e)}"))
    
    def _get_facility_summary(self, livestock_list: List[UserLivestock], 
                             max_slots: int, level: int,
                             weather_modifier: float, event_growth_modifier: float,
                             facility_type: str) -> Dict:
        """Get summary statistics for a facility"""
        total = len(livestock_list)
        mature = 0
        estimated_value = 0
        products_ready = 0
        
        for livestock in livestock_list:
            # Check maturity
            is_mature, _ = calculate_livestock_maturity(
                livestock, weather_modifier, event_growth_modifier
            )
            
            if is_mature:
                mature += 1
                
                # Get species for value calculation
                species_config = None
                if facility_type == 'pond' and livestock.species_id in config.FISH_SPECIES:
                    species_config = config.FISH_SPECIES[livestock.species_id]
                elif facility_type == 'barn' and livestock.species_id in config.ANIMAL_SPECIES:
                    species_config = config.ANIMAL_SPECIES[livestock.species_id]
                
                if species_config:
                    estimated_value += species_config['sell_price']
            
            # Check products (barn only)
            if facility_type == 'barn' and can_collect_product(livestock):
                products_ready += 1
        
        return {
            'total': total,
            'occupied': total,
            'mature': mature,
            'estimated_value': estimated_value,
            'products_ready': products_ready
        }

async def setup(bot):
    await bot.add_cog(LivestockCog(bot))