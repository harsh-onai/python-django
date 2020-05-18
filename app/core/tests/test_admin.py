from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class Admin(TestCase):

    def setUp(self) -> None:
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email='admin@oaknorth.com',
            password='test@123')
        self.client.force_login(self.admin_user)
        self.user = get_user_model(). \
            objects.create_user(email='harsh@oaknorth.com',
                                password='password123',
                                name='Harsh Pratyush')

    def test_list_user(self):
        """Test user are listed"""
        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)

        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_change_page_admin(self):
        """Test user edit page works"""
        url = reverse('admin:core_user_change', args=[self.user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_create_user_page(self):
        """test for create user"""
        url = reverse('admin:core_user_add')
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
