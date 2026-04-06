from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


MAIN_MENU_BUTTONS = [
    [KeyboardButton(text="О мероприятии"), KeyboardButton(text="Программа")],
    [KeyboardButton(text="Спикеры"), KeyboardButton(text="Место проведения")],
    [KeyboardButton(text="Зарегистрироваться"), KeyboardButton(text="Получить материалы")],
    [KeyboardButton(text="Контакты")],
]


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=MAIN_MENU_BUTTONS, resize_keyboard=True)


def consent_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Согласен")],
            [KeyboardButton(text="❌ Не согласен")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def admin_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="/stats"), KeyboardButton(text="/registrations")],
            [KeyboardButton(text="/export_csv"), KeyboardButton(text="/broadcast")],
        ],
        resize_keyboard=True,
    )
