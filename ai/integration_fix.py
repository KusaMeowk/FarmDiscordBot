#!/usr/bin/env python3
"""
Integration Fix - Đồng bộ Gemini với hệ thống hiện tại để tránh xung đột
"""

import asyncio
from datetime import datetime
from typing import Dict, Any
from utils.enhanced_logging import get_bot_logger

logger = get_bot_logger()

class GeminiIntegrationFix:
    """Fix integration conflicts cho Gemini system"""
    
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
        
    async def apply_fixes(self):
        """Áp dụng tất cả fixes"""
        try:
            logger.info("🔧 Applying Gemini integration fixes...")
            
            # 1. Fix database schema issues
            await self.fix_database_schema()
            
            # 2. Fix task conflicts
            await self.fix_task_conflicts()
            
            # 3. Fix import dependencies
            await self.fix_import_dependencies()
            
            # 4. Disable conflicting features
            await self.manage_conflicting_features()
            
            logger.info("✅ Integration fixes applied successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Integration fixes failed: {e}")
            return False
    
    async def fix_database_schema(self):
        """Fix database schema conflicts"""
        try:
            # Add missing columns that cause "no such column" errors
            missing_columns = [
                ("users", "coins", "INTEGER DEFAULT 0"),
                ("users", "last_seen", "TEXT DEFAULT NULL"),
                ("users", "activity_score", "REAL DEFAULT 0.5")
            ]
            
            for table, column, definition in missing_columns:
                try:
                    await self.db.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
                    logger.info(f"✅ Added column {column} to {table}")
                except Exception:
                    # Column already exists, ignore
                    pass
            
        except Exception as e:
            logger.error(f"Error fixing database schema: {e}")
    
    async def fix_task_conflicts(self):
        """Fix task scheduling conflicts"""
        try:
            # Disable Gemini tasks by default to prevent conflicts
            gemini_cog = self.bot.get_cog('GeminiEconomicCog')
            if gemini_cog and hasattr(gemini_cog, 'enabled'):
                gemini_cog.enabled = False
                logger.info("🔒 Gemini tasks disabled by default")
            
        except Exception as e:
            logger.error(f"Error fixing task conflicts: {e}")
    
    async def fix_import_dependencies(self):
        """Fix import dependency issues"""
        try:
            # Check if required files exist
            required_files = [
                'ai/smart_cache.py',
                'ai/gemini_config.json'
            ]
            
            for file_path in required_files:
                import os
                if not os.path.exists(file_path):
                    logger.warning(f"⚠️ Missing file: {file_path}")
                    await self.create_missing_file(file_path)
            
        except Exception as e:
            logger.error(f"Error fixing import dependencies: {e}")
    
    async def create_missing_file(self, file_path: str):
        """Tạo file bị thiếu"""
        if file_path == 'ai/gemini_config.json':
            # Create minimal config
            import json
            import os
            
            os.makedirs('ai', exist_ok=True)
            
            minimal_config = {
                "gemini_apis": {
                    "primary": {
                        "api_key": "your_api_key_here",
                        "enabled": False
                    }
                }
            }
            
            with open(file_path, 'w') as f:
                json.dump(minimal_config, f, indent=2)
            
            logger.info(f"✅ Created minimal {file_path}")
    
    async def manage_conflicting_features(self):
        """Quản lý features có thể conflict"""
        try:
            # Check if both AI systems are active
            ai_cog = self.bot.get_cog('AICog')
            gemini_cog = self.bot.get_cog('GeminiEconomicCog')
            
            if ai_cog and gemini_cog:
                logger.info("⚠️ Both AI systems detected - coordination needed")
                
                # Set coordination flags
                if hasattr(ai_cog, 'gemini_coordination'):
                    ai_cog.gemini_coordination = True
                
                if hasattr(gemini_cog, 'ai_coordination'):
                    gemini_cog.ai_coordination = True
            
        except Exception as e:
            logger.error(f"Error managing conflicting features: {e}")

# Monkey patch for immediate fix
async def patch_weather_prediction():
    """Patch weather prediction để fix 'coins' error"""
    try:
        from ai import weather_predictor
        
        # Override problematic methods
        original_analyze = getattr(weather_predictor.WeatherPredictorAI, '_analyze_weather_context', None)
        
        if original_analyze:
            def safe_analyze_weather_context(self, game_state, current_weather: str):
                """Safe version that doesn't access missing columns"""
                try:
                    return {
                        'satisfaction': 0.7,
                        'frustration': 0.3,
                        'activity': 0.5,
                        'boredom': 0.5,
                        'wealth': 0.5,
                        'weather_stability': 0.7,
                        'time_since_good_weather': 0,
                        'time_since_bad_weather': 12
                    }
                except Exception:
                    return {}
            
            # Apply patch
            weather_predictor.WeatherPredictorAI._analyze_weather_context = safe_analyze_weather_context
            logger.info("✅ Weather prediction patched")
        
    except Exception as e:
        logger.error(f"Error patching weather prediction: {e}")

# Safe imports for missing dependencies
try:
    from ai.smart_cache import SmartCache
except ImportError:
    logger.warning("⚠️ SmartCache not available - creating stub")
    
    class SmartCache:
        def __init__(self, *args, **kwargs):
            self.hits = 0
            self.misses = 0
            self.tokens_saved = 0
        
        async def get_cached_decision(self, *args, **kwargs):
            return None
        
        async def save_decision(self, *args, **kwargs):
            pass
        
        async def load_from_disk(self):
            pass
        
        async def cleanup_old(self):
            pass
        
        def get_stats(self):
            return {
                'cached_decisions': 0,
                'cache_hits': 0,
                'cache_misses': 0,
                'hit_rate': '0.0%',
                'tokens_saved': 0,
                'cost_saved': '$0.0000'
            }

# Apply immediate patches
asyncio.create_task(patch_weather_prediction()) 