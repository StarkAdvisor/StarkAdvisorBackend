from .base import *
import os
import logging


DEBUG = env.bool("DEBUG", default=True)
logging.getLogger('django.utils.autoreload').setLevel(logging.CRITICAL)

# Permitir todos los hosts durante desarrollo local
ALLOWED_HOSTS = ["*"]

# Clave secreta (usa la misma desde .env)
SECRET_KEY = env("SECRET_KEY", default="django-insecure-dev-key")

# -------------------------------
# 🗄️ Base de datos (PostgreSQL local o SQLite)
# -------------------------------

# Si usas PostgreSQL local
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("DB_NAME", default="starkadvisorbd"),
        "USER": env("DB_USER", default="postgres"),
        "PASSWORD": env("DB_PASSWORD", default="root"),
        "HOST": env("DB_HOST", default="localhost"),
        "PORT": env("DB_PORT", default="5432"),
    }
}


REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ]
}



# --- Middleware personalizado para deshabilitar CSRF ---
# Insertar antes de los demás middlewares
MIDDLEWARE.insert(0, 'starkadvisorbackend.middleware.DisableCSRFMiddleware')



# -----------------------------
# Redis configuration (from .env)
# -----------------------------
REDIS_URL = env(
    "REDIS_URL",
    default="redis://localhost:6379/0"  # fallback para desarrollo o docker
)
REDIS_HOST = env("REDIS_HOST", default="localhost")
REDIS_PORT = env.int("REDIS_PORT", default=6379)
REDIS_DB = env.int("REDIS_DB", default=0)
REDIS_KEY_PREFIX = env("REDIS_KEY_PREFIX", default="starkadvisor_local")

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
        "KEY_PREFIX": REDIS_KEY_PREFIX,
    }
}




# -------------------------------
# 💬 CORS y Debug Toolbar
# -------------------------------

# Activar CORS abierto para desarrollo
CORS_ALLOW_ALL_ORIGINS = True

# Internal IPs para django-debug-toolbar
INTERNAL_IPS = ["127.0.0.1", "localhost"]


# -------------------------------
# ⚙️ Logging (simplificado para desarrollo)
# -------------------------------

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",  # Cambia DEBUG → INFO
        },
        "django.db.backends": {
            "handlers": ["console"],
            "level": "WARNING",  # Oculta los SELECTs
            "propagate": False,
        },
    },
}