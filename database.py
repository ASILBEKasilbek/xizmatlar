import logging
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from config import config

logger = logging.getLogger(__name__)

# Database yaratish
engine = create_engine(
    config.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in config.DATABASE_URL else {},
    echo=False
)

SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, index=True)
    fullname = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)
    user_type = Column(String(20), nullable=False) 
    car_model = Column(String(100), nullable=True)
    area = Column(String(100), nullable=True)
    
    telegram_name = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Order(Base):
    __tablename__ = "orders"
    
    order_id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Yo'lovchi ma'lumotlari
    passenger_id = Column(Integer, nullable=False, index=True)
    passenger_name = Column(String(100), nullable=False)
    passenger_phone = Column(String(20), nullable=False)
    passenger_area = Column(String(100), nullable=True)
    
    # Buyurtma turi va guruhi
    service_type = Column(String(50), nullable=False)  # 🚕 Taxi, 🥖 Non, 🌾 Yem
    group_chat = Column(String(100), nullable=False)   # Qaysi guruhga yuborilgan
    
    # Haydovchi ma'lumotlari (faqat taxi uchun)
    driver_id = Column(Integer, nullable=True, index=True)
    driver_name = Column(String(100), nullable=True)
    
    # Status
    status = Column(String(20), default="waiting")  # waiting, accepted, confirmed, cancelled
    reject_count = Column(Integer, default=0)       # Necha marta rad etilgan
    
    # Guruh xabar ID'si (o'chirish uchun)
    group_message_id = Column(Integer, nullable=True)
    
    # Vaqtlar
    created_at = Column(DateTime, default=datetime.utcnow)
    accepted_at = Column(DateTime, nullable=True)
    confirmed_at = Column(DateTime, nullable=True)


class ProductCooldown(Base):
    __tablename__ = "product_cooldown"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    product_type = Column(String(50), nullable=False)  # 🥖 Non yoki 🌾 Yem
    last_order_time = Column(DateTime, nullable=False)


def init_db():
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Error initializing database: {e}")
        raise


def get_db() -> Session:
    return SessionLocal()


# ===== DATABASE MANAGER =====

class DatabaseManager:
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
        telegram_name: str = None
    ) -> User:
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
            logger.info(f"✅ User created: {user_id} - {fullname} ({user_type})")
            return user
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Error creating user: {e}")
            raise
    
    @staticmethod
    def get_all_drivers(db: Session):
        return db.query(User).filter(User.user_type == "driver").all()
    
    @staticmethod
    def get_all_passengers(db: Session):
        return db.query(User).filter(User.user_type == "passenger").all()


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
        return db.query(Order).filter(Order.order_id == order_id).first()
    
    @staticmethod
    def get_active_taxi_order(db: Session, passenger_id: int) -> Order:
        return db.query(Order).filter(
            Order.passenger_id == passenger_id,
            Order.service_type == "🚕 Taxi",
            Order.status.in_(["waiting", "accepted"])
        ).first()
    
    @staticmethod
    def get_driver_active_order(db: Session, driver_id: int) -> Order:
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
        cooldown = db.query(ProductCooldown).filter(
            ProductCooldown.user_id == user_id,
            ProductCooldown.product_type == product_type
        ).first()
        
        if not cooldown:
            return False  # Hech qachon buyurtma bermagan
        
        # 3 soat o'tganmi?
        time_diff = datetime.utcnow() - cooldown.last_order_time
        if time_diff < timedelta(seconds=config.PRODUCT_COOLDOWN):
            return True  # Cheklov hali mavjud
        
        return False  # Cheklov o'tgan
    
    @staticmethod
    def get_remaining_cooldown_time(db: Session, user_id: int, product_type: str) -> int:
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


db_manager = DatabaseManager()
