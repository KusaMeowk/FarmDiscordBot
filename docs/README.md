# 🌾 Bot Discord Game Nông Trại

Một bot Discord game nông trại hoàn chỉnh được viết bằng Python với đầy đủ tính năng trồng trọt, kinh doanh và tương tác xã hội.

## ✨ Tính năng

### 🌱 Hệ thống Nông trại
- **Trồng cây**: 4 loại cây với thời gian sinh trưởng khác nhau
- **Bulk planting**: Trồng nhiều ô cùng lúc hoặc tất cả ô trống
- **Thu hoạch**: Sản lượng ngẫu nhiên, nông sản vào kho inventory
- **Thị trường động**: Giá bán thay đổi theo thời tiết và sự kiện
- **Bán nông sản**: Manual selling từ inventory với dynamic pricing
- **Thông báo giá**: Cảnh báo tự động khi giá biến động ≥ ngưỡng
- **Mở rộng đất**: Mua thêm ô đất để trồng nhiều cây hơn

### 🤖 AI Engine (MỚI!)
- **Game Master AI**: Phân tích trạng thái game và ra quyết định thông minh
- **Event Manager AI**: Tạo sự kiện contextual dựa trên hành vi người chơi  
- **Weather Predictor AI**: Quản lý weather patterns thích ứng
- **Adaptive Balance**: AI tự động cân bằng độ khó và tạo trải nghiệm dynamic
- **Personality System**: AI có tính cách có thể điều chỉnh (benevolence, mischief, unpredictability)
- **Real-time Analysis**: AI phân tích player satisfaction, activity level, economy balance
- **Smart Events**: Sự kiện được tạo contextual theo game state (Economy Boost, Recovery, Challenge, Surprise)

### 🏪 Hệ thống Cửa hàng  
- **Mua hạt giống**: 4 loại hạt với giá và thời gian khác nhau
- **Mở rộng trang trại**: Mua thêm ô đất với chi phí tăng dần
- **Bảng giá**: Xem thông tin chi tiết về lợi nhuận

### 📅 Hệ thống Điểm danh
- **Điểm danh hàng ngày**: Nhận coins và xây dựng streak
- **Streak bonus**: Phần thưởng tăng theo số ngày liên tiếp
- **Milestone rewards**: Thưởng đặc biệt cho các mốc streak

### 🌤️ Hệ thống Thời tiết
- **Thời tiết thực**: Lấy dữ liệu từ OpenWeatherMap API
- **Ảnh hưởng game**: Thời tiết ảnh hưởng đến tốc độ sinh trưởng và sản lượng
- **4 loại thời tiết**: Nắng, mưa, có mây, bão với hiệu ứng khác nhau
- **Thông báo tự động**: Cảnh báo khi thời tiết thay đổi (30 phút/lần)
- **Rate limiting**: Giới hạn 900 API calls/ngày, có cache 30 phút

### 📊 Hệ thống Thông báo
- **Thông báo thời tiết**: Setup kênh tự động thông báo thay đổi thời tiết
- **Thông báo giá**: Setup kênh tự động thông báo biến động giá nông sản
  - Kiểm tra mỗi 15 phút
  - Threshold tùy chỉnh (1% - 100%)
  - Hiển thị nguyên nhân và lời khuyên giao dịch
  - Ví dụ giá cả cụ thể

### 🎉 Hệ thống Sự kiện
- **Sự kiện theo mùa**: Tự động kích hoạt theo tháng
- **Sự kiện ngẫu nhiên**: 5% cơ hội mỗi giờ cho bonus đặc biệt
- **Hiệu ứng đa dạng**: Tăng tốc độ, sản lượng, giá bán

### 🏆 Hệ thống Xếp hạng
- **3 bảng xếp hạng**: Giàu có, Streak, Đất đai
- **So sánh người chơi**: Xem thứ hạng và so sánh với người khác
- **UI tương tác**: Chuyển đổi bảng xếp hạng bằng nút bấm

## 🛠️ Cài đặt

### Yêu cầu hệ thống
- Python 3.8+
- Discord Bot Token
- OpenWeatherMap API Key (tùy chọn)

### Bước 1: Clone dự án
```bash
git clone <repository-url>
cd BotNôngTrại
```

### Bước 2: Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### Bước 3: Cấu hình
1. Sao chép `.env.example` thành `.env`
2. Điền thông tin bot:
```env
DISCORD_TOKEN=your_bot_token_here
WEATHER_API_KEY=your_weather_api_key_here
PREFIX=f!
OWNER_ID=your_discord_user_id
```

### Bước 4: Chạy bot
```bash
python bot.py
```

## 📖 Hướng dẫn sử dụng

### Lệnh cơ bản
- `f!help` - Xem danh sách lệnh
- `f!register` - Đăng ký tài khoản nông trại
- `f!profile` - Xem hồ sơ của bạn

### Nông trại
- `f!farm` - Xem tổng quan nông trại
- `f!plant <loại_cây> <số_ô>` - Trồng cây đơn lẻ
- `f!plant <loại_cây> <số_ô>,<số_ô>,<số_ô>` - Trồng nhiều ô cụ thể
- `f!plant <loại_cây> all` - Trồng tất cả ô trống
- `f!harvest <số_ô>` - Thu hoạch cây vào kho
- `f!harvest all` - Thu hoạch tất cả vào kho
- `f!market` - Xem giá thị trường hiện tại
- `f!sell <loại_cây> <số_lượng>` - Bán nông sản từ kho
- `f!setupmarket [channel_id] [threshold]` - Setup thông báo biến động giá (Admin)
- `f!togglemarket [true/false]` - Bật/tắt thông báo giá (Admin)
- `f!marketstatus` - Xem trạng thái thông báo giá

### Cửa hàng
- `f!shop` - Xem cửa hàng
- `f!buy <vật_phẩm> <số_lượng>` - Mua vật phẩm
- `f!price` - Xem bảng giá

### Điểm danh
- `f!daily` - Điểm danh hàng ngày
- `f!streak` - Xem streak hiện tại
- `f!rewards` - Xem bảng phần thưởng

### Thời tiết
- `f!weather` - Xem thời tiết hiện tại
- `f!forecast` - Xem ảnh hưởng thời tiết
- `f!weatherstats` - Thống kê ảnh hưởng lên cây trồng
- `f!setupweather [channel_id] [city]` - Setup kênh thông báo thời tiết (Admin)
- `f!toggleweather [true/false]` - Bật/tắt thông báo thời tiết (Admin)
- `f!weatherstatus` - Xem trạng thái thông báo thời tiết
- `f!apistats` - Xem thống kê API usage (Admin only)
- `f!clearcache` - Xóa weather cache (Admin only)

### Sự kiện
- `f!event` - Xem sự kiện hiện tại
- `f!events` - Danh sách tất cả sự kiện
- `f!claim_event` - Nhận thưởng sự kiện

### Xếp hạng
- `f!leaderboard [money|streak|land]` - Xem bảng xếp hạng
- `f!rank` - Xem thứ hạng của bạn
- `f!compare @user` - So sánh với người khác

### AI Engine (Admin only)
- `f!ai` - Menu quản lý AI Engine
- `f!ai status` - Trạng thái hệ thống AI
- `f!ai report` - Báo cáo chi tiết hoạt động AI
- `f!ai analytics` - Phân tích performance AI
- `f!ai toggle` - Bật/tắt AI Engine
- `f!ai reset` - Reset trạng thái AI
- `f!ai force` - Buộc AI thực hiện analysis ngay

## 🌾 Loại cây trồng

| Tên | Emoji | Giá hạt | Thời gian | Giá bán | Lợi nhuận |
|-----|-------|---------|-----------|---------|-----------|
| Cà rót | 🥕 | 10 coins | 5 phút | 12 coins | 2 coins |
| Cà chua | 🍅 | 25 coins | 10 phút | 30 coins | 5 coins |
| Ngô | 🌽 | 50 coins | 20 phút | 60 coins | 10 coins |
| Lúa mì | 🌾 | 100 coins | 30 phút | 120 coins | 20 coins |

## 🌤️ Hiệu ứng thời tiết

| Thời tiết | Tốc độ sinh trưởng | Sản lượng |
|-----------|-------------------|-----------|
| ☀️ Nắng | +20% | +10% |
| 🌧️ Mưa | Bình thường | +30% |
| ☁️ Có mây | -10% | Bình thường |
| ⛈️ Bão | -30% | -20% |

## 🎉 Sự kiện

### Theo mùa
- **🌸 Mùa xuân** (Tháng 3): +20% tốc độ sinh trưởng
- **☀️ Mùa hè** (Tháng 6): +30% sản lượng  
- **🍂 Mùa thu** (Tháng 9): +15% giá bán
- **❄️ Mùa đông** (Tháng 12): +50% phần thưởng điểm danh

### Ngẫu nhiên
- **🍀 Ngày may mắn**: Sản lượng gấp đôi
- **⚡ Tăng tốc**: Phát triển gấp đôi
- **💰 Thị trường sôi động**: Giá bán x1.5
- **🌟 Hạt giống miễn phí**: Giảm 50% giá hạt

## 🔧 Cấu trúc dự án

```
BotNôngTrại/
├── bot.py                 # File chính để chạy bot
├── config.py             # Cấu hình game và API
├── requirements.txt      # Dependencies Python
├── database/
│   ├── database.py       # Quản lý database
│   └── models.py         # Data models
├── ai/
│   ├── game_master.py    # Game Master AI - bộ não chính
│   ├── event_manager.py  # Event Manager AI - quản lý sự kiện
│   └── weather_predictor.py # Weather Predictor AI - dự báo thời tiết
├── features/
│   ├── profile.py        # Quản lý hồ sơ người dùng
│   ├── farm.py          # Hệ thống nông trại
│   ├── shop.py          # Hệ thống cửa hàng
│   ├── daily.py         # Điểm danh hàng ngày
│   ├── weather.py       # Hệ thống thời tiết
│   ├── events.py        # Sự kiện theo mùa
│   ├── leaderboard.py   # Bảng xếp hạng
│   └── ai_manager.py    # AI Engine coordinator
├── utils/
│   ├── embeds.py        # Discord embed utilities
│   └── helpers.py       # Helper functions
└── memory-bank/         # Tài liệu dự án
```

## 🤝 Đóng góp

1. Fork dự án
2. Tạo feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Mở Pull Request

## 📝 License

Dự án này được phân phối dưới MIT License. Xem file `LICENSE` để biết thêm chi tiết.

## 📞 Hỗ trợ

Nếu gặp vấn đề hoặc có câu hỏi, hãy tạo issue trên GitHub hoặc liên hệ qua Discord.

## 🙏 Credits

- **Discord.py**: Framework Discord bot
- **OpenWeatherMap**: API thời tiết
- **SQLite**: Database engine 