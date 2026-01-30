import logging
from datetime import date, datetime
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from database import get_db, db_manager
from keyboards import admin_keyboard, services_keyboard,channels_list_keyboard,users_list_keyboard
from utils import format_date
from states import AdminStates
from config import config
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

logger = logging.getLogger(__name__)

router = Router()


def is_admin(user_id: int) -> bool:
    return user_id in config.ADMIN_IDS


@router.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext):

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
    try:
        if not is_admin(message.from_user.id):
            await message.answer("❌ Sizda admin huquqlari yo'q!")
            return
        
        await state.clear()
        
        db = get_db()
        try:
            stats_list = db_manager.get_daily_stats(db)
            
            if not stats_list:
                await message.answer("📊 Bugun hali statistika yo'q.")
                return
            
            total_orders = sum(s.orders_count for s in stats_list)
            total_confirmed = sum(s.confirmed_count for s in stats_list)
            total_rejected = sum(s.rejected_count for s in stats_list)
            
            passengers = [s for s in stats_list if s.user_type == "passenger"]
            passengers.sort(key=lambda x: x.orders_count, reverse=True)
            
            drivers_confirmed = [s for s in stats_list if s.user_type == "driver"]
            drivers_confirmed.sort(key=lambda x: x.confirmed_count, reverse=True)
            
            drivers_rejected = [s for s in stats_list if s.user_type == "driver"]
            drivers_rejected.sort(key=lambda x: x.rejected_count, reverse=True)
            
            text = (
                f"📊 <b>BUGUNGI STATISTIKA</b>\n"
                f"📅 Sana: {date.today().strftime('%d.%m.%Y')}\n\n"
                f"📈 <b>Umumiy:</b>\n"
                f"Buyurtmalar: {total_orders}\n"
                f"Tasdiqlangan: {total_confirmed}\n"
                f"Rad etilgan: {total_rejected}\n\n"
            )
            
            if passengers:
                text += "🧍‍♂️ <b>Yo'lovchilar (buyurtmalar):</b>\n"
                for s in passengers[:10]:  # Top 10
                    text += f"{s.user_name}: {s.orders_count} ta\n"
                text += "\n"
            
            if drivers_confirmed:
                text += "🚖 <b>Haydovchilar (tasdiqlangan):</b>\n"
                for s in drivers_confirmed[:10]:  # Top 10
                    if s.confirmed_count > 0:
                        text += f"{s.user_name}: {s.confirmed_count} ta\n"
                text += "\n"
            
            if drivers_rejected:
                rejected_list = [s for s in drivers_rejected if s.rejected_count > 0]
                if rejected_list:
                    text += "❌ <b>Haydovchilar (rad etilgan):</b>\n"
                    for s in rejected_list[:10]:  # Top 10
                        text += f"{s.user_name}: {s.rejected_count} ta\n"
            
            await message.answer(text)
        
        finally:
            db.close()
    
    except Exception as e:
        logger.error(f"Error in today_stats_handler: {e}")
        await message.answer("❌ Xatolik yuz berdi.")


@router.message(F.text == "📅 Boshqa kun statistikasi")
async def other_date_stats_handler(message: Message, state: FSMContext):
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
    try:
        if not is_admin(message.from_user.id):
            await message.answer("❌ Sizda admin huquqlari yo'q!")
            await state.clear()
            return
        
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
            stats_list = db_manager.get_daily_stats(db, target_date.date())
            
            if not stats_list:
                await message.answer(f"📊 {target_date.strftime('%d.%m.%Y')} kuni statistika yo'q.")
                return
            
            total_orders = sum(s.orders_count for s in stats_list)
            total_confirmed = sum(s.confirmed_count for s in stats_list)
            total_rejected = sum(s.rejected_count for s in stats_list)
            
            passengers = [s for s in stats_list if s.user_type == "passenger"]
            passengers.sort(key=lambda x: x.orders_count, reverse=True)
            
            drivers_confirmed = [s for s in stats_list if s.user_type == "driver"]
            drivers_confirmed.sort(key=lambda x: x.confirmed_count, reverse=True)
            
            drivers_rejected = [s for s in stats_list if s.user_type == "driver"]
            drivers_rejected.sort(key=lambda x: x.rejected_count, reverse=True)
            
            text = (
                f"📊 <b>STATISTIKA</b>\n"
                f"📅 Sana: {target_date.strftime('%d.%m.%Y')}\n\n"
                f"📈 <b>Umumiy:</b>\n"
                f"Buyurtmalar: {total_orders}\n"
                f"Tasdiqlangan: {total_confirmed}\n"
                f"Rad etilgan: {total_rejected}\n\n"
            )
            
            if passengers:
                text += "🧍‍♂️ <b>Yo'lovchilar (buyurtmalar):</b>\n"
                for s in passengers[:10]:
                    text += f"{s.user_name}: {s.orders_count} ta\n"
                text += "\n"
            
            if drivers_confirmed:
                text += "🚖 <b>Haydovchilar (tasdiqlangan):</b>\n"
                for s in drivers_confirmed[:10]: 
                    if s.confirmed_count > 0:
                        text += f"{s.user_name}: {s.confirmed_count} ta\n"
                text += "\n"
            
            if drivers_rejected:
                rejected_list = [s for s in drivers_rejected if s.rejected_count > 0]
                if rejected_list:
                    text += "❌ <b>Haydovchilar (rad etilgan):</b>\n"
                    for s in rejected_list[:10]: 
                        text += f"{s.user_name}: {s.rejected_count} ta\n"
            
            await message.answer(text, reply_markup=admin_keyboard())
        
        finally:
            db.close()
    
    except Exception as e:
        logger.error(f"Error in date_stats_handler: {e}")
        await message.answer("❌ Xatolik yuz berdi.")
        await state.clear()


@router.message(F.text == "🔙 Asosiy menyu")
async def back_to_main_menu_handler(message: Message, state: FSMContext):
    try:
        await state.clear()
        
        user_id = message.from_user.id
        
        if is_admin(user_id):
            text = "👨‍💼 Admin rejimi o'chirildi.\n\n/admin - Admin panelga qaytish"
            await message.answer(text)
            return
        
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
    try:
        if not is_admin(message.from_user.id):
            await message.answer("❌ Sizda admin huquqlari yo'q!")
            return
        
        await state.clear()
        
        db = get_db()
        try:
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
    try:
        if not is_admin(callback.from_user.id):
            await callback.answer("❌ Sizda admin huquqlari yo'q!", show_alert=True)
            return
        
        await callback.answer()
        
        text = (
            "➕ <b>KANAL QO'SHISH</b>\n\n"
            "Kanal username yoki ID ni yuboring:\n\n"
            "📝 <b>To'g'ri formatlar:</b>\n"
            "<code>@mychannel</code> - Username\n"
            "<code>mychannel</code> - Username (@ siz)\n"
            "<code>https://t.me/mychannel</code> - URL\n"
            "<code>-1001234567890</code> - Raqamli ID\n\n"
            "❌ Bekor qilish uchun /cancel yozing"
        )
        await callback.message.answer(text)
        await state.set_state(AdminStates.waiting_for_channel)
    
    except Exception as e:
        logger.error(f"Error in add_channel_callback: {e}")
        await callback.message.answer("❌ Xatolik yuz berdi.")


@router.message(AdminStates.waiting_for_channel)
async def channel_input_handler(message: Message, state: FSMContext):
    try:
        if not is_admin(message.from_user.id):
            await message.answer("❌ Sizda admin huquqlari yo'q!")
            await state.clear()
            return
        
        if message.text and message.text.strip().lower() == "/cancel":
            await state.clear()
            await message.answer("❌ Bekor qilindi.", reply_markup=admin_keyboard())
            return
        
        channel_input = message.text.strip()
        
        if not channel_input:
            await message.answer("❌ Kanal username bo'sh bo'lishi mumkin emas!")
            return
        
        if channel_input.startswith("@"):
            channel_id = channel_input
        elif channel_input.startswith("http"):
            if "t.me/" in channel_input:
                username = channel_input.split("t.me/")[-1].split("/")[0]
                channel_id = f"@{username}"
            else:
                await message.answer("❌ Kanal URL noto'g'ri!")
                return
        elif channel_input.lstrip("-").isdigit():
            channel_id = channel_input
        else:
            channel_id = f"@{channel_input}"
        
        try:
            from main import bot
            chat = await bot.get_chat(channel_id)
            
            if chat.type not in ["channel", "supergroup"]:
                await message.answer("❌ Bu kanal yoki guruh emas!")
                return
            
            channel_name = chat.title or chat.username or channel_id
            
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
        
        db = get_db()
        try:
            existing_channels = db_manager.get_all_channels(db)
            for ch in existing_channels:
                if ch.channel_id == channel_id:
                    await message.answer("❌ Bu kanal allaqachon qo'shilgan!")
                    return
            
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
    try:
        if not is_admin(callback.from_user.id):
            await callback.answer("❌ Sizda admin huquqlari yo'q!", show_alert=True)
            return
        
        channel_db_id = int(callback.data.split("_")[2])
        
        db = get_db()
        try:
            channels = db_manager.get_all_channels(db)
            channel_to_delete = None
            for ch in channels:
                if ch.id == channel_db_id:
                    channel_to_delete = ch
                    break
            
            if not channel_to_delete:
                await callback.answer("❌ Kanal topilmadi!", show_alert=True)
                return
            
            success = db_manager.delete_channel(db, channel_to_delete.channel_id)
            
            if success:
                await callback.answer("✅ Kanal o'chirildi!", show_alert=True)
                
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



@router.message(F.text == "👥 Foydalanuvchilar")
async def admin_users_handler(message: Message, state: FSMContext):
    try:
        if not is_admin(message.from_user.id):
            await message.answer("❌ Sizda admin huquqlari yo'q!")
            return

        await state.clear()
        page = 1
        limit = 10

        db = get_db()
        try:
            users, total, total_pages = db_manager.get_users_page(db, page=page, limit=limit)
        finally:
            db.close()

        if not users:
            await message.answer("👥 Hozircha foydalanuvchilar yo'q.")
            return

        text = f"👥 <b>FOYDALANUVCHILAR</b>\nJami: {total} ta\n\nBirini tanlang:"
        await message.answer(text, reply_markup=users_list_keyboard(users, page, total_pages))

    except Exception as e:
        logger.error(f"Error in admin_users_handler: {e}")
        await message.answer("❌ Xatolik yuz berdi.")



@router.callback_query(F.data.startswith("admin_users_page:"))
async def admin_users_page_callback(callback: CallbackQuery):
    try:
        if not is_admin(callback.from_user.id):
            await callback.answer("❌ Admin emassiz!", show_alert=True)
            return

        page = int(callback.data.split(":")[1])
        limit = 10

        db = get_db()
        try:
            users, total, total_pages = db_manager.get_users_page(db, page=page, limit=limit)
        finally:
            db.close()

        if not users:
            await callback.answer("Foydalanuvchi topilmadi", show_alert=True)
            return

        text = f"👥 <b>FOYDALANUVCHILAR</b>\nJami: {total} ta\n\nBirini tanlang:"
        await callback.message.edit_text(text, reply_markup=users_list_keyboard(users, page, total_pages))
        await callback.answer()

    except Exception as e:
        logger.error(f"Error in admin_users_page_callback: {e}")
        await callback.answer("❌ Xatolik!", show_alert=True)


@router.callback_query(F.data.startswith("admin_user:"))
async def admin_user_detail_callback(callback: CallbackQuery):
    try:
        if not is_admin(callback.from_user.id):
            await callback.answer("❌ Admin emassiz!", show_alert=True)
            return

        user_id = int(callback.data.split(":")[1])

        db = get_db()
        try:
            user = db_manager.get_user(db, user_id)
            if not user:
                await callback.answer("❌ User topilmadi!", show_alert=True)
                return

            orders, confirmed, rejected = db_manager.get_user_total_stats(db, user_id)
        finally:
            db.close()

        # ✅ user bor bo‘lgandan keyin ishlatamiz
        is_banned = getattr(user, "is_banned", False)
        ban_text = "✅ Unban qilish" if is_banned else "🚫 Ban qilish"
        ban_cb = f"admin_toggle_ban:{user.user_id}"

        role = "🚖 Haydovchi" if user.user_type == "driver" else "🧍‍♂️ Yo'lovchi"
        extra = ""
        if user.user_type == "driver":
            extra = f"🚗 Mashina: {user.car_model or '-'}\n"
        else:
            extra = f"📍 Hudud: {user.area or '-'}\n"

        text = (
            f"👤 <b>FOYDALANUVCHI</b>\n\n"
            f"🆔 ID: <code>{user.user_id}</code>\n"
            f"👤 Ism: {user.fullname}\n"
            f"📞 Tel: {user.phone}\n"
            f"👥 Rol: {role}\n"
            f"{extra}\n"
            f"📊 <b>Umumiy statistika:</b>\n"
            f"Buyurtmalar: {orders}\n"
            f"Tasdiqlangan: {confirmed}\n"
            f"Rad etilgan: {rejected}\n"
        )

        back_kb = InlineKeyboardBuilder()
        back_kb.row(InlineKeyboardButton(text=ban_text, callback_data=ban_cb))
        back_kb.row(InlineKeyboardButton(text="🔙 Foydalanuvchilar", callback_data="admin_users_page:1"))
        back_kb.row(InlineKeyboardButton(text="🔙 Admin panel", callback_data="admin_back"))

        await callback.message.edit_text(text, reply_markup=back_kb.as_markup())
        await callback.answer()

    except Exception as e:
        logger.error(f"Error in admin_user_detail_callback: {e}")
        await callback.answer("❌ Xatolik!", show_alert=True)

@router.callback_query(F.data == "admin_back")
async def admin_back_callback(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "👨‍💼 <b>ADMIN PANEL</b>\n\nKerakli bo'limni tanlang:",
        reply_markup=None
    )
    await callback.message.answer("👇", reply_markup=admin_keyboard())
    await callback.answer()


@router.callback_query(F.data == "noop")
async def noop_callback(callback: CallbackQuery):
    await callback.answer()


@router.callback_query(F.data.startswith("admin_toggle_ban:"))
async def admin_toggle_ban_callback(callback: CallbackQuery):
    try:
        if not is_admin(callback.from_user.id):
            await callback.answer("❌ Admin emassiz!", show_alert=True)
            return

        target_user_id = int(callback.data.split(":")[1])

        db = get_db()
        try:
            user = db_manager.get_user(db, target_user_id)
            if not user:
                await callback.answer("User topilmadi!", show_alert=True)
                return

            current = getattr(user, "is_banned", False)
            new_value = not current
            db_manager.set_user_ban(db, target_user_id, new_value)

        finally:
            db.close()

        await callback.answer("✅ Yangilandi!")
        
        callback.data = f"admin_user:{target_user_id}"
        await admin_user_detail_callback(callback)

    except Exception as e:
        logger.error(f"Error in admin_toggle_ban_callback: {e}")
        await callback.answer("❌ Xatolik!", show_alert=True)
