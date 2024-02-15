import os
import logging
from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv
from split_settings.tools import include, optional


load_dotenv()


ENV_SETTING = "ENVIRONMENT_SETTING"


current_env = os.getenv(ENV_SETTING, "DEVELOPMENT")

include(
    "vars/logging.py",
    "vars/celery_vars.py",
    "vars/rest_framework.py",
    "vars/aws_config.py",
    "vars/cache_vars.py",
    "vars/drf_spectacular.py"
)


if current_env == "PRODUCTION":
    from cheruven.settings.production import *  # noqa
elif current_env == "STAGING":
    from cheruven.settings.staging import *  # noqa
elif current_env == "DEVELOPMENT":
    from cheruven.settings.development import *  # noqa
else:
    raise ImproperlyConfigured("Set {} environment variable.".format(ENV_SETTING))

logging.captureWarnings(True)
