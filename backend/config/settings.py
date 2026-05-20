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
    'rest_framework_simplejwt.token_blacklist',  # Logout token geçersiz kılma
    'django_filters',
    'corsheaders',  # Mobil istemci CORS desteği
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
    'corsheaders.middleware.CorsMiddleware',         # CORS — SecurityMiddleware'den hemen sonra
    'apps.api.v1.middleware.RequireHTTPSMiddleware', # API HTTPS zorunluluğu (prod)
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
    # Rate Limiting — Brute-force koruması
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '30/hour',           # Anonim: saatte 30 istek
        'user': '1000/day',          # Kayıtlı: günde 1000 istek
        'auth_login': '5/minute',    # Login: dakikada 5 deneme (brute-force)
        'auth_register': '3/hour',   # Kayıt: saatte 3 deneme
        'token_refresh': '10/minute', # Token yenile: dakikada 10
        'password_change': '5/hour', # Şifre değiştir: saatte 5
    },
    # Hata yanıt formatı
    'EXCEPTION_HANDLER': 'rest_framework.views.exception_handler',
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.openapi.AutoSchema',
}

# JWT Ayarları
from datetime import timedelta
SIMPLE_JWT = {
    # Token süreleri
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=env.int('JWT_ACCESS_LIFETIME_MINUTES', default=60)),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=env.int('JWT_REFRESH_LIFETIME_DAYS', default=7)),

    # Güvenlik davranışları
    'ROTATE_REFRESH_TOKENS': True,      # Her refresh'te yeni refresh token ver
    'BLACKLIST_AFTER_ROTATION': True,   # Eski refresh token'ı geçersiz kıl
    'UPDATE_LAST_LOGIN': True,          # Son giriş zamanını güncelle

    # İmzalama algoritması (HS256 — SECRET_KEY ile)
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': env('SECRET_KEY'),
    'VERIFYING_KEY': None,

    # Header yapılandırması
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',

    # Token tipi doğrulama
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',

    # Özel claim'ler (CustomTokenObtainPairSerializer tarafından doldurulur)
    'TOKEN_OBTAIN_SERIALIZER': 'apps.accounts.token_serializers.CustomTokenObtainPairSerializer',
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
import sys

# QueueHandler 'handlers' parametresi Python 3.12+ gerektirir
_use_queue_handler = sys.version_info >= (3, 12)

_handlers = {
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
}

if _use_queue_handler:
    _handlers['queue'] = {
        'class': 'logging.handlers.QueueHandler',
        'handlers': ['console', 'file'],
        'respect_handler_level': True,
    }

_default_handler = ['queue'] if _use_queue_handler else ['console', 'file']

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
    'handlers': _handlers,
    'loggers': {
        'django': {
            'handlers': _default_handler,
            'level': 'INFO',
            'propagate': False,
        },
        'django.server': {
            'handlers': _default_handler,
            'level': 'WARNING',  # Filtre: 200 OK HTTP loglarını gizle
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': _default_handler,
            'level': 'WARNING',  # Filtre: Gereksiz SQL sorgu loglarını gizle
            'propagate': False,
        },
        'apps': {
            'handlers': _default_handler,
            'level': 'INFO',
            'propagate': False,
        },
        'ml': {
            'handlers': _default_handler,
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# ---------------------------------------------------------------------------
# HTTPS & Güvenlik Başlıkları
# ---------------------------------------------------------------------------
# Üretim ortamında .env'de SECURE_SSL_REDIRECT=True olarak ayarlayın.
# Geliştirme ortamında tüm bu ayarlar False'dır.

# HTTPS yönlendirme (prod'da True)
SECURE_SSL_REDIRECT = env.bool('SECURE_SSL_REDIRECT', default=False)

# HSTS — tarayıcıya HTTPS zorunu bildir (prod'da aktif edilir)
SECURE_HSTS_SECONDS = env.int('SECURE_HSTS_SECONDS', default=0)
SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool('SECURE_HSTS_INCLUDE_SUBDOMAINS', default=False)
SECURE_HSTS_PRELOAD = env.bool('SECURE_HSTS_PRELOAD', default=False)

# Güvenli Cookie'ler (prod'da True — HTTPS gerektirir)
SESSION_COOKIE_SECURE = env.bool('SESSION_COOKIE_SECURE', default=False)
CSRF_COOKIE_SECURE = env.bool('CSRF_COOKIE_SECURE', default=False)

# HTTP Güvenlik Başlıkları
X_FRAME_OPTIONS = 'DENY'                     # Clickjacking koruması
SECURE_CONTENT_TYPE_NOSNIFF = True           # MIME sniffing koruması
SECURE_BROWSER_XSS_FILTER = True             # XSS filtresi (eski tarayıcılar)
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# Proxy arkasında çalışıyorsa (nginx, load balancer)
USE_X_FORWARDED_HOST = env.bool('USE_X_FORWARDED_HOST', default=False)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https') if env.bool('BEHIND_PROXY', default=False) else None

# ---------------------------------------------------------------------------
# CORS — Mobil İstemci Cross-Origin Desteği
# ---------------------------------------------------------------------------
# Geliştirme: CORS_ALLOW_ALL_ORIGINS=True (sadece dev!)
# Üretim:     CORS_ALLOWED_ORIGINS listesine domain ekleyin.

CORS_ALLOW_ALL_ORIGINS = env.bool('CORS_ALLOW_ALL_ORIGINS', default=False)

CORS_ALLOWED_ORIGINS = env.list(
    'CORS_ALLOWED_ORIGINS',
    default=[
        'http://localhost:3000',
        'http://localhost:8080',
        'http://127.0.0.1:3000',
    ],
)

CORS_ALLOW_CREDENTIALS = True  # Cookie/Authorization header ile istek

CORS_ALLOWED_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

CORS_ALLOWED_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]
