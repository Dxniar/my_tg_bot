import asyncio
import logging

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from config import load_settings
from database.db import Database
from handlers import admin, registration, user
from middlewares.context import ContextMiddleware
from services.reminders import ReminderService


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    settings = load_settings()
    bot = Bot(token=settings.bot_token)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    db = Database(settings.database_path)
    await db.init()

    reminder_service = ReminderService(bot=bot, db=db, settings=settings)

    context_middleware = ContextMiddleware(
        settings=settings,
        db=db,
        reminder_service=reminder_service,
        bot=bot,
    )
    dp.message.middleware(context_middleware)
    dp.callback_query.middleware(context_middleware)

    dp.include_router(user.router)
    dp.include_router(registration.router)
    dp.include_router(admin.router)

    webhook_url = f"{settings.webhook_base_url.rstrip('/')}{settings.webhook_path}"
    set_webhook_kwargs = {"url": webhook_url, "drop_pending_updates": False}
    if settings.webhook_secret:
        set_webhook_kwargs["secret_token"] = settings.webhook_secret
    await bot.set_webhook(**set_webhook_kwargs)

    reminder_service.start()
    await reminder_service.schedule_for_all_registered_users()

    app = web.Application()
    webhook_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=settings.webhook_secret,
    )
    webhook_handler.register(app, path=settings.webhook_path)
    setup_application(app, dp, bot=bot)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host=settings.webapp_host, port=settings.webapp_port)
    await site.start()

    logging.info("Webhook установлен: %s", webhook_url)
    if settings.webhook_secret:
        logging.info("Проверка webhook secret включена")
    else:
        logging.warning("Проверка webhook secret отключена")
    logging.info("Webhook-сервер запущен на %s:%s", settings.webapp_host, settings.webapp_port)

    stop_event = asyncio.Event()
    try:
        await stop_event.wait()
    finally:
        await bot.delete_webhook(drop_pending_updates=False)
        await bot.session.close()
        await runner.cleanup()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Бот остановлен")
