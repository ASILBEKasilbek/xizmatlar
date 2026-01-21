"""
Admin handler - Admin panel va statistika
"""
import logging
from datetime import date, datetime
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from database import get_db, db_manager
from keyboards import admin_keyboard, services_keyboard
from utils import format_date
from states import AdminStates
from config import config

logger = logging.getLogger(__name__)

router = Router()


def is_admin(user_id: int) -> bool:
    """Admin ekanligini tekshirish"""
    return user_id in config.ADMIN_IDS


@router.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext):
    """Admin panel"""
    try:
        if not is_admin(message.from_user.id):
            await message.answer("❌ Sizda admin huquqlari yo'q!")
            return
        
        await state.clear()
        
        text = (
            "👨‍💼 <b>ADMIN PANEL</b>\n\n"
            "Kerakli bo'limni tanlang:"
        )
        await message.answer(text, reply_markup=admin_keyboard())
    
    except Exception as e:
        logger.error(f"Error in cmd_admin: {e}")
        await message.answer("❌ Xatolik yuz berdi.")


@router.message(F.text == "📊 Bugungi statistika")
async def today_stats_handler(message: Message, state: FSMContext):
    """Bugungi statistika"""
    try:
        if not is_admin(message.from_user.id):
            await message.answer("❌ Sizda admin huquqlari yo'q!")
            return
        
        await state.clear()
        
        db = get_db()
        try:
            # Bugungi statistikani olish
            stats_list = db_manager.get_daily_stats(db)
            
            if not stats_list:
                await message.answer("📊 Bugun hali statistika yo'q.")
                return
            
            # Umumiy hisoblar
            total_orders = sum(s.orders_count for s in stats_list)
            total_confirmed = sum(s.confirmed_count for s in stats_list)
            total_rejected = sum(s.rejected_count for s in stats_list)
            
            # Yo'lovchilar statistikasi
            passengers = [s for s in stats_list if s.user_type == "passenger"]
            passengers.sort(key=lambda x: x.orders_count, reverse=True)
            
            # Haydovchilar statistikasi (tasdiqlangan)
            drivers_confirmed = [s for s in stats_list if s.user_type == "driver"]
            drivers_confirmed.sort(key=lambda x: x.confirmed_count, reverse=True)
            
            # Haydovchilar statistikasi (rad etilgan)
            drivers_rejected = [s for s in stats_list if s.user_type == "driver"]
            drivers_rejected.sort(key=lambda x: x.rejected_count, reverse=True)
            
            # Xabar yaratish
            text = (
                f"📊 <b>BUGUNGI STATISTIKA</b>\n"
                f"📅 Sana: {date.today().strftime('%d.%m.%Y')}\n\n"
                f"📈 <b>Umumiy:</b>\n"
                f"• Buyurtmalar: {total_orders}\n"
                f"• Tasdiqlangan: {total_confirmed}\n"
                f"• Rad etilgan: {total_rejected}\n\n"
            )
            
            # Yo'lovchilar
            if passengers:
                text += "🧍‍♂️ <b>Yo'lovchilar (buyurtmalar):</b>\n"
                for s in passengers[:10]:  # Top 10
                    text += f"• {s.user_name}: {s.orders_count} ta\n"
                text += "\n"
            
            # Haydovchilar (tasdiqlangan)
            if drivers_confirmed:
                text += "🚖 <b>Haydovchilar (tasdiqlangan):</b>\n"
                for s in drivers_confirmed[:10]:  # Top 10
                    if s.confirmed_count > 0:
                        text += f"• {s.user_name}: {s.confirmed_count} ta\n"
                text += "\n"
            
            # Haydovchilar (rad etilgan)
            if drivers_rejected:
                rejected_list = [s for s in drivers_rejected if s.rejected_count > 0]
                if rejected_list:
                    text += "❌ <b>Haydovchilar (rad etilgan):</b>\n"
                    for s in rejected_list[:10]:  # Top 10
                        text += f"• {s.user_name}: {s.rejected_count} ta\n"
            
            await message.answer(text)
        
        finally:
            db.close()
    
    except Exception as e:
        logger.error(f"Error in today_stats_handler: {e}")
        await message.answer("❌ Xatolik yuz berdi.")


@router.message(F.text == "📅 Boshqa kun statistikasi")
async def other_date_stats_handler(message: Message, state: FSMContext):
    """Boshqa kun statistikasi"""
    try:
        if not is_admin(message.from_user.id):
            await message.answer("❌ Sizda admin huquqlari yo'q!")
            return
        
        text = (
            "📅 <b>Boshqa kun statistikasi</b>\n\n"
            "Sanani DD.MM.YYYY formatida yuboring:\n"
            "(Masalan: 20.01.2026)"
        )
        await message.answer(text)
        await state.set_state(AdminStates.waiting_for_date)
    
    except Exception as e:
        logger.error(f"Error in other_date_stats_handler: {e}")
        await message.answer("❌ Xatolik yuz berdi.")


@router.message(AdminStates.waiting_for_date)
async def date_stats_handler(message: Message, state: FSMContext):
    """Sana bo'yicha statistika"""
    try:
        if not is_admin(message.from_user.id):
            await message.answer("❌ Sizda admin huquqlari yo'q!")
            await state.clear()
            return
        
        # Sanani parse qilish
        target_date = format_date(message.text.strip())
        
        if not target_date:
            await message.answer(
                "❌ Sana noto'g'ri!\n"
                "DD.MM.YYYY formatida yuboring (masalan: 20.01.2026)"
            )
            return
        
        await state.clear()
        
        db = get_db()
        try:
            # Sana bo'yicha statistikani olish
            stats_list = db_manager.get_daily_stats(db, target_date.date())
            
            if not stats_list:
                await message.answer(f"📊 {target_date.strftime('%d.%m.%Y')} kuni statistika yo'q.")
                return
            
            # Umumiy hisoblar
            total_orders = sum(s.orders_count for s in stats_list)
            total_confirmed = sum(s.confirmed_count for s in stats_list)
            total_rejected = sum(s.rejected_count for s in stats_list)
            
            # Yo'lovchilar statistikasi
            passengers = [s for s in stats_list if s.user_type == "passenger"]
            passengers.sort(key=lambda x: x.orders_count, reverse=True)
            
            # Haydovchilar statistikasi (tasdiqlangan)
            drivers_confirmed = [s for s in stats_list if s.user_type == "driver"]
            drivers_confirmed.sort(key=lambda x: x.confirmed_count, reverse=True)
            
            # Haydovchilar statistikasi (rad etilgan)
            drivers_rejected = [s for s in stats_list if s.user_type == "driver"]
            drivers_rejected.sort(key=lambda x: x.rejected_count, reverse=True)
            
            # Xabar yaratish
            text = (
                f"📊 <b>STATISTIKA</b>\n"
                f"📅 Sana: {target_date.strftime('%d.%m.%Y')}\n\n"
                f"📈 <b>Umumiy:</b>\n"
                f"• Buyurtmalar: {total_orders}\n"
                f"• Tasdiqlangan: {total_confirmed}\n"
                f"• Rad etilgan: {total_rejected}\n\n"
            )
            
            # Yo'lovchilar
            if passengers:
                text += "🧍‍♂️ <b>Yo'lovchilar (buyurtmalar):</b>\n"
                for s in passengers[:10]:  # Top 10
                    text += f"• {s.user_name}: {s.orders_count} ta\n"
                text += "\n"
            
            # Haydovchilar (tasdiqlangan)
            if drivers_confirmed:
                text += "🚖 <b>Haydovchilar (tasdiqlangan):</b>\n"
                for s in drivers_confirmed[:10]:  # Top 10
                    if s.confirmed_count > 0:
                        text += f"• {s.user_name}: {s.confirmed_count} ta\n"
                text += "\n"
            
            # Haydovchilar (rad etilgan)
            if drivers_rejected:
                rejected_list = [s for s in drivers_rejected if s.rejected_count > 0]
                if rejected_list:
                    text += "❌ <b>Haydovchilar (rad etilgan):</b>\n"
                    for s in rejected_list[:10]:  # Top 10
                        text += f"• {s.user_name}: {s.rejected_count} ta\n"
            
            await message.answer(text, reply_markup=admin_keyboard())
        
        finally:
            db.close()
    
    except Exception as e:
        logger.error(f"Error in date_stats_handler: {e}")
        await message.answer("❌ Xatolik yuz berdi.")
        await state.clear()


@router.message(F.text == "🔙 Asosiy menyu")
async def back_to_main_menu_handler(message: Message, state: FSMContext):
    """Asosiy menyuga qaytish"""
    try:
        await state.clear()
        
        user_id = message.from_user.id
        
        # Admin uchun
        if is_admin(user_id):
            text = "👨‍💼 Admin rejimi o'chirildi.\n\n/admin - Admin panelga qaytish"
            await message.answer(text)
            return
        
        # Oddiy foydalanuvchi uchun
        db = get_db()
        try:
            user = db_manager.get_user(db, user_id)
            
            if user and user.user_type == "passenger":
                text = "🔙 Asosiy menyuga qaytdingiz.\n\nKerakli xizmatni tanlang:"
                await message.answer(text, reply_markup=services_keyboard())
            else:
                text = "🔙 Asosiy menyuga qaytdingiz."
                await message.answer(text)
        
        finally:
            db.close()
    
    except Exception as e:
        logger.error(f"Error in back_to_main_menu_handler: {e}")
        await message.answer("❌ Xatolik yuz berdi.")
