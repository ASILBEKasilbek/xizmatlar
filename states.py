"""
FSM (Finite State Machine) va Middleware
State management va authentication uchun
"""

from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, Update
from sqlalchemy.orm import Session
from typing import Any, Awaitable, Callable, Optional
import logging

from database import SessionLocal
from crud import get_user_by_telegram_id

logger = logging.getLogger(__name__)


# ==================== FSM STATES ====================

class RegistrationState(StatesGroup):
    """Ro'yxatdan o'tish jarayoni states"""
    waiting_for_role = State()
    
    # Haydovchi uchun states
    driver_waiting_for_name = State()
    driver_waiting_for_phone = State()
    driver_waiting_for_car_info = State()
    driver_waiting_for_car_number = State()
    
    # Yo'lovchi uchun states
    passenger_waiting_for_name = State()
    passenger_waiting_for_phone = State()
    passenger_waiting_for_area = State()


class OrderState(StatesGroup):
    """Buyurtma berish jarayoni states"""
    waiting_for_description = State()
    waiting_for_location = State()
    waiting_for_confirmation = State()


class AdminState(StatesGroup):
    """Admin paneli states"""
    waiting_for_stat_date = State()
    waiting_for_action = State()


# ==================== MIDDLEWARE ====================

class DatabaseMiddleware(BaseMiddleware):
    """Database session middleware"""
    
    async def __call__(
        self,
        handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: dict[str, Any],
    ) -> Any:
        db = SessionLocal()
        data["db"] = db
        try:
            return await handler(event, data)
        finally:
            db.close()


class UserCheckMiddleware(BaseMiddleware):
    """Foydalanuvchi bazada borligini tekshirish middleware"""
    
    async def __call__(
        self,
        handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: dict[str, Any],
    ) -> Any:
        user = event.message.from_user if event.message else None
        user = user or (event.callback_query.from_user if event.callback_query else None)
        
        if user:
            db: Session = data.get("db")
            if db:
                db_user = get_user_by_telegram_id(db, user.id)
                data["db_user"] = db_user
        
        return await handler(event, data)


class AdminCheckMiddleware(BaseMiddleware):
    """Admin tekshirish middleware"""
    
    async def __call__(
        self,
        handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: dict[str, Any],
    ) -> Any:
        from config import config
        
        user = event.message.from_user if event.message else None
        user = user or (event.callback_query.from_user if event.callback_query else None)
        
        if user:
            data["is_admin"] = user.id in config.ADMIN_IDS
        
        return await handler(event, data)


# ==================== STATE MANAGEMENT HELPER ====================

class StateManager:
    """State boshqaruvi uchun helper class"""
    
    @staticmethod
    async def reset_state(state: FSMContext):
        """Barcha statelari toza qilish"""
        await state.clear()
    
    @staticmethod
    async def set_data(state: FSMContext, **kwargs):
        """Datani state-ga saqlash"""
        data = await state.get_data()
        data.update(kwargs)
        await state.update_data(**kwargs)
    
    @staticmethod
    async def get_data(state: FSMContext) -> dict:
        """State datani olish"""
        return await state.get_data()


# ==================== SUBSCRIPTION CHECK ====================

async def check_subscription(bot, user_id: int, channel_id: int) -> bool:
    """Foydalanuvchining kanalga obuna bo'lganligini tekshirish"""
    try:
        member = await bot.get_chat_member(channel_id, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        logger.error(f"Subscription check error: {e}")
        return False


async def force_subscribe(bot, message: Message, channel_id: int, channel_username: str) -> bool:
    """Foydalanuvchini kanalga obuna bo'lishga majbur qilish"""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    is_subscribed = await check_subscription(bot, message.from_user.id, channel_id)
    
    if not is_subscribed:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="📢 Kanalga obuna bo'lish",
                url=f"https://t.me/{channel_username}"
            )]
        ])
        
        await message.answer(
            "❌ Bot ishlamoqda, avval kanalga obuna bo'lishing kerak!\n\n"
            "Kanalni kuzatib turish muhim, yangi xizmatlar va e'lonlar uchun.",
            reply_markup=keyboard
        )
        return False
    
    return True
