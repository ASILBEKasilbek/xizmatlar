# Xizmatlar Bot 🤖

Professional darajadagi **Telegram Bot** - Mahalliy xizmatlar uchun buyurtma va vositachilik tizimi.

## ✨ Xususiyatlari

### 🎯 Asosiy Funksiyalari
- **🚕 Taxi** - Haraka qilish uchun buyurtma berish
- **🥖 Non** - Non buyurtma qilish  
- **🌾 Yem** - Yem buyurtma qilish

### 👥 Ishtirokchilar (Rollar)
1. **Yo'lovchi** - Xizmat buyurtish
2. **Haydovchi** - Buyurtmalarni qabul qilish va bajarish
3. **Admin** - Statistika va nazorat

### ⚙️ Texnik Xususiyatlari
- ✅ Aiogram 3.x (eng yangi versiya)
- ✅ SQLAlchemy ORM
- ✅ PostgreSQL/SQLite support
- ✅ APScheduler (avtomatik timerlar)
- ✅ State Management (FSM)
- ✅ Middleware architecture
- ✅ Admin panel statistika
- ✅ Avtomatik bekor qilish tizimi

## 📋 Loyiha Strukturasi

```
xizmatlar/
├── main.py                    # Bot entry point
├── config.py                  # Konfiguratsiya
├── database.py               # SQLAlchemy models
├── crud.py                   # Database operatsiyalari
├── states.py                 # FSM states va middlewares
├── keyboards.py              # Button va klaviaturalar
├── scheduler.py              # APScheduler integration
├── utils.py                  # Helper funksiyalari
├── handlers/
│   ├── __init__.py
│   ├── start.py             # /start va rol tanlash
│   ├── driver_registration.py  # Haydovchi ro'yxatdan o'tish
│   ├── passenger_registration.py # Yo'lovchi ro'yxatdan o'tish
│   ├── orders.py            # Buyurtma management
│   └── admin.py             # Admin paneli
├── requirements.txt         # Dependencies
├── .env.example             # Environment variables
└── README.md               # This file
```

## 🚀 O'rnatish

### 1. Talablar
- Python 3.10+
- pip yoki poetry

### 2. Kutubxonalarni o'rnatish

```bash
# Virtual environment yaratish
python -m venv venv

# Activate
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate      # Windows

# Dependencies o'rnatish
pip install -r requirements.txt
```

### 3. Konfiguratsiyani o'rnatish

```bash
# .env.example-ni .env-ga nusxa olish
cp .env.example .env

# .env faylini o'zingiz rahbarida to'ldirish
nano .env  # yoki o'z editoringizda
```

**Kerakli sozlamalar:**
```env
BOT_TOKEN=YOUR_BOT_TOKEN_HERE
ADMIN_IDS=YOUR_ID_HERE
CHANNEL_ID=-1001234567890
DRIVERS_GROUP_ID=-1001234567891
PASSENGERS_GROUP_ID=-1001234567892
DRIVERS_ORDERS_GROUP_ID=-1001234567893
```

### 4. Bot-ni boshlash

```bash
python main.py
```

## 📊 Iş Jarayonlari

### Yo'lovchi
1. `/start` - Botni boshlash
2. Kanalga obuna - Majburiy
3. Rol tanlash - "Yo'lovchi"
4. Ro'yxatdan o'tish - Ism, telefon, hudud
5. Xizmat tanlash - Taxi/Non/Yem
6. Buyurtma berish - Haydovchi kutilasi

### Haydovchi
1. `/start` - Botni boshlash
2. Kanalga obuna - Majburiy
3. Rol tanlash - "Haydovchi"
4. Ro'yxatdan o'tish - Ism, telefon, mashina ma'lumotlari
5. Buyurtmalarni qabul qilish - Guruhdan
6. Yo'lovchi bilan bog'lanish - Telefon orqali

### Admin
1. `/admin` - Admin panelini ochish
2. Statistika ko'rish - Bugun yoki boshqa sana
3. Foydalanuvchilari boshqarish
4. Aktiv buyurtmalarni ko'rish

## ⏰ Avtomatik Timerlar

| Timer | Vaqt | Harakat |
|-------|------|--------|
| Taxi timeout | 7 daqiqa | Haydovchi topilmasa, bekor qilish |
| Driver response | 6 daqiqa | Haydovchi javob bermasa, bekor qilish |
| Cooldown (Non/Yem) | 3 soat | Spam oldini olish |
| Kunlik statistika | 00:05 | Avtomatik hisoblash |

## 🗄️ Database Modellari

### User
- `telegram_id` - Telegram ID
- `first_name, last_name` - Ism-familiya
- `phone_number` - Telefon
- `role` - Rol (driver/passenger)
- `car_number, car_info` - Mashina ma'lumotlari (haydovchi uchun)
- `residence_area` - Yashash hududi (yo'lovchi uchun)
- `rating, confirmed_orders, declined_orders` - Statistika

### Order
- `user_id` - Yo'lovchi ID
- `driver_id` - Haydovchi ID
- `service_type` - Xizmat turi
- `status` - Holati
- `phone_number` - Telefon
- `created_at, accepted_at, confirmed_at` - Timestamps

### Statistics
- `user_id` - Foydalanuvchi ID
- `stat_date` - Sana
- `total_orders, confirmed_orders, cancelled_orders` - Statistika

## 🔒 Xavfsizlik

✅ Kanalga obuna majburiy
✅ Telefon raqamlar haydovchilarga yopiq
✅ Admin komandalar tekshiriladi
✅ Bitta taxi buyurtma (faol)
✅ 3 soatlik cooldown (Non/Yem)

## 📝 API/Handler Examples

### Buyurtma yaratish
```python
order = create_order(
    db=db,
    user_id=user.user_id,
    service_type=ServiceType.TAXI,
    phone_number=user.phone_number
)
```

### Haydovchini qabul qilish
```python
accept_order(
    db=db,
    order_id=order_id,
    driver_id=driver.user_id,
    message_id=callback.message.message_id,
    group_id=callback.message.chat.id
)
```

### Statistika olish
```python
stats = get_daily_stats(db, datetime.utcnow())
```

## 🐛 Debugging

```bash
# Log faylini ko'rish
tail -f bot.log

# Debug mode-da boshlash
# config.py-da: echo=True o'rnatish
```

## 📌 Muhim Shuqliqliklar

1. **Group ID'larini alohida qo'yish** - Taxi, Non, Yem uchun alohida guruhlar
2. **Admin ID'larini ko'rsatish** - config.py-da ADMIN_IDS
3. **.env faylini bevosita saqlash** - Git'dan ignore qilish
4. **Database backup** - Kunlik statistika avtomatik saqlansa ham

## 🤝 Hissa Qo'shish

Agar muammolar yoki taklif bo'lsa, pull request yoki issue ochib qo'ying.

## 📄 Litsenziya

MIT License

## 📞 Qo'llab-Quvvatlash

Savollar yoki muammolar uchun:
- Telegram: @admin
- Email: admin@xizmatlar.uz

---

**⭐ Agar foydali bo'lsa, yulduzcha berish unutmang!**
