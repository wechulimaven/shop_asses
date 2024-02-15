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
    name = models.CharField(
        _("first name"), max_length=150, validators=[validate_min_length]
    )
    code = models.CharField(
        _("display name"), max_length=150, validators=[validate_min_length]
    )
    email = models.EmailField(_("email address"), unique=True)

    def __str__(self):
        return self.username


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)



class Order(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.item