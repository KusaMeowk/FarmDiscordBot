"""
Pond System - Nuôi cá
Quản lý ao cá, mua/bán cá, thu hoạch cá
"""

import discord
from discord.ext import commands
from datetime import datetime, timedelta
import asyncio
from typing import Optional, List, Dict, Any

import config
from database.database import Database
from database.models import Species, UserLivestock, UserFacilities
from utils.embeds import EmbedBuilder
from utils.livestock_helpers import (
    calculate_livestock_maturity, get_livestock_display_info,
    get_livestock_weather_modifier, validate_facility_slot,
    get_available_species_for_purchase, format_livestock_value,
    calculate_livestock_value, get_weather_modifier
)
# Remove direct imports to avoid circular imports

class PondCog(commands.Cog):
    """Pond management system for fish farming"""
    
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
    
    @commands.group(name='pond', aliases=['ao'], invoke_without_command=True)
    async def pond(self, ctx):
        """🐟 Quản lý ao cá - Xem trạng thái ao cá của bạn
        
        Subcommands:
        • f!pond buy <loại_cá> [số_lượng] - Mua cá cho ao
        • f!pond harvest [ô] - Thu hoạch cá đã trưởng thành
        • f!pond upgrade - Nâng cấp ao cá
        
        Sử dụng: f!pond
        """
        await self.show_pond(ctx)
    
    @pond.command(name='buy', aliases=['mua'])
    async def buy_fish(self, ctx, fish_type: str = None, quantity: int = 1):
        """🛒 Mua cá cho ao - Mua các loại cá để nuôi trong ao
        
        Sử dụng: f!pond buy [loại_cá] [số_lượng]
        Ví dụ: f!pond buy carp 2
        """
        await self.buy_fish_command(ctx, fish_type, quantity)
    
    @pond.command(name='harvest', aliases=['thu'])
    async def harvest_fish(self, ctx, slot: str = None):
        """🎣 Thu hoạch cá - Thu hoạch cá đã trưởng thành từ ao
        
        Sử dụng: f!pond harvest [số_ô]
        Ví dụ: f!pond harvest 1
        """
        await self.harvest_fish_command(ctx, slot)
    
    @pond.command(name='upgrade', aliases=['nangcap'])
    async def upgrade_pond(self, ctx):
        """⬆️ Nâng cấp ao cá - Tăng số lượng ô nuôi cá
        
        Sử dụng: f!pond upgrade
        """
        await self.upgrade_pond_command(ctx)
    
    async def show_pond(self, ctx):
        """Display pond status with fish information"""
        try:
            user_id = ctx.author.id
            
            # Check if user is registered
            user = await self.db.get_user(user_id)
            if not user:
                await ctx.send(embed=EmbedBuilder.create_error_embed("❌ Bạn chưa đăng ký! Sử dụng `f!register` để bắt đầu."))
                return
            
            # Get user facilities
            facilities = await self.db.get_user_facilities(user_id)
            if not facilities:
                # Create default facilities
                facilities = await self.db.create_user_facilities(user_id)
            
            # Get fish in pond
            fish_list = await self.db.get_user_livestock(user_id, 'pond')
            
            # Get current weather modifier
            weather_modifier = 1.0
            current_weather = "sunny"
            try:
                weather_cog = self.bot.get_cog('WeatherCog')
                if weather_cog and hasattr(weather_cog, 'current_weather'):
                    current_weather_data = weather_cog.current_weather
                    # Extract weather type from dict or use as string
                    if isinstance(current_weather_data, dict):
                        current_weather = current_weather_data.get('type', 'sunny')
                    else:
                        current_weather = current_weather_data
                    # Get weather modifier
                    from utils.livestock_helpers import get_livestock_weather_modifier
                    weather_modifier = get_livestock_weather_modifier(current_weather, 'fish')
            except Exception as e:
                print(f"Weather error: {e}")
                pass
            
            # Get event modifier
            event_modifier = 1.0
            try:
                events_cog = self.bot.get_cog('EventsCog')
                if events_cog and hasattr(events_cog, 'get_current_growth_modifier'):
                    event_modifier = events_cog.get_current_growth_modifier()
            except:
                pass
            
            total_modifier = weather_modifier * event_modifier
            
            # Create embed
            embed = EmbedBuilder.create_base_embed(
                title=f"🐟 Ao Cá của {ctx.author.display_name}",
                description=f"**Cấp độ:** {facilities.pond_level} | **Số ô:** {facilities.pond_slots}/6\n"
                           f"**Thời tiết:** {current_weather.title()} (×{weather_modifier:.1f})",
                color=0x1e90ff
            )
            
            # Show pond slots
            pond_display = []
            for i in range(facilities.pond_slots):
                slot_fish = next((f for f in fish_list if f.facility_slot == i), None)
                if slot_fish:
                    # Get fish species info
                    species = await self.db.get_species(slot_fish.species_id)
                    if species:
                        # Check if mature
                        is_mature, _ = calculate_livestock_maturity(
                            slot_fish, total_modifier, 1.0
                        )
                        
                        if is_mature:
                            status = "✨ Có thể thu hoạch"
                            status_icon = "✨"
                        else:
                            # Calculate remaining time
                            elapsed = (datetime.now() - slot_fish.birth_time).total_seconds()
                            adjusted_growth_time = species.growth_time / total_modifier
                            remaining = max(0, adjusted_growth_time - elapsed)
                            
                            if remaining > 0:
                                mins = int(remaining // 60)
                                secs = int(remaining % 60)
                                status = f"⏰ {mins}p {secs}s"
                                status_icon = "🐟"
                            else:
                                status = "✨ Có thể thu hoạch"
                                status_icon = "✨"
                        
                        pond_display.append(f"**Ô {i+1}:** {status_icon} {species.name}")
                    else:
                        pond_display.append(f"**Ô {i+1}:** ❌ Lỗi dữ liệu")
                else:
                    pond_display.append(f"**Ô {i+1}:** ⬜ Trống")
            
            if pond_display:
                embed.add_field(
                    name="🗺️ Trạng thái ao cá",
                    value="\n".join(pond_display),
                    inline=False
                )
            
            # Add statistics
            ready_count = 0
            for f in fish_list:
                if f:
                    species = await self.db.get_species(f.species_id)
                    if species:
                        is_mature, _ = calculate_livestock_maturity(f, total_modifier, 1.0)
                        if is_mature:
                            ready_count += 1
            
            embed.add_field(
                name="📊 Thống kê",
                value=f"🐟 Tổng cá: {len(fish_list)}/{facilities.pond_slots}\n"
                      f"✨ Sẵn sàng: {ready_count}\n"
                      f"💰 Số dư: {user.money:,} coins",
                inline=True
            )
            
            # Add upgrade info
            if facilities.pond_level < 6:
                next_level = facilities.pond_level + 1
                upgrade_cost = config.POND_UPGRADE_COSTS.get(next_level, 0)
                embed.add_field(
                    name="⬆️ Nâng cấp",
                    value=f"Cấp {next_level}: +2 ô\n💰 Chi phí: {upgrade_cost:,} coins",
                    inline=True
                )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            # Enhanced error logging for debugging
            error_msg = f"❌ Lỗi hiển thị ao: {str(e)}"
            print(f"\n🐛 POND ERROR DEBUG:")
            print(f"Error: {e}")
            print(f"Type: {type(e).__name__}")
            
            if "unhashable" in str(e).lower():
                import traceback
                import sys
                print(f"🔍 UNHASHABLE TYPE ERROR DETECTED!")
                print(f"Full traceback:")
                traceback.print_exc()
                
                # Try to identify the problematic line
                tb = sys.exc_info()[2]
                while tb.tb_next:
                    tb = tb.tb_next
                print(f"Error at line {tb.tb_lineno} in {tb.tb_frame.f_code.co_filename}")
                print(f"Local variables: {tb.tb_frame.f_locals}")
            
            await ctx.send(embed=EmbedBuilder.create_error_embed(error_msg))
    
    async def buy_fish_command(self, ctx, fish_type: str = None, quantity: int = 1):
        """Handle fish purchase"""
        try:
            user_id = ctx.author.id
            
            # Check if user is registered
            user = await self.db.get_user(user_id)
            if not user:
                await ctx.send(embed=EmbedBuilder.create_error_embed("❌ Bạn chưa đăng ký! Sử dụng `f!register` để bắt đầu."))
                return
            
            # If no fish type specified, show shop
            if not fish_type:
                await self.show_fish_shop(ctx)
                return
            
            # Validate quantity
            if quantity < 1 or quantity > 10:
                quantity = 1
            
            # Get facilities
            facilities = await self.db.get_user_facilities(user_id)
            if not facilities:
                facilities = await self.db.create_user_facilities(user_id)
            
            # Check available slots
            current_fish = await self.db.get_user_livestock(user_id, 'pond')
            available_slots = facilities.pond_slots - len(current_fish)
            
            if available_slots < quantity:
                await ctx.send(embed=EmbedBuilder.create_error_embed(
                    f"❌ Không đủ chỗ trong ao! Còn trống: {available_slots} ô"
                ))
                return
            
            # Find fish species
            fish_species = None
            species_id = None
            for species_id, species_data in config.FISH_SPECIES.items():
                if (fish_type.lower() in species_data['name'].lower() or 
                    fish_type.lower() == species_id or
                    fish_type.lower() in species_data.get('aliases', [])):
                    fish_species = species_data
                    break
            
            if not fish_species:
                await ctx.send(embed=EmbedBuilder.create_error_embed(f"❌ Không tìm thấy loại cá `{fish_type}`!"))
                return
            
            # Check if user has enough money
            total_cost = fish_species['buy_price'] * quantity
            if user.money < total_cost:
                await ctx.send(embed=EmbedBuilder.create_error_embed(
                    f"❌ Không đủ tiền! Cần: {total_cost:,} coins, có: {user.money:,} coins"
                ))
                return
            
            # Find available slots
            used_slots = {f.facility_slot for f in current_fish}
            available_slot_indices = [i for i in range(facilities.pond_slots) if i not in used_slots]
            
            if len(available_slot_indices) < quantity:
                await ctx.send(embed=EmbedBuilder.create_error_embed(
                    f"❌ Không đủ chỗ trong ao! Còn trống: {len(available_slot_indices)} ô"
                ))
                return
            
            # Purchase fish
            purchased_slots = []
            for i in range(quantity):
                slot_index = available_slot_indices[i]
                
                # Add fish to database  
                livestock_id = await self.db.add_livestock(
                    user_id=user_id,
                    species_id=species_id,
                    facility_type='pond',
                    facility_slot=slot_index,
                    birth_time=datetime.now()
                )
                
                if livestock_id:
                    purchased_slots.append(slot_index + 1)  # Display as 1-indexed
            
            if purchased_slots:
                # Deduct money
                await self.db.update_user_money(user_id, -total_cost)
                
                # Create success embed
                embed = EmbedBuilder.create_success_embed(
                    title="🐟 Mua cá thành công!",
                    message=f"**Đã mua:** {quantity}x {fish_species['name']}\n"
                           f"**Vị trí:** Ô {', '.join(map(str, purchased_slots))}\n"
                           f"**Chi phí:** {total_cost:,} coins\n"
                           f"**Thời gian lớn:** {fish_species['growth_time'] // 60} phút"
                )
                embed.color = 0x1e90ff
                await ctx.send(embed=embed)
            else:
                await ctx.send(embed=EmbedBuilder.create_error_embed("❌ Không thể mua cá! Vui lòng thử lại."))
                
        except Exception as e:
            await ctx.send(embed=EmbedBuilder.create_error_embed(f"❌ Lỗi mua cá: {str(e)}"))
    
    async def harvest_fish_command(self, ctx, slot: str = None):
        """Handle fish harvesting"""
        try:
            user_id = ctx.author.id
            
            # Check if user is registered
            user = await self.db.get_user(user_id)
            if not user:
                await ctx.send(embed=EmbedBuilder.create_error_embed("❌ Bạn chưa đăng ký! Sử dụng `f!register` để bắt đầu."))
                return
            
            # Get fish in pond
            fish_list = await self.db.get_user_livestock(user_id, 'pond')
            if not fish_list:
                await ctx.send(embed=EmbedBuilder.create_error_embed("❌ Ao của bạn đang trống!"))
                return
            
            # Get weather and event modifiers
            weather_modifier = get_weather_modifier(self.bot, 'fish')
            event_modifier = 1.0
            try:
                events_cog = self.bot.get_cog('EventsCog')
                if events_cog and hasattr(events_cog, 'get_current_growth_modifier'):
                    event_modifier = events_cog.get_current_growth_modifier()
            except:
                pass
            
            total_modifier = weather_modifier * event_modifier
            
            # If no slot specified, harvest all ready fish
            if slot is None or slot.lower() == 'all':
                ready_fish = []
                for fish in fish_list:
                    species_config = config.FISH_SPECIES.get(fish.species_id)
                    if species_config:
                        time_passed = (datetime.now() - fish.birth_time).total_seconds()
                        adjusted_growth_time = species_config['growth_time'] / total_modifier
                        if time_passed >= adjusted_growth_time:
                            ready_fish.append((fish, species_config))
                
                if not ready_fish:
                    await ctx.send(embed=EmbedBuilder.create_error_embed("❌ Không có cá nào sẵn sàng thu hoạch!"))
                    return
                
                # Harvest all ready fish
                total_value = 0
                harvested_fish = []
                
                for fish, species_config in ready_fish:
                    # Calculate value with weather bonus
                    fish_value = int(species_config['sell_price'] * weather_modifier)
                    total_value += fish_value
                    harvested_fish.append(f"{species_config['name']} (Ô {fish.facility_slot + 1}): {fish_value:,} coins")
                    
                    # Remove from database
                    await self.db.remove_livestock(fish.livestock_id)
                
                # Add money to user
                await self.db.update_user_money(user_id, total_value)
                
                # Create success embed
                embed = EmbedBuilder.create_success_embed(
                    title="🐟 Thu hoạch thành công!",
                    message=f"**Đã thu hoạch:** {len(ready_fish)} con cá\n"
                           f"**Tổng giá trị:** {total_value:,} coins\n"
                           f"**Số dư mới:** {user.money + total_value:,} coins"
                )
                embed.color = 0x1e90ff
                
                # Add detailed breakdown if not too long
                if len(harvested_fish) <= 5:
                    embed.add_field(
                        name="📋 Chi tiết",
                        value="\n".join(harvested_fish),
                        inline=False
                    )
                
                await ctx.send(embed=embed)
                return
            
            # Harvest specific slot
            try:
                slot_index = int(slot) - 1  # Convert to 0-indexed
            except ValueError:
                await ctx.send(embed=EmbedBuilder.create_error_embed(
                    "❌ Số ô không hợp lệ! Sử dụng: `f!pond harvest <số_ô>` hoặc `f!pond harvest all`"
                ))
                return
            
            # Find fish in specified slot
            target_fish = next((f for f in fish_list if f.facility_slot == slot_index), None)
            if not target_fish:
                await ctx.send(embed=EmbedBuilder.create_error_embed(f"❌ Ô {slot} đang trống!"))
                return
            
            # Get species info
            species_config = config.FISH_SPECIES.get(target_fish.species_id)
            if not species_config:
                await ctx.send(embed=EmbedBuilder.create_error_embed(
                    f"❌ Không tìm thấy thông tin loài cá trong ô {slot}!"
                ))
                return
            
            # Check if fish is mature
            time_passed = (datetime.now() - target_fish.birth_time).total_seconds()
            adjusted_growth_time = species_config['growth_time'] / total_modifier
            if time_passed < adjusted_growth_time:
                await ctx.send(embed=EmbedBuilder.create_error_embed("❌ Cá chưa trưởng thành!"))
                return
            
            # Calculate value
            fish_value = int(species_config['sell_price'] * weather_modifier)
            
            # Remove fish and add money
            await self.db.remove_livestock(target_fish.livestock_id)
            await self.db.update_user_money(user_id, fish_value)
            
            # Create success embed
            embed = EmbedBuilder.create_success_embed(
                title="🐟 Thu hoạch thành công!",
                message=f"**Đã thu hoạch:** {species_config['name']} (Ô {slot})\n"
                       f"**Giá trị:** {fish_value:,} coins\n"
                       f"**Số dư mới:** {user.money + fish_value:,} coins"
            )
            embed.color = 0x1e90ff
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(embed=EmbedBuilder.create_error_embed(f"❌ Lỗi thu hoạch: {str(e)}"))
    
    async def upgrade_pond_command(self, ctx):
        """Handle pond upgrade"""
        try:
            user_id = ctx.author.id
            
            # Check if user is registered
            user = await self.db.get_user(user_id)
            if not user:
                await ctx.send(embed=EmbedBuilder.create_error_embed("❌ Bạn chưa đăng ký! Sử dụng `f!register` để bắt đầu."))
                return
            
            # Get facilities
            facilities = await self.db.get_user_facilities(user_id)
            if not facilities:
                await ctx.send(embed=EmbedBuilder.create_error_embed("❌ Không tìm thấy thông tin cơ sở!"))
                return
            
            # Check if pond is at max level
            if facilities.pond_level >= 6:
                await ctx.send(embed=EmbedBuilder.create_error_embed("❌ Ao đã đạt cấp độ tối đa!"))
                return
            
            # Get upgrade cost
            next_level = facilities.pond_level + 1
            upgrade_cost = config.POND_UPGRADE_COSTS.get(next_level, 0)
            if user.money < upgrade_cost:
                await ctx.send(embed=EmbedBuilder.create_error_embed(
                    f"❌ Không đủ tiền nâng cấp!\n"
                    f"Cần: {upgrade_cost:,} coins\n"
                    f"Có: {user.money:,} coins"
                ))
                return
            
            # Perform upgrade
            new_slots = facilities.pond_slots + 2
            facilities.pond_level = next_level
            facilities.pond_slots = new_slots
            await self.db.update_user_facilities(facilities)
            
            # Deduct money
            await self.db.update_user_money(user_id, -upgrade_cost)
            
            # Create success embed
            embed = EmbedBuilder.create_success_embed(
                title="⬆️ Nâng cấp ao thành công!",
                message=f"**Cấp độ mới:** {next_level}\n"
                       f"**Số ô mới:** {new_slots}\n"
                       f"**Chi phí:** {upgrade_cost:,} coins\n"
                       f"**Số dư còn lại:** {user.money - upgrade_cost:,} coins"
            )
            embed.color = 0x1e90ff
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(embed=EmbedBuilder.create_error_embed(f"❌ Lỗi nâng cấp: {str(e)}"))
    
    async def show_fish_shop(self, ctx):
        """Display fish shop with available species"""
        try:
            # Get all fish species
            fish_species = []
            for species_id, species_data in config.FISH_SPECIES.items():
                species = await self.db.get_species(species_id)
                if species:
                    fish_species.append(species)
            
            if not fish_species:
                await ctx.send(embed=EmbedBuilder.create_error_embed("❌ Không có cá nào để bán!"))
                return
            
            # Sort by tier and price
            fish_species.sort(key=lambda x: (x.tier, x.buy_price))
            
            # Create shop embed
            embed = EmbedBuilder.create_base_embed(
                title="🐟 Cửa hàng cá",
                description="Chọn loại cá để mua cho ao của bạn!",
                color=0x1e90ff
            )
            
            # Group by tier
            tier_names = {1: "🥉 Cơ bản", 2: "🥈 Cao cấp", 3: "🥇 Huyền thoại"}
            current_tier = None
            tier_fish = []
            
            for species in fish_species:
                if current_tier != species.tier:
                    if tier_fish:
                        # Add previous tier to embed
                        embed.add_field(
                            name=tier_names.get(current_tier, f"Tier {current_tier}"),
                            value="\n".join(tier_fish),
                            inline=False
                        )
                    current_tier = species.tier
                    tier_fish = []
                
                # Add species to current tier
                growth_mins = species.growth_time // 60
                tier_fish.append(
                    f"**{species.name}** - {species.buy_price:,} coins ({growth_mins}p)"
                )
            
            # Add last tier
            if tier_fish:
                embed.add_field(
                    name=tier_names.get(current_tier, f"Tier {current_tier}"),
                    value="\n".join(tier_fish),
                    inline=False
                )
            
            embed.add_field(
                name="💡 Hướng dẫn",
                value="Sử dụng: `f!pond buy <tên_cá> [số_lượng]`\n"
                      "Ví dụ: `f!pond buy cá_vàng 2`",
                inline=False
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(embed=EmbedBuilder.create_error_embed(f"❌ Lỗi hiển thị cửa hàng: {str(e)}"))

async def setup(bot):
    """Setup function for the cog"""
    await bot.add_cog(PondCog(bot)) 