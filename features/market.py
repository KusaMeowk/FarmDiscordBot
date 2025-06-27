import discord
from discord.ext import commands
from utils.embeds import EmbedBuilder
from utils.pricing import pricing_coordinator
import config
import asyncio

class MarketCog(commands.Cog):
    """Market commands for viewing crop prices and trading advice"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='market', aliases=['thitruong', 'chonthi'])
    async def market_overview(self, ctx):
        """Hiển thị thông tin thị trường với pagination"""
        try:
            # Get market data
            market_data = pricing_coordinator.get_market_overview(self.bot)
            
            # Organize data into pages (4 items per page for compact display)
            crops_list = list(market_data.items())
            items_per_page = 4
            total_pages = (len(crops_list) + items_per_page - 1) // items_per_page
            current_page = 0
            
            def create_market_embed(page):
                embed = EmbedBuilder.create_base_embed(
                    "📊 Thị Trường Nông Sản",
                    f"Giá cả và điều kiện thị trường hiện tại • Trang {page + 1}/{total_pages}",
                    color=0x00ff00
                )
                
                # Get items for current page
                start_idx = page * items_per_page
                end_idx = min(start_idx + items_per_page, len(crops_list))
                page_items = crops_list[start_idx:end_idx]
                
                # Create compact list format
                market_list = []
                for crop_id, data in page_items:
                    # Price change indicator
                    if data['price_change'] >= 10:
                        trend = "📈"
                    elif data['price_change'] <= -10:
                        trend = "📉"
                    else:
                        trend = "➡️"
                    
                    market_list.append(
                        f"{data['emoji']} **{data['name']}**\n"
                        f"💰 Giá: **{data['current_price']}** coins (gốc: {data['base_price']})\n"
                        f"{trend} Thay đổi: **{data['price_change']:+.1f}%**\n"
                        f"📊 Tình trạng: {data['condition']}"
                    )
                
                embed.add_field(
                    name="💹 Danh Sách Thị Trường",
                    value="\n\n".join(market_list),
                    inline=False
                )
                
                # Add trading advice on first page
                if page == 0:
                    advice = pricing_coordinator.get_trading_advice(market_data)
                    embed.add_field(
                        name="💡 Lời Khuyên Giao Dịch",
                        value=advice,
                        inline=False
                    )
                
                embed.set_footer(text="📱 Sử dụng 'f!marketprice <tên_cây>' để xem chi tiết • ⬅️➡️ để chuyển trang")
                return embed
            
            # Create initial message
            embed = create_market_embed(current_page)
            message = await ctx.send(embed=embed)
            
            # Add navigation buttons if more than one page
            if total_pages > 1:
                await message.add_reaction("⬅️")
                await message.add_reaction("➡️")
                await message.add_reaction("❌")
                
                def check(reaction, user):
                    return (user == ctx.author and 
                           str(reaction.emoji) in ["⬅️", "➡️", "❌"] and 
                           reaction.message.id == message.id)
                
                # Navigation loop
                timeout_duration = 60  # 1 minute timeout
                while True:
                    try:
                        reaction, user = await self.bot.wait_for('reaction_add', timeout=timeout_duration, check=check)
                        
                        if str(reaction.emoji) == "❌":
                            break
                        elif str(reaction.emoji) == "⬅️":
                            current_page = (current_page - 1) % total_pages
                        elif str(reaction.emoji) == "➡️":
                            current_page = (current_page + 1) % total_pages
                        
                        # Update embed
                        new_embed = create_market_embed(current_page)
                        await message.edit(embed=new_embed)
                        
                        # Remove user's reaction
                        try:
                            await message.remove_reaction(reaction.emoji, user)
                        except discord.Forbidden:
                            pass
                            
                    except asyncio.TimeoutError:
                        break
                
                # Clean up reactions
                try:
                    await message.clear_reactions()
                except discord.Forbidden:
                    pass
            
        except Exception as e:
            await ctx.send(f"❌ Lỗi khi lấy thông tin thị trường: {e}")
    
    @commands.command(name='marketprice', aliases=['giaca', 'giathuong'])
    async def crop_price_detail(self, ctx, *, crop_name: str = None):
        """Xem chi tiết giá của một loại cây cụ thể"""
        if not crop_name:
            await ctx.send("❓ Vui lòng nhập tên cây cần xem giá! VD: `f!price lúa`")
            return
        
        try:
            # Find crop by name
            crop_id = None
            crop_config = None
            
            for cid, cfg in config.CROPS.items():
                if crop_name.lower() in cfg['name'].lower():
                    crop_id = cid
                    crop_config = cfg
                    break
            
            if not crop_id:
                available_crops = [cfg['name'] for cfg in config.CROPS.values()]
                await ctx.send(f"❌ Không tìm thấy cây '{crop_name}'\n"
                              f"📝 Cây có sẵn: {', '.join(available_crops)}")
                return
            
            # Get detailed price info
            final_price, modifiers = pricing_coordinator.calculate_final_price(crop_id, self.bot)
            
            # Create detailed embed
            embed = EmbedBuilder.create_base_embed(
                f"{crop_config.get('emoji', '🌾')} Chi Tiết Giá - {crop_config['name']}",
                "Phân tích chi tiết các yếu tố ảnh hưởng đến giá",
                color=0x00ff00
            )
            
            # Price breakdown
            breakdown = pricing_coordinator.format_price_breakdown(modifiers, crop_config['name'])
            embed.add_field(
                name="💰 Phân Tích Giá",
                value=breakdown,
                inline=False
            )
            
            # Final price highlight
            base_price = modifiers['base_price']
            change_percent = ((final_price - base_price) / base_price) * 100
            
            if change_percent >= 10:
                trend_info = f"📈 **Tăng mạnh** (+{change_percent:.1f}%)"
                trend_color = "🟢"
            elif change_percent >= 5:
                trend_info = f"📈 **Tăng nhẹ** (+{change_percent:.1f}%)"
                trend_color = "🟡"
            elif change_percent <= -10:
                trend_info = f"📉 **Giảm mạnh** ({change_percent:.1f}%)"
                trend_color = "🔴"
            elif change_percent <= -5:
                trend_info = f"📉 **Giảm nhẹ** ({change_percent:.1f}%)"
                trend_color = "🟠"
            else:
                trend_info = f"➡️ **Ổn định** ({change_percent:+.1f}%)"
                trend_color = "⚫"
            
            embed.add_field(
                name="🎯 Giá Hiện Tại",
                value=f"{trend_color} **{final_price} coins**\n{trend_info}",
                inline=True
            )
            
            # Add growing time and yield info
            grow_time = crop_config.get('grow_time', 3600)
            hours = grow_time // 3600
            embed.add_field(
                name="⏰ Thông Tin Cây",
                value=f"🕐 Thời gian: {hours}h\n🌾 Số lượng: {crop_config.get('harvest_quantity', 1)}",
                inline=True
            )
            
            # Trading advice for this crop
            if change_percent >= 10:
                advice = f"💡 **Nên bán ngay** - Giá đang cao!"
            elif change_percent <= -10:
                advice = f"⏳ **Nên chờ** - Giá đang thấp!"
            else:
                advice = f"➡️ **Có thể giao dịch** - Giá ổn định"
            
            embed.add_field(
                name="💭 Lời Khuyên",
                value=advice,
                inline=False
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Lỗi khi lấy thông tin giá: {e}")
    
    @commands.command(name='trends', aliases=['xuhuong'])
    async def market_trends(self, ctx):
        """Hiển thị xu hướng thị trường"""
        try:
            market_data = pricing_coordinator.get_market_overview(self.bot)
            
            # Categorize crops by trend
            rising = []
            falling = []
            stable = []
            
            for crop_id, data in market_data.items():
                change = data['price_change']
                if change >= 5:
                    rising.append((data['name'], change))
                elif change <= -5:
                    falling.append((data['name'], change))
                else:
                    stable.append((data['name'], change))
            
            # Sort by change percentage
            rising.sort(key=lambda x: x[1], reverse=True)
            falling.sort(key=lambda x: x[1])
            
            embed = EmbedBuilder.create_base_embed(
                "📈 Xu Hướng Thị Trường",
                "Phân tích xu hướng giá cả các loại cây trồng",
                color=0x0099ff
            )
            
            if rising:
                rising_text = "\n".join([f"📈 **{name}**: +{change:.1f}%" for name, change in rising[:5]])
                embed.add_field(
                    name="🔥 Đang Tăng Giá",
                    value=rising_text,
                    inline=True
                )
            
            if falling:
                falling_text = "\n".join([f"📉 **{name}**: {change:.1f}%" for name, change in falling[:5]])
                embed.add_field(
                    name="❄️ Đang Giảm Giá",
                    value=falling_text,
                    inline=True
                )
            
            if stable:
                stable_text = "\n".join([f"➡️ **{name}**: {change:+.1f}%" for name, change in stable[:5]])
                embed.add_field(
                    name="⚖️ Ổn Định",
                    value=stable_text,
                    inline=True
                )
            
            # Market summary
            total_crops = len(market_data)
            rising_count = len(rising)
            falling_count = len(falling)
            stable_count = len(stable)
            
            summary = (
                f"📊 **Tổng quan:** {total_crops} loại cây\n"
                f"📈 Tăng: {rising_count} | "
                f"📉 Giảm: {falling_count} | "
                f"➡️ Ổn định: {stable_count}"
            )
            
            embed.add_field(
                name="📋 Tóm Tắt Thị Trường",
                value=summary,
                inline=False
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Lỗi khi lấy xu hướng thị trường: {e}")

async def setup(bot):
    await bot.add_cog(MarketCog(bot)) 