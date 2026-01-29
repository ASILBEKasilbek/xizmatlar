"""
FSM States - Registration holatlari
"""
from aiogram.fsm.state import State, StatesGroup


class DriverRegistration(StatesGroup):
    """Haydovchi ro'yxatdan o'tish holatlari"""
    waiting_for_fullname = State()
    waiting_for_phone = State()
    waiting_for_car_model = State()


class PassengerRegistration(StatesGroup):
    """Yo'lovchi ro'yxatdan o'tish holatlari"""
    waiting_for_fullname = State()
    waiting_for_phone = State()
    waiting_for_area = State()
