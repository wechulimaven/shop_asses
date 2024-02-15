from django.db import models
from django.conf import settings
from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.core.cache import cache

from utilities.utils import generate_hash

from rest_framework.authtoken.models import Token
from django.utils.translation import gettext_lazy as _

from utilities.validators import validate_min_length
from utilities.utils import (
    avatar_file_name,)
from utilities.base_model import BaseModel
from utilities.utils import generate_link, account_activation_token



import logging

logger = logging.getLogger(__name__)


class User(AbstractUser):
    first_name = models.CharField(
        _("first name"), max_length=150, validators=[validate_min_length]
    )
    last_name = models.CharField(
        _("last name"), max_length=150, validators=[validate_min_length]
    )
    code = models.CharField(
        _("display name"), max_length=150, validators=[validate_min_length]
    )

    def __str__(self):
        return self.username

    def send_verification_email(self):
        verification_link = generate_link(self)
        from utilities.tasks import send_account_verification_mail
        logger.info(f"User details ==============> ${self.id}")
        logger.info(f"User verification link ==============> ${verification_link}")
        send_account_verification_mail.run(self.id, verification_link)

    def check_user_verification_token(self, token):
        return account_activation_token.check_token(self, token)

    def verify_account(self, token):
        from utilities.tasks import send_welcome_mail
        if self.check_user_verification_token(token):
            self.is_account_verified = True
            self.save()

            send_welcome_mail.delay(self.id)

            return True
    def send_reset_token_email(self):
        reset_token = generate_hash(self.email)
        # cache.set(reset_token, self.email)
        from utilities.tasks import send_forgot_password_mail

        send_forgot_password_mail.run(self.id, reset_token)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

