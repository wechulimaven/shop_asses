from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.utils import IntegrityError
from django.contrib.auth import authenticate

from rest_framework.exceptions import APIException, ValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.serializers import ValidationError as DRFValidationError
from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.authtoken.models import Token

import os
import six
import uuid
import logging
import hashlib


from django.utils import timezone
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import PasswordResetTokenGenerator


logger = logging.getLogger(__name__)


def custom_error_response(errors, message):
    return {
        "status": False,
        "message": message if message is not None else _("An exception occured"),
        **errors}


def get_uuid() -> str:
    ulid = uuid.uuid4()
    return ulid.hex


def generate_hash(val):
    return hashlib.sha256(get_uuid().encode() + val.encode()).hexdigest()



class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.id) + six.text_type(timestamp) +
            six.text_type(user.email)
        )


account_activation_token = AccountActivationTokenGenerator()


def generate_link(user):
    url = settings.BASE_URL
    uid = urlsafe_base64_encode(force_bytes(user)),
    token = account_activation_token.make_token(user)

    from requests.models import PreparedRequest
    params = {'uid': uid, 'token': token}
    url = url + '/account/verify-email'
    req = PreparedRequest()
    req.prepare_url(url, params)

    return req.url


def send_template_email(template, email, subject, **context):
    if not isinstance(email, list):
        email = [email]
    context["instagram_url"] = settings.SOCIAL_MEDIA_INSTAGRAM_URL
    context["facebook_url"] = settings.SOCIAL_MEDIA_FACEBOOK_URL
    context["linkedin_url"] = settings.SOCIAL_MEDIA_LINKEDIN_URL
    context["twitter_url"] = settings.SOCIAL_MEDIA_TWITTER_URL

    html_message = render_to_string(template, context)
    plain_message = strip_tags(html_message)

    send_mail(
        subject,
        plain_message,
        "Cheruven <{}>".format(settings.EMAIL_HOST_USER),
        email,
        html_message=html_message,
    )


def register_social_user(provider, user_id, email, name):
    from accounts.models import User
    from .tasks import send_welcome_mail
    
    filtered_user_by_email = User.objects.filter(email=email)

    if filtered_user_by_email.exists():
        user = filtered_user_by_email.first()
        if not user.is_active:
            raise ValidationError({
                "user": ["user is inactive"]
            })
        Token.objects.filter(user=user).delete()
        token, _ = Token.objects.get_or_create(user=user)
        user.last_login = timezone.now()
        user.save()

        return {"username": user.email, "token": token.key}
    else:
        user = User.objects.create_user(
            email=email,
            password=os.getenv("DEFAULT_SOCIAL_SECRET_PASSWORD"),
            is_account_verified=True,
            first_name=name,
        )
        user.is_account_verified = True
        user.auth_provider = provider
        user.save()
        registered_user = authenticate(
            username=email, password=os.getenv("DEFAULT_SOCIAL_SECRET_PASSWORD")
        )
        Token.objects.filter(user=user).delete()
        token, _ = Token.objects.get_or_create(user=registered_user)
        send_welcome_mail.delay(registered_user.id)
        return {"username": registered_user.email, "token": token.key}
