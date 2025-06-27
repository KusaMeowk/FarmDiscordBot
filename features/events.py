import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
import random
import asyncio
import config
from utils.embeds import EmbedBuilder
from utils.helpers import generate_seasonal_event
from utils.registration import registration_required
from utils.state_manager import StateManager

class EventsCog(commands.Cog):
    """Hệ thống sự kiện theo mùa và ngẫu nhiên"""
    
    def __init__(self, bot):
        self.bot = bot
        self.current_event = None
        self.event_end_time = None
        
        # State Manager cho persistence
        self.state_manager = None  # Sẽ được khởi tạo trong setup_hook
        
        # Track recent random events để tránh duplicate
        self.recent_random_events = []
        self.max_recent_events = 2  # Remember last 2 events
        
        self.check_events.start()
    
    async def setup_hook(self):
        """Khởi tạo StateManager và load state từ database"""
        try:
            # Khởi tạo StateManager
            self.state_manager = StateManager(self.bot.db)
            
            # Load event state từ database
            await self._load_event_state()
            
            print("✅ EventsCog state loaded successfully")
            
        except Exception as e:
            print(f"❌ Error loading EventsCog state: {e}")
    
    async def _load_event_state(self):
        """Load event state từ database"""
        try:
            event_state = await self.state_manager.load_event_state()
            
            if event_state and await self.state_manager.is_event_state_valid():
                # Restore state từ database
                self.current_event = event_state.get('current_event')
                self.event_end_time = event_state.get('event_end_time')
                
                print(f"🔄 Event state restored - Current event: {self.current_event['data']['name'] if self.current_event else 'None'}")
                
            else:
                print("🆕 No valid event state found, starting fresh")
                
        except Exception as e:
            print(f"❌ Error loading event state: {e}")
    
    async def _save_event_state(self):
        """Lưu event state vào database"""
        try:
            if self.state_manager:
                # Convert datetime objects to strings for JSON serialization
                current_event_copy = None
                if self.current_event:
                    current_event_copy = self.current_event.copy()
                    if current_event_copy.get('start_time'):
                        current_event_copy['start_time'] = current_event_copy['start_time'].isoformat()
                
                await self.state_manager.save_event_state(
                    current_event=current_event_copy,
                    event_end_time=self.event_end_time
                )
                
        except Exception as e:
            print(f"❌ Error saving event state: {e}")
    
    def cog_unload(self):
        """Clean up when cog is unloaded"""
        try:
            if hasattr(self, 'check_events') and not self.check_events.cancelled():
                self.check_events.cancel()
                print("🛑 Events check task cancelled")
        except Exception as e:
            print(f"Error cancelling events task: {e}")
        
        print("🧹 Events cleanup completed")
    
    @tasks.loop(hours=1)  # Check every hour
    async def check_events(self):
        """Kiểm tra và cập nhật sự kiện"""
        await self._check_seasonal_events()
        # Random events now managed by AI Event Manager
        await self._check_random_events()  # ✅ ENABLE Random Events
    
    @check_events.before_loop
    async def before_check_events(self):
        await self.bot.wait_until_ready()
    
    async def _check_seasonal_events(self):
        """Kiểm tra sự kiện theo mùa"""
        seasonal_event = generate_seasonal_event()
        
        if seasonal_event and not self.current_event:
            # Start seasonal event
            self.current_event = {
                'type': 'seasonal',
                'data': seasonal_event,
                'start_time': datetime.now()
            }
            
            # Set end time
            duration_days = seasonal_event.get('duration_days', 7)
            self.event_end_time = datetime.now() + timedelta(days=duration_days)
            
            # Save state
            await self._save_event_state()
            
            # Announce event (would need a announcement channel system)
            print(f"Seasonal event started: {seasonal_event['name']}")
    
    async def _check_random_events(self):
        """Kiểm tra sự kiện ngẫu nhiên"""
        if self.current_event:
            return  # Don't start random events during seasonal events
        
        # 100% chance every hour for random event (guaranteed)
        if True:  # Always start a random event when no other event is active
            # Positive events (buffs)
            positive_events = [
                {
                    'name': '🍀 Ngày may mắn',
                    'description': 'Hôm nay là ngày may mắn! Tất cả thu hoạch có sản lượng gấp đôi!',
                    'effect': 'double_yield',
                    'duration_hours': 6,
                    'type': 'buff'
                },
                {
                    'name': '⚡ Tăng tốc',
                    'description': 'Năng lượng đặc biệt! Cây trồng phát triển nhanh gấp đôi!',
                    'effect': 'double_growth',
                    'duration_hours': 4,
                    'type': 'buff'
                },
                {
                    'name': '💰 Thị trường sôi động',
                    'description': 'Giá nông sản tăng cao! Tất cả bán được giá gấp 1.5 lần!',
                    'effect': 'price_boost',
                    'duration_hours': 8,
                    'type': 'buff'
                },
                {
                    'name': '🌟 Hạt giống miễn phí',
                    'description': 'Chính phủ phát hạt giống miễn phí! Mua hạt giống giảm 50%!',
                    'effect': 'seed_discount',
                    'duration_hours': 12,
                    'type': 'buff'
                }
            ]
            
            # Negative events (debuffs)
            negative_events = [
                {
                    'name': '🌧️ Mưa acid',
                    'description': 'Mưa acid làm giảm năng suất! Thu hoạch chỉ được 50% sản lượng bình thường.',
                    'effect': 'yield_reduction',
                    'duration_hours': 8,
                    'type': 'debuff'
                },
                {
                    'name': '🐛 Dịch sâu bệnh',
                    'description': 'Sâu bệnh tấn công! Cây trồng phát triển chậm hơn 50%.',
                    'effect': 'growth_reduction',
                    'duration_hours': 10,
                    'type': 'debuff'
                },
                {
                    'name': '📉 Khủng hoảng kinh tế',
                    'description': 'Thị trường suy thoái! Giá bán nông sản giảm 30%.',
                    'effect': 'price_reduction',
                    'duration_hours': 6,
                    'type': 'debuff'
                },
                {
                    'name': '💸 Lạm phát hạt giống',
                    'description': 'Giá hạt giống tăng vọt! Mua hạt giống tốn gấp 2 lần tiền.',
                    'effect': 'seed_expensive',
                    'duration_hours': 12,
                    'type': 'debuff'
                }
            ]
            
            # Combine all events (70% buff, 30% debuff chance)
            random_events = positive_events + negative_events
            event_weights = [0.7] * len(positive_events) + [0.3] * len(negative_events)
            
            # Filter out recent events để tránh duplicate
            available_events = []
            available_weights = []
            
            for i, event in enumerate(random_events):
                if event['name'] not in self.recent_random_events:
                    available_events.append(event)
                    available_weights.append(event_weights[i])
            
            # Nếu đã dùng hết events, reset recent list
            if not available_events:
                self.recent_random_events.clear()
                available_events = random_events
                available_weights = event_weights
            
            # Weighted random selection (70% buff, 30% debuff)
            event = random.choices(available_events, weights=available_weights, k=1)[0]
            
            # Track event để tránh duplicate trong tương lai
            self.recent_random_events.append(event['name'])
            if len(self.recent_random_events) > self.max_recent_events:
                self.recent_random_events.pop(0)  # Remove oldest
            
            self.current_event = {
                'type': 'random',
                'data': event,
                'start_time': datetime.now()
            }
            
            duration_hours = event.get('duration_hours', 6)
            self.event_end_time = datetime.now() + timedelta(hours=duration_hours)
            
            # Save state
            await self._save_event_state()
            
            print(f"Random event started: {event['name']} (avoiding duplicates: {self.recent_random_events})")
    
    async def start_event(self, event_data: dict):
        """Start an AI-generated event
        
        Args:
            event_data: Event data from AI Event Manager
        """
        # Convert AI event format to EventsCog format
        ai_event = {
            'name': event_data['name'],
            'description': event_data['description'],
            'effect_type': event_data['effect_type'],
            'effect_value': event_data['effect_value'],
            'duration_hours': event_data.get('duration', 3600) // 3600,  # Convert seconds to hours
            'ai_generated': event_data.get('ai_generated', True),
            'ai_reasoning': event_data.get('ai_reasoning', 'AI-generated event'),
            'rarity': event_data.get('rarity', 'common')
        }
        
        # Set current event
        self.current_event = {
            'type': 'ai_generated',
            'data': ai_event,
            'start_time': datetime.now()
        }
        
        # Set end time
        duration_hours = ai_event.get('duration_hours', 4)
        self.event_end_time = datetime.now() + timedelta(hours=duration_hours)
        
        # Save state
        await self._save_event_state()
        
        print(f"AI Event started: {ai_event['name']} - {ai_event.get('ai_reasoning', '')}")
    
    def get_current_event_effects(self) -> dict:
        """Lấy hiệu ứng sự kiện hiện tại"""
        if not self.current_event or not self.event_end_time:
            return {}
        
        # Check if event has expired
        if datetime.now() > self.event_end_time:
            self.current_event = None
            self.event_end_time = None
            # Clear expired state
            asyncio.create_task(self._save_event_state())
            return {}
        
        event_data = self.current_event['data']
        effects = {}
        
        if self.current_event['type'] == 'seasonal':
            # Seasonal event effects
            effects.update({
                'growth_bonus': event_data.get('growth_bonus', 1.0),
                'yield_bonus': event_data.get('yield_bonus', 1.0),
                'price_bonus': event_data.get('price_bonus', 1.0),
                'daily_bonus': event_data.get('daily_bonus', 1.0)
            })
        
        elif self.current_event['type'] == 'random':
            # Random event effects
            effect_type = event_data.get('effect', '')
            
            # Positive effects (buffs)
            if effect_type == 'double_yield':
                effects['yield_bonus'] = 2.0
            elif effect_type == 'double_growth':
                effects['growth_bonus'] = 2.0
            elif effect_type == 'price_boost':
                effects['price_bonus'] = 1.5
            elif effect_type == 'seed_discount':
                effects['seed_discount'] = 0.5
            
            # Negative effects (debuffs)
            elif effect_type == 'yield_reduction':
                effects['yield_bonus'] = 0.5  # 50% yield
            elif effect_type == 'growth_reduction':
                effects['growth_bonus'] = 0.5  # 50% growth speed
            elif effect_type == 'price_reduction':
                effects['price_bonus'] = 0.7  # 70% price (30% reduction)
            elif effect_type == 'seed_expensive':
                effects['seed_cost_multiplier'] = 2.0  # 2x seed cost
        
        elif self.current_event['type'] == 'ai_generated':
            # AI-generated event effects
            effect_type = event_data.get('effect_type', '')
            effect_value = event_data.get('effect_value', 1.0)
            
            if effect_type == 'price_bonus':
                effects['price_bonus'] = effect_value
            elif effect_type == 'growth_bonus':
                effects['growth_bonus'] = effect_value
            elif effect_type == 'yield_bonus':
                effects['yield_bonus'] = effect_value
            elif effect_type == 'seed_cost_increase':
                effects['seed_cost_multiplier'] = effect_value
            elif effect_type == 'instant_growth':
                effects['instant_growth'] = True
            elif effect_type == 'free_seeds':
                effects['free_seeds'] = int(effect_value)
            elif effect_type == 'multi_bonus':
                # Multi-bonus events affect multiple areas
                effects['price_bonus'] = effect_value
                effects['yield_bonus'] = effect_value
        
        elif self.current_event['type'] == 'gemini_controlled':
            # Gemini-controlled event effects
            effect_type = event_data.get('effect_type', '')
            effect_value = event_data.get('effect_value', 1.0)
            
            # Gemini có thể control tất cả effect types
            if effect_type == 'price_bonus':
                effects['price_bonus'] = effect_value
            elif effect_type == 'growth_bonus':
                effects['growth_bonus'] = effect_value
            elif effect_type == 'yield_bonus':
                effects['yield_bonus'] = effect_value
            elif effect_type == 'seed_cost_reduction':
                effects['seed_discount'] = effect_value
            elif effect_type == 'seed_cost_increase':
                effects['seed_cost_multiplier'] = effect_value
            elif effect_type == 'daily_bonus':
                effects['daily_bonus'] = effect_value
            elif effect_type == 'instant_growth':
                effects['instant_growth'] = True
            elif effect_type == 'free_seeds':
                effects['free_seeds'] = int(effect_value)
            elif effect_type == 'multi_bonus':
                # Multi-bonus events từ Gemini
                effects['price_bonus'] = effect_value
                effects['yield_bonus'] = effect_value
                effects['growth_bonus'] = effect_value
        
        return effects
    
    def get_current_price_modifier(self) -> float:
        """Get current price modifier from active events"""
        effects = self.get_current_event_effects()
        return effects.get('price_bonus', 1.0)
    
    def get_current_yield_modifier(self) -> float:
        """Get current yield modifier from active events"""
        effects = self.get_current_event_effects()
        return effects.get('yield_bonus', 1.0)
    
    def get_current_growth_modifier(self) -> float:
        """Get current growth speed modifier from active events"""
        effects = self.get_current_event_effects()
        return effects.get('growth_bonus', 1.0)
    
    def get_current_seed_cost_modifier(self) -> float:
        """Get current seed cost modifier from active events"""
        effects = self.get_current_event_effects()
        seed_discount = effects.get('seed_discount', 1.0)
        seed_multiplier = effects.get('seed_cost_multiplier', 1.0)
        
        # Apply discount first, then multiplier
        if seed_discount < 1.0:
            return seed_discount
        else:
            return seed_multiplier
    
    @property
    def current_random_event(self):
        """Compatibility property for external access"""
        if self.current_event and self.current_event.get('type') == 'random':
            return self.current_event.get('data', {})
        return None
    
    @commands.command(name='event', aliases=['sukien'])
    async def event(self, ctx):
        """Xem sự kiện hiện tại
        
        Sử dụng: f!event
        """
        if not self.current_event:
            embed = EmbedBuilder.create_base_embed(
                "📅 Không có sự kiện",
                "Hiện tại không có sự kiện nào đang diễn ra.",
                color=0x95a5a6
            )
            
            embed.add_field(
                name="🔮 Sự kiện sắp tới",
                value="Sự kiện có thể xuất hiện bất cứ lúc nào!\nTiếp tục chơi để không bỏ lỡ!",
                inline=False
            )
        
        else:
            event_data = self.current_event['data']
            event_type = "🌸 Sự kiện theo mùa" if self.current_event['type'] == 'seasonal' else "⚡ Sự kiện đặc biệt"
            
            embed = EmbedBuilder.create_base_embed(
                f"{event_type}: {event_data['name']}",
                event_data['description'],
                color=0xe74c3c
            )
            
            # Time remaining
            time_remaining = self.event_end_time - datetime.now()
            hours = int(time_remaining.total_seconds() // 3600)
            minutes = int((time_remaining.total_seconds() % 3600) // 60)
            
            embed.add_field(
                name="⏰ Thời gian còn lại",
                value=f"{hours}h {minutes}p",
                inline=True
            )
            
            # Show effects
            effects = self.get_current_event_effects()
            effect_text = []
            
            for effect, value in effects.items():
                if effect == 'growth_bonus' and value != 1.0:
                    effect_text.append(f"⚡ Tốc độ sinh trưởng: {value:.1%}")
                elif effect == 'yield_bonus' and value != 1.0:
                    effect_text.append(f"🎯 Sản lượng: {value:.1%}")
                elif effect == 'price_bonus' and value != 1.0:
                    effect_text.append(f"💰 Giá bán: {value:.1%}")
                elif effect == 'daily_bonus' and value != 1.0:
                    effect_text.append(f"📅 Phần thưởng điểm danh: {value:.1%}")
                elif effect == 'seed_discount' and value != 1.0:
                    effect_text.append(f"🌱 Giảm giá hạt giống: {(1-value):.1%}")
                elif effect == 'seed_cost_multiplier' and value != 1.0:
                    if value > 1.0:
                        effect_text.append(f"🌱 Tăng giá hạt giống: {(value-1):.1%}")
                    else:
                        effect_text.append(f"🌱 Giảm giá hạt giống: {(1-value):.1%}")
            
            if effect_text:
                embed.add_field(
                    name="📈 Hiệu ứng",
                    value="\n".join(effect_text),
                    inline=False
                )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='events', aliases=['lichsu_sukien'])
    async def events_history(self, ctx):
        """Xem lịch sử các sự kiện có thể xảy ra
        
        Sử dụng: f!events
        """
        embed = EmbedBuilder.create_base_embed(
            "📚 Danh sách sự kiện",
            "Các sự kiện có thể xuất hiện trong game",
            color=0x9b59b6
        )
        
        # Seasonal events
        seasonal_events = [
            "🌸 **Lễ hội mùa xuân** (Tháng 3)\n• Cây trồng phát triển nhanh hơn 20%\n• Kéo dài 7 ngày",
            "☀️ **Mùa hè nắng nóng** (Tháng 6)\n• Sản lượng tăng 30%\n• Kéo dài 10 ngày",
            "🍂 **Mùa thu thu hoạch** (Tháng 9)\n• Giá bán tăng 15%\n• Kéo dài 14 ngày",
            "❄️ **Lễ hội mùa đông** (Tháng 12)\n• Phần thưởng điểm danh tăng 50%\n• Kéo dài 21 ngày"
        ]
        
        embed.add_field(
            name="🌍 Sự kiện theo mùa",
            value="\n\n".join(seasonal_events),
            inline=False
        )
        
        # Random events
        random_events = [
            "🍀 **Ngày may mắn**\n• Sản lượng gấp đôi\n• Kéo dài 6 giờ",
            "⚡ **Tăng tốc**\n• Phát triển gấp đôi\n• Kéo dài 4 giờ",
            "💰 **Thị trường sôi động**\n• Giá bán x1.5\n• Kéo dài 8 giờ",
            "🌟 **Hạt giống miễn phí**\n• Giảm 50% giá hạt\n• Kéo dài 12 giờ"
        ]
        
        embed.add_field(
            name="🎲 Sự kiện ngẫu nhiên",
            value="\n\n".join(random_events),
            inline=False
        )
        
        embed.add_field(
            name="📝 Lưu ý",
            value="• Sự kiện theo mùa tự động kích hoạt\n"
                  "• Sự kiện ngẫu nhiên có 5% cơ hội mỗi giờ\n"
                  "• Chỉ có 1 sự kiện tại một thời điểm",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='claim_event', aliases=['nhan_sukien'])
    @registration_required
    async def claim_event_reward(self, ctx):
        """Nhận phần thưởng đặc biệt từ sự kiện (nếu có)
        
        Sử dụng: f!claim_event
        """
        if not self.current_event:
            await ctx.send("❌ Hiện tại không có sự kiện nào!")
            return
        
        user = await self.bot.db.get_user(ctx.author.id)
        if not user:
            user = await self.bot.db.create_user(ctx.author.id, ctx.author.display_name)
        
        # Generate unique event ID for current event
        event_data = self.current_event['data']
        event_start_time = self.current_event['start_time'].strftime('%Y%m%d_%H%M')
        event_id = f"{self.current_event['type']}_{event_data['name']}_{event_start_time}"
        
        # Check if user already claimed this event
        has_claimed = await self.bot.db.has_claimed_event(ctx.author.id, event_id)
        if has_claimed:
            embed = EmbedBuilder.create_error_embed(
                f"Bạn đã nhận thưởng từ sự kiện **{event_data['name']}** rồi!\n"
                f"Mỗi người chỉ có thể nhận thưởng 1 lần cho mỗi sự kiện."
            )
            await ctx.send(embed=embed)
            return
        
        # Calculate reward based on event type
        reward = 200  # Base event participation reward
        
        if self.current_event['type'] == 'seasonal':
            reward = 500
        elif self.current_event['type'] == 'ai_generated':
            # AI events may have custom rewards
            if event_data.get('effect_type') == 'free_seeds':
                reward = 300
            elif event_data.get('rarity') == 'legendary':
                reward = 750
            elif event_data.get('rarity') == 'rare':
                reward = 400
        
        # Give reward
        user.money += reward
        await self.bot.db.update_user(user)
        
        # Record the claim to prevent double claiming
        await self.bot.db.record_event_claim(ctx.author.id, event_id)
        
        embed = EmbedBuilder.create_success_embed(
            "🎁 Nhận thưởng sự kiện!",
            f"Bạn đã nhận {reward} coins từ sự kiện **{event_data['name']}**!\n"
            f"💰 Số dư mới: {user.money:,} coins\n\n"
            f"📝 *Lưu ý: Mỗi sự kiện chỉ có thể nhận thưởng 1 lần*"
        )
        
        await ctx.send(embed=embed)

    @commands.command(name='event_stats', aliases=['thongke_sukien'])
    @commands.has_permissions(administrator=True)
    async def event_stats(self, ctx, user_id: int = None):
        """Xem thống kê về việc claim event rewards (Admin only)
        
        Sử dụng: f!event_stats [user_id]
        """
        if user_id:
            # Stats for specific user
            user = await self.bot.db.get_user(user_id)
            if not user:
                await ctx.send("❌ Không tìm thấy user!")
                return
            
            claimed_events = await self.bot.db.get_user_event_claims(user_id)
            
            embed = EmbedBuilder.create_base_embed(
                f"📊 Thống kê sự kiện - {user.username}",
                f"Tổng số sự kiện đã claim: {len(claimed_events)}",
                color=0x3498db
            )
            
            if claimed_events:
                recent_claims = claimed_events[-5:]  # Last 5 claims
                embed.add_field(
                    name="🎁 Sự kiện gần đây",
                    value="\n".join([f"• {event_id}" for event_id in recent_claims]),
                    inline=False
                )
        else:
            # General stats
            embed = EmbedBuilder.create_base_embed(
                "📊 Thống kê sự kiện hệ thống",
                "Thông tin về hệ thống sự kiện",
                color=0x3498db
            )
            
            # Current event info
            if self.current_event:
                event_data = self.current_event['data']
                embed.add_field(
                    name="🎪 Sự kiện hiện tại",
                    value=f"**{event_data['name']}**\n{event_data.get('description', 'Không có mô tả')}",
                    inline=False
                )
                
                # Time remaining
                if self.event_end_time:
                    time_remaining = self.event_end_time - datetime.now()
                    hours = int(time_remaining.total_seconds() // 3600)
                    minutes = int((time_remaining.total_seconds() % 3600) // 60)
                    
                    embed.add_field(
                        name="⏰ Thời gian còn lại",
                        value=f"{hours}h {minutes}p",
                        inline=True
                    )
            else:
                embed.add_field(
                    name="🎪 Sự kiện hiện tại",
                    value="Không có sự kiện nào đang diễn ra",
                    inline=False
        )
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(EventsCog(bot)) 