"""
Start handler - /start, subscription check, role selection
"""
import logging
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from database import get_db, db_manager
from keyboards import subscription_keyboard, role_selection_keyboard, services_keyboard, admin_keyboard
from utils import check_subscription
from config import config

logger = logging.getLogger(__name__)

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Start komandasi"""
    try:
        user_id = message.from_user.id
        
        # FSM state'ni tozalash
        await state.clear()
        
        # Admin ekanligini tekshirish
        is_admin = user_id in config.ADMIN_IDS
        
        # Admin bo'lmasa obunani tekshirish
        if not is_admin:
            is_subscribed = await check_subscription(message.bot, user_id)
            
            if not is_subscribed:
                # Obuna bo'lmagan
                text = (
                    f"👋 Assalomu alaykum, {message.from_user.first_name}!\n\n"
                    "❗️ Botdan foydalanish uchun avval quyidagi kanallarga obuna bo'lishingiz kerak!\n\n"
                    "Barcha kanallarga obuna bo'lgandan keyin <b>✅ Tasdiqlash</b> tugmasini bosing."
                )
                await message.answer(text, reply_markup=subscription_keyboard())
                return
        
        # Database'dan foydalanuvchini tekshirish
        db = get_db()
        try:
            user = db_manager.get_user(db, user_id)
            
            if user:
                # Ro'yxatdan o'tgan foydalanuvchi
                if user.user_type == "driver":
                    text = (
                        f"👋 Xush kelibsiz, {user.fullname}!\n\n"
                        f"🚖 Siz haydovchi sifatida ro'yxatdan o'tgansiz.\n"
                        f"📱 Telefon: {user.phone}\n"
                        f"🚗 Mashina: {user.car_model}\n\n"
                        f"Buyurtmalar GROUP3 guruhida keladi."
                    )
                    await message.answer(text)
                
                elif user.user_type == "passenger":
                    text = (
                        f"👋 Xush kelibsiz, {user.fullname}!\n\n"
                        f"🧍‍♂️ Siz yo'lovchi sifatida ro'yxatdan o'tgansiz.\n"
                        f"📱 Telefon: {user.phone}\n"
                        f"📍 Hudud: {user.area}\n\n"
                        f"Kerakli xizmatni tanlang:"
                    )
                    await message.answer(text, reply_markup=services_keyboard())
                
                elif user.user_type == "admin":
                    text = f"👋 Xush kelibsiz, Admin!\n\nAdmin panelini tanlang:"
                    await message.answer(text, reply_markup=admin_keyboard())
            
            else:
                # Yangi foydalanuvchi - rol tanlash
                text = (
                    f"👋 Assalomu alaykum, {message.from_user.first_name}!\n\n"
                    "🚖 Xizmatlar botiga xush kelibsiz!\n\n"
                    "Iltimos, rolingizni tanlang:"
                )
                await message.answer(text, reply_markup=role_selection_keyboard())
        
        finally:
            db.close()
    
    except Exception as e:
        logger.error(f"Error in cmd_start: {e}")
        await message.answer("❌ Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.")


@router.callback_query(F.data == "check_subscription")
async def check_subscription_callback(callback: CallbackQuery, state: FSMContext):
    """Obunani tekshirish callback"""
    try:
        user_id = callback.from_user.id
        
        # Obunani tekshirish
        is_subscribed = await check_subscription(callback.bot, user_id)
        
        if not is_subscribed:
            await callback.answer("❗️ Siz hali barcha kanallarga obuna bo'lmadingiz! Iltimos, barcha kanallarga obuna bo'ling.", show_alert=True)
            return
        
        # Obuna bo'lgan - xabarni o'chirish va role selection
        await callback.message.delete()
        
        # Database'dan foydalanuvchini tekshirish
        db = get_db()
        try:
            user = db_manager.get_user(db, user_id)
            
            if user:
                # Ro'yxatdan o'tgan
                if user.user_type == "driver":
                    text = (
                        f"✅ Obuna tasdiqlandi!\n\n"
                        f"👋 Xush kelibsiz, {user.fullname}!\n"
                        f"🚖 Siz haydovchi sifatida ro'yxatdan o'tgansiz."
                    )
                    await callback.message.answer(text)
                
                elif user.user_type == "passenger":
                    text = (
                        f"✅ Obuna tasdiqlandi!\n\n"
                        f"👋 Xush kelibsiz, {user.fullname}!\n"
                        f"Kerakli xizmatni tanlang:"
                    )
                    await callback.message.answer(text, reply_markup=services_keyboard())
            
            else:
                # Yangi foydalanuvchi
                text = (
                    f"✅ Obuna tasdiqlandi!\n\n"
                    f"👋 Xush kelibsiz, {callback.from_user.first_name}!\n\n"
                    "Iltimos, rolingizni tanlang:"
                )
                await callback.message.answer(text, reply_markup=role_selection_keyboard())
        
        finally:
            db.close()
        
        await callback.answer()
    
    except Exception as e:
        logger.error(f"Error in check_subscription_callback: {e}")
        await callback.answer("❌ Xatolik yuz berdi.", show_alert=True)


@router.callback_query(F.data == "role_driver")
async def role_driver_callback(callback: CallbackQuery, state: FSMContext):
    """Haydovchi roli callback"""
    try:
        await callback.message.delete()
        
        from states import DriverRegistration
        
        text = (
            "🚖 <b>Haydovchi ro'yxatdan o'tish</b>\n\n"
            "Iltimos, ism va familiyangizni kiriting:\n"
            "(Faqat harflar, maksimal 40 ta belgi)"
        )
        await callback.message.answer(text)
        await state.set_state(DriverRegistration.waiting_for_fullname)
        await callback.answer()
    
    except Exception as e:
        logger.error(f"Error in role_driver_callback: {e}")
        await callback.answer("❌ Xatolik yuz berdi.", show_alert=True)


@router.callback_query(F.data == "role_passenger")
async def role_passenger_callback(callback: CallbackQuery, state: FSMContext):
    """Yo'lovchi roli callback"""
    try:
        await callback.message.delete()
        
        from states import PassengerRegistration
        
        text = (
            "🧍‍♂️ <b>Yo'lovchi ro'yxatdan o'tish</b>\n\n"
            "Iltimos, ism va familiyangizni kiriting:\n"
            "(Faqat harflar, maksimal 40 ta belgi)"
        )
        await callback.message.answer(text)
        await state.set_state(PassengerRegistration.waiting_for_fullname)
        await callback.answer()
    
    except Exception as e:
        logger.error(f"Error in role_passenger_callback: {e}")
        await callback.answer("❌ Xatolik yuz berdi.", show_alert=True)


@router.callback_query(F.data == "role_support")
async def role_support_callback(callback: CallbackQuery):
    """Qo'llab-quvvatlash callback"""
    try:
        text = (
            "🆘 <b>Qo'llab-quvvatlash</b>\n\n"
            "Savollar yoki muammolar bo'lsa, admin bilan bog'laning:\n"
            f"@admin_username"
        )
        await callback.message.answer(text)
        await callback.answer()
    
    except Exception as e:
        logger.error(f"Error in role_support_callback: {e}")
        await callback.answer("❌ Xatolik yuz berdi.", show_alert=True)
