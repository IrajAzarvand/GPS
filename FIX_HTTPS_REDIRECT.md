# رفع مشکل HTTPS Redirect

## مشکل

مرورگر سعی می‌کند به HTTPS برود اما SSL تنظیم نشده است و خطای ERR_CONNECTION_REFUSED می‌دهد.

## علت

Django settings می‌گوید `SECURE_SSL_REDIRECT = True` که باعث می‌شود Django به HTTPS redirect کند.

## راه حل

### 1. بررسی فایل .env

مطمئن شوید که در فایل `.env` این مقادیر را دارید:

```env
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
```

### 2. بررسی وضعیت کانتینرها

```bash
docker compose ps
```

### 3. بررسی لاگ‌های nginx

```bash
docker compose logs nginx --tail=50
```

### 4. بررسی لاگ‌های web

```bash
docker compose logs web --tail=50
```

### 5. راه‌اندازی مجدد

```bash
docker compose restart web nginx
```

### 6. تست دسترسی

```bash
# تست از داخل سرور
curl http://localhost/

# یا از مرورگر
http://91.107.169.72
```

## نکته

اگر می‌خواهید از HTTPS استفاده کنید، باید SSL certificate نصب کنید. در حال حاضر فقط HTTP کار می‌کند.
