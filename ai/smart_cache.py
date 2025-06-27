#!/usr/bin/env python3
"""
Smart Cache - Tiết kiệm token bằng cách cache và tái sử dụng quyết định
"""

import json
import os
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Optional
import aiofiles
from utils.enhanced_logging import get_bot_logger

logger = get_bot_logger()

class SmartCache:
    """Cache thông minh để tiết kiệm token Gemini"""
    
    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = cache_dir
        self.cache_file = os.path.join(cache_dir, "smart_cache.json")
        self.decisions = {}
        
        # Stats
        self.hits = 0
        self.misses = 0
        self.tokens_saved = 0
        
        os.makedirs(cache_dir, exist_ok=True)
    
    def create_pattern(self, economic_data: Dict, weather_data: Dict) -> str:
        """Tạo pattern từ context"""
        # Simplify data thành categories
        activity = self._get_level(economic_data.get('activity_rate', 0), [0.3, 0.7])
        health = self._get_level(economic_data.get('economic_health_score', 0.5), [0.4, 0.7])
        players = self._get_level(economic_data.get('total_players', 0), [50, 200])
        weather = weather_data.get('current_weather', 'sunny')
        
        return f"{activity}-{health}-{players}-{weather}"
    
    def _get_level(self, value: float, thresholds: list) -> str:
        """Convert số thành level (low/medium/high)"""
        if value < thresholds[0]:
            return 'low'
        elif value < thresholds[1]:
            return 'medium'
        else:
            return 'high'
    
    async def get_cached_decision(self, economic_data: Dict, weather_data: Dict) -> Optional[Dict]:
        """Tìm decision đã cache"""
        pattern = self.create_pattern(economic_data, weather_data)
        
        if pattern in self.decisions:
            cached = self.decisions[pattern]
            
            # Check if not too old (7 days)
            created = datetime.fromisoformat(cached['created_at'])
            if (datetime.now() - created).days <= 7:
                
                # Update usage
                cached['usage_count'] += 1
                cached['last_used'] = datetime.now().isoformat()
                
                self.hits += 1
                self.tokens_saved += 400  # Estimated tokens saved
                
                logger.info(f"💾 Cache HIT: Pattern {pattern} (used {cached['usage_count']} times)")
                return cached['decision']
        
        self.misses += 1
        logger.info(f"💾 Cache MISS: Pattern {pattern}")
        return None
    
    async def save_decision(self, economic_data: Dict, weather_data: Dict, decision: Dict):
        """Lưu decision vào cache"""
        pattern = self.create_pattern(economic_data, weather_data)
        
        self.decisions[pattern] = {
            'decision': decision,
            'created_at': datetime.now().isoformat(),
            'last_used': datetime.now().isoformat(),
            'usage_count': 1,
            'pattern': pattern
        }
        
        await self.save_to_disk()
        logger.info(f"💾 Cached decision: {pattern}")
    
    def get_stats(self) -> Dict:
        """Lấy thống kê cache"""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        cost_saved = self.tokens_saved * 0.002 / 1000  # Rough cost estimate
        
        return {
            'cached_decisions': len(self.decisions),
            'cache_hits': self.hits,
            'cache_misses': self.misses,
            'hit_rate': f"{hit_rate:.1f}%",
            'tokens_saved': self.tokens_saved,
            'cost_saved': f"${cost_saved:.4f}"
        }
    
    async def save_to_disk(self):
        """Lưu cache xuống file"""
        try:
            # Convert any GeminiDecision objects to dict
            serializable_decisions = {}
            for key, value in self.decisions.items():
                if hasattr(value, 'asdict'):
                    # If it's a GeminiDecision or has asdict method
                    serializable_decisions[key] = value.asdict()
                elif isinstance(value, dict):
                    serializable_decisions[key] = value
                else:
                    # Try to convert to dict if possible
                    try:
                        from dataclasses import asdict
                        serializable_decisions[key] = asdict(value)
                    except:
                        # Fallback to string representation
                        serializable_decisions[key] = str(value)
            
            data = {
                'decisions': serializable_decisions,
                'stats': {
                    'hits': self.hits,
                    'misses': self.misses,
                    'tokens_saved': self.tokens_saved
                }
            }
            
            async with aiofiles.open(self.cache_file, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(data, ensure_ascii=False, indent=2))
                
        except Exception as e:
            logger.error(f"Error saving cache: {e}")
    
    async def load_from_disk(self):
        """Load cache từ file"""
        try:
            if not os.path.exists(self.cache_file):
                return
            
            async with aiofiles.open(self.cache_file, 'r', encoding='utf-8') as f:
                data = json.loads(await f.read())
            
            self.decisions = data.get('decisions', {})
            stats = data.get('stats', {})
            self.hits = stats.get('hits', 0)
            self.misses = stats.get('misses', 0)
            self.tokens_saved = stats.get('tokens_saved', 0)
            
            logger.info(f"💾 Loaded cache: {len(self.decisions)} decisions")
            
        except Exception as e:
            logger.error(f"Error loading cache: {e}")
    
    async def cleanup_old(self):
        """Dọn dẹp decisions cũ"""
        current_time = datetime.now()
        to_remove = []
        
        for pattern, data in self.decisions.items():
            created = datetime.fromisoformat(data['created_at'])
            if (current_time - created).days > 30:
                to_remove.append(pattern)
        
        for pattern in to_remove:
            del self.decisions[pattern]
        
        if to_remove:
            logger.info(f"💾 Cleaned up {len(to_remove)} old decisions")
            await self.save_to_disk() 