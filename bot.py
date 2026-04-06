import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

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
    reminder_service.start()
    await reminder_service.schedule_for_all_registered_users()

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

    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Бот остановлен")
