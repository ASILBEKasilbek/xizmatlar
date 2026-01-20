"""
Avtomatik Timerlar va APScheduler Integration
Buyurtmalarning avtomatik bekor qilinishi va timeoutlari
"""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timedelta
import logging
from typing import Optional

from sqlalchemy.orm import Session
from database import SessionLocal, Order, OrderStatus
from config import config, ServiceType
from crud import (
    get_order_by_id,
    cancel_order,
    get_waiting_orders_by_service
)

logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler: Optional[AsyncIOScheduler] = None


async def init_scheduler(bot):
    """Schedulerni ishga tushirish"""
    global scheduler
    
    scheduler = AsyncIOScheduler()
    
    # Taxi buyurtmalarini tekshirish (har 30 sekundda)
    scheduler.add_job(
        check_taxi_timeout,
        trigger=IntervalTrigger(seconds=30),
        args=(bot,),
        id="check_taxi_timeout",
        replace_existing=True
    )
    
    # Driver response timeout (har 30 sekundda)
    scheduler.add_job(
        check_driver_timeout,
        trigger=IntervalTrigger(seconds=30),
        args=(bot,),
        id="check_driver_timeout",
        replace_existing=True
    )
    
    # Kunlik statistika (har kun saat 00:05 da)
    scheduler.add_job(
        generate_daily_stats,
        trigger=IntervalTrigger(hours=24, start_date=datetime.now() + timedelta(hours=1)),
        args=(bot,),
        id="generate_daily_stats",
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("Scheduler started successfully")


def stop_scheduler():
    """Schedulerni to'xtatish"""
    global scheduler
    if scheduler and scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler stopped")


async def check_taxi_timeout(bot):
    """
    Taxi buyurtmalarining timeout'ini tekshirish
    7 daqiqa ichida javob bo'lmasa, buyurtmani bekor qilish
    """
    db = SessionLocal()
    try:
        # Waiting status'dagi buyurtmalarni olish
        waiting_orders = get_waiting_orders_by_service(db, ServiceType.TAXI)
        
        now = datetime.utcnow()
        
        for order in waiting_orders:
            # Vaqt farqini hisoblash
            time_elapsed = now - order.created_at
            
            # 7 daqiqa timeout
            if time_elapsed > timedelta(seconds=config.TAXI_ORDER_TIMEOUT):
                
                # Buyurtmani bekor qilish
                cancel_order(db, order.order_id, "Timeout - haydovchi topilmadi")
                
                # Guruhdagi xabarni o'chirish
                if order.message_id and order.group_id:
                    try:
                        await bot.delete_message(
                            chat_id=order.group_id,
                            message_id=order.message_id
                        )
                    except Exception as e:
                        logger.error(f"Failed to delete message: {e}")
                
                # Yo'lovchiga xabar
                try:
                    await bot.send_message(
                        chat_id=order.user_id,
                        text=f"❌ Taxi buyurtmasi #{order.order_id} 7 daqiqa ichida biron haydovchi topilmadi. "
                             f"Iltimos, qayta urinib ko'ring."
                    )
                except Exception as e:
                    logger.error(f"Failed to notify passenger: {e}")
                
                logger.info(f"Taxi order {order.order_id} cancelled due to timeout")
    
    except Exception as e:
        logger.error(f"Error checking taxi timeout: {e}")
    
    finally:
        db.close()


async def check_driver_timeout(bot):
    """
    Haydovchi response timeout'ini tekshirish
    6 daqiqa ichida javob bo'lmasa, avtomatik rad etilgan ko'riladi
    """
    db = SessionLocal()
    try:
        # Accepted status'dagi buyurtmalarni olish
        from database import Order
        
        accepted_orders = db.query(Order).filter(
            Order.status == OrderStatus.ACCEPTED
        ).all()
        
        now = datetime.utcnow()
        
        for order in accepted_orders:
            # Vaqt farqini hisoblash
            time_elapsed = now - order.accepted_at
            
            # 6 daqiqa timeout
            if time_elapsed > timedelta(seconds=config.DRIVER_RESPONSE_TIMEOUT):
                
                # Buyurtmani bekor qilish
                cancel_order(db, order.order_id, "Haydovchi timeout - javob bermadi")
                
                # Yo'lovchiga xabar
                try:
                    await bot.send_message(
                        chat_id=order.user_id,
                        text=f"❌ Haydovchi buyurtma #{order.order_id} ni 6 daqiqada "
                             f"tasdiqlashni butskunlar. Iltimos, qayta urinib ko'ring."
                    )
                except Exception as e:
                    logger.error(f"Failed to notify passenger: {e}")
                
                logger.info(f"Order {order.order_id} cancelled due to driver timeout")
    
    except Exception as e:
        logger.error(f"Error checking driver timeout: {e}")
    
    finally:
        db.close()


async def generate_daily_stats(bot):
    """
    Kunlik statistika yaratish
    Har kun 00:05 da ishlaydi
    """
    db = SessionLocal()
    try:
        from crud import get_daily_stats, create_daily_stats, get_orders_by_date
        
        yesterday = datetime.utcnow() - timedelta(days=1)
        
        # O'tgan kuning statistikasini olish
        stats_data = get_daily_stats(db, yesterday)
        
        # Database-ga saqlash
        create_daily_stats(db, None, stats_data)
        
        # Admin-ga bildirishlash
        stats_text = (
            f"📊 <b>Kunlik Statistika - {yesterday.strftime('%d.%m.%Y')}</b>\n\n"
            f"Jami buyurtmalar: {stats_data['total_orders']}\n"
            f"Tasdiqlangan: {stats_data['confirmed_orders']}\n"
            f"Bekor qilingan: {stats_data['cancelled_orders']}\n\n"
            f"Xizmat turi bo'yicha:\n"
            f"🚕 Taxi: {stats_data['taxi_orders']}\n"
            f"🥖 Non: {stats_data['bread_orders']}\n"
            f"🌾 Yem: {stats_data['feed_orders']}"
        )
        
        for admin_id in config.ADMIN_IDS:
            try:
                await bot.send_message(
                    chat_id=admin_id,
                    text=stats_text,
                    parse_mode="HTML"
                )
            except Exception as e:
                logger.error(f"Failed to send daily stats to admin {admin_id}: {e}")
        
        logger.info("Daily statistics generated successfully")
    
    except Exception as e:
        logger.error(f"Error generating daily stats: {e}")
    
    finally:
        db.close()


async def cleanup_old_orders(db: Session):
    """
    Eski buyurtmalarni tozalash (30 kundan qadimroq)
    Jami statistikada saqlab turiladi, lekin buyurtmalarni o'chirib tashlash
    """
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        old_orders = db.query(Order).filter(
            Order.created_at < cutoff_date,
            Order.status.in_([OrderStatus.CANCELLED, OrderStatus.COMPLETED])
        ).delete()
        
        db.commit()
        
        logger.info(f"Cleaned up {old_orders} old orders")
    
    except Exception as e:
        logger.error(f"Error cleaning up old orders: {e}")
