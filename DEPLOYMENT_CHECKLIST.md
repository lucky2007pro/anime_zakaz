# AniStream - Deployment Checklist

## 📋 Pre-Deployment Checklist

### Code Quality
- [ ] Barcha xatolar fix qilindi
- [ ] Code review qilindi
- [ ] Tests passes
- [ ] Linting errors yo'q

### Database
- [ ] Migrations created: `python manage.py makemigrations`
- [ ] Migrations applied: `python manage.py migrate`
- [ ] Database backup qilindi

### Static & Media Files
- [ ] Static files collected: `python manage.py collectstatic --noinput`
- [ ] Media files directory structure correct
- [ ] File permissions set correctly

### Configuration
- [ ] `.env` file created from `.env.example`
- [ ] `SECRET_KEY` yangi qiymat (prod)
- [ ] `DEBUG=False` production'da
- [ ] `ALLOWED_HOSTS` to'g'ri
- [ ] `CSRF_TRUSTED_ORIGINS` to'g'ri
- [ ] Database credentials to'g'ri
- [ ] Cloudinary credentials (agar kerak bo'lsa)

### Security
- [ ] HTTPS enabled (production)
- [ ] Security headers qo'shildi
- [ ] CORS configured (agar kerak bo'lsa)
- [ ] Rate limiting configured
- [ ] Logging configured

### Version Control
- [ ] Barcha fayllar committed
- [ ] `.gitignore` correct
- [ ] Sensitive files excluded:
  - [ ] `.env` not committed
  - [ ] `db.sqlite3` not committed
  - [ ] `venv/` not committed
  - [ ] `__pycache__/` not committed
  - [ ] `*.pyc` not committed

### Docker/Container (Agar kerak)
- [ ] Dockerfile works: `docker build -t anistream .`
- [ ] Docker-compose works: `docker-compose up`
- [ ] Health checks configured
- [ ] Volume mounts correct
- [ ] Network configuration correct

### Local Testing
- [ ] `python manage.py runserver` works
- [ ] Homepage loads correctly
- [ ] Admin panel accessible: /admin
- [ ] Login/Register works
- [ ] Video upload works (agar feature mavjud)
- [ ] Video streaming works
- [ ] Search functionality works
- [ ] User profile works

---

## 🚀 Deployment Steps

### 1. GitHub Push

```bash
# Terminal'dan:
chmod +x github_push.sh
./github_push.sh

# Yoki qo'lda:
git add .
git commit -m "AniStream ready for production deployment"
git branch -M main
git remote add origin https://github.com/username/anistream.git
git push -u origin main
```

### 2. Railway Deployment

1. https://railway.app ga kiring
2. "New Project" → "Deploy from GitHub"
3. Repository tanlang
4. Environment Variables qo'shish:

```env
# Required
SECRET_KEY=generate-new-key-here
ENVIRONMENT=production
DEBUG=False
ALLOWED_HOSTS=your-app.railway.app
CSRF_TRUSTED_ORIGINS=https://your-app.railway.app

# Database (Railway PostgreSQL orqali avtomatik)
DATABASE_URL=automatically_injected

# Optional
USE_HTTPS=true
DJANGO_LOG_LEVEL=INFO
```

### 3. Ubuntu Server Deployment

```bash
# README_UBUNTU.md ni o'qing:
cat README_UBUNTU.md

# Setup script'ni ishga tushiring:
chmod +x setup.sh
./setup.sh
```

### 4. Docker Deployment

```bash
# Local
docker-compose up -d

# Production
docker build -t anistream:latest .
docker run -d -p 80:8000 -e ENVIRONMENT=production anistream:latest
```

---

## 📊 Post-Deployment Verification

- [ ] Website accessible
- [ ] Admin panel working: `/admin`
- [ ] Static files loading (CSS, JS, images)
- [ ] Media files accessible
- [ ] Database connection OK
- [ ] Logs are being recorded
- [ ] Email notifications working (agar kerak)
- [ ] Performance acceptable
- [ ] SSL certificate valid (HTTPS)

---

## 🔒 Production Security Checklist

### Django Security
- [ ] `DEBUG = False`
- [ ] `ALLOWED_HOSTS` specified
- [ ] `SECRET_KEY` strong and changed
- [ ] CSRF protection enabled
- [ ] XSS protection enabled
- [ ] SQL injection prevention
- [ ] HTTPS enforced
- [ ] HSTS headers set
- [ ] Security headers configured

### Database Security
- [ ] Strong passwords
- [ ] Database user permissions restricted
- [ ] Backups automated
- [ ] Backups encrypted
- [ ] Connection pooling configured

### Server Security
- [ ] Firewall configured
- [ ] SSH keys configured (no password login)
- [ ] Unused ports closed
- [ ] SSL certificate valid
- [ ] Regular security updates

### API Security (agar RESTful API mavjud)
- [ ] Rate limiting
- [ ] Authentication required
- [ ] Input validation
- [ ] Output encoding
- [ ] CORS properly configured

---

## 🛠️ Troubleshooting

### Database Connection Error
```bash
# PostgreSQL service status
systemctl status postgresql

# Check connection
psql -U username -d database_name -h localhost
```

### Static Files Not Loading
```bash
# Collect static files
python manage.py collectstatic --clear --noinput

# Check permissions
sudo chown -R www-data:www-data /path/to/staticfiles
```

### 502 Bad Gateway
```bash
# Check Gunicorn
sudo supervisorctl status anistream

# Check Nginx logs
sudo tail -f /var/log/nginx/error.log
```

### Migration Issues
```bash
# Show migration status
python manage.py showmigrations

# Rollback migration
python manage.py migrate app_name 0001
```

---

## 📈 Monitoring & Maintenance

### Daily
- [ ] Check error logs
- [ ] Monitor server resources
- [ ] Check backup status

### Weekly
- [ ] Review security logs
- [ ] Update packages (pip)
- [ ] Database integrity check

### Monthly
- [ ] Full security audit
- [ ] Performance analysis
- [ ] Database optimization
- [ ] Backup restoration test

---

## 📞 Support & Documentation

- Django Docs: https://docs.djangoproject.com/
- Railway Docs: https://docs.railway.app/
- PostgreSQL Docs: https://www.postgresql.org/docs/
- Nginx Docs: https://nginx.org/en/docs/

---

**Last Updated:** 2026-04-05
**Project:** AniStream v1.0

