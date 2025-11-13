# راه حل سریع برای مشکل Staticfiles

## راه حل سریع (بدون rebuild)

اگر نمی‌خواهید کانتینر را rebuild کنید، می‌توانید دسترسی‌ها را در host تنظیم کنید:

```bash
cd ~/GPS

# تنظیم دسترسی‌های دایرکتوری‌ها
sudo chown -R 1000:1000 staticfiles/ media/ logs/
chmod -R 755 staticfiles/ media/ logs/

# یا اگر کاربر app UID متفاوتی دارد:
chmod -R 777 staticfiles/ media/ logs/

# راه‌اندازی مجدد
docker compose restart web

# حالا collectstatic را اجرا کنید
docker compose exec web python manage.py collectstatic --noinput
```

## راه حل دائمی (توصیه می‌شود)

با استفاده از entrypoint script که ایجاد کردیم:

### 1. آپلود فایل‌های جدید

- `docker-entrypoint.sh`
- `Dockerfile`

### 2. در سرور

```bash
cd ~/GPS

# توقف کانتینرها
docker compose down

# راه‌اندازی مجدد
docker compose up -d --build

# بررسی لاگ‌ها
docker compose logs web
```

حالا `collectstatic` به صورت خودکار در entrypoint اجرا می‌شود و نیازی به اجرای دستی آن نیست.
