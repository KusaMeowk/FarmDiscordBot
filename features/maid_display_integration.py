"""
Maid Display Integration
Tích hợp hiển thị maid buffs vào UI của farm/shop systems
"""
from features.maid_helper import maid_helper
from features.maid_config import BUFF_TYPES

class MaidDisplayIntegration:
    """Utility để hiển thị maid buffs trong game UI"""
    
    @staticmethod
    def get_farm_embed_footer(user_id: int) -> str:
        """
        Tạo footer cho farm embed hiển thị maid buffs
        
        Returns:
            String footer text hoặc empty nếu không có buffs
        """
        try:
            buff_summary = maid_helper.get_buff_summary_text(user_id)
            
            if buff_summary:
                return f"🎀 Maid Buffs: {buff_summary}"
            else:
                return "💤 Không có maid active - Dùng f!mequip để trang bị"
        except Exception:
            return ""
    
    @staticmethod
    def get_shop_embed_footer(user_id: int) -> str:
        """
        Tạo footer cho shop embed hiển thị seed discount
        
        Returns:
            String footer text hoặc empty nếu không có discount
        """
        try:
            buffs = maid_helper.get_user_maid_buffs(user_id)
            seed_discount = buffs.get("seed_discount", 0.0)
            
            if seed_discount > 0:
                return f"💰 Maid Discount: -{seed_discount}% giá hạt giống"
            else:
                return ""
        except Exception:
            # Return empty if there's any error to avoid breaking shop
            return ""
    
    @staticmethod
    def get_harvest_embed_footer(user_id: int) -> str:
        """
        Tạo footer cho harvest embed hiển thị yield boost
        
        Returns:
            String footer text hoặc empty nếu không có boost  
        """
        try:
            buffs = maid_helper.get_user_maid_buffs(user_id)
            yield_boost = buffs.get("yield_boost", 0.0)
            
            if yield_boost > 0:
                return f"📈 Maid Bonus: +{yield_boost}% sản lượng"
            else:
                return ""
        except Exception:
            return ""
    
    @staticmethod
    def get_sell_embed_footer(user_id: int) -> str:
        """
        Tạo footer cho sell embed hiển thị price boost
        
        Returns:
            String footer text hoặc empty nếu không có boost
        """
        try:
            buffs = maid_helper.get_user_maid_buffs(user_id)
            sell_price = buffs.get("sell_price", 0.0)
            
            if sell_price > 0:
                return f"💎 Maid Bonus: +{sell_price}% giá bán"
            else:
                return ""
        except Exception:
            return ""
    
    @staticmethod
    def get_plant_time_display(user_id: int, base_time: int) -> str:
        """
        Hiển thị thời gian trồng cây với và không có buff
        
        Args:
            user_id: ID của user
            base_time: Thời gian gốc (seconds)
            
        Returns:
            String hiển thị time comparison
        """
        buffed_time = maid_helper.apply_growth_speed_buff(user_id, base_time)
        
        if buffed_time < base_time:
            time_saved = base_time - buffed_time
            saved_minutes = time_saved // 60
            
            base_minutes = base_time // 60
            buffed_minutes = buffed_time // 60
            
            return f"⏱️ {buffed_minutes}m (tiết kiệm {saved_minutes}m từ {base_minutes}m)"
        else:
            minutes = base_time // 60
            return f"⏱️ {minutes}m"
    
    @staticmethod
    def format_maid_active_indicator(user_id: int) -> str:
        """
        Tạo indicator ngắn gọn về maid active status
        
        Returns:
            Emoji indicator + short description
        """
        active_maid_info = maid_helper.get_active_maid_info(user_id)
        
        if active_maid_info:
            name = active_maid_info["name"]
            emoji = active_maid_info["emoji"]
            rarity = active_maid_info["rarity"]
            
            from features.maid_config import RARITY_EMOJIS
            rarity_emoji = RARITY_EMOJIS.get(rarity, "")
            
            return f"🎀 {rarity_emoji}{emoji} {name} active"
        else:
            return "💤 Không có maid active"
    
    @staticmethod
    def get_detailed_buff_breakdown(user_id: int) -> str:
        """
        Tạo breakdown chi tiết về tất cả buffs hiện tại
        
        Returns:
            Multi-line string với chi tiết buffs
        """
        active_maid_info = maid_helper.get_active_maid_info(user_id)
        
        if not active_maid_info:
            return "💤 **Không có maid active**\nDùng `/maid_equip <id>` để trang bị maid"
        
        lines = [
            f"🎀 **{active_maid_info['emoji']} {active_maid_info['name']}** ({active_maid_info['rarity']})",
            "**Active Buffs:**"
        ]
        
        if active_maid_info["buffs"]:
            for buff in active_maid_info["buffs"]:
                buff_type = buff["type"]
                value = buff["value"]
                
                if buff_type in BUFF_TYPES:
                    emoji = BUFF_TYPES[buff_type]["emoji"]
                    name = BUFF_TYPES[buff_type]["name"]
                    lines.append(f"├─ {emoji} {name}: **+{value}%**")
        else:
            lines.append("├─ Không có buffs")
        
        return "\n".join(lines)

# Global instance
maid_display = MaidDisplayIntegration()

# Export convenience functions
def add_maid_buffs_to_embed(embed, user_id: int, context: str):
    """
    Thêm maid buffs vào Discord embed
    
    Args:
        embed: Discord.Embed object
        user_id: ID của user
        context: Context type ("farm", "shop", "harvest", "sell")
    
    Returns:
        Modified embed with maid info
    """
    if context == "farm":
        footer_text = maid_display.get_farm_embed_footer(user_id)
        if footer_text:
            embed.set_footer(text=footer_text)
    elif context == "shop":
        footer_text = maid_display.get_shop_embed_footer(user_id)
        if footer_text:
            embed.set_footer(text=footer_text)
    elif context == "harvest":
        footer_text = maid_display.get_harvest_embed_footer(user_id)
        if footer_text:
            embed.set_footer(text=footer_text)
    elif context == "sell":
        footer_text = maid_display.get_sell_embed_footer(user_id)
        if footer_text:
            embed.set_footer(text=footer_text)
    
    return embed

def format_active_maid_buffs(user_id: int) -> str:
    """Export function for getting detailed buff breakdown"""
    return maid_display.get_detailed_buff_breakdown(user_id)

def format_maid_icon(maid_name: str) -> str:
    """Export function for formatting maid icon"""
    return f"🎀 {maid_name}" 