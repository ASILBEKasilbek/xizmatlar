"""
Start va Rol tanlash Handlers
/start komandasi va dastlabki o'rnatish
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, User
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from sqlalchemy.orm import Session
import logging

from config import config, UserRole
from states import RegistrationState, check_subscription, force_subscribe
from keyboards import get_role_keyboard, get_back_button
from crud import get_user_by_telegram_id, create_user

logger = logging.getLogger(__name__)

router = Router()


@router.message(Command("start"))
async def start_command(message: Message, state: FSMContext, db: Session):
    """
    /start komandasi
    Foydalanuvchini karsilash va kanalga obuna tekshirish
    """
    user_id = message.from_user.id
    
    # Kanalga obuna tekshirish
    channel_username = config.CHANNEL_ID  # Channel ID yoki username
    # Channel username-ni qo'lda belgilash kerak (config'dan)
    channel_username = "xizmatlar_bot_channel"  # Example
    
    is_subscribed = await force_subscribe(
        message.bot,
        message,
        config.CHANNEL_ID,
        channel_username
    )
    
    if not is_subscribed:
        return
    
    # Foydalanuvchini tekshirish
    existing_user = get_user_by_telegram_id(db, user_id)
    
    if existing_user:
        # Foydalanuvchi allaqachon ro'yxatdan o'tgan
        await message.answer(
            f"👋 Salom, {existing_user.first_name}! \n\n"
            f"Rolni tanlang yoki mavjud xizmatlardan foydalaning.",
            reply_markup=get_role_keyboard()
        )
        return
    
    # Yangi foydalanuvchi - ro'yxatdan o'tish jarayoniga boshlash
    await message.answer(
        "👋 <b>Xoʻsh kelibsiz Xizmatlar Bot-ga!</b>\n\n"
        "🤖 Men sizga quyidagi xizmatlarni taqdim qilaman:\n\n"
        "🚕 <b>Taxi</b> - Haraka qilish uchun\n"
        "🥖 <b>Non</b> - Nonni buyurtma qilish\n"
        "🌾 <b>Yem</b> - Yem buyurtma qilish\n\n"
        "Roli tanlang:",
        reply_markup=get_role_keyboard()
    )
    
    await state.set_state(RegistrationState.waiting_for_role)


@router.callback_query(F.data == "role_driver", RegistrationState.waiting_for_role)
async def select_driver_role(callback: CallbackQuery, state: FSMContext):
    """Haydovchi rolini tanlash"""
    await callback.answer()
    
    await callback.message.edit_text(
        "🚖 <b>Haydovchi Ro'yxatdan O'tish</b>\n\n"
        "Boshlab, ism va familiyangizni kiriting:",
        reply_markup=None
    )
    
    await state.set_state(RegistrationState.driver_waiting_for_name)
    await state.update_data(role=UserRole.DRIVER)


@router.callback_query(F.data == "role_passenger", RegistrationState.waiting_for_role)
async def select_passenger_role(callback: CallbackQuery, state: FSMContext):
    """Yo'lovchi rolini tanlash"""
    await callback.answer()
    
    await callback.message.edit_text(
        "🧍 <b>Yo'lovchi Ro'yxatdan O'tish</b>\n\n"
        "Boshlab, ism va familiyangizni kiriting:",
        reply_markup=None
    )
    
    await state.set_state(RegistrationState.passenger_waiting_for_name)
    await state.update_data(role=UserRole.PASSENGER)


@router.callback_query(F.data == "role_support")
async def select_support_role(callback: CallbackQuery):
    """Qo'llab-quvvatlash"""
    await callback.answer()
    
    support_text = (
        "🆘 <b>Qo'llab-Quvvatlash</b>\n\n"
        "Agar savollaringiz bo'lsa yoki muammo bilan duch kelsangiz, "
        "iltimos adminga yozing:\n\n"
        "📧 @admin\n"
        "☎️ +998 XX XXX XX XX"
    )
    
    await callback.message.edit_text(support_text, reply_markup=get_back_button())


@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery, state: FSMContext, db: Session):
    """Menuga qaytish"""
    await callback.answer()
    
    user_id = callback.from_user.id
    user = get_user_by_telegram_id(db, user_id)
    
    if not user:
        await callback.message.edit_text(
            "Ro'yxatdan o'tish uchun /start buyrug'ini kiriting",
            reply_markup=None
        )
        return
    
    await callback.message.edit_text(
        f"👋 {user.first_name}, xush kelibsiz!\n\n"
        "Quyidagi amallardan birini tanlang:",
        reply_markup=get_role_keyboard()
    )
    
    await state.clear()


@router.callback_query(F.data == "cancel_action")
async def cancel_action(callback: CallbackQuery, state: FSMContext):
    """Amalni bekor qilish"""
    await callback.answer("❌ Amal bekor qilindi")
    await state.clear()
    
    await callback.message.edit_text(
        "Amal bekor qilindi. /start buyrug'ini qayta kiriting",
        reply_markup=None
    )
