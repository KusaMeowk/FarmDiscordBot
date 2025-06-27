#!/usr/bin/env python3
"""
Decision Cache Manager - Tiết kiệm token bằng cách cache và tái sử dụng quyết định
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
    context_hash: str
    decision_data: Dict[str, Any]
    success_rate: float
    usage_count: int
    created_at: datetime
    last_used: datetime
    effectiveness_score: float

class DecisionCacheManager:
    """Quản lý cache quyết định để tiết kiệm token"""
    
    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = cache_dir
        self.cache_file = os.path.join(cache_dir, "decision_cache.json")
        self.cached_decisions: Dict[str, CachedDecision] = {}
        
        # Thống kê
        self.cache_hits = 0
        self.cache_misses = 0
        self.tokens_saved = 0
        
        os.makedirs(cache_dir, exist_ok=True)
    
    def create_context_hash(self, economic_data: Dict, weather_data: Dict) -> str:
        """Tạo hash cho context tương tự"""
        # Làm tròn các giá trị để tạo pattern
        simplified_context = {
            'activity_level': self._categorize_activity(economic_data.get('activity_rate', 0)),
            'health_score': self._categorize_health(economic_data.get('economic_health_score', 0.5)),
            'player_count': self._categorize_players(economic_data.get('total_players', 0)),
            'weather': weather_data.get('current_weather', 'sunny'),
            'time_period': self._get_time_period()
        }
        
        context_str = json.dumps(simplified_context, sort_keys=True)
        return hashlib.md5(context_str.encode()).hexdigest()[:12]
    
    def _categorize_activity(self, rate: float) -> str:
        if rate < 0.3: return 'low'
        elif rate < 0.7: return 'medium'
        else: return 'high'
    
    def _categorize_health(self, score: float) -> str:
        if score < 0.4: return 'poor'
        elif score < 0.7: return 'fair'
        else: return 'good'
    
    def _categorize_players(self, count: int) -> str:
        if count < 50: return 'small'
        elif count < 200: return 'medium'
        else: return 'large'
    
    def _get_time_period(self) -> str:
        hour = datetime.now().hour
        if 6 <= hour < 12: return 'morning'
        elif 12 <= hour < 18: return 'afternoon'
        elif 18 <= hour < 22: return 'evening'
        else: return 'night'
    
    async def find_cached_decision(self, economic_data: Dict, weather_data: Dict) -> Optional[Dict]:
        """Tìm quyết định đã cache cho context tương tự"""
        context_hash = self.create_context_hash(economic_data, weather_data)
        
        if context_hash in self.cached_decisions:
            cached = self.cached_decisions[context_hash]
            
            # Kiểm tra độ cũ (không quá 7 ngày)
            age_days = (datetime.now() - cached.created_at).days
            if age_days > 7:
                return None
            
            # Kiểm tra success rate
            if cached.success_rate < 0.6:
                return None
            
            # Update usage
            cached.usage_count += 1
            cached.last_used = datetime.now()
            
            self.cache_hits += 1
            self.tokens_saved += 400  # Ước tính token tiết kiệm
            
            logger.info(f"📋 Cache HIT: Reusing decision for {context_hash}")
            return cached.decision_data
        
        self.cache_misses += 1
        return None
    
    async def cache_decision(self, economic_data: Dict, weather_data: Dict, 
                           decision_data: Dict, effectiveness: float = 0.8):
        """Lưu quyết định vào cache"""
        context_hash = self.create_context_hash(economic_data, weather_data)
        decision_id = f"{context_hash}_{int(datetime.now().timestamp())}"
        
        cached_decision = CachedDecision(
            decision_id=decision_id,
            context_hash=context_hash,
            decision_data=decision_data.copy(),
            success_rate=effectiveness,
            usage_count=1,
            created_at=datetime.now(),
            last_used=datetime.now(),
            effectiveness_score=effectiveness
        )
        
        self.cached_decisions[context_hash] = cached_decision
        await self.save_cache()
        
        logger.info(f"📋 Cached decision: {context_hash}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Lấy thống kê cache"""
        total = self.cache_hits + self.cache_misses
        hit_rate = self.cache_hits / total if total > 0 else 0
        
        return {
            'total_decisions': len(self.cached_decisions),
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'hit_rate': f"{hit_rate:.1%}",
            'tokens_saved': self.tokens_saved,
            'estimated_cost_saved': f"${self.tokens_saved * 0.002:.2f}"  # Rough estimate
        }
    
    async def save_cache(self):
        """Lưu cache xuống disk"""
        try:
            cache_data = {
                'decisions': {},
                'stats': {
                    'cache_hits': self.cache_hits,
                    'cache_misses': self.cache_misses,
                    'tokens_saved': self.tokens_saved
                }
            }
            
            for context_hash, decision in self.cached_decisions.items():
                cache_data['decisions'][context_hash] = {
                    'decision_id': decision.decision_id,
                    'decision_data': decision.decision_data,
                    'success_rate': decision.success_rate,
                    'usage_count': decision.usage_count,
                    'created_at': decision.created_at.isoformat(),
                    'last_used': decision.last_used.isoformat(),
                    'effectiveness_score': decision.effectiveness_score
                }
            
            async with aiofiles.open(self.cache_file, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(cache_data, indent=2, ensure_ascii=False))
                
        except Exception as e:
            logger.error(f"Error saving cache: {e}")
    
    async def load_cache(self):
        """Load cache từ disk"""
        try:
            if not os.path.exists(self.cache_file):
                return
            
            async with aiofiles.open(self.cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.loads(await f.read())
            
            # Load decisions
            for context_hash, data in cache_data.get('decisions', {}).items():
                self.cached_decisions[context_hash] = CachedDecision(
                    decision_id=data['decision_id'],
                    context_hash=context_hash,
                    decision_data=data['decision_data'],
                    success_rate=data['success_rate'],
                    usage_count=data['usage_count'],
                    created_at=datetime.fromisoformat(data['created_at']),
                    last_used=datetime.fromisoformat(data['last_used']),
                    effectiveness_score=data['effectiveness_score']
                )
            
            # Load stats
            stats = cache_data.get('stats', {})
            self.cache_hits = stats.get('cache_hits', 0)
            self.cache_misses = stats.get('cache_misses', 0)
            self.tokens_saved = stats.get('tokens_saved', 0)
            
            logger.info(f"📋 Loaded {len(self.cached_decisions)} cached decisions")
            
        except Exception as e:
            logger.error(f"Error loading cache: {e}")
    
    async def cleanup_old_decisions(self):
        """Dọn dẹp quyết định cũ"""
        current_time = datetime.now()
        old_decisions = []
        
        for context_hash, decision in self.cached_decisions.items():
            age_days = (current_time - decision.created_at).days
            if age_days > 30 or decision.success_rate < 0.4:
                old_decisions.append(context_hash)
        
        for context_hash in old_decisions:
            del self.cached_decisions[context_hash]
        
        if old_decisions:
            logger.info(f"📋 Cleaned up {len(old_decisions)} old decisions")
            await self.save_cache() 