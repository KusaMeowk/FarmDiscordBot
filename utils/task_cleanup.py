#!/usr/bin/env python3
"""
Task Cleanup Utility - Safe cleanup cho tasks và loops
"""

import asyncio
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

class TaskCleanupManager:
    """Manager cho việc cleanup tasks an toàn"""
    
    @staticmethod
    def safe_cancel_task(task, task_name: str = "Unknown") -> bool:
        """Cancel task một cách an toàn"""
        try:
            if not task:
                return True
            
            if hasattr(task, 'done') and task.done():
                return True
                
            if hasattr(task, 'cancelled') and task.cancelled():
                return True
            
            # Cancel task
            task.cancel()
            logger.info(f"✅ Task '{task_name}' cancelled successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error cancelling task '{task_name}': {e}")
            return False
    
    @staticmethod
    async def cleanup_pending_tasks(timeout: float = 5.0) -> int:
        """Cleanup tất cả pending tasks"""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            logger.warning("No active event loop found")
            return 0
        
        if not loop or loop.is_closed():
            return 0
        
        try:
            # Get all pending tasks
            pending_tasks = [task for task in asyncio.all_tasks(loop) if not task.done()]
            
            if not pending_tasks:
                return 0
            
            logger.info(f"🧹 Cleaning up {len(pending_tasks)} pending tasks...")
            
            # Cancel all tasks
            for task in pending_tasks:
                if not task.done():
                    task.cancel()
            
            # Wait for tasks to complete with timeout
            try:
                await asyncio.wait_for(
                    asyncio.gather(*pending_tasks, return_exceptions=True), 
                    timeout=timeout
                )
                logger.info("✅ All tasks cleaned up successfully")
            except asyncio.TimeoutError:
                logger.warning(f"⚠️ Some tasks did not cancel within {timeout}s timeout")
            except asyncio.CancelledError:
                logger.info("✅ Task cleanup cancelled (expected during shutdown)")
            except Exception as e:
                logger.warning(f"⚠️ Error during task cleanup: {e}")
            
            return len(pending_tasks)
            
        except Exception as e:
            logger.error(f"Error during task cleanup: {e}")
            return 0
    
    @staticmethod
    def safe_get_loop() -> Optional[asyncio.AbstractEventLoop]:
        """Get event loop một cách an toàn"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                return None
            return loop
        except RuntimeError:
            return None
    
    @staticmethod
    def safe_close_loop(loop: Optional[asyncio.AbstractEventLoop] = None):
        """Close event loop một cách an toàn"""
        if not loop:
            loop = TaskCleanupManager.safe_get_loop()
        
        if not loop:
            return
        
        try:
            if not loop.is_closed():
                loop.close()
                logger.info("🔄 Event loop closed properly")
        except Exception as e:
            logger.error(f"Error closing event loop: {e}")

# Decorators for safe task management
def safe_task_cleanup(task_names: List[str]):
    """Decorator để tự động cleanup tasks trong cog_unload"""
    def decorator(func):
        def wrapper(self):
            # Call original cog_unload
            try:
                func(self)
            except Exception as e:
                logger.error(f"Error in original cog_unload: {e}")
            
            # Safe cleanup
            for task_name in task_names:
                if hasattr(self, task_name):
                    task = getattr(self, task_name)
                    TaskCleanupManager.safe_cancel_task(task, task_name)
        
        return wrapper
    return decorator

# Context manager for safe task execution
class SafeTaskContext:
    """Context manager cho safe task execution"""
    
    def __init__(self, task_name: str):
        self.task_name = task_name
        self.task = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.task:
            TaskCleanupManager.safe_cancel_task(self.task, self.task_name)
    
    def set_task(self, task):
        self.task = task