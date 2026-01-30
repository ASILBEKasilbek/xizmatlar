
import logging
from datetime import datetime, timedelta, date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from config import config
from .models import Base, User, Order, ProductCooldown, DailyStats
from sqlalchemy import create_engine, func

logger = logging.getLogger(__name__)

engine = create_engine(
    config.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in config.DATABASE_URL else {},
    echo=False
)

SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def init_db():
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Error initializing database: {e}")
        raise


def get_db() -> Session:
    return SessionLocal()


class DatabaseManager:
    @staticmethod
    def get_user(db: Session, user_id: int) -> User:
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
    def delete_user(db: Session, user_id: int) -> bool:
        try:
            user = db.query(User).filter(User.user_id == user_id).first()
            if not user:
                return False

            db.delete(user)
            db.commit()
            logger.info(f"✅ User deleted: {user_id}")
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Error deleting user: {e}")
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

    @staticmethod
    def check_product_cooldown(db: Session, user_id: int, product_type: str) -> bool:
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
   
    @staticmethod
    def get_daily_stats(db: Session, target_date: date = None):
        if target_date is None:
            target_date = date.today()
        
        return db.query(DailyStats).filter(
            DailyStats.date >= datetime.combine(target_date, datetime.min.time()),
            DailyStats.date < datetime.combine(target_date + timedelta(days=1), datetime.min.time())
        ).all()
    
    @staticmethod
    def update_stats_order_created(db: Session, user_id: int, user_name: str):
        try:
            today = date.today()
            
            stats = db.query(DailyStats).filter(
                DailyStats.date >= datetime.combine(today, datetime.min.time()),
                DailyStats.date < datetime.combine(today + timedelta(days=1), datetime.min.time()),
                DailyStats.user_id == user_id,
                DailyStats.user_type == "passenger"
            ).first()
            
            if stats:
                stats.orders_count += 1
            else:
                stats = DailyStats(
                    date=datetime.utcnow(),
                    user_id=user_id,
                    user_name=user_name,
                    user_type="passenger",
                    orders_count=1,
                    confirmed_count=0,
                    rejected_count=0
                )
                db.add(stats)
            
            db.commit()
            logger.info(f"✅ Stats updated: order created by {user_id}")
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Error updating stats: {e}")
    
    @staticmethod
    def update_stats_order_confirmed(db: Session, driver_id: int, driver_name: str):
        try:
            today = date.today()
            
            stats = db.query(DailyStats).filter(
                DailyStats.date >= datetime.combine(today, datetime.min.time()),
                DailyStats.date < datetime.combine(today + timedelta(days=1), datetime.min.time()),
                DailyStats.user_id == driver_id,
                DailyStats.user_type == "driver"
            ).first()
            
            if stats:
                stats.confirmed_count += 1
            else:
                stats = DailyStats(
                    date=datetime.utcnow(),
                    user_id=driver_id,
                    user_name=driver_name,
                    user_type="driver",
                    orders_count=0,
                    confirmed_count=1,
                    rejected_count=0
                )
                db.add(stats)
            
            db.commit()
            logger.info(f"✅ Stats updated: order confirmed by {driver_id}")
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Error updating stats: {e}")
    
    @staticmethod
    def update_stats_order_rejected(db: Session, driver_id: int, driver_name: str):
        try:
            today = date.today()
            
            stats = db.query(DailyStats).filter(
                DailyStats.date >= datetime.combine(today, datetime.min.time()),
                DailyStats.date < datetime.combine(today + timedelta(days=1), datetime.min.time()),
                DailyStats.user_id == driver_id,
                DailyStats.user_type == "driver"
            ).first()
            
            if stats:
                stats.rejected_count += 1
            else:
                stats = DailyStats(
                    date=datetime.utcnow(),
                    user_id=driver_id,
                    user_name=driver_name,
                    user_type="driver",
                    orders_count=0,
                    confirmed_count=0,
                    rejected_count=1
                )
                db.add(stats)
            
            db.commit()
            logger.info(f"✅ Stats updated: order rejected by {driver_id}")
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Error updating stats: {e}")
    @staticmethod
    def get_users_page(db: Session, page: int = 1, limit: int = 10):
        """Userlarni pagination bilan olish"""
        if page < 1:
            page = 1
        offset = (page - 1) * limit

        total = db.query(func.count(User.user_id)).scalar() or 0
        users = (
            db.query(User)
            .order_by(User.user_id.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        total_pages = (total + limit - 1) // limit if total else 1
        return users, total, total_pages

    @staticmethod
    def get_user_total_stats(db: Session, user_id: int):
        res = (
            db.query(
                func.coalesce(func.sum(DailyStats.orders_count), 0),
                func.coalesce(func.sum(DailyStats.confirmed_count), 0),
                func.coalesce(func.sum(DailyStats.rejected_count), 0),
            )
            .filter(DailyStats.user_id == user_id)
            .first()
        )

        orders, confirmed, rejected = res if res else (0, 0, 0)
        return int(orders), int(confirmed), int(rejected)

    @staticmethod
    def set_user_ban(db: Session, user_id: int, banned: bool) -> bool:
        try:
            user = db.query(User).filter(User.user_id == user_id).first()
            if not user:
                return False
            user.is_banned = banned
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            raise

    @staticmethod
    def is_user_banned(db: Session, user_id: int) -> bool:
        user = db.query(User).filter(User.user_id == user_id).first()
        return bool(user and getattr(user, "is_banned", False))
db_manager = DatabaseManager()
