from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Order

User = get_user_model()

class UserModelTestCase(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword',
            name='Test User',
            code='TEST123',
            phone='1234567890'
        )
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.name, 'Test User')
        self.assertEqual(user.code, 'TEST123')
        self.assertEqual(user.phone, '1234567890')
        self.assertTrue(user.check_password('testpassword'))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

class OrderModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword',
            name='Test User',
            code='TEST123',
            phone='1234567890'
        )

    def test_create_order(self):
        order = Order.objects.create(
            customer=self.user,
            item='Test Item',
            amount=10.99
        )
        self.assertEqual(order.customer, self.user)
        self.assertEqual(order.item, 'Test Item')
        self.assertEqual(order.amount, 10.99)

    def test_order_str(self):
        order = Order.objects.create(
            customer=self.user,
            item='Test Item',
            amount=10.99
        )
        self.assertEqual(str(order), 'Test Item')

    def test_order_customer_cascade_delete(self):
        order = Order.objects.create(
            customer=self.user,
            item='Test Item',
            amount=10.99
        )
        user_id = self.user.id
        self.user.delete()
        # Check if order is deleted after user deletion
        self.assertFalse(Order.objects.filter(pk=order.pk).exists())
