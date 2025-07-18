# Anime Waifu & Husbando Collector Bot

A Telegram bot that lets users collect anime characters through a gacha system with trading features.

## Features

- 🎰 **Gacha System**: Summon anime characters with coins
- 💰 **Economy**: Earn coins through daily rewards
- 📚 **Collection**: View and manage your character inventory
- 🔄 **Trading**: Trade characters with other players
- 📊 **Statistics**: Track your collection and progress
- 🎮 **Interactive UI**: Easy-to-use button interface

## How to Use

1. Start the bot with `/start`
2. Use `/menu` to access the main menu
3. Summon characters using your coins
4. Collect, trade, and build your collection!

## Commands

- `/start` - Register and get started
- `/menu` - Show main menu
- `/help` - Get help information

## Character Rarities

- 🟡 **Legendary** (1% chance) - Extremely rare and valuable
- 🟣 **Epic** (4% chance) - Very rare characters
- 🔵 **Rare** (15% chance) - Hard to find characters
- 🟢 **Uncommon** (30% chance) - Moderately rare
- ⚪ **Common** (50% chance) - Easy to obtain

## Project Structure

- `main.py` - Entry point
- `src/` - Source code directory
  - `main.py` - Main bot logic
  - `database.py` - Database operations
  - `gacha.py` - Character summoning
  - `trading.py` - Trading system
  - `utils.py` - UI helpers
  - `config.py` - Configuration
  - `characters.py` - Character data

## Requirements

- Python 3.11+
- python-telegram-bot 21.9
- SQLite3

## Setup

1. Get a bot token from @BotFather on Telegram
2. Set the `BOT_TOKEN` environment variable
3. Run `python main.py`

The bot will automatically:
- Initialize the database
- Populate character data
- Start polling for messages

## Database

The bot uses SQLite for data persistence with the following tables:
- `users` - User accounts and coins
- `characters` - Available anime characters
- `user_characters` - User inventory
- `trades` - Trading history
- `daily_rewards` - Daily reward tracking

## Contributing

Feel free to add more anime characters, improve the trading system, or enhance the UI!