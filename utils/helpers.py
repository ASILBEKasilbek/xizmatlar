"""
Yordamchi funksiyalar
"""
import logging
from datetime import datetime
from aiogram import Bot
from aiogram.exceptions import TelegramAPIError
from config import config

logger = logging.getLogger(__name__)


async def check_subscription(bot: Bot, user_id: int) -> bool:
    """
    Foydalanuvchi kanalga obuna bo'lganmi tekshirish
    - config.CHANNEL_ID kanalini tekshiradi
    - member, administrator, creator statuslari qabul qilinadi
    """
    if not config.CHANNEL_ID:
        return True  # Kanal yo'q bo'lsa, obuna talab qilinmaydi
    
    try:
        member = await bot.get_chat_member(config.CHANNEL_ID, user_id)
        return member.status in ["member", "administrator", "creator"]
    except TelegramAPIError as e:
        logger.error(f"Kanal obunasini tekshirishda xato {config.CHANNEL_ID}: {e}")
        return False  # Xato bo'lsa, obuna bo'lmagan deb hisoblaymiz


def format_datetime(dt: datetime) -> str:
    """Vaqtni formatlash - 26.01.2026 14:30"""
    return dt.strftime("%d.%m.%Y %H:%M")


def format_date(date_str: str) -> datetime:
    """Sana stringini datetime ga o'girish (DD.MM.YYYY)"""
    try:
        return datetime.strptime(date_str, "%d.%m.%Y")
    except ValueError:
        return None
