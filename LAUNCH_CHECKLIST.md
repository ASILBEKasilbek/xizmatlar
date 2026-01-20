# 🚀 Bot Launch Checklist

## Pre-Launch (15 daqiqa)

### 1. Telegram Setup ✅
- [ ] Bot token olindi (@BotFather)
- [ ] Channel yaratildi
- [ ] Channel ID olindi
- [ ] Bot channel adminiga qo'shildi
- [ ] 3 ta group yaratildi:
  - [ ] Haydovchilar guruhi
  - [ ] Yo'lovchilar guruhi
  - [ ] Taxi buyurtmalar guruhi
- [ ] Bot barcha guruhlarga adminiga qo'shildi
- [ ] Permissions berildi (send, edit, delete messages)

### 2. Environment Setup ✅
- [ ] `.env` fayli yaratildi (`.env.example`-dan)
- [ ] `BOT_TOKEN` to'ldirildi
- [ ] `ADMIN_IDS` to'ldirildi (virgul bilan ajratib)
- [ ] `CHANNEL_ID` to'ldirildi (manfiy son)
- [ ] `DRIVERS_GROUP_ID` to'ldirildi
- [ ] `PASSENGERS_GROUP_ID` to'ldirildi
- [ ] `DRIVERS_ORDERS_GROUP_ID` to'ldirildi

### 3. Dependencies ✅
- [ ] Python 3.10+ o'rnatildi
- [ ] Virtual environment yaratildi
- [ ] `pip install -r requirements.txt` ishlatildi
- [ ] Barcha kutubxonalar o'rnatildi (xatosiz)

### 4. Database ✅
- [ ] SQLite yoki PostgreSQL tanlandi
- [ ] `DATABASE_URL` to'g'ri o'rnatildi
- [ ] Database yaratildi (birinchi ishga tushganda)

---

## Launch Test (5 daqiqa)

### Test 1: Bot Starts ✅
```bash
python main.py
```
- [ ] Bot started successfully xabari
- [ ] Scheduler started successfully xabari
- [ ] Database initialized xabari
- [ ] Hech qanday xato yo'q

### Test 2: Bot Commands ✅
- [ ] `/start` - bot javob beradi
- [ ] Kanalga obuna majburiyati ishlaydi
- [ ] Rol tanlash klaviaturasi ko'rinadi

### Test 3: Registration ✅

**Haydovchi:**
- [ ] Haydovchi rolini tanlash mumkin
- [ ] Ism kiritish jarayoni ishlaydi
- [ ] Telefon kontakti so'raladi
- [ ] Mashina ma'lumotlari so'raladi
- [ ] Davlat raqami so'raladi
- [ ] Haydovchilar guruhiga xabar keladi
- [ ] Ro'yxatdan o'tish yakunlanadi

**Yo'lovchi:**
- [ ] Yo'lovchi rolini tanlash mumkin
- [ ] Ism kiritish jarayoni ishlaydi
- [ ] Telefon kontakti so'raladi
- [ ] Hudud so'raladi
- [ ] Yo'lovchilar guruhiga xabar keladi
- [ ] Xizmat tanlash klaviaturasi ko'rinadi

### Test 4: Orders ✅

**Taxi:**
- [ ] Taxi tugmasi ishlaydi
- [ ] Buyurtma taxi guruhiga yuboriladi
- [ ] Telefon raqam ko'rinmaydi
- [ ] "Qabul qilish" tugmasi ishlaydi
- [ ] Haydovchi qabul qiladi
- [ ] Yo'lovchi telefoni haydovchiga yuboriladi
- [ ] Tasdiqlash tugmalari ko'rinadi
- [ ] Tasdiqlash ishlaydi

**Non/Yem:**
- [ ] Non tugmasi ishlaydi
- [ ] Buyurtma guruhga yuboriladi
- [ ] Telefon raqam ko'rinadi
- [ ] 3 soatlik cooldown ishlaydi

### Test 5: Timers ✅
- [ ] 7 daqiqalik timeout ishlaydi (taxi)
- [ ] 6 daqiqalik driver response ishlaydi
- [ ] Avtomatik bekor qilish ishlaydi

### Test 6: Admin Panel ✅
- [ ] `/admin` - panel ochiladi
- [ ] Bugungi statistika ko'rinadi
- [ ] Istalgan kuning statistikasi ishlaydi
- [ ] Foydalanuvchilar haqida ma'lumot
- [ ] Aktiv buyurtmalar ko'rinadi

---

## Production Launch

### Security ✅
- [ ] `.env` fayli gitignore'da
- [ ] Strong password ishlatilyapti
- [ ] Admin ID'lari xavfsiz
- [ ] HTTPS ishlatiladi (webhook uchun)

### Monitoring ✅
- [ ] `bot.log` fayli yaratildi
- [ ] Logs kuzatilmoqda
- [ ] Database backup o'rnatildi
- [ ] Health check (Docker uchun)

### Performance ✅
- [ ] Server tezligi yetarli
- [ ] Database connection stable
- [ ] Memory usage qabul qilinadigan

---

## Common Issues & Fixes

### Issue: Bot javob bermayapti
**Fix:**
```bash
# 1. Token tekshirish
echo $BOT_TOKEN

# 2. Logs
tail -f bot.log

# 3. Internet
ping api.telegram.org
```

### Issue: Channel'ga obuna kerak xatosi
**Fix:**
- Channel ID manfiy son (-1001234567890)
- Bot channel adminimi?
- Channel public yoki private?

### Issue: Buyurtma guruhga kelmaydi
**Fix:**
- Group ID to'g'rimi?
- Bot group adminimi?
- Bot send message permission bormi?

### Issue: Database xatosi
**Fix:**
```bash
# Connection string tekshirish
echo $DATABASE_URL

# SQLite uchun
ls -lh xizmatlar_bot.db

# PostgreSQL uchun
psql -U user -d xizmatlar_bot -c "SELECT 1"
```

---

## 📊 Success Metrics

### Day 1 Targets
- [ ] 10+ foydalanuvchi ro'yxatdan o'tdi
- [ ] 5+ taxi buyurtmalari
- [ ] 100% uptime
- [ ] Hech qanday kritik xato yo'q

### Week 1 Targets
- [ ] 50+ foydalanuvchi
- [ ] 50+ buyurtmalar
- [ ] 95%+ tasdiqlash rate
- [ ] Kunlik statistika avtomatik keladi

---

## 🎉 Go Live!

**Final Steps:**
1. ✅ Barcha testlar o'tdi
2. ✅ Admin panel ishlaydi
3. ✅ Monitoring o'rnatildi
4. ✅ Backup strategy ready

**Launch Command:**
```bash
# Production
nohup python main.py > output.log 2>&1 &

# Docker
docker-compose up -d

# Systemd (recommended)
sudo systemctl start xizmatlar-bot
sudo systemctl enable xizmatlar-bot
```

**Post-Launch:**
- [ ] Bot ishlamoqda (5 daqiqadan keyin tekshirish)
- [ ] Xabar yuborish test qilish
- [ ] Logs monitoring boshlash
- [ ] Foydalanuvchilarga e'lon qilish

---

**Omad bilan ishga tushirish! 🎊**
