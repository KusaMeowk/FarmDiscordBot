import discord
from discord.ext import commands
from datetime import datetime, timedelta
import random
import config
from utils.embeds import EmbedBuilder
from utils.registration import registration_required

class DailyCog(commands.Cog):
    """Hệ thống thưởng hàng ngày"""
    
    def __init__(self, bot):
        self.bot = bot
    
    async def get_user_safe(self, user_id: int):
        """Get user from database (registration required)"""
        user = await self.bot.db.get_user(user_id)
        return user
    
    @commands.command(name='daily', aliases=['hangngay'])
    @registration_required
    async def daily(self, ctx):
        """Nhận thưởng hàng ngày
        
        Sử dụng: f!daily
        """
        user = await self.get_user_safe(ctx.author.id)
        
        now = datetime.now()
        
        # Check if user can claim daily
        if user.last_daily:
            time_since_last = now - user.last_daily
            
            if time_since_last < timedelta(hours=20):
                # Calculate time until next daily
                next_daily = user.last_daily + timedelta(hours=20)
                time_left = next_daily - now
                hours = int(time_left.total_seconds() // 3600)
                minutes = int((time_left.total_seconds() % 3600) // 60)
                
                embed = EmbedBuilder.create_error_embed(
                    "Chưa thể nhận thưởng!",
                    f"Bạn đã nhận thưởng hàng ngày rồi!\n"
                    f"⏰ Có thể nhận lại sau: {hours}h {minutes}p"
                )
                
                await ctx.send(embed=embed)
                return
            
            # Check if streak should continue (within 48 hours)
            if time_since_last <= timedelta(hours=48):
                user.daily_streak += 1
            else:
                user.daily_streak = 1
        else:
            user.daily_streak = 1
        
        # Calculate rewards based on streak
        base_reward = config.DAILY_BASE_REWARD
        streak_bonus = min(user.daily_streak * config.DAILY_STREAK_BONUS, config.DAILY_MAX_STREAK_BONUS)
        total_reward = base_reward + streak_bonus
        
        # Random bonus chance
        bonus_chance = random.randint(1, 100)
        bonus_reward = 0
        bonus_text = ""
        
        if bonus_chance <= 10:  # 10% chance for big bonus
            bonus_reward = total_reward
            bonus_text = "🎰 **JACKPOT!** Gấp đôi phần thưởng!"
        elif bonus_chance <= 30:  # 20% chance for medium bonus
            bonus_reward = total_reward // 2
            bonus_text = "✨ **Lucky!** Thêm 50% phần thưởng!"
        
        final_reward = total_reward + bonus_reward
        
        # Give rewards
        user.money += final_reward
        user.last_daily = now
        await self.bot.db.update_user(user)
        
        # Create success embed
        embed = EmbedBuilder.create_success_embed(
            "🎁 Nhận thưởng hàng ngày thành công!",
            f"💰 Phần thưởng: {final_reward:,} coins\n"
            f"🔥 Streak: {user.daily_streak} ngày\n"
            f"💰 Số dư mới: {user.money:,} coins"
        )
        
        # Reward breakdown
        embed.add_field(
            name="📊 Chi tiết phần thưởng",
            value=f"💵 Cơ bản: {base_reward:,} coins\n"
                  f"🔥 Streak bonus: {streak_bonus:,} coins\n" + 
                  (f"🎲 Bonus may mắn: {bonus_reward:,} coins\n" if bonus_reward > 0 else ""),
            inline=False
        )
        
        if bonus_text:
            embed.add_field(name="🎉 May mắn!", value=bonus_text, inline=False)
        
        # Streak milestones
        next_milestone = ((user.daily_streak // 5) + 1) * 5
        days_to_milestone = next_milestone - user.daily_streak
        
        embed.add_field(
            name="🎯 Mục tiêu tiếp theo",
            value=f"Còn {days_to_milestone} ngày để đạt streak {next_milestone}!",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='streak', aliases=['chuoi'])
    @registration_required
    async def streak(self, ctx, member: discord.Member = None):
        """Xem chuỗi thưởng hàng ngày
        
        Sử dụng: f!streak [@user]
        """
        target = member or ctx.author
        user = await self.get_user_safe(target.id)
        
        if member and not user:
            await ctx.send(f"❌ {member.display_name} chưa đăng ký tài khoản nông trại!")
            return
        
        embed = EmbedBuilder.create_base_embed(
            f"🔥 Streak của {target.display_name}",
            color=0xe67e22
        )
        
        embed.set_thumbnail(url=target.display_avatar.url)
        
        # Current streak info
        if user.daily_streak > 0:
            embed.add_field(
                name="🔥 Streak hiện tại",
                value=f"{user.daily_streak} ngày",
                inline=True
            )
            
            # Calculate next rewards
            next_base = config.DAILY_BASE_REWARD
            next_bonus = min((user.daily_streak + 1) * config.DAILY_STREAK_BONUS, config.DAILY_MAX_STREAK_BONUS)
            next_total = next_base + next_bonus
            
            embed.add_field(
                name="💰 Thưởng ngày mai",
                value=f"{next_total:,} coins",
                inline=True
            )
        else:
            embed.add_field(
                name="🔥 Streak hiện tại",
                value="0 ngày",
                inline=True
            )
            
            embed.add_field(
                name="💰 Thưởng ngày mai",
                value=f"{config.DAILY_BASE_REWARD:,} coins",
                inline=True
            )
        
        # Last claim time
        if user.last_daily:
            last_claim = user.last_daily.strftime("%d/%m/%Y %H:%M")
            embed.add_field(
                name="⏰ Lần cuối nhận",
                value=last_claim,
                inline=True
            )
        
        # Streak milestones
        milestones = [5, 10, 25, 50, 100]
        achieved = [m for m in milestones if user.daily_streak >= m]
        next_milestone = next((m for m in milestones if user.daily_streak < m), None)
        
        if achieved:
            embed.add_field(
                name="🏆 Thành tích đạt được",
                value="⭐ " + ", ".join([f"{m} ngày" for m in achieved]),
                inline=False
            )
        
        if next_milestone:
            days_left = next_milestone - user.daily_streak
            embed.add_field(
                name="🎯 Mục tiêu tiếp theo",
                value=f"Streak {next_milestone} ngày (còn {days_left} ngày)",
                inline=False
            )
        else:
            embed.add_field(
                name="🎉 Hoàn thành tất cả",
                value="Bạn đã đạt tất cả mục tiêu streak!",
                inline=False
            )
        
        # Show claim status
        now = datetime.now()
        if user.last_daily:
            time_since = now - user.last_daily
            if time_since >= timedelta(hours=20):
                embed.add_field(
                    name="✅ Trạng thái",
                    value="Có thể nhận thưởng ngay!",
                    inline=False
                )
            else:
                next_daily = user.last_daily + timedelta(hours=20)
                time_left = next_daily - now
                hours = int(time_left.total_seconds() // 3600)
                minutes = int((time_left.total_seconds() % 3600) // 60)
                
                embed.add_field(
                    name="⏳ Trạng thái",
                    value=f"Có thể nhận lại sau {hours}h {minutes}p",
                    inline=False
                )
        else:
            embed.add_field(
                name="🎁 Trạng thái",
                value="Chưa từng nhận thưởng hàng ngày!",
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='rewards', aliases=['thuong'])
    async def rewards_info(self, ctx):
        """Xem thông tin hệ thống thưởng hàng ngày
        
        Sử dụng: f!rewards
        """
        embed = EmbedBuilder.create_base_embed(
            "🎁 Hệ thống thưởng hàng ngày",
            "Thông tin chi tiết về phần thưởng",
            color=0x3498db
        )
        
        embed.add_field(
            name="💰 Phần thưởng cơ bản",
            value=f"{config.DAILY_BASE_REWARD:,} coins mỗi ngày",
            inline=True
        )
        
        embed.add_field(
            name="🔥 Streak bonus",
            value=f"+{config.DAILY_STREAK_BONUS:,} coins/ngày streak\n"
                  f"(Tối đa +{config.DAILY_MAX_STREAK_BONUS:,} coins)",
            inline=True
        )
        
        embed.add_field(
            name="⏰ Thời gian",
            value="Mỗi 20 tiếng có thể nhận 1 lần",
            inline=True
        )
        
        # Streak examples
        example_streaks = [1, 5, 10, 25, 50]
        examples = []
        
        for streak in example_streaks:
            base = config.DAILY_BASE_REWARD
            bonus = min(streak * config.DAILY_STREAK_BONUS, config.DAILY_MAX_STREAK_BONUS)
            total = base + bonus
            examples.append(f"Ngày {streak}: {total:,} coins")
        
        embed.add_field(
            name="📈 Ví dụ phần thưởng",
            value="\n".join(examples),
            inline=False
        )
        
        embed.add_field(
            name="🎲 Bonus may mắn",
            value="• 10% cơ hội gấp đôi phần thưởng (Jackpot!)\n"
                  "• 20% cơ hội thêm 50% phần thưởng (Lucky!)\n"
                  "• 70% phần thưởng bình thường",
            inline=False
        )
        
        embed.add_field(
            name="🏆 Milestone thành tích",
            value="⭐ 5 ngày | ⭐ 10 ngày | ⭐ 25 ngày | ⭐ 50 ngày | ⭐ 100 ngày",
            inline=False
        )
        
        embed.set_footer(text="💡 Tip: Nhận thưởng đều đặn để duy trì streak cao!")
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(DailyCog(bot)) 