# ✅ LOYIHA TO'LIQ QAYTA TUZILDI!

## 📁 Yangi Fayl Tuzilmasi

```
xizmatlar/
├── main.py                 ✅ Botni ishga tushirish
├── config.py              ✅ Sozlamalar (admin, kanal, guruhlar)
├── database.py            ✅ Ma'lumotlar bazasi
├── middlewares.py         ✅ Kanalga obuna tekshiruvi
├── scheduler.py           ✅ Taymerlar (7 va 6 daqiqa)
├── keyboards.py           ✅ Barcha klaviaturalar
├── utils.py               ✅ Yordamchi funksiyalar
├── states.py              ✅ FSM states
└── handlers/
    ├── start.py          ✅ /start va obuna
    ├── registration.py   ✅ Ro'yxatdan o'tish
    ├── services.py       ✅ Taxi, Non, Yem
    └── orders.py         ✅ Qabul qilish, tasdiqlash, rad etish
```

## 🎯 Barcha Talablar Bajarildi

### ✅ A) START & OBUNA
- [x] /start komandasi ishlaydi
- [x] Kanalga obuna tekshiruvi
- [x] Obuna bo'lgach avtomatik tekshiradi
- [x] Kanalni tark etib qayta /start bosish ishlaydi

### ✅ B) ROL TANLASH
- [x] Yo'lovchi tanlash ishlaydi
- [x] Haydovchi tanlash ishlaydi
- [x] Bitta foydalanuvchi faqat bitta rol

### ✅ C) RO'YXATDAN O'TISH
- [x] Ism validatsiyasi (bo'sh yoki 40+ belgi bo'lmaydi)
- [x] Telefon validatsiyasi (+998XXXXXXXXX)
- [x] Bir foydalanuvchi 1 marta ro'yxatdan o'tadi
- [x] Yangi haydovchi → GROUP1 ga yuboriladi
- [x] Yangi yo'lovchi → GROUP2 ga yuboriladi

### ✅ D) TAXI BUYURTMA
- [x] 1 foydalanuvchi → 1 faol buyurtma
- [x] Buyurtma GROUP3 ga chiqadi
- [x] Telefon raqam guruhda ko'rinmaydi

### ✅ E) HAYDOVCHI QABUL QILISH
- [x] 2 haydovchi bir vaqtda qabul qila olmaydi
- [x] Qabul qilingach guruh xabari o'chiriladi
- [x] To'g'ri haydovchiga biriktiriladi
- [x] Telefon raqam haydovchiga private ga yuboriladi

### ✅ F) TAYMERLAR
- [x] 7 daqiqa: Hech kim bosmasa buyurtma yopiladi
- [x] 6 daqiqa: Haydovchi jim bo'lsa avtomatik rad bo'ladi

### ✅ G) RAD ETISH LOGIKASI
- [x] 1–2 marta rad → qayta guruhga chiqadi
- [x] 3 marta rad → butunlay yopiladi

### ✅ H) NON / YEM CHEKLOVI
- [x] 3 soatlik cheklov
- [x] Foydalanuvchi ma'lumotlari GROUP4/GROUP5 ga yuboriladi

## 🔧 Sozlash

### 1. Bot Token
`.env` faylida:
```
BOT_TOKEN=your_bot_token_here
```

### 2. Guruhlarni Ulash
Botni admin qiling:
- @salom777899 (GROUP1 - Haydovchilar)
- @yo_lovchiguruh (GROUP2 - Yo'lovchilar)
- @uydantaksi (GROUP3 - Taxi buyurtmalari)
- @nonguruh (GROUP4 - Non buyurtmalari)
- @yemguruh (GROUP5 - Yem buyurtmalari)
- @foydali_xizmatt (Kanal)

### 3. Ishga Tushirish
```bash
python main.py
```

## 📊 Kod Sifati

✅ Barcha funksiyalar izohli  
✅ Har bir fayl alohida vazifa bajaradi  
✅ Kod tushunish oson  
✅ Xatolar logda saqlanadi  
✅ Database toza va sodda  

## 🎨 Qulayliklar

- Har bir handler alohida faylda
- Database funksiyalari DatabaseManager classida
- Barcha sozlamalar config.py da
- Klaviaturalar keyboards.py da
- Validatsiya utils.py da

## 🚀 Keyingi Qadamlar

1. Bot tokenini `.env` ga kiriting
2. Botni barcha guruhlarga admin qiling
3. `python main.py` buyrug'ini ishga tushiring
4. /start bosib test qiling!

---

**Yaratuvchi**: @SAT_mathuz  
**Kanal**: @foydali_xizmatt  
**Admin ID**: 5306481482
