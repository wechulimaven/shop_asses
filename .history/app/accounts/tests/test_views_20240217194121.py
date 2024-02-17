from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from accounts.models import User
from accounts.serializers import GoogleSocialAuthSerializer, OrderSerializer


class GoogleSocialAuthViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("google-social-auth")

    def test_google_social_auth_valid(self):
        # Assuming serializer works correctly and returns a token
        data = {"auth_token": "4/0AeaYSHCjkuqIVl5d_T6r5CcVxmTB1JrLDzSg5rBlWZoNdL1vdI0tbiMCI2hBCpSkKaJSjA"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)
        # Assuming token can be used to retrieve user
        token = response.data["token"]
        user = Token.objects.get(key=token).user
        self.assertIsInstance(user, User)


class AddOrderViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("add-order")

    def test_add_order_valid(self):
        # Assuming authentication is not required for adding orders
        data = {"order_field": "order_value"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Assuming CustomResponse success_response() method is well implemented
        self.assertIn("order", response.data)
        self.assertEqual(response.data["order"]["order_field"], "order_value")
