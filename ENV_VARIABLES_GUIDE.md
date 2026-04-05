# AniStream Environment Variables Guide

Bu dokumentda barcha environment variables va ularning ma'nolari yozilgan.

## 🎯 Development vs Production

### Development (.env)
```env
ENVIRONMENT=development
DEBUG=True
SECRET_KEY=django-insecure-not-for-production
```

### Production
```env
ENVIRONMENT=production
DEBUG=False
SECRET_KEY=generate-strong-key
```

---

## 📋 Barcha Environment Variables

### Django Asosiy Sozlamalar

#### `SECRET_KEY`
- **Tavsif:** Django SECRET_KEY - xavfsizlik kaliti
- **Development:** `django-insecure-any-value` (test uchun)
- **Production:** Strong random key
- **Generate qilish:**
```bash
python manage.py shell -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

#### `DEBUG`
- **Tavsif:** Debug mode
- **Development:** `True`
- **Production:** `False` (MUHIM!)
- **Qiymatlar:** `True`, `False`

#### `ENVIRONMENT`
- **Tavsif:** Ishchi muhiti
- **Development:** `development`
- **Production:** `production`
- **Effects:** Database, Security headers, Logging

#### `ALLOWED_HOSTS`
- **Tavsif:** Qabul qilinadigan domain/IP manzillari
- **Format:** Vergul bilan ajratilgan: `127.0.0.1,localhost,example.com`
- **Development:** `127.0.0.1,localhost`
- **Production:** `your-domain.com,www.your-domain.com`

#### `CSRF_TRUSTED_ORIGINS`
- **Tavsif:** CSRF protection uchun ishonilgan origins
- **Format:** `http://example.com,https://example.com`
- **Development:** `http://127.0.0.1,http://localhost`
- **Production:** `https://your-domain.com`

#### `USE_HTTPS`
- **Tavsif:** HTTPS protocol'ni majburi qilish
- **Development:** `False`
- **Production:** `True`

#### `DJANGO_LOG_LEVEL`
- **Tavsif:** Logging darajasi
- **Qiymatlar:** `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
- **Tavsiya:** `INFO` (production)

---

## 🗄️ Database Sozlamalari

### Option 1: DATABASE_URL (Tavsiya - Railway uchun)
```env
DATABASE_URL=postgresql://user:password@host:5432/dbname
```

### Option 2: Individual Settings

#### `DB_ENGINE`
- **Tavsif:** Database engine
- **Qiymatlar:** `postgresql`, `sqlite3`
- **Default:** `sqlite3` (development)

#### `DB_NAME`
- **Tavsif:** Database nomi
- **Development:** `db.sqlite3` (SQLite) yoki `bestmedia_db`
- **Production:** PostgreSQL database nomi

#### `DB_USER`
- **Tavsif:** Database foydalanuvchi
- **Default:** `postgres`
- **Production:** Xavfsiz foydalanuvchi nomi

#### `DB_PASSWORD`
- **Tavsif:** Database parol
- **Development:** Ko'rsatmay qo'y
- **Production:** Xavfsiz, murakkab parol

#### `DB_HOST`
- **Tavsif:** Database server manzili
- **Development:** `localhost` yoki `127.0.0.1`
- **Production:** PostgreSQL server IP/domain
- **Docker:** `db` (service nomi)

#### `DB_PORT`
- **Tavsif:** Database port
- **Default:** `5432` (PostgreSQL)
- **SQLite:** Kerak emas

---

## 🌐 Media va Storage Sozlamalari

### Cloudinary (Optional)

#### `USE_CLOUDINARY`
- **Tavsif:** Cloudinary storage'ni ishlatish
- **Qiymatlar:** `True`, `False`
- **Default:** `False`

#### `CLOUDINARY_CLOUD_NAME`
- **Tavsif:** Cloudinary cloud nomi
- **Format:** `your-cloud-name`
- **Olib olish:** https://cloudinary.com/console

#### `CLOUDINARY_API_KEY`
- **Tavsif:** Cloudinary API key
- **Olib olish:** https://cloudinary.com/console/settings

#### `CLOUDINARY_API_SECRET`
- **Tavsif:** Cloudinary API secret
- **EHTIYOT:** Maxfiy saqlang!

---

## 🔐 Security Sozlamalari

### `SESSION_COOKIE_SECURE`
- **Tavsif:** Faqat HTTPS orqali cookie yuborish
- **Development:** `False`
- **Production:** `True` (HTTPS kerak)

### `CSRF_COOKIE_SECURE`
- **Tavsif:** CSRF cookie'sini faqat HTTPS orqali yuborish
- **Development:** `False`
- **Production:** `True`

### `SECURE_SSL_REDIRECT`
- **Tavsif:** Barcha HTTP requestni HTTPS'ga redirect qilish
- **Development:** `False`
- **Production:** `True` (SSL sertifikat kerak)

### `SECURE_HSTS_SECONDS`
- **Tavsif:** HSTS header'da max-age qiymati
- **Production:** `31536000` (1 yil)

### `SECURE_HSTS_INCLUDE_SUBDOMAINS`
- **Tavsif:** HSTS'ni subdomainlar uchun qo'llash
- **Production:** `True`

### `X_FRAME_OPTIONS`
- **Tavsif:** Clickjacking protection
- **Qiymatlar:** `DENY`, `SAMEORIGIN`, `ALLOW-FROM`
- **Default:** `DENY` (hamma joydan embed qilish mumkin emas)

---

## 📧 Email Sozlamalari (Optional)

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@anistream.uz
```

---

## 🚀 Railway Specific Variables

Railway avtomatik qo'yadi (kerak emas):
- `DATABASE_URL` - PostgreSQL connection string
- `PORT` - Application port

Siz qo'shishingiz kerak:
```env
SECRET_KEY=your-secure-key
ENVIRONMENT=production
DEBUG=False
ALLOWED_HOSTS=your-app.railway.app,anistream.uz
CSRF_TRUSTED_ORIGINS=https://your-app.railway.app,https://anistream.uz
USE_HTTPS=true
```

---

## 🐳 Docker Environment

`docker-compose.yml` yoki `.env` faylida:

```env
# Database
POSTGRES_DB=bestmedia_db
POSTGRES_USER=bestmedia_admin
POSTGRES_PASSWORD=secure_password_123

# Django
ENVIRONMENT=development
DEBUG=False
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=127.0.0.1,localhost,anistream.local
DB_HOST=db
DB_PORT=5432
DB_NAME=bestmedia_db
DB_USER=bestmedia_admin
DB_PASSWORD=secure_password_123
```

---

## 📝 .env File Misol

### Development uchun:

```env
# Django
SECRET_KEY=django-insecure-dev-key-not-for-production
DEBUG=True
ENVIRONMENT=development
ALLOWED_HOSTS=127.0.0.1,localhost,*.local
CSRF_TRUSTED_ORIGINS=http://127.0.0.1,http://localhost

# Database
DB_ENGINE=sqlite3
DB_NAME=db.sqlite3

# Security (development'da False)
USE_HTTPS=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False

# Logging
DJANGO_LOG_LEVEL=DEBUG

# Email (optional)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

### Production uchun:

```env
# Django
SECRET_KEY=your-super-secure-random-key-generated
DEBUG=False
ENVIRONMENT=production
ALLOWED_HOSTS=anistream.uz,www.anistream.uz
CSRF_TRUSTED_ORIGINS=https://anistream.uz,https://www.anistream.uz

# Database
DATABASE_URL=postgresql://bestmedia:password@prod-db.example.com:5432/bestmedia_db

# Security (MUHIM!)
USE_HTTPS=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_SSL_REDIRECT=True

# Logging
DJANGO_LOG_LEVEL=INFO

# Email (production)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=alerts@anistream.uz
EMAIL_HOST_PASSWORD=app-specific-password
```

---

## ✅ Sozlamalarni Tekshirish

```bash
# Django settings'ni debug qilish
python manage.py shell

# Settings ichida
from django.conf import settings
print(settings.DEBUG)
print(settings.ALLOWED_HOSTS)
print(settings.DATABASES)
```

---

## 🔧 Troubleshooting

### "Disallowed host" error
```
ImproperlyConfigured: The ALLOWED_HOSTS setting must be a list or tuple.
```
**Echimi:** `ALLOWED_HOSTS` to'g'ri format'da bo'lsin (vergul bilan ajratilgan)

### "CSRF token missing" error
```
Reason given for failure: CSRF cookie not set.
```
**Echimi:** 
1. `CSRF_TRUSTED_ORIGINS` to'g'ri bo'lsin
2. Domain bilan `www` yoki `www.` bo'lmagan versiyalar saytladi?

### "Database connection refused"
```
could not translate host name "postgres.railway.internal" to address
```
**Echimi:**
- DATABASE_URL to'g'ri bo'lsin
- Database service ishlamaydimi? Tekshiring
- Host nomi to'g'ri bo'lsin

---

## 📚 Reference Links

- Django Settings: https://docs.djangoproject.com/en/stable/ref/settings/
- Environment Variables: https://12factor.net/config
- Cloudinary: https://cloudinary.com/documentation
- Railway Docs: https://docs.railway.app/

---

**Last Updated:** 2026-04-05

