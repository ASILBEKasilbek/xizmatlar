from typing import Callable, Dict, Any, Awaitable, Union
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

from database import get_db, db_manager

Event = Union[Message, CallbackQuery]

class BanCheckMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Event, Dict[str, Any]], Awaitable[Any]],
        event: Event,
        data: Dict[str, Any],
    ) -> Any:
        user_id = event.from_user.id

        db = get_db()
        try:
            if db_manager.is_user_banned(db, user_id):
                if isinstance(event, CallbackQuery):
                    await event.answer("🚫 Siz botdan foydalanolmaysiz.", show_alert=True)
                else:
                    await event.answer("🚫 Siz botdan foydalanolmaysiz.")
                return
        finally:
            db.close()

        return await handler(event, data)
