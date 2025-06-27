#!/usr/bin/env python3
"""
💸 TRANSFER SYSTEM - Hệ thống chuyển tiền đơn giản
Cho phép người dùng give/transfer tiền cho nhau
"""

import discord
from discord.ext import commands
from datetime import datetime, timedelta
from typing import Dict, Optional
import logging

import config
from utils.embeds import EmbedBuilder
from utils.registration import registration_required

# Setup logger
logger = logging.getLogger('transfer')

class TransferCog(commands.Cog):
    """💸 Hệ thống chuyển tiền"""
    
    def __init__(self, bot):
        self.bot = bot
        # Cooldown tracking: user_id -> last_transfer_time
        self.transfer_cooldowns: Dict[int, datetime] = {}
        # Daily limits tracking: user_id -> (date, total_transferred)
        self.daily_limits: Dict[int, tuple] = {}
        
        logger.info("💸 Transfer System initialized")
    
    def _check_transfer_cooldown(self, user_id: int) -> Optional[float]:
        """Kiểm tra cooldown chuyển tiền (30 giây)"""
        if user_id not in self.transfer_cooldowns:
            return None
        
        elapsed = datetime.now() - self.transfer_cooldowns[user_id]
        cooldown_seconds = 30  # 30 giây cooldown
        
        if elapsed.total_seconds() < cooldown_seconds:
            return cooldown_seconds - elapsed.total_seconds()
        
        return None
    
    def _check_daily_limit(self, user_id: int, amount: int) -> tuple:
        """
        Theo dõi số tiền đã chuyển (không giới hạn)
        Returns: (can_transfer, current_transferred, daily_limit)
        """
        today = datetime.now().date()
        
        if user_id not in self.daily_limits:
            self.daily_limits[user_id] = (today, 0)
        
        last_date, transferred_today = self.daily_limits[user_id]
        
        # Reset if new day
        if last_date != today:
            transferred_today = 0
            self.daily_limits[user_id] = (today, 0)
        
        # Không giới hạn - luôn cho phép chuyển
        return True, transferred_today, 999999999
    
    def _update_daily_limit(self, user_id: int, amount: int):
        """Cập nhật số tiền đã chuyển hôm nay"""
        today = datetime.now().date()
        
        if user_id not in self.daily_limits:
            self.daily_limits[user_id] = (today, amount)
        else:
            _, transferred_today = self.daily_limits[user_id]
            self.daily_limits[user_id] = (today, transferred_today + amount)
    
    async def _find_user(self, ctx, user_input: str) -> Optional[discord.Member]:
        """Tìm user theo nhiều cách khác nhau"""
        if not user_input.strip():
            return None
        
        # Clean input - remove Discord mention formatting
        clean_input = user_input.replace('@', '').replace('<', '').replace('>', '').replace('!', '').strip()
        
        # Method 1: Try Discord's built-in converter
        try:
            converter = commands.MemberConverter()
            member = await converter.convert(ctx, user_input)
            if member and isinstance(member, discord.Member):
                return member
        except commands.MemberNotFound:
            pass
        except Exception:
            pass
        
        # Method 2: Try as user ID
        if clean_input.isdigit():
            try:
                user_id = int(clean_input)
                member = ctx.guild.get_member(user_id)
                if member and isinstance(member, discord.Member):
                    return member
            except ValueError:
                pass
        
        # Method 3: Search by display name or username (case-insensitive)
        for member in ctx.guild.members:
            if (member.display_name.lower() == clean_input.lower() or 
                member.name.lower() == clean_input.lower()):
                if isinstance(member, discord.Member):
                    return member
        
        # Method 4: Partial name search
        matches = []
        for member in ctx.guild.members:
            if (clean_input.lower() in member.display_name.lower() or 
                clean_input.lower() in member.name.lower()):
                matches.append(member)
        
        if len(matches) == 1:
            return matches[0]
        
        return None
    
    def _parse_amount(self, amount_str: str) -> Optional[int]:
        """Parse số tiền với hỗ trợ k, m"""
        try:
            amount_str = amount_str.lower().replace(',', '').replace('.', '')
            
            # Handle suffixes
            if amount_str.endswith('k'):
                amount = int(float(amount_str[:-1]) * 1000)
            elif amount_str.endswith('m'):
                amount = int(float(amount_str[:-1]) * 1000000)
            else:
                amount = int(amount_str)
            
            return amount if amount > 0 else None
                
        except (ValueError, TypeError):
            return None
    
    @commands.command(name='give', aliases=['transfer', 'send', 'pay'])
    @registration_required
    async def give_money(self, ctx, user_input: str = None, amount_str: str = None):
        """
        💸 Chuyển tiền cho người dùng khác
        
        Cách dùng: f!give @user <số_tiền>
        Ví dụ: f!give @Latina 1000
        
        Tính năng:
        • Không giới hạn số tiền
        • Cooldown: 30 giây
        • Hỗ trợ: 1k = 1,000, 1m = 1,000,000
        """
        try:
            # Check if arguments provided
            if not user_input or not amount_str:
                embed = discord.Embed(
                    title="💸 **CHUYỂN TIỀN**",
                    description=(
                        f"**Cách dùng:** `{config.PREFIX}give @user <số_tiền>`\n"
                        f"**Ví dụ:** `{config.PREFIX}give @Latina 1000`\n\n"
                        f"**Tính năng:**\n"
                        f"• Không giới hạn số tiền\n"
                        f"• Cooldown: 30 giây\n"
                        f"• Hỗ trợ: `1k` = 1,000, `1m` = 1,000,000\n\n"
                        f"💡 **Chuyển bao nhiêu cũng được!**"
                    ),
                    color=0x3498db
                )
                await ctx.send(embed=embed)
                return
            
            # Parse amount
            amount = self._parse_amount(amount_str)
            if amount is None:
                await ctx.send("❌ **Số tiền không hợp lệ!** Ví dụ: `1000`, `5k`, `1.5m`")
                return
            
            # Chỉ kiểm tra số tiền phải lớn hơn 0
            if amount <= 0:
                await ctx.send("❌ **Số tiền phải lớn hơn 0!**")
                return
            
            # Find target user
            target_user = await self._find_user(ctx, user_input)
            if not target_user:
                await ctx.send(f"❌ **Không tìm thấy user** `{user_input}`!\n"
                             f"💡 Thử: `{config.PREFIX}give @username 1000`")
                return
            
            # Security checks
            if target_user.id == ctx.author.id:
                await ctx.send("❌ **Không thể chuyển tiền cho chính mình!**")
                return
            
            if target_user.bot:
                await ctx.send("❌ **Không thể chuyển tiền cho bot!**")
                return
            
            # Check cooldown
            cooldown = self._check_transfer_cooldown(ctx.author.id)
            if cooldown:
                await ctx.send(f"⏰ **Đang cooldown!** Chờ `{cooldown:.1f}s` nữa.")
                return
            
            # Track daily transfers (không giới hạn)
            can_transfer, transferred_today, daily_limit = self._check_daily_limit(ctx.author.id, amount)
            
            # Check sender balance
            sender = await self.bot.db.get_user(ctx.author.id)
            if not sender:
                await ctx.send(f"❌ **Chưa đăng ký!** Dùng `{config.PREFIX}register`")
                return
            
            if sender.money < amount:
                await ctx.send(f"❌ **Không đủ tiền!**\n"
                             f"Số dư: `{sender.money:,}` coins\n"
                             f"Cần: `{amount:,}` coins")
                return
            
            # Check receiver registration
            receiver = await self.bot.db.get_user(target_user.id)
            if not receiver:
                await ctx.send(f"❌ **{target_user.display_name} chưa đăng ký!**\n"
                             f"Họ cần dùng `{config.PREFIX}register` trước.")
                return
            
            # Execute transfer
            sender_new_balance = await self.bot.db.update_user_money(ctx.author.id, -amount)
            receiver_new_balance = await self.bot.db.update_user_money(target_user.id, amount)
            
            # Update tracking
            self.transfer_cooldowns[ctx.author.id] = datetime.now()
            self._update_daily_limit(ctx.author.id, amount)
            
            # Log transaction
            logger.info(f"Transfer: {ctx.author.id} -> {target_user.id}, amount: {amount}")
            
            # Create success embed
            embed = discord.Embed(
                title="✅ **CHUYỂN TIỀN THÀNH CÔNG**",
                color=0x00ff00,
                timestamp=datetime.now()
            )
            
            embed.add_field(
                name="👤 **Người gửi**",
                value=f"{ctx.author.display_name}\n💰 Số dư: `{sender_new_balance:,}` coins",
                inline=True
            )
            
            embed.add_field(
                name="🎯 **Người nhận**",
                value=f"{target_user.display_name}\n💰 Số dư: `{receiver_new_balance:,}` coins",
                inline=True
            )
            
            embed.add_field(
                name="💰 **Số tiền**",
                value=f"`{amount:,}` coins",
                inline=False
            )
            
            # Daily transfer info (no limits)
            _, new_transferred_today, _ = self._check_daily_limit(ctx.author.id, 0)
            
            embed.add_field(
                name="📊 **Đã chuyển hôm nay**",
                value=f"Tổng cộng: `{new_transferred_today:,}` coins\n"
                      f"💡 Không giới hạn",
                inline=False
            )
            
            embed.set_footer(text=f"Transfer ID: {ctx.author.id}")
            
            await ctx.send(embed=embed)
            
            # Try to notify receiver via DM
            try:
                if target_user.status != discord.Status.offline:
                    notify_embed = discord.Embed(
                        title="💰 **BẠN NHẬN ĐƯỢC TIỀN!**",
                        description=f"**{ctx.author.display_name}** đã chuyển cho bạn `{amount:,}` coins!",
                        color=0xf1c40f
                    )
                    notify_embed.add_field(
                        name="💰 **Số dư mới**",
                        value=f"`{receiver_new_balance:,}` coins",
                        inline=False
                    )
                    
                    await target_user.send(embed=notify_embed)
            except:
                # Cannot send DM, ignore
                pass
            
        except Exception as e:
            logger.error(f"Transfer error: {e}")
            await ctx.send(f"❌ **Lỗi chuyển tiền:** {str(e)}")
    
    @commands.command(name='transfer_stats', aliases=['tstats'])
    @registration_required 
    async def transfer_stats(self, ctx):
        """
        📊 Xem thống kê chuyển tiền của bạn
        """
        try:
            user_id = ctx.author.id
            
            # Get daily transfer info (no limits)
            today = datetime.now().date()
            
            if user_id in self.daily_limits:
                last_date, transferred_today = self.daily_limits[user_id]
                if last_date != today:
                    transferred_today = 0
            else:
                transferred_today = 0
            
            # Check cooldown
            cooldown = self._check_transfer_cooldown(user_id)
            cooldown_text = f"⏰ {cooldown:.1f}s" if cooldown else "✅ Sẵn sàng"
            
            # Create embed
            embed = discord.Embed(
                title="📊 **THỐNG KÊ CHUYỂN TIỀN**",
                color=0x3498db,
                timestamp=datetime.now()
            )
            
            embed.add_field(
                name="📅 **Hôm nay**",
                value=f"Đã chuyển: `{transferred_today:,}` coins\n"
                      f"💡 Không giới hạn",
                inline=False
            )
            
            embed.add_field(
                name="⏰ **Trạng thái**",
                value=cooldown_text,
                inline=True
            )
            
            embed.add_field(
                name="📋 **Tính năng**",
                value="• Không giới hạn số tiền\n"
                      "• Cooldown: `30` giây\n"
                      "• Hỗ trợ: `1k`, `1m`\n"
                      "• Chuyển bao nhiêu cũng được! 🚀",
                inline=False
            )
            
            embed.set_footer(text=f"User ID: {user_id}")
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Transfer stats error: {e}")
            await ctx.send(f"❌ **Lỗi xem thống kê:** {str(e)}")

async def setup(bot):
    await bot.add_cog(TransferCog(bot)) 