import logging

from webhooks.pay_stack_webhook import PaystackWebhookProcessor

from .utils import send_template_email
from furl import furl
from cheruven.celery import app as celery_app
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


@celery_app.task(name="send_account_verification_mail")
def send_account_verification_mail(user_id, verification_code):
    from accounts.models import User

    user = User.objects.get_user(user_id)
    logger.info("Sending account verification email for user: {}".format(user.email))

    send_template_email(
        "account_verification.html",
        user.email,
        "Account Verification",
        **{
            "name": user.first_name,
            "account_name": user.email,
            "verification_code": verification_code,
            "expiration_time": get_expiration_time(),
        },
    )

    logger.info("Verfication email sent to follower: {}".format(user.email))


@celery_app.task(name="send_forgot_password_mail")
def send_forgot_password_mail(user_id, reset_token):
    user = User.objects.get_user(user_id)
    logger.info("Sending forgot password email for user: {}".format(user.email))

    reset_url = SITE_BASE_URL.copy().add(path=settings.PASSWORD_RESET_PATH)
    reset_url.add({"token": reset_token})

    send_template_email(
        "forgot_password.html",
        user.email,
        "Account Password Reset",
        **{
            "name": user.first_name,
            "reset_url": reset_url.url,
            "email_addr": user.email,
            "expiration_time": get_expiration_time(),
        },
    )

    logger.info("Forgot password email sent to user: {}".format(user.email))


@celery_app.task(name="handle_paystack_webhook_event")
def handle_paystack_webhook_event(event, data):
    webhook = PaystackWebhookProcessor(event, data)
    webhook.run()
