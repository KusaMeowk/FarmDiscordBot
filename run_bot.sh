#!/bin/bash

# ===============================
# SCRIPT CHẠY BOT NÔNG TRẠI
# ===============================

echo "🚀 Đang khởi động Bot Nông Trại..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Không tìm thấy virtual environment!"
    echo "Chạy setup trước: bash ubuntu_quick_setup.sh"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ Không tìm thấy file .env!"
    echo "Tạo file .env và điền Discord token + Gemini API key"
    exit 1
fi

# Activate virtual environment
echo "🔧 Kích hoạt virtual environment..."
source venv/bin/activate

# Check if requirements are installed
echo "🔍 Kiểm tra dependencies..."
python3 -c "import discord" 2>/dev/null || {
    echo "❌ Discord.py chưa được cài đặt!"
    echo "Chạy: pip install -r requirements.txt"
    exit 1
}

# Start the bot
echo "🎮 Khởi động Bot Nông Trại..."
echo "📍 Bot sẽ chạy tại: $(pwd)"
echo "⏰ Thời gian: $(date)"
echo "----------------------------------------"

python3 bot.py 