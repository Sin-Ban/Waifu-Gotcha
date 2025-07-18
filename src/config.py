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

# Rarity system with colored emojis
RARITY_COLORS = {
    "Common": "⚪",
    "Uncommon": "🟢", 
    "Rare": "🔵",
    "Epic": "🟣",
    "Legendary": "🟡"
}

# New rarity system with colored circle emojis
RARITY_LEVELS = {
    "Common": {"emoji": "⚪", "color": "White", "value": 1},
    "Uncommon": {"emoji": "🟢", "color": "Green", "value": 2},
    "Rare": {"emoji": "🔵", "color": "Blue", "value": 3},
    "Epic": {"emoji": "🟣", "color": "Purple", "value": 4},
    "Legendary": {"emoji": "🟡", "color": "Gold", "value": 5},
    "Mythical": {"emoji": "🔴", "color": "Red", "value": 6},
    "Divine": {"emoji": "⭐", "color": "Star", "value": 7}
}

# Valid rarity options for adding characters
VALID_RARITIES = list(RARITY_LEVELS.keys())

# Trading configuration
TRADE_TIMEOUT = 300  # 5 minutes for trade to be accepted/declined

# Character drop settings
DROP_TIMEOUT = 60  # 60 seconds to catch a character
CATCH_SIMILARITY_THRESHOLD = 0.8  # How similar the name needs to be
