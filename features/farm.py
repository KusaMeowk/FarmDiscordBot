import discord
from discord.ext import commands
from datetime import datetime
import random
import config
from utils.embeds import EmbedBuilder
from utils.helpers import calculate_crop_yield, calculate_yield_range, is_crop_ready, validate_plot_index
from utils.pricing import pricing_coordinator
from utils.registration import registration_required
from features.maid_helper import maid_helper
from features.maid_display_integration import add_maid_buffs_to_embed

class FarmView(discord.ui.View):
    """View với các nút bấm cho nông trại và phân trang"""
    
    def __init__(self, bot, user_id, page=0):
        super().__init__(timeout=300)
        self.bot = bot
        self.user_id = user_id
        self.current_page = page
        self.plots_per_page = 8  # Hiển thị 8 ô đất mỗi trang (2 hàng x 4 cột)
    
    @discord.ui.button(label="🌱 Trồng cây", style=discord.ButtonStyle.green)
    async def plant_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Sử dụng lệnh `f!plant <tên_cây> <ô_đất>` để trồng cây!", ephemeral=True)
    
    @discord.ui.button(label="◀️", style=discord.ButtonStyle.grey)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            if interaction.user.id != self.user_id:
                await interaction.response.send_message("❌ Bạn không thể sử dụng nút này!", ephemeral=True)
                return
            
            if self.current_page > 0:
                self.current_page -= 1
                await self._update_farm_display(interaction)
            else:
                await interaction.response.send_message("❌ Đã ở trang đầu tiên!", ephemeral=True)
        except Exception as e:
            print(f"Farm previous page error: {e}")
            try:
                await interaction.response.send_message("❌ Có lỗi xảy ra. Vui lòng thử lại!", ephemeral=True)
            except:
                pass
    
    @discord.ui.button(label="🔄 Cập nhật", style=discord.ButtonStyle.blurple)
    async def refresh_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            if interaction.user.id != self.user_id:
                await interaction.response.send_message("❌ Bạn không thể sử dụng nút này!", ephemeral=True)
                return
            
            await self._update_farm_display(interaction)
        except Exception as e:
            print(f"Farm refresh error: {e}")
            try:
                await interaction.response.send_message("❌ Có lỗi xảy ra. Vui lòng thử lại!", ephemeral=True)
            except:
                pass
    
    @discord.ui.button(label="▶️", style=discord.ButtonStyle.grey)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            if interaction.user.id != self.user_id:
                await interaction.response.send_message("❌ Bạn không thể sử dụng nút này!", ephemeral=True)
                return
            
            # Get user to check max pages
            user = await self.bot.db.get_user(self.user_id)
            if not user:
                await interaction.response.send_message("❌ Không tìm thấy thông tin người dùng!", ephemeral=True)
                return
                
            max_pages = (user.land_slots - 1) // self.plots_per_page
            
            if self.current_page < max_pages:
                self.current_page += 1
                await self._update_farm_display(interaction)
            else:
                await interaction.response.send_message("❌ Đã ở trang cuối cùng!", ephemeral=True)
        except Exception as e:
            print(f"Farm next page error: {e}")
            try:
                await interaction.response.send_message("❌ Có lỗi xảy ra. Vui lòng thử lại!", ephemeral=True)
            except:
                pass
    
    @discord.ui.button(label="✨ Thu hoạch tất cả", style=discord.ButtonStyle.red)
    async def harvest_all_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            if interaction.user.id != self.user_id:
                await interaction.response.send_message("❌ Bạn không thể sử dụng nút này!", ephemeral=True)
                return
            
            # Get FarmCog instance from bot
            farm_cog = self.bot.get_cog('FarmCog')
            if not farm_cog:
                await interaction.response.send_message("❌ Lỗi hệ thống!", ephemeral=True)
                return
            
            # Execute harvest all logic
            result = await farm_cog.harvest_all_logic(interaction.user.id, interaction.user.display_name)
            
            if result['success']:
                # Refresh the farm view with current page
                await self._update_farm_display(interaction)
                await interaction.followup.send(embed=result['embed'], ephemeral=True)
            else:
                # Send error message
                await interaction.response.send_message(result['message'], ephemeral=True)
        except Exception as e:
            print(f"Farm harvest all error: {e}")
            try:
                await interaction.response.send_message("❌ Có lỗi xảy ra. Vui lòng thử lại!", ephemeral=True)
            except:
                pass
    
    async def _update_farm_display(self, interaction: discord.Interaction):
        """Helper method to update farm display with pagination"""
        try:
            user = await self.bot.db.get_user(self.user_id)
            if not user:
                await interaction.response.send_message("❌ Không tìm thấy thông tin người dùng!", ephemeral=True)
                return
                
            crops = await self.bot.db.get_user_crops(self.user_id)
            
            # Create farm embed with pagination
            embed = await EmbedBuilder.create_farm_embed_paginated(user, crops, self.current_page, self.plots_per_page, self.bot)
            
            # Add maid buffs to embed
            embed = add_maid_buffs_to_embed(embed, self.user_id, "farm")
            
            # Update button states
            max_pages = (user.land_slots - 1) // self.plots_per_page
            
            # Update navigation button states
            for item in self.children:
                if item.label == "◀️":
                    item.disabled = (self.current_page == 0)
                elif item.label == "▶️":
                    item.disabled = (self.current_page >= max_pages)
            
            await interaction.response.edit_message(embed=embed, view=self)
        except Exception as e:
            print(f"Farm update display error: {e}")
            try:
                await interaction.response.send_message("❌ Có lỗi xảy ra khi cập nhật trang trại!", ephemeral=True)
            except:
                pass

class FarmCog(commands.Cog):
    """Hệ thống nông trại - trồng và thu hoạch cây"""
    
    def __init__(self, bot):
        self.bot = bot
    
    async def get_user_safe(self, user_id: int):
        """Get user from database (registration required)"""
        user = await self.bot.db.get_user(user_id)
        return user

    async def harvest_all_logic(self, user_id: int, username: str):
        """Logic để thu hoạch tất cả cây chín - dùng cho cả command và button"""
        user = await self.get_user_safe(user_id)
        if not user:
            return {
                'success': False,
                'message': "❌ Bạn cần đăng ký tài khoản trước! Sử dụng `f!register`"
            }
            
        crops = await self.bot.db.get_user_crops(user.user_id)
        
        if not crops:
            return {
                'success': False,
                'message': "❌ Bạn chưa trồng cây nào!"
            }
        
        harvested_crops = []
        
        # Get modifiers once for all crops
        weather_cog = self.bot.get_cog('WeatherCog')
        weather_modifier = 1.0
        if weather_cog:
            _, weather_modifier = await weather_cog.get_current_weather_modifier()
        
        events_cog = self.bot.get_cog('EventsCog')
        event_yield_modifier = 1.0
        event_growth_modifier = 1.0
        if events_cog:
            if hasattr(events_cog, 'get_current_yield_modifier'):
                event_yield_modifier = events_cog.get_current_yield_modifier()
            if hasattr(events_cog, 'get_current_growth_modifier'):
                event_growth_modifier = events_cog.get_current_growth_modifier()
        
        # Harvest all ready crops
        for crop in crops:
            if is_crop_ready(crop.plant_time, crop.crop_type, weather_modifier, event_growth_modifier, user_id):
                # Calculate yield với tất cả modifiers
                crop_config = config.CROPS[crop.crop_type]
                base_yield = calculate_crop_yield(crop.crop_type, weather_modifier, event_yield_modifier)
                
                # 🎀 Apply maid buff to yield
                yield_amount = maid_helper.apply_yield_boost_buff(user_id, base_yield)
                
                min_yield, max_yield = calculate_yield_range(crop.crop_type, weather_modifier, event_yield_modifier)
                
                # Add to inventory only (no auto-sell)
                await self.bot.db.add_item(user.user_id, 'crop', crop.crop_type, yield_amount)
                
                # Remove the crop from database
                await self.bot.db.harvest_crop(crop.crop_id)
                
                harvested_crops.append({
                    'name': crop_config['name'],
                    'plot': crop.plot_index + 1,
                    'yield': yield_amount,
                    'yield_range': f"{min_yield}-{max_yield}"
                })
        
        if not harvested_crops:
            return {
                'success': False,
                'message': "❌ Không có cây nào sẵn sàng thu hoạch!"
            }
        
        # Create success embed
        embed = EmbedBuilder.create_success_embed(
            "✨ Thu hoạch tất cả thành công!",
            f"📦 Đã thu thập {len(harvested_crops)} loại nông sản vào kho."
        )
        
        harvest_details = []
        for crop_data in harvested_crops:
            harvest_details.append(
                f"Ô {crop_data['plot']}: {crop_data['name']} x{crop_data['yield']}"
            )
        
        embed.add_field(
            name="📦 Chi tiết thu hoạch",
            value="\n".join(harvest_details[:10]),  # Limit to 10 entries for readability
            inline=False
        )
        
        if len(harvested_crops) > 10:
            embed.add_field(
                name="📋 Tổng kết",
                value=f"Và {len(harvested_crops) - 10} ô khác...",
                inline=False
            )
        
        embed.add_field(
            name="💡 Tip",
            value="Sử dụng `f!market` để xem giá hiện tại\nDùng `f!sell <loại_cây> <số_lượng>` hoặc `f!sell <loại_cây> all` để bán",
            inline=False
        )
        
        return {
            'success': True,
            'embed': embed,
            'harvested_count': len(harvested_crops)
        }
    
    @commands.command(name='farm', aliases=['nongtraia'])
    @registration_required
    async def farm(self, ctx, page = 1):
        """Xem tổng quan nông trại của bạn
        
        Sử dụng: f!farm [trang]
        """
        try:
            # Convert page to int if it's a string
            if isinstance(page, str):
                try:
                    page = int(page)
                except ValueError:
                    page = 1
            
            user = await self.get_user_safe(ctx.author.id)
            if not user:
                await ctx.send("❌ Không tìm thấy thông tin người dùng!")
                return
                
            crops = await self.bot.db.get_user_crops(user.user_id)
            
            # Validate page number
            plots_per_page = 8
            max_pages = (user.land_slots - 1) // plots_per_page + 1
            page = max(1, min(page, max_pages))  # Clamp between 1 and max_pages
            current_page = page - 1  # Convert to 0-based index
            
            # Create paginated embed
            embed = await EmbedBuilder.create_farm_embed_paginated(user, crops, current_page, plots_per_page, self.bot)
            
            # Add maid buffs to embed
            embed = add_maid_buffs_to_embed(embed, user.user_id, "farm")
            
            view = FarmView(self.bot, user.user_id, current_page)
            
            # Set initial button states
            for item in view.children:
                if item.label == "◀️":
                    item.disabled = (current_page == 0)
                elif item.label == "▶️":
                    item.disabled = (current_page >= max_pages - 1)
            
            await ctx.send(embed=embed, view=view)
            
        except Exception as e:
            print(f"Farm command error: {e}")
            await ctx.send("❌ Có lỗi xảy ra khi xem nông trại!")
    
    @commands.command(name='plant', aliases=['trong'])
    @registration_required
    async def plant(self, ctx, *args):
        """Trồng cây trên ô đất với nhiều tùy chọn
        
        Sử dụng: 
        - f!plant <loại_cây> <số_ô> - Trồng ô đơn lẻ
        - f!plant <loại_cây> <số_ô>,<số_ô>,<số_ô> - Trồng nhiều ô cụ thể
        - f!plant <loại_cây> all - Trồng tất cả ô trống
        
        Ví dụ: 
        - f!plant carrot 1
        - f!plant tomato 1,3,5,7
        - f!plant wheat all
        """
        try:
            # Parse arguments
            if len(args) == 0:
                embed = EmbedBuilder.create_error_embed(
                    "Cách sử dụng lệnh trồng cây",
                    "**Các tùy chọn:**\n"
                    "• `f!plant <loại_cây> <số_ô>` - Trồng ô đơn lẻ\n"
                    "• `f!plant <loại_cây> <số_ô>,<số_ô>,<số_ô>` - Trồng nhiều ô\n"
                    "• `f!plant <loại_cây> all` - Trồng tất cả ô trống\n\n"
                    "**Loại cây có sẵn:**\n" +
                    "\n".join([f"• `{k}` - {v['name']} ({v['price']} coins)" 
                              for k, v in config.CROPS.items()])
                )
                await ctx.send(embed=embed)
                return
            
            crop_type = args[0] if len(args) > 0 else None
            target = args[1] if len(args) > 1 else None
            
            if not target:
                await ctx.send("❌ Vui lòng chỉ định ô đất hoặc 'all'!")
                return

            user = await self.get_user_safe(ctx.author.id)
            
            # Validate crop type
            if crop_type not in config.CROPS:
                crop_names = [config.CROPS[key]['name'] for key in config.CROPS.keys()]
                await ctx.send(f"❌ Loại cây không hợp lệ!\nCó thể trồng: {', '.join(crop_names)}")
                return
            
            crop_config = config.CROPS[crop_type]
            
            # Parse target plots
            plots_to_plant = []
            
            if target.lower() == 'all':
                # Plant on all empty plots
                existing_crops = await self.bot.db.get_user_crops(user.user_id)
                occupied_plots = {crop.plot_index for crop in existing_crops}
                
                plots_to_plant = [i for i in range(user.land_slots) if i not in occupied_plots]
                
                if not plots_to_plant:
                    await ctx.send("❌ Không có ô đất trống nào!")
                    return
                
                # Limit bulk planting to prevent spam
                if len(plots_to_plant) > 50:
                    await ctx.send("❌ Chỉ có thể trồng tối đa 50 ô cùng lúc!")
                    return
                    
            else:
                # Parse specific plots
                try:
                    if ',' in target:
                        # Multiple plots: "1,3,5,7"
                        plot_numbers = [int(x.strip()) for x in target.split(',')]
                    else:
                        # Single plot: "1"
                        plot_numbers = [int(target)]
                    
                    # Convert to 0-based indexing and validate
                    for plot_num in plot_numbers:
                        plot_index = plot_num - 1  # Convert to 0-based
                        
                        if not validate_plot_index(plot_index, user.land_slots):
                            await ctx.send(f"❌ Ô đất {plot_num} không hợp lệ! Bạn có {user.land_slots} ô đất (1-{user.land_slots}).")
                            return
                        
                        plots_to_plant.append(plot_index)
                    
                    # Limit manual bulk planting
                    if len(plots_to_plant) > 20:
                        await ctx.send("❌ Chỉ có thể trồng tối đa 20 ô cùng lúc!")
                        return
                        
                except ValueError:
                    await ctx.send("❌ Định dạng ô đất không hợp lệ! Sử dụng số (ví dụ: 1 hoặc 1,3,5)")
                    return
            
            # Check if any plots are already occupied
            existing_crops = await self.bot.db.get_user_crops(user.user_id)
            occupied_plots = {crop.plot_index for crop in existing_crops}
            
            already_planted = [i for i in plots_to_plant if i in occupied_plots]
            if already_planted:
                plot_numbers = [str(i + 1) for i in already_planted]
                await ctx.send(f"❌ Các ô sau đã có cây: {', '.join(plot_numbers)}")
                return
            
            # Check if user has enough seeds
            inventory = await self.bot.db.get_user_inventory(user.user_id)
            available_seeds = 0
            
            for item in inventory:
                if item.item_type == 'seed' and item.item_id == crop_type:
                    available_seeds = item.quantity
                    break
            
            seeds_needed = len(plots_to_plant)
            if available_seeds < seeds_needed:
                await ctx.send(f"❌ Bạn cần {seeds_needed} hạt {crop_config['name']}, chỉ có {available_seeds}!")
                return
            
            # Use seeds from inventory
            await self.bot.db.use_item(user.user_id, 'seed', crop_type, seeds_needed)
            
            # Plant crops on all specified plots
            current_time = datetime.now()
            for plot_index in plots_to_plant:
                await self.bot.db.plant_crop(user.user_id, crop_type, plot_index, current_time)
            
            # Create success message
            if len(plots_to_plant) == 1:
                embed = EmbedBuilder.create_success_embed(
                    "Trồng cây thành công!",
                    f"Đã trồng {crop_config['name']} ở ô {plots_to_plant[0] + 1}\n"
                    f"⏰ Thời gian chín: {crop_config['growth_time'] // 60} phút"
                )
            else:
                plot_numbers = [str(i + 1) for i in plots_to_plant]
                embed = EmbedBuilder.create_success_embed(
                    "Trồng cây hàng loạt thành công!",
                    f"Đã trồng {seeds_needed} {crop_config['name']} ở {len(plots_to_plant)} ô đất\n"
                    f"📍 Các ô: {', '.join(plot_numbers)}\n"
                    f"⏰ Thời gian chín: {crop_config['growth_time'] // 60} phút"
                )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            # Log error and send user-friendly message
            print(f"Plant command error: {e}")
            await ctx.send(f"❌ Đã xảy ra lỗi khi trồng cây. Vui lòng thử lại sau!")
            # In production, you'd want to log this to a proper logging system
    
    @commands.command(name='harvest', aliases=['thuhoach'])
    @registration_required
    async def harvest(self, ctx, target = None):
        """Thu hoạch cây đã chín với nhiều tùy chọn
        
        Sử dụng:
        - f!harvest <số_ô> - Thu hoạch ô cụ thể  
        - f!harvest <số_ô>,<số_ô>,<số_ô> - Thu hoạch nhiều ô
        - f!harvest all - Thu hoạch tất cả cây chín
        
        Ví dụ:
        - f!harvest 1
        - f!harvest 1,3,5,7  
        - f!harvest all
        """
        if not target:
            await ctx.send("❌ Vui lòng chỉ định ô đất hoặc 'all' để thu hoạch!")
            return
        
        if target.lower() == 'all':
            # Use the shared harvest all logic
            result = await self.harvest_all_logic(ctx.author.id, ctx.author.display_name)
            
            if result['success']:
                await ctx.send(embed=result['embed'])
            else:
                await ctx.send(result['message'])
            return
        
        user = await self.get_user_safe(ctx.author.id)
        
        # Parse target plots  
        plots_to_harvest = []
        try:
            if ',' in target:
                # Multiple plots: "1,3,5,7"
                plot_numbers = [int(x.strip()) for x in target.split(',')]
            else:
                # Single plot: "1"
                plot_numbers = [int(target)]
            
            # Convert to 0-based indexing and validate
            for plot_num in plot_numbers:
                plot_index = plot_num - 1  # Convert to 0-based
                
                if not validate_plot_index(plot_index, user.land_slots):
                    await ctx.send(f"❌ Ô đất {plot_num} không hợp lệ! Bạn có {user.land_slots} ô đất (1-{user.land_slots}).")
                    return
                
                plots_to_harvest.append(plot_index)
                
        except ValueError:
            await ctx.send("❌ Định dạng ô đất không hợp lệ! Sử dụng số (ví dụ: 1 hoặc 1,3,5)")
            return
        
        # Get crops on specified plots
        crops = await self.bot.db.get_user_crops(user.user_id)
        crops_to_harvest = [crop for crop in crops if crop.plot_index in plots_to_harvest]
        
        if not crops_to_harvest:
            plot_numbers = [str(i + 1) for i in plots_to_harvest]
            await ctx.send(f"❌ Không có cây nào ở các ô: {', '.join(plot_numbers)}")
            return
        
        # Check which crops are ready
        harvested_crops = []
        not_ready_crops = []
        
        for crop in crops_to_harvest:
            if is_crop_ready(crop.plant_time, crop.crop_type, 1.0, 1.0, user.user_id):
                # Get weather modifier
                weather_cog = self.bot.get_cog('WeatherCog')
                weather_modifier = 1.0
                if weather_cog:
                    _, weather_modifier = await weather_cog.get_current_weather_modifier()
                
                # Get event modifier 
                events_cog = self.bot.get_cog('EventsCog')
                event_modifier = 1.0
                if events_cog and hasattr(events_cog, 'get_current_yield_modifier'):
                    event_modifier = events_cog.get_current_yield_modifier()
                
                # Calculate yield với tất cả modifiers
                crop_config = config.CROPS[crop.crop_type]
                base_yield = calculate_crop_yield(crop.crop_type, weather_modifier, event_modifier)
                
                # 🎀 Apply maid buff to yield
                yield_amount = maid_helper.apply_yield_boost_buff(user.user_id, base_yield)
                
                # Cũng tính range để hiển thị thông tin
                min_yield, max_yield = calculate_yield_range(crop.crop_type, weather_modifier, event_modifier)
                
                await self.bot.db.add_item(user.user_id, 'crop', crop.crop_type, yield_amount)
                await self.bot.db.harvest_crop(crop.crop_id)
                
                harvested_crops.append({
                    'name': crop_config['name'],
                    'plot': crop.plot_index + 1,
                    'yield': yield_amount,
                    'yield_range': f"{min_yield}-{max_yield}",
                    'weather_modifier': weather_modifier,
                    'event_modifier': event_modifier
                })
            else:
                crop_config = config.CROPS[crop.crop_type]
                not_ready_crops.append({
                    'name': crop_config['name'],
                    'plot': crop.plot_index + 1
                })
        
        # Create response message
        if harvested_crops:
            # Tính toán tổng modifier để hiển thị
            total_modifier = harvested_crops[0]['weather_modifier'] * harvested_crops[0]['event_modifier']
            modifier_text = ""
            if total_modifier > 1.1:
                modifier_text = f" (Buff +{((total_modifier-1)*100):.0f}%)"
            elif total_modifier < 0.9:
                modifier_text = f" (Debuff {((total_modifier-1)*100):.0f}%)"
            
            embed = EmbedBuilder.create_success_embed(
                f"Thu hoạch thành công!{modifier_text}",
                f"📦 Đã thu thập nông sản vào kho. Sử dụng `f!sell` để bán!"
            )
            
            harvest_details = []
            for crop_data in harvested_crops:
                harvest_details.append(
                    f"Ô {crop_data['plot']}: {crop_data['name']} x{crop_data['yield']} `({crop_data['yield_range']})`"
                )
            
            embed.add_field(
                name="✅ Đã thu hoạch",
                value="\n".join(harvest_details),
                inline=False
            )
            
            # Hiển thị thông tin modifier
            if len(harvested_crops) > 0 and (harvested_crops[0]['weather_modifier'] != 1.0 or harvested_crops[0]['event_modifier'] != 1.0):
                modifier_info = []
                if harvested_crops[0]['weather_modifier'] != 1.0:
                    weather_mod = harvested_crops[0]['weather_modifier']
                    if weather_mod > 1.0:
                        modifier_info.append(f"🌤️ Thời tiết: +{((weather_mod-1)*100):.0f}%")
                    else:
                        modifier_info.append(f"🌧️ Thời tiết: {((weather_mod-1)*100):.0f}%")
                
                if harvested_crops[0]['event_modifier'] != 1.0:
                    event_mod = harvested_crops[0]['event_modifier']
                    if event_mod > 1.0:
                        modifier_info.append(f"🎉 Sự kiện: +{((event_mod-1)*100):.0f}%")
                    else:
                        modifier_info.append(f"🎪 Sự kiện: {((event_mod-1)*100):.0f}%")
                
                if modifier_info:
                    embed.add_field(
                        name="⚡ Hiệu ứng áp dụng",
                        value="\n".join(modifier_info),
                        inline=True
                    )
            
            if not_ready_crops:
                not_ready_details = []
                for crop_data in not_ready_crops:
                    not_ready_details.append(f"Ô {crop_data['plot']}: {crop_data['name']}")
                
                embed.add_field(
                    name="⏳ Chưa chín",
                    value="\n".join(not_ready_details),
                    inline=False
                )
            
            embed.add_field(
                name="💡 Tip",
                value="Sử dụng `f!market` để xem giá hiện tại\nDùng `f!sell <loại_cây> <số_lượng>` hoặc `f!sell <loại_cây> all` để bán",
                inline=False
            )
            
        else:
            embed = EmbedBuilder.create_error_embed(
                "Tất cả các cây được chỉ định chưa chín!"
            )
            
            not_ready_details = []
            for crop_data in not_ready_crops:
                not_ready_details.append(f"Ô {crop_data['plot']}: {crop_data['name']}")
            
            embed.add_field(
                name="⏳ Cây chưa chín",
                value="\n".join(not_ready_details),
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='sell', aliases=['ban'])
    @registration_required
    async def sell(self, ctx, crop_type: str = None, quantity = None):
        """Bán nông sản từ kho với giá động theo thời tiết
        
        Sử dụng: 
        - f!sell <loại_cây> <số_lượng>
        - f!sell <loại_cây> all - Bán toàn bộ loại cây đó
        
        Ví dụ: 
        - f!sell carrot 5
        - f!sell tomato all
        """
        if not crop_type or quantity is None:
            await ctx.send("❌ Cách sử dụng: `f!sell <loại_cây> <số_lượng>`\n"
                          "Hoặc: `f!sell <loại_cây> all` để bán toàn bộ\n"
                          "Sử dụng `f!market` để xem giá hiện tại")
            return
        
        # Handle "all" keyword
        if isinstance(quantity, str) and quantity.lower() == "all":
            quantity = -1  # Special flag for "all"
        elif isinstance(quantity, str):
            try:
                quantity = int(quantity)
            except ValueError:
                await ctx.send("❌ Số lượng phải là số hoặc 'all'!")
                return
        
        if quantity != -1 and quantity <= 0:
            await ctx.send("❌ Số lượng phải lớn hơn 0!")
            return
        
        user = await self.get_user_safe(ctx.author.id)
        
        # Check if crop type exists
        if crop_type not in config.CROPS:
            crop_names = [config.CROPS[key]['name'] for key in config.CROPS.keys()]
            await ctx.send(f"❌ Loại cây không hợp lệ!\nCó thể bán: {', '.join(crop_names)}")
            return
        
        # Check if user has enough crops
        inventory = await self.bot.db.get_user_inventory(user.user_id)
        available_quantity = 0
        
        for item in inventory:
            if item.item_type == 'crop' and item.item_id == crop_type:
                available_quantity = item.quantity
                break
        
        # Handle "all" case
        if quantity == -1:
            if available_quantity == 0:
                crop_config = config.CROPS[crop_type]
                await ctx.send(f"❌ Bạn không có {crop_config['name']} nào để bán!")
                return
            quantity = available_quantity  # Sell all available
        elif available_quantity < quantity:
            crop_config = config.CROPS[crop_type]
            await ctx.send(f"❌ Bạn chỉ có {available_quantity} {crop_config['name']}!")
            return
        
        # Get unified pricing
        crop_config = config.CROPS[crop_type]
        base_final_price, modifiers = pricing_coordinator.calculate_final_price(crop_type, self.bot)
        
        # 🎀 Apply maid sell price buff
        final_price = maid_helper.apply_sell_price_buff(user.user_id, base_final_price)
        total_earned = quantity * final_price
        
        # Get maid buff info for display
        maid_buffs = maid_helper.get_user_maid_buffs(user.user_id)
        maid_sell_buff = maid_buffs.get('sell_price', 0.0)
        
        # Calculate price change percentage
        base_price = modifiers['base_price']
        price_change = ((final_price - base_price) / base_price) * 100
        
        # Remove crops from inventory
        await self.bot.db.use_item(user.user_id, 'crop', crop_type, quantity)
        
        # Add money
        user.money += total_earned
        await self.bot.db.update_user(user)
        
        # Create detailed embed with "all" indication
        sell_description = f"Đã bán {quantity} {crop_config['name']}"
        if quantity == available_quantity and available_quantity > 1:
            sell_description += " (toàn bộ)"
        
        embed = EmbedBuilder.create_success_embed(
            "💰 Bán thành công!",
            sell_description
        )
        
        # Price breakdown
        price_info = f"💵 Giá bán: {final_price:,} coins/cây\n"
        price_info += f"📊 Giá gốc: {base_price:,} coins/cây\n"
        
        if price_change > 0:
            price_info += f"📈 Bonus: +{price_change:.1f}%"
        elif price_change < 0:
            price_info += f"📉 Giảm: {price_change:.1f}%"
        else:
            price_info += f"➡️ Giá chuẩn (0%)"
        
        embed.add_field(
            name="💱 Chi tiết giá",
            value=price_info,
            inline=True
        )
        
        # Enhanced modifiers explanation including maid buff
        modifiers_breakdown = pricing_coordinator.format_price_breakdown(modifiers, crop_config['name'])
        
        # Add maid buff to breakdown if active
        if maid_sell_buff > 0:
            if modifiers_breakdown:
                modifiers_breakdown += f"\n🎀 Maid Buff: +{maid_sell_buff}%"
            else:
                modifiers_breakdown = f"🎀 Maid Buff: +{maid_sell_buff}%"
        
        # Show step-by-step calculation if multiple modifiers
        if modifiers_breakdown and (modifiers.get('total_modifier', 1.0) != 1.0 or maid_sell_buff > 0):
            step_by_step = f"📊 Giá gốc: {base_price:,} coins\n"
            
            # System modifiers (weather, events, AI)
            if base_final_price != base_price:
                step_by_step += f"⚡ Sau hệ thống: {base_final_price:,} coins\n"
            
            # Maid buff
            if maid_sell_buff > 0:
                step_by_step += f"🎀 Sau maid buff: {final_price:,} coins\n"
            
            modifiers_breakdown = step_by_step + "\n" + modifiers_breakdown
        
        if modifiers_breakdown:
            embed.add_field(
                name="⚡ Phân Tích Giá",
                value=modifiers_breakdown,
                inline=True
            )
        
        # Final totals
        embed.add_field(
            name="💰 Kết quả",
            value=f"Tổng thu: {total_earned:,} coins\n"
                  f"Số dư mới: {user.money:,} coins",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='farmmarket', aliases=['nongsan'])
    @registration_required
    async def farm_market_simple(self, ctx):
        """Xem giá thị trường nông sản (phiên bản đơn giản)
        
        Sử dụng: f!farmmarket
        Sử dụng: f!market để xem thị trường chi tiết hơn
        """
        # Use unified pricing for all crops
        market_data = pricing_coordinator.get_market_overview(self.bot)
        
        embed = EmbedBuilder.create_base_embed(
            "🛒 Giá Nông Sản",
            "Giá bán hiện tại tại nông trại",
            color=0xf39c12
        )
        
        # Add crops in a compact format
        crops_text = []
        for crop_id, data in market_data.items():
            price_change = data['price_change']
            if price_change >= 5:
                icon = "📈"
            elif price_change <= -5:
                icon = "📉"
            else:
                icon = "➡️"
            
            crops_text.append(
                f"{data['emoji']} **{data['name']}**: {data['current_price']} coins {icon}"
            )
        
        # Split into two columns
        half = len(crops_text) // 2
        left_column = "\n".join(crops_text[:half])
        right_column = "\n".join(crops_text[half:])
        
        embed.add_field(
            name="🌾 Nhóm 1",
            value=left_column,
            inline=True
        )
        
        embed.add_field(
            name="🥕 Nhóm 2", 
            value=right_column,
            inline=True
        )
        
        # Trading advice
        advice = pricing_coordinator.get_trading_advice(market_data)
        embed.add_field(
            name="💡 Lời Khuyên",
            value=advice,
            inline=False
        )
        
        embed.set_footer(text="💰 Sử dụng 'f!market' để xem phân tích chi tiết | 'f!sell <cây> <số>' hoặc 'f!sell <cây> all' để bán")
        
        await ctx.send(embed=embed)
    
    @commands.command(name='setupmarket', aliases=['setup_market'])
    @commands.has_permissions(manage_channels=True)
    async def setup_market_notification(self, ctx, channel_id = None, threshold: float = 0.1):
        """Setup kênh thông báo biến động giá nông sản
        
        Sử dụng: f!setupmarket [channel_id] [threshold]
        threshold: % thay đổi tối thiểu để thông báo (mặc định 10%)
        """
        try:
            # Convert channel_id to int if it's a string
            if channel_id is not None and isinstance(channel_id, str):
                try:
                    channel_id = int(channel_id)
                except ValueError:
                    await ctx.send("❌ Channel ID phải là một số!")
                    return
            
            if channel_id is None:
                channel_id = ctx.channel.id
            
            if threshold <= 0 or threshold > 1:
                await ctx.send("❌ Threshold phải từ 0.01 (1%) đến 1.0 (100%)!")
                return
            
            # Verify channel exists and bot can send messages there
            channel = self.bot.get_channel(channel_id)
            if not channel:
                await ctx.send("❌ Không tìm thấy kênh với ID này!")
                return
            
            if not channel.permissions_for(ctx.guild.me).send_messages:
                await ctx.send("❌ Bot không có quyền gửi tin nhắn trong kênh này!")
                return
            
            # Save to database
            await self.bot.db.set_market_notification(ctx.guild.id, channel_id, threshold)
            
            embed = EmbedBuilder.create_success_embed(
                "✅ Đã setup thông báo giá nông sản!",
                f"**Kênh:** <#{channel_id}>\n"
                f"**Ngưỡng thông báo:** {threshold:.1%}\n"
                f"**Trạng thái:** Bật\n\n"
                f"Bot sẽ tự động thông báo khi giá thay đổi ≥ {threshold:.1%}!"
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            print(f"Setup market error: {e}")
            await ctx.send("❌ Có lỗi xảy ra khi setup thông báo!")
    
    @commands.command(name='togglemarket', aliases=['toggle_market'])
    @commands.has_permissions(manage_channels=True)
    async def toggle_market_notification(self, ctx, enabled: bool = None):
        """Bật/tắt thông báo biến động giá nông sản
        
        Sử dụng: f!togglemarket [true/false]
        """
        # Get current settings
        notification = await self.bot.db.get_market_notification(ctx.guild.id)
        
        if not notification:
            await ctx.send("❌ Chưa setup thông báo! Sử dụng `f!setupmarket` trước.")
            return
        
        if enabled is None:
            # Toggle current state
            enabled = not notification.enabled
        
        # Update in database  
        await self.bot.db.toggle_market_notification(ctx.guild.id, enabled)
        
        status = "Bật" if enabled else "Tắt"
        embed = EmbedBuilder.create_success_embed(
            f"✅ Đã {status.lower()} thông báo giá nông sản!",
            f"**Trạng thái:** {status}\n"
            f"**Kênh:** <#{notification.channel_id}>\n"
            f"**Ngưỡng:** {notification.threshold:.1%}"
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='marketstatus', aliases=['market_status'])
    async def market_notification_status(self, ctx):
        """Xem trạng thái thông báo biến động giá nông sản
        
        Sử dụng: f!marketstatus
        """
        notification = await self.bot.db.get_market_notification(ctx.guild.id)
        
        if not notification:
            embed = EmbedBuilder.create_base_embed(
                "📊 Trạng thái thông báo giá nông sản",
                "Chưa được thiết lập",
                color=0x95a5a6
            )
            
            embed.add_field(
                name="💡 Để bắt đầu",
                value="Sử dụng `f!setupmarket` để thiết lập thông báo tự động",
                inline=False
            )
        else:
            status_color = 0x2ecc71 if notification.enabled else 0xe74c3c
            status_text = "🟢 Đang hoạt động" if notification.enabled else "🔴 Đã tắt"
            
            embed = EmbedBuilder.create_base_embed(
                "📊 Trạng thái thông báo giá nông sản",
                status_text,
                color=status_color
            )
            
            embed.add_field(
                name="⚙️ Cài đặt",
                value=f"**Kênh:** <#{notification.channel_id}>\n"
                      f"**Ngưỡng thông báo:** {notification.threshold:.1%}\n"
                      f"**Trạng thái:** {status_text}",
                inline=False
            )
            
            embed.add_field(
                name="🔧 Điều khiển",
                value=f"`f!togglemarket` - Bật/tắt thông báo\n"
                      f"`f!setupmarket` - Cài đặt lại",
                inline=False
            )
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(FarmCog(bot)) 