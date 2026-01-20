"""
Keyboard va Button helpers
Barcha klaviaturalar va tugmalarni shu yerda belgilash
"""

from aiogram.types import (
    InlineKeyboardButton, InlineKeyboardMarkup,
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
)
from config import ServiceType


# ==================== ROLE SELECTION ====================

def get_role_keyboard() -> InlineKeyboardMarkup:
    """Rol tanlash klaviaturasi"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚖 Haydovchi", callback_data="role_driver")],
        [InlineKeyboardButton(text="🧍 Yo'lovchi", callback_data="role_passenger")],
        [InlineKeyboardButton(text="🆘 Qo'llab-quvvatlash", callback_data="role_support")],
    ])


# ==================== SERVICE SELECTION ====================

def get_service_keyboard() -> InlineKeyboardMarkup:
    """Xizmat tanlash klaviaturasi"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚕 Taxi", callback_data="service_taxi")],
        [InlineKeyboardButton(text="🥖 Non", callback_data="service_bread")],
        [InlineKeyboardButton(text="🌾 Yem", callback_data="service_feed")],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_menu")],
    ])


# ==================== ORDER CONFIRMATION ====================

def get_order_confirmation_keyboard(order_id: int) -> InlineKeyboardMarkup:
    """Buyurtma tasdiqlash klaviaturasi"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"confirm_order_{order_id}"),
            InlineKeyboardButton(text="❌ Rad etish", callback_data=f"decline_order_{order_id}"),
        ]
    ])


def get_taxi_order_confirmation_keyboard(order_id: int) -> InlineKeyboardMarkup:
    """Taxi buyurtma aksepptash uchun klaviaturasi (haydovchi uchun)"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Qabul qilish", callback_data=f"accept_taxi_{order_id}")],
        [InlineKeyboardButton(text="❌ Rad etish", callback_data=f"decline_taxi_{order_id}")],
    ])


def get_driver_confirm_keyboard(order_id: int) -> InlineKeyboardMarkup:
    """Haydovchi taxini tasdiqlash uchun klaviaturasi"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"driver_confirm_{order_id}")],
        [InlineKeyboardButton(text="❌ Rad etish", callback_data=f"driver_decline_{order_id}")],
    ])


# ==================== CONTACT SHARING ====================

def get_phone_request_keyboard() -> ReplyKeyboardMarkup:
    """Telefon raqam so'rash uchun klaviaturasi"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📞 Telefon raqamni yuborish", request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )


def get_remove_keyboard() -> ReplyKeyboardRemove:
    """Klaviaturani o'chirish"""
    return ReplyKeyboardRemove()


# ==================== ADMIN MENU ====================

def get_admin_menu_keyboard() -> InlineKeyboardMarkup:
    """Admin menyu klaviaturasi"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Bugungi statistika", callback_data="admin_today_stats")],
        [InlineKeyboardButton(text="📅 O'tgan kuning statistikasi", callback_data="admin_date_stats")],
        [InlineKeyboardButton(text="👥 Foydalanuvchiler haqida", callback_data="admin_users_info")],
        [InlineKeyboardButton(text="📋 Aktiv buyurtmalar", callback_data="admin_active_orders")],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_menu")],
    ])


# ==================== PASSENGER MENU ====================

def get_passenger_menu_keyboard() -> InlineKeyboardMarkup:
    """Yo'lovchi menyu klaviaturasi"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🆕 Xizmat tanlash", callback_data="select_service")],
        [InlineKeyboardButton(text="📋 Mening buyurtmalarim", callback_data="my_orders")],
        [InlineKeyboardButton(text="⚙️ Sozlamalar", callback_data="settings")],
        [InlineKeyboardButton(text="❓ Ko'llab-quvvatlash", callback_data="support")],
    ])


# ==================== DRIVER MENU ====================

def get_driver_menu_keyboard() -> InlineKeyboardMarkup:
    """Haydovchi menyu klaviaturasi"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Mening buyurtmalarim", callback_data="my_orders")],
        [InlineKeyboardButton(text="📊 Mening statistikam", callback_data="my_stats")],
        [InlineKeyboardButton(text="⚙️ Sozlamalar", callback_data="settings")],
        [InlineKeyboardButton(text="❓ Ko'llab-quvvatlash", callback_data="support")],
    ])


# ==================== BACK BUTTON ====================

def get_back_button() -> InlineKeyboardMarkup:
    """Orqaga qaytish tugmasi"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_menu")]
    ])


# ==================== PAGINATION ====================

def get_pagination_keyboard(
    current_page: int,
    total_pages: int,
    callback_prefix: str
) -> InlineKeyboardMarkup:
    """Pagination klaviaturasi"""
    buttons = []
    
    # Orqaga tugmasi
    if current_page > 1:
        buttons.append(
            InlineKeyboardButton(
                text="⬅️ Oldingi",
                callback_data=f"{callback_prefix}_{current_page - 1}"
            )
        )
    
    # Sahifa raqami
    buttons.append(
        InlineKeyboardButton(
            text=f"{current_page}/{total_pages}",
            callback_data="noop"
        )
    )
    
    # Oldinga tugmasi
    if current_page < total_pages:
        buttons.append(
            InlineKeyboardButton(
                text="Keyingi ➡️",
                callback_data=f"{callback_prefix}_{current_page + 1}"
            )
        )
    
    return InlineKeyboardMarkup(inline_keyboard=[buttons])


# ==================== CANCEL BUTTON ====================

def get_cancel_button() -> InlineKeyboardMarkup:
    """Bekor qilish tugmasi"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_action")]
    ])


# ==================== YES/NO BUTTONS ====================

def get_yes_no_keyboard(yes_callback: str, no_callback: str) -> InlineKeyboardMarkup:
    """Ha/Yo'q tugmalari"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Ha", callback_data=yes_callback),
            InlineKeyboardButton(text="❌ Yo'q", callback_data=no_callback),
        ]
    ])


# ==================== TEXT HELPERS ====================

def format_order_message(order_data: dict, show_phone: bool = False) -> str:
    """Buyurtma xabarini formatida berish"""
    message = f"""
📋 <b>Buyurtma #{order_data.get('order_id', 'N/A')}</b>

<b>Xizmat turi:</b> {order_data.get('service_type', 'N/A')}
<b>Holati:</b> {order_data.get('status', 'N/A')}
<b>Tavsif:</b> {order_data.get('description', 'No description')}

<b>Vaqti:</b> {order_data.get('created_at', 'N/A')}
    """
    
    if show_phone:
        message += f"\n<b>📞 Telefon:</b> <code>{order_data.get('phone_number', 'N/A')}</code>"
    
    return message.strip()


def format_user_profile(user_data: dict) -> str:
    """Foydalanuvchi profili formatida berish"""
    return f"""
👤 <b>{user_data.get('first_name', 'N/A')} {user_data.get('last_name', '')}</b>

<b>Rol:</b> {user_data.get('role', 'N/A')}
<b>📞 Telefon:</b> {user_data.get('phone_number', 'N/A')}
<b>Rating:</b> ⭐ {user_data.get('rating', 'N/A')}
<b>Jami buyurtmalar:</b> {user_data.get('total_orders', 0)}
<b>Tasdiqlangan:</b> {user_data.get('confirmed_orders', 0)}
<b>Rad etilgan:</b> {user_data.get('declined_orders', 0)}
    """.strip()


def format_statistics(stats: dict) -> str:
    """Statistikani formatida berish"""
    return f"""
📊 <b>Statistika - {stats.get('date', 'N/A')}</b>

<b>Jami buyurtmalar:</b> {stats.get('total_orders', 0)}
<b>Tasdiqlangan:</b> {stats.get('confirmed_orders', 0)}
<b>Bekor qilingan:</b> {stats.get('cancelled_orders', 0)}

<b>Xizmat turi bo'yicha:</b>
🚕 Taxi: {stats.get('taxi_orders', 0)}
🥖 Non: {stats.get('bread_orders', 0)}
🌾 Yem: {stats.get('feed_orders', 0)}
    """.strip()
