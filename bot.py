import discord
from discord.ext import commands
import asyncio
import sys
import signal
import config
from database.database import Database
from utils.enhanced_logging import setup_enhanced_logging, log_error, get_bot_logger
from utils.task_cleanup import TaskCleanupManager
from utils.signal_handler import run_bot_with_graceful_shutdown
from utils.discord_cleanup import DiscordCleanupManager

# Setup enhanced logging với Unicode safety
setup_enhanced_logging()
logger = get_bot_logger()

class FarmBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        
        super().__init__(
            command_prefix=config.PREFIX,
            intents=intents,
            description="🌾 Bot Game Nông Trại Discord"
        )
        
        self.db = None
        
    async def setup_hook(self):
        """Setup bot when starting"""
        logger.info("🔧 Initializing bot systems...")
        
        try:
            # Initialize database
            self.db = Database(config.DATABASE_PATH)
            await self.db.init_db()
            logger.info("✅ Database connected successfully")
            
            # Apply integration fixes for Gemini
            from ai.integration_fix import GeminiIntegrationFix
            integration_fix = GeminiIntegrationFix(self)
            await integration_fix.apply_fixes()
            
            # Initialize Game Master instance
            await self._initialize_game_master()
            
        except Exception as e:
            log_error(logger, "❌ Database initialization failed", e)
            return
        
        # Load all cogs
        extensions = [
            'features.help_system',  # Must load first to replace default help
            'features.shortcuts',    # Load shortcuts system
            'features.profile',
            'features.maid_system_v2', # Maid Gacha System V2 - AUTO LOAD ENABLED
            'features.maid_info_system', # Maid Info System - Avatar Support & Database Search
            'features.maid_trading', # Maid Trading System - Trade maids between users
            'features.limited_banner_system', # Limited Banner System for special events
            'features.farm', 
            'features.shop',
            'features.daily',
            'features.weather',
            'features.events',
            'features.leaderboard',
            'features.market',     # Unified Market System
            'features.casino_v2',  # Casino V2 - LOGIC MỚI HOÀN TOÀN (casino cũ đã xóa)
            'features.transfer',   # Transfer System - Chuyển tiền giữa người dùng
            # 'features.ai_manager',  # AI Engine - DISABLED (Gemini takes control)
            'features.gemini_economic_cog',
            'features.gemini_game_master_cog',
            'features.admin_cog',
            'features.state_admin', # State Management Admin Commands
            'features.pond',       # Pond System - Fish farming
            'features.barn',       # Barn System - Animal farming
            'features.livestock',  # Livestock Overview System
        ]
        
        loaded_count = 0
        failed_extensions = []
        
        for extension in extensions:
            try:
                await self.load_extension(extension)
                loaded_count += 1
                logger.info(f"✅ Loaded extension: {extension}")
            except Exception as e:
                # Special handling for admin_cog - known intermittent issue
                if extension == 'features.admin_cog':
                    logger.warning(f"⚠️ Admin cog failed to load (intermittent issue): {e}")
                    failed_extensions.append(extension)
                else:
                    log_error(logger, f"❌ Failed to load extension {extension}", e)
                    failed_extensions.append(extension)
        
        # Try to retry admin_cog once if it failed
        if 'features.admin_cog' in failed_extensions:
            try:
                import asyncio
                await asyncio.sleep(1)  # Brief delay before retry
                await self.load_extension('features.admin_cog')
                loaded_count += 1
                failed_extensions.remove('features.admin_cog')
                logger.info("✅ Admin cog loaded successfully on retry")
            except Exception as e:
                logger.warning(f"⚠️ Admin cog retry failed - proceeding without admin commands: {e}")
        
        logger.info(f"🎯 Successfully loaded {loaded_count}/{len(extensions)} extensions")
        
        # Report failed extensions if any
        if failed_extensions:
            logger.warning(f"⚠️ Failed extensions: {', '.join(failed_extensions)}")
            if len(failed_extensions) == 1 and 'features.admin_cog' in failed_extensions:
                logger.info("ℹ️ Admin cog failure is a known intermittent issue and doesn't affect core functionality")
        
        # Initialize maid helper
        await self._initialize_maid_helper()
        
        # Initialize cog state managers
        await self._initialize_cog_states()
    
    async def _initialize_game_master(self):
        """Initialize Gemini Game Master instance"""
        try:
            from ai.gemini_game_master import GeminiGameMaster
            self.game_master = GeminiGameMaster(self.db)
            await self.game_master.initialize()
            logger.info("🎮 Game Master instance initialized")
        except Exception as e:
            log_error(logger, "❌ Error initializing Game Master", e)
    
    async def _initialize_maid_helper(self):
        """Initialize maid helper for buff integration"""
        try:
            from features.maid_helper_v2 import init_maid_helper
            maid_helper = init_maid_helper(self)
            logger.info("✅ Maid helper initialized")
        except Exception as e:
            log_error(logger, "❌ Error initializing maid helper", e)
    
    async def _initialize_cog_states(self):
        """Initialize state managers for cogs that need persistence"""
        try:
            # Initialize WeatherCog state
            weather_cog = self.get_cog('WeatherCog')
            if weather_cog and hasattr(weather_cog, 'setup_hook'):
                await weather_cog.setup_hook()
                logger.info("✅ WeatherCog state initialized")
            
            # Initialize EventsCog state
            events_cog = self.get_cog('EventsCog')
            if events_cog and hasattr(events_cog, 'setup_hook'):
                await events_cog.setup_hook()
                logger.info("✅ EventsCog state initialized")
            
            # Save system startup time
            from utils.state_manager import StateManager
            state_manager = StateManager(self.db)
            await state_manager.save_system_startup_time()
            logger.info("✅ System startup time recorded")
            
        except Exception as e:
            log_error(logger, "❌ Error initializing cog states", e)
    
    async def on_ready(self):
        """Called when bot is ready"""
        logger.info(f"🤖 {self.user} ready for farming!")
        logger.info(f"🌐 Connected to {len(self.guilds)} servers")
        
        # 🎀 Để Latina AI gửi thông báo đầu tiên (2 giây)
        # 🌅 Sau đó gửi thông báo Farm Bot (6 giây)
        asyncio.create_task(self._send_farm_bot_notification_later())
        
        # Set bot status
        activity = discord.Game(name=f"{config.PREFIX}help | 🌾 Nông trại")
        await self.change_presence(activity=activity)
        logger.info("🎮 Bot status updated")
    
    async def _send_farm_bot_notification_later(self):
        """Gửi thông báo Farm Bot sau khi Latina đã gửi - DISABLED"""
        # DISABLED: Loại bỏ thông báo "🌅 Farm Bot đã sẵn sàng!" theo yêu cầu người dùng
        logger.info("🔇 Farm Bot startup notification disabled")
        return
    
    async def _find_best_notification_channel(self, guild):
        """Tìm channel tốt nhất để gửi thông báo"""
        # Danh sách ưu tiên channel names
        priority_names = ['general', 'announce', 'announcements', 'bot', 'notification', 'notifications', 'farm', 'farming']
        
        # Tìm channel theo priority
        for priority_name in priority_names:
            for channel in guild.text_channels:
                if (priority_name in channel.name.lower() and 
                    channel.permissions_for(guild.me).send_messages):
                    return channel
        
        # Nếu không tìm thấy, dùng channel đầu tiên có permission
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                return channel
        
        return None
    
    def _get_current_time(self):
        """Lấy thời gian hiện tại định dạng đẹp"""
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S %d/%m/%Y")
    
    async def on_command_error(self, ctx, error):
        """Handle command errors cleanly"""
        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Thiếu tham số. Sử dụng `{config.PREFIX}help` để xem hướng dẫn.")
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"⏰ Lệnh đang cooldown. Thử lại sau {error.retry_after:.1f}s.")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ Bạn không có quyền sử dụng lệnh này.")
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("❌ Bot không có quyền thực hiện hành động này.")
        else:
            # Log error with full traceback for debugging
            import traceback
            error_msg = f"Command error in {ctx.command.name if ctx.command else 'unknown'}"
            logger.error(f"{error_msg}: {error}")
            logger.error(f"Full traceback:\n{''.join(traceback.format_exception(type(error), error, error.__traceback__))}")
            await ctx.send("❌ Có lỗi xảy ra. Vui lòng thử lại.")

    async def on_error(self, event, *args, **kwargs):
        """Handle general bot errors"""
        exc_type, exc_value, exc_traceback = sys.exc_info()
        log_error(logger, f"Bot error in event '{event}'", exc_value)

async def shutdown_handler(bot):
    """Handle graceful shutdown"""
    logger.info("🛑 Shutting down bot gracefully...")
    
    # Cleanup cogs first
    try:
        logger.info("🧹 Cleaning up cogs...")
        
        # Get all cogs and unload them properly
        cog_names = list(bot.cogs.keys())
        for cog_name in cog_names:
            try:
                cog = bot.get_cog(cog_name)
                if cog and hasattr(cog, 'cog_unload'):
                    cog.cog_unload()
                
                # Try to unload extension safely
                extension_name = None
                if cog_name.lower().endswith('cog'):
                    extension_name = f'features.{cog_name.lower()[:-3]}'
                else:
                    extension_name = f'features.{cog_name.lower()}'
                
                try:
                    await bot.unload_extension(extension_name)
                    logger.info(f"✅ Unloaded cog: {cog_name}")
                except Exception:
                    # Extension might not be loaded or already unloaded
                    logger.info(f"✅ Cleaned up cog: {cog_name}")
                    
            except Exception as e:
                logger.warning(f"⚠️ Error unloading cog {cog_name}: {e}")
        
        # Cancel all remaining tasks using safe cleanup
        cleaned_tasks = await TaskCleanupManager.cleanup_pending_tasks(timeout=3.0)
        
    except Exception as e:
        log_error(logger, "⚠️ Error during cog cleanup", e)
    
    # Use Discord cleanup manager for safe bot closure
    try:
        await DiscordCleanupManager.graceful_discord_shutdown(bot, timeout=8.0)
    except Exception as e:
        log_error(logger, "⚠️ Error during Discord shutdown", e)
    
    try:
        # Close database connection
        if bot.db:
            await bot.db.close()
            logger.info("🗄️  Database connection closed")
    except Exception as e:
        log_error(logger, "⚠️  Error closing database", e)
    
    logger.info("👋 Bot shutdown complete")

async def main():
    """Main function with graceful shutdown"""
    logger.info("🚀 Starting Discord Farming Bot...")
    
    bot = None
    try:
        # Create bot instance
        bot = FarmBot()
        
        # Define bot runner
        async def run_bot_instance():
            logger.info("🔐 Logging in to Discord...")
            await bot.start(config.DISCORD_TOKEN)
        
        # Use graceful shutdown handler
        await run_bot_with_graceful_shutdown(run_bot_instance(), timeout=8.0)
        
    except Exception as e:
        log_error(logger, "💥 Critical bot error", e)
    finally:
        # Ensure cleanup if bot was created
        if bot:
            try:
                logger.info("🧹 Final cleanup...")
                await shutdown_handler(bot)
            except Exception as e:
                log_error(logger, "Error in final cleanup", e)
        
        logger.info("👋 Bot main function completed")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"💥 Fatal error: {e}")
        sys.exit(1) 