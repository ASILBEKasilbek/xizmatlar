"""
Database modellari - User, Order, ProductCooldown
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    """
    Foydalanuvchilar jadvali
    - Haydovchilar va yo'lovchilar
    - Bir foydalanuvchi faqat bitta rol tanlashi mumkin
    """
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, index=True)
    fullname = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)
    user_type = Column(String(20), nullable=False)  # driver yoki passenger
    
    # Faqat haydovchilar uchun
    car_model = Column(String(100), nullable=True)
    
    # Faqat yo'lovchilar uchun
    area = Column(String(100), nullable=True)
    latitude = Column(String(50), nullable=True)
    longitude = Column(String(50), nullable=True)
    
    telegram_name = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Order(Base):
    """
    Buyurtmalar jadvali
    - Taxi, Non, Yem buyurtmalari
    """
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
    """
    Non/Yem buyurtmalar uchun 3 soatlik cheklov jadvali
    """
    __tablename__ = "product_cooldown"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    product_type = Column(String(50), nullable=False)  # 🥖 Non yoki 🌾 Yem
    last_order_time = Column(DateTime, nullable=False)
