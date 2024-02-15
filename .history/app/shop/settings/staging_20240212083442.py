from .base import *  # noqa
import os
from .vars.logging import *
from corsheaders.defaults import default_headers


DEBUG = True

ALLOWED_HOSTS = [
    "api.cheruven.com",
    ".cloudfront.net",
    ".elasticbeanstalk.com",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("RDS_NAME"),
        "HOST": os.getenv("RDS_HOST"),
        "PORT": os.getenv("RDS_PORT"),
        "USER": os.getenv("RDS_USER"),
        "PASSWORD": os.getenv("RDS_PASSWORD"),
    }
}

CSRF_TRUSTED_ORIGINS = ['https://api.cheruven.com']

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = (
    "https://api.cheruven.com",
    "https://www.api.cheruven.com",
)
CORS_ALLOW_HEADERS = default_headers + (
    "access-control-allow-headers",
    "withcredentials",
    "x-incognito"
)
CORS_EXPOSE_HEADERS = (
    "access-control-allow-origin",
    "access-control-allow-credentials",
)

BASE_URL = "https://api.cheruven.com"

LOGGING["root"]["level"] = "DEBUG"  # noqa

DEFAULT_CHARSET = 'utf-8'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com' # gmail
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'mavenwechuli@gmail.com'
EMAIL_HOST_PASSWORD = 'fxdwugifkargqmig'
