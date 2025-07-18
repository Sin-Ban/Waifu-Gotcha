import logging
import random
import asyncio
import difflib
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatMember, BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from telegram.constants import ChatType
from database import db
from config import BOT_TOKEN, CATCH_TIMEOUT, VALID_GENDERS, TRADE_TIMEOUT, RARITY_LEVELS, VALID_RARITIES, DROP_TIMEOUT, SPECIAL_USERS, OWNER_USER_ID, BANNED_USERS

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# MIDDLEWARE
async def check_banned_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Check if user is banned before processing any command"""
    user_id = update.effective_user.id
    
    if db.is_banned(user_id):
        await update.message.reply_text("❌ You are banned from using this bot!")
        return False
    
    return True

def owner_only(func):
    """Decorator to restrict commands to owner only"""
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not OWNER_USER_ID:
            await update.message.reply_text("❌ Owner not set in configuration!")
            return
        
        if update.effective_user.id != OWNER_USER_ID:
            await update.message.reply_text("❌ This command is owner-only!")
            return
            
        # Check if user is banned
        if not await check_banned_user(update, context):
            return
            
        await func(update, context)
    return wrapper

# Global state for active drops
active_drops = {}

def create_mode_keyboard():
    """Create keyboard for switching modes"""
    keyboard = [
        [
            InlineKeyboardButton("Switch to Waifu", callback_data="mode_waifu"),
            InlineKeyboardButton("Switch to Husbando", callback_data="mode_husbando")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def create_collection_keyboard(page=0, total_pages=1):
    """Create keyboard for collection navigation"""
    keyboard = []
    
    # Navigation buttons
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("◀️ Prev", callback_data=f"collection_page_{page-1}"))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("Next ▶️", callback_data=f"collection_page_{page+1}"))
    
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    return InlineKeyboardMarkup(keyboard)

def create_search_keyboard(results, page=0):
    """Create keyboard for search results"""
    keyboard = []
    
    # Add character buttons
    start_idx = page * 5
    end_idx = min(start_idx + 5, len(results))
    
    for i in range(start_idx, end_idx):
        char = results[i]
        keyboard.append([
            InlineKeyboardButton(f"{char['name']} - {char['series_name']}", callback_data=f"search_view_{char['id']}")
        ])
    
    # Navigation
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("◀️ Prev", callback_data=f"search_page_{page-1}"))
    if end_idx < len(results):
        nav_buttons.append(InlineKeyboardButton("Next ▶️", callback_data=f"search_page_{page+1}"))
    
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    return InlineKeyboardMarkup(keyboard)

def create_trade_keyboard(trade_id):
    """Create keyboard for trade requests"""
    keyboard = [
        [
            InlineKeyboardButton("✅ Accept", callback_data=f"trade_accept_{trade_id}"),
            InlineKeyboardButton("❌ Decline", callback_data=f"trade_decline_{trade_id}")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int) -> bool:
    """Check if user is admin in the group"""
    try:
        chat_member = await context.bot.get_chat_member(update.effective_chat.id, user_id)
        return chat_member.status in [ChatMember.ADMINISTRATOR, ChatMember.OWNER]
    except Exception:
        return False

# COMMAND HANDLERS
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    # Check if user is banned
    if not await check_banned_user(update, context):
        return
    
    if update.effective_chat.type == ChatType.PRIVATE:
        await update.message.reply_text(
            "🌟 Welcome to Waifu/Husbando Collector Bot!\n\n"
            "Add me to a group to start collecting characters!\n\n"
            "Commands:\n"
            "/setmode <waifu/husbando> - Set group mode (admin only)\n"
            "/setwaifulimit <number> - Set drop limit (admin only)\n"
            "/addchar <name> | <series> | <waifu/husbando> - Add character\n"
            "/catch - Catch a dropped character\n"
            "/mycollection - View your collection\n"
            "/search <query> - Search characters\n"
            "/trade <char_id> @user - Trade with user"
        )
    else:
        # Register group
        db.register_group(update.effective_chat.id)
        await update.message.reply_text(
            "🎌 Waifu/Husbando Collector Bot activated!\n\n"
            "Start chatting to make characters drop!"
        )

async def set_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /setmode command"""
    if update.effective_chat.type == ChatType.PRIVATE:
        await update.message.reply_text("This command only works in groups!")
        return
    
    # Check if user is admin
    if not await is_admin(update, context, update.effective_user.id):
        await update.message.reply_text("❌ Only admins can change the group mode!")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /setmode <waifu/husbando>")
        return
    
    mode = context.args[0].lower()
    if mode not in VALID_GENDERS:
        await update.message.reply_text("Mode must be 'waifu' or 'husbando'")
        return
    
    db.set_group_mode(update.effective_chat.id, mode)
    await update.message.reply_text(
        f"✅ Group mode set to {mode.title()}!",
        reply_markup=create_mode_keyboard()
    )

async def set_waifu_limit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /setwaifulimit command"""
    if update.effective_chat.type == ChatType.PRIVATE:
        await update.message.reply_text("This command only works in groups!")
        return
    
    if not await is_admin(update, context, update.effective_user.id):
        await update.message.reply_text("❌ Only admins can change the waifu limit!")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /setwaifulimit <number>")
        return
    
    try:
        limit = int(context.args[0])
        if limit < 1 or limit > 100:
            await update.message.reply_text("Limit must be between 1 and 100")
            return
    except ValueError:
        await update.message.reply_text("Please enter a valid number")
        return
    
    db.set_waifu_limit(update.effective_chat.id, limit)
    await update.message.reply_text(f"✅ Waifu limit set to {limit} messages!")

async def giveme_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Give all characters to special users"""
    user_id = update.effective_user.id
    
    # Check if user is banned
    if not await check_banned_user(update, context):
        return
    
    if not db.is_special_user(user_id):
        await update.message.reply_text("❌ You don't have permission to use this command!")
        return
    
    # Give all characters to the user
    db.give_all_characters_to_user(user_id)
    
    await update.message.reply_text(
        f"🎉 All characters have been added to {update.effective_user.first_name}'s collection!"
    )

@owner_only
async def add_special_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add a special user (owner only)"""
    if not context.args:
        await update.message.reply_text("Usage: /addspecial <user_id> [username]")
        return
    
    try:
        user_id = int(context.args[0])
        username = context.args[1] if len(context.args) > 1 else None
        
        db.add_special_user(user_id, username)
        await update.message.reply_text(f"✅ Added special user: {user_id} ({username or 'Unknown'})")
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID!")

@owner_only
async def remove_special_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove a special user (owner only)"""
    if not context.args:
        await update.message.reply_text("Usage: /removespecial <user_id>")
        return
    
    try:
        user_id = int(context.args[0])
        db.remove_special_user(user_id)
        await update.message.reply_text(f"✅ Removed special user: {user_id}")
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID!")

@owner_only
async def list_special_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all special users (owner only)"""
    users = db.get_special_users()
    
    if not users:
        await update.message.reply_text("📝 No special users found.")
        return
    
    text = "👥 **Special Users:**\n\n"
    for user in users:
        text += f"🆔 {user['user_id']}"
        if user['username']:
            text += f" (@{user['username']})"
        text += f"\n📅 Added: {user['added_at'][:10]}\n\n"
    
    await update.message.reply_text(text)

@owner_only
async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ban a user (owner only)"""
    if not context.args:
        await update.message.reply_text("Usage: /ban <user_id> [reason]")
        return
    
    try:
        user_id = int(context.args[0])
        reason = ' '.join(context.args[1:]) if len(context.args) > 1 else "No reason provided"
        
        db.ban_user(user_id, None, reason)
        await update.message.reply_text(f"🚫 Banned user: {user_id}\nReason: {reason}")
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID!")

@owner_only
async def unban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Unban a user (owner only)"""
    if not context.args:
        await update.message.reply_text("Usage: /unban <user_id>")
        return
    
    try:
        user_id = int(context.args[0])
        db.unban_user(user_id)
        await update.message.reply_text(f"✅ Unbanned user: {user_id}")
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID!")

@owner_only
async def list_banned_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all banned users (owner only)"""
    users = db.get_banned_users()
    
    if not users:
        await update.message.reply_text("📝 No banned users found.")
        return
    
    text = "🚫 **Banned Users:**\n\n"
    for user in users:
        text += f"🆔 {user['user_id']}"
        if user['username']:
            text += f" (@{user['username']})"
        text += f"\n📅 Banned: {user['banned_at'][:10]}"
        if user['reason']:
            text += f"\n💬 Reason: {user['reason']}"
        text += "\n\n"
    
    await update.message.reply_text(text)

async def add_character(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /addchar command"""
    # Check if user is banned
    if not await check_banned_user(update, context):
        return
    
    # Check if this is a photo message with caption
    if update.message.photo and update.message.caption:
        # Parse caption as addchar command
        caption = update.message.caption.strip()
        if caption.startswith('/addchar'):
            # Remove /addchar and parse the rest
            full_text = caption[8:].strip()  # Remove '/addchar'
        else:
            full_text = caption
        
        parts = [part.strip() for part in full_text.split('|')]
        
        if len(parts) not in [3, 4]:
            await update.message.reply_text(
                "Please use the format: name | series | waifu/husbando | rarity (optional)"
            )
            return
        
        name, series, gender = parts[:3]
        rarity = parts[3] if len(parts) == 4 else "Common"
        
        # Get the largest photo
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        image_url = file.file_path
        
    elif context.args:
        # Parse arguments from command
        full_text = ' '.join(context.args)
        parts = [part.strip() for part in full_text.split('|')]
        
        if len(parts) not in [3, 4]:
            await update.message.reply_text(
                "Please use the format: name | series | waifu/husbando | rarity (optional)"
            )
            return
        
        name, series, gender = parts[:3]
        rarity = parts[3] if len(parts) == 4 else "Common"
        
        # Check if message has photo
        image_url = None
        if update.message.photo:
            # Get the largest photo
            photo = update.message.photo[-1]
            file = await context.bot.get_file(photo.file_id)
            image_url = file.file_path
    else:
        # Show help message
        rarity_list = " | ".join([f"{rarity} {RARITY_LEVELS[rarity]['emoji']}" for rarity in VALID_RARITIES])
        await update.message.reply_text(
            f"Usage: /addchar <name> | <series> | <waifu/husbando> | <rarity>\n"
            f"Example: /addchar Zero Two | Darling in the FranXX | waifu | Legendary\n\n"
            f"**Or send an image with caption:**\n"
            f"<name> | <series> | <waifu/husbando> | <rarity>\n\n"
            f"Available rarities:\n{rarity_list}"
        )
        return
    
    gender = gender.lower()
    rarity = rarity.title()
    
    if gender not in VALID_GENDERS:
        await update.message.reply_text("Gender must be 'waifu' or 'husbando'")
        return
    
    if rarity not in VALID_RARITIES:
        rarity_list = " | ".join([f"{r} {RARITY_LEVELS[r]['emoji']}" for r in VALID_RARITIES])
        await update.message.reply_text(f"Invalid rarity! Choose from:\n{rarity_list}")
        return
    
    # Add character to database
    character_id = db.add_character(name, series, image_url, gender, update.effective_user.id, rarity)
    
    rarity_info = RARITY_LEVELS[rarity]
    await update.message.reply_text(
        f"✅ Added {gender} character:\n"
        f"🍎 Name: {name}\n"
        f"📚 Series: {series}\n"
        f"✨ Rarity: {rarity_info['emoji']} {rarity}\n"
        f"🆔 ID: {character_id}"
    )

async def catch_character(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /catch command"""
    # Check if user is banned
    if not await check_banned_user(update, context):
        return
    
    if update.effective_chat.type == ChatType.PRIVATE:
        await update.message.reply_text("This command only works in groups!")
        return
    
    group_id = update.effective_chat.id
    user_id = update.effective_user.id
    
    # Check if there's an active drop
    active_drop = db.get_active_drop(group_id)
    if not active_drop:
        await update.message.reply_text("❌ No character available to catch!")
        return
    
    # Claim the character
    new_count = db.claim_character(user_id, active_drop['character_id'], group_id)
    if new_count:
        db.remove_active_drop(group_id)
        rarity_info = RARITY_LEVELS.get(active_drop['rarity'], RARITY_LEVELS['Common'])
        
        catch_text = f"🎉 Congratulations {update.effective_user.first_name}!\n"
        catch_text += f"You caught {active_drop['name']} from {active_drop['series_name']}!\n"
        catch_text += f"✨ Rarity: {rarity_info['emoji']} {active_drop['rarity']}\n"
        
        if new_count > 1:
            catch_text += f"🔢 Count: {new_count} (duplicate caught!)"
        else:
            catch_text += f"🔢 Count: {new_count} (first time!)"
        
        await update.message.reply_text(catch_text)
    else:
        await update.message.reply_text("❌ Failed to catch character!")

async def my_collection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /mycollection command"""
    # Check if user is banned
    if not await check_banned_user(update, context):
        return
    
    user_id = update.effective_user.id
    page = 0
    
    # Get collection
    collection = db.get_user_collection(user_id, limit=5, offset=page * 5)
    count_info = db.get_collection_count(user_id)
    
    if not collection:
        await update.message.reply_text("📝 Your collection is empty! Start catching characters in groups!")
        return
    
    # Format collection
    text = f"📚 **{update.effective_user.first_name}'s Harem**\n\n"
    text += f"👥 Unique characters: {count_info['unique']}\n"
    text += f"🎯 Total catches: {count_info['total']}\n\n"
    
    for char in collection:
        rarity_info = RARITY_LEVELS.get(char['rarity'], RARITY_LEVELS['Common'])
        text += f"🆔 {char['id']} - {char['name']}\n"
        text += f"📚 {char['series_name']}\n"
        text += f"🎭 {char['gender'].title()}\n"
        text += f"✨ {rarity_info['emoji']} {char['rarity']}\n"
        text += f"🔢 Count: {char['count']}\n\n"
    
    total_pages = (count_info['unique'] + 4) // 5
    text += f"📄 Page {page + 1}/{total_pages}"
    
    keyboard = create_collection_keyboard(page, total_pages)
    
    if update.message.photo:
        # Send as photo caption
        await update.message.reply_photo(
            photo=collection[0]['image_url'] if collection[0]['image_url'] else 'https://via.placeholder.com/400x600/FF69B4/FFFFFF?text=No+Image',
            caption=text,
            reply_markup=keyboard
        )
    else:
        await update.message.reply_text(text, reply_markup=keyboard)

async def search_characters(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /search command"""
    # Check if user is banned
    if not await check_banned_user(update, context):
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /search <name or series>")
        return
    
    query = ' '.join(context.args)
    results = db.search_characters(query)
    
    if not results:
        await update.message.reply_text(f"❌ No characters found matching '{query}'")
        return
    
    # Format results
    text = f"🔍 **Search Results for '{query}'**\n\n"
    text += f"Found {len(results)} characters:\n\n"
    
    # Show first 5 results
    for i, char in enumerate(results[:5]):
        text += f"🆔 {char['id']} - {char['name']}\n"
        text += f"📺 {char['series_name']}\n"
        text += f"🎭 {char['gender'].title()}\n\n"
    
    keyboard = create_search_keyboard(results, 0)
    
    await update.message.reply_text(text, reply_markup=keyboard)

async def trade_character(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /trade command"""
    # Check if user is banned
    if not await check_banned_user(update, context):
        return
    
    if len(context.args) < 2:
        await update.message.reply_text(
            "Usage: /trade <character_id> @username\n"
            "Example: /trade 123 @friend"
        )
        return
    
    try:
        char_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Invalid character ID")
        return
    
    # Get target user
    target_username = context.args[1].replace('@', '')
    
    # Check if sender owns the character
    if not db.user_owns_character(update.effective_user.id, char_id):
        await update.message.reply_text("❌ You don't own this character!")
        return
    
    # Get character info
    character = db.get_character_by_id(char_id)
    if not character:
        await update.message.reply_text("❌ Character not found!")
        return
    
    # For now, we'll store the trade request and let the target user accept via callback
    await update.message.reply_text(
        f"🔄 Trade request sent!\n"
        f"Character: {character['name']} ({character['series_name']})\n"
        f"Target: @{target_username}\n\n"
        f"Waiting for @{target_username} to accept..."
    )

# MESSAGE HANDLERS
async def handle_group_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular group messages for character drops and name-based catching"""
    if update.effective_chat.type == ChatType.PRIVATE:
        return
    
    group_id = update.effective_chat.id
    user_id = update.effective_user.id
    message_text = update.message.text.strip()
    
    # Register group if not exists
    group = db.get_group(group_id)
    if not group:
        db.register_group(group_id)
        group = db.get_group(group_id)
    
    # Check if there's an active drop and user is trying to catch by name
    active_drop = db.get_active_drop(group_id)
    if active_drop and len(message_text) > 2:
        # Check if the message matches the character name
        character_name = active_drop['name'].lower()
        user_guess = message_text.lower()
        
        # Use fuzzy matching for name similarity
        similarity = difflib.SequenceMatcher(None, character_name, user_guess).ratio()
        
        if similarity >= 0.7:  # 70% similarity threshold
            # Claim the character
            new_count = db.claim_character(user_id, active_drop['character_id'], group_id)
            if new_count:
                db.remove_active_drop(group_id)
                rarity_info = RARITY_LEVELS.get(active_drop['rarity'], RARITY_LEVELS['Common'])
                
                # Send catch success message
                catch_text = f"🎉 **{update.effective_user.first_name}** caught **{active_drop['name']}**!\n\n"
                catch_text += f"🍎 Name: {active_drop['name']}\n"
                catch_text += f"📚 Series: {active_drop['series_name']}\n"
                catch_text += f"🎭 Type: {active_drop['gender'].title()}\n"
                catch_text += f"✨ Rarity: {rarity_info['emoji']} {active_drop['rarity']}\n"
                catch_text += f"👤 Owner: {update.effective_user.first_name}\n"
                
                if new_count > 1:
                    catch_text += f"🔢 Count: {new_count} (duplicate caught!)"
                else:
                    catch_text += f"🔢 Count: {new_count} (first time!)"
                
                await update.message.reply_text(catch_text)
                return
    
    # Increment message count
    db.increment_message_count(group_id)
    
    # Get updated group info to check message count
    group = db.get_group(group_id)
    
    # Debug logging
    print(f"Group {group_id}: message count = {group['message_count']}, limit = {group['waifu_limit']}")
    
    # Check if we should drop a character
    if group['message_count'] >= group['waifu_limit']:
        await drop_character(update, context, group)

async def drop_character(update: Update, context: ContextTypes.DEFAULT_TYPE, group):
    """Drop a character in the group"""
    group_id = update.effective_chat.id
    
    # Get random character based on group mode
    character = db.get_random_character(group['mode'])
    if not character:
        # No user-added characters of this type available
        await context.bot.send_message(
            chat_id=group_id,
            text=f"❌ No {group['mode']} characters have been added to the database yet!\n"
                 f"Use `/addchar` or send an image with character details to add some characters first."
        )
        return
    
    # Create drop
    drop_id = db.create_drop(group_id, character['id'])
    
    # Reset message count
    db.reset_message_count(group_id)
    
    # Get rarity info
    rarity_info = RARITY_LEVELS.get(character['rarity'], RARITY_LEVELS['Common'])
    
    # Send character drop message
    text = f"🎉 A wild {group['mode']} appeared!\n\n"
    text += f"📛 Name: ❓❓❓\n"
    text += f"📺 Series: {character['series_name']}\n"
    text += f"🎭 Type: {character['gender'].title()}\n"
    text += f"✨ Rarity: {rarity_info['emoji']} {character['rarity']}\n\n"
    text += f"🔍 Type the character's name to catch them!\n"
    text += f"⏰ {DROP_TIMEOUT} seconds to catch!"
    
    if character['image_url']:
        try:
            message = await context.bot.send_photo(
                chat_id=group_id,
                photo=character['image_url'],
                caption=text
            )
        except Exception:
            # If image fails, send text
            message = await context.bot.send_message(
                chat_id=group_id,
                text=text
            )
    else:
        message = await context.bot.send_message(
            chat_id=group_id,
            text=text
        )
    
    # Set timeout to remove drop if not caught
    asyncio.create_task(drop_timeout(group_id, DROP_TIMEOUT))

async def drop_timeout(group_id: int, timeout: int):
    """Handle drop timeout"""
    await asyncio.sleep(timeout)
    
    # Check if drop still exists
    active_drop = db.get_active_drop(group_id)
    if active_drop:
        db.remove_active_drop(group_id)
        # Could send timeout message here if needed

# CALLBACK HANDLERS
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data.startswith("mode_"):
        await handle_mode_change(query, context)
    elif data.startswith("collection_page_"):
        await handle_collection_page(query, context)
    elif data.startswith("search_page_"):
        await handle_search_page(query, context)
    elif data.startswith("search_view_"):
        await handle_search_view(query, context)
    elif data.startswith("trade_accept_"):
        await handle_trade_accept(query, context)
    elif data.startswith("trade_decline_"):
        await handle_trade_decline(query, context)

async def handle_mode_change(query, context):
    """Handle mode change button"""
    if not await is_admin(query, context, query.from_user.id):
        await query.edit_message_text("❌ Only admins can change the group mode!")
        return
    
    mode = query.data.split("_")[1]
    db.set_group_mode(query.message.chat.id, mode)
    
    await query.edit_message_text(
        f"✅ Group mode changed to {mode.title()}!",
        reply_markup=create_mode_keyboard()
    )

async def handle_collection_page(query, context):
    """Handle collection page navigation"""
    page = int(query.data.split("_")[-1])
    user_id = query.from_user.id
    
    # Get collection
    collection = db.get_user_collection(user_id, limit=5, offset=page * 5)
    total_count = db.get_collection_count(user_id)
    
    if not collection:
        await query.edit_message_text("📝 Your collection is empty!")
        return
    
    # Format collection
    text = f"📚 **{query.from_user.first_name}'s Collection**\n\n"
    text += f"Total characters: {total_count}\n\n"
    
    for char in collection:
        text += f"🆔 {char['id']} - {char['name']}\n"
        text += f"📺 {char['series_name']}\n"
        text += f"🎭 {char['gender'].title()}\n\n"
    
    total_pages = (total_count + 4) // 5
    text += f"📄 Page {page + 1}/{total_pages}"
    
    keyboard = create_collection_keyboard(page, total_pages)
    
    await query.edit_message_text(text, reply_markup=keyboard)

async def handle_search_page(query, context):
    """Handle search page navigation"""
    # This would need to store search results in context
    await query.edit_message_text("Search pagination not implemented yet")

async def handle_search_view(query, context):
    """Handle search character view"""
    char_id = int(query.data.split("_")[-1])
    character = db.get_character_by_id(char_id)
    
    if not character:
        await query.edit_message_text("❌ Character not found!")
        return
    
    text = f"📛 **{character['name']}**\n\n"
    text += f"📺 Series: {character['series_name']}\n"
    text += f"🎭 Type: {character['gender'].title()}\n"
    text += f"🆔 ID: {character['id']}\n"
    
    if character['image_url']:
        try:
            await query.message.reply_photo(
                photo=character['image_url'],
                caption=text
            )
        except Exception:
            await query.edit_message_text(text)
    else:
        await query.edit_message_text(text)

async def handle_trade_accept(query, context):
    """Handle trade accept"""
    await query.edit_message_text("✅ Trade accepted! (Implementation pending)")

async def handle_trade_decline(query, context):
    """Handle trade decline"""
    await query.edit_message_text("❌ Trade declined!")

async def setup_bot_commands(application):
    """Set up bot commands menu"""
    commands = [
        BotCommand("start", "Start the bot and get welcome message"),
        BotCommand("setmode", "[Admin] Set group mode (waifu/husbando)"),
        BotCommand("setwaifulimit", "[Admin] Set message limit for drops"),
        BotCommand("addchar", "Add new character with rarity to database"),
        BotCommand("giveme", "[Special] Get all characters in collection"),
        BotCommand("catch", "Catch a dropped character (or type name)"),
        BotCommand("mycollection", "View your character collection"),
        BotCommand("search", "Search for characters by name or series"),
        BotCommand("trade", "Trade character with another user"),
        BotCommand("addspecial", "[Owner] Add special user"),
        BotCommand("removespecial", "[Owner] Remove special user"),
        BotCommand("listspecial", "[Owner] List special users"),
        BotCommand("ban", "[Owner] Ban a user"),
        BotCommand("unban", "[Owner] Unban a user"),
        BotCommand("listbanned", "[Owner] List banned users"),
    ]
    
    await application.bot.set_my_commands(commands)
    print("✅ Bot commands menu configured")

def main():
    """Main function to run the bot"""
    # Initialize database with sample characters
    from characters import populate_characters
    populate_characters()
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("setmode", set_mode))
    application.add_handler(CommandHandler("setwaifulimit", set_waifu_limit))
    application.add_handler(CommandHandler("addchar", add_character))
    application.add_handler(CommandHandler("giveme", giveme_all))
    application.add_handler(CommandHandler("catch", catch_character))
    application.add_handler(CommandHandler("mycollection", my_collection))
    application.add_handler(CommandHandler("search", search_characters))
    application.add_handler(CommandHandler("trade", trade_character))
    
    # Owner-only management commands
    application.add_handler(CommandHandler("addspecial", add_special_user))
    application.add_handler(CommandHandler("removespecial", remove_special_user))
    application.add_handler(CommandHandler("listspecial", list_special_users))
    application.add_handler(CommandHandler("ban", ban_user))
    application.add_handler(CommandHandler("unban", unban_user))
    application.add_handler(CommandHandler("listbanned", list_banned_users))
    
    # Add message handler for group messages
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & filters.ChatType.GROUPS,
        handle_group_message
    ))
    
    # Add message handler for photo messages with captions
    application.add_handler(MessageHandler(
        filters.PHOTO & filters.CAPTION,
        add_character
    ))
    
    # Add callback query handler
    application.add_handler(CallbackQueryHandler(button_callback))
    
    print("🤖 Waifu/Husbando Collector Bot is starting...")
    print("🎌 Ready to collect waifus and husbandos!")
    
    # Set up bot commands menu
    async def post_init(application):
        await setup_bot_commands(application)
    
    application.post_init = post_init
    
    # Run the bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()