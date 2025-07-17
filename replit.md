# Anime Waifu & Husbando Collector Bot

## Overview

This is a Telegram bot that implements an anime character collection game with a gacha system. Users can summon anime characters using coins, manage their collection, and trade with other players. The bot features a rarity-based character system with legendary, epic, rare, uncommon, and common characters from popular anime series.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Python-based Telegram bot** using the `python-telegram-bot` library
- **SQLite database** for data persistence with thread-safe operations
- **Modular design** with separate modules for different functionalities
- **Object-oriented approach** with dedicated classes for game systems

### Core Components
1. **Main Bot Handler** (`main.py`) - Handles Telegram interactions and command routing
2. **Database Layer** (`database.py`) - Manages all data operations with SQLite
3. **Gacha System** (`gacha.py`) - Implements the character summoning mechanics
4. **Trading System** (`trading.py`) - Handles player-to-player character trading
5. **Utilities** (`utils.py`) - Provides UI helpers and formatting functions
6. **Configuration** (`config.py`) - Centralizes all bot settings and constants
7. **Character Data** (`characters.py`) - Contains predefined anime character information

## Key Components

### Database Schema
- **Users Table**: Stores user profiles, coins, and activity tracking
- **Characters Table**: Contains all available anime characters with metadata
- **User Characters Table**: Tracks character ownership (user inventory)
- **Trades Table**: Manages trading transactions between users

### Gacha System
- **Weighted Random Selection**: Characters have different probabilities based on rarity
- **Rarity Tiers**: Common (50%), Uncommon (30%), Rare (15%), Epic (4%), Legendary (1%)
- **Economy System**: Uses coin-based currency with daily rewards and summon costs

### Trading System
- **Character Value Calculation**: Based on rarity multipliers
- **Trade Proposals**: Users can propose character exchanges
- **Trade Management**: Accept/reject functionality with database tracking

### User Interface
- **Inline Keyboards**: Interactive buttons for navigation and actions
- **Paginated Views**: Efficient display of large character collections
- **Rich Formatting**: Character cards with emojis and structured information

## Data Flow

1. **User Registration**: New users are automatically registered with initial coin balance
2. **Character Summoning**: Users spend coins → system selects random character by rarity → character added to user inventory
3. **Collection Management**: Users can view paginated inventory with character details
4. **Trading Process**: User A proposes trade → User B receives notification → Accept/reject → Database updates both inventories
5. **Daily Rewards**: Users claim daily coin bonuses with cooldown tracking

## External Dependencies

### Core Libraries
- `python-telegram-bot`: Telegram Bot API integration
- `sqlite3`: Database operations (Python standard library)
- `random`: Gacha probability calculations
- `threading`: Thread-safe database operations
- `datetime`: Time-based features (daily rewards, trade tracking)

### Character Assets
- **Image URLs**: Uses Pixabay links for character images
- **Character Database**: Predefined list of anime characters from popular series (Naruto, Attack on Titan, Demon Slayer, etc.)

## Deployment Strategy

### Environment Setup
- **Bot Token**: Required environment variable `BOT_TOKEN`
- **Database**: SQLite file (`anime_bot.db`) created automatically
- **Character Population**: Automatic initialization on first run

### Configuration Management
- **Centralized Settings**: All game parameters in `config.py`
- **Flexible Economy**: Adjustable coin rewards, summon costs, and rarity weights
- **Easy Character Management**: Simple addition of new characters to the predefined list

### Scalability Considerations
- **Thread-Safe Operations**: Database operations use threading locks
- **Modular Design**: Easy to extend with new features
- **Efficient Queries**: Optimized database operations for character lookups

### Current Limitations
- **Single Database File**: SQLite suitable for small to medium user bases
- **No User Authentication**: Relies on Telegram user IDs
- **Static Character Pool**: Characters are predefined rather than dynamically managed

The system is designed to be easily extensible, with clear separation of concerns and well-defined interfaces between components. The SQLite database provides simplicity for deployment while maintaining data integrity through proper transaction handling.