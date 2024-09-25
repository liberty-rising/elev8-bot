import logging
from telegram import Update
from telegram.ext import ContextTypes

from handlers.supergroups.elev8_council.elev8_council import handle_elev8_council_supergroup_messages
from settings import ELEV8_COUNCIL_SUPERGROUP_ID


async def handle_supergroup_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.info("Handling a supergroup message")

    message = update.message or update.edited_message

    logging.debug(f"Message details: {message.to_dict()}")

    if message.chat_id == ELEV8_COUNCIL_SUPERGROUP_ID: 
        await handle_elev8_council_supergroup_messages(update, context)