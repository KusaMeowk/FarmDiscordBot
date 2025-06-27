import discord
from discord.ext import commands
from utils.embeds import EmbedBuilder
from utils.registration import require_registration

class LeaderboardView(discord.ui.View):
    """View với các nút cho bảng xếp hạng"""
    
    def __init__(self, bot):
        super().__init__(timeout=300)
        self.bot = bot
        self.current_board = "money"
    
    @discord.ui.button(label="💰 Giàu có", style=discord.ButtonStyle.green)
    async def money_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await self._update_leaderboard(interaction, "money")
        except Exception as e:
            print(f"Leaderboard money button error: {e}")
            try:
                await interaction.response.send_message("❌ Có lỗi xảy ra. Vui lòng thử lại!", ephemeral=True)
            except:
                pass
    
    @discord.ui.button(label="🔥 Streak", style=discord.ButtonStyle.red)
    async def streak_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await self._update_leaderboard(interaction, "streak")
        except Exception as e:
            print(f"Leaderboard streak button error: {e}")
            try:
                await interaction.response.send_message("❌ Có lỗi xảy ra. Vui lòng thử lại!", ephemeral=True)
            except:
                pass
    
    @discord.ui.button(label="🏞️ Đất đai", style=discord.ButtonStyle.blurple)
    async def land_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await self._update_leaderboard(interaction, "land")
        except Exception as e:
            print(f"Leaderboard land button error: {e}")
            try:
                await interaction.response.send_message("❌ Có lỗi xảy ra. Vui lòng thử lại!", ephemeral=True)
            except:
                pass
    
    @discord.ui.button(label="🔄 Cập nhật", style=discord.ButtonStyle.grey)
    async def refresh_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await self._update_leaderboard(interaction, self.current_board)
        except Exception as e:
            print(f"Leaderboard refresh button error: {e}")
            try:
                await interaction.response.send_message("❌ Có lỗi xảy ra. Vui lòng thử lại!", ephemeral=True)
            except:
                pass
    
    async def _update_leaderboard(self, interaction: discord.Interaction, board_type: str):
        """Cập nhật leaderboard theo loại"""
        try:
            if board_type == "money":
                users = await self.bot.db.get_top_users_by_money(10)
            elif board_type == "streak":
                users = await self.bot.db.get_top_users_by_streak(10)
            elif board_type == "land":
                users = await self.bot.db.get_top_users_by_land(10)
            else:
                users = await self.bot.db.get_top_users(10)
            
            embed = EmbedBuilder.create_leaderboard_embed(users, board_type)
            self.current_board = board_type
            await interaction.response.edit_message(embed=embed, view=self)
        
        except Exception as e:
            print(f"Leaderboard update error: {e}")
            try:
                await interaction.response.send_message("❌ Có lỗi xảy ra khi tải bảng xếp hạng!", ephemeral=True)
            except:
                pass

class LeaderboardCog(commands.Cog):
    """Hệ thống bảng xếp hạng"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='leaderboard', aliases=['top', 'bangxephang'])
    async def leaderboard(self, ctx, board_type: str = "money"):
        """Xem bảng xếp hạng
        
        Sử dụng: f!leaderboard [money|streak|land]
        """
        valid_types = ["money", "streak", "land"]
        if board_type not in valid_types:
            board_type = "money"
        
        # Get users data
        if board_type == "money":
            users = await self.bot.db.get_top_users_by_money(10)
        elif board_type == "streak":
            users = await self.bot.db.get_top_users_by_streak(10)
        elif board_type == "land":
            users = await self.bot.db.get_top_users_by_land(10)
        
        embed = EmbedBuilder.create_leaderboard_embed(users, board_type)
        
        # Add user's rank if not in top 10 and if user is registered
        user = await self.bot.db.get_user(ctx.author.id)
        if user:
            user_rank = await self._get_user_rank(user, board_type)
            if user_rank > 10:
                if board_type == "money":
                    value = f"{user.money:,} coins"
                elif board_type == "streak":
                    value = f"{user.daily_streak} ngày"
                elif board_type == "land":
                    value = f"{user.land_slots} ô đất"
                
                embed.add_field(
                    name="📍 Vị trí của bạn",
                    value=f"#{user_rank} - **{user.username}** - {value}",
                    inline=False
                )
        
        view = LeaderboardView(self.bot)
        view.current_board = board_type
        
        await ctx.send(embed=embed, view=view)
    
    async def _get_user_rank(self, user, board_type: str) -> int:
        """Lấy thứ hạng của user"""
        if board_type == "money":
            all_users = await self.bot.db.get_top_users_by_money(1000)  # Get more users
            for i, u in enumerate(all_users, 1):
                if u.user_id == user.user_id:
                    return i
        elif board_type == "streak":
            all_users = await self.bot.db.get_top_users_by_streak(1000)
            for i, u in enumerate(all_users, 1):
                if u.user_id == user.user_id:
                    return i
        elif board_type == "land":
            all_users = await self.bot.db.get_top_users_by_land(1000)
            for i, u in enumerate(all_users, 1):
                if u.user_id == user.user_id:
                    return i
        
        return 999  # Default if not found
    
    @commands.command(name='rank', aliases=['xephang'])
    async def rank(self, ctx, member: discord.Member = None):
        """Xem thứ hạng của bạn hoặc người khác
        
        Sử dụng: f!rank [@user]
        """
        target = member or ctx.author
        user = await self.bot.db.get_user(target.id)
        
        if not user:
            # Check if it's the command author
            if target == ctx.author:
                # User needs to register
                if not await require_registration(self.bot, ctx):
                    return
                # After registration check passed, get user again
                user = await self.bot.db.get_user(target.id)
            else:
                # Someone else's profile who isn't registered
                await ctx.send(f"❌ {target.display_name} chưa đăng ký tài khoản nông trại!")
                return
        
        # Get ranks for all categories
        money_rank = await self._get_user_rank(user, "money")
        streak_rank = await self._get_user_rank(user, "streak")
        land_rank = await self._get_user_rank(user, "land")
        
        embed = EmbedBuilder.create_base_embed(
            f"📊 Thứ hạng của {user.username}",
            color=0xe74c3c
        )
        
        embed.add_field(
            name="💰 Giàu có",
            value=f"#{money_rank}\n{user.money:,} coins",
            inline=True
        )
        
        embed.add_field(
            name="🔥 Streak",
            value=f"#{streak_rank}\n{user.daily_streak} ngày",
            inline=True
        )
        
        embed.add_field(
            name="🏞️ Đất đai",
            value=f"#{land_rank}\n{user.land_slots} ô",
            inline=True
        )
        
        # Calculate overall score
        overall_score = (1000 - money_rank) + (1000 - streak_rank) + (1000 - land_rank)
        embed.add_field(
            name="🏆 Điểm tổng",
            value=f"{overall_score} điểm",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='compare', aliases=['sosanh'])
    async def compare(self, ctx, member: discord.Member):
        """So sánh thống kê với người khác
        
        Sử dụng: f!compare @user
        """
        # Check if command author is registered
        if not await require_registration(self.bot, ctx):
            return
            
        user1 = await self.bot.db.get_user(ctx.author.id)
        user2 = await self.bot.db.get_user(member.id)
        
        if not user2:
            await ctx.send(f"❌ {member.display_name} chưa đăng ký tài khoản nông trại!")
            return
        
        embed = EmbedBuilder.create_base_embed(
            f"⚔️ So sánh: {user1.username} vs {user2.username}",
            color=0x9b59b6
        )
        
        # Money comparison
        if user1.money > user2.money:
            money_winner = f"🏆 {user1.username}"
            money_diff = user1.money - user2.money
        elif user2.money > user1.money:
            money_winner = f"🏆 {user2.username}"
            money_diff = user2.money - user1.money
        else:
            money_winner = "🤝 Hòa"
            money_diff = 0
        
        embed.add_field(
            name="💰 Tiền",
            value=f"{user1.username}: {user1.money:,}\n"
                  f"{user2.username}: {user2.money:,}\n"
                  f"{money_winner}" + (f" (+{money_diff:,})" if money_diff > 0 else ""),
            inline=True
        )
        
        # Streak comparison
        if user1.daily_streak > user2.daily_streak:
            streak_winner = f"🏆 {user1.username}"
            streak_diff = user1.daily_streak - user2.daily_streak
        elif user2.daily_streak > user1.daily_streak:
            streak_winner = f"🏆 {user2.username}"
            streak_diff = user2.daily_streak - user1.daily_streak
        else:
            streak_winner = "🤝 Hòa"
            streak_diff = 0
        
        embed.add_field(
            name="🔥 Streak",
            value=f"{user1.username}: {user1.daily_streak}\n"
                  f"{user2.username}: {user2.daily_streak}\n"
                  f"{streak_winner}" + (f" (+{streak_diff})" if streak_diff > 0 else ""),
            inline=True
        )
        
        # Land comparison
        if user1.land_slots > user2.land_slots:
            land_winner = f"🏆 {user1.username}"
            land_diff = user1.land_slots - user2.land_slots
        elif user2.land_slots > user1.land_slots:
            land_winner = f"🏆 {user2.username}"
            land_diff = user2.land_slots - user1.land_slots
        else:
            land_winner = "🤝 Hòa"
            land_diff = 0
        
        embed.add_field(
            name="🏞️ Đất",
            value=f"{user1.username}: {user1.land_slots}\n"
                  f"{user2.username}: {user2.land_slots}\n"
                  f"{land_winner}" + (f" (+{land_diff})" if land_diff > 0 else ""),
            inline=True
        )
        
        # Overall winner
        score1 = user1.money + (user1.daily_streak * 1000) + (user1.land_slots * 500)
        score2 = user2.money + (user2.daily_streak * 1000) + (user2.land_slots * 500)
        
        if score1 > score2:
            overall_winner = f"🎉 {user1.username} thắng!"
        elif score2 > score1:
            overall_winner = f"🎉 {user2.username} thắng!"
        else:
            overall_winner = "🤝 Hoàn toàn hòa!"
        
        embed.add_field(
            name="🏆 Tổng kết",
            value=overall_winner,
            inline=False
        )
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(LeaderboardCog(bot)) 