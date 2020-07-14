from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient, Recipe

from recipe.serializers import IngredientSerializer

INGREDIENT_URL = reverse('recipe:ingredient-list')


class PublicAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        res = self.client.get(INGREDIENT_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_required_create(self):
        res = self.client.post(INGREDIENT_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateAPITest(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='harsh@gmail.com',
            password='harsh',
            name="Harsh"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_ingredient_list(self):
        """Test """
        Ingredient.objects.create(users=self.user, name='Rum')
        Ingredient.objects.create(users=self.user, name='Tequila')
        Ingredient.objects.create(users=self.user, name='Beer')

        res = self.client.get(INGREDIENT_URL)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_get_loggedin_user_data(self):
        user = get_user_model().objects.create_user(
            email='harsh2345@gmail.com',
            password='harsh',
            name="Harsh"
        )
        Ingredient.objects.create(users=self.user, name='Check 1')
        Ingredient.objects.create(users=self.user, name='Check 2')
        Ingredient.objects.create(users=user, name='Should not come')

        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

        self.assertEqual(res.data[1]['name'], 'Check 1')
        self.assertEqual(res.data[0]['name'], 'Check 2')

    def test_create_user_sucess(self):
        payload = {'name': 'Garlic'}
        self.client.post(INGREDIENT_URL, payload)

        exists = Ingredient.objects.filter(
            users=self.user,
            name=payload['name']
        ).exists()
        self.assertTrue(exists)

    def test_ingredient_create_invalid(self):
        payload = {'name': ''}
        res = self.client.post(INGREDIENT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_ingredient_assigned(self):
        ing1 = Ingredient.objects.create(users=self.user, name='Non veg')
        ing2 = Ingredient.objects.create(users=self.user, name='Veg')
        ing3 = Ingredient.objects.create(users=self.user, name='Low Fat')

        recipe = Recipe.objects.create(
            title='Chicken Butter Masala',
            time_minutes=30,
            price=300,
            users=self.user
        )

        recipe.ingredients.add(ing1)
        recipe.ingredients.add(ing2)

        res = self.client.get(INGREDIENT_URL, {'assigned_only': 1})
        serializer1 = IngredientSerializer(ing1)
        serializer2 = IngredientSerializer(ing2)
        serializer3 = IngredientSerializer(ing3)

        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

    def test_retrieve_ingredient_assigned_unique(self):
        ing1 = Ingredient.objects.create(users=self.user, name='Non veg')
        ing2 = Ingredient.objects.create(users=self.user, name='Veg')
        Ingredient.objects.create(users=self.user, name='Low Fat')

        recipe = Recipe.objects.create(
            title='Chicken Butter Masala',
            time_minutes=30,
            price=300,
            users=self.user
        )

        recipe2 = Recipe.objects.create(
            title='Panner',
            time_minutes=30,
            price=300,
            users=self.user
        )

        recipe.ingredients.add(ing1)
        recipe2.ingredients.add(ing2)
        recipe2.ingredients.add(ing1)

        res = self.client.get(INGREDIENT_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 2)
