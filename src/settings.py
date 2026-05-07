import os
import sys
from pathlib import Path

try:
    from decouple import config, Csv
except ImportError:
    class Csv:
        def __call__(self, value):
            return [item.strip() for item in str(value).split(',') if item.strip()]

    def config(key, default=None, cast=None):
        value = os.getenv(key, default)
        if cast is None:
            return value
        if cast is bool:
            return str(value).strip().lower() in {'1', 'true', 'yes', 'on'}
        if callable(cast):
            return cast(value)
        return value

# Loyihaning asosiy yo'li
BASE_DIR = Path(__file__).resolve().parent.parent

# .env faylidan sozlamalarni o'qish (environment variable uchun)
SECRET_KEY = config('SECRET_KEY', default='django-insecure-bestmedia-vps-key-2026-change-in-production')

# Production: False, Development: True (environment variable dan o'qish)
DEBUG = config('DEBUG', default=True, cast=bool)

# Allowed hosts (environment variable dan o'qish yoki default qo'yish)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='bestmedia-official.uz,www.bestmedia-official.uz,5.189.136.95,www.anibest.uz,45.138.159.4', cast=Csv())


# Ilovalar ro'yxati
INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Sizning ilovangiz
    'my_app.apps.MyAppConfig',

    # Media va Static uchun
    'cloudinary_storage',
    'cloudinary',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Static fayllarni yetkazish uchun
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    # Custom Device Session Limits
    'my_app.middleware.DeviceLimitMiddleware',
]

ROOT_URLCONF = 'src.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'src.wsgi.application'

# --- MA'LUMOTLAR BAZASI (Production: PostgreSQL, Development: SQLite) ---
import dj_database_url

ENVIRONMENT = config('ENVIRONMENT', default='production')

# DATABASE_URL mavjud bo'lsa (Railway/Production) uni ishlatish
if config('DATABASE_URL', default=None):
    DATABASES = {
        'default': dj_database_url.config(
            default=config('DATABASE_URL'),
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
elif ENVIRONMENT == 'production':
    # Railway PostgreSQL (manual konfiguratsiya)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config('DB_NAME', default='bestmedia_db'),
            'USER': config('DB_USER', default='postgres'),
            'PASSWORD': config('DB_PASSWORD', default=''),
            'HOST': config('DB_HOST', default='localhost'),
            'PORT': config('DB_PORT', default='5432'),
            'CONN_MAX_AGE': 600,
            'OPTIONS': {
                'connect_timeout': 10,
            }
        }
    }
else:
    # Development - SQLite
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Custom User Model
AUTH_USER_MODEL = 'my_app.CustomUser'
LOGIN_URL = '/login/'

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Tashkent'
USE_I18N = True
USE_TZ = True

# --- STATIC VA MEDIA FAYLLAR ---
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Whitenoise static fayllarni siqish uchun
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- CSRF VA SECURITY SOZLAMALARI ---
# Environment'dan ALLOWED_HOSTS va CSRF_TRUSTED_ORIGINS ni o'qish
CSRF_TRUSTED_ORIGINS = config(
    'CSRF_TRUSTED_ORIGINS',
    default='http://bestmedia-official.uz,https://www.bestmedia-official.uz',
    cast=Csv()
)

# Session va Cookie sozlamalari (Production)
if ENVIRONMENT == 'production':
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = config('USE_HTTPS', default=True, cast=bool)
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = 'DENY'
else:
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    SECURE_SSL_REDIRECT = False

DATA_UPLOAD_MAX_MEMORY_SIZE = 524288000
FILE_UPLOAD_MAX_MEMORY_SIZE = 524288000
