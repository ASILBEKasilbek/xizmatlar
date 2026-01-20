# 📁 Xizmatlar Bot - Project Structure

```
xizmatlar/
│
├── 📄 main.py                      # Bot entry point
├── 📄 config.py                    # Konfiguratsiya va konstantlar
├── 📄 database.py                  # SQLAlchemy models va database setup
├── 📄 crud.py                      # Database CRUD operatsiyalari
├── 📄 states.py                    # FSM states va middlewares
├── 📄 keyboards.py                 # Telegram klaviaturalar va button'lar
├── 📄 scheduler.py                 # APScheduler timerlar
├── 📄 utils.py                     # Helper funksiyalar
├── 📄 test_bot.py                  # Test script
│
├── 📁 handlers/                    # Message va callback handlers
│   ├── 📄 __init__.py
│   ├── 📄 start.py                # /start va rol tanlash
│   ├── 📄 driver_registration.py # Haydovchi ro'yxatdan o'tish
│   ├── 📄 passenger_registration.py # Yo'lovchi ro'yxatdan o'tish
│   ├── 📄 orders.py               # Buyurtma management
│   └── 📄 admin.py                # Admin paneli
│
├── 📄 requirements.txt             # Python dependencies
├── 📄 .env.example                 # Environment variables template
├── 📄 .gitignore                   # Git ignore file
├── 📄 .dockerignore                # Docker ignore file
│
├── 📄 Dockerfile                   # Docker image config
├── 📄 docker-compose.yml           # Docker compose config
├── 📄 xizmatlar-bot.service        # Systemd service file
├── 📄 Makefile                     # Command shortcuts
│
├── 📄 README.md                    # Main documentation
├── 📄 SETUP_GUIDE.md               # Detailed setup guide
├── 📄 LAUNCH_CHECKLIST.md          # Pre-launch checklist
└── 📄 MIGRATIONS.md                # Database migrations guide
```

## 📊 File Sizes & Lines of Code

| File | Purpose | LOC |
|------|---------|-----|
| main.py | Bot initialization | ~100 |
| config.py | Configuration | ~80 |
| database.py | SQLAlchemy models | ~200 |
| crud.py | Database operations | ~300 |
| states.py | FSM & middleware | ~150 |
| keyboards.py | UI elements | ~250 |
| scheduler.py | Timers | ~200 |
| utils.py | Helpers | ~200 |
| handlers/start.py | Start handler | ~100 |
| handlers/driver_registration.py | Driver reg | ~150 |
| handlers/passenger_registration.py | Passenger reg | ~150 |
| handlers/orders.py | Order management | ~400 |
| handlers/admin.py | Admin panel | ~200 |
| **Total** | | **~2,500 LOC** |

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Telegram API                        │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│              Aiogram Bot (main.py)                   │
│  ┌──────────────────────────────────────────────┐   │
│  │          Dispatcher + Routers                │   │
│  └──────────────────────────────────────────────┘   │
└──────────┬──────────────────────────────────────────┘
           │
           ├─── Middlewares (states.py)
           │     ├── DatabaseMiddleware
           │     ├── UserCheckMiddleware
           │     └── AdminCheckMiddleware
           │
           ├─── Handlers (handlers/)
           │     ├── start.py
           │     ├── driver_registration.py
           │     ├── passenger_registration.py
           │     ├── orders.py
           │     └── admin.py
           │
           ├─── FSM States (states.py)
           │     ├── RegistrationState
           │     ├── OrderState
           │     └── AdminState
           │
           ├─── CRUD Operations (crud.py)
           │     ├── User management
           │     ├── Order management
           │     └── Statistics
           │
           └─── Database (database.py)
                 ├── User model
                 ├── Order model
                 ├── Statistics model
                 └── CooldownTracker model
```

## 🔄 Data Flow

### 1. User Registration Flow
```
User → /start → Channel Check → Role Selection
                                      ↓
                      Driver ←────────┴────────→ Passenger
                        ↓                           ↓
                   Name Input                   Name Input
                        ↓                           ↓
                   Phone Input                  Phone Input
                        ↓                           ↓
                   Car Info                     Area Input
                        ↓                           ↓
                   Car Number                   Database Save
                        ↓                           ↓
                   Database Save                Group Notify
                        ↓
                   Group Notify
```

### 2. Taxi Order Flow
```
Passenger → Select Service → Taxi
                              ↓
                    Check Active Order (1 max)
                              ↓
                    Create Order → Database
                              ↓
                    Send to Drivers Group (7 min timer)
                              ↓
                    Driver Accept → Order Status: accepted
                              ↓
                    Send Passenger Info (6 min timer)
                              ↓
              Driver Confirm ←────→ Driver Decline
                    ↓                     ↓
            Status: confirmed      Retry (max 3x)
                    ↓                     ↓
             Complete Order         Cancel Order
```

### 3. Timer Management
```
APScheduler (scheduler.py)
    ↓
    ├─── check_taxi_timeout (every 30s)
    │     └─── Cancel orders after 7 min
    │
    ├─── check_driver_timeout (every 30s)
    │     └─── Cancel orders after 6 min (no driver response)
    │
    └─── generate_daily_stats (00:05 daily)
          └─── Calculate and send statistics
```

## 🗄️ Database Schema

```sql
-- Users Table
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    telegram_id INTEGER UNIQUE NOT NULL,
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    phone_number VARCHAR(20),
    role VARCHAR(50) NOT NULL,
    car_number VARCHAR(50),
    car_info VARCHAR(500),
    residence_area VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    rating FLOAT DEFAULT 5.0,
    total_orders INTEGER DEFAULT 0,
    confirmed_orders INTEGER DEFAULT 0,
    declined_orders INTEGER DEFAULT 0,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Orders Table
CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id),
    driver_id INTEGER REFERENCES users(user_id),
    service_type VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'waiting',
    phone_number VARCHAR(20) NOT NULL,
    description VARCHAR(1000),
    location VARCHAR(255),
    message_id INTEGER,
    group_id INTEGER,
    declined_count INTEGER DEFAULT 0,
    created_at TIMESTAMP,
    accepted_at TIMESTAMP,
    confirmed_at TIMESTAMP
);

-- Statistics Table
CREATE TABLE statistics (
    stat_id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id),
    stat_date TIMESTAMP,
    total_orders INTEGER DEFAULT 0,
    completed_orders INTEGER DEFAULT 0,
    cancelled_orders INTEGER DEFAULT 0,
    taxi_orders INTEGER DEFAULT 0,
    bread_orders INTEGER DEFAULT 0,
    feed_orders INTEGER DEFAULT 0
);

-- Cooldown Tracker
CREATE TABLE cooldown_tracker (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id),
    service_type VARCHAR(50) NOT NULL,
    last_order_at TIMESTAMP NOT NULL
);
```

## 🎯 Key Features Implementation

| Feature | Files Involved | Status |
|---------|---------------|--------|
| User Registration | handlers/driver_registration.py, handlers/passenger_registration.py, crud.py | ✅ |
| Channel Subscription | states.py, handlers/start.py | ✅ |
| Taxi Orders | handlers/orders.py, crud.py | ✅ |
| Non/Yem Orders | handlers/orders.py, crud.py | ✅ |
| Auto Timers | scheduler.py | ✅ |
| Cooldown System | crud.py, database.py | ✅ |
| Admin Panel | handlers/admin.py | ✅ |
| Statistics | crud.py, scheduler.py | ✅ |
| FSM States | states.py | ✅ |
| Middlewares | states.py | ✅ |

## 🔧 Configuration Files

| File | Purpose |
|------|---------|
| .env | Environment variables (tokens, IDs) |
| config.py | Bot configuration constants |
| requirements.txt | Python dependencies |
| Dockerfile | Docker image configuration |
| docker-compose.yml | Multi-container setup |
| xizmatlar-bot.service | Systemd service |
| Makefile | Command shortcuts |

---

**Umumiy kod: ~2,500 lines**  
**Fayllar soni: 20+**  
**Arxitektura: Clean, Modular, Scalable**  
**Status: Production-Ready ✅**
