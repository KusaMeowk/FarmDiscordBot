#!/usr/bin/env python3
"""
Discord Cleanup Utility - Xử lý cleanup Discord gateway threads
"""

import asyncio
import logging
import threading
import time
from typing import Optional

logger = logging.getLogger(__name__)

class DiscordCleanupManager:
    """Manager để cleanup Discord gateway threads an toàn"""
    
    @staticmethod
    def force_cleanup_discord_threads(timeout: float = 3.0):
        """Force cleanup Discord gateway threads"""
        try:
            # Get all active threads
            active_threads = threading.enumerate()
            discord_threads = [
                thread for thread in active_threads 
                if thread.name and ('gateway' in thread.name.lower() or 
                                  'discord' in thread.name.lower() or
                                  'websocket' in thread.name.lower())
            ]
            
            if not discord_threads:
                logger.info("✅ No Discord threads to cleanup")
                return
            
            logger.info(f"🧹 Found {len(discord_threads)} Discord threads to cleanup")
            
            # Wait for threads to finish naturally first
            start_time = time.time()
            while discord_threads and (time.time() - start_time) < timeout:
                discord_threads = [t for t in discord_threads if t.is_alive()]
                if discord_threads:
                    time.sleep(0.1)
                else:
                    break
            
            # Check remaining threads
            remaining_threads = [t for t in discord_threads if t.is_alive()]
            
            if remaining_threads:
                logger.warning(f"⚠️ {len(remaining_threads)} Discord threads still active after {timeout}s")
                for thread in remaining_threads:
                    logger.warning(f"  - Thread: {thread.name} (daemon: {thread.daemon})")
            else:
                logger.info("✅ All Discord threads cleaned up successfully")
                
        except Exception as e:
            logger.error(f"Error during Discord thread cleanup: {e}")
    
    @staticmethod
    async def safe_bot_close(bot, timeout: float = 5.0):
        """Safely close bot connection với proper error handling"""
        try:
            if bot.is_closed():
                logger.info("✅ Bot already closed")
                return
            
            logger.info("🔌 Closing bot connection...")
            
            # Create close task with timeout
            close_task = asyncio.create_task(bot.close())
            
            try:
                await asyncio.wait_for(close_task, timeout=timeout)
                logger.info("✅ Bot connection closed successfully")
            except asyncio.TimeoutError:
                logger.warning(f"⚠️ Bot close timeout after {timeout}s, cancelling...")
                close_task.cancel()
                try:
                    await close_task
                except asyncio.CancelledError:
                    logger.info("✅ Bot close task cancelled")
                except Exception as e:
                    logger.warning(f"Error during bot close cancellation: {e}")
            
            # Wait a moment for Discord gateway to cleanup
            await asyncio.sleep(0.5)
            
        except Exception as e:
            logger.error(f"Error during safe bot close: {e}")
    
    @staticmethod
    def suppress_discord_errors():
        """Suppress common Discord errors during shutdown"""
        import warnings
        
        # Suppress specific warnings
        warnings.filterwarnings("ignore", message=".*Event loop is closed.*")
        warnings.filterwarnings("ignore", message=".*coroutine.*was never awaited.*")
        warnings.filterwarnings("ignore", message=".*Task was destroyed.*")
        
        # Override logging for specific Discord modules during shutdown
        discord_loggers = [
            'discord.gateway',
            'discord.client', 
            'discord.http',
            'websockets'
        ]
        
        for logger_name in discord_loggers:
            discord_logger = logging.getLogger(logger_name)
            # Set to ERROR level to suppress INFO/WARNING during shutdown
            discord_logger.setLevel(logging.ERROR)
    
    @staticmethod
    async def graceful_discord_shutdown(bot, timeout: float = 8.0):
        """Complete graceful Discord bot shutdown"""
        logger.info("🛑 Starting graceful Discord shutdown...")
        
        try:
            # Step 1: Suppress Discord errors
            DiscordCleanupManager.suppress_discord_errors()
            
            # Step 2: Close bot connection safely
            await DiscordCleanupManager.safe_bot_close(bot, timeout=timeout/2)
            
            # Step 3: Wait for gateway threads
            await asyncio.sleep(1.0)
            
            # Step 4: Force cleanup Discord threads
            DiscordCleanupManager.force_cleanup_discord_threads(timeout=timeout/2)
            
            logger.info("✅ Graceful Discord shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during graceful Discord shutdown: {e}")

# Context manager for Discord cleanup
class DiscordShutdownContext:
    """Context manager cho Discord shutdown"""
    
    def __init__(self, bot, timeout: float = 8.0):
        self.bot = bot
        self.timeout = timeout
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await DiscordCleanupManager.graceful_discord_shutdown(self.bot, self.timeout)

# Decorator for bot shutdown
def with_discord_cleanup(timeout: float = 8.0):
    """Decorator để tự động cleanup Discord khi function kết thúc"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            bot = None
            
            # Try to find bot in args
            for arg in args:
                if hasattr(arg, 'close') and hasattr(arg, 'is_closed'):
                    bot = arg
                    break
            
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                if bot:
                    await DiscordCleanupManager.graceful_discord_shutdown(bot, timeout)
        
        return wrapper
    return decorator 