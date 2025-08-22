# ☁️ Configuración para PRODUCCIÓN EN CLOUD
import os
from .settings import *

# Base de datos en la nube (ej: AWS RDS, Google Cloud SQL, Azure Database)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'starkadvisor_prod'),
        'USER': os.getenv('DB_USER', 'starkuser_prod'),
        'PASSWORD': os.getenv('DB_PASSWORD'),  # Variable de entorno
        'HOST': os.getenv('DB_HOST'),  # URL del servicio cloud
        'PORT': os.getenv('DB_PORT', '5432'),
        'OPTIONS': {
            'sslmode': 'require',  # Seguridad SSL para cloud
        },
    }
}

# Redis en la nube (ej: AWS ElastiCache, Google Cloud Memorystore)
REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT = os.getenv('REDIS_PORT', 6379)
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')  # Redis con contraseña
REDIS_DB = 0

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f'redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'ssl_cert_reqs': None,  # SSL para Redis cloud
            }
        },
        'KEY_PREFIX': 'starkadvisor_prod'
    }
}

# Configuración de producción
DEBUG = False
ALLOWED_HOSTS = [
    os.getenv('DOMAIN_NAME'),  # Tu dominio
    'starkadvisor.com',  # Ejemplo
    '*.herokuapp.com',  # Si usas Heroku
    '*.vercel.app',  # Si usas Vercel
]

# Seguridad en producción
SECURE_SSL_REDIRECT = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# CORS para producción
CORS_ALLOWED_ORIGINS = [
    "https://starkadvisor.com",  # Tu frontend en producción
    "https://www.starkadvisor.com",
]

# Archivos estáticos en cloud (AWS S3, Google Cloud Storage)
STATIC_URL = os.getenv('STATIC_URL', '/static/')
MEDIA_URL = os.getenv('MEDIA_URL', '/media/')

print("☁️ Configuración PRODUCCIÓN cargada")
