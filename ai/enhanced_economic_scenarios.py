#!/usr/bin/env python3
"""
Enhanced Economic Scenarios - Hệ thống tình huống kinh tế đa dạng
Tạo ra nhiều scenarios phong phú để đưa vào smart_cache.json
"""

import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass, asdict
from utils.enhanced_logging import get_bot_logger

logger = get_bot_logger()

@dataclass
class EconomicScenario:
    """Định nghĩa một tình huống kinh tế"""
    pattern: str
    name: str
    description: str
    triggers: Dict[str, Any]
    decision: Dict[str, Any]
    frequency: str  # common, uncommon, rare, legendary
    season_preference: List[str]  # spring, summer, autumn, winter, all
    player_count_range: Tuple[int, int]
    economic_health_range: Tuple[float, float]

class EnhancedEconomicScenarios:
    """Quản lý tình huống kinh tế đa dạng"""
    
    def __init__(self):
        self.scenarios = self._create_scenario_database()
        self.seasonal_events = self._create_seasonal_events()
        self.crisis_scenarios = self._create_crisis_scenarios()
        self.prosperity_scenarios = self._create_prosperity_scenarios()
        self.market_manipulation_scenarios = self._create_market_scenarios()
        
    def _create_scenario_database(self) -> List[EconomicScenario]:
        """Tạo database với hơn 50 scenarios đa dạng"""
        scenarios = []
        
        # === MORNING SCENARIOS (6AM - 12PM) ===
        scenarios.extend([
            EconomicScenario(
                pattern="high-good-medium-sunny-morning-balanced",
                name="🌅 Bình Minh Vàng Son",
                description="Ánh nặng ban mai tạo điều kiện lý tương cho nông nghiệp",
                triggers={"time": "morning", "weather": "sunny", "health": "good"},
                decision={
                    "action_type": "WEATHER_ENHANCEMENT",
                    "reasoning": "Thời tiết thuận lợi buổi sáng tạo cơ hội tăng năng suất cây trồng. Nên tận dụng momentum này.",
                    "confidence": 0.85,
                    "parameters": {
                        "weather_type": "sunny",
                        "growth_boost": 1.25,
                        "duration_hours": 6,
                        "crop_types": ["all"]
                    },
                    "expected_impact": "Tăng 25% tốc độ sinh trưởng cho tất cả cây trồng trong 6 giờ",
                    "priority": "medium"
                },
                frequency="common",
                season_preference=["spring", "summer"],
                player_count_range=(10, 100),
                economic_health_range=(0.6, 1.0)
            ),
            
            EconomicScenario(
                pattern="medium-fair-high-cloudy-morning-unbalanced",
                name="☁️ Sương Mù Kì Bí",
                description="Lớp sương mù dày đặc che phủ nông trại, tạo điều kiện đặc biệt",
                triggers={"time": "morning", "weather": "cloudy", "player_mood": "neutral"},
                decision={
                    "action_type": "EVENT_TRIGGER", 
                    "reasoning": "Sương mù tạo điều kiện lý tưởng cho nấm và cây ăn lá. Cơ hội kiếm tiền hiếm có.",
                    "confidence": 0.9,
                    "parameters": {
                        "event_name": "🍄 Mùa Nấm Bí Ẩn",
                        "description": "Sương mù dày đặc giúp nấm mọc dày đặc! Giá nấm tăng 200%",
                        "effect_type": "crop_price_bonus",
                        "target_crops": ["mushroom", "lettuce", "spinach"],
                        "multiplier": 3.0,
                        "duration_hours": 8,
                        "rarity": "rare"
                    },
                    "expected_impact": "Tăng mạnh thu nhập từ cây ăn lá và nấm",
                    "priority": "high"
                },
                frequency="rare",
                season_preference=["autumn", "winter"],
                player_count_range=(20, 200),
                economic_health_range=(0.3, 0.8)
            )
        ])
        
        # === AFTERNOON SCENARIOS (12PM - 6PM) ===
        scenarios.extend([
            EconomicScenario(
                pattern="high-good-low-sunny-afternoon-balanced",
                name="☀️ Nắng Vàng Cháy",
                description="Nắng gắt buổi trưa thử thách sức bền của nông dân",
                triggers={"time": "afternoon", "weather": "sunny", "temperature": "high"},
                decision={
                    "action_type": "CHALLENGE_EVENT",
                    "reasoning": "Nắng gắt tạo thách thức nhưng cũng có cơ hội. Cây chịu nắng sẽ phát triển mạnh.",
                    "confidence": 0.8,
                    "parameters": {
                        "event_name": "🔥 Thử Thách Nắng Gắt",
                        "description": "Nắng cực gắt! Cây chịu hạn phát triển 150%, cây khác chậm 25%",
                        "effect_type": "selective_growth",
                        "bonus_crops": ["tomato", "corn", "chili"],
                        "bonus_multiplier": 1.5,
                        "penalty_crops": ["lettuce", "cabbage"],
                        "penalty_multiplier": 0.75,
                        "duration_hours": 4
                    },
                    "expected_impact": "Khuyến khích đa dạng hóa cây trồng và chiến thuật farming",
                    "priority": "medium"
                },
                frequency="common",
                season_preference=["summer"],
                player_count_range=(5, 50),
                economic_health_range=(0.4, 0.9)
            ),
            
            EconomicScenario(
                pattern="low-poor-medium-rainy-afternoon-unbalanced", 
                name="🌧️ Cơn Mưa Cứu Tinh",
                description="Cơn mưa xuất hiện đúng lúc khi nông dân đang khó khăn",
                triggers={"economic_health": "poor", "weather": "rainy", "time": "afternoon"},
                decision={
                    "action_type": "RECOVERY_EVENT",
                    "reasoning": "Kinh tế đang khó khăn, cần sự kiện phục hồi để giúp người chơi. Mưa mang lại hy vọng mới.",
                    "confidence": 0.95,
                    "parameters": {
                        "event_name": "💧 Hồi Sinh Đất Đai",
                        "description": "Cơn mưa phù sa mang lại dinh dưỡng! Tất cả cây trồng tăng 200% yield",
                        "effect_type": "yield_boost",
                        "multiplier": 3.0,
                        "duration_hours": 12,
                        "additional_effects": {
                            "free_seeds": 10,
                            "reduced_costs": 0.5
                        }
                    },
                    "expected_impact": "Phục hồi kinh tế player, tăng motivation farming",
                    "priority": "critical"
                },
                frequency="uncommon",
                season_preference=["spring", "autumn"],
                player_count_range=(3, 30),
                economic_health_range=(0.1, 0.5)
            )
        ])
        
        # === EVENING SCENARIOS (6PM - 11PM) ===
        scenarios.extend([
            EconomicScenario(
                pattern="medium-fair-high-clear-evening-balanced",
                name="🌅 Hoàng Hôn Cát Tường",
                description="Hoàng hôn đẹp mang lại cảm hứng và may mắn cho nông dân",
                triggers={"time": "evening", "weather": "clear", "mood": "positive"},
                decision={
                    "action_type": "LUCK_EVENT",
                    "reasoning": "Hoàng hôn đẹp tạo tâm trạng tích cực. Thời điểm tốt cho sự kiện may mắn.",
                    "confidence": 0.88,
                    "parameters": {
                        "event_name": "🍀 Điều Ước Hoàng Hôn",
                        "description": "Hoàng hôn cát tường! 25% cơ hội nhận double coins khi harvest",
                        "effect_type": "luck_bonus",
                        "probability": 0.25,
                        "bonus_type": "double_coins",
                        "duration_hours": 6,
                        "activation": "on_harvest"
                    },
                    "expected_impact": "Tăng excitement và reward cho người chơi active",
                    "priority": "medium"
                },
                frequency="uncommon",
                season_preference=["summer", "autumn"],
                player_count_range=(15, 80),
                economic_health_range=(0.5, 0.9)
            ),
            
            EconomicScenario(
                pattern="high-good-medium-windy-evening-concentrated",
                name="💨 Gió Thổi Của Cải",
                description="Gió mạnh mang theo cơ hội kinh doanh từ vùng xa",
                triggers={"time": "evening", "weather": "windy", "distribution": "concentrated"},
                decision={
                    "action_type": "MARKET_EVENT",
                    "reasoning": "Phân phối tiền tập trung ở người giàu. Cần event để lan tỏa richness ra community.",
                    "confidence": 0.82,
                    "parameters": {
                        "event_name": "💰 Thương Gia Xa Xứ",
                        "description": "Thương gia từ vùng xa đến mua nông sản! Giá mua +50%, nhưng chỉ 3 người đầu tiên",
                        "effect_type": "limited_bonus",
                        "price_multiplier": 1.5,
                        "participant_limit": 3,
                        "duration_hours": 2,
                        "first_come_first_serve": True
                    },
                    "expected_impact": "Tạo cạnh tranh lành mạnh, khuyến khích người chơi active",
                    "priority": "high"
                },
                frequency="rare",
                season_preference=["all"],
                player_count_range=(10, 60),
                economic_health_range=(0.6, 1.0)
            )
        ])
        
        # === NIGHT SCENARIOS (11PM - 6AM) ===
        scenarios.extend([
            EconomicScenario(
                pattern="low-fair-low-clear-night-balanced",
                name="🌙 Ánh Trăng Thần Bí", 
                description="Ánh trăng sáng tạo ra hiện tượng kỳ lạ trong nông trại",
                triggers={"time": "night", "weather": "clear", "moon_phase": "full"},
                decision={
                    "action_type": "MYSTICAL_EVENT",
                    "reasoning": "Ít người chơi active ban đêm, nhưng trăng tròn tạo cơ hội đặc biệt cho night owls.",
                    "confidence": 0.9,
                    "parameters": {
                        "event_name": "✨ Phép Thuật Ánh Trăng",
                        "description": "Ánh trăng biến cây trồng thành phiên bản premium! +300% giá trị",
                        "effect_type": "transformation",
                        "transform_chance": 0.15,
                        "value_multiplier": 4.0,
                        "duration_hours": 8,
                        "night_only": True
                    },
                    "expected_impact": "Reward cho người chơi thức khuya, tạo unique experience",
                    "priority": "high"
                },
                frequency="legendary",
                season_preference=["all"],
                player_count_range=(1, 15),
                economic_health_range=(0.3, 0.8)
            ),
            
            EconomicScenario(
                pattern="medium-poor-medium-stormy-night-unbalanced",
                name="⛈️ Bão Tố Kinh Hoàng",
                description="Cơn bão dữ dội tấn công trong đêm, đe dọa mọi thứ",
                triggers={"time": "night", "weather": "stormy", "health": "poor"},
                decision={
                    "action_type": "CRISIS_EVENT",
                    "reasoning": "Kinh tế yếu + bão đêm = crisis. Cần event dramatic để test player resilience.",
                    "confidence": 0.92,
                    "parameters": {
                        "event_name": "💀 Thảm Họa Tự Nhiên",
                        "description": "Bão tố phá hủy 50% cây trồng! Nhưng ai survive sẽ nhận bonus 5x",
                        "effect_type": "high_risk_high_reward",
                        "destruction_rate": 0.5,
                        "survivor_bonus": 5.0,
                        "duration_hours": 6,
                        "requires_action": True,
                        "action_type": "protect_crops"
                    },
                    "expected_impact": "Tạo drama và excitement, test player commitment",
                    "priority": "critical"
                },
                frequency="rare",
                season_preference=["autumn", "winter"],
                player_count_range=(5, 40),
                economic_health_range=(0.1, 0.6)
            )
        ])
        
        return scenarios
    
    def _create_seasonal_events(self) -> Dict[str, List[Dict]]:
        """Tạo events theo mùa"""
        return {
            "spring": [
                {
                    "pattern": "any-any-any-any-spring-any",
                    "name": "🌸 Lễ Hội Hoa Anh Đào",
                    "description": "Mùa xuân nở hoa, du khách đến tham quan nông trại",
                    "effect": "tourist_bonus",
                    "multiplier": 1.4,
                    "duration": 24
                },
                {
                    "pattern": "any-any-any-rainy-spring-any", 
                    "name": "🌱 Mưa Phù Sa Màu Mỡ",
                    "description": "Mưa xuân mang phù sa, đất đai trở nên màu mỡ hơn",
                    "effect": "soil_improvement",
                    "bonus": "permanent_yield_+10%",
                    "duration": 168  # 1 tuần
                }
            ],
            "summer": [
                {
                    "pattern": "any-any-any-sunny-summer-any",
                    "name": "☀️ Ngày Hè Rực Rỡ",
                    "description": "Nắng hè cháy mang lại năng lượng tối đa cho cây trồng",
                    "effect": "solar_boost",
                    "growth_speed": 2.0,
                    "duration": 12
                },
                {
                    "pattern": "any-any-any-hot-summer-any",
                    "name": "🔥 Sóng Nhiệt Cực Đoan",
                    "description": "Nhiệt độ cực cao, chỉ cây chịu hạn mới survive",
                    "effect": "heat_challenge",
                    "resistant_crops": ["cactus", "corn", "tomato"],
                    "bonus": 3.0,
                    "duration": 8
                }
            ],
            "autumn": [
                {
                    "pattern": "any-any-any-any-autumn-any",
                    "name": "🍂 Mùa Thu Vàng Óng",
                    "description": "Mùa thu đến, thời điểm vàng của nông nghiệp",
                    "effect": "harvest_festival",
                    "all_crops_bonus": 1.5,
                    "duration": 72  # 3 ngày
                },
                {
                    "pattern": "any-any-any-windy-autumn-any",
                    "name": "💨 Gió Thu Mang Lá Vàng",
                    "description": "Gió thu thổi bay hạt giống đặc biệt từ xa",
                    "effect": "seed_rain",
                    "free_rare_seeds": 5,
                    "duration": 6
                }
            ],
            "winter": [
                {
                    "pattern": "any-any-any-cold-winter-any",
                    "name": "❄️ Mùa Đông Băng Giá",
                    "description": "Băng tuyết phủ trắng, chỉ cây chịu lạnh mới phát triển",
                    "effect": "winter_survival",
                    "cold_resistant_bonus": 2.5,
                    "duration": 24
                },
                {
                    "pattern": "any-any-any-snowy-winter-any",
                    "name": "⛄ Tuyết Rơi Ma Thuật",
                    "description": "Tuyết ma thuật làm đất đai màu mỡ cho năm tới",
                    "effect": "snow_blessing",
                    "next_season_bonus": 1.2,
                    "duration": 48
                }
            ]
        }
    
    def _create_crisis_scenarios(self) -> List[Dict]:
        """Tạo scenarios khủng hoảng kinh tế"""
        return [
            {
                "pattern": "low-poor-any-any-any-concentrated",
                "name": "📉 Khủng Hoảng Kinh Tế",
                "description": "Nền kinh tế suy thoái, cần biện pháp khẩn cấp",
                "triggers": {"health": "<0.3", "activity": "<0.3"},
                "solutions": [
                    {
                        "type": "emergency_stimulus",
                        "action": "give_all_players_money",
                        "amount": 5000,
                        "reason": "Gói cứu trợ khẩn cấp từ chính phủ"
                    },
                    {
                        "type": "mega_event", 
                        "action": "super_harvest_festival",
                        "duration": 48,
                        "multiplier": 3.0
                    }
                ]
            },
            {
                "pattern": "any-poor-low-stormy-any-unbalanced",
                "name": "🌪️ Siêu Bão Tàn Phá",
                "description": "Thiên tai tàn phá nặng nề, cộng đồng phải đoàn kết",
                "triggers": {"weather": "stormy", "health": "<0.4"},
                "solutions": [
                    {
                        "type": "community_effort",
                        "action": "rebuild_together",
                        "reward": "collective_bonus",
                        "requirement": "min_participants: 10"
                    }
                ]
            }
        ]
    
    def _create_prosperity_scenarios(self) -> List[Dict]:
        """Tạo scenarios thịnh vượng"""
        return [
            {
                "pattern": "high-good-high-sunny-any-balanced",
                "name": "🏆 Thời Đại Hoàng Kim",
                "description": "Nền kinh tế phát triển mạnh, mọi người đều thịnh vượng",
                "triggers": {"health": ">0.8", "activity": ">0.8", "balance": "good"},
                "effects": [
                    {
                        "type": "golden_age_bonus",
                        "all_activities": 1.5,
                        "duration": 72,
                        "special_rewards": True
                    }
                ]
            },
            {
                "pattern": "high-good-medium-any-any-balanced",
                "name": "💎 Phát Hiện Kho Báu",
                "description": "Phát hiện kho báu cổ đại trong đất nông trại",
                "triggers": {"health": ">0.7", "luck_factor": ">0.9"},
                "effects": [
                    {
                        "type": "treasure_discovery",
                        "rare_items": ["diamond_seeds", "golden_tools"],
                        "coin_bonus": 50000,
                        "duration": 24
                    }
                ]
            }
        ]
    
    def _create_market_scenarios(self) -> List[Dict]:
        """Tạo scenarios thao túng thị trường"""
        return [
            {
                "pattern": "medium-fair-high-any-any-concentrated",
                "name": "📈 Thao Túng Thị Trường",
                "description": "Các nhà đầu tư lớn thao túng giá cả nông sản",
                "effects": [
                    {
                        "type": "price_manipulation",
                        "random_crop_spike": {"multiplier": "2-5x", "duration": 2},
                        "warning": "Giá có thể thay đổi bất ngờ!"
                    }
                ]
            },
            {
                "pattern": "high-good-any-any-any-unbalanced",
                "name": "🚀 Bọt Kinh Tế",
                "description": "Thị trường quá sôi động, có nguy cơ bong bóng",
                "effects": [
                    {
                        "type": "bubble_warning",
                        "temporary_super_bonus": 5.0,
                        "crash_risk": 0.3,
                        "duration": 4
                    }
                ]
            }
        ]
    
    def generate_hourly_scenarios(self, current_cache: Dict) -> Dict[str, Any]:
        """Tạo scenarios mới cho từng giờ"""
        current_time = datetime.now()
        hour = current_time.hour
        season = self._get_current_season()
        
        # Xác định time period
        if 6 <= hour < 12:
            time_period = "morning"
        elif 12 <= hour < 18:
            time_period = "afternoon" 
        elif 18 <= hour < 23:
            time_period = "evening"
        else:
            time_period = "night"
        
        # Lọc scenarios phù hợp với thời gian hiện tại
        suitable_scenarios = [
            s for s in self.scenarios
            if time_period in s.pattern or "any" in s.pattern
        ]
        
        # Thêm seasonal scenarios
        if season in self.seasonal_events:
            seasonal = self.seasonal_events[season]
            suitable_scenarios.extend([
                self._convert_seasonal_to_scenario(s) for s in seasonal
            ])
        
        # Tạo 10-15 scenarios mới cho giờ này
        new_scenarios = {}
        for _ in range(random.randint(10, 15)):
            scenario = random.choice(suitable_scenarios)
            
            # Tạo variations
            variation = self._create_scenario_variation(scenario, time_period, season)
            pattern_key = f"{variation['pattern']}_{random.randint(1000, 9999)}"
            
            new_scenarios[pattern_key] = {
                "decision": variation["decision"],
                "created_at": current_time.isoformat(),
                "last_used": current_time.isoformat(),
                "usage_count": 0,
                "pattern": pattern_key,
                "scenario_type": variation.get("frequency", "common"),
                "time_generated": time_period,
                "season": season
            }
        
        return new_scenarios
    
    def _get_current_season(self) -> str:
        """Xác định mùa hiện tại"""
        month = datetime.now().month
        if month in [12, 1, 2]:
            return "winter"
        elif month in [3, 4, 5]:
            return "spring"
        elif month in [6, 7, 8]:
            return "summer"
        else:
            return "autumn"
    
    def _convert_seasonal_to_scenario(self, seasonal_event: Dict) -> EconomicScenario:
        """Chuyển đổi seasonal event thành scenario"""
        return EconomicScenario(
            pattern=seasonal_event["pattern"],
            name=seasonal_event["name"],
            description=seasonal_event["description"],
            triggers={},
            decision={
                "action_type": "SEASONAL_EVENT",
                "reasoning": seasonal_event["description"],
                "confidence": 0.9,
                "parameters": seasonal_event,
                "expected_impact": "Seasonal bonus effect",
                "priority": "medium"
            },
            frequency="seasonal",
            season_preference=["all"],
            player_count_range=(1, 1000),
            economic_health_range=(0.0, 1.0)
        )
    
    def _create_scenario_variation(self, base_scenario: EconomicScenario, time_period: str, season: str) -> Dict:
        """Tạo variation của scenario để tăng độ đa dạng"""
        variation = asdict(base_scenario)
        
        # Điều chỉnh parameters dựa trên thời gian
        if time_period == "night":
            # Giảm số người tham gia, tăng reward
            if "multiplier" in variation["decision"]["parameters"]:
                variation["decision"]["parameters"]["multiplier"] *= 1.5
            variation["decision"]["parameters"]["night_bonus"] = True
            
        elif time_period == "morning":
            # Tăng duration cho morning events
            if "duration_hours" in variation["decision"]["parameters"]:
                variation["decision"]["parameters"]["duration_hours"] += 2
                
        # Điều chỉnh theo mùa
        seasonal_multipliers = {
            "spring": 1.2,  # Mùa sinh trưởng
            "summer": 1.3,  # Mùa cao điểm
            "autumn": 1.4,  # Mùa thu hoạch
            "winter": 0.8   # Mùa khó khăn
        }
        
        if "multiplier" in variation["decision"]["parameters"]:
            variation["decision"]["parameters"]["multiplier"] *= seasonal_multipliers.get(season, 1.0)
        
        # Thêm random factor
        random_factors = [
            "lucky_charm",
            "community_spirit", 
            "innovation_bonus",
            "tradition_blessing",
            "weather_luck"
        ]
        
        variation["decision"]["parameters"]["random_factor"] = random.choice(random_factors)
        variation["decision"]["parameters"]["randomness"] = random.uniform(0.8, 1.5)
        
        return variation
    
    def create_comprehensive_cache(self) -> Dict[str, Any]:
        """Tạo cache hoàn chỉnh với tất cả scenarios"""
        cache_data = {
            "decisions": {},
            "stats": {
                "hits": 0,
                "misses": 0,
                "tokens_saved": 0,
                "total_scenarios": 0,
                "last_update": datetime.now().isoformat(),
                "scenario_types": {
                    "common": 0,
                    "uncommon": 0,
                    "rare": 0,
                    "legendary": 0
                }
            },
            "metadata": {
                "version": "2.0",
                "generator": "EnhancedEconomicScenarios",
                "total_patterns": 0,
                "coverage": {
                    "time_periods": ["morning", "afternoon", "evening", "night"],
                    "seasons": ["spring", "summer", "autumn", "winter"],
                    "weather_types": ["sunny", "cloudy", "rainy", "stormy", "windy", "clear"],
                    "economic_states": ["poor", "fair", "good"],
                    "activity_levels": ["low", "medium", "high"],
                    "distribution_types": ["balanced", "unbalanced", "concentrated"]
                }
            }
        }
        
        # Tạo scenarios cho tất cả combinations
        all_scenarios = []
        all_scenarios.extend(self.scenarios)
        
        # Thêm seasonal events
        for season, events in self.seasonal_events.items():
            for event in events:
                all_scenarios.append(self._convert_seasonal_to_scenario(event))
        
        # Convert scenarios thành cache format
        for i, scenario in enumerate(all_scenarios):
            pattern_key = f"{scenario.pattern}_{i:04d}"
            
            cache_data["decisions"][pattern_key] = {
                "decision": scenario.decision,
                "created_at": datetime.now().isoformat(),
                "last_used": datetime.now().isoformat(),
                "usage_count": 0,
                "pattern": scenario.pattern,
                "scenario_metadata": {
                    "name": scenario.name,
                    "description": scenario.description,
                    "frequency": scenario.frequency,
                    "season_preference": scenario.season_preference,
                    "player_count_range": scenario.player_count_range,
                    "economic_health_range": scenario.economic_health_range
                }
            }
            
            # Update stats
            frequency = scenario.frequency if scenario.frequency in ["common", "uncommon", "rare", "legendary"] else "common"
            cache_data["stats"]["scenario_types"][frequency] += 1
        
        cache_data["stats"]["total_scenarios"] = len(all_scenarios)
        cache_data["metadata"]["total_patterns"] = len(cache_data["decisions"])
        
        return cache_data

    def get_random_scenario_for_state(self, economic_health: float, activity: float, 
                                    weather: str, time_period: str = None) -> Dict:
        """Lấy scenario ngẫu nhiên phù hợp với state hiện tại"""
        if not time_period:
            hour = datetime.now().hour
            if 6 <= hour < 12:
                time_period = "morning"
            elif 12 <= hour < 18:
                time_period = "afternoon" 
            elif 18 <= hour < 23:
                time_period = "evening"
            else:
                time_period = "night"
        
        # Lọc scenarios phù hợp
        suitable = [
            s for s in self.scenarios
            if (economic_health >= s.economic_health_range[0] and 
                economic_health <= s.economic_health_range[1])
        ]
        
        if suitable:
            chosen = random.choice(suitable)
            return asdict(chosen)
        
        # Fallback scenario
        return {
            "pattern": f"dynamic-{economic_health:.1f}-{activity:.1f}-{weather}-{time_period}",
            "decision": {
                "action_type": "ADAPTIVE_RESPONSE",
                "reasoning": f"Tình huống động: Sức khỏe kinh tế {economic_health:.1f}, hoạt động {activity:.1f}",
                "confidence": 0.7,
                "parameters": {
                    "adaptive": True,
                    "health_factor": economic_health,
                    "activity_factor": activity,
                    "weather_factor": weather,
                    "time_factor": time_period
                },
                "expected_impact": "Điều chỉnh linh hoạt theo tình hình",
                "priority": "medium"
            }
        }