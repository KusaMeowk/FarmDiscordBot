"""
Maid System Monitoring & Security
Track usage, buffs, và detect suspicious activity
"""
import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class MaidMonitoringSystem:
    def __init__(self, db_path: str = "farm_bot.db"):
        self.db_path = db_path
        self.init_tables()
    
    def init_tables(self):
        """Tạo bảng monitoring"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Bảng buff usage logs
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS maid_buff_logs (
                        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        buff_type TEXT,
                        buff_value REAL,
                        base_value INTEGER,
                        final_value INTEGER,
                        timestamp TEXT,
                        context TEXT
                    )
                ''')
                
                # Bảng security alerts
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS maid_security_alerts (
                        alert_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        alert_type TEXT,
                        description TEXT,
                        severity TEXT,
                        timestamp TEXT,
                        resolved BOOLEAN DEFAULT 0
                    )
                ''')
                
                conn.commit()
        except Exception as e:
            print(f"Error initializing monitoring tables: {e}")
    
    def log_buff_usage(self, user_id: int, buff_type: str, buff_value: float, 
                      base_value: int, final_value: int, context: str = ""):
        """Log buff usage để track economic impact"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO maid_buff_logs 
                    (user_id, buff_type, buff_value, base_value, final_value, timestamp, context)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_id, buff_type, buff_value, base_value, 
                    final_value, datetime.now().isoformat(), context
                ))
                conn.commit()
        except Exception as e:
            print(f"Error logging buff usage: {e}")
    
    def create_security_alert(self, user_id: int, alert_type: str, 
                            description: str, severity: str = "medium"):
        """Tạo security alert"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO maid_security_alerts 
                    (user_id, alert_type, description, severity, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    user_id, alert_type, description, 
                    severity, datetime.now().isoformat()
                ))
                conn.commit()
        except Exception as e:
            print(f"Error creating security alert: {e}")
    
    def detect_suspicious_buff_usage(self, user_id: int) -> List[str]:
        """Detect suspicious buff usage patterns"""
        alerts = []
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check for excessive buff values
                cursor.execute('''
                    SELECT buff_type, MAX(buff_value) as max_buff, COUNT(*) as usage_count
                    FROM maid_buff_logs 
                    WHERE user_id = ? AND timestamp > datetime('now', '-24 hours')
                    GROUP BY buff_type
                ''', (user_id,))
                
                for row in cursor.fetchall():
                    buff_type, max_buff, usage_count = row
                    
                    # Suspicious high buff values
                    if max_buff > 100:  # Over 100% is suspicious
                        alerts.append(f"High {buff_type} buff: {max_buff}%")
                        self.create_security_alert(
                            user_id, "high_buff_value", 
                            f"Buff {buff_type} reached {max_buff}%", "high"
                        )
                    
                    # Excessive usage
                    if usage_count > 1000:  # Over 1000 uses per day
                        alerts.append(f"Excessive {buff_type} usage: {usage_count} times")
                        self.create_security_alert(
                            user_id, "excessive_usage",
                            f"Buff {buff_type} used {usage_count} times in 24h", "medium"
                        )
                
        except Exception as e:
            print(f"Error detecting suspicious activity: {e}")
        
        return alerts
    
    def get_buff_statistics(self, hours: int = 24) -> Dict:
        """Get buff usage statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT 
                        buff_type,
                        COUNT(*) as usage_count,
                        AVG(buff_value) as avg_buff,
                        MAX(buff_value) as max_buff,
                        SUM(final_value - base_value) as total_economic_impact
                    FROM maid_buff_logs 
                    WHERE timestamp > datetime('now', '-{} hours')
                    GROUP BY buff_type
                    ORDER BY usage_count DESC
                '''.format(hours))
                
                stats = {}
                for row in cursor.fetchall():
                    buff_type, count, avg_buff, max_buff, impact = row
                    stats[buff_type] = {
                        "usage_count": count,
                        "avg_buff": round(avg_buff, 2),
                        "max_buff": max_buff,
                        "economic_impact": impact or 0
                    }
                
                return stats
        except Exception as e:
            print(f"Error getting buff statistics: {e}")
            return {}
    
    def cleanup_old_logs(self, days_old: int = 30):
        """Cleanup logs cũ hơn X ngày"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Cleanup buff logs
                cursor.execute('''
                    DELETE FROM maid_buff_logs 
                    WHERE timestamp < datetime('now', '-{} days')
                '''.format(days_old))
                deleted_logs = cursor.rowcount
                
                # Cleanup resolved alerts
                cursor.execute('''
                    DELETE FROM maid_security_alerts 
                    WHERE resolved = 1 AND timestamp < datetime('now', '-{} days')
                '''.format(days_old))
                deleted_alerts = cursor.rowcount
                
                conn.commit()
                
                if deleted_logs > 0 or deleted_alerts > 0:
                    print(f"Cleaned up {deleted_logs} logs and {deleted_alerts} alerts")
                
                return deleted_logs + deleted_alerts
        except Exception as e:
            print(f"Error cleaning up logs: {e}")
            return 0

# Global instance
maid_monitor = MaidMonitoringSystem() 