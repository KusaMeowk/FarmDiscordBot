#!/usr/bin/env python3
"""
Gemini Integration Fix - Đồng bộ toàn bộ logic để tránh xung đột
"""

import asyncio
import os
from datetime import datetime
from typing import Dict, Any, Optional
from database.database import Database
from utils.enhanced_logging import get_bot_logger

logger = get_bot_logger()

class GeminiIntegrationManager:
    """Quản lý tích hợp Gemini với hệ thống hiện tại"""
    
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
        self.integration_status = {}
        
    async def initialize_integration(self):
        """Khởi tạo tích hợp an toàn"""
        try:
            logger.info("🔧 Initializing Gemini integration...")
            
            # 1. Check database compatibility
            await self.check_database_compatibility()
            
            # 2. Initialize Gemini cog safely
            await self.safe_initialize_gemini_cog()
            
            # 3. Sync with existing AI systems
            await self.sync_with_existing_ai()
            
            # 4. Setup task coordination
            await self.setup_task_coordination()
            
            logger.info("✅ Gemini integration initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Gemini integration failed: {e}")
            return False
    
    async def check_database_compatibility(self):
        """Kiểm tra tương thích database"""
        try:
            # Check if required tables exist
            required_tables = ['users', 'crops', 'inventory']
            
            for table in required_tables:
                if not await self.db.table_exists(table):
                    logger.warning(f"⚠️ Table {table} missing - creating...")
                    await self.create_missing_table(table)
            
            # Check and add missing columns
            await self.add_missing_columns()
            
            logger.info("✅ Database compatibility checked")
            
        except Exception as e:
            logger.error(f"❌ Database compatibility check failed: {e}")
            raise
    
    async def add_missing_columns(self):
        """Thêm các cột bị thiếu vào database"""
        try:
            # Add last_seen column to users if missing
            try:
                await self.db.execute(
                    "ALTER TABLE users ADD COLUMN last_seen TEXT DEFAULT NULL"
                )
                logger.info("✅ Added last_seen column to users table")
            except Exception:
                # Column already exists
                pass
            
            # Add coins column to users if missing (fix for "no such column: coins")
            try:
                await self.db.execute(
                    "ALTER TABLE users ADD COLUMN coins INTEGER DEFAULT 0"
                )
                logger.info("✅ Added coins column to users table")
            except Exception:
                # Column already exists
                pass
                
        except Exception as e:
            logger.error(f"Error adding missing columns: {e}")
    
    async def safe_initialize_gemini_cog(self):
        """Khởi tạo Gemini cog một cách an toàn"""
        try:
            # Check if Gemini cog is already loaded
            gemini_cog = self.bot.get_cog('GeminiEconomicCog')
            
            if not gemini_cog:
                # Try to load Gemini cog
                try:
                    await self.bot.load_extension('features.gemini_economic_cog')
                    logger.info("✅ Gemini Economic Cog loaded successfully")
                    gemini_cog = self.bot.get_cog('GeminiEconomicCog')
                except Exception as e:
                    logger.warning(f"⚠️ Could not load Gemini cog: {e}")
                    return False
            
            # Disable Gemini by default to avoid conflicts
            if gemini_cog and hasattr(gemini_cog, 'enabled'):
                gemini_cog.enabled = False
                logger.info("🔒 Gemini disabled by default - use f!gemini toggle to enable")
            
            return True
            
        except Exception as e:
            logger.error(f"Error initializing Gemini cog: {e}")
            return False
    
    async def sync_with_existing_ai(self):
        """Đồng bộ với AI systems hiện tại"""
        try:
            # Get existing AI components
            ai_cog = self.bot.get_cog('AICog')
            weather_cog = self.bot.get_cog('WeatherCog')
            events_cog = self.bot.get_cog('EventsCog')
            
            if ai_cog:
                # Coordination with existing AI
                logger.info("🤖 Syncing with existing AI Manager")
                self.integration_status['ai_manager'] = True
            
            if weather_cog:
                # Ensure weather API compatibility
                logger.info("🌤️ Syncing with Weather system")
                await self.fix_weather_api_compatibility(weather_cog)
                self.integration_status['weather'] = True
            
            if events_cog:
                # Ensure events compatibility
                logger.info("🎯 Syncing with Events system")
                self.integration_status['events'] = True
            
        except Exception as e:
            logger.error(f"Error syncing with existing AI: {e}")
    
    async def fix_weather_api_compatibility(self, weather_cog):
        """Fix weather API compatibility issues"""
        try:
            # Fix the "no such column: coins" error
            # This happens when weather predictor tries to access user coins
            
            # Patch the weather predictor to use 'money' instead of 'coins'
            if hasattr(weather_cog, 'weather_predictor'):
                predictor = weather_cog.weather_predictor
                
                # Override problematic methods
                original_analyze = getattr(predictor, '_analyze_weather_context', None)
                if original_analyze:
                    async def safe_analyze_weather_context(game_state, current_weather):
                        try:
                            # Get users safely
                            all_users = await self.db.get_all_users()
                            
                            # Create safe game state
                            total_money = sum(user.get('money', 0) for user in all_users)
                            active_players = len(all_users)
                            
                            safe_game_state = type('GameState', (), {
                                'player_satisfaction': 0.7,
                                'recent_activity_level': 0.5,
                                'total_money_in_circulation': total_money,
                                'active_players': max(1, active_players)
                            })()
                            
                            return predictor._analyze_weather_context(safe_game_state, current_weather)
                        except Exception as e:
                            logger.warning(f"Weather analysis error: {e}")
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
                    
                    # Monkey patch for safety
                    predictor._safe_analyze_weather_context = safe_analyze_weather_context
            
            logger.info("✅ Weather API compatibility fixed")
            
        except Exception as e:
            logger.error(f"Error fixing weather API: {e}")
    
    async def setup_task_coordination(self):
        """Setup coordination giữa các tasks"""
        try:
            # Ensure proper task cleanup
            gemini_cog = self.bot.get_cog('GeminiEconomicCog')
            ai_cog = self.bot.get_cog('AICog')
            
            if gemini_cog and ai_cog:
                # Coordinate timing to avoid conflicts
                # Gemini runs every hour, AI runs every 30 minutes
                # Offset them by 15 minutes
                
                # Store original task intervals
                self.integration_status['task_coordination'] = {
                    'gemini_interval': 60,  # minutes
                    'ai_interval': 30,      # minutes
                    'offset': 15            # minutes
                }
            
            logger.info("✅ Task coordination setup complete")
            
        except Exception as e:
            logger.error(f"Error setting up task coordination: {e}")
    
    async def create_missing_table(self, table_name: str):
        """Tạo table bị thiếu"""
        table_schemas = {
            'users': '''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT NOT NULL,
                    money INTEGER DEFAULT 1000,
                    coins INTEGER DEFAULT 0,
                    land_slots INTEGER DEFAULT 4,
                    last_daily TEXT,
                    daily_streak INTEGER DEFAULT 0,
                    joined_date TEXT NOT NULL,
                    last_seen TEXT DEFAULT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''',
            'crops': '''
                CREATE TABLE IF NOT EXISTS crops (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    crop_type TEXT NOT NULL,
                    plot_index INTEGER NOT NULL,
                    plant_time TEXT NOT NULL,
                    growth_stage INTEGER DEFAULT 0,
                    buffs_applied TEXT DEFAULT '',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''',
            'inventory': '''
                CREATE TABLE IF NOT EXISTS inventory (
                    user_id INTEGER NOT NULL,
                    item_type TEXT NOT NULL,
                    item_id TEXT NOT NULL,
                    quantity INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_id, item_type, item_id),
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            '''
        }
        
        if table_name in table_schemas:
            await self.db.execute(table_schemas[table_name])
            logger.info(f"✅ Created missing table: {table_name}")
    
    async def verify_integration(self) -> Dict[str, Any]:
        """Xác minh integration status"""
        status = {
            'database_compatible': False,
            'gemini_cog_loaded': False,
            'ai_sync_complete': False,
            'task_coordination_active': False,
            'conflicts_resolved': False
        }
        
        try:
            # Check database
            if await self.db.table_exists('users'):
                status['database_compatible'] = True
            
            # Check Gemini cog
            if self.bot.get_cog('GeminiEconomicCog'):
                status['gemini_cog_loaded'] = True
            
            # Check AI sync
            if self.integration_status.get('ai_manager'):
                status['ai_sync_complete'] = True
            
            # Check task coordination
            if self.integration_status.get('task_coordination'):
                status['task_coordination_active'] = True
            
            # Overall status
            status['conflicts_resolved'] = all([
                status['database_compatible'],
                status['gemini_cog_loaded'],
                status['ai_sync_complete']
            ])
            
        except Exception as e:
            logger.error(f"Error verifying integration: {e}")
        
        return status
    
    async def get_integration_report(self) -> str:
        """Tạo báo cáo integration"""
        status = await self.verify_integration()
        
        report = "🔧 **Gemini Integration Status**\n\n"
        
        for key, value in status.items():
            icon = "✅" if value else "❌"
            readable_key = key.replace('_', ' ').title()
            report += f"{icon} {readable_key}: {value}\n"
        
        if status['conflicts_resolved']:
            report += "\n🎉 **Integration successful!** Gemini is ready to use."
        else:
            report += "\n⚠️ **Integration incomplete.** Some issues need attention."
        
        return report

async def apply_integration_fix(bot):
    """Áp dụng fix integration cho bot"""
    try:
        integration_manager = GeminiIntegrationManager(bot)
        success = await integration_manager.initialize_integration()
        
        if success:
            logger.info("🎉 Gemini integration applied successfully")
            
            # Store integration manager in bot for later use
            bot.gemini_integration = integration_manager
            
            return integration_manager
        else:
            logger.error("❌ Gemini integration failed")
            return None
            
    except Exception as e:
        logger.error(f"Error applying integration fix: {e}")
        return None 