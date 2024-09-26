import logging
import asyncio
from aiohttp import web
from telegram.ext import Application, CommandHandler, MessageHandler, ChatMemberHandler, filters
from handlers.all_chats import handle_new_member, handle_all_messages, start
from handlers.supergroups.elev8_council.elev8_council import collect_and_send_user_data
from handlers.supergroups.supergroups import handle_supergroup_messages
from settings import TOKEN


async def health_check(request):
    return web.Response(text="OK")

async def run_web_server():
    app = web.Application()
    app.router.add_get('/health', health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()

async def main() -> None:
    application = Application.builder().token(TOKEN).build()

    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("update_tg_data", collect_and_send_user_data))

    # Message handlers
    application.add_handler(MessageHandler(filters.TEXT & filters.ChatType.SUPERGROUP, handle_supergroup_messages))
    application.add_handler(MessageHandler(filters.ALL, handle_all_messages))

    # Chat member handlers
    application.add_handler(ChatMemberHandler(handle_new_member, ChatMemberHandler.CHAT_MEMBER))

    # Start the web server for health checks
    await run_web_server()
    
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