"""
Utility Functions va Helpers
Barcha shuqliy funksiyalar
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class DateHelper:
    """Sana bilan ishlash uchun helper"""
    
    @staticmethod
    def format_datetime(dt: datetime, format_str: str = "%d.%m.%Y %H:%M") -> str:
        """Sana va vaqtni formatida berish"""
        if dt is None:
            return "N/A"
        return dt.strftime(format_str)
    
    @staticmethod
    def get_time_ago(dt: datetime) -> str:
        """Vaqt farqini Uzbek tilidda berish"""
        if dt is None:
            return "N/A"
        
        now = datetime.utcnow()
        diff = now - dt
        
        if diff.days > 0:
            return f"{diff.days} kun oldin"
        
        hours = diff.seconds // 3600
        if hours > 0:
            return f"{hours} soat oldin"
        
        minutes = diff.seconds // 60
        if minutes > 0:
            return f"{minutes} daqiqa oldin"
        
        return "Hozir"
    
    @staticmethod
    def get_remaining_time(dt: datetime, timeout_seconds: int) -> str:
        """Qolgan vaqtni Uzbek tilidda berish"""
        now = datetime.utcnow()
        elapsed = now - dt
        remaining_seconds = timeout_seconds - elapsed.total_seconds()
        
        if remaining_seconds <= 0:
            return "Vaqt tugadi"
        
        minutes = int(remaining_seconds // 60)
        seconds = int(remaining_seconds % 60)
        
        return f"{minutes}:{seconds:02d}"


class ValidationHelper:
    """Validatsiya uchun helper"""
    
    @staticmethod
    def is_valid_phone(phone: str) -> bool:
        """Telefon raqamni validatsiya qilish"""
        import re
        pattern = r"^\+?\d{10,20}$"
        return bool(re.match(pattern, phone.replace(" ", "")))
    
    @staticmethod
    def is_valid_date(date_str: str, format_str: str = "%d.%m.%Y") -> bool:
        """Sanani validatsiya qilish"""
        try:
            datetime.strptime(date_str, format_str)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def is_valid_car_number(car_number: str) -> bool:
        """Mashina davlat raqamini validatsiya qilish"""
        import re
        # Uzbekistan format: 01A001AA yoki 10A001AA
        pattern = r"^[0-9]{2}[A-Z]{1}[0-9]{3}[A-Z]{2}$"
        return bool(re.match(pattern, car_number.replace(" ", "").upper()))


class TextHelper:
    """Matn bilan ishlash uchun helper"""
    
    @staticmethod
    def truncate(text: str, max_length: int = 100) -> str:
        """Matnni kesib, ellipsis qo'shish"""
        if len(text) <= max_length:
            return text
        return text[:max_length] + "..."
    
    @staticmethod
    def format_name(first_name: str, last_name: Optional[str] = None) -> str:
        """Ism va familiyani formatida berish"""
        if not first_name:
            return "Unknown User"
        
        if last_name:
            return f"{first_name} {last_name}"
        
        return first_name
    
    @staticmethod
    def clean_input(text: str) -> str:
        """Kiritilgan matnni tozalash"""
        if not text:
            return ""
        
        return text.strip().replace("\n", " ").replace("\t", " ")


class PaginationHelper:
    """Pagination uchun helper"""
    
    @staticmethod
    def paginate(items: List, page: int = 1, per_page: int = 10) -> Dict:
        """Itemlarni sahifalarga bo'lish"""
        total = len(items)
        total_pages = (total + per_page - 1) // per_page
        
        # Page validatsiyasi
        if page < 1:
            page = 1
        if page > total_pages:
            page = total_pages
        
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        
        return {
            "items": items[start_idx:end_idx],
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }


class StatusHelper:
    """Status bilan ishlash uchun helper"""
    
    STATUS_EMOJIS = {
        "waiting": "⏳",
        "accepted": "👤",
        "confirmed": "✅",
        "cancelled": "❌",
        "completed": "🏁"
    }
    
    STATUS_TEXTS = {
        "waiting": "Kutilmoqda",
        "accepted": "Qabul qilindi",
        "confirmed": "Tasdiqlandi",
        "cancelled": "Bekor qilindi",
        "completed": "Yakunlandi"
    }
    
    SERVICE_EMOJIS = {
        "taxi": "🚕",
        "bread": "🥖",
        "feed": "🌾"
    }
    
    SERVICE_TEXTS = {
        "taxi": "Taxi",
        "bread": "Non",
        "feed": "Yem"
    }
    
    @staticmethod
    def get_status_emoji(status: str) -> str:
        """Status emojisini olish"""
        return StatusHelper.STATUS_EMOJIS.get(status, "❓")
    
    @staticmethod
    def get_status_text(status: str) -> str:
        """Status matnini olish"""
        return StatusHelper.STATUS_TEXTS.get(status, "Noma'lum")
    
    @staticmethod
    def get_service_emoji(service_type: str) -> str:
        """Xizmat turi emojisini olish"""
        return StatusHelper.SERVICE_EMOJIS.get(service_type, "❓")
    
    @staticmethod
    def get_service_text(service_type: str) -> str:
        """Xizmat turi matnini olish"""
        return StatusHelper.SERVICE_TEXTS.get(service_type, "Noma'lum")


class RatingHelper:
    """Reyting bilan ishlash uchun helper"""
    
    @staticmethod
    def format_rating(rating: float) -> str:
        """Reytingni formatida berish"""
        stars = int(rating)
        return "⭐" * stars + "☆" * (5 - stars)
    
    @staticmethod
    def calculate_rating_change(confirmed: int, declined: int) -> float:
        """Reyting o'zgarishini hisoblash"""
        if confirmed + declined == 0:
            return 5.0
        
        success_rate = confirmed / (confirmed + declined)
        base_rating = 5.0
        
        # Success rate bo'yicha reyting hisoblash
        if success_rate >= 0.95:
            return 5.0
        elif success_rate >= 0.85:
            return 4.5
        elif success_rate >= 0.75:
            return 4.0
        elif success_rate >= 0.65:
            return 3.5
        else:
            return 3.0


class LogHelper:
    """Loggingni o'rnatish uchun helper"""
    
    @staticmethod
    def setup_logging(log_file: str = "bot.log", level=logging.INFO):
        """Loggingni o'rnatish"""
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_format)
        
        # File handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_format)
        
        # Root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(level)
        root_logger.addHandler(console_handler)
        root_logger.addHandler(file_handler)
        
        return root_logger
