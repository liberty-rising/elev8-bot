import os
import logging
import aiohttp
import asyncio
from telegram import Update, ChatMemberUpdated
from telegram.ext import Application, CommandHandler, MessageHandler, ChatMemberHandler, filters, ContextTypes
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Get environment variables
TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_URL_INTROS = os.getenv("WEBHOOK_URL_INTROS")
WEBHOOK_URL_USERNAME_CHANGES = os.getenv("WEBHOOK_URL_USERNAME_CHANGES")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Hello!')

async def handle_introductions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message or update.edited_message

    logging.info(f"Message details: {message.to_dict()}")
    
    if message.message_thread_id == 2:
        data = {
            'chat_id': message.chat_id,
            'username': message.from_user.username,
            'first_name': message.from_user.first_name,
            'last_name': message.from_user.last_name,
            'text': message.text
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(WEBHOOK_URL_INTROS, json=data) as response:
                if response.status != 200:
                    logging.error(f"Failed to send data to webhook. Status: {response.status}")

async def handle_username_change(update: ChatMemberUpdated, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle username changes in the group."""
    if update.old_chat_member and update.new_chat_member:
        old_username = update.old_chat_member.user.username
        new_username = update.new_chat_member.user.username
        
        if old_username != new_username:
            logging.info(f"Username change detected: {old_username} -> {new_username}")
            
            data = {
                'chat_id': update.chat.id,
                'user_id': update.new_chat_member.user.id,
                'first_name': update.new_chat_member.user.first_name,
                'last_name': update.new_chat_member.user.last_name,
                'old_username': old_username,
                'new_username': new_username
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(WEBHOOK_URL_USERNAME_CHANGES, json=data) as response:
                    if response.status != 200:
                        logging.error(f"Failed to send username change data to webhook. Status: {response.status}")

async def main() -> None:
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & filters.ChatType.SUPERGROUP, handle_introductions))
    application.add_handler(ChatMemberHandler(handle_username_change, ChatMemberHandler.CHAT_MEMBER))

    # Start the bot
    await application.initialize()
    await application.start()
    await application.updater.start_polling()

    logging.info("Bot is running. Press Ctrl+C to stop.")

    # Run the bot until you press Ctrl-C
    stop_signal = asyncio.Event()
    await stop_signal.wait()

    # Clean up
    await application.updater.stop()
    await application.stop()
    await application.shutdown()

async def run_bot():
    try:
        await main()
    except KeyboardInterrupt:
        logging.info("Bot stopped by user. Shutting down.")
    finally:
        # Stop the bot gracefully
        application = Application.get_current()
        await application.updater.stop()
        await application.stop()
        await application.shutdown()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Bot stopped by user. Shutting down.")