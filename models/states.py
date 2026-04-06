from aiogram.fsm.state import State, StatesGroup


class RegistrationStates(StatesGroup):
    full_name = State()
    phone = State()
    email = State()
    company = State()
    position = State()
    city = State()
    consent = State()
