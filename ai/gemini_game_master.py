#!/usr/bin/env python3
"""
Gemini Game Master - Hệ thống AI toàn năng điều khiển mọi hoạt động game
Gemini có quyền admin hoàn toàn: mua bán, sự kiện, thời tiết, kinh tế
Truy vấn và quyết định mỗi 15 phút dựa trên data tổng thể người dùng
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
from ai.gemini_client import get_gemini_manager, GEMINI_AVAILABLE
import discord
from ai.smart_decision_cache import SmartDecisionCache

logger = get_bot_logger()

@dataclass
class GameMasterDecision:
    """Quyết định từ Gemini Game Master"""
    decision_id: str
    action_type: str  # weather_control, event_trigger, market_control, economy_intervention, user_rewards
    reasoning: str
    confidence: float
    parameters: Dict[str, Any]
    expected_impact: str
    execution_time: datetime
    priority: str  # low, medium, high, critical, emergency
    affected_users: List[int]  # Danh sách user_id bị ảnh hưởng
    timestamp: datetime

@dataclass
class GameStateSnapshot:
    """Snapshot trạng thái game toàn diện"""
    timestamp: datetime
    
    # Player Statistics
    total_players: int
    active_players_15min: int
    active_players_1hour: int
    active_players_24hour: int
    new_players_today: int
    
    # Economic Data
    total_money_circulation: int
    average_money_per_player: float
    median_money_per_player: float
    money_distribution: Dict[str, int]
    inflation_rate: float
    
    # Market Activity
    market_transactions_15min: int
    top_selling_crops: List[str]
    crop_price_trends: Dict[str, float]
    market_volatility: float
    
    # Farming Activity
    total_plots: int
    occupied_plots: int
    crop_distribution: Dict[str, int]
    harvest_frequency: float
    
    # Weather & Environment
    current_weather: str
    weather_duration: int
    weather_satisfaction: float
    
    # Events & Engagement
    active_events: List[str]
    event_participation: float
    daily_streak_average: float
    
    # System Health
    economic_health_score: float
    player_satisfaction: float
    game_balance_score: float

class GeminiGameMaster:
    """
    Gemini Game Master - AI toàn năng với quyền admin hoàn toàn
    """
    
    def __init__(self, database: Database):
        self.db = database
        self.gemini_manager = get_gemini_manager()
        
        # Game Master Config
        self.config = {
            "analysis_interval_minutes": 15,  # Truy vấn mỗi 15 phút
            "enable_auto_control": True,      # Tự động điều khiển
            "emergency_intervention": True,   # Can thiệp khẩn cấp
            "max_decisions_per_hour": 8,      # Giới hạn quyết định/giờ
            "min_confidence_threshold": 0.6   # Ngưỡng confidence tối thiểu
        }
        
        # Decision tracking
        self.decision_history = []
        self.last_analysis_time = None
        self.current_interventions = {}
        
        # Game state cache
        self.game_state_cache = {}
        self.user_behavior_patterns = {}
        
        # Control flags
        self.enabled = True
        self.emergency_mode = False
        
        # Token optimization features
        self.smart_cache = None
        self.context_cache_enabled = True
        self.cached_context_id = None
        self.base_prompt_tokens = 0
        
        # Rate limiting
        self.decisions_per_hour = 0
        self.last_hour_reset = datetime.now()
        
        # Tracking
        self.total_tokens_used = 0
        self.total_tokens_saved = 0
        self.cache_hit_rate = 0.0
        
        # Weather history tracking để tránh lặp lại
        self._weather_history = []  # Track last 10 weather changes
        self._event_history = []    # Track last 10 event triggers
        
        # Performance tracking
        self.api_call_count = 0
        
    async def initialize(self):
        """Khởi tạo Game Master với token optimization"""
        try:
            await self.load_config()
            await self.initialize_tracking_systems()
            
            # Initialize smart cache for token savings
            self.smart_cache = SmartDecisionCache()
            await self.smart_cache.initialize()
            
            # Initialize context caching
            await self.initialize_context_caching()
            
            logger.info("🎮 Gemini Game Master initialized with token optimization")
            logger.info(f"💾 Smart cache: {len(self.smart_cache.cached_decisions) if self.smart_cache else 0} decisions")
            logger.info(f"🔄 Context caching: {'enabled' if self.context_cache_enabled else 'disabled'}")
            
        except Exception as e:
            logger.error(f"Error initializing Game Master: {e}")
            raise

    async def initialize_context_caching(self):
        """Khởi tạo context caching để tiết kiệm token"""
        try:
            # Create base context that rarely changes
            base_context = self.create_base_context()
            
            # This would be cached on Gemini's side to save input tokens
            self.base_prompt_tokens = len(base_context.split()) * 1.3  # Rough token estimate
            
            logger.info(f"📝 Base context prepared: ~{self.base_prompt_tokens:.0f} tokens")
            
        except Exception as e:
            logger.error(f"Error initializing context caching: {e}")
            self.context_cache_enabled = False

    def create_base_context(self) -> str:
        """Tạo base context có thể cache để tiết kiệm token"""
        return """
BẠN LÀ GEMINI GAME MASTER - AI với quyền admin toàn bộ game Discord farming bot.

=== QUYỀN ADMIN CỦA BẠN ===

1. WEATHER_CONTROL (ƯU TIÊN HÀNG ĐẦU):
   - Thay đổi thời tiết (sunny, rainy, storm, drought, cloudy, windy, foggy)
   - Điều chỉnh thời gian diễn ra (15-180 phút)
   - Tạo weather pattern phù hợp với game state
   - **QUAN TRỌNG**: Thay đổi thời tiết mỗi 15 phút để tối ưu game balance
   - **MỤC TIÊU**: Duy trì satisfaction > 60%, balance growth effects

2. EVENT_TRIGGER:
   - Tạo sự kiện mới (festival, sale, bonus, etc.)
   - Điều chỉnh phần thưởng sự kiện
   - Kích hoạt sự kiện khẩn cấp

3. MARKET_CONTROL:
   - Điều chỉnh giá cây trồng (từng loại hoặc toàn bộ)
   - Thay đổi giá hạt giống
   - Tạo sale/discount đặc biệt

4. ECONOMY_INTERVENTION:
   - Can thiệp lạm phát
   - Điều chỉnh phân bổ tiền
   - Tạo cơ hội kiếm tiền mới

5. USER_REWARDS:
   - Thưởng cho người chơi tích cực
   - Khuyến khích người mới
   - Tạo competition/contest

=== RESPONSE FORMAT ===
Luôn trả về JSON với format:
{
    "analysis": "Phân tích chi tiết tình hình game",
    "action_type": "weather_control/event_trigger/market_control/economy_intervention/user_rewards",
    "reasoning": "Lý do tại sao chọn hành động này",
    "confidence": 0.8,
    "parameters": {
        // Tham số cụ thể cho từng action_type
    },
    "expected_impact": "Tác động dự kiến",
    "priority": "low/medium/high/critical/emergency",
    "affected_users": [123, 456, 789],
    "execution_time": "immediate/in_5_minutes/in_30_minutes",
    "duration": "30_minutes/1_hour/6_hours/24_hours"
}
"""

    async def analyze_and_control(self, bot) -> Optional[GameMasterDecision]:
        """Phân tích và đưa ra quyết định với token optimization"""
        try:
            # Collect current game state
            game_state = await self.collect_comprehensive_game_state(bot)
            user_patterns = await self.analyze_user_behavior_patterns(bot)
            game_health = await self.evaluate_game_health(game_state, user_patterns)
            
            # Try to find cached decision first
            cached_decision = await self.find_cached_decision(game_state, user_patterns)
            if cached_decision:
                self.total_tokens_saved += 2500  # Estimated tokens saved
                logger.info("💾 Using cached decision - saved ~2500 tokens")
                return cached_decision
            
            # Create optimized prompt (only variable data)
            current_data_prompt = await self.create_optimized_prompt(game_state, user_patterns, game_health, bot)
            
            # Use context caching if available
            if self.context_cache_enabled:
                full_prompt = self.create_base_context() + "\n\n" + current_data_prompt
            else:
                full_prompt = await self.create_master_prompt(game_state, user_patterns, game_health, bot)
            
            # Get Gemini response
            gemini_manager = get_gemini_manager()
            response = await gemini_manager.call_gemini_json(full_prompt)
            
            if not response:
                logger.error("❌ No response from Gemini")
                return None
            
            # Parse decision
            decision = await self.parse_master_decision(response)
            
            # Cache this decision for future use
            await self.cache_decision(game_state, user_patterns, decision)
            
            # Track token usage
            estimated_tokens = len(full_prompt.split()) * 1.3
            self.total_tokens_used += estimated_tokens
            
            # Update cache hit rate
            total_requests = self.smart_cache.cache_hits + self.smart_cache.cache_misses
            if total_requests > 0:
                self.cache_hit_rate = self.smart_cache.cache_hits / total_requests
            
            logger.info(f"🎮 Game Master decision made - used ~{estimated_tokens:.0f} tokens")
            logger.info(f"💾 Cache hit rate: {self.cache_hit_rate:.1%}")
            
            return decision
            
        except Exception as e:
            logger.error(f"Error in Game Master analysis: {e}")
            return None

    async def create_optimized_prompt(self, game_state: GameStateSnapshot, user_patterns: Dict, game_health: float, bot) -> str:
        """Tạo prompt tối ưu cho Gemini với context caching"""
        try:
            # Check if we should use cached context or full prompt
            if self.context_cache_name:
                # Use cached context + current data only
                current_data_prompt = f"""
=== TRẠNG THÁI HIỆN TẠI ===
⏰ THỜI GIAN: {game_state.timestamp.strftime("%H:%M %d/%m/%Y")}
👥 NGƯỜI CHƠI: {game_state.active_players_15min}/15p, {game_state.total_players} tổng
💰 KINH TẾ: {game_state.total_money_circulation:,} coins lưu hành, lạm phát {game_state.inflation_rate:.1%}
📊 THỊ TRƯỜNG: {game_state.market_transactions_15min} giao dịch, biến động {game_state.market_volatility:.1%}
🌱 NÔNG NGHIỆP: {game_state.occupied_plots}/{game_state.total_plots} ô đất
🌤️ THỜI TIẾT: {game_state.current_weather} ({game_state.weather_duration}p)
📈 SỨC KHỎE: Kinh tế {game_state.economic_health_score:.1%}, Hài lòng {game_state.player_satisfaction:.1%}

Quyết định cần thiết nhất cho tình hình hiện tại?
"""
                return current_data_prompt
            else:
                # Use full prompt
                return await self.create_master_prompt(game_state, user_patterns, game_health, bot)
                
        except Exception as e:
            logger.error(f"Error creating optimized prompt: {e}")
            return await self.create_master_prompt(game_state, user_patterns, game_health, bot)

    async def find_cached_decision(self, game_state: GameStateSnapshot, user_patterns: Dict) -> Optional[GameMasterDecision]:
        """Tìm quyết định đã cache cho tình huống tương tự"""
        if not self.smart_cache:
            return None
        
        try:
            # Create context pattern for similarity matching
            context_pattern = self.create_context_pattern(game_state, user_patterns)
            
            # Look for similar cached decisions
            cached_data = await self.smart_cache.find_similar_decision(context_pattern)
            
            if cached_data:
                # Convert cached data back to GameMasterDecision
                return self.convert_cached_to_decision(cached_data)
            
            return None
            
        except Exception as e:
            logger.error(f"Error finding cached decision: {e}")
            return None

    def create_context_pattern(self, game_state: GameStateSnapshot, user_patterns: Dict) -> str:
        """Tạo pattern để match với cached decisions"""
        # Categorize current state
        activity_level = "high" if game_state.active_players_15min > 20 else "medium" if game_state.active_players_15min > 10 else "low"
        health_level = "good" if game_state.economic_health_score > 0.7 else "fair" if game_state.economic_health_score > 0.4 else "poor"
        inflation_level = "high" if game_state.inflation_rate > 0.1 else "medium" if game_state.inflation_rate > 0.05 else "low"
        
        return f"{activity_level}-{health_level}-{inflation_level}-{game_state.current_weather}"

    async def cache_decision(self, game_state: GameStateSnapshot, user_patterns: Dict, decision: GameMasterDecision):
        """Cache quyết định để tái sử dụng sau"""
        if not self.smart_cache:
            return
        
        try:
            context_pattern = self.create_context_pattern(game_state, user_patterns)
            
            cached_decision = {
                'decision_id': decision.decision_id,
                'context_pattern': context_pattern,
                'action_type': decision.action_type,
                'reasoning': decision.reasoning,
                'confidence': decision.confidence,
                'parameters': decision.parameters,
                'expected_impact': decision.expected_impact,
                'priority': decision.priority,
                'affected_users': decision.affected_users,
                'created_at': datetime.now().isoformat()
            }
            
            # Cache decision with proper format for smart_cache
            fake_economic_data = {"pattern": context_pattern}
            fake_weather_data = {"cached": True}
            await self.smart_cache.save_decision(fake_economic_data, fake_weather_data, cached_decision)
            
        except Exception as e:
            logger.error(f"Error caching decision: {e}")

    def convert_cached_to_decision(self, cached_data: Dict) -> GameMasterDecision:
        """Convert cached data back to GameMasterDecision object"""
        return GameMasterDecision(
            decision_id=cached_data.get('decision_id', f"cached_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
            action_type=cached_data.get('action_type', 'no_action'),
            reasoning=cached_data.get('reasoning', 'Cached decision'),
            confidence=cached_data.get('confidence', 0.7),
            parameters=cached_data.get('parameters', {}),
            expected_impact=cached_data.get('expected_impact', 'Reused cached decision'),
            execution_time=datetime.now(),
            priority=cached_data.get('priority', 'medium'),
            affected_users=cached_data.get('affected_users', []),
            timestamp=datetime.now()
        )

    async def get_token_optimization_stats(self) -> Dict[str, Any]:
        """Lấy thống kê tối ưu hóa token"""
        cache_stats = self.smart_cache.get_stats() if self.smart_cache else {}
        
        return {
            'total_tokens_used': self.total_tokens_used,
            'total_tokens_saved': self.total_tokens_saved + cache_stats.get('tokens_saved', 0),
            'cache_hit_rate': self.cache_hit_rate,
            'estimated_cost_saved': (self.total_tokens_saved * 0.30) / 1000000,  # $0.30 per 1M tokens
            'context_caching_enabled': self.context_cache_enabled,
            'smart_cache_stats': cache_stats
        }

    async def initialize(self):
        """Khởi tạo Game Master"""
        try:
            await self.load_config()
            await self.initialize_tracking_systems()
            logger.info("🎮 Gemini Game Master initialized - FULL CONTROL MODE")
            
        except Exception as e:
            logger.error(f"Error initializing Game Master: {e}")
            
    async def load_config(self):
        """Load configuration"""
        config_file = "ai/game_master_config.json"
        try:
            if os.path.exists(config_file):
                async with aiofiles.open(config_file, 'r', encoding='utf-8') as f:
                    content = await f.read()
                    saved_config = json.loads(content)
                    self.config.update(saved_config)
        except Exception as e:
            logger.warning(f"Using default config: {e}")
            await self.save_config()
    
    async def save_config(self):
        """Save configuration"""
        config_file = "ai/game_master_config.json"
        try:
            os.makedirs("ai", exist_ok=True)
            async with aiofiles.open(config_file, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(self.config, indent=2, ensure_ascii=False))
        except Exception as e:
            logger.error(f"Error saving config: {e}")
    
    async def initialize_tracking_systems(self):
        """Khởi tạo hệ thống theo dõi"""
        try:
            # Ensure database connection
            conn = await self.db.get_connection()
            
            # Tạo tables theo dõi nếu chưa có
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS game_master_decisions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    decision_id TEXT UNIQUE,
                    action_type TEXT,
                    reasoning TEXT,
                    confidence REAL,
                    parameters TEXT,
                    execution_time TEXT,
                    priority TEXT,
                    affected_users TEXT,
                    created_at TEXT,
                    executed BOOLEAN DEFAULT FALSE
                )
            """)
            
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS game_state_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    snapshot_data TEXT,
                    health_score REAL,
                    created_at TEXT
                )
            """)
            
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS user_behavior_tracking (
                    user_id INTEGER,
                    activity_pattern TEXT,
                    last_active TEXT,
                    engagement_score REAL,
                    spending_pattern TEXT,
                    farming_efficiency REAL,
                    updated_at TEXT,
                    PRIMARY KEY (user_id)
                )
            """)
            
            await conn.commit()
            logger.info("✅ Game Master tracking systems initialized")
            
        except Exception as e:
            logger.error(f"Error initializing tracking: {e}")
    
    async def collect_comprehensive_game_state(self, bot) -> GameStateSnapshot:
        """Thu thập trạng thái game toàn diện"""
        try:
            current_time = datetime.now()
            
            # Player statistics
            all_users = await self.db.get_all_users()
            total_players = len(all_users)
            
            # Time-based activity
            cutoff_15min = current_time - timedelta(minutes=15)
            cutoff_1hour = current_time - timedelta(hours=1)
            cutoff_24hour = current_time - timedelta(hours=24)
            cutoff_today = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
            
            active_15min = sum(1 for user in all_users if user.get('last_seen', current_time) > cutoff_15min)
            active_1hour = sum(1 for user in all_users if user.get('last_seen', current_time) > cutoff_1hour)
            active_24hour = sum(1 for user in all_users if user.get('last_seen', current_time) > cutoff_24hour)
            new_today = sum(1 for user in all_users if user.get('joined_date', current_time) > cutoff_today)
            
            # Economic data
            money_amounts = [user.get('money', 0) for user in all_users]
            total_money = sum(money_amounts)
            avg_money = total_money / total_players if total_players > 0 else 0
            median_money = self._calculate_median(money_amounts)
            money_distribution = self._analyze_money_distribution(money_amounts)
            
            # Market activity
            market_transactions = await self._get_market_activity(cutoff_15min)
            crop_trends = await self._analyze_crop_trends()
            
            # Farming activity
            farming_stats = await self._get_farming_statistics()
            
            # Weather data
            weather_data = await self._get_weather_status(bot)
            
            # Events data
            events_data = await self._get_events_status(bot)
            
            # Calculate scores
            economic_health = self._calculate_economic_health(money_distribution, total_money, active_24hour)
            player_satisfaction = self._calculate_player_satisfaction(active_15min, total_players, events_data)
            game_balance = self._calculate_game_balance(economic_health, player_satisfaction)
            
            snapshot = GameStateSnapshot(
                timestamp=current_time,
                total_players=total_players,
                active_players_15min=active_15min,
                active_players_1hour=active_1hour,
                active_players_24hour=active_24hour,
                new_players_today=new_today,
                total_money_circulation=total_money,
                average_money_per_player=avg_money,
                median_money_per_player=median_money,
                money_distribution=money_distribution,
                inflation_rate=await self._calculate_inflation_rate(),
                market_transactions_15min=market_transactions,
                top_selling_crops=crop_trends.get('top_selling', []),
                crop_price_trends=crop_trends.get('price_trends', {}),
                market_volatility=crop_trends.get('volatility', 0.0),
                total_plots=farming_stats.get('total_plots', 0),
                occupied_plots=farming_stats.get('occupied_plots', 0),
                crop_distribution=farming_stats.get('crop_distribution', {}),
                harvest_frequency=farming_stats.get('harvest_frequency', 0.0),
                current_weather=weather_data.get('type', 'sunny'),
                weather_duration=weather_data.get('duration', 0),
                weather_satisfaction=weather_data.get('satisfaction', 0.5),
                active_events=events_data.get('active_events', []),
                event_participation=events_data.get('participation', 0.0),
                daily_streak_average=await self._calculate_daily_streak_average(),
                economic_health_score=economic_health,
                player_satisfaction=player_satisfaction,
                game_balance_score=game_balance
            )
            
            # Cache snapshot
            await self.save_game_state_snapshot(snapshot)
            
            return snapshot
            
        except Exception as e:
            logger.error(f"Error collecting game state: {e}")
            return self._get_default_game_state()
    
    async def create_master_prompt(self, game_state: GameStateSnapshot, user_patterns: Dict, game_health: float, bot) -> str:
        """Tạo prompt cho Gemini Game Master"""
        
        # Get detailed weather data
        weather_data = await self._get_weather_status(bot)
        
        prompt = f"""
BẠN LÀ GEMINI GAME MASTER - AI với quyền admin toàn bộ game Discord farming bot.

THỜI GIAN: {game_state.timestamp.strftime("%H:%M %d/%m/%Y")}

=== TRẠNG THÁI GAME HIỆN TẠI ===

👥 NGƯỜI CHƠI:
- Tổng số: {game_state.total_players}
- Hoạt động 15 phút: {game_state.active_players_15min}
- Hoạt động 1 giờ: {game_state.active_players_1hour}  
- Hoạt động 24 giờ: {game_state.active_players_24hour}
- Người mới hôm nay: {game_state.new_players_today}

💰 KINH TẾ:
- Tổng tiền lưu hành: {game_state.total_money_circulation:,} coins
- Tiền trung bình/người: {game_state.average_money_per_player:,.0f} coins
- Tiền trung vị: {game_state.median_money_per_player:,.0f} coins
- Tỷ lệ lạm phát: {game_state.inflation_rate:.1%}
- Phân bổ tiền: {game_state.money_distribution}

📊 THỊ TRƯỜNG:
- Giao dịch 15 phút: {game_state.market_transactions_15min}
- Cây bán chạy: {game_state.top_selling_crops}
- Biến động giá: {game_state.market_volatility:.1%}

🌱 NÔNG NGHIỆP:
- Tổng ô đất: {game_state.total_plots}
- Ô đang trồng: {game_state.occupied_plots}
- Tỷ lệ sử dụng đất: {(game_state.occupied_plots/max(1,game_state.total_plots)*100):.1f}%
- Phân bố cây trồng: {game_state.crop_distribution}

🌤️ THỜI TIẾT & SỰ KIỆN:
- Thời tiết hiện tại: {weather_data.get('type', 'sunny')}
- Thời gian còn lại: {weather_data.get('duration', 0)} phút
- Mức hài lòng thời tiết: {weather_data.get('satisfaction', 0.5):.1%}
- Hiệu ứng hiện tại: Growth {weather_data.get('effects', {}).get('growth_rate', 1.0):.1%}, Price {weather_data.get('effects', {}).get('sell_price', 1.0):.1%}
- Cần thay đổi thời tiết: {"CÓ" if weather_data.get('should_change', False) else "KHÔNG"}
- Sự kiện đang diễn ra: {game_state.active_events}
- Tham gia sự kiện: {game_state.event_participation:.1%}

📈 CHỈ SỐ GAME:
- Sức khỏe kinh tế: {game_state.economic_health_score:.1%}
- Hài lòng người chơi: {game_state.player_satisfaction:.1%}
- Cân bằng game: {game_state.game_balance_score:.1%}
- Streak điểm danh TB: {game_state.daily_streak_average:.1f}

=== QUYỀN ADMIN CỦA BẠN ===

1. WEATHER_CONTROL (ƯU TIÊN HÀNG ĐẦU):
   - Thay đổi thời tiết (sunny, rainy, storm, drought, cloudy, windy, foggy)
   - Điều chỉnh thời gian diễn ra (15-180 phút)
   - Tạo weather pattern phù hợp với game state
   - **QUAN TRỌNG**: Thay đổi thời tiết mỗi 15 phút để tối ưu game balance
   - **MỤC TIÊU**: Duy trì satisfaction > 60%, balance growth effects

2. EVENT_TRIGGER:
   - Tạo sự kiện mới (festival, sale, bonus, etc.)
   - Điều chỉnh phần thưởng sự kiện
   - Kích hoạt sự kiện khẩn cấp

3. MARKET_CONTROL:
   - Điều chỉnh giá cây trồng (từng loại hoặc toàn bộ)
   - Thay đổi giá hạt giống
   - Tạo sale/discount đặc biệt

4. ECONOMY_INTERVENTION:
   - Can thiệp lạm phát
   - Điều chỉnh phân bổ tiền
   - Tạo cơ hội kiếm tiền mới

5. USER_REWARDS:
   - Thưởng cho người chơi tích cực
   - Khuyến khích người mới
   - Tạo competition/contest

=== NHIỆM VỤ ===

Phân tích tình hình và đưa ra MỘT quyết định cần thiết nhất.

**ƯU TIÊN WEATHER_CONTROL** nếu:
- Thời tiết còn lại < 15 phút
- Weather satisfaction < 60%
- Cần balance game với weather effects

RESPONSE FORMAT (JSON):
{{
    "analysis": "Phân tích chi tiết tình hình game",
    "action_type": "weather_control/event_trigger/market_control/economy_intervention/user_rewards",
    "reasoning": "Lý do tại sao chọn hành động này",
    "confidence": 0.8,
    "parameters": {{
        // Cho weather_control:
        "weather_type": "sunny/rainy/storm/drought/cloudy/windy/foggy",
        "duration_hours": 1.0,
        // Cho event_trigger:
        "event_type": "bonus/sale/festival",
        "name": "Event name",
        "description": "Event description",
        "duration_hours": 2,
        "rewards": {{"money": 1000}},
        // Cho market_control:
        "crop_type": "carrot/wheat/all",
        "sell_price_modifier": 1.2,
        "seed_price_modifier": 0.9,
        "duration_hours": 1
    }},
    "expected_impact": "Tác động dự kiến",
    "priority": "low/medium/high/critical/emergency",
    "affected_users": [123, 456, 789],  // user_id list hoặc "all"
    "execution_time": "immediate/in_5_minutes/in_30_minutes",
    "duration": "30_minutes/1_hour/6_hours/24_hours"
}}

Hãy quyết định ngay bây giờ!
"""
        
        return prompt

    async def parse_master_decision(self, gemini_response: Dict) -> GameMasterDecision:
        """Parse quyết định từ Gemini"""
        try:
            decision_id = f"gm_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000,9999)}"
            
            return GameMasterDecision(
                decision_id=decision_id,
                action_type=gemini_response.get('action_type', 'no_action'),
                reasoning=gemini_response.get('reasoning', 'No reasoning provided'),
                confidence=float(gemini_response.get('confidence', 0.5)),
                parameters=gemini_response.get('parameters', {}),
                expected_impact=gemini_response.get('expected_impact', 'Unknown impact'),
                execution_time=datetime.now(),
                priority=gemini_response.get('priority', 'medium'),
                affected_users=gemini_response.get('affected_users', []),
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error parsing Game Master decision: {e}")
            return self._get_fallback_decision()
    
    async def execute_master_decision(self, decision: GameMasterDecision, bot) -> bool:
        """Thực thi quyết định Game Master"""
        try:
            logger.info(f"🎮 Executing Game Master decision: {decision.action_type}")
            
            if decision.action_type == "weather_control":
                return await self._execute_weather_control(decision, bot)
            elif decision.action_type == "event_trigger":
                return await self._execute_event_trigger(decision, bot)
            elif decision.action_type == "market_control":
                return await self._execute_market_control(decision, bot)
            elif decision.action_type == "economy_intervention":
                return await self._execute_economy_intervention(decision, bot)
            elif decision.action_type == "user_rewards":
                return await self._execute_user_rewards(decision, bot)
            else:
                logger.info(f"No action needed: {decision.action_type}")
                return True
                
        except Exception as e:
            logger.error(f"Error executing Game Master decision: {e}")
            return False
    
    async def _execute_weather_control(self, decision: GameMasterDecision, bot) -> bool:
        """Thực thi điều khiển thời tiết với logic thông minh tránh lặp lại"""
        try:
            weather_cog = bot.get_cog('WeatherCog')
            if not weather_cog:
                logger.error("WeatherCog not found")
                return False
            
            params = decision.parameters
            weather_type = params.get('weather_type', 'sunny')
            duration_hours = params.get('duration_hours', 1)
            
            # Smart weather selection - tránh lặp lại
            current_weather = weather_cog.current_weather or 'sunny'
            
            # Nếu weather giống nhau, chọn weather khác phù hợp
            if weather_type == current_weather:
                weather_type = self._select_smart_weather(current_weather)
                logger.info(f"🔄 Changed weather selection from {current_weather} to {weather_type} (avoid repetition)")
            
            # Validate weather type
            valid_weather_types = ['sunny', 'rainy', 'storm', 'drought', 'cloudy', 'windy', 'foggy']
            if weather_type not in valid_weather_types:
                # Fallback to smart selection
                weather_type = self._select_smart_weather(current_weather)
                logger.warning(f"Invalid weather type, using smart selection: {weather_type}")
            
            # Set weather through WeatherCog
            success = await self._set_master_weather(weather_cog, weather_type, duration_hours, decision)
            
            if success:
                # Update weather history
                self._weather_history.append(weather_type)
                if len(self._weather_history) > 10:  # Keep only last 10
                    self._weather_history.pop(0)
                
                # Notify weather change
                await self._notify_weather_change(bot, weather_type, decision)
                
                logger.info(f"✅ Weather changed to {weather_type} for {duration_hours} hours")
                return True
            else:
                logger.error(f"❌ Failed to set weather to {weather_type}")
                return False
                
        except Exception as e:
            logger.error(f"Error executing weather control: {e}")
            return False
    
    def _select_smart_weather(self, current_weather: str) -> str:
        """Chọn thời tiết thông minh dựa trên history và game state"""
        try:
            # All available weather types
            all_weather = ['sunny', 'rainy', 'cloudy', 'windy', 'storm', 'foggy', 'drought']
            
            # Remove current weather
            available_weather = [w for w in all_weather if w != current_weather]
            
            # Remove recently used weather from history
            recent_weather = self._weather_history[-3:] if len(self._weather_history) >= 3 else []
            for recent in recent_weather:
                if recent in available_weather:
                    available_weather.remove(recent)
            
            # If all weather removed, use all except current
            if not available_weather:
                available_weather = [w for w in all_weather if w != current_weather]
            
            # Smart selection based on game needs
            # Prefer beneficial weather (sunny, rainy, cloudy) over harsh weather
            preferred_weather = [w for w in available_weather if w in ['sunny', 'rainy', 'cloudy', 'windy']]
            
            if preferred_weather:
                import random
                return random.choice(preferred_weather)
            else:
                import random
                return random.choice(available_weather)
                
        except Exception as e:
            logger.error(f"Error in smart weather selection: {e}")
            return 'sunny'  # Safe fallback
    
    async def _execute_event_trigger(self, decision: GameMasterDecision, bot) -> bool:
        """Thực thi tạo sự kiện với logic thông minh tránh lặp lại"""
        try:
            events_cog = bot.get_cog('EventsCog')
            if not events_cog:
                logger.error("EventsCog not found")
                return False
            
            params = decision.parameters
            event_type = params.get('event_type', 'harvest_bonus')
            
            # Smart event selection - tránh lặp lại
            if self._is_event_recently_used(event_type):
                event_type = self._select_smart_event(event_type)
                logger.info(f"🔄 Changed event selection to {event_type} (avoid repetition)")
            
            # Create comprehensive event data
            event_data = {
                'name': self._get_event_name(event_type),
                'type': event_type,
                'description': params.get('description', f'Event triggered by Game Master: {event_type}'),
                'duration_hours': params.get('duration_hours', 2),
                'bonus_multiplier': params.get('bonus_multiplier', 1.5),
                'affected_activities': params.get('affected_activities', ['farming']),
                'source': 'Gemini Game Master',
                'auto_generated': True
            }
            
            # Validate event type
            valid_event_types = [
                'harvest_bonus', 'double_exp', 'market_boost', 'rain_blessing', 
                'golden_hour', 'lucky_day', 'speed_growth', 'mega_yield'
            ]
            
            if event_type not in valid_event_types:
                event_type = self._select_smart_event('harvest_bonus')
                event_data['type'] = event_type
                event_data['name'] = self._get_event_name(event_type)
                logger.warning(f"Invalid event type, using smart selection: {event_type}")
            
            # Start event
            success = await self._start_master_event(events_cog, event_data, decision)
            
            if success:
                # Update event history
                self._event_history.append(event_type)
                if len(self._event_history) > 10:  # Keep only last 10
                    self._event_history.pop(0)
                
                # Notify event start
                await self._notify_event_start(bot, event_data, decision)
                
                logger.info(f"✅ Event '{event_data['name']}' started for {event_data['duration_hours']} hours")
                return True
            else:
                logger.error(f"❌ Failed to start event {event_type}")
                return False
                
        except Exception as e:
            logger.error(f"Error executing event trigger: {e}")
            return False
    
    def _is_event_recently_used(self, event_type: str) -> bool:
        """Kiểm tra xem event đã được dùng gần đây chưa"""
        recent_events = self._event_history[-3:] if len(self._event_history) >= 3 else []
        return event_type in recent_events
    
    def _select_smart_event(self, current_event: str) -> str:
        """Chọn sự kiện thông minh dựa trên history"""
        try:
            # All available event types
            all_events = [
                'harvest_bonus', 'double_exp', 'market_boost', 'rain_blessing',
                'golden_hour', 'lucky_day', 'speed_growth', 'mega_yield'
            ]
            
            # Remove current event
            available_events = [e for e in all_events if e != current_event]
            
            # Remove recently used events from history
            recent_events = self._event_history[-3:] if len(self._event_history) >= 3 else []
            for recent in recent_events:
                if recent in available_events:
                    available_events.remove(recent)
            
            # If all events removed, use all except current
            if not available_events:
                available_events = [e for e in all_events if e != current_event]
            
            # Smart selection based on popularity and usefulness
            preferred_events = [e for e in available_events if e in ['harvest_bonus', 'double_exp', 'market_boost', 'lucky_day']]
            
            if preferred_events:
                import random
                return random.choice(preferred_events)
            else:
                import random
                return random.choice(available_events)
                
        except Exception as e:
            logger.error(f"Error in smart event selection: {e}")
            return 'harvest_bonus'  # Safe fallback
    
    def _get_event_name(self, event_type: str) -> str:
        """Lấy tên sự kiện theo type"""
        event_names = {
            'harvest_bonus': 'Thu Hoạch Bội Thu',
            'double_exp': 'Kinh Nghiệm Kép',
            'market_boost': 'Thị Trường Thịnh Vượng',
            'rain_blessing': 'Phước Lành Mưa Ngọc',
            'golden_hour': 'Giờ Vàng',
            'lucky_day': 'Ngày May Mắn',
            'speed_growth': 'Tăng Trưởng Thần Tốc',
            'mega_yield': 'Siêu Sản Lượng'
        }
        return event_names.get(event_type, event_type.replace('_', ' ').title())
    
    async def _execute_market_control(self, decision: GameMasterDecision, bot) -> bool:
        """Thực thi điều khiển thị trường"""
        try:
            from utils.pricing import pricing_coordinator
            
            params = decision.parameters
            crop_type = params.get('crop_type', 'all')
            sell_modifier = params.get('sell_price_modifier', 1.0)
            seed_modifier = params.get('seed_price_modifier', 1.0)
            duration_hours = params.get('duration_hours', 1)
            
            # Apply price adjustment
            success = pricing_coordinator.apply_ai_price_adjustment(
                crop_type=crop_type,
                sell_price_modifier=sell_modifier,
                seed_price_modifier=seed_modifier,
                reasoning=f"Game Master: {decision.reasoning}",
                duration_hours=duration_hours
            )
            
            if success:
                await self._notify_market_change(bot, crop_type, sell_modifier, seed_modifier, decision)
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"Error executing market control: {e}")
            return False
    
    async def _execute_economy_intervention(self, decision: GameMasterDecision, bot) -> bool:
        """Thực thi can thiệp kinh tế"""
        try:
            params = decision.parameters
            intervention_type = params.get('intervention_type', 'bonus')
            
            if intervention_type == 'money_redistribution':
                return await self._execute_money_redistribution(params, bot)
            elif intervention_type == 'inflation_control':
                return await self._execute_inflation_control(params, bot)
            elif intervention_type == 'economic_boost':
                return await self._execute_economic_boost(params, bot)
            else:
                logger.warning(f"Unknown intervention type: {intervention_type}")
                return False
                
        except Exception as e:
            logger.error(f"Error executing economy intervention: {e}")
            return False
    
    async def _execute_user_rewards(self, decision: GameMasterDecision, bot) -> bool:
        """Thực thi thưởng người dùng"""
        try:
            params = decision.parameters
            reward_type = params.get('reward_type', 'money')
            target_users = decision.affected_users
            
            if target_users == "all":
                all_users = await self.db.get_all_users()
                target_users = [user['user_id'] for user in all_users]
            
            rewards_given = 0
            
            for user_id in target_users:
                try:
                    user = await self.db.get_user(user_id)
                    if not user:
                        continue
                    
                    if reward_type == 'money':
                        amount = params.get('amount', 1000)
                        user.money += amount
                        await self.db.update_user(user)
                        rewards_given += 1
                    elif reward_type == 'items':
                        # Thêm items vào inventory
                        items = params.get('items', {})
                        for item_type, quantity in items.items():
                            await self.db.add_to_inventory(user_id, item_type, quantity)
                        rewards_given += 1
                    
                except Exception as e:
                    logger.error(f"Error rewarding user {user_id}: {e}")
                    continue
            
            if rewards_given > 0:
                await self._notify_user_rewards(bot, reward_type, rewards_given, decision)
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"Error executing user rewards: {e}")
            return False
    
    # Helper methods for data collection
    async def _get_market_activity(self, cutoff_time: datetime) -> int:
        """Lấy số giao dịch thị trường trong khoảng thời gian"""
        try:
            # Placeholder - thực tế sẽ query từ market transactions table
            return random.randint(5, 50)
        except Exception:
            return 0
    
    async def _analyze_crop_trends(self) -> Dict[str, Any]:
        """Phân tích xu hướng cây trồng"""
        try:
            # Placeholder - thực tế sẽ phân tích từ database
            return {
                'top_selling': ['carrot', 'wheat', 'corn'],
                'price_trends': {'carrot': 1.1, 'wheat': 0.9, 'corn': 1.05},
                'volatility': 0.15
            }
        except Exception:
            return {'top_selling': [], 'price_trends': {}, 'volatility': 0.0}
    
    async def _get_farming_statistics(self) -> Dict[str, Any]:
        """Lấy thống kê farming"""
        try:
            cursor = await self.db.connection.execute("SELECT COUNT(*) FROM crops")
            total_crops = (await cursor.fetchone())[0] or 0
            
            cursor = await self.db.connection.execute("SELECT crop_type, COUNT(*) FROM crops GROUP BY crop_type")
            crop_counts = dict(await cursor.fetchall())
            
            cursor = await self.db.connection.execute("SELECT SUM(land_slots) FROM users")
            total_plots = (await cursor.fetchone())[0] or 0
            
            return {
                'total_plots': total_plots,
                'occupied_plots': total_crops,
                'crop_distribution': crop_counts,
                'harvest_frequency': 0.7  # Placeholder
            }
        except Exception as e:
            logger.error(f"Error getting farming stats: {e}")
            return {'total_plots': 0, 'occupied_plots': 0, 'crop_distribution': {}, 'harvest_frequency': 0.0}
    
    async def _get_weather_status(self, bot) -> Dict[str, Any]:
        """Lấy trạng thái thời tiết hiện tại từ WeatherCog"""
        try:
            weather_cog = bot.get_cog('WeatherCog')
            if not weather_cog:
                return {
                    'type': 'sunny',
                    'duration': 60,
                    'satisfaction': 0.5,
                    'effects': {'growth_rate': 1.0, 'sell_price': 1.0, 'quality_bonus': 1.0},
                    'last_change': None,
                    'next_change': None,
                    'should_change': True
                }
            
            # Get detailed weather info from WeatherCog
            weather_info = await weather_cog.get_current_weather_info()
            current_weather = weather_info.get('current_weather', 'sunny')
            duration_remaining = weather_info.get('duration_remaining_minutes', 0)
            
            # Check if weather should change based on time and variety
            should_change = False
            
            # Condition 1: Less than 5 minutes remaining
            if duration_remaining < 5:
                should_change = True
                
            # Condition 2: Same weather for too long (over 2 hours)
            if duration_remaining > 120:  # More than 2 hours
                should_change = True
                
            # Condition 3: Weather pattern analysis - avoid repetition
            weather_history = getattr(self, '_weather_history', [])
            if len(weather_history) >= 3 and all(w == current_weather for w in weather_history[-3:]):
                should_change = True  # Same weather 3 times in a row
            
            return {
                'type': current_weather,
                'duration': duration_remaining,
                'satisfaction': weather_info.get('satisfaction_score', 0.5),
                'effects': weather_info.get('weather_effects', {}),
                'last_change': weather_info.get('last_change_time'),
                'next_change': weather_info.get('next_change_time'),
                'should_change': should_change,
                'weather_history': weather_history
            }
            
        except Exception as e:
            logger.error(f"Error getting weather status: {e}")
            return {
                'type': 'sunny',
                'duration': 60,
                'satisfaction': 0.5,
                'effects': {'growth_rate': 1.0, 'sell_price': 1.0, 'quality_bonus': 1.0},
                'should_change': True
            }
    
    async def _get_events_status(self, bot) -> Dict[str, Any]:
        """Lấy trạng thái sự kiện"""
        try:
            events_cog = bot.get_cog('EventsCog')
            if events_cog and hasattr(events_cog, 'current_event'):
                current_event = events_cog.current_event
                if current_event:
                    return {
                        'active_events': [current_event.get('name', 'Unknown Event')],
                        'participation': 0.6  # Placeholder
                    }
            
            return {'active_events': [], 'participation': 0.0}
        except Exception:
            return {'active_events': [], 'participation': 0.0}
    
    async def _calculate_daily_streak_average(self) -> float:
        """Tính streak điểm danh trung bình"""
        try:
            cursor = await self.db.connection.execute("SELECT AVG(daily_streak) FROM users WHERE daily_streak > 0")
            result = await cursor.fetchone()
            return float(result[0]) if result and result[0] else 0.0
        except Exception:
            return 0.0
    
    async def _calculate_inflation_rate(self) -> float:
        """Tính tỷ lệ lạm phát"""
        try:
            # Placeholder - so sánh giá hiện tại với giá base
            return random.uniform(0.02, 0.08)  # 2-8%
        except Exception:
            return 0.05
    
    def _calculate_median(self, values: List[float]) -> float:
        """Tính median"""
        if not values:
            return 0.0
        sorted_values = sorted(values)
        n = len(sorted_values)
        if n % 2 == 0:
            return (sorted_values[n//2 - 1] + sorted_values[n//2]) / 2
        else:
            return sorted_values[n//2]
    
    def _analyze_money_distribution(self, money_amounts: List[int]) -> Dict[str, int]:
        """Phân tích phân bổ tiền"""
        if not money_amounts:
            return {'0-1k': 0, '1k-10k': 0, '10k-100k': 0, '100k+': 0}
        
        ranges = {'0-1k': 0, '1k-10k': 0, '10k-100k': 0, '100k+': 0}
        
        for amount in money_amounts:
            if amount < 1000:
                ranges['0-1k'] += 1
            elif amount < 10000:
                ranges['1k-10k'] += 1
            elif amount < 100000:
                ranges['10k-100k'] += 1
            else:
                ranges['100k+'] += 1
        
        return ranges
    
    def _calculate_economic_health(self, distribution: Dict, total_money: int, active_players: int) -> float:
        """Tính sức khỏe kinh tế"""
        try:
            # Điểm phân bổ (0-0.4)
            total_players = sum(distribution.values())
            if total_players == 0:
                return 0.5
            
            # Lý tưởng: phân bổ đều
            ideal_dist = total_players / 4
            dist_score = 1.0 - sum(abs(count - ideal_dist) for count in distribution.values()) / (total_players * 2)
            
            # Điểm hoạt động (0-0.3)
            activity_score = min(1.0, active_players / max(1, total_players))
            
            # Điểm lưu hành tiền (0-0.3)
            money_per_active = total_money / max(1, active_players)
            money_score = min(1.0, money_per_active / 10000)  # Normalize to 10k coins
            
            return (dist_score * 0.4 + activity_score * 0.3 + money_score * 0.3)
            
        except Exception:
            return 0.5
    
    def _calculate_player_satisfaction(self, active_15min: int, total_players: int, events_data: Dict) -> float:
        """Tính độ hài lòng người chơi"""
        try:
            # Hoạt động gần đây
            activity_score = active_15min / max(1, total_players)
            
            # Có sự kiện đang diễn ra
            event_score = 1.0 if events_data.get('active_events') else 0.5
            
            # Tham gia sự kiện
            participation_score = events_data.get('participation', 0.0)
            
            return (activity_score * 0.5 + event_score * 0.3 + participation_score * 0.2)
            
        except Exception:
            return 0.5
    
    def _calculate_game_balance(self, economic_health: float, player_satisfaction: float) -> float:
        """Tính cân bằng tổng thể game"""
        return (economic_health * 0.6 + player_satisfaction * 0.4)
    
    def _get_default_game_state(self) -> GameStateSnapshot:
        """Game state mặc định khi có lỗi"""
        return GameStateSnapshot(
            timestamp=datetime.now(),
            total_players=0, active_players_15min=0, active_players_1hour=0,
            active_players_24hour=0, new_players_today=0,
            total_money_circulation=0, average_money_per_player=0.0,
            median_money_per_player=0.0, money_distribution={},
            inflation_rate=0.05, market_transactions_15min=0,
            top_selling_crops=[], crop_price_trends={}, market_volatility=0.0,
            total_plots=0, occupied_plots=0, crop_distribution={},
            harvest_frequency=0.0, current_weather='sunny',
            weather_duration=0, weather_satisfaction=0.5,
            active_events=[], event_participation=0.0,
            daily_streak_average=0.0, economic_health_score=0.5,
            player_satisfaction=0.5, game_balance_score=0.5
        )
    
    def _get_fallback_decision(self) -> GameMasterDecision:
        """Quyết định fallback khi có lỗi"""
        return GameMasterDecision(
            decision_id=f"fallback_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            action_type='no_action',
            reasoning='System fallback - no action taken due to error',
            confidence=0.0,
            parameters={},
            expected_impact='No impact',
            execution_time=datetime.now(),
            priority='low',
            affected_users=[],
            timestamp=datetime.now()
        )
    
    # Notification methods
    async def _notify_weather_change(self, bot, weather_type: str, decision: GameMasterDecision):
        """Thông báo thay đổi thời tiết"""
        try:
            embed = discord.Embed(
                title="🌤️ Gemini Game Master - Thay đổi thời tiết",
                description=f"**Thời tiết mới:** {weather_type}\n**Lý do:** {decision.reasoning}",
                color=0x00ff00
            )
            embed.add_field(name="Confidence", value=f"{decision.confidence:.1%}", inline=True)
            embed.add_field(name="Priority", value=decision.priority.upper(), inline=True)
            embed.set_footer(text=f"Game Master Decision ID: {decision.decision_id}")
            
            await self._send_notification_to_all_guilds(bot, embed)
            
        except Exception as e:
            logger.error(f"Error sending weather notification: {e}")
    
    async def _send_notification_to_all_guilds(self, bot, embed):
        """Gửi thông báo tới tất cả guild"""
        try:
            for guild in bot.guilds:
                try:
                    # Tìm channel phù hợp để gửi
                    target_channel = None
                    for channel in guild.text_channels:
                        if channel.permissions_for(guild.me).send_messages:
                            if any(name in channel.name.lower() for name in ['general', 'announce', 'bot', 'notification']):
                                target_channel = channel
                                break
                    
                    if not target_channel:
                        for channel in guild.text_channels:
                            if channel.permissions_for(guild.me).send_messages:
                                target_channel = channel
                                break
                    
                    if target_channel:
                        await target_channel.send(embed=embed)
                        await asyncio.sleep(1)  # Rate limit protection
                        
                except Exception as e:
                    logger.warning(f"Could not send notification to guild {guild.name}: {e}")
                    
        except Exception as e:
            logger.error(f"Error sending notifications: {e}")
    
    # Record keeping methods
    async def record_decision(self, decision: GameMasterDecision):
        """Ghi lại quyết định"""
        try:
            conn = await self.db.get_connection()
            await conn.execute("""
                INSERT INTO game_master_decisions 
                (decision_id, action_type, reasoning, confidence, parameters, execution_time, priority, affected_users, created_at, executed)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                decision.decision_id, decision.action_type, decision.reasoning, decision.confidence,
                json.dumps(decision.parameters), decision.execution_time.isoformat(), decision.priority,
                json.dumps(decision.affected_users), datetime.now().isoformat(), True
            ))
            await conn.commit()
            
        except Exception as e:
            logger.error(f"Error recording decision: {e}")
    
    async def save_game_state_snapshot(self, snapshot: GameStateSnapshot):
        """Lưu snapshot game state"""
        try:
            conn = await self.db.get_connection()
            await conn.execute("""
                INSERT INTO game_state_snapshots (timestamp, snapshot_data, health_score, created_at)
                VALUES (?, ?, ?, ?)
            """, (
                snapshot.timestamp.isoformat(), json.dumps(snapshot.__dict__, default=str), 
                snapshot.game_balance_score, datetime.now().isoformat()
            ))
            await conn.commit()
            
        except Exception as e:
            logger.error(f"Error saving game state snapshot: {e}")
    
    async def validate_decision(self, decision: GameMasterDecision, game_state: GameStateSnapshot) -> bool:
        """Validate quyết định trước khi thực thi"""
        try:
            # Check confidence threshold
            if decision.confidence < self.config['min_confidence_threshold']:
                logger.warning(f"Decision confidence too low: {decision.confidence}")
                return False
            
            # Check decision rate limit
            recent_decisions = [d for d in self.decision_history 
                             if datetime.now() - d.timestamp < timedelta(hours=1)]
            if len(recent_decisions) >= self.config['max_decisions_per_hour']:
                logger.warning("Decision rate limit exceeded")
                return False
            
            # Validate parameters based on action type
            if decision.action_type == "weather_control":
                valid_weather = ['sunny', 'rainy', 'storm', 'drought', 'windy']
                if decision.parameters.get('weather_type') not in valid_weather:
                    logger.warning("Invalid weather type")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating decision: {e}")
            return False
    
    async def analyze_user_behavior_patterns(self, bot) -> Dict[str, Any]:
        """Phân tích pattern hành vi người dùng"""
        try:
            all_users = await self.db.get_all_users()
            
            patterns = {
                'high_activity': [],
                'low_activity': [],
                'new_users': [],
                'inactive_users': [],
                'big_spenders': [],
                'savers': []
            }
            
            current_time = datetime.now()
            
            for user in all_users:
                user_id = user.get('user_id')
                money = user.get('money', 0)
                last_seen = user.get('last_seen', current_time)
                joined = user.get('joined_date', current_time)
                
                # Activity patterns
                if current_time - last_seen < timedelta(hours=1):
                    patterns['high_activity'].append(user_id)
                elif current_time - last_seen > timedelta(days=7):
                    patterns['inactive_users'].append(user_id)
                else:
                    patterns['low_activity'].append(user_id)
                
                # New users (joined in last 24h)
                if current_time - joined < timedelta(hours=24):
                    patterns['new_users'].append(user_id)
                
                # Money patterns
                if money > 50000:
                    patterns['big_spenders'].append(user_id)
                elif money > 10000:
                    patterns['savers'].append(user_id)
            
            return patterns
            
        except Exception as e:
            logger.error(f"Error analyzing user patterns: {e}")
            return {}
    
    async def evaluate_game_health(self, game_state: GameStateSnapshot, user_patterns: Dict) -> float:
        """Đánh giá sức khỏe tổng thể game"""
        try:
            # Tính các metric
            activity_score = game_state.active_players_15min / max(1, game_state.total_players)
            economic_score = game_state.economic_health_score
            balance_score = game_state.game_balance_score
            engagement_score = game_state.player_satisfaction
            
            # Penalty cho các vấn đề nghiêm trọng
            penalties = 0
            if game_state.inflation_rate > 0.15:  # Lạm phát quá cao
                penalties += 0.2
            if activity_score < 0.1:  # Hoạt động quá thấp
                penalties += 0.3
            if len(user_patterns.get('inactive_users', [])) > game_state.total_players * 0.5:  # Quá nhiều user inactive
                penalties += 0.2
            
            # Tổng điểm sức khỏe
            health_score = (activity_score * 0.3 + economic_score * 0.3 + 
                          balance_score * 0.2 + engagement_score * 0.2) - penalties
            
            return max(0.0, min(1.0, health_score))
            
        except Exception as e:
            logger.error(f"Error evaluating game health: {e}")
            return 0.5
    
    # Additional execution methods
    async def _set_master_weather(self, weather_cog, weather_type: str, duration_hours: int, decision: GameMasterDecision) -> bool:
        """Set weather thông qua Game Master"""
        try:
            # Use the new set_weather method from WeatherCog
            duration_minutes = duration_hours * 60
            success = await weather_cog.set_weather(
                weather_type=weather_type,
                duration_minutes=duration_minutes,
                source="Gemini Game Master"
            )
            
            if success:
                logger.info(f"🌤️ Gemini Game Master set weather: {weather_type} for {duration_hours}h")
                return True
            else:
                logger.error("Failed to set weather through WeatherCog.set_weather")
                return False
                
        except Exception as e:
            logger.error(f"Error setting weather: {e}")
            return False
    
    async def _start_master_event(self, events_cog, event_data: Dict, decision: GameMasterDecision) -> bool:
        """Tạo sự kiện thông qua Game Master"""
        try:
            # Set event in events cog
            if hasattr(events_cog, 'start_custom_event'):
                await events_cog.start_custom_event(event_data)
                logger.info(f"🎉 Game Master started event: {event_data['name']}")
                return True
            elif hasattr(events_cog, 'current_event'):
                events_cog.current_event = event_data
                events_cog.current_event['start_time'] = datetime.now()
                events_cog.current_event['end_time'] = datetime.now() + timedelta(hours=event_data['duration_hours'])
                logger.info(f"🎉 Game Master created event: {event_data['name']}")
                return True
            else:
                logger.error("Events cog doesn't have expected methods")
                return False
                
        except Exception as e:
            logger.error(f"Error starting event: {e}")
            return False
    
    async def _execute_money_redistribution(self, params: Dict, bot) -> bool:
        """Thực thi phân phối lại tiền"""
        try:
            redistribution_type = params.get('type', 'robin_hood')  # robin_hood, universal_basic, wealth_cap
            
            if redistribution_type == 'robin_hood':
                # Lấy từ người giàu cho người nghèo
                wealth_threshold = params.get('wealth_threshold', 100000)
                redistribution_rate = params.get('rate', 0.1)  # 10%
                
                all_users = await self.db.get_all_users()
                rich_users = [u for u in all_users if u.get('money', 0) > wealth_threshold]
                poor_users = [u for u in all_users if u.get('money', 0) < wealth_threshold / 2]
                
                if not rich_users or not poor_users:
                    return False
                
                total_redistributed = 0
                for user in rich_users:
                    tax_amount = int(user.get('money', 0) * redistribution_rate)
                    user_obj = await self.db.get_user(user['user_id'])
                    if user_obj:
                        user_obj.money -= tax_amount
                        await self.db.update_user(user_obj)
                        total_redistributed += tax_amount
                
                # Phân phối cho người nghèo
                per_person = total_redistributed // len(poor_users)
                for user in poor_users:
                    user_obj = await self.db.get_user(user['user_id'])
                    if user_obj:
                        user_obj.money += per_person
                        await self.db.update_user(user_obj)
                
                logger.info(f"💰 Game Master redistributed {total_redistributed:,} coins from {len(rich_users)} to {len(poor_users)} users")
                return True
                
            elif redistribution_type == 'universal_basic':
                # Universal Basic Income
                amount_per_person = params.get('amount', 5000)
                all_users = await self.db.get_all_users()
                
                for user in all_users:
                    try:
                        user_obj = await self.db.get_user(user['user_id'])
                        if user_obj:
                            user_obj.money += amount_per_person
                            await self.db.update_user(user_obj)
                    except Exception as e:
                        logger.error(f"Error giving UBI to user {user['user_id']}: {e}")
                        continue
                
                logger.info(f"💰 Game Master gave {amount_per_person:,} coins to {len(all_users)} users (UBI)")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error in money redistribution: {e}")
            return False
    
    async def _execute_inflation_control(self, params: Dict, bot) -> bool:
        """Thực thi kiểm soát lạm phát"""
        try:
            control_type = params.get('type', 'price_adjustment')
            
            if control_type == 'price_adjustment':
                # Điều chỉnh giá để chống lạm phát
                from utils.pricing import pricing_coordinator
                
                deflation_rate = params.get('deflation_rate', 0.9)  # Giảm 10%
                crops_affected = params.get('crops', 'all')
                
                success = pricing_coordinator.apply_ai_price_adjustment(
                    crop_type=crops_affected,
                    sell_price_modifier=deflation_rate,
                    seed_price_modifier=deflation_rate,
                    reasoning="Game Master: Inflation control measure",
                    duration_hours=params.get('duration_hours', 6)
                )
                
                if success:
                    logger.info(f"💹 Game Master applied deflation: {(1-deflation_rate)*100:.1f}% price reduction")
                    return True
                
            elif control_type == 'money_sink':
                # Tạo money sink event
                sink_event = {
                    'name': 'Tax Collection Event',
                    'description': 'Chính phủ thu thuế để kiểm soát lạm phát',
                    'type': 'tax',
                    'tax_rate': params.get('tax_rate', 0.05),  # 5%
                    'duration_hours': params.get('duration_hours', 12)
                }
                
                events_cog = bot.get_cog('EventsCog')
                if events_cog:
                    return await self._start_master_event(events_cog, sink_event, None)
            
            return False
            
        except Exception as e:
            logger.error(f"Error in inflation control: {e}")
            return False
    
    async def _execute_economic_boost(self, params: Dict, bot) -> bool:
        """Thực thi kích thích kinh tế"""
        try:
            boost_type = params.get('type', 'bonus_event')
            
            if boost_type == 'bonus_event':
                # Tạo sự kiện bonus
                bonus_event = {
                    'name': params.get('event_name', 'Economic Stimulus Event'),
                    'description': params.get('description', 'Sự kiện kích thích kinh tế từ Game Master'),
                    'type': 'bonus',
                    'bonus_multiplier': params.get('bonus_multiplier', 1.5),
                    'duration_hours': params.get('duration_hours', 4),
                    'rewards': {
                        'money_multiplier': params.get('money_multiplier', 2.0),
                        'exp_multiplier': params.get('exp_multiplier', 1.5)
                    }
                }
                
                events_cog = bot.get_cog('EventsCog')
                if events_cog:
                    return await self._start_master_event(events_cog, bonus_event, None)
                    
            elif boost_type == 'market_boost':
                # Tăng giá bán để khuyến khích hoạt động
                from utils.pricing import pricing_coordinator
                
                boost_rate = params.get('boost_rate', 1.3)  # Tăng 30%
                
                success = pricing_coordinator.apply_ai_price_adjustment(
                    crop_type='all',
                    sell_price_modifier=boost_rate,
                    seed_price_modifier=1.0,  # Không thay đổi giá hạt giống
                    reasoning="Game Master: Economic stimulus - higher crop prices",
                    duration_hours=params.get('duration_hours', 3)
                )
                
                if success:
                    logger.info(f"📈 Game Master applied market boost: {(boost_rate-1)*100:.1f}% price increase")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error in economic boost: {e}")
            return False
    
    # Additional notification methods
    async def _notify_event_start(self, bot, event_data: Dict, decision: GameMasterDecision):
        """Thông báo sự kiện mới"""
        try:
            embed = discord.Embed(
                title="🎉 Gemini Game Master - Sự kiện mới!",
                description=f"**{event_data['name']}**\n{event_data['description']}",
                color=0xff6b6b
            )
            embed.add_field(name="Thời gian", value=f"{event_data['duration_hours']} giờ", inline=True)
            embed.add_field(name="Lý do", value=decision.reasoning, inline=False)
            embed.set_footer(text=f"Game Master Decision ID: {decision.decision_id}")
            
            await self._send_notification_to_all_guilds(bot, embed)
            
        except Exception as e:
            logger.error(f"Error sending event notification: {e}")
    
    async def _notify_market_change(self, bot, crop_type: str, sell_modifier: float, seed_modifier: float, decision: GameMasterDecision):
        """Thông báo thay đổi thị trường"""
        try:
            sell_change = f"{(sell_modifier-1)*100:+.1f}%" if sell_modifier != 1.0 else "Không đổi"
            seed_change = f"{(seed_modifier-1)*100:+.1f}%" if seed_modifier != 1.0 else "Không đổi"
            
            embed = discord.Embed(
                title="💰 Gemini Game Master - Điều chỉnh thị trường",
                description=f"**Cây trồng:** {crop_type}\n**Lý do:** {decision.reasoning}",
                color=0x4ecdc4
            )
            embed.add_field(name="Giá bán", value=sell_change, inline=True)
            embed.add_field(name="Giá hạt giống", value=seed_change, inline=True)
            embed.set_footer(text=f"Game Master Decision ID: {decision.decision_id}")
            
            await self._send_notification_to_all_guilds(bot, embed)
            
        except Exception as e:
            logger.error(f"Error sending market notification: {e}")
    
    async def _notify_user_rewards(self, bot, reward_type: str, rewards_given: int, decision: GameMasterDecision):
        """Thông báo thưởng người dùng"""
        try:
            embed = discord.Embed(
                title="🎁 Gemini Game Master - Phần thưởng!",
                description=f"**Loại thưởng:** {reward_type}\n**Số người nhận:** {rewards_given}\n**Lý do:** {decision.reasoning}",
                color=0xf7b733
            )
            embed.set_footer(text=f"Game Master Decision ID: {decision.decision_id}")
            
            await self._send_notification_to_all_guilds(bot, embed)
            
        except Exception as e:
            logger.error(f"Error sending rewards notification: {e}")
    
    # Status and admin methods
    async def get_status(self) -> Dict[str, Any]:
        """Lấy trạng thái Game Master"""
        try:
            current_time = datetime.now()
            recent_decisions = [d for d in self.decision_history 
                             if current_time - d.timestamp < timedelta(hours=24)]
            
            return {
                'enabled': self.enabled,
                'emergency_mode': self.emergency_mode,
                'last_analysis': self.last_analysis_time.isoformat() if self.last_analysis_time else None,
                'total_decisions': len(self.decision_history),
                'decisions_24h': len(recent_decisions),
                'analysis_interval_minutes': self.config['analysis_interval_minutes'],
                'next_analysis_eta': (self.last_analysis_time + timedelta(minutes=self.config['analysis_interval_minutes']) - current_time).total_seconds() / 60 if self.last_analysis_time else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting Game Master status: {e}")
            return {}
    
    async def get_recent_decisions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Lấy quyết định gần đây"""
        try:
            recent = sorted(self.decision_history, key=lambda x: x.timestamp, reverse=True)[:limit]
            return [
                {
                    'decision_id': d.decision_id,
                    'action_type': d.action_type,
                    'reasoning': d.reasoning,
                    'confidence': d.confidence,
                    'priority': d.priority,
                    'timestamp': d.timestamp.isoformat()
                }
                for d in recent
            ]
        except Exception as e:
            logger.error(f"Error getting recent decisions: {e}")
            return []
    
    def enable(self):
        """Bật Game Master"""
        self.enabled = True
        logger.info("🎮 Gemini Game Master ENABLED")
    
    def disable(self):
        """Tắt Game Master"""
        self.enabled = False
        logger.info("🔒 Gemini Game Master DISABLED")
    
    def toggle_emergency_mode(self):
        """Chuyển đổi emergency mode"""
        self.emergency_mode = not self.emergency_mode
        if self.emergency_mode:
            self.config['analysis_interval_minutes'] = 5  # Phân tích mỗi 5 phút trong emergency
            self.config['max_decisions_per_hour'] = 20   # Cho phép nhiều quyết định hơn
            logger.warning("🚨 Gemini Game Master: EMERGENCY MODE ACTIVATED")
        else:
            self.config['analysis_interval_minutes'] = 15  # Trở về 15 phút
            self.config['max_decisions_per_hour'] = 8     # Giới hạn bình thường
            logger.info("✅ Gemini Game Master: Emergency mode deactivated")
    
    async def force_analysis(self, bot) -> Optional[GameMasterDecision]:
        """Ép buộc phân tích ngay lập tức"""
        old_time = self.last_analysis_time
        self.last_analysis_time = None  # Reset để bypass cooldown
        
        try:
            decision = await self.analyze_and_control(bot)
            logger.info("🔧 Game Master: Force analysis completed")
            return decision
        except Exception as e:
            logger.error(f"Error in force analysis: {e}")
            self.last_analysis_time = old_time  # Restore nếu có lỗi
            return None 