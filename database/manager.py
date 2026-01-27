"""
Database manager - CRUD operatsiyalari
"""
import logging
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from config import config
from .models import Base, User, Order, ProductCooldown

logger = logging.getLogger(__name__)

# Database yaratish
engine = create_engine(
    config.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in config.DATABASE_URL else {},
    echo=False
)

SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def init_db():
    """Database jadvallarini yaratish"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Error initializing database: {e}")
        raise


def get_db() -> Session:
    """Database session olish"""
    return SessionLocal()


class DatabaseManager:
    """Ma'lumotlar bazasi bilan ishlash uchun barcha funksiyalar"""
    
    # ===== USER OPERATIONS =====
    
    @staticmethod
    def get_user(db: Session, user_id: int) -> User:
        """Foydalanuvchini olish"""
        return db.query(User).filter(User.user_id == user_id).first()
    
    @staticmethod
    def create_user(
        db: Session, 
        user_id: int, 
        fullname: str, 
        phone: str, 
        user_type: str, 
        car_model: str = None, 
        area: str = None,
        latitude: str = None,
        longitude: str = None,
        telegram_name: str = None
    ) -> User:
        """Yangi foydalanuvchi yaratish"""
        try:
            user = User(
                user_id=user_id,
                fullname=fullname,
                phone=phone,
                user_type=user_type,
                car_model=car_model,
                area=area,
                latitude=latitude,
                longitude=longitude,
                telegram_name=telegram_name
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.info(f"✅ User created: {user_id} - {fullname} ({user_type})")
            return user
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Error creating user: {e}")
            raise
    
    @staticmethod
    def get_all_drivers(db: Session):
        """Barcha haydovchilarni olish"""
        return db.query(User).filter(User.user_type == "driver").all()
    
    @staticmethod
    def get_all_passengers(db: Session):
        """Barcha yo'lovchilarni olish"""
        return db.query(User).filter(User.user_type == "passenger").all()
    
    # ===== ORDER OPERATIONS =====
    
    @staticmethod
    def create_order(
        db: Session, 
        passenger_id: int, 
        passenger_name: str, 
        passenger_phone: str, 
        passenger_area: str, 
        service_type: str, 
        group_chat: str
    ) -> Order:
        """Yangi buyurtma yaratish"""
        try:
            order = Order(
                passenger_id=passenger_id,
                passenger_name=passenger_name,
                passenger_phone=passenger_phone,
                passenger_area=passenger_area,
                service_type=service_type,
                group_chat=group_chat,
                status="waiting"
            )
            db.add(order)
            db.commit()
            db.refresh(order)
            logger.info(f"✅ Order created: #{order.order_id} - {service_type} by {passenger_name}")
            return order
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Error creating order: {e}")
            raise
    
    @staticmethod
    def get_order(db: Session, order_id: int) -> Order:
        """Buyurtmani ID bo'yicha olish"""
        return db.query(Order).filter(Order.order_id == order_id).first()
    
    @staticmethod
    def get_active_taxi_order(db: Session, passenger_id: int) -> Order:
        """Yo'lovchining aktiv taxi buyurtmasini olish"""
        return db.query(Order).filter(
            Order.passenger_id == passenger_id,
            Order.service_type == "🚕 Taxi",
            Order.status.in_(["waiting", "accepted"])
        ).first()
    
    @staticmethod
    def get_driver_active_order(db: Session, driver_id: int) -> Order:
        """Haydovchining aktiv buyurtmasini olish"""
        return db.query(Order).filter(
            Order.driver_id == driver_id,
            Order.status == "accepted"
        ).first()
    
    @staticmethod
    def update_order_status(
        db: Session, 
        order_id: int, 
        status: str, 
        driver_id: int = None, 
        driver_name: str = None
    ):
        """Buyurtma statusini yangilash"""
        try:
            order = db.query(Order).filter(Order.order_id == order_id).first()
            if order:
                order.status = status
                
                if driver_id:
                    order.driver_id = driver_id
                if driver_name:
                    order.driver_name = driver_name
                
                if status == "accepted":
                    order.accepted_at = datetime.utcnow()
                elif status == "confirmed":
                    order.confirmed_at = datetime.utcnow()
                
                db.commit()
                logger.info(f"✅ Order #{order_id} status updated to: {status}")
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Error updating order status: {e}")
            raise
    
    @staticmethod
    def increment_reject_count(db: Session, order_id: int):
        """Buyurtma rad etilishlar sonini oshirish"""
        try:
            order = db.query(Order).filter(Order.order_id == order_id).first()
            if order:
                order.reject_count += 1
                db.commit()
                logger.info(f"✅ Order #{order_id} reject count: {order.reject_count}")
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Error incrementing reject count: {e}")
            raise
    
    @staticmethod
    def update_order_group_message(db: Session, order_id: int, message_id: int):
        """Buyurtmaning guruh xabar ID'sini saqlash"""
        try:
            order = db.query(Order).filter(Order.order_id == order_id).first()
            if order:
                order.group_message_id = message_id
                db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Error updating group message ID: {e}")
    
    # ===== COOLDOWN OPERATIONS =====
    
    @staticmethod
    def check_product_cooldown(db: Session, user_id: int, product_type: str) -> bool:
        """Non/Yem uchun 3 soatlik cheklovni tekshirish"""
        cooldown = db.query(ProductCooldown).filter(
            ProductCooldown.user_id == user_id,
            ProductCooldown.product_type == product_type
        ).first()
        
        if not cooldown:
            return False
        
        time_diff = datetime.utcnow() - cooldown.last_order_time
        if time_diff < timedelta(seconds=config.PRODUCT_COOLDOWN):
            return True
        
        return False
    
    @staticmethod
    def get_remaining_cooldown_time(db: Session, user_id: int, product_type: str) -> int:
        """Qolgan cheklov vaqtini (soniyalarda) olish"""
        cooldown = db.query(ProductCooldown).filter(
            ProductCooldown.user_id == user_id,
            ProductCooldown.product_type == product_type
        ).first()
        
        if not cooldown:
            return 0
        
        time_diff = datetime.utcnow() - cooldown.last_order_time
        remaining = config.PRODUCT_COOLDOWN - int(time_diff.total_seconds())
        
        return max(0, remaining)
    
    @staticmethod
    def set_product_cooldown(db: Session, user_id: int, product_type: str):
        """Non/Yem buyurtma berganidan keyin cooldown o'rnatish"""
        try:
            cooldown = db.query(ProductCooldown).filter(
                ProductCooldown.user_id == user_id,
                ProductCooldown.product_type == product_type
            ).first()
            
            if cooldown:
                cooldown.last_order_time = datetime.utcnow()
            else:
                cooldown = ProductCooldown(
                    user_id=user_id,
                    product_type=product_type,
                    last_order_time=datetime.utcnow()
                )
                db.add(cooldown)
            
            db.commit()
            logger.info(f"✅ Cooldown set for user {user_id} - {product_type}")
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Error setting cooldown: {e}")


# Global instance
db_manager = DatabaseManager()
