import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from database import db
from gacha import gacha
from trading import trading
from utils import (
    create_main_menu, create_inventory_navigation, create_trading_menu,
    create_trade_action_buttons, format_character_card, format_trade_info,
    paginate_list, get_help_text, format_coins
)
from config import BOT_TOKEN, DAILY_REWARD

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    
    # Register user in database
    db.register_user(user.id, user.username, user.first_name)
    
    welcome_message = f"""
🌟 **Welcome to Anime Waifu & Husbando Collector!** 🌟

Hello {user.first_name}! 🎌

Collect your favorite anime characters through our gacha system!
✨ Start with 100 coins
🎰 Each summon costs 10 coins
🎁 Get daily rewards to earn more coins

Use /menu to start collecting!
"""
    
    await update.message.reply_text(welcome_message, reply_markup=create_main_menu())

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /menu command"""
    user = update.effective_user
    user_data = db.get_user(user.id)
    
    if not user_data:
        await update.message.reply_text("Please use /start first to register!")
        return
    
    menu_text = f"""
🎮 **ANIME CHARACTER COLLECTOR** 🎮

👤 **Player:** {user.first_name}
💰 **Coins:** {user_data['coins']}
🎲 **Total Summons:** {user_data['total_summons']}

Choose an option below:
"""
    
    await update.message.reply_text(menu_text, reply_markup=create_main_menu())

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    await update.message.reply_text(get_help_text())

# Callback query handlers
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data
    
    if data == "main_menu":
        await show_main_menu(query, user_id)
    elif data == "summon":
        await handle_summon(query, user_id)
    elif data == "multi_summon":
        await handle_multi_summon(query, user_id)
    elif data == "inventory":
        await show_inventory(query, user_id, page=0)
    elif data.startswith("inventory_page_"):
        page = int(data.split("_")[-1])
        await show_inventory(query, user_id, page)
    elif data == "stats":
        await show_stats(query, user_id)
    elif data == "daily_reward":
        await claim_daily_reward(query, user_id)
    elif data == "trading_menu":
        await show_trading_menu(query, user_id)
    elif data == "pending_trades":
        await show_pending_trades(query, user_id)
    elif data == "trade_history":
        await show_trade_history(query, user_id)
    elif data.startswith("accept_trade_"):
        trade_id = int(data.split("_")[-1])
        await accept_trade(query, user_id, trade_id)
    elif data.startswith("reject_trade_"):
        trade_id = int(data.split("_")[-1])
        await reject_trade(query, user_id, trade_id)
    elif data == "trade_help":
        await show_trade_help(query)
    elif data == "help":
        await query.edit_message_text(get_help_text(), reply_markup=create_main_menu())

async def show_main_menu(query, user_id):
    """Show main menu"""
    user_data = db.get_user(user_id)
    
    menu_text = f"""
🎮 **ANIME CHARACTER COLLECTOR** 🎮

👤 **Player:** {query.from_user.first_name}
💰 **Coins:** {user_data['coins']}
🎲 **Total Summons:** {user_data['total_summons']}

Choose an option below:
"""
    
    await query.edit_message_text(menu_text, reply_markup=create_main_menu())

async def handle_summon(query, user_id):
    """Handle single summon"""
    character, message = gacha.summon_character(user_id)
    
    if character:
        # Send character image if available
        if character['image_url']:
            try:
                await query.message.reply_photo(
                    photo=character['image_url'],
                    caption=message,
                    reply_markup=create_main_menu()
                )
            except Exception as e:
                # If image fails, send text message
                await query.edit_message_text(
                    f"{message}\n\n(Image could not be loaded)",
                    reply_markup=create_main_menu()
                )
        else:
            await query.edit_message_text(message, reply_markup=create_main_menu())
    else:
        await query.edit_message_text(message, reply_markup=create_main_menu())

async def handle_multi_summon(query, user_id):
    """Handle multi-summon (5 characters)"""
    characters, message = gacha.multi_summon(user_id, 5)
    
    if characters:
        # Show summary first
        await query.edit_message_text(message, reply_markup=create_main_menu())
        
        # Send individual character cards
        for char in characters:
            if char['image_url']:
                try:
                    await query.message.reply_photo(
                        photo=char['image_url'],
                        caption=format_character_card(char)
                    )
                except Exception:
                    await query.message.reply_text(format_character_card(char))
            else:
                await query.message.reply_text(format_character_card(char))
    else:
        await query.edit_message_text(message, reply_markup=create_main_menu())

async def show_inventory(query, user_id, page=0):
    """Show user's character inventory"""
    per_page = 5
    characters = db.get_user_characters(user_id)
    
    if not characters:
        await query.edit_message_text(
            "📦 Your collection is empty!\n\n🎰 Use the summon feature to collect characters!",
            reply_markup=create_main_menu()
        )
        return
    
    total_pages = (len(characters) + per_page - 1) // per_page
    page_characters = paginate_list(characters, page, per_page)
    
    inventory_text = f"📦 **YOUR COLLECTION** (Page {page + 1}/{total_pages})\n\n"
    
    for i, char in enumerate(page_characters, 1):
        inventory_text += f"**{(page * per_page) + i}.** {format_character_card(char, show_obtained=True)}\n\n"
    
    await query.edit_message_text(
        inventory_text,
        reply_markup=create_inventory_navigation(page, total_pages)
    )

async def show_stats(query, user_id):
    """Show user statistics"""
    stats_text = gacha.get_summon_statistics(user_id)
    await query.edit_message_text(stats_text, reply_markup=create_main_menu())

async def claim_daily_reward(query, user_id):
    """Handle daily reward claim"""
    if db.can_claim_daily_reward(user_id):
        db.claim_daily_reward(user_id)
        user_data = db.get_user(user_id)
        
        message = f"""
🎁 **DAILY REWARD CLAIMED!** 🎁

You received {DAILY_REWARD} coins!
💰 Current balance: {user_data['coins']} coins

Come back tomorrow for another reward!
"""
    else:
        message = """
⏰ **DAILY REWARD NOT READY** ⏰

You have already claimed your daily reward!
Come back tomorrow for another reward!
"""
    
    await query.edit_message_text(message, reply_markup=create_main_menu())

async def show_trading_menu(query, user_id):
    """Show trading menu"""
    message = """
🔄 **TRADING SYSTEM** 🔄

Trade your characters with other users!

**How to Trade:**
1. Find another user who wants to trade
2. Both users must know each other's character IDs
3. Use the pending trades section to manage trades

**Note:** Trading feature requires both users to be registered with the bot.
"""
    
    await query.edit_message_text(message, reply_markup=create_trading_menu())

async def show_pending_trades(query, user_id):
    """Show pending trades"""
    trades = trading.get_pending_trades(user_id)
    
    if not trades:
        message = """
📋 **NO PENDING TRADES** 📋

You have no pending trade requests.
"""
        await query.edit_message_text(message, reply_markup=create_trading_menu())
        return
    
    message = "📋 **PENDING TRADES** 📋\n\n"
    for trade in trades[:5]:  # Show first 5 trades
        message += format_trade_info(trade) + "\n"
        
        # Add action buttons for trades directed to this user
        if trade['to_user_id'] == user_id:
            await query.message.reply_text(
                f"**Trade #{trade['id']}** - Action Required:",
                reply_markup=create_trade_action_buttons(trade['id'])
            )
    
    await query.edit_message_text(message, reply_markup=create_trading_menu())

async def show_trade_history(query, user_id):
    """Show trade history"""
    trades = trading.get_trade_history(user_id)
    
    if not trades:
        message = """
📚 **NO TRADE HISTORY** 📚

You haven't completed any trades yet.
"""
    else:
        message = "📚 **TRADE HISTORY** 📚\n\n"
        for trade in trades:
            status_emoji = "✅" if trade['status'] == 'accepted' else "❌"
            message += f"{status_emoji} **Trade #{trade['id']}** - {trade['status'].title()}\n"
            message += f"📅 {trade['completed_at'][:16]}\n\n"
    
    await query.edit_message_text(message, reply_markup=create_trading_menu())

async def accept_trade(query, user_id, trade_id):
    """Accept a trade"""
    success, message = trading.accept_trade(trade_id, user_id)
    
    if success:
        await query.edit_message_text(f"✅ {message}", reply_markup=create_trading_menu())
    else:
        await query.edit_message_text(f"❌ {message}", reply_markup=create_trading_menu())

async def reject_trade(query, user_id, trade_id):
    """Reject a trade"""
    success, message = trading.reject_trade(trade_id, user_id)
    
    if success:
        await query.edit_message_text(f"❌ {message}", reply_markup=create_trading_menu())
    else:
        await query.edit_message_text(f"❌ {message}", reply_markup=create_trading_menu())

async def show_trade_help(query):
    """Show trading help"""
    help_text = """
❓ **HOW TO TRADE** ❓

**Trading is currently simplified:**
1. Both users need to be registered with the bot
2. Users can view pending trades
3. Accept or reject trade proposals

**Future Features:**
- Direct trading interface
- Character browsing for trades
- Trade value calculations
- Trade notifications

**Tips:**
- Only trade characters you're willing to part with
- Check character rarity before trading
- Legendary characters are very valuable!
"""
    
    await query.edit_message_text(help_text, reply_markup=create_trading_menu())

def main():
    """Main function to run the bot"""
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("menu", menu))
    application.add_handler(CommandHandler("help", help_command))
    
    # Add callback query handler
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Initialize database and populate characters
    from characters import populate_characters
    populate_characters()
    
    print("🤖 Anime Waifu & Husbando Collector Bot is starting...")
    print(f"🔗 Bot should be accessible via Telegram")
    print("📊 Database initialized with characters")
    print("✅ Bot is ready to collect waifus and husbandos!")
    
    # Run the bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
