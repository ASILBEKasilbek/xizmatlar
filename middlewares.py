"""
Middleware'lar - Subscription checker
"""
import logging
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from utils import check_subscription
from keyboards import subscription_keyboard

logger = logging.getLogger(__name__)


class SubscriptionMiddleware(BaseMiddleware):
    """Foydalanuvchi kanalga obuna bo'lganmi tekshirish"""
    
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        """Middleware ishlov berish"""
        
        # Callback query dan user olish
        if isinstance(event, CallbackQuery):
            user_id = event.from_user.id
            # check_subscription callback'ini o'tkazib yuborish
            if event.data == "check_subscription":
                return await handler(event, data)
        else:
            user_id = event.from_user.id
            # /start komandasi uchun middleware ishlamaydi (start handler o'zi tekshiradi)
            if event.text and event.text.startswith("/start"):
                return await handler(event, data)
        
        # Admin va servicelar botning o'zini o'tkazib yuborish
        from config import config
        if user_id in config.ADMIN_IDS:
            return await handler(event, data)
        
        # Obunani tekshirish
        is_subscribed = await check_subscription(event.bot, user_id)
        
        if not is_subscribed:
            # Obuna bo'lmagan - xabar yuborish
            text = (
                "❗️ Botdan foydalanish uchun avval kanalimizga obuna bo'lishingiz kerak!\n\n"
                "Obuna bo'lgandan keyin <b>✅ Tasdiqlash</b> tugmasini bosing."
            )
            
            if isinstance(event, CallbackQuery):
                await event.answer("❗️ Avval kanalga obuna bo'ling!", show_alert=True)
                try:
                    await event.message.answer(text, reply_markup=subscription_keyboard())
                except:
                    pass
            else:
                await event.answer(text, reply_markup=subscription_keyboard())
            
            return
        
        # Obuna bo'lgan - davom ettirish
        return await handler(event, data)
