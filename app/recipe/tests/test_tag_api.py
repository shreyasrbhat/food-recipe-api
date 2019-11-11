from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Tag

from recipe.serializers import TagSerializer

TAG_URL = reverse("recipe:tag-list")


class PublicAPITests(TestCase):
    """Test publicaly available api"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test if login required for tag list"""
        res = self.client.get(TAG_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PivateAPITest(TestCase):
    """Test tags apis post authorization"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="testuser1@xyz.com",
            password="password"
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_user_tag_list(self):
        """Test for tag lists under a user"""
        Tag.objects.create(user=self.user, name="Vegan")
        Tag.objects.create(user=self.user, name="Continental")

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)

        res = self.client.get(TAG_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_for_authenticated_user(self):
        """Test tags are return for authenticated user"""
        user2 = get_user_model().objects.create_user(
            email="testuser2@xyz.com",
            password="password"
        )
        Tag.objects.create(user=user2, name="Vegan")

        tag = Tag.objects.create(user=self.user, name="Eggitarian")

        res = self.client.get(TAG_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["name"], tag.name)

    def test_create_tag_successful(self):
        """Create a new tag"""
        payload = {"name": "vegan"}

        self.client.post(TAG_URL, payload)
        exists = Tag.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()
        self.assertTrue(exists)

    def test_create_invalid_tag(self):
        """Test creating tag with invalid payload"""
        payload = {"name": ""}
        res = self.client.post(TAG_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
