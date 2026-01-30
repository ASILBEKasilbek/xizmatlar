import logging
from datetime import datetime, timedelta
from aiogram import Bot
from database import get_db, Order, db_manager
from config import config
from keyboards import accept_order_keyboard

logger = logging.getLogger(__name__)


async def check_old_orders_on_startup(bot: Bot):
    db = get_db()
    try:
        now = datetime.utcnow()
        logger.info("🔍 Checking old orders on startup...")
        
        waiting_orders = db.query(Order).filter(
            Order.status == "waiting",
            Order.service_type == "🚕 Taxi"
        ).all()
        
        for order in waiting_orders:
            time_diff = now - order.created_at
            
            if time_diff >= timedelta(seconds=config.GROUP_TIMEOUT):
                db_manager.update_order_status(db, order.order_id, "cancelled")
                
                try:
                    if order.group_message_id:
                        await bot.delete_message(order.group_chat, order.group_message_id)
                except Exception as e:
                    logger.error(f"Error deleting group message on startup: {e}")
                
                try:
                    await bot.send_message(
                        order.passenger_id,
                        f"⏰ <b>Buyurtmangiz bekor qilindi</b>\n\n"
                        f"📋 Buyurtma ID: #{order.order_id}\n"
                        f"Afsuski, haydovchi topilmadi (bot qayta ishga tushdi).\n\n"
                        f"Iltimos, qaytadan buyurtma bering."
                    )
                except Exception as e:
                    logger.error(f"Error sending message to passenger on startup: {e}")
                
                logger.info(f"⏰ Order #{order.order_id} cancelled on startup (timeout)")
        
        accepted_orders = db.query(Order).filter(
            Order.status == "accepted",
            Order.service_type == "🚕 Taxi"
        ).all()
        
        for order in accepted_orders:
            time_diff = now - order.accepted_at
            
            if time_diff >= timedelta(seconds=config.ACCEPTED_TIMEOUT):
                db_manager.increment_reject_count(db, order.order_id)
                order = db_manager.get_order(db, order.order_id)
                
                try:
                    await bot.send_message(
                        order.driver_id,
                        f"⏰ <b>Buyurtma #{order.order_id} avtomatik rad etildi!</b>\n\n"
                        f"Bot qayta ishga tushdi va siz 6 daqiqa ichida tasdiqlasdan yoki rad qilmadingiz.\n"
                        f"Buyurtma avtomatik ravishda rad etildi."
                    )
                except Exception as e:
                    logger.error(f"Error sending message to driver on startup: {e}")
                
                if order.reject_count >= config.MAX_REJECT_COUNT:
                    db_manager.update_order_status(db, order.order_id, "cancelled")
                    
                    try:
                        await bot.send_message(
                            order.passenger_id,
                            f"❌ <b>Buyurtmangiz bekor qilindi</b>\n\n"
                            f"📋 Buyurtma ID: #{order.order_id}\n"
                            f"Afsuski, hozirda haydovchi topilmadi.\n\n"
                            f"Iltimos, keyinroq qaytadan urinib ko'ring."
                        )
                    except Exception as e:
                        logger.error(f"Error sending cancellation to passenger on startup: {e}")
                    
                    logger.info(f"❌ Order #{order.order_id} cancelled on startup (3x reject)")
                
                else:
                    db_manager.update_order_status(
                        db, 
                        order.order_id, 
                        "waiting", 
                        driver_id=None, 
                        driver_name=None
                    )
                    
                    group_text = (
                        "🚕 <b>YANGI TAXI BUYURTMA</b>\n\n"
                        f"📋 Buyurtma ID: #{order.order_id}\n"
                        f"👤 Yo'lovchi: {order.passenger_name}\n"
                        f"📍 Hudud: {order.passenger_area}\n"
                        f"⚠️ Rad etilishlar: {order.reject_count}/{config.MAX_REJECT_COUNT}\n"
                        f"🔄 Bot qayta ishga tushdi"
                    )
                    
                    try:
                        group_msg = await bot.send_message(
                            config.GROUP3,
                            group_text,
                            reply_markup=accept_order_keyboard(order.order_id)
                        )
                        db_manager.update_order_group_message(db, order.order_id, group_msg.message_id)
                    except Exception as e:
                        logger.error(f"Error re-posting to GROUP3 on startup: {e}")
                    
                    logger.info(f"🔄 Order #{order.order_id} re-posted on startup")
        
        logger.info(f"✅ Startup check complete. Waiting: {len(waiting_orders)}, Accepted: {len(accepted_orders)}")
    
    finally:
        db.close()


async def health_check_loop(bot: Bot):
    import asyncio
    
    logger.info("❤️ Health check started")
    
    while True:
        try:
            await asyncio.sleep(3600)  # 1 soat
            logger.info("❤️ Health check: Bot ishlamoqda")
            
            db = get_db()
            try:
                db.execute("SELECT 1")
                logger.info("❤️ Database connection: OK")
            except Exception as e:
                logger.error(f"❤️ Database connection: FAILED - {e}")
            finally:
                db.close()
        
        except Exception as e:
            logger.error(f"❤️ Health check error: {e}")
            await asyncio.sleep(60) 