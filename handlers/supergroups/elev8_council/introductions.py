import logging
import aiohttp
from telegram import Update
from telegram.ext import ContextTypes

from settings import WEBHOOK_URL_INTROS


async def handle_introductions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.info("Handling an introduction")

    message = update.message or update.edited_message
    
    data = {
        'chat_id': message.chat_id,
        'user_id': message.from_user.id,
        'username': message.from_user.username,
        'first_name': message.from_user.first_name,
        'last_name': message.from_user.last_name,
        'introduction': message.text
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(WEBHOOK_URL_INTROS, json=data) as response:
            if response.status != 200:
                logging.error(f"Failed to send data to webhook. Status: {response.status}")