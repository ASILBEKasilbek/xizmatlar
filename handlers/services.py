import logging
from aiogram import Router, F
from aiogram.types import Message
from database import get_db, db_manager
from keyboards import accept_order_keyboard
from config import config, ServiceType

logger = logging.getLogger(__name__)

router = Router()


@router.message(F.text == "🚕 Taxi")
async def taxi_order_handler(message: Message):
    try:
        user_id = message.from_user.id
        
        db = get_db()
        try:
            user = db_manager.get_user(db, user_id)
            
            if not user:
                await message.answer("❌ Avval ro'yxatdan o'ting! /start bosing.")
                return
            
            if user.user_type != "passenger":
                await message.answer("❌ Faqat yo'lovchilar taxi buyurtma qilishi mumkin!")
                return
            
            active_order = db_manager.get_active_taxi_order(db, user_id)
            
            if active_order:
                await message.answer(
                    f"❌ Sizda allaqachon aktiv buyurtma bor!\n"
                    f"📋 Buyurtma ID: {active_order.order_id}\n"
                    f"⏳ Status: {active_order.status}\n\n"
                    f"Iltimos, joriy buyurtma tugashini kuting."
                )
                return
            
            order = db_manager.create_order(
                db=db,
                passenger_id=user_id,
                passenger_name=user.fullname,
                passenger_phone=user.phone,
                passenger_area=user.area,
                service_type=ServiceType.TAXI,
                group_chat=config.GROUP3
            )
            
            db_manager.update_stats_order_created(db, user_id, user.fullname)
            
            group_text = (
                "🚕 <b>YANGI TAXI BUYURTMA</b>\n\n"
                f"📋 Buyurtma ID: #{order.order_id}\n"
                f"👤 Yo'lovchi: {user.fullname}\n"
                f"📍 Hudud: {user.area}\n"
            )
            
            try:
                group_msg = await message.bot.send_message(
                    config.GROUP3, 
                    group_text, 
                    reply_markup=accept_order_keyboard(order.order_id)
                )
                
                db_manager.update_order_group_message(db, order.order_id, group_msg.message_id)
                
            except Exception as e:
                logger.error(f"Error sending to GROUP3: {e}")
                await message.answer("❌ Buyurtma guruhga yuborbilmadi. Iltimos, qaytadan urinib ko'ring.")
                return
            
            success_text = ("✅ <b>Buyurtmangiz qabul qilindi.</b> Iltimos kuting, sizga aloqaga chiqishadi.")
            await message.answer(success_text)
            
        finally:
            db.close()
    
    except Exception as e:
        logger.error(f"Error in taxi_order_handler: {e}")
        await message.answer("❌ Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.")


@router.message(F.text == "💬 Qo'llab-quvvatlash")
async def quvatlash(message: Message):
    await message.answer("""💬 Qo'llab-quvvatlash
Telegram: @SAT_mathuz
""")


@router.message(F.text == "🥖 Non mahsulotlariga buyurtma berish")
async def bread_order_handler(message: Message):
    try:
        user_id = message.from_user.id
        
        db = get_db()
        try:
            user = db_manager.get_user(db, user_id)
            
            if not user:
                await message.answer("❌ Avval ro'yxatdan o'ting! /start bosing.")
                return
            
            if user.user_type != "passenger":
                await message.answer("❌ Faqat yo'lovchilar non buyurtma qilishi mumkin!")
                return
            
            has_cooldown = db_manager.check_product_cooldown(db, user_id, ServiceType.BREAD)
            
            if has_cooldown:
                remaining_seconds = db_manager.get_remaining_cooldown_time(db, user_id, ServiceType.BREAD)
                hours = remaining_seconds // 3600
                minutes = (remaining_seconds % 3600) // 60
                
                await message.answer(
                    f"❌ Siz 3 soat ichida faqat 1 marta non buyurtma qilishingiz mumkin!\n\n"
                    f"⏳ Qolgan vaqt: {hours} soat {minutes} daqiqa\n\n"
                    f"Iltimos, kutib turing."
                )
                return
            
            group_text = (
                "🥖 <b>YANGI NON BUYURTMA</b>\n\n"
                f"👤 Ism: {user.fullname}\n"
                f"📞 Telefon: {user.phone}\n"
                f"📍 Hudud: {user.area}\n"
                f"📱 Telegram: @{user.telegram_name}\n"
                f"🆔 ID: {user_id}"
            )
            
            try:
                await message.bot.send_message(config.GROUP4, group_text)
            except Exception as e:
                logger.error(f"Error sending to GROUP4: {e}")
                await message.answer("❌ Buyurtma guruhga yuborilmadi. Iltimos, qaytadan urinib ko'ring.")
                return
            
            db_manager.set_product_cooldown(db, user_id, ServiceType.BREAD)
            
            success_text = ("✅ <b>Buyurtmangiz qabul qilindi.</b> Iltimos kuting, sizga aloqaga chiqishadi.")
            await message.answer(success_text)
            
        finally:
            db.close()
    
    except Exception as e:
        logger.error(f"Error in bread_order_handler: {e}")
        await message.answer("❌ Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.")


@router.message(F.text == "🌾 Yem mahsulotlariga buyurtma berish")
async def feed_order_handler(message: Message):
    try:
        user_id = message.from_user.id
        
        db = get_db()
        try:

            user = db_manager.get_user(db, user_id)
            
            if not user:
                await message.answer("❌ Avval ro'yxatdan o'ting! /start bosing.")
                return
            
            if user.user_type != "passenger":
                await message.answer("❌ Faqat yo'lovchilar yem buyurtma qilishi mumkin!")
                return
            
            has_cooldown = db_manager.check_product_cooldown(db, user_id, ServiceType.FEED)
            
            if has_cooldown:
                remaining_seconds = db_manager.get_remaining_cooldown_time(db, user_id, ServiceType.FEED)
                hours = remaining_seconds // 3600
                minutes = (remaining_seconds % 3600) // 60
                
                await message.answer(
                    f"❌ Siz 3 soat ichida faqat 1 marta yem buyurtma qilishingiz mumkin!\n\n"
                    f"⏳ Qolgan vaqt: {hours} soat {minutes} daqiqa\n\n"
                    f"Iltimos, kutib turing."
                )
                return
            
            group_text = (
                "🌾 <b>YANGI YEM BUYURTMA</b>\n\n"
                f"👤 Ism: {user.fullname}\n"
                f"📞 Telefon: {user.phone}\n"
                f"📍 Hudud: {user.area}\n"
                f"📱 Telegram: @{user.telegram_name}\n"
                f"🆔 ID: {user_id}"
            )
            
            try:
                await message.bot.send_message(config.GROUP5, group_text)
            except Exception as e:
                logger.error(f"Error sending to GROUP5: {e}")
                await message.answer("❌ Buyurtma guruhga yuborilmadi. Iltimos, qaytadan urinib ko'ring.")
                return
            
            db_manager.set_product_cooldown(db, user_id, ServiceType.FEED)
            
            success_text = (
                "✅ <b>Buyurtmangiz qabul qilindi.</b> Iltimos kuting, sizga aloqaga chiqishadi."
            )
            await message.answer(success_text)
            
        finally:
            db.close()
    
    except Exception as e:
        logger.error(f"Error in feed_order_handler: {e}")
        await message.answer("❌ Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.")
