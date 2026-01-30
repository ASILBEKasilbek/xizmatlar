"""
Services handler - Taxi, Non, Yem buyurtmalari
"""
import logging
from datetime import datetime, timedelta
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from database import get_db, db_manager
from keyboards import accept_order_keyboard, services_keyboard
from config import config

logger = logging.getLogger(__name__)

router = Router()


@router.message(F.text == "🚕 Taxi")
async def taxi_order_handler(message: Message, state: FSMContext):
    """Taxi buyurtma berish"""
    try:
        user_id = message.from_user.id
        
        # FSM state'ni tozalash
        await state.clear()
        
        # Database'dan foydalanuvchini olish
        db = get_db()
        try:
            user = db_manager.get_user(db, user_id)
            
            if not user:
                await message.answer("❌ Siz ro'yxatdan o'tmagansiz! /start ni bosing.")
                return
            
            if user.user_type != "passenger":
                await message.answer("❌ Faqat yo'lovchilar taxi buyurtma berishi mumkin!")
                return
            
            # Aktiv taxi buyurtmasini tekshirish
            active_order = db_manager.get_active_taxi_order(db, user_id)
            
            if active_order:
                # Aktiv buyurtma bor
                status_text = {
                    "waiting": "⏳ Kutilmoqda",
                    "accepted": "✅ Qabul qilindi"
                }
                
                elapsed_time = datetime.utcnow() - active_order.created_at
                minutes = int(elapsed_time.total_seconds() / 60)
                
                text = (
                    "❌ Sizda allaqachon aktiv taxi buyurtma bor!\n\n"
                    f"📋 Buyurtma ID: {active_order.order_id}\n"
                    f"📊 Status: {status_text.get(active_order.status, active_order.status)}\n"
                    f"⏰ Vaqt: {minutes} daqiqa oldin\n\n"
                    "Yangi buyurtma berish uchun avvalgi buyurtma tugashini kuting."
                )
                await message.answer(text)
                return
            
            # Yangi buyurtma yaratish
            order = db_manager.create_order(
                db=db,
                passenger_id=user_id,
                passenger_name=user.fullname,
                passenger_phone=user.phone,
                passenger_area=user.area,
                service_type="🚕 Taxi",
                group_chat=config.GROUP3
            )
            
            # Daily stats'ga qo'shish
            db_manager.increment_orders_count(db, user_id, user.fullname, "passenger")
            
            # GROUP3 ga TELEFONSIZ yuborish
            if config.GROUP3:
                group_text = (
                    "🧍‍♂️ <b>YO'LOVCHI XIZMATI</b>\n\n"
                    f"📍 Hudud: {user.area}\n"
                    f"👤 Ism: {user.fullname}\n"
                    f"🚕 Xizmat: Taxi\n\n"
                    f"⏰ Vaqt: {datetime.utcnow().strftime('%H:%M')}\n"
                    f"🆔 Buyurtma ID: {order.order_id}"
                )
                
                try:
                    group_message = await message.bot.send_message(
                        config.GROUP3,
                        group_text,
                        reply_markup=accept_order_keyboard(order.order_id)
                    )
                    
                    # Group message ID'sini saqlash
                    db_manager.set_group_message_id(db, order.order_id, group_message.message_id)
                
                except Exception as e:
                    logger.error(f"Error sending to GROUP3: {e}")
            
            # Foydalanuvchiga javob
            text = (
                "✅ <b>Taxi buyurtma qabul qilindi!</b>\n\n"
                f"📋 Buyurtma ID: {order.order_id}\n"
                f"📍 Hudud: {user.area}\n"
                f"👤 Ism: {user.fullname}\n\n"
                "⏳ Haydovchilarning javobini kuting...\n"
                "🕐 Maksimal 7 daqiqa"
            )
            await message.answer(text)
            
            logger.info(f"Taxi order created: {order.order_id} by {user_id}")
        
        finally:
            db.close()
    
    except Exception as e:
        logger.error(f"Error in taxi_order_handler: {e}")
        await message.answer("❌ Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.")


@router.message(F.text == "🥖 Non mahsulotlariga buyurtma berish")
async def bread_order_handler(message: Message, state: FSMContext):
    try:
        user_id = message.from_user.id
        
        # FSM state'ni tozalash
        await state.clear()
        
        # Database'dan foydalanuvchini olish
        db = get_db()
        try:
            user = db_manager.get_user(db, user_id)
            
            if not user:
                await message.answer("❌ Siz ro'yxatdan o'tmagansiz! /start ni bosing.")
                return
            
            if user.user_type != "passenger":
                await message.answer("❌ Faqat yo'lovchilar buyurtma berishi mumkin!")
                return
            
            # Cooldown tekshirish
            if db_manager.check_product_cooldown(db, user_id, "🥖 Non"):
                text = (
                    "❌ Siz yaqinda non buyurtma berdingiz!\n\n"
                    "⏳ Keyingi buyurtma berish uchun 3 soat kutishingiz kerak."
                )
                await message.answer(text)
                return
            
            # Yangi buyurtma yaratish
            order = db_manager.create_order(
                db=db,
                passenger_id=user_id,
                passenger_name=user.fullname,
                passenger_phone=user.phone,
                passenger_area=user.area,
                service_type="🥖 Non",
                group_chat=config.GROUP2  # Non buyurtmalari GROUP2 ga
            )
            
            # Cooldown qo'shish
            db_manager.add_product_cooldown(db, user_id, "🥖 Non")
            
            # Daily stats'ga qo'shish
            db_manager.increment_orders_count(db, user_id, user.fullname, "passenger")
            
            # GROUP2 ga TELEFON bilan yuborish
            if config.GROUP2:
                group_text = (
                    "🥖 <b>NON BUYURTMASI</b>\n\n"
                    f"👤 Ism: {user.fullname}\n"
                    f"📞 Telefon: {user.phone}\n"
                    f"📍 Hudud: {user.area}\n"
                    f"👨‍💼 Username: @{user.telegram_name if user.telegram_name else 'mavjud emas'}\n"
                    f"🆔 ID: {user_id}\n\n"
                    f"⏰ Vaqt: {datetime.utcnow().strftime('%H:%M')}"
                )
                
                try:
                    await message.bot.send_message(config.GROUP2, group_text)
                except Exception as e:
                    logger.error(f"Error sending to GROUP2: {e}")
            
            # Foydalanuvchiga javob
            text = (
                "✅ <b>Non buyurtma qabul qilindi!</b>\n\n"
                f"📋 Buyurtma ID: {order.order_id}\n"
                f"👤 Ism: {user.fullname}\n"
                f"📞 Telefon: {user.phone}\n"
                f"📍 Hudud: {user.area}\n\n"
                "✅ Tez orada aloqaga chiqamiz!"
            )
            await message.answer(text)
            
            logger.info(f"Bread order created: {order.order_id} by {user_id}")
        
        finally:
            db.close()
    
    except Exception as e:
        logger.error(f"Error in bread_order_handler: {e}")
        await message.answer("❌ Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.")


@router.message(F.text == "🌾 Yem mahsulotlariga buyurtma berish")
async def feed_order_handler(message: Message, state: FSMContext):
    try:
        user_id = message.from_user.id
        
        # FSM state'ni tozalash
        await state.clear()
        
        # Database'dan foydalanuvchini olish
        db = get_db()
        try:
            user = db_manager.get_user(db, user_id)
            
            if not user:
                await message.answer("❌ Siz ro'yxatdan o'tmagansiz! /start ni bosing.")
                return
            
            if user.user_type != "passenger":
                await message.answer("❌ Faqat yo'lovchilar buyurtma berishi mumkin!")
                return
            
            # Cooldown tekshirish
            if db_manager.check_product_cooldown(db, user_id, "🌾 Yem"):
                text = (
                    "❌ Siz yaqinda yem buyurtma berdingiz!\n\n"
                    "⏳ Keyingi buyurtma berish uchun 3 soat kutishingiz kerak."
                )
                await message.answer(text)
                return
            
            # Yangi buyurtma yaratish
            order = db_manager.create_order(
                db=db,
                passenger_id=user_id,
                passenger_name=user.fullname,
                passenger_phone=user.phone,
                passenger_area=user.area,
                service_type="🌾 Yem",
                group_chat=config.GROUP2  # Yem buyurtmalari GROUP2 ga
            )
            
            # Cooldown qo'shish
            db_manager.add_product_cooldown(db, user_id, "🌾 Yem")
            
            # Daily stats'ga qo'shish
            db_manager.increment_orders_count(db, user_id, user.fullname, "passenger")
            
            # GROUP2 ga TELEFON bilan yuborish
            if config.GROUP2:
                group_text = (
                    "🌾 <b>YEM BUYURTMASI</b>\n\n"
                    f"👤 Ism: {user.fullname}\n"
                    f"📞 Telefon: {user.phone}\n"
                    f"📍 Hudud: {user.area}\n"
                    f"👨‍💼 Username: @{user.telegram_name if user.telegram_name else 'mavjud emas'}\n"
                    f"🆔 ID: {user_id}\n\n"
                    f"⏰ Vaqt: {datetime.utcnow().strftime('%H:%M')}"
                )
                
                try:
                    await message.bot.send_message(config.GROUP2, group_text)
                except Exception as e:
                    logger.error(f"Error sending to GROUP2: {e}")
            
            # Foydalanuvchiga javob
            text = (
                "✅ <b>Yem buyurtma qabul qilindi!</b>\n\n"
                f"📋 Buyurtma ID: {order.order_id}\n"
                f"👤 Ism: {user.fullname}\n"
                f"📞 Telefon: {user.phone}\n"
                f"📍 Hudud: {user.area}\n\n"
                "✅ Tez orada aloqaga chiqamiz!"
            )
            await message.answer(text)
            
            logger.info(f"Feed order created: {order.order_id} by {user_id}")
        
        finally:
            db.close()
    
    except Exception as e:
        logger.error(f"Error in feed_order_handler: {e}")
        await message.answer("❌ Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.")


@router.message(F.text == "🆘 Qo'llab-quvvatlash")
async def support_handler(message: Message, state: FSMContext):
    """Qo'llab-quvvatlash"""
    try:
        # FSM state'ni tozalash
        await state.clear()
        
        text = (
            "🆘 <b>Qo'llab-quvvatlash</b>\n\n"
            "Savollar yoki muammolar bo'lsa, admin bilan bog'laning:\n\n"
            "📞 Telefon: +998 XX XXX XX XX\n"
            "👨‍💼 Admin: @admin_username"
        )
        await message.answer(text)
    
    except Exception as e:
        logger.error(f"Error in support_handler: {e}")
        await message.answer("❌ Xatolik yuz berdi.")
