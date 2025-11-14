# دستورات سریع دیپلوی

این فایل شامل دستورات سریع برای دیپلوی پروژه است.

## در سرور Ubuntu 22

### 1. راه‌اندازی اولیه سرور (یک بار)

```bash
# اتصال به سرور
ssh root@91.107.169.72

# اجرای اسکریپت راه‌اندازی
chmod +x scripts/server_setup.sh
sudo bash scripts/server_setup.sh
```

### 2. آپلود پروژه

```bash
# در سرور
cd ~
git clone YOUR_REPO_URL GpsStore
cd GpsStore

# یا از کامپیوتر محلی با SCP
scp -r . root@91.107.169.72:/root/GpsStore
```

### 3. تنظیم .env

```bash
cd ~/GpsStore
cp env.example .env
nano .env
# مقادیر را تنظیم کنید و ذخیره کنید (Ctrl+O, Enter, Ctrl+X)
```

### 4. دیپلوی

```bash
cd ~/GpsStore
docker compose up -d --build
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py collectstatic --noinput
```

### 5. بررسی

```bash
# بررسی وضعیت
docker compose ps

# تست سلامت
curl http://localhost/health/

# مشاهده لاگ‌ها
docker compose logs -f
```

## دستورات مفید

### راه‌اندازی مجدد
```bash
docker compose restart
```

### توقف
```bash
docker compose down
```

### به‌روزرسانی
```bash
git pull
docker compose up -d --build
docker compose exec web python manage.py migrate
docker compose exec web python manage.py collectstatic --noinput
docker compose restart
```

### پشتیبان‌گیری دیتابیس
```bash
docker compose exec db pg_dump -U gpsstore_user gpsstore_db > backup_$(date +%Y%m%d).sql
```

### مشاهده لاگ‌ها
```bash
docker compose logs -f web
docker compose logs -f nginx
docker compose logs -f db
```

