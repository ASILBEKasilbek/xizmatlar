from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Boolean

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, index=True)
    fullname = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)
    user_type = Column(String(20), nullable=False)  

    car_model = Column(String(100), nullable=True)
    
    area = Column(String(100), nullable=True)
    latitude = Column(String(50), nullable=True)
    longitude = Column(String(50), nullable=True)
    
    telegram_name = Column(String(100), nullable=True)
    is_banned = Column(Boolean, default=False, nullable=False)  # 🔴 NEW

    created_at = Column(DateTime, default=datetime.utcnow)


class Order(Base):
    __tablename__ = "orders"
    
    order_id = Column(Integer, primary_key=True, autoincrement=True)
    
    passenger_id = Column(Integer, nullable=False, index=True)
    passenger_name = Column(String(100), nullable=False)
    passenger_phone = Column(String(20), nullable=False)
    passenger_area = Column(String(100), nullable=True)
    
    service_type = Column(String(50), nullable=False) 
    group_chat = Column(String(100), nullable=False)   
    
    driver_id = Column(Integer, nullable=True, index=True)
    driver_name = Column(String(100), nullable=True)
    
    status = Column(String(20), default="waiting")  
    reject_count = Column(Integer, default=0)       
    group_message_id = Column(Integer, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    accepted_at = Column(DateTime, nullable=True)
    confirmed_at = Column(DateTime, nullable=True)


class ProductCooldown(Base):
    __tablename__ = "product_cooldown"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    product_type = Column(String(50), nullable=False)  
    last_order_time = Column(DateTime, nullable=False)


class DailyStats(Base):
    __tablename__ = "daily_stats"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime, nullable=False, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    user_name = Column(String(100), nullable=False)
    user_type = Column(String(20), nullable=False)  
    
    orders_count = Column(Integer, default=0)     
    confirmed_count = Column(Integer, default=0) 
    rejected_count = Column(Integer, default=0)    
