"""
Bot konfiguratsiyasi - Barcha sozlamalar
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Bot konfiguratsiyasi"""
    
    def __init__(self):
        # ===== BOT ASOSIY SOZLAMALARI =====
        self.BOT_TOKEN = os.getenv("BOT_TOKEN")
        
        # ===== ADMIN =====
        # Sizning ID'ingiz
        self.ADMIN_IDS = [5306481482]
        
        # ===== KANAL =====
        self.CHANNEL_ID = "@foydali_xizmatt"  # Majburiy obuna kanali
        self.CHANNEL_LINK = "https://t.me/foydali_xizmatt"
        self.SUPPORT_LINK = "https://t.me/SAT_mathuz"
        
        # ===== GURUHLAR =====
        self.GROUP1 = "@salom777899"      # Haydovchilar ro'yxati (yangi haydovchi ma'lumotlari)
        self.GROUP2 = "@yo_lovchiguruh"   # Yo'lovchilar ro'yxati (yangi yo'lovchi ma'lumotlari)
        self.GROUP3 = "@uydantaksi"       # Taxi buyurtmalari
        self.GROUP4 = "@nonguruh"         # Non buyurtmalari
        self.GROUP5 = "@yemguruh"         # Yem buyurtmalari
        
        # ===== DATABASE =====
        self.DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///xizmatlar_bot.db")
        
        # ===== TAYMERLAR (soniyalarda) =====
        self.GROUP_TIMEOUT = 7 * 60          # 7 daqiqa - hech kim bosmasa buyurtma yopiladi
        self.ACCEPTED_TIMEOUT = 6 * 60       # 6 daqiqa - haydovchi jim bo'lsa rad bo'ladi
        
        # ===== CHEKLOVLAR =====
        self.PRODUCT_COOLDOWN = 3 * 60 * 60  # 3 soat - Non/Yem uchun
        self.MAX_REJECT_COUNT = 3            # 3 marta rad etilsa butunlay yopiladi
        
        # ===== LOGGING =====
        self.LOG_FILE = "xizmatlar_bot.log"
        self.LOG_MAX_BYTES = 10 * 1024 * 1024  # 10 MB
        self.LOG_BACKUP_COUNT = 5


config = Config()


# ===== XIZMAT TURLARI =====
class ServiceType:
    """Xizmat turlari"""
    TAXI = "🚕 Taxi"
    BREAD = "🥖 Non"
    FEED = "🌾 Yem"


# ===== BUYURTMA STATUSLARI =====
class OrderStatus:
    """Buyurtma statuslari"""
    WAITING = "waiting"         # Guruhda kutmoqda
    ACCEPTED = "accepted"       # Haydovchi qabul qildi
    CONFIRMED = "confirmed"     # Haydovchi tasdiqladi
    CANCELLED = "cancelled"     # Bekor qilindi
    COMPLETED = "completed"     # Yakunlandi


# ===== FOYDALANUVCHI ROLLARI =====
class UserRole:
    """Foydalanuvchi rollari"""
    DRIVER = "driver"
    PASSENGER = "passenger"
