import logging
from typing import Dict, Tuple, Optional
import config
import json
import os
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class PricingCoordinator:
    """
    Unified pricing coordinator that handles all price modifiers
    from weather, events, and AI systems
    """
    
    def __init__(self):
        self.base_prices = {}
        self.current_modifiers = {}
        self.ai_price_adjustments = {}  # Store AI-driven price changes
        self.ai_adjustments_file = "cache/ai_price_adjustments.json"
        self._load_ai_adjustments()
        
    def _load_ai_adjustments(self):
        """Load AI price adjustments from file"""
        try:
            if os.path.exists(self.ai_adjustments_file):
                with open(self.ai_adjustments_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Convert string timestamps back to datetime
                    for crop_id, adjustment in data.items():
                        if 'timestamp' in adjustment:
                            adjustment['timestamp'] = datetime.fromisoformat(adjustment['timestamp'])
                        if 'expires_at' in adjustment:
                            adjustment['expires_at'] = datetime.fromisoformat(adjustment['expires_at'])
                    self.ai_price_adjustments = data
                    logger.info(f"💾 Loaded {len(self.ai_price_adjustments)} AI price adjustments")
        except Exception as e:
            logger.error(f"Error loading AI adjustments: {e}")
            self.ai_price_adjustments = {}
    
    def _save_ai_adjustments(self):
        """Save AI price adjustments to file"""
        try:
            os.makedirs(os.path.dirname(self.ai_adjustments_file), exist_ok=True)
            # Convert datetime to string for JSON serialization
            data_to_save = {}
            for crop_id, adjustment in self.ai_price_adjustments.items():
                data_to_save[crop_id] = adjustment.copy()
                if 'timestamp' in data_to_save[crop_id]:
                    data_to_save[crop_id]['timestamp'] = adjustment['timestamp'].isoformat()
                if 'expires_at' in data_to_save[crop_id]:
                    data_to_save[crop_id]['expires_at'] = adjustment['expires_at'].isoformat()
            
            with open(self.ai_adjustments_file, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving AI adjustments: {e}")
    
    def apply_ai_price_adjustment(self, crop_type: str, sell_price_modifier: float, 
                                seed_price_modifier: float, reasoning: str, 
                                duration_hours: int = 1) -> bool:
        """
        Apply AI-driven price adjustment for specific crop
        
        Args:
            crop_type: Type of crop to adjust
            sell_price_modifier: Multiplier for sell price (1.0 = no change, 1.2 = +20%)
            seed_price_modifier: Multiplier for seed price (0.8 = -20% discount)
            reasoning: AI reasoning for the adjustment
            duration_hours: How long the adjustment lasts
        """
        try:
            # Validate crop type
            if crop_type not in config.CROPS:
                logger.error(f"Invalid crop type for AI adjustment: {crop_type}")
                return False
            
            # Create adjustment record
            adjustment = {
                'sell_price_modifier': max(0.1, min(10.0, sell_price_modifier)),  # Clamp between 0.1x and 10x
                'seed_price_modifier': max(0.1, min(10.0, seed_price_modifier)),  # Clamp between 0.1x and 10x
                'reasoning': reasoning,
                'timestamp': datetime.now(),
                'expires_at': datetime.now() + timedelta(hours=duration_hours),
                'duration_hours': duration_hours
            }
            
            self.ai_price_adjustments[crop_type] = adjustment
            self._save_ai_adjustments()
            
            crop_name = config.CROPS[crop_type]['name']
            logger.info(f"🎀 Latina Price Adjustment: {crop_name} - Sell: {sell_price_modifier:.2f}x, Seed: {seed_price_modifier:.2f}x")
            logger.info(f"   Reasoning: {reasoning}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error applying AI price adjustment: {e}")
            return False
    
    def get_ai_price_modifier(self, crop_type: str) -> Tuple[float, float]:
        """
        Get current AI price modifiers for crop
        
        Returns:
            Tuple of (sell_price_modifier, seed_price_modifier)
        """
        try:
            if crop_type not in self.ai_price_adjustments:
                return 1.0, 1.0
            
            adjustment = self.ai_price_adjustments[crop_type]
            
            # Check if adjustment has expired
            if datetime.now() > adjustment['expires_at']:
                # Remove expired adjustment
                del self.ai_price_adjustments[crop_type]
                self._save_ai_adjustments()
                logger.info(f"🕐 AI price adjustment expired for {crop_type}")
                return 1.0, 1.0
            
            return adjustment['sell_price_modifier'], adjustment['seed_price_modifier']
            
        except Exception as e:
            logger.error(f"Error getting AI price modifier: {e}")
            return 1.0, 1.0
    
    def clear_expired_adjustments(self):
        """Remove all expired AI price adjustments"""
        try:
            current_time = datetime.now()
            expired_crops = []
            
            for crop_type, adjustment in self.ai_price_adjustments.items():
                if current_time > adjustment['expires_at']:
                    expired_crops.append(crop_type)
            
            for crop_type in expired_crops:
                del self.ai_price_adjustments[crop_type]
                logger.info(f"🧹 Cleared expired AI adjustment for {crop_type}")
            
            if expired_crops:
                self._save_ai_adjustments()
                
        except Exception as e:
            logger.error(f"Error clearing expired adjustments: {e}")
    
    def get_active_ai_adjustments(self) -> Dict:
        """Get all currently active AI price adjustments"""
        self.clear_expired_adjustments()
        
        active_adjustments = {}
        for crop_type, adjustment in self.ai_price_adjustments.items():
            crop_name = config.CROPS.get(crop_type, {}).get('name', crop_type)
            time_remaining = adjustment['expires_at'] - datetime.now()
            
            active_adjustments[crop_type] = {
                'crop_name': crop_name,
                'sell_modifier': adjustment['sell_price_modifier'],
                'seed_modifier': adjustment['seed_price_modifier'],
                'reasoning': adjustment['reasoning'],
                'time_remaining_minutes': int(time_remaining.total_seconds() / 60)
            }
        
        return active_adjustments
        
    def calculate_final_price(self, crop_type: str, bot = None) -> Tuple[int, Dict[str, float]]:
        """
        Calculate final crop price with all modifiers including AI adjustments
        
        Returns:
            Tuple of (final_price, modifier_breakdown)
        """
        try:
            # Get base price
            crop_config = config.CROPS.get(crop_type, {})
            base_price = crop_config.get('sell_price', 10)
            
            # Initialize modifiers
            modifiers = {
                'base_price': base_price,
                'weather_modifier': 1.0,
                'event_modifier': 1.0,
                'ai_modifier': 1.0,
                'total_modifier': 1.0
            }
            
            if not bot:
                # Check for AI modifiers even without bot
                ai_sell_modifier, _ = self.get_ai_price_modifier(crop_type)
                modifiers['ai_modifier'] = ai_sell_modifier
                final_price = int(base_price * ai_sell_modifier)
                modifiers['total_modifier'] = ai_sell_modifier
                return max(1, final_price), modifiers
            
            # Get weather modifier
            weather_modifier = self._get_weather_modifier(bot)
            modifiers['weather_modifier'] = weather_modifier
            
            # Get event modifier
            event_modifier = self._get_event_modifier(bot)
            modifiers['event_modifier'] = event_modifier
            
            # Get AI modifier
            ai_sell_modifier, _ = self.get_ai_price_modifier(crop_type)
            modifiers['ai_modifier'] = ai_sell_modifier
            
            # Calculate total modifier
            total_modifier = weather_modifier * event_modifier * ai_sell_modifier
            modifiers['total_modifier'] = total_modifier
            
            # Calculate final price
            final_price = int(base_price * total_modifier)
            final_price = max(1, final_price)  # Minimum 1 coin
            
            return final_price, modifiers
            
        except Exception as e:
            logger.error(f"Error calculating price for {crop_type}: {e}")
            # Return base price on error
            base_price = config.CROPS.get(crop_type, {}).get('sell_price', 10)
            return base_price, {'base_price': base_price, 'total_modifier': 1.0}
    
    def _get_weather_modifier(self, bot) -> float:
        """Get weather price modifier"""
        try:
            weather_cog = bot.get_cog('WeatherCog')
            if not weather_cog:
                return 1.0
            
            # Get current weather directly
            current_weather = getattr(weather_cog, 'current_weather', 'sunny')
            
            # Weather price effects - affect market prices directly
            weather_price_effects = {
                'sunny': 1.15,    # +15% (high demand, premium quality crops)
                'perfect': 1.25,  # +25% (perfect conditions, premium pricing)
                'cloudy': 1.0,    # No change (normal market conditions)
                'rainy': 1.1,     # +10% (good for growth, steady supply)
                'stormy': 0.75    # -25% (poor conditions, damaged/lower quality crops)
            }
            
            # Handle weather as string or dict
            if isinstance(current_weather, dict):
                weather_type = current_weather.get('type', 'sunny')
            else:
                weather_type = current_weather if current_weather else 'sunny'
            
            modifier = weather_price_effects.get(weather_type, 1.0)
            logger.info(f"Weather modifier: {weather_type} -> {modifier:.2f}")
            
            return modifier
            
        except Exception as e:
            logger.error(f"Error getting weather modifier: {e}")
            return 1.0
    
    def _get_event_modifier(self, bot) -> float:
        """Get event price modifier"""
        try:
            events_cog = bot.get_cog('EventsCog')
            if not events_cog:
                return 1.0
            
            effects = events_cog.get_current_event_effects()
            
            # Combine multiple event effects that affect pricing
            price_modifier = 1.0
            
            # Direct price bonus from events
            if 'price_bonus' in effects:
                price_modifier *= effects['price_bonus']
            
            # Yield bonus affects market price (higher yield = lower unit price, but better profits)
            # Convert yield bonus to subtle price effect
            if 'yield_bonus' in effects:
                yield_bonus = effects['yield_bonus']
                # Higher yield = slightly lower market price due to supply increase
                # But overall profit is still higher due to more quantity
                if yield_bonus > 1.0:
                    # Reduce price slightly due to increased supply, but not too much
                    price_modifier *= (1.0 + (yield_bonus - 1.0) * 0.3)  # 30% of yield bonus affects price
                elif yield_bonus < 1.0:
                    # Lower yield = higher prices due to scarcity
                    price_modifier *= (1.0 + (yield_bonus - 1.0) * 0.5)  # 50% of yield reduction affects price
            
            # Growth bonus can affect price (faster growth = more supply = slight price adjustment)
            if 'growth_bonus' in effects:
                growth_bonus = effects['growth_bonus']
                if growth_bonus > 1.0:
                    # Faster growth = more supply = slightly lower prices
                    price_modifier *= (1.0 + (growth_bonus - 1.0) * 0.1)  # 10% of growth bonus affects price
            
            return price_modifier
            
        except Exception as e:
            logger.error(f"Error getting event modifier: {e}")
            return 1.0
    
    def get_seed_cost_modifier(self, bot) -> float:
        """Get seed cost modifier from events (legacy method)"""
        try:
            events_cog = bot.get_cog('EventsCog')
            if not events_cog:
                return 1.0
            
            effects = events_cog.get_current_event_effects()
            
            # Combine multiple effects that affect seed costs
            seed_modifier = 1.0
            
            # Direct seed discount
            if 'seed_discount' in effects:
                seed_modifier *= effects['seed_discount']
            
            # Seed cost multiplier
            if 'seed_cost_multiplier' in effects:
                seed_modifier *= effects['seed_cost_multiplier']
            
            # Events with growth bonus might reduce seed costs slightly (government subsidies)
            if 'growth_bonus' in effects:
                growth_bonus = effects['growth_bonus']
                if growth_bonus > 1.0:
                    # Better growing conditions = slight seed discount (government support)
                    seed_modifier *= (1.0 - (growth_bonus - 1.0) * 0.1)  # 10% of growth bonus as seed discount
            
            return max(0.1, seed_modifier)  # Minimum 10% of original cost
            
        except Exception as e:
            logger.error(f"Error getting seed cost modifier: {e}")
            return 1.0
    
    def get_seed_cost_with_ai(self, crop_type: str, bot = None) -> Tuple[int, Dict[str, float]]:
        """
        Calculate final seed cost with all modifiers including AI adjustments
        
        Returns:
            Tuple of (final_seed_cost, modifier_breakdown)
        """
        try:
            # Get base seed cost
            crop_config = config.CROPS.get(crop_type, {})
            base_seed_cost = crop_config.get('seed_cost', 5)
            
            # Initialize modifiers
            modifiers = {
                'base_seed_cost': base_seed_cost,
                'event_modifier': 1.0,
                'ai_modifier': 1.0,
                'total_modifier': 1.0
            }
            
            # Get event modifier
            event_modifier = self.get_seed_cost_modifier(bot) if bot else 1.0
            modifiers['event_modifier'] = event_modifier
            
            # Get AI seed modifier
            _, ai_seed_modifier = self.get_ai_price_modifier(crop_type)
            modifiers['ai_modifier'] = ai_seed_modifier
            
            # Calculate total modifier
            total_modifier = event_modifier * ai_seed_modifier
            modifiers['total_modifier'] = total_modifier
            
            # Calculate final seed cost
            final_seed_cost = int(base_seed_cost * total_modifier)
            final_seed_cost = max(1, final_seed_cost)  # Minimum 1 coin
            
            return final_seed_cost, modifiers
            
        except Exception as e:
            logger.error(f"Error calculating seed cost for {crop_type}: {e}")
            # Return base cost on error
            base_cost = config.CROPS.get(crop_type, {}).get('seed_cost', 5)
            return base_cost, {'base_seed_cost': base_cost, 'total_modifier': 1.0}
    
    def get_market_overview(self, bot = None) -> Dict[str, Dict]:
        """Get market overview for all crops"""
        market_data = {}
        
        for crop_id, crop_config in config.CROPS.items():
            final_price, modifiers = self.calculate_final_price(crop_id, bot)
            
            # Calculate price change percentage
            base_price = crop_config['sell_price']
            price_change = ((final_price - base_price) / base_price) * 100
            
            # Get seed cost info with AI adjustments
            final_seed_cost, seed_modifiers = self.get_seed_cost_with_ai(crop_id, bot)
            base_seed_cost = seed_modifiers['base_seed_cost']
            seed_cost_change = ((final_seed_cost - base_seed_cost) / base_seed_cost) * 100
            
            # Determine market condition
            if price_change >= 15:
                condition = "🔥 Tăng mạnh"
                condition_color = "green"
            elif price_change >= 5:
                condition = "📈 Tăng nhẹ"
                condition_color = "lightgreen"
            elif price_change <= -15:
                condition = "📉 Giảm mạnh"
                condition_color = "red"
            elif price_change <= -5:
                condition = "📉 Giảm nhẹ"
                condition_color = "orange"
            else:
                condition = "➡️ Ổn định"
                condition_color = "gray"
            
            market_data[crop_id] = {
                'name': crop_config['name'],
                'emoji': crop_config.get('emoji', '🌾'),
                'base_price': base_price,
                'current_price': final_price,
                'price_change': price_change,
                'condition': condition,
                'condition_color': condition_color,
                'modifiers': modifiers,
                'seed_cost': final_seed_cost,
                'seed_cost_change': seed_cost_change,
                'seed_cost_modifiers': seed_modifiers
            }
        
        return market_data
    
    def get_trading_advice(self, market_data: Dict) -> str:
        """Generate trading advice based on market conditions"""
        increasing_crops = []
        decreasing_crops = []
        stable_crops = []
        
        for crop_id, data in market_data.items():
            change = data['price_change']
            if change >= 10:
                increasing_crops.append(data['name'])
            elif change <= -10:
                decreasing_crops.append(data['name'])
            else:
                stable_crops.append(data['name'])
        
        advice = []
        
        if increasing_crops:
            advice.append(f"💡 **Nên bán:** {', '.join(increasing_crops)} (giá cao)")
        
        if decreasing_crops:
            advice.append(f"⏳ **Nên chờ:** {', '.join(decreasing_crops)} (giá thấp)")
        
        if stable_crops:
            advice.append(f"➡️ **Ổn định:** {', '.join(stable_crops)}")
        
        if not advice:
            advice.append("📊 Thị trường đang cân bằng, có thể giao dịch bình thường")
        
        return "\n".join(advice)
    
    def format_price_breakdown(self, modifiers: Dict[str, float], crop_name: str) -> str:
        """Format price breakdown for display"""
        breakdown = []
        
        base_price = modifiers.get('base_price', 0)
        breakdown.append(f"💰 Giá gốc: {base_price} coins")
        
        weather_mod = modifiers.get('weather_modifier', 1.0)
        if weather_mod != 1.0:
            change = f"{weather_mod:.1%}" if weather_mod >= 1.0 else f"{weather_mod:.1%}"
            breakdown.append(f"🌤️ Thời tiết: {change}")
        
        event_mod = modifiers.get('event_modifier', 1.0)
        if event_mod != 1.0:
            change = f"{event_mod:.1%}" if event_mod >= 1.0 else f"{event_mod:.1%}"
            breakdown.append(f"🎪 Sự kiện: {change}")
        
        total_mod = modifiers.get('total_modifier', 1.0)
        if total_mod != 1.0:
            change = f"+{(total_mod-1)*100:.1f}%" if total_mod >= 1.0 else f"{(total_mod-1)*100:.1f}%"
            breakdown.append(f"📊 Tổng thay đổi: {change}")
        
        return "\n".join(breakdown)

# Global pricing coordinator instance
pricing_coordinator = PricingCoordinator() 