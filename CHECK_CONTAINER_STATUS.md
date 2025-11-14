# بررسی وضعیت کانتینر

## دستورات برای بررسی مشکل

### 1. بررسی لاگ‌های کانتینر web

```bash
docker compose logs web --tail=100
```

### 2. بررسی وضعیت همه کانتینرها

```bash
docker compose ps -a
```

### 3. بررسی لاگ‌های همه سرویس‌ها

```bash
docker compose logs --tail=50
```

### 4. بررسی اینکه آیا دیتابیس آماده است

```bash
docker compose logs db --tail=20
```

### 5. اگر کانتینر مدام restart می‌شود، توقف و بررسی

```bash
# توقف همه کانتینرها
docker compose down

# بررسی فایل .env
cat .env

# راه‌اندازی مجدد و مشاهده لاگ‌های زنده
docker compose up
```

## مشکلات احتمالی

1. **مشکل در .env**: متغیرهای محیطی درست تنظیم نشده‌اند
2. **مشکل در اتصال به دیتابیس**: دیتابیس آماده نیست یا اطلاعات اشتباه است
3. **مشکل در entrypoint script**: خطا در اجرای script
4. **مشکل در collectstatic**: هنوز مشکل دسترسی وجود دارد

لطفاً خروجی `docker compose logs web --tail=100` را ارسال کنید.
