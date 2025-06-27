"""
🔍 Maid Info System - Comprehensive Information Display
Tính năng hiển thị thông tin chi tiết maid với avatar, stats và database search
"""

import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional, List, Dict, Any
import json
import os
from datetime import datetime

from utils.embeds import EmbedBuilder
from utils.registration import require_registration
from utils.enhanced_logging import get_bot_logger

# Import maid config from backup with avatar URLs
from features.maid_config_backup import (
    MAID_TEMPLATES as BACKUP_MAID_TEMPLATES,
    RARITY_CONFIG as BACKUP_RARITY_CONFIG,
    BUFF_TYPES as BACKUP_BUFF_TYPES,
    RARITY_EMOJIS
)

logger = get_bot_logger()

class MaidInfoSystem(commands.Cog):
    """🎀 Maid Information System with Avatar Support"""
    
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
        # Cache search results for numbered selection
        self.user_search_cache = {}
        
    async def cog_load(self):
        """Initialize when cog loads"""
        logger.info("MaidInfoSystem cog loaded with avatar support and numbered selection")
    
    def cleanup_expired_cache(self):
        """🧹 Clean up expired cache entries"""
        current_time = datetime.now().timestamp()
        expired_users = []
        
        for user_id, cache_data in self.user_search_cache.items():
            if current_time - cache_data['timestamp'] > 300:  # 5 minutes
                expired_users.append(user_id)
        
        for user_id in expired_users:
            del self.user_search_cache[user_id]
        
        if expired_users:
            logger.info(f"Cleaned up {len(expired_users)} expired cache entries")

    async def get_db_connection(self):
        """Get database connection safely"""
        if not hasattr(self.bot, 'db') or not self.bot.db:
            raise Exception("Database not available")
        return await self.bot.db.get_connection()
    
    async def find_user_maid(self, user_id: int, maid_input: str) -> Optional[Dict]:
        """🔍 Find user's maid by ID, name, or custom name"""
        try:
            connection = await self.get_db_connection()
            
            # Search strategies: instance_id, template name, custom name
            search_queries = [
                "SELECT * FROM user_maids_v2 WHERE user_id = ? AND instance_id LIKE ?",
                "SELECT * FROM user_maids_v2 WHERE user_id = ? AND maid_id LIKE ?", 
                "SELECT * FROM user_maids_v2 WHERE user_id = ? AND custom_name LIKE ?"
            ]
            
            search_terms = [
                f"{maid_input.lower()}%",  # Instance ID prefix
                f"%{maid_input.lower()}%",  # Maid ID contains
                f"%{maid_input.lower()}%"   # Custom name contains
            ]
            
            for query, term in zip(search_queries, search_terms):
                cursor = await connection.execute(query, (user_id, term))
                row = await cursor.fetchone()
                if row:
                    # Convert to dict và parse buffs
                    maid_data = {
                        "id": row[0],
                        "user_id": row[1], 
                        "maid_id": row[2],
                        "instance_id": row[3],
                        "custom_name": row[4],
                        "obtained_at": row[5],
                        "is_active": bool(row[6]),
                        "buffs": json.loads(row[7]) if row[7] else [],
                        "reroll_count": row[8] or 0,
                        "last_reroll_time": row[9]
                    }
                    return maid_data
            
            return None
            
        except Exception as e:
            logger.error(f"Error finding user maid: {e}")
            return None
    
    async def search_maid_database(self, search_term: str) -> List[Dict]:
        """🔍 Search maids in database by name"""
        search_lower = search_term.lower()
        found_maids = []
        
        for maid_id, template in BACKUP_MAID_TEMPLATES.items():
            if (search_lower in template["name"].lower() or 
                search_lower in template.get("full_name", "").lower() or
                search_lower in maid_id.lower()):
                found_maids.append((maid_id, template))
        
        return found_maids
    
    async def check_user_ownership(self, user_id: int, maid_id: str) -> bool:
        """🔒 Check if user owns specific maid"""
        try:
            connection = await self.get_db_connection()
            cursor = await connection.execute(
                "SELECT COUNT(*) FROM user_maids_v2 WHERE user_id = ? AND maid_id = ?",
                (user_id, maid_id)
            )
            count = await cursor.fetchone()
            return count[0] > 0 if count else False
        except Exception as e:
            logger.error(f"Error checking ownership: {e}")
            return False
    
    def create_maid_info_embed(self, maid_data: Dict, template: Dict, user_data: Optional[Dict] = None) -> discord.Embed:
        """🎨 Create detailed maid info embed with avatar"""
        
        # Display name priority: custom_name > template name
        display_name = maid_data.get("custom_name") or template["name"]
        
        # Create embed với rarity color
        rarity = template["rarity"]
        embed = EmbedBuilder.create_base_embed(
            title=f"🔍 {template['emoji']} {display_name}",
            description=f"**{template.get('full_name', template['name'])}**\n*{template.get('description', 'Maid huyền thoại')}*",
            color=BACKUP_RARITY_CONFIG[rarity]["color"]
        )
        
        # 🖼️ Set avatar with 3:4 aspect ratio (priority: art_url > placeholder)
        if template.get("art_url"):
            embed.set_image(url=template["art_url"])
        else:
            # Placeholder hoặc default avatar
            embed.set_thumbnail(url="https://via.placeholder.com/480x640/FF6B9D/FFFFFF?text=No+Image")
        
        # 📋 Basic Information
        embed.add_field(
            name="📋 Thông Tin Cơ Bản",
            value=(
                f"**Rarity**: {RARITY_EMOJIS[rarity]} {rarity}\n"
                f"**ID**: `{maid_data['instance_id'][:8]}`\n"
                f"**Status**: {'⭐ Active' if maid_data.get('is_active') else '💤 Inactive'}\n"
                f"**Series**: {template.get('series', 'Unknown')}\n"
                f"**Obtained**: <t:{int(datetime.fromisoformat(maid_data['obtained_at']).timestamp())}:R>"
            ),
            inline=True
        )
        
        # ✨ Current Buffs (what maid currently has)
        current_buffs = []
        for buff in maid_data.get("buffs", []):
            buff_type = buff.get("type") or buff.get("buff_type", "unknown")
            value = buff.get("value", 0)
            if buff_type in BACKUP_BUFF_TYPES:
                buff_info = BACKUP_BUFF_TYPES[buff_type]
                current_buffs.append(f"{buff_info['emoji']} **{buff_info['name']}**: +{value}%")
        
        embed.add_field(
            name="✨ Skills Đang Sở Hữu",
            value="\n".join(current_buffs) if current_buffs else "❌ Chưa có buffs",
            inline=True
        )
        
        # 🎲 Possible Skills (what maid can get when rerolled)
        possible_buffs = []
        rarity_range = BACKUP_RARITY_CONFIG[rarity]["buff_range"]
        for buff_type in template.get("possible_buffs", []):
            if buff_type in BACKUP_BUFF_TYPES:
                buff_info = BACKUP_BUFF_TYPES[buff_type]
                possible_buffs.append(
                    f"{buff_info['emoji']} **{buff_info['name']}**\n"
                    f"└ `{rarity_range[0]}-{rarity_range[1]}%`"
                )
        
        embed.add_field(
            name="🎲 Skills Có Thể Có (Khi Reroll)",
            value="\n\n".join(possible_buffs) if possible_buffs else "❌ Không có buffs",
            inline=False
        )
        
        # 📊 Gacha & Economics Info
        individual_rate = BACKUP_RARITY_CONFIG[rarity]["total_rate"] / BACKUP_RARITY_CONFIG[rarity]["maid_count"]
        expected_rolls = 100 / individual_rate
        expected_cost = expected_rolls * 10000
        
        reroll_cost = {
            "UR": 80, "SSR": 40, "SR": 20, "R": 8
        }.get(rarity, 8)
        
        dismantle_reward = {
            "UR": 100, "SSR": 50, "SR": 25, "R": 10
        }.get(rarity, 10)
        
        embed.add_field(
            name="📊 Gacha & Economics",
            value=(
                f"**Drop Rate**: {individual_rate:.4f}%\n"
                f"**Expected Cost**: {expected_cost:,.0f} coins\n"
                f"**Reroll Cost**: {reroll_cost} ⭐ stardust\n"
                f"**Dismantle**: {dismantle_reward} ⭐ stardust"
            ),
            inline=True
        )
        
        # 🔄 Reroll History (if available)
        reroll_count = maid_data.get("reroll_count", 0)
        last_reroll = maid_data.get("last_reroll_time")
        
        reroll_info = f"**Times Rerolled**: {reroll_count}\n"
        if last_reroll:
            try:
                last_time = datetime.fromisoformat(last_reroll)
                reroll_info += f"**Last Reroll**: <t:{int(last_time.timestamp())}:R>"
            except:
                reroll_info += "**Last Reroll**: Unknown"
        else:
            reroll_info += "**Last Reroll**: Never"
        
        embed.add_field(
            name="🔄 Reroll History", 
            value=reroll_info,
            inline=True
        )
        
        # 💡 Footer with tips
        embed.set_footer(text=f"💡 Tip: Use f!mreroll {maid_data['instance_id'][:8]} to reroll buffs!")
        
        return embed
    
    def create_database_search_embed(self, maids_found: List[tuple], search_term: str) -> discord.Embed:
        """🔍 Create database search results embed"""
        
        if len(maids_found) == 1:
            # Single result - detailed view
            maid_id, template = maids_found[0]
            return self.create_single_database_result(maid_id, template)
        else:
            # Multiple results - grouped by rarity
            return self.create_multiple_database_results(maids_found, search_term)
    
    def create_single_database_result(self, maid_id: str, template: Dict) -> discord.Embed:
        """📚 Single maid database result with full details"""
        rarity = template["rarity"]
        
        embed = EmbedBuilder.create_base_embed(
            title=f"📚 {template['emoji']} {template['name']}",
            description=f"**{template.get('full_name', template['name'])}**\n*{template.get('description', 'Maid huyền thoại')}*",
            color=BACKUP_RARITY_CONFIG[rarity]["color"]
        )
        
        # Set avatar
        if template.get("art_url"):
            embed.set_image(url=template["art_url"])
        
        # Basic Info
        individual_rate = BACKUP_RARITY_CONFIG[rarity]["total_rate"] / BACKUP_RARITY_CONFIG[rarity]["maid_count"]
        
        embed.add_field(
            name="📋 Database Info",
            value=(
                f"**Rarity**: {RARITY_EMOJIS[rarity]} {rarity}\n"
                f"**Maid ID**: `{maid_id}`\n" 
                f"**Drop Rate**: {individual_rate:.4f}%\n"
                f"**Buff Count**: {BACKUP_RARITY_CONFIG[rarity]['buff_count']} buffs\n"
                f"**Series**: {template.get('series', 'Unknown')}"
            ),
            inline=True
        )
        
        # Possible Skills when rolled
        possible_buffs = []
        rarity_range = BACKUP_RARITY_CONFIG[rarity]["buff_range"]
        for buff_type in template.get("possible_buffs", []):
            if buff_type in BACKUP_BUFF_TYPES:
                buff_info = BACKUP_BUFF_TYPES[buff_type]
                possible_buffs.append(
                    f"{buff_info['emoji']} **{buff_info['name']}**\n"
                    f"└ `{rarity_range[0]}-{rarity_range[1]}%` - {buff_info['description']}"
                )
        
        embed.add_field(
            name="🎲 Skills Khi Roll Trúng",
            value="\n\n".join(possible_buffs) if possible_buffs else "❌ Không có buffs",
            inline=False
        )
        
        # Economics
        expected_rolls = 100 / individual_rate
        expected_cost = expected_rolls * 10000
        
        embed.add_field(
            name="💰 Economics",
            value=(
                f"**Expected Rolls**: {expected_rolls:.0f} rolls\n"
                f"**Expected Cost**: {expected_cost:,.0f} coins\n"
                f"**Reroll Cost**: {BACKUP_RARITY_CONFIG[rarity].get('reroll_cost', 8)} ⭐\n"
                f"**Dismantle**: {BACKUP_RARITY_CONFIG[rarity].get('dismantle_reward', 10)} ⭐"
            ),
            inline=True
        )
        
        return embed
    
    def create_numbered_selection_embed(self, maids_found: List[tuple], search_term: str, user_id: int) -> discord.Embed:
        """📋 Create numbered selection list for multiple maids"""
        
        embed = EmbedBuilder.create_base_embed(
            title=f"🔍 Chọn Maid: `{search_term}`",
            description=f"Tìm thấy **{len(maids_found)}** maids. Chọn số để xem chi tiết:",
            color=0x9932CC
        )
        
        # Cache results for this user
        self.user_search_cache[user_id] = {
            'results': maids_found,
            'search_term': search_term,
            'timestamp': datetime.now().timestamp()
        }
        
        # Create numbered list
        maid_list = []
        for i, (maid_id, template) in enumerate(maids_found[:15], 1):  # Limit to 15 results
            rarity = template["rarity"]
            individual_rate = BACKUP_RARITY_CONFIG[rarity]["total_rate"] / BACKUP_RARITY_CONFIG[rarity]["maid_count"]
            series = template.get("series", "Unknown")
            
            maid_list.append(
                f"**{i}.** {template['emoji']} **{template['name']}**\n"
                f"    {RARITY_EMOJIS[rarity]} {rarity} • {series} • `{individual_rate:.4f}%`"
            )
        
        # Split into chunks for better display
        chunk_size = 5
        chunks = [maid_list[i:i+chunk_size] for i in range(0, len(maid_list), chunk_size)]
        
        for i, chunk in enumerate(chunks):
            field_name = f"📋 Maids {i*chunk_size + 1}-{min((i+1)*chunk_size, len(maid_list))}"
            embed.add_field(
                name=field_name,
                value="\n\n".join(chunk),
                inline=True
            )
        
        if len(maids_found) > 15:
            embed.add_field(
                name="⚠️ Lưu ý", 
                value=f"Chỉ hiển thị 15/{len(maids_found)} kết quả đầu tiên",
                inline=False
            )
        
        embed.add_field(
            name="🎯 Cách chọn",
            value=(
                f"• `f!select <số>` - Xem chi tiết maid (vd: `f!select 1`)\n"
                f"• `f!mdbsearch <tên chính xác>` - Search cụ thể hơn\n"
                "• Cache sẽ expire sau 5 phút"
            ),
            inline=False
        )
        
        return embed
    
    def create_maid_list_embed(self, rarity: Optional[str] = None) -> discord.Embed:
        """📜 Create maid list embed by rarity"""
        
        # Group all maids by rarity
        by_rarity = {"UR": [], "SSR": [], "SR": [], "R": []}
        for maid_id, template in BACKUP_MAID_TEMPLATES.items():
            by_rarity[template["rarity"]].append((maid_id, template))
        
        if rarity and rarity.upper() in by_rarity:
            # Show specific rarity
            target_rarity = rarity.upper()
            embed = EmbedBuilder.create_base_embed(
                title=f"📜 {RARITY_EMOJIS[target_rarity]} {target_rarity} Maids",
                description=f"Tất cả {len(by_rarity[target_rarity])} maids rarity {target_rarity}",
                color=BACKUP_RARITY_CONFIG[target_rarity]["color"]
            )
            
            maid_list = []
            for maid_id, template in by_rarity[target_rarity]:
                individual_rate = BACKUP_RARITY_CONFIG[target_rarity]["total_rate"] / BACKUP_RARITY_CONFIG[target_rarity]["maid_count"]
                series = template.get("series", "Unknown")
                maid_list.append(
                    f"{template['emoji']} **{template['name']}** - {series}\n"
                    f"└ `{individual_rate:.4f}%` • `f!minfo {template['name'].lower()}`"
                )
            
            # Split into chunks if too long
            chunk_size = 8
            chunks = [maid_list[i:i+chunk_size] for i in range(0, len(maid_list), chunk_size)]
            
            for i, chunk in enumerate(chunks):
                field_name = f"📋 Maids {i*chunk_size + 1}-{min((i+1)*chunk_size, len(maid_list))}"
                embed.add_field(
                    name=field_name,
                    value="\n\n".join(chunk),
                    inline=True
                )
                
        else:
            # Show overview of all rarities
            embed = EmbedBuilder.create_base_embed(
                title="📜 Complete Maid Database",
                description="🎯 Tất cả 50 maids trong hệ thống",
                color=0x9932CC
            )
            
            for rarity_name in ["UR", "SSR", "SR", "R"]:
                maid_list = []
                total_rate = BACKUP_RARITY_CONFIG[rarity_name]["total_rate"]
                individual_rate = BACKUP_RARITY_CONFIG[rarity_name]["total_rate"] / BACKUP_RARITY_CONFIG[rarity_name]["maid_count"]
                
                # Show first few maids as examples
                for maid_id, template in by_rarity[rarity_name][:6]:
                    maid_list.append(f"{template['emoji']} {template['name']}")
                
                if len(by_rarity[rarity_name]) > 6:
                    maid_list.append(f"... và {len(by_rarity[rarity_name]) - 6} maids khác")
                
                embed.add_field(
                    name=f"{RARITY_EMOJIS[rarity_name]} {rarity_name} ({len(by_rarity[rarity_name])} maids)",
                    value=(
                        f"**Total Rate**: {total_rate}%\n"
                        f"**Per Maid**: {individual_rate:.4f}%\n"
                        f"**Examples**:\n" + "\n".join(maid_list)
                    ),
                    inline=True
                )
            
            embed.add_field(
                name="🔍 Commands",
                value=(
                    "• `f!mlist UR` - Xem tất cả UR maids\n"
                    "• `f!mdbsearch <tên>` - Search maid cụ thể\n"
                    "• `f!minfo <id>` - Chi tiết maid trong collection"
                ),
                inline=False
            )
        
        return embed

    # ===== COMMANDS =====
    
    @commands.hybrid_command(name="minfo", description="🔍 Xem thông tin chi tiết maid trong collection")
    async def maid_info(self, ctx, *, maid_input: str):
        """Xem thông tin chi tiết maid trong collection với avatar"""
        
        # Check registration
        if not await require_registration(ctx.bot, ctx):
            return
        
        user_id = ctx.author.id
        
        # Find user's maid
        maid_data = await self.find_user_maid(user_id, maid_input)
        
        if not maid_data:
            embed = EmbedBuilder.create_base_embed(
                title="❌ Không Tìm Thấy Maid",
                description=f"Không tìm thấy maid với ID/tên `{maid_input}` trong collection của bạn!",
                color=0xFF0000
            )
            embed.add_field(
                name="💡 Gợi ý",
                value=(
                    "• Dùng `f!mc` để xem collection\n"
                    "• Dùng 8 ký tự đầu của Instance ID\n"
                    "• Hoặc tên maid (vd: `rem`, `saber`)\n"
                    "• Hoặc custom name nếu đã đặt"
                ),
                inline=False
            )
            await ctx.send(embed=embed)
            return
        
        # Get template from backup config
        maid_id = maid_data["maid_id"]
        if maid_id not in BACKUP_MAID_TEMPLATES:
            embed = EmbedBuilder.create_base_embed(
                title="❌ Lỗi Template",
                description=f"Không tìm thấy template cho maid ID: `{maid_id}`",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            return
        
        template = BACKUP_MAID_TEMPLATES[maid_id]
        
        # Create detailed info embed with avatar
        embed = self.create_maid_info_embed(maid_data, template)
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="mdbsearch", description="📚 Tìm kiếm maid trong database hệ thống")
    async def maid_database_search(self, ctx, *, search_term: str):
        """Tìm kiếm maid trong database với smart detection"""
        
        # Clean expired cache
        self.cleanup_expired_cache()
        
        maids_found = await self.search_maid_database(search_term)
        
        if not maids_found:
            embed = EmbedBuilder.create_base_embed(
                title="❌ Không Tìm Thấy",
                description=f"Không tìm thấy maid nào với từ khóa `{search_term}`",
                color=0xFF0000
            )
            embed.add_field(
                name="💡 Gợi ý",
                value=(
                    "• Thử từ khóa khác (vd: `rem`, `saber`, `zero`)\n"
                    "• Dùng `f!mlist` để xem tất cả maids\n"
                    "• Dùng `f!mlist UR` để xem theo rarity"
                ),
                inline=False
            )
            await ctx.send(embed=embed)
            return
        
        # Smart detection: if exactly 1 result, show detailed info
        if len(maids_found) == 1:
            maid_id, template = maids_found[0]
            embed = self.create_single_database_result(maid_id, template)
            
            # Try to attach avatar image
            files = []
            cropped_path = f"art/maids_cropped/{maid_id}.jpg"
            if os.path.exists(cropped_path):
                file = discord.File(cropped_path, filename=f"{maid_id}.jpg")
                files.append(file)
                # Update embed to use attachment
                embed.set_thumbnail(url=f"attachment://{maid_id}.jpg")
            
            if files:
                await ctx.send(embed=embed, files=files)
            else:
                await ctx.send(embed=embed)
        else:
            # Multiple results: show numbered selection list
            embed = self.create_numbered_selection_embed(maids_found, search_term, ctx.author.id)
            await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="select", description="🎯 Chọn maid từ kết quả search bằng số")
    async def select_maid(self, ctx, number: int):
        """Chọn maid từ kết quả search trước đó bằng số"""
        
        user_id = ctx.author.id
        
        # Check if user has cached search results
        if user_id not in self.user_search_cache:
            embed = EmbedBuilder.create_base_embed(
                title="❌ Không Có Kết Quả Cache",
                description="Bạn chưa search maid nào hoặc cache đã expire!",
                color=0xFF0000
            )
            embed.add_field(
                name="💡 Cách sử dụng",
                value=(
                    "1. `f!mdbsearch <tên>` - Search maid\n"
                    "2. `f!select <số>` - Chọn từ kết quả\n"
                    "Cache expire sau 5 phút"
                ),
                inline=False
            )
            await ctx.send(embed=embed)
            return
        
        cache_data = self.user_search_cache[user_id]
        
        # Check cache expiry (5 minutes)
        if datetime.now().timestamp() - cache_data['timestamp'] > 300:
            del self.user_search_cache[user_id]
            embed = EmbedBuilder.create_base_embed(
                title="⏰ Cache Đã Expire",
                description="Kết quả search đã expire sau 5 phút!",
                color=0xFF0000
            )
            embed.add_field(
                name="🔄 Thử lại",
                value=f"Dùng `f!mdbsearch {cache_data['search_term']}` để search lại",
                inline=False
            )
            await ctx.send(embed=embed)
            return
        
        results = cache_data['results']
        
        # Validate number
        if number < 1 or number > len(results):
            embed = EmbedBuilder.create_base_embed(
                title="❌ Số Không Hợp Lệ",
                description=f"Chọn số từ 1 đến {len(results)}!",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            return
        
        # Get selected maid
        maid_id, template = results[number - 1]
        embed = self.create_single_database_result(maid_id, template)
        
        # Try to attach avatar image
        files = []
        cropped_path = f"art/maids_cropped/{maid_id}.jpg"
        if os.path.exists(cropped_path):
            file = discord.File(cropped_path, filename=f"{maid_id}.jpg")
            files.append(file)
            embed.set_thumbnail(url=f"attachment://{maid_id}.jpg")
        
        if files:
            await ctx.send(embed=embed, files=files)
        else:
            await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="mlist", description="📜 Xem danh sách tất cả maids theo rarity")
    async def maid_list(self, ctx, rarity: Optional[str] = None):
        """Xem danh sách maids với optional rarity filter"""
        
        # Validate rarity if provided
        if rarity and rarity.upper() not in ["UR", "SSR", "SR", "R"]:
            embed = EmbedBuilder.create_base_embed(
                title="❌ Rarity Không Hợp Lệ",
                description=f"Rarity `{rarity}` không tồn tại!",
                color=0xFF0000
            )
            embed.add_field(
                name="✅ Rarities Hợp Lệ",
                value="• `UR` - Ultra Rare\n• `SSR` - Super Super Rare\n• `SR` - Super Rare\n• `R` - Rare",
                inline=False
            )
            await ctx.send(embed=embed)
            return
        
        # Create maid list embed
        embed = self.create_maid_list_embed(rarity)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(MaidInfoSystem(bot)) 