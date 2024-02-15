import os

from .base import *  # noqa
from .configs.logging import *
from corsheaders.defaults import default_headers

DEBUG = False

EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_SECURITY = os.getenv("EMAIL_SECURITY")
if EMAIL_SECURITY == "TLS":
    EMAIL_USE_TLS = True
if EMAIL_SECURITY == "SSL":
    EMAIL_USE_SSL = True
EMAIL_PORT = os.getenv("EMAIL_PORT")
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")

ALLOWED_HOSTS = [
    ".amazonaws.com",
    ".cheruvenapi.com",
    ".cloudfront.net",
    ".elasticbeanstalk.com",
    "54.243.69.191",
    "172.31.32.222",
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

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = (
    # "https://cheruven.com",
    # "https://www.cheruven.com",
    # "https://cheruven-frontend-web-cheruvenweb.vercel.app"
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

LOGGING["root"]["level"] = "INFO"  # noqa
