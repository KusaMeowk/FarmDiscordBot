#!/usr/bin/env python3
"""
Hourly Scenario Updater - Cập nhật scenarios kinh tế mỗi giờ
Đồng bộ với Gemini Economic Manager và các hệ thống khác
"""

import asyncio
import json
import os
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any
from discord.ext import tasks
from ai.enhanced_economic_scenarios import EnhancedEconomicScenarios
from ai.smart_cache import SmartCache
from ai.gemini_economic_manager import GeminiEconomicManager
from utils.enhanced_logging import get_bot_logger

logger = get_bot_logger()

class HourlyScenarioUpdater:
    """Cập nhật scenarios kinh tế theo giờ và đồng bộ với game"""
    
    def __init__(self, bot, gemini_manager: GeminiEconomicManager = None):
        self.bot = bot
        self.gemini_manager = gemini_manager
        self.scenario_generator = EnhancedEconomicScenarios()
        self.smart_cache = SmartCache()
        
        # Load cache hiện tại
        asyncio.create_task(self.smart_cache.load_from_disk())
        
        # Settings
        self.update_interval_hours = 1
        self.max_scenarios_per_update = 20
        self.scenario_expiry_hours = 24
        
        # Tracking
        self.last_update = None
        self.update_count = 0
        self.integration_status = {
            "weather_sync": True,
            "event_sync": True, 
            "market_sync": True,
            "gemini_sync": True
        }
        
        logger.info("🔄 Hourly Scenario Updater initialized")
    
    async def start_updater(self):
        """Khởi động updater task"""
        self.hourly_update_task.start()
        logger.info("⏰ Started hourly scenario update task")
    
    def stop_updater(self):
        """Dừng updater task"""
        if self.hourly_update_task.is_running():
            self.hourly_update_task.cancel()
            logger.info("⏹️ Stopped hourly scenario update task")
    
    @tasks.loop(hours=1)
    async def hourly_update_task(self):
        """Task chạy mỗi giờ để cập nhật scenarios"""
        try:
            logger.info("🔄 Starting hourly scenario update...")
            
            # Thu thập dữ liệu game hiện tại
            game_state = await self.collect_current_game_state()
            
            # Tạo scenarios mới dựa trên game state
            new_scenarios = await self.generate_contextual_scenarios(game_state)
            
            # Cập nhật smart cache
            await self.update_smart_cache(new_scenarios)
            
            # Đồng bộ với các hệ thống khác
            await self.sync_with_game_systems(new_scenarios, game_state)
            
            # Cleanup scenarios cũ
            await self.cleanup_old_scenarios()
            
            # Log kết quả
            self.last_update = datetime.now()
            self.update_count += 1
            
            logger.info(f"✅ Hourly update #{self.update_count} completed: {len(new_scenarios)} new scenarios")
            
            # Optional: Notify về scenarios đặc biệt
            await self.notify_special_scenarios(new_scenarios)
            
        except Exception as e:
            logger.error(f"❌ Error in hourly update: {e}")
    
    async def collect_current_game_state(self) -> Dict[str, Any]:
        """Thu thập trạng thái game hiện tại"""
        try:
            # Lấy dữ liệu từ Gemini Manager nếu có
            if self.gemini_manager:
                economic_data = await self.gemini_manager.collect_economic_data(self.bot)
                game_state = {
                    "economic_health": economic_data.economic_health_score,
                    "activity_rate": economic_data.active_players_24h / max(1, economic_data.total_players),
                    "total_players": economic_data.total_players,
                    "money_distribution": economic_data.money_distribution,
                    "inflation_rate": economic_data.inflation_rate,
                    "weather_type": economic_data.weather_type,
                    "active_events": economic_data.active_events
                }
            else:
                # Fallback: Thu thập dữ liệu cơ bản
                game_state = await self.collect_basic_game_state()
            
            # Thêm thông tin thời gian và mùa
            current_time = datetime.now()
            game_state.update({
                "current_hour": current_time.hour,
                "season": self.scenario_generator._get_current_season(),
                "time_period": self.get_time_period(current_time.hour),
                "day_of_week": current_time.weekday(),
                "is_weekend": current_time.weekday() >= 5
            })
            
            return game_state
            
        except Exception as e:
            logger.error(f"Error collecting game state: {e}")
            return self.get_default_game_state()
    
    async def collect_basic_game_state(self) -> Dict[str, Any]:
        """Thu thập dữ liệu game cơ bản khi không có Gemini Manager"""
        try:
            # Lấy dữ liệu từ database
            all_users = await self.bot.db.get_all_users()
            total_players = len(all_users)
            
            # Tính toán metrics cơ bản
            if total_players > 0:
                money_amounts = [user.get('money', 0) for user in all_users]
                avg_money = sum(money_amounts) / total_players
                economic_health = min(1.0, avg_money / 10000)  # Normalize to 0-1
                activity_rate = 0.5  # Default estimate
            else:
                economic_health = 0.5
                activity_rate = 0.1
            
            return {
                "economic_health": economic_health,
                "activity_rate": activity_rate,
                "total_players": total_players,
                "money_distribution": {"balanced": True},
                "inflation_rate": 0.05,
                "weather_type": "sunny",
                "active_events": []
            }
            
        except Exception as e:
            logger.error(f"Error collecting basic game state: {e}")
            return self.get_default_game_state()
    
    def get_default_game_state(self) -> Dict[str, Any]:
        """Game state mặc định khi có lỗi"""
        return {
            "economic_health": 0.6,
            "activity_rate": 0.4,
            "total_players": 10,
            "money_distribution": {"balanced": True},
            "inflation_rate": 0.05,
            "weather_type": "sunny",
            "active_events": [],
            "current_hour": datetime.now().hour,
            "season": "spring",
            "time_period": "morning",
            "day_of_week": 1,
            "is_weekend": False
        }
    
    def get_time_period(self, hour: int) -> str:
        """Xác định thời gian trong ngày"""
        if 6 <= hour < 12:
            return "morning"
        elif 12 <= hour < 18:
            return "afternoon"
        elif 18 <= hour < 23:
            return "evening"
        else:
            return "night"
    
    async def generate_contextual_scenarios(self, game_state: Dict[str, Any]) -> Dict[str, Any]:
        """Tạo scenarios phù hợp với context hiện tại"""
        try:
            # Tạo scenarios cơ bản từ generator
            base_scenarios = self.scenario_generator.generate_hourly_scenarios({})
            
            # Điều chỉnh scenarios dựa trên game state
            contextual_scenarios = {}
            
            for pattern, scenario_data in base_scenarios.items():
                # Điều chỉnh dựa trên game state
                adjusted_scenario = await self.adjust_scenario_for_context(scenario_data, game_state)
                
                if adjusted_scenario:  # Nếu scenario phù hợp
                    contextual_scenarios[pattern] = adjusted_scenario
            
            # Thêm scenarios đặc biệt dựa trên tình hình cụ thể
            special_scenarios = await self.create_special_scenarios(game_state)
            contextual_scenarios.update(special_scenarios)
            
            # Limit số lượng scenarios
            if len(contextual_scenarios) > self.max_scenarios_per_update:
                # Sắp xếp theo priority và giới hạn
                sorted_scenarios = sorted(
                    contextual_scenarios.items(),
                    key=lambda x: self.get_scenario_priority_score(x[1], game_state),
                    reverse=True
                )
                contextual_scenarios = dict(sorted_scenarios[:self.max_scenarios_per_update])
            
            return contextual_scenarios
            
        except Exception as e:
            logger.error(f"Error generating contextual scenarios: {e}")
            return {}
    
    async def adjust_scenario_for_context(self, scenario_data: Dict, game_state: Dict) -> Dict:
        """Điều chỉnh scenario theo context"""
        try:
            decision = scenario_data["decision"].copy()
            
            # Điều chỉnh dựa trên economic health
            health = game_state.get("economic_health", 0.5)
            
            if health < 0.3:  # Kinh tế khó khăn
                # Tăng rewards, giảm challenges
                if "multiplier" in decision.get("parameters", {}):
                    decision["parameters"]["multiplier"] *= 1.3
                if decision.get("action_type") == "CHALLENGE_EVENT":
                    decision["parameters"]["difficulty_reduction"] = 0.7
                    
            elif health > 0.8:  # Kinh tế thịnh vượng  
                # Tăng challenges, điều chỉnh rewards
                if decision.get("action_type") == "RECOVERY_EVENT":
                    return None  # Bỏ qua recovery events khi không cần
                if "multiplier" in decision.get("parameters", {}):
                    decision["parameters"]["multiplier"] *= 0.9
            
            # Điều chỉnh dựa trên activity rate
            activity = game_state.get("activity_rate", 0.5)
            
            if activity < 0.3:  # Ít hoạt động
                # Tăng incentives
                decision["parameters"]["low_activity_bonus"] = 1.5
                if "duration_hours" in decision.get("parameters", {}):
                    decision["parameters"]["duration_hours"] *= 1.5
                    
            elif activity > 0.8:  # Hoạt động cao
                # Tạo competition events
                decision["parameters"]["high_activity_competition"] = True
            
            # Điều chỉnh theo thời gian
            if game_state.get("is_weekend"):
                decision["parameters"]["weekend_bonus"] = 1.2
            
            if game_state.get("time_period") == "night":
                decision["parameters"]["night_owl_bonus"] = 1.8
            
            # Update scenario data
            scenario_data["decision"] = decision
            scenario_data["context_adjusted"] = True
            scenario_data["adjustment_factors"] = {
                "economic_health": health,
                "activity_rate": activity,
                "time_period": game_state.get("time_period"),
                "is_weekend": game_state.get("is_weekend")
            }
            
            return scenario_data
            
        except Exception as e:
            logger.error(f"Error adjusting scenario: {e}")
            return scenario_data
    
    async def create_special_scenarios(self, game_state: Dict) -> Dict[str, Any]:
        """Tạo scenarios đặc biệt dựa trên tình hình cụ thể"""
        special_scenarios = {}
        current_time = datetime.now()
        
        try:
            # Crisis scenarios
            if game_state.get("economic_health", 0.5) < 0.2:
                special_scenarios[f"crisis_{current_time.hour}"] = {
                    "decision": {
                        "action_type": "EMERGENCY_INTERVENTION",
                        "reasoning": "Kinh tế trong tình trạng khẩn cấp, cần can thiệp ngay lập tức",
                        "confidence": 0.95,
                        "parameters": {
                            "emergency_stimulus": 10000,
                            "free_resources": True,
                            "boost_multiplier": 3.0,
                            "duration_hours": 6
                        },
                        "expected_impact": "Phục hồi kinh tế khỏi khủng hoảng",
                        "priority": "critical"
                    },
                    "created_at": current_time.isoformat(),
                    "usage_count": 0,
                    "pattern": f"emergency_crisis_{game_state.get('economic_health', 0):.2f}",
                    "scenario_type": "emergency"
                }
            
            # Low activity scenarios
            if game_state.get("activity_rate", 0.5) < 0.2:
                special_scenarios[f"low_activity_{current_time.hour}"] = {
                    "decision": {
                        "action_type": "ENGAGEMENT_BOOST",
                        "reasoning": "Hoạt động người chơi thấp, cần events thu hút",
                        "confidence": 0.85,
                        "parameters": {
                            "engagement_multiplier": 2.5,
                            "special_rewards": True,
                            "social_incentives": True,
                            "duration_hours": 12
                        },
                        "expected_impact": "Tăng engagement và thu hút người chơi quay lại",
                        "priority": "high"
                    },
                    "created_at": current_time.isoformat(),
                    "usage_count": 0,
                    "pattern": f"low_activity_{game_state.get('activity_rate', 0):.2f}",
                    "scenario_type": "engagement"
                }
            
            # Weekend special events
            if game_state.get("is_weekend"):
                special_scenarios[f"weekend_special_{current_time.hour}"] = {
                    "decision": {
                        "action_type": "WEEKEND_CELEBRATION",
                        "reasoning": "Cuối tuần, thời gian lý tưởng cho events đặc biệt",
                        "confidence": 0.9,
                        "parameters": {
                            "weekend_bonus": 1.8,
                            "community_events": True,
                            "extended_duration": True,
                            "duration_hours": 48
                        },
                        "expected_impact": "Tạo không khí lễ hội cuối tuần",
                        "priority": "medium"
                    },
                    "created_at": current_time.isoformat(),
                    "usage_count": 0,
                    "pattern": f"weekend_{current_time.weekday()}",
                    "scenario_type": "weekend"
                }
            
            # Prosperity scenarios
            if game_state.get("economic_health", 0.5) > 0.9 and game_state.get("activity_rate", 0.5) > 0.8:
                special_scenarios[f"golden_age_{current_time.hour}"] = {
                    "decision": {
                        "action_type": "GOLDEN_AGE_EVENT",
                        "reasoning": "Nền kinh tế thịnh vượng và người chơi active cao, thời kỳ hoàng kim",
                        "confidence": 0.95,
                        "parameters": {
                            "golden_age_multiplier": 2.0,
                            "exclusive_rewards": True,
                            "prestige_bonuses": True,
                            "duration_hours": 24
                        },
                        "expected_impact": "Kỷ niệm thời kỳ thịnh vượng của cộng đồng",
                        "priority": "legendary"
                    },
                    "created_at": current_time.isoformat(),
                    "usage_count": 0,
                    "pattern": f"golden_age_{game_state.get('economic_health', 0):.1f}_{game_state.get('activity_rate', 0):.1f}",
                    "scenario_type": "legendary"
                }
            
            return special_scenarios
            
        except Exception as e:
            logger.error(f"Error creating special scenarios: {e}")
            return {}
    
    def get_scenario_priority_score(self, scenario_data: Dict, game_state: Dict) -> float:
        """Tính điểm priority cho scenario"""
        try:
            base_score = 0.5
            decision = scenario_data.get("decision", {})
            
            # Priority từ decision
            priority_scores = {
                "critical": 1.0,
                "high": 0.8,
                "medium": 0.6,
                "low": 0.4
            }
            base_score += priority_scores.get(decision.get("priority", "medium"), 0.6)
            
            # Confidence score
            confidence = decision.get("confidence", 0.5)
            base_score += confidence * 0.3
            
            # Context relevance
            if scenario_data.get("context_adjusted"):
                base_score += 0.2
            
            # Scenario type bonus
            type_bonuses = {
                "emergency": 0.5,
                "legendary": 0.4,
                "weekend": 0.3,
                "engagement": 0.2
            }
            scenario_type = scenario_data.get("scenario_type", "common")
            base_score += type_bonuses.get(scenario_type, 0)
            
            return base_score
            
        except Exception as e:
            logger.error(f"Error calculating priority score: {e}")
            return 0.5
    
    async def update_smart_cache(self, new_scenarios: Dict[str, Any]):
        """Cập nhật smart cache với scenarios mới"""
        try:
            # Load cache hiện tại
            await self.smart_cache.load_from_disk()
            
            # Thêm scenarios mới
            for pattern, scenario_data in new_scenarios.items():
                self.smart_cache.decisions[pattern] = scenario_data
            
            # Save cache
            await self.smart_cache.save_to_disk()
            
            logger.info(f"📝 Updated smart cache with {len(new_scenarios)} new scenarios")
            
        except Exception as e:
            logger.error(f"Error updating smart cache: {e}")
    
    async def sync_with_game_systems(self, new_scenarios: Dict, game_state: Dict):
        """Đồng bộ scenarios với các hệ thống game khác"""
        try:
            # Sync với Weather system
            if self.integration_status["weather_sync"]:
                await self.sync_with_weather_system(new_scenarios, game_state)
            
            # Sync với Event system
            if self.integration_status["event_sync"]:
                await self.sync_with_event_system(new_scenarios, game_state)
            
            # Sync với Market system
            if self.integration_status["market_sync"]:
                await self.sync_with_market_system(new_scenarios, game_state)
            
            # Sync với Gemini Manager
            if self.integration_status["gemini_sync"] and self.gemini_manager:
                await self.sync_with_gemini_manager(new_scenarios, game_state)
            
        except Exception as e:
            logger.error(f"Error syncing with game systems: {e}")
    
    async def sync_with_weather_system(self, scenarios: Dict, game_state: Dict):
        """Đồng bộ với hệ thống thời tiết"""
        try:
            weather_cog = self.bot.get_cog('WeatherCog')
            if not weather_cog:
                return
            
            # Tìm scenarios liên quan đến thời tiết
            weather_scenarios = [
                s for s in scenarios.values()
                if s["decision"].get("action_type") in ["WEATHER_CHANGE", "WEATHER_ENHANCEMENT"]
            ]
            
            if weather_scenarios:
                # Thông báo về weather scenarios
                logger.info(f"🌤️ Found {len(weather_scenarios)} weather-related scenarios")
                
                # Có thể trigger weather changes nếu cần
                for scenario in weather_scenarios[:1]:  # Chỉ apply 1 weather change
                    weather_params = scenario["decision"].get("parameters", {})
                    if weather_params.get("weather_type"):
                        # Optionally trigger weather change
                        pass
            
        except Exception as e:
            logger.error(f"Error syncing with weather system: {e}")
    
    async def sync_with_event_system(self, scenarios: Dict, game_state: Dict):
        """Đồng bộ với hệ thống events"""
        try:
            events_cog = self.bot.get_cog('EventsCog')
            if not events_cog:
                return
            
            # Tìm scenarios event-related
            event_scenarios = [
                s for s in scenarios.values()
                if s["decision"].get("action_type") in ["EVENT_TRIGGER", "SEASONAL_EVENT", "CRISIS_EVENT"]
            ]
            
            if event_scenarios:
                logger.info(f"🎪 Found {len(event_scenarios)} event-related scenarios")
                
                # Có thể trigger events tự động hoặc lưu để reference
                for scenario in event_scenarios:
                    event_params = scenario["decision"].get("parameters", {})
                    if event_params.get("event_name"):
                        # Store event for potential triggering
                        pass
            
        except Exception as e:
            logger.error(f"Error syncing with event system: {e}")
    
    async def sync_with_market_system(self, scenarios: Dict, game_state: Dict):
        """Đồng bộ với hệ thống thị trường"""
        try:
            # Market-related scenarios có thể ảnh hưởng đến pricing
            market_scenarios = [
                s for s in scenarios.values() 
                if s["decision"].get("action_type") in ["MARKET_EVENT", "PRICE_ADJUSTMENT"]
            ]
            
            if market_scenarios:
                logger.info(f"💰 Found {len(market_scenarios)} market-related scenarios")
                # Có thể adjust market conditions
            
        except Exception as e:
            logger.error(f"Error syncing with market system: {e}")
    
    async def sync_with_gemini_manager(self, scenarios: Dict, game_state: Dict):
        """Đồng bộ với Gemini Economic Manager"""
        try:
            # Update Gemini với scenarios mới
            if hasattr(self.gemini_manager, 'scenario_context'):
                self.gemini_manager.scenario_context = {
                    "available_scenarios": len(scenarios),
                    "scenario_types": list(set(s.get("scenario_type", "common") for s in scenarios.values())),
                    "last_update": datetime.now().isoformat(),
                    "game_state_snapshot": game_state
                }
            
            logger.info("🤖 Synced scenarios with Gemini Manager")
            
        except Exception as e:
            logger.error(f"Error syncing with Gemini Manager: {e}")
    
    async def cleanup_old_scenarios(self):
        """Dọn dẹp scenarios cũ"""
        try:
            current_time = datetime.now()
            cutoff_time = current_time - timedelta(hours=self.scenario_expiry_hours)
            
            old_patterns = []
            for pattern, data in self.smart_cache.decisions.items():
                created_at = datetime.fromisoformat(data["created_at"])
                if created_at < cutoff_time and data.get("usage_count", 0) == 0:
                    old_patterns.append(pattern)
            
            # Xóa scenarios cũ
            for pattern in old_patterns:
                del self.smart_cache.decisions[pattern]
            
            if old_patterns:
                await self.smart_cache.save_to_disk()
                logger.info(f"🧹 Cleaned up {len(old_patterns)} old scenarios")
            
        except Exception as e:
            logger.error(f"Error cleaning up old scenarios: {e}")
    
    async def notify_special_scenarios(self, scenarios: Dict):
        """Thông báo về scenarios đặc biệt"""
        try:
            special_scenarios = [
                s for s in scenarios.values()
                if s.get("scenario_type") in ["legendary", "emergency", "golden_age"]
            ]
            
            if special_scenarios:
                logger.info(f"⭐ Generated {len(special_scenarios)} special scenarios this hour")
                
                # Có thể gửi notification đến Discord channel nếu cần
                for scenario in special_scenarios:
                    decision = scenario["decision"]
                    logger.info(f"🌟 Special scenario: {decision.get('action_type')} - {decision.get('reasoning')}")
            
        except Exception as e:
            logger.error(f"Error notifying special scenarios: {e}")
    
    async def generate_comprehensive_cache_update(self):
        """Tạo update toàn diện cho cache (dùng khi khởi động)"""
        try:
            logger.info("🔄 Generating comprehensive cache update...")
            
            # Tạo cache hoàn chỉnh từ generator
            comprehensive_cache = self.scenario_generator.create_comprehensive_cache()
            
            # Merge với cache hiện tại
            await self.smart_cache.load_from_disk()
            
            # Backup cache cũ
            backup_file = f"cache/smart_cache_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            if self.smart_cache.decisions:
                with open(backup_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        "decisions": self.smart_cache.decisions,
                        "stats": {
                            "hits": self.smart_cache.hits,
                            "misses": self.smart_cache.misses,
                            "tokens_saved": self.smart_cache.tokens_saved
                        }
                    }, f, ensure_ascii=False, indent=2)
                logger.info(f"💾 Backed up old cache to {backup_file}")
            
            # Update với comprehensive cache
            self.smart_cache.decisions.update(comprehensive_cache["decisions"])
            
            # Save
            await self.smart_cache.save_to_disk()
            
            logger.info(f"✅ Comprehensive cache update completed: {len(comprehensive_cache['decisions'])} total scenarios")
            return comprehensive_cache
            
        except Exception as e:
            logger.error(f"Error in comprehensive cache update: {e}")
            return {}
    
    def get_status(self) -> Dict[str, Any]:
        """Lấy trạng thái của updater"""
        return {
            "is_running": self.hourly_update_task.is_running() if hasattr(self, 'hourly_update_task') else False,
            "last_update": self.last_update.isoformat() if self.last_update else None,
            "update_count": self.update_count,
            "update_interval_hours": self.update_interval_hours,
            "max_scenarios_per_update": self.max_scenarios_per_update,
            "scenario_expiry_hours": self.scenario_expiry_hours,
            "integration_status": self.integration_status,
            "cache_stats": self.smart_cache.get_stats() if self.smart_cache else {}
        }