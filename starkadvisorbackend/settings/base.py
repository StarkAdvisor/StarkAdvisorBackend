"""
Base settings for StarkAdvisor backend.
This file holds all configurations shared by all environments.
"""

from pathlib import Path
import environ
import os

# -----------------------------
# Paths and environment setup
# -----------------------------
# BASE_DIR should point to the project root (repository root). base.py is located
# at <project>/starkadvisorbackend/settings/base.py so go up three levels to reach
# the repository root.
BASE_DIR = Path(__file__).resolve().parent.parent.parent
env = environ.Env()
environ.Env.read_env()

# -----------------------------
# Core Django settings
# -----------------------------
SECRET_KEY = env("SECRET_KEY", default="change-this-in-production")

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sessions',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'debug_toolbar',   # Solo se usará si está activado en local
    'news',
    'stocks',
    'chatbot',
    'user_admin',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
     'debug_toolbar.middleware.DebugToolbarMiddleware',
]

ROOT_URLCONF = 'starkadvisorbackend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'starkadvisorbackend.wsgi.application'

# -----------------------------
# Authentication
# -----------------------------
AUTH_USER_MODEL = "user_admin.CustomUser"

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# -----------------------------
# Internationalization
# -----------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# -----------------------------
# Static files
# -----------------------------
STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# -----------------------------
# DRF settings
# -----------------------------
REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

# -----------------------------
# MongoDB configuration
# -----------------------------
MONGO_DB = {
    "NAME": env("MONGO_NAME", default="starkadvisor"),
    "HOST": env("MONGO_HOST", default="localhost"),
    "PORT": env.int("MONGO_PORT", default=27017),
    "URI": env("MONGO_URI", default=None)
}

# -----------------------------
# Chatbot & FAQ configuration
# -----------------------------
FAQ_PATH = env("FAQ_PATH", default=os.path.join(BASE_DIR, "chatbot/faqs/faqs.json"))
FAQ_NORMALIZED_PATH = env("FAQ_NORMALIZED_PATH", default=os.path.join(BASE_DIR, "chatbot/faqs/faqs_normalized.json"))
FALLOVER_THRESHOLD = env.float("FALLOVER_THRESHOLD", default=0.08)
FALLOVER_MESSAGE = env("FALLOVER_MESSAGE", default="Lo siento, Starky no entendió tu pregunta. Por favor intenta con otra.")
FAQ_MODEL_PATH = env("FAQ_MODEL_PATH", default=os.path.join(BASE_DIR, "chatbot/faq_model_2"))

FINANCIAL_NEWS_SOURCES = env.list("FINANCIAL_NEWS_SOURCES", default=[])




