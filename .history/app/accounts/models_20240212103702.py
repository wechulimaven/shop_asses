from django.db import models
from django.conf import settings
from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.core.cache import cache

from utilities.utils import generate_hash

from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField

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
    display_name = models.CharField(
        _("display name"), max_length=150, validators=[validate_min_length]
    )
    email = models.EmailField(_("email address"), unique=True)
    avatar = models.ImageField(
        upload_to=avatar_file_name, max_length=254, blank=True, null=True
    )
    user_id = models.UUIDField(editable=False, unique=True, blank=True, null=True)
    phone_number = PhoneNumberField(
        _("phone number"),
    )
    is_account_verified = models.BooleanField(_("account verified"), default=False)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    interest = models.CharField(max_length=1500, blank=True, null=True)
    bio = models.CharField(max_length=1500, blank=True, null=True)
    occupation = models.CharField(max_length=50, blank=True, null=True)
    goal = models.CharField(max_length=1500, blank=True, null=True)
    is_blacklisted = models.BooleanField(_("account blacklisted"), default=False)
    subscriptions = models.ManyToManyField(
        "self",
        through="Subscription",
        verbose_name=_("subscriptions"),)
    objects = UserManager()

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

