import random
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass 
class SmartEvent:
    """AI-generated event with context"""
    name: str
    description: str
    effect_type: str
    effect_value: float
    duration_hours: int
    trigger_condition: str
    rarity: str  # common, rare, epic, legendary
    ai_reasoning: str

class EventManagerAI:
    """
    Event Manager AI - Creates and manages dynamic events
    
    This AI creates contextual events based on game state,
    player behavior, and timing to maintain engagement.
    """
    
    def __init__(self, database=None):
        self.db = database
        self.event_templates = self._load_event_templates()
        self.active_events = []
        self.event_history = []
        self.last_event_time = None
        
    async def load_ai_state(self):
        """Load AI Event Manager state từ database"""
        if not self.db:
            return
            
        try:
            # Load từ AI_SYSTEM_STATE với key 'event_manager'
            state_data = await self.db.get_bot_state_value('ai_system', 'event_manager')
            
            if state_data:
                # Restore last_event_time
                if state_data.get('last_event_time'):
                    self.last_event_time = datetime.fromisoformat(state_data['last_event_time'])
                
                # Restore event_history (limit to last 10 events)
                # Convert dict events back to SmartEvent objects
                if state_data.get('event_history'):
                    loaded_events = []
                    for event_data in state_data['event_history'][-10:]:
                        if isinstance(event_data, dict):
                            # Convert dict to SmartEvent
                            smart_event = SmartEvent(
                                name=event_data.get('name', 'Unknown Event'),
                                description=event_data.get('description', 'No description'),
                                effect_type=event_data.get('effect_type', 'unknown'),
                                effect_value=event_data.get('effect_value', 1.0),
                                duration_hours=event_data.get('duration_hours', 1),
                                trigger_condition=event_data.get('trigger_condition', 'unknown'),
                                rarity=event_data.get('rarity', 'common'),
                                ai_reasoning=event_data.get('ai_reasoning', 'Unknown')
                            )
                            loaded_events.append(smart_event)
                        else:
                            # Already a SmartEvent object
                            loaded_events.append(event_data)
                    
                    self.event_history = loaded_events
                
                logger.info(f"🤖 AI Event Manager state loaded - Last event: {self.last_event_time}")
            else:
                logger.info("🆕 No AI Event Manager state found, starting fresh")
                
        except Exception as e:
            logger.error(f"Error loading AI Event Manager state: {e}")
    
    async def save_ai_state(self):
        """Save AI Event Manager state vào database"""
        if not self.db:
            return
            
        try:
            state_data = {
                'last_event_time': self.last_event_time.isoformat() if self.last_event_time else None,
                'event_history': [
                    {
                        'name': event.name if hasattr(event, 'name') else event.get('name', 'Unknown Event'),
                        'effect_type': event.effect_type if hasattr(event, 'effect_type') else event.get('effect_type', 'unknown'),
                        'trigger_condition': event.trigger_condition if hasattr(event, 'trigger_condition') else event.get('trigger_condition', 'unknown'),
                        'rarity': event.rarity if hasattr(event, 'rarity') else event.get('rarity', 'common'),
                        'ai_reasoning': event.ai_reasoning if hasattr(event, 'ai_reasoning') else event.get('ai_reasoning', 'Unknown'),
                        'duration_hours': event.duration_hours if hasattr(event, 'duration_hours') else event.get('duration_hours', 1)
                    } for event in self.event_history[-10:] if event  # Keep last 10 events, skip None
                ],
                'last_updated': datetime.now().isoformat()
            }
            
            await self.db.set_bot_state_value('ai_system', 'event_manager', state_data)
            
        except Exception as e:
            logger.error(f"Error saving AI Event Manager state: {e}")
    
    def should_trigger_new_event(self, game_state) -> bool:
        """Kiểm tra có nên trigger event mới không"""
        # Nếu không có last_event_time thì có thể trigger
        if not self.last_event_time:
            return True
            
        # Kiểm tra thời gian từ event cuối
        time_since_last = datetime.now() - self.last_event_time
        
        # Minimum cooldown 2 giờ giữa các AI events
        min_cooldown = timedelta(hours=2)
        
        if time_since_last < min_cooldown:
            logger.info(f"🤖 AI Event cooldown: {min_cooldown - time_since_last} remaining")
            return False
            
        return True
    
    def _load_event_templates(self) -> Dict[str, List[Dict]]:
        """Load base event templates for AI to modify"""
        return {
            'economy_boost': [
                {
                    'name_template': '{emotion} Thị trường {type}',
                    'description_template': '{cause} khiến giá nông sản {effect}!',
                    'effect_type': 'price_bonus',
                    'effect_range': (1.2, 2.0),
                    'duration_range': (2, 8)
                }
            ],
            'productivity': [
                {
                    'name_template': '{magical} {boost_type}',
                    'description_template': '{phenomenon} giúp cây trồng {outcome}!',
                    'effect_type': 'growth_bonus',
                    'effect_range': (1.3, 2.5),
                    'duration_range': (1, 6)
                }
            ],
            'challenge': [
                {
                    'name_template': '{threat} {severity}',
                    'description_template': '{disaster} ảnh hưởng đến {target}!',
                    'effect_type': 'growth_penalty',
                    'effect_range': (0.5, 0.8),
                    'duration_range': (1, 4)
                }
            ],
            'special': [
                {
                    'name_template': '{festival} {celebration}',
                    'description_template': '{occasion} mang lại {benefit}!',
                    'effect_type': 'multi_bonus',
                    'effect_range': (1.1, 1.5),
                    'duration_range': (6, 24)
                }
            ]
        }
    
    async def generate_contextual_event(self, game_state, ai_decision) -> Optional[SmartEvent]:
        """Generate event based on current game context"""
        try:
            if ai_decision.action == 'trigger_excitement_event':
                return self._create_excitement_event(game_state, ai_decision)
            elif ai_decision.action == 'trigger_balance_event':
                return self._create_balance_event(game_state, ai_decision)
            elif ai_decision.action == 'trigger_weather_event':
                return self._create_weather_event(game_state, ai_decision)
            elif ai_decision.action == 'trigger_surprise_event':
                return self._create_surprise_event(game_state, ai_decision)
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating contextual event: {e}")
            return self._create_fallback_event()
    
    def _create_excitement_event(self, game_state, ai_decision) -> SmartEvent:
        """Create event to boost player excitement"""
        # Choose exciting event type based on current conditions
        if game_state.player_satisfaction < 0.5:
            # Players are unhappy, give them big boost
            event_type = 'productivity'
            effect_multiplier = 1.5
            rarity = 'epic'
        else:
            # Players are okay, give moderate boost
            event_type = 'economy_boost'
            effect_multiplier = 1.2
            rarity = 'rare'
        
        return self._generate_smart_event(
            event_type=event_type,
            context=f"Low activity ({game_state.recent_activity_level:.1%})",
            multiplier=effect_multiplier,
            rarity=rarity,
            ai_reasoning=ai_decision.reasoning
        )
    
    def _create_balance_event(self, game_state, ai_decision) -> SmartEvent:
        """Create event to rebalance economy"""
        avg_money = game_state.total_money_in_circulation / max(1, game_state.active_players)
        
        if avg_money > 7000:  # Too much money
            return SmartEvent(
                name="💸 Thuế nông nghiệp",
                description="Chính phủ thu thuế để cân bằng nền kinh tế! Chi phí hạt giống tăng 20%.",
                effect_type='seed_cost_increase',
                effect_value=1.2,
                duration_hours=8,
                trigger_condition='economy_rebalance',
                rarity='uncommon',
                ai_reasoning=f"Economy imbalance: {avg_money:.0f} coins/player (target: 5000)"
            )
        else:  # Too little money
            return SmartEvent(
                name="💰 Trợ cấp nông dân",
                description="Chính phủ hỗ trợ nông dân! Giá bán nông sản tăng 30%.",
                effect_type='price_bonus',
                effect_value=1.3,
                duration_hours=8,
                trigger_condition='economy_boost',
                rarity='rare',
                ai_reasoning=f"Low economy: {avg_money:.0f} coins/player (target: 5000)"
            )
    
    def _create_weather_event(self, game_state, ai_decision) -> SmartEvent:
        """Create weather-related event"""
        current_weather = game_state.current_weather.lower()
        
        if current_weather in ['storm', 'rain']:
            return SmartEvent(
                name="🌈 Cầu vồng sau mưa",
                description="Cầu vồng xuất hiện sau cơn mưa! Cây trồng phát triển nhanh gấp đôi!",
                effect_type='growth_bonus',
                effect_value=2.0,
                duration_hours=3,
                trigger_condition='weather_compensation',
                rarity='rare',
                ai_reasoning=f"Compensating for bad weather: {current_weather}"
            )
        else:
            return SmartEvent(
                name="⚡ Năng lượng thiên nhiên",
                description="Dòng năng lượng bí ẩn từ thiên nhiên! Sản lượng tăng 50%!",
                effect_type='yield_bonus',
                effect_value=1.5,
                duration_hours=4,
                trigger_condition='nature_power',
                rarity='epic',
                ai_reasoning=f"Adding variety to stable weather: {current_weather}"
            )
    
    def _create_surprise_event(self, game_state, ai_decision) -> SmartEvent:
        """Create unexpected surprise event"""
        surprise_events = [
            SmartEvent(
                name="🎪 Lễ hội thu hoạch bất ngờ",
                description="Làng tổ chức lễ hội đột xuất! Mọi thứ bán được giá gấp đôi!",
                effect_type='price_bonus',
                effect_value=2.0,
                duration_hours=2,
                trigger_condition='surprise_festival',
                rarity='legendary',
                ai_reasoning="Creating memorable surprise moment"
            ),
            SmartEvent(
                name="🌟 Phép màu của đất",
                description="Đất đai được phù phép! Mọi cây trồng chín ngay lập tức!",
                effect_type='instant_growth',
                effect_value=1.0,
                duration_hours=1,
                trigger_condition='magic_surge',
                rarity='legendary',
                ai_reasoning="Instant gratification surprise"
            ),
            SmartEvent(
                name="🎁 Quà tặng thiên thần",
                description="Thiên thần nông nghiệp ban phát hạt giống miễn phí!",
                effect_type='free_seeds',
                effect_value=10.0,  # 10 free seeds per player
                duration_hours=1,
                trigger_condition='divine_gift',
                rarity='legendary',
                ai_reasoning="Resource gift surprise"
            )
        ]
        
        return random.choice(surprise_events)
    
    def _generate_smart_event(self, event_type: str, context: str, multiplier: float, 
                            rarity: str, ai_reasoning: str) -> SmartEvent:
        """Generate event using templates with AI modifications"""
        templates = self.event_templates.get(event_type, [])
        if not templates:
            return self._create_fallback_event()
        
        template = random.choice(templates)
        
        # AI-driven name generation
        name_parts = self._get_contextual_name_parts(event_type, context, rarity)
        name = template['name_template'].format(**name_parts)
        
        # AI-driven description
        desc_parts = self._get_contextual_description_parts(event_type, context)
        description = template['description_template'].format(**desc_parts)
        
        # AI-adjusted effects
        effect_min, effect_max = template['effect_range']
        effect_value = effect_min + (effect_max - effect_min) * multiplier
        
        duration_min, duration_max = template['duration_range']
        duration = random.randint(duration_min, duration_max)
        
        return SmartEvent(
            name=name,
            description=description,
            effect_type=template['effect_type'],
            effect_value=effect_value,
            duration_hours=duration,
            trigger_condition=f"ai_generated_{event_type}",
            rarity=rarity,
            ai_reasoning=ai_reasoning
        )
    
    def _get_contextual_name_parts(self, event_type: str, context: str, rarity: str) -> Dict[str, str]:
        """Generate contextual name parts based on game state"""
        emotion_words = {
            'common': ['Nhẹ nhàng', 'Bình thường', 'Ổn định'],
            'rare': ['Tuyệt vời', 'Khuyến khích', 'Hứng khởi'],
            'epic': ['Phi thường', 'Kỳ diệu', 'Tuyệt đỉnh'],
            'legendary': ['Huyền thoại', 'Thần thánh', 'Vĩ đại']
        }
        
        type_words = {
            'economy_boost': ['sôi động', 'thịnh vượng', 'phát đạt'],
            'productivity': ['tăng trưởng', 'phát triển', 'sinh sôi'],
            'challenge': ['thử thách', 'khó khăn', 'thách thức'],
            'special': ['đặc biệt', 'kỳ lạ', 'bất thường']
        }
        
        return {
            'emotion': random.choice(emotion_words.get(rarity, emotion_words['common'])),
            'type': random.choice(type_words.get(event_type, ['đặc biệt'])),
            'magical': random.choice(['✨ Phép màu', '🌟 Kỳ tích', '⚡ Năng lượng']),
            'boost_type': random.choice(['tăng trưởng', 'phát triển', 'thịnh vượng']),
            'threat': random.choice(['⚠️ Cảnh báo', '🌪️ Bão táp', '☄️ Thiên tai']),
            'severity': random.choice(['nhẹ', 'vừa phải', 'nghiêm trọng']),
            'festival': random.choice(['🎉 Lễ hội', '🎪 Carnival', '🎭 Hội hè']),
            'celebration': random.choice(['vui vẻ', 'tưng bừng', 'sôi động'])
        }
    
    def _get_contextual_description_parts(self, event_type: str, context: str) -> Dict[str, str]:
        """Generate contextual description parts"""
        causes = [
            'Thời tiết thuận lợi', 'Chính sách mới', 'Khám phá khoa học',
            'Sự kiện thiên nhiên', 'Hoạt động cộng đồng', 'Phép màu bí ẩn'
        ]
        
        effects = {
            'economy_boost': ['tăng giá', 'có giá trị cao', 'được ưa chuộng'],
            'productivity': ['phát triển nhanh', 'sinh sôi mạnh', 'tăng trưởng vượt bậc'],
            'challenge': ['gặp khó khăn', 'bị ảnh hưởng', 'cần chăm sóc đặc biệt']
        }
        
        return {
            'cause': random.choice(causes),
            'effect': random.choice(effects.get(event_type, ['thay đổi'])),
            'phenomenon': random.choice(['Hiện tượng lạ', 'Năng lượng bí ẩn', 'Phép thuật']),
            'outcome': random.choice(['phát triển thần kỳ', 'sinh trưởng nhanh chóng', 'tăng trưởng vượt bậc']),
            'disaster': random.choice(['Thiên tai', 'Sâu bệnh', 'Thời tiết xấu']),
            'target': random.choice(['cây trồng', 'nông trại', 'sản lượng']),
            'occasion': random.choice(['Dịp đặc biệt', 'Ngày lễ', 'Sự kiện hiếm']),
            'benefit': random.choice(['may mắn', 'thịnh vượng', 'phước lành'])
        }
    
    def _create_fallback_event(self) -> SmartEvent:
        """Create simple fallback event if generation fails"""
        return SmartEvent(
            name="🌱 Ngày trồng cây",
            description="Một ngày bình thường tốt lành cho việc trồng trọt!",
            effect_type='growth_bonus',
            effect_value=1.1,
            duration_hours=4,
            trigger_condition='fallback',
            rarity='common',
            ai_reasoning="Fallback event due to generation error"
        )
    
    def should_trigger_event(self, game_state, time_factor: float = 1.0) -> bool:
        """Determine if an event should be triggered based on AI analysis"""
        if not self.last_event_time:
            return True
        
        # Time-based probability
        hours_since_last = (datetime.now() - self.last_event_time).total_seconds() / 3600
        time_probability = min(0.8, hours_since_last / 6)  # Max 80% chance after 6 hours
        
        # Game state factors
        activity_factor = 1.0 - game_state.recent_activity_level  # Lower activity = higher chance
        satisfaction_factor = 1.0 - game_state.player_satisfaction  # Lower satisfaction = higher chance
        
        # Combined probability
        total_probability = (time_probability + activity_factor * 0.3 + satisfaction_factor * 0.2) * time_factor
        
        return random.random() < min(0.9, total_probability)
    
    def get_event_analytics(self) -> Dict[str, any]:
        """Get analytics about AI event management"""
        return {
            'total_events_generated': len(self.event_history),
            'active_events': len(self.active_events),
            'last_event_time': self.last_event_time,
            'event_types_distribution': self._calculate_event_distribution(),
            'average_event_duration': self._calculate_average_duration(),
            'rarity_distribution': self._calculate_rarity_distribution()
        }
    
    def _calculate_event_distribution(self) -> Dict[str, int]:
        """Calculate distribution of event types"""
        distribution = {}
        for event in self.event_history:
            event_type = event.effect_type
            distribution[event_type] = distribution.get(event_type, 0) + 1
        return distribution
    
    def _calculate_average_duration(self) -> float:
        """Calculate average event duration"""
        if not self.event_history:
            return 0.0
        return sum(event.duration_hours for event in self.event_history) / len(self.event_history)
    
    def _calculate_rarity_distribution(self) -> Dict[str, int]:
        """Calculate rarity distribution"""
        distribution = {}
        for event in self.event_history:
            rarity = event.rarity
            distribution[rarity] = distribution.get(rarity, 0) + 1
        return distribution 