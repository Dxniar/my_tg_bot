from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from database.db import Database
from keyboards.reply import consent_keyboard, main_menu_keyboard
from models.states import RegistrationStates
from services.materials import send_materials
from services.reminders import ReminderService
from utils.validators import is_valid_email, is_valid_phone
from config import Settings, BASE_DIR


router = Router()


@router.message(F.text == "Зарегистрироваться")
async def start_registration(message: Message, state: FSMContext, db: Database) -> None:
    existing = await db.get_registration_by_user(message.from_user.id)
    if existing:
        await message.answer(
            f"Вы уже зарегистрированы. Ваш ID заявки: #{existing.id}.\n"
            "Если нужно обновить данные, обратитесь к организатору.",
            reply_markup=main_menu_keyboard(),
        )
        return

    await state.set_state(RegistrationStates.full_name)
    await message.answer(
        "Отлично! Начинаем регистрацию.\nВведите ваше ФИО:",
        reply_markup=main_menu_keyboard(),
    )


@router.message(RegistrationStates.full_name)
async def process_full_name(message: Message, state: FSMContext) -> None:
    if len(message.text.strip()) < 5:
        await message.answer("Пожалуйста, введите корректное ФИО (минимум 5 символов).")
        return
    await state.update_data(full_name=message.text.strip())
    await state.set_state(RegistrationStates.phone)
    await message.answer("Введите телефон для связи:")


@router.message(RegistrationStates.phone)
async def process_phone(message: Message, state: FSMContext) -> None:
    phone = message.text.strip()
    if not is_valid_phone(phone):
        await message.answer("Телефон не должен быть пустым. Введите номер ещё раз.")
        return
    await state.update_data(phone=phone)
    await state.set_state(RegistrationStates.email)
    await message.answer("Введите email:")


@router.message(RegistrationStates.email)
async def process_email(message: Message, state: FSMContext) -> None:
    email = message.text.strip()
    if not is_valid_email(email):
        await message.answer("Похоже, email указан некорректно. Пример: broker@company.ru")
        return
    await state.update_data(email=email)
    await state.set_state(RegistrationStates.company)
    await message.answer("Укажите компанию:")


@router.message(RegistrationStates.company)
async def process_company(message: Message, state: FSMContext) -> None:
    company = message.text.strip()
    if len(company) < 2:
        await message.answer("Введите корректное название компании.")
        return
    await state.update_data(company=company)
    await state.set_state(RegistrationStates.position)
    await message.answer("Укажите должность:")


@router.message(RegistrationStates.position)
async def process_position(message: Message, state: FSMContext) -> None:
    position = message.text.strip()
    if len(position) < 2:
        await message.answer("Введите корректную должность.")
        return
    await state.update_data(position=position)
    await state.set_state(RegistrationStates.city)
    await message.answer("Укажите город:")


@router.message(RegistrationStates.city)
async def process_city(message: Message, state: FSMContext) -> None:
    city = message.text.strip()
    if len(city) < 2:
        await message.answer("Введите корректный город.")
        return
    await state.update_data(city=city)
    await state.set_state(RegistrationStates.consent)
    await message.answer(
        "Подтвердите согласие на обработку персональных данных для участия в мероприятии.",
        reply_markup=consent_keyboard(),
    )


@router.message(RegistrationStates.consent, F.text == "❌ Не согласен")
async def process_consent_no(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "Без согласия мы не можем завершить регистрацию. Если передумаете, начните заново.",
        reply_markup=main_menu_keyboard(),
    )


@router.message(RegistrationStates.consent, F.text == "✅ Согласен")
async def process_consent_yes(
    message: Message,
    state: FSMContext,
    db: Database,
    settings: Settings,
    reminder_service: ReminderService,
    bot,
) -> None:
    data = await state.get_data()
    registration_id = await db.add_registration(
        user_id=message.from_user.id,
        full_name=data["full_name"],
        phone=data["phone"],
        email=data["email"],
        company=data["company"],
        position=data["position"],
        city=data["city"],
        consent=True,
    )

    await reminder_service.schedule_for_user(message.from_user.id)

    await message.answer(
        "Регистрация успешно завершена!\n"
        f"Ваш ID заявки: #{registration_id}.\n"
        "Мы будем ждать вас на мероприятии.",
        reply_markup=main_menu_keyboard(),
    )

    await send_materials(bot, message.from_user.id, settings.event.materials_text, BASE_DIR / "materials")
    await state.clear()


@router.message(RegistrationStates.consent)
async def process_consent_unknown(message: Message) -> None:
    await message.answer("Пожалуйста, выберите вариант кнопкой: «✅ Согласен» или «❌ Не согласен».")
