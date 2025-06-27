"""
State Manager - Quản lý trạng thái hệ thống bot
Lưu trữ các state keys và helper functions cho việc manage bot state
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import json

# State Keys Constants
WEATHER_CYCLE_STATE = "weather_cycle"
EVENT_STATE = "event_system"
AI_SYSTEM_STATE = "ai_system"

class StateManager:
    """Helper class để quản lý bot state"""
    
    def __init__(self, database):
        self.db = database
    
    # Weather State Management
    async def save_weather_state(self, 
                                next_weather_change: Optional[datetime] = None,
                                current_weather: Optional[Dict[str, Any]] = None,
                                weather_change_duration: int = 3600):
        """Lưu trạng thái weather cycle"""
        try:
            weather_data = {
                'next_weather_change': next_weather_change.isoformat() if next_weather_change else None,
                'current_weather': current_weather,
                'weather_change_duration': weather_change_duration,
                'last_updated': datetime.now().isoformat()
            }
            
            await self.db.update_bot_state(WEATHER_CYCLE_STATE, weather_data)
            return True
            
        except Exception as e:
            print(f"Error saving weather state: {e}")
            return False
    
    async def load_weather_state(self) -> Dict[str, Any]:
        """Load trạng thái weather cycle"""
        try:
            bot_state = await self.db.get_bot_state(WEATHER_CYCLE_STATE)
            if not bot_state:
                return {}
            
            # Convert datetime strings back to datetime objects
            state_data = bot_state.state_data.copy()
            
            if state_data.get('next_weather_change'):
                state_data['next_weather_change'] = datetime.fromisoformat(
                    state_data['next_weather_change']
                )
            
            if state_data.get('last_updated'):
                state_data['last_updated'] = datetime.fromisoformat(
                    state_data['last_updated']
                )
            
            return state_data
            
        except Exception as e:
            print(f"Error loading weather state: {e}")
            return {}
    
    async def is_weather_state_valid(self, max_age_hours: int = 24) -> bool:
        """Kiểm tra xem weather state có hợp lệ không"""
        try:
            weather_state = await self.load_weather_state()
            if not weather_state:
                return False
            
            last_updated = weather_state.get('last_updated')
            if not last_updated:
                return False
                
            # Check if state is too old
            age = datetime.now() - last_updated
            if age > timedelta(hours=max_age_hours):
                print(f"Weather state too old ({age.total_seconds()/3600:.1f}h), marking as invalid")
                return False
            
            return True
            
        except Exception as e:
            print(f"Error validating weather state: {e}")
            return False
    
    # Event State Management
    async def save_event_state(self, 
                              current_event: Optional[Dict[str, Any]] = None,
                              event_end_time: Optional[datetime] = None):
        """Lưu trạng thái event system"""
        try:
            event_data = {
                'current_event': current_event,
                'event_end_time': event_end_time.isoformat() if event_end_time else None,
                'last_updated': datetime.now().isoformat()
            }
            
            await self.db.update_bot_state(EVENT_STATE, event_data)
            return True
            
        except Exception as e:
            print(f"Error saving event state: {e}")
            return False
    
    async def load_event_state(self) -> Dict[str, Any]:
        """Load trạng thái event system"""
        try:
            bot_state = await self.db.get_bot_state(EVENT_STATE)
            if not bot_state:
                return {}
            
            # Convert datetime strings back to datetime objects
            state_data = bot_state.state_data.copy()
            
            if state_data.get('event_end_time'):
                state_data['event_end_time'] = datetime.fromisoformat(
                    state_data['event_end_time']
                )
            
            if state_data.get('last_updated'):
                state_data['last_updated'] = datetime.fromisoformat(
                    state_data['last_updated']
                )
            
            # Convert start_time in current_event if exists
            if state_data.get('current_event') and state_data['current_event'].get('start_time'):
                state_data['current_event']['start_time'] = datetime.fromisoformat(
                    state_data['current_event']['start_time']
                )
            
            return state_data
            
        except Exception as e:
            print(f"Error loading event state: {e}")
            return {}
    
    async def is_event_state_valid(self) -> bool:
        """Kiểm tra xem event state có hợp lệ không"""
        try:
            event_state = await self.load_event_state()
            if not event_state:
                return False
            
            # Check if event has expired
            event_end_time = event_state.get('event_end_time')
            if event_end_time and datetime.now() > event_end_time:
                print("Event has expired, clearing state")
                await self.clear_event_state()
                return False
            
            return True
            
        except Exception as e:
            print(f"Error validating event state: {e}")
            return False
    
    async def clear_event_state(self):
        """Xóa event state đã expired"""
        try:
            await self.db.delete_bot_state(EVENT_STATE)
        except Exception as e:
            print(f"Error clearing event state: {e}")
    
    # System State Management
    async def save_system_startup_time(self):
        """Lưu thời gian khởi động hệ thống"""
        try:
            await self.db.set_bot_state_value(
                AI_SYSTEM_STATE, 
                'last_startup', 
                datetime.now().isoformat()
            )
        except Exception as e:
            print(f"Error saving system startup time: {e}")
    
    async def get_system_uptime(self) -> Optional[timedelta]:
        """Lấy thời gian uptime của hệ thống"""
        try:
            startup_time_str = await self.db.get_bot_state_value(
                AI_SYSTEM_STATE, 
                'last_startup'
            )
            
            if startup_time_str:
                startup_time = datetime.fromisoformat(startup_time_str)
                return datetime.now() - startup_time
            
            return None
            
        except Exception as e:
            print(f"Error getting system uptime: {e}")
            return None
    
    # Utility Methods
    async def get_all_states(self) -> Dict[str, Any]:
        """Lấy tất cả states để debugging"""
        try:
            weather_state = await self.load_weather_state()
            event_state = await self.load_event_state()
            
            return {
                'weather_cycle': weather_state,
                'event_system': event_state,
                'system_uptime': await self.get_system_uptime()
            }
            
        except Exception as e:
            print(f"Error getting all states: {e}")
            return {}
    
    async def cleanup_old_states(self, max_age_days: int = 7):
        """Cleanup các states cũ"""
        try:
            # This would be more complex in a real implementation
            # For now, just validate current states
            await self.is_weather_state_valid()
            await self.is_event_state_valid()
            
        except Exception as e:
            print(f"Error cleaning up old states: {e}") 