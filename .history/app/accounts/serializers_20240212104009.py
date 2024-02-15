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

from utilities.utils import (
    register_social_user,
)


from .models import User
from utilities.choices import AUTH_PROVIDER

from services.social_auth import google


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


class UserBaseSerializer(serializers.ModelSerializer):
    interest = serializers.SerializerMethodField()
    goal = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "code",
            "email",
            "goal",
            "avatar",
            "user_id",
            "occupation",
            "bio",
            "phone_number",
        )
        read_only_fields = ("user_id", "is_blacklisted")

    def get_interest(self, obj):
        from ast import literal_eval

        return literal_eval(str(obj.interest))

    def get_goal(self, obj):
        from ast import literal_eval

        return literal_eval(str(obj.goal))


class MinorUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "avatar",
            "user_id",
        )


class UserAccountSerializer(UserBaseSerializer):
    confirm_password = serializers.CharField(
        write_only=True, required=True, allow_blank=False, allow_null=False
    )

    following = serializers.SerializerMethodField()
    followers = serializers.SerializerMethodField()
    no_of_following = serializers.SerializerMethodField()
    no_of_followers = serializers.SerializerMethodField()
    no_of_podcasts = serializers.SerializerMethodField()
    no_of_rooms = serializers.SerializerMethodField()
    no_of_prayer_journal = serializers.SerializerMethodField()

    class Meta(UserBaseSerializer.Meta):
        fields = UserBaseSerializer.Meta.fields + (
            "email",
            "password",
            "is_account_verified",
            "is_blacklisted",
            "confirm_password",
            "following",
            "followers",
            "no_of_followers",
            "no_of_following",
            "no_of_podcasts",
            "no_of_rooms",
            "no_of_prayer_journal",
        )
        read_only_fields = UserBaseSerializer.Meta.read_only_fields + (
            "avatar",
            "is_account_verified",
        )
        extra_kwargs = {"password": {"write_only": True}}

    def get_no_of_podcasts(self, obj):
        from podcasts.models import Podcast

        return Podcast.objects.get_user_podcasts(obj).count()

    def get_no_of_rooms(self, obj):
        from rooms.models import PrayerRoom

        return PrayerRoom.objects.get_user_rooms(obj).count()

    def get_no_of_prayer_journal(self, obj):
        from journals.models import PrayerJournal

        return PrayerJournal.objects.filter(user=obj).count()

    def get_no_of_following(self, obj):
        return User.objects.get_user_following(user=obj).count()

    def get_no_of_followers(self, obj):
        return User.objects.get_user_followers(followers=obj).count()

    def get_following(self, obj):
        return MinorUserSerializer(
            User.objects.get_user_following(user=obj), many=True
        ).data

    def get_followers(self, obj):
        return MinorUserSerializer(
            User.objects.get_user_followers(followers=obj), many=True
        ).data

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

    def validate(self, data):
        password = data.get("password")
        confirm_password = data.get("confirm_password")

        if password != confirm_password:
            raise serializers.ValidationError(
                {"password": _("Passwords do not match.")}
            )
        data.pop("confirm_password")
        return data

    def create(self, validated_data):
        with transaction.atomic():
            # referral_code = validated_data.pop("referral_code", None)
            user = User.objects.create_user(**validated_data)
            token = Token.objects.get_or_create(user=user)
            user.send_verification_email()
        return token, user


class UserAccountUpdateSerializer(UserBaseSerializer):
    interest = serializers.MultipleChoiceField(
        choices=UserInterest.choices, required=False, allow_blank=True, allow_null=True
    )
    goal = serializers.MultipleChoiceField(
        choices=UserGoals.choices, required=False, allow_blank=True, allow_null=True
    )
    occupation = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )
    bio = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    avatar = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    phone_number = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )

    def validate_phone_number(self, value):
        if value and value[:3] != "254":
            raise serializers.ValidationError(
                _("Number must be in the format 254xxxxxxxxx")
            )

        if value and len(value) != 12:
            raise serializers.ValidationError(
                _("Number must be 12 digits - including phone code")
            )

        return value

    def validate_interest(self, interest):
        if interest:
            return list(interest)

    def validate_goal(self, interest):
        if interest:
            return list(interest)

    class Meta(UserBaseSerializer.Meta):
        pass

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get("first_name", instance.first_name)
        instance.last_name = validated_data.get("last_name", instance.last_name)
        instance.goal = validated_data.get("goal", instance.goal)
        instance.interest = validated_data.get("interest", instance.interest)
        instance.avatar = validated_data.get("avatar", instance.avatar)
        instance.bio = validated_data.get("bio", instance.bio)
        instance.occupation = validated_data.get("occupation", instance.occupation)
        instance.phone_number = validated_data.get(
            "phone_number", instance.phone_number
        )
        instance.save()
        return instance


class GoogleSocialAuthSerializer(serializers.Serializer):
    credential = serializers.CharField()
    clientId = serializers.CharField(required=False, allow_blank=True)
    select_by = serializers.CharField(required=False, allow_blank=True)
    g_csrf_token = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        auth_token = attrs.get("credential")
        user_data = google.Google.validate(auth_token)
        try:
            user_data["sub"]
        except Exception:
            raise serializers.ValidationError(
                "The token is invalid or expired. Please login again."
            )

        if user_data["aud"] != os.getenv("GOOGLE_CLIENT_ID"):
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


class ChangeUserAccountPasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True)

    def validate_old_password(self, value):
        instance = self.context["request"].user
        if not instance.check_password(value):
            raise serializers.ValidationError(_("Invalid password"))
        return value

    def validate_new_password(self, value):
        try:
            django_validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value

    def update(self, instance, validated_data):
        instance.set_password(validated_data["new_password"])
        instance.save()
        return instance


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        if not User.objects.user_exists(value):
            raise serializers.ValidationError(_("Invalid email address."))
        return value

    def create(self, validated_data):
        email_addr = validated_data["email"]
        user = User.objects.get_user(validated_data["email"])
        send_password_reset_otp(user)
        return email_addr


class VerifyOtpSerializer(serializers.Serializer):
    otp = serializers.CharField(write_only=True, required=True)

    def validate_otp(self, value):
        user, status = otp_verification(value)
        if not user:
            raise serializers.ValidationError(_("OTP does not belong to this user"))
        return user


# TODO: Finish on OTP verification before password reset


class ResetUserAccountPasswordSerializer(serializers.Serializer):
    otp = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True)

    def validate_otp(self, value):
        user, status = otp_verification(value)
        if not user:
            raise serializers.ValidationError(_("OTP does not belong to this user"))
        return user

    def validate_new_password(self, value):
        try:
            django_validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value

    def update(self, instance, validated_data):
        instance = validated_data["otp"]
        instance.set_password(validated_data["new_password"])
        instance.save()
        return instance


class SubscriptionSerializer(serializers.Serializer):
    follower_email = serializers.EmailField(required=True)

    def validate_follower_email(self, value):
        user = self.context["request"].user
        if user.email == value:
            raise serializers.ValidationError(_("User cannot subscribe to self."))
        return value

    def create(self, validated_data):
        follower_email = validated_data["follower_email"]
        user = self.context["request"].user

        try:
            follower = User.objects.get_user(follower_email)
            subscription = Subscription.objects.create_subscription(
                follower_email, user
            )
            # send_you_have_subscribed_email.delay(
            #     user_id=user.id,
            #     follower_id=follower.id)
            send_you_have_subscribed_email(user_id=user.id, follower_id=follower.id)
            return subscription
        except IntegrityError:
            raise serializers.ValidationError(
                {
                    "follower_email": [
                        _(
                            "User has already subscribed to follower {}.".format(
                                follower_email
                            )
                        )
                    ]
                }
            )

    def delete(self, validated_data):
        follower_email = validated_data["follower_email"]
        user = self.context["request"].user
        follower = User.objects.get_user(follower_email)
        # send_you_have_unsubscribed_email.delay(
        #     user_id=user.id,
        #     follower_id=follower.id)
        send_you_have_unsubscribed_email(user_id=user.id, follower_id=follower.id)
        Subscription.objects.delete_subscription(follower_email, user)
