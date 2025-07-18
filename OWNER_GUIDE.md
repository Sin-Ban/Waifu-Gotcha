# Owner Management Guide

## Setup Instructions

1. **Set Your Owner ID** in `src/config.py`:
   - Find your user ID using @userinfobot on Telegram
   - Replace `OWNER_USER_ID = None` with your actual user ID
   - Example: `OWNER_USER_ID = 123456789`

## Owner-Only Commands

### Special User Management
- `/addspecial <user_id> [username]` - Add a special user who can use /giveme
- `/removespecial <user_id>` - Remove special user privileges
- `/listspecial` - View all special users

### Ban Management
- `/ban <user_id> [reason]` - Ban a user from using the bot
- `/unban <user_id>` - Unban a user
- `/listbanned` - View all banned users

### How It Works

1. **Special Users**: Can use `/giveme` to get all characters in their collection
2. **Banned Users**: Cannot use any bot commands (automatic blocking)
3. **Owner Only**: These management commands only work for the owner

### Example Usage

```
/addspecial 123456789 friend_username
/ban 987654321 spamming in groups
/unban 987654321
/listspecial
/listbanned
```

## Important Notes

- Set your `OWNER_USER_ID` in config.py before using these commands
- Banned users are automatically blocked from all bot features
- Special users can collect all characters with `/giveme`
- Only the owner can manage special users and bans

## Command Menu

All owner commands are now available in the Telegram bot menu:
- [Owner] commands are restricted to the owner only
- [Special] commands are for special users only
- [Admin] commands are for group administrators