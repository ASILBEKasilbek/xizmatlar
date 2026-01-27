"""
Registration handler - Haydovchi va Yo'lovchi ro'yxatdan o'tish
"""
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from states import DriverRegistration, PassengerRegistration
from database import get_db, db_manager
from keyboards import (
    request_phone_keyboard, 
    request_location_keyboard,
    services_keyboard, 
    remove_keyboard
)
from utils import validate_fullname, validate_phone, format_phone
from config import config

logger = logging.getLogger(__name__)

router = Router()


# ===== ROL TANLASH =====

@router.callback_query(F.data == "role_driver")
async def role_driver_callback(callback: CallbackQuery, state: FSMContext):
    """Haydovchi rol tanlandi"""
    try:
        user_id = callback.from_user.id
        
        # Database'da allaqachon bor ekanligini tekshirish
        db = get_db()
        try:
            user = db_manager.get_user(db, user_id)
            
            if user:
                # Allaqachon ro'yxatdan o'tgan
                await callback.answer(
                    f"❌ Siz allaqachon {user.user_type} sifatida ro'yxatdan o'tgansiz!\n"
                    f"Bitta foydalanuvchi faqat bitta rol tanlashi mumkin.",
                    show_alert=True
                )
                return
        finally:
            db.close()
        
        # Ro'yxatdan o'tish boshlash
        await callback.answer("✅ Haydovchi ro'yxatdan o'tish")
        
        text = (
            "🚖 <b>HAYDOVCHI RO'YXATDAN O'TISH</b>\n\n"
            "Ism-familiyangizni kiriting:"
        )
        await callback.message.answer(text)
        await state.set_state(DriverRegistration.waiting_for_fullname)
        
        # Eski xabarni o'chirish
        try:
            await callback.message.delete()
        except:
            pass
    
    except Exception as e:
        logger.error(f"Error in role_driver_callback: {e}")
        await callback.answer("❌ Xatolik yuz berdi!", show_alert=True)


@router.callback_query(F.data == "role_passenger")
async def role_passenger_callback(callback: CallbackQuery, state: FSMContext):
    """Yo'lovchi rol tanlandi"""
    try:
        user_id = callback.from_user.id
        
        # Database'da allaqachon bor ekanligini tekshirish
        db = get_db()
        try:
            user = db_manager.get_user(db, user_id)
            
            if user:
                # Allaqachon ro'yxatdan o'tgan
                await callback.answer(
                    f"❌ Siz allaqachon {user.user_type} sifatida ro'yxatdan o'tgansiz!\n"
                    f"Bitta foydalanuvchi faqat bitta rol tanlashi mumkin.",
                    show_alert=True
                )
                return
        finally:
            db.close()
        
        # Ro'yxatdan o'tish boshlash
        await callback.answer("✅ Yo'lovchi ro'yxatdan o'tish")
        
        text = (
            "🧍‍♂️ <b>YO'LOVCHI RO'YXATDAN O'TISH</b>\n\n"
            "Ism-familiyangizni kiriting:"
        )
        await callback.message.answer(text)
        await state.set_state(PassengerRegistration.waiting_for_fullname)
        
        # Eski xabarni o'chirish
        try:
            await callback.message.delete()
        except:
            pass
    
    except Exception as e:
        logger.error(f"Error in role_passenger_callback: {e}")
        await callback.answer("❌ Xatolik yuz berdi!", show_alert=True)


# ===== HAYDOVCHI RO'YXATDAN O'TISH =====

@router.message(DriverRegistration.waiting_for_fullname)
async def driver_fullname_handler(message: Message, state: FSMContext):
    """Haydovchi ism-familiya"""
    try:
        fullname = message.text.strip()
        
        if not validate_fullname(fullname):
            await message.answer(
                "❌ Ism-familiya noto'g'ri!\n"
                "Faqat harflar va bo'sh joy ishlatilishi mumkin.\n"
                "Maksimal 40 ta belgi.\n\n"
                "Qaytadan kiriting:"
            )
            return
        
        await state.update_data(fullname=fullname)
        
        text = "📱 Telefon raqamingizni yuboring:\n(+998XXXXXXXXX formatida yoki 9 xonali raqam)"
        await message.answer(text, reply_markup=request_phone_keyboard())
        await state.set_state(DriverRegistration.waiting_for_phone)
    
    except Exception as e:
        logger.error(f"Error in driver_fullname_handler: {e}")
        await message.answer("❌ Xatolik yuz berdi. /start bosing.")


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
            phone = message.text.strip() if message.text else ""
        
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
        await message.answer("❌ Xatolik yuz berdi. /start bosing.")


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
            db_manager.create_user(
                db=db,
                user_id=user_id,
                fullname=fullname,
                phone=phone,
                user_type="driver",
                car_model=car_model,
                telegram_name=telegram_name
            )
            
            # GROUP1 ga yuborish
            group_text = (
                "🚖 <b>YANGI HAYDOVCHI</b>\n\n"
                f"👤 Ism: {fullname}\n"
                f"📞 Tel: {phone}\n"
                f"🚗 Mashina: {car_model}\n"
                f"📱 Telegram: @{telegram_name} \n"
                f"🆔 ID: {user_id}"
            )
            
            try:
                await message.bot.send_message(config.GROUP1, group_text)
            except Exception as e:
                logger.error(f"Error sending to GROUP1: {e}")
            
            # Foydalanuvchiga xabar
            success_text = (
                "✅ <b>Ro'yxatdan o'tish muvaffaqiyatli tugadi!</b>\n\n"
                f"👤 Ism: {fullname}\n"
                f"📞 Telefon: {phone}\n"
                f"🚗 Mashina: {car_model}\n\n"
                f"Buyurtmalar {config.GROUP3} guruhida keladi.\n"
                f"Buyurtmani qabul qilish uchun \"✅ Qabul qilish\" tugmasini bosing."
            )
            await message.answer(success_text)
            
        finally:
            db.close()
        
        # State'ni tozalash
        await state.clear()
    
    except Exception as e:
        logger.error(f"Error in driver_car_model_handler: {e}")
        await message.answer("❌ Xatolik yuz berdi. /start bosing.")


# ===== YO'LOVCHI RO'YXATDAN O'TISH =====

@router.message(PassengerRegistration.waiting_for_fullname)
async def passenger_fullname_handler(message: Message, state: FSMContext):
    """Yo'lovchi ism-familiya"""
    try:
        fullname = message.text.strip()
        
        if not validate_fullname(fullname):
            await message.answer(
                "❌ Ism-familiya noto'g'ri!\n"
                "Faqat harflar va bo'sh joy ishlatilishi mumkin.\n"
                "Maksimal 40 ta belgi.\n\n"
                "Qaytadan kiriting:"
            )
            return
        
        await state.update_data(fullname=fullname)
        
        text = "📱 Telefon raqamingizni yuboring:\n(+998XXXXXXXXX formatida yoki 9 xonali raqam)"
        await message.answer(text, reply_markup=request_phone_keyboard())
        await state.set_state(PassengerRegistration.waiting_for_phone)
    
    except Exception as e:
        logger.error(f"Error in passenger_fullname_handler: {e}")
        await message.answer("❌ Xatolik yuz berdi. /start bosing.")


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
            phone = message.text.strip() if message.text else ""
        
        if not validate_phone(phone):
            await message.answer(
                "❌ Telefon raqam noto'g'ri!\n"
                "+998XXXXXXXXX yoki 9 xonali raqam kiriting.\n\n"
                "Qaytadan kiriting:"
            )
            return
        
        phone = format_phone(phone)
        await state.update_data(phone=phone)
        
        text = (
            "📍 <b>Lokatsiyangizni yuboring</b>\n\n"
            "Iltimos, quyidagi tugma orqali yoki telegramdan lokatsiya yuboring:"
        )
        await message.answer(text, reply_markup=request_location_keyboard())
        await state.set_state(PassengerRegistration.waiting_for_location)
    
    except Exception as e:
        logger.error(f"Error in passenger_phone_handler: {e}")
        await message.answer("❌ Xatolik yuz berdi. /start bosing.")


@router.message(PassengerRegistration.waiting_for_location)
async def passenger_location_handler(message: Message, state: FSMContext):
    """Yo'lovchi lokatsiya"""
    try:
        # Lokatsiya yuborilganmi tekshirish
        if not message.location:
            await message.answer(
                "❌ Iltimos, lokatsiya yuboring!\n\n"
                "Quyidagi tugmani bosing yoki telegramdan lokatsiya yuboring."
            )
            return
        
        latitude = str(message.location.latitude)
        longitude = str(message.location.longitude)
        
        # Ma'lumotlarni olish
        data = await state.get_data()
        fullname = data.get("fullname")
        phone = data.get("phone")
        user_id = message.from_user.id
        telegram_name = message.from_user.username or message.from_user.first_name
        
        # Database'ga saqlash
        db = get_db()
        try:
            db_manager.create_user(
                db=db,
                user_id=user_id,
                fullname=fullname,
                phone=phone,
                user_type="passenger",
                area=None,
                latitude=latitude,
                longitude=longitude,
                telegram_name=telegram_name
            )
            
            # GROUP2 ga yuborish (lokatsiya bilan)
            group_text = (
                "🧍‍♂️ <b>YANGI YO'LOVCHI</b>\n\n"
                f"👤 Ism: {fullname}\n"
                f"📞 Tel: {phone}\n"
                f"📍 Lokatsiya: {latitude}, {longitude}\n"
                f"📱 Telegram: @{telegram_name}\n"
                f"🆔 ID: {user_id}"
            )
            
            try:
                await message.bot.send_message(config.GROUP2, group_text)
            except Exception as e:
                logger.error(f"Error sending to GROUP2: {e}")
            
            # Foydalanuvchiga xabar
            success_text = (
                "✅ <b>Ro'yxatdan o'tish muvaffaqiyatli tugadi!</b>\n\n"
                f"👤 Ism: {fullname}\n"
                f"📞 Telefon: {phone}\n"
                f"📍 Lokatsiya saqlandi\n\n"
                "Kerakli xizmatni tanlang:"
            )
            await message.answer(success_text, reply_markup=services_keyboard())
            
        finally:
            db.close()
        
        # State'ni tozalash
        await state.clear()
    
    except Exception as e:
        logger.error(f"Error in passenger_area_handler: {e}")
        await message.answer("❌ Xatolik yuz berdi. /start bosing.")
