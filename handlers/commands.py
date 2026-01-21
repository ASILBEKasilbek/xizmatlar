"""
Commands handler - /active, /status, /cleanup
"""
import logging
from datetime import datetime
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from database import get_db, db_manager, User, Order
from config import config

logger = logging.getLogger(__name__)

router = Router()


@router.message(Command("active"))
async def cmd_active(message: Message, state: FSMContext):
    """/active - Aktiv buyurtmalarni ko'rish"""
    try:
        user_id = message.from_user.id
        
        await state.clear()
        
        db = get_db()
        try:
            user = db_manager.get_user(db, user_id)
            
            if not user:
                await message.answer("❌ Siz ro'yxatdan o'tmagansiz! /start ni bosing.")
                return
            
            if user.user_type == "driver":
                # Haydovchi uchun - accepted orderini ko'rsatish
                order = db_manager.get_driver_active_order(db, user_id)
                
                if not order:
                    await message.answer("📋 Sizda hozirda aktiv buyurtma yo'q.")
                    return
                
                elapsed = datetime.utcnow() - order.accepted_at
                minutes = int(elapsed.total_seconds() / 60)
                
                text = (
                    "📋 <b>SIZNING AKTIV BUYURTMANGIZ:</b>\n\n"
                    f"🆔 Buyurtma ID: {order.order_id}\n"
                    f"👤 Yo'lovchi: {order.passenger_name}\n"
                    f"📞 Telefon: {order.passenger_phone}\n"
                    f"📍 Hudud: {order.passenger_area}\n"
                    f"📊 Status: Qabul qilingan\n"
                    f"⏰ Qabul qilingan: {minutes} daqiqa oldin\n\n"
                    f"⚠️ {config.ACCEPTED_TIMEOUT // 60} daqiqa ichida tasdiqlang yoki rad eting!"
                )
                await message.answer(text)
            
            elif user.user_type == "passenger":
                # Yo'lovchi uchun - waiting yoki accepted taxi orderini ko'rsatish
                order = db_manager.get_active_taxi_order(db, user_id)
                
                if not order:
                    await message.answer("📋 Sizda hozirda aktiv taxi buyurtma yo'q.")
                    return
                
                elapsed = datetime.utcnow() - order.created_at
                minutes = int(elapsed.total_seconds() / 60)
                
                status_text = {
                    "waiting": "⏳ Kutilmoqda",
                    "accepted": "✅ Qabul qilindi"
                }
                
                text = (
                    "📋 <b>SIZNING AKTIV BUYURTMANGIZ:</b>\n\n"
                    f"🆔 Buyurtma ID: {order.order_id}\n"
                    f"📍 Hudud: {order.passenger_area}\n"
                    f"📊 Status: {status_text.get(order.status, order.status)}\n"
                    f"⏰ Yaratilgan: {minutes} daqiqa oldin\n"
                )
                
                if order.status == "accepted" and order.driver_name:
                    text += f"\n🚖 Haydovchi: {order.driver_name}"
                
                await message.answer(text)
            
            else:
                await message.answer("❌ Noma'lum foydalanuvchi turi.")
        
        finally:
            db.close()
    
    except Exception as e:
        logger.error(f"Error in cmd_active: {e}")
        await message.answer("❌ Xatolik yuz berdi.")


@router.message(Command("status"))
async def cmd_status(message: Message, state: FSMContext):
    """/status - Bot statistikasi (faqat admin)"""
    try:
        user_id = message.from_user.id
        
        if user_id not in config.ADMIN_IDS:
            await message.answer("❌ Sizda admin huquqlari yo'q!")
            return
        
        await state.clear()
        
        db = get_db()
        try:
            # Users count
            users_count = db.query(User).count()
            drivers_count = db.query(User).filter(User.user_type == "driver").count()
            passengers_count = db.query(User).filter(User.user_type == "passenger").count()
            
            # Orders count
            orders_count = db.query(Order).count()
            waiting_orders = db.query(Order).filter(Order.status == "waiting").count()
            accepted_orders = db.query(Order).filter(Order.status == "accepted").count()
            confirmed_orders = db.query(Order).filter(Order.status == "confirmed").count()
            cancelled_orders = db.query(Order).filter(Order.status == "cancelled").count()
            
            text = (
                "📊 <b>BOT STATISTIKASI</b>\n\n"
                f"👥 <b>Foydalanuvchilar:</b>\n"
                f"• Jami: {users_count}\n"
                f"• Haydovchilar: {drivers_count}\n"
                f"• Yo'lovchilar: {passengers_count}\n\n"
                f"📋 <b>Buyurtmalar:</b>\n"
                f"• Jami: {orders_count}\n"
                f"• Kutilmoqda: {waiting_orders}\n"
                f"• Qabul qilingan: {accepted_orders}\n"
                f"• Tasdiqlangan: {confirmed_orders}\n"
                f"• Bekor qilingan: {cancelled_orders}\n\n"
                f"⏰ Vaqt: {datetime.utcnow().strftime('%d.%m.%Y %H:%M')}"
            )
            
            await message.answer(text)
        
        finally:
            db.close()
    
    except Exception as e:
        logger.error(f"Error in cmd_status: {e}")
        await message.answer("❌ Xatolik yuz berdi.")


@router.message(Command("cleanup"))
async def cmd_cleanup(message: Message, state: FSMContext):
    """/cleanup - Eski ma'lumotlarni tozalash (faqat admin)"""
    try:
        user_id = message.from_user.id
        
        if user_id not in config.ADMIN_IDS:
            await message.answer("❌ Sizda admin huquqlari yo'q!")
            return
        
        await state.clear()
        
        await message.answer("🔄 Eski ma'lumotlar tozalanmoqda...")
        
        db = get_db()
        try:
            # Tozalash
            db_manager.cleanup_old_data(db)
            
            text = (
                "✅ <b>Tozalash tugallandi!</b>\n\n"
                "Quyidagi ma'lumotlar o'chirildi:\n"
                "• 30 kundan eski product cooldownlar\n"
                "• 90 kundan eski tugallangan/bekor qilingan buyurtmalar\n"
                "• 90 kundan eski statistikalar"
            )
            
            await message.answer(text)
            logger.info("Cleanup completed by admin")
        
        finally:
            db.close()
    
    except Exception as e:
        logger.error(f"Error in cmd_cleanup: {e}")
        await message.answer("❌ Xatolik yuz berdi.")
