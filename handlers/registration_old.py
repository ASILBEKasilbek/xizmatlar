"""
Registration handler - Driver va Passenger ro'yxatdan o'tish
"""
import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from states import DriverRegistration, PassengerRegistration
from database import get_db, db_manager
from keyboards import request_phone_keyboard, area_selection_keyboard, services_keyboard, remove_keyboard
from utils import validate_fullname, validate_phone, format_phone
from config import config

logger = logging.getLogger(__name__)

router = Router()


# ===== DRIVER REGISTRATION =====

@router.message(DriverRegistration.waiting_for_fullname)
async def driver_fullname_handler(message: Message, state: FSMContext):
    """Haydovchi ism-familiya"""
    try:
        fullname = message.text.strip()
        
        if not validate_fullname(fullname):
            await message.answer(
                "❌ Ism-familiya noto'g'ri!\n"
                "Faqat harflar ishlatilishi mumkin, maksimal 40 ta belgi.\n\n"
                "Qaytadan kiriting:"
            )
            return
        
        await state.update_data(fullname=fullname)
        
        text = "📱 Telefon raqamingizni yuboring:\n(+998XXXXXXXXX formatida yoki 9 xonali raqam)"
        await message.answer(text, reply_markup=request_phone_keyboard())
        await state.set_state(DriverRegistration.waiting_for_phone)
    
    except Exception as e:
        logger.error(f"Error in driver_fullname_handler: {e}")
        await message.answer("❌ Xatolik yuz berdi.")


@router.message(DriverRegistration.waiting_for_phone)
async def driver_phone_handler(message: Message, state: FSMContext):
    """Haydovchi telefon"""
    try:
        # Contact orqali yuborilgan bo'lsa
        if message.contact:
            phone = message.contact.phone_number
            if not phone.startswith("+"):
                phone = f"+{phone}"
        else:
            phone = message.text.strip()
        
        if not validate_phone(phone):
            await message.answer(
                "❌ Telefon raqam noto'g'ri!\n"
                "+998XXXXXXXXX yoki 9 xonali raqam kiriting.\n\n"
                "Qaytadan kiriting:"
            )
            return
        
        phone = format_phone(phone)
        await state.update_data(phone=phone)
        
        text = "🚗 Mashina modelini kiriting:\n(Masalan: Nexia 3, Gentra, Cobalt)"
        await message.answer(text, reply_markup=remove_keyboard())
        await state.set_state(DriverRegistration.waiting_for_car_model)
    
    except Exception as e:
        logger.error(f"Error in driver_phone_handler: {e}")
        await message.answer("❌ Xatolik yuz berdi.")


@router.message(DriverRegistration.waiting_for_car_model)
async def driver_car_model_handler(message: Message, state: FSMContext):
    """Haydovchi mashina modeli"""
    try:
        car_model = message.text.strip()
        
        if not car_model or len(car_model) > 40:
            await message.answer(
                "❌ Mashina modeli noto'g'ri!\n"
                "Maksimal 40 ta belgi.\n\n"
                "Qaytadan kiriting:"
            )
            return
        
        # Ma'lumotlarni olish
        data = await state.get_data()
        fullname = data.get("fullname")
        phone = data.get("phone")
        user_id = message.from_user.id
        telegram_name = message.from_user.username or message.from_user.first_name
        
        # Database'ga saqlash
        db = get_db()
        try:
            user = db_manager.create_user(
                db=db,
                user_id=user_id,
                fullname=fullname,
                phone=phone,
                user_type="driver",
                car_model=car_model,
                telegram_name=telegram_name
            )
            
            # GROUP1 ga xabar yuborish (haydovchilar guruhi)
            if config.GROUP1:
                group_text = (
                    "🚖 <b>YANGI HAYDOVCHI</b>\n\n"
                    f"👤 Ism: {fullname}\n"
                    f"📱 Telefon: {phone}\n"
                    f"🚗 Mashina: {car_model}\n"
                    f"🆔 ID: {user_id}\n"
                    f"👨‍💼 Username: @{telegram_name if telegram_name else 'mavjud emas'}"
                )
                try:
                    await message.bot.send_message(config.GROUP1, group_text)
                except Exception as e:
                    logger.error(f"Error sending to GROUP1: {e}")
            
            # Foydalanuvchiga javob
            success_text = (
                "✅ <b>Ro'yxatdan o'tish muvaffaqiyatli!</b>\n\n"
                f"👤 Ism: {fullname}\n"
                f"📱 Telefon: {phone}\n"
                f"🚗 Mashina: {car_model}\n\n"
                "🚖 Siz haydovchi sifatida ro'yxatdan o'tdingiz!\n\n"
            )
            
            # GROUP3 linkini yuborish (buyurtmalar guruhi)
            if config.GROUP3:
                success_text += (
                    f"📢 Buyurtmalar GROUP3 guruhida keladi.\n"
                    f"Guruhga qo'shilish uchun adminga murojaat qiling."
                )
            
            await message.answer(success_text)
            logger.info(f"Driver registered: {user_id} - {fullname}")
        
        finally:
            db.close()
        
        await state.clear()
    
    except Exception as e:
        logger.error(f"Error in driver_car_model_handler: {e}")
        await message.answer("❌ Xatolik yuz berdi.")
        await state.clear()


# ===== PASSENGER REGISTRATION =====

@router.message(PassengerRegistration.waiting_for_fullname)
async def passenger_fullname_handler(message: Message, state: FSMContext):
    """Yo'lovchi ism-familiya"""
    try:
        fullname = message.text.strip()
        
        if not validate_fullname(fullname):
            await message.answer(
                "❌ Ism-familiya noto'g'ri!\n"
                "Faqat harflar ishlatilishi mumkin, maksimal 40 ta belgi.\n\n"
                "Qaytadan kiriting:"
            )
            return
        
        await state.update_data(fullname=fullname)
        
        text = "📱 Telefon raqamingizni yuboring:\n(+998XXXXXXXXX formatida yoki 9 xonali raqam)"
        await message.answer(text, reply_markup=request_phone_keyboard())
        await state.set_state(PassengerRegistration.waiting_for_phone)
    
    except Exception as e:
        logger.error(f"Error in passenger_fullname_handler: {e}")
        await message.answer("❌ Xatolik yuz berdi.")


@router.message(PassengerRegistration.waiting_for_phone)
async def passenger_phone_handler(message: Message, state: FSMContext):
    """Yo'lovchi telefon"""
    try:
        # Contact orqali yuborilgan bo'lsa
        if message.contact:
            phone = message.contact.phone_number
            if not phone.startswith("+"):
                phone = f"+{phone}"
        else:
            phone = message.text.strip()
        
        if not validate_phone(phone):
            await message.answer(
                "❌ Telefon raqam noto'g'ri!\n"
                "+998XXXXXXXXX yoki 9 xonali raqam kiriting.\n\n"
                "Qaytadan kiriting:"
            )
            return
        
        phone = format_phone(phone)
        await state.update_data(phone=phone)
        
        text = "📍 Hududingizni tanlang:"
        await message.answer(text, reply_markup=area_selection_keyboard())
        await state.set_state(PassengerRegistration.waiting_for_area)
    
    except Exception as e:
        logger.error(f"Error in passenger_phone_handler: {e}")
        await message.answer("❌ Xatolik yuz berdi.")


@router.message(PassengerRegistration.waiting_for_area)
async def passenger_area_handler(message: Message, state: FSMContext):
    """Yo'lovchi hududi"""
    try:
        area = message.text.strip()
        
        if not area or len(area) > 100:
            await message.answer(
                "❌ Hudud noto'g'ri!\n"
                "Iltimos, hududni tanlang yoki kiriting."
            )
            return
        
        # Ma'lumotlarni olish
        data = await state.get_data()
        fullname = data.get("fullname")
        phone = data.get("phone")
        user_id = message.from_user.id
        telegram_name = message.from_user.username or message.from_user.first_name
        
        # Database'ga saqlash
        db = get_db()
        try:
            user = db_manager.create_user(
                db=db,
                user_id=user_id,
                fullname=fullname,
                phone=phone,
                user_type="passenger",
                area=area,
                telegram_name=telegram_name
            )
            
            # GROUP2 ga xabar yuborish (yo'lovchilar guruhi)
            if config.GROUP2:
                group_text = (
                    "🧍‍♂️ <b>YANGI YO'LOVCHI</b>\n\n"
                    f"👤 Ism: {fullname}\n"
                    f"📱 Telefon: {phone}\n"
                    f"📍 Hudud: {area}\n"
                    f"🆔 ID: {user_id}\n"
                    f"👨‍💼 Username: @{telegram_name if telegram_name else 'mavjud emas'}"
                )
                try:
                    await message.bot.send_message(config.GROUP2, group_text)
                except Exception as e:
                    logger.error(f"Error sending to GROUP2: {e}")
            
            # Foydalanuvchiga javob
            success_text = (
                "✅ <b>Ro'yxatdan o'tish muvaffaqiyatli!</b>\n\n"
                f"👤 Ism: {fullname}\n"
                f"📱 Telefon: {phone}\n"
                f"📍 Hudud: {area}\n\n"
                "🧍‍♂️ Siz yo'lovchi sifatida ro'yxatdan o'tdingiz!\n\n"
                "Kerakli xizmatni tanlang:"
            )
            
            await message.answer(success_text, reply_markup=services_keyboard())
            logger.info(f"Passenger registered: {user_id} - {fullname}")
        
        finally:
            db.close()
        
        await state.clear()
    
    except Exception as e:
        logger.error(f"Error in passenger_area_handler: {e}")
        await message.answer("❌ Xatolik yuz berdi.")
        await state.clear()
