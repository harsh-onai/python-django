from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('users:create')
ME_URL = reverse('users:me')


def create_user(**param):
    return get_user_model().objects.create_user(**param)


class PublicUserApiTest(TestCase):
    """Test user API"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        payload = {
            'email': 'harsh@gmail.com',
            'password': '12345',
            'name': 'harsh'
        }

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_already_exists(self):
        payload = {
            'email': 'harsh@gmail.com',
            'password': '12345',
            'name': 'harsh'
        }
        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        payload = {
            'email': 'harsh@gmail.com',
            'password': '1234',
            'name': 'harsh'
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_retrieve_user_unauth(self):
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserAPITest(TestCase):

    def setUp(self):
        self.user = create_user(
            email='harsh@gmail.com',
            password='harsh',
            name="Harsh"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def retrieve_profile(self):
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'email': 'harsh@gmail.com',
            'name': 'Harsh'
        })

    def post_method_not_allowed(self):
        res = self.client.post(ME_URL, {})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_profile(self):
        payload = {
            'name': 'Harsh Pratyush'
        }

        self.client.patch(ME_URL, payload)
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])

    def test_update_profile_without_change(self):
        payload = {}
        self.client.patch(ME_URL, payload)
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, self.user.name)
