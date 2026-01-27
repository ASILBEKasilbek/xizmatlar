"""
Orders handler - Buyurtmalarni qabul qilish, tasdiqlash, rad etish
"""
import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery
from database import get_db, db_manager
from keyboards import driver_action_keyboard
from config import config

logger = logging.getLogger(__name__)

router = Router()


@router.callback_query(F.data.startswith("accept_"))
async def accept_order_callback(callback: CallbackQuery):
    """
    Buyurtmani qabul qilish (haydovchi)
    - Guruhda "✅ Qabul qilish" tugmasi bosilganda
    - 2 haydovchi bir vaqtda qabul qila olmaydi
    - Qabul qilingach guruh xabari o'chiriladi
    """
    try:
        order_id = int(callback.data.split("_")[1])
        driver_id = callback.from_user.id
        
        db = get_db()
        try:
            # Haydovchini tekshirish
            driver = db_manager.get_user(db, driver_id)
            
            if not driver or driver.user_type != "driver":
                await callback.answer("❌ Faqat haydovchilar buyurtma qabul qilishi mumkin!", show_alert=True)
                return
            
            # Buyurtmani olish
            order = db_manager.get_order(db, order_id)
            
            if not order:
                await callback.answer("❌ Buyurtma topilmadi!", show_alert=True)
                return
            
            if order.status != "waiting":
                await callback.answer("❌ Bu buyurtma allaqachon qabul qilingan!", show_alert=True)
                return
            
            # Haydovchida boshqa aktiv buyurtma bormi
            driver_active_order = db_manager.get_driver_active_order(db, driver_id)
            
            if driver_active_order:
                await callback.answer(
                    f"❌ Sizda allaqachon aktiv buyurtma bor (ID: {driver_active_order.order_id})!",
                    show_alert=True
                )
                return
            
            # Guruh xabarini o'chirish
            try:
                if order.group_message_id:
                    await callback.bot.delete_message(order.group_chat, order.group_message_id)
            except Exception as e:
                logger.error(f"Error deleting group message: {e}")
            
            # Buyurtmani update qilish
            db_manager.update_order_status(
                db=db,
                order_id=order_id,
                status="accepted",
                driver_id=driver_id,
                driver_name=driver.fullname
            )
            
            # GROUP3 ga info yuborish
            info_text = f"✅ Buyurtma #{order_id} {driver.fullname} ga yuborildi."
            try:
                await callback.bot.send_message(config.GROUP3, info_text)
            except Exception as e:
                logger.error(f"Error sending info to GROUP3: {e}")
            
            # Haydovchiga PRIVATE ga yo'lovchi ma'lumotini TELEFON bilan yuborish
            private_text = (
                "✅ <b>SIZ BUYURTMANI QABUL QILDINGIZ</b>\n\n"
                f"📋 Buyurtma ID: #{order.order_id}\n"
                f"👤 Yo'lovchi: {order.passenger_name}\n"
                f"📞 Telefon: {order.passenger_phone}\n"
                f"📍 Hudud: {order.passenger_area}\n\n"
                "Iltimos, yo'lovchi bilan bog'lanib, buyurtmani tasdiqlang yoki rad eting."
            )
            
            await callback.bot.send_message(
                driver_id,
                private_text,
                reply_markup=driver_action_keyboard(order_id)
            )
            
            await callback.answer("✅ Buyurtma qabul qilindi! Telefon raqami sizga yuborildi.")
            logger.info(f"Order #{order_id} accepted by driver {driver_id}")
        
        finally:
            db.close()
    
    except Exception as e:
        logger.error(f"Error in accept_order_callback: {e}")
        await callback.answer("❌ Xatolik yuz berdi!", show_alert=True)


@router.callback_query(F.data.startswith("confirm_"))
async def confirm_order_callback(callback: CallbackQuery):
    """
    Buyurtmani tasdiqlash (haydovchi)
    - Haydovchi yo'lovchi bilan gaplashgandan keyin
    - Buyurtma yakunlanadi
    """
    try:
        order_id = int(callback.data.split("_")[1])
        driver_id = callback.from_user.id
        
        db = get_db()
        try:
            # Buyurtmani olish
            order = db_manager.get_order(db, order_id)
            
            if not order:
                await callback.answer("❌ Buyurtma topilmadi!", show_alert=True)
                return
            
            if order.driver_id != driver_id:
                await callback.answer("❌ Bu buyurtma sizga tegishli emas!", show_alert=True)
                return
            
            if order.status != "accepted":
                await callback.answer("❌ Bu buyurtma allaqachon yakunlangan!", show_alert=True)
                return
            
            # Buyurtmani tasdiqlash
            db_manager.update_order_status(db, order_id, "confirmed")
            
            # Haydovchiga xabar
            await callback.message.edit_text(
                f"✅ <b>Buyurtma #{order_id} tasdiqlandi!</b>\n\n"
                f"Rahmat, {order.driver_name}!"
            )
            
            # Yo'lovchiga xabar
            passenger_text = (
                f"✅ <b>Buyurtmangiz tasdiqlandi!</b>\n\n"
                f"📋 Buyurtma ID: #{order_id}\n"
                f"🚖 Haydovchi: {order.driver_name}\n\n"
                f"Tez orada haydovchi yetib keladi!"
            )
            try:
                await callback.bot.send_message(order.passenger_id, passenger_text)
            except Exception as e:
                logger.error(f"Error sending confirmation to passenger: {e}")
            
            # GROUP3 ga xabar
            try:
                await callback.bot.send_message(
                    config.GROUP3, 
                    f"✅ Buyurtma #{order_id} tasdiqlandi! ({order.driver_name})"
                )
            except Exception as e:
                logger.error(f"Error sending confirmation to GROUP3: {e}")
            
            await callback.answer("✅ Buyurtma tasdiqlandi!")
            logger.info(f"Order #{order_id} confirmed by driver {driver_id}")
        
        finally:
            db.close()
    
    except Exception as e:
        logger.error(f"Error in confirm_order_callback: {e}")
        await callback.answer("❌ Xatolik yuz berdi!", show_alert=True)


@router.callback_query(F.data.startswith("reject_"))
async def reject_order_callback(callback: CallbackQuery):
    """
    Buyurtmani rad etish (haydovchi)
    - 1-2 marta rad etilsa, qayta guruhga chiqariladi
    - 3 marta rad etilsa, butunlay bekor qilinadi
    """
    try:
        order_id = int(callback.data.split("_")[1])
        driver_id = callback.from_user.id
        
        db = get_db()
        try:
            # Buyurtmani olish
            order = db_manager.get_order(db, order_id)
            
            if not order:
                await callback.answer("❌ Buyurtma topilmadi!", show_alert=True)
                return
            
            if order.driver_id != driver_id:
                await callback.answer("❌ Bu buyurtma sizga tegishli emas!", show_alert=True)
                return
            
            if order.status != "accepted":
                await callback.answer("❌ Bu buyurtma allaqachon yakunlangan!", show_alert=True)
                return
            
            # Rad etishlar sonini oshirish
            db_manager.increment_reject_count(db, order_id)
            
            # Buyurtmani qayta olish (yangilangan reject_count bilan)
            order = db_manager.get_order(db, order_id)
            
            # Haydovchiga xabar
            await callback.message.edit_text(
                f"❌ <b>Buyurtma #{order_id} rad etildi!</b>\n\n"
                f"Buyurtma {order.reject_count} marta rad etildi."
            )
            
            if order.reject_count >= config.MAX_REJECT_COUNT:
                # 3 marta rad etilgan - butunlay bekor qilish
                db_manager.update_order_status(db, order_id, "cancelled")
                
                # Yo'lovchiga xabar
                passenger_text = (
                    f"❌ <b>Buyurtmangiz bekor qilindi</b>\n\n"
                    f"📋 Buyurtma ID: #{order_id}\n"
                    f"Afsuski, hozirda haydovchi topilmadi.\n\n"
                    f"Iltimos, keyinroq qaytadan urinib ko'ring."
                )
                try:
                    await callback.bot.send_message(order.passenger_id, passenger_text)
                except Exception as e:
                    logger.error(f"Error sending cancellation to passenger: {e}")
                
                # GROUP3 ga xabar
                try:
                    await callback.bot.send_message(
                        config.GROUP3, 
                        f"❌ Buyurtma #{order_id} 3 marta rad etildi va bekor qilindi!"
                    )
                except Exception as e:
                    logger.error(f"Error sending cancellation to GROUP3: {e}")
                
            else:
                # 1-2 marta rad etilgan - qayta guruhga chiqarish
                db_manager.update_order_status(
                    db, 
                    order_id, 
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
                    group_msg = await callback.bot.send_message(
                        config.GROUP3, 
                        group_text,
                        reply_markup=accept_order_keyboard(order_id)
                    )
                    
                    # Guruh xabar ID'sini saqlash
                    db_manager.update_order_group_message(db, order_id, group_msg.message_id)
                    
                except Exception as e:
                    logger.error(f"Error re-posting to GROUP3: {e}")
            
            await callback.answer("✅ Buyurtma rad etildi!")
            logger.info(f"Order #{order_id} rejected by driver {driver_id}. Reject count: {order.reject_count}")
        
        finally:
            db.close()
    
    except Exception as e:
        logger.error(f"Error in reject_order_callback: {e}")
        await callback.answer("❌ Xatolik yuz berdi!", show_alert=True)
