from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag

from recipe.serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list')


class APITest(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTest(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='harsh@gmail.com',
            password='harsh',
            name="Harsh"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def tags_retrieve_user(self):
        Tag.objects.create(users=self.user, name='Check 1')
        Tag.objects.create(users=self.user, name='Check 2')

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')

        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_get_loggedin_user_data(self):
        user = get_user_model().objects.create_user(
            email='harsh2345@gmail.com',
            password='harsh',
            name="Harsh"
        )
        Tag.objects.create(users=self.user, name='Check 1')
        Tag.objects.create(users=self.user, name='Check 2')
        Tag.objects.create(users=user, name='Should not come')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

        self.assertEqual(res.data[1]['name'], 'Check 1')
        self.assertEqual(res.data[0]['name'], 'Check 2')

    def test_tags_create_success(self):
        payload = {'name': 'Test tag'}
        self.client.post(TAGS_URL, payload)

        exists = Tag.objects.filter(
            users=self.user,
            name=payload['name']
        )
        self.assertTrue(exists)

    def test_tags_create_invalid(self):
        payload = {'name': ''}
        res = self.client.post(TAGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
