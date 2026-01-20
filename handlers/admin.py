"""
Admin Panel Handlers
Admin komandalarini boshqarish va statistika
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from sqlalchemy.orm import Session
import logging
from datetime import datetime, timedelta
import re

from config import config, UserRole
from states import AdminState
from keyboards import get_admin_menu_keyboard, get_back_button, format_statistics
from crud import (
    get_user_by_telegram_id,
    get_daily_stats,
    get_orders_by_date,
    get_all_drivers,
    get_all_passengers,
    log_admin_action
)
from database import Order, OrderStatus

logger = logging.getLogger(__name__)

router = Router()


def is_admin(user_id: int) -> bool:
    """Admin tekshirish"""
    return user_id in config.ADMIN_IDS


@router.message(Command("admin"))
async def admin_command(message: Message, db: Session):
    """Admin paneli"""
    
    if not is_admin(message.from_user.id):
        await message.answer("❌ Siz admin emassiz!")
        return
    
    admin_user = get_user_by_telegram_id(db, message.from_user.id)
    
    welcome_text = (
        "👨‍💼 <b>Admin Paneli</b>\n\n"
        f"Salom, admin {admin_user.first_name if admin_user else 'User'}!\n\n"
        "Quyidagi amallarni tanlang:"
    )
    
    await message.answer(
        welcome_text,
        reply_markup=get_admin_menu_keyboard()
    )
    
    # Log
    log_admin_action(db, message.from_user.id, "ADMIN_PANEL_OPENED")


@router.callback_query(F.data == "admin_today_stats")
async def today_stats(callback: CallbackQuery, db: Session):
    """Bugungi statistika"""
    await callback.answer()
    
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Siz admin emassiz", show_alert=True)
        return
    
    today = datetime.utcnow()
    stats = get_daily_stats(db, today)
    
    stats_text = format_statistics(stats)
    
    await callback.message.edit_text(
        f"📊 <b>Bugungi Statistika ({datetime.now().strftime('%d.%m.%Y')})</b>\n\n{stats_text}",
        reply_markup=get_back_button()
    )
    
    log_admin_action(db, callback.from_user.id, "VIEWED_TODAY_STATS")


@router.callback_query(F.data == "admin_date_stats")
async def date_stats_request(callback: CallbackQuery, state: FSMContext):
    """Istalgan sana bo'yicha statistika"""
    await callback.answer()
    
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Siz admin emassiz", show_alert=True)
        return
    
    await callback.message.edit_text(
        "📅 <b>Sana Tanlang</b>\n\n"
        "Format: <code>DD.MM.YYYY</code>\n"
        "Masalan: <code>15.01.2026</code>",
        reply_markup=None
    )
    
    await state.set_state(AdminState.waiting_for_stat_date)


@router.message(AdminState.waiting_for_stat_date)
async def process_date_stats(message: Message, state: FSMContext, db: Session):
    """Sana bo'yicha statistikani qayta ishlash"""
    
    if not is_admin(message.from_user.id):
        await message.answer("❌ Siz admin emassiz!")
        return
    
    date_str = message.text.strip()
    
    # Date format validatsiyasi
    try:
        stat_date = datetime.strptime(date_str, "%d.%m.%Y")
    except ValueError:
        await message.answer(
            "❌ Noto'g'ri format!\n\n"
            "To'g'ri format: <code>DD.MM.YYYY</code>\n"
            "Masalan: <code>15.01.2026</code>"
        )
        return
    
    stats = get_daily_stats(db, stat_date)
    stats_text = format_statistics(stats)
    
    await message.answer(
        f"📊 <b>Statistika - {stat_date.strftime('%d.%m.%Y')}</b>\n\n{stats_text}",
        reply_markup=get_back_button()
    )
    
    await state.clear()
    
    log_admin_action(
        db,
        message.from_user.id,
        "VIEWED_DATE_STATS",
        f"Date: {date_str}"
    )


@router.callback_query(F.data == "admin_users_info")
async def users_info(callback: CallbackQuery, db: Session):
    """Foydalanuvchiler haqida ma'lumot"""
    await callback.answer()
    
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Siz admin emassiz", show_alert=True)
        return
    
    drivers = get_all_drivers(db)
    passengers = get_all_passengers(db)
    
    users_text = (
        f"👥 <b>Foydalanuvchiler Haqida Ma'lumot</b>\n\n"
        f"🚖 <b>Haydovchilar:</b> {len(drivers)}\n"
        f"🧍 <b>Yo'lovchilar:</b> {len(passengers)}\n"
        f"👨‍💼 <b>Jami:</b> {len(drivers) + len(passengers)}\n\n"
        f"<b>Eng faol haydovchilar:</b>\n"
    )
    
    # Top 5 drivers by confirmed orders
    top_drivers = sorted(drivers, key=lambda x: x.confirmed_orders, reverse=True)[:5]
    for idx, driver in enumerate(top_drivers, 1):
        users_text += f"\n{idx}. {driver.first_name} - {driver.confirmed_orders} tasdiqlangan"
    
    await callback.message.edit_text(
        users_text,
        reply_markup=get_back_button()
    )
    
    log_admin_action(db, callback.from_user.id, "VIEWED_USERS_INFO")


@router.callback_query(F.data == "admin_active_orders")
async def active_orders(callback: CallbackQuery, db: Session):
    """Aktiv buyurtmalar"""
    await callback.answer()
    
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Siz admin emassiz", show_alert=True)
        return
    
    # Aktiv buyurtmalarni olish
    from sqlalchemy import select
    active_orders = db.query(Order).filter(
        Order.status.in_([OrderStatus.WAITING, OrderStatus.ACCEPTED])
    ).all()
    
    if not active_orders:
        await callback.message.edit_text(
            "✅ Hech qanday aktiv buyurtma yo'q",
            reply_markup=get_back_button()
        )
        return
    
    orders_text = (
        f"📋 <b>Aktiv Buyurtmalar ({len(active_orders)})</b>\n\n"
    )
    
    for order in active_orders[:10]:  # Birinchi 10 ta
        status_emoji = "⏳" if order.status == OrderStatus.WAITING else "👤"
        orders_text += (
            f"{status_emoji} ID: {order.order_id} | "
            f"Turi: {order.service_type} | "
            f"Vaqti: {order.created_at.strftime('%H:%M')}\n"
        )
    
    if len(active_orders) > 10:
        orders_text += f"\n... va {len(active_orders) - 10} ta ko'p"
    
    await callback.message.edit_text(
        orders_text,
        reply_markup=get_back_button()
    )
    
    log_admin_action(
        db,
        callback.from_user.id,
        "VIEWED_ACTIVE_ORDERS",
        f"Total: {len(active_orders)}"
    )


@router.callback_query(F.data == "admin_send_broadcast")
async def send_broadcast_prompt(callback: CallbackQuery, state: FSMContext):
    """Xabar yuborish uchun admin amaliyoti"""
    await callback.answer()
    
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Siz admin emassiz", show_alert=True)
        return
    
    await callback.message.edit_text(
        "📢 <b>Xabar Yuborish</b>\n\n"
        "Barcha foydalanuvchilarga yuborish uchun xabar kiriting:",
        reply_markup=None
    )
    
    await state.set_state(AdminState.waiting_for_action)


@router.callback_query(F.data == "back_to_menu")
async def back_to_admin_menu(callback: CallbackQuery, state: FSMContext):
    """Admin menyusiga qaytish"""
    await callback.answer()
    
    await callback.message.edit_text(
        "👨‍💼 <b>Admin Paneli</b>\n\nQuyidagi amallarni tanlang:",
        reply_markup=get_admin_menu_keyboard()
    )
    
    await state.clear()
