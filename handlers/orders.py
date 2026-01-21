"""
Orders handler - Accept, Confirm, Reject callbacks
"""
import logging
from datetime import datetime
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from database import get_db, db_manager
from keyboards import driver_action_keyboard, accept_order_keyboard
from config import config

logger = logging.getLogger(__name__)

router = Router()


@router.callback_query(F.data.startswith("accept_"))
async def accept_order_callback(callback: CallbackQuery, state: FSMContext):
    """Buyurtmani qabul qilish (haydovchi)"""
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
            if config.GROUP3:
                info_text = f"✅ Buyurtma #{order_id} {driver.fullname} ga yuborildi."
                try:
                    await callback.bot.send_message(config.GROUP3, info_text)
                except Exception as e:
                    logger.error(f"Error sending info to GROUP3: {e}")
            
            # Haydovchiga PRIVATE ga yo'lovchi ma'lumotini TELEFON bilan yuborish
            private_text = (
                "✅ <b>SIZ BUYURTMANI QABUL QILDINGIZ</b>\n\n"
                f"📋 Buyurtma ID: {order_id}\n"
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
            logger.info(f"Order {order_id} accepted by driver {driver_id}")
        
        finally:
            db.close()
    
    except Exception as e:
        logger.error(f"Error in accept_order_callback: {e}")
        await callback.answer("❌ Xatolik yuz berdi!", show_alert=True)


@router.callback_query(F.data.startswith("confirm_"))
async def confirm_order_callback(callback: CallbackQuery, state: FSMContext):
    """Buyurtmani tasdiqlash (haydovchi)"""
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
            
            if order.status != "accepted":
                await callback.answer("❌ Bu buyurtma accepted statusida emas!", show_alert=True)
                return
            
            if order.driver_id != driver_id:
                await callback.answer("❌ Faqat o'zingiz qabul qilgan buyurtmani tasdiqlashingiz mumkin!", show_alert=True)
                return
            
            # Buyurtmani tasdiqlash
            db_manager.update_order_status(db, order_id, "confirmed")
            
            # Driver statsga qo'shish
            driver = db_manager.get_user(db, driver_id)
            if driver:
                db_manager.increment_confirmed_count(db, driver_id, driver.fullname, "driver")
            
            # Haydovchi xabarini edit qilish
            try:
                await callback.message.edit_text(
                    f"✅ <b>BUYURTMA TASDIQLANDI</b>\n\n"
                    f"📋 Buyurtma ID: {order_id}\n"
                    f"👤 Yo'lovchi: {order.passenger_name}\n"
                    f"📞 Telefon: {order.passenger_phone}\n"
                    f"📍 Hudud: {order.passenger_area}\n\n"
                    f"⏰ Tasdiqlangan vaqt: {datetime.utcnow().strftime('%H:%M')}"
                )
            except Exception as e:
                logger.error(f"Error editing message: {e}")
            
            # Yo'lovchiga haydovchi ma'lumotini yuborish
            passenger_text = (
                "✅ <b>BUYURTMA TASDIQLANDI!</b>\n\n"
                f"📋 Buyurtma ID: {order_id}\n"
            )
            
            # Haydovchi ma'lumotlari
            if driver:
                passenger_text += (
                    f"🚖 Haydovchi: {driver.fullname}\n"
                    f"📞 Telefon: {driver.phone}\n"
                    f"🚗 Mashina: {driver.car_model}\n"
                )
            else:
                passenger_text += f"🚖 Haydovchi: {order.driver_name}\n"
            
            passenger_text += f"\n⏰ Vaqt: {datetime.utcnow().strftime('%H:%M')}"
            
            try:
                await callback.bot.send_message(order.passenger_id, passenger_text)
            except Exception as e:
                logger.error(f"Error sending to passenger: {e}")
            
            await callback.answer("✅ Buyurtma tasdiqlandi!")
            logger.info(f"Order {order_id} confirmed by driver {driver_id}")
        
        finally:
            db.close()
    
    except Exception as e:
        logger.error(f"Error in confirm_order_callback: {e}")
        await callback.answer("❌ Xatolik yuz berdi!", show_alert=True)


@router.callback_query(F.data.startswith("reject_"))
async def reject_order_callback(callback: CallbackQuery, state: FSMContext):
    """Buyurtmani rad etish (haydovchi)"""
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
            
            if order.status != "accepted":
                await callback.answer("❌ Bu buyurtma accepted statusida emas!", show_alert=True)
                return
            
            if order.driver_id != driver_id:
                await callback.answer("❌ Faqat o'zingiz qabul qilgan buyurtmani rad etishingiz mumkin!", show_alert=True)
                return
            
            # Reject count'ni oshirish
            order = db_manager.increment_reject_count(db, order_id)
            
            # Driver statsga qo'shish
            driver = db_manager.get_user(db, driver_id)
            if driver:
                db_manager.increment_rejected_count(db, driver_id, driver.fullname, "driver")
            
            # Haydovchi xabarini edit qilish
            try:
                await callback.message.edit_text(
                    f"❌ <b>BUYURTMA RAD ETILDI</b>\n\n"
                    f"📋 Buyurtma ID: {order_id}\n"
                    f"👤 Yo'lovchi: {order.passenger_name}\n\n"
                    f"⏰ Rad etilgan vaqt: {datetime.utcnow().strftime('%H:%M')}"
                )
            except Exception as e:
                logger.error(f"Error editing message: {e}")
            
            # 3 martadan kam rad etilgan bo'lsa - qayta yuborish
            if order.reject_count < config.MAX_REJECT_COUNT:
                # Buyurtmani reset qilish
                order = db_manager.reset_order_for_repost(db, order_id)
                
                # GROUP3 ga QAYTA yuborish (TELEFONSIZ)
                if config.GROUP3:
                    group_text = (
                        f"🔄 <b>QAYTA YUBORILDI ({order.reject_count}/{config.MAX_REJECT_COUNT})</b>\n\n"
                        "🧍‍♂️ <b>YO'LOVCHI XIZMATI</b>\n\n"
                        f"📍 Hudud: {order.passenger_area}\n"
                        f"👤 Ism: {order.passenger_name}\n"
                        f"🚕 Xizmat: Taxi\n\n"
                        f"⏰ Vaqt: {datetime.utcnow().strftime('%H:%M')}\n"
                        f"🆔 Buyurtma ID: {order_id}"
                    )
                    
                    try:
                        group_message = await callback.bot.send_message(
                            config.GROUP3,
                            group_text,
                            reply_markup=accept_order_keyboard(order_id)
                        )
                        
                        # Group message ID'sini saqlash
                        db_manager.set_group_message_id(db, order_id, group_message.message_id)
                    
                    except Exception as e:
                        logger.error(f"Error sending to GROUP3: {e}")
                
                await callback.answer(f"❌ Buyurtma rad etildi va qayta yuborildi ({order.reject_count}/{config.MAX_REJECT_COUNT})")
            
            else:
                # 3 marta rad etilgan - buyurtmani yopish
                db_manager.update_order_status(db, order_id, "cancelled")
                
                # GROUP3 ga xabar
                if config.GROUP3:
                    cancel_text = f"❌ Buyurtma #{order_id} 3 marta rad etildi va yopildi."
                    try:
                        await callback.bot.send_message(config.GROUP3, cancel_text)
                    except Exception as e:
                        logger.error(f"Error sending to GROUP3: {e}")
                
                # Yo'lovchiga xabar
                passenger_text = (
                    f"❌ Buyurtma #{order_id} 3 marta rad etildi va yopildi.\n\n"
                    "Iltimos, keyinroq qaytadan urinib ko'ring."
                )
                try:
                    await callback.bot.send_message(order.passenger_id, passenger_text)
                except Exception as e:
                    logger.error(f"Error sending to passenger: {e}")
                
                await callback.answer("❌ Buyurtma 3 marta rad etildi va yopildi!", show_alert=True)
            
            logger.info(f"Order {order_id} rejected by driver {driver_id} (count: {order.reject_count})")
        
        finally:
            db.close()
    
    except Exception as e:
        logger.error(f"Error in reject_order_callback: {e}")
        await callback.answer("❌ Xatolik yuz berdi!", show_alert=True)
