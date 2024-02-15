from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from utilities.custom_response import CustomResponse

from .serializers import (
    TokenSerializer,
    GoogleSocialAuthSerializer,
    UserAccountSerializer)
from .models import User
import logging

logger = logging.getLogger(__name__)


# Create your views here.
class TokenLoginView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = TokenSerializer

    def get_serializer_context(self):
        return {"request": self.request}

    def get_serializer(self, *args, **kwargs):
        kwargs["context"] = self.get_serializer_context()
        return self.serializer_class(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token, user = serializer.save()
        serializer = UserAccountSerializer(user)

        kwargs["user"] = serializer.data
        kwargs["token"] = token.key
        response = CustomResponse(**kwargs)
        return response.success_response()


class TokenLogoutView(APIView):
    serializer_class = TokenSerializer

    def get_serializer_context(self):
        return {"request": self.request}

    def get_serializer(self, *args, **kwargs):
        kwargs["context"] = self.get_serializer_context()
        return self.serializer_class(*args, **kwargs)

    def delete(self, request, *args, **kwargs):
        serializer = self.get_serializer()
        serializer.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AccountRegistrationView(CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = UserAccountSerializer

    def get_serializer_context(self):
        return {"request": self.request}

    def get_serializer(self, *args, **kwargs):
        kwargs["context"] = self.get_serializer_context()
        return self.serializer_class(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token, user = serializer.save()
        serializer = UserAccountSerializer(user)
        kwargs["user"] = serializer.data
        kwargs["token"] = str(token[0])
        response = CustomResponse(**kwargs)
        return response.success_response()


class GoogleSocialAuthView(APIView):
    permission_classes = ()

    serializer_class = GoogleSocialAuthSerializer

    def post(self, request):
        """

        POST with "auth_token"

        Send an idtoken as from google to get user information

        """

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.save()
        get_token = Token.objects.get(key=token["token"])
        return Response({**token}, status=status.HTTP_200_OK)


class ChangeAccountPasswordView(APIView):
    serializer_class = ChangeUserAccountPasswordSerializer
    permission_classes = (IsAuthenticated,)

    def get_serializer_context(self):
        return {"request": self.request}

    def get_serializer(self, *args, **kwargs):
        kwargs["context"] = self.get_serializer_context()
        return self.serializer_class(*args, **kwargs)

    def put(self, request, *args, **kwargs):
        serializer = self.get_serializer(instance=self.request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": _("User account password changed successfully.")})


class ForgotPasswordView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = ForgotPasswordSerializer

    def get_serializer_context(self):
        return {"request": self.request}

    def get_serializer(self, *args, **kwargs):
        kwargs["context"] = self.get_serializer_context()
        return self.serializer_class(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.save()
        return Response(
            {
                "message": _(
                    "Your password reset token sent to email {} successfully.".format(
                        email
                    )
                )
            }
        )


class ResetAccountPasswordView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = ResetUserAccountPasswordSerializer

    def get_serializer_context(self):
        return {"request": self.request}

    def get_serializer(self, *args, **kwargs):
        kwargs["context"] = self.get_serializer_context()
        return self.serializer_class(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(instance=self.request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": _("Your password has been resetted successfully.")})


class GetAllUsers(APIView):

    permission_classes = (IsAuthenticated,)
    serializer_class = UserAccountSerializer

    def get_serializer_context(self):
        return {"request": self.request}

    def get_serializer(self, *args, **kwargs):
        kwargs["context"] = self.get_serializer_context()
        return self.serializer_class(*args, **kwargs)

    def __get_active_users(self):
        return User.objects.get_active_users_queryset()

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.__get_active_users(), many=True)
        kwargs["users"] = serializer.data
        response = CustomResponse(**kwargs)
        return response.success_response()


class GetLoggedInUserDetail(APIView):

    permission_classes = (IsAuthenticated,)
    serializer_class = UserAccountSerializer

    def get_serializer_context(self):
        return {"request": self.request}

    def get_serializer(self, *args, **kwargs):
        kwargs["context"] = self.get_serializer_context()
        return self.serializer_class(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.request.user)
        kwargs["user"] = serializer.data
        response = CustomResponse(**kwargs)
        return response.success_response()


class GetUserDetail(APIView):

    permission_classes = (AllowAny,)
    serializer_class = UserAccountSerializer

    def get_serializer_context(self):
        return {"request": self.request}

    def get_serializer(self, *args, **kwargs):
        kwargs["context"] = self.get_serializer_context()
        return self.serializer_class(*args, **kwargs)

    def __get_user(self, id):
        return User.objects.get(id=id)

    def get(self, request, id, *args, **kwargs):
        serializer = self.get_serializer(self.__get_user(id))
        kwargs["user"] = serializer.data
        response = CustomResponse(**kwargs)
        return response.success_response()


class UserSubscriptionView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = SubscriptionSerializer

    def get_serializer_context(self):
        return {"request": self.request}

    def get_serializer(self, *args, **kwargs):
        kwargs["context"] = self.get_serializer_context()
        return self.serializer_class(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {
                "message": _(
                    "User successfully subscribed to {}".format(
                        serializer.validated_data["follower_email"]
                    )
                )
            }
        )

    def delete(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        serializer.delete(serializer.validated_data)
        return Response(
            {
                "message": _(
                    "User successfully unsubscribed from brand {}".format(
                        serializer.validated_data["follower_email"]
                    )
                )
            }
        )