import logging
from datetime import datetime
from aiogram import Bot
from aiogram.exceptions import TelegramAPIError
from config import config

logger = logging.getLogger(__name__)


async def check_subscription(bot: Bot, user_id: int) -> bool:
    if not config.CHANNEL_ID:
        return True  
    
    try:
        member = await bot.get_chat_member(config.CHANNEL_ID, user_id)
        return member.status in ["member", "administrator", "creator"]
    except TelegramAPIError as e:
        logger.error(f"Kanal obunasini tekshirishda xato {config.CHANNEL_ID}: {e}")
        return False  

def format_datetime(dt: datetime) -> str:
    return dt.strftime("%d.%m.%Y %H:%M")


def format_date(date_str: str) -> datetime:
    try:
        return datetime.strptime(date_str, "%d.%m.%Y")
    except ValueError:
        return None
