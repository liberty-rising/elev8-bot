import aiohttp
import logging
from telegram import Update, ChatMemberUpdated, ChatMember
from telegram.ext import ContextTypes
from telegram.error import TelegramError

from settings import WEBHOOK_URL_TG_DATA_UPDATE, AUTHORIZED_USER_IDS

async def handle_all_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message or update.edited_message
    logging.info(f"Message details: {message.to_dict()}")

async def handle_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_member_updated: ChatMemberUpdated = update.chat_member
    
    if chat_member_updated.new_chat_member.status == ChatMember.MEMBER:
        new_member = chat_member_updated.new_chat_member.user
        chat_id = update.effective_chat.id
        
        logging.info(f"New member joined: user_id={new_member.id}, chat_id={chat_id}")
        
        try:
            # Check bot's status and permissions
            bot_member = await context.bot.get_chat_member(chat_id, context.bot.id)
            logging.info(f"Bot status in chat {chat_id}: {bot_member.status}")
            
            # Log all bot permissions
            permissions = {
                "can_change_info": bot_member.can_change_info,
                "can_post_messages": bot_member.can_post_messages,
                "can_edit_messages": bot_member.can_edit_messages,
                "can_delete_messages": bot_member.can_delete_messages,
                "can_invite_users": bot_member.can_invite_users,
                "can_restrict_members": bot_member.can_restrict_members,
                "can_pin_messages": bot_member.can_pin_messages,
                "can_promote_members": bot_member.can_promote_members,
                "can_manage_chat": bot_member.can_manage_chat,
                "can_manage_video_chats": bot_member.can_manage_video_chats,
            }
            logging.info(f"Bot permissions in chat {chat_id}: {permissions}")

            if bot_member.status != ChatMember.ADMINISTRATOR:
                logging.error(f"Bot is not an administrator in chat {chat_id}. Cannot promote new members.")
                return

            if not bot_member.can_promote_members:
                logging.error(f"Bot doesn't have permission to promote members in chat {chat_id}.")
                return

            logging.info(f"Attempting to promote user {new_member.id} in chat {chat_id}")
            # Promote the new member to admin with no permissions
            await context.bot.promoteChatMember(
                chat_id=chat_id,
                user_id=new_member.id,
                can_post_messages=True,
                can_post_stories=True
            )
            
            logging.info(f"Successfully promoted user {new_member.id} in chat {chat_id}")

            # Set custom title
            await context.bot.set_chat_administrator_custom_title(
                chat_id=chat_id,
                user_id=new_member.id,
                custom_title="■■■■■■■■■■"
            )
            
            logging.info(f"Set custom title for user {new_member.id} in chat {chat_id}")
        except TelegramError as e:
            logging.error(f"Telegram error when handling new member {new_member.id} in chat {chat_id}: {str(e)}")
            # Log the full error details for debugging
            logging.exception("Full error traceback:")
        except Exception as e:
            logging.error(f"Unexpected error handling new member {new_member.id} in chat {chat_id}: {str(e)}")
            # Log the full error details for debugging
            logging.exception("Full error traceback:")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Hello!')