"""
Bot Configuration Module
Barcha konfiguratsiyalar va o'zgarmalarni shu yerda saqlash
"""

import os
from dataclasses import dataclass


@dataclass
class Config:
    """Bot va database konfiguratsiyasi"""
    
    # Telegram Bot Tokens va ID'lar
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
    ADMIN_IDS: list = [int(x) for x in os.getenv("ADMIN_IDS", "123456789").split(",")]
    CHANNEL_ID: int = int(os.getenv("CHANNEL_ID", "-1001234567890"))
    
    # Guruhlar ID'ari
    DRIVERS_GROUP_ID: int = int(os.getenv("DRIVERS_GROUP_ID", "-1001234567891"))
    PASSENGERS_GROUP_ID: int = int(os.getenv("PASSENGERS_GROUP_ID", "-1001234567892"))
    DRIVERS_ORDERS_GROUP_ID: int = int(os.getenv("DRIVERS_ORDERS_GROUP_ID", "-1001234567893"))
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "sqlite:///./xizmatlar_bot.db"
    )
    
    # Timers (sekundda)
    TAXI_ORDER_TIMEOUT: int = 7 * 60  # 7 daqiqa
    DRIVER_RESPONSE_TIMEOUT: int = 6 * 60  # 6 daqiqa
    BREAD_COOLDOWN: int = 3 * 60 * 60  # 3 soat
    FEED_COOLDOWN: int = 3 * 60 * 60  # 3 soat
    
    # Haydovchi radlarini cheklov
    MAX_DECLINE_BEFORE_CANCEL: int = 3
    
    # Pagination
    ITEMS_PER_PAGE: int = 10
    
    # Redis (opsional, kesh uchun)
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")


config = Config()


# Xizmat turlarining konstant qiymatlari
class ServiceType:
    TAXI = "taxi"
    BREAD = "bread"
    FEED = "feed"


class OrderStatus:
    WAITING = "waiting"
    ACCEPTED = "accepted"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class UserRole:
    DRIVER = "driver"
    PASSENGER = "passenger"
    ADMIN = "admin"
