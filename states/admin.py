"""
Admin FSM States
"""
from aiogram.fsm.state import State, StatesGroup


class AdminStates(StatesGroup):
    """Admin panel holatlari"""
    waiting_for_date = State()
