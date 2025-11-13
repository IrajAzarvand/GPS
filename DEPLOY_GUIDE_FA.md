# راهنمای کامل دیپلوی پروژه GpsStore روی سرور Ubuntu 22

این راهنما به شما کمک می‌کند تا پروژه GpsStore را روی سرور مجازی Ubuntu 22 با IP `91.107.169.72` دیپلوی کنید.

## پیش‌نیازها

- سرور Ubuntu 22.04
- دسترسی root یا sudo
- اتصال به اینترنت

---

## مرحله 1: اتصال به سرور

ابتدا باید به سرور خود متصل شوید. در ترمینال ویندوز خود (PowerShell یا CMD) دستور زیر را اجرا کنید:

```bash
ssh root@91.107.169.72
```

یا اگر کاربر دیگری دارید:

```bash
ssh username@91.107.169.72
```

**نکته:** اگر اولین بار است که به سرور متصل می‌شوید، ممکن است از شما تأیید بخواهد. `yes` را تایپ کنید.

---

## مرحله 2: به‌روزرسانی سیستم

پس از اتصال به سرور، دستورات زیر را به ترتیب اجرا کنید:

```bash
# به‌روزرسانی لیست پکیج‌ها
sudo apt update

# به‌روزرسانی سیستم
sudo apt upgrade -y

# نصب پکیج‌های ضروری
sudo apt install -y curl wget git vim ufw
```

---

## مرحله 3: نصب Docker و Docker Compose

### نصب Docker:

```bash
# حذف نسخه‌های قدیمی (اگر وجود دارد)
sudo apt remove -y docker docker-engine docker.io containerd runc

# نصب dependencies
sudo apt install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# اضافه کردن GPG key رسمی Docker
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# اضافه کردن repository Docker
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# نصب Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# اضافه کردن کاربر فعلی به گروه docker (برای اجرای بدون sudo)
sudo usermod -aG docker $USER

# راه‌اندازی Docker
sudo systemctl enable docker
sudo systemctl start docker

# بررسی نصب Docker
docker --version
```

### نصب Docker Compose (اگر به صورت جداگانه نیاز دارید):

```bash
# Docker Compose معمولاً با docker-compose-plugin نصب می‌شود
# اما اگر نیاز به نسخه قدیمی دارید:
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
docker-compose --version
```

**نکته مهم:** پس از اضافه کردن کاربر به گروه docker، باید از سرور خارج شوید و دوباره وارد شوید تا تغییرات اعمال شود:

```bash
exit
# سپس دوباره ssh کنید
ssh root@91.107.169.72
```

---

## مرحله 4: تنظیم فایروال (UFW)

```bash
# فعال‌سازی UFW
sudo ufw enable

# باز کردن پورت SSH (خیلی مهم!)
sudo ufw allow 22/tcp

# باز کردن پورت HTTP
sudo ufw allow 80/tcp

# باز کردن پورت HTTPS (برای آینده)
sudo ufw allow 443/tcp

# بررسی وضعیت فایروال
sudo ufw status
```

---

## مرحله 5: آپلود پروژه به سرور

### روش 1: استفاده از Git (توصیه می‌شود)

اگر پروژه شما در Git است:

```bash
# رفتن به دایرکتوری home
cd ~

# کلون کردن پروژه (آدرس repository خود را جایگزین کنید)
git clone https://github.com/yourusername/GpsStore.git
# یا اگر private است:
# git clone https://username:token@github.com/yourusername/GpsStore.git

cd GpsStore
```

### روش 2: استفاده از SCP (از کامپیوتر محلی)

در ترمینال ویندوز خود (PowerShell)، در مسیر پروژه GpsStore:

```bash
# آپلود کل پروژه
scp -r . root@91.107.169.72:/root/GpsStore

# سپس در سرور:
cd /root/GpsStore
```

### روش 3: استفاده از rsync (بهتر برای آپدیت‌های بعدی)

```bash
# از کامپیوتر محلی
rsync -avz --exclude '__pycache__' --exclude '*.pyc' --exclude '.git' . root@91.107.169.72:/root/GpsStore
```

---

## مرحله 6: تنظیم فایل .env

```bash
# رفتن به دایرکتوری پروژه
cd ~/GpsStore
# یا
cd /root/GpsStore

# کپی کردن فایل نمونه
cp env.example .env

# ویرایش فایل .env
nano .env
```

در فایل `.env` باید مقادیر زیر را تنظیم کنید:

```env
# Django Settings
SECRET_KEY=یک-کلید-تصادفی-و-قوی-اینجا-بگذارید
DEBUG=False
ALLOWED_HOSTS=91.107.169.72,localhost,127.0.0.1
ENVIRONMENT=production

# Database Configuration
DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_NAME=gpsstore_db
DATABASE_USER=gpsstore_user
DATABASE_PASSWORD=یک-رمز-قوی-برای-دیتابیس
DATABASE_HOST=db
DATABASE_PORT=5432

# CORS Settings
CORS_ALLOWED_ORIGINS=http://91.107.169.72

# Email Configuration (اختیاری - می‌توانید بعداً تنظیم کنید)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-email-password
DEFAULT_FROM_EMAIL=noreply@gpsstore.com

# Security Settings
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
```

**برای تولید SECRET_KEY:**

```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

یا می‌توانید از یک سایت آنلاین استفاده کنید.

**نحوه ذخیره در nano:**
- `Ctrl + O` برای ذخیره
- `Enter` برای تأیید
- `Ctrl + X` برای خروج

---

## مرحله 7: ساخت و راه‌اندازی پروژه با Docker

```bash
# اطمینان از اینکه در دایرکتوری پروژه هستید
cd ~/GpsStore

# ساخت و راه‌اندازی کانتینرها
docker compose up -d --build

# بررسی وضعیت کانتینرها
docker compose ps

# مشاهده لاگ‌ها (برای بررسی مشکلات)
docker compose logs -f
```

**اگر مشکلی پیش آمد، می‌توانید لاگ‌های هر سرویس را جداگانه ببینید:**

```bash
docker compose logs web
docker compose logs db
docker compose logs nginx
```

---

## مرحله 8: اجرای Migration‌های دیتابیس

```bash
# اجرای migration‌ها
docker compose exec web python manage.py migrate

# ایجاد superuser (مدیر سایت)
docker compose exec web python manage.py createsuperuser

# جمع‌آوری فایل‌های استاتیک
docker compose exec web python manage.py collectstatic --noinput
```

---

## مرحله 9: بررسی وضعیت سرویس‌ها

```bash
# بررسی وضعیت کانتینرها
docker compose ps

# بررسی سلامت اپلیکیشن
curl http://localhost/health/

# یا از خارج سرور
curl http://91.107.169.72/health/
```

---

## مرحله 10: تست دسترسی به سایت

در مرورگر خود، آدرس زیر را باز کنید:

```
http://91.107.169.72
```

باید صفحه اصلی سایت را ببینید.

برای دسترسی به پنل ادمین:

```
http://91.107.169.72/admin/
```

---

## دستورات مفید برای مدیریت

### مشاهده لاگ‌ها:
```bash
# لاگ همه سرویس‌ها
docker compose logs -f

# لاگ سرویس خاص
docker compose logs -f web
docker compose logs -f nginx
```

### راه‌اندازی مجدد سرویس‌ها:
```bash
docker compose restart
# یا برای سرویس خاص
docker compose restart web
```

### توقف سرویس‌ها:
```bash
docker compose down
```

### راه‌اندازی مجدد:
```bash
docker compose up -d
```

### به‌روزرسانی پروژه:
```bash
# اگر از Git استفاده می‌کنید
git pull origin main
docker compose up -d --build
docker compose exec web python manage.py migrate
docker compose exec web python manage.py collectstatic --noinput
docker compose restart
```

### پشتیبان‌گیری از دیتابیس:
```bash
docker compose exec db pg_dump -U gpsstore_user gpsstore_db > backup_$(date +%Y%m%d_%H%M%S).sql
```

### بازگردانی دیتابیس:
```bash
docker compose exec -T db psql -U gpsstore_user gpsstore_db < backup_file.sql
```

---

## رفع مشکلات رایج

### مشکل 1: پورت 80 در حال استفاده است

```bash
# بررسی چه چیزی از پورت 80 استفاده می‌کند
sudo lsof -i :80
# یا
sudo netstat -tulpn | grep :80

# اگر nginx سیستم عامل استفاده می‌کند، آن را متوقف کنید:
sudo systemctl stop nginx
sudo systemctl disable nginx
```

### مشکل 2: کانتینرها راه‌اندازی نمی‌شوند

```bash
# بررسی لاگ‌ها
docker compose logs

# بررسی وضعیت
docker compose ps -a

# حذف و ساخت مجدد
docker compose down -v
docker compose up -d --build
```

### مشکل 3: خطای اتصال به دیتابیس

```bash
# بررسی اینکه کانتینر db در حال اجرا است
docker compose ps

# بررسی لاگ دیتابیس
docker compose logs db

# راه‌اندازی مجدد دیتابیس
docker compose restart db
```

### مشکل 4: فایل‌های استاتیک نمایش داده نمی‌شوند

```bash
# جمع‌آوری مجدد فایل‌های استاتیک
docker compose exec web python manage.py collectstatic --noinput

# بررسی دسترسی‌ها
docker compose exec web ls -la /app/staticfiles
```

---

## تنظیم SSL (HTTPS) - اختیاری

اگر می‌خواهید از HTTPS استفاده کنید، می‌توانید از Let's Encrypt استفاده کنید:

```bash
# نصب Certbot
sudo apt install -y certbot python3-certbot-nginx

# دریافت گواهینامه (اگر دامنه دارید)
sudo certbot --nginx -d yourdomain.com

# یا برای IP address، باید از روش‌های دیگر استفاده کنید
```

---

## نکات امنیتی

1. **همیشه SECRET_KEY قوی استفاده کنید**
2. **رمز دیتابیس را قوی انتخاب کنید**
3. **فایروال را فعال نگه دارید**
4. **به‌روزرسانی‌های امنیتی را نصب کنید**
5. **از SSH key به جای password استفاده کنید** (توصیه می‌شود)

---

## پشتیبانی

اگر مشکلی پیش آمد، لاگ‌ها را بررسی کنید:

```bash
# لاگ Django
docker compose exec web tail -f /app/logs/django.log

# لاگ Nginx
docker compose logs nginx

# لاگ Gunicorn
docker compose exec web tail -f /app/logs/gunicorn_error.log
```

---

**موفق باشید! 🚀**

