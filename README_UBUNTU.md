# AniStream - Ubuntu Deployment Guide

AniStream - Uzbekistan'dagi eng yaxshi anime streaming platformasi. Bu qo'llanmani o'zbekcha va ingilizcha.

## 🚀 Mahalliy Ubuntu Serverida O'rnatish

### 1. Sistem Zavisimliklarini O'rnatish

```bash
# Ubuntu paket menejerini yangilash
sudo apt-get update
sudo apt-get upgrade -y

# Python 3 va zarur kutubxonalarni o'rnatish
sudo apt-get install -y python3 python3-pip python3-venv python3-dev
sudo apt-get install -y postgresql postgresql-contrib
sudo apt-get install -y git wget curl
sudo apt-get install -y libpq-dev
```

### 2. PostgreSQL Database Tayyorlash

```bash
# PostgreSQL xizmatini ishga tushirish
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Postgres foydalanuvchiga o'tish
sudo -u postgres psql

# Database va foydalanuvchi yaratish
CREATE DATABASE bestmedia_db;
CREATE USER bestmedia_admin WITH PASSWORD 'your_secure_password';
ALTER ROLE bestmedia_admin SET client_encoding TO 'utf8';
ALTER ROLE bestmedia_admin SET default_transaction_isolation TO 'read committed';
ALTER ROLE bestmedia_admin SET default_transaction_deferrable TO on;
ALTER ROLE bestmedia_admin SET timezone TO 'Asia/Tashkent';
GRANT ALL PRIVILEGES ON DATABASE bestmedia_db TO bestmedia_admin;
\q
```

### 3. Loyihani Klonlash va Virtual Environment Yaratish

```bash
# Proyektni klonlash
cd /home/user
git clone https://github.com/yourusername/anistream.git
cd anistream

# Virtual environment yaratish
python3 -m venv venv
source venv/bin/activate

# Zavisimliklarni o'rnatish
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Django Sozlamalarini Tayyorlash

```bash
# .env faylini yaratish
cp .env.example .env

# .env faylini tahrirlash (nano yoki vi bilan)
nano .env
```

**Muhim sozlamalar:**

```env
# Development uchun:
ENVIRONMENT=development
DEBUG=True
SECRET_KEY=your-very-secure-key-change-this
ALLOWED_HOSTS=127.0.0.1,localhost,your-server-ip

# PostgreSQL (production uchun):
DB_NAME=bestmedia_db
DB_USER=bestmedia_admin
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432
```

### 5. Database Migratsiyalarini Qo'llash

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput
```

### 6. Superuser Yaratish

```bash
python manage.py createsuperuser
# Username, email va parolni kiriting
```

### 7. Mahalliy Testlash

```bash
python manage.py runserver 0.0.0.0:8000
```

Brauzerda `http://localhost:8000` yoki `http://your-server-ip:8000` ga kiring.

---

## 🚀 Production uchun Gunicorn + Nginx Sozlamalari

### 1. Gunicorn va Supervisor O'rnatish

```bash
pip install gunicorn
sudo apt-get install -y supervisor
```

### 2. Supervisor Konfiguratsiyasi

```bash
sudo nano /etc/supervisor/conf.d/anistream.conf
```

**Faylning tarkibi:**

```ini
[program:anistream]
command=/home/user/anistream/venv/bin/gunicorn src.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 60
directory=/home/user/anistream
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/anistream/gunicorn.log
```

### 3. Supervisor Ishga Tushirish

```bash
sudo mkdir -p /var/log/anistream
sudo chown www-data:www-data /var/log/anistream
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start anistream
```

### 4. Nginx Konfiguratsiyasi

```bash
sudo nano /etc/nginx/sites-available/anistream
```

**Faylning tarkibi:**

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    client_max_body_size 200M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /home/user/anistream/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /home/user/anistream/media/;
        expires 30d;
    }
}
```

### 5. Nginx Sozlamalarini Aktiva qilish

```bash
sudo ln -s /etc/nginx/sites-available/anistream /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 6. SSL Sertifikatini O'rnatish (Let's Encrypt)

```bash
sudo apt-get install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

---

## 🐳 Docker bilan Deployment

### 1. Dockerfile Yaratish

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "src.wsgi:application", "--bind", "0.0.0.0:8000"]
```

### 2. Docker-Compose

```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: bestmedia_db
      POSTGRES_USER: bestmedia_admin
      POSTGRES_PASSWORD: your_secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  web:
    build: .
    command: gunicorn src.wsgi:application --bind 0.0.0.0:8000
    ports:
      - "8000:8000"
    environment:
      ENVIRONMENT: production
      DEBUG: False
      DATABASE_URL: postgresql://bestmedia_admin:your_secure_password@db:5432/bestmedia_db
    depends_on:
      - db
    volumes:
      - .:/app

volumes:
  postgres_data:
```

**Docker bilan ishga tushirish:**

```bash
docker-compose up -d
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

---

## 🚀 Railway Deployment (Eng Tez Usuli)

### 1. Railway Account Yaratish

https://railway.app ga kiring va account yarating

### 2. Railway CLI O'rnatish

```bash
npm install -g @railway/cli
# yoki
curl -fsSL cli.new/railway | bash
```

### 3. Login qilish

```bash
railway login
```

### 4. Project Yaratish

```bash
cd /home/user/anistream
railway init
```

### 5. Environment Variables O'rnatish

Railway dashboard'dan:

```
SECRET_KEY = your-secure-key
ENVIRONMENT = production
DEBUG = False
ALLOWED_HOSTS = your-app.up.railway.app
```

### 6. Deploy qilish

```bash
railway up
```

**Yoki GitHub orqali:**

1. Loyihani GitHub'ga push qiling
2. Railway'da GitHub ulash
3. Auto-deploy aktivlash

---

## 📊 Database Backup va Restore

### PostgreSQL Backup

```bash
# Backup yaratish
pg_dump -U bestmedia_admin -h localhost bestmedia_db > backup_$(date +%Y%m%d).sql

# Backup o'rnatish
psql -U bestmedia_admin -h localhost bestmedia_db < backup_date.sql
```

### SQLite Backup (Development)

```bash
cp db.sqlite3 db.sqlite3.backup_$(date +%Y%m%d)
```

---

## 🛠️ Foydalı Buyruqlar

```bash
# Django shell
python manage.py shell

# Database reset (EHTIYOT!)
python manage.py flush

# Superuser parolini o'zgartirish
python manage.py changepassword admin

# Har bir login uchun sessiyani o'chirish
python manage.py clearsessions

# Static fayllarni qayta to'plash
python manage.py collectstatic --clear --noinput

# Migration statusini ko'rish
python manage.py showmigrations

# Specific migration yaratish
python manage.py makemigrations my_app
```

---

## 🐛 Muammolar va Echimi

### 1. PostgreSQL ulanish xatosi

```bash
# PostgreSQL xizmati ishlamaydimi?
sudo systemctl start postgresql
sudo systemctl status postgresql
```

### 2. Permission xatosi

```bash
# Django fayllari uchun ruxsat
sudo chown -R www-data:www-data /home/user/anistream/media
sudo chmod -R 755 /home/user/anistream/media
```

### 3. Static fayllar ko'rinmay qolyapdi

```bash
python manage.py collectstatic --clear --noinput
sudo systemctl restart nginx
```

### 4. 502 Bad Gateway (Nginx)

```bash
# Gunicorn xizmati ishlamaydimi?
sudo supervisorctl status anistream
sudo supervisorctl restart anistream

# Loglarni ko'rish
tail -f /var/log/anistream/gunicorn.log
sudo tail -f /var/log/nginx/error.log
```

---

## 📝 Security Best Practices

1. **SECRET_KEY ni o'zgartirish** - production'da yangi key yarating
2. **DEBUG = False** - production'da debug mode o'chiqlash
3. **ALLOWED_HOSTS ni to'g'ri qo'yish** - faqat har xil domenlarga ruxsat
4. **HTTPS** - SSL sertifikatini o'rnatish (Let's Encrypt)
5. **Firewall** - ufuqli portlarni yopish
6. **Regular Backups** - har kuni database backup qilish

---

## 📧 Support

Savollar uchun: support@anistream.uz

**Happy Streaming! 🎬**

