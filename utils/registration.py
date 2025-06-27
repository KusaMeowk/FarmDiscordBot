import discord
from discord.ext import commands
from utils.embeds import EmbedBuilder

async def check_user_registered(bot, user_id: int):
    """Check if user is registered (exists in database)"""
    user = await bot.db.get_user(user_id)
    return user is not None

async def require_registration(bot, ctx):
    """
    Decorator function để yêu cầu user phải register trước
    Returns True nếu user đã register, False nếu chưa (và gửi thông báo)
    """
    user = await bot.db.get_user(ctx.author.id)
    
    if not user:
        embed = EmbedBuilder.create_base_embed(
            "🚫 Cần đăng ký tài khoản!",
            f"Bạn cần đăng ký tài khoản trước khi sử dụng lệnh này.",
            color=0xe74c3c
        )
        
        embed.add_field(
            name="🎯 Để bắt đầu",
            value=(
                f"**1.** Sử dụng `f!register` để tạo tài khoản\n"
                f"**2.** Nhận {1000:,} coins và đất khởi điểm\n" 
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
        return False
    
    return True

def registration_required(func):
    """Decorator để yêu cầu user phải register trước khi dùng command"""
    async def wrapper(self, ctx, *args, **kwargs):
        # Check registration using ctx.bot instead of self.bot
        if not await require_registration(ctx.bot, ctx):
            return
        
        # If registered, proceed with original function
        return await func(self, ctx, *args, **kwargs)
    
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper 