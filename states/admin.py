from aiogram.fsm.state import State, StatesGroup


class AdminStates(StatesGroup):
    waiting_for_date = State()
    waiting_for_channel = State()
