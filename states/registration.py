from aiogram.fsm.state import State, StatesGroup


class DriverRegistration(StatesGroup):
    waiting_for_fullname = State()
    waiting_for_phone = State()
    waiting_for_car_model = State()


class PassengerRegistration(StatesGroup):
    waiting_for_fullname = State()
    waiting_for_phone = State()
    waiting_for_area = State()
