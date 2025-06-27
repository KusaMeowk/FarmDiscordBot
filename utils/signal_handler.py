#!/usr/bin/env python3
"""
Signal Handler Utility - Safe signal handling cho bot shutdown
"""

import asyncio
import signal
import logging
from typing import Callable, Optional

logger = logging.getLogger(__name__)

class SafeSignalHandler:
    """Safe signal handler với proper cleanup"""
    
    def __init__(self):
        self.shutdown_event = asyncio.Event()
        self.original_handlers = {}
        
    def setup_signal_handlers(self, custom_handler: Optional[Callable] = None):
        """Setup signal handlers safely"""
        def signal_handler(signum, frame):
            logger.info(f"🛑 Received signal {signum}, initiating shutdown...")
            
            # Set shutdown event
            self.shutdown_event.set()
            
            # Call custom handler if provided
            if custom_handler:
                try:
                    custom_handler(signum, frame)
                except Exception as e:
                    logger.error(f"Error in custom signal handler: {e}")
        
        # Register signal handlers (Windows and Unix)
        signals_to_handle = [signal.SIGINT, signal.SIGTERM]
        
        # Add Windows-specific signal
        if hasattr(signal, 'SIGBREAK'):
            signals_to_handle.append(signal.SIGBREAK)
        
        for sig in signals_to_handle:
            try:
                # Store original handler
                self.original_handlers[sig] = signal.signal(sig, signal_handler)
                logger.info(f"✅ Registered handler for signal {sig}")
            except (OSError, ValueError) as e:
                logger.warning(f"⚠️ Could not register handler for signal {sig}: {e}")
    
    def restore_signal_handlers(self):
        """Restore original signal handlers"""
        for sig, original_handler in self.original_handlers.items():
            try:
                signal.signal(sig, original_handler)
                logger.info(f"✅ Restored original handler for signal {sig}")
            except Exception as e:
                logger.warning(f"⚠️ Could not restore handler for signal {sig}: {e}")
        
        self.original_handlers.clear()
    
    async def wait_for_shutdown(self):
        """Wait for shutdown signal"""
        await self.shutdown_event.wait()
    
    def is_shutdown_requested(self) -> bool:
        """Check if shutdown was requested"""
        return self.shutdown_event.is_set()

class GracefulShutdown:
    """Context manager cho graceful shutdown"""
    
    def __init__(self, timeout: float = 10.0):
        self.timeout = timeout
        self.signal_handler = SafeSignalHandler()
        
    async def __aenter__(self):
        self.signal_handler.setup_signal_handlers()
        return self.signal_handler
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        logger.info("🧹 Graceful shutdown context exiting...")
        
        # Restore signal handlers
        self.signal_handler.restore_signal_handlers()
        
        # Cancel all pending tasks with timeout
        try:
            loop = asyncio.get_event_loop()
            if loop and not loop.is_closed():
                pending_tasks = [task for task in asyncio.all_tasks(loop) if not task.done()]
                
                if pending_tasks:
                    logger.info(f"🧹 Cleaning up {len(pending_tasks)} pending tasks...")
                    
                    # Cancel tasks
                    for task in pending_tasks:
                        if not task.done():
                            task.cancel()
                    
                    # Wait with timeout
                    try:
                        await asyncio.wait_for(
                            asyncio.gather(*pending_tasks, return_exceptions=True),
                            timeout=self.timeout
                        )
                        logger.info("✅ All tasks cleaned up")
                    except asyncio.TimeoutError:
                        logger.warning(f"⚠️ Some tasks did not cancel within {self.timeout}s")
                    except asyncio.CancelledError:
                        logger.info("✅ Cleanup cancelled (expected)")
                        
        except Exception as e:
            logger.error(f"Error during graceful shutdown: {e}")

# Example usage for bot
async def run_bot_with_graceful_shutdown(bot_coro, timeout: float = 10.0):
    """Run bot với graceful shutdown handling"""
    logger.info("🚀 Starting bot with graceful shutdown handler...")
    
    # Setup signal handler
    shutdown_event = asyncio.Event()
    
    def signal_handler(signum, frame):
        logger.info(f"🛑 Received signal {signum} (Ctrl+C), initiating graceful shutdown...")
        shutdown_event.set()
    
    # Register signal handlers
    import signal
    original_sigint = signal.signal(signal.SIGINT, signal_handler)
    original_sigterm = signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Start bot task
        bot_task = asyncio.create_task(bot_coro)
        shutdown_task = asyncio.create_task(shutdown_event.wait())
        
        logger.info("✅ Bot task started, waiting for completion or shutdown signal...")
        
        # Wait for either bot completion or shutdown signal
        done, pending = await asyncio.wait(
            [bot_task, shutdown_task],
            return_when=asyncio.FIRST_COMPLETED
        )
        
        # Handle shutdown
        if shutdown_task in done:
            logger.info("🛑 Shutdown signal received, stopping bot...")
            
            # Cancel bot task gracefully
            if not bot_task.done():
                bot_task.cancel()
                try:
                    await asyncio.wait_for(bot_task, timeout=timeout)
                except asyncio.TimeoutError:
                    logger.warning(f"⚠️ Bot task did not stop within {timeout}s")
                except asyncio.CancelledError:
                    logger.info("✅ Bot task cancelled successfully")
                except Exception as e:
                    logger.error(f"Error during bot cancellation: {e}")
        
        # Clean up pending tasks
        for task in pending:
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        # Wait a moment for Discord gateway threads to cleanup
        await asyncio.sleep(0.5)
        
        # Cancel any remaining tasks
        try:
            loop = asyncio.get_event_loop()
            if loop and not loop.is_closed():
                remaining_tasks = [task for task in asyncio.all_tasks(loop) 
                                 if not task.done() and task != asyncio.current_task()]
                
                if remaining_tasks:
                    logger.info(f"🧹 Cleaning up {len(remaining_tasks)} remaining tasks...")
                    for task in remaining_tasks:
                        task.cancel()
                    
                    try:
                        await asyncio.wait_for(
                            asyncio.gather(*remaining_tasks, return_exceptions=True),
                            timeout=2.0
                        )
                    except asyncio.TimeoutError:
                        logger.warning("⚠️ Some tasks did not cancel in time")
                    except Exception:
                        pass  # Expected during shutdown
        except Exception as e:
            logger.warning(f"⚠️ Error during final cleanup: {e}")
        
        logger.info("✅ Graceful shutdown completed")
        
    except KeyboardInterrupt:
        logger.info("🛑 KeyboardInterrupt caught, shutting down...")
    except Exception as e:
        logger.error(f"💥 Error during bot execution: {e}")
        raise
    finally:
        # Restore original signal handlers
        try:
            signal.signal(signal.SIGINT, original_sigint)
            signal.signal(signal.SIGTERM, original_sigterm)
            logger.info("✅ Signal handlers restored")
        except Exception as e:
            logger.warning(f"⚠️ Error restoring signal handlers: {e}")
        
        # Final cleanup message
        logger.info("👋 Bot shutdown handler completed") 