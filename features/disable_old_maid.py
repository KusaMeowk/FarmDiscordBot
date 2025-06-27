import discord
from discord.ext import commands
from discord import app_commands
from utils.enhanced_logging import get_bot_logger

logger = get_bot_logger()

class DisableOldMaidCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="disable_old_maid")
    @commands.is_owner()
    async def disable_old_maid(self, ctx):
        """Disable old maid system"""
        try:
            # Unload old maid extension
            await self.bot.unload_extension('features.maid')
            
            embed = discord.Embed(
                title="✅ Disabled Old Maid System",
                description="Old maid system has been disabled. Use new V2 commands:\n\n"
                           "🎰 `f!mg` - Gacha 1 maid\n"
                           "🎰 `f!mg10` - Gacha 10 maids\n"
                           "👑 `f!ma` - Xem maid active\n"
                           "📚 `f!mc` - Xem collection\n"
                           "🎯 `f!me <id>` - Trang bị maid\n"
                           "⭐ `f!mstar` - Xem stardust\n"
                           "💥 `f!mdis <id>` - Tách maid\n"
                           "🎲 `f!mreroll <id>` - Reroll buffs",
                color=0x00FF00
            )
            await ctx.send(embed=embed)
            logger.info("Old maid system disabled successfully")
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"Failed to disable old maid system: {str(e)}",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            logger.error(f"Error disabling old maid: {e}")
    
    @commands.command(name="enable_old_maid")
    @commands.is_owner()
    async def enable_old_maid(self, ctx):
        """Re-enable old maid system"""
        try:
            # Load old maid extension
            await self.bot.load_extension('features.maid')
            
            embed = discord.Embed(
                title="✅ Enabled Old Maid System",
                description="Old maid system has been re-enabled.",
                color=0x00FF00
            )
            await ctx.send(embed=embed)
            logger.info("Old maid system re-enabled successfully")
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"Failed to enable old maid system: {str(e)}",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            logger.error(f"Error enabling old maid: {e}")
    
    @commands.command(name="maid_status")
    @commands.is_owner()
    async def maid_status(self, ctx):
        """Check maid system status"""
        old_maid_loaded = 'MaidSystem' in [cog.__class__.__name__ for cog in self.bot.cogs.values()]
        new_maid_loaded = 'MaidSystemV2' in [cog.__class__.__name__ for cog in self.bot.cogs.values()]
        
        embed = discord.Embed(
            title="🔍 Maid System Status",
            color=0x0099FF
        )
        
        embed.add_field(
            name="Old Maid System",
            value="✅ Loaded" if old_maid_loaded else "❌ Not loaded",
            inline=True
        )
        
        embed.add_field(
            name="New Maid System V2",
            value="✅ Loaded" if new_maid_loaded else "❌ Not loaded",
            inline=True
        )
        
        if old_maid_loaded and new_maid_loaded:
            embed.add_field(
                name="⚠️ Warning",
                value="Both systems are loaded! This may cause conflicts.",
                inline=False
            )
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(DisableOldMaidCog(bot)) 