"""
Yordamchi funksiyalar - Validatsiya, formatlash
"""
import re
import logging
from datetime import datetime
from aiogram import Bot
from aiogram.exceptions import TelegramAPIError
from config import config

logger = logging.getLogger(__name__)


# ===== VALIDATSIYA FUNKSIYALARI =====

def validate_fullname(fullname: str) -> bool:
    """
    Ism-familiyani tekshirish
    - Faqat harflar, bo'sh joy va - ruxsat
    - Maksimal 40 ta belgi
    """
    if not fullname or len(fullname) > 40:
        return False
    pattern = r"^[a-zA-Zа-яА-ЯёЁўЎқҚғҒҳҲ\s'\-]+$"
    return bool(re.match(pattern, fullname))


def validate_phone(phone: str) -> bool:
    """
    Telefon raqamini tekshirish
    - +998XXXXXXXXX formatida yoki
    - 9 xonali raqam
    """
    phone = phone.strip().replace(" ", "").replace("-", "")
    
    if phone.startswith("+998") and len(phone) == 13:
        return True
    elif phone.isdigit() and len(phone) == 9:
        return True
    
    return False


def format_phone(phone: str) -> str:
    """
    Telefon raqamini formatlash
    - Barcha raqamlarni +998XXXXXXXXX formatiga keltiradi
    """
    phone = phone.strip().replace(" ", "").replace("-", "")
    
    if phone.startswith("+998"):
        return phone
    elif phone.isdigit() and len(phone) == 9:
        return f"+998{phone}"
    
    return phone


# ===== KANAL OBUNA TEKSHIRUVI =====

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


# ===== VAQT FORMATLASH =====

def format_datetime(dt: datetime) -> str:
    """Vaqtni formatlash - 26.01.2026 14:30"""
    return dt.strftime("%d.%m.%Y %H:%M")


def format_date(date_str: str) -> datetime:
    """Sana stringini datetime ga o'girish (DD.MM.YYYY)"""
    try:
        return datetime.strptime(date_str, "%d.%m.%Y")
    except ValueError:
        return None
