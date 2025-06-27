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
logger = logging.getLogger('casino')

class Card:
    """Class đại diện cho một lá bài"""
    SUITS = ['♠️', '♥️', '♦️', '♣️']
    RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
    
    def __init__(self, suit: str, rank: str):
        self.suit = suit
        self.rank = rank
        self.emoji_key = f"{rank}_{suit}"
        logger.debug(f"Created card: {self.rank} of {self.suit}, emoji_key: {self.emoji_key}")
    
    def get_value(self, ace_high: bool = False) -> int:
        """Lấy giá trị của lá bài trong Blackjack"""
        if self.rank in ['J', 'Q', 'K']:
            return 10
        elif self.rank == 'A':
            return 11 if ace_high else 1
        else:
            return int(self.rank)
    
    def get_emoji(self, bot) -> str:
        """Lấy emoji của lá bài từ bot - Hỗ trợ cả Application và Guild emojis"""
        logger.debug(f"Getting emoji for key: {self.emoji_key}")
        emoji_id = config.CARD_EMOJIS.get(self.emoji_key)
        
        if emoji_id and isinstance(emoji_id, int) and emoji_id > 0:
            logger.debug(f"Found emoji ID: {emoji_id}")
            # Try to get emoji object from Discord
            try:
                emoji_obj = bot.get_emoji(emoji_id)
                if emoji_obj:
                    logger.debug(f"Successfully got emoji object: {emoji_obj}")
                    return str(emoji_obj)
                else:
                    # For Application emojis, they might not be in bot cache
                    # Format manually for cross-guild usage
                    logger.debug(f"Using manual format for Application emoji ID: {emoji_id}")
                    # Use generic emoji name since we don't know the actual name
                    return f"<:card:{emoji_id}>"
            except Exception as e:
                logger.error(f"Error getting emoji: {e}")
        elif emoji_id and isinstance(emoji_id, str):
            # Handle string emojis like "⬜"
            return emoji_id
        
        # Fallback to text representation with better formatting
        suit_symbols = {
            'spades': '♠️',
            'hearts': '♥️', 
            'diamonds': '♦️',
            'clubs': '♣️'
        }
        
        # Enhanced text fallback with better visual
        rank_display = self.rank
        if self.rank == '10':
            rank_display = 'T'  # Shorter for better display
        
        suit_symbol = suit_symbols.get(self.suit, self.suit)
        fallback = f"`{rank_display}{suit_symbol}`"
        logger.debug(f"Using fallback text: {fallback}")
        return fallback
    
    def __str__(self):
        return f"{self.rank} of {self.suit}"

class BlackjackHand:
    """Class đại diện cho tay bài trong Blackjack"""
    def __init__(self):
        self.cards: List[Card] = []
        
    def add_card(self, card: Card):
        """Thêm lá bài vào tay"""
        self.cards.append(card)
    
    def get_value(self) -> int:
        """Tính tổng giá trị tay bài"""
        total = 0
        aces = 0
        
        for card in self.cards:
            if card.rank == 'A':
                aces += 1
                total += 11
            else:
                total += card.get_value()
        
        # Xử lý Ace: Chuyển từ 11 -> 1 nếu cần
        while total > 21 and aces > 0:
            total -= 10
            aces -= 1
            
        return total
    
    def is_blackjack(self) -> bool:
        """Kiểm tra có phải blackjack không (21 với 2 lá đầu)"""
        return len(self.cards) == 2 and self.get_value() == 21
    
    def is_bust(self) -> bool:
        """Kiểm tra có bị bust không (> 21)"""
        return self.get_value() > 21
    
    def display_cards(self, bot, hide_first: bool = False) -> str:
        """Hiển thị các lá bài"""
        if not self.cards:
            return "Không có lá bài nào"
        
        card_display = []
        for i, card in enumerate(self.cards):
            if hide_first and i == 0:
                # Hiển thị mặt sau cho lá đầu tiên của dealer
                card_back_id = config.CARD_EMOJIS.get("card_back")
                if card_back_id and isinstance(card_back_id, int) and card_back_id > 0:
                    try:
                        emoji_obj = bot.get_emoji(card_back_id)
                        if emoji_obj:
                            card_display.append(str(emoji_obj))
                        else:
                            # For Application emojis
                            card_display.append(f"<:card_back:{card_back_id}>")
                    except Exception:
                        card_display.append("`[?]`")
                elif card_back_id and isinstance(card_back_id, str):
                    card_display.append(card_back_id)
                else:
                    card_display.append("`[?]`")
            else:
                card_display.append(card.get_emoji(bot))
        
        return " ".join(card_display)

class BlackjackGame:
    """Class chính cho game Blackjack"""
    def __init__(self, user_id: int, bet_amount: int):
        self.user_id = user_id
        self.bet_amount = bet_amount
        self.deck = self._create_deck()
        self.player_hand = BlackjackHand()
        self.dealer_hand = BlackjackHand()
        self.game_over = False
        self.player_won = False
        self.result_message = ""
        
        # Chia bài ban đầu
        self._deal_initial_cards()
    
    def _create_deck(self) -> List[Card]:
        """Tạo bộ bài 52 lá và xáo bài"""
        suits = ['spades', 'hearts', 'diamonds', 'clubs']
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        
        deck = []
        for suit in suits:
            for rank in ranks:
                deck.append(Card(suit, rank))
        
        random.shuffle(deck)
        return deck
    
    def _deal_initial_cards(self):
        """Chia 2 lá đầu cho player và dealer"""
        # Player gets 2 cards face up
        self.player_hand.add_card(self.deck.pop())
        self.player_hand.add_card(self.deck.pop())
        
        # Dealer gets 2 cards (1 face down, 1 face up)
        self.dealer_hand.add_card(self.deck.pop())
        self.dealer_hand.add_card(self.deck.pop())
    
    def hit(self) -> bool:
        """Player rút thêm bài"""
        if self.game_over:
            return False
            
        self.player_hand.add_card(self.deck.pop())
        
        if self.player_hand.is_bust():
            self.game_over = True
            self.player_won = False
            self.result_message = "🔥 **BUST!** Bạn đã vượt quá 21!"
            return False
        
        return True
    
    def stand(self):
        """Player dừng, dealer chơi theo luật"""
        if self.game_over:
            return
        
        # Dealer phải rút bài đến khi có ít nhất 17
        while self.dealer_hand.get_value() < 17:
            self.dealer_hand.add_card(self.deck.pop())
        
        self._determine_winner()
    
    def _determine_winner(self):
        """Xác định người thắng"""
        self.game_over = True
        
        player_value = self.player_hand.get_value()
        dealer_value = self.dealer_hand.get_value()
        
        # Kiểm tra blackjack
        player_blackjack = self.player_hand.is_blackjack()
        dealer_blackjack = self.dealer_hand.is_blackjack()
        
        if player_blackjack and dealer_blackjack:
            self.player_won = None  # Tie
            self.result_message = "🤝 **HOÀ!** Cả hai đều có Blackjack!"
        elif player_blackjack:
            self.player_won = True
            self.result_message = "🎉 **BLACKJACK!** Bạn thắng!"
        elif dealer_blackjack:
            self.player_won = False
            self.result_message = "😢 **Dealer Blackjack!** Bạn thua!"
        elif dealer_value > 21:
            self.player_won = True
            self.result_message = "🎉 **Dealer Bust!** Bạn thắng!"
        elif player_value > dealer_value:
            self.player_won = True
            self.result_message = "🎉 **Bạn thắng!** Tay bài cao hơn!"
        elif player_value < dealer_value:
            self.player_won = False
            self.result_message = "😢 **Bạn thua!** Dealer có tay bài cao hơn!"
        else:
            self.player_won = None  # Tie
            self.result_message = "🤝 **HOÀ!** Cùng điểm số!"
    
    def get_winnings(self) -> int:
        """Tính tiền thắng - CHỈ TRẢ VỀ TIỀN THẮNG THÊM, KHÔNG BAO GỒM TIỀN CƯỢC BAN ĐẦU"""
        if self.player_won is None:  # Tie
            return self.bet_amount  # Trả lại tiền cược (vì đã bị trừ ở đầu)
        elif self.player_won:
            if self.player_hand.is_blackjack():
                # Blackjack pays 3:2 - chỉ trả thêm 1.5x tiền cược + tiền cược gốc
                return self.bet_amount + int(self.bet_amount * config.CASINO_CONFIG["blackjack_payout"])
            else:
                # Normal win pays 1:1 - chỉ trả thêm 1x tiền cược + tiền cược gốc
                return self.bet_amount * 2  # bet_amount (gốc) + bet_amount (thắng)
        else:
            return 0  # Loss - không trả gì

class BlackjackView(discord.ui.View):
    """Discord UI View cho game Blackjack"""
    
    def __init__(self, bot, game: BlackjackGame):
        super().__init__(timeout=300)
        self.bot = bot
        self.game = game
        
        # Disable buttons if game is over
        if game.game_over:
            self._disable_all_buttons()
    
    def _disable_all_buttons(self):
        """Vô hiệu hóa tất cả buttons"""
        for item in self.children:
            item.disabled = True
    
    @discord.ui.button(label="🎯 Hit", style=discord.ButtonStyle.green)
    async def hit_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.game.user_id:
            await interaction.response.send_message("❌ Đây không phải game của bạn!", ephemeral=True)
            return
        
        if not self.game.hit():
            # Game over
            self._disable_all_buttons()
        
        embed = self._create_game_embed()
        await interaction.response.edit_message(embed=embed, view=self)
        
        # Pay out if game ended
        if self.game.game_over:
            await self._handle_game_end(interaction)
    
    @discord.ui.button(label="🛑 Stand", style=discord.ButtonStyle.red)
    async def stand_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.game.user_id:
            await interaction.response.send_message("❌ Đây không phải game của bạn!", ephemeral=True)
            return
        
        self.game.stand()
        self._disable_all_buttons()
        
        embed = self._create_game_embed()
        await interaction.response.edit_message(embed=embed, view=self)
        await self._handle_game_end(interaction)
    
    @discord.ui.button(label="🔄 Chơi lại", style=discord.ButtonStyle.grey)
    async def play_again_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.game.user_id:
            await interaction.response.send_message("❌ Đây không phải game của bạn!", ephemeral=True)
            return
        
        # Start new game with same bet
        casino_cog = self.bot.get_cog('CasinoCog')
        if casino_cog:
            await interaction.response.defer()
            await casino_cog.start_blackjack_game(interaction, self.game.bet_amount)
    
    def _create_game_embed(self) -> discord.Embed:
        """Tạo embed hiển thị trạng thái game"""
        embed = discord.Embed(
            title="🎰 **BLACKJACK CASINO**",
            color=0x2ecc71 if not self.game.game_over else (0xe74c3c if self.game.player_won is False else 0xf39c12),
            timestamp=datetime.now()
        )
        
        # Player hand
        player_cards = self.game.player_hand.display_cards(self.bot)
        player_value = self.game.player_hand.get_value()
        embed.add_field(
            name=f"🎮 **Tay bài của bạn** (Tổng: {player_value})",
            value=player_cards,
            inline=False
        )
        
        # Dealer hand
        if self.game.game_over:
            dealer_cards = self.game.dealer_hand.display_cards(self.bot)
            dealer_value = self.game.dealer_hand.get_value()
            embed.add_field(
                name=f"🏪 **Tay bài Dealer** (Tổng: {dealer_value})",
                value=dealer_cards,
                inline=False
            )
        else:
            dealer_cards = self.game.dealer_hand.display_cards(self.bot, hide_first=True)
            visible_value = self.game.dealer_hand.cards[1].get_value() if len(self.game.dealer_hand.cards) > 1 else 0
            embed.add_field(
                name=f"🏪 **Tay bài Dealer** (Hiện: {visible_value}+?)",
                value=dealer_cards,
                inline=False
            )
        
        # Game info
        embed.add_field(
            name="💰 **Tiền cược**",
            value=f"{self.game.bet_amount:,} coins",
            inline=True
        )
        
        if self.game.game_over:
            winnings = self.game.get_winnings()
            # Tính net change: winnings - bet_amount (vì tiền đã bị trừ ở đầu)
            net_change = winnings - self.game.bet_amount
            
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
        
        embed.set_footer(text="Farm Bot Casino | Chơi có trách nhiệm!")
        return embed
    
    async def _handle_game_end(self, interaction: discord.Interaction):
        """Xử lý khi game kết thúc - cập nhật tiền"""
        try:
            user = await self.bot.db.get_user(self.game.user_id)
            if user:
                winnings = self.game.get_winnings()
                
                # BUG FIX: update_user_money CỘNG THÊM amount, không phải set total
                # Vậy nên chỉ truyền winnings (số tiền cần cộng thêm), không phải user.money
                new_total = await self.bot.db.update_user_money(user.user_id, winnings)
                
                # Tính net change để log cho rõ ràng
                net_change = winnings - self.game.bet_amount
                logger.info(f"💰 Game end: User {self.game.user_id} bet {self.game.bet_amount}, won {winnings}, net_change: {net_change:+}, total money: {new_total}")
                
                # Update casino stats if exists
                # TODO: Implement casino stats tracking
                
        except Exception as e:
            logger.error(f"Error handling game end: {e}")
            print(f"Error handling game end: {e}")

class CasinoCog(commands.Cog):
    """Hệ thống Casino - Blackjack và các trò chơi khác"""
    
    def __init__(self, bot):
        self.bot = bot
        self.active_games: Dict[int, BlackjackGame] = {}
        self.last_played: Dict[int, datetime] = {}
        logger.info("🎰 Casino Cog initialized")
    
    def _check_cooldown(self, user_id: int) -> Optional[float]:
        """Kiểm tra cooldown giữa các game"""
        if user_id not in self.last_played:
            return None
        
        elapsed = datetime.now() - self.last_played[user_id]
        cooldown = config.CASINO_CONFIG["cooldown"]
        
        if elapsed.total_seconds() < cooldown:
            return cooldown - elapsed.total_seconds()
        
        return None
    
    @commands.command(name='blackjack', aliases=['bj'])
    @registration_required
    async def blackjack(self, ctx, bet_amount: int = None):
        """
        🎰 Chơi Blackjack tại Casino!
        
        Cách sử dụng: f!bj <tiền_cược>
        
        Luật chơi:
        - Mục tiêu: Đạt tổng điểm gần 21 nhất mà không vượt quá
        - A = 1 hoặc 11, J/Q/K = 10
        - Blackjack (21 với 2 lá đầu) trả 3:2
        - Thắng thường trả 1:1
        """
        logger.info(f"🎲 Blackjack command called by {ctx.author.id} with bet {bet_amount}")
        
        try:
            if bet_amount is None:
                embed = discord.Embed(
                    title="🎰 **BLACKJACK CASINO**",
                    description="Chơi Blackjack và thử vận may của bạn!",
                    color=0x3498db
                )
                embed.add_field(
                    name="📋 **Cách chơi**",
                    value=f"Sử dụng: `{config.PREFIX}bj <tiền_cược>`\n"
                          f"Ví dụ: `{config.PREFIX}bj 1000`",
                    inline=False
                )
                embed.add_field(
                    name="🎯 **Mục tiêu**",
                    value="Đạt tổng điểm gần 21 nhất mà không vượt quá",
                    inline=False
                )
                embed.add_field(
                    name="🃏 **Giá trị bài**",
                    value="• A = 1 hoặc 11\n• J, Q, K = 10\n• Các số = giá trị thực",
                    inline=True
                )
                embed.add_field(
                    name="💰 **Tỷ lệ trả**",
                    value="• Blackjack: 3:2\n• Thắng thường: 1:1\n• Hòa: Trả lại tiền cược",
                    inline=True
                )
                embed.add_field(
                    name="💸 **Giới hạn cược**",
                    value=f"Tối thiểu: {config.CASINO_CONFIG['min_bet']:,} coins\n"
                          f"Tối đa: {config.CASINO_CONFIG['max_bet']:,} coins",
                    inline=False
                )
                
                embed.set_footer(text="Chơi có trách nhiệm!")
                await ctx.send(embed=embed)
                logger.debug(f"❌ No bet amount provided by {ctx.author.id}")
                return
            
            # Ensure bet_amount is integer before passing
            try:
                bet_amount = int(bet_amount)
            except (ValueError, TypeError):
                embed = EmbedBuilder.create_error_embed(
                    "❌ Lỗi Input", 
                    "Số tiền cược phải là một số nguyên!"
                )
                await ctx.send(embed=embed)
                return
                
            await self.start_blackjack_game(ctx, bet_amount)
            
        except Exception as e:
            logger.error(f"❌ Error in blackjack command: {e}")
            import traceback
            traceback.print_exc()
            
            embed = EmbedBuilder.create_error_embed(
                "❌ Lỗi Casino",
                f"Có lỗi xảy ra khi chơi Blackjack: {str(e)}"
            )
            await ctx.send(embed=embed)
    
    async def start_blackjack_game(self, ctx_or_interaction, bet_amount: int):
        """Bắt đầu game Blackjack mới"""
        # Handle both ctx and interaction
        if hasattr(ctx_or_interaction, 'response'):
            # This is an interaction
            user = ctx_or_interaction.user
            send_func = ctx_or_interaction.followup.send
        else:
            # This is a context
            user = ctx_or_interaction.author
            send_func = ctx_or_interaction.send
        
        # Validation
        user_data = await self.bot.db.get_user(user.id)
        if not user_data:
            await send_func("❌ Bạn cần đăng ký tài khoản trước! Sử dụng `f!register`")
            return
        
        # Check cooldown
        cooldown_remaining = self._check_cooldown(user.id)
        if cooldown_remaining:
            await send_func(f"⏰ Bạn cần chờ {cooldown_remaining:.1f}s trước khi chơi tiếp!")
            return
        
        # Ensure bet_amount is integer
        try:
            bet_amount = int(bet_amount)
        except (ValueError, TypeError):
            await send_func("❌ Số tiền cược phải là một số nguyên!")
            return
        
        # Validate bet amount
        if bet_amount < config.CASINO_CONFIG["min_bet"]:
            await send_func(f"❌ Số tiền cược tối thiểu là {config.CASINO_CONFIG['min_bet']:,} coins!")
            return
        
        if bet_amount > config.CASINO_CONFIG["max_bet"]:
            await send_func(f"❌ Số tiền cược tối đa là {config.CASINO_CONFIG['max_bet']:,} coins!")
            return
        
        if bet_amount > user_data.money:
            await send_func(f"❌ Bạn không đủ tiền! Bạn có {user_data.money:,} coins.")
            return
        
        # Deduct bet amount immediately
        user_data.money -= bet_amount
        await self.bot.db.update_user_money(user.id, user_data.money)
        
        # Create new game
        game = BlackjackGame(user.id, bet_amount)
        self.active_games[user.id] = game
        self.last_played[user.id] = datetime.now()
        
        # Create view and embed
        view = BlackjackView(self.bot, game)
        embed = view._create_game_embed()
        
        await send_func(embed=embed, view=view)
        
        # Check for immediate blackjack
        if game.player_hand.is_blackjack():
            game.stand()  # Auto-stand on blackjack
            view._disable_all_buttons()
            
            # Update the message
            updated_embed = view._create_game_embed()
            if hasattr(ctx_or_interaction, 'response'):
                # For interactions, edit the followup message
                pass  # The message was already sent above
            else:
                # For regular context, edit the last message
                pass
            
            await view._handle_game_end(ctx_or_interaction if hasattr(ctx_or_interaction, 'response') else None)

    async def cog_load(self):
        """Called when the cog is loaded"""
        logger.info("🎰 Casino Cog loaded successfully")
    
    async def cog_unload(self):
        """Called when the cog is unloaded"""
        logger.info("🎰 Casino Cog unloaded")

async def setup(bot):
    """Setup function để load cog"""
    logger.info("🎰 Setting up Casino Cog...")
    try:
        await bot.add_cog(CasinoCog(bot))
        logger.info("✅ Casino Cog setup completed successfully")
    except Exception as e:
        logger.error(f"❌ Failed to setup Casino Cog: {e}")
        raise 