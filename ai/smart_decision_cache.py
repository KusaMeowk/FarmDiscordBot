#!/usr/bin/env python3
"""
Smart Decision Cache - Hệ thống cache thông minh để tiết kiệm token Gemini
"""

import json
import os
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import aiofiles
from utils.enhanced_logging import get_bot_logger

logger = get_bot_logger()

@dataclass
class CachedDecision:
    """Quyết định được cache"""
    decision_id: str
    context_pattern: str  
    decision_data: Dict[str, Any]
    success_rate: float
    usage_count: int
    created_at: datetime
    last_used: datetime
    effectiveness_score: float

class SmartDecisionCache:
    """
    Cache thông minh cho quyết định Gemini
    Tiết kiệm token bằng cách tái sử dụng decisions cho context tương tự
    """
    
    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = cache_dir
        self.cache_file = os.path.join(cache_dir, "smart_decision_cache.json")
        
        # Cache storage
        self.cached_decisions: Dict[str, CachedDecision] = {}
        
        # Thống kê tiết kiệm
        self.cache_hits = 0
        self.cache_misses = 0
        self.tokens_saved = 0
        self.api_calls_saved = 0
        
        # Settings
        self.similarity_threshold = 0.8
        self.max_cache_age_days = 14
        self.min_success_rate = 0.6
        
        os.makedirs(cache_dir, exist_ok=True)
    
    async def initialize(self):
        """Khởi tạo cache system"""
        await self.load_cache_from_disk()
        await self.cleanup_old_entries()
        logger.info(f"💾 Smart Decision Cache initialized: {len(self.cached_decisions)} cached decisions")
    
    def create_context_pattern(self, economic_data: Dict, weather_data: Dict) -> str:
        """Tạo pattern từ context để matching"""
        # Simplified pattern cho easier matching
        pattern = {
            # Activity level (3 categories)
            'activity': self._get_activity_level(economic_data.get('activity_rate', 0)),
            
            # Economic health (3 categories) 
            'health': self._get_health_level(economic_data.get('economic_health_score', 0.5)),
            
            # Player size (3 categories)
            'size': self._get_size_level(economic_data.get('total_players', 0)),
            
            # Weather type
            'weather': weather_data.get('current_weather', 'sunny'),
            
            # Time period
            'time': self._get_time_period(),
            
            # Money distribution
            'distribution': self._get_distribution_level(economic_data.get('money_distribution', {}))
        }
        
        # Create pattern string
        pattern_str = f"{pattern['activity']}-{pattern['health']}-{pattern['size']}-{pattern['weather']}-{pattern['time']}-{pattern['distribution']}"
        return pattern_str
    
    def _get_activity_level(self, rate: float) -> str:
        """Phân loại mức độ hoạt động"""
        if rate < 0.3:
            return 'low'
        elif rate < 0.7:
            return 'medium'
        else:
            return 'high'
    
    def _get_health_level(self, score: float) -> str:
        """Phân loại tình trạng kinh tế"""
        if score < 0.4:
            return 'poor'
        elif score < 0.7:
            return 'fair'
        else:
            return 'good'
    
    def _get_size_level(self, count: int) -> str:
        """Phân loại quy mô người chơi"""
        if count < 50:
            return 'small'
        elif count < 200:
            return 'medium'
        else:
            return 'large'
    
    def _get_time_period(self) -> str:
        """Lấy khoảng thời gian trong ngày"""
        hour = datetime.now().hour
        if 6 <= hour < 12:
            return 'morning'
        elif 12 <= hour < 18:
            return 'afternoon'
        elif 18 <= hour < 22:
            return 'evening'
        else:
            return 'night'
    
    def _get_distribution_level(self, distribution: Dict) -> str:
        """Phân loại phân bổ tiền"""
        if not distribution:
            return 'balanced'
        
        total = sum(distribution.values())
        if total == 0:
            return 'balanced'
        
        wealthy_ratio = distribution.get('100k+', 0) / total
        if wealthy_ratio > 0.6:
            return 'concentrated'
        elif wealthy_ratio < 0.2:
            return 'distributed'
        else:
            return 'balanced'
    
    async def find_cached_decision(self, economic_data: Dict, weather_data: Dict) -> Optional[Dict]:
        """Tìm quyết định đã cache cho tình huống tương tự"""
        try:
            current_pattern = self.create_context_pattern(economic_data, weather_data)
            
            # Tìm exact match trước
            if current_pattern in self.cached_decisions:
                cached = self.cached_decisions[current_pattern]
                
                # Kiểm tra validity
                if self._is_decision_valid(cached):
                    return await self._use_cached_decision(cached, "exact_match")
            
            # Tìm similar pattern
            for pattern, cached in self.cached_decisions.items():
                if self._is_decision_valid(cached):
                    similarity = self._calculate_pattern_similarity(current_pattern, pattern)
                    if similarity >= self.similarity_threshold:
                        return await self._use_cached_decision(cached, "similar_match", similarity)
            
            # Cache miss
            self.cache_misses += 1
            logger.info(f"💾 Cache MISS: Pattern {current_pattern}")
            return None
            
        except Exception as e:
            logger.error(f"Error finding cached decision: {e}")
            return None
    
    def _is_decision_valid(self, cached: CachedDecision) -> bool:
        """Kiểm tra quyết định cache còn valid không"""
        # Check age
        age_days = (datetime.now() - cached.created_at).days
        if age_days > self.max_cache_age_days:
            return False
        
        # Check success rate
        if cached.success_rate < self.min_success_rate:
            return False
        
        return True
    
    async def _use_cached_decision(self, cached: CachedDecision, match_type: str, similarity: float = 1.0) -> Dict:
        """Sử dụng cached decision"""
        # Update usage stats
        cached.usage_count += 1
        cached.last_used = datetime.now()
        
        # Update global stats
        self.cache_hits += 1
        self.api_calls_saved += 1
        self.tokens_saved += self._estimate_tokens_saved(cached.decision_data)
        
        logger.info(f"💾 Cache HIT ({match_type}): Pattern {cached.context_pattern} "
                   f"(similarity: {similarity:.2f}, usage: {cached.usage_count})")
        
        return cached.decision_data.copy()
    
    def _estimate_tokens_saved(self, decision_data: Dict) -> int:
        """Ước tính số token đã tiết kiệm"""
        # Rough estimation based on decision complexity
        base_tokens = 300  # Base prompt tokens
        
        if decision_data.get('action_type') == 'EVENT_TRIGGER':
            return base_tokens + 200  # Complex event generation
        elif decision_data.get('action_type') == 'WEATHER_CHANGE':
            return base_tokens + 100  # Weather analysis
        else:
            return base_tokens + 50   # Simple decisions
    
    def _calculate_pattern_similarity(self, pattern1: str, pattern2: str) -> float:
        """Tính độ tương tự giữa 2 patterns"""
        parts1 = pattern1.split('-')
        parts2 = pattern2.split('-')
        
        if len(parts1) != len(parts2):
            return 0.0
        
        # Weight cho từng phần
        weights = [0.25, 0.25, 0.15, 0.20, 0.10, 0.05]  # activity, health, size, weather, time, distribution
        
        similarity = 0.0
        for i, (p1, p2) in enumerate(zip(parts1, parts2)):
            if i < len(weights):
                if p1 == p2:
                    similarity += weights[i]
                elif self._is_similar_category(p1, p2, i):
                    similarity += weights[i] * 0.5  # Partial match
        
        return similarity
    
    def _is_similar_category(self, val1: str, val2: str, category_index: int) -> bool:
        """Kiểm tra categories có tương tự không"""
        similar_groups = {
            0: [['low', 'medium'], ['medium', 'high']],  # activity
            1: [['poor', 'fair'], ['fair', 'good']],     # health
            2: [['small', 'medium'], ['medium', 'large']], # size
            5: [['concentrated', 'balanced'], ['balanced', 'distributed']] # distribution
        }
        
        if category_index in similar_groups:
            for group in similar_groups[category_index]:
                if val1 in group and val2 in group:
                    return True
        
        return False
    
    async def cache_decision(self, economic_data: Dict, weather_data: Dict, 
                           decision_data: Dict, effectiveness_score: float = 0.8):
        """Cache quyết định mới"""
        try:
            pattern = self.create_context_pattern(economic_data, weather_data)
            decision_id = f"{pattern}_{int(datetime.now().timestamp())}"
            
            cached_decision = CachedDecision(
                decision_id=decision_id,
                context_pattern=pattern,
                decision_data=decision_data.copy(),
                success_rate=effectiveness_score,
                usage_count=1,
                created_at=datetime.now(),
                last_used=datetime.now(),
                effectiveness_score=effectiveness_score
            )
            
            # Store in cache
            self.cached_decisions[pattern] = cached_decision
            
            # Auto save every 10 new decisions
            if len(self.cached_decisions) % 10 == 0:
                await self.save_cache_to_disk()
            
            logger.info(f"💾 Cached new decision: {pattern} (effectiveness: {effectiveness_score:.2f})")
            
        except Exception as e:
            logger.error(f"Error caching decision: {e}")
    
    async def update_decision_effectiveness(self, pattern: str, new_effectiveness: float):
        """Cập nhật hiệu quả của decision"""
        if pattern in self.cached_decisions:
            cached = self.cached_decisions[pattern]
            
            # Weighted average
            old_weight = 0.7
            new_weight = 0.3
            
            cached.effectiveness_score = (
                old_weight * cached.effectiveness_score + 
                new_weight * new_effectiveness
            )
            
            # Update success rate
            cached.success_rate = (
                (cached.success_rate * (cached.usage_count - 1) + new_effectiveness) /
                cached.usage_count
            )
            
            logger.info(f"💾 Updated effectiveness: {pattern} -> {new_effectiveness:.2f}")
    
    def get_cache_statistics(self) -> Dict[str, Any]:
        """Lấy thống kê cache"""
        total_requests = self.cache_hits + self.cache_misses
        hit_rate = self.cache_hits / total_requests if total_requests > 0 else 0
        
        # Cost savings (rough estimate: $0.002 per 1k tokens)
        cost_saved = (self.tokens_saved / 1000) * 0.002
        
        return {
            'total_cached_decisions': len(self.cached_decisions),
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'hit_rate_percent': round(hit_rate * 100, 1),
            'api_calls_saved': self.api_calls_saved,
            'tokens_saved': self.tokens_saved,
            'estimated_cost_saved_usd': round(cost_saved, 4),
            'average_effectiveness': self._calculate_average_effectiveness()
        }
    
    def _calculate_average_effectiveness(self) -> float:
        """Tính hiệu quả trung bình của cache"""
        if not self.cached_decisions:
            return 0.0
        
        total_effectiveness = sum(d.effectiveness_score for d in self.cached_decisions.values())
        return round(total_effectiveness / len(self.cached_decisions), 3)
    
    async def get_top_patterns(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Lấy top patterns được sử dụng nhiều nhất"""
        sorted_decisions = sorted(
            self.cached_decisions.values(),
            key=lambda x: (x.usage_count, x.effectiveness_score),
            reverse=True
        )
        
        top_patterns = []
        for decision in sorted_decisions[:limit]:
            top_patterns.append({
                'pattern': decision.context_pattern,
                'action_type': decision.decision_data.get('action_type', 'unknown'),
                'usage_count': decision.usage_count,
                'effectiveness_score': decision.effectiveness_score,
                'success_rate': decision.success_rate,
                'age_days': (datetime.now() - decision.created_at).days
            })
        
        return top_patterns
    
    async def cleanup_old_entries(self):
        """Dọn dẹp entries cũ hoặc không hiệu quả"""
        try:
            current_time = datetime.now()
            to_remove = []
            
            for pattern, cached in self.cached_decisions.items():
                age_days = (current_time - cached.created_at).days
                
                # Remove if too old or low success rate
                if (age_days > self.max_cache_age_days or 
                    cached.success_rate < self.min_success_rate):
                    to_remove.append(pattern)
            
            for pattern in to_remove:
                del self.cached_decisions[pattern]
            
            if to_remove:
                logger.info(f"💾 Cleaned up {len(to_remove)} old/ineffective cached decisions")
                await self.save_cache_to_disk()
                
        except Exception as e:
            logger.error(f"Error cleaning up cache: {e}")
    
    async def save_cache_to_disk(self):
        """Lưu cache xuống disk"""
        try:
            cache_data = {
                'cached_decisions': {},
                'statistics': {
                    'cache_hits': self.cache_hits,
                    'cache_misses': self.cache_misses,
                    'tokens_saved': self.tokens_saved,
                    'api_calls_saved': self.api_calls_saved
                },
                'settings': {
                    'similarity_threshold': self.similarity_threshold,
                    'max_cache_age_days': self.max_cache_age_days,
                    'min_success_rate': self.min_success_rate
                },
                'last_save': datetime.now().isoformat()
            }
            
            # Serialize decisions
            for pattern, decision in self.cached_decisions.items():
                cache_data['cached_decisions'][pattern] = {
                    'decision_id': decision.decision_id,
                    'context_pattern': decision.context_pattern,
                    'decision_data': decision.decision_data,
                    'success_rate': decision.success_rate,
                    'usage_count': decision.usage_count,
                    'created_at': decision.created_at.isoformat(),
                    'last_used': decision.last_used.isoformat(),
                    'effectiveness_score': decision.effectiveness_score
                }
            
            async with aiofiles.open(self.cache_file, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(cache_data, ensure_ascii=False, indent=2))
            
            logger.info(f"💾 Cache saved: {len(self.cached_decisions)} decisions")
            
        except Exception as e:
            logger.error(f"Error saving cache: {e}")
    
    async def load_cache_from_disk(self):
        """Load cache từ disk"""
        try:
            if not os.path.exists(self.cache_file):
                return
            
            async with aiofiles.open(self.cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.loads(await f.read())
            
            # Load decisions
            for pattern, data in cache_data.get('cached_decisions', {}).items():
                self.cached_decisions[pattern] = CachedDecision(
                    decision_id=data['decision_id'],
                    context_pattern=data['context_pattern'],
                    decision_data=data['decision_data'],
                    success_rate=data['success_rate'],
                    usage_count=data['usage_count'],
                    created_at=datetime.fromisoformat(data['created_at']),
                    last_used=datetime.fromisoformat(data['last_used']),
                    effectiveness_score=data['effectiveness_score']
                )
            
            # Load statistics
            stats = cache_data.get('statistics', {})
            self.cache_hits = stats.get('cache_hits', 0)
            self.cache_misses = stats.get('cache_misses', 0)
            self.tokens_saved = stats.get('tokens_saved', 0)
            self.api_calls_saved = stats.get('api_calls_saved', 0)
            
            # Load settings
            settings = cache_data.get('settings', {})
            self.similarity_threshold = settings.get('similarity_threshold', 0.8)
            
            logger.info(f"💾 Cache loaded: {len(self.cached_decisions)} decisions, "
                       f"{self.tokens_saved} tokens saved")
            
        except Exception as e:
            logger.error(f"Error loading cache: {e}")
    
    async def export_cache_report(self) -> str:
        """Export báo cáo chi tiết"""
        try:
            report = {
                'cache_performance': self.get_cache_statistics(),
                'top_patterns': await self.get_top_patterns(15),
                'pattern_analysis': self._analyze_patterns(),
                'export_timestamp': datetime.now().isoformat()
            }
            
            report_file = os.path.join(
                self.cache_dir, 
                f"cache_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            
            async with aiofiles.open(report_file, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(report, ensure_ascii=False, indent=2))
            
            logger.info(f"💾 Cache report exported: {report_file}")
            return report_file
            
        except Exception as e:
            logger.error(f"Error exporting cache report: {e}")
            return ""
    
    def _analyze_patterns(self) -> Dict[str, Any]:
        """Phân tích patterns trong cache"""
        pattern_stats = {}
        
        for decision in self.cached_decisions.values():
            parts = decision.context_pattern.split('-')
            if len(parts) >= 4:
                activity, health, size, weather = parts[:4]
                
                key = f"{activity}-{health}-{weather}"
                if key not in pattern_stats:
                    pattern_stats[key] = {
                        'count': 0,
                        'total_usage': 0,
                        'avg_effectiveness': 0,
                        'common_actions': {}
                    }
                
                pattern_stats[key]['count'] += 1
                pattern_stats[key]['total_usage'] += decision.usage_count
                pattern_stats[key]['avg_effectiveness'] += decision.effectiveness_score
                
                action = decision.decision_data.get('action_type', 'unknown')
                pattern_stats[key]['common_actions'][action] = pattern_stats[key]['common_actions'].get(action, 0) + 1
        
        # Calculate averages
        for stats in pattern_stats.values():
            if stats['count'] > 0:
                stats['avg_effectiveness'] /= stats['count']
                stats['avg_effectiveness'] = round(stats['avg_effectiveness'], 3)
        
        return pattern_stats 