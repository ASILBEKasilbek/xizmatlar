"""
Utility funksiyalari
"""
import re
import logging
from datetime import datetime
from aiogram import Bot
from aiogram.exceptions import TelegramAPIError
from config import config

logger = logging.getLogger(__name__)


def validate_fullname(fullname: str) -> bool:
    """Ism-familiyani tekshirish"""
    if not fullname or len(fullname) > 40:
        return False
    # Faqat harflar, bo'sh joy, ' va - ruxsat
    pattern = r"^[a-zA-Zа-яА-ЯёЁўЎқҚғҒҳҲ\s'\-]+$"
    return bool(re.match(pattern, fullname))


def validate_phone(phone: str) -> bool:
    """Telefon raqamini tekshirish"""
    # +998XXXXXXXXX yoki 9 xonali raqam
    phone = phone.strip().replace(" ", "").replace("-", "")
    
    if phone.startswith("+998") and len(phone) == 13:
        return True
    elif phone.isdigit() and len(phone) == 9:
        return True
    
    return False


def format_phone(phone: str) -> str:
    """Telefon raqamini formatlash"""
    phone = phone.strip().replace(" ", "").replace("-", "")
    
    if phone.startswith("+998"):
        return phone
    elif phone.isdigit() and len(phone) == 9:
        return f"+998{phone}"
    
    return phone


async def check_subscription(bot: Bot, user_id: int) -> bool:
    """Foydalanuvchi kanalga obuna bo'lganmi tekshirish"""
    try:
        member = await bot.get_chat_member(config.CHANNEL_ID, user_id)
        return member.status in ["member", "administrator", "creator"]
    except TelegramAPIError as e:
        logger.error(f"Error checking subscription: {e}")
        return False


def format_datetime(dt: datetime) -> str:
    """Vaqtni formatlash"""
    return dt.strftime("%d.%m.%Y %H:%M")


def format_date(date_str: str) -> datetime:
    """Sana stringini datetime ga o'girish (DD.MM.YYYY)"""
    try:
        return datetime.strptime(date_str, "%d.%m.%Y")
    except ValueError:
        return None
