"""
Database Models va SQLAlchemy Setup
Barcha ma'lumotlar bazasi modellarini shu yerda aniqlanadi
"""

from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import (
    Column, String, Integer, DateTime, Boolean, Float, 
    ForeignKey, Enum, Index, create_engine, func
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import enum
from config import config, UserRole, ServiceType, OrderStatus

# Asosiy baza classi
Base = declarative_base()

# Database engine va session factory
engine = create_engine(
    config.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in config.DATABASE_URL else {},
    echo=False
)

SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


class User(Base):
    """Foydalanuvchi modeli"""
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True, nullable=False)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    phone_number = Column(String(20), nullable=True)
    role = Column(String(50), nullable=False, default=UserRole.PASSENGER)
    
    # Haydovchi uchun qo'shimcha ma'lumotlar
    car_number = Column(String(50), nullable=True)
    car_info = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Yo'lovchi uchun qo'shimcha ma'lumotlar
    residence_area = Column(String(255), nullable=True)
    
    # Reyting va statistika
    rating = Column(Float, default=5.0)
    total_orders = Column(Integer, default=0)
    confirmed_orders = Column(Integer, default=0)
    declined_orders = Column(Integer, default=0)
    
    # Ob'yektlar (relationships)
    orders = relationship("Order", foreign_keys="Order.user_id", back_populates="user")
    statistics = relationship("Statistics", back_populates="user")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index("idx_user_telegram_id_role", "telegram_id", "role"),
    )
    
    def __repr__(self):
        return f"<User(telegram_id={self.telegram_id}, role={self.role})>"


class Order(Base):
    """Buyurtma modeli"""
    __tablename__ = "orders"
    
    order_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    driver_id = Column(Integer, ForeignKey("users.user_id"), nullable=True)
    
    service_type = Column(String(50), nullable=False)  # taxi, bread, feed
    status = Column(String(50), default=OrderStatus.WAITING)
    
    # Buyurtma ma'lumotlari
    phone_number = Column(String(20), nullable=False)
    description = Column(String(1000), nullable=True)
    location = Column(String(255), nullable=True)
    
    # Haydovchi uchun ma'lumot
    driver_phone_shared = Column(Boolean, default=False)
    
    # Taymerlar uchun ma'lumotlar
    message_id = Column(Integer, nullable=True)  # Guruhdagi xabarning ID'si
    group_id = Column(Integer, nullable=True)
    declined_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    accepted_at = Column(DateTime, nullable=True)
    confirmed_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Ob'yektlar (relationships)
    user = relationship("User", foreign_keys=[user_id], back_populates="orders")
    driver = relationship("User", foreign_keys=[driver_id])
    
    # Indexes
    __table_args__ = (
        Index("idx_order_user_id_status", "user_id", "status"),
        Index("idx_order_driver_id_status", "driver_id", "status"),
        Index("idx_order_created_at", "created_at"),
    )
    
    def __repr__(self):
        return f"<Order(order_id={self.order_id}, service_type={self.service_type}, status={self.status})>"


class Statistics(Base):
    """Kunlik statistika modeli"""
    __tablename__ = "statistics"
    
    stat_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=True)
    stat_date = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Umumiy statistika
    total_orders = Column(Integer, default=0)
    completed_orders = Column(Integer, default=0)
    cancelled_orders = Column(Integer, default=0)
    declined_orders = Column(Integer, default=0)
    
    # Xizmat turi bo'yicha
    taxi_orders = Column(Integer, default=0)
    bread_orders = Column(Integer, default=0)
    feed_orders = Column(Integer, default=0)
    
    # Relationship
    user = relationship("User", back_populates="statistics")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index("idx_statistics_user_date", "user_id", "stat_date"),
    )
    
    def __repr__(self):
        return f"<Statistics(stat_date={self.stat_date})>"


class CooldownTracker(Base):
    """Cooldown (cheklov) tracker - spam oldini olish uchun"""
    __tablename__ = "cooldown_tracker"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, index=True)
    service_type = Column(String(50), nullable=False)
    last_order_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    __table_args__ = (
        Index("idx_cooldown_user_service", "user_id", "service_type"),
    )
    
    def __repr__(self):
        return f"<CooldownTracker(user_id={self.user_id}, service_type={self.service_type})>"


class AdminLog(Base):
    """Admin loglar"""
    __tablename__ = "admin_logs"
    
    log_id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, nullable=False)
    action = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f"<AdminLog(admin_id={self.admin_id}, action={self.action})>"


# Database bilan ishlash funksiyalari
def init_db():
    """Database tablalarini yaratish"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Database session berish"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
