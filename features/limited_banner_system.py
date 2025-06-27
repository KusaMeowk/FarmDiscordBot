import discord
from discord.ext import commands
from discord import app_commands
import uuid
import random
import json
import aiosqlite
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple

from database.database import Database
from utils.embeds import EmbedBuilder
from utils.registration import require_registration
from utils.enhanced_logging import get_bot_logger

# Import từ maid config backup
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from features.maid_config_backup import (
    LIMITED_BANNER_CONFIG, LIMITED_RARITY_CONFIG, MAID_TEMPLATES, BUFF_TYPES,
    get_random_maid_limited_banner, is_limited_banner_active, get_limited_banner_info,
    get_featured_characters, generate_random_buffs, STARDUST_CONFIG
)

logger = get_bot_logger()

class LimitedBannerSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
    
    async def cog_load(self):
        """Khởi tạo khi load cog"""
        logger.info("LimitedBannerSystem cog loaded")
        # Tận dụng tables từ maid_system_v2
    
    async def get_db_connection(self):
        """Get database connection safely"""
        if not hasattr(self.bot, 'db') or not self.bot.db:
            raise Exception("Database not available")
        return await self.bot.db.get_connection()
    
    @commands.hybrid_command(name="2mg", description="🌟 Limited Banner - Roll 1 lần (12,000 coins)")
    async def limited_gacha_single(self, ctx):
        """Limited banner single gacha"""
        # Check registration
        if not await require_registration(ctx.bot, ctx):
            return
            
        # Check nếu multi-banner active
        from features.maid_config_backup import ACTIVE_BANNER_CONFIG
        if not ACTIVE_BANNER_CONFIG["enabled"]:
            embed = EmbedBuilder.create_base_embed(
                title="❌ Banner không active",
                description="Hiện không có banner nào đang hoạt động!\nHãy dùng `f!mg` cho gacha thường.",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            return
            
        user_id = ctx.author.id
        cost = LIMITED_BANNER_CONFIG["single_roll_cost"]
        
        # Check coins
        user = await self.db.get_user(user_id)
        if user.money < cost:
            embed = EmbedBuilder.create_base_embed(
                title="❌ Không đủ coins",
                description=f"Bạn cần {cost:,} coins để roll Limited Banner!\nBạn hiện có: {user.money:,} coins",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            return
        
        # 🛡️ SAFETY: Atomic transaction for limited gacha
        connection = await self.get_db_connection()
        try:
            await connection.execute('BEGIN TRANSACTION')
            
            # Double-check coins and deduct atomically
            cursor = await connection.execute(
                'UPDATE users SET money = money - ? WHERE user_id = ? AND money >= ?',
                (cost, user_id, cost)
            )
            
            if cursor.rowcount == 0:
                await connection.execute('ROLLBACK')
                embed = EmbedBuilder.create_base_embed(
                    title="❌ Không đủ coins",
                    description="Không đủ tiền để thực hiện Limited Banner gacha!",
                    color=0xFF0000
                )
                await ctx.send(embed=embed)
                return
            
            # Multi-banner gacha roll (after successful payment)
            from features.maid_config_backup import get_random_maid_multi_banner
            maid_id = get_random_maid_multi_banner()
            instance_id = str(uuid.uuid4())
            buffs = generate_random_buffs(maid_id)
            
            # Save maid to database (same table as regular gacha)
            await connection.execute('''
                INSERT INTO user_maids_v2 (user_id, maid_id, instance_id, obtained_at, buff_values)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, maid_id, instance_id, datetime.now().isoformat(), json.dumps(buffs)))
            
            # Save limited gacha history
            await connection.execute('''
                INSERT INTO gacha_history_v2 (user_id, roll_type, cost, results, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, "limited_single", cost, json.dumps([maid_id]), datetime.now().isoformat()))
            
            # 🛡️ COMMIT: All operations successful
            await connection.commit()
            
        except Exception as e:
            # 🛡️ ROLLBACK: Any error rolls back entire transaction
            await connection.execute('ROLLBACK')
            logger.error(f"Limited gacha transaction failed for user {user_id}: {e}")
            embed = EmbedBuilder.create_base_embed(
                title="❌ Lỗi Limited Banner gacha",
                description="Đã xảy ra lỗi trong quá trình gacha. Tiền của bạn không bị trừ.",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            return
        
        # Create result embed with LIMITED styling
        template = MAID_TEMPLATES[maid_id]
        featured_chars = get_featured_characters()
        is_featured = maid_id in featured_chars
        is_limited_only = template.get("limited_only", False)
        
        # Special color for limited banner
        embed_color = LIMITED_BANNER_CONFIG["background_color"]
        if is_limited_only:
            embed_color = 0xFF1493  # Hot pink for limited-only
        
        embed = EmbedBuilder.create_base_embed(
            title="🌟 LIMITED BANNER RESULT!",
            description=f"**{LIMITED_BANNER_CONFIG['banner_name']}**\nChi phí: {cost:,} coins",
            color=embed_color
        )
        
        # Maid info with special LIMITED badges
        rarity_emoji = {"GR": "👻", "UR": "💎", "SSR": "🌟", "SR": "⭐", "R": "✨"}[template["rarity"]]
        name_display = template["name"]
        
        badges = []
        if is_limited_only:
            badges.append("🌟 **LIMITED**")
        if is_featured:
            badges.append("⭐ **FEATURED**")
        
        badge_text = " ".join(badges) if badges else ""
        
        embed.add_field(
            name=f"{rarity_emoji} {template['emoji']} {name_display} {badge_text}",
            value=f"**{template['rarity']} Maid** | {template.get('series', 'Unknown')}",
            inline=False
        )
        
        # Buffs
        buff_text = "\n".join([
            f"{BUFF_TYPES[buff['buff_type']]['emoji']} {BUFF_TYPES[buff['buff_type']]['name']}: +{buff['value']}%"
            for buff in buffs
        ])
        
        embed.add_field(name="✨ Buffs", value=buff_text, inline=False)
        embed.add_field(name="🆔 Instance ID", value=f"`{instance_id[:8]}`", inline=True)
        
        # Add limited banner footer
        embed.set_footer(text="🌟 Limited Banner Event | f!2mg10 cho 10-roll")
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="2mg10", description="🌟 Limited Banner - Roll 10 lần (108,000 coins)")
    async def limited_gacha_ten(self, ctx):
        """Limited banner 10-roll gacha"""
        # Check registration
        if not await require_registration(ctx.bot, ctx):
            return
            
        # Check nếu multi-banner active
        from features.maid_config_backup import ACTIVE_BANNER_CONFIG
        if not ACTIVE_BANNER_CONFIG["enabled"]:
            embed = EmbedBuilder.create_base_embed(
                title="❌ Banner không active",
                description="Hiện không có banner nào đang hoạt động!\nHãy dùng `f!mg10` cho gacha thường.",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            return
            
        user_id = ctx.author.id
        cost = LIMITED_BANNER_CONFIG["ten_roll_cost"]
        
        # Check coins
        user = await self.db.get_user(user_id)
        if user.money < cost:
            embed = EmbedBuilder.create_base_embed(
                title="❌ Không đủ coins",
                description=f"Bạn cần {cost:,} coins để roll Limited Banner 10 lần!\nBạn hiện có: {user.money:,} coins",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            return
        
        # 🛡️ SAFETY: Atomic transaction for 10-roll limited gacha
        connection = await self.get_db_connection()
        try:
            await connection.execute('BEGIN TRANSACTION')
            
            # Double-check coins and deduct atomically
            cursor = await connection.execute(
                'UPDATE users SET money = money - ? WHERE user_id = ? AND money >= ?',
                (cost, user_id, cost)
            )
            
            if cursor.rowcount == 0:
                await connection.execute('ROLLBACK')
                embed = EmbedBuilder.create_base_embed(
                    title="❌ Không đủ coins",
                    description="Không đủ tiền để thực hiện Limited Banner 10-roll!",
                    color=0xFF0000
                )
                await ctx.send(embed=embed)
                return
            
            # Roll 10 times (after successful payment)
            from features.maid_config_backup import get_random_maid_multi_banner
            results = []
            for _ in range(10):
                maid_id = get_random_maid_multi_banner()
                instance_id = str(uuid.uuid4())
                buffs = generate_random_buffs(maid_id)
                
                # Save to database
                await connection.execute('''
                    INSERT INTO user_maids_v2 (user_id, maid_id, instance_id, obtained_at, buff_values)
                    VALUES (?, ?, ?, ?, ?)
                ''', (user_id, maid_id, instance_id, datetime.now().isoformat(), json.dumps(buffs)))
                
                results.append({
                    "maid_id": maid_id,
                    "instance_id": instance_id,
                    "buffs": buffs
                })
            
            # Save limited gacha history
            await connection.execute('''
                INSERT INTO gacha_history_v2 (user_id, roll_type, cost, results, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, "limited_ten_roll", cost, json.dumps([r["maid_id"] for r in results]), datetime.now().isoformat()))
            
            # 🛡️ COMMIT: All operations successful
            await connection.commit()
            
        except Exception as e:
            # 🛡️ ROLLBACK: Any error rolls back entire transaction
            await connection.execute('ROLLBACK')
            logger.error(f"Limited 10-roll gacha transaction failed for user {user_id}: {e}")
            embed = EmbedBuilder.create_base_embed(
                title="❌ Lỗi Limited Banner gacha",
                description="Đã xảy ra lỗi trong quá trình gacha 10 lần. Tiền của bạn không bị trừ.",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            return
        
        # Send results with view
        view = LimitedGachaResultsView(user_id, results)
        embed = view.create_embed(show_remaining=False)
        await ctx.send(embed=embed, view=view)
    
    @commands.hybrid_command(name="2mbanner", description="ℹ️ Xem thông tin Banner hiện tại")
    async def limited_banner_info(self, ctx):
        """Hiển thị thông tin multi-banner"""
        from features.maid_config_backup import (
            get_current_banner, get_banner_info, 
            ACTIVE_BANNER_CONFIG
        )
        
        if not ACTIVE_BANNER_CONFIG["enabled"]:
            embed = EmbedBuilder.create_base_embed(
                title="❌ Không có banner nào active",
                description="Hiện tại không có banner nào đang hoạt động.\n"
                           "Admin có thể sử dụng `f!banner set <banner_id>` để bật banner.",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            return
        
        current_banner = get_current_banner()
        banner_info = get_banner_info(current_banner)
        
        if not banner_info["enabled"]:
            embed = EmbedBuilder.create_base_embed(
                title="❌ Banner không active",
                description="Hiện tại không có banner nào đang diễn ra.\n\nAdmin có thể bật bằng `f!banner set <banner_id>`",
                color=0x808080
            )
            await ctx.send(embed=embed)
            return
        
        embed = EmbedBuilder.create_base_embed(
            title=f"🌟 {banner_info['banner_name']}",
            description=banner_info["description"],
            color=banner_info["background_color"]
        )
        
        # Featured character (single featured per banner)
        featured_char = banner_info["featured_character"]
        if featured_char and featured_char in MAID_TEMPLATES:
            template = MAID_TEMPLATES[featured_char]
            rarity_emoji = {"GR": "👻", "UR": "💎", "SSR": "🌟", "SR": "⭐", "R": "✨"}[template["rarity"]]
            limited_badge = "🌟 **LIMITED**" if template.get("limited_only", False) else ""
            
            embed.add_field(
                name="⭐ Featured Character (EXCLUSIVE)",
                value=f"{rarity_emoji} {template['emoji']} {template['name']} {limited_badge}",
                inline=False
            )
        
        # Rates comparison
        embed.add_field(
            name="📊 Gacha Rates",
            value=f"👻 **GR**: 0.05% (EXCLUSIVE!)\n"
                  f"💎 **UR**: 0.15% (vs 0.1% thường)\n"
                  f"🌟 **SSR**: 7.9% (vs 5.9% thường)\n" 
                  f"⭐ **SR**: 22.1% (vs 24.0% thường)\n"
                  f"✨ **R**: 69.8% (vs 70.0% thường)",
            inline=True
        )
        
        # Costs
        embed.add_field(
            name="💰 Chi phí",
            value=f"Single: {banner_info['single_cost']:,} coins\n"
                  f"10-roll: {banner_info['ten_cost']:,} coins",
            inline=True
        )
        
        # Commands
        embed.add_field(
            name="🎮 Commands",
            value="`f!2mg` - Single roll\n"
                  "`f!2mg10` - 10-roll\n"
                  "`f!2mbanner` - Banner info",
            inline=False
        )
        
        embed.set_footer(text=f"🌟 {banner_info['theme_emoji']} Banner Active! Roll now!")
        
        await ctx.send(embed=embed)

class LimitedGachaResultsView(discord.ui.View):
    """View cho limited gacha x10 results với LIMITED styling"""
    
    def __init__(self, user_id: int, results: List[Dict]):
        super().__init__(timeout=300)  # 5 minutes timeout
        self.user_id = user_id
        self.results = results
        self.showing_remaining = False
        
        # Only show button if there are more than 5 results
        if len(results) > 5:
            self.update_button()
    
    def update_button(self):
        """Update button state"""
        self.clear_items()
        
        if len(self.results) > 5:
            if self.showing_remaining:
                button = discord.ui.Button(
                    label="📋 Hiện 5 maid đầu",
                    style=discord.ButtonStyle.secondary,
                    emoji="📋"
                )
                button.callback = self.show_first_five
            else:
                button = discord.ui.Button(
                    label=f"👁️ Hiện {len(self.results) - 5} maid còn lại",
                    style=discord.ButtonStyle.primary,
                    emoji="👁️"
                )
                button.callback = self.show_remaining
            
            self.add_item(button)
    
    def create_embed(self, show_remaining: bool = False) -> discord.Embed:
        """Tạo embed cho limited gacha results"""
        self.showing_remaining = show_remaining
        
        # Create result embed with banner styling
        from features.maid_config_backup import get_current_banner, get_banner_info
        current_banner = get_current_banner()
        banner_info = get_banner_info(current_banner)
        
        embed = EmbedBuilder.create_base_embed(
            title=f"🌟 {banner_info['theme_emoji']} BANNER x10 RESULTS!",
            description=f"**{banner_info['banner_name']}**\nChi phí: {banner_info['ten_cost']:,} coins • Tiết kiệm: {banner_info['single_cost'] * 10 - banner_info['ten_cost']:,} coins",
            color=banner_info["background_color"]
        )
        
        # Count by rarity và special types
        rarity_count = {"GR": 0, "UR": 0, "SSR": 0, "SR": 0, "R": 0}
        limited_count = 0
        featured_count = 0
        featured_char = banner_info["featured_character"]
        
        for result in self.results:
            template = MAID_TEMPLATES[result["maid_id"]]
            rarity_count[template["rarity"]] += 1
            
            if template.get("limited_only", False):
                limited_count += 1
            if result["maid_id"] == featured_char:
                featured_count += 1
        
        # Summary chỉ hiện rarity counts
        summary_parts = []
        for rarity in ["GR", "UR", "SSR", "SR", "R"]:
            if rarity_count[rarity] > 0:
                rarity_emoji = {"GR": "👻", "UR": "💎", "SSR": "🌟", "SR": "⭐", "R": "✨"}[rarity]
                summary_parts.append(f"{rarity_emoji} {rarity}: {rarity_count[rarity]}x")
        
        embed.add_field(name="📊 Tổng kết", value=" • ".join(summary_parts), inline=False)
        
        # Show maids based on current state
        if show_remaining and len(self.results) > 5:
            # Show maids 6-10
            maids_to_show = self.results[5:]
            start_index = 6
        else:
            # Show first 5 maids
            maids_to_show = self.results[:5]
            start_index = 1
        
        for i, result in enumerate(maids_to_show):
            template = MAID_TEMPLATES[result["maid_id"]]
            rarity_emoji = {"GR": "👻", "UR": "💎", "SSR": "🌟", "SR": "⭐", "R": "✨"}[template["rarity"]]
            
            # Special badges
            badges = []
            if template.get("limited_only", False):
                badges.append("🌟")
            if result["maid_id"] == featured_char:
                badges.append("⭐")
            
            badge_text = "".join(badges) + " " if badges else ""
            
            buff_summary = " • ".join([f"{BUFF_TYPES[buff['buff_type']]['emoji']}{buff['value']:.1f}%" for buff in result["buffs"]])
            
            embed.add_field(
                name=f"{start_index + i}. {badge_text}{rarity_emoji} {template['emoji']} {template['name']}",
                value=f"`{result['instance_id'][:8]}` • {buff_summary}",
                inline=False
            )
        
        # Show status if not showing all
        if not show_remaining and len(self.results) > 5:
            embed.add_field(name="...", value=f"Và {len(self.results) - 5} maids khác", inline=False)
        
        embed.set_footer(text=f"🌟 {banner_info['theme_emoji']} Banner Event Results")
        return embed
    
    async def show_remaining(self, interaction: discord.Interaction):
        """Hiện 5 maid còn lại"""
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Chỉ người gacha mới có thể xem!", ephemeral=True)
            return
        
        self.update_button()
        embed = self.create_embed(show_remaining=True)
        await interaction.response.edit_message(embed=embed, view=self)
    
    async def show_first_five(self, interaction: discord.Interaction):
        """Quay lại hiện 5 maid đầu"""
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Chỉ người gacha mới có thể xem!", ephemeral=True)
            return
        
        self.update_button()
        embed = self.create_embed(show_remaining=False)
        await interaction.response.edit_message(embed=embed, view=self)
    
    async def on_timeout(self):
        """Disable button when timeout"""
        for item in self.children:
            item.disabled = True

async def setup(bot):
    await bot.add_cog(LimitedBannerSystem(bot)) 