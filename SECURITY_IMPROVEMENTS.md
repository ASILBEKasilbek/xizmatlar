# Xavfsizlik yaxshilashlari uchun config o'zgartirish

Hozirgi config faylida admin ID'lar hardcode qilingan. Bu xavfsizlik muammosi.

## Yechim:

### 1. .env fayliga qo'shish:
```bash
ADMIN_IDS=5306481482,1234567890,9876543210
```

### 2. config/settings.py da o'zgartirish:

```python
# Eski kod:
self.ADMIN_IDS = [5306481482]

# Yangi kod:
admin_ids_str = os.getenv("ADMIN_IDS", "5306481482")
self.ADMIN_IDS = [int(x.strip()) for x in admin_ids_str.split(",") if x.strip()]
```

Bu yaxshilash:
- ✅ Admin ID'lar .env faylda
- ✅ Ko'p admin qo'shish mumkin
- ✅ Git'ga commit qilinmaydi
- ✅ Xavfsiz
