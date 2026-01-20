"""
Yo'lovchi Ro'yxatdan O'tish Handlers
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ContentType
from aiogram.fsm.context import FSMContext
from sqlalchemy.orm import Session
import logging
import re

from config import config, UserRole
from states import RegistrationState
from keyboards import get_phone_request_keyboard, get_remove_keyboard, get_service_keyboard
from crud import create_user

logger = logging.getLogger(__name__)

router = Router()


@router.message(RegistrationState.passenger_waiting_for_name)
async def passenger_name_input(message: Message, state: FSMContext):
    """Yo'lovchi ismini olish"""
    
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
    
    await state.set_state(RegistrationState.passenger_waiting_for_phone)


@router.message(RegistrationState.passenger_waiting_for_phone, ContentType.contact)
async def passenger_phone_contact(message: Message, state: FSMContext):
    """Yo'lovchi telefon raqami (contact orqali)"""
    phone = message.contact.phone_number
    
    if not phone.startswith("+"):
        phone = f"+{phone}"
    
    await state.update_data(phone_number=phone)
    
    await message.answer(
        "🏘️ Qaysi hududa yashasiz? (Shahar nomi yoki mahallasi)\n"
        "Masalan: <b>Tashkent shahar, Shaykhontohur tumani</b>",
        reply_markup=get_remove_keyboard()
    )
    
    await state.set_state(RegistrationState.passenger_waiting_for_area)


@router.message(RegistrationState.passenger_waiting_for_phone)
async def passenger_phone_text(message: Message, state: FSMContext):
    """Yo'lovchi telefon raqami (text orqali)"""
    
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
        "🏘️ Qaysi hududa yashasiz? (Shahar nomi yoki mahallasi)\n"
        "Masalan: <b>Tashkent shahar, Shaykhontohur tumani</b>"
    )
    
    await state.set_state(RegistrationState.passenger_waiting_for_area)


@router.message(RegistrationState.passenger_waiting_for_area)
async def passenger_area_input(message: Message, state: FSMContext, db: Session):
    """Yo'lovchi hududi"""
    
    if not message.text or len(message.text.strip()) < 2:
        await message.answer("❌ Iltimos, hududni to'g'ri kiriting")
        return
    
    # Barcha ma'lumotlarni olish
    data = await state.get_data()
    
    # Foydalanuvchini bazaga saqlash
    user = create_user(
        db=db,
        telegram_id=message.from_user.id,
        first_name=data.get("first_name"),
        last_name=data.get("last_name", ""),
        phone_number=data.get("phone_number"),
        role=UserRole.PASSENGER
    )
    
    # Yo'lovchiga qo'shimcha ma'lumotlarni qo'shish
    from crud import update_user
    update_user(
        db=db,
        user_id=user.user_id,
        residence_area=message.text.strip()
    )
    
    # Yo'lovchilar guruhiga xabar yuborish
    try:
        passenger_group_message = (
            f"👤 <b>Yangi Yo'lovchi Ro'yxatdan O'tdi!</b>\n\n"
            f"<b>Ism:</b> {data.get('first_name')} {data.get('last_name', '')}\n"
            f"<b>📞 Telefon:</b> <code>{data.get('phone_number')}</code>\n"
            f"<b>🏘️ Hudud:</b> {message.text.strip()}\n\n"
            f"ID: <code>{message.from_user.id}</code>"
        )
        
        await message.bot.send_message(
            chat_id=config.PASSENGERS_GROUP_ID,
            text=passenger_group_message,
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Failed to send message to passengers group: {e}")
    
    # Foydalanuvchiga tasdiqlash xabari
    confirmation_text = (
        f"✅ <b>Ro'yxatdan O'tish Yakunlandi!</b>\n\n"
        f"<b>Sizning Ma'lumotlaringiz:</b>\n"
        f"👤 {data.get('first_name')} {data.get('last_name', '')}\n"
        f"📞 {data.get('phone_number')}\n"
        f"🏘️ {message.text.strip()}\n\n"
        f"🎯 Endi xizmat tanlashingiz mumkin!\n\n"
        f"Quyidagi xizmatlardan foydalanishingiz mumkin:"
    )
    
    await message.answer(
        confirmation_text,
        reply_markup=get_service_keyboard()
    )
    
    await state.clear()
    
    logger.info(f"Passenger registered: {message.from_user.id} - {data.get('first_name')}")
