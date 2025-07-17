import os

# Bot configuration
BOT_TOKEN = os.getenv("BOT_TOKEN", "your_bot_token_here")

# Database configuration
DATABASE_PATH = "anime_bot.db"

# Game configuration
INITIAL_COINS = 100
SUMMON_COST = 10
DAILY_REWARD = 50
MAX_TRADES_PER_DAY = 3

# Rarity system with weights (lower = rarer)
RARITY_WEIGHTS = {
    "Common": 50,
    "Uncommon": 30,
    "Rare": 15,
    "Epic": 4,
    "Legendary": 1
}

# Rarity colors for display
RARITY_COLORS = {
    "Common": "⚪",
    "Uncommon": "🟢", 
    "Rare": "🔵",
    "Epic": "🟣",
    "Legendary": "🟡"
}

# Character multipliers for trading value
RARITY_MULTIPLIERS = {
    "Common": 1,
    "Uncommon": 2,
    "Rare": 5,
    "Epic": 15,
    "Legendary": 50
}
