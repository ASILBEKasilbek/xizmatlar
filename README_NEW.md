# 🚖 Xizmatlar Bot - Taxi, Non, Yem

Telegram bot - Haydovchilar va yo'lovchilar uchun xizmatlar platformasi

## 📋 Loyiha Tuzilmasi

```
xizmatlar/
├── main.py                 # Botni ishga tushirish
├── config.py              # Barcha sozlamalar (kanal, guruhlar, admin ID)
├── database.py            # Ma'lumotlar bazasi (User, Order modellari)
├── middlewares.py         # Kanalga obuna tekshiruvi
├── scheduler.py           # Taymerlar (7 va 6 daqiqalik timeout'lar)
├── keyboards.py           # Barcha klaviaturalar
├── utils.py               # Yordamchi funksiyalar
├── states.py              # FSM states (ro'yxatdan o'tish)
├── handlers/              # Barcha handlerlar
│   ├── start.py          # /start va obuna tekshiruvi
│   ├── registration.py   # Haydovchi/Yo'lovchi ro'yxatdan o'tish
│   ├── services.py       # Taxi, Non, Yem buyurtma berish
│   └── orders.py         # Buyurtmalarni qabul qilish, tasdiqlash, rad etish
└── requirements.txt       # Python kutubxonalari
```

## ⚙️ Sozlash

### 1. Bot Token

`.env` faylini yarating va bot tokenini kiriting:

```env
BOT_TOKEN=your_bot_token_here
```

### 2. Sozlamalar

[config.py](config.py) faylida barcha sozlamalar mavjud:

```python
# Admin ID
ADMIN_IDS = [5306481482]

# Kanal
CHANNEL_ID = "@foydali_xizmatt"

# Guruhlar
GROUP1 = "@salom777899"      # Haydovchilar ro'yxati
GROUP2 = "@yo_lovchiguruh"   # Yo'lovchilar ro'yxati
GROUP3 = "@uydantaksi"       # Taxi buyurtmalari
GROUP4 = "@nonguruh"         # Non buyurtmalari
GROUP5 = "@yemguruh"         # Yem buyurtmalari
```

### 3. Guruhlarni Sozlash

1. Botni barcha guruhlarga admin qiling
2. Guruh usernamlarini yoki ID'larini config.py ga kiriting
3. Kanalga ham botni admin qiling

## 🚀 Ishga Tushirish

```bash
# Kutubxonalarni o'rnatish
pip install -r requirements.txt

# Botni ishga tushirish
python main.py
```

## 📱 Funksiyalar

### START & OBUNA
✅ `/start` komandasi  
✅ Kanalga obuna tekshiruvi  
✅ Obuna bo'lgach avtomatik tekshirish  
✅ Kanalni tark etib qayta /start bosish ishlaydi

### ROL TANLASH
✅ Yo'lovchi tanlash  
✅ Haydovchi tanlash  
✅ Bitta foydalanuvchi faqat bitta rol

### RO'YXATDAN O'TISH
✅ Ism-familiya validatsiyasi  
✅ Telefon raqam validatsiyasi (+998XXXXXXXXX)  
✅ Bir foydalanuvchi 1 marta ro'yxatdan o'tadi  
✅ Yangi haydovchi → GROUP1 ga yuboriladi  
✅ Yangi yo'lovchi → GROUP2 ga yuboriladi

### TAXI BUYURTMA
✅ 1 foydalanuvchi → 1 faol buyurtma  
✅ Buyurtma GROUP3 guruhiga chiqadi  
✅ Telefon raqam guruhda ko'rinmaydi  
✅ Haydovchi qabul qilgach, telefon private ga yuboriladi

### HAYDOVCHI QABUL QILISH
✅ 2 haydovchi bir vaqtda qabul qila olmaydi  
✅ Qabul qilingach guruh xabari o'chiriladi  
✅ To'g'ri haydovchiga biriktiriladi

### TAYMERLAR
⏱️ **7 daqiqa**: Hech kim bosmasa buyurtma yopiladi  
⏱️ **6 daqiqa**: Haydovchi jim bo'lsa avtomatik rad bo'ladi

### RAD ETISH LOGIKASI
✅ 1–2 marta rad → qayta guruhga chiqadi  
✅ 3 marta rad → butunlay yopiladi

### NON & YEM CHEKLOVI
✅ 3 soatlik cheklov  
✅ Foydalanuvchi ma'lumotlari guruhga yuboriladi

## 📂 Database Modellari

### User (Foydalanuvchilar)
- `user_id`: Telegram ID
- `fullname`: Ism-familiya
- `phone`: Telefon raqam
- `user_type`: "driver" yoki "passenger"
- `car_model`: Mashina modeli (haydovchilar uchun)
- `area`: Hudud (yo'lovchilar uchun)

### Order (Buyurtmalar)
- `order_id`: Buyurtma ID
- `passenger_id`: Yo'lovchi ID
- `service_type`: "🚕 Taxi", "🥖 Non", "🌾 Yem"
- `status`: "waiting", "accepted", "confirmed", "cancelled"
- `reject_count`: Rad etilishlar soni
- `driver_id`: Haydovchi ID (qabul qilgandan keyin)

### ProductCooldown (Non/Yem cheklovi)
- `user_id`: Foydalanuvchi ID
- `product_type`: "🥖 Non" yoki "🌾 Yem"
- `last_order_time`: Oxirgi buyurtma vaqti

## 🔧 Xususiyatlar

✅ Kanal obunasini avtomatik tekshirish  
✅ Bitta foydalanuvchi faqat bitta rol (haydovchi yoki yo'lovchi)  
✅ Telefon raqam guruhda ko'rinmaydi (xavfsizlik)  
✅ 7 va 6 daqiqalik taymerlar  
✅ 3 soatlik Non/Yem cheklovi  
✅ 3 marta rad etilsa buyurtma yopiladi  
✅ Barcha xatolar log faylida saqlanadi

## 👨‍💻 Yaratuvchi

**Admin**: @SAT_mathuz  
**Kanal**: @foydali_xizmatt

## 📝 Litsenziya

MIT License
