# دیباگ Entrypoint Script

## بررسی لاگ‌ها

لطفاً این دستورات را اجرا کنید و خروجی را ارسال کنید:

```bash
# بررسی لاگ‌های کانتینر web
docker compose logs web --tail=100

# بررسی وضعیت دقیق
docker compose ps -a web

# بررسی اینکه آیا کانتینر crash می‌کند
docker inspect gps-web-1 | grep -A 10 State
```

## مشکلات احتمالی

1. **خطا در entrypoint script**: ممکن است syntax error یا خطای دیگری وجود داشته باشد
2. **مشکل در دستور su**: ممکن است هنوز arguments به درستی پاس نشوند
3. **مشکل در gunicorn**: ممکن است gunicorn نتواند راه‌اندازی شود

لطفاً خروجی `docker compose logs web --tail=100` را ارسال کنید.
