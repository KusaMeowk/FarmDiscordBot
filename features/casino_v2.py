#!/usr/bin/env python3
"""
🎰 CASINO BLACKJACK V2 - Được viết lại hoàn toàn
Logic đơn giản, rõ ràng, không còn bug

Key principles:
1. Trừ tiền trước khi chơi
2. Chỉ cộng tiền khi thắng/hòa
3. Logic tính toán minh bạch
4. Logging chi tiết để debug
"""

import discord
from discord.ext import commands
import random
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import config
from utils.embeds import EmbedBuilder
from utils.registration import registration_required
import logging

# Setup casino logger
logger = logging.getLogger('casino_v2')

class SimpleCard:
    """Class đơn giản cho lá bài"""
    def __init__(self, suit: str, rank: str):
        self.suit = suit  # spades, hearts, diamonds, clubs
        self.rank = rank  # A, 2-10, J, Q, K
    
    def get_value(self) -> int:
        """Lấy giá trị blackjack"""
        if self.rank in ['J', 'Q', 'K']:
            return 10
        elif self.rank == 'A':
            return 11  # Sẽ xử lý ace sau
        else:
            return int(self.rank)
    
    def __str__(self):
        suit_symbols = {
            'spades': '♠️', 'hearts': '♥️', 
            'diamonds': '♦️', 'clubs': '♣️'
        }
        return f"{self.rank}{suit_symbols.get(self.suit, self.suit)}"

class SimpleBlackjackGame:
    """Game Blackjack đơn giản với logic rõ ràng"""
    
    def __init__(self, user_id: int, bet_amount: int):
        self.user_id = user_id
        self.bet_amount = bet_amount
        self.player_cards = []
        self.dealer_cards = []
        self.game_over = False
        self.player_won = None  # None=ongoing, True=win, False=lose
        self.result_message = ""
        
        # Tạo deck và chia bài
        self._deal_initial_cards()
    
    def _create_deck(self) -> List[SimpleCard]:
        """Tạo bộ 52 lá bài"""
        suits = ['spades', 'hearts', 'diamonds', 'clubs']
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        deck = [SimpleCard(suit, rank) for suit in suits for rank in ranks]
        random.shuffle(deck)
        return deck
    
    def _deal_initial_cards(self):
        """Chia 2 lá ban đầu"""
        deck = self._create_deck()
        self.player_cards = [deck.pop(), deck.pop()]
        self.dealer_cards = [deck.pop(), deck.pop()]
        self.deck = deck
        
        # Kiểm tra blackjack ngay
        if self._get_hand_value(self.player_cards) == 21:
            self._finish_game()
    
    def _get_hand_value(self, cards: List[SimpleCard]) -> int:
        """Tính giá trị tay bài, xử lý Ace"""
        value = 0
        aces = 0
        
        for card in cards:
            if card.rank == 'A':
                aces += 1
                value += 11
            else:
                value += card.get_value()
        
        # Chuyển Ace từ 11 thành 1 nếu cần
        while value > 21 and aces > 0:
            value -= 10
            aces -= 1
        
        return value
    
    def hit(self) -> bool:
        """Player rút thêm bài"""
        if self.game_over:
            return False
        
        self.player_cards.append(self.deck.pop())
        
        if self._get_hand_value(self.player_cards) > 21:
            # Bust
            self.game_over = True
            self.player_won = False
            self.result_message = "💥 **BUST!** Bạn vượt quá 21!"
            return False
        
        return True
    
    def stand(self):
        """Player dừng, dealer chơi"""
        if self.game_over:
            return
        
        self._finish_game()
    
    def _finish_game(self):
        """Hoàn thành game và xác định người thắng"""
        self.game_over = True
        
        player_value = self._get_hand_value(self.player_cards)
        
        # Player blackjack
        if len(self.player_cards) == 2 and player_value == 21:
            dealer_value = self._get_hand_value(self.dealer_cards)
            if len(self.dealer_cards) == 2 and dealer_value == 21:
                self.player_won = None  # Cả hai blackjack = hòa
                self.result_message = "🤝 **HÒA!** Cả hai đều Blackjack!"
            else:
                self.player_won = True
                self.result_message = "🎉 **BLACKJACK!** Bạn thắng!"
            return
        
        # Player đã bust thì thua
        if player_value > 21:
            self.player_won = False
            self.result_message = "💥 **BUST!** Bạn vượt quá 21!"
            return
        
        # Dealer chơi
        while self._get_hand_value(self.dealer_cards) < 17:
            self.dealer_cards.append(self.deck.pop())
        
        dealer_value = self._get_hand_value(self.dealer_cards)
        
        # So sánh kết quả
        if dealer_value > 21:
            self.player_won = True
            self.result_message = "🎉 **THẮNG!** Dealer bị bust!"
        elif player_value > dealer_value:
            self.player_won = True
            self.result_message = "🎉 **THẮNG!** Điểm cao hơn dealer!"
        elif player_value < dealer_value:
            self.player_won = False
            self.result_message = "😔 **THUA!** Dealer điểm cao hơn!"
        else:
            self.player_won = None
            self.result_message = "🤝 **HÒA!** Cùng điểm số!"
    
    def get_cards_display(self, cards: List[SimpleCard], hide_first: bool = False) -> str:
        """Hiển thị các lá bài"""
        if hide_first and len(cards) > 0:
            return "🂠 " + " ".join(str(card) for card in cards[1:])
        return " ".join(str(card) for card in cards)
    
    def calculate_payout(self) -> int:
        """Tính toán số tiền user nhận được (TOTAL, không phải delta)"""
        if self.player_won is None:  # Hòa
            return self.bet_amount  # Trả lại tiền cược
        elif self.player_won:  # Thắng
            player_value = self._get_hand_value(self.player_cards)
            if len(self.player_cards) == 2 and player_value == 21:
                # Blackjack: 3:2 payout
                return self.bet_amount + int(self.bet_amount * 1.5)
            else:
                # Thắng thường: 1:1 payout
                return self.bet_amount * 2
        else:  # Thua
            return 0

class SimpleBlackjackView(discord.ui.View):
    """UI View đơn giản cho blackjack"""
    
    def __init__(self, game: SimpleBlackjackGame):
        super().__init__(timeout=300)
        self.game = game
        
        if game.game_over:
            self._disable_buttons()
    
    def _disable_buttons(self):
        """Vô hiệu hóa buttons"""
        for item in self.children:
            if hasattr(item, 'disabled'):
                item.disabled = True
    
    @discord.ui.button(label="🎯 Hit", style=discord.ButtonStyle.green)
    async def hit_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.game.user_id:
            await interaction.response.send_message("❌ Đây không phải game của bạn!", ephemeral=True)
            return
        
        still_playing = self.game.hit()
        
        if not still_playing:
            self._disable_buttons()
        
        embed = self._create_embed()
        await interaction.response.edit_message(embed=embed, view=self)
        
        if self.game.game_over:
            await self._handle_payout(interaction)
    
    @discord.ui.button(label="🛑 Stand", style=discord.ButtonStyle.red)
    async def stand_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.game.user_id:
            await interaction.response.send_message("❌ Đây không phải game của bạn!", ephemeral=True)
            return
        
        self.game.stand()
        self._disable_buttons()
        
        embed = self._create_embed()
        await interaction.response.edit_message(embed=embed, view=self)
        await self._handle_payout(interaction)
    
    def _create_embed(self) -> discord.Embed:
        """Tạo embed hiển thị game"""
        color = 0x2ecc71  # Xanh lá
        if self.game.game_over:
            if self.game.player_won is True:
                color = 0xf1c40f  # Vàng (thắng)
            elif self.game.player_won is False:
                color = 0xe74c3c  # Đỏ (thua)
            else:
                color = 0x95a5a6  # Xám (hòa)
        
        embed = discord.Embed(
            title="🎰 **BLACKJACK CASINO V2**",
            color=color,
            timestamp=datetime.now()
        )
        
        # Player hand
        player_value = self.game._get_hand_value(self.game.player_cards)
        embed.add_field(
            name=f"🎮 **Tay bài của bạn** (Tổng: {player_value})",
            value=self.game.get_cards_display(self.game.player_cards),
            inline=False
        )
        
        # Dealer hand
        if self.game.game_over:
            dealer_value = self.game._get_hand_value(self.game.dealer_cards)
            embed.add_field(
                name=f"🏪 **Tay bài Dealer** (Tổng: {dealer_value})",
                value=self.game.get_cards_display(self.game.dealer_cards),
                inline=False
            )
        else:
            visible_value = self.game.dealer_cards[1].get_value() if len(self.game.dealer_cards) > 1 else 0
            embed.add_field(
                name=f"🏪 **Tay bài Dealer** (Hiện: {visible_value}+?)",
                value=self.game.get_cards_display(self.game.dealer_cards, hide_first=True),
                inline=False
            )
        
        # Game info
        embed.add_field(
            name="💰 **Tiền cược**",
            value=f"{self.game.bet_amount:,} coins",
            inline=True
        )
        
        if self.game.game_over:
            payout = self.game.calculate_payout()
            net_change = payout - self.game.bet_amount
            
            embed.add_field(
                name="💸 **Kết quả**",
                value=f"{net_change:+,} coins",
                inline=True
            )
            
            embed.add_field(
                name="🎯 **Trạng thái**",
                value=self.game.result_message,
                inline=False
            )
        else:
            embed.add_field(
                name="🎯 **Hành động**",
                value="Chọn **Hit** để rút thêm bài hoặc **Stand** để dừng",
                inline=False
            )
        
        embed.set_footer(text="Farm Bot Casino V2 | Logic hoàn toàn mới!")
        return embed
    
    async def _handle_payout(self, interaction: discord.Interaction):
        """Xử lý chi trả đơn giản và rõ ràng"""
        try:
            # Lấy bot từ interaction
            bot = interaction.client
            
            # Tính payout
            payout = self.game.calculate_payout()
            
            # Cập nhật database - CHỈ CỘNG PAYOUT (không trừ bet vì đã trừ ở đầu)
            if payout > 0:
                await bot.db.update_user_money(self.game.user_id, payout)
                net_change = payout - self.game.bet_amount
                logger.info(f"💰 Casino V2 payout: User {self.game.user_id} bet {self.game.bet_amount}, payout {payout}, net {net_change:+}")
            else:
                # Thua - không cần làm gì vì tiền đã bị trừ ở đầu
                logger.info(f"💸 Casino V2 loss: User {self.game.user_id} bet {self.game.bet_amount}, lost all")
            
        except Exception as e:
            logger.error(f"❌ Error in casino V2 payout: {e}")

class CasinoV2Cog(commands.Cog):
    """Casino V2 với logic đơn giản"""
    
    def __init__(self, bot):
        self.bot = bot
        self.active_games: Dict[int, SimpleBlackjackGame] = {}
        self.cooldowns: Dict[int, datetime] = {}
        logger.info("🎰 Casino V2 Cog initialized")
    
    def _check_cooldown(self, user_id: int) -> Optional[float]:
        """Kiểm tra cooldown"""
        if user_id not in self.cooldowns:
            return None
        
        elapsed = datetime.now() - self.cooldowns[user_id]
        cooldown_seconds = float(config.CASINO_CONFIG.get("cooldown", 3))
        
        if elapsed.total_seconds() < cooldown_seconds:
            return cooldown_seconds - elapsed.total_seconds()
        
        return None
    
    @commands.command(name='casino2', aliases=['bj2'])
    @registration_required
    async def casino2(self, ctx, bet_amount: str = None):
        """
        🎰 Casino Blackjack V2 - Logic hoàn toàn mới!
        
        Cách dùng: f!casino2 <số_tiền>
        Ví dụ: f!casino2 1000
        """
        try:
            # Validation
            if bet_amount is None:
                embed = EmbedBuilder.create_info_embed(
                    "🎰 **CASINO BLACKJACK V2**",
                    f"Sử dụng: `{config.PREFIX}casino2 <tiền_cược>`\n"
                    f"Ví dụ: `{config.PREFIX}casino2 1000`\n\n"
                    f"**Luật chơi:**\n"
                    f"• Mục tiêu: Đạt 21 điểm hoặc gần nhất\n"
                    f"• A = 1 hoặc 11, J/Q/K = 10\n"
                    f"• Blackjack trả 3:2, thắng thường 1:1\n"
                    f"• Logic hoàn toàn mới, không còn bug!"
                )
                await ctx.send(embed=embed)
                return
            
            # Convert bet_amount to int safely
            try:
                bet_amount = int(bet_amount)
            except (ValueError, TypeError):
                await ctx.send("❌ Số tiền cược phải là số nguyên! Ví dụ: `f!casino2 1000`")
                return
            
            # Basic validation
            if bet_amount <= 0:
                await ctx.send("❌ Số tiền cược phải lớn hơn 0!")
                return
            
            # Kiểm tra cooldown
            cooldown = self._check_cooldown(ctx.author.id)
            if cooldown:
                await ctx.send(f"⏰ Chờ {cooldown:.1f}s trước khi chơi tiếp!")
                return
            
            # Validate bet với safe defaults
            try:
                min_bet = int(config.CASINO_CONFIG.get("min_bet", 100))
                max_bet = int(config.CASINO_CONFIG.get("max_bet", 100000))
            except (ValueError, TypeError):
                min_bet = 100
                max_bet = 100000
            
            if bet_amount < min_bet:
                await ctx.send(f"❌ Tối thiểu {min_bet:,} coins!")
                return
            
            if bet_amount > max_bet:
                await ctx.send(f"❌ Tối đa {max_bet:,} coins!")
                return
            
            # Kiểm tra tiền user
            user = await self.bot.db.get_user(ctx.author.id)
            if not user:
                await ctx.send("❌ Bạn cần đăng ký trước! Dùng `f!register`")
                return
            
            if user.money < bet_amount:
                await ctx.send(f"❌ Không đủ tiền! Bạn có {user.money:,} coins.")
                return
            
            # Trừ tiền trước (very important)
            new_balance = await self.bot.db.update_user_money(ctx.author.id, -bet_amount)
            logger.info(f"🎲 Casino V2 bet: User {ctx.author.id} bet {bet_amount}, balance: {new_balance}")
            
            # Tạo game mới
            game = SimpleBlackjackGame(ctx.author.id, bet_amount)
            self.active_games[ctx.author.id] = game
            self.cooldowns[ctx.author.id] = datetime.now()
            
            # Gửi game
            view = SimpleBlackjackView(game)
            embed = view._create_embed()
            
            await ctx.send(embed=embed, view=view)
            
            # Xử lý blackjack tự động
            if game.game_over:
                await view._handle_payout(ctx)
            
        except Exception as e:
            logger.error(f"❌ Casino V2 error: {e}")
            await ctx.send(f"❌ Lỗi casino V2: {str(e)}")

async def setup(bot):
    await bot.add_cog(CasinoV2Cog(bot)) 