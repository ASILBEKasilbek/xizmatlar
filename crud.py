from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from database import User, Order, Statistics, CooldownTracker, AdminLog, SessionLocal
from config import config, ServiceType, OrderStatus, UserRole

def get_user_by_telegram_id(db: Session, telegram_id: int) -> Optional[User]:
    return db.query(User).filter(User.telegram_id == telegram_id).first()


def create_user(
    db: Session,
    telegram_id: int,
    first_name: str,
    last_name: Optional[str] = None,
    role: str = UserRole.PASSENGER,
    phone_number: Optional[str] = None
) -> User:
    user = User(
        telegram_id=telegram_id,
        first_name=first_name,
        last_name=last_name,
        phone_number=phone_number,
        role=role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, user_id: int, **kwargs) -> Optional[User]:
    user = db.query(User).filter(User.user_id == user_id).first()
    if user:
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
        user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(user)
    return user


def get_all_drivers(db: Session, active_only: bool = True) -> List[User]:
    query = db.query(User).filter(User.role == UserRole.DRIVER)
    if active_only:
        query = query.filter(User.is_active == True)
    return query.all()


def get_all_passengers(db: Session) -> List[User]:
    return db.query(User).filter(User.role == UserRole.PASSENGER).all()

def create_order(
    db: Session,
    user_id: int,
    service_type: str,
    phone_number: str,
    description: Optional[str] = None,
    location: Optional[str] = None,
) -> Order:
    order = Order(
        user_id=user_id,
        service_type=service_type,
        phone_number=phone_number,
        description=description,
        location=location,
        status=OrderStatus.WAITING
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


def get_order_by_id(db: Session, order_id: int) -> Optional[Order]:
    return db.query(Order).filter(Order.order_id == order_id).first()


def get_active_taxi_order_for_user(db: Session, user_id: int) -> Optional[Order]:
    return db.query(Order).filter(
        and_(
            Order.user_id == user_id,
            Order.service_type == ServiceType.TAXI,
            Order.status.in_([OrderStatus.WAITING, OrderStatus.ACCEPTED])
        )
    ).first()


def get_active_orders_by_driver(db: Session, driver_id: int) -> List[Order]:
    return db.query(Order).filter(
        and_(
            Order.driver_id == driver_id,
            Order.status.in_([OrderStatus.ACCEPTED, OrderStatus.CONFIRMED])
        )
    ).all()


def get_waiting_orders_by_service(db: Session, service_type: str) -> List[Order]:
    return db.query(Order).filter(
        and_(
            Order.service_type == service_type,
            Order.status == OrderStatus.WAITING
        )
    ).order_by(Order.created_at.desc()).all()


def accept_order(db: Session, order_id: int, driver_id: int, message_id: int, group_id: int) -> Optional[Order]:
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if order and order.status == OrderStatus.WAITING:
        order.driver_id = driver_id
        order.status = OrderStatus.ACCEPTED
        order.accepted_at = datetime.utcnow()
        order.message_id = message_id
        order.group_id = group_id
        db.commit()
        db.refresh(order)
    return order


def decline_order(db: Session, order_id: int) -> Optional[Order]:
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if order:
        order.declined_count = (order.declined_count or 0) + 1
        db.commit()
        db.refresh(order)
    return order


def confirm_order(db: Session, order_id: int) -> Optional[Order]:
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if order:
        order.status = OrderStatus.CONFIRMED
        order.confirmed_at = datetime.utcnow()
        
        if order.driver_id:
            driver = db.query(User).filter(User.user_id == order.driver_id).first()
            if driver:
                driver.confirmed_orders = (driver.confirmed_orders or 0) + 1
        
        if order.user_id:
            passenger = db.query(User).filter(User.user_id == order.user_id).first()
            if passenger:
                passenger.confirmed_orders = (passenger.confirmed_orders or 0) + 1
        
        db.commit()
        db.refresh(order)
    return order


def complete_order(db: Session, order_id: int) -> Optional[Order]:
    """Buyurtmani yakunlash"""
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if order:
        order.status = OrderStatus.COMPLETED
        order.completed_at = datetime.utcnow()
        db.commit()
        db.refresh(order)
    return order


def cancel_order(db: Session, order_id: int, reason: Optional[str] = None) -> Optional[Order]:
    """Buyurtmani bekor qilish"""
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if order:
        order.status = OrderStatus.CANCELLED
        order.description = f"{order.description or ''}\n[CANCELLED: {reason}]".strip()
        db.commit()
        db.refresh(order)
    return order


def get_orders_by_date(db: Session, date: datetime) -> List[Order]:
    start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1)
    
    return db.query(Order).filter(
        and_(
            Order.created_at >= start_of_day,
            Order.created_at < end_of_day
        )
    ).all()


def can_place_order(db: Session, user_id: int, service_type: str) -> tuple[bool, Optional[str]]:
    if service_type == ServiceType.TAXI:
        active_order = get_active_taxi_order_for_user(db, user_id)
        if active_order:
            return False, "Siz allaqachon faol taxi buyurtmaga egasiz! Avval uni bekor qiling."
    
    if service_type in [ServiceType.BREAD, ServiceType.FEED]:
        cooldown = db.query(CooldownTracker).filter(
            and_(
                CooldownTracker.user_id == user_id,
                CooldownTracker.service_type == service_type
            )
        ).first()
        
        if cooldown:
            time_elapsed = datetime.utcnow() - cooldown.last_order_at
            cooldown_duration = config.BREAD_COOLDOWN if service_type == ServiceType.BREAD else config.FEED_COOLDOWN
            
            if time_elapsed < timedelta(seconds=cooldown_duration):
                remaining_minutes = (cooldown_duration - time_elapsed.total_seconds()) / 60
                return False, f"Iltimos, {int(remaining_minutes)} daqiqadan keyin urinib ko'ring."
    
    return True, None


def set_cooldown(db: Session, user_id: int, service_type: str):
    cooldown = db.query(CooldownTracker).filter(
        and_(
            CooldownTracker.user_id == user_id,
            CooldownTracker.service_type == service_type
        )
    ).first()
    
    if cooldown:
        cooldown.last_order_at = datetime.utcnow()
    else:
        cooldown = CooldownTracker(
            user_id=user_id,
            service_type=service_type,
            last_order_at=datetime.utcnow()
        )
        db.add(cooldown)
    
    db.commit()

def get_daily_stats(db: Session, date: datetime) -> dict:
    orders = get_orders_by_date(db, date)
    
    total = len(orders)
    confirmed = len([o for o in orders if o.status == OrderStatus.CONFIRMED])
    cancelled = len([o for o in orders if o.status == OrderStatus.CANCELLED])
    taxi = len([o for o in orders if o.service_type == ServiceType.TAXI])
    bread = len([o for o in orders if o.service_type == ServiceType.BREAD])
    feed = len([o for o in orders if o.service_type == ServiceType.FEED])
    
    return {
        "date": date.strftime("%d.%m.%Y"),
        "total_orders": total,
        "confirmed_orders": confirmed,
        "cancelled_orders": cancelled,
        "taxi_orders": taxi,
        "bread_orders": bread,
        "feed_orders": feed,
    }


def create_daily_stats(db: Session, user_id: Optional[int], stat_data: dict):
    stats = Statistics(
        user_id=user_id,
        stat_date=datetime.utcnow(),
        **stat_data
    )
    db.add(stats)
    db.commit()


def log_admin_action(db: Session, admin_id: int, action: str, description: Optional[str] = None):
    log_entry = AdminLog(
        admin_id=admin_id,
        action=action,
        description=description
    )
    db.add(log_entry)
    db.commit()
