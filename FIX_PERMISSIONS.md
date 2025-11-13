# رفع مشکل دسترسی (Permission Denied)

## مشکل
کانتینر web نمی‌تواند به فایل‌های لاگ بنویسد و مدام restart می‌شود.

## راه حل سریع

در سرور، این دستورات را اجرا کنید:

```bash
cd ~/GPS

# توقف کانتینرها
docker compose down

# تنظیم دسترسی‌های دایرکتوری logs
sudo chown -R 1000:1000 logs/
chmod -R 755 logs/

# یا اگر کاربر app UID متفاوتی دارد:
mkdir -p logs
chmod 777 logs/

# راه‌اندازی مجدد
docker compose up -d --build
```

## راه حل دائمی (توصیه می‌شود)

ما فایل‌های `gunicorn.conf.py` و `Dockerfile` را به‌روزرسانی کرده‌ایم تا:
1. Gunicorn به جای فایل، به stdout/stderr بنویسد (که Docker آن را capture می‌کند)
2. دسترسی‌های logs در Dockerfile تنظیم شود

بعد از pull کردن تغییرات:

```bash
cd ~/GPS
git pull  # یا آپلود مجدد فایل‌های تغییر یافته
docker compose down
docker compose up -d --build
```

## بررسی

```bash
# بررسی لاگ‌ها (حالا باید کار کند)
docker compose logs web

# بررسی وضعیت
docker compose ps
```

## اگر هنوز مشکل دارید

```bash
# بررسی دسترسی‌ها در کانتینر
docker compose exec web ls -la /app/logs

# اگر لازم است، دسترسی‌ها را تغییر دهید
docker compose exec web chmod 777 /app/logs
```

