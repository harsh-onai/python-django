import tempfile
import os

from PIL import Image
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag, Ingredient

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPE_URL = reverse('recipe:recipe-list')


def image_upload_url(recipe_id):
    return reverse('recipe:recipe-upload-image', args=[recipe_id])


def detail_url(recipe_id):
    return reverse('recipe:recipe-detail', args=[recipe_id])


def aggregate_url(recipe_id):
    return reverse('recipe:recipe-get-aggregate', args=[recipe_id])


# RECIPE_AGG_URL = reverse('recipe:recipe-get-aggregate')


def sample_recipe(user, **params):
    """create return sample"""
    defaults = {
        'title': 'sample recipe',
        'time_minutes': 10,
        'price': 5.00
    }
    defaults.update(params)

    return Recipe.objects.create(users=user, **defaults)


def sample_tag(user, name='Chinese'):
    return Tag.objects.create(users=user, name=name)


def sample_ingredient(user, name='Ginger'):
    return Ingredient.objects.create(users=user, name=name)


class PublicAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_unauthroized(self):
        res = self.client.get(RECIPE_URL)
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

    def test_get_recipe(self):
        """test recipe"""
        sample_recipe(self.user)
        sample_recipe(self.user)

        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_authorized_data(self):
        user2 = get_user_model().objects.create_user(
            email='harsh123@gmail.com',
            password='harsh',
            name="Harsh"
        )

        sample_recipe(user2)
        sample_recipe(self.user)

        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.filter(users=self.user).order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_detail_recipe(self):
        """Test for single data"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serialized_data = RecipeDetailSerializer(recipe)

        self.assertEqual(res.data, serialized_data.data)

    def test_create_basic_recipe(self):
        payload = {
            'title': 'Maggi',
            'time_minutes': 2,
            'price': 300
        }

        res = self.client.post(RECIPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data['id'])

        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_create_recipe_ingredient(self):
        ingredient = sample_ingredient(user=self.user, name='Maggi massala')
        ingredient1 = sample_ingredient(user=self.user, name='Maggi Seasoning')
        payload = {
            'title': 'Maggi',
            'time_minutes': 2,
            'price': 300,
            'ingredients': [ingredient.id, ingredient1.id]
        }

        res = self.client.post(RECIPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data['id'])
        ingredients = recipe.ingredients.all()
        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient, ingredients)
        self.assertIn(ingredient1, ingredients)

    def test_create_recipe_tag(self):
        tag = sample_tag(user=self.user, name='Maggi massala')
        tag1 = sample_tag(user=self.user, name='Maggi Seasoning')
        payload = {
            'title': 'Maggi',
            'time_minutes': 2,
            'price': 300,
            'tags': [tag.id, tag1.id]
        }

        res = self.client.post(RECIPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data['id'])
        tags = recipe.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag, tags)
        self.assertIn(tag1, tags)

    def test_patch_recipe(self):
        """Patch recipe"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))
        new_tag = sample_tag(user=self.user, name='Maggi Seasoning')
        payload = {
            'title': 'Maggi', 'tags': [new_tag.id]
        }
        self.client.patch(detail_url(recipe.id), payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 1)
        self.assertIn(new_tag, tags)

    def test_put_recipe(self):
        """Patch recipe"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))
        new_tag = sample_tag(user=self.user, name='Maggi Seasoning')
        payload = {
            'title': 'Maggi', 'tags': [new_tag.id],
            'time_minutes': 10, 'price': 200
        }
        self.client.put(detail_url(recipe.id), payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.time_minutes, payload['time_minutes'])
        tags = recipe.tags.all()
        ingredient = recipe.ingredients.all()
        self.assertEqual(len(tags), 1)
        self.assertEqual(len(ingredient), 0)
        self.assertIn(new_tag, tags)


class RecipeImageTest(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='harsh@gmail.com',
            password='harsh',
            name="Harsh"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.recipe = sample_recipe(user=self.user)

    def tearDown(self):
        self.recipe.image.delete()

    def test_upload_image(self):
        url = image_upload_url(self.recipe.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            img = Image.new('RGB', (10, 10), )
            img.save(ntf, format='JPEG')
            ntf.seek(0)
            res = self.client.post(url, {'image': ntf}, format='multipart')
            self.recipe.refresh_from_db()
            self.assertEqual(res.status_code, status.HTTP_200_OK)
            self.assertEqual('image uploaded', res.data)
            self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_failed(self):
        url = image_upload_url(self.recipe.id)
        res = self.client.post(url, {'image': 'check'}, format='multipart')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class FilterTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='harsh@gmail.com',
            password='harsh',
            name="Harsh"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.recipe = sample_recipe(user=self.user)

    def test_filter_recipe_tags(self):
        recipe1 = sample_recipe(user=self.user, title="Chicken BTM")
        recipe2 = sample_recipe(user=self.user, title="Chicken Curry")
        recipe3 = sample_recipe(user=self.user, title="Paneer BTM")

        tag_chicken = sample_tag(user=self.user, name="Chicken")
        tag_paneer = sample_tag(user=self.user, name="Paneer")

        recipe1.tags.add(tag_chicken)
        recipe2.tags.add(tag_chicken)
        recipe3.tags.add(tag_paneer)

        res = self.client.get(RECIPE_URL,
                              {'tags': f'{tag_chicken.id}'})

        serializer1 = RecipeSerializer(recipe1)
        serializer2 = RecipeSerializer(recipe2)
        serializer3 = RecipeSerializer(recipe3)

        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

    def test_filter_recipe_ingredient(self):
        recipe1 = sample_recipe(user=self.user, title="Chicken BTM")
        recipe2 = sample_recipe(user=self.user, title="Chicken Curry")
        recipe3 = sample_recipe(user=self.user, title="Paneer BTM")

        ingredient_chicken = sample_ingredient(user=self.user, name="Chicken")
        ingredient_paneer = sample_ingredient(user=self.user, name="Paneer")

        recipe1.ingredients.add(ingredient_chicken)
        recipe2.ingredients.add(ingredient_chicken)
        recipe3.ingredients.add(ingredient_paneer)

        res = self.client.get(RECIPE_URL,
                              {'ingredients': f'{ingredient_chicken.id}'})

        serializer1 = RecipeSerializer(recipe1)
        serializer2 = RecipeSerializer(recipe2)
        serializer3 = RecipeSerializer(recipe3)

        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

    def test_filter_with_tag_recipe(self):
        recipe1 = sample_recipe(user=self.user, title="Chicken BTM")
        recipe2 = sample_recipe(user=self.user, title="Fish Curry")
        recipe3 = sample_recipe(user=self.user, title="Paneer BTM")

        tag_chicken = sample_tag(user=self.user, name="Non veg")
        tag_paneer = sample_tag(user=self.user, name="Paneer")

        ingredient_chicken = sample_ingredient(user=self.user, name="Chicken")
        ingredient_fish = sample_ingredient(user=self.user, name="Fish")
        ingredient_paneer = sample_ingredient(user=self.user, name="Paneer")

        recipe1.ingredients.add(ingredient_chicken)
        recipe2.ingredients.add(ingredient_fish)
        recipe3.ingredients.add(ingredient_paneer)

        recipe1.tags.add(tag_chicken)
        recipe2.tags.add(tag_chicken)
        recipe3.tags.add(tag_paneer)

        res = self.client.get(RECIPE_URL,
                              {'tags': f'{tag_chicken.id}',
                               'ingredients': f'{ingredient_chicken.id}'})

        serializer1 = RecipeSerializer(recipe1)
        serializer2 = RecipeSerializer(recipe2)
        serializer3 = RecipeSerializer(recipe3)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

    def test_aggregate_data(self):
        recipe1 = sample_recipe(user=self.user, title="Chicken BTM")
        recipe2 = sample_recipe(user=self.user, title="Fish Curry")
        recipe3 = sample_recipe(user=self.user, title="Paneer BTM")

        tag_chicken = sample_tag(user=self.user, name="Non veg")
        tag_paneer = sample_tag(user=self.user, name="Paneer")

        ingredient_chicken = sample_ingredient(user=self.user, name="Chicken")
        ingredient_fish = sample_ingredient(user=self.user, name="Fish")
        ingredient_paneer = sample_ingredient(user=self.user, name="Paneer")

        recipe1.ingredients.add(ingredient_chicken)
        recipe2.ingredients.add(ingredient_fish)
        recipe3.ingredients.add(ingredient_paneer)

        recipe1.tags.add(tag_chicken)
        recipe2.tags.add(tag_chicken)
        recipe3.tags.add(tag_paneer)

        res = self.client.get(aggregate_url(recipe1.id))
        self.assertEqual(recipe1.title, res.data['recipe'])
        self.assertEqual(recipe1.tags.all().count(), res.data['noOfTags'])
        self.assertEqual(recipe1.ingredients.all().count(),
                         res.data['noOfIngredients'])

        res = self.client.get(aggregate_url(recipe2.id))
        self.assertEqual(recipe2.title, res.data['recipe'])
        self.assertEqual(recipe2.tags.all().count(), res.data['noOfTags'])
        self.assertEqual(recipe2.ingredients.all().count(),
                         res.data['noOfIngredients'])

        res = self.client.get(aggregate_url(recipe3.id))
        self.assertEqual(recipe3.title, res.data['recipe'])
        self.assertEqual(recipe3.tags.all().count(), res.data['noOfTags'])
        self.assertEqual(recipe3.ingredients.all().count(),
                         res.data['noOfIngredients'])
