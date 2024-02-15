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


class AddOrderView(A)