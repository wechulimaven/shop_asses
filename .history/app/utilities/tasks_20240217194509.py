import logging

from .utils import send_template_email
from furl import furl
from shop.celery import app as celery_app
from django.conf import settings
from accounts.models import User

logger = logging.getLogger(__name__)

SITE_BASE_URL = furl(settings.BASE_URL)


def get_expiration_time():
    return int(settings.CACHES["default"]["TIMEOUT"] / 60)


@celery_app.task(name="send_welcome_mail")
def send_welcome_mail(user_id):
    user = User.objects.get_user(user_id)
    logger.info("Sending welcome mail to: {}".format(user.email))

    send_template_email(
        "welcome_message.html",
        user.email,
        "Welcome Onboard",
        **{
            "name": user.first_name,
            "site_url": SITE_BASE_URL.url,
        },
    )

    logger.info("Welcome message sent to: {}".format(user.email))

@celery_app.task(name="send_sms")
def send_sms(user, message):
    logger.info("Sendingsms to: {}".format(phone))

    sms = SMSClient(
                    recepient=phone,
                    message=f'Dear {user.name} new order item was added.'
                )
                sms.send()

    logger.info("Sms sent essage sent to: {}".format(phone))
