#!/usr/bin/env python3
"""
Restart Bot Script
Script để restart bot và load configuration changes mới
"""

import sys
import os
import subprocess
import time
import psutil
import signal

def find_bot_process():
    """Tìm process bot đang chạy"""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['name'] == 'python.exe' or proc.info['name'] == 'python':
                cmdline = proc.info['cmdline']
                if cmdline and any('bot.py' in arg or 'start_bot.py' in arg for arg in cmdline):
                    return proc
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return None

def stop_bot():
    """Dừng bot process hiện tại"""
    bot_proc = find_bot_process()
    if bot_proc:
        print(f"🛑 Stopping bot process PID: {bot_proc.pid}")
        try:
            # Thử graceful shutdown trước
            bot_proc.send_signal(signal.SIGINT)
            # Đợi 5 giây cho graceful shutdown
            bot_proc.wait(timeout=5)
        except psutil.TimeoutExpired:
            # Force kill nếu không graceful shutdown được
            print("💥 Force killing bot process...")
            bot_proc.kill()
        except Exception as e:
            print(f"❌ Error stopping bot: {e}")
        
        print("✅ Bot stopped")
        return True
    else:
        print("ℹ️ No bot process found")
        return False

def start_bot():
    """Khởi động bot"""
    print("🚀 Starting bot...")
    
    # Kiểm tra file bot.py hoặc start_bot.py
    if os.path.exists('start_bot.py'):
        start_file = 'start_bot.py'
    elif os.path.exists('bot.py'):
        start_file = 'bot.py'
    else:
        print("❌ Bot file not found!")
        return False
    
    try:
        # Khởi động bot trong background
        subprocess.Popen([sys.executable, start_file], 
                        creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0)
        print(f"✅ Bot started with {start_file}")
        return True
    except Exception as e:
        print(f"❌ Error starting bot: {e}")
        return False

def main():
    """Main restart function"""
    print("🔄 Bot Restart Script")
    print("=" * 40)
    
    # Bước 1: Stop bot hiện tại
    print("Step 1: Stopping current bot...")
    stop_bot()
    
    # Bước 2: Đợi 2 giây
    print("Step 2: Waiting for cleanup...")
    time.sleep(2)
    
    # Bước 3: Start bot mới
    print("Step 3: Starting bot with new config...")
    if start_bot():
        print("\n🎉 Bot restart completed!")
        print("✅ New PREFIX f! should now be active")
        print("💡 Try: f!help, f!mg, f!profile")
    else:
        print("\n❌ Bot restart failed!")
        print("💡 Try running manually: python bot.py")
    
    print("\n" + "=" * 40)

if __name__ == "__main__":
    main() 