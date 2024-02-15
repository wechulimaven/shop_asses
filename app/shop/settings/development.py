from .base import *  # noqa
import os
from .configs.logging import *


DEBUG = True


ALLOWED_HOSTS = ["*"]


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",  # noqa
    }
}


CORS_ALLOW_ALL_ORIGINS = True

BASE_URL = "https://a785-102-89-33-37.eu.ngrok.io"

LOGGING["root"]["level"] = "DEBUG"  # noqa

DEFAULT_CHARSET = 'utf-8'


# EMAIL_PORT = 
# # os.getenv("EMAIL_PORT")
# EMAIL_HOST_USER = "mavenwechuli@gmail.com"
# # os.getenv("EMAIL_HOST_USER")
# EMAIL_HOST_PASSWORD = "fxdwugifkargqmig"
# # os.getenv("EMAIL_HOST_PASSWORD")
# EMAIL_USE_TLS = True
# EMAIL_USE_SSL = False

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com' # gmail
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'mavenwechuli@gmail.com'
EMAIL_HOST_PASSWORD = 'fxdwugifkargqmig'
