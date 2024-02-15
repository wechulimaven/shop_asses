from django.utils.translation import gettext_lazy as _

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from utilities.custom_response import CustomResponse

from .serializers import (
    GoogleSocialAuthSerializer,
    OrderSerializer,
)
from .models import User
import logging

logger = logging.getLogger(__name__)


# Create your views here.


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


class AddOrderView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = OrderSerializer

    def get_serializer_context(self):
        return {"request": self.request}

    def get_serializer(self, *args, **kwargs):
        kwargs["context"] = self.get_serializer_context()
        return self.serializer_class(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        serializer = self.get_serializer