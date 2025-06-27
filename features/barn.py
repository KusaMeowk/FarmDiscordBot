"""
Barn System - Nuôi gia súc
Quản lý chuồng trại, mua/bán gia súc, thu hoạch sản phẩm
"""

import discord
from discord.ext import commands
from datetime import datetime, timedelta
import asyncio
from typing import Optional, List

import config
from database.database import Database
from database.models import Species, UserLivestock, UserFacilities, LivestockProduct
from utils.embeds import EmbedBuilder
from utils.livestock_helpers import (
    calculate_livestock_maturity, get_livestock_display_info,
    get_livestock_weather_modifier, validate_facility_slot,
    get_available_species_for_purchase, format_livestock_value,
    can_collect_product, get_product_ready_time, get_weather_modifier
)

class BarnCog(commands.Cog):
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
        # Get weather modifier using helper function
        weather_modifier = get_weather_modifier(self.bot, 'animal')
        
        # Get current weather for display
        current_weather = "sunny"
        weather_cog = self.bot.get_cog('WeatherCog')
        if weather_cog and hasattr(weather_cog, 'current_weather'):
            current_weather_data = weather_cog.current_weather
            if isinstance(current_weather_data, dict):
                current_weather = current_weather_data.get('type', 'sunny')
            elif isinstance(current_weather_data, str):
                current_weather = current_weather_data
            else:
                current_weather = 'sunny'
        
        # Get event modifier
        events_cog = self.bot.get_cog('EventsCog')
        event_growth_modifier = 1.0
        
        if events_cog and hasattr(events_cog, 'get_current_growth_modifier'):
            event_growth_modifier = events_cog.get_current_growth_modifier()
        
        return weather_modifier, event_growth_modifier, current_weather
    
    @commands.group(name='barn', aliases=['chuong'], invoke_without_command=True)
    async def barn_group(self, ctx):
        """🐄 Quản lý chuồng trại - Xem trạng thái chuồng gia súc
        
        Subcommands:
        • f!barn buy <loại_gia_súc> [số_lượng] - Mua gia súc
        • f!barn harvest [ô] - Thu hoạch gia súc trưởng thành
        • f!barn collect [ô] - Thu thập sản phẩm (sữa, trứng...)
        • f!barn upgrade - Nâng cấp chuồng
        
        Sử dụng: f!barn
        """
        await self.show_barn(ctx)
    
    @barn_group.command(name='buy', aliases=['mua'])
    async def buy_animal(self, ctx, animal_type: str = None, quantity: int = 1):
        """🛒 Mua gia súc cho chuồng trại
        
        Sử dụng: f!barn buy <loại_gia_súc> [số_lượng]
        Ví dụ: f!barn buy heo 2
        """
        if animal_type is None:
            await self.show_animal_shop(ctx)
            return
            
        await self.buy_animal_command(ctx, animal_type, quantity)
    
    @barn_group.command(name='harvest', aliases=['thu'])
    async def harvest_animal(self, ctx, slot: str = None):
        """🥩 Thu hoạch gia súc trưởng thành
        
        Sử dụng: f!barn harvest [ô]
        Ví dụ: f!barn harvest 1 hoặc f!barn harvest all
        """
        await self.harvest_animal_command(ctx, slot)
    
    @barn_group.command(name='collect', aliases=['thu_san_pham'])
    async def collect_product(self, ctx, slot: str = None):
        """🥛 Thu thập sản phẩm từ gia súc
        
        Sử dụng: f!barn collect [ô]
        Ví dụ: f!barn collect 1 hoặc f!barn collect all
        """
        await self.collect_product_command(ctx, slot)
    
    @barn_group.command(name='upgrade', aliases=['nangcap'])
    async def upgrade_barn(self, ctx):
        """🔧 Nâng cấp chuồng trại
        
        Sử dụng: f!barn upgrade
        """
        await self.upgrade_barn_command(ctx)

    async def show_barn(self, ctx):
        """Display user's barn status"""
        user_id = ctx.author.id
        
        try:
            # Get user and facilities
            user = await self.db.get_user(user_id)
            if not user:
                await ctx.send(embed=EmbedBuilder.create_error_embed("❌ Bạn chưa đăng ký! Sử dụng `f!register` để bắt đầu."))
                return
            
            facilities = await self.db.get_user_facilities(user_id)
            
            # Get barn livestock
            barn_livestock = await self.db.get_user_livestock(user_id, 'barn')
            
            # Get modifiers
            weather_modifier, event_growth_modifier, current_weather = self.get_current_modifiers()
            
            # Create embed
            embed = EmbedBuilder.create_base_embed(
                title=f"🐄 Chuồng Trại của {ctx.author.display_name}",
                description=f"**Cấp độ:** {facilities.barn_level} | **Số ô:** {facilities.barn_slots}/6\n"
                           f"**Thời tiết:** {current_weather.title()} (×{weather_modifier:.1f})"
            )
            
            # Display each barn slot
            for slot in range(facilities.barn_slots):
                # Find livestock in this slot
                livestock_in_slot = None
                for livestock in barn_livestock:
                    if livestock.facility_slot == slot:
                        livestock_in_slot = livestock
                        break
                
                if livestock_in_slot:
                    # Get species info from config
                    species_config = config.ANIMAL_SPECIES.get(livestock_in_slot.species_id)
                    if species_config:
                        # Calculate maturity
                        total_modifier = weather_modifier * event_growth_modifier
                        birth_time = livestock_in_slot.birth_time
                        growth_time = species_config['growth_time']
                    
                        # Calculate time passed and remaining
                        time_passed = (datetime.now() - birth_time).total_seconds()
                        adjusted_growth_time = growth_time / total_modifier
                        is_mature = time_passed >= adjusted_growth_time
                        
                        if is_mature:
                            status = "🟢 Trưởng thành"
                            time_remaining = ""
                        else:
                            remaining_seconds = adjusted_growth_time - time_passed
                            hours = int(remaining_seconds // 3600)
                            minutes = int((remaining_seconds % 3600) // 60)
                            status = "🟡 Đang lớn"
                            time_remaining = f"⏰ Còn: {hours}h {minutes}m\n"
                        
                        slot_value = f"{species_config['emoji']} **{species_config['name']}**\n"
                        slot_value += f"📊 {status}\n"
                        slot_value += time_remaining
                        slot_value += f"✨ {species_config['special_ability']}"
                        
                        embed.add_field(
                            name=f"🐄 Ô {slot + 1}",
                            value=slot_value,
                            inline=True
                        )
                else:
                    embed.add_field(
                        name=f"⬜ Ô {slot + 1}",
                        value="*Trống*\nSử dụng `f!barn buy` để mua gia súc",
                        inline=True
                    )
            
            # Add expansion info if not max level
            if facilities.barn_level < 6:
                next_level = facilities.barn_level + 1
                expansion_cost = 1000 * (next_level ** 2)  # Simple cost formula
                embed.add_field(
                    name="🔧 Mở rộng",
                    value=f"Nâng cấp lên cấp {next_level}: {expansion_cost:,}🪙\n"
                          f"Sử dụng `f!barn upgrade`",
                    inline=False
                )
            
            # Add footer with commands
            embed.set_footer(text="💡 f!barn buy | f!barn harvest | f!barn collect | f!barn upgrade")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(embed=EmbedBuilder.create_error_embed(f"❌ Lỗi hiển thị chuồng: {str(e)}"))

    async def buy_animal_command(self, ctx, animal_type: str, quantity: int = 1):
        """Handle animal purchase"""
        try:
            user_id = ctx.author.id
            
            # Validate quantity
            if quantity < 1 or quantity > 10:
                await ctx.send(embed=EmbedBuilder.create_error_embed("❌ Số lượng phải từ 1-10!"))
                return
            
            # Check if user is registered
            user = await self.db.get_user(user_id)
            if not user:
                await ctx.send(embed=EmbedBuilder.create_error_embed("❌ Bạn chưa đăng ký! Sử dụng `f!register` để bắt đầu."))
                return
            
            # Get user facilities
            facilities = await self.db.get_user_facilities(user_id)
            
            # Get current animals in barn
            current_animals = await self.db.get_user_livestock(user_id, 'barn')
            available_slots = facilities.barn_slots - len(current_animals)
            
            if available_slots < quantity:
                await ctx.send(embed=EmbedBuilder.create_error_embed(
                    f"❌ Không đủ chỗ trong chuồng! Còn trống: {available_slots} ô"
                ))
                return
            
            # Find animal species
            animal_species = None
            species_id = None
            for species_id, species_data in config.ANIMAL_SPECIES.items():
                if (animal_type.lower() in species_data['name'].lower() or 
                    animal_type.lower() == species_id):
                    animal_species = species_data
                    break
            
            if not animal_species:
                await ctx.send(embed=EmbedBuilder.create_error_embed(f"❌ Không tìm thấy loại gia súc `{animal_type}`!"))
                return
            
            # Check if user has enough money
            total_cost = animal_species['buy_price'] * quantity
            if user.money < total_cost:
                await ctx.send(embed=EmbedBuilder.create_error_embed(
                    f"❌ Không đủ tiền! Cần: {total_cost:,} coins, có: {user.money:,} coins"
                ))
                return
            
            # Find available slots
            used_slots = {a.facility_slot for a in current_animals}
            available_slot_indices = [i for i in range(facilities.barn_slots) if i not in used_slots]
            
            if len(available_slot_indices) < quantity:
                await ctx.send(embed=EmbedBuilder.create_error_embed(
                    f"❌ Không đủ chỗ trong chuồng! Còn trống: {len(available_slot_indices)} ô"
                ))
                return
            
            # Purchase animals
            purchased_slots = []
            for i in range(quantity):
                slot_index = available_slot_indices[i]
                
                # Add animal to database  
                livestock_id = await self.db.add_livestock(
                    user_id=user_id,
                    species_id=species_id,
                    facility_type='barn',
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
                    title="🐄 Mua gia súc thành công!",
                    message=f"**Đã mua:** {quantity}x {animal_species['name']}\n"
                           f"**Vị trí:** Ô {', '.join(map(str, purchased_slots))}\n"
                           f"**Chi phí:** {total_cost:,} coins\n"
                           f"**Thời gian lớn:** {animal_species['growth_time'] // 60} phút"
                )
                embed.color = 0x8B4513
                await ctx.send(embed=embed)
            else:
                await ctx.send(embed=EmbedBuilder.create_error_embed("❌ Không thể mua gia súc! Vui lòng thử lại."))
                
        except Exception as e:
            await ctx.send(embed=EmbedBuilder.create_error_embed(f"❌ Lỗi mua gia súc: {str(e)}"))

    async def harvest_animal_command(self, ctx, slot: str = None):
        """Handle animal harvesting"""
        try:
            user_id = ctx.author.id
            
            # Check if user is registered
            user = await self.db.get_user(user_id)
            if not user:
                await ctx.send(embed=EmbedBuilder.create_error_embed("❌ Bạn chưa đăng ký! Sử dụng `f!register` để bắt đầu."))
                return
            
            # Get animals in barn
            animals_list = await self.db.get_user_livestock(user_id, 'barn')
            if not animals_list:
                await ctx.send(embed=EmbedBuilder.create_error_embed("❌ Chuồng của bạn đang trống!"))
                return
            
            # Get modifiers
            weather_modifier, event_modifier, _ = self.get_current_modifiers()
            total_modifier = weather_modifier * event_modifier
            
            # If no slot specified, harvest all ready animals
            if slot is None or slot.lower() == 'all':
                ready_animals = []
                for animal in animals_list:
                    species_config = config.ANIMAL_SPECIES.get(animal.species_id)
                    if species_config:
                        time_passed = (datetime.now() - animal.birth_time).total_seconds()
                        adjusted_growth_time = species_config['growth_time'] / total_modifier
                        if time_passed >= adjusted_growth_time:
                            ready_animals.append((animal, species_config))
                
                if not ready_animals:
                    await ctx.send(embed=EmbedBuilder.create_error_embed("❌ Không có gia súc nào sẵn sàng thu hoạch!"))
                    return
                
                # Harvest all ready animals
                total_value = 0
                harvested_animals = []
                
                for animal, species_config in ready_animals:
                    animal_value = int(species_config['sell_price'] * weather_modifier)
                    total_value += animal_value
                    harvested_animals.append(f"{species_config['name']} (Ô {animal.facility_slot + 1}): {animal_value:,} coins")
                    
                    # Remove from database
                    await self.db.remove_livestock(animal.livestock_id)
                
                # Add money to user
                await self.db.update_user_money(user_id, total_value)
                
                # Create success embed
                embed = EmbedBuilder.create_success_embed(
                    title="🐄 Thu hoạch thành công!",
                    message=f"**Đã thu hoạch:** {len(ready_animals)} con gia súc\n"
                           f"**Tổng giá trị:** {total_value:,} coins\n"
                           f"**Số dư mới:** {user.money + total_value:,} coins"
                )
                embed.color = 0x8B4513
                
                # Add detailed breakdown if not too long
                if len(harvested_animals) <= 5:
                    embed.add_field(
                        name="📋 Chi tiết",
                        value="\n".join(harvested_animals),
                        inline=False
                    )
                
                await ctx.send(embed=embed)
                return
            
            # Harvest specific slot
            try:
                slot_index = int(slot) - 1  # Convert to 0-indexed
            except ValueError:
                await ctx.send(embed=EmbedBuilder.create_error_embed(
                    "❌ Số ô không hợp lệ! Sử dụng: `f!barn harvest <số_ô>` hoặc `f!barn harvest all`"
                ))
                return
            
            # Find animal in specified slot
            target_animal = next((a for a in animals_list if a.facility_slot == slot_index), None)
            if not target_animal:
                await ctx.send(embed=EmbedBuilder.create_error_embed(f"❌ Ô {slot} đang trống!"))
                return
            
            # Get species info
            species_config = config.ANIMAL_SPECIES.get(target_animal.species_id)
            if not species_config:
                await ctx.send(embed=EmbedBuilder.create_error_embed(
                    f"❌ Không tìm thấy thông tin loài gia súc trong ô {slot}!"
                ))
                return
            
            # Check if animal is mature
            time_passed = (datetime.now() - target_animal.birth_time).total_seconds()
            adjusted_growth_time = species_config['growth_time'] / total_modifier
            if time_passed < adjusted_growth_time:
                await ctx.send(embed=EmbedBuilder.create_error_embed("❌ Gia súc chưa trưởng thành!"))
                return
            
            # Calculate value
            animal_value = int(species_config['sell_price'] * weather_modifier)
            
            # Remove animal and add money
            await self.db.remove_livestock(target_animal.livestock_id)
            await self.db.update_user_money(user_id, animal_value)
            
            # Create success embed
            embed = EmbedBuilder.create_success_embed(
                title="🐄 Thu hoạch thành công!",
                message=f"**Đã thu hoạch:** {species_config['name']} (Ô {slot})\n"
                       f"**Giá trị:** {animal_value:,} coins\n"
                       f"**Số dư mới:** {user.money + animal_value:,} coins"
            )
            embed.color = 0x8B4513
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(embed=EmbedBuilder.create_error_embed(f"❌ Lỗi thu hoạch: {str(e)}"))

    async def collect_product_command(self, ctx, slot: str = None):
        """Handle product collection (placeholder for now)"""
        await ctx.send(embed=EmbedBuilder.create_error_embed("🚧 Tính năng thu thập sản phẩm đang phát triển!"))

    async def upgrade_barn_command(self, ctx):
        """Handle barn upgrade"""
        try:
            user_id = ctx.author.id
            
            # Check if user is registered
            user = await self.db.get_user(user_id)
            if not user:
                await ctx.send(embed=EmbedBuilder.create_error_embed("❌ Bạn chưa đăng ký! Sử dụng `f!register` để bắt đầu."))
                return
            
            # Get user facilities
            facilities = await self.db.get_user_facilities(user_id)
            
            if facilities.barn_level >= 6:
                await ctx.send(embed=EmbedBuilder.create_error_embed("❌ Chuồng trại đã đạt cấp độ tối đa!"))
                return
            
            # Calculate upgrade cost using config
            next_level = facilities.barn_level + 1
            upgrade_cost = config.BARN_UPGRADE_COSTS.get(next_level, 0)
            
            if upgrade_cost == 0:
                await ctx.send(embed=EmbedBuilder.create_error_embed("❌ Chuồng trại đã đạt cấp độ tối đa!"))
                return
            
            if user.money < upgrade_cost:
                await ctx.send(embed=EmbedBuilder.create_error_embed(
                    f"❌ Không đủ tiền! Cần: {upgrade_cost:,} coins, có: {user.money:,} coins"
                ))
                return
            
            # Perform upgrade
            await self.db.update_user_money(user_id, -upgrade_cost)
            
            # Update facilities
            new_slots = facilities.barn_slots + 2
            facilities.barn_level = next_level
            facilities.barn_slots = new_slots
            await self.db.update_user_facilities(facilities)
            
            # Create success embed
            embed = EmbedBuilder.create_success_embed(
                title="🔧 Nâng cấp thành công!",
                message=f"**Chuồng trại nâng cấp lên cấp {next_level}!**\n"
                       f"**Chi phí:** {upgrade_cost:,} coins\n"
                       f"**Số ô mới:** {new_slots}\n"
                       f"**Số dư còn lại:** {user.money - upgrade_cost:,} coins"
            )
            embed.color = 0x8B4513
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(embed=EmbedBuilder.create_error_embed(f"❌ Lỗi nâng cấp: {str(e)}"))

    async def show_animal_shop(self, ctx):
        """Display animal shop"""
        embed = EmbedBuilder.create_base_embed(
            title="🛒 Cửa Hàng Gia Súc",
            description="Chọn loại gia súc bạn muốn mua cho chuồng trại",
            color=0x8B4513
        )
        
        # Group animals by tier
        for tier in [1, 2, 3]:
            tier_animals = []
            for species_id, species_data in config.ANIMAL_SPECIES.items():
                if species_data['tier'] == tier:
                    tier_animals.append(
                        f"{species_data['emoji']} **{species_data['name']}**\n"
                        f"💰 {species_data['buy_price']:,} coins | "
                        f"⏰ {species_data['growth_time']//60}p | "
                        f"💎 {species_data['sell_price']:,} coins\n"
                        f"✨ {species_data['special_ability']}\n"
                        f"`f!barn buy {species_id}`"
                    )
            
            if tier_animals:
                tier_names = {1: "🥉 Cơ Bản", 2: "🥈 Cao Cấp", 3: "🥇 Huyền Thoại"}
                embed.add_field(
                    name=tier_names[tier],
                    value="\n\n".join(tier_animals),
                    inline=False
                )
        
        embed.set_footer(text="💡 Sử dụng: f!barn buy <loại_gia_súc> [số_lượng]")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(BarnCog(bot))