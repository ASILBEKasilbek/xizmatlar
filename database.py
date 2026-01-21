"""
Database modellari va CRUD operatsiyalari
"""
import logging
from datetime import datetime, timedelta, date
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text, Date, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from config import config

logger = logging.getLogger(__name__)

# Database engine va session
engine = create_engine(
    config.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in config.DATABASE_URL else {},
    echo=False
)

SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
Base = declarative_base()


# ===== MODELS =====

class User(Base):
    """Foydalanuvchilar jadvali"""
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, index=True)
    fullname = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)
    user_type = Column(String(20), nullable=False)  # driver / passenger
    car_model = Column(String(100), nullable=True)  # faqat haydovchilar uchun
    area = Column(String(100), nullable=True)  # faqat yo'lovchilar uchun
    telegram_name = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Order(Base):
    """Buyurtmalar jadvali"""
    __tablename__ = "orders"
    
    order_id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Yo'lovchi ma'lumotlari
    passenger_id = Column(Integer, nullable=False)
    passenger_name = Column(String(100), nullable=False)
    passenger_phone = Column(String(20), nullable=False)
    passenger_area = Column(String(100), nullable=True)
    
    # Buyurtma ma'lumotlari
    service_type = Column(String(50), nullable=False)  # 🚕 Taxi, 🥖 Non, 🌾 Yem
    group_chat = Column(Integer, nullable=False)  # GROUP3 yoki boshqa
    
    # Haydovchi ma'lumotlari
    driver_id = Column(Integer, nullable=True)
    driver_name = Column(String(100), nullable=True)
    
    # Status va hisoblagichlar
    status = Column(String(20), default="waiting")  # waiting, accepted, confirmed, cancelled
    reject_count = Column(Integer, default=0)
    
    # Guruh xabari
    group_message_id = Column(Integer, nullable=True)
    
    # Vaqtlar
    created_at = Column(DateTime, default=datetime.utcnow)
    accepted_at = Column(DateTime, nullable=True)
    confirmed_at = Column(DateTime, nullable=True)
    group_message_sent_at = Column(DateTime, nullable=True)


class ProductCooldown(Base):
    """Non/Yem buyurtmalar cooldown jadvali"""
    __tablename__ = "product_cooldown"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    product_type = Column(String(50), nullable=False)  # 🥖 Non, 🌾 Yem
    last_order_time = Column(DateTime, nullable=False)


class DailyStats(Base):
    """Kunlik statistika jadvali"""
    __tablename__ = "daily_stats"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    user_name = Column(String(100), nullable=False)
    user_type = Column(String(20), nullable=False)  # driver / passenger
    orders_count = Column(Integer, default=0)
    confirmed_count = Column(Integer, default=0)
    rejected_count = Column(Integer, default=0)
    
    __table_args__ = (UniqueConstraint('date', 'user_id', name='_date_user_uc'),)


# ===== DATABASE INIT =====

def init_db():
    """Database jadvallarini yaratish"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise


def get_db() -> Session:
    """Database session olish"""
    db = SessionLocal()
    try:
        return db
    except Exception:
        db.close()
        raise


# ===== CRUD FUNCTIONS =====

class DatabaseManager:
    """Database CRUD operatsiyalari"""
    
    @staticmethod
    def get_user(db: Session, user_id: int) -> User:
        """Foydalanuvchini olish"""
        return db.query(User).filter(User.user_id == user_id).first()
    
    @staticmethod
    def create_user(db: Session, user_id: int, fullname: str, phone: str, 
                   user_type: str, car_model: str = None, area: str = None, 
                   telegram_name: str = None) -> User:
        """Yangi foydalanuvchi yaratish"""
        try:
            user = User(
                user_id=user_id,
                fullname=fullname,
                phone=phone,
                user_type=user_type,
                car_model=car_model,
                area=area,
                telegram_name=telegram_name
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.info(f"User created: {user_id} - {fullname} ({user_type})")
            return user
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating user: {e}")
            raise
    
    @staticmethod
    def create_order(db: Session, passenger_id: int, passenger_name: str, 
                    passenger_phone: str, passenger_area: str, service_type: str, 
                    group_chat: int) -> Order:
        """Yangi buyurtma yaratish"""
        try:
            order = Order(
                passenger_id=passenger_id,
                passenger_name=passenger_name,
                passenger_phone=passenger_phone,
                passenger_area=passenger_area,
                service_type=service_type,
                group_chat=group_chat,
                status="waiting",
                group_message_sent_at=datetime.utcnow()
            )
            db.add(order)
            db.commit()
            db.refresh(order)
            logger.info(f"Order created: {order.order_id} - {service_type} by {passenger_name}")
            return order
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating order: {e}")
            raise
    
    @staticmethod
    def get_order(db: Session, order_id: int) -> Order:
        """Buyurtmani olish"""
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
    def update_order_status(db: Session, order_id: int, status: str, 
                           driver_id: int = None, driver_name: str = None) -> Order:
        """Buyurtma statusini yangilash"""
        try:
            order = db.query(Order).filter(Order.order_id == order_id).first()
            if not order:
                return None
            
            order.status = status
            if driver_id:
                order.driver_id = driver_id
                order.driver_name = driver_name
            
            if status == "accepted":
                order.accepted_at = datetime.utcnow()
            elif status == "confirmed":
                order.confirmed_at = datetime.utcnow()
            
            db.commit()
            db.refresh(order)
            logger.info(f"Order {order_id} status updated to: {status}")
            return order
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating order status: {e}")
            raise
    
    @staticmethod
    def increment_reject_count(db: Session, order_id: int) -> Order:
        """Rad etish sonini oshirish"""
        try:
            order = db.query(Order).filter(Order.order_id == order_id).first()
            if order:
                order.reject_count += 1
                db.commit()
                db.refresh(order)
                logger.info(f"Order {order_id} reject count: {order.reject_count}")
            return order
        except Exception as e:
            db.rollback()
            logger.error(f"Error incrementing reject count: {e}")
            raise
    
    @staticmethod
    def reset_order_for_repost(db: Session, order_id: int) -> Order:
        """Buyurtmani qayta yuborish uchun reset qilish"""
        try:
            order = db.query(Order).filter(Order.order_id == order_id).first()
            if order:
                order.status = "waiting"
                order.driver_id = None
                order.driver_name = None
                order.accepted_at = None
                order.group_message_sent_at = datetime.utcnow()
                order.group_message_id = None
                db.commit()
                db.refresh(order)
                logger.info(f"Order {order_id} reset for repost")
            return order
        except Exception as e:
            db.rollback()
            logger.error(f"Error resetting order: {e}")
            raise
    
    @staticmethod
    def set_group_message_id(db: Session, order_id: int, message_id: int) -> Order:
        """Guruh xabar ID'sini saqlash"""
        try:
            order = db.query(Order).filter(Order.order_id == order_id).first()
            if order:
                order.group_message_id = message_id
                db.commit()
                db.refresh(order)
            return order
        except Exception as e:
            db.rollback()
            logger.error(f"Error setting group message ID: {e}")
            raise
    
    @staticmethod
    def check_product_cooldown(db: Session, user_id: int, product_type: str) -> bool:
        """Non/Yem cooldown tekshirish (True - cooldownda, False - buyurtma bersa bo'ladi)"""
        cooldown_limit = datetime.utcnow() - timedelta(seconds=config.PRODUCT_COOLDOWN)
        cooldown = db.query(ProductCooldown).filter(
            ProductCooldown.user_id == user_id,
            ProductCooldown.product_type == product_type,
            ProductCooldown.last_order_time > cooldown_limit
        ).first()
        return cooldown is not None
    
    @staticmethod
    def add_product_cooldown(db: Session, user_id: int, product_type: str):
        """Non/Yem cooldown qo'shish"""
        try:
            cooldown = ProductCooldown(
                user_id=user_id,
                product_type=product_type,
                last_order_time=datetime.utcnow()
            )
            db.add(cooldown)
            db.commit()
            logger.info(f"Cooldown added: {user_id} - {product_type}")
        except Exception as e:
            db.rollback()
            logger.error(f"Error adding cooldown: {e}")
            raise
    
    @staticmethod
    def get_or_create_daily_stats(db: Session, user_id: int, user_name: str, 
                                  user_type: str, target_date: date = None) -> DailyStats:
        """Kunlik statistikani olish yoki yaratish"""
        if target_date is None:
            target_date = date.today()
        
        try:
            stats = db.query(DailyStats).filter(
                DailyStats.date == target_date,
                DailyStats.user_id == user_id
            ).first()
            
            if not stats:
                stats = DailyStats(
                    date=target_date,
                    user_id=user_id,
                    user_name=user_name,
                    user_type=user_type
                )
                db.add(stats)
                db.commit()
                db.refresh(stats)
                logger.info(f"Daily stats created: {target_date} - {user_id}")
            
            return stats
        except Exception as e:
            db.rollback()
            logger.error(f"Error getting or creating daily stats: {e}")
            raise
    
    @staticmethod
    def increment_orders_count(db: Session, user_id: int, user_name: str, user_type: str):
        """Buyurtmalar sonini oshirish"""
        try:
            stats = DatabaseManager.get_or_create_daily_stats(db, user_id, user_name, user_type)
            stats.orders_count += 1
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"Error incrementing orders count: {e}")
    
    @staticmethod
    def increment_confirmed_count(db: Session, user_id: int, user_name: str, user_type: str):
        """Tasdiqlangan buyurtmalar sonini oshirish"""
        try:
            stats = DatabaseManager.get_or_create_daily_stats(db, user_id, user_name, user_type)
            stats.confirmed_count += 1
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"Error incrementing confirmed count: {e}")
    
    @staticmethod
    def increment_rejected_count(db: Session, user_id: int, user_name: str, user_type: str):
        """Rad etilgan buyurtmalar sonini oshirish"""
        try:
            stats = DatabaseManager.get_or_create_daily_stats(db, user_id, user_name, user_type)
            stats.rejected_count += 1
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"Error incrementing rejected count: {e}")
    
    @staticmethod
    def get_daily_stats(db: Session, target_date: date = None):
        """Kunlik statistikani olish"""
        if target_date is None:
            target_date = date.today()
        
        return db.query(DailyStats).filter(DailyStats.date == target_date).all()
    
    @staticmethod
    def get_waiting_orders_timeout(db: Session):
        """7 daqiqadan oshgan waiting orderlarni olish"""
        timeout_time = datetime.utcnow() - timedelta(seconds=config.GROUP_TIMEOUT)
        return db.query(Order).filter(
            Order.status == "waiting",
            Order.group_message_sent_at < timeout_time,
            Order.group_message_id.isnot(None)
        ).all()
    
    @staticmethod
    def get_accepted_orders_timeout(db: Session):
        """6 daqiqadan oshgan accepted orderlarni olish"""
        timeout_time = datetime.utcnow() - timedelta(seconds=config.ACCEPTED_TIMEOUT)
        return db.query(Order).filter(
            Order.status == "accepted",
            Order.accepted_at < timeout_time
        ).all()
    
    @staticmethod
    def cleanup_old_data(db: Session):
        """Eski ma'lumotlarni tozalash"""
        try:
            # 30 kundan eski cooldownlarni o'chirish
            cooldown_limit = datetime.utcnow() - timedelta(days=30)
            db.query(ProductCooldown).filter(
                ProductCooldown.last_order_time < cooldown_limit
            ).delete()
            
            # 90 kundan eski completed/cancelled orderlarni o'chirish
            order_limit = datetime.utcnow() - timedelta(days=90)
            db.query(Order).filter(
                Order.status.in_(["confirmed", "cancelled"]),
                Order.created_at < order_limit
            ).delete()
            
            # 90 kundan eski statslarni o'chirish
            stats_limit = date.today() - timedelta(days=90)
            db.query(DailyStats).filter(
                DailyStats.date < stats_limit
            ).delete()
            
            db.commit()
            logger.info("Old data cleaned up successfully")
        except Exception as e:
            db.rollback()
            logger.error(f"Error cleaning up old data: {e}")


db_manager = DatabaseManager()
