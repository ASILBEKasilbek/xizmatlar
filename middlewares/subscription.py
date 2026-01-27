"""
Kanalga obuna tekshiruvi middleware
"""
import logging
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from utils import check_subscription
from keyboards import subscription_keyboard
from config import config

logger = logging.getLogger(__name__)


class SubscriptionMiddleware(BaseMiddleware):
    """
    Kanalga obuna bo'lganmi tekshirish middleware
    - Admin'larni o'tkazib yuboradi
    - /start va check_subscription callback'larini o'tkazib yuboradi
    - Qolganlarni kanalga obuna tekshiradi
    """
    
    async def __call__(
        self,
        handler: Callable[[Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        """Middleware ishlov berish"""
        
        # User ID olish
        user_id = event.from_user.id
        
        # Admin'larni o'tkazib yuborish
        if user_id in config.ADMIN_IDS:
            return await handler(event, data)
        
        # /start komandasi uchun o'tkazib yuborish (start handler o'zi tekshiradi)
        if isinstance(event, Message):
            if event.text and event.text.startswith("/start"):
                return await handler(event, data)
        
        # check_subscription callback'ini o'tkazib yuborish
        if isinstance(event, CallbackQuery):
            if event.data == "check_subscription":
                return await handler(event, data)
        
        # Obunani tekshirish
        is_subscribed = await check_subscription(event.bot, user_id)
        
        if not is_subscribed:
            # Obuna bo'lmagan
            text = (
                "❗️ Botdan foydalanish uchun avval kanalga obuna bo'lishingiz kerak!\n\n"
                "Kanalga obuna bo'lgandan keyin <b>✅ Tasdiqlash</b> tugmasini bosing."
            )
            
            if isinstance(event, CallbackQuery):
                await event.answer("❗️ Avval kanalga obuna bo'ling!", show_alert=True)
                try:
                    await event.message.answer(text, reply_markup=subscription_keyboard())
                except Exception as e:
                    logger.error(f"Error sending subscription message: {e}")
            else:
                await event.answer(text, reply_markup=subscription_keyboard())
            
            return  # Handler'ni ishga tushirmaslik
        
        # Obuna bo'lgan - davom ettirish
        return await handler(event, data)
