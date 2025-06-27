#!/usr/bin/env python3
"""
Gemini Game Master - Proof of Concept
"""

import asyncio
import json
import os
from typing import Dict

class GeminiGameMasterPOC:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        print("⚠️ Running in demo mode without Gemini API")
    
    async def analyze_game_situation(self, game_data: Dict) -> Dict:
        """Phân tích tình hình game"""
        return self._mock_gemini_response(game_data)
    
    def _mock_gemini_response(self, game_data: Dict) -> Dict:
        """Mock response cho demo"""
        satisfaction = game_data['player_satisfaction']
        activity = game_data['activity_level']
        
        if satisfaction < 0.5:
            mood = "frustrated"
            urgency = "high"
            action_name = "🎉 Lễ Hội Mùa Xuân"
            reasoning = "Players đang không hài lòng, cần event boost morale"
        elif activity < 0.3:
            mood = "bored"
            urgency = "medium"
            action_name = "🌟 Thử Thách Nông Dân"
            reasoning = "Hoạt động thấp, cần tạo excitement"
        else:
            mood = "neutral"
            urgency = "low"
            action_name = "☀️ Nắng Đẹp"
            reasoning = "Tình hình ổn định, duy trì"
        
        return {
            "source": "mock",
            "overall_analysis": f"Game đang trong tình trạng {mood}. Player satisfaction {satisfaction:.1%}, hoạt động {activity:.1%}.",
            "player_mood": mood,
            "urgency_level": urgency,
            "recommended_actions": [{
                "type": "event",
                "priority": urgency,
                "probability": 0.75,
                "reasoning": reasoning,
                "parameters": {
                    "name": action_name,
                    "description": f"Event để cải thiện tình hình {mood}",
                    "duration_hours": 6,
                    "effects": {"modifier": 1.2}
                }
            }],
            "predictions": {
                "player_satisfaction_24h": min(satisfaction + 0.2, 1.0),
                "economic_stability": "stable",
                "engagement_forecast": "improving"
            }
        }

async def demo_gemini_game_master():
    """Demo POC"""
    print("🤖 Gemini Game Master - Proof of Concept")
    print("=" * 50)
    
    mock_game_data = {
        'active_players': 45,
        'total_money': 2500000,
        'activity_level': 0.65,
        'current_weather': 'sunny',
        'player_satisfaction': 0.45,  # Low satisfaction
        'economic_health': 0.75
    }
    
    gm = GeminiGameMasterPOC()
    
    print("\n📊 TÌNH HÌNH GAME:")
    print(f"🎮 Players: {mock_game_data['active_players']}")
    print(f"💰 Tiền: {mock_game_data['total_money']:,} coins")
    print(f"📈 Hoạt động: {mock_game_data['activity_level']:.1%}")
    print(f"😊 Hài lòng: {mock_game_data['player_satisfaction']:.1%}")
    
    analysis = await gm.analyze_game_situation(mock_game_data)
    
    print(f"\n✨ PHÂN TÍCH AI:")
    print(f"📝 {analysis['overall_analysis']}")
    print(f"😊 Mood: {analysis['player_mood']}")
    print(f"⚡ Urgency: {analysis['urgency_level']}")
    
    action = analysis['recommended_actions'][0]
    print(f"\n🎯 ĐỀ XUẤT:")
    print(f"📛 {action['parameters']['name']}")
    print(f"📋 {action['reasoning']}")
    print(f"🎯 Priority: {action['priority']}")

if __name__ == "__main__":
    asyncio.run(demo_gemini_game_master()) 