from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from config import BASE_DIR, Settings
from database.db import Database
from keyboards.reply import main_menu_keyboard
from services.materials import send_materials


router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message, settings: Settings) -> None:
    event_dt = settings.event_datetime.strftime("%d.%m.%Y в %H:%M")
    text = (
        f"Добро пожаловать в бот мероприятия «{settings.event.title}»!\n\n"
        f"🗓 Дата и время: {event_dt}\n"
        f"📍 Место: {settings.event.venue_name}\n\n"
        "Выберите раздел в меню ниже."
    )
    await message.answer(text, reply_markup=main_menu_keyboard())


@router.message(Command("my_registration"))
async def cmd_my_registration(message: Message, db: Database) -> None:
    registration = await db.get_registration_by_user(message.from_user.id)
    if not registration:
        await message.answer(
            "Вы ещё не зарегистрированы. Нажмите «Зарегистрироваться» в главном меню.",
            reply_markup=main_menu_keyboard(),
        )
        return

    text = (
        "Ваши регистрационные данные:\n"
        f"ID заявки: #{registration.id}\n"
        f"ФИО: {registration.full_name}\n"
        f"Телефон: {registration.phone}\n"
        f"Email: {registration.email}\n"
        f"Компания: {registration.company}\n"
        f"Должность: {registration.position}\n"
        f"Город: {registration.city}\n"
        f"Дата регистрации (UTC): {registration.created_at}"
    )
    await message.answer(text, reply_markup=main_menu_keyboard())


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if not current_state:
        await message.answer("Сейчас нет активного процесса, который нужно отменить.")
        return
    await state.clear()
    await message.answer("Регистрация отменена. Вы можете начать заново в любой момент.", reply_markup=main_menu_keyboard())


@router.message(F.text == "О мероприятии")
async def about_event(message: Message, settings: Settings) -> None:
    event_dt = settings.event_datetime.strftime("%d.%m.%Y в %H:%M")
    text = (
        f"{settings.event.title}\n"
        f"{settings.event.subtitle}\n\n"
        f"🗓 Когда: {event_dt}\n"
        f"📍 Где: {settings.event.venue_name}, {settings.event.venue_address}\n\n"
        f"{settings.event.description}\n\n"
        f"Почему стоит прийти:\n{settings.event.benefits}"
    )
    await message.answer(text)


@router.message(F.text == "Программа")
async def show_program(message: Message, settings: Settings) -> None:
    await message.answer(f"Программа мероприятия:\n\n{settings.event.program}")


@router.message(F.text == "Спикеры")
async def show_speakers(message: Message, settings: Settings) -> None:
    await message.answer(f"Спикеры:\n\n{settings.event.speakers}")


@router.message(F.text == "Место проведения")
async def show_place(message: Message, settings: Settings) -> None:
    await message.answer(
        f"{settings.event.venue_name}\n{settings.event.venue_address}\n\n"
        "Рекомендуем приехать за 20 минут до начала для комфортной регистрации."
    )


@router.message(F.text == "Контакты")
async def show_contacts(message: Message, settings: Settings) -> None:
    await message.answer(settings.event.contacts)


@router.message(F.text == "Получить материалы")
async def get_materials(message: Message, settings: Settings, db: Database, bot) -> None:
    registration = await db.get_registration_by_user(message.from_user.id)
    if not registration:
        await message.answer(
            "Чтобы получить материалы, сначала зарегистрируйтесь на мероприятие.\n"
            "Нажмите кнопку «Зарегистрироваться» в главном меню.",
            reply_markup=main_menu_keyboard(),
        )
        return

    await send_materials(bot, message.from_user.id, settings.event.materials_text, BASE_DIR / "materials")
