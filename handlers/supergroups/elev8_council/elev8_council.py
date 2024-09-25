import aiohttp
import logging
from telegram import Update
from telegram.ext import ContextTypes

from handlers.supergroups.elev8_council.introductions import handle_introductions
from settings import AUTHORIZED_USER_IDS, INTRODUCTIONS_THREAD_ID, ELEV8_COUNCIL_SUPERGROUP_ID, WEBHOOK_URL_TG_DATA_UPDATE


async def handle_elev8_council_supergroup_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.info("Handling an Elev8 Council supergroup message")

    message = update.message or update.edited_message
    
    if message.message_thread_id == INTRODUCTIONS_THREAD_ID:
        await handle_introductions(update, context)

async def collect_and_send_user_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.info(f"collect_and_send_user_data called by user {update.effective_user.id}")

    if update.effective_user.id not in AUTHORIZED_USER_IDS:
        await update.message.reply_text("Sorry, you're not authorized to use this command.")
        return

    try:
        chat_members = await context.bot.get_chat_administrators(ELEV8_COUNCIL_SUPERGROUP_ID)
        user_data = [
            {
                'user_id': member.user.id,
                'first_name': member.user.first_name,
                'last_name': member.user.last_name,
                'username': member.user.username
            }
            for member in chat_members if member.user.is_bot is False
        ]

        # Send user data to Make.com scenario
        async with aiohttp.ClientSession() as session:
            async with session.post(WEBHOOK_URL_TG_DATA_UPDATE, json={'user_data': user_data}) as response:
                if response.status == 200:
                    await update.message.reply_text("User data has been sent to the Make.com scenario.")
                else:
                    await update.message.reply_text("Failed to send user data to the Make.com scenario.")
                    logging.error(f"Failed to send data to Make.com webhook. Status: {response.status}")
    except Exception as e:
        await update.message.reply_text("An error occurred while collecting user data.")
        logging.error(f"Error in collect_and_send_user_data: {str(e)}")