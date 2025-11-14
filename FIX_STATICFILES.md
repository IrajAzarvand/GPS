# رفع مشکل دسترسی Staticfiles

## مشکل
کاربر `app` نمی‌تواند به دایرکتوری `staticfiles` که از host mount شده است، دسترسی داشته باشد.

## راه حل
ما یک entrypoint script (`docker-entrypoint.sh`) ایجاد کرده‌ایم که:
1. به عنوان root اجرا می‌شود
2. دسترسی‌های دایرکتوری‌های mount شده را تنظیم می‌کند
3. `collectstatic` را اجرا می‌کند
4. سپس به کاربر `app` سوئیچ می‌کند و gunicorn را راه‌اندازی می‌کند

## مراحل

### 1. آپلود فایل‌های جدید به سرور
این فایل‌ها را به سرور آپلود کنید:
- `docker-entrypoint.sh`
- `Dockerfile`

### 2. در سرور اجرا کنید:

```bash
cd ~/GPS

# توقف کانتینرها
docker compose down

# راه‌اندازی مجدد با فایل‌های جدید
docker compose up -d --build

# بررسی لاگ‌ها
docker compose logs web --tail=50
```

### 3. بررسی

```bash
# بررسی وضعیت
docker compose ps

# بررسی اینکه staticfiles جمع‌آوری شده است
docker compose exec web ls -la /app/staticfiles

# یا از host
ls -la ~/GPS/staticfiles
```

## نکته
حالا `collectstatic` به صورت خودکار در entrypoint script اجرا می‌شود، پس نیازی به اجرای دستی آن نیست.

اگر می‌خواهید migration را هم به صورت خودکار اجرا شود، می‌توانید خط مربوطه را در `docker-entrypoint.sh` uncomment کنید.

