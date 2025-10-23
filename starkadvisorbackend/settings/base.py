import os
from pathlib import Path
from urllib.parse import quote_plus

BASE_DIR = Path(__file__).resolve().parent.parent

# ------- helpers -------
def env(name: str, default: str | None = None) -> str | None:
    return os.getenv(name, default)

def env_bool(name: str, default: bool = False) -> bool:
    v = os.getenv(name)
    if v is None:
        return default
    return str(v).strip().lower() in ("1", "true", "yes", "on")

def env_list(name: str) -> list[str]:
    v = os.getenv(name, "")
    return [s.strip() for s in v.split(",") if s.strip()]

# ------- core -------
SECRET_KEY = env("SECRET_KEY", "CHANGE_ME")

DEBUG = env_bool("DEBUG", False)

ALLOWED_HOSTS = env_list("ALLOWED_HOSTS") or ["localhost", "127.0.0.1"]

# ------- apps -------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # third-party
    "corsheaders",
    # tu app(s)
    "core",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",  # << debe ir muy arriba
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "starkadvisorbackend.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "starkadvisorbackend.wsgi.application"

# ------- database (PostgreSQL) -------
# Prioriza DATABASE_URL. Si no existe, usa DB_* con sslmode=require por defecto.
# Requiere: dj-database-url
import dj_database_url

DATABASE_URL = env("DATABASE_URL")
if DATABASE_URL:
    # Si la URL no trae sslmode, lo forzamos.
    db_cfg = dj_database_url.parse(DATABASE_URL, conn_max_age=600)
    if "OPTIONS" not in db_cfg:
        db_cfg["OPTIONS"] = {}
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
            "OPTIONS": {"sslmode": env("DB_SSLMODE", "require")},
        }
    }

# ------- MongoDB (Atlas) -------
# Lee MONGODB_URI / MONGO_URI y MONGO_NAME
MONGODB_URI = env("MONGODB_URI") or env("MONGO_URI")
MONGO_NAME = env("MONGO_NAME", "starkadvisor")
MONGO_COLLECTION_NEWS = env("MONGO_COLLECTION_NEWS", "news")
MONGO_COLLECTION_TRADE_OF_THE_DAY = env("MONGO_COLLECTION_TRADE_OF_THE_DAY", "trade_of_the_day")

# ------- i18n / tz -------
LANGUAGE_CODE = "es-co"
TIME_ZONE = "America/Bogota"
USE_I18N = True
USE_TZ = True

# ------- static / media -------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ------- CORS / CSRF -------
CORS_ALLOWED_ORIGINS = env_list("CORS_ALLOWED_ORIGINS")
CSRF_TRUSTED_ORIGINS = env_list("CSRF_TRUSTED_ORIGINS")
CORS_ALLOW_CREDENTIALS = env_bool("CORS_ALLOW_CREDENTIALS", True)
CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]

# ------- logging (útil en Azure Log Stream) -------
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
