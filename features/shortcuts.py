import discord
from discord.ext import commands

class ShortcutsCog(commands.Cog):
    """Hệ thống lệnh viết tắt cho tất cả commands"""
    
    def __init__(self, bot):
        self.bot = bot
    
    # Profile shortcuts
    @commands.command(name='p', aliases=['pro'], hidden=True)
    async def profile_shortcut(self, ctx, member: discord.Member = None):
        """Shortcut cho f!profile"""
        profile_cmd = self.bot.get_command('profile')
        if profile_cmd:
            await ctx.invoke(profile_cmd, member=member)
    
    @commands.command(name='i', hidden=True) 
    async def inventory_shortcut(self, ctx):
        """Shortcut cho f!inventory"""
        inventory_cmd = self.bot.get_command('inventory')
        if inventory_cmd:
            await ctx.invoke(inventory_cmd)
    
    @commands.command(name='r', hidden=True)
    async def register_shortcut(self, ctx):
        """Shortcut cho f!register"""
        register_cmd = self.bot.get_command('register')
        if register_cmd:
            await ctx.invoke(register_cmd)
    
    @commands.command(name='ren', hidden=True)
    async def rename_shortcut(self, ctx, *, new_name):
        """Shortcut cho f!rename"""
        rename_cmd = self.bot.get_command('rename')
        if rename_cmd:
            await ctx.invoke(rename_cmd, new_name=new_name)
    
    # Farm shortcuts
    @commands.command(name='f', hidden=True)
    async def farm_shortcut(self, ctx, page = 1):
        """Shortcut cho f!farm"""
        farm_cmd = self.bot.get_command('farm')
        if farm_cmd:
            await ctx.invoke(farm_cmd, page=page)
    
    @commands.command(name='pl', hidden=True)
    async def plant_shortcut(self, ctx, *args):
        """Shortcut cho f!plant"""
        plant_cmd = self.bot.get_command('plant')
        if plant_cmd:
            # Forward all arguments to main plant command
            await ctx.invoke(plant_cmd, *args)
    
    @commands.command(name='h', hidden=True)
    async def harvest_shortcut(self, ctx, target=None):
        """Shortcut cho f!harvest"""
        harvest_cmd = self.bot.get_command('harvest')
        if harvest_cmd:
            await ctx.invoke(harvest_cmd, target=target)
    
    @commands.command(name='s', hidden=True)
    async def sell_shortcut(self, ctx, crop_type = None, quantity=None):
        """Shortcut cho f!sell"""
        sell_cmd = self.bot.get_command('sell')
        if sell_cmd:
            await ctx.invoke(sell_cmd, crop_type=crop_type, quantity=quantity)
    
    # Shop shortcuts  
    @commands.command(name='sh', hidden=True)
    async def shop_shortcut(self, ctx):
        """Shortcut cho f!shop"""
        shop_cmd = self.bot.get_command('shop')
        if shop_cmd:
            await ctx.invoke(shop_cmd)
    
    @commands.command(name='b', hidden=True)
    async def buy_shortcut(self, ctx, item_type = None, quantity = 1):
        """Shortcut cho f!buy"""
        buy_cmd = self.bot.get_command('buy')
        if buy_cmd:
            await ctx.invoke(buy_cmd, item_type=item_type, quantity=quantity)
    
    @commands.command(name='pr', hidden=True)
    async def price_shortcut(self, ctx, crop_type = None):
        """Shortcut cho f!price"""
        price_cmd = self.bot.get_command('price')
        if price_cmd:
            await ctx.invoke(price_cmd, crop_type=crop_type)
    
    # Market shortcuts
    @commands.command(name='m', hidden=True)
    async def market_shortcut(self, ctx):
        """Shortcut cho f!market"""
        market_cmd = self.bot.get_command('market')
        if market_cmd:
            await ctx.invoke(market_cmd)
    
    @commands.command(name='tr', hidden=True)
    async def trends_shortcut(self, ctx):
        """Shortcut cho f!trends"""
        trends_cmd = self.bot.get_command('trends')
        if trends_cmd:
            await ctx.invoke(trends_cmd)
    
    @commands.command(name='fm', hidden=True)
    async def farmmarket_shortcut(self, ctx):
        """Shortcut cho f!farmmarket"""
        farmmarket_cmd = self.bot.get_command('farmmarket')
        if farmmarket_cmd:
            await ctx.invoke(farmmarket_cmd)
    
    # Weather shortcuts
    @commands.command(name='w', hidden=True)
    async def weather_shortcut(self, ctx):
        """Shortcut cho f!weather"""
        weather_cmd = self.bot.get_command('weather')
        if weather_cmd:
            await ctx.invoke(weather_cmd)
    
    @commands.command(name='fo', hidden=True)
    async def forecast_shortcut(self, ctx):
        """Shortcut cho f!forecast"""
        forecast_cmd = self.bot.get_command('forecast')
        if forecast_cmd:
            await ctx.invoke(forecast_cmd)
    
    @commands.command(name='aw', hidden=True)
    async def aiweather_shortcut(self, ctx):
        """Shortcut cho f!aiweather"""
        aiweather_cmd = self.bot.get_command('aiweather')
        if aiweather_cmd:
            await ctx.invoke(aiweather_cmd)
    
    # Daily shortcuts
    @commands.command(name='d', hidden=True)
    async def daily_shortcut(self, ctx):
        """Shortcut cho f!daily"""
        daily_cmd = self.bot.get_command('daily')
        if daily_cmd:
            await ctx.invoke(daily_cmd)
    
    @commands.command(name='st', hidden=True)
    async def streak_shortcut(self, ctx):
        """Shortcut cho f!streak"""
        streak_cmd = self.bot.get_command('streak')
        if streak_cmd:
            await ctx.invoke(streak_cmd)
    
    @commands.command(name='rw', hidden=True)
    async def rewards_shortcut(self, ctx):
        """Shortcut cho f!rewards"""
        rewards_cmd = self.bot.get_command('rewards')
        if rewards_cmd:
            await ctx.invoke(rewards_cmd)
    
    # Events shortcuts
    @commands.command(name='e', hidden=True)
    async def event_shortcut(self, ctx):
        """Shortcut cho f!event"""
        event_cmd = self.bot.get_command('event')
        if event_cmd:
            await ctx.invoke(event_cmd)
    
    @commands.command(name='ev', hidden=True)
    async def events_shortcut(self, ctx):
        """Shortcut cho f!events"""
        events_cmd = self.bot.get_command('events')
        if events_cmd:
            await ctx.invoke(events_cmd)
    
    @commands.command(name='c', hidden=True)
    async def claim_event_shortcut(self, ctx):
        """Shortcut cho f!claim_event"""
        claim_cmd = self.bot.get_command('claim_event')
        if claim_cmd:
            await ctx.invoke(claim_cmd)
    
    # Leaderboard shortcuts
    @commands.command(name='l', hidden=True)
    async def leaderboard_shortcut(self, ctx, board_type = "money"):
        """Shortcut cho f!leaderboard"""
        leaderboard_cmd = self.bot.get_command('leaderboard')
        if leaderboard_cmd:
            await ctx.invoke(leaderboard_cmd, board_type=board_type)
    
    @commands.command(name='ra', hidden=True)
    async def rank_shortcut(self, ctx, member: discord.Member = None):
        """Shortcut cho f!rank"""
        rank_cmd = self.bot.get_command('rank')
        if rank_cmd:
            await ctx.invoke(rank_cmd, member=member)
    
    @commands.command(name='co', hidden=True)
    async def compare_shortcut(self, ctx, member: discord.Member):
        """Shortcut cho f!compare"""
        compare_cmd = self.bot.get_command('compare')
        if compare_cmd:
            await ctx.invoke(compare_cmd, member=member)
    
    # AI shortcuts
    @commands.command(name='a', hidden=True)
    async def ai_shortcut(self, ctx):
        """Shortcut cho f!ai"""
        ai_cmd = self.bot.get_command('ai')
        if ai_cmd:
            await ctx.invoke(ai_cmd)
    
    # 🎰 Casino shortcuts
    @commands.command(name='bjack', hidden=True)
    async def blackjack_shortcut(self, ctx, bet_amount: int = None):
        """🎰 Shortcut cho blackjack"""
        blackjack_cmd = self.bot.get_command('blackjack')
        if blackjack_cmd:
            await ctx.invoke(blackjack_cmd, bet_amount=bet_amount)
    
    @commands.command(name='casino', hidden=True)
    async def casino_shortcut(self, ctx):
        """🎰 Shortcut cho casino info"""
        blackjack_cmd = self.bot.get_command('blackjack')
        if blackjack_cmd:
            await ctx.invoke(blackjack_cmd)  # Show casino info

async def setup(bot):
    await bot.add_cog(ShortcutsCog(bot)) 