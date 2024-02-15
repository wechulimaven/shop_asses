from io import BytesIO
from django.utils.timezone import now
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
import json
import filetype
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
from datetime import datetime


logger = logging.getLogger(__name__)


def custom_error_response(errors, message):
    return {
        "status": False,
        "message": message if message is not None else _("An exception occured"),
        **errors}


def custom_exception_handler(exc, context):
    """Handle Django ValidationError as an accepted exception
    Must be set in settings:
    # ...
    'EXCEPTION_HANDLER': 'mtp.apps.common.drf.exception_handler',
    # ...
    For the parameters, see ``exception_handler``
    """
    if (
            isinstance(exc, DjangoValidationError)
            or isinstance(exc, IntegrityError)
            or isinstance(exc, ObjectDoesNotExist)
    ):
        if hasattr(exc, "message_dict"):
            logger.info("HERE===>")
            exc = DRFValidationError(detail=custom_error_response({"errors": exc.message_dict}))
        elif hasattr(exc, "message"):
            exc = DRFValidationError(detail=custom_error_response({"errors": [exc.message]}))
        elif hasattr(exc, "messages"):
            exc = DRFValidationError(detail=custom_error_response(
                {"errors": exc.messages},
                exc.messages))
        else:
            exc = DRFValidationError(detail=custom_error_response(
                {"errors": [str(exc)]},exc))
    elif type(exc) == Exception:
        logger.error(f"EXCEPTION <=======> {exc}")
        exc = APIException(detail=custom_error_response(
            exc.message,
            {"errors": exc.message}))

    return drf_exception_handler(exc, context)


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


def send_password_reset_otp(user):
    from apiclients.sms_client import SMSClient

    action="Password reset"
    otp_generator = OTPGenerator(request_type=action)
    token, expires_at = otp_generator.generate_otp(seconds=600, user=user)
    difference = expires_at - now()
    minutes = difference.total_seconds() / 60
    message = """
    Kindly use {token} to verify your {action}. Token expires in {expires_at} minutes
    """.format(
        token=token, expires_at=round(minutes), action=action
    )
    client = SMSClient(user.phone_number, message)
    client.send_sms()


def otp_verification(otp):
    from accounts.models import OneTimePassword

    token_qs = OneTimePassword.objects.filter(otp=otp).first()
    if not token_qs:
        raise DRFValidationError({"otp": ["Invalid OTP"]})
    user = token_qs.user
    otp_generator = OTPGenerator()
    otp_status = otp_generator.verify_otp(otp)
    logger.info(otp_status)
    if not otp_status:
        raise DRFValidationError({"otp": ["Invalid OTP"]})

    return user, otp_status
