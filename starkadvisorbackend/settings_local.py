# 🏠 Configuración para DESARROLLO LOCAL
from .settings import *

# Deshabilitar CSRF completamente para desarrollo
CSRF_USE_SESSIONS = False
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SECURE = False
CSRF_TRUSTED_ORIGINS = ['http://127.0.0.1:8000', 'http://localhost:8000']

# Base de datos local (PostgreSQL en Docker)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'starkadvisor',
        'USER': 'starkuser',
        'PASSWORD': 'starkpass123',
        'HOST': 'localhost',  # Docker local
        'PORT': '5432',
    }
}

# Redis local (Docker)
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'starkadvisor_local'
    }
}

# Configuración de desarrollo
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Deshabilitar CSRF para desarrollo
CSRF_TRUSTED_ORIGINS = ['http://127.0.0.1:8000', 'http://localhost:8000']
CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = False

# CORS para desarrollo
CORS_ALLOW_ALL_ORIGINS = True

# REST Framework - deshabilitar CSRF para APIs
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ]
}

# Middleware personalizado para deshabilitar CSRF en APIs
MIDDLEWARE = [
    'StarkAdvisor.middleware.DisableCSRFMiddleware',  # ← Agregar primero
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

print("🏠 Configuración LOCAL cargada")
