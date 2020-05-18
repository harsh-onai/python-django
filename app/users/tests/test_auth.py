from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import status

TOKEN_URL = reverse('users:token')


def create_user(**param):
    return get_user_model().objects.create_user(**param)


class APITokeTest(TestCase):
    """Test user API"""

    def setUp(self):
        self.client = APIClient()

    def test_create_token_for_user(self):
        payload = {
            'email': 'harsh@gmail.com',
            'password': '123456',
            'name': 'harsh'
        }
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_invalid_credentials(self):
        create_user(email='harsh@gmail.com', password='123456')
        payload = {
            'email': 'harsh@gmail.com',
            'password': '12345',
            'name': 'harsh'
        }

        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_invalid_user(self):
        create_user(email='harsh@gmail.com', password='123456')
        payload = {
            'email': 'harsh12@gmail.com',
            'password': '12345'
        }

        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
