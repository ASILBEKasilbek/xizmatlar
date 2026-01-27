"""
Taymerlar - 7 va 6 daqiqalik timeout'lar
"""
import asyncio
import logging
from datetime import datetime, timedelta
from aiogram import Bot
from database import get_db, db_manager, Order
from config import config

logger = logging.getLogger(__name__)


async def check_waiting_orders(bot: Bot):
    """
    7 daqiqalik taymerni tekshirish
    - Hech kim bosmasa buyurtma yopiladi
    - Waiting statusdagi buyurtmalarni tekshiradi
    """
    db = get_db()
    try:
        # Barcha waiting statusdagi buyurtmalarni olish
        waiting_orders = db.query(Order).filter(
            Order.status == "waiting",
            Order.service_type == "🚕 Taxi"
        ).all()
        
        for order in waiting_orders:
            # 7 daqiqa o'tganmi?
            time_diff = datetime.utcnow() - order.created_at
            
            if time_diff >= timedelta(seconds=config.GROUP_TIMEOUT):
                # 7 daqiqa o'tgan - buyurtmani yopish
                db_manager.update_order_status(db, order.order_id, "cancelled")
                
                # Guruh xabarini o'chirish
                try:
                    if order.group_message_id:
                        await bot.delete_message(order.group_chat, order.group_message_id)
                except Exception as e:
                    logger.error(f"Error deleting group message: {e}")
                
                # GROUP3 ga xabar
                try:
                    await bot.send_message(
                        config.GROUP3,
                        f"⏰ Buyurtma #{order.order_id} 7 daqiqa ichida qabul qilinmadi va bekor qilindi!"
                    )
                except Exception as e:
                    logger.error(f"Error sending timeout message to GROUP3: {e}")
                
                # Yo'lovchiga xabar
                try:
                    await bot.send_message(
                        order.passenger_id,
                        f"⏰ <b>Buyurtmangiz bekor qilindi</b>\n\n"
                        f"📋 Buyurtma ID: #{order.order_id}\n"
                        f"Afsuski, 7 daqiqa ichida haydovchi topilmadi.\n\n"
                        f"Iltimos, keyinroq qaytadan urinib ko'ring."
                    )
                except Exception as e:
                    logger.error(f"Error sending timeout message to passenger: {e}")
                
                logger.info(f"Order #{order.order_id} cancelled due to 7-minute timeout")
    
    finally:
        db.close()


async def check_accepted_orders(bot: Bot):
    """
    6 daqiqalik taymerni tekshirish
    - Haydovchi jim bo'lsa avtomatik rad bo'ladi
    - Accepted statusdagi buyurtmalarni tekshiradi
    """
    db = get_db()
    try:
        # Barcha accepted statusdagi buyurtmalarni olish
        accepted_orders = db.query(Order).filter(
            Order.status == "accepted",
            Order.service_type == "🚕 Taxi"
        ).all()
        
        for order in accepted_orders:
            # 6 daqiqa o'tganmi?
            time_diff = datetime.utcnow() - order.accepted_at
            
            if time_diff >= timedelta(seconds=config.ACCEPTED_TIMEOUT):
                # 6 daqiqa o'tgan - avtomatik rad etish
                db_manager.increment_reject_count(db, order.order_id)
                
                # Buyurtmani qayta olish (yangilangan reject_count bilan)
                order = db_manager.get_order(db, order.order_id)
                
                # Haydovchiga xabar
                try:
                    await bot.send_message(
                        order.driver_id,
                        f"⏰ <b>Buyurtma #{order.order_id} avtomatik rad etildi!</b>\n\n"
                        f"Siz 6 daqiqa ichida tasdiqlasdan yoki rad qilmadingiz.\n"
                        f"Buyurtma avtomatik ravishda rad etildi."
                    )
                except Exception as e:
                    logger.error(f"Error sending timeout message to driver: {e}")
                
                if order.reject_count >= config.MAX_REJECT_COUNT:
                    # 3 marta rad etilgan - butunlay bekor qilish
                    db_manager.update_order_status(db, order.order_id, "cancelled")
                    
                    # Yo'lovchiga xabar
                    try:
                        await bot.send_message(
                            order.passenger_id,
                            f"❌ <b>Buyurtmangiz bekor qilindi</b>\n\n"
                            f"📋 Buyurtma ID: #{order.order_id}\n"
                            f"Afsuski, hozirda haydovchi topilmadi.\n\n"
                            f"Iltimos, keyinroq qaytadan urinib ko'ring."
                        )
                    except Exception as e:
                        logger.error(f"Error sending cancellation to passenger: {e}")
                    
                    # GROUP3 ga xabar
                    try:
                        await bot.send_message(
                            config.GROUP3,
                            f"❌ Buyurtma #{order.order_id} 3 marta rad etildi va bekor qilindi!"
                        )
                    except Exception as e:
                        logger.error(f"Error sending cancellation to GROUP3: {e}")
                
                else:
                    # 1-2 marta rad etilgan - qayta guruhga chiqarish
                    db_manager.update_order_status(
                        db, 
                        order.order_id, 
                        "waiting", 
                        driver_id=None, 
                        driver_name=None
                    )
                    
                    # Qayta GROUP3 ga yuborish
                    group_text = (
                        "🚕 <b>YANGI TAXI BUYURTMA</b>\n\n"
                        f"📋 Buyurtma ID: #{order.order_id}\n"
                        f"👤 Yo'lovchi: {order.passenger_name}\n"
                        f"📍 Hudud: {order.passenger_area}\n"
                        f"⚠️ Rad etilishlar: {order.reject_count}/{config.MAX_REJECT_COUNT}"
                    )
                    
                    try:
                        from keyboards import accept_order_keyboard
                        group_msg = await bot.send_message(
                            config.GROUP3,
                            group_text,
                            reply_markup=accept_order_keyboard(order.order_id)
                        )
                        
                        # Guruh xabar ID'sini saqlash
                        db_manager.update_order_group_message(db, order.order_id, group_msg.message_id)
                        
                    except Exception as e:
                        logger.error(f"Error re-posting to GROUP3: {e}")
                
                logger.info(f"Order #{order.order_id} auto-rejected due to 6-minute timeout. Reject count: {order.reject_count}")
    
    finally:
        db.close()


async def scheduler_loop(bot: Bot):
    """
    Asosiy scheduler loop
    - Har 30 soniyada bir marta ishlaydi
    - Waiting va accepted buyurtmalarni tekshiradi
    """
    logger.info("✅ Scheduler started")
    
    while True:
        try:
            # 7 daqiqalik taymerni tekshirish
            await check_waiting_orders(bot)
            
            # 6 daqiqalik taymerni tekshirish
            await check_accepted_orders(bot)
            
            # 30 soniya kutish
            await asyncio.sleep(30)
        
        except Exception as e:
            logger.error(f"Error in scheduler loop: {e}")
            await asyncio.sleep(30)


def start_scheduler(bot: Bot):
    """Schedulerni ishga tushirish"""
    asyncio.create_task(scheduler_loop(bot))
    logger.info("✅ Scheduler task created")
