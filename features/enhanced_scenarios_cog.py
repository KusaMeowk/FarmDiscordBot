#!/usr/bin/env python3
"""
Enhanced Scenarios Cog - Discord commands cho hệ thống Enhanced Economic Scenarios
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any

import discord
from discord.ext import commands, tasks

from ai.enhanced_economic_scenarios import EnhancedEconomicScenarios
from ai.hourly_scenario_updater import HourlyScenarioUpdater
from ai.smart_cache import SmartCache
from ai.gemini_economic_manager import GeminiEconomicManager
from utils.embeds import create_embed, Colors
from utils.enhanced_logging import get_bot_logger

logger = get_bot_logger()

class EnhancedScenariosCog(commands.Cog):
    """Cog quản lý Enhanced Economic Scenarios"""
    
    def __init__(self, bot):
        self.bot = bot
        self.scenario_generator = EnhancedEconomicScenarios()
        self.smart_cache = SmartCache()
        self.scenario_updater = None
        self.gemini_manager = None
        
        # Initialize task
        asyncio.create_task(self.initialize_systems())
        
        logger.info("📊 Enhanced Scenarios Cog loaded")
    
    async def initialize_systems(self):
        """Khởi tạo các hệ thống"""
        try:
            # Load smart cache
            await self.smart_cache.load_from_disk()
            logger.info(f"📂 Loaded {len(self.smart_cache.decisions)} cached scenarios")
            
            # Initialize Gemini Manager nếu có API key
            try:
                self.gemini_manager = GeminiEconomicManager(self.bot.db)
                logger.info("🤖 Gemini Economic Manager initialized")
            except Exception as e:
                logger.warning(f"⚠️ Gemini Manager not available: {e}")
            
            # Initialize Scenario Updater
            self.scenario_updater = HourlyScenarioUpdater(self.bot, self.gemini_manager)
            
            # Khởi động updater task
            await self.scenario_updater.start_updater()
            logger.info("⏰ Hourly Scenario Updater started")
            
        except Exception as e:
            logger.error(f"❌ Error initializing Enhanced Scenarios: {e}")
    
    @commands.group(name="scenarios", aliases=["scenario", "sc"])
    async def scenarios_group(self, ctx):
        """🎭 Enhanced Economic Scenarios management"""
        if ctx.invoked_subcommand is None:
            await self.show_scenarios_help(ctx)
    
    async def show_scenarios_help(self, ctx):
        """Hiển thị help cho scenarios commands"""
        embed = create_embed(
            title="🎭 Enhanced Economic Scenarios",
            description="Hệ thống quản lý tình huống kinh tế đa dạng",
            color=Colors.INFO
        )
        
        embed.add_field(
            name="📊 Thống kê",
            value="`f!scenarios stats` - Xem thống kê cache\n"
                  "`f!scenarios status` - Trạng thái hệ thống\n"
                  "`f!scenarios coverage` - Phạm vi bao phủ",
            inline=False
        )
        
        embed.add_field(
            name="🎯 Quản lý",
            value="`f!scenarios generate` - Tạo scenarios mới\n"
                  "`f!scenarios update` - Force update hourly\n"
                  "`f!scenarios cleanup` - Dọn dẹp cache cũ",
            inline=False
        )
        
        embed.add_field(
            name="🔍 Xem",
            value="`f!scenarios sample` - Xem scenarios mẫu\n"
                  "`f!scenarios search <pattern>` - Tìm kiếm\n"
                  "`f!scenarios current` - Scenarios hiện tại",
            inline=False
        )
        
        embed.add_field(
            name="⚙️ Cài đặt",
            value="`f!scenarios config` - Xem cấu hình\n"
                  "`f!scenarios interval <hours>` - Đặt tần suất\n"
                  "`f!scenarios toggle <system>` - Bật/tắt sync",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @scenarios_group.command(name="stats")
    async def scenarios_stats(self, ctx):
        """📊 Xem thống kê cache scenarios"""
        try:
            # Cache stats
            cache_stats = self.smart_cache.get_stats()
            
            # Scenario type distribution
            type_distribution = {}
            for pattern, data in self.smart_cache.decisions.items():
                scenario_type = data.get("scenario_type", "unknown")
                type_distribution[scenario_type] = type_distribution.get(scenario_type, 0) + 1
            
            embed = create_embed(
                title="📊 Enhanced Scenarios Statistics",
                description="Thống kê chi tiết về cache và scenarios",
                color=Colors.SUCCESS
            )
            
            # Cache performance
            embed.add_field(
                name="🎯 Cache Performance",
                value=f"**Hit Rate**: {cache_stats['hit_rate']}\n"
                      f"**Cache Hits**: {cache_stats['cache_hits']:,}\n"
                      f"**Cache Misses**: {cache_stats['cache_misses']:,}\n"
                      f"**Tokens Saved**: {cache_stats['tokens_saved']:,}\n"
                      f"**Cost Saved**: {cache_stats['cost_saved']}",
                inline=True
            )
            
            # Scenario counts
            total_scenarios = cache_stats['cached_decisions']
            embed.add_field(
                name="🎭 Scenarios Count",
                value=f"**Total**: {total_scenarios:,}\n"
                      f"**Active**: {len([d for d in self.smart_cache.decisions.values() if d.get('usage_count', 0) > 0])}\n"
                      f"**Unused**: {len([d for d in self.smart_cache.decisions.values() if d.get('usage_count', 0) == 0])}\n"
                      f"**Today**: {len([d for d in self.smart_cache.decisions.values() if datetime.fromisoformat(d.get('created_at', '2000-01-01')).date() == datetime.now().date()])}",
                inline=True
            )
            
            # Type distribution (top 6)
            sorted_types = sorted(type_distribution.items(), key=lambda x: x[1], reverse=True)[:6]
            type_text = "\n".join([f"**{t.title()}**: {count}" for t, count in sorted_types])
            embed.add_field(
                name="📈 Type Distribution",
                value=type_text or "Chưa có dữ liệu",
                inline=True
            )
            
            # Updater status
            if self.scenario_updater:
                status = self.scenario_updater.get_status()
                embed.add_field(
                    name="⏰ Hourly Updater",
                    value=f"**Running**: {'✅' if status['is_running'] else '❌'}\n"
                          f"**Updates**: {status['update_count']}\n"
                          f"**Last Update**: {status['last_update'][:16] if status['last_update'] else 'Never'}\n"
                          f"**Interval**: {status['update_interval_hours']}h",
                    inline=True
                )
            
            embed.set_footer(text=f"Cache updated: {datetime.now().strftime('%H:%M:%S')}")
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Lỗi khi lấy stats: {e}")
    
    @scenarios_group.command(name="status")
    async def scenarios_status(self, ctx):
        """📊 Trạng thái tổng quan của hệ thống"""
        try:
            embed = create_embed(
                title="🔄 Enhanced Scenarios System Status",
                description="Trạng thái các component trong hệ thống",
                color=Colors.INFO
            )
            
            # Core components
            components = []
            components.append(f"**Smart Cache**: {'✅ Active' if self.smart_cache else '❌ Error'}")
            components.append(f"**Scenario Generator**: {'✅ Ready' if self.scenario_generator else '❌ Error'}")
            components.append(f"**Hourly Updater**: {'✅ Running' if self.scenario_updater and self.scenario_updater.get_status()['is_running'] else '❌ Stopped'}")
            components.append(f"**Gemini Manager**: {'✅ Connected' if self.gemini_manager else '⚠️ Not Available'}")
            
            embed.add_field(
                name="🔧 Core Components",
                value="\n".join(components),
                inline=False
            )
            
            # Integration status
            if self.scenario_updater:
                integration = self.scenario_updater.integration_status
                integrations = []
                for system, status in integration.items():
                    status_icon = "✅" if status else "❌"
                    system_name = system.replace("_", " ").title()
                    integrations.append(f"**{system_name}**: {status_icon}")
                
                embed.add_field(
                    name="🔗 System Integration",
                    value="\n".join(integrations),
                    inline=True
                )
            
            # Performance metrics
            if hasattr(self.smart_cache, 'decisions'):
                perf_data = []
                total_scenarios = len(self.smart_cache.decisions)
                recent_scenarios = len([
                    d for d in self.smart_cache.decisions.values()
                    if datetime.fromisoformat(d.get('created_at', '2000-01-01')) > datetime.now() - timedelta(hours=24)
                ])
                
                perf_data.append(f"**Total Scenarios**: {total_scenarios:,}")
                perf_data.append(f"**Recent (24h)**: {recent_scenarios}")
                perf_data.append(f"**Cache Size**: {len(str(self.smart_cache.decisions)) / 1024:.1f}KB")
                
                embed.add_field(
                    name="📊 Performance",
                    value="\n".join(perf_data),
                    inline=True
                )
            
            embed.set_footer(text=f"System check: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Lỗi khi kiểm tra status: {e}")
    
    @scenarios_group.command(name="generate")
    @commands.has_permissions(administrator=True)
    async def scenarios_generate(self, ctx, count: int = 20):
        """🎯 Tạo scenarios mới (Admin only)"""
        if count > 100:
            await ctx.send("❌ Không thể tạo quá 100 scenarios cùng lúc")
            return
        
        try:
            # Tạo scenarios mới
            msg = await ctx.send("🔄 Đang tạo scenarios mới...")
            
            # Collect current game state
            game_state = await self.scenario_updater.collect_current_game_state() if self.scenario_updater else {}
            
            # Generate scenarios
            new_scenarios = await self.scenario_updater.generate_contextual_scenarios(game_state) if self.scenario_updater else {}
            
            # Limit scenarios
            limited_scenarios = dict(list(new_scenarios.items())[:count])
            
            # Update cache
            await self.scenario_updater.update_smart_cache(limited_scenarios) if self.scenario_updater else None
            
            # Update message
            embed = create_embed(
                title="✅ Scenarios Generated Successfully",
                description=f"Đã tạo {len(limited_scenarios)} scenarios mới",
                color=Colors.SUCCESS
            )
            
            # Scenario types
            type_counts = {}
            for data in limited_scenarios.values():
                scenario_type = data.get("scenario_type", "common")
                type_counts[scenario_type] = type_counts.get(scenario_type, 0) + 1
            
            if type_counts:
                type_text = "\n".join([f"**{t.title()}**: {count}" for t, count in type_counts.items()])
                embed.add_field(name="📊 Generated Types", value=type_text, inline=False)
            
            embed.add_field(
                name="🎮 Game State Context",
                value=f"**Economic Health**: {game_state.get('economic_health', 0):.2f}\n"
                      f"**Activity Rate**: {game_state.get('activity_rate', 0):.2f}\n"
                      f"**Season**: {game_state.get('season', 'unknown').title()}\n"
                      f"**Time Period**: {game_state.get('time_period', 'unknown').title()}",
                inline=True
            )
            
            await msg.edit(content="", embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Lỗi khi tạo scenarios: {e}")
    
    @scenarios_group.command(name="sample")
    async def scenarios_sample(self, ctx, scenario_type: str = None):
        """🔍 Xem scenarios mẫu"""
        try:
            # Filter by type if specified
            scenarios = self.smart_cache.decisions
            
            if scenario_type:
                scenarios = {
                    k: v for k, v in scenarios.items()
                    if v.get("scenario_type", "").lower() == scenario_type.lower()
                }
                
                if not scenarios:
                    await ctx.send(f"❌ Không tìm thấy scenarios loại `{scenario_type}`")
                    return
            
            # Get random samples
            import random
            sample_items = random.sample(list(scenarios.items()), min(5, len(scenarios)))
            
            for i, (pattern, data) in enumerate(sample_items):
                decision = data["decision"]
                metadata = data.get("scenario_metadata", {})
                
                embed = create_embed(
                    title=f"🎭 {metadata.get('name', 'Unknown Scenario')}",
                    description=metadata.get('description', 'No description'),
                    color=Colors.INFO
                )
                
                embed.add_field(
                    name="📊 Details",
                    value=f"**Pattern**: `{pattern[:50]}...`\n"
                          f"**Type**: {data.get('scenario_type', 'unknown')}\n"
                          f"**Frequency**: {metadata.get('frequency', 'unknown')}\n"
                          f"**Priority**: {decision.get('priority', 'medium')}",
                    inline=True
                )
                
                embed.add_field(
                    name="🎯 Action",
                    value=f"**Type**: {decision.get('action_type', 'Unknown')}\n"
                          f"**Confidence**: {decision.get('confidence', 0):.2f}\n"
                          f"**Usage**: {data.get('usage_count', 0)} times",
                    inline=True
                )
                
                reasoning = decision.get('reasoning', 'No reasoning provided')
                if len(reasoning) > 200:
                    reasoning = reasoning[:200] + "..."
                
                embed.add_field(
                    name="💭 Reasoning",
                    value=reasoning,
                    inline=False
                )
                
                embed.set_footer(text=f"Sample {i+1}/{len(sample_items)} • Created: {data.get('created_at', '')[:10]}")
                await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Lỗi khi lấy sample: {e}")
    
    @scenarios_group.command(name="update")
    @commands.has_permissions(administrator=True)
    async def scenarios_update(self, ctx):
        """🔄 Force update hourly scenarios (Admin only)"""
        try:
            if not self.scenario_updater:
                await ctx.send("❌ Scenario Updater chưa được khởi tạo")
                return
            
            msg = await ctx.send("🔄 Đang force update scenarios...")
            
            # Force manual update
            await self.scenario_updater.hourly_update_task()
            
            status = self.scenario_updater.get_status()
            
            embed = create_embed(
                title="✅ Scenarios Updated Successfully",
                description="Đã force update scenarios thành công",
                color=Colors.SUCCESS
            )
            
            embed.add_field(
                name="📊 Update Stats",
                value=f"**Update Count**: {status['update_count']}\n"
                      f"**Last Update**: {status['last_update'][:19] if status['last_update'] else 'Just now'}\n"
                      f"**Cache Size**: {len(self.smart_cache.decisions):,} scenarios",
                inline=False
            )
            
            await msg.edit(content="", embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Lỗi khi update scenarios: {e}")
    
    @scenarios_group.command(name="coverage")
    async def scenarios_coverage(self, ctx):
        """📈 Xem phạm vi bao phủ scenarios"""
        try:
            # Analyze coverage
            coverage_data = {
                "time_periods": {},
                "seasons": {},
                "weather_types": {},
                "scenario_types": {},
                "action_types": {}
            }
            
            for pattern, data in self.smart_cache.decisions.items():
                # Time periods
                for period in ["morning", "afternoon", "evening", "night"]:
                    if period in pattern:
                        coverage_data["time_periods"][period] = coverage_data["time_periods"].get(period, 0) + 1
                
                # Seasons
                for season in ["spring", "summer", "autumn", "winter"]:
                    if season in pattern:
                        coverage_data["seasons"][season] = coverage_data["seasons"].get(season, 0) + 1
                
                # Weather types
                for weather in ["sunny", "cloudy", "rainy", "stormy", "windy", "clear"]:
                    if weather in pattern:
                        coverage_data["weather_types"][weather] = coverage_data["weather_types"].get(weather, 0) + 1
                
                # Scenario types
                scenario_type = data.get("scenario_type", "unknown")
                coverage_data["scenario_types"][scenario_type] = coverage_data["scenario_types"].get(scenario_type, 0) + 1
                
                # Action types
                action_type = data["decision"].get("action_type", "unknown")
                coverage_data["action_types"][action_type] = coverage_data["action_types"].get(action_type, 0) + 1
            
            embed = create_embed(
                title="📈 Scenarios Coverage Analysis",
                description="Phân tích phạm vi bao phủ của scenarios",
                color=Colors.INFO
            )
            
            # Time periods
            if coverage_data["time_periods"]:
                time_text = "\n".join([f"**{t.title()}**: {count}" for t, count in coverage_data["time_periods"].items()])
                embed.add_field(name="🕒 Time Periods", value=time_text, inline=True)
            
            # Seasons
            if coverage_data["seasons"]:
                season_text = "\n".join([f"**{s.title()}**: {count}" for s, count in coverage_data["seasons"].items()])
                embed.add_field(name="🍃 Seasons", value=season_text, inline=True)
            
            # Weather types (top 6)
            if coverage_data["weather_types"]:
                sorted_weather = sorted(coverage_data["weather_types"].items(), key=lambda x: x[1], reverse=True)[:6]
                weather_text = "\n".join([f"**{w.title()}**: {count}" for w, count in sorted_weather])
                embed.add_field(name="🌤️ Weather Types", value=weather_text, inline=True)
            
            # Scenario types
            if coverage_data["scenario_types"]:
                sorted_types = sorted(coverage_data["scenario_types"].items(), key=lambda x: x[1], reverse=True)[:6]
                types_text = "\n".join([f"**{t.title()}**: {count}" for t, count in sorted_types])
                embed.add_field(name="🎭 Scenario Types", value=types_text, inline=True)
            
            # Action types (top 6)
            if coverage_data["action_types"]:
                sorted_actions = sorted(coverage_data["action_types"].items(), key=lambda x: x[1], reverse=True)[:6]
                actions_text = "\n".join([f"**{a}**: {count}" for a, count in sorted_actions])
                embed.add_field(name="⚡ Action Types", value=actions_text, inline=True)
            
            total_coverage = sum(sum(cat.values()) for cat in coverage_data.values())
            embed.add_field(
                name="📊 Summary",
                value=f"**Total Coverage Points**: {total_coverage:,}\n"
                      f"**Unique Patterns**: {len(self.smart_cache.decisions):,}\n"
                      f"**Coverage Score**: {min(100, total_coverage/50):.1f}%",
                inline=True
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Lỗi khi phân tích coverage: {e}")
    
    @scenarios_group.command(name="config")
    @commands.has_permissions(administrator=True)
    async def scenarios_config(self, ctx):
        """⚙️ Xem cấu hình hệ thống (Admin only)"""
        try:
            if not self.scenario_updater:
                await ctx.send("❌ Scenario Updater chưa được khởi tạo")
                return
            
            status = self.scenario_updater.get_status()
            
            embed = create_embed(
                title="⚙️ Enhanced Scenarios Configuration",
                description="Cấu hình hiện tại của hệ thống",
                color=Colors.INFO
            )
            
            # Updater settings
            embed.add_field(
                name="⏰ Updater Settings",
                value=f"**Update Interval**: {status['update_interval_hours']}h\n"
                      f"**Max Scenarios/Update**: {status['max_scenarios_per_update']}\n"
                      f"**Scenario Expiry**: {status['scenario_expiry_hours']}h\n"
                      f"**Is Running**: {'✅' if status['is_running'] else '❌'}",
                inline=True
            )
            
            # Integration settings
            integration = self.scenario_updater.integration_status
            integrations = []
            for system, enabled in integration.items():
                icon = "✅" if enabled else "❌"
                integrations.append(f"**{system.replace('_', ' ').title()}**: {icon}")
            
            embed.add_field(
                name="🔗 Integration Status",
                value="\n".join(integrations),
                inline=True
            )
            
            # Cache settings
            embed.add_field(
                name="💾 Cache Settings",
                value=f"**Cache Dir**: {self.smart_cache.cache_dir}\n"
                      f"**Cache File**: smart_cache.json\n"
                      f"**Auto Cleanup**: ✅ Enabled\n"
                      f"**Backup**: ✅ Auto backup",
                inline=True
            )
            
            embed.set_footer(text=f"Config checked: {datetime.now().strftime('%H:%M:%S')}")
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Lỗi khi xem config: {e}")
    
    @scenarios_group.command(name="cleanup")
    @commands.has_permissions(administrator=True)
    async def scenarios_cleanup(self, ctx):
        """🧹 Dọn dẹp cache scenarios cũ (Admin only)"""
        try:
            if not self.scenario_updater:
                await ctx.send("❌ Scenario Updater chưa được khởi tạo")
                return
            
            old_count = len(self.smart_cache.decisions)
            
            # Run cleanup
            await self.scenario_updater.cleanup_old_scenarios()
            
            new_count = len(self.smart_cache.decisions)
            cleaned = old_count - new_count
            
            embed = create_embed(
                title="🧹 Cache Cleanup Completed",
                description=f"Đã dọn dẹp {cleaned} scenarios cũ",
                color=Colors.SUCCESS if cleaned > 0 else Colors.INFO
            )
            
            embed.add_field(
                name="📊 Cleanup Stats",
                value=f"**Before**: {old_count:,} scenarios\n"
                      f"**After**: {new_count:,} scenarios\n"
                      f"**Cleaned**: {cleaned:,} scenarios\n"
                      f"**Retention**: {(new_count/old_count*100):.1f}%" if old_count > 0 else "N/A",
                inline=False
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Lỗi khi cleanup: {e}")
    
    async def cog_unload(self):
        """Cleanup khi unload cog"""
        if self.scenario_updater:
            self.scenario_updater.stop_updater()
        logger.info("📊 Enhanced Scenarios Cog unloaded")

async def setup(bot):
    """Setup function cho cog"""
    await bot.add_cog(EnhancedScenariosCog(bot))