"""
Klaviatura funksiyalari
"""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from config import config


def subscription_keyboard():
    """Kanalga obuna bo'lish klaviaturasi"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📢 Kanalga obuna bo'lish", url=f"https://t.me/{config.CHANNEL_ID.replace('@', '')}")
    )
    builder.row(
        InlineKeyboardButton(text="✅ Tasdiqlash", callback_data="check_subscription")
    )
    return builder.as_markup()


def role_selection_keyboard():
    """Rol tanlash klaviaturasi"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🚖 Haydovchi", callback_data="role_driver")
    )
    builder.row(
        InlineKeyboardButton(text="🧍‍♂️ Yo'lovchi", callback_data="role_passenger")
    )
    builder.row(
        InlineKeyboardButton(text="🆘 Qo'llab-quvvatlash", callback_data="role_support")
    )
    return builder.as_markup()


def request_phone_keyboard():
    """Telefon raqamini so'rash klaviaturasi"""
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="📱 Telefon raqamimni yuborish", request_contact=True)
    )
    return builder.as_markup(resize_keyboard=True)


def area_selection_keyboard():
    """Hudud tanlash klaviaturasi"""
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="Yangiqo'rgon"))
    builder.row(KeyboardButton(text="Boybuta"))
    builder.row(KeyboardButton(text="Arpaqishloq"))
    builder.row(KeyboardButton(text="Boshqa"))
    return builder.as_markup(resize_keyboard=True)


def services_keyboard():
    """Xizmatlar klaviaturasi"""
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="🚕 Taxi"))
    builder.row(KeyboardButton(text="🥖 Non buyurtma berish"))
    builder.row(KeyboardButton(text="🌾 Yem buyurtma berish"))
    builder.row(KeyboardButton(text="🆘 Qo'llab-quvvatlash"))
    return builder.as_markup(resize_keyboard=True)


def admin_keyboard():
    """Admin panel klaviaturasi"""
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="📊 Bugungi statistika"))
    builder.row(KeyboardButton(text="📅 Boshqa kun statistikasi"))
    builder.row(KeyboardButton(text="🔙 Asosiy menyu"))
    return builder.as_markup(resize_keyboard=True)


def accept_order_keyboard(order_id: int):
    """Buyurtmani qabul qilish klaviaturasi"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Qabul qilish", callback_data=f"accept_{order_id}")
    )
    return builder.as_markup()


def driver_action_keyboard(order_id: int):
    """Haydovchi tasdiqlash/rad etish klaviaturasi"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"confirm_{order_id}"),
        InlineKeyboardButton(text="❌ Rad etish", callback_data=f"reject_{order_id}")
    )
    return builder.as_markup()


def remove_keyboard():
    """Klaviaturani o'chirish"""
    from aiogram.types import ReplyKeyboardRemove
    return ReplyKeyboardRemove()
