"""
Admin handler - Admin panel va statistika
"""
import logging
from datetime import date, datetime
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
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


@router.message(F.text == "📢 Kanallar boshqaruvi")
async def channels_management_handler(message: Message, state: FSMContext):
    """Kanallar boshqaruvini ko'rsatish"""
    try:
        if not is_admin(message.from_user.id):
            await message.answer("❌ Sizda admin huquqlari yo'q!")
            return
        
        await state.clear()
        
        db = get_db()
        try:
            # Barcha kanallarni olish
            channels = db_manager.get_all_channels(db)
            
            text = (
                "📢 <b>KANALLAR BOSHQARUVI</b>\n\n"
                "Majburiy obuna kanallari:\n"
            )
            
            if channels:
                text += f"Jami: {len(channels)} ta kanal\n\n"
                for idx, channel in enumerate(channels, 1):
                    text += f"{idx}. {channel.channel_name}\n"
                    text += f"   ID: <code>{channel.channel_id}</code>\n"
                    text += f"   Qo'shgan: {channel.added_by}\n"
                    text += f"   Sana: {channel.created_at.strftime('%d.%m.%Y %H:%M')}\n\n"
            else:
                text += "Hozircha kanallar yo'q.\n\n"
            
            text += "Kanallarni boshqarish uchun quyidagi tugmalardan foydalaning:"
            
            keyboard = channels_list_keyboard(channels)
            await message.answer(text, reply_markup=keyboard)
        
        finally:
            db.close()
    
    except Exception as e:
        logger.error(f"Error in channels_management_handler: {e}")
        await message.answer("❌ Xatolik yuz berdi.")


@router.callback_query(F.data == "add_channel")
async def add_channel_callback(callback: CallbackQuery, state: FSMContext):
    """Kanal qo'shish"""
    try:
        if not is_admin(callback.from_user.id):
            await callback.answer("❌ Sizda admin huquqlari yo'q!", show_alert=True)
            return
        
        await callback.answer()
        
        text = (
            "➕ <b>KANAL QO'SHISH</b>\n\n"
            "Kanal username yoki ID ni yuboring:\n\n"
            "📝 <b>To'g'ri formatlar:</b>\n"
            "• <code>@mychannel</code> - Username\n"
            "• <code>mychannel</code> - Username (@ siz)\n"
            "• <code>https://t.me/mychannel</code> - URL\n"
            "• <code>-1001234567890</code> - Raqamli ID\n\n"
            "❌ Bekor qilish uchun /cancel yozing"
        )
        await callback.message.answer(text)
        await state.set_state(AdminStates.waiting_for_channel)
    
    except Exception as e:
        logger.error(f"Error in add_channel_callback: {e}")
        await callback.message.answer("❌ Xatolik yuz berdi.")


@router.message(AdminStates.waiting_for_channel)
async def channel_input_handler(message: Message, state: FSMContext):
    """Kanal qo'shish - kanal ID kiritish"""
    try:
        if not is_admin(message.from_user.id):
            await message.answer("❌ Sizda admin huquqlari yo'q!")
            await state.clear()
            return
        
        # Bekor qilish
        if message.text and message.text.strip().lower() == "/cancel":
            await state.clear()
            await message.answer("❌ Bekor qilindi.", reply_markup=admin_keyboard())
            return
        
        channel_input = message.text.strip()
        
        # Kanal ID validatsiya
        if not channel_input:
            await message.answer("❌ Kanal username bo'sh bo'lishi mumkin emas!")
            return
        
        # Username formatini tekshirish va normalizatsiya qilish
        if channel_input.startswith("@"):
            # Username: @mychannel
            channel_id = channel_input
        elif channel_input.startswith("http"):
            # URL: https://t.me/mychannel
            if "t.me/" in channel_input:
                username = channel_input.split("t.me/")[-1].split("/")[0]
                channel_id = f"@{username}"
            else:
                await message.answer("❌ Kanal URL noto'g'ri!")
                return
        elif channel_input.lstrip("-").isdigit():
            # Raqamli ID: -1001234567890
            channel_id = channel_input
        else:
            # Username @ belgisisiz: mychannel -> @mychannel
            channel_id = f"@{channel_input}"
        
        # Bot kanalda adminmi tekshirish
        try:
            from main import bot
            chat = await bot.get_chat(channel_id)
            
            # Kanal yoki supergrup ekanligini tekshirish
            if chat.type not in ["channel", "supergroup"]:
                await message.answer("❌ Bu kanal yoki guruh emas!")
                return
            
            channel_name = chat.title or chat.username or channel_id
            
            # Bot adminmi tekshirish
            bot_member = await bot.get_chat_member(channel_id, bot.id)
            if bot_member.status not in ["administrator", "creator"]:
                await message.answer(
                    "❌ Bot bu kanalda admin emas!\n"
                    "Botni avval kanal adminlariga qo'shing."
                )
                return
        
        except Exception as e:
            logger.error(f"Error checking channel {channel_id}: {e}")
            await message.answer(
                "❌ Kanalga ulanishda xatolik!\n"
                "Kanal ID to'g'riligini va bot kanalda adminligini tekshiring."
            )
            return
        
        # Kanalni bazaga qo'shish
        db = get_db()
        try:
            # Kanal mavjudmi tekshirish
            existing_channels = db_manager.get_all_channels(db)
            for ch in existing_channels:
                if ch.channel_id == channel_id:
                    await message.answer("❌ Bu kanal allaqachon qo'shilgan!")
                    return
            
            # Qo'shish
            added_by = message.from_user.full_name or f"User_{message.from_user.id}"
            success = db_manager.add_channel(db, channel_id, channel_name, added_by)
            
            if success:
                await state.clear()
                
                text = (
                    "✅ <b>Kanal muvaffaqiyatli qo'shildi!</b>\n\n"
                    f"📢 Kanal: {channel_name}\n"
                    f"🆔 ID: <code>{channel_id}</code>\n\n"
                    "Endi foydalanuvchilar bu kanalga obuna bo'lishlari shart."
                )
                await message.answer(text, reply_markup=admin_keyboard())
                
                # Yangilangan ro'yxatni ko'rsatish
                channels = db_manager.get_all_channels(db)
                keyboard = channels_list_keyboard(channels)
                await message.answer(
                    "📢 <b>Yangilangan kanallar ro'yxati:</b>",
                    reply_markup=keyboard
                )
            else:
                await message.answer("❌ Kanalni qo'shishda xatolik yuz berdi.")
        
        finally:
            db.close()
    
    except Exception as e:
        logger.error(f"Error in channel_input_handler: {e}")
        await message.answer("❌ Xatolik yuz berdi.")
        await state.clear()


@router.callback_query(F.data.startswith("delete_channel_"))
async def delete_channel_callback(callback: CallbackQuery, state: FSMContext):
    """Kanalni o'chirish"""
    try:
        if not is_admin(callback.from_user.id):
            await callback.answer("❌ Sizda admin huquqlari yo'q!", show_alert=True)
            return
        
        # Channel ID olish
        channel_db_id = int(callback.data.split("_")[2])
        
        db = get_db()
        try:
            # Kanalni topish
            channels = db_manager.get_all_channels(db)
            channel_to_delete = None
            for ch in channels:
                if ch.id == channel_db_id:
                    channel_to_delete = ch
                    break
            
            if not channel_to_delete:
                await callback.answer("❌ Kanal topilmadi!", show_alert=True)
                return
            
            # O'chirish
            success = db_manager.delete_channel(db, channel_to_delete.channel_id)
            
            if success:
                await callback.answer("✅ Kanal o'chirildi!", show_alert=True)
                
                # Yangilangan ro'yxatni ko'rsatish
                remaining_channels = db_manager.get_all_channels(db)
                
                text = (
                    "✅ <b>Kanal o'chirildi!</b>\n\n"
                    f"📢 Kanal: {channel_to_delete.channel_name}\n"
                    f"🆔 ID: <code>{channel_to_delete.channel_id}</code>\n\n"
                    "Yangilangan kanallar ro'yxati:"
                )
                
                keyboard = channels_list_keyboard(remaining_channels)
                await callback.message.edit_text(text, reply_markup=keyboard)
            else:
                await callback.answer("❌ Kanalni o'chirishda xatolik!", show_alert=True)
        
        finally:
            db.close()
    
    except Exception as e:
        logger.error(f"Error in delete_channel_callback: {e}")
        await callback.answer("❌ Xatolik yuz berdi!", show_alert=True)

