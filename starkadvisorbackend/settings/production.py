# starkadvisorbackend/settings/production.py
from .base import *  # noqa
import os

# -------------------------------------------------------------------
# Helpers (si no existen en base.py, los definimos aquí como fallback)
# -------------------------------------------------------------------
if "env_list" not in globals():
    def env(name: str, default: str | None = None):
        return os.getenv(name, default)

    def env_bool(name: str, default: bool = False) -> bool:
        v = os.getenv(name)
        if v is None:
            return default
        return str(v).strip().lower() in ("1", "true", "yes", "on")

    def env_list(name: str) -> list[str]:
        v = os.getenv(name, "")
        return [s.strip() for s in v.split(",") if s.strip()]

# =========================
# Flags de seguridad
# =========================
DEBUG = env_bool("DEBUG", False)

# ALLOWED_HOSTS: separar por comas en Azure, p. ej.:
# ALLOWED_HOSTS=starkadvisor-backend-XXXX.azurewebsites.net
ALLOWED_HOSTS = env_list("ALLOWED_HOSTS") or ["*.azurewebsites.net"]

SECRET_KEY = env("SECRET_KEY", "CHANGE_ME_IN_PRODUCTION")

# Detrás de Azure App Service (termina TLS)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = False  # Azure ya maneja HTTPS a la app
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# HSTS (recomendado en prod). Ajusta si usas dominios sin HTTPS.
SECURE_HSTS_SECONDS = int(os.getenv("SECURE_HSTS_SECONDS", "31536000"))  # 1 año
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# =========================
# CORS / CSRF (desde env)
# =========================
# Ejemplo en Azure:
# CORS_ALLOWED_ORIGINS=https://calm-plant-02a26be0f.2.azurestaticapps.net
# CSRF_TRUSTED_ORIGINS=https://calm-plant-02a26be0f.2.azurestaticapps.net
CORS_ALLOWED_ORIGINS = env_list("CORS_ALLOWED_ORIGINS")
CSRF_TRUSTED_ORIGINS = env_list("CSRF_TRUSTED_ORIGINS")
CORS_ALLOW_CREDENTIALS = env_bool("CORS_ALLOW_CREDENTIALS", True)

# =========================
# Base de Datos (PostgreSQL Azure)
# =========================
# Opción A: DATABASE_URL (recomendado)
#   postgresql://<USER>@<SERVER>:<PASSWORD>@<HOST>:5432/<DB>?sslmode=require
# Opción B: variables DB_* con sslmode=require
import dj_database_url  # asegúrate en requirements.txt

DATABASE_URL = env("DATABASE_URL")
if DATABASE_URL:
    db_cfg = dj_database_url.parse(DATABASE_URL, conn_max_age=600)
    # Forzar sslmode=require si la URL no lo trae
    db_cfg.setdefault("OPTIONS", {})
    db_cfg["OPTIONS"].setdefault("sslmode", "require")
    DATABASES = {"default": db_cfg}
else:
    DB_NAME = env("DB_NAME", "starkadvisor_db")
    DB_USER = env("DB_USER", "")
    DB_PASSWORD = env("DB_PASSWORD", "")
    DB_HOST = env("DB_HOST", "localhost")
    DB_PORT = env("DB_PORT", "5432")
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": DB_NAME,
            "USER": DB_USER,
            "PASSWORD": DB_PASSWORD,
            "HOST": DB_HOST,
            "PORT": DB_PORT,
            "CONN_MAX_AGE": 600,
            "OPTIONS": {"sslmode": os.getenv("DB_SSLMODE", "require")},
        }
    }

# =========================
# Redis (opcional): cae a LocMem si no hay REDIS_URL
# =========================
REDIS_URL = env("REDIS_URL")
REDIS_KEY_PREFIX = env("REDIS_KEY_PREFIX", "starkadvisor_prod")

if REDIS_URL:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": REDIS_URL,  # en Azure suele ser rediss://...:6380/0
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            },
            "KEY_PREFIX": REDIS_KEY_PREFIX,
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "starkadvisor-locmem",
        }
    }

# =========================
# Archivos estáticos / media
# =========================
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# =========================
# Logging (a consola para Azure Log Stream)
# =========================
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": {
        "django": {"handlers": ["console"], "level": "INFO", "propagate": True},
        "pymongo": {"handlers": ["console"], "level": "WARNING", "propagate": True},
        "core": {"handlers": ["console"], "level": "INFO", "propagate": True},
    },
}

# =========================
# MongoDB (usado por tu app via core.mongo_client)
# =========================
# En Azure define:
#   MONGODB_URI=mongodb+srv://<USER>:<PASS>@starkadvisor.sw4vzwy.mongodb.net/starkadvisor?retryWrites=true&w=majority&appName=StarkAdvisor
#   MONGO_NAME=starkadvisor
#   MONGO_COLLECTION_NEWS=news
#   MONGO_COLLECTION_TRADE_OF_THE_DAY=trade_of_the_day
# (El cliente se inicializa en core/mongo_client.py)
