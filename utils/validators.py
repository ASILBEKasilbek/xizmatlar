"""
Validatsiya funksiyalari
"""
import re


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
