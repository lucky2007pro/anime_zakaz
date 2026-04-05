import os
from pathlib import Path
import dj_database_url
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-3stjy_8w_4-1$67wt@hvzi$3nu@elz^n$33frr(zbf=p31el3&')

ENVIRONMENT = os.environ.get('ENVIRONMENT', 'development').lower()
USE_HTTPS = os.environ.get('USE_HTTPS', 'false').lower() in ('1', 'true', 'yes')

if 'DEBUG' in os.environ:
    DEBUG = os.environ.get('DEBUG', 'False') == 'True'
else:
    DEBUG = ENVIRONMENT != 'production'


def _env_bool(var_name, default=False):
    return os.environ.get(var_name, str(default)).strip().lower() in ('1', 'true', 'yes', 'on')


def _split_csv_env(var_name, default_value=''):
    """Comma-separated env qiymatini tozalab list ko'rinishiga o'tkazadi."""
    raw_value = os.environ.get(var_name, default_value)
    return [item.strip() for item in raw_value.split(',') if item.strip()]


DEFAULT_ALLOWED_HOSTS = [
    'healthcheck.railway.app',
    '.up.railway.app',
    '127.0.0.1',
    'localhost',
]

DEFAULT_CSRF_TRUSTED_ORIGINS = [
    'https://healthcheck.railway.app',
    'https://*.up.railway.app',
]

ALLOWED_HOSTS = list(dict.fromkeys(_split_csv_env('ALLOWED_HOSTS') + DEFAULT_ALLOWED_HOSTS))
CSRF_TRUSTED_ORIGINS = list(dict.fromkeys(_split_csv_env('CSRF_TRUSTED_ORIGINS') + DEFAULT_CSRF_TRUSTED_ORIGINS))

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'cloudinary_storage',
    'cloudinary',

    'my_app.apps.MyAppConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'src.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'src.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

if 'DATABASE_URL' in os.environ:
    DATABASES['default'] = dict(dj_database_url.config(
        conn_max_age=600,
        conn_health_checks=True,
    ))

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTH_USER_MODEL = 'my_app.CustomUser'

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')] if os.path.exists(os.path.join(BASE_DIR, 'static')) else []

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

cloudinary_cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME', '').strip()
cloudinary_api_key = os.environ.get('CLOUDINARY_API_KEY', '').strip()
cloudinary_api_secret = os.environ.get('CLOUDINARY_API_SECRET', '').strip()
cloudinary_credentials_set = all([
    cloudinary_cloud_name,
    cloudinary_api_key,
    cloudinary_api_secret,
])

# In production prefer remote media storage to avoid Railway's ephemeral filesystem loss.
use_cloudinary = _env_bool('USE_CLOUDINARY', default=(not DEBUG)) and cloudinary_credentials_set

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': cloudinary_cloud_name,
    'API_KEY': cloudinary_api_key,
    'API_SECRET': cloudinary_api_secret,
    'SECURE': True,
    'RESOURCE_TYPE': 'auto',
}

STORAGES = {
    'default': {
        'BACKEND': 'cloudinary_storage.storage.MediaCloudinaryStorage' if use_cloudinary else 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}

if not use_cloudinary:
    STORAGES['default']['OPTIONS'] = {
        'location': MEDIA_ROOT,
        'base_url': MEDIA_URL,
    }

if ENVIRONMENT == 'production' and not DEBUG and USE_HTTPS:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
    },
}

