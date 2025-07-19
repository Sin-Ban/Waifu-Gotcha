# Waifu/Husbando Collector Bot

## Overview

This is an advanced Telegram bot that implements a group-based anime character collection game with waifu/husbando mechanics. Users can collect characters that drop in groups, claim them with /catch commands, and trade with other players. The bot features group-specific modes (waifu/husbando), configurable drop rates, and a comprehensive trading system with inline UI.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Python-based Telegram bot** using the `python-telegram-bot` library (version 21.9)
- **SQLite database** for data persistence with thread-safe operations
- **Modular design** with separate modules in `src/` folder
- **Group-based collection system** with configurable drop mechanics
- **OuraDB-style character database** format

### Project Structure
```
root/
├── main.py              # Entry point that imports from src/
├── src/                 # Source code folder
│   ├── main.py         # Main bot handler with all commands
│   ├── database.py     # Database layer and operations
│   ├── config.py       # Bot configuration and settings
│   └── characters.py   # Predefined character data
├── waifu_bot.db        # SQLite database file
└── replit.md           # Project documentation
```

### Core Components
1. **Main Bot Handler** (`src/main.py`) - Handles Telegram interactions and command routing
2. **Database Layer** (`src/database.py`) - Manages all data operations with SQLite
3. **Configuration** (`src/config.py`) - Centralizes all bot settings and constants
4. **Character Data** (`src/characters.py`) - Contains predefined anime character information

## Key Components

### Database Schema
- **Groups Table**: Stores group settings, modes, and drop configurations
- **Characters Table**: Contains all available anime characters with OuraDB format
- **User Collections Table**: Tracks character ownership per user
- **Trades Table**: Manages trading transactions between users
- **Active Drops Table**: Tracks characters currently available for catching

### Group-Based System
- **Group Modes**: Configurable waifu/husbando modes per group
- **Drop Mechanics**: Message-based character drops with configurable limits
- **Admin Controls**: Group admins can configure modes and drop rates
- **Character Claiming**: Users claim characters with /catch command

### Trading System
- **Character Trading**: Users can trade characters with each other
- **Trade Proposals**: Interactive inline buttons for accepting/declining trades
- **Trade Management**: Database tracking of trade status and completion

### User Interface
- **Inline Keyboards**: Interactive buttons for mode switching and navigation
- **Paginated Views**: Efficient display of large character collections
- **Rich Formatting**: Character cards with emojis and structured information
- **Group Integration**: Commands work seamlessly in group environments

## Data Flow

1. **Group Registration**: Groups are automatically registered when bot is added
2. **Character Drops**: After configured message count, random character drops
3. **Character Claiming**: Users use /catch to claim dropped characters
4. **Collection Management**: Users can view their collections with paginated display
5. **Trading Process**: Users propose trades using character IDs and usernames

## Bot Commands

### Admin Commands (Group Admins Only)
- `/setmode <waifu/husbando>` - Set group mode
- `/setwaifulimit <number>` - Set message limit for drops

### User Commands
- `/start` - Initialize bot and show welcome message
- `/addchar <name> | <series> | <waifu/husbando>` - Add new character
- `/catch` - Catch a dropped character
- `/mycollection` - View personal collection
- `/search <query>` - Search for characters
- `/trade <char_id> @user` - Trade character with another user

## Recent Changes (July 2025)

### Owner Management System (July 18, 2025)
- **Owner-Only Commands**: Complete management system for special users and bans
- **Special User System**: Database-driven special user management with `/addspecial`, `/removespecial`, `/listspecial`
- **Ban System**: Comprehensive ban/unban functionality with `/ban`, `/unban`, `/listbanned`
- **Automatic Ban Checking**: Middleware prevents banned users from using any bot features
- **Database Integration**: Special users and banned users stored in SQLite with proper tracking

### Character Addition Restrictions (July 19, 2025)
- **Permission System**: Only owner and special users can add characters using `/addchar`
- **Database Schema Fix**: Fixed user_collections table missing 'count' column that was breaking /mycollection
- **Character Drops Fix**: All characters (system + user-added) now available for drops
- **Collection System**: Fixed duplicate character counting and collection display functionality

### Database Cleanup & Management (July 19, 2025)
- **Pre-loaded Characters Removed**: Cleaned database of all 20 pre-loaded characters for fresh start
- **User-Only Content**: Database now contains only user-added characters (4 husbandos remaining)
- **Database Statistics Command**: Added `/dbstats` owner command to check character counts and user statistics
- **Complete Flexibility**: Bot now starts with empty character database, all content is user-generated

### Collection Display Improvements (July 19, 2025)
- **Clean Character Display**: Removed bot tag numbers (ID: 21, 22, etc.) for cleaner appearance
- **Enhanced Formatting**: Character names displayed prominently with attractive layout
- **Improved Navigation**: Added Previous, Next, and Close buttons for better user experience
- **Fixed Pagination**: Corrected page system calculation and navigation functionality
- **Compact Layout**: Streamlined display with emojis and better information organization

### Advanced Visual Collection System
- **Image-Based Character Drops**: Characters now drop with images and hidden names (❓❓❓)
- **Name-Based Catching**: Players catch characters by typing names with fuzzy matching (70% similarity)
- **7-Tier Rarity System**: Complete rarity levels with colored emojis (⚪🟢🔵🟣🟡🔴⭐)
- **Enhanced Image Upload**: Support for image uploads with captions for character addition
- **Smart Caption Processing**: Bot handles both `/addchar` commands and direct captions
- **Duplicate Character System**: Users can catch same character multiple times with count tracking

### Visual and UX Improvements
- **Emoji Formatting**: Proper character display with 🍎 Name and 📚 Series emojis
- **Mystery Gameplay**: Characters drop with hidden names creating guessing mechanics
- **Rarity Visualization**: Each rarity level has distinct colored emoji representation
- **Image Integration**: Full support for character images in drops and database storage
- **Automatic Bot Commands**: Complete command menu system in Telegram interface
- **Enhanced Collection Display**: Shows unique characters, total catches, and individual character counts

### Previous Architecture (January 2025)
- **Complete Database Restructure**: Migrated from gacha system to group-based collection
- **New Collection Mechanics**: Implemented message-based character drops
- **Group Management**: Added comprehensive group settings and admin controls
- **Trading System**: Rebuilt trading with inline button interface
- **Character Management**: Switched to OuraDB-style character database format

## External Dependencies

### Core Libraries
- `python-telegram-bot`: Telegram Bot API integration
- `sqlite3`: Database operations (Python standard library)
- `random`: Character drop probability calculations
- `threading`: Thread-safe database operations
- `datetime`: Time-based features and tracking
- `asyncio`: Asynchronous drop timeout handling

### Character Assets
- **Image URLs**: Uses Wikia links for character images
- **Character Database**: Predefined list of 20 anime characters (10 waifus, 10 husbandos)
- **Popular Series**: Includes characters from Demon Slayer, Attack on Titan, Naruto, My Hero Academia, etc.

## Deployment Strategy

### Environment Setup
- **Bot Token**: Required environment variable `BOT_TOKEN`
- **Database**: SQLite file (`waifu_bot.db`) created automatically
- **Character Population**: Automatic initialization on first run

### Configuration Management
- **Centralized Settings**: All game parameters in `config.py`
- **Flexible Drop System**: Adjustable message limits and timeouts
- **Easy Character Management**: Simple addition of new characters

### Bot Features
- **Group-Focused Design**: Optimized for group chat interactions
- **Real-Time Drops**: Characters drop based on group activity
- **Interactive UI**: Inline keyboards for better user experience
- **Admin Controls**: Comprehensive group management features

### Current Implementation Status
- **Core Features**: Group modes, character drops, claiming system ✅
- **Database**: Complete schema with all required tables ✅
- **Commands**: All basic commands implemented ✅
- **UI**: Inline keyboards for navigation ✅
- **Character Data**: 20 sample characters loaded ✅

The system is designed as a modern group-based character collection bot with emphasis on interactive gameplay and community features. The SQLite database provides simplicity for deployment while maintaining data integrity through proper transaction handling.