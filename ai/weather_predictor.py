import random
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import math

logger = logging.getLogger(__name__)

@dataclass
class WeatherPrediction:
    """AI weather prediction with reasoning"""
    weather_type: str
    probability: float
    duration_hours: int
    intensity: float  # 0.0 - 1.0
    effect_multiplier: float
    ai_reasoning: str
    optimal_for_crops: List[str]

@dataclass
class WeatherPattern:
    """Weather pattern with AI context"""
    name: str
    sequence: List[str]
    probability_modifiers: Dict[str, float]
    trigger_conditions: List[str]
    description: str

class WeatherPredictorAI:
    """
    Weather Predictor AI - Intelligent weather pattern management
    
    This AI creates realistic weather patterns that respond to game state,
    player behavior, and maintain strategic balance.
    """
    
    def __init__(self):
        self.weather_history = []
        self.current_pattern = None
        self.pattern_start_time = None
        self.base_weather_types = self._load_weather_types()
        self.weather_patterns = self._load_weather_patterns()
        self.prediction_accuracy = 0.85  # AI gets better over time
        
    def _load_weather_types(self) -> Dict[str, Dict]:
        """Load base weather types with their effects"""
        return {
            'sunny': {
                'display_name': '☀️ Nắng đẹp',
                'effect_multiplier': 1.2,
                'optimal_crops': ['tomato', 'corn'],
                'description': 'Thời tiết nắng đẹp tuyệt vời cho việc trồng trọt',
                'base_probability': 0.3
            },
            'cloudy': {
                'display_name': '☁️ Có mây',
                'effect_multiplier': 1.0,
                'optimal_crops': ['wheat'],
                'description': 'Thời tiết ôn hòa, phù hợp với mọi loại cây',
                'base_probability': 0.4
            },
            'rainy': {
                'display_name': '🌧️ Mưa nhẹ',
                'effect_multiplier': 1.1,
                'optimal_crops': ['carrot', 'wheat'],
                'description': 'Mưa nhẹ giúp cây trồng hấp thụ nước tốt',
                'base_probability': 0.2
            },
            'stormy': {
                'display_name': '⛈️ Bão tố',
                'effect_multiplier': 0.7,
                'optimal_crops': [],
                'description': 'Thời tiết khắc nghiệt, cây trồng phát triển chậm',
                'base_probability': 0.08
            },
            'perfect': {
                'display_name': '🌈 Hoàn hảo',
                'effect_multiplier': 1.5,
                'optimal_crops': ['tomato', 'corn', 'wheat', 'carrot'],
                'description': 'Thời tiết hoàn hảo cho mọi loại cây trồng!',
                'base_probability': 0.02
            }
        }
    
    def _load_weather_patterns(self) -> Dict[str, WeatherPattern]:
        """Load intelligent weather patterns"""
        return {
            'stable_growth': WeatherPattern(
                name='Thời kỳ ổn định',
                sequence=['sunny', 'cloudy', 'sunny', 'cloudy'],
                probability_modifiers={'growth_bonus': 1.2},
                trigger_conditions=['low_player_frustration', 'stable_economy'],
                description='Pattern ổn định giúp người chơi phát triển đều đặn'
            ),
            'challenging_cycle': WeatherPattern(
                name='Chu kỳ thách thức',
                sequence=['cloudy', 'rainy', 'stormy', 'sunny'],
                probability_modifiers={'challenge_factor': 1.5},
                trigger_conditions=['high_player_satisfaction', 'strong_economy'],
                description='Pattern thách thức để tăng độ khó khi người chơi quá mạnh'
            ),
            'recovery_boost': WeatherPattern(
                name='Giai đoạn phục hồi',
                sequence=['perfect', 'sunny', 'sunny', 'cloudy'],
                probability_modifiers={'recovery_boost': 2.0},
                trigger_conditions=['high_player_frustration', 'low_activity'],
                description='Pattern hỗ trợ khi người chơi gặp khó khăn'
            ),
            'surprise_mix': WeatherPattern(
                name='Bất thường',
                sequence=['stormy', 'perfect', 'rainy', 'sunny'],
                probability_modifiers={'unpredictability': 2.0},
                trigger_conditions=['boredom_detected', 'random_event'],
                description='Pattern bất ngờ để tạo excitement'
            )
        }
    
    async def predict_next_weather(self, game_state, current_weather: str) -> WeatherPrediction:
        """Predict next weather based on AI analysis"""
        try:
            # Analyze current game context
            context = self._analyze_weather_context(game_state, current_weather)
            
            # Determine if pattern change is needed
            if self._should_change_pattern(game_state, context):
                new_pattern = self._select_optimal_pattern(game_state, context)
                if new_pattern:
                    self.current_pattern = new_pattern
                    self.pattern_start_time = datetime.now()
            
            # Generate prediction based on current pattern or standalone logic
            if self.current_pattern:
                prediction = self._predict_from_pattern(game_state, current_weather, context)
            else:
                prediction = self._predict_standalone(game_state, current_weather, context)
            
            # Add some AI uncertainty
            if random.random() > self.prediction_accuracy:
                prediction = self._add_prediction_noise(prediction)
            
            return prediction
            
        except Exception as e:
            logger.error(f"Error predicting weather: {e}")
            return self._fallback_prediction(current_weather)
    
    def _analyze_weather_context(self, game_state, current_weather: str) -> Dict[str, float]:
        """Analyze game context for weather decisions"""
        context = {}
        
        # Player satisfaction factor
        context['satisfaction'] = game_state.player_satisfaction
        context['frustration'] = 1.0 - game_state.player_satisfaction
        
        # Activity level
        context['activity'] = game_state.recent_activity_level
        context['boredom'] = 1.0 - game_state.recent_activity_level
        
        # Economic factors
        avg_money = game_state.total_money_in_circulation / max(1, game_state.active_players)
        context['wealth'] = min(1.0, avg_money / 10000)  # Normalize to 0-1
        
        # Weather history analysis
        context['weather_stability'] = self._calculate_weather_stability()
        context['time_since_good_weather'] = self._time_since_weather_type(['sunny', 'perfect'])
        context['time_since_bad_weather'] = self._time_since_weather_type(['stormy'])
        
        return context
    
    def _should_change_pattern(self, game_state, context: Dict[str, float]) -> bool:
        """Determine if weather pattern should change"""
        if not self.current_pattern:
            return True
        
        # Time-based change
        if self.pattern_start_time:
            hours_in_pattern = (datetime.now() - self.pattern_start_time).total_seconds() / 3600
            if hours_in_pattern > 24:  # Max 24 hours per pattern
                return True
        
        # Context-based change
        if context['frustration'] > 0.8 and self.current_pattern.name != 'Giai đoạn phục hồi':
            return True
        
        if context['boredom'] > 0.7 and self.current_pattern.name != 'Bất thường':
            return True
        
        if context['satisfaction'] > 0.9 and context['wealth'] > 0.8:
            return True  # Time for challenge
        
        return False
    
    def _select_optimal_pattern(self, game_state, context: Dict[str, float]) -> Optional[WeatherPattern]:
        """Select the best weather pattern for current game state"""
        pattern_scores = {}
        
        for pattern_name, pattern in self.weather_patterns.items():
            score = 0.0
            
            # Check trigger conditions
            for condition in pattern.trigger_conditions:
                if self._evaluate_trigger_condition(condition, context):
                    score += 2.0
            
            # Context-based scoring
            if pattern_name == 'recovery_boost' and context['frustration'] > 0.6:
                score += 3.0
            elif pattern_name == 'challenging_cycle' and context['satisfaction'] > 0.8:
                score += 2.5
            elif pattern_name == 'surprise_mix' and context['boredom'] > 0.6:
                score += 2.0
            elif pattern_name == 'stable_growth' and 0.4 < context['satisfaction'] < 0.7:
                score += 1.5
            
            pattern_scores[pattern_name] = score
        
        # Select pattern with highest score
        if pattern_scores:
            best_pattern_name = max(pattern_scores, key=pattern_scores.get)
            if pattern_scores[best_pattern_name] > 1.0:
                return self.weather_patterns[best_pattern_name]
        
        return None
    
    def _evaluate_trigger_condition(self, condition: str, context: Dict[str, float]) -> bool:
        """Evaluate if a trigger condition is met"""
        conditions_map = {
            'low_player_frustration': context['frustration'] < 0.4,
            'stable_economy': 0.3 < context['wealth'] < 0.7,
            'high_player_satisfaction': context['satisfaction'] > 0.7,
            'strong_economy': context['wealth'] > 0.7,
            'high_player_frustration': context['frustration'] > 0.7,
            'low_activity': context['activity'] < 0.4,
            'boredom_detected': context['boredom'] > 0.6,
            'random_event': random.random() < 0.1
        }
        
        return conditions_map.get(condition, False)
    
    def _predict_from_pattern(self, game_state, current_weather: str, context: Dict[str, float]) -> WeatherPrediction:
        """Predict weather based on current pattern"""
        pattern = self.current_pattern
        
        # Determine position in pattern sequence
        pattern_position = len(self.weather_history) % len(pattern.sequence)
        next_weather = pattern.sequence[pattern_position]
        
        # Apply context modifications
        if context['frustration'] > 0.8 and next_weather in ['stormy']:
            # Don't make frustrated players more frustrated
            next_weather = 'cloudy'
            reasoning = f"AI modified pattern to avoid player frustration (pattern: {pattern.name})"
        elif context['satisfaction'] > 0.9 and next_weather in ['perfect', 'sunny']:
            # Add some challenge to satisfied players
            if random.random() < 0.3:
                next_weather = 'rainy'
                reasoning = f"AI added challenge to prevent game being too easy (pattern: {pattern.name})"
            else:
                reasoning = f"Following {pattern.name} pattern"
        else:
            reasoning = f"Following {pattern.name} pattern"
        
        weather_data = self.base_weather_types[next_weather]
        
        return WeatherPrediction(
            weather_type=next_weather,
            probability=0.9,  # High confidence in pattern
            duration_hours=random.randint(2, 6),
            intensity=random.uniform(0.7, 1.0),
            effect_multiplier=weather_data['effect_multiplier'],
            ai_reasoning=reasoning,
            optimal_for_crops=weather_data['optimal_crops']
        )
    
    def _predict_standalone(self, game_state, current_weather: str, context: Dict[str, float]) -> WeatherPrediction:
        """Predict weather without following a pattern"""
        # Calculate probabilities for each weather type
        probabilities = {}
        
        for weather_type, data in self.base_weather_types.items():
            base_prob = data['base_probability']
            
            # Modify based on context
            if weather_type == 'sunny' and context['frustration'] > 0.6:
                base_prob *= 2.0  # Help frustrated players
            elif weather_type == 'stormy' and context['satisfaction'] > 0.8:
                base_prob *= 1.5  # Challenge satisfied players
            elif weather_type == 'perfect' and context['boredom'] > 0.7:
                base_prob *= 3.0  # Excitement for bored players
            elif weather_type == current_weather:
                base_prob *= 0.3  # Reduce consecutive same weather
            
            probabilities[weather_type] = base_prob
        
        # Normalize probabilities
        total_prob = sum(probabilities.values())
        for weather_type in probabilities:
            probabilities[weather_type] /= total_prob
        
        # Select weather based on probabilities
        rand = random.random()
        cumulative = 0.0
        selected_weather = 'cloudy'  # fallback
        
        for weather_type, prob in probabilities.items():
            cumulative += prob
            if rand <= cumulative:
                selected_weather = weather_type
                break
        
        weather_data = self.base_weather_types[selected_weather]
        
        reasoning = self._generate_standalone_reasoning(selected_weather, context)
        
        return WeatherPrediction(
            weather_type=selected_weather,
            probability=probabilities[selected_weather],
            duration_hours=random.randint(1, 4),
            intensity=random.uniform(0.5, 1.0),
            effect_multiplier=weather_data['effect_multiplier'],
            ai_reasoning=reasoning,
            optimal_for_crops=weather_data['optimal_crops']
        )
    
    def _generate_standalone_reasoning(self, weather_type: str, context: Dict[str, float]) -> str:
        """Generate reasoning for standalone weather prediction"""
        reasons = []
        
        if context['frustration'] > 0.6 and weather_type in ['sunny', 'perfect']:
            reasons.append("Giúp người chơi frustrated")
        elif context['satisfaction'] > 0.8 and weather_type in ['stormy', 'rainy']:
            reasons.append("Thêm thách thức cho người chơi mạnh")
        elif context['boredom'] > 0.6:
            reasons.append("Tạo sự thay đổi thú vị")
        else:
            reasons.append("Duy trì cân bằng game")
        
        if context['weather_stability'] > 0.7:
            reasons.append("phá vỡ pattern quá ổn định")
        
        return "AI quyết định: " + ", ".join(reasons)
    
    def _calculate_weather_stability(self) -> float:
        """Calculate how stable recent weather has been"""
        if len(self.weather_history) < 3:
            return 0.0
        
        recent_weather = self.weather_history[-6:]  # Last 6 weather changes
        unique_weather = len(set(recent_weather))
        
        return 1.0 - (unique_weather / len(recent_weather))
    
    def _time_since_weather_type(self, weather_types: List[str]) -> int:
        """Calculate hours since last occurrence of weather types"""
        for i, weather in enumerate(reversed(self.weather_history)):
            if weather in weather_types:
                return i
        return 999  # Very long time
    
    def _add_prediction_noise(self, prediction: WeatherPrediction) -> WeatherPrediction:
        """Add some uncertainty to prediction (AI isn't perfect)"""
        # Sometimes AI makes suboptimal choices
        weather_types = list(self.base_weather_types.keys())
        if random.random() < 0.1:  # 10% chance of random choice
            random_weather = random.choice(weather_types)
            weather_data = self.base_weather_types[random_weather]
            
            return WeatherPrediction(
                weather_type=random_weather,
                probability=0.3,  # Low confidence
                duration_hours=prediction.duration_hours,
                intensity=prediction.intensity,
                effect_multiplier=weather_data['effect_multiplier'],
                ai_reasoning="AI uncertainty: random weather selection",
                optimal_for_crops=weather_data['optimal_crops']
            )
        
        return prediction
    
    def _fallback_prediction(self, current_weather: str) -> WeatherPrediction:
        """Fallback prediction if main logic fails"""
        return WeatherPrediction(
            weather_type='cloudy',
            probability=1.0,
            duration_hours=3,
            intensity=0.5,
            effect_multiplier=1.0,
            ai_reasoning="Fallback prediction due to error",
            optimal_for_crops=['wheat']
        )
    
    def update_history(self, weather_type: str):
        """Update weather history for AI learning"""
        self.weather_history.append(weather_type)
        
        # Keep only recent history
        if len(self.weather_history) > 50:
            self.weather_history = self.weather_history[-50:]
    
    def get_weather_analytics(self) -> Dict[str, any]:
        """Get analytics about AI weather management"""
        if not self.weather_history:
            return {"message": "No weather history available"}
        
        # Calculate weather distribution
        weather_count = {}
        for weather in self.weather_history:
            weather_count[weather] = weather_count.get(weather, 0) + 1
        
        return {
            'weather_history_length': len(self.weather_history),
            'current_pattern': self.current_pattern.name if self.current_pattern else 'None',
            'pattern_duration': self._get_pattern_duration(),
            'weather_distribution': weather_count,
            'prediction_accuracy': self.prediction_accuracy,
            'weather_stability': self._calculate_weather_stability(),
            'recent_weather': self.weather_history[-10:] if len(self.weather_history) >= 10 else self.weather_history
        }
    
    def _get_pattern_duration(self) -> str:
        """Get current pattern duration"""
        if not self.pattern_start_time:
            return "N/A"
        
        duration = datetime.now() - self.pattern_start_time
        hours = int(duration.total_seconds() / 3600)
        return f"{hours} hours"
    
    def get_ai_weather_report(self) -> str:
        """Generate human-readable AI weather report"""
        analytics = self.get_weather_analytics()
        
        report = f"""🌤️ **Weather Predictor AI Report**

**🔮 Current Analysis:**
• Pattern: {analytics.get('current_pattern', 'Standalone')}
• Pattern Duration: {analytics.get('pattern_duration', 'N/A')}
• Prediction Accuracy: {analytics.get('prediction_accuracy', 0.85):.1%}
• Weather Stability: {analytics.get('weather_stability', 0.0):.1%}

**📊 Recent Weather History:**
{' → '.join(analytics.get('recent_weather', ['No data']))}

**🎯 AI Weather Strategy:**
{self._get_current_strategy_description()}
        """
        
        return report
    
    def _get_current_strategy_description(self) -> str:
        """Get description of current AI weather strategy"""
        if self.current_pattern:
            return f"• Following '{self.current_pattern.name}' pattern\n• {self.current_pattern.description}"
        else:
            return "• Using adaptive standalone predictions\n• Responding to real-time game conditions" 