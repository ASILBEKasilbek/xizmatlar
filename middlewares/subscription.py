import logging
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from utils import check_subscription
from keyboards import subscription_keyboard
from config import config

logger = logging.getLogger(__name__)


class SubscriptionMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        user_id = event.from_user.id
        if user_id in config.ADMIN_IDS:
            return await handler(event, data)
        
        if isinstance(event, Message):
            if event.text and event.text.startswith("/start"):
                return await handler(event, data)
        
        if isinstance(event, CallbackQuery):
            if event.data == "check_subscription":
                return await handler(event, data)
        
        is_subscribed = await check_subscription(event.bot, user_id)
        
        if not is_subscribed:
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
            
            return  
        
        return await handler(event, data)
