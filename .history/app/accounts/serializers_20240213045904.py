from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.authtoken.models import Token

import os

from django.utils.translation import gettext_lazy as _
from django.contrib.auth.password_validation import (
    validate_password as django_validate_password,
)
from django.contrib.auth import authenticate
from django.utils import timezone
from django.db import IntegrityError, transaction
from django.core.exceptions import ValidationError as DjangoValidationError
from django.conf import settings
from services.sms.sms_client import SMSClient

from utilities.utils import (
    register_social_user,
)


from .models import User, Order
from utilities.choices import AUTH_PROVIDER

from services.social_auth import google

import logging

logger = logging.getLogger(__name__)


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(trim_whitespace=False, write_only=True)

    def validate(self, data):
        username = data.get("username")
        password = data.get("password")

        if password and username:
            user = authenticate(
                request=self.context.get("request"),
                username=username,
                password=password,
            )
            if not user:
                msg = _("Unable to log in with provided credentials.")
                raise serializers.ValidationError(msg, code="authorization")
            if user.is_staff:
                msg = _("Unable to log in with provided credentials.")
                raise serializers.ValidationError(msg, code="authorization")
        else:
            msg = _('Must include "username" and "password".')
            raise serializers.ValidationError(msg, code="authorization")

        data["user"] = user
        return data

    def create(self, validated_data):
        user = validated_data["user"]
        token, _ = Token.objects.get_or_create(user=user)
        user.last_login = timezone.now()
        user.save()
        return token, user

    def delete(self):
        user = self.context["request"].user
        Token.objects.filter(user=user).delete()


class UserAccountSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            "id",
            "name",
            "code",
            "email",
        )
        read_only_fields = ("id", "is_active", 'code')
    
    def validate_password(self, value):
        try:
            django_validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value

    def validate_email(self, value):
        user_qs = User.objects.filter(email__iexact=value)
        if user_qs.exists():
            raise serializers.ValidationError(
                "user with this email address already exists."
            )
        else:
            return value

    def create(self, validated_data):
        with transaction.atomic():
            user = User.objects.create_user(**validated_data)
            token = Token.objects.get_or_create(user=user)
            user.send_verification_email()
        return token, user


class GoogleSocialAuthSerializer(serializers.Serializer):
    credential = serializers.CharField()
    # clientId = serializers.CharField(required=False, allow_blank=True)
    # select_by = serializers.CharField(required=False, allow_blank=True)
    # g_csrf_token = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        auth_token = attrs.get("credential")
        user_data = google.Google.validate(auth_token)
        try:
            logger.info(user_data)
            user_data["sub"]
        except Exception:
            raise serializers.ValidationError(
                "The token is invalid or expired. Please login again."
            )

        if user_data["aud"] != os.getenv("SOCIAL_AUTH_GOOGLE_OAUTH2_KEY"):
            raise AuthenticationFailed("Oops, unrecognised sender. Who are you?")

        attrs["user_id"] = user_data["sub"]
        attrs["email"] = user_data["email"]
        attrs["name"] = user_data["name"]
        attrs["provider"] = AUTH_PROVIDER.GMAIL

        return attrs

    def create(self, validated_data):
        return register_social_user(
            provider=validated_data.get("provider"),
            user_id=validated_data.get("user_id"),
            email=validated_data.get("email"),
            name=validated_data.get("name"),
        )


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'
        verbose_name = 'Orders'
        verbose_name_plural = 'Order'

    def create(self, validated_data):
        try:
            order_obj= super().create(validated_data)
            user = order_obj.user
            if order_obj.user.phone:
                sms = SMSClient(
                    recepient=user.phone
                    message='Dear {user.name} '
                )
                sms.send()
        except Exception :
            raise 

