import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    def __init__(self):
        self.BOT_TOKEN = os.getenv("BOT_TOKEN")
        
        self.ADMIN_IDS = [5306481482]
        
        self.CHANNEL_ID = "@foydali_xizmatt" 
        self.CHANNEL_LINK = "https://t.me/foydali_xizmatt"
        self.SUPPORT_LINK = "https://t.me/SAT_mathuz"
        
        self.GROUP1 = "@salom777899"     
        self.GROUP2 = "@yo_lovchiguruh"  
        self.GROUP3 = "@uydantaksi"       
        self.GROUP4 = "@nonguruh"         
        self.GROUP5 = "@yemguruh"   

        self.DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///xizmatlar_bot.db")
        

        self.GROUP_TIMEOUT = 7 * 60        
        self.ACCEPTED_TIMEOUT = 6 * 60      
        
        self.PRODUCT_COOLDOWN = 3 * 60 * 60
        self.MAX_REJECT_COUNT = 3          
        

        self.LOG_FILE = "xizmatlar_bot.log"
        self.LOG_MAX_BYTES = 10 * 1024 * 1024  
        self.LOG_BACKUP_COUNT = 5


config = Config()


class ServiceType:
    TAXI = "🚕 Taxi"
    BREAD = "🥖 Non"
    FEED = "🌾 Yem"


class OrderStatus:

    WAITING = "waiting"       
    ACCEPTED = "accepted"       
    CONFIRMED = "confirmed"    
    CANCELLED = "cancelled"     
    COMPLETED = "completed"   


class UserRole:
    
    DRIVER = "driver"
    PASSENGER = "passenger"
