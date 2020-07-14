from unittest.mock import patch, MagicMock

from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models


def create_mock_user(email='test@gmail.com', password='password'):
    """Create a mock user"""
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):

    def test_create_user_with_email_success(self):
        """Test creating a new user with email"""
        email = 'harsh.pratyush@gmail.com'
        password = 'pass123'
        user = get_user_model(). \
            objects.create_user(email=email, password=password)

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_normalize_password(self):
        email = 'harsh.pratyush@GMAIL.COM'
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
        user = get_user_model().objects.create_superuser('admin@gmail.com',
                                                         'test@123')
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        """test tag"""
        tag = models.Tag.objects.create(
            users=create_mock_user(),
            name='Velle'
        )

        self.assertEqual(str(tag), tag.name)

    def test_ingredient_str(self):
        """Test"""
        ingredient = models.Ingredient.objects.create(
            users=create_mock_user(),
            name='Cucumber'
        )

        self.assertEqual(str(ingredient), ingredient.name)

    def test_recipe_str(self):
        """__str__ resp"""

        recipe = models.Recipe.objects.create(
            users=create_mock_user(),
            title='Burger',
            price=23.28,
            time_minutes=10
        )

        self.assertEqual(str(recipe), recipe.title)

    @patch('uuid.uuid4')
    def test_recipe_file_name_uuid(self, mock_uuid: MagicMock):
        """Test file location"""
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid

        file_path = models.recipe_image_file_path(None, 'sample.png')

        exp_path = f'uploads/recipe/{uuid}.png'

        self.assertEqual(file_path, exp_path)
