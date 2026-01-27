"""
Klaviatura funksiyalari - Barcha tugmalar
"""
from aiogram.types import (
    KeyboardButton, 
    InlineKeyboardButton,
    ReplyKeyboardRemove
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from config import config


# ===== KANALGA OBUNA KLAVIATURASI =====

def subscription_keyboard():
    """Kanalga obuna bo'lish klaviaturasi"""
    builder = InlineKeyboardBuilder()
    
    # Kanal linkini yaratish
    channel_link = config.CHANNEL_LINK or f"https://t.me/{config.CHANNEL_ID.replace('@', '')}"
    
    builder.row(
        InlineKeyboardButton(
            text="📢 Kanalga obuna bo'lish",
            url=channel_link
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="✅ Tasdiqlash", 
            callback_data="check_subscription"
        )
    )
    
    return builder.as_markup()


# ===== ROL TANLASH =====

def role_selection_keyboard():
    """Rol tanlash klaviaturasi - Haydovchi yoki Yo'lovchi"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="🚖 Haydovchi", callback_data="role_driver")
    )
    builder.row(
        InlineKeyboardButton(text="🧍‍♂️ Yo'lovchi", callback_data="role_passenger")
    )
    
    return builder.as_markup()


# ===== TELEFON SO'RASH =====

def request_phone_keyboard():
    """Telefon raqamini so'rash klaviaturasi"""
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="📱 Telefon raqamimni yuborish", request_contact=True)
    )
    return builder.as_markup(resize_keyboard=True)


# ===== HUDUD TANLASH =====

def area_selection_keyboard():
    """Hudud tanlash klaviaturasi (Yo'lovchilar uchun)"""
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="Yangiqo'rgon"))
    builder.row(KeyboardButton(text="Boybuta"))
    builder.row(KeyboardButton(text="Arpaqishloq"))
    builder.row(KeyboardButton(text="Boshqa"))
    return builder.as_markup(resize_keyboard=True)


# ===== LOKATSIYA SO'RASH =====

def request_location_keyboard():
    """Lokatsiya yuborishni so'rash klaviaturasi"""
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="📍 Lokatsiyani yuborish", request_location=True)
    )
    return builder.as_markup(resize_keyboard=True)


# ===== XIZMATLAR KLAVIATURASI (YO'LOVCHILAR) =====

def services_keyboard():
    """Xizmatlar klaviaturasi - Taxi, Non, Yem"""
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="🚕 Taxi"))
    builder.row(KeyboardButton(text="🥖 Non buyurtma berish"))
    builder.row(KeyboardButton(text="🌾 Yem buyurtma berish"))
    return builder.as_markup(resize_keyboard=True)


# ===== BUYURTMA QABUL QILISH (GURUHDA) =====

def accept_order_keyboard(order_id: int):
    """Buyurtmani qabul qilish tugmasi - Guruhda ko'rsatiladi"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="✅ Qabul qilish", 
            callback_data=f"accept_{order_id}"
        )
    )
    return builder.as_markup()


# ===== HAYDOVCHI TASDIQLASH/RAD ETISH =====

def driver_action_keyboard(order_id: int):
    """Haydovchi tasdiqlash/rad etish klaviaturasi"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="✅ Tasdiqlash", 
            callback_data=f"confirm_{order_id}"
        ),
        InlineKeyboardButton(
            text="❌ Rad etish", 
            callback_data=f"reject_{order_id}"
        )
    )
    return builder.as_markup()


# ===== ADMIN PANEL =====

def admin_keyboard():
    """Admin panel klaviaturasi"""
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="📊 Statistika"))
    builder.row(KeyboardButton(text="👥 Foydalanuvchilar"))
    builder.row(KeyboardButton(text="📨 Xabar yuborish"))
    return builder.as_markup(resize_keyboard=True)


# ===== KLAVIATURANI O'CHIRISH =====

def remove_keyboard():
    """Klaviaturani o'chirish"""
    return ReplyKeyboardRemove()
