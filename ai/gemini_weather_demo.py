"""
Demo: Gemini Game Master Weather Control System
Minh họa cách Gemini có thể thay đổi thời tiết mỗi 15 phút dựa trên game state
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any

class WeatherControlDemo:
    """Demo hệ thống điều khiển thời tiết của Gemini Game Master"""
    
    def __init__(self):
        self.weather_types = [
            'sunny',    # Nắng - tăng trưởng nhanh, giá bán cao
            'cloudy',   # Mây - cân bằng
            'rainy',    # Mưa - tăng chất lượng, giá hạt giống rẻ
            'windy',    # Gió - tăng tốc độ thu hoạch
            'foggy',    # Sương mù - giảm hiệu suất
            'storm',    # Bão - rủi ro cao, phần thưởng cao
            'drought'   # Hạn hán - giá nước tăng, cây khó trồng
        ]
        
        self.weather_effects = {
            'sunny': {
                'growth_rate': 1.3,
                'sell_price': 1.2,
                'quality_bonus': 1.0,
                'satisfaction': 0.8,
                'best_for': 'Tăng thu nhập nhanh'
            },
            'cloudy': {
                'growth_rate': 1.0,
                'sell_price': 1.0,
                'quality_bonus': 1.1,
                'satisfaction': 0.7,
                'best_for': 'Cân bằng chung'
            },
            'rainy': {
                'growth_rate': 1.1,
                'sell_price': 0.9,
                'quality_bonus': 1.4,
                'satisfaction': 0.6,
                'best_for': 'Tăng chất lượng cây trồng'
            },
            'windy': {
                'growth_rate': 1.2,
                'sell_price': 1.1,
                'quality_bonus': 0.9,
                'satisfaction': 0.5,
                'best_for': 'Thu hoạch nhanh'
            },
            'foggy': {
                'growth_rate': 0.8,
                'sell_price': 1.3,
                'quality_bonus': 0.8,
                'satisfaction': 0.4,
                'best_for': 'Giá bán cao nhưng khó trồng'
            },
            'storm': {
                'growth_rate': 0.7,
                'sell_price': 1.5,
                'quality_bonus': 1.2,
                'satisfaction': 0.3,
                'best_for': 'Rủi ro cao, lợi nhuận cao'
            },
            'drought': {
                'growth_rate': 0.6,
                'sell_price': 1.4,
                'quality_bonus': 0.7,
                'satisfaction': 0.2,
                'best_for': 'Thử thách cho người chơi giàu có'
            }
        }
    
    def simulate_game_state(self, time_of_day: int, active_players: int, economic_health: float) -> Dict[str, Any]:
        """Mô phỏng trạng thái game tại thời điểm cụ thể"""
        return {
            'time_of_day': time_of_day,  # 0-23
            'active_players_15min': active_players,
            'total_players': active_players * 3,
            'economic_health_score': economic_health,
            'player_satisfaction': 0.7,
            'weather_duration_remaining': 5,  # < 15 minutes = cần thay đổi
            'current_weather': 'sunny',
            'weather_satisfaction': 0.6
        }
    
    def gemini_weather_decision(self, game_state: Dict[str, Any]) -> Dict[str, Any]:
        """Mô phỏng quyết định thời tiết của Gemini Game Master"""
        
        # Phân tích tình hình
        time = game_state['time_of_day']
        active_players = game_state['active_players_15min']
        economic_health = game_state['economic_health_score']
        current_weather = game_state['current_weather']
        weather_satisfaction = game_state['weather_satisfaction']
        
        # Logic quyết định thời tiết
        if time >= 6 and time <= 18:  # Ban ngày (6h-18h)
            if active_players > 10:  # Nhiều người chơi
                if economic_health < 0.6:  # Kinh tế yếu
                    # Chọn thời tiết tăng thu nhập
                    recommended_weather = 'sunny'
                    reasoning = "Ban ngày + nhiều người chơi + kinh tế yếu → cần thời tiết tăng thu nhập"
                elif weather_satisfaction < 0.6:  # Không hài lòng với thời tiết
                    # Thay đổi để tăng satisfaction
                    recommended_weather = 'cloudy' if current_weather in ['storm', 'drought'] else 'rainy'
                    reasoning = "Thời tiết hiện tại không được ưa chuộng → chuyển sang thời tiết cân bằng hơn"
                else:
                    # Tạo thử thách nhẹ
                    recommended_weather = 'windy'
                    reasoning = "Tình hình tốt → tạo thử thách nhẹ với thời tiết windy"
            else:  # Ít người chơi
                # Thời tiết dễ chơi để khuyến khích
                recommended_weather = 'sunny'
                reasoning = "Ít người chơi → chọn thời tiết dễ chơi để khuyến khích tham gia"
        else:  # Ban đêm (19h-5h)
            if active_players > 5:  # Vẫn có người chơi đêm
                # Tạo thử thách thú vị
                recommended_weather = 'storm' if economic_health > 0.7 else 'rainy'
                reasoning = "Ban đêm + có người chơi → tạo thử thách thú vị"
            else:
                # Thời tiết nhẹ nhàng cho người chơi đêm
                recommended_weather = 'cloudy'
                reasoning = "Ban đêm + ít người → thời tiết nhẹ nhàng"
        
        # Tính thời gian duy trì (15-60 phút tùy tình hình)
        if active_players > 15:
            duration_minutes = 15  # Thay đổi nhanh khi đông người
        elif active_players > 5:
            duration_minutes = 30  # Trung bình
        else:
            duration_minutes = 60  # Ít người thì giữ lâu hơn
        
        return {
            "analysis": f"Thời gian: {time}h, Người chơi: {active_players}, Kinh tế: {economic_health:.1%}",
            "action_type": "weather_control",
            "reasoning": reasoning,
            "confidence": 0.85,
            "parameters": {
                "weather_type": recommended_weather,
                "duration_hours": duration_minutes / 60
            },
            "expected_impact": f"Tăng {self.weather_effects[recommended_weather]['best_for']}",
            "priority": "high" if game_state['weather_duration_remaining'] < 10 else "medium",
            "affected_users": "all"
        }
    
    def run_24hour_simulation(self):
        """Chạy mô phỏng 24 giờ với Gemini thay đổi thời tiết mỗi 15 phút"""
        print("🌤️ GEMINI GAME MASTER - WEATHER CONTROL SIMULATION")
        print("=" * 60)
        print("Mô phỏng 24 giờ với Gemini thay đổi thời tiết mỗi 15 phút")
        print()
        
        weather_schedule = []
        
        # Mô phỏng từng khung giờ
        for hour in range(24):
            # Tính số người chơi dựa trên giờ
            if 6 <= hour <= 9:  # Sáng sớm
                active_players = 8
            elif 10 <= hour <= 12:  # Trưa
                active_players = 15
            elif 13 <= hour <= 17:  # Chiều
                active_players = 20
            elif 18 <= hour <= 22:  # Tối
                active_players = 25
            else:  # Đêm khuya
                active_players = 3
            
            # Tính sức khỏe kinh tế (dao động theo thời gian)
            economic_health = 0.5 + 0.3 * (active_players / 25)
            
            # Tạo game state
            game_state = self.simulate_game_state(hour, active_players, economic_health)
            
            # Gemini đưa ra quyết định
            decision = self.gemini_weather_decision(game_state)
            
            # Lưu vào lịch trình
            weather_info = {
                'time': f"{hour:02d}:00",
                'weather': decision['parameters']['weather_type'],
                'duration': int(decision['parameters']['duration_hours'] * 60),
                'players': active_players,
                'reasoning': decision['reasoning'],
                'effects': self.weather_effects[decision['parameters']['weather_type']]
            }
            weather_schedule.append(weather_info)
            
            # In thông tin
            print(f"⏰ {weather_info['time']} | 🌤️ {weather_info['weather'].upper():<8} | "
                  f"👥 {weather_info['players']:2d} players | ⏱️ {weather_info['duration']:2d}min")
            print(f"   💡 {weather_info['reasoning']}")
            print(f"   📊 Growth: {weather_info['effects']['growth_rate']:.1f}x | "
                  f"Price: {weather_info['effects']['sell_price']:.1f}x | "
                  f"Quality: {weather_info['effects']['quality_bonus']:.1f}x")
            print()
        
        # Thống kê tổng kết
        print("📈 THỐNG KÊ TỔNG KẾT")
        print("=" * 60)
        
        weather_count = {}
        for entry in weather_schedule:
            weather = entry['weather']
            weather_count[weather] = weather_count.get(weather, 0) + 1
        
        print("🌤️ Phân bố thời tiết trong 24h:")
        for weather, count in sorted(weather_count.items()):
            percentage = (count / 24) * 100
            print(f"   {weather:<8}: {count:2d} lần ({percentage:4.1f}%)")
        
        print(f"\n🎯 Tổng số lần thay đổi: {len(weather_schedule)} lần")
        print(f"⏱️ Trung bình mỗi {24*60/len(weather_schedule):.0f} phút thay đổi 1 lần")
        
        # Lưu kết quả
        with open('cache/gemini_weather_simulation.json', 'w', encoding='utf-8') as f:
            json.dump({
                'simulation_time': datetime.now().isoformat(),
                'weather_schedule': weather_schedule,
                'statistics': weather_count
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Kết quả đã lưu vào: cache/gemini_weather_simulation.json")

if __name__ == "__main__":
    demo = WeatherControlDemo()
    demo.run_24hour_simulation() 