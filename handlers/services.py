"""
Services handler - Taxi, Non, Yem buyurtma berish
"""
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
    """
    Taxi buyurtma berish
    - 1 foydalanuvchi 1 faol buyurtma
    - Buyurtma GROUP3 ga yuboriladi
    - Telefon raqam guruhda ko'rinmaydi
    """
    try:
        user_id = message.from_user.id
        
        db = get_db()
        try:
            # Foydalanuvchini tekshirish
            user = db_manager.get_user(db, user_id)
            
            if not user:
                await message.answer("❌ Avval ro'yxatdan o'ting! /start bosing.")
                return
            
            if user.user_type != "passenger":
                await message.answer("❌ Faqat yo'lovchilar taxi buyurtma qilishi mumkin!")
                return
            
            # Aktiv buyurtmani tekshirish
            active_order = db_manager.get_active_taxi_order(db, user_id)
            
            if active_order:
                await message.answer(
                    f"❌ Sizda allaqachon aktiv buyurtma bor!\n"
                    f"📋 Buyurtma ID: {active_order.order_id}\n"
                    f"⏳ Status: {active_order.status}\n\n"
                    f"Iltimos, joriy buyurtma tugashini kuting."
                )
                return
            
            # Yangi buyurtma yaratish
            order = db_manager.create_order(
                db=db,
                passenger_id=user_id,
                passenger_name=user.fullname,
                passenger_phone=user.phone,
                passenger_area=user.area,
                service_type=ServiceType.TAXI,
                group_chat=config.GROUP3
            )
            
            # Statistikani yangilash
            db_manager.update_stats_order_created(db, user_id, user.fullname)
            
            # GROUP3 ga yuborish (telefon raqamsiz)
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
                
                # Guruh xabar ID'sini saqlash
                db_manager.update_order_group_message(db, order.order_id, group_msg.message_id)
                
            except Exception as e:
                logger.error(f"Error sending to GROUP3: {e}")
                await message.answer("❌ Buyurtma guruhga yuborbilmadi. Iltimos, qaytadan urinib ko'ring.")
                return
            
            # Foydalanuvchiga xabar
            success_text = (
                "✅ <b>Buyurtmangiz qabul qilindi.</b> Iltimos kuting, sizga aloqaga chiqishadi."
                # f"📋 Buyurtma ID: #{order.order_id}\n"
                # f"⏳ Status: Kutilmoqda...\n\n"
                # f"Haydovchilar {config.GROUP3} guruhida buyurtmangizni ko'rishadi.\n"
                # f"Iltimos kuting, sizga aloqaga chiqishadi."
            )
            await message.answer(success_text)
            
        finally:
            db.close()
    
    except Exception as e:
        logger.error(f"Error in taxi_order_handler: {e}")
        await message.answer("❌ Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.")


@router.message(F.text == "💬 Qo'llab-quvvatlash")
async def quvatlash(message: Message):
    await message.answer("""💬 Qo'llab-quvvatlash
Telegram:usernamiz yuq ekan tashlasayiz quyib quyaman
""")


@router.message(F.text == "🥖 Non buyurtma berish")
async def bread_order_handler(message: Message):
    try:
        user_id = message.from_user.id
        
        db = get_db()
        try:
            # Foydalanuvchini tekshirish
            user = db_manager.get_user(db, user_id)
            
            if not user:
                await message.answer("❌ Avval ro'yxatdan o'ting! /start bosing.")
                return
            
            if user.user_type != "passenger":
                await message.answer("❌ Faqat yo'lovchilar non buyurtma qilishi mumkin!")
                return
            
            # 3 soatlik cheklovni tekshirish
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
            
            # GROUP4 ga foydalanuvchi ma'lumotlarini yuborish
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
            
            # Cooldown o'rnatish
            db_manager.set_product_cooldown(db, user_id, ServiceType.BREAD)
            
            # Foydalanuvchiga xabar
            success_text = (
                "✅ <b>Buyurtmangiz qabul qilindi.</b> Iltimos kuting, sizga aloqaga chiqishadi."
                # f"👤 Ism: {user.fullname}\n"
                # f"📞 Telefon: {user.phone}\n"
                # f"📍 Hudud: {user.area}\n\n"
                # f"Ma'lumotlaringiz {config.GROUP4} guruhiga yuborildi.\n"
                # f"Tez orada siz bilan bog'lanishadi!\n\n"
                # f"⏳ Keyingi buyurtma 3 soatdan keyin!"
            )
            await message.answer(success_text)
            
        finally:
            db.close()
    
    except Exception as e:
        logger.error(f"Error in bread_order_handler: {e}")
        await message.answer("❌ Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.")


@router.message(F.text == "🌾 Yem buyurtma berish")
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
            
            # Cooldown o'rnatish
            db_manager.set_product_cooldown(db, user_id, ServiceType.FEED)
            
            # Foydalanuvchiga xabar
            success_text = (
                # "✅ <b>Yem buyurtmangiz qabul qilindi!</b>\n\n"
                "✅ <b>Buyurtmangiz qabul qilindi.</b> Iltimos kuting, sizga aloqaga chiqishadi."
                # f"👤 Ism: {user.fullname}\n"
                # f"📞 Telefon: {user.phone}\n"
                # f"📍 Hudud: {user.area}\n\n"
                # f"Ma'lumotlaringiz {config.GROUP5} guruhiga yuborildi.\n"
                # f"Tez orada siz bilan bog'lanishadi!\n\n"
                # f"⏳ Keyingi buyurtma 3 soatdan keyin!"
            )
            await message.answer(success_text)
            
        finally:
            db.close()
    
    except Exception as e:
        logger.error(f"Error in feed_order_handler: {e}")
        await message.answer("❌ Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.")
