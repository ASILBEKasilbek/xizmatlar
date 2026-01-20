# Xizmatlar Bot - Setup va Deploy Guide

## 🚀 Quick Start (5 daqiqada)

### Step 1: Clone yoki fayllarni yuklash
```bash
cd xizmatlar
```

### Step 2: Virtual environment
```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate      # Windows
```

### Step 3: Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Environment o'rnatish
```bash
cp .env.example .env
# .env-ni o'zingizning tokenlaringiz bilan to'ldirish
```

### Step 5: Bot-ni boshlash
```bash
python main.py
```

---

## 📱 Telegram Setup

### 1. Bot token olish
1. Telegram-da `@BotFather` ga yozing
2. `/newbot` komandasi
3. Bot nomini kiriting
4. Bot usernameni kiriting  
5. Token oling va `.env`-ga qo'ying

### 2. Channel yaratish
1. Yangi channel yaratish: "@xizmatlar_bot_channel" (example)
2. Channel ID olish:
   - Bot-ni channelga add qilish
   - Xabar yuborish
   - `/getChannelID` (special bot orqali yoki API)
   - ID: `-1001234567890` format

### 3. Group'lar yaratish
- **Haydovchilar**: @drivers_xizmatlar
- **Yo'lovchilar**: @passengers_xizmatlar  
- **Taxi Buyurtmalar**: @taxi_orders_xizmatlar
- **Non Buyurtmalar**: @bread_orders_xizmatlar
- **Yem Buyurtmalar**: @feed_orders_xizmatlar

### 4. IDs olish
```python
# Bot-da xabar yuborib, logging-dan ID olish
# Yoki BotFather-da /getgroupid
```

### 5. Bot permissions
- Guruhlarda: Message send, Edit messages, Delete messages
- Channel-da: Obuna check

---

## 🗄️ Database Setup

### SQLite (Development)
```bash
# Avtomatik yaratiladi
# xizmatlar_bot.db fayli tugatiladi
```

### PostgreSQL (Production)

#### Option 1: Manual
```bash
# PostgreSQL o'rnatish
brew install postgresql  # macOS
apt-get install postgresql  # Ubuntu

# Database yaratish
createdb xizmatlar_bot

# .env-da
DATABASE_URL=postgresql://user:password@localhost/xizmatlar_bot
```

#### Option 2: Docker
```bash
docker-compose up -d postgres

# .env-da
DATABASE_URL=postgresql://xizmatlar:password@postgres:5432/xizmatlar_bot
```

---

## 🐳 Docker Deployment

### Tugmach boshlash
```bash
# .env fayli bilan
docker-compose up -d
```

### Logs ko'rish
```bash
docker-compose logs -f bot
```

### Xizmatni to'xtatish
```bash
docker-compose down
```

### Services:
- Bot: xizmatlar_bot container
- Database: PostgreSQL
- Cache: Redis
- Admin: PgAdmin (localhost:5050)

---

## 📊 Admin Setup

### Admin ID'larini qo'shish
```env
ADMIN_IDS=123456789,987654321,111222333
```

### Admin Komandalar
- `/admin` - Admin panelini ochish
- Bugungi statistika
- Istalgan kuning statistikasi
- Foydalanuvchilar haqida
- Aktiv buyurtmalar

---

## 🔧 Configuration Tuning

### Timers (config.py)
```python
TAXI_ORDER_TIMEOUT = 7 * 60        # 7 daqiqa
DRIVER_RESPONSE_TIMEOUT = 6 * 60   # 6 daqiqa
BREAD_COOLDOWN = 3 * 60 * 60       # 3 soat
FEED_COOLDOWN = 3 * 60 * 60        # 3 soat
MAX_DECLINE_BEFORE_CANCEL = 3      # 3 rad
```

### Database
```python
# SQLite -> PostgreSQL o'zgarish
DATABASE_URL = "postgresql://user:pass@localhost/db"
```

### Logging
```python
# DEBUG, INFO, WARNING, ERROR
LOG_LEVEL = "INFO"
```

---

## 🧪 Testing

### Local test
```bash
# Bot to'g'ri ishlayotganini tekshirish
python -c "from main import main; import asyncio; asyncio.run(main())"
```

### Database test
```bash
python -c "from database import init_db; init_db()"
```

### API test
```bash
# CRUD funksiyalarini tekshirish
python -c "from crud import get_all_drivers; from database import SessionLocal; db = SessionLocal(); print(get_all_drivers(db))"
```

---

## 🚨 Troubleshooting

### Bot to'g'ri javob bermayapti
```bash
# 1. Token tekshirish
echo $BOT_TOKEN

# 2. Internet connection
ping api.telegram.org

# 3. Logs ko'rish
tail -f bot.log
```

### Database xatosi
```bash
# 1. Connection string tekshirish
# 2. Database running?
psql -U user -d xizmatlar_bot -c "SELECT 1"

# 3. Logs
docker-compose logs postgres
```

### Channel'ga obuna kerak
```bash
# 1. Channel ID to'g'ri?
# 2. Bot channel adminimi?
# 3. Bot channel-ga message yuboradimi?
```

---

## 📈 Monitoring

### Log File
```bash
tail -f bot.log
```

### Database Size
```bash
# PostgreSQL
psql -U user -d xizmatlar_bot -c "SELECT pg_size_pretty(pg_database_size('xizmatlar_bot'))"

# SQLite
ls -lh xizmatlar_bot.db
```

### Active Orders
```bash
# Admin paneldan /admin -> "Aktiv buyurtmalar"
```

---

## 🔐 Security

### Production Deployment
1. ✅ HTTPS/TLS
2. ✅ Strong database password
3. ✅ Environment variables secure
4. ✅ Firewall configured
5. ✅ Regular backups
6. ✅ Logs rotate

### Backup Strategy
```bash
# PostgreSQL backup
pg_dump -U user -d xizmatlar_bot > backup.sql

# Restore
psql -U user -d xizmatlar_bot < backup.sql

# Automated (cron)
0 2 * * * pg_dump -U user -d xizmatlar_bot > /backups/db_$(date +\%Y\%m\%d).sql
```

---

## 📚 API Reference

### User Management
```python
from crud import create_user, get_user_by_telegram_id, update_user

# Foydalanuvchi yaratish
user = create_user(db, telegram_id, "John", "Doe", "driver")

# Foydalanuvchini olish
user = get_user_by_telegram_id(db, telegram_id)

# Foydalanuvchini yangilash
update_user(db, user_id, phone_number="+998901234567")
```

### Order Management
```python
from crud import create_order, accept_order, confirm_order, cancel_order

# Buyurtma yaratish
order = create_order(db, user_id, "taxi", "+998901234567")

# Qabul qilish
accept_order(db, order_id, driver_id, message_id, group_id)

# Tasdiqlash
confirm_order(db, order_id)

# Bekor qilish
cancel_order(db, order_id, "Sabab")
```

### Statistics
```python
from crud import get_daily_stats, get_orders_by_date

# Bugungi statistika
stats = get_daily_stats(db, datetime.utcnow())

# O'tgan kuning buyurtmalari
orders = get_orders_by_date(db, yesterday)
```

---

## 🎓 Learning Resources

- [Aiogram Documentation](https://docs.aiogram.dev)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org)
- [APScheduler](https://apscheduler.readthedocs.io)
- [Telegram Bot API](https://core.telegram.org/bots/api)

---

## 📞 Support

Muammolar uchun:
1. Logs ko'rish
2. Database connection tekshirish  
3. Token va ID'lar to'g'riligini tekshirish
4. Discord/GitHub issue ochish

---

**Omad bilan! 🚀**
