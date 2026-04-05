# 🎬 AniStream - QUICK START GUIDE

Loyiha 100% tayyorlandi. Siz quyidagi qadamlarni takip qiling:

---

## 🚀 DEPLOYMENT - 3 OPTIONS

### OPTION 1: Railway (⭐ TAVSIYA - Fastest)

**Time:** 5-10 minut | **Cost:** Free tier mavjud | **Setup:** Easiest

```bash
# Step 1: GitHub'ga push qiling
github_push.bat        # Windows
# yoki
./github_push.sh       # Linux/Mac

# Step 2: Railway.app'ga kiring
# 1. https://railway.app
# 2. Login/Sign up
# 3. "New Project" → "Deploy from GitHub"
# 4. Repo tanlang va authorize qiling

# Step 3: PostgreSQL qo'shish
# Railway console'da:
# Add → PostgreSQL → Select
# DATABASE_URL avtomatik beriladi

# Step 4: Environment Variables qo'shish
# Railway console'da Variables:
# - SECRET_KEY: generate-new-secure-key
# - ENVIRONMENT: production
# - DEBUG: False
# - ALLOWED_HOSTS: your-app.railway.app
# - CSRF_TRUSTED_ORIGINS: https://your-app.railway.app

# Step 5: Deploy
# Auto-deploy! GitHub push qilingiz bilan deploy bo'ladi

# RESULT: https://your-app.railway.app
```

---

### OPTION 2: Ubuntu Server (Full Control)

**Time:** 30-60 minut | **Cost:** $5-10/month | **Setup:** Medium

```bash
# Step 1: SSH'ga ulanish
ssh user@your-server-ip

# Step 2: Auto-setup
chmod +x setup.sh
./setup.sh

# Step 3: PostgreSQL setup
sudo -u postgres psql
CREATE DATABASE bestmedia_db;
CREATE USER bestmedia_admin WITH PASSWORD 'strong_password';
GRANT ALL ON DATABASE bestmedia_db TO bestmedia_admin;
\q

# Step 4: .env configure
nano .env
# ENVIRONMENT=production
# DB_PASSWORD=strong_password
# SECRET_KEY=your-key
# etc.

# Step 5: Django setup
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser

# Step 6: Gunicorn + Nginx
sudo cp supervisor_anistream.conf /etc/supervisor/conf.d/
sudo supervisorctl reread && sudo supervisorctl update
sudo systemctl restart nginx

# Step 7: SSL Certificate (Let's Encrypt)
sudo certbot --nginx -d your-domain.com

# RESULT: https://your-domain.com
```

**Detailed Guide:** README_UBUNTU.md

---

### OPTION 3: Docker (Containerized)

**Time:** 10-15 minut | **Cost:** Depends on host | **Setup:** Hardest

```bash
# Step 1: Docker o'rnatish (agar yo'q bo'lsa)
# See: https://docs.docker.com/install/

# Step 2: .env yaratish
cp .env.example .env
# Edit .env va:
# - DB_PASSWORD: secure_password
# - SECRET_KEY: your-key
# - ENVIRONMENT: production

# Step 3: Build va run
docker-compose build
docker-compose up -d

# Step 4: Django setup
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser

# Step 5: Access
# http://localhost:8000
# Admin: http://localhost:8000/admin

# Stop
docker-compose down
```

---

## 📋 LOCAL TESTING (Oldin deploy qil!)

```bash
# Windows
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

# Browser: http://127.0.0.1:8000
# Admin: http://127.0.0.1:8000/admin
```

---

## 🔐 SECRET_KEY GENERATE QILISH

Railway yoki Ubuntu'da:

```bash
python manage.py shell -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Result: Copy qiling va `.env`ga yoki Railway variables'ga paste qiling

---

## 📁 IMPORTANT FILES

### Documentation
- `README.md` - Overview
- `README_UBUNTU.md` - Ubuntu deployment (detailed)
- `PRODUCTION_DEPLOYMENT.md` - Railway/Ubuntu/Docker guide
- `ENV_VARIABLES_GUIDE.md` - Environment variables
- `DEPLOYMENT_CHECKLIST.md` - Pre/Post checklist
- `SETUP_SUMMARY.md` - Project summary

### Configuration
- `.env.example` - Environment template
- `nginx_config.conf` - Nginx settings
- `supervisor_anistream.conf` - Process manager
- `Dockerfile` - Docker image
- `docker-compose.yml` - Docker stack
- `railway.json` - Railway config

### Scripts
- `github_push.bat` - GitHub push (Windows)
- `github_push.sh` - GitHub push (Linux/Mac)
- `setup.sh` - Auto-setup (Ubuntu)

---

## ✅ DEPLOYMENT CHECKLIST

Har bir deployment uchun:

- [ ] Local'da test qildi
- [ ] `.env` faylini create qildi
- [ ] `SECRET_KEY` generate qildi
- [ ] `DEBUG=False` qildi
- [ ] `ALLOWED_HOSTS` to'g'ri qildi
- [ ] Database migratsiyalari qo'lladi
- [ ] Static files collected
- [ ] Admin panel test qildi
- [ ] Git commit va push qildi
- [ ] Environment variables qo'shdi
- [ ] Deploy qildi
- [ ] Live URL'ni test qildi

---

## 🆘 QUICK FIXES

| Problem | Solution |
|---------|----------|
| `502 Bad Gateway` | `sudo supervisorctl restart anistream` |
| Static files missing | `python manage.py collectstatic --noinput` |
| `Disallowed host` error | `ALLOWED_HOSTS`'ni yangilang |
| PostgreSQL connection error | DATABASE_URL va password check qiling |
| CSRF token error | CSRF_TRUSTED_ORIGINS check qiling |

---

## 📞 RESOURCES

- [Django Docs](https://docs.djangoproject.com/)
- [Railway Docs](https://docs.railway.app/)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)
- [Docker Docs](https://docs.docker.com/)
- [Nginx Docs](https://nginx.org/en/docs/)

---

## 🎯 NEXT STEPS

1. **Choose Deployment:** Railway (easy) / Ubuntu (control) / Docker (portable)
2. **Local Test:** `python manage.py runserver`
3. **Push to GitHub:** `github_push.bat` or `./github_push.sh`
4. **Deploy:** Follow chosen option above
5. **Configure:** Add environment variables
6. **Verify:** Test admin panel at `/admin`
7. **Monitor:** Check logs va status

---

## 📊 PROJECT STATUS

```
✅ Code: Production-ready
✅ Config: Environment-based
✅ Database: SQLite (dev) + PostgreSQL (prod)
✅ Deployment: Railway / Ubuntu / Docker
✅ Documentation: Complete (6 files, 40+ KB)
✅ Scripts: Automated (bash + batch)
✅ Security: Hardened (SSL, CSRF, XSS)
✅ Monitoring: Configured (logs, metrics)

Status: READY FOR PRODUCTION DEPLOYMENT 🚀
```

---

## 💡 TIPS

1. **Railway uchun:** Push to GitHub → Auto-deploy
2. **Ubuntu uchun:** `setup.sh` ishga tushirish yoki README_UBUNTU.md o'qish
3. **Docker uchun:** `docker-compose up -d` va migrating
4. **SECRET_KEY'ni o'zgartir:** Production'da yangi key
5. **DEBUG OFF:** Production'da `DEBUG=False`
6. **HTTPS qo'llang:** Security uchun SSL mandatory
7. **Backups:** Database regular backup qil
8. **Monitoring:** Logs va metrics kuzatib tur

---

## 🎉 LET'S GO!

Juda tezda deploy qilish uchun:

```bash
# Windows
github_push.bat

# Linux
./github_push.sh

# Then go to: https://railway.app
# Click: New Project → Deploy from GitHub
# Select: Your repository
# Wait: ~5 minutes
# Access: https://your-app.railway.app
```

---

**Happy Streaming! 🎬✨**

**Project:** AniStream v1.0  
**Updated:** 2026-04-05  
**Status:** Production Ready ✅

