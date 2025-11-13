# رفع مشکل su command

## مشکل

خطا: `su: unrecognized option '--config'`

این خطا به این دلیل است که `su` فکر می‌کند `--config` یک option برای خودش است، نه بخشی از دستور gunicorn.

## راه حل

ما `docker-entrypoint.sh` را اصلاح کرده‌ایم تا از `su` با `sh -c` استفاده کند که arguments را به درستی handle می‌کند.

## مراحل

### 1. آپلود فایل جدید

فایل `docker-entrypoint.sh` را به سرور آپلود کنید.

### 2. در سرور

```bash
cd ~/GPS

# توقف کانتینرها
docker compose down

# راه‌اندازی مجدد
docker compose up -d --build

# بررسی لاگ‌ها
docker compose logs web --tail=50
```

### 3. بررسی

```bash
# بررسی وضعیت
docker compose ps

# اگر همه چیز درست بود، migration را اجرا کنید
docker compose exec web python manage.py migrate
```

## تغییرات

- استفاده از `su -s /bin/sh app -c 'exec "$@"' -- "$@"` به جای روش قبلی
- این روش arguments را به درستی به دستور پاس می‌دهد
