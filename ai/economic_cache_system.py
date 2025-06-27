#!/usr/bin/env python3
"""
Economic Cache System - Hệ thống cache nâng cao cho Gemini Economic Manager
"""

import asyncio
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import aiofiles
from utils.enhanced_logging import get_bot_logger

logger = get_bot_logger()

@dataclass
class EconomicSnapshot:
    """Snapshot dữ liệu kinh tế tại một thời điểm"""
    timestamp: datetime
    total_players: int
    active_players_24h: int
    total_money_circulation: int
    average_money_per_player: float
    median_money_per_player: float
    money_distribution: Dict[str, int]
    top_10_percent_money_share: float
    inflation_rate: float
    economic_health_score: float

@dataclass 
class WeatherSnapshot:
    """Snapshot dữ liệu thời tiết"""
    timestamp: datetime
    current_weather: str
    weather_modifier: float
    temperature: float
    humidity: float
    real_weather_source: str
    ai_predicted_weather: str
    prediction_confidence: float

@dataclass
class PlayerActivitySnapshot:
    """Snapshot hoạt động người chơi"""
    timestamp: datetime
    total_commands_24h: int
    unique_active_users_24h: int
    farm_actions_24h: int
    market_transactions_24h: int
    new_players_24h: int
    retention_rate_7d: float
    average_session_duration: float

@dataclass
class MarketSnapshot:
    """Snapshot dữ liệu thị trường"""
    timestamp: datetime
    crop_sales_24h: Dict[str, int]
    total_crop_value_traded: int
    most_popular_crops: List[str]
    price_volatility: Dict[str, float]
    market_balance_score: float

class EconomicCacheSystem:
    """
    Hệ thống cache nâng cao cho dữ liệu kinh tế game
    Lưu trữ và quản lý snapshots để Gemini phân tích
    """
    
    def __init__(self, cache_dir: str = "cache", max_snapshots: int = 168):  # 7 days hourly
        self.cache_dir = cache_dir
        self.max_snapshots = max_snapshots
        
        # Cache storage
        self.economic_cache: List[EconomicSnapshot] = []
        self.weather_cache: List[WeatherSnapshot] = []
        self.activity_cache: List[PlayerActivitySnapshot] = []
        self.market_cache: List[MarketSnapshot] = []
        
        # Cache settings
        self.cache_intervals = {
            'economic': timedelta(hours=1),
            'weather': timedelta(minutes=15),
            'activity': timedelta(hours=1),
            'market': timedelta(hours=2)
        }
        
        # Last update tracking
        self.last_updates = {
            'economic': None,
            'weather': None, 
            'activity': None,
            'market': None
        }
        
        # Create cache directory
        os.makedirs(cache_dir, exist_ok=True)
        
    async def initialize(self):
        """Khởi tạo cache system và load dữ liệu cũ"""
        try:
            await self.load_cache_from_disk()
            logger.info("📊 Economic Cache System initialized")
        except Exception as e:
            logger.error(f"Error initializing cache system: {e}")
    
    async def update_economic_snapshot(self, database) -> EconomicSnapshot:
        """Cập nhật snapshot dữ liệu kinh tế"""
        try:
            current_time = datetime.now()
            
            # Skip if too soon since last update
            if (self.last_updates['economic'] and 
                current_time - self.last_updates['economic'] < self.cache_intervals['economic']):
                return self.economic_cache[-1] if self.economic_cache else None
            
            # Collect economic data
            all_users = await database.get_all_users()
            
            # Basic statistics
            total_players = len(all_users)
            active_cutoff = current_time - timedelta(hours=24)
            active_players = sum(1 for user in all_users 
                               if user.get('last_seen', current_time) > active_cutoff)
            
            # Money analysis
            money_amounts = [user.get('money', 0) for user in all_users]
            total_money = sum(money_amounts)
            avg_money = total_money / total_players if total_players > 0 else 0
            median_money = self._calculate_median(money_amounts)
            
            # Money distribution analysis
            money_distribution = self._analyze_money_distribution(money_amounts)
            top_10_share = self._calculate_top_percent_share(money_amounts, 0.1)
            
            # Economic health metrics
            inflation_rate = await self._calculate_inflation_rate()
            health_score = self._calculate_economic_health_score(
                money_distribution, inflation_rate, active_players, total_players
            )
            
            snapshot = EconomicSnapshot(
                timestamp=current_time,
                total_players=total_players,
                active_players_24h=active_players,
                total_money_circulation=total_money,
                average_money_per_player=avg_money,
                median_money_per_player=median_money,
                money_distribution=money_distribution,
                top_10_percent_money_share=top_10_share,
                inflation_rate=inflation_rate,
                economic_health_score=health_score
            )
            
            # Add to cache
            self.economic_cache.append(snapshot)
            self._trim_cache(self.economic_cache)
            self.last_updates['economic'] = current_time
            
            logger.info(f"📊 Economic snapshot updated: {total_players} players, Health: {health_score:.2f}")
            return snapshot
            
        except Exception as e:
            logger.error(f"Error updating economic snapshot: {e}")
            return None
    
    async def update_weather_snapshot(self, weather_data: Dict) -> WeatherSnapshot:
        """Cập nhật snapshot dữ liệu thời tiết"""
        try:
            current_time = datetime.now()
            
            # Skip if too soon
            if (self.last_updates['weather'] and 
                current_time - self.last_updates['weather'] < self.cache_intervals['weather']):
                return self.weather_cache[-1] if self.weather_cache else None
            
            snapshot = WeatherSnapshot(
                timestamp=current_time,
                current_weather=weather_data.get('weather', 'sunny'),
                weather_modifier=weather_data.get('modifier', 1.0),
                temperature=weather_data.get('temperature', 25.0),
                humidity=weather_data.get('humidity', 60.0),
                real_weather_source=weather_data.get('source', 'api'),
                ai_predicted_weather=weather_data.get('ai_prediction', 'sunny'),
                prediction_confidence=weather_data.get('confidence', 0.8)
            )
            
            self.weather_cache.append(snapshot)
            self._trim_cache(self.weather_cache)
            self.last_updates['weather'] = current_time
            
            return snapshot
            
        except Exception as e:
            logger.error(f"Error updating weather snapshot: {e}")
            return None
    
    async def update_activity_snapshot(self, database) -> PlayerActivitySnapshot:
        """Cập nhật snapshot hoạt động người chơi"""
        try:
            current_time = datetime.now()
            
            # Skip if too soon
            if (self.last_updates['activity'] and 
                current_time - self.last_updates['activity'] < self.cache_intervals['activity']):
                return self.activity_cache[-1] if self.activity_cache else None
            
            # Get activity data (would need to track these in database)
            total_commands = await self._get_command_count_24h(database)
            unique_users = await self._get_unique_active_users_24h(database)
            farm_actions = await self._get_farm_actions_24h(database)
            market_transactions = await self._get_market_transactions_24h(database)
            new_players = await self._get_new_players_24h(database)
            retention_rate = await self._calculate_retention_rate_7d(database)
            avg_session = await self._calculate_average_session_duration(database)
            
            snapshot = PlayerActivitySnapshot(
                timestamp=current_time,
                total_commands_24h=total_commands,
                unique_active_users_24h=unique_users,
                farm_actions_24h=farm_actions,
                market_transactions_24h=market_transactions,
                new_players_24h=new_players,
                retention_rate_7d=retention_rate,
                average_session_duration=avg_session
            )
            
            self.activity_cache.append(snapshot)
            self._trim_cache(self.activity_cache)
            self.last_updates['activity'] = current_time
            
            return snapshot
            
        except Exception as e:
            logger.error(f"Error updating activity snapshot: {e}")
            return None
    
    async def update_market_snapshot(self, database) -> MarketSnapshot:
        """Cập nhật snapshot dữ liệu thị trường"""
        try:
            current_time = datetime.now()
            
            # Skip if too soon
            if (self.last_updates['market'] and 
                current_time - self.last_updates['market'] < self.cache_intervals['market']):
                return self.market_cache[-1] if self.market_cache else None
            
            # Market analysis
            crop_sales = await self._get_crop_sales_24h(database)
            total_value = sum(crop_sales.values())
            popular_crops = sorted(crop_sales.keys(), key=lambda x: crop_sales[x], reverse=True)[:5]
            volatility = await self._calculate_price_volatility(database)
            balance_score = self._calculate_market_balance_score(crop_sales, volatility)
            
            snapshot = MarketSnapshot(
                timestamp=current_time,
                crop_sales_24h=crop_sales,
                total_crop_value_traded=total_value,
                most_popular_crops=popular_crops,
                price_volatility=volatility,
                market_balance_score=balance_score
            )
            
            self.market_cache.append(snapshot)
            self._trim_cache(self.market_cache)
            self.last_updates['market'] = current_time
            
            return snapshot
            
        except Exception as e:
            logger.error(f"Error updating market snapshot: {e}")
            return None
    
    def get_economic_trends(self, hours: int = 24) -> Dict[str, Any]:
        """Phân tích xu hướng kinh tế trong X giờ qua"""
        if not self.economic_cache:
            return {}
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_snapshots = [s for s in self.economic_cache if s.timestamp >= cutoff_time]
        
        if len(recent_snapshots) < 2:
            return {}
        
        trends = {
            'player_growth': self._calculate_trend([s.total_players for s in recent_snapshots]),
            'activity_trend': self._calculate_trend([s.active_players_24h for s in recent_snapshots]),
            'money_inflation': self._calculate_trend([s.inflation_rate for s in recent_snapshots]),
            'health_trend': self._calculate_trend([s.economic_health_score for s in recent_snapshots]),
            'money_concentration_trend': self._calculate_trend([s.top_10_percent_money_share for s in recent_snapshots])
        }
        
        return trends
    
    def get_gemini_analysis_data(self) -> Dict[str, Any]:
        """Chuẩn bị dữ liệu cho Gemini phân tích"""
        current_time = datetime.now()
        
        # Get latest snapshots
        latest_economic = self.economic_cache[-1] if self.economic_cache else None
        latest_weather = self.weather_cache[-1] if self.weather_cache else None
        latest_activity = self.activity_cache[-1] if self.activity_cache else None
        latest_market = self.market_cache[-1] if self.market_cache else None
        
        # Get trends
        trends_24h = self.get_economic_trends(24)
        trends_7d = self.get_economic_trends(168)
        
        return {
            'timestamp': current_time.isoformat(),
            'current_state': {
                'economic': asdict(latest_economic) if latest_economic else {},
                'weather': asdict(latest_weather) if latest_weather else {},
                'activity': asdict(latest_activity) if latest_activity else {},
                'market': asdict(latest_market) if latest_market else {}
            },
            'trends': {
                '24h': trends_24h,
                '7d': trends_7d
            },
            'alerts': self._generate_alerts(),
            'cache_health': {
                'economic_snapshots': len(self.economic_cache),
                'weather_snapshots': len(self.weather_cache),
                'activity_snapshots': len(self.activity_cache),
                'market_snapshots': len(self.market_cache),
                'oldest_snapshot': min([
                    self.economic_cache[0].timestamp if self.economic_cache else current_time,
                    self.weather_cache[0].timestamp if self.weather_cache else current_time,
                    self.activity_cache[0].timestamp if self.activity_cache else current_time,
                    self.market_cache[0].timestamp if self.market_cache else current_time
                ]).isoformat()
            }
        }
    
    # Utility methods
    def _trim_cache(self, cache_list: List):
        """Giới hạn số lượng snapshots trong cache"""
        if len(cache_list) > self.max_snapshots:
            cache_list[:] = cache_list[-self.max_snapshots:]
    
    def _calculate_median(self, values: List[float]) -> float:
        """Tính median"""
        if not values:
            return 0.0
        sorted_values = sorted(values)
        n = len(sorted_values)
        if n % 2 == 0:
            return (sorted_values[n//2-1] + sorted_values[n//2]) / 2
        return sorted_values[n//2]
    
    def _analyze_money_distribution(self, money_amounts: List[int]) -> Dict[str, int]:
        """Phân tích phân bổ tiền"""
        distribution = {
            '0-1k': 0,
            '1k-10k': 0, 
            '10k-100k': 0,
            '100k+': 0
        }
        
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
    
    def _calculate_top_percent_share(self, money_amounts: List[int], percent: float) -> float:
        """Tính phần trăm tiền mà top X% player sở hữu"""
        if not money_amounts:
            return 0.0
        
        sorted_amounts = sorted(money_amounts, reverse=True)
        top_count = max(1, int(len(sorted_amounts) * percent))
        top_money = sum(sorted_amounts[:top_count])
        total_money = sum(money_amounts)
        
        return top_money / total_money if total_money > 0 else 0.0
    
    async def _calculate_inflation_rate(self) -> float:
        """Tính tỷ lệ lạm phát (placeholder)"""
        # Would compare current prices vs historical prices
        return 0.05  # 5% placeholder
    
    def _calculate_economic_health_score(self, distribution: Dict, inflation: float, 
                                       active: int, total: int) -> float:
        """Tính điểm health kinh tế (0-1)"""
        if total == 0:
            return 0.0
        
        # Activity factor (0-1)
        activity_factor = min(1.0, active / total)
        
        # Inflation factor (1 = good, 0 = bad)
        inflation_factor = max(0.0, 1.0 - (inflation / 0.2))  # Bad if >20%
        
        # Distribution factor (more even = better)
        total_players = sum(distribution.values())
        if total_players > 0:
            # Penalize extreme concentration
            wealthy_percent = distribution.get('100k+', 0) / total_players
            distribution_factor = max(0.0, 1.0 - (wealthy_percent / 0.5))  # Bad if >50% wealthy
        else:
            distribution_factor = 0.5
        
        # Weighted average
        health_score = (activity_factor * 0.4 + inflation_factor * 0.3 + distribution_factor * 0.3)
        return round(health_score, 3)
    
    def _calculate_trend(self, values: List[float]) -> Dict[str, float]:
        """Tính xu hướng từ list values"""
        if len(values) < 2:
            return {'direction': 0, 'change_percent': 0, 'volatility': 0}
        
        # Simple trend calculation
        start_val = values[0] if values[0] != 0 else 0.001
        end_val = values[-1]
        
        change_percent = ((end_val - start_val) / start_val) * 100 if start_val != 0 else 0
        direction = 1 if change_percent > 0 else -1 if change_percent < 0 else 0
        
        # Calculate volatility (standard deviation)
        if len(values) > 1:
            mean_val = sum(values) / len(values)
            variance = sum((x - mean_val) ** 2 for x in values) / len(values)
            volatility = variance ** 0.5
        else:
            volatility = 0
        
        return {
            'direction': direction,
            'change_percent': round(change_percent, 2),
            'volatility': round(volatility, 2)
        }
    
    def _generate_alerts(self) -> List[Dict[str, Any]]:
        """Tạo alerts cho tình trạng bất thường"""
        alerts = []
        
        if not self.economic_cache:
            return alerts
        
        latest = self.economic_cache[-1]
        
        # Check inflation
        if latest.inflation_rate > 0.15:
            alerts.append({
                'type': 'critical',
                'message': f'Lạm phát cao: {latest.inflation_rate:.1%}',
                'recommendation': 'Cần giảm nguồn cung tiền'
            })
        
        # Check activity
        activity_rate = latest.active_players_24h / latest.total_players if latest.total_players > 0 else 0
        if activity_rate < 0.3:
            alerts.append({
                'type': 'warning', 
                'message': f'Hoạt động thấp: {activity_rate:.1%}',
                'recommendation': 'Cần sự kiện kích thích hoạt động'
            })
        
        # Check money concentration
        if latest.top_10_percent_money_share > 0.7:
            alerts.append({
                'type': 'warning',
                'message': f'Tập trung tiền: Top 10% có {latest.top_10_percent_money_share:.1%}',
                'recommendation': 'Cần tái phân phối'
            })
        
        return alerts
    
    # Placeholder methods for database queries (implement based on your schema)
    async def _get_command_count_24h(self, database) -> int:
        return 0  # Implement command logging
    
    async def _get_unique_active_users_24h(self, database) -> int:
        return 0  # Implement activity tracking
    
    async def _get_farm_actions_24h(self, database) -> int:
        return 0  # Track planting/harvesting
    
    async def _get_market_transactions_24h(self, database) -> int:
        return 0  # Track buying/selling
    
    async def _get_new_players_24h(self, database) -> int:
        return 0  # Track registrations
    
    async def _calculate_retention_rate_7d(self, database) -> float:
        return 0.0  # Track player retention
    
    async def _calculate_average_session_duration(self, database) -> float:
        return 0.0  # Track session times
    
    async def _get_crop_sales_24h(self, database) -> Dict[str, int]:
        return {}  # Track crop sales
    
    async def _calculate_price_volatility(self, database) -> Dict[str, float]:
        return {}  # Track price changes
    
    def _calculate_market_balance_score(self, sales: Dict, volatility: Dict) -> float:
        return 0.5  # Calculate market health
    
    async def save_cache_to_disk(self):
        """Lưu cache xuống disk"""
        try:
            cache_data = {
                'economic': [asdict(s) for s in self.economic_cache],
                'weather': [asdict(s) for s in self.weather_cache],
                'activity': [asdict(s) for s in self.activity_cache],
                'market': [asdict(s) for s in self.market_cache],
                'last_updates': {k: v.isoformat() if v else None for k, v in self.last_updates.items()}
            }
            
            cache_file = os.path.join(self.cache_dir, 'economic_cache.json')
            async with aiofiles.open(cache_file, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(cache_data, default=str, ensure_ascii=False, indent=2))
                
        except Exception as e:
            logger.error(f"Error saving cache to disk: {e}")
    
    async def load_cache_from_disk(self):
        """Load cache từ disk"""
        try:
            cache_file = os.path.join(self.cache_dir, 'economic_cache.json')
            if not os.path.exists(cache_file):
                return
            
            async with aiofiles.open(cache_file, 'r', encoding='utf-8') as f:
                content = await f.read()
                cache_data = json.loads(content)
            
            # Restore caches (implement deserialization)
            # This would need proper datetime parsing
            logger.info("📊 Cache loaded from disk")
            
        except Exception as e:
            logger.error(f"Error loading cache from disk: {e}") 