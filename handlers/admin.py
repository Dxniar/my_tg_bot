from datetime import datetime
from pathlib import Path

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import FSInputFile, Message

from config import Settings
from database.db import Database
from keyboards.reply import admin_keyboard, main_menu_keyboard
from services.export import export_registrations_to_csv


router = Router()


def _is_admin(user_id: int, settings: Settings) -> bool:
    return user_id in settings.admin_ids


@router.message(Command("admin"))
async def cmd_admin(message: Message, settings: Settings) -> None:
    if not _is_admin(message.from_user.id, settings):
        await message.answer("У вас нет доступа к админ-функциям.")
        return
    await message.answer("Панель администратора:\nВыберите команду ниже.", reply_markup=admin_keyboard())


@router.message(Command("stats"))
async def cmd_stats(message: Message, settings: Settings, db: Database) -> None:
    if not _is_admin(message.from_user.id, settings):
        await message.answer("У вас нет доступа к команде /stats.")
        return
    total = await db.count_registrations()
    await message.answer(f"Всего регистраций: {total}")


@router.message(Command("registrations"))
async def cmd_registrations(message: Message, settings: Settings, db: Database) -> None:
    if not _is_admin(message.from_user.id, settings):
        await message.answer("У вас нет доступа к команде /registrations.")
        return

    records = await db.get_latest_registrations(limit=10)
    if not records:
        await message.answer("Пока нет зарегистрированных участников.")
        return

    lines = ["Последние регистрации:"]
    for reg in records:
        lines.append(
            f"#{reg.id} | {reg.full_name} | {reg.phone} | {reg.email} | "
            f"{reg.company} | {reg.city} | {reg.created_at}"
        )
    await message.answer("\n".join(lines))


@router.message(Command("export_csv"))
async def cmd_export_csv(message: Message, settings: Settings, db: Database) -> None:
    if not _is_admin(message.from_user.id, settings):
        await message.answer("У вас нет доступа к команде /export_csv.")
        return

    records = await db.get_all_registrations()
    export_dir = Path("exports")
    filename = f"registrations_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
    csv_path = export_registrations_to_csv(records, export_dir / filename)

    await message.answer_document(FSInputFile(csv_path), caption="Экспорт заявок готов")


@router.message(Command("broadcast"))
async def cmd_broadcast(message: Message, settings: Settings, db: Database, bot) -> None:
    if not _is_admin(message.from_user.id, settings):
        await message.answer("У вас нет доступа к команде /broadcast.")
        return

    user_ids = await db.get_registered_user_ids()
    if not user_ids:
        await message.answer("Нет зарегистрированных пользователей для рассылки.")
        return

    text = (
        "Пример рассылки:\n"
        "Уважаемые партнёры, напоминаем о мероприятии и готовности нашей команды "
        "ответить на ваши вопросы до события."
    )
    sent = 0
    for user_id in user_ids:
        try:
            await bot.send_message(user_id, text)
            sent += 1
        except Exception:
            continue

    await message.answer(f"Рассылка завершена. Доставлено: {sent} из {len(user_ids)}")


@router.message(Command("menu"))
async def cmd_menu(message: Message) -> None:
    await message.answer("Главное меню", reply_markup=main_menu_keyboard())
