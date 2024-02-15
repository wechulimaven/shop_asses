import os
import logging
from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv
from split_settings.tools import include, optional


load_dotenv()


ENV_SETTING = "ENVIRONMENT_SETTING"


current_env = os.getenv(ENV_SETTING, "DEVELOPMENT")

include(
    "configs/logging.py",
    "configs/celery_vars.py",
    "configs/rest_framework.py",
    "configs/aws_config.py",
    "configs/cache_vars.py",
    "configs/drf_spectacular.py"
)


if current_env == "PRODUCTION":
    from shop.settings.production import *  # noqa
elif current_env == "STAGING":
    from shop.settings.staging import *  # noqa
elif current_env == "DEVELOPMENT":
    from shop.settings.development import *  # noqa
else:
    raise ImproperlyConfigured("Set {} environment variable.".format(ENV_SETTING))

logging.captureWarnings(True)
