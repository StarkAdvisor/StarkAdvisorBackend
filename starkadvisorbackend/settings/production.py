from .base import *  # noqa
import os

# ------------------------
# Flags de seguridad
# ------------------------
DEBUG = env_bool("DEBUG", False)
ALLOWED_HOSTS = env_list("ALLOWED_HOSTS") or ["*.azurewebsites.net"]
SECRET_KEY = env("SECRET_KEY", "CHANGE_ME_IN_PRODUCTION")

# Detrás de Azure App Service (termina TLS)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = False  # Azure ya maneja HTTPS
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# HSTS (actívalo si TODO es HTTPS)
SECURE_HSTS_SECONDS = int(os.getenv("SECURE_HSTS_SECONDS", "31536000"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# ------------------------
# CORS / CSRF desde env
# ------------------------
CORS_ALLOWED_ORIGINS = env_list("CORS_ALLOWED_ORIGINS")
CSRF_TRUSTED_ORIGINS = env_list("CSRF_TRUSTED_ORIGINS")
CORS_ALLOW_CREDENTIALS = env_bool("CORS_ALLOW_CREDENTIALS", True)

# ------------------------
# Base de datos
# ------------------------
# Ya queda configurada en base.py con DATABASE_URL/DB_* (sslmode=require).
# Importante en Azure PostgreSQL flexible: usa DB_USER sin el sufijo @servername
# (tú ya comprobaste que funciona como 'juancknino123').

# ------------------------
# Redis (opcional): si no hay REDIS_URL, base.py usa LocMem
# ------------------------
REDIS_URL = env("REDIS_URL")
REDIS_KEY_PREFIX = env("REDIS_KEY_PREFIX", "starkadvisor_prod")
if REDIS_URL:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": REDIS_URL,  # típico: rediss://...:6380/0
            "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
            "KEY_PREFIX": REDIS_KEY_PREFIX,
        }
    }

# ------------------------
# Estáticos / Media (hereda de base.py)
# ------------------------

# ------------------------
# Logging (a consola)
# ------------------------
# Hereda de base.py; si necesitas más verbosidad, descomenta:
# LOGGING["root"]["level"] = "INFO"
