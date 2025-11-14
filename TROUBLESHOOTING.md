# راهنمای رفع مشکلات دیپلوی

## مشکل: کانتینر در حال Restart است

اگر کانتینر `web` مدام restart می‌شود، مراحل زیر را انجام دهید:

### مرحله 1: بررسی لاگ‌های کانتینر

```bash
# مشاهده لاگ‌های کانتینر web
docker compose logs web

# یا برای مشاهده لاگ‌های زنده
docker compose logs -f web

# مشاهده آخرین خطوط لاگ
docker compose logs --tail=100 web
```

### مرحله 2: بررسی وضعیت کانتینرها

```bash
# بررسی وضعیت همه کانتینرها
docker compose ps -a

# بررسی جزئیات کانتینر
docker inspect <container_id>
```

### مرحله 3: بررسی فایل .env

مطمئن شوید که فایل `.env` وجود دارد و تمام متغیرهای ضروری را دارد:

```bash
# بررسی وجود فایل .env
ls -la .env

# مشاهده محتوای .env (بدون نمایش رمزها)
cat .env | grep -v PASSWORD
```

**متغیرهای ضروری:**
- `SECRET_KEY` - باید مقدار داشته باشد
- `DEBUG=False`
- `ALLOWED_HOSTS=91.107.169.72,localhost,127.0.0.1`
- `DATABASE_ENGINE=django.db.backends.postgresql`
- `DATABASE_NAME` - باید مقدار داشته باشد
- `DATABASE_USER` - باید مقدار داشته باشد
- `DATABASE_PASSWORD` - باید مقدار داشته باشد

### مرحله 4: بررسی اتصال به دیتابیس

```bash
# بررسی اینکه کانتینر db در حال اجرا است
docker compose ps db

# بررسی لاگ دیتابیس
docker compose logs db

# تست اتصال به دیتابیس از داخل کانتینر web
docker compose exec web python -c "import psycopg2; psycopg2.connect(host='db', database='gpsstore_db', user='gpsstore_user', password='YOUR_PASSWORD')"
```

### مرحله 5: اجرای دستی کانتینر برای دیباگ

```bash
# توقف کانتینرها
docker compose down

# اجرای کانتینر web به صورت interactive
docker compose run --rm web bash

# در داخل کانتینر:
python manage.py check
python manage.py migrate --dry-run
```

### مرحله 6: بررسی Dockerfile

مطمئن شوید که Dockerfile درست است:

```bash
# تست build
docker compose build web

# مشاهده خروجی build
docker compose build --no-cache web
```

### مرحله 7: بررسی دسترسی‌های فایل

```bash
# بررسی دسترسی‌های دایرکتوری‌ها
ls -la media/
ls -la staticfiles/
ls -la logs/

# اگر دسترسی ندارند:
mkdir -p media staticfiles logs
chmod 755 media staticfiles logs
```

---

## مشکلات رایج و راه حل‌ها

### مشکل 1: خطای "Container is restarting"

**علت:** معمولاً به خاطر خطا در اجرای application است.

**راه حل:**
```bash
# 1. بررسی لاگ‌ها
docker compose logs web

# 2. بررسی .env
cat .env

# 3. توقف و راه‌اندازی مجدد
docker compose down
docker compose up -d --build

# 4. اگر مشکل حل نشد، کانتینر را بدون restart اجرا کنید
docker compose up web
```

### مشکل 2: خطای اتصال به دیتابیس

**علت:** دیتابیس آماده نیست یا اطلاعات اتصال اشتباه است.

**راه حل:**
```bash
# 1. صبر کنید تا دیتابیس آماده شود
docker compose logs db

# 2. بررسی متغیرهای دیتابیس در .env
grep DATABASE .env

# 3. تست اتصال
docker compose exec db psql -U gpsstore_user -d gpsstore_db -c "SELECT 1;"
```

### مشکل 3: خطای "ModuleNotFoundError"

**علت:** پکیج‌های Python نصب نشده‌اند.

**راه حل:**
```bash
# rebuild کانتینر
docker compose build --no-cache web
docker compose up -d
```

### مشکل 4: خطای "Permission denied"

**علت:** مشکل دسترسی به فایل‌ها یا دایرکتوری‌ها.

**راه حل:**
```bash
# تنظیم دسترسی‌ها
sudo chown -R $USER:$USER .
chmod -R 755 media staticfiles logs
```

### مشکل 5: خطای "Port already in use"

**علت:** پورت 80 یا 443 قبلاً استفاده می‌شود.

**راه حل:**
```bash
# بررسی استفاده از پورت
sudo lsof -i :80
sudo lsof -i :443

# متوقف کردن nginx سیستم عامل
sudo systemctl stop nginx
sudo systemctl disable nginx

# یا تغییر پورت در docker-compose.yml
```

---

## دستورات مفید برای دیباگ

```bash
# مشاهده لاگ‌های همه سرویس‌ها
docker compose logs

# مشاهده لاگ‌های زنده
docker compose logs -f

# اجرای دستور در کانتینر
docker compose exec web python manage.py shell
docker compose exec web python manage.py check

# بررسی متغیرهای محیطی در کانتینر
docker compose exec web env

# بررسی فایل‌های داخل کانتینر
docker compose exec web ls -la /app

# دسترسی به shell کانتینر
docker compose exec web bash

# مشاهده استفاده از منابع
docker stats

# پاک کردن کانتینرها و volume‌ها
docker compose down -v

# ساخت مجدد از صفر
docker compose down -v
docker compose build --no-cache
docker compose up -d
```

---

## بررسی سلامت سیستم

```bash
# بررسی وضعیت Docker
docker info
docker version

# بررسی فضای دیسک
df -h

# بررسی استفاده از حافظه
free -h

# بررسی لاگ‌های سیستم
journalctl -u docker -n 50
```

---

## درخواست کمک

اگر مشکل حل نشد، این اطلاعات را جمع‌آوری کنید:

```bash
# 1. لاگ‌های کانتینر web
docker compose logs web > web_logs.txt

# 2. وضعیت کانتینرها
docker compose ps -a > containers_status.txt

# 3. محتوای .env (بدون رمزها)
cat .env | grep -v PASSWORD > env_vars.txt

# 4. خروجی docker info
docker info > docker_info.txt
```

سپس این فایل‌ها را برای بررسی ارسال کنید.

