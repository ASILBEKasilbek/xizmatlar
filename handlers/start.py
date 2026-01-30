import logging
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from database import get_db, db_manager
from keyboards import subscription_keyboard, role_selection_keyboard, services_keyboard
from utils import check_subscription
from config import config

logger = logging.getLogger(__name__)

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    try:
        user_id = message.from_user.id
        await state.clear()
        is_admin = user_id in config.ADMIN_IDS
        if not is_admin:
            is_subscribed = await check_subscription(message.bot, user_id)
            
            if not is_subscribed:
                text = (
                    f"👋 Assalomu alaykum, {message.from_user.first_name}!\n\n"
                    "❗️ Botdan foydalanish uchun avval kanalga obuna bo'lishingiz kerak!\n\n"
                    "Kanalga obuna bo'lgandan keyin <b>✅ Tasdiqlash</b> tugmasini bosing."
                )
                await message.answer(text, reply_markup=subscription_keyboard())
                return
        
        db = get_db()
        try:
            user = db_manager.get_user(db, user_id)
            
            if user:
                if user.user_type == "driver":
                    text = (
                        f"👋 Xush kelibsiz, {user.fullname}!\n\n"
                        f"🚖 Siz haydovchi sifatida ro'yxatdan o'tgansiz.\n"
                        f"📱 Telefon: {user.phone}\n"
                        f"🚗 Mashina: {user.car_model}\n\n"
                        f"Buyurtmalar {config.GROUP3} guruhida keladi.\n"
                        f"Buyurtmani qabul qilish uchun guruhda \"✅ Qabul qilish\" tugmasini bosing."
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
            
            else:
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
        await message.answer("❌ Xatolik yuz berdi. Iltimos, qaytadan /start bosing.")


@router.callback_query(F.data == "check_subscription")
async def check_subscription_callback(callback: CallbackQuery, state: FSMContext):
    try:
        user_id = callback.from_user.id
        
        is_subscribed = await check_subscription(callback.bot, user_id)
        
        if not is_subscribed:
            await callback.answer(
                "❗️ Siz hali kanalga obuna bo'lmadingiz!\n"
                "Kanalga obuna bo'lgandan keyin qaytadan \"✅ Tasdiqlash\" tugmasini bosing.",
                show_alert=True
            )
            return
        
        await callback.answer("✅ Obuna tasdiqlandi!")
        
        db = get_db()
        try:
            user = db_manager.get_user(db, user_id)
            
            if user:
                if user.user_type == "driver":
                    text = (
                        f"👋 Xush kelibsiz, {user.fullname}!\n\n"
                        f"🚖 Siz haydovchi sifatida ro'yxatdan o'tgansiz.\n"
                        f"📱 Telefon: {user.phone}\n"
                        f"🚗 Mashina: {user.car_model}\n\n"
                        f"Buyurtmalar {config.GROUP3} guruhida keladi."
                    )
                    await callback.message.answer(text)
                
                elif user.user_type == "passenger":
                    text = (
                        f"👋 Xush kelibsiz, {user.fullname}!\n\n"
                        f"🧍‍♂️ Siz yo'lovchi sifatida ro'yxatdan o'tgansiz.\n"
                        f"📱 Telefon: {user.phone}\n"
                        f"📍 Hudud: {user.area}\n\n"
                        f"Kerakli xizmatni tanlang:"
                    )
                    await callback.message.answer(text, reply_markup=services_keyboard())
            
            else:
                text = (
                    f"👋 Assalomu alaykum, {callback.from_user.first_name}!\n\n"
                    "🚖 Xizmatlar botiga xush kelibsiz!\n\n"
                    "Iltimos, rolingizni tanlang:"
                )
                await callback.message.answer(text, reply_markup=role_selection_keyboard())
        
        finally:
            db.close()
        
        try:
            await callback.message.delete()
        except:
            pass
    
    except Exception as e:
        logger.error(f"Error in check_subscription_callback: {e}")
        await callback.answer("❌ Xatolik yuz berdi!", show_alert=True)
