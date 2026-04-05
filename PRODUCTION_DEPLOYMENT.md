# AniStream - Production Deployment Guide

Bu qo'llanma loyihani production'da ishga tushirish uchun to'liq ko'rsatmalar beradi.

## 🎯 Deployment Variantlari

### 1️⃣ Railway (Tavsiya - Eng Tez)

Railway - Eng oson va tezkor deployment usuli.

#### Step 1: GitHub Repository Tayyorlash

```bash
# Windows'da:
github_push.bat

# Linux/Mac'da:
chmod +x github_push.sh
./github_push.sh
```

#### Step 2: Railway'da Project Yaratish

1. https://railway.app ga kiring
2. "New Project" ni bosing
3. "Deploy from GitHub" ni tanlang
4. Repository'ni authorize qiling

#### Step 3: Environment Variables Qo'shish

Railway Console'da:

```
SECRET_KEY = (generate-qiling)
ENVIRONMENT = production
DEBUG = False
ALLOWED_HOSTS = your-app.railway.app
CSRF_TRUSTED_ORIGINS = https://your-app.railway.app
USE_HTTPS = true
```

#### Step 4: PostgreSQL Plugin Qo'shish

1. Railway projectda "Add" bosing
2. "PostgreSQL" tanlang
3. Avtomatik DATABASE_URL beriladi

#### Step 5: Deploy

Railway avtomatik deploy qiladi GitHub'ga push qildingiz bilan.

```
Status: https://your-app.railway.app
Admin: https://your-app.railway.app/admin
```

**Foydalanuvchi:**
- Username: admin
- Password: Railway Console'da set qiling

---

### 2️⃣ Ubuntu Server (Manual - Batafsil)

Kendi serveringizda deploy qilish.

#### Prerequisites
- Ubuntu 20.04 yoki yangroq
- SSH access
- Domain name (optional)
- SSL certificate (optional)

#### Step 1: Sistem Tayyorlash

```bash
# SSH'ga ulanish
ssh user@your-server-ip

# System update
sudo apt-get update
sudo apt-get upgrade -y

# Dependencies
sudo apt-get install -y python3 python3-pip python3-venv
sudo apt-get install -y postgresql postgresql-contrib
sudo apt-get install -y nginx supervisor git
```

#### Step 2: PostgreSQL Database

```bash
# PostgreSQL'ni start qilish
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Database yaratish
sudo -u postgres psql

# SQL commands:
CREATE DATABASE bestmedia_db;
CREATE USER bestmedia_admin WITH PASSWORD 'strong_password_here';
ALTER ROLE bestmedia_admin SET client_encoding TO 'utf8';
ALTER ROLE bestmedia_admin SET default_transaction_isolation TO 'read committed';
ALTER ROLE bestmedia_admin SET timezone TO 'Asia/Tashkent';
GRANT ALL PRIVILEGES ON DATABASE bestmedia_db TO bestmedia_admin;
\q
```

#### Step 3: Project Setup

```bash
# Project klonlash
cd /home/user
git clone https://github.com/yourusername/anistream.git
cd anistream

# Virtual environment
python3 -m venv venv
source venv/bin/activate

# Dependencies
pip install -r requirements.txt
```

#### Step 4: .env Configuration

```bash
nano .env
```

```env
ENVIRONMENT=production
DEBUG=False
SECRET_KEY=your-generated-key
ALLOWED_HOSTS=your-domain.com,www.your-domain.com,server-ip
CSRF_TRUSTED_ORIGINS=https://your-domain.com

DB_ENGINE=django.db.backends.postgresql
DB_NAME=bestmedia_db
DB_USER=bestmedia_admin
DB_PASSWORD=strong_password_here
DB_HOST=localhost
DB_PORT=5432

USE_HTTPS=true
```

#### Step 5: Django Setup

```bash
# Migrations
python manage.py migrate

# Static files
python manage.py collectstatic --noinput

# Superuser
python manage.py createsuperuser
```

#### Step 6: Gunicorn Setup

```bash
# supervisor config copy
sudo cp supervisor_anistream.conf /etc/supervisor/conf.d/

# Permissions
sudo chown -R www-data:www-data /home/user/anistream/media

# Supervisor enable
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start anistream
```

#### Step 7: Nginx Setup

```bash
# Nginx config copy
sudo cp nginx_config.conf /etc/nginx/sites-available/anistream

# Enable
sudo ln -s /etc/nginx/sites-available/anistream /etc/nginx/sites-enabled/

# Test va restart
sudo nginx -t
sudo systemctl restart nginx
```

#### Step 8: SSL Certificate (Let's Encrypt)

```bash
# Certbot o'rnatish
sudo apt-get install -y certbot python3-certbot-nginx

# Certificate yaratish
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Auto-renew
sudo systemctl enable certbot.timer
```

#### Step 9: Monitoring

```bash
# Gunicorn status
sudo supervisorctl status anistream

# Logs
tail -f /var/log/anistream/gunicorn.log
sudo tail -f /var/log/nginx/error.log

# Restart (agar kerak bo'lsa)
sudo supervisorctl restart anistream
```

---

### 3️⃣ Docker (Container - Production Ready)

Docker bilan containerized deployment.

#### Step 1: Docker O'rnatish

```bash
# Ubuntu'da
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Docker-compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### Step 2: .env File

```bash
cp .env.example .env
nano .env
```

```env
# Database
DB_NAME=bestmedia_db
DB_USER=bestmedia_admin
DB_PASSWORD=secure_password_123

# Django
ENVIRONMENT=production
DEBUG=False
SECRET_KEY=your-secure-key
```

#### Step 3: Build va Start

```bash
# Build
docker-compose build

# Start
docker-compose up -d

# Logs
docker-compose logs -f web

# Stop
docker-compose down
```

#### Step 4: Status

```bash
# Check containers
docker ps

# Database connection
docker-compose exec web python manage.py migrate

# Admin access
http://your-server-ip
```

---

## 🔐 Security Best Practices

### 1. SECRET_KEY Generate Qilish

```bash
python manage.py shell -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 2. Passwords

- Kompleks password ishlating (min 16 characters)
- Hamma muhim password'larni boshqalash uchun saqlab qo'ying
- Regular rotate qiling

### 3. Firewall

```bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 4. Backups

```bash
# PostgreSQL backup
pg_dump -U bestmedia_admin -h localhost bestmedia_db > backup_$(date +%Y%m%d).sql

# Restore
psql -U bestmedia_admin -h localhost bestmedia_db < backup_date.sql

# Media files backup
tar -czf media_backup_$(date +%Y%m%d).tar.gz media/
```

### 5. Monitoring

- Error logs monitoring
- Server resources (CPU, RAM, Disk)
- Database performance
- Regular security audits

---

## ✅ Post-Deployment Checklist

- [ ] Website accessible
- [ ] Admin panel working
- [ ] Static files loading
- [ ] Database connected
- [ ] SSL certificate valid (HTTPS)
- [ ] Email notifications working
- [ ] Backups scheduled
- [ ] Logs rotating
- [ ] Monitoring active
- [ ] DNS configured

---

## 🆘 Troubleshooting

### 502 Bad Gateway

```bash
# Ubuntu'da
sudo supervisorctl restart anistream
sudo systemctl restart nginx

# Docker'da
docker-compose restart web nginx
```

### Static Files Not Loading

```bash
# Ubuntu'da
python manage.py collectstatic --clear --noinput
sudo systemctl restart nginx

# Docker'da
docker-compose exec web python manage.py collectstatic --noinput
```

### Database Connection Error

```bash
# Test connection
psql -U bestmedia_admin -h localhost -d bestmedia_db

# Django shell
python manage.py shell -c "from django.db import connection; print(connection.ensure_connection())"
```

---

## 📞 Support

- Railway Support: https://railway.app/support
- Django Issues: https://github.com/django/django/issues
- Ubuntu Help: https://help.ubuntu.com/

---

**Happy Deployment! 🚀**

