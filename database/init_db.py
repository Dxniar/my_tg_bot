import argparse
import asyncio

from config import load_settings
from database.db import Database


SEED_USERS = [
    {
        "user_id": 10000001,
        "full_name": "Ирина Лебедева",
        "phone": "+7 999 000-11-22",
        "email": "i.lebedeva@example.ru",
        "company": "Городские Решения",
        "position": "Старший брокер",
        "city": "Москва",
    },
    {
        "user_id": 10000002,
        "full_name": "Денис Морозов",
        "phone": "+7 999 000-22-33",
        "email": "d.morozov@example.ru",
        "company": "Prime Partners",
        "position": "Руководитель отдела продаж",
        "city": "Санкт-Петербург",
    },
]


async def init_db(seed: bool = False) -> None:
    settings = load_settings()
    db = Database(settings.database_path)
    await db.init()

    if seed:
        for payload in SEED_USERS:
            exists = await db.get_registration_by_user(payload["user_id"])
            if exists:
                continue
            await db.add_registration(consent=True, **payload)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Инициализация SQLite базы Telegram-бота")
    parser.add_argument("--seed", action="store_true", help="Добавить demo-записи")
    args = parser.parse_args()

    asyncio.run(init_db(seed=args.seed))
