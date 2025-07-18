import os

# Bot configuration
BOT_TOKEN = os.getenv("BOT_TOKEN", "your_bot_token_here")

# Database configuration
DATABASE_PATH = "waifu_bot.db"

# Waifu/Husbando Bot Configuration
DEFAULT_WAIFU_LIMIT = 10  # Default messages before character drop
DEFAULT_GROUP_MODE = "waifu"  # Default group mode
CATCH_TIMEOUT = 30  # Seconds to catch a character before timeout

# Character drop settings
MIN_MESSAGES_FOR_DROP = 5
MAX_MESSAGES_FOR_DROP = 15

# Admin permissions
REQUIRED_ADMIN_PERMISSIONS = ['can_change_info', 'can_delete_messages', 'can_restrict_members']

# Character genders
VALID_GENDERS = ['waifu', 'husbando']

# Rarity system (for display purposes)
RARITY_COLORS = {
    "Common": "⚪",
    "Uncommon": "🟢", 
    "Rare": "🔵",
    "Epic": "🟣",
    "Legendary": "🟡"
}

# Trading configuration
TRADE_TIMEOUT = 300  # 5 minutes for trade to be accepted/declined
