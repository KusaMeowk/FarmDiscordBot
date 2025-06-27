#!/bin/bash

# ===============================
# TẠO SYSTEMD SERVICE CHO BOT
# ===============================

BOT_DIR=$(pwd)
BOT_USER=$(whoami)

echo "🔧 Tạo systemd service cho Bot Nông Trại..."
echo "📍 Thư mục bot: $BOT_DIR"
echo "👤 User: $BOT_USER"

# Create service file
sudo tee /etc/systemd/system/farmbot.service > /dev/null << EOF
[Unit]
Description=Farm Bot Discord Game
After=network.target
Wants=network.target

[Service]
Type=simple
User=$BOT_USER
Group=$BOT_USER
WorkingDirectory=$BOT_DIR
Environment=PATH=$BOT_DIR/venv/bin
ExecStart=$BOT_DIR/venv/bin/python $BOT_DIR/bot.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# Security settings
NoNewPrivileges=yes
PrivateTmp=yes
ProtectSystem=strict
ReadWritePaths=$BOT_DIR

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and enable service
echo "🔄 Reload systemd daemon..."
sudo systemctl daemon-reload

echo "✅ Enable farmbot service..."
sudo systemctl enable farmbot

echo ""
echo "🎉 SYSTEMD SERVICE ĐÃ ĐƯỢC TẠO!"
echo ""
echo "📝 CÁCH SỬ DỤNG:"
echo "• Khởi động bot: sudo systemctl start farmbot"
echo "• Dừng bot: sudo systemctl stop farmbot"
echo "• Khởi động lại: sudo systemctl restart farmbot"
echo "• Xem trạng thái: sudo systemctl status farmbot"
echo "• Xem logs: sudo journalctl -u farmbot -f"
echo "• Tắt auto-start: sudo systemctl disable farmbot"
echo ""
echo "⚠️ QUAN TRỌNG:"
echo "• Đảm bảo file .env đã được cấu hình đúng"
echo "• Bot sẽ tự động khởi động khi server reboot" 