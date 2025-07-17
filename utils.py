from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config import RARITY_COLORS

def create_main_menu():
    """Create the main menu keyboard"""
    keyboard = [
        [InlineKeyboardButton("🎰 Summon (10 coins)", callback_data="summon")],
        [InlineKeyboardButton("🎊 Multi-Summon (50 coins)", callback_data="multi_summon")],
        [InlineKeyboardButton("📦 My Collection", callback_data="inventory")],
        [InlineKeyboardButton("📊 Statistics", callback_data="stats")],
        [InlineKeyboardButton("🎁 Daily Reward", callback_data="daily_reward")],
        [InlineKeyboardButton("🔄 Trading", callback_data="trading_menu")],
        [InlineKeyboardButton("❓ Help", callback_data="help")]
    ]
    return InlineKeyboardMarkup(keyboard)

def create_inventory_navigation(page, total_pages):
    """Create navigation buttons for inventory"""
    keyboard = []
    
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"inventory_page_{page-1}"))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("➡️ Next", callback_data=f"inventory_page_{page+1}"))
    
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    keyboard.append([InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")])
    
    return InlineKeyboardMarkup(keyboard)

def create_trading_menu():
    """Create trading menu keyboard"""
    keyboard = [
        [InlineKeyboardButton("📋 Pending Trades", callback_data="pending_trades")],
        [InlineKeyboardButton("📚 Trade History", callback_data="trade_history")],
        [InlineKeyboardButton("❓ How to Trade", callback_data="trade_help")],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def create_trade_action_buttons(trade_id):
    """Create buttons for trade actions"""
    keyboard = [
        [InlineKeyboardButton("✅ Accept", callback_data=f"accept_trade_{trade_id}")],
        [InlineKeyboardButton("❌ Reject", callback_data=f"reject_trade_{trade_id}")],
        [InlineKeyboardButton("🔙 Back", callback_data="pending_trades")]
    ]
    return InlineKeyboardMarkup(keyboard)

def format_character_card(character, show_obtained=False):
    """Format character information as a card"""
    rarity_icon = RARITY_COLORS.get(character['rarity'], "⚪")
    
    card = f"""
{rarity_icon} **{character['name']}** {rarity_icon}
📺 **Anime:** {character['anime']}
⭐ **Rarity:** {character['rarity']}
💭 **Description:** {character['description']}
{'♀️' if character['type'] == 'waifu' else '♂️'} **Type:** {character['type'].title()}
"""
    
    if show_obtained and 'obtained_at' in character:
        card += f"🕒 **Obtained:** {character['obtained_at'][:10]}"
    
    return card

def format_trade_info(trade):
    """Format trade information"""
    from_icon = RARITY_COLORS.get(trade['from_char_rarity'], "⚪")
    to_icon = RARITY_COLORS.get(trade['to_char_rarity'], "⚪")
    
    return f"""
**Trade #{trade['id']}**
👤 **From:** {trade['from_user_name']}
{from_icon} **Offering:** {trade['from_char_name']} ({trade['from_char_rarity']})

👤 **To:** {trade['to_user_name']}  
{to_icon} **Wants:** {trade['to_char_name']} ({trade['to_char_rarity']})

⏰ **Created:** {trade['created_at'][:16]}
"""

def paginate_list(items, page, per_page=5):
    """Paginate a list of items"""
    start = page * per_page
    end = start + per_page
    return items[start:end]

def get_help_text():
    """Get help text for the bot"""
    return """
🎮 **ANIME WAIFU & HUSBANDO COLLECTOR** 🎮

**Commands:**
/start - Start the bot and register
/menu - Show main menu
/help - Show this help message

**How to Play:**
🎰 **Summoning:** Use coins to summon random characters
💰 **Coins:** Earn coins through daily rewards
⭐ **Rarity:** Characters have different rarities (Common to Legendary)
📦 **Collection:** View your character inventory
🔄 **Trading:** Trade characters with other users

**Rarity Levels:**
⚪ Common - Easy to get
🟢 Uncommon - Somewhat rare
🔵 Rare - Hard to get
🟣 Epic - Very rare
🟡 Legendary - Extremely rare

**Daily Rewards:**
🎁 Claim 50 coins every 24 hours!

**Trading:**
To trade, both users must have the bot started and characters in their collection.
Trading is based on mutual agreement between users.

Have fun collecting your favorite anime characters! 🌟
"""

def get_character_emoji(character_type):
    """Get emoji for character type"""
    return "♀️" if character_type == "waifu" else "♂️"

def format_coins(amount):
    """Format coin amount with emoji"""
    return f"💰 {amount} coins"

def format_rarity_with_icon(rarity):
    """Format rarity with appropriate icon"""
    icon = RARITY_COLORS.get(rarity, "⚪")
    return f"{icon} {rarity}"
