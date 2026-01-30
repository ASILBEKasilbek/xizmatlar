from aiogram.types import (
    KeyboardButton, 
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



def request_location_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="📍 Lokatsiyani yuborish", request_location=True)
    )
    return builder.as_markup(resize_keyboard=True)


def services_keyboard():
    builder = ReplyKeyboardBuilder()

    builder.row(KeyboardButton(text="🚕 Taxi"))
    builder.row(KeyboardButton(text="🥖 Non mahsulotlariga buyurtma berish"))
    builder.row(KeyboardButton(text="🌾 Yem mahsulotlariga buyurtma berish"))

    # 👇 yonma-yon bo‘lsin
    builder.row(
        KeyboardButton(text="💬 Qo'llab-quvvatlash"),
        KeyboardButton(text="🔄 Qayta ro'yxatdan o'tish"),
    )

    return builder.as_markup(resize_keyboard=True)

def re_register_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🔄 Qayta ro'yxatdan o'tish", callback_data="re_register")
    )
    return builder.as_markup()



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
    builder.row(KeyboardButton(text="📊 Bugungi statistika"))
    builder.row(KeyboardButton(text="📅 Boshqa kun statistikasi"))
    builder.row(KeyboardButton(text="👥 Foydalanuvchilar"))
    builder.row(KeyboardButton(text="🔙 Orqaga"))
    return builder.as_markup(resize_keyboard=True)


def remove_keyboard():
    return ReplyKeyboardRemove()


def channels_list_keyboard(channels: list[tuple[str, str]]):
    builder = InlineKeyboardBuilder()
    for name, channel_id in channels:
        builder.row(InlineKeyboardButton(text=name, callback_data=f"ch:{channel_id}"))
    return builder.as_markup()


def users_list_keyboard(users, page: int, total_pages: int):
    builder = InlineKeyboardBuilder()

    for u in users:
        title = f"{u.fullname} ({'🚖' if u.user_type=='driver' else '🧍‍♂️'})"
        builder.row(
            InlineKeyboardButton(
                text=title,
                callback_data=f"admin_user:{u.user_id}"
            )
        )

    nav = []
    if page > 1:
        nav.append(InlineKeyboardButton(text="⬅️ Oldingi", callback_data=f"admin_users_page:{page-1}"))
    nav.append(InlineKeyboardButton(text=f"{page}/{total_pages}", callback_data="noop"))
    if page < total_pages:
        nav.append(InlineKeyboardButton(text="➡️ Keyingi", callback_data=f"admin_users_page:{page+1}"))

    builder.row(*nav)

    builder.row(InlineKeyboardButton(text="🔙 Admin panel", callback_data="admin_back"))

    return builder.as_markup()
