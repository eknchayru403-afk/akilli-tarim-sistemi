"""
Django settings for Akıllı Tarım Yönetim Sistemi (ATYS).

Environment variables are loaded from .env file using django-environ.
"""

import os
from pathlib import Path

import environ

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# Environment
env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, ['localhost', '127.0.0.1']),
)
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# Security
SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')
ALLOWED_HOSTS = env('ALLOWED_HOSTS')

# Application definition
DJANGO_APPS = [
    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'django_htmx',
    'crispy_forms',
    'crispy_bootstrap5',
    'channels',
    'rest_framework',
    'rest_framework_simplejwt',
    'django_filters',
]

LOCAL_APPS = [
    'apps.accounts',
    'apps.fields',
    'apps.analysis',
    'apps.weather',
    'apps.dashboard',
    'apps.api',
    'apps.reports',
    'apps.iot',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_htmx.middleware.HtmxMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}

# Database — DATABASE_URL veya DB_ENGINE ile yapılandırılır
# Örnek: DATABASE_URL=postgres://ats:ats@localhost:5432/akilli_tarim
_db_engine = env('DB_ENGINE', default='')
if _db_engine == 'django.db.backends.postgresql':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': env('DB_NAME', default='akilli_tarim'),
            'USER': env('DB_USER', default='ats'),
            'PASSWORD': env('DB_PASSWORD', default='ats'),
            'HOST': env('DB_HOST', default='localhost'),
            'PORT': env('DB_PORT', default='5432'),
            'CONN_MAX_AGE': env.int('DB_CONN_MAX_AGE', default=60),
            'OPTIONS': {'connect_timeout': 10},
        }
    }
elif _db_engine == 'django.db.backends.mysql':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': env('DB_NAME', default='akilli_tarim'),
            'USER': env('DB_USER', default='root'),
            'PASSWORD': env('DB_PASSWORD', default=''),
            'HOST': env('DB_HOST', default='localhost'),
            'PORT': env('DB_PORT', default='3306'),
            'OPTIONS': {
                'charset': 'utf8mb4',
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            },
        }
    }
else:
    DATABASES = {
        'default': env.db('DATABASE_URL', default=f'sqlite:///{BASE_DIR}/db.sqlite3'),
    }

# Custom User Model
AUTH_USER_MODEL = 'accounts.CustomUser'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'tr'
TIME_ZONE = 'Europe/Istanbul'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'

# Login/Logout URLs
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/accounts/login/'

# Data files paths
DATA_DIR = BASE_DIR / 'data'
ML_DIR = BASE_DIR / 'ml'
ML_MODELS_DIR = ML_DIR / 'saved_models'

# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'apps.api.v1.pagination.StandardPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
}

# JWT Ayarları
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}

# Cache — LocMemCache (geliştirme), Redis'e geçiş için django-redis ekleyin
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'atys-cache',
        'TIMEOUT': 300,  # 5 dakika varsayılan
    }
}

# MQTT / IoT (EMQX broker)
MQTT_HOST = env('MQTT_HOST', default='localhost')
MQTT_PORT = env.int('MQTT_PORT', default=1883)
MQTT_TLS = env.bool('MQTT_TLS', default=False)
MQTT_CA_CERT = env('MQTT_CA_CERT', default='')
MQTT_USERNAME = env('MQTT_USERNAME', default='ingest')
MQTT_PASSWORD = env('MQTT_PASSWORD', default='')
MQTT_CLIENT_ID = env('MQTT_CLIENT_ID', default='ats-ingest-1')
MQTT_ENV = env('MQTT_ENV', default='dev')
MQTT_TOPIC_VERSION = env('MQTT_TOPIC_VERSION', default='v1')
MQTT_KEEPALIVE = env.int('MQTT_KEEPALIVE', default=60)

# Uygulama önbellek süreleri (saniye)
CACHE_TTL_PRICES = 60 * 30       # 30 dakika — Fiyat verisi (seyrek değişir)
CACHE_TTL_DASHBOARD = 60 * 2     # 2 dakika  — Dashboard istatistikleri
CACHE_TTL_CSV_DATA = 60 * 60     # 1 saat    — Simülasyon CSV verisi

# Logging dizini
LOGS_DIR = BASE_DIR / 'logs'
import os
os.makedirs(LOGS_DIR, exist_ok=True)

# Logging Konfigürasyonu
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{asctime}] {levelname} [{name}:{lineno}] [PID:{process} TID:{thread}] - {message}',
            'style': '{',
        },
        'simple': {
            'format': '[{asctime}] {levelname} - {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'atys.log',
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
            'formatter': 'verbose',
            'encoding': 'utf-8',
        },
        'queue': {
            'class': 'logging.handlers.QueueHandler',
            'handlers': ['console', 'file'],
            'respect_handler_level': True,
        },
    },
    'loggers': {
        'django': {
            'handlers': ['queue'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.server': {
            'handlers': ['queue'],
            'level': 'WARNING',  # Filtre: 200 OK HTTP loglarını gizle
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['queue'],
            'level': 'WARNING',  # Filtre: Gereksiz SQL sorgu loglarını gizle
            'propagate': False,
        },
        'apps': {
            'handlers': ['queue'],
            'level': 'INFO',
            'propagate': False,
        },
        'ml': {
            'handlers': ['queue'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
