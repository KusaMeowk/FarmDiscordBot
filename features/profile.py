import discord
from discord.ext import commands
from datetime import datetime
import config
from utils.embeds import EmbedBuilder
from utils.registration import registration_required

class ProfileCog(commands.Cog):
    """Quản lý hồ sơ người dùng"""
    
    def __init__(self, bot):
        self.bot = bot
    
    async def get_user_safe(self, user_id: int):
        """Get user from database (registration required)"""
        user = await self.bot.db.get_user(user_id)
        return user
    
    @commands.command(name='profile', aliases=['hoso', 'me'])
    async def profile(self, ctx, member: discord.Member = None):
        """Xem hồ sơ nông trại chi tiết của bạn hoặc người khác
        
        Sử dụng: f!profile [@user]
        """
        target = member or ctx.author
        user = await self.bot.db.get_user(target.id)
        
        # If user is not registered
        if not user:
            # If checking someone else's profile who isn't registered
            if member:
                await ctx.send(f"❌ {member.display_name} chưa đăng ký tài khoản nông trại!")
                return
            
            # If it's the author and they're not registered, show registration guide
            embed = EmbedBuilder.create_base_embed(
                "🌱 Chào mừng đến với nông trại!",
                "Bạn chưa có tài khoản. Hãy đăng ký để bắt đầu!",
                color=0x2ecc71
            )
            
            embed.add_field(
                name="🎯 Để bắt đầu",
                value=(
                    f"**1.** Sử dụng `f!register` để tạo tài khoản\n"
                    f"**2.** Nhận {config.INITIAL_MONEY:,} coins và đất khởi điểm\n" 
                    f"**3.** Bắt đầu hành trình nông trại của bạn!"
                ),
                inline=False
            )
            
            embed.add_field(
                name="💡 Lệnh đăng ký",
                value="`f!register` hoặc `f!dangky`",
                inline=False
            )
            
            embed.set_footer(text="✨ Miễn phí và chỉ mất vài giây!")
            await ctx.send(embed=embed)
            return
        
        # Get detailed farm stats
        crops = await self.bot.db.get_user_crops(user.user_id)
        inventory = await self.bot.db.get_user_inventory(user.user_id)
        
        # Calculate farm statistics
        active_crops = len(crops)
        empty_plots = user.land_slots - active_crops
        
        embed = EmbedBuilder.create_base_embed(
            f"👤 Hồ sơ nông trại - {user.username}",
            color=0x2ecc71
        )
        
        # Add user avatar
        embed.set_thumbnail(url=target.display_avatar.url)
        
        # Basic info
        embed.add_field(
            name="💰 Tài chính",
            value=f"💵 Coins: {user.money:,}",
            inline=True
        )
        
        embed.add_field(
            name="🏡 Nông trại", 
            value=f"🌱 Đất canh tác: {user.land_slots} ô\n"
                  f"🌾 Cây đang trồng: {active_crops}\n"
                  f"⬜ Ô trống: {empty_plots}",
            inline=True
        )
        
        embed.add_field(
            name="📅 Thống kê",
            value=f"🔥 Streak: {user.daily_streak} ngày\n"
                  f"📆 Tham gia: {user.joined_date.strftime('%d/%m/%Y')}",
            inline=True
        )
        
        # Count crops by type
        if crops:
            crop_counts = {}
            total_crop_value = 0
            
            for crop in crops:
                crop_counts[crop.crop_type] = crop_counts.get(crop.crop_type, 0) + 1
                crop_config = config.CROPS.get(crop.crop_type, {})
                total_crop_value += crop_config.get('sell_price', 0)
            
            crop_display = []
            for crop_type, count in crop_counts.items():
                crop_config = config.CROPS.get(crop_type, {})
                emoji = crop_config.get('emoji', '🌱')
                name = crop_config.get('name', crop_type)
                crop_display.append(f"{emoji} {name}: {count}")
            
            embed.add_field(
                name="🌱 Cây đang trồng",
                value="\n".join(crop_display),
                inline=False
            )
            
            # Calculate total value
            net_worth = user.money + total_crop_value
            embed.add_field(
                name="💎 Tổng tài sản",
                value=f"{net_worth:,} coins\n(Bao gồm {total_crop_value:,} từ cây trồng)",
                inline=False
            )
        else:
            embed.add_field(
                name="🌱 Tình trạng nông trại",
                value="🗣️ Chưa trồng cây nào!\nSử dụng `f!shop` để mua hạt và `f!plant` để trồng.",
                inline=False
            )
        
        # Show inventory summary
        if inventory:
            seed_count = sum(1 for item in inventory if item.item_type == 'seed')
            crop_count = sum(1 for item in inventory if item.item_type == 'crop')
            total_items = len(inventory)
            
            inventory_text = f"📦 Tổng: {total_items} loại vật phẩm\n"
            if seed_count > 0:
                inventory_text += f"🌰 Hạt giống: {seed_count} loại\n"
            if crop_count > 0:
                inventory_text += f"🥕 Nông sản: {crop_count} loại"
            
            embed.add_field(
                name="🎒 Kho đồ",
                value=inventory_text,
                inline=True
            )
        
        # Add efficiency stats
        if user.land_slots > 0:
            efficiency = (active_crops / user.land_slots) * 100
            
            if efficiency == 100:
                efficiency_icon = "🔥"
                efficiency_text = "Tối ưu hoàn hảo!"
            elif efficiency >= 75:
                efficiency_icon = "⭐"
                efficiency_text = "Rất tốt!"
            elif efficiency >= 50:
                efficiency_icon = "👍"
                efficiency_text = "Khá tốt"
            elif efficiency >= 25:
                efficiency_icon = "📈"
                efficiency_text = "Cần cải thiện"
            else:
                efficiency_icon = "💤"
                efficiency_text = "Cần hoạt động!"
            
            embed.add_field(
                name="📊 Hiệu suất nông trại",
                value=f"{efficiency_icon} {efficiency:.1f}% - {efficiency_text}",
                inline=True
            )
        
        # Add footer with quick tips
        tips = [
            "💡 Tip: f!farm để xem chi tiết nông trại với timer",
            "💡 Tip: f!daily để nhận phần thưởng hàng ngày",
            "💡 Tip: f!shop để mua hạt giống hoặc mở rộng đất",
            "💡 Tip: f!weather để xem ảnh hưởng thời tiết",
            "💡 Tip: f!leaderboard để xem thứ hạng của bạn"
        ]
        
        tip_index = hash(str(user.user_id) + str(target.id)) % len(tips)
        embed.set_footer(text=tips[tip_index])
        
        await ctx.send(embed=embed)
    
    @commands.command(name='register', aliases=['dangky'])
    async def register(self, ctx):
        """Đăng ký tài khoản nông trại
        
        Sử dụng: f!register
        """
        existing_user = await self.bot.db.get_user(ctx.author.id)
        if existing_user:
            await ctx.send("❌ Bạn đã có tài khoản rồi! Sử dụng `f!profile` để xem thông tin.")
            return
        
        user = await self.bot.db.create_user(ctx.author.id, ctx.author.display_name)
        
        embed = EmbedBuilder.create_success_embed(
            "Chào mừng đến với nông trại!",
            f"Tài khoản đã được tạo thành công!\n"
            f"💰 Tiền khởi điểm: {config.INITIAL_MONEY:,} coins\n"
            f"🏞️ Đất ban đầu: {config.INITIAL_LAND_SLOTS} ô\n\n"
            f"Sử dụng `{config.PREFIX}help` để xem hướng dẫn!"
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='inventory', aliases=['inv', 'kho'])
    @registration_required
    async def inventory(self, ctx):
        """Xem kho đồ của bạn
        
        Sử dụng: f!inventory
        """
        user = await self.get_user_safe(ctx.author.id)
        inventory = await self.bot.db.get_user_inventory(user.user_id)
        
        embed = EmbedBuilder.create_base_embed(
            f"🎒 Kho đồ của {ctx.author.display_name}",
            color=0x95a5a6
        )
        
        if not inventory:
            embed.add_field(
                name="Trống",
                value="Bạn chưa có vật phẩm nào. Hãy mua ở cửa hàng!",
                inline=False
            )
        else:
            # Group items by type
            seeds = [item for item in inventory if item.item_type == 'seed']
            crops = [item for item in inventory if item.item_type == 'crop']
            tools = [item for item in inventory if item.item_type == 'tool']
            buffs = [item for item in inventory if item.item_type == 'buff']
            
            if seeds:
                seed_list = []
                for item in seeds:
                    crop_config = config.CROPS.get(item.item_id, {})
                    name = crop_config.get('name', item.item_id)
                    seed_list.append(f"{name}: {item.quantity}")
                
                embed.add_field(
                    name="🌱 Hạt giống",
                    value="\n".join(seed_list),
                    inline=True
                )
            
            if crops:
                crop_list = []
                for item in crops:
                    crop_config = config.CROPS.get(item.item_id, {})
                    name = crop_config.get('name', item.item_id)
                    crop_list.append(f"{name}: {item.quantity}")
                
                embed.add_field(
                    name="🥕 Nông sản",
                    value="\n".join(crop_list),
                    inline=True
                )
            
            if tools:
                tool_list = []
                for item in tools:
                    tool_list.append(f"{item.item_id}: {item.quantity}")
                
                embed.add_field(
                    name="🔧 Công cụ",
                    value="\n".join(tool_list),
                    inline=True
                )
            
            if buffs:
                buff_list = []
                for item in buffs:
                    buff_list.append(f"{item.item_id}: {item.quantity}")
                
                embed.add_field(
                    name="⚡ Buff",
                    value="\n".join(buff_list),
                    inline=True
                )
        
        embed.add_field(
            name="💰 Số dư",
            value=f"{user.money:,} coins",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='rename', aliases=['doiten'])
    @registration_required
    async def rename(self, ctx, *, new_name: str):
        """Đổi tên hiển thị trong game
        
        Sử dụng: f!rename <tên mới>
        """
        if len(new_name) > 20:
            await ctx.send("❌ Tên không được quá 20 ký tự!")
            return
        
        if len(new_name) < 2:
            await ctx.send("❌ Tên phải có ít nhất 2 ký tự!")
            return
        
        user = await self.get_user_safe(ctx.author.id)
        old_name = user.username
        user.username = new_name
        
        await self.bot.db.update_user(user)
        
        embed = EmbedBuilder.create_success_embed(
            "Đổi tên thành công!",
            f"Tên đã được đổi từ **{old_name}** thành **{new_name}**"
        )
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(ProfileCog(bot)) 