import discord
from discord.ext import commands
import math
from utils.embeds import EmbedBuilder

class HelpPaginationView(discord.ui.View):
    """View pagination cho help system"""
    
    def __init__(self, bot, user_id, pages):
        super().__init__(timeout=300)
        self.bot = bot
        self.user_id = user_id
        self.pages = pages
        self.current_page = 0
        self.max_page = len(pages) - 1
        
        # Update button states
        self.update_buttons()
    
    def update_buttons(self):
        """Update button states based on current page"""
        self.first_page.disabled = self.current_page == 0
        self.prev_page.disabled = self.current_page == 0
        self.next_page.disabled = self.current_page >= self.max_page
        self.last_page.disabled = self.current_page >= self.max_page
    
    @discord.ui.button(emoji="⏪", style=discord.ButtonStyle.blurple)
    async def first_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            if interaction.user.id != self.user_id:
                await interaction.response.send_message("❌ Bạn không thể sử dụng nút này!", ephemeral=True)
                return
            
            self.current_page = 0
            self.update_buttons()
            embed = self.pages[self.current_page]
            await interaction.response.edit_message(embed=embed, view=self)
        except Exception as e:
            print(f"Help first page error: {e}")
            try:
                await interaction.response.send_message("❌ Có lỗi xảy ra. Vui lòng thử lại!", ephemeral=True)
            except:
                pass
    
    @discord.ui.button(emoji="◀️", style=discord.ButtonStyle.blurple)
    async def prev_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            if interaction.user.id != self.user_id:
                await interaction.response.send_message("❌ Bạn không thể sử dụng nút này!", ephemeral=True)
                return
            
            self.current_page -= 1
            self.update_buttons()
            embed = self.pages[self.current_page]
            await interaction.response.edit_message(embed=embed, view=self)
        except Exception as e:
            print(f"Help prev page error: {e}")
            try:
                await interaction.response.send_message("❌ Có lỗi xảy ra. Vui lòng thử lại!", ephemeral=True)
            except:
                pass
    
    @discord.ui.button(emoji="🏠", style=discord.ButtonStyle.green)
    async def home_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            if interaction.user.id != self.user_id:
                await interaction.response.send_message("❌ Bạn không thể sử dụng nút này!", ephemeral=True)
                return
            
            self.current_page = 0
            self.update_buttons()
            embed = self.pages[self.current_page]
            await interaction.response.edit_message(embed=embed, view=self)
        except Exception as e:
            print(f"Help home page error: {e}")
            try:
                await interaction.response.send_message("❌ Có lỗi xảy ra. Vui lòng thử lại!", ephemeral=True)
            except:
                pass
    
    @discord.ui.button(emoji="▶️", style=discord.ButtonStyle.blurple)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            if interaction.user.id != self.user_id:
                await interaction.response.send_message("❌ Bạn không thể sử dụng nút này!", ephemeral=True)
                return
            
            self.current_page += 1
            self.update_buttons()
            embed = self.pages[self.current_page]
            await interaction.response.edit_message(embed=embed, view=self)
        except Exception as e:
            print(f"Help next page error: {e}")
            try:
                await interaction.response.send_message("❌ Có lỗi xảy ra. Vui lòng thử lại!", ephemeral=True)
            except:
                pass
    
    @discord.ui.button(emoji="⏩", style=discord.ButtonStyle.blurple)
    async def last_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            if interaction.user.id != self.user_id:
                await interaction.response.send_message("❌ Bạn không thể sử dụng nút này!", ephemeral=True)
                return
            
            self.current_page = self.max_page
            self.update_buttons()
            embed = self.pages[self.current_page]
            await interaction.response.edit_message(embed=embed, view=self)
        except Exception as e:
            print(f"Help last page error: {e}")
            try:
                await interaction.response.send_message("❌ Có lỗi xảy ra. Vui lòng thử lại!", ephemeral=True)
            except:
                pass

class HelpSystemCog(commands.Cog):
    """Hệ thống help mới với pagination và shortcuts"""
    
    def __init__(self, bot):
        self.bot = bot
        
        # Command categories với descriptions
        self.categories = {
            "👤 Profile & Account": {
                "description": "Quản lý hồ sơ và tài khoản cá nhân",
                "commands": ["profile", "inventory", "register", "rename"],
                "emoji": "👤"
            },
            "🌾 Farming Core": {
                "description": "Trồng trọt và quản lý nông trại", 
                "commands": ["farm", "plant", "harvest", "sell"],
                "emoji": "🌾"
            },
            "🛒 Shopping & Trading": {
                "description": "Mua bán và giao dịch",
                "commands": ["shop", "buy", "price", "market", "trends", "farmmarket"],
                "emoji": "🛒"
            },
            "🌤️ Weather System": {
                "description": "Thời tiết và dự báo",
                "commands": ["weather", "forecast"],
                "emoji": "🌤️"
            },
            "📅 Daily & Events": {
                "description": "Hoạt động hàng ngày và sự kiện",
                "commands": ["daily", "streak", "rewards", "event", "events", "claim_event"],
                "emoji": "📅"
            },
            "🏆 Rankings": {
                "description": "Bảng xếp hạng và so sánh",
                "commands": ["leaderboard", "rank", "compare"],
                "emoji": "🏆"
            },
            "🐟 Livestock System": {
                "description": "Nuôi cá và động vật",
                "commands": ["pond", "barn", "livestock"],
                "emoji": "🐟"
            },
            "🎰 Casino & Games": {
                "description": "Trò chơi casino và giải trí",
                "commands": ["casino", "blackjack"],
                "emoji": "🎰"
            },
            "🤖 AI System": {
                "description": "Hệ thống AI thông minh",
                "commands": ["ai", "gamemaster"],
                "emoji": "🤖"
            },
            "🎀 Maid System": {
                "description": "Hệ thống maid - thu thập và nâng cấp maid để nhận buffs với numbered selection",
                "commands": [
                    "mg", "mg10", "ma", "mc", "mequip", "mstar", "mdis", "mdisall", "mreroll",
                    "maid_gacha", "maid_gacha10", "maid_pity",
                    "maid_collection", "maid_equip", "maid_active", 
                    "maid_rename", "minfo", "mdbsearch", "select", "mlist",
                    "maid_stardust", "maid_dismantle", "maid_dismantle_all", "maid_reroll", "maid_reroll_cost",
                    "maid_stats"
                ],
                "emoji": "🎀"
            }
        }
        
        # Shortcut mappings
        self.shortcuts = {
            # Profile
            "profile": "p", "inventory": "i", "register": "r", "rename": "ren",
            # Farm
            "farm": "f", "plant": "pl", "harvest": "h", "sell": "s",
            # Shop
            "shop": "sh", "buy": "b", "price": "pr",
            # Market
            "market": "m", "trends": "tr", "farmmarket": "fm",
            # Weather
            "weather": "w", "forecast": "fo",
            # Daily
            "daily": "d", "streak": "st", "rewards": "rw",
            # Events
            "event": "e", "events": "ev", "claim_event": "c",
            # Leaderboard
            "leaderboard": "l", "rank": "ra", "compare": "co",
            # Livestock
            "pond": "po", "barn": "ba", "livestock": "li",
            # Casino & Games
            "casino": "ca", "blackjack": "bj",
            # AI
            "ai": "a", "gamemaster": "gm",
            # Maid System
            "maid_gacha": "mg", "maid_gacha10": "mg10", "maid_pity": "mp",
            "maid_collection": "mc", "maid_equip": "mequip", "maid_active": "ma",
            "maid_rename": "mr", "minfo": "minfo", "mdbsearch": "mdbsearch", "select": "select", "mlist": "mlist",
            "maid_stardust": "mstar", "maid_dismantle": "mdis", "maid_dismantle_all": "mdisall", 
            "maid_reroll": "mreroll", "maid_reroll_cost": "mrc", "maid_stats": "mst"
        }
    
    def create_overview_page(self):
        """Tạo trang tổng quan"""
        embed = EmbedBuilder.create_base_embed(
            "🎮 Bot Nông Trại - Hướng Dẫn Sử Dụng",
            "Chào mừng đến với bot farming Discord! Dưới đây là danh sách đầy đủ các tính năng.",
            color=0x00ff00
        )
        
        # Add quick start guide
        embed.add_field(
            name="🚀 Quick Start",
            value=(
                "• `f!register` - Đăng ký tài khoản\n"
                "• `f!farm` - Xem nông trại\n"
                "• `f!daily` - Nhận thưởng hàng ngày\n"
                "• `f!shop` - Mua hạt giống\n"
                "• `f!pond` - Quản lý ao cá\n"
                "• `f!barn` - Quản lý chuồng gia súc\n"
                "• `f!mg` - Roll maid để nhận buffs\n"
                "• `f!mdbsearch <tên>` → `f!select <số>` - Tìm maid"
            ),
            inline=False
        )
        
        # Add categories overview
        categories_text = ""
        for idx, (cat_name, cat_data) in enumerate(self.categories.items(), 1):
            categories_text += f"**{idx}.** {cat_data['emoji']} {cat_name.split(' ', 1)[1]}\n"
        
        embed.add_field(
            name="📚 Danh Mục Lệnh",
            value=categories_text,
            inline=True
        )
        
        # Add shortcuts info
        embed.add_field(
            name="⚡ Lệnh Viết Tắt",
            value=(
                "Tất cả lệnh đều có phiên bản viết tắt:\n"
                "• `f!farm` → `f!f`\n"
                "• `f!plant` → `f!pl`\n"
                "• `f!harvest` → `f!h`\n"
                "• `f!sell` → `f!s`\n"
                "• Và nhiều hơn nữa..."
            ),
            inline=True
        )
        
        embed.set_footer(text="📖 Trang 1 • Sử dụng nút mũi tên để xem chi tiết từng danh mục")
        return embed
    
    def create_category_page(self, category_name, category_data, page_num):
        """Tạo trang cho một category"""
        embed = EmbedBuilder.create_base_embed(
            f"{category_data['emoji']} {category_name}",
            category_data['description'],
            color=0x3498db
        )
        
        # Get commands for this category
        # For maid system, use compact format to avoid Discord embed limits
        if category_name == "🎀 Maid System":
            # Compact maid system help
            basic_commands = """
**🎰 Gacha & Collection**
• `f!mg` - Roll 1 maid (10k coins) | `f!mg10` - Roll 10 (90k)
• `f!mc` - Collection với filter (-r/-n) | `f!ma` - Active maid

**⚔️ Management**  
• `f!mequip <id>` - Trang bị maid | `f!mstar` - Xem stardust
• `f!mdis <id>` - Tách maid | `f!mreroll <id>` - Reroll buffs

**🔍 Database Search**
• `f!mdbsearch <tên>` - Search maid | `f!select <số>` - Chọn từ kết quả
• `f!minfo <id>` - Chi tiết maid | `f!mlist [rarity]` - List maids
            """
            
            embed.add_field(
                name="📋 Lệnh Maid System",
                value=basic_commands,
                inline=False
            )
            
            # Add note about full command list
            embed.add_field(
                name="💡 Thông tin thêm",
                value=(
                    "• Dùng instance ID (8 ký tự đầu) cho maid commands\n"
                    "• Search cache expire sau 5 phút\n"
                    "• Buffs áp dụng tự động khi equip maid"
                ),
                inline=False
            )
        else:
            # Normal processing for other categories
            for cmd_name in category_data['commands']:
                cmd = self.bot.get_command(cmd_name)
                
                # Skip if command not found
                if not cmd:
                    continue
                
                # Handle text commands
                # Get shortcut
                shortcut = self.shortcuts.get(cmd_name, "")
                shortcut_text = f" | `f!{shortcut}`" if shortcut else ""
                
                # Get aliases
                aliases = [f"`f!{alias}`" for alias in cmd.aliases] if cmd.aliases else []
                aliases_text = f" | {', '.join(aliases)}" if aliases else ""
                
                # Command description
                description = cmd.brief or (cmd.help.split('\n')[0] if cmd.help else "Không có mô tả")
                if len(description) > 100:
                    description = description[:97] + "..."
                
                embed.add_field(
                    name=f"🔹 `f!{cmd_name}`{shortcut_text}",
                    value=f"{description}{aliases_text}",
                    inline=False
                )
        
        embed.set_footer(text=f"📖 Trang {page_num} • Dùng mũi tên để xem danh mục khác")
        return embed
    
    def create_shortcuts_page(self):
        """Tạo trang shortcuts tổng hợp"""
        embed = EmbedBuilder.create_base_embed(
            "⚡ Danh Sách Lệnh Viết Tắt",
            "Tất cả shortcuts để sử dụng bot nhanh hơn",
            color=0xf39c12
        )
        
        # Group shortcuts by category
        for cat_name, cat_data in self.categories.items():
            shortcut_list = []
            for cmd_name in cat_data['commands']:
                shortcut = self.shortcuts.get(cmd_name)
                if shortcut:
                    shortcut_list.append(f"`f!{cmd_name}` → `f!{shortcut}`")
            
            # Special case for maid commands with selected examples
            if cat_name == "🎀 Maid System":
                shortcut_list = [
                    "**🎰 Gacha**: `f!mg` (single) • `f!mg10` (10x roll)",
                    "**📚 Management**: `f!mc` (collection) • `f!ma` (active)",
                    "**⚔️ Equipment**: `f!mequip <id>` - Trang bị maid",
                    "**🔍 Database**: `f!mdbsearch <tên>` → `f!select <số>`",
                    "**⭐ Stardust**: `f!mstar` • `f!mdis <id>` • `f!mdisall -r R`",
                    "**🎲 Reroll**: `f!mreroll <id>` - Reroll buffs",
                    "**📋 Lists**: `f!minfo <id>` • `f!mlist UR`"
                ]
            
            if shortcut_list:
                embed.add_field(
                    name=f"{cat_data['emoji']} {cat_name.split(' ', 1)[1]}",
                    value="\n".join(shortcut_list),
                    inline=True
                )
        
        embed.add_field(
            name="💡 Tips",
            value=(
                "• **Text commands**: `f!command` và shortcuts `f!shortcut`\n"
                "• **Maid System**: Sử dụng text commands `f!maid_*`\n"
                "• Shortcuts hoạt động giống lệnh gốc\n"
                "• Ví dụ: `f!s carrot all` = `f!sell carrot all`\n"
                "• Ví dụ: `f!mg` = `f!maid_gacha` để roll maid mới"
            ),
            inline=False
        )
        
        embed.set_footer(text="📖 Trang Shortcuts • Tiết kiệm thời gian với lệnh viết tắt!")
        return embed
    
    def create_all_pages(self):
        """Tạo tất cả pages cho help system"""
        pages = []
        
        # Page 1: Overview
        pages.append(self.create_overview_page())
        
        # Pages 2-8: Categories
        for idx, (cat_name, cat_data) in enumerate(self.categories.items(), 2):
            pages.append(self.create_category_page(cat_name, cat_data, idx))
        
        # Last page: Shortcuts
        pages.append(self.create_shortcuts_page())
        
        return pages
    
    @commands.command(name='help', aliases=['giupdo', 'huongdan'])
    async def help_command(self, ctx, *, command_name: str = None):
        """Hệ thống help mới với pagination và shortcuts
        
        Sử dụng: f!help [tên_lệnh]
        """
        if command_name:
            # Show specific command help
            cmd = self.bot.get_command(command_name)
            if not cmd:
                await ctx.send(f"❌ Không tìm thấy lệnh `{command_name}`!")
                return
            
            embed = EmbedBuilder.create_base_embed(
                f"📖 Hướng dẫn: {cmd.name}",
                cmd.help or "Không có mô tả chi tiết",
                color=0x3498db
            )
            
            # Add shortcut info
            shortcut = self.shortcuts.get(cmd.name)
            if shortcut:
                embed.add_field(
                    name="⚡ Shortcut",
                    value=f"`f!{shortcut}`",
                    inline=True
                )
            
            # Add aliases
            if cmd.aliases:
                aliases_text = ", ".join([f"`f!{alias}`" for alias in cmd.aliases])
                embed.add_field(
                    name="🔄 Aliases",
                    value=aliases_text,
                    inline=True
                )
            
            await ctx.send(embed=embed)
        else:
            # Show paginated help
            pages = self.create_all_pages()
            view = HelpPaginationView(self.bot, ctx.author.id, pages)
            view.update_buttons()
            
            await ctx.send(embed=pages[0], view=view)

async def setup(bot):
    # Remove default help command
    bot.remove_command('help')
    await bot.add_cog(HelpSystemCog(bot)) 