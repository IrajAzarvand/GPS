# رفع مشکل Logging Configuration

## مشکل
Django نمی‌تواند handler 'file' را configure کند چون کاربر app نمی‌تواند به فایل‌های لاگ دسترسی داشته باشد.

## راه حل
ما `gps_store/settings.py` را به‌روزرسانی کرده‌ایم تا:
- در production (DEBUG=False) فقط از console handler استفاده کند
- لاگ‌ها به stdout/stderr بروند که Docker آن‌ها را capture می‌کند
- در development (DEBUG=True) اگر دسترسی داشت، از فایل هم استفاده کند

## مراحل

### 1. آپلود فایل جدید به سرور
فایل `gps_store/settings.py` را به سرور آپلود کنید.

### 2. در سرور اجرا کنید:

```bash
cd ~/GPS

# توقف کانتینرها
docker compose down

# راه‌اندازی مجدد
docker compose up -d --build

# بررسی لاگ‌ها
docker compose logs web --tail=50
```

### 3. اگر همه چیز درست بود:

```bash
# اجرای migration
docker compose exec web python manage.py migrate

# ایجاد superuser
docker compose exec web python manage.py createsuperuser

# جمع‌آوری فایل‌های استاتیک
docker compose exec web python manage.py collectstatic --noinput
```

## بررسی

```bash
# بررسی وضعیت کانتینرها
docker compose ps

# مشاهده لاگ‌های Django (حالا باید کار کند)
docker compose logs web

# تست دسترسی به سایت
curl http://localhost/health/
```

## نکته
حالا تمام لاگ‌های Django و Gunicorn از طریق `docker compose logs web` قابل مشاهده هستند. این روش بهتر است چون:
- مشکل دسترسی ندارد
- لاگ‌ها در یک جا جمع می‌شوند
- می‌توانید لاگ‌ها را به راحتی ببینید و فیلتر کنید

