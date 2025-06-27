import discord
from datetime import datetime
from typing import List, Optional
import config
from database.models import User, Crop
from utils.helpers import is_crop_ready, get_crop_growth_progress, format_time_remaining

class EmbedBuilder:
    """Utility class for creating Discord embeds"""
    
    @staticmethod
    def create_base_embed(title: str, description: str = "", color: int = 0x00ff00) -> discord.Embed:
        """Create a base embed with consistent styling"""
        embed = discord.Embed(
            title=title,
            description=description,
            color=color,
            timestamp=datetime.now()
        )
        embed.set_footer(text="🌾 Bot Nông Trại", icon_url="https://cdn.discordapp.com/emojis/1234567890123456789.png")
        return embed
    
    @staticmethod
    def create_profile_embed(user: User) -> discord.Embed:
        """Create user profile embed"""
        embed = EmbedBuilder.create_base_embed(f"👤 Hồ sơ của {user.username}", color=0x3498db)
        
        embed.add_field(
            name="💰 Tiền",
            value=f"{user.money:,} coins",
            inline=True
        )
        
        embed.add_field(
            name="🏞️ Đất đai",
            value=f"{user.land_slots} ô đất",
            inline=True
        )
        
        embed.add_field(
            name="🔥 Streak điểm danh",
            value=f"{user.daily_streak} ngày",
            inline=True
        )
        
        embed.add_field(
            name="📅 Tham gia",
            value=user.joined_date.strftime("%d/%m/%Y"),
            inline=True
        )
        
        return embed
    
    @staticmethod
    def create_farm_embed(user: User, crops: List[Crop]) -> discord.Embed:
        """Create farm overview embed"""
        embed = EmbedBuilder.create_base_embed(f"🌾 Nông trại của {user.username}", color=0x2ecc71)
        
        # Create farm grid visualization
        farm_grid = ["⬜"] * user.land_slots
        
        for crop in crops:
            if crop.plot_index < len(farm_grid):
                crop_config = config.CROPS.get(crop.crop_type, {})
                growth_time = crop_config.get('growth_time', 300)
                elapsed_time = (datetime.now() - crop.plant_time).total_seconds()
                
                if elapsed_time >= growth_time:
                    # Ready to harvest
                    farm_grid[crop.plot_index] = "✨"
                else:
                    # Growing
                    progress = min(elapsed_time / growth_time, 1.0)
                    if progress < 0.33:
                        farm_grid[crop.plot_index] = "🌱"
                    elif progress < 0.66:
                        farm_grid[crop.plot_index] = "🌿"
                    else:
                        farm_grid[crop.plot_index] = "🌾"
        
        # Display grid (4 columns)
        grid_rows = []
        for i in range(0, len(farm_grid), 4):
            row = " ".join(farm_grid[i:i+4])
            grid_rows.append(row)
        
        embed.add_field(
            name="🗺️ Bản đồ nông trại",
            value="\n".join(grid_rows) if grid_rows else "Chưa có đất",
            inline=False
        )
        
        # Crop status
        if crops:
            crop_status = []
            for crop in crops:
                crop_config = config.CROPS.get(crop.crop_type, {})
                growth_time = crop_config.get('growth_time', 300)
                elapsed_time = (datetime.now() - crop.plant_time).total_seconds()
                
                if elapsed_time >= growth_time:
                    status = "✅ Có thể thu hoạch"
                else:
                    remaining = growth_time - elapsed_time
                    mins = int(remaining // 60)
                    secs = int(remaining % 60)
                    status = f"⏰ {mins}p {secs}s"
                
                crop_name = crop_config.get('name', crop.crop_type)
                crop_status.append(f"Ô {crop.plot_index + 1}: {crop_name} - {status}")
            
            embed.add_field(
                name="🌱 Trạng thái cây trồng",
                value="\n".join(crop_status[:5]),  # Limit to 5 crops
                inline=False
            )
        
        embed.add_field(
            name="💰 Số dư",
            value=f"{user.money:,} coins",
            inline=True
        )
        
        return embed
    
    @staticmethod
    async def create_farm_embed_paginated(user: User, crops: List[Crop], page: int = 0, plots_per_page: int = 8, bot=None) -> discord.Embed:
        """Create paginated farm overview embed"""
        # Calculate page info
        total_pages = (user.land_slots - 1) // plots_per_page + 1
        start_plot = page * plots_per_page
        end_plot = min(start_plot + plots_per_page, user.land_slots)
        
        # Get event and weather modifiers
        weather_modifier = 1.0
        event_growth_modifier = 1.0
        event_yield_modifier = 1.0
        event_info = ""
        
        if bot:
            # Get weather modifier
            weather_cog = bot.get_cog('WeatherCog')
            if weather_cog:
                try:
                    _, weather_modifier = await weather_cog.get_current_weather_modifier()
                except:
                    pass
            
            # Get event modifiers
            events_cog = bot.get_cog('EventsCog')
            if events_cog:
                try:
                    if hasattr(events_cog, 'get_current_growth_modifier'):
                        event_growth_modifier = events_cog.get_current_growth_modifier()
                    if hasattr(events_cog, 'get_current_yield_modifier'):
                        event_yield_modifier = events_cog.get_current_yield_modifier()
                    
                    # Get current event info for display
                    if hasattr(events_cog, 'current_event') and events_cog.current_event:
                        event_data = events_cog.current_event.get('data', {})
                        event_name = event_data.get('name', 'Sự kiện đặc biệt')
                        event_info = f"🎯 **{event_name}**\n"
                except:
                    pass
        
        embed_title = f"🌾 Nông trại của {user.username}"
        embed_description = f"Trang {page + 1}/{total_pages} • Ô {start_plot + 1}-{end_plot}/{user.land_slots}"
        
        if event_info:
            embed_description = event_info + embed_description
        
        embed = EmbedBuilder.create_base_embed(
            embed_title,
            embed_description,
            color=0x2ecc71
        )
        
        # Create farm grid visualization for current page
        page_plots = ["⬜"] * (end_plot - start_plot)
        
        # Fill with crop data using proper modifiers
        for crop in crops:
            if start_plot <= crop.plot_index < end_plot:
                local_index = crop.plot_index - start_plot
                
                # Use helper functions with modifiers
                if is_crop_ready(crop.plant_time, crop.crop_type, weather_modifier, event_growth_modifier, user.user_id):
                    # Ready to harvest
                    page_plots[local_index] = "✨"
                else:
                    # Growing - use progress with modifiers
                    progress = get_crop_growth_progress(crop.plant_time, crop.crop_type, weather_modifier, event_growth_modifier, user.user_id)
                    if progress < 0.33:
                        page_plots[local_index] = "🌱"
                    elif progress < 0.66:
                        page_plots[local_index] = "🌿"
                    else:
                        page_plots[local_index] = "🌾"
        
        # Display grid (4 columns)
        grid_rows = []
        for i in range(0, len(page_plots), 4):
            row_plots = page_plots[i:i+4]
            row_numbers = [str(start_plot + i + j + 1) for j in range(len(row_plots))]
            
            # Add plot numbers and symbols with better formatting
            symbols_row = " ".join([f"{plot:^3}" for plot in row_plots])
            numbers_row = " ".join([f"{num:^3}" for num in row_numbers])
            
            grid_rows.append(symbols_row)
            grid_rows.append(numbers_row)
            if i + 4 < len(page_plots):  # Add separator between rows
                grid_rows.append("")
        
        embed.add_field(
            name="🗺️ Bản đồ nông trại",
            value="\n".join(grid_rows) if grid_rows else "Chưa có đất",
            inline=False
        )
        
        # Crop status for current page only with proper modifiers
        page_crops = [crop for crop in crops if start_plot <= crop.plot_index < end_plot]
        if page_crops:
            crop_status = []
            for crop in page_crops:
                crop_config = config.CROPS.get(crop.crop_type, {})
                crop_name = crop_config.get('name', crop.crop_type)
                
                if is_crop_ready(crop.plant_time, crop.crop_type, weather_modifier, event_growth_modifier, user.user_id):
                    status = "✅ Có thể thu hoạch"
                else:
                    # Use format_time_remaining with modifiers
                    status = f"⏰ {format_time_remaining(crop.plant_time, crop.crop_type, weather_modifier, event_growth_modifier, user.user_id)}"
                
                crop_status.append(f"Ô {crop.plot_index + 1}: {crop_name} - {status}")
            
            embed.add_field(
                name="🌱 Trạng thái cây trồng",
                value="\n".join(crop_status),
                inline=False
            )
        
        # Summary info
        total_crops = len(crops)
        ready_crops = sum(1 for crop in crops if is_crop_ready(crop.plant_time, crop.crop_type, weather_modifier, event_growth_modifier, user.user_id))
        
        embed.add_field(
            name="📊 Tổng quan",
            value=f"Tổng cây: {total_crops}/{user.land_slots}\nSẵn sàng thu hoạch: {ready_crops}",
            inline=True
        )
        
        embed.add_field(
            name="💰 Số dư",
            value=f"{user.money:,} coins",
            inline=True
        )
        
        # Add navigation info if multiple pages
        if total_pages > 1:
            embed.add_field(
                name="🔄 Điều hướng",
                value=f"Sử dụng các nút ◀️ ▶️ để xem tất cả {user.land_slots} ô đất",
                inline=False
            )
        
        return embed
    

    
    @staticmethod
    def create_shop_embed() -> discord.Embed:
        """Create shop embed"""
        embed = EmbedBuilder.create_base_embed("🏪 Cửa hàng Nông Trại", "Chọn danh mục sản phẩm bạn muốn xem:", color=0xf39c12)
        
        # Seeds section overview
        embed.add_field(
            name="🌱 Hạt Giống",
            value="• Cây trồng cơ bản và cao cấp\n• Thời gian sinh trưởng khác nhau\n• Lợi nhuận từ thấp đến cao\n• `f!buy <crop_id> <số_lượng>`",
            inline=True
        )
        
        # Land expansion overview  
        embed.add_field(
            name="🏞️ Mở Rộng Đất",
            value="• Tăng số ô đất trồng trọt\n• Chi phí tăng dần theo cấp\n• Tối đa có thể mở rộng\n• `f!buy land`",
            inline=True
        )
        
        # Fish overview
        embed.add_field(
            name="🐟 Cá",
            value="• 3 tier: Cơ bản, Hiếm, Huyền thoại\n• Nuôi trong ao (f!pond)\n• Có khả năng đặc biệt\n• `f!pond buy <fish_id>`",
            inline=True
        )
        
        # Livestock overview
        embed.add_field(
            name="🐄 Gia Súc",
            value="• Động vật nuôi trong chuồng\n• Sản xuất sản phẩm định kỳ\n• Giá trị cao, thời gian lâu\n• `f!barn buy <animal_id>`",
            inline=True
        )
        
        # Quick stats
        total_crops = len(config.CROPS)
        total_fish = len(config.FISH_SPECIES)
        total_animals = len(config.ANIMAL_SPECIES)
        
        embed.add_field(
            name="📊 Thống Kê Cửa Hàng",
            value=f"🌱 {total_crops} loại hạt giống\n🐟 {total_fish} loại cá\n🐄 {total_animals} loại gia súc",
            inline=True
        )
        
        # Usage instructions
        embed.add_field(
            name="💡 Hướng Dẫn Sử Dụng",
            value="• Nhấn nút bên dưới để xem chi tiết từng danh mục\n• Kiểm tra số dư và ô trống trước khi mua\n• Mỗi loại có yêu cầu khác nhau",
            inline=False
        )
        
        return embed
    
    @staticmethod
    def create_leaderboard_embed(users: List[User], board_type: str = "money") -> discord.Embed:
        """Create leaderboard embed"""
        title_map = {
            "money": "💰 Bảng xếp hạng Giàu có",
            "streak": "🔥 Bảng xếp hạng Streak",
            "land": "🏞️ Bảng xếp hạng Đất đai"
        }
        
        embed = EmbedBuilder.create_base_embed(
            title_map.get(board_type, "📊 Bảng xếp hạng"),
            color=0xe74c3c
        )
        
        if not users:
            embed.add_field(name="Trống", value="Chưa có dữ liệu", inline=False)
            return embed
        
        leaderboard_text = []
        medals = ["🥇", "🥈", "🥉"]
        
        for i, user in enumerate(users[:10]):
            rank = medals[i] if i < 3 else f"{i+1}."
            
            if board_type == "money":
                value = f"{user.money:,} coins"
            elif board_type == "streak":
                value = f"{user.daily_streak} ngày"
            elif board_type == "land":
                value = f"{user.land_slots} ô đất"
            else:
                value = "N/A"
            
            leaderboard_text.append(f"{rank} **{user.username}** - {value}")
        
        embed.add_field(
            name="Top 10",
            value="\n".join(leaderboard_text),
            inline=False
        )
        
        return embed
    
    @staticmethod
    def create_daily_embed(reward: int, streak: int, is_first_time: bool = False) -> discord.Embed:
        """Create daily reward embed"""
        if is_first_time:
            embed = EmbedBuilder.create_base_embed(
                "🎉 Chào mừng đến với nông trại!",
                f"Bạn đã nhận {reward} coins khởi điểm!",
                color=0x9b59b6
            )
        else:
            embed = EmbedBuilder.create_base_embed(
                "📅 Điểm danh hàng ngày",
                f"Bạn đã nhận {reward} coins!",
                color=0x3498db
            )
        
        embed.add_field(
            name="🔥 Streak hiện tại",
            value=f"{streak} ngày",
            inline=True
        )
        
        if streak < config.MAX_DAILY_STREAK:
            next_bonus = config.DAILY_REWARD_BASE + (streak + 1) * 10
            embed.add_field(
                name="🎁 Phần thưởng ngày mai",
                value=f"{next_bonus} coins",
                inline=True
            )
        else:
            embed.add_field(
                name="🏆 Streak tối đa",
                value="Bạn đã đạt streak cao nhất!",
                inline=True
            )
        
        return embed
    
    @staticmethod
    def create_weather_embed(weather_data: dict) -> discord.Embed:
        """Create weather embed"""
        weather_map = {
            'clear': {'emoji': '☀️', 'name': 'Nắng'},
            'clouds': {'emoji': '☁️', 'name': 'Nhiều mây'},
            'rain': {'emoji': '🌧️', 'name': 'Mưa'},
            'thunderstorm': {'emoji': '⛈️', 'name': 'Bão'},
            'snow': {'emoji': '🌨️', 'name': 'Tuyết'},
            'mist': {'emoji': '🌫️', 'name': 'Sương mù'}
        }
        
        weather_main = weather_data.get('weather', [{}])[0].get('main', '').lower()
        weather_info = weather_map.get(weather_main, {'emoji': '🌤️', 'name': 'Khác'})
        
        embed = EmbedBuilder.create_base_embed(
            f"{weather_info['emoji']} Thời tiết hiện tại",
            f"Điều kiện thời tiết đang ảnh hưởng đến nông trại của bạn",
            color=0x34495e
        )
        
        embed.add_field(
            name="🌡️ Nhiệt độ",
            value=f"{weather_data.get('main', {}).get('temp', 0):.1f}°C",
            inline=True
        )
        
        embed.add_field(
            name="🌤️ Thời tiết",
            value=weather_info['name'],
            inline=True
        )
        
        embed.add_field(
            name="💧 Độ ẩm",
            value=f"{weather_data.get('main', {}).get('humidity', 0)}%",
            inline=True
        )
        
        # Weather effects
        effects = config.WEATHER_EFFECTS.get(weather_main, config.WEATHER_EFFECTS['cloudy'])
        
        embed.add_field(
            name="📈 Hiệu ứng lên cây trồng",
            value=f"Tốc độ sinh trưởng: {effects['growth_modifier']:.1%}\nSản lượng: {effects['yield_modifier']:.1%}",
            inline=False
        )
        
        return embed
    
    @staticmethod
    def create_error_embed(message: str) -> discord.Embed:
        """Create error embed"""
        return EmbedBuilder.create_base_embed("❌ Lỗi", message, color=0xe74c3c)
    
    @staticmethod
    def create_success_embed(title: str, message: str) -> discord.Embed:
        """Create success embed"""
        return EmbedBuilder.create_base_embed(f"✅ {title}", message, color=0x2ecc71) 