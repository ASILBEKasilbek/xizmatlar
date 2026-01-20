"""
Haydovchi Ro'yxatdan O'tish Handlers
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ContentType
from aiogram.fsm.context import FSMContext
from sqlalchemy.orm import Session
import logging
import re

from config import config, UserRole
from states import RegistrationState
from keyboards import get_phone_request_keyboard, get_remove_keyboard, get_back_button
from crud import create_user, get_user_by_telegram_id

logger = logging.getLogger(__name__)

router = Router()


@router.message(RegistrationState.driver_waiting_for_name)
async def driver_name_input(message: Message, state: FSMContext):
    """Haydovchi ismini olish"""
    
    if not message.text or len(message.text.strip()) < 2:
        await message.answer(
            "❌ Iltimos, to'g'ri ism va familiyani kiriting (minimal 2 ta harf):"
        )
        return
    
    names = message.text.strip().split()
    first_name = names[0]
    last_name = " ".join(names[1:]) if len(names) > 1 else ""
    
    await state.update_data(
        first_name=first_name,
        last_name=last_name
    )
    
    await message.answer(
        "📞 Endi telefon raqamni yuborish uchun tugmani bosing yoki to'g'ri formatda kiriting:\n"
        "<code>+998901234567</code>",
        reply_markup=get_phone_request_keyboard()
    )
    
    await state.set_state(RegistrationState.driver_waiting_for_phone)


@router.message(RegistrationState.driver_waiting_for_phone, ContentType.contact)
async def driver_phone_contact(message: Message, state: FSMContext):
    """Haydovchi telefon raqami (contact orqali)"""
    phone = message.contact.phone_number
    
    if not phone.startswith("+"):
        phone = f"+{phone}"
    
    await state.update_data(phone_number=phone)
    
    await message.answer(
        "🚗 Endi mashinaning rusumi va modeli haqida ma'lumot bering:\n"
        "Masalan: <b>Toyota Camry, Chevrolet Spark</b>",
        reply_markup=get_remove_keyboard()
    )
    
    await state.set_state(RegistrationState.driver_waiting_for_car_info)


@router.message(RegistrationState.driver_waiting_for_phone)
async def driver_phone_text(message: Message, state: FSMContext):
    """Haydovchi telefon raqami (text orqali)"""
    
    # Telefon raqami validatsiyasi
    phone = message.text.strip()
    
    # Simple validation
    if not re.match(r"^\+?\d{10,20}$", phone.replace(" ", "")):
        await message.answer(
            "❌ Noto'g'ri telefon raqami! Iltimos, to'g'ri formatda kiriting:\n"
            "<code>+998901234567</code>"
        )
        return
    
    if not phone.startswith("+"):
        phone = f"+{phone}"
    
    await state.update_data(phone_number=phone)
    
    await message.answer(
        "🚗 Endi mashinaning rusumi va modeli haqida ma'lumot bering:\n"
        "Masalan: <b>Toyota Camry, Chevrolet Spark</b>"
    )
    
    await state.set_state(RegistrationState.driver_waiting_for_car_info)


@router.message(RegistrationState.driver_waiting_for_car_info)
async def driver_car_info(message: Message, state: FSMContext):
    """Haydovchi mashinani modeli"""
    
    if not message.text or len(message.text.strip()) < 3:
        await message.answer("❌ Iltimos, mashinaning haqiqiy ma'lumotini kiriting")
        return
    
    await state.update_data(car_info=message.text.strip())
    
    await message.answer(
        "🔢 Endi mashinaning davlat raqamini kiriting:\n"
        "Masalan: <b>10A001AA, 01M123OA</b>"
    )
    
    await state.set_state(RegistrationState.driver_waiting_for_car_number)


@router.message(RegistrationState.driver_waiting_for_car_number)
async def driver_car_number(message: Message, state: FSMContext, db: Session):
    """Haydovchi mashinaning davlat raqami"""
    
    if not message.text or len(message.text.strip()) < 3:
        await message.answer("❌ Iltimos, to'g'ri davlat raqamini kiriting")
        return
    
    car_number = message.text.strip().upper()
    
    # Barcha ma'lumotlarni olish
    data = await state.get_data()
    
    # Foydalanuvchini bazaga saqlash
    user = create_user(
        db=db,
        telegram_id=message.from_user.id,
        first_name=data.get("first_name"),
        last_name=data.get("last_name", ""),
        phone_number=data.get("phone_number"),
        role=UserRole.DRIVER
    )
    
    # Haydovchiga qo'shimcha ma'lumotlarni qo'shish
    from crud import update_user
    update_user(
        db=db,
        user_id=user.user_id,
        car_info=data.get("car_info"),
        car_number=car_number,
        is_active=True
    )
    
    # Haydovchilar guruhiga xabar yuborish
    try:
        driver_group_message = (
            f"🚖 <b>Yangi Haydovchi Ro'yxatdan O'tdi!</b>\n\n"
            f"<b>Ism:</b> {data.get('first_name')} {data.get('last_name', '')}\n"
            f"<b>📞 Telefon:</b> <code>{data.get('phone_number')}</code>\n"
            f"<b>🚗 Mashina:</b> {data.get('car_info')}\n"
            f"<b>🔢 Davlat Raqami:</b> {car_number}\n\n"
            f"ID: <code>{message.from_user.id}</code>"
        )
        
        await message.bot.send_message(
            chat_id=config.DRIVERS_GROUP_ID,
            text=driver_group_message,
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Failed to send message to drivers group: {e}")
    
    # Foydalanuvchiga tasdiqlash xabari
    confirmation_text = (
        f"✅ <b>Ro'yxatdan O'tish Yakunlandi!</b>\n\n"
        f"<b>Sizning Ma'lumotlaringiz:</b>\n"
        f"👤 {data.get('first_name')} {data.get('last_name', '')}\n"
        f"📞 {data.get('phone_number')}\n"
        f"🚗 {data.get('car_info')}\n"
        f"🔢 {car_number}\n\n"
        f"🎯 Siz endi taxi buyurtmalarini qabul qila olasiz!\n\n"
        f"👉 <a href='https://t.me/+GROUP_LINK'>Haydovchilar Guruhiga O'tish</a>"
    )
    
    await message.answer(
        confirmation_text,
        reply_markup=get_remove_keyboard()
    )
    
    await state.clear()
    
    logger.info(f"Driver registered: {message.from_user.id} - {data.get('first_name')}")
