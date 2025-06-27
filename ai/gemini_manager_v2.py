#!/usr/bin/env python3
"""
Gemini Manager V2 - Thay thế AI local bằng Gemini với multi API và cache
"""

import asyncio
import json
import os
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import aiofiles
from database.database import Database
from utils.enhanced_logging import get_bot_logger
from ai.smart_cache import SmartCache
from ai.gemini_client import get_gemini_manager, GEMINI_AVAILABLE

logger = get_bot_logger()

@dataclass
class GeminiDecision:
    """Quyết định từ Gemini AI"""
    action_type: str  # weather, event, price_adjustment, intervention
    reasoning: str
    confidence: float
    parameters: Dict[str, Any]
    expected_impact: str
    duration_hours: int
    priority: str  # low, medium, high, critical
    timestamp: datetime
    
    def asdict(self) -> Dict[str, Any]:
        """Convert to dict với datetime serialization"""
        return {
            'action_type': self.action_type,
            'reasoning': self.reasoning,
            'confidence': self.confidence,
            'parameters': self.parameters,
            'expected_impact': self.expected_impact,
            'duration_hours': self.duration_hours,
            'priority': self.priority,
            'timestamp': self.timestamp.isoformat()
        }

class GeminiAPIManager:
    """Quản lý multiple Gemini API keys với rotation và fallback - Updated for google-genai SDK"""
    
    def __init__(self, config_file: str = "ai/gemini_config.json"):
        self.config_file = config_file
        self.gemini_manager = get_gemini_manager()
        self.balance_config = {}
        self.prompts = {}
        
    async def load_config(self):
        """Load config từ file JSON"""
        try:
            if not os.path.exists(self.config_file):
                await self._create_default_config()
            
            async with aiofiles.open(self.config_file, 'r', encoding='utf-8') as f:
                content = await f.read()
                config = json.loads(content)
            
            self.balance_config = config.get('economic_balance_config', {})
            self.prompts = config.get('gemini_prompts', {})
            
            # Get status from new manager
            status = self.gemini_manager.get_status()
            logger.info(f"🤖 Gemini API Manager loaded: {status['available_clients']} clients")
            
        except Exception as e:
            logger.error(f"Error loading Gemini config: {e}")
            await self._create_default_config()
    
    async def _create_default_config(self):
        """Tạo config mặc định"""
        default_config = {
            "economic_balance_config": {
                "analysis_interval_hours": 1,
                "enable_auto_intervention": True,
                "inflation_warning_threshold": 0.08,
                "inflation_critical_threshold": 0.15
            },
            "gemini_prompts": {
                "economic_analysis": "Bạn là AI chuyên phân tích kinh tế game. Hãy phân tích dữ liệu và đưa ra quyết định cân bằng.",
                "system_message": "Bạn là AI quản lý kinh tế game Discord farming bot. Luôn trả lời bằng JSON hợp lệ."
            }
        }
        
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        async with aiofiles.open(self.config_file, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(default_config, indent=2, ensure_ascii=False))
    
    async def call_gemini(self, prompt: str, max_retries: int = 3) -> Optional[str]:
        """Gọi Gemini API sử dụng google-genai SDK"""
        if not GEMINI_AVAILABLE:
            logger.error("❌ google-genai SDK not available")
            return None
        
        try:
            system_message = self.prompts.get('system_message', 
                "Bạn là AI quản lý kinh tế game Discord farming bot.")
            
            response = await self.gemini_manager.generate_response(
                prompt=prompt,
                system_message=system_message,
                use_thinking=True  # Enable advanced reasoning
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error calling Gemini: {e}")
            return None
    
    async def call_gemini_json(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Gọi Gemini API và trả về JSON"""
        if not GEMINI_AVAILABLE:
            logger.error("❌ google-genai SDK not available")
            return None
        
        try:
            system_message = self.prompts.get('system_message', 
                "Bạn là AI quản lý kinh tế game Discord farming bot. Luôn trả lời bằng JSON hợp lệ.")
            
            response = await self.gemini_manager.generate_json_response(
                prompt=prompt,
                system_message=system_message,
                use_thinking=True
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error calling Gemini JSON: {e}")
            return None
    
    def get_api_status(self) -> Dict[str, Any]:
        """Get API status"""
        return self.gemini_manager.get_status()

class GeminiEconomicManagerV2:
    """
    Latina Economic Manager V2 - Thay thế AI local hoàn toàn
    """
    
    def __init__(self, database: Database):
        self.db = database
        self.api_manager = GeminiAPIManager()
        self.smart_cache = SmartCache()  # Smart cache for token saving
        
        # Cache và decision tracking
        self.economic_cache = {}
        self.weather_cache = {}
        self.player_cache = {}
        self.last_decision_time = None
        self.decision_history = []
        
        # Economic thresholds
        self.thresholds = {
            'inflation_critical': 0.15,
            'inflation_warning': 0.08,
            'activity_low': 0.3,
            'money_concentration_max': 0.7,
            'health_score_min': 0.4
        }
        
    async def initialize(self):
        """Khởi tạo Latina Manager"""
        await self.api_manager.load_config()
        await self.smart_cache.load_from_disk()
        await self.smart_cache.cleanup_old()
        logger.info("🎀 Latina Economic Manager V2 initialized")
    
    async def analyze_and_decide(self, bot) -> Optional[GeminiDecision]:
        """Phân tích toàn bộ và đưa ra quyết định"""
        try:
            current_time = datetime.now()
            
            # Check cooldown
            if (self.last_decision_time and 
                current_time - self.last_decision_time < timedelta(hours=1)):
                return None
            
            logger.info("🎀 Latina: Starting economic analysis...")
            
            # Thu thập dữ liệu
            economic_data = await self.collect_economic_data(bot)
            weather_data = await self.collect_weather_data(bot)
            player_data = await self.collect_player_data(bot)
            
            # Kiểm tra cache trước
            cached_decision = await self.smart_cache.get_cached_decision(economic_data, weather_data)
            if cached_decision:
                decision = self._convert_cached_to_decision(cached_decision)
                logger.info("💾 Cache HIT: Pattern {}-{}-{}-{} (used {} times)".format(
                    cached_decision.get('economic_pattern', 'unknown'),
                    cached_decision.get('weather_pattern', 'unknown'),
                    cached_decision.get('activity_pattern', 'unknown'),
                    cached_decision.get('weather_type', 'unknown'),
                    cached_decision.get('usage_count', 0)
                ))
                logger.info("💾 Using cached decision - Token saved!")
            else:
                # Tạo prompt cho Latina
                analysis_prompt = self._create_analysis_prompt(economic_data, weather_data, player_data)
                
                # Gọi Latina (JSON response)
                gemini_response = await self.api_manager.call_gemini_json(analysis_prompt)
                if not gemini_response:
                    logger.error("❌ Failed to get Latina response")
                    return None
                
                # Parse response
                decision = self._parse_gemini_json_decision(gemini_response)
                
                # Cache decision for future use
                await self.smart_cache.save_decision(
                    economic_data, weather_data, decision.asdict()
                )
            
            self.last_decision_time = current_time
            logger.info(f"🎀 Latina Decision: {decision.action_type} - {decision.reasoning[:100]}...")
            
            return decision
            
        except Exception as e:
            logger.error(f"Error in Latina analysis: {e}")
            return None
    
    async def collect_economic_data(self, bot) -> Dict[str, Any]:
        """Thu thập dữ liệu kinh tế từ cache hoặc database"""
        cache_key = 'economic_data'
        current_time = datetime.now()
        
        # Check cache
        if (cache_key in self.economic_cache and 
            current_time - self.economic_cache[cache_key]['timestamp'] < timedelta(minutes=30)):
            return self.economic_cache[cache_key]['data']
        
        # Collect fresh data
        all_users = await self.db.get_all_users()
        total_players = len(all_users)
        
        # Player activity
        active_cutoff = current_time - timedelta(hours=24)
        active_players = sum(1 for user in all_users 
                           if user.get('last_seen', current_time) > active_cutoff)
        
        # Money analysis
        money_amounts = [user.get('money', 0) for user in all_users]
        total_money = sum(money_amounts)
        avg_money = total_money / total_players if total_players > 0 else 0
        median_money = self._calculate_median(money_amounts)
        
        # Money distribution
        distribution = self._analyze_money_distribution(money_amounts)
        
        economic_data = {
            'total_players': total_players,
            'active_players_24h': active_players,
            'activity_rate': active_players / total_players if total_players > 0 else 0,
            'total_money_circulation': total_money,
            'average_money_per_player': avg_money,
            'median_money_per_player': median_money,
            'money_distribution': distribution,
            'economic_health_score': self._calculate_health_score(distribution, active_players, total_players)
        }
        
        # Cache result
        self.economic_cache[cache_key] = {
            'data': economic_data,
            'timestamp': current_time
        }
        
        return economic_data
    
    async def collect_weather_data(self, bot) -> Dict[str, Any]:
        """Thu thập dữ liệu thời tiết"""
        weather_cog = bot.get_cog('WeatherCog')
        if not weather_cog:
            return {'current_weather': 'sunny', 'modifier': 1.0}
        
        try:
            weather_data = await weather_cog.fetch_weather_data()
            current_weather = weather_data.get('weather', [{}])[0].get('main', 'clouds').lower()
            
            return {
                'current_weather': current_weather,
                'modifier': weather_cog.get_weather_effects().get('yield_modifier', 1.0),
                'temperature': weather_data.get('main', {}).get('temp', 25),
                'api_source': 'openweather'
            }
        except:
            return {'current_weather': 'sunny', 'modifier': 1.0}
    
    async def collect_player_data(self, bot) -> Dict[str, Any]:
        """Thu thập dữ liệu người chơi"""
        # Basic player stats (would expand with more tracking)
        return {
            'total_guilds': len(bot.guilds),
            'total_members': sum(len(guild.members) for guild in bot.guilds),
            'bot_uptime_hours': (datetime.now() - bot.start_time).total_seconds() / 3600 if hasattr(bot, 'start_time') else 0
        }
    
    def _create_analysis_prompt(self, economic_data: Dict, weather_data: Dict, player_data: Dict) -> str:
        """Tạo prompt phân tích cho Latina"""
        prompt = f"""
Bạn là chuyên gia kinh tế game nông trại Discord. Hãy phân tích dữ liệu sau và đưa ra quyết định cân bằng kinh tế:

DỮ LIỆU KINH TẾ:
- Tổng người chơi: {economic_data['total_players']}
- Người chơi hoạt động 24h: {economic_data['active_players_24h']} ({economic_data['activity_rate']:.1%})
- Tổng tiền lưu hành: {economic_data['total_money_circulation']:,} coins
- Trung bình tiền/người: {economic_data['average_money_per_player']:,.0f} coins
- Phân bổ tiền: {economic_data['money_distribution']}
- Điểm health kinh tế: {economic_data['economic_health_score']:.2f}/1.0

THỜI TIẾT HIỆN TẠI:
- Loại: {weather_data['current_weather']}
- Hệ số: {weather_data['modifier']}

HOẠT ĐỘNG HỆ THỐNG:
- Servers: {player_data['total_guilds']}
- Uptime: {player_data['bot_uptime_hours']:.1f} giờ

QUYỀN KIỂM SOÁT TOÀN BỘ:
Bạn có thể HOÀN TOÀN KIỂM SOÁT hệ thống thời tiết và sự kiện của game.
- Thời tiết sẽ thay đổi NGAY LẬP TỨC theo quyết định của bạn  
- Sự kiện sẽ được tạo và kích hoạt TỨC THỜI
- Bạn có thể override bất kỳ thời tiết/sự kiện nào đang chạy

NHIỆM VỤ:
Dựa vào dữ liệu trên, hãy quyết định MỘT trong các hành động sau để cân bằng kinh tế:

1. WEATHER_CHANGE: Thay đổi thời tiết ngay lập tức (sunny/rainy/cloudy/stormy/perfect)
2. EVENT_TRIGGER: Tạo và kích hoạt sự kiện đặc biệt ngay (buff/debuff/reward)
3. PRICE_ADJUSTMENT: Điều chỉnh giá cả thị trường
4. NO_ACTION: Không can thiệp

FORMAT PHẢN HỒI (JSON):
{{
  "action_type": "[WEATHER_CHANGE/EVENT_TRIGGER/PRICE_ADJUSTMENT/NO_ACTION]",
  "reasoning": "Lý do chi tiết cho quyết định này",
  "confidence": 0.85,
  "parameters": {{
    // For WEATHER_CHANGE:
    "weather_type": "rainy",  // sunny/rainy/cloudy/stormy/perfect
    "duration_hours": 4,
    
    // For EVENT_TRIGGER:
    "event_name": "Mưa phùng phí",
    "effect_type": "yield_bonus",  // yield_bonus/growth_bonus/price_bonus/seed_cost_reduction
    "effect_value": 1.2,  // Multiplier (1.2 = +20%, 0.8 = -20%)
    "duration_hours": 4,
    
    // For PRICE_ADJUSTMENT:
    "crop_type": "carrot",  // specific crop ID or "all" for all crops
    "sell_price_modifier": 1.15,  // Multiplier for sell price (1.15 = +15%)
    "seed_price_modifier": 0.9,   // Multiplier for seed cost (0.9 = -10% discount)
    "duration_hours": 1
  }},
  "expected_impact": "Mô tả tác động dự kiến",
  "priority": "medium"
}}

Hãy trả lời CHÍNH XÁC theo format JSON trên:
"""
        return prompt
    
    def _parse_gemini_decision(self, response: str) -> GeminiDecision:
        """Parse response từ Gemini thành decision object (deprecated - use JSON version)"""
        try:
            # Extract JSON from response
            response = response.strip()
            if response.startswith('```json'):
                response = response[7:]
            if response.endswith('```'):
                response = response[:-3]
            
            data = json.loads(response)
            
            return GeminiDecision(
                action_type=data.get('action_type', 'NO_ACTION'),
                reasoning=data.get('reasoning', 'No reasoning provided'),
                confidence=float(data.get('confidence', 0.5)),
                parameters=data.get('parameters', {}),
                expected_impact=data.get('expected_impact', ''),
                duration_hours=data.get('parameters', {}).get('duration_hours', 1),
                priority=data.get('priority', 'medium'),
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error parsing Gemini response: {e}")
            return self._get_fallback_decision()
    
    def _parse_gemini_json_decision(self, response_data: Dict[str, Any]) -> GeminiDecision:
        """Parse JSON response từ Gemini thành decision object"""
        try:
            return GeminiDecision(
                action_type=response_data.get('action_type', 'NO_ACTION'),
                reasoning=response_data.get('reasoning', 'No reasoning provided'),
                confidence=float(response_data.get('confidence', 0.5)),
                parameters=response_data.get('parameters', {}),
                expected_impact=response_data.get('expected_impact', ''),
                duration_hours=response_data.get('parameters', {}).get('duration_hours', 1),
                priority=response_data.get('priority', 'medium'),
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error parsing Gemini JSON response: {e}")
            logger.error(f"Response data: {response_data}")
            return self._get_fallback_decision()
    
    def _get_fallback_decision(self) -> GeminiDecision:
        """Quyết định dự phòng khi Gemini fail"""
        return GeminiDecision(
            action_type='NO_ACTION',
            reasoning='Fallback decision due to parsing error',
            confidence=0.1,
            parameters={},
            expected_impact='No impact',
            duration_hours=1,
            priority='low',
            timestamp=datetime.now()
        )
    
    # Utility methods
    def _calculate_median(self, values: List[float]) -> float:
        if not values:
            return 0.0
        sorted_values = sorted(values)
        n = len(sorted_values)
        if n % 2 == 0:
            return (sorted_values[n//2-1] + sorted_values[n//2]) / 2
        return sorted_values[n//2]
    
    def _analyze_money_distribution(self, money_amounts: List[int]) -> Dict[str, int]:
        distribution = {'0-1k': 0, '1k-10k': 0, '10k-100k': 0, '100k+': 0}
        for amount in money_amounts:
            if amount < 1000:
                distribution['0-1k'] += 1
            elif amount < 10000:
                distribution['1k-10k'] += 1
            elif amount < 100000:
                distribution['10k-100k'] += 1
            else:
                distribution['100k+'] += 1
        return distribution
    
    def _calculate_health_score(self, distribution: Dict, active: int, total: int) -> float:
        if total == 0:
            return 0.0
        
        activity_factor = min(1.0, active / total)
        total_players = sum(distribution.values())
        wealthy_percent = distribution.get('100k+', 0) / total_players if total_players > 0 else 0
        distribution_factor = max(0.0, 1.0 - (wealthy_percent / 0.5))
        
        return (activity_factor * 0.6 + distribution_factor * 0.4)
    
    def _convert_cached_to_decision(self, cached_data: Dict) -> GeminiDecision:
        """Chuyển đổi cached decision thành GeminiDecision object"""
        return GeminiDecision(
            action_type=cached_data.get('action_type', 'NO_ACTION'),
            reasoning=cached_data.get('reasoning', 'Cached decision'),
            confidence=cached_data.get('confidence', 0.8),
            parameters=cached_data.get('parameters', {}),
            expected_impact=cached_data.get('expected_impact', 'Reused from cache'),
            duration_hours=cached_data.get('parameters', {}).get('duration_hours', 1),
            priority=cached_data.get('priority', 'medium'),
            timestamp=datetime.now()
        )
    
    async def execute_decision(self, decision: GeminiDecision, bot) -> bool:
        """Thực thi quyết định từ Gemini"""
        try:
            if decision.action_type == 'WEATHER_CHANGE':
                return await self._execute_weather_change(decision, bot)
            elif decision.action_type == 'EVENT_TRIGGER':
                return await self._execute_event_trigger(decision, bot)
            elif decision.action_type == 'PRICE_ADJUSTMENT':
                return await self._execute_price_adjustment(decision, bot)
            else:
                logger.info("🤖 Gemini decided no action needed")
                return True
                
        except Exception as e:
            logger.error(f"Error executing Gemini decision: {e}")
            return False
    
    async def _execute_weather_change(self, decision: GeminiDecision, bot) -> bool:
        """Thực thi thay đổi thời tiết - Latina full control"""
        try:
            weather_cog = bot.get_cog('WeatherCog')
            if not weather_cog:
                logger.error("WeatherCog not found for Latina weather control")
                return False
            
            # Get current weather before change
            old_weather = weather_cog.current_weather
            new_weather = decision.parameters.get('weather_type', 'sunny')
            
            # Change weather với Latina control
            success = await self._set_gemini_weather(weather_cog, new_weather, decision.duration_hours, decision)
            
            if success:
                # Notify weather change
                await self._notify_gemini_weather_change(bot, old_weather, new_weather, decision)
                logger.info(f"🌤️ Latina Weather Control: {old_weather} → {new_weather} - {decision.reasoning}")
                return True
            else:
                logger.error("Failed to change weather via Latina")
                return False
                
        except Exception as e:
            logger.error(f"Error in Latina weather control: {e}")
            return False
    
    async def _set_gemini_weather(self, weather_cog, weather_type: str, duration_hours: int, decision: GeminiDecision) -> bool:
        """Set weather với Gemini control"""
        try:
            from datetime import datetime, timedelta
            
            # Set current weather với Gemini control
            weather_cog.current_weather = {
                'type': weather_type,
                'applied_at': datetime.now(),
                'duration': duration_hours * 3600,  # Convert to seconds
                'ai_generated': True,
                'gemini_controlled': True,
                'reasoning': decision.reasoning,
                'confidence': decision.confidence,
                'priority': decision.priority
            }
            
            # Set next weather change time
            weather_cog.next_weather_change = datetime.now() + timedelta(hours=duration_hours)
            weather_cog.weather_change_duration = duration_hours * 3600
            
            # Save weather state
            if hasattr(weather_cog, '_save_weather_state'):
                await weather_cog._save_weather_state()
            
            logger.info(f"🤖 Gemini set weather: {weather_type} until {weather_cog.next_weather_change}")
            return True
            
        except Exception as e:
            logger.error(f"Error setting Gemini weather: {e}")
            return False
    
    async def _execute_event_trigger(self, decision: GeminiDecision, bot) -> bool:
        """Thực thi sự kiện - Latina full control"""
        try:
            events_cog = bot.get_cog('EventsCog')
            if not events_cog:
                logger.error("EventsCog not found for Latina event control")
                return False
            
            # Tạo event data từ Latina decision
            event_data = {
                'name': decision.parameters.get('event_name', 'Sự kiện Latina AI'),
                'description': f"🎀 {decision.reasoning}",
                'effect_type': decision.parameters.get('effect_type', 'yield_bonus'),
                'effect_value': decision.parameters.get('effect_value', 1.2),
                'duration': decision.duration_hours * 3600,  # Convert to seconds
                'ai_generated': True,
                'gemini_controlled': True,
                'gemini_reasoning': decision.reasoning,
                'rarity': decision.priority,
                'confidence': decision.confidence
            }
            
            # Start event với Latina control
            success = await self._start_gemini_event(events_cog, event_data, decision)
            
            if success:
                # Notify về event start
                await self._notify_gemini_event_start(bot, event_data, decision)
                logger.info(f"🎯 Latina Event Control: {event_data['name']} - {decision.reasoning}")
                return True
            else:
                logger.error("Failed to start Latina event")
                return False
                
        except Exception as e:
            logger.error(f"Error in Latina event control: {e}")
            return False
    
    async def _start_gemini_event(self, events_cog, event_data: dict, decision: GeminiDecision) -> bool:
        """Start event với Latina control"""
        try:
            from datetime import datetime, timedelta
            
            # Stop current event if any (Latina takes priority)
            if events_cog.current_event:
                logger.info(f"🎀 Latina overriding current event: {events_cog.current_event.get('data', {}).get('name', 'Unknown')}")
            
            # Set Latina event
            events_cog.current_event = {
                'type': 'gemini_controlled',
                'data': event_data,
                'start_time': datetime.now()
            }
            
            # Set end time
            duration_hours = decision.duration_hours
            events_cog.event_end_time = datetime.now() + timedelta(hours=duration_hours)
            
            # Save event state
            if hasattr(events_cog, '_save_event_state'):
                await events_cog._save_event_state()
            
            logger.info(f"🎀 Latina started event: {event_data['name']} until {events_cog.event_end_time}")
            return True
            
        except Exception as e:
            logger.error(f"Error starting Latina event: {e}")
            return False
    
    async def _notify_gemini_weather_change(self, bot, old_weather: str, new_weather: str, decision: GeminiDecision):
        """Thông báo thay đổi thời tiết bởi Latina"""
        try:
            # Get all AI notification channels (with error handling)
            try:
                notifications = await bot.db.get_all_ai_notifications()
            except Exception:
                notifications = []  # Fallback if method doesn't exist or fails
            
            for notification in notifications:
                if notification.weather_notifications:  # Check if weather notifications are enabled
                    channel = bot.get_channel(notification.channel_id)
                    if channel:
                        embed = await self._create_gemini_weather_embed(old_weather, new_weather, decision)
                        try:
                            await channel.send(embed=embed)
                        except Exception as e:
                            logger.error(f"Error sending Latina weather notification to {notification.channel_id}: {e}")
                            
        except Exception as e:
            logger.error(f"Error notifying Latina weather change: {e}")
    
    async def _notify_gemini_event_start(self, bot, event_data: dict, decision: GeminiDecision):
        """Thông báo sự kiện được start bởi Latina"""
        try:
            # Get all AI notification channels (with error handling)
            try:
                notifications = await bot.db.get_all_ai_notifications()
            except Exception:
                notifications = []  # Fallback if method doesn't exist or fails
            
            for notification in notifications:
                if notification.event_notifications:  # Check if event notifications are enabled
                    channel = bot.get_channel(notification.channel_id)
                    if channel:
                        embed = await self._create_gemini_event_embed(event_data, decision)
                        try:
                            await channel.send(embed=embed)
                        except Exception as e:
                            logger.error(f"Error sending Latina event notification to {notification.channel_id}: {e}")
                            
        except Exception as e:
            logger.error(f"Error notifying Latina event start: {e}")
    
    async def _create_gemini_weather_embed(self, old_weather: str, new_weather: str, decision: GeminiDecision):
        """Tạo embed thông báo weather change bởi Latina"""
        from utils.embeds import EmbedBuilder
        
        weather_emojis = {
            'sunny': '☀️', 'cloudy': '☁️', 'rainy': '🌧️', 
            'stormy': '⛈️', 'perfect': '🌟'
        }
        
        weather_names = {
            'sunny': 'Nắng', 'cloudy': 'Có mây', 'rainy': 'Mưa',
            'stormy': 'Bão', 'perfect': 'Hoàn hảo'
        }
        
        old_emoji = weather_emojis.get(old_weather, '🌤️')
        new_emoji = weather_emojis.get(new_weather, '🌤️')
        old_name = weather_names.get(old_weather, old_weather or 'Không rõ')
        new_name = weather_names.get(new_weather, new_weather)
        
        embed = EmbedBuilder.create_base_embed(
            "🎀 Latina đã thay đổi thời tiết!",
            f"Mình đã phân tích tình hình và quyết định thay đổi thời tiết cho trang trại nhé! 💖",
            color=0xff69b4
        )
        
        embed.add_field(
            name="🔄 Thay đổi thời tiết",
            value=f"{old_emoji} {old_name} ➜ {new_emoji} {new_name}",
            inline=False
        )
        
        embed.add_field(
            name="🌸 Lý do của mình",
            value=decision.reasoning,
            inline=False
        )
        
        embed.add_field(
            name="📊 Độ tin cậy",
            value=f"{decision.confidence:.1%}",
            inline=True
        )
        
        embed.add_field(
            name="⏰ Thời gian",
            value=f"{decision.duration_hours} giờ",
            inline=True
        )
        
        embed.add_field(
            name="🎯 Ưu tiên",
            value=decision.priority.upper(),
            inline=True
        )
        
        embed.set_footer(text="Latina AI Economic Manager • f!weather để xem chi tiết")
        
        return embed
    
    async def _create_gemini_event_embed(self, event_data: dict, decision: GeminiDecision):
        """Tạo embed thông báo event start bởi Latina"""
        from utils.embeds import EmbedBuilder
        
        embed = EmbedBuilder.create_base_embed(
            f"🎉 {event_data['name']}",
            f"Mình đã tạo sự kiện mới cho mọi người! 💖",
            color=0xff69b4
        )
        
        embed.add_field(
            name="📝 Mô tả",
            value=event_data['description'],
            inline=False
        )
        
        # Effect info
        effect_type = event_data.get('effect_type', 'unknown')
        effect_value = event_data.get('effect_value', 1.0)
        
        effect_names = {
            'yield_bonus': '🎯 Sản lượng',
            'growth_bonus': '⚡ Tốc độ sinh trưởng', 
            'price_bonus': '💰 Giá bán',
            'seed_cost_reduction': '🌱 Giảm giá hạt giống'
        }
        
        effect_name = effect_names.get(effect_type, effect_type)
        embed.add_field(
            name="⚡ Hiệu ứng",
            value=f"{effect_name}: {effect_value:.1%}",
            inline=True
        )
        
        embed.add_field(
            name="⏰ Thời gian",
            value=f"{decision.duration_hours} giờ",
            inline=True
        )
        
        embed.add_field(
            name="📊 Độ tin cậy",
            value=f"{decision.confidence:.1%}",
            inline=True
        )
        
        embed.add_field(
            name="🌸 Lý do của mình",
            value=decision.reasoning,
            inline=False
        )
        
        embed.set_footer(text="Latina AI Economic Manager • f!event để xem chi tiết")
        
        return embed
    
    async def _execute_price_adjustment(self, decision: GeminiDecision, bot) -> bool:
        """Thực thi điều chỉnh giá thông qua PricingCoordinator"""
        try:
            from utils.pricing import pricing_coordinator
            import config
            
            # Extract price adjustment parameters
            params = decision.parameters
            crop_type = params.get('crop_type', '')
            sell_modifier = params.get('sell_price_modifier', 1.0)
            seed_modifier = params.get('seed_price_modifier', 1.0)
            
            # Validate parameters
            if not crop_type:
                logger.error("🎀 Latina Price Adjustment: No crop type specified")
                return False
            
            if crop_type == 'all':
                # Apply to all crops
                success_count = 0
                for crop_id in config.CROPS.keys():
                    if pricing_coordinator.apply_ai_price_adjustment(
                        crop_id, sell_modifier, seed_modifier, 
                        decision.reasoning, decision.duration_hours
                    ):
                        success_count += 1
                
                logger.info(f"🎀 Latina applied price adjustment to {success_count}/{len(config.CROPS)} crops")
                await self._notify_gemini_price_adjustment(bot, crop_type, sell_modifier, seed_modifier, decision)
                return success_count > 0
            else:
                # Apply to specific crop
                success = pricing_coordinator.apply_ai_price_adjustment(
                    crop_type, sell_modifier, seed_modifier,
                    decision.reasoning, decision.duration_hours
                )
                
                if success:
                    await self._notify_gemini_price_adjustment(bot, crop_type, sell_modifier, seed_modifier, decision)
                    logger.info(f"🎀 Latina Price Adjustment successful for {crop_type}")
                else:
                    logger.error(f"🎀 Latina Price Adjustment failed for {crop_type}")
                
                return success
                
        except Exception as e:
            logger.error(f"Error executing Latina price adjustment: {e}")
            return False
    
    async def _notify_gemini_price_adjustment(self, bot, crop_type: str, sell_modifier: float, 
                                           seed_modifier: float, decision: GeminiDecision):
        """Thông báo điều chỉnh giá bởi Latina"""
        try:
            # Get all AI notification channels
            try:
                notifications = await bot.db.get_all_ai_notifications()
            except Exception:
                notifications = []
            
            for notification in notifications:
                if notification.economic_notifications:  # Check if economic notifications are enabled
                    channel = bot.get_channel(notification.channel_id)
                    if channel:
                        embed = await self._create_gemini_price_embed(crop_type, sell_modifier, seed_modifier, decision)
                        try:
                            await channel.send(embed=embed)
                        except Exception as e:
                            logger.error(f"Error sending Latina price notification to {notification.channel_id}: {e}")
                            
        except Exception as e:
            logger.error(f"Error notifying Latina price adjustment: {e}")
    
    async def _create_gemini_price_embed(self, crop_type: str, sell_modifier: float, 
                                       seed_modifier: float, decision: GeminiDecision):
        """Tạo embed thông báo price adjustment bởi Latina"""
        from utils.embeds import EmbedBuilder
        import config
        
        if crop_type == 'all':
            title = "💰 Latina đã điều chỉnh giá thị trường!"
            crop_name = "Tất cả nông sản"
            emoji = "🌾"
        else:
            crop_config = config.CROPS.get(crop_type, {})
            crop_name = crop_config.get('name', crop_type)
            emoji = crop_config.get('emoji', '🌾')
            title = f"💰 Latina đã điều chỉnh giá {crop_name}!"
        
        embed = EmbedBuilder.create_base_embed(
            title,
            f"Mình đã phân tích thị trường và quyết định điều chỉnh giá cả để cân bằng kinh tế nhé! 💖",
            color=0xff69b4
        )
        
        # Price changes
        sell_change = (sell_modifier - 1.0) * 100
        seed_change = (seed_modifier - 1.0) * 100
        
        sell_icon = "📈" if sell_change > 0 else "📉" if sell_change < 0 else "➡️"
        seed_icon = "📈" if seed_change > 0 else "📉" if seed_change < 0 else "➡️"
        
        embed.add_field(
            name=f"{emoji} Sản phẩm",
            value=crop_name,
            inline=True
        )
        
        embed.add_field(
            name="💰 Giá bán",
            value=f"{sell_icon} {sell_change:+.1f}% ({sell_modifier:.2f}x)",
            inline=True
        )
        
        embed.add_field(
            name="🌱 Giá hạt giống",
            value=f"{seed_icon} {seed_change:+.1f}% ({seed_modifier:.2f}x)",
            inline=True
        )
        
        embed.add_field(
            name="🌸 Lý do của mình",
            value=decision.reasoning,
            inline=False
        )
        
        embed.add_field(
            name="📊 Độ tin cậy",
            value=f"{decision.confidence:.1%}",
            inline=True
        )
        
        embed.add_field(
            name="⏰ Thời gian hiệu lực",
            value=f"{decision.duration_hours} giờ",
            inline=True
        )
        
        embed.add_field(
            name="🎯 Ưu tiên",
            value=decision.priority.upper(),
            inline=True
        )
        
        embed.set_footer(text="Latina AI Economic Manager • f!market để xem giá mới")
        
        return embed 