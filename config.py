"""
Bot konfiguratsiyasi
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Bot konfiguratsiyasi"""
    
    def __init__(self):
        # Bot tokeni
        self.BOT_TOKEN = os.getenv("BOT_TOKEN")
        
        # Admin ID'lari (vergul bilan ajratilgan)
        self.ADMIN_IDS = [int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]
        
        # Majburiy kanal
        self.CHANNEL_ID = os.getenv("CHANNEL_ID")  # @channel_username yoki -100123456789
        
        # Guruhlar
        self.GROUP1 = int(os.getenv("GROUP1")) if os.getenv("GROUP1") else None  # Haydovchilar guruhi
        self.GROUP2 = int(os.getenv("GROUP2")) if os.getenv("GROUP2") else None  # Yo'lovchilar guruhi
        self.GROUP3 = int(os.getenv("GROUP3")) if os.getenv("GROUP3") else None  # Buyurtmalar guruhi
        
        # Database
        self.DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///taksi_bot.db")
        
        # Timeoutlar (soniyalarda)
        self.GROUP_TIMEOUT = 7 * 60  # 7 daqiqa
        self.ACCEPTED_TIMEOUT = 6 * 60  # 6 daqiqa
        
        # Cooldown (soniyalarda)
        self.PRODUCT_COOLDOWN = 3 * 60 * 60  # 3 soat
        
        # Maksimal rad etish soni
        self.MAX_REJECT_COUNT = 3
        
        # Logging
        self.LOG_FILE = "taksi_bot.log"
        self.LOG_MAX_BYTES = 10 * 1024 * 1024  # 10 MB
        self.LOG_BACKUP_COUNT = 5


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
