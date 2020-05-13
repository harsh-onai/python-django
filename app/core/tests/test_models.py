from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):

    def test_create_user_with_email_success(self):
        """Test creating a new user with email"""
        email = 'harsh.pratyush@oaknorth.ai'
        password = 'pass123'
        user = get_user_model(). \
            objects.create_user(email=email, password=password)

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_normalize_password(self):
        email = 'harsh.pratyush@OAKNORTH.AI'
        password = 'pass123'
        user = get_user_model().objects. \
            create_user(email=email, password=password)
        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Test for raise error for email == null"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, '12345')

    def test_create_super_user(self):
        """test for new super user"""
        user = get_user_model().objects.create_superuser('admin@oaknorth.com',
                                                         'test@123')
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
