#!/usr/bin/env python3
"""
Gemini Economic Manager - Cân bằng kinh tế game thông qua Gemini AI
"""

import asyncio
import json
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import aiohttp
from database.database import Database
from utils.enhanced_logging import get_bot_logger

logger = get_bot_logger()

@dataclass
class GameEconomicData:
    """Dữ liệu kinh tế game cho cache"""
    timestamp: datetime
    total_players: int
    active_players_24h: int
    total_money_circulation: int
    average_money_per_player: float
    median_money_per_player: float
    money_distribution: Dict[str, int]  # ranges: 0-1k, 1k-10k, 10k-100k, 100k+
    weather_type: str
    weather_modifier: float
    active_events: List[str]
    market_activity: Dict[str, int]  # crop sales last 24h
    inflation_rate: float
    economic_health_score: float

@dataclass 
class GeminiEconomicDecision:
    """Quyết định kinh tế từ Gemini"""
    action_type: str  # weather_change, event_trigger, price_adjustment
    reasoning: str
    confidence: float
    parameters: Dict
    expected_impact: str
    duration_hours: int
    priority: str  # low, medium, high, critical

class EconomicCache:
    """Cache system cho dữ liệu kinh tế"""
    
    def __init__(self, cache_duration_minutes: int = 30):
        self.cache_duration = timedelta(minutes=cache_duration_minutes)
        self.cache = {}
        self.last_update = {}
        
    def is_valid(self, key: str) -> bool:
        """Kiểm tra cache còn hợp lệ không"""
        if key not in self.last_update:
            return False
        return datetime.now() - self.last_update[key] < self.cache_duration
    
    def get(self, key: str) -> Optional[any]:
        """Lấy dữ liệu từ cache"""
        if self.is_valid(key):
            return self.cache.get(key)
        return None
    
    def set(self, key: str, value: any):
        """Lưu dữ liệu vào cache"""
        self.cache[key] = value
        self.last_update[key] = datetime.now()
    
    def clear(self, key: str = None):
        """Xóa cache"""
        if key:
            self.cache.pop(key, None)
            self.last_update.pop(key, None)
        else:
            self.cache.clear()
            self.last_update.clear()

class GeminiEconomicManager:
    """
    Quản lý kinh tế game bằng Gemini AI
    Thay thế AI local để cân bằng kinh tế thông qua cache data
    """
    
    def __init__(self, database: Database, api_key: str = None):
        self.db = database
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        self.cache = EconomicCache(cache_duration_minutes=30)
        
        # Gemini API endpoint
        self.gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={self.api_key}"
        
        # Economic thresholds
        self.economic_thresholds = {
            'inflation_critical': 0.15,      # 15% inflation = critical
            'inflation_warning': 0.08,       # 8% inflation = warning  
            'money_concentration_max': 0.7,  # 70% money in top 20% players
            'activity_low': 0.3,             # 30% activity = low
            'health_score_min': 0.4          # Below 40% = unhealthy
        }
        
        # Decision history
        self.decision_history = []
        self.last_analysis_time = None
        
    async def collect_economic_data(self, bot) -> GameEconomicData:
        """Thu thập dữ liệu kinh tế từ database"""
        try:
            logger.info("📊 Collecting economic data for Gemini analysis...")
            
            # Check cache first
            cached_data = self.cache.get('economic_data')
            if cached_data:
                logger.info("📊 Using cached economic data")
                return cached_data
            
            # Collect fresh data
            current_time = datetime.now()
            
            # Player statistics
            all_users = await self.db.get_all_users()
            total_players = len(all_users)
            
            # Active players (có hoạt động trong 24h)
            active_cutoff = current_time - timedelta(hours=24)
            active_players = sum(1 for user in all_users 
                               if user.get('last_seen', current_time) > active_cutoff)
            
            # Money statistics
            money_amounts = [user.get('money', 0) for user in all_users]
            total_money = sum(money_amounts)
            avg_money = total_money / total_players if total_players > 0 else 0
            
            # Money distribution
            money_distribution = self._calculate_money_distribution(money_amounts)
            median_money = self._calculate_median(money_amounts)
            
            # Weather data
            weather_type = 'sunny'  # Default
            weather_modifier = 1.0
            
            # Market activity (placeholder - would track actual sales)
            market_activity = await self._get_market_activity()
            
            # Economic health metrics
            inflation_rate = await self._calculate_inflation_rate()
            health_score = self._calculate_economic_health(
                money_distribution, inflation_rate, active_players, total_players
            )
            
            economic_data = GameEconomicData(
                timestamp=current_time,
                total_players=total_players,
                active_players_24h=active_players,
                total_money_circulation=total_money,
                average_money_per_player=avg_money,
                median_money_per_player=median_money,
                money_distribution=money_distribution,
                weather_type=weather_type,
                weather_modifier=weather_modifier,
                active_events=[],  # Would get from events cog
                market_activity=market_activity,
                inflation_rate=inflation_rate,
                economic_health_score=health_score
            )
            
            # Cache the data
            self.cache.set('economic_data', economic_data)
            logger.info(f"📊 Economic data collected: {total_players} players, {total_money:,} coins total")
            
            return economic_data
            
        except Exception as e:
            logger.error(f"Error collecting economic data: {e}")
            return self._get_default_economic_data()
    
    async def analyze_economy_with_gemini(self, economic_data: GameEconomicData) -> Optional[GeminiEconomicDecision]:
        """Phân tích kinh tế bằng Gemini AI"""
        try:
            if not self.api_key:
                logger.warning("⚠️ No Gemini API key, using mock decision")
                return self._get_mock_decision(economic_data)
            
            # Prepare data for Gemini
            analysis_prompt = self._create_gemini_prompt(economic_data)
            
            # Call Gemini API
            async with aiohttp.ClientSession() as session:
                payload = {
                    "contents": [{
                        "parts": [{"text": analysis_prompt}]
                    }]
                }
                
                async with session.post(self.gemini_url, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        gemini_response = result['candidates'][0]['content']['parts'][0]['text']
                        
                        # Parse Gemini response
                        decision = self._parse_gemini_response(gemini_response)
                        logger.info(f"🤖 Gemini decision: {decision.action_type} - {decision.reasoning}")
                        return decision
                    else:
                        logger.error(f"Gemini API error: {response.status}")
                        return self._get_mock_decision(economic_data)
            
        except Exception as e:
            logger.error(f"Error analyzing with Gemini: {e}")
            return self._get_mock_decision(economic_data)
    
    def _create_gemini_prompt(self, data: GameEconomicData) -> str:
        """Tạo prompt cho Gemini để phân tích kinh tế"""
        return f"""
Bạn là Economic Game Master của một game nông trại Discord. Phân tích dữ liệu kinh tế sau và đưa ra quyết định cân bằng:

DỮ LIỆU KINH TẾ:
- Tổng số người chơi: {data.total_players}
- Người chơi hoạt động 24h: {data.active_players_24h} ({data.active_players_24h/data.total_players*100:.1f}%)
- Tổng tiền trong game: {data.total_money_circulation:,} coins
- Tiền trung bình/người: {data.average_money_per_player:,.0f} coins
- Tiền trung vị: {data.median_money_per_player:,.0f} coins
- Phân phối tiền: {data.money_distribution}
- Tỷ lệ lạm phát: {data.inflation_rate:.1%}
- Điểm sức khỏe kinh tế: {data.economic_health_score:.1%}
- Thời tiết hiện tại: {data.weather_type} (modifier: {data.weather_modifier})

NGƯỠNG CẢNH BÁO:
- Lạm phát nguy hiểm: >15%
- Lạm phát cảnh báo: >8%
- Tập trung tiền tệ: >70% trong top 20%
- Hoạt động thấp: <30%
- Sức khỏe kinh tế tối thiểu: >40%

YÊU CẦU:
Đưa ra quyết định để cân bằng kinh tế. Trả lời theo format JSON:
{{
    "action_type": "weather_change|event_trigger|price_adjustment|no_action",
    "reasoning": "Giải thích tại sao chọn hành động này",
    "confidence": 0.85,
    "parameters": {{"specific_action": "sunny", "modifier": 1.2}},
    "expected_impact": "Tác động dự kiến",
    "duration_hours": 6,
    "priority": "low|medium|high|critical"
}}

Chỉ cần trả lời JSON, không cần giải thích thêm.
"""
    
    def _parse_gemini_response(self, response: str) -> GeminiEconomicDecision:
        """Parse phản hồi từ Gemini thành decision object"""
        try:
            # Extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                decision_data = json.loads(json_match.group())
                
                return GeminiEconomicDecision(
                    action_type=decision_data.get('action_type', 'no_action'),
                    reasoning=decision_data.get('reasoning', 'No reasoning provided'),
                    confidence=decision_data.get('confidence', 0.5),
                    parameters=decision_data.get('parameters', {}),
                    expected_impact=decision_data.get('expected_impact', 'Unknown impact'),
                    duration_hours=decision_data.get('duration_hours', 6),
                    priority=decision_data.get('priority', 'medium')
                )
            else:
                logger.error("No JSON found in Gemini response")
                return self._get_fallback_decision()
                
        except Exception as e:
            logger.error(f"Error parsing Gemini response: {e}")
            return self._get_fallback_decision()
    
    def _get_mock_decision(self, data: GameEconomicData) -> GeminiEconomicDecision:
        """Tạo quyết định mock khi không có Gemini API"""
        if data.economic_health_score < self.economic_thresholds['health_score_min']:
            return GeminiEconomicDecision(
                action_type="event_trigger",
                reasoning="Sức khỏe kinh tế thấp, cần event boost để kích thích hoạt động",
                confidence=0.8,
                parameters={"event_type": "money_boost", "multiplier": 1.5},
                expected_impact="Tăng tiền và hoạt động của người chơi",
                duration_hours=6,
                priority="high"
            )
        elif data.inflation_rate > self.economic_thresholds['inflation_warning']:
            return GeminiEconomicDecision(
                action_type="weather_change", 
                reasoning="Lạm phát cao, thay đổi thời tiết để điều chỉnh economy",
                confidence=0.7,
                parameters={"weather": "rainy", "modifier": 0.8},
                expected_impact="Giảm hiệu suất farming, kiểm soát lạm phát",
                duration_hours=4,
                priority="medium"
            )
        else:
            return GeminiEconomicDecision(
                action_type="no_action",
                reasoning="Kinh tế đang ổn định, không cần can thiệp",
                confidence=0.6,
                parameters={},
                expected_impact="Duy trì trạng thái hiện tại",
                duration_hours=0,
                priority="low"
            )
    
    def _get_fallback_decision(self) -> GeminiEconomicDecision:
        """Quyết định dự phòng khi có lỗi"""
        return GeminiEconomicDecision(
            action_type="no_action",
            reasoning="Có lỗi trong phân tích, duy trì trạng thái hiện tại",
            confidence=0.3,
            parameters={},
            expected_impact="Không thay đổi",
            duration_hours=0,
            priority="low"
        )
    
    def _calculate_money_distribution(self, money_amounts: List[int]) -> Dict[str, int]:
        """Tính phân phối tiền theo khoảng"""
        distribution = {"0-1k": 0, "1k-10k": 0, "10k-100k": 0, "100k+": 0}
        
        for amount in money_amounts:
            if amount < 1000:
                distribution["0-1k"] += 1
            elif amount < 10000:
                distribution["1k-10k"] += 1
            elif amount < 100000:
                distribution["10k-100k"] += 1
            else:
                distribution["100k+"] += 1
        
        return distribution
    
    def _calculate_median(self, values: List[int]) -> float:
        """Tính median"""
        if not values:
            return 0
        sorted_values = sorted(values)
        n = len(sorted_values)
        if n % 2 == 0:
            return (sorted_values[n//2-1] + sorted_values[n//2]) / 2
        return sorted_values[n//2]
    
    async def _get_market_activity(self) -> Dict[str, int]:
        """Lấy hoạt động thị trường (placeholder)"""
        # TODO: Implement actual market tracking
        return {
            "crop_sales_24h": 150,
            "total_transactions": 300,
            "average_transaction_value": 2500
        }
    
    async def _calculate_inflation_rate(self) -> float:
        """Tính tỷ lệ lạm phát (placeholder)"""
        # TODO: Implement actual inflation calculation based on price history
        return 0.05  # 5% default
    
    def _calculate_economic_health(self, distribution: Dict, inflation: float, 
                                 active: int, total: int) -> float:
        """Tính điểm sức khỏe kinh tế tổng hợp"""
        # Activity score (0-1)
        activity_score = active / total if total > 0 else 0
        
        # Distribution score (0-1) - better when more balanced
        total_dist = sum(distribution.values())
        if total_dist > 0:
            rich_ratio = distribution["100k+"] / total_dist
            distribution_score = 1 - min(rich_ratio, 0.7) / 0.7
        else:
            distribution_score = 0.5
        
        # Inflation score (0-1) - worse with high inflation
        inflation_score = max(0, 1 - inflation / 0.15)
        
        # Weighted average
        health_score = (
            activity_score * 0.4 +
            distribution_score * 0.3 + 
            inflation_score * 0.3
        )
        
        return health_score
    
    def _get_default_economic_data(self) -> GameEconomicData:
        """Dữ liệu mặc định khi có lỗi"""
        return GameEconomicData(
            timestamp=datetime.now(),
            total_players=10,
            active_players_24h=5,
            total_money_circulation=50000,
            average_money_per_player=5000,
            median_money_per_player=3000,
            money_distribution={"0-1k": 3, "1k-10k": 5, "10k-100k": 2, "100k+": 0},
            weather_type="sunny",
            weather_modifier=1.0,
            active_events=[],
            market_activity={"crop_sales_24h": 50, "total_transactions": 100, "average_transaction_value": 2000},
            inflation_rate=0.03,
            economic_health_score=0.6
        )
    
    async def execute_economic_decision(self, decision: GeminiEconomicDecision, bot) -> bool:
        """Thực hiện quyết định kinh tế"""
        try:
            if decision.action_type == "no_action":
                logger.info("🤖 Gemini Economic Decision: No action needed")
                return True
            
            success = False
            
            if decision.action_type == "weather_change":
                success = await self._execute_weather_change(decision, bot)
            elif decision.action_type == "event_trigger":
                success = await self._execute_event_trigger(decision, bot)
            elif decision.action_type == "price_adjustment":
                success = await self._execute_price_adjustment(decision, bot)
            
            # Record decision
            self.decision_history.append({
                'timestamp': datetime.now(),
                'decision': asdict(decision),
                'success': success
            })
            
            # Keep only last 50 decisions
            if len(self.decision_history) > 50:
                self.decision_history = self.decision_history[-50:]
            
            return success
            
        except Exception as e:
            logger.error(f"Error executing economic decision: {e}")
            return False
    
    async def _execute_weather_change(self, decision: GeminiEconomicDecision, bot) -> bool:
        """Thực hiện thay đổi thời tiết"""
        try:
 