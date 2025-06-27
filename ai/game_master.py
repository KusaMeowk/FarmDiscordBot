import random
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import asyncio

logger = logging.getLogger(__name__)

@dataclass
class GameState:
    """Current state of the game for AI decision making"""
    active_players: int
    total_money_in_circulation: int
    average_player_level: float
    recent_activity_level: float  # 0.0 - 1.0
    current_weather: str
    active_events: List[str]
    time_since_last_event: int  # minutes
    player_satisfaction: float  # 0.0 - 1.0
    weather_condition: str
    temperature: float
    humidity: int

@dataclass
class AIDecision:
    """AI decision with reasoning"""
    action: str
    probability: float
    reasoning: str
    expected_impact: str
    
class GameMasterAI:
    """
    Game Master AI - The brain that orchestrates game events and weather
    
    This AI analyzes player behavior, game state, and makes intelligent
    decisions about when to trigger events, change weather patterns,
    and maintain game balance.
    """
    
    def __init__(self):
        self.personality_traits = {
            'benevolence': 0.7,      # How often to help players
            'mischief': 0.3,         # How often to create challenges  
            'unpredictability': 0.5,  # How random vs calculated
            'balance_focus': 0.8,     # How much to focus on game balance
            'player_retention': 0.9   # Priority on keeping players engaged
        }
        
        self.decision_history = []
        self.last_analysis_time = None
        self.game_state = None
        
    async def analyze_game_state(self, bot) -> GameState:
        """Analyze current game state for decision making"""
        try:
            # Get player statistics
            active_players = await self._count_active_players(bot)
            total_money = await self._calculate_total_money(bot)
            avg_level = await self._calculate_average_level(bot)
            activity_level = await self._measure_activity_level(bot)
            
            # Get current conditions
            weather_cog = bot.get_cog('WeatherCog')
            current_weather = 'unknown'
            weather_condition = 'scattered clouds'
            temperature = 26.0
            humidity = 70
            
            if weather_cog:
                try:
                    weather_data = await weather_cog.fetch_weather_data()
                    current_weather = weather_data.get('weather', [{}])[0].get('main', 'unknown').lower()
                    weather_condition = weather_data.get('weather', [{}])[0].get('description', 'scattered clouds')
                    temperature = weather_data.get('main', {}).get('temp', 26.0)
                    humidity = weather_data.get('main', {}).get('humidity', 70)
                except Exception as e:
                    print(f"Error getting weather data: {e}")
                    current_weather = 'cloudy'
            
            # Get active events
            events_cog = bot.get_cog('EventsCog')
            active_events = []
            if events_cog and events_cog.current_event:
                active_events.append(events_cog.current_event.get('data', {}).get('name', 'Unknown'))
            
            # Calculate time since last event
            time_since_event = self._calculate_time_since_last_event(events_cog)
            
            # Estimate player satisfaction (mock for now)
            satisfaction = self._estimate_player_satisfaction(
                active_players, total_money, activity_level
            )
            
            self.game_state = GameState(
                active_players=active_players,
                total_money_in_circulation=total_money,
                average_player_level=avg_level,
                recent_activity_level=activity_level,
                current_weather=current_weather,
                active_events=active_events,
                time_since_last_event=time_since_event,
                player_satisfaction=satisfaction,
                weather_condition=weather_condition,
                temperature=temperature,
                humidity=humidity
            )
            
            return self.game_state
            
        except Exception as e:
            logger.error(f"Error analyzing game state: {e}")
            return self._default_game_state()
    
    async def make_event_decision(self, bot) -> Optional[AIDecision]:
        """Make intelligent decision about triggering events"""
        await self.analyze_game_state(bot)
        
        if not self.game_state:
            return None
        
        # Decision factors
        factors = self._calculate_event_factors()
        
        # AI reasoning process
        if factors['boredom_factor'] > 0.7:
            return AIDecision(
                action='trigger_excitement_event',
                probability=0.8,
                reasoning='Players seem bored, need excitement boost',
                expected_impact='Increase engagement and activity'
            )
        
        elif factors['economy_imbalance'] > 0.6:
            return AIDecision(
                action='trigger_balance_event',
                probability=0.7,
                reasoning='Economy needs rebalancing',
                expected_impact='Restore economic equilibrium'
            )
        
        elif factors['weather_stagnation'] > 0.5:
            return AIDecision(
                action='trigger_weather_event',
                probability=0.6,
                reasoning='Weather has been stable too long',
                expected_impact='Add weather variety and dynamics'
            )
        
        elif factors['random_surprise'] > 0.9:
            return AIDecision(
                action='trigger_surprise_event',
                probability=0.95,
                reasoning='Time for unexpected surprise to delight players',
                expected_impact='Create memorable moment and buzz'
            )
        
        return None
    
    async def make_weather_decision(self, bot) -> Optional[AIDecision]:
        """Make intelligent decision about weather changes"""
        await self.analyze_game_state(bot)
        
        if not self.game_state:
            return None
        
        factors = self._calculate_weather_factors()
        
        if factors['player_frustration'] > 0.7:
            return AIDecision(
                action='improve_weather',
                probability=0.8,
                reasoning='Players seem frustrated, improve conditions',
                expected_impact='Boost player morale and profits'
            )
        
        elif factors['too_easy'] > 0.6:
            return AIDecision(
                action='challenging_weather',
                probability=0.7,
                reasoning='Game is too easy, add challenge',
                expected_impact='Increase strategic depth'
            )
        
        elif factors['pattern_break_needed'] > 0.8:
            return AIDecision(
                action='break_weather_pattern',
                probability=0.9,
                reasoning='Weather pattern too predictable',
                expected_impact='Restore unpredictability and interest'
            )
        
        return None
    
    def _calculate_event_factors(self) -> Dict[str, float]:
        """Calculate various factors for event decisions"""
        if not self.game_state:
            return {}
        
        # Boredom factor - based on activity and time since last event
        boredom = min(1.0, self.game_state.time_since_last_event / 180)  # 3 hours max
        boredom += (1.0 - self.game_state.recent_activity_level) * 0.5
        
        # Economy imbalance - if players have too much/little money
        ideal_money_per_player = 5000  # Target average
        avg_money = self.game_state.total_money_in_circulation / max(1, self.game_state.active_players)
        economy_imbalance = abs(avg_money - ideal_money_per_player) / ideal_money_per_player
        
        # Weather stagnation
        weather_stagnation = 0.3 if self.game_state.current_weather == 'clouds' else 0.1
        
        # Random surprise factor
        random_surprise = random.random() * self.personality_traits['unpredictability']
        
        return {
            'boredom_factor': min(1.0, boredom),
            'economy_imbalance': min(1.0, economy_imbalance),
            'weather_stagnation': weather_stagnation,
            'random_surprise': random_surprise
        }
    
    def _calculate_weather_factors(self) -> Dict[str, float]:
        """Calculate factors for weather decisions"""
        if not self.game_state:
            return {}
        
        # Player frustration - low satisfaction with bad weather
        frustration = 0.0
        if self.game_state.current_weather in ['storm', 'rain'] and self.game_state.player_satisfaction < 0.5:
            frustration = 0.8
        
        # Game too easy - high satisfaction with good weather for too long
        too_easy = 0.0
        if self.game_state.current_weather in ['clear', 'sunny'] and self.game_state.player_satisfaction > 0.8:
            too_easy = 0.7
        
        # Pattern break needed
        pattern_break = random.random() * 0.3 + (self.game_state.time_since_last_event / 120) * 0.5
        
        return {
            'player_frustration': frustration,
            'too_easy': too_easy,
            'pattern_break_needed': min(1.0, pattern_break)
        }
    
    async def _count_active_players(self, bot) -> int:
        """Count recently active players"""
        try:
            # Use bot's database instance
            if not bot.db:
                return random.randint(5, 20)
            
            # Get users who have played recently (total users as proxy)
            cursor = await bot.db.connection.execute("SELECT COUNT(DISTINCT user_id) FROM users")
            result = await cursor.fetchone()
            count = result[0] if result else 0
            
            return max(1, count)  # At least 1 to avoid division by zero
        except Exception as e:
            logger.error(f"Error counting active players: {e}")
            return random.randint(5, 20)  # Fallback
    
    async def _calculate_total_money(self, bot) -> int:
        """Calculate total money in circulation"""
        try:
            if not bot.db:
                return random.randint(10000, 50000)
            
            # Sum all money from all users
            cursor = await bot.db.connection.execute("SELECT SUM(money) FROM users")
            result = await cursor.fetchone()
            total = result[0] if result and result[0] else 0
            
            return int(total)
        except Exception as e:
            logger.error(f"Error calculating total money: {e}")
            return random.randint(10000, 50000)  # Fallback
    
    async def _calculate_average_level(self, bot) -> float:
        """Calculate average player progression level"""
        try:
            if not bot.db:
                return random.uniform(2.0, 6.0)
            
            # Calculate average based on land slots (proxy for progression)
            cursor = await bot.db.connection.execute("SELECT AVG(land_slots) FROM users WHERE land_slots > 0")
            result = await cursor.fetchone()
            avg_slots = result[0] if result and result[0] else 1.0
            
            # Convert land slots to level (1-10 scale)
            level = min(10.0, max(1.0, float(avg_slots)))
            return level
        except Exception as e:
            logger.error(f"Error calculating average level: {e}")
            return random.uniform(2.0, 6.0)  # Fallback
    
    async def _measure_activity_level(self, bot) -> float:
        """Measure recent activity level (0.0 - 1.0)"""
        try:
            if not bot.db:
                return random.uniform(0.4, 0.8)
            
            # Count users with crops (active farmers)
            cursor1 = await bot.db.connection.execute("SELECT COUNT(*) FROM users")
            total_result = await cursor1.fetchone()
            
            cursor2 = await bot.db.connection.execute("SELECT COUNT(DISTINCT user_id) FROM crops")
            active_result = await cursor2.fetchone()
            
            total_users = total_result[0] if total_result else 1
            active_users = active_result[0] if active_result else 0
            
            activity_ratio = active_users / max(1, total_users)
            
            # Add some randomness for simulation
            return min(1.0, activity_ratio + random.uniform(-0.1, 0.2))
        except Exception as e:
            logger.error(f"Error measuring activity level: {e}")
            return random.uniform(0.4, 0.8)  # Fallback
    
    def _calculate_time_since_last_event(self, events_cog) -> int:
        """Calculate minutes since last event"""
        if not events_cog or not events_cog.current_event:
            return random.randint(60, 240)  # 1-4 hours
        return 0
    
    def _estimate_player_satisfaction(self, players: int, money: int, activity: float) -> float:
        """Estimate overall player satisfaction"""
        # Simple satisfaction model
        base_satisfaction = 0.6
        activity_bonus = activity * 0.3
        engagement_bonus = min(0.1, players / 100)  # More players = higher satisfaction
        
        return min(1.0, base_satisfaction + activity_bonus + engagement_bonus)
    
    def _default_game_state(self) -> GameState:
        """Return default game state if analysis fails"""
        return GameState(
            active_players=10,
            total_money_in_circulation=50000,
            average_player_level=5.0,
            recent_activity_level=0.6,
            current_weather='clouds',
            active_events=[],
            time_since_last_event=120,
            player_satisfaction=0.6,
            weather_condition='scattered clouds',
            temperature=26.0,
            humidity=70
        )
    
    def get_ai_report(self) -> str:
        """Generate human-readable AI analysis report"""
        if not self.game_state:
            return "🤖 AI Engine: No analysis available"
        
        report = f"""🤖 **Game Master AI Report**
        
**📊 Game State Analysis:**
• Active Players: {self.game_state.active_players}
• Economy: {self.game_state.total_money_in_circulation:,} coins in circulation
• Activity Level: {self.game_state.recent_activity_level:.1%}
• Player Satisfaction: {self.game_state.player_satisfaction:.1%}
• Current Weather: {self.game_state.current_weather}
• Time Since Last Event: {self.game_state.time_since_last_event} minutes

**🧠 AI Personality:**
• Benevolence: {self.personality_traits['benevolence']:.1%}
• Mischief: {self.personality_traits['mischief']:.1%}
• Unpredictability: {self.personality_traits['unpredictability']:.1%}
• Balance Focus: {self.personality_traits['balance_focus']:.1%}

**🎯 Next Decision Factors:**
{self._format_decision_factors()}
        """
        
        return report
    
    def _format_decision_factors(self) -> str:
        """Format decision factors for display"""
        event_factors = self._calculate_event_factors()
        weather_factors = self._calculate_weather_factors()
        
        factors = []
        
        if event_factors:
            if event_factors.get('boredom_factor', 0) > 0.5:
                factors.append(f"• Players may be getting bored ({event_factors['boredom_factor']:.1%})")
            if event_factors.get('economy_imbalance', 0) > 0.4:
                factors.append(f"• Economy imbalance detected ({event_factors['economy_imbalance']:.1%})")
        
        if weather_factors:
            if weather_factors.get('player_frustration', 0) > 0.5:
                factors.append(f"• Player frustration from weather ({weather_factors['player_frustration']:.1%})")
            if weather_factors.get('too_easy', 0) > 0.5:
                factors.append(f"• Game may be too easy ({weather_factors['too_easy']:.1%})")
        
        return "\n".join(factors) if factors else "• All systems optimal" 