
from aiogram.types import (
    ReplyKeyboardMarkup, 
    KeyboardButton, 
    InlineKeyboardMarkup, 
    InlineKeyboardButton,
    ReplyKeyboardRemove
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from config import config

def subscription_keyboard():
    builder = InlineKeyboardBuilder()
    
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


def role_selection_keyboard():
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="🚖 Haydovchi", callback_data="role_driver")
    )
    builder.row(
        InlineKeyboardButton(text="🧍‍♂️ Yo'lovchi", callback_data="role_passenger")
    )
    
    return builder.as_markup()



def request_phone_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="📱 Telefon raqamimni yuborish", request_contact=True)
    )
    return builder.as_markup(resize_keyboard=True)

def area_selection_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="Yangiqo'rgon"))
    builder.row(KeyboardButton(text="Boybuta"))
    builder.row(KeyboardButton(text="Arpaqishloq"))
    builder.row(KeyboardButton(text="Boshqa"))
    return builder.as_markup(resize_keyboard=True)



def services_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="🚕 Taxi"))
    builder.row(KeyboardButton(text="🥖 Non mahsulotlariga buyurtma berish"))
    builder.row(KeyboardButton(text="🌾 Yem mahsulotlariga buyurtma berish"))
    builder.row(KeyboardButton(text="💬 Qo'llab-quvvatlash"))
    return builder.as_markup(resize_keyboard=True)



def accept_order_keyboard(order_id: int):
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="✅ Qabul qilish", 
            callback_data=f"accept_{order_id}"
        )
    )
    return builder.as_markup()



def driver_action_keyboard(order_id: int):
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


def admin_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="📊 Statistika"))
    builder.row(KeyboardButton(text="👥 Foydalanuvchilar"))
    builder.row(KeyboardButton(text="📨 Xabar yuborish"))
    return builder.as_markup(resize_keyboard=True)

def remove_keyboard():
    return ReplyKeyboardRemove()


def channels_list_keyboard(channels):
    builder = InlineKeyboardBuilder()
    
    for channel in channels:
        channel_name = channel.channel_name or channel.channel_id
        builder.row(
            InlineKeyboardButton(
                text=f"❌ {channel_name}",
                callback_data=f"delete_channel_{channel.channel_id}"
            )
        )
    
    builder.row(
        InlineKeyboardButton(text="➕ Kanal qo'shish", callback_data="add_channel")
    )
    
    return builder.as_markup()
