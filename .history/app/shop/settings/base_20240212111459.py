"""
Django settings for shop project.

Generated by 'django-admin startproject' using Django 4.0.5.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

from pathlib import Path
from corsheaders.defaults import default_headers
import os
from celery.schedules import crontab

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent
SECRET_KEY = "django-insecure-goj@j03mpe9%*458mw*$gcpdyzv1zgs=(y#3pe685)3687wh5x"

DEBUG = True

ALLOWED_HOSTS = [
    "127.0.0.1",
]


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "oauth2_provider",
    "corsheaders",
    "django_celery_beat",
    "django_celery_results",
    "storages",
    "drf_spectacular",
    # apps
    "report",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "shop.urls"

# Configure the Social Auth Backend
AUTHENTICATION_BACKENDS = (
    'rest_framework_social_oauth2.backends.DjangoOAuth2',
)

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

WSGI_APPLICATION = "shop.wsgi.application"

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = default_headers + (
    "access-control-allow-headers",
    "withcredentials",
    "x-incognito",
    "x-referrer-value",
)
CORS_EXPOSE_HEADERS = (
    "access-control-allow-origin",
    "access-control-allow-credentials",
)

# AUTH_USER_MODEL = "accounts.User"

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

COOKIE_KEY = "__shop_hub_cookie__"

STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"),)
STATIC_URL = "/staticfiles/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
MEDIA_URL = "/mediafiles/"
MEDIA_ROOT = os.path.join(BASE_DIR, "mediafiles")

PASSWORD_RESET_PATH = "http://127.0.0.1:8000/"

DJANGO_SU_NAME = os.getenv("DJANGO_SU_NAME")
DJANGO_SU_EMAIL = os.getenv("DJANGO_SU_EMAIL")
DJANGO_SU_PASSWORD = os.getenv("DJANGO_SU_PASSWORD")

SMS_USERNAME = os.getenv("SMS_USERNAME")
SMS_API_KEY = os.getenv("SMS_API_KEY")

# Social Auth Settings
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.getenv("SMS_USERNAME")
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.getenv("SMS_USERNAME")
