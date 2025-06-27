import discord
from discord.ext import commands
from discord import app_commands
import uuid
import random
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

from database.database import Database
from database.models import UserMaid, MaidBuff, GachaHistory, UserGachaPity, MaidTrade, UserStardust
from features.maid_config import (
    GACHA_CONFIG, RARITY_CONFIG, STARDUST_CONFIG, BUFF_TYPES, MAID_TEMPLATES,
    UI_CONFIG, RARITY_EMOJIS, get_random_maid_by_individual_rates, get_all_maid_rates, 
    get_rarity_by_rate, get_maids_by_rarity, generate_random_buffs
)
from features.maid_database import MaidDatabase
from features.maid_cooldown import cooldown_manager
from features.maid_dynamic_reroll import dynamic_cost_calculator, reroll_history_manager
from utils.embeds import EmbedBuilder
from utils.registration import registration_required
from utils.enhanced_logging import get_bot_logger

logger = get_bot_logger()

class MaidSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Use the bot's central database connection
        self.maid_db = MaidDatabase(self.bot.db.connection)
        
        # 🔒 Use persistent cooldowns instead of in-memory
        self.GACHA_COOLDOWN = 3  # 3 seconds between gacha rolls
    
    async def cog_load(self):
        """Special discord.py method called when the cog is loaded."""
        try:
            await self.maid_db.init_tables()
            logger.info("✅ MaidSystem Cog loaded and tables initialized.")
        except Exception as e:
            logger.error(f"❌ Failed to initialize MaidSystem tables: {e}", exc_info=True)
    
    # ======================
    # GACHA COMMANDS
    # ======================
    
    def _check_gacha_cooldown(self, user_id: int) -> tuple[bool, float]:
        """🔒 Check if user can roll gacha với persistent cooldowns"""
        can_proceed, remaining = cooldown_manager.check_cooldown(user_id, self.GACHA_COOLDOWN)
        
        return can_proceed, remaining
    
    async def _find_user_maid(self, user_id: int, maid_id: str) -> Optional[UserMaid]:
        """🔒 Securely find user's maid by ID or name with ownership validation"""
        user_maids = await self.maid_db.get_user_maids(user_id)
        search_lower = maid_id.lower()
        
        # First pass: Try exact instance ID match
        for maid in user_maids:
            if maid.instance_id.startswith(search_lower):
                # Double-check ownership (security)
                if maid.user_id != user_id:
                    return None  # Ownership violation
                return maid
        
        # Second pass: Try maid name or custom name match
        for maid in user_maids:
            template = MAID_TEMPLATES.get(maid.maid_id)
            if template:
                # Check template name
                if search_lower in template["name"].lower():
                    if maid.user_id != user_id:
                        return None  # Ownership violation  
                    return maid
                
                # Check custom name
                if maid.custom_name and search_lower in maid.custom_name.lower():
                    if maid.user_id != user_id:
                        return None  # Ownership violation
                    return maid
        
        return None  # Not found

    @app_commands.command(name="maid_gacha", description="🎰 Roll gacha để nhận maid (10,000 coins)")
    async def maid_gacha_single(self, interaction: discord.Interaction):
        """Roll gacha 1 lần"""
        user_id = interaction.user.id
        
        # 🔒 Check rate limit with persistent cooldowns
        can_proceed, remaining = self._check_gacha_cooldown(user_id)
        if not can_proceed:
            await interaction.response.send_message(
                f"⏰ Vui lòng đợi {remaining:.1f}s trước khi roll tiếp!", 
                ephemeral=True
            )
            return
        
        cost = GACHA_CONFIG["single_roll_cost"]
        
        # Kiểm tra tiền
        user = await self.bot.db.get_user(user_id)
        if not user:
            await interaction.response.send_message("❌ Bạn chưa đăng ký! Dùng lệnh farm để bắt đầu.", ephemeral=True)
            return
        
        if user.money < cost:
            await interaction.response.send_message(
                f"❌ Không đủ tiền! Cần {cost:,} coins, bạn có {user.money:,} coins.", 
                ephemeral=True
            )
            return
        
        # 🔒 Transaction safety: Trừ tiền trước, rollback nếu fail
        try:
            # Set cooldown immediately after all checks pass
            cooldown_manager.set_cooldown(user_id, self.GACHA_COOLDOWN)
            
            # Trừ tiền trước
            await self.bot.db.update_user_money(user_id, -cost)
            
            # Thực hiện roll
            result = await self._perform_gacha_roll(user_id, 1, cost, "single")
            
            if result["success"]:
                # Tạo embed kết quả
                embed = await self._create_gacha_result_embed(result["maids"], "single", cost)
                await interaction.response.send_message(embed=embed)
            else:
                # Rollback tiền nếu gacha fail
                await self.bot.db.update_user_money(user_id, cost)
                await interaction.response.send_message(f"❌ Lỗi gacha: {result['error']}", ephemeral=True)
                
        except Exception as e:
            # Rollback tiền nếu có exception
            await self.bot.db.update_user_money(user_id, cost)
            await interaction.response.send_message(f"❌ Lỗi hệ thống: {str(e)}", ephemeral=True)
            logger.error(f"Error in maid_gacha_single for user {user_id}: {e}", exc_info=True)
    
    @app_commands.command(name="maid_gacha10", description="🎰 Roll gacha 10 lần (90,000 coins - Giảm 10%)")
    async def maid_gacha_ten(self, interaction: discord.Interaction):
        """Roll gacha 10 lần"""
        user_id = interaction.user.id
        
        # 🔒 Check rate limit with persistent cooldowns
        can_proceed, remaining = self._check_gacha_cooldown(user_id)
        if not can_proceed:
            await interaction.response.send_message(
                f"⏰ Vui lòng đợi {remaining:.1f}s trước khi roll tiếp!", 
                ephemeral=True
            )
            return
        
        cost = GACHA_CONFIG["ten_roll_cost"]
        
        # Kiểm tra tiền
        user = await self.bot.db.get_user(user_id)
        if not user:
            await interaction.response.send_message("❌ Bạn chưa đăng ký! Dùng lệnh farm để bắt đầu.", ephemeral=True)
            return
        
        if user.money < cost:
            await interaction.response.send_message(
                f"❌ Không đủ tiền! Cần {cost:,} coins, bạn có {user.money:,} coins.", 
                ephemeral=True
            )
            return
        
        # 🔒 Transaction safety: Trừ tiền trước, rollback nếu fail
        try:
            # Set cooldown immediately after all checks pass
            cooldown_manager.set_cooldown(user_id, self.GACHA_COOLDOWN)
            
            # Trừ tiền trước
            await self.bot.db.update_user_money(user_id, -cost)
            
            # Thực hiện roll
            result = await self._perform_gacha_roll(user_id, 10, cost, "ten")
            
            if result["success"]:
                # Tạo embed kết quả
                embed = await self._create_gacha_result_embed(result["maids"], "ten", cost)
                await interaction.response.send_message(embed=embed)
            else:
                # Rollback tiền nếu gacha fail
                await self.bot.db.update_user_money(user_id, cost)
                await interaction.response.send_message(f"❌ Lỗi gacha: {result['error']}", ephemeral=True)
                
        except Exception as e:
            # Rollback tiền nếu có exception
            await self.bot.db.update_user_money(user_id, cost)
            await interaction.response.send_message(f"❌ Lỗi hệ thống: {str(e)}", ephemeral=True)
            logger.error(f"Error in maid_gacha_ten for user {user_id}: {e}", exc_info=True)
    
    @app_commands.command(name="maid_pity", description="📊 Xem tỷ lệ gacha rates")
    async def maid_pity(self, interaction: discord.Interaction):
        """📊 NEW: Hiển thị individual maid rates"""
        user_id = interaction.user.id
        
        embed = EmbedBuilder.create_base_embed(
            title="📊 Individual Maid Rates",
            description="🎯 **NEW SYSTEM**: Mỗi maid có tỷ lệ riêng!",
            color=0x9932CC
        )
        
        # Hiển thị total rates by rarity
        embed.add_field(
            name="🎯 Total Rates by Rarity",
            value=f"💎 UR: {RARITY_CONFIG['UR']['total_rate']}% (6 maids)\n"
                  f"🌟 SSR: {RARITY_CONFIG['SSR']['total_rate']}% (10 maids)\n"
                  f"⭐ SR: {RARITY_CONFIG['SR']['total_rate']}% (15 maids)\n"
                  f"✨ R: {RARITY_CONFIG['R']['total_rate']}% (19 maids)",
            inline=True
        )
        
        # Hiển thị individual rates
        embed.add_field(
            name="🔍 Per Maid Rates",
            value=f"💎 UR: {RARITY_CONFIG['UR']['individual_rate']:.4f}%/maid\n"
                  f"🌟 SSR: {RARITY_CONFIG['SSR']['individual_rate']:.3f}%/maid\n"
                  f"⭐ SR: {RARITY_CONFIG['SR']['individual_rate']:.2f}%/maid\n"
                  f"✨ R: {RARITY_CONFIG['R']['individual_rate']:.2f}%/maid",
            inline=True
        )
        
        embed.add_field(
            name="🎲 How It Works",
            value="• **Individual System**: Mỗi maid có rate riêng\n"
                  "• **Fair Distribution**: Rate chia đều theo rarity\n"
                  "• **No Pity**: Pure RNG cho mọi rolls\n"
                  "• **Example**: Rem UR có 0.0167% chance",
            inline=False
        )
        
        # User stats
        stats = await self.maid_db.get_user_gacha_history(user_id)
        if stats:
            total_rolls = len(stats)
            ur_count = len([s for s in stats if MAID_TEMPLATES[s.maid_id]["rarity"] == "UR"])
            ssr_count = len([s for s in stats if MAID_TEMPLATES[s.maid_id]["rarity"] == "SSR"])
            sr_count = len([s for s in stats if MAID_TEMPLATES[s.maid_id]["rarity"] == "SR"])
            r_count = len([s for s in stats if MAID_TEMPLATES[s.maid_id]["rarity"] == "R"])
            
            embed.add_field(
                name="📈 Your Stats",
                value=f"🎯 Total rolls: {total_rolls}\n"
                      f"💎 UR: {ur_count} ({ur_count/total_rolls*100:.1f}%)\n"
                      f"🌟 SSR: {ssr_count} ({ssr_count/total_rolls*100:.1f}%)\n"
                      f"⭐ SR: {sr_count} ({sr_count/total_rolls*100:.1f}%)\n"
                      f"✨ R: {r_count} ({r_count/total_rolls*100:.1f}%)",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed)
    
    # ======================
    # COLLECTION COMMANDS
    # ======================
    
    @app_commands.command(name="maid_collection", description="📚 Xem collection maid của bạn")
    @app_commands.describe(page="Trang hiển thị")
    async def maid_collection(self, interaction: discord.Interaction, page: int = 1):
        """Hiển thị collection maid"""
        user_id = interaction.user.id
        maids = await self.maid_db.get_user_maids(user_id)
        
        if not maids:
            embed = EmbedBuilder.create_base_embed(
                title="📚 Collection Maid",
                description="Bạn chưa có maid nào! Dùng `/maid_gacha` để roll maid đầu tiên.",
                color=0x9932CC
            )
            await interaction.response.send_message(embed=embed)
            return
        
        # Pagination
        per_page = UI_CONFIG["maids_per_page"]
        total_pages = (len(maids) + per_page - 1) // per_page
        page = max(1, min(page, total_pages))
        
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        page_maids = maids[start_idx:end_idx]
        
        embed = EmbedBuilder.create_base_embed(
            title="📚 Collection Maid",
            description=f"Trang {page}/{total_pages} • {len(maids)} maids",
            color=0x9932CC
        )
        
        for maid in page_maids:
            template = MAID_TEMPLATES[maid.maid_id]
            rarity_emoji = RARITY_EMOJIS[template["rarity"]]
            
            # Tên hiển thị
            display_name = maid.custom_name if maid.custom_name else template["name"]
            if maid.is_active:
                display_name += " ⭐"
            
            # Buffs
            buff_text = "\n".join([
                f"{BUFF_TYPES[buff.buff_type]['emoji']} {buff.buff_type.replace('_', ' ').title()}: +{buff.value}%"
                for buff in maid.buff_values
            ])
            
            embed.add_field(
                name=f"{rarity_emoji} {template['emoji']} {display_name}",
                value=f"**{template['full_name']}**\n{buff_text}\n`ID: {maid.instance_id[:8]}`",
                inline=True
            )
        
        # Navigation buttons
        if total_pages > 1:
            view = CollectionNavigationView(user_id, page, total_pages)
            await interaction.response.send_message(embed=embed, view=view)
        else:
            await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="maid_equip", description="⚔️ Trang bị maid")
    @app_commands.describe(maid_id="ID của maid (8 ký tự đầu)")
    async def maid_equip(self, interaction: discord.Interaction, maid_id: str):
        """Trang bị maid"""
        user_id = interaction.user.id
        
        # 🔒 Tìm maid với ownership validation
        maid_to_equip = await self._find_user_maid(user_id, maid_id)
        
        if not maid_to_equip:
            await interaction.response.send_message(f"❌ Không tìm thấy maid với ID `{maid_id}` hoặc bạn không sở hữu maid này!", ephemeral=True)
            return
        
        # Set active
        success = await self.maid_db.set_active_maid(user_id, maid_to_equip.instance_id)
        
        if success:
            template = MAID_TEMPLATES[maid_to_equip.maid_id]
            display_name = maid_to_equip.custom_name if maid_to_equip.custom_name else template["name"]
            
            embed = EmbedBuilder.create_base_embed(
                title="⚔️ Maid Equipped!",
                description=f"Đã trang bị **{display_name}**!",
                color=RARITY_CONFIG[template["rarity"]]["color"]
            )
            
            # Hiển thị buffs
            buff_text = "\n".join([
                f"{BUFF_TYPES[buff.buff_type]['emoji']} {BUFF_TYPES[buff.buff_type]['name']}: +{buff.value}%"
                for buff in maid_to_equip.buff_values
            ])
            
            embed.add_field(
                name="✨ Active Buffs",
                value=buff_text,
                inline=False
            )
            
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("❌ Lỗi khi trang bị maid!", ephemeral=True)
    
    @app_commands.command(name="maid_active", description="👑 Xem maid đang active và buffs")
    async def maid_active(self, interaction: discord.Interaction):
        """Xem maid active hiện tại"""
        user_id = interaction.user.id
        active_maid = await self.maid_db.get_active_maid(user_id)
        
        if not active_maid:
            embed = EmbedBuilder.create_base_embed(
                title="👑 Maid Active",
                description="Bạn chưa trang bị maid nào!\nDùng `/maid_equip <id>` để trang bị maid.",
                color=0x9932CC
            )
            await interaction.response.send_message(embed=embed)
            return
        
        template = MAID_TEMPLATES[active_maid.maid_id]
        display_name = active_maid.custom_name if active_maid.custom_name else template["name"]
        
        embed = EmbedBuilder.create_base_embed(
            title="👑 Maid Active",
            description=f"**{template['full_name']}**\n*{template['description']}*",
            color=RARITY_CONFIG[template["rarity"]]["color"]
        )
        
        embed.set_thumbnail(url=interaction.user.avatar.url if interaction.user.avatar else None)
        
        # Thông tin cơ bản
        embed.add_field(
            name="📝 Tên",
            value=display_name,
            inline=True
        )
        
        embed.add_field(
            name="⭐ Rarity", 
            value=f"{RARITY_EMOJIS[template['rarity']]} {template['rarity']}",
            inline=True
        )
        
        embed.add_field(
            name="🆔 ID",
            value=f"`{active_maid.instance_id[:8]}`",
            inline=True
        )
        
        # Buffs
        buff_text = ""
        for buff in active_maid.buff_values:
            buff_info = BUFF_TYPES[buff.buff_type]
            buff_text += f"{buff_info['emoji']} **{buff_info['name']}**: +{buff.value}%\n"
        
        embed.add_field(
            name="✨ Active Buffs",
            value=buff_text or "Không có buff",
            inline=False
        )
        
        # Thời gian nhận
        embed.add_field(
            name="🕐 Nhận lúc",
            value=f"<t:{int(active_maid.obtained_at.timestamp())}:F>",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)
    
    # ======================
    # MANAGEMENT COMMANDS
    # ======================
    
    @app_commands.command(name="maid_rename", description="✏️ Đổi tên maid")
    @app_commands.describe(maid_id="ID của maid (8 ký tự đầu)", new_name="Tên mới cho maid")
    async def maid_rename(self, interaction: discord.Interaction, maid_id: str, new_name: str):
        """Đổi tên maid"""
        user_id = interaction.user.id
        
        # Giới hạn độ dài tên
        if len(new_name) > 30:
            await interaction.response.send_message("❌ Tên quá dài! Tối đa 30 ký tự.", ephemeral=True)
            return
        
        # 🔒 Tìm maid với ownership validation
        maid_to_rename = await self._find_user_maid(user_id, maid_id)
        
        if not maid_to_rename:
            await interaction.response.send_message(f"❌ Không tìm thấy maid với ID `{maid_id}` hoặc bạn không sở hữu maid này!", ephemeral=True)
            return
        
        # Đổi tên
        success = await self.maid_db.rename_maid(user_id, maid_to_rename.instance_id, new_name)
        
        if success:
            template = MAID_TEMPLATES[maid_to_rename.maid_id]
            embed = EmbedBuilder.create_base_embed(
                title="✏️ Đổi Tên Thành Công!",
                description=f"**{template['name']}** đã được đổi tên thành **{new_name}**!",
                color=RARITY_CONFIG[template["rarity"]]["color"]
            )
            embed.add_field(name="🆔 ID", value=f"`{maid_to_rename.instance_id[:8]}`", inline=True)
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("❌ Lỗi khi đổi tên maid!", ephemeral=True)
    
    # ======================
    # STARDUST COMMANDS
    # ======================
    
    @app_commands.command(name="maid_stardust", description="⭐ Xem số bụi sao hiện có")
    async def maid_stardust(self, interaction: discord.Interaction):
        """Xem stardust"""
        user_id = interaction.user.id
        stardust = await self.maid_db.get_user_stardust(user_id)
        
        embed = EmbedBuilder.create_base_embed(
            title="⭐ Bụi Sao",
            description=f"Bụi sao của {interaction.user.mention}",
            color=0xFFD700
        )
        
        embed.add_field(
            name="💫 Số lượng",
            value=f"{stardust.stardust_amount:,} bụi sao",
            inline=True
        )
        
        embed.add_field(
            name="🔄 Reroll Costs",
            value=f"UR: {STARDUST_CONFIG['reroll_costs']['UR']} ⭐\n"
                  f"SSR: {STARDUST_CONFIG['reroll_costs']['SSR']} ⭐\n"
                  f"SR: {STARDUST_CONFIG['reroll_costs']['SR']} ⭐\n"
                  f"R: {STARDUST_CONFIG['reroll_costs']['R']} ⭐",
            inline=True
        )
        
        embed.add_field(
            name="💥 Dismantle Rewards",
            value=f"UR: {STARDUST_CONFIG['dismantle_rewards']['UR']} ⭐\n"
                  f"SSR: {STARDUST_CONFIG['dismantle_rewards']['SSR']} ⭐\n"
                  f"SR: {STARDUST_CONFIG['dismantle_rewards']['SR']} ⭐\n"
                  f"R: {STARDUST_CONFIG['dismantle_rewards']['R']} ⭐",
            inline=True
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="maid_dismantle", description="💥 Tách maid thành bụi sao")
    @app_commands.describe(maid_id="ID của maid (8 ký tự đầu)")
    async def maid_dismantle(self, interaction: discord.Interaction, maid_id: str):
        """Tách maid thành stardust"""
        user_id = interaction.user.id
        
        # 🔒 Tìm maid với ownership validation
        maid_to_dismantle = await self._find_user_maid(user_id, maid_id)
        
        if not maid_to_dismantle:
            await interaction.response.send_message(f"❌ Không tìm thấy maid với ID `{maid_id}` hoặc bạn không sở hữu maid này!", ephemeral=True)
            return
        
        # Không cho phép tách maid đang active
        if maid_to_dismantle.is_active:
            await interaction.response.send_message("❌ Không thể tách maid đang active! Hãy equip maid khác trước.", ephemeral=True)
            return
        
        template = MAID_TEMPLATES[maid_to_dismantle.maid_id]
        rarity = template["rarity"]
        stardust_reward = STARDUST_CONFIG["dismantle_rewards"][rarity]
        
        # Tạo view xác nhận
        view = DismantleConfirmView(user_id, maid_to_dismantle, stardust_reward)
        
        embed = EmbedBuilder.create_base_embed(
            title="💥 Xác Nhận Dismantle",
            description=f"Bạn có chắc muốn tách **{maid_to_dismantle.custom_name or template['name']}** thành bụi sao?",
            color=0xFF6B6B
        )
        
        embed.add_field(
            name="🗑️ Maid bị xóa",
            value=f"{RARITY_EMOJIS[rarity]} {template['emoji']} {template['full_name']}",
            inline=True
        )
        
        embed.add_field(
            name="⭐ Nhận được",
            value=f"{stardust_reward:,} bụi sao",
            inline=True
        )
        
        embed.add_field(
            name="⚠️ Cảnh báo",
            value="**Hành động này không thể hoàn tác!**",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, view=view)
    
    @app_commands.command(name="maid_reroll_cost", description="💰 Xem chi phí reroll động của maid")
    @app_commands.describe(maid_id="ID của maid (8 ký tự đầu)")
    async def maid_reroll_cost(self, interaction: discord.Interaction, maid_id: str):
        """Preview chi phí reroll động của maid"""
        user_id = interaction.user.id
        
        # Find maid
        maid = await self._find_user_maid(user_id, maid_id)
        if not maid:
            await interaction.response.send_message(
                "❌ Không tìm thấy maid hoặc maid không thuộc về bạn!", 
                ephemeral=True
            )
            return
        
        # Get maid template
        template = MAID_TEMPLATES.get(maid.maid_id)
        if not template:
            await interaction.response.send_message("❌ Không tìm thấy thông tin maid!", ephemeral=True)
            return
        
        # Get reroll history
        reroll_times = reroll_history_manager.get_reroll_times(maid.instance_id)
        
        # Calculate dynamic cost
        cost, breakdown = dynamic_cost_calculator.calculate_reroll_cost(
            maid, template, reroll_times
        )
        
        # Create embed
        embed = EmbedBuilder.create_base_embed(
            title=f"💰 Chi Phí Reroll - {template['name']}",
            description=f"**{RARITY_EMOJIS[template['rarity']]} {template['rarity']} Maid**\n"
                       f"ID: `{maid.instance_id[:8]}`",
            color=0x9932CC
        )
        
        # Current buffs
        current_buffs_text = []
        for buff in maid.buff_values:
            current_buffs_text.append(f"{buff.buff_type}: +{buff.value}%")
        
        embed.add_field(
            name="🔧 Current Buffs",
            value="\n".join(current_buffs_text) if current_buffs_text else "Chưa có buffs",
            inline=True
        )
        
        # Reroll stats
        embed.add_field(
            name="📊 Reroll Stats", 
            value=f"Số lần reroll: {len(reroll_times)}\n"
                  f"Lần cuối: {reroll_times[0][:10] if reroll_times else 'Chưa bao giờ'}",
            inline=True
        )
        
        # Cost breakdown
        breakdown_text = dynamic_cost_calculator.format_cost_breakdown(breakdown)
        embed.add_field(
            name="📋 Cost Breakdown",
            value=breakdown_text,
            inline=False
        )
        
        # Check if user has enough stardust
        user_stardust = await self.maid_db.get_user_stardust(user_id)
        
        if user_stardust >= cost:
            embed.add_field(
                name="✅ Stardust Status",
                value=f"Có đủ: {user_stardust:,}/⭐ (cần {cost:,}⭐)",
                inline=True
            )
        else:
            needed = cost - user_stardust
            embed.add_field(
                name="❌ Stardust Status", 
                value=f"Thiếu {needed:,}⭐ (có {user_stardust:,}⭐, cần {cost:,}⭐)",
                inline=True
            )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="maid_reroll", description="🎲 Reroll buffs của maid bằng bụi sao")
    @app_commands.describe(maid_id="ID của maid (8 ký tự đầu)")
    async def maid_reroll(self, interaction: discord.Interaction, maid_id: str):
        """Reroll buffs của maid"""
        user_id = interaction.user.id
        
        # 🔒 Tìm maid với ownership validation
        maid_to_reroll = await self._find_user_maid(user_id, maid_id)
        
        if not maid_to_reroll:
            await interaction.response.send_message(f"❌ Không tìm thấy maid với ID `{maid_id}` hoặc bạn không sở hữu maid này!", ephemeral=True)
            return
        
        template = MAID_TEMPLATES[maid_to_reroll.maid_id]
        rarity = template["rarity"]
        
        # 🆕 Calculate dynamic reroll cost
        reroll_times = reroll_history_manager.get_reroll_times(maid_to_reroll.instance_id)
        reroll_cost, breakdown = dynamic_cost_calculator.calculate_reroll_cost(
            maid_to_reroll, template, reroll_times
        )
        
        # Kiểm tra stardust
        stardust = await self.maid_db.get_user_stardust(user_id)
        if stardust.stardust_amount < reroll_cost:
            # Show cost breakdown when not enough stardust
            breakdown_text = dynamic_cost_calculator.format_cost_breakdown(breakdown)
            await interaction.response.send_message(
                f"❌ **Không đủ bụi sao!**\n"
                f"Cần {reroll_cost:,}⭐, bạn có {stardust.stardust_amount:,}⭐\n\n"
                f"{breakdown_text}\n\n"
                f"💡 *Dùng `/maid_reroll_cost {maid_to_reroll.instance_id[:8]}` để xem chi tiết*",
                ephemeral=True
            )
            return
        
        # Tạo view xác nhận với dynamic cost
        view = RerollConfirmView(user_id, maid_to_reroll, reroll_cost)
        
        embed = EmbedBuilder.create_base_embed(
            title="🎲 Xác Nhận Reroll",
            description=f"Bạn có chắc muốn reroll buffs của **{maid_to_reroll.custom_name or template['name']}**?",
            color=0x9932CC
        )
        
        embed.add_field(
            name="🎯 Maid",
            value=f"{RARITY_EMOJIS[rarity]} {template['emoji']} {template['full_name']}",
            inline=True
        )
        
        embed.add_field(
            name="💰 Chi phí (Dynamic)",
            value=f"{reroll_cost:,} ⭐ bụi sao\n"
                  f"*Base: {breakdown['base_cost']} × {breakdown['final_multiplier']:.1f}*",
            inline=True
        )
        
        # Hiển thị buffs hiện tại
        current_buffs = "\n".join([
            f"{BUFF_TYPES[buff.buff_type]['emoji']} {BUFF_TYPES[buff.buff_type]['name']}: +{buff.value}%"
            for buff in maid_to_reroll.buff_values
        ])
        
        embed.add_field(
            name="✨ Buffs hiện tại",
            value=current_buffs,
            inline=False
        )
        
        embed.add_field(
            name="⚠️ Lưu ý",
            value="Buffs mới sẽ được random trong cùng rarity range!",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, view=view)
    
    # ======================
    # STATS COMMANDS
    # ======================
    
    @app_commands.command(name="maid_info", description="🔍 Xem thông tin chi tiết maid trong collection")
    @app_commands.describe(maid_id="ID hoặc tên maid (8 ký tự đầu)")
    async def maid_info(self, interaction: discord.Interaction, maid_id: str):
        """Xem thông tin chi tiết maid trong collection"""
        user_id = interaction.user.id
        
        # 🔒 Tìm maid với ownership validation
        maid = await self._find_user_maid(user_id, maid_id)
        
        if not maid:
            await interaction.response.send_message(f"❌ Không tìm thấy maid với ID `{maid_id}` trong collection của bạn!", ephemeral=True)
            return
        
        template = MAID_TEMPLATES[maid.maid_id]
        display_name = maid.custom_name if maid.custom_name else template["name"]
        
        embed = EmbedBuilder.create_base_embed(
            title=f"🔍 {template['emoji']} {display_name}",
            description=f"**{template['full_name']}**\n*{template['description']}*",
            color=RARITY_CONFIG[template["rarity"]]["color"]
        )
        
        # Set avatar if available
        if template.get("art_url"):
            embed.set_image(url=template["art_url"])
        else:
            # Placeholder avatar based on emoji/rarity
            embed.set_thumbnail(url=interaction.user.avatar.url if interaction.user.avatar else None)
        
        # Basic Info
        embed.add_field(
            name="📋 Thông Tin Cơ Bản",
            value=f"**Rarity**: {RARITY_EMOJIS[template['rarity']]} {template['rarity']}\n"
                  f"**ID**: `{maid.instance_id[:8]}`\n"
                  f"**Status**: {'⭐ Active' if maid.is_active else '💤 Inactive'}\n"
                  f"**Obtained**: <t:{int(maid.obtained_at.timestamp())}:R>",
            inline=True
        )
        
        # Current Buffs (Actual owned)
        current_buffs = []
        for buff in maid.buff_values:
            buff_info = BUFF_TYPES[buff.buff_type]
            current_buffs.append(f"{buff_info['emoji']} **{buff_info['name']}**\n└ `+{buff.value}%` - {buff_info['description']}")
        
        embed.add_field(
            name="✨ Skills Đang Sở Hữu",
            value="\n\n".join(current_buffs) if current_buffs else "Không có buffs",
            inline=False
        )
        
        # Possible Buffs (What this maid can have)
        possible_buffs = []
        for buff_type in template["possible_buffs"]:
            buff_info = BUFF_TYPES[buff_type]
            rarity_range = RARITY_CONFIG[template["rarity"]]["buff_range"]
            possible_buffs.append(f"{buff_info['emoji']} **{buff_info['name']}**\n└ `{rarity_range[0]}-{rarity_range[1]}%` - {buff_info['description']}")
        
        embed.add_field(
            name="🎲 Skills Có Thể Có (Reroll)",
            value="\n\n".join(possible_buffs),
            inline=False
        )
        
        # Individual Rate Info
        individual_rate = RARITY_CONFIG[template["rarity"]]["individual_rate"]
        embed.add_field(
            name="📊 Gacha Info",
            value=f"**Drop Rate**: {individual_rate:.4f}% per roll\n"
                  f"**Buff Count**: {RARITY_CONFIG[template['rarity']]['buff_count']} buffs\n"
                  f"**Reroll Cost**: {STARDUST_CONFIG['reroll_costs'][template['rarity']]} ⭐\n"
                  f"**Dismantle**: {STARDUST_CONFIG['dismantle_rewards'][template['rarity']]} ⭐",
            inline=True
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="maid_database", description="📚 Tìm kiếm maid trong database hệ thống") 
    @app_commands.describe(search="Tên maid cần tìm (có thể viết tắt)")
    async def maid_database(self, interaction: discord.Interaction, search: str):
        """Tìm kiếm và hiển thị thông tin maid trong database"""
        search_lower = search.lower()
        
        # Tìm kiếm maid
        found_maids = []
        for maid_id, template in MAID_TEMPLATES.items():
            if (search_lower in template["name"].lower() or 
                search_lower in template["full_name"].lower() or
                search_lower in maid_id.lower()):
                found_maids.append((maid_id, template))
        
        if not found_maids:
            embed = EmbedBuilder.create_base_embed(
                title="❌ Không Tìm Thấy",
                description=f"Không tìm thấy maid nào với từ khóa `{search}`",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if len(found_maids) == 1:
            # Hiển thị chi tiết 1 maid
            maid_id, template = found_maids[0]
            
            embed = EmbedBuilder.create_base_embed(
                title=f"📚 {template['emoji']} {template['name']}",
                description=f"**{template['full_name']}**\n*{template['description']}*",
                color=RARITY_CONFIG[template["rarity"]]["color"]
            )
            
            # Set avatar if available
            if template.get("art_url"):
                embed.set_image(url=template["art_url"])
            
            # Basic Info
            embed.add_field(
                name="📋 Thông Tin Cơ Bản",
                value=f"**Rarity**: {RARITY_EMOJIS[template['rarity']]} {template['rarity']}\n"
                      f"**Maid ID**: `{maid_id}`\n"
                      f"**Drop Rate**: {RARITY_CONFIG[template['rarity']]['individual_rate']:.4f}%\n"
                      f"**Buff Count**: {RARITY_CONFIG[template['rarity']]['buff_count']} buffs",
                inline=True
            )
            
            # Possible Skills when rolled
            possible_buffs = []
            for buff_type in template["possible_buffs"]:
                buff_info = BUFF_TYPES[buff_type]
                rarity_range = RARITY_CONFIG[template["rarity"]]["buff_range"]
                possible_buffs.append(f"{buff_info['emoji']} **{buff_info['name']}**\n└ `{rarity_range[0]}-{rarity_range[1]}%` - {buff_info['description']}")
            
            embed.add_field(
                name="🎲 Skills Khi Roll Trúng",
                value="\n\n".join(possible_buffs),
                inline=False
            )
            
            # Gacha Economics
            embed.add_field(
                name="💰 Economics",
                value=f"**Reroll Cost**: {STARDUST_CONFIG['reroll_costs'][template['rarity']]} ⭐\n"
                      f"**Dismantle Reward**: {STARDUST_CONFIG['dismantle_rewards'][template['rarity']]} ⭐\n"
                      f"**Expected Rolls**: ~{100/RARITY_CONFIG[template['rarity']]['individual_rate']:.0f} rolls\n"
                      f"**Expected Cost**: ~{100/RARITY_CONFIG[template['rarity']]['individual_rate'] * 10000:.0f} coins",
                inline=True
            )
            
            # Check if user owns this maid
            user_id = interaction.user.id
            user_maids = self.maid_db.get_user_maids(user_id)
            owned_count = len([m for m in user_maids if m.maid_id == maid_id])
            
            if owned_count > 0:
                embed.add_field(
                    name=" Ownership Status",
                    value=f"✅ **Bạn sở hữu {owned_count}x {template['name']}**\n"
                          f"Dùng `/maid_info <id>` để xem chi tiết",
                    inline=False
                )
            else:
                embed.add_field(
                    name="💫 Acquisition",
                    value=f"❌ **Bạn chưa sở hữu {template['name']}**\n"
                          f"Roll gacha để có cơ hội nhận được!",
                    inline=False
                )
                
        else:
            # Hiển thị list nhiều maids
            embed = EmbedBuilder.create_base_embed(
                title=f"🔍 Kết Quả Tìm Kiếm: `{search}`",
                description=f"Tìm thấy {len(found_maids)} maids:",
                color=0x9932CC
            )
            
            # Group by rarity
            by_rarity = {"UR": [], "SSR": [], "SR": [], "R": []}
            for maid_id, template in found_maids:
                by_rarity[template["rarity"]].append((maid_id, template))
            
            for rarity in ["UR", "SSR", "SR", "R"]:
                if by_rarity[rarity]:
                    maid_list = []
                    for maid_id, template in by_rarity[rarity][:5]:  # Limit 5 per rarity
                        rate = RARITY_CONFIG[template["rarity"]]["individual_rate"]
                        maid_list.append(f"{template['emoji']} **{template['name']}** - {series}\n"
                               f"└ `{individual_rate:.4f}%` • `/maid_database {template['name'].lower()}`")
                    
                    if len(by_rarity[rarity]) > 5:
                        maid_list.append(f"... và {len(by_rarity[rarity]) - 5} maids khác")
                    
                    embed.add_field(
                        name=f"{RARITY_EMOJIS[rarity]} {rarity} Maids",
                        value="\n".join(maid_list),
                        inline=True
                    )
            
            embed.add_field(
                name="💡 Tip",
                value="Gõ tên maid cụ thể để xem thông tin chi tiết!\nVD: `/maid_database rem`",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="maid_list", description="📜 Xem danh sách tất cả maids theo rarity")
    @app_commands.describe(rarity="Rarity để xem (UR/SSR/SR/R), để trống để xem tất cả")
    async def maid_list(self, interaction: discord.Interaction, rarity: str = None):
        """Hiển thị danh sách tất cả maids theo rarity"""
        
        if rarity and rarity.upper() not in ["UR", "SSR", "SR", "R"]:
            await interaction.response.send_message("❌ Rarity phải là: UR, SSR, SR, hoặc R", ephemeral=True)
            return
        
        target_rarity = rarity.upper() if rarity else None
        
        # Group maids by rarity
        by_rarity = {"UR": [], "SSR": [], "SR": [], "R": []}
        for maid_id, template in MAID_TEMPLATES.items():
            by_rarity[template["rarity"]].append((maid_id, template))
        
        # Sort each rarity by name
        for r in by_rarity:
            by_rarity[r].sort(key=lambda x: x[1]["name"])
        
        if target_rarity:
            # Show specific rarity
            embed = EmbedBuilder.create_base_embed(
                title=f"📜 {RARITY_EMOJIS[target_rarity]} {target_rarity} Maids",
                description=f"Tất cả {len(by_rarity[target_rarity])} maids rarity {target_rarity}",
                color=RARITY_CONFIG[target_rarity]["color"]
            )
            
            maid_list = []
            for maid_id, template in by_rarity[target_rarity]:
                individual_rate = RARITY_CONFIG[template["rarity"]]["individual_rate"]
                series = template.get("series", "Unknown")
                maid_list.append(f"{template['emoji']} **{template['name']}** - {series}\n"
                               f"└ `{individual_rate:.4f}%` • `/maid_database {template['name'].lower()}`")
            
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
            
            for rarity in ["UR", "SSR", "SR", "R"]:
                maid_list = []
                total_rate = RARITY_CONFIG[rarity]["total_rate"]
                individual_rate = RARITY_CONFIG[rarity]["individual_rate"]
                
                # Show first few maids as examples
                for maid_id, template in by_rarity[rarity][:6]:
                    maid_list.append(f"{template['emoji']} {template['name']}")
                
                if len(by_rarity[rarity]) > 6:
                    maid_list.append(f"... và {len(by_rarity[rarity]) - 6} maids khác")
                
                embed.add_field(
                    name=f"{RARITY_EMOJIS[rarity]} {rarity} ({len(by_rarity[rarity])} maids)",
                    value=f"**Total Rate**: {total_rate}%\n"
                          f"**Per Maid**: {individual_rate:.4f}%\n"
                          f"**Examples**:\n" + "\n".join(maid_list),
                    inline=True
                )
            
            embed.add_field(
                name="🔍 Commands",
                value="• `/maid_list UR` - Xem tất cả UR maids\n"
                      "• `/maid_database <tên>` - Search maid cụ thể\n"
                      "• `/maid_info <id>` - Chi tiết maid trong collection",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="maid_stats", description="📊 Xem thống kê gacha của bạn")
    async def maid_stats(self, interaction: discord.Interaction):
        """Xem thống kê maid"""
        user_id = interaction.user.id
        stats = await self.maid_db.get_user_maid_stats(user_id)
        stardust = await self.maid_db.get_user_stardust(user_id)
        
        embed = EmbedBuilder.create_base_embed(
            title="📊 Thống Kê Maid",
            description=f"Thống kê của {interaction.user.mention}",
            color=0x9932CC
        )
        
        embed.add_field(
            name="👥 Tổng Maid",
            value=f"{stats['total_maids']} maids",
            inline=True
        )
        
        embed.add_field(
            name="💰 Tổng Chi Tiêu",
            value=f"{stats['total_spent']:,} coins",
            inline=True
        )
        
        embed.add_field(
            name="🎰 Tổng Rolls",
            value=f"{stats['total_rolls']} lần",
            inline=True
        )
        
        # Breakdown theo rarity
        rarity_text = ""
        for rarity in ["UR", "SSR", "SR", "R"]:
            count = stats['rarity_count'][rarity]
            rarity_text += f"{RARITY_EMOJIS[rarity]} {rarity}: {count}\n"
        
        embed.add_field(
            name="⭐ Phân Loại",
            value=rarity_text,
            inline=True
        )
        
        embed.add_field(
            name="💫 Bụi Sao",
            value=f"{stardust.stardust_amount:,} ⭐",
            inline=True
        )
        
        # Tính tỷ lệ UR
        if stats['total_rolls'] > 0:
            ur_rate = (stats['rarity_count']['UR'] / stats['total_rolls']) * 100
            embed.add_field(
                name="📈 Tỷ Lệ UR",
                value=f"{ur_rate:.2f}%",
                inline=True
            )
        
            await interaction.response.send_message(embed=embed)
    
    # ======================
    # TEXT COMMAND WRAPPERS
    # ======================
    
    @commands.command(name="maid_gacha", aliases=["mg"], brief="🎰 Roll gacha để nhận maid (10,000 coins)")
    @registration_required
    async def maid_gacha_text(self, ctx, *args):
        """Text command wrapper cho maid gacha"""
        try:
            # Create fake interaction object
            class FakeInteraction:
                def __init__(self, user, channel):
                    self.user = user
                    self.channel = channel
                    self.response = FakeResponse(channel)
            
            class FakeResponse:
                def __init__(self, channel):
                    self.channel = channel
                
                async def send_message(self, content=None, *, embed=None, ephemeral=False):
                    if embed:
                        await self.channel.send(embed=embed)
                    else:
                        await self.channel.send(content)
            
            fake_interaction = FakeInteraction(ctx.author, ctx.channel)
            await self.maid_gacha_single(fake_interaction)
        except Exception as e:
            await ctx.send(f"❌ Lỗi maid gacha: {str(e)}")
            print(f"Error in maid_gacha_text: {e}")
            import traceback
            traceback.print_exc()
    
    @commands.command(name="maid_collection", aliases=["mc"], brief="📚 Xem collection maid của bạn")
    @registration_required
    async def maid_collection_text(self, ctx, page=None, *args):
        """Text command wrapper cho maid collection"""
        try:
            # Handle default page
            if page is None:
                page = 1
            else:
                try:
                    page = int(page)
                except (ValueError, TypeError):
                    await ctx.send("❌ Page phải là số nguyên!")
                    return
            class FakeInteraction:
                def __init__(self, user, channel):
                    self.user = user
                    self.channel = channel
                    self.response = FakeResponse(channel)
            
            class FakeResponse:
                def __init__(self, channel):
                    self.channel = channel
                
                async def send_message(self, content=None, *, embed=None, view=None, ephemeral=False):
                    if embed:
                        await self.channel.send(embed=embed, view=view)
                    else:
                        await self.channel.send(content, view=view)
            
            fake_interaction = FakeInteraction(ctx.author, ctx.channel)
            await self.maid_collection(fake_interaction, page)
        except Exception as e:
            await ctx.send(f"❌ Lỗi maid collection: {str(e)}")
            print(f"Error in maid_collection_text: {e}")
            import traceback
            traceback.print_exc()
    
    @commands.command(name="maid_active", aliases=["ma"], brief="👑 Xem maid đang active và buffs")
    @registration_required  
    async def maid_active_text(self, ctx, *args):
        """Text command wrapper cho maid active"""
        try:
            class FakeInteraction:
                def __init__(self, user, channel):
                    self.user = user
                    self.channel = channel
                    self.response = FakeResponse(channel)
            
            class FakeResponse:
                def __init__(self, channel):
                    self.channel = channel
                
                async def send_message(self, content=None, *, embed=None, ephemeral=False):
                    if embed:
                        await self.channel.send(embed=embed)
                    else:
                        await self.channel.send(content)
            
            fake_interaction = FakeInteraction(ctx.author, ctx.channel)
            await self.maid_active(fake_interaction)
        except Exception as e:
            await ctx.send(f"❌ Lỗi maid active: {str(e)}")
            print(f"Error in maid_active_text: {e}")
            import traceback
            traceback.print_exc()
    
    # ======================
    # HELPER METHODS
    # ======================
    
    async def _perform_gacha_roll(self, user_id: int, roll_count: int, cost: int, roll_type: str) -> Dict[str, Any]:
        """🎯 NEW: Thực hiện gacha roll với individual maid rates"""
        try:
            results = []
            
            for _ in range(roll_count):
                # 🎯 NEW: Roll trực tiếp cho maid cụ thể với individual rates
                maid_id = get_random_maid_by_individual_rates()
                
                # Generate buffs
                buffs = generate_random_buffs(maid_id)
                
                # Tạo UserMaid instance
                user_maid = UserMaid(
                    instance_id=str(uuid.uuid4()),
                    user_id=user_id,
                    maid_id=maid_id,
                    buff_values=[MaidBuff.from_dict(buff) for buff in buffs]
                )
                
                # Lưu vào database
                await self.maid_db.add_user_maid(user_maid)
                results.append(user_maid)
            
            # Lưu history
            history = GachaHistory(
                user_id=user_id,
                roll_type=roll_type,
                cost=cost,
                results=[maid.maid_id for maid in results]
            )
            await self.maid_db.add_gacha_history(history)
            
            return {"success": True, "maids": results}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _create_gacha_result_embed(self, maids: List[UserMaid], roll_type: str, cost: int) -> discord.Embed:
        """Tạo embed hiển thị kết quả gacha"""
        
        if roll_type == "single":
            maid = maids[0]
            template = MAID_TEMPLATES[maid.maid_id]
            
            embed = EmbedBuilder.create_base_embed(
                title="🎰 Gacha Result!",
                description=f"Chi phí: {cost:,} coins",
                color=RARITY_CONFIG[template["rarity"]]["color"]
            )
            
            embed.add_field(
                name=f"{RARITY_EMOJIS[template['rarity']]} {template['emoji']} {template['name']}",
                value=f"**{template['full_name']}**\n*{template['description']}*",
                inline=False
            )
            
            # Buffs
            buff_text = "\n".join([
                f"{BUFF_TYPES[buff.buff_type]['emoji']} {BUFF_TYPES[buff.buff_type]['name']}: +{buff.value}%"
                for buff in maid.buff_values
            ])
            
            embed.add_field(
                name="✨ Buffs",
                value=buff_text,
                inline=False
            )
            
            embed.add_field(
                name="🆔 Instance ID",
                value=f"`{maid.instance_id[:8]}`",
                inline=True
            )
            
        else:  # ten roll
            embed = EmbedBuilder.create_base_embed(
                title="🎰 Gacha x10 Results!",
                description=f"Chi phí: {cost:,} coins",
                color=0xFFD700
            )
            
            # Đếm theo rarity
            rarity_count = {"UR": 0, "SSR": 0, "SR": 0, "R": 0}
            for maid in maids:
                template = MAID_TEMPLATES[maid.maid_id]
                rarity_count[template["rarity"]] += 1
            
            # Hiển thị summary
            summary_text = ""
            for rarity, count in rarity_count.items():
                if count > 0:
                    summary_text += f"{RARITY_EMOJIS[rarity]} {rarity}: {count}\n"
            
            embed.add_field(
                name="📊 Summary",
                value=summary_text,
                inline=True
            )
            
            # Hiển thị từng maid
            results_text = ""
            for i, maid in enumerate(maids, 1):
                template = MAID_TEMPLATES[maid.maid_id]
                results_text += f"{i}. {RARITY_EMOJIS[template['rarity']]} {template['emoji']} {template['name']}\n"
            
            embed.add_field(
                name="🎁 Results",
                value=results_text,
                inline=True
            )
        
        return embed

class CollectionNavigationView(discord.ui.View):
    def __init__(self, user_id: int, current_page: int, total_pages: int):
        super().__init__(timeout=300)
        self.user_id = user_id
        self.current_page = current_page
        self.total_pages = total_pages
        
        # Disable buttons nếu cần
        if current_page <= 1:
            self.prev_button.disabled = True
        if current_page >= total_pages:
            self.next_button.disabled = True
    
    @discord.ui.button(label="◀️ Prev", style=discord.ButtonStyle.secondary)
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Chỉ chủ sở hữu mới có thể điều khiển!", ephemeral=True)
            return
        
        # Update page và gọi lại command
        new_page = max(1, self.current_page - 1)
        await interaction.response.defer()
        
        # Gọi lại maid_collection với page mới
        cog = interaction.client.get_cog("MaidSystem")
        if cog:
            await cog.maid_collection.callback(cog, interaction, new_page)
    
    @discord.ui.button(label="▶️ Next", style=discord.ButtonStyle.secondary)  
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Chỉ chủ sở hữu mới có thể điều khiển!", ephemeral=True)
            return
        
        # Update page và gọi lại command
        new_page = min(self.total_pages, self.current_page + 1)
        await interaction.response.defer()
        
        # Gọi lại maid_collection với page mới
        cog = interaction.client.get_cog("MaidSystem")
        if cog:
            await cog.maid_collection.callback(cog, interaction, new_page)

class DismantleConfirmView(discord.ui.View):
    def __init__(self, user_id: int, maid: UserMaid, stardust_reward: int):
        super().__init__(timeout=300)
        self.user_id = user_id
        self.maid = maid
        self.stardust_reward = stardust_reward
    
    @discord.ui.button(label="✅ Xác Nhận", style=discord.ButtonStyle.danger)
    async def confirm_dismantle(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Chỉ chủ sở hữu mới có thể xác nhận!", ephemeral=True)
            return
        
        cog = interaction.client.get_cog("MaidSystem")
        if not cog:
            await interaction.response.send_message("❌ Lỗi hệ thống!", ephemeral=True)
            return
        
        # Xóa maid
        success = cog.maid_db.delete_maid(self.user_id, self.maid.instance_id)
        
        if success:
            # Thêm stardust
            stardust = cog.maid_db.get_user_stardust(self.user_id)
            stardust.add_stardust(self.stardust_reward)
            cog.maid_db.update_user_stardust(stardust)
            
            template = MAID_TEMPLATES[self.maid.maid_id]
            embed = EmbedBuilder.create_base_embed(
                title="💥 Dismantle Thành Công!",
                description=f"**{self.maid.custom_name or template['name']}** đã được tách thành {self.stardust_reward:,} bụi sao!",
                color=0x00FF00
            )
            
            await interaction.response.edit_message(embed=embed, view=None)
        else:
            await interaction.response.send_message("❌ Lỗi khi tách maid!", ephemeral=True)
    
    @discord.ui.button(label="❌ Hủy", style=discord.ButtonStyle.secondary)
    async def cancel_dismantle(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Chỉ chủ sở hữu mới có thể hủy!", ephemeral=True)
            return
        
        embed = EmbedBuilder.create_base_embed(
            title="❌ Đã Hủy",
            description="Hủy dismantle maid.",
            color=0x808080
        )
        await interaction.response.edit_message(embed=embed, view=None)

class RerollConfirmView(discord.ui.View):
    def __init__(self, user_id: int, maid: UserMaid, reroll_cost: int):
        super().__init__(timeout=300)
        self.user_id = user_id
        self.maid = maid
        self.reroll_cost = reroll_cost
    
    @discord.ui.button(label="🎲 Reroll", style=discord.ButtonStyle.primary)
    async def confirm_reroll(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Chỉ chủ sở hữu mới có thể reroll!", ephemeral=True)
            return
        
        cog = interaction.client.get_cog("MaidSystem")
        if not cog:
            await interaction.response.send_message("❌ Lỗi hệ thống!", ephemeral=True)
            return
        
        # Kiểm tra stardust lần nữa
        stardust = cog.maid_db.get_user_stardust(self.user_id)
        if not stardust.spend_stardust(self.reroll_cost):
            await interaction.response.send_message("❌ Không đủ bụi sao!", ephemeral=True)
            return
        
        # 🔄 Save old buffs for history
        old_buffs = self.maid.buff_values.copy()
        
        # Generate buffs mới
        new_buffs_data = generate_random_buffs(self.maid.maid_id)
        new_buffs = [MaidBuff.from_dict(buff) for buff in new_buffs_data]
        
        # Update buffs
        success = cog.maid_db.update_maid_buffs(self.user_id, self.maid.instance_id, new_buffs)
        
        if success:
            # Update stardust
            cog.maid_db.update_user_stardust(stardust)
            
            # 📝 Record reroll history for dynamic cost system
            reroll_history_manager.add_reroll_record(
                self.user_id, 
                self.maid.instance_id,
                old_buffs,
                new_buffs,
                self.reroll_cost
            )
            
            template = MAID_TEMPLATES[self.maid.maid_id]
            embed = EmbedBuilder.create_base_embed(
                title="🎲 Reroll Thành Công!",
                description=f"**{self.maid.custom_name or template['name']}** đã có buffs mới!",
                color=RARITY_CONFIG[template["rarity"]]["color"]
            )
            
            # Hiển thị buffs mới
            new_buffs_text = "\n".join([
                f"{BUFF_TYPES[buff.buff_type]['emoji']} {BUFF_TYPES[buff.buff_type]['name']}: +{buff.value}%"
                for buff in new_buffs
            ])
            
            embed.add_field(
                name="✨ Buffs Mới",
                value=new_buffs_text,
                inline=False
            )
            
            embed.add_field(
                name="💫 Stardust Còn Lại",
                value=f"{stardust.stardust_amount:,} bụi sao",
                inline=True
            )
            
            await interaction.response.edit_message(embed=embed, view=None)
        else:
            await interaction.response.send_message("❌ Lỗi khi reroll!", ephemeral=True)
    
    @discord.ui.button(label="❌ Hủy", style=discord.ButtonStyle.secondary)
    async def cancel_reroll(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Chỉ chủ sở hữu mới có thể hủy!", ephemeral=True)
            return
        
        embed = EmbedBuilder.create_base_embed(
            title="❌ Đã Hủy",
            description="Hủy reroll buffs.",
            color=0x808080
        )
        await interaction.response.edit_message(embed=embed, view=None)

async def setup(bot):
    await bot.add_cog(MaidSystem(bot)) 
