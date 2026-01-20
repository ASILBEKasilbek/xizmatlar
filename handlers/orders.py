"""
Order Management Handlers
Buyurtma yaratish, qabul qilish, tasdiqlash
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.orm import Session
import logging
from datetime import datetime

from config import config, ServiceType, OrderStatus, UserRole
from states import OrderState
from keyboards import (
    get_taxi_order_confirmation_keyboard,
    get_driver_confirm_keyboard,
    get_service_keyboard,
    get_back_button,
    format_order_message
)
from crud import (
    get_user_by_telegram_id,
    create_order,
    get_order_by_id,
    accept_order,
    decline_order,
    confirm_order,
    cancel_order,
    can_place_order,
    set_cooldown,
    get_active_taxi_order_for_user,
    get_waiting_orders_by_service,
    get_all_drivers
)

logger = logging.getLogger(__name__)

router = Router()


@router.callback_query(F.data == "select_service")
async def select_service(callback: CallbackQuery, state: FSMContext, db: Session):
    """Xizmat tanlash"""
    await callback.answer()
    
    user_id = callback.from_user.id
    user = get_user_by_telegram_id(db, user_id)
    
    if not user or user.role != UserRole.PASSENGER:
        await callback.answer("❌ Siz yo'lovchi hisobiga kira olmadingiz", show_alert=True)
        return
    
    await callback.message.edit_text(
        "🎯 Quyidagi xizmatlardan birini tanlang:",
        reply_markup=get_service_keyboard()
    )


@router.callback_query(F.data == "service_taxi")
async def order_taxi(callback: CallbackQuery, state: FSMContext, db: Session):
    """Taxi buyurtma berish"""
    await callback.answer()
    
    user_id = callback.from_user.id
    user = get_user_by_telegram_id(db, user_id)
    
    if not user:
        await callback.answer("❌ Avval ro'yxatdan o'ting", show_alert=True)
        return
    
    # Taxi uchun shartlarni tekshirish
    can_order, reason = can_place_order(db, user.user_id, ServiceType.TAXI)
    
    if not can_order:
        await callback.answer(reason, show_alert=True)
        return
    
    # Buyurtma yaratish
    order = create_order(
        db=db,
        user_id=user.user_id,
        service_type=ServiceType.TAXI,
        phone_number=user.phone_number,
        description="Taxi buyurtmasi"
    )
    
    # Xabarni haydovchilar guruhiga yuborish
    order_text = (
        f"🚕 <b>YANGI TAXI BUYURTMASI!</b>\n\n"
        f"📋 Buyurtma ID: <code>{order.order_id}</code>\n"
        f"⏰ Vaqti: {order.created_at.strftime('%H:%M:%S')}\n"
        f"📞 Telefon: <code>{user.phone_number}</code>\n"
        f"👤 Yo'lovchi: {user.first_name} {user.last_name or ''}\n\n"
        f"⏳ <b>7 daqiqada javob yoki bekor qilinadi</b>"
    )
    
    sent_message = await callback.bot.send_message(
        chat_id=config.DRIVERS_ORDERS_GROUP_ID,
        text=order_text,
        reply_markup=get_taxi_order_confirmation_keyboard(order.order_id),
        parse_mode="HTML"
    )
    
    # Order ma'lumotlarini yangilash
    from crud import update_order_group_info
    # Order message ID ni yangilash
    from crud import update_order_message_id
    # Alternative: directly update
    order.message_id = sent_message.message_id
    order.group_id = config.DRIVERS_ORDERS_GROUP_ID
    db.commit()
    
    # Yo'lovchiga xabar
    await callback.message.edit_text(
        f"✅ <b>Taxi Buyurtmasi Berildi!</b>\n\n"
        f"📋 Buyurtma ID: {order.order_id}\n"
        f"⏳ Haydovchi aniqlashi uchun 7 daqiqa kutilmoqda...\n\n"
        f"Yo'lovchiga ko'rsatadigan telefon: <code>{user.phone_number}</code>",
        reply_markup=get_back_button()
    )
    
    # Cooldown o'rnatish
    set_cooldown(db, user.user_id, ServiceType.TAXI)
    
    logger.info(f"Taxi order created: {order.order_id} by user {user_id}")


@router.callback_query(F.data.startswith("service_bread"))
async def order_bread(callback: CallbackQuery, state: FSMContext, db: Session):
    """Non buyurtma berish"""
    await callback.answer()
    
    user_id = callback.from_user.id
    user = get_user_by_telegram_id(db, user_id)
    
    if not user:
        await callback.answer("❌ Avval ro'yxatdan o'ting", show_alert=True)
        return
    
    # Cooldown tekshirish
    can_order, reason = can_place_order(db, user.user_id, ServiceType.BREAD)
    
    if not can_order:
        await callback.answer(reason, show_alert=True)
        return
    
    # Buyurtma yaratish
    order = create_order(
        db=db,
        user_id=user.user_id,
        service_type=ServiceType.BREAD,
        phone_number=user.phone_number,
        description="Non buyurtmasi"
    )
    
    # Xabarni non guruhiga yuborish
    order_text = (
        f"🥖 <b>YANGI NON BUYURTMASI!</b>\n\n"
        f"📋 Buyurtma ID: <code>{order.order_id}</code>\n"
        f"⏰ Vaqti: {order.created_at.strftime('%H:%M:%S')}\n"
        f"📞 Telefon: <code>{user.phone_number}</code>\n"
        f"👤 Buyurtmachi: {user.first_name} {user.last_name or ''}\n"
        f"🏘️ Hudud: {user.residence_area}"
    )
    
    await callback.bot.send_message(
        chat_id=config.DRIVERS_ORDERS_GROUP_ID,
        text=order_text,
        parse_mode="HTML"
    )
    
    # Yo'lovchiga xabar
    await callback.message.edit_text(
        f"✅ <b>Non Buyurtmasi Berildi!</b>\n\n"
        f"📋 Buyurtma ID: {order.order_id}\n"
        f"📞 Telefon: <code>{user.phone_number}</code>\n\n"
        f"Tez orada sizga bog'lanishadi.",
        reply_markup=get_back_button()
    )
    
    # Cooldown o'rnatish
    set_cooldown(db, user.user_id, ServiceType.BREAD)
    
    logger.info(f"Bread order created: {order.order_id} by user {user_id}")


@router.callback_query(F.data.startswith("service_feed"))
async def order_feed(callback: CallbackQuery, state: FSMContext, db: Session):
    """Yem buyurtma berish"""
    await callback.answer()
    
    user_id = callback.from_user.id
    user = get_user_by_telegram_id(db, user_id)
    
    if not user:
        await callback.answer("❌ Avval ro'yxatdan o'ting", show_alert=True)
        return
    
    # Cooldown tekshirish
    can_order, reason = can_place_order(db, user.user_id, ServiceType.FEED)
    
    if not can_order:
        await callback.answer(reason, show_alert=True)
        return
    
    # Buyurtma yaratish
    order = create_order(
        db=db,
        user_id=user.user_id,
        service_type=ServiceType.FEED,
        phone_number=user.phone_number,
        description="Yem buyurtmasi"
    )
    
    # Xabarni yem guruhiga yuborish
    order_text = (
        f"🌾 <b>YANGI YEM BUYURTMASI!</b>\n\n"
        f"📋 Buyurtma ID: <code>{order.order_id}</code>\n"
        f"⏰ Vaqti: {order.created_at.strftime('%H:%M:%S')}\n"
        f"📞 Telefon: <code>{user.phone_number}</code>\n"
        f"👤 Buyurtmachi: {user.first_name} {user.last_name or ''}\n"
        f"🏘️ Hudud: {user.residence_area}"
    )
    
    await callback.bot.send_message(
        chat_id=config.DRIVERS_ORDERS_GROUP_ID,
        text=order_text,
        parse_mode="HTML"
    )
    
    # Yo'lovchiga xabar
    await callback.message.edit_text(
        f"✅ <b>Yem Buyurtmasi Berildi!</b>\n\n"
        f"📋 Buyurtma ID: {order.order_id}\n"
        f"📞 Telefon: <code>{user.phone_number}</code>\n\n"
        f"Tez orada sizga bog'lanishadi.",
        reply_markup=get_back_button()
    )
    
    # Cooldown o'rnatish
    set_cooldown(db, user.user_id, ServiceType.FEED)
    
    logger.info(f"Feed order created: {order.order_id} by user {user_id}")


# ==================== DRIVER HANDLERS ====================

@router.callback_query(F.data.startswith("accept_taxi_"))
async def accept_taxi_order(callback: CallbackQuery, state: FSMContext, db: Session):
    """Haydovchi taxi buyurtmasini qabul qilish"""
    await callback.answer()
    
    order_id = int(callback.data.replace("accept_taxi_", ""))
    driver_id = callback.from_user.id
    
    # Haydovchini tekshirish
    driver = get_user_by_telegram_id(db, driver_id)
    
    if not driver or driver.role != UserRole.DRIVER:
        await callback.answer("❌ Siz haydovchi hisobiga kira olmadingiz", show_alert=True)
        return
    
    # Buyurtmani tekshirish
    order = get_order_by_id(db, order_id)
    
    if not order or order.status != OrderStatus.WAITING:
        await callback.answer("❌ Bu buyurtma allaqachon qabul qilingan", show_alert=True)
        return
    
    # Buyurtmani qabul qilish
    accept_order(
        db=db,
        order_id=order_id,
        driver_id=driver.user_id,
        message_id=callback.message.message_id,
        group_id=callback.message.chat.id
    )
    
    # Guruhdagi xabarni o'chirish
    try:
        await callback.message.delete()
    except:
        pass
    
    # Haydovchiga yo'lovchi ma'lumotlarini yuborish
    from database import User as UserModel
    
    passenger = order.user
    
    passenger_info_text = (
        f"✅ <b>Buyurtma Qabul Qilindi!</b>\n\n"
        f"📋 Buyurtma ID: {order_id}\n"
        f"👤 Yo'lovchi: {order.user.first_name} {order.user.last_name or ''}\n"
        f"📞 Telefon: <code>{order.phone_number}</code>\n\n"
        f"⏰ <b>6 daqiqa vaqt berildi</b>\n"
        f"Haydovchi bilan bog'lanib, tasdiqlang yoki rad eting"
    )
    
    await callback.bot.send_message(
        chat_id=driver_id,
        text=passenger_info_text,
        reply_markup=get_driver_confirm_keyboard(order_id),
        parse_mode="HTML"
    )
    
    logger.info(f"Order {order_id} accepted by driver {driver_id}")


@router.callback_query(F.data.startswith("decline_taxi_"))
async def decline_taxi_order(callback: CallbackQuery, state: FSMContext, db: Session):
    """Haydovchi taxi buyurtmasini rad etish"""
    await callback.answer()
    
    order_id = int(callback.data.replace("decline_taxi_", ""))
    driver_id = callback.from_user.id
    
    # Buyurtmani tekshirish
    order = get_order_by_id(db, order_id)
    
    if not order or order.status != OrderStatus.WAITING:
        await callback.answer("❌ Bu buyurtma allaqachon qabul qilingan", show_alert=True)
        return
    
    # Rad etish sonini oshirish
    decline_order(db, order_id)
    order = get_order_by_id(db, order_id)
    
    # Agar 3 marta rad etilgan bo'lsa, buyurtmani bekor qilish
    if order.declined_count >= config.MAX_DECLINE_BEFORE_CANCEL:
        cancel_order(db, order_id, "Haydovchilar rad etdi")
        
        await callback.bot.send_message(
            chat_id=driver_id,
            text="❌ Bu buyurtma juda ko'p rad etilgani uchun bekor qilingan"
        )
        
        # Yo'lovchiga xabar
        await callback.bot.send_message(
            chat_id=order.user_id,
            text=f"❌ Sizning buyurtma #{order_id} bekor qilindi. Iltimos, qayta urinib ko'ring"
        )
        
        # Guruhdagi xabarni o'chirish
        try:
            await callback.message.delete()
        except:
            pass
    else:
        # Qayta guruhga yuborish
        remaining = config.MAX_DECLINE_BEFORE_CANCEL - order.declined_count
        
        order_text = (
            f"🚕 <b>TAXI BUYURTMASI (Rad {order.declined_count}/{config.MAX_DECLINE_BEFORE_CANCEL})</b>\n\n"
            f"📋 Buyurtma ID: <code>{order.order_id}</code>\n"
            f"📞 Telefon: <code>{order.phone_number}</code>\n"
            f"👤 Yo'lovchi: {order.user.first_name} {order.user.last_name or ''}\n\n"
            f"⏳ <b>7 daqiqada javob yoki bekor qilinadi</b>"
        )
        
        new_message = await callback.bot.send_message(
            chat_id=config.DRIVERS_ORDERS_GROUP_ID,
            text=order_text,
            reply_markup=get_taxi_order_confirmation_keyboard(order_id),
            parse_mode="HTML"
        )
        
        # Order message ID ni yangilash
        order.message_id = new_message.message_id
        db.commit()
        
        # Eski xabarni o'chirish
        try:
            await callback.message.delete()
        except:
            pass
        
        await callback.answer(f"❌ Rad etildi. Qolgan: {remaining} ta")
    
    logger.info(f"Order {order_id} declined by driver {driver_id}")


@router.callback_query(F.data.startswith("driver_confirm_"))
async def driver_confirm_order(callback: CallbackQuery, state: FSMContext, db: Session):
    """Haydovchi buyurtmani tasdiqlash"""
    await callback.answer()
    
    order_id = int(callback.data.replace("driver_confirm_", ""))
    
    order = get_order_by_id(db, order_id)
    
    if not order or order.status != OrderStatus.ACCEPTED:
        await callback.answer("❌ Bu buyurtma bekor qilingan", show_alert=True)
        return
    
    # Buyurtmani tasdiqlash
    confirm_order(db, order_id)
    
    await callback.answer("✅ Buyurtma tasdiqlandi!")
    
    # Yo'lovchiga xabar
    await callback.bot.send_message(
        chat_id=order.user_id,
        text=f"✅ Haydovchi sizning taxi buyurtmasini #{order_id} tasdiqladi!"
    )
    
    logger.info(f"Order {order_id} confirmed by driver")


@router.callback_query(F.data.startswith("driver_decline_"))
async def driver_decline_order(callback: CallbackQuery, state: FSMContext, db: Session):
    """Haydovchi buyurtmani rad etish"""
    await callback.answer("❌ Buyurtma rad etildi")
    
    order_id = int(callback.data.replace("driver_decline_", ""))
    
    # Buyurtmani bekor qilish
    cancel_order(db, order_id, "Haydovchi rad etdi")
    
    # Yo'lovchiga xabar
    order = get_order_by_id(db, order_id)
    await callback.bot.send_message(
        chat_id=order.user_id,
        text=f"❌ Haydovchi #buyurtma {order_id} ni rad etdi. Iltimos, qayta urinib ko'ring"
    )
    
    logger.info(f"Order {order_id} declined by driver")
