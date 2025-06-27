import discord
from discord.ext import commands
import config
from utils.embeds import EmbedBuilder
from utils.helpers import calculate_land_expansion_cost
from utils.registration import registration_required
from features.maid_helper import maid_helper
from features.maid_display_integration import add_maid_buffs_to_embed

class ShopView(discord.ui.View):
    """View với các nút bấm cho cửa hàng"""
    
    def __init__(self, bot, user_id):
        super().__init__(timeout=300)
        self.bot = bot
        self.user_id = user_id
    
    @discord.ui.button(label="🌱 Hạt giống", style=discord.ButtonStyle.green)
    async def seeds_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            if interaction.user.id != self.user_id:
                await interaction.response.send_message("❌ Bạn không thể sử dụng nút này!", ephemeral=True)
                return
            
            # Get event modifier for seed costs
            events_cog = self.bot.get_cog('EventsCog')
            cost_modifier = 1.0
            event_note = ""
            
            if events_cog and hasattr(events_cog, 'get_current_seed_cost_modifier'):
                cost_modifier = events_cog.get_current_seed_cost_modifier()
                
                if cost_modifier < 1.0:
                    discount_percent = (1.0 - cost_modifier) * 100
                    event_note = f"🌟 **Giảm giá sự kiện: -{discount_percent:.0f}%**\n"
                elif cost_modifier > 1.0:
                    increase_percent = (cost_modifier - 1.0) * 100
                    event_note = f"💸 **Tăng giá sự kiện: +{increase_percent:.0f}%**\n"
            
            # Create seeds shop embed
            embed_title = "🌱 Cửa hàng Hạt giống"
            if event_note:
                embed_title += " (Có sự kiện!)"
                
            embed = EmbedBuilder.create_base_embed(embed_title, color=0x2ecc71)
            
            # Add maid buffs to seed shop
            embed = add_maid_buffs_to_embed(embed, self.user_id, "shop")
            
            if event_note:
                embed.description = event_note
            
            # Split crops into groups to avoid Discord embed limits
            basic_seeds = []
            premium_seeds = []
            
            for crop_id, crop_data in config.CROPS.items():
                growth_time = crop_data['growth_time'] // 60  # Convert to minutes
                base_price = crop_data['price']
                event_price = int(base_price * cost_modifier)
                
                # 🎀 Apply maid seed discount buff to displayed price
                from features.maid_helper import maid_helper
                final_price = maid_helper.apply_seed_discount_buff(self.user_id, event_price)
                
                # 🔍 Debug logging
                if final_price != base_price:
                    print(f"🎀 Maid buff applied: {crop_id} {base_price} -> {final_price} coins (user: {self.user_id})")
                profit = crop_data['sell_price'] - final_price  # Profit with all modifiers
                
                price_display = f"{final_price:,} coins"
                if final_price != base_price:
                    price_display += f" ~~{base_price:,}~~"
                
                seed_info = (
                    f"**{crop_data['name']}**\n"
                    f"💰 Giá: {price_display} | ⏰ {growth_time}p\n"
                    f"💎 Bán: {crop_data['sell_price']:,} coins | 📈 Lợi: {profit:,}\n"
                    f"`f!buy {crop_id} <số_lượng>`"
                )
                
                if crop_data['price'] <= 100:  # Basic crops
                    basic_seeds.append(seed_info)
                else:  # Premium crops
                    premium_seeds.append(seed_info)
            
            # Add basic seeds field
            if basic_seeds:
                embed.add_field(
                    name="🌱 Hạt giống cơ bản",
                    value="\n\n".join(basic_seeds),
                    inline=False
                )
            
            # Add premium seeds fields (split if needed)
            if premium_seeds:
                # Check if we need to split premium seeds
                all_premium_text = "\n\n".join(premium_seeds)
                if len(all_premium_text) > 1000:  # Discord field limit is 1024
                    # Split into multiple fields
                    mid_point = len(premium_seeds) // 2
                    
                    embed.add_field(
                        name="✨ Hạt giống cao cấp (Phần 1)",
                        value="\n\n".join(premium_seeds[:mid_point]),
                        inline=False
                    )
                    
                    embed.add_field(
                        name="✨ Hạt giống cao cấp (Phần 2)",
                        value="\n\n".join(premium_seeds[mid_point:]),
                        inline=False
                    )
                else:
                    embed.add_field(
                        name="✨ Hạt giống cao cấp",
                        value=all_premium_text,
                        inline=False
                    )
            
            embed.add_field(
                name="💡 Tip",
                value="Các loại cây cao cấp có lợi nhuận và thời gian phát triển khác nhau. Chọn theo chiến lược của bạn!",
                inline=False
            )
            
            await interaction.response.edit_message(embed=embed, view=self)
            
        except Exception as e:
            print(f"Shop seeds button error: {e}")
            try:
                await interaction.response.send_message("❌ Có lỗi xảy ra. Vui lòng thử lại!", ephemeral=True)
            except:
                pass
    
    @discord.ui.button(label="🏞️ Mở rộng đất", style=discord.ButtonStyle.blurple)
    async def land_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            if interaction.user.id != self.user_id:
                await interaction.response.send_message("❌ Bạn không thể sử dụng nút này!", ephemeral=True)
                return
            
            user = await self.bot.db.get_user(self.user_id)
            if not user:
                await interaction.response.send_message("❌ Không tìm thấy thông tin người dùng!", ephemeral=True)
                return
                
            expansion_cost = calculate_land_expansion_cost(user.land_slots)
            
            embed = EmbedBuilder.create_base_embed("🏞️ Mở rộng đất đai", color=0x3498db)
            
            embed.add_field(
                name="📊 Thông tin hiện tại",
                value=f"🏞️ Ô đất hiện có: {user.land_slots}\n💰 Số dư: {user.money:,} coins",
                inline=False
            )
            
            if expansion_cost is None:
                embed.add_field(
                    name="🏆 Đã đạt tối đa",
                    value="Bạn đã mở rộng hết mức có thể!",
                    inline=False
                )
            else:
                embed.add_field(
                    name="💰 Chi phí mở rộng",
                    value=f"{expansion_cost:,} coins (+1 ô đất)",
                    inline=False
                )
                
                if user.money >= expansion_cost:
                    embed.add_field(
                        name="✅ Có thể mua",
                        value=f"Sử dụng `f!buy land` để mở rộng",
                        inline=False
                    )
                else:
                    needed = expansion_cost - user.money
                    embed.add_field(
                        name="❌ Không đủ tiền",
                        value=f"Cần thêm {needed:,} coins",
                        inline=False
                    )
            
            await interaction.response.edit_message(embed=embed, view=self)
            
        except Exception as e:
            print(f"Shop land button error: {e}")
            try:
                await interaction.response.send_message("❌ Có lỗi xảy ra. Vui lòng thử lại!", ephemeral=True)
            except:
                pass
    
    @discord.ui.button(label="🐟 Cá", style=discord.ButtonStyle.secondary)
    async def fish_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            if interaction.user.id != self.user_id:
                await interaction.response.send_message("❌ Bạn không thể sử dụng nút này!", ephemeral=True)
                return
            
            # Create fish shop embed
            embed = EmbedBuilder.create_base_embed("🐟 Cửa hàng Cá", color=0x1e90ff)
            embed.description = "Chọn loại cá để nuôi trong ao của bạn!"
            
            # Group fish by tier
            tier_groups = {}
            for fish_id, fish_data in config.FISH_SPECIES.items():
                tier = fish_data.get('tier', 1)
                if tier not in tier_groups:
                    tier_groups[tier] = []
                
                growth_time = fish_data['growth_time'] // 60  # Convert to minutes
                profit = fish_data['sell_price'] - fish_data['buy_price']
                profit_percent = (profit / fish_data['buy_price']) * 100
                
                fish_info = (
                    f"**{fish_data['name']}**\n"
                    f"💰 Giá: {fish_data['buy_price']:,} coins | ⏰ {growth_time}p\n"
                    f"💎 Bán: {fish_data['sell_price']:,} coins | 📈 Lợi: {profit_percent:.1f}%\n"
                    f"✨ {fish_data['special_ability']}\n"
                    f"`f!pond buy {fish_id}`"
                )
                tier_groups[tier].append(fish_info)
            
            # Add fields for each tier
            tier_names = {1: "🐟 Cá Cơ Bản", 2: "✨ Cá Hiếm", 3: "🌟 Cá Huyền Thoại"}
            
            for tier in sorted(tier_groups.keys()):
                tier_name = tier_names.get(tier, f"Tier {tier}")
                embed.add_field(
                    name=tier_name,
                    value="\n\n".join(tier_groups[tier]),
                    inline=False
                )
            
            embed.add_field(
                name="💡 Hướng dẫn",
                value="• Sử dụng `f!pond` để xem ao cá\n• Cá tier cao có lợi nhuận lớn hơn nhưng cần thời gian lâu hơn\n• Đảm bảo có đủ ô trống trong ao trước khi mua",
                inline=False
            )
            
            await interaction.response.edit_message(embed=embed, view=self)
            
        except Exception as e:
            print(f"Shop fish button error: {e}")
            try:
                await interaction.response.send_message("❌ Có lỗi xảy ra. Vui lòng thử lại!", ephemeral=True)
            except:
                pass

    @discord.ui.button(label="🐄 Gia Súc", style=discord.ButtonStyle.secondary)
    async def livestock_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            if interaction.user.id != self.user_id:
                await interaction.response.send_message("❌ Bạn không thể sử dụng nút này!", ephemeral=True)
                return
            
            # Create livestock shop embed
            embed = EmbedBuilder.create_base_embed("🐄 Cửa hàng Gia Súc", color=0x8b4513)
            embed.description = "Chọn loại gia súc để nuôi trong chuồng của bạn!"
            
            # Group animals by tier
            tier_groups = {}
            for animal_id, animal_data in config.ANIMAL_SPECIES.items():
                tier = animal_data.get('tier', 1)
                if tier not in tier_groups:
                    tier_groups[tier] = []
                
                growth_time = animal_data['growth_time'] // 3600  # Convert to hours
                profit = animal_data['sell_price'] - animal_data['buy_price']
                profit_percent = (profit / animal_data['buy_price']) * 100
                
                # Check if animal produces products
                product_info = ""
                if animal_id in config.LIVESTOCK_PRODUCTS:
                    product_data = config.LIVESTOCK_PRODUCTS[animal_id]
                    product_time = product_data['production_time'] // 60  # Convert to minutes
                    product_info = f"\n🥛 Sản phẩm: {product_data['product_emoji']} {product_data['product_name']} (mỗi {product_time}p)"
                
                animal_info = (
                    f"**{animal_data['name']}**\n"
                    f"💰 Giá: {animal_data['buy_price']:,} coins | ⏰ {growth_time}h\n"
                    f"💎 Bán: {animal_data['sell_price']:,} coins | 📈 Lợi: {profit_percent:.1f}%\n"
                    f"✨ {animal_data['special_ability']}{product_info}\n"
                    f"`f!barn buy {animal_id}`"
                )
                tier_groups[tier].append(animal_info)
            
            # Add fields for each tier
            tier_names = {1: "🐄 Gia Súc Cơ Bản", 2: "✨ Gia Cầm", 3: "🌟 Thú Cưng Cao Cấp"}
            
            for tier in sorted(tier_groups.keys()):
                tier_name = tier_names.get(tier, f"Tier {tier}")
                field_value = "\n\n".join(tier_groups[tier])
                
                # Check if field is too long and split if needed
                if len(field_value) > 1000:
                    mid_point = len(tier_groups[tier]) // 2
                    embed.add_field(
                        name=f"{tier_name} (Phần 1)",
                        value="\n\n".join(tier_groups[tier][:mid_point]),
                        inline=False
                    )
                    embed.add_field(
                        name=f"{tier_name} (Phần 2)",
                        value="\n\n".join(tier_groups[tier][mid_point:]),
                        inline=False
                    )
                else:
                    embed.add_field(
                        name=tier_name,
                        value=field_value,
                        inline=False
                    )
            
            embed.add_field(
                name="💡 Hướng dẫn",
                value="• Sử dụng `f!barn` để xem chuồng trại\n• Gia súc tier cao cần thời gian lâu hơn nhưng có giá trị cao\n• Một số gia súc có thể sản xuất sản phẩm định kỳ\n• Đảm bảo có đủ ô trống trong chuồng trước khi mua",
                inline=False
            )
            
            await interaction.response.edit_message(embed=embed, view=self)
            
        except Exception as e:
            print(f"Shop livestock button error: {e}")
            try:
                await interaction.response.send_message("❌ Có lỗi xảy ra. Vui lòng thử lại!", ephemeral=True)
            except:
                pass

    @discord.ui.button(label="🔄 Quay lại", style=discord.ButtonStyle.grey)
    async def back_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            if interaction.user.id != self.user_id:
                await interaction.response.send_message("❌ Bạn không thể sử dụng nút này!", ephemeral=True)
                return
            
            embed = EmbedBuilder.create_shop_embed()
            await interaction.response.edit_message(embed=embed, view=self)
            
        except Exception as e:
            print(f"Shop back button error: {e}")
            try:
                await interaction.response.send_message("❌ Có lỗi xảy ra. Vui lòng thử lại!", ephemeral=True)
            except:
                pass

class ShopCog(commands.Cog):
    """Hệ thống cửa hàng - mua bán vật phẩm"""
    
    def __init__(self, bot):
        self.bot = bot
    
    async def get_user_safe(self, user_id: int):
        """Get user from database (registration required)"""
        user = await self.bot.db.get_user(user_id)
        return user
    
    @commands.command(name='shop', aliases=['cuahang'])
    @registration_required
    async def shop(self, ctx):
        """Xem cửa hàng
        
        Sử dụng: f!shop
        """
        user = await self.get_user_safe(ctx.author.id)
        
        embed = EmbedBuilder.create_shop_embed()
        embed.add_field(
            name="💰 Số dư của bạn",
            value=f"{user.money:,} coins",
            inline=False
        )
        
        # Add maid buffs to main shop
        embed = add_maid_buffs_to_embed(embed, ctx.author.id, "shop")
        
        view = ShopView(self.bot, user.user_id)
        await ctx.send(embed=embed, view=view)
    
    @commands.command(name='buy', aliases=['mua'])
    @registration_required
    async def buy(self, ctx, item_type: str = None, quantity = 1):
        """Mua vật phẩm từ cửa hàng
        
        Sử dụng: 
        - f!buy <loại_hạt> <số_lượng> - Mua hạt giống
        - f!buy land - Mở rộng đất
        
        Ví dụ: f!buy carrot 5
        """
        try:
            if not item_type:
                await ctx.send("❌ Cách sử dụng: `f!buy <vật_phẩm> <số_lượng>`\n"
                              "Ví dụ: `f!buy carrot 5` hoặc `f!buy land`")
                return
            
            # Convert quantity to int if it's a string
            if isinstance(quantity, str):
                try:
                    quantity = int(quantity)
                except ValueError:
                    await ctx.send("❌ Số lượng phải là một số nguyên!\n"
                                  "Ví dụ: `f!buy carrot 5`")
                    return
            
            user = await self.get_user_safe(ctx.author.id)
            if not user:
                await ctx.send("❌ Không tìm thấy thông tin người dùng!")
                return
            
            if item_type == "land":
                await self._buy_land(ctx, user)
            elif item_type in config.CROPS:
                await self._buy_seeds(ctx, user, item_type, quantity)
            else:
                await ctx.send("❌ Vật phẩm không tồn tại! Sử dụng `f!shop` để xem danh sách.")
                
        except Exception as e:
            print(f"Buy command error: {e}")
            await ctx.send("❌ Có lỗi xảy ra. Vui lòng thử lại!")
    
    async def _buy_seeds(self, ctx, user, crop_type: str, quantity):
        """Mua hạt giống"""
        try:
            # Ensure quantity is int
            if isinstance(quantity, str):
                quantity = int(quantity)
            
            if quantity <= 0:
                await ctx.send("❌ Số lượng phải lớn hơn 0!")
                return
            
            crop_config = config.CROPS[crop_type]
            base_price = crop_config['price']
            
            # Apply event modifier to seed cost
            events_cog = self.bot.get_cog('EventsCog')
            cost_modifier = 1.0
            event_info = ""
            
            if events_cog and hasattr(events_cog, 'get_current_seed_cost_modifier'):
                cost_modifier = events_cog.get_current_seed_cost_modifier()
                
                if cost_modifier < 1.0:
                    discount_percent = (1.0 - cost_modifier) * 100
                    event_info = f"\n🌟 Giảm giá sự kiện: -{discount_percent:.0f}%"
                elif cost_modifier > 1.0:
                    increase_percent = (cost_modifier - 1.0) * 100
                    event_info = f"\n💸 Tăng giá sự kiện: +{increase_percent:.0f}%"
            
            # Calculate final cost with modifier
            event_price_per_seed = int(base_price * cost_modifier)
            
            # 🎀 Apply maid seed discount buff
            final_price_per_seed = maid_helper.apply_seed_discount_buff(user.user_id, event_price_per_seed)
            total_cost = final_price_per_seed * quantity
            
            if user.money < total_cost:
                await ctx.send(f"❌ Không đủ tiền! Cần {total_cost:,} coins, bạn có {user.money:,} coins.")
                return
            
            # Deduct money
            user.money -= total_cost
            await self.bot.db.update_user(user)
            
            # Add seeds to inventory
            await self.bot.db.add_item(user.user_id, 'seed', crop_type, quantity)
            
            # Build success message
            success_message = f"Đã mua {quantity} hạt {crop_config['name']}\n"
            
            if cost_modifier != 1.0:
                success_message += f"💰 Giá gốc: {base_price:,} coins/hạt\n"
                success_message += f"💰 Giá thực: {final_price_per_seed:,} coins/hạt{event_info}\n"
            else:
                success_message += f"💰 Giá: {final_price_per_seed:,} coins/hạt\n"
            
            success_message += f"💰 Tổng chi phí: {total_cost:,} coins\n"
            success_message += f"💰 Số dư còn lại: {user.money:,} coins"
            
            embed = EmbedBuilder.create_success_embed(
                "Mua thành công!",
                success_message
            )
            
            await ctx.send(embed=embed)
            
        except ValueError:
            await ctx.send("❌ Số lượng phải là một số nguyên!")
        except Exception as e:
            print(f"Buy seeds error: {e}")
            await ctx.send("❌ Có lỗi xảy ra khi mua hạt giống!")
    
    async def _buy_land(self, ctx, user):
        """Mở rộng đất đai"""
        expansion_cost = calculate_land_expansion_cost(user.land_slots)
        
        if expansion_cost is None:
            await ctx.send("❌ Bạn đã mở rộng hết mức có thể!")
            return
        
        if user.money < expansion_cost:
            needed = expansion_cost - user.money
            await ctx.send(f"❌ Không đủ tiền! Cần {expansion_cost:,} coins, "
                          f"bạn có {user.money:,} coins (thiếu {needed:,} coins).")
            return
        
        # Deduct money and add land slot
        user.money -= expansion_cost
        user.land_slots += 1
        await self.bot.db.update_user(user)
        
        embed = EmbedBuilder.create_success_embed(
            "Mở rộng đất thành công!",
            f"Đã mở rộng thêm 1 ô đất!\n"
            f"💰 Chi phí: {expansion_cost:,} coins\n"
            f"🏞️ Tổng ô đất: {user.land_slots}\n"
            f"💰 Số dư còn lại: {user.money:,} coins"
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='price', aliases=['gia'])
    async def price(self, ctx, crop_type: str = None):
        """Xem giá một loại cây cụ thể
        
        Sử dụng: f!price <loại_cây>
        """
        if not crop_type:
            await ctx.send("❌ Cách sử dụng: `f!price <loại_cây>`\n"
                          "Ví dụ: `f!price carrot`")
            return
        
        if crop_type not in config.CROPS:
            crop_names = [config.CROPS[key]['name'] for key in config.CROPS.keys()]
            await ctx.send(f"❌ Loại cây không hợp lệ!\nCó thể xem: {', '.join(crop_names)}")
            return
        
        crop_config = config.CROPS[crop_type]
        
        # Get dynamic pricing if available
        try:
            from utils.pricing import pricing_coordinator
            final_price, modifiers = pricing_coordinator.calculate_final_price(crop_type, self.bot)
            
            base_price = modifiers['base_price']
            price_change = ((final_price - base_price) / base_price) * 100
        except:
            # Fallback to static pricing
            final_price = crop_config['sell_price']
            price_change = 0
        
        embed = EmbedBuilder.create_base_embed(
            f"💰 Giá {crop_config['name']}",
            color=0xf39c12
        )
        
        embed.add_field(
            name="🌱 Hạt giống",
            value=f"💰 Giá mua: {crop_config['price']:,} coins",
            inline=True
        )
        
        embed.add_field(
            name="🥕 Nông sản",
            value=f"💰 Giá bán: {final_price:,} coins\n"
                  f"📊 Giá gốc: {crop_config['sell_price']:,} coins",
            inline=True
        )
        
        # Profit calculation
        profit = final_price - crop_config['price']
        profit_margin = (profit / crop_config['price']) * 100
        
        embed.add_field(
            name="📈 Phân tích",
            value=f"💰 Lợi nhuận: {profit:,} coins\n"
                  f"📊 Tỷ suất: {profit_margin:.1f}%\n"
                  f"⏰ Thời gian: {crop_config['growth_time'] // 60}p",
            inline=False
        )
        
        if price_change != 0:
            if price_change > 0:
                embed.add_field(
                    name="📈 Giá hiện tại",
                    value=f"Tăng {price_change:.1f}% so với giá gốc",
                    inline=False
                )
            else:
                embed.add_field(
                    name="📉 Giá hiện tại",
                    value=f"Giảm {abs(price_change):.1f}% so với giá gốc",
                    inline=False
                )
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(ShopCog(bot)) 