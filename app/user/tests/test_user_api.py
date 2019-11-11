from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
PROFILE_URL = reverse('user:profile')


def create_user(**params):
    """Helper function to create user"""
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test user api (public)"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test user creation with valid payload success"""
        payload = {
            "email": "testuser@xyz.com",
            "password": "password",
            "name": 'testuser'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload["password"]))
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        """Test user already exist"""
        payload = {"email": "testuser2@xyz.com", "password": "password"}
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test for invalid password"""
        payload = {"email": "testuser3@xyz.com", "password": "pa"}
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exist = get_user_model().objects.filter(
            email=payload["email"]).exists()
        self.assertFalse(user_exist)

    def test_create_token_for_user(self):
        """Test that token is created for user"""
        payload = {"email": "testuser4@xyz.com", "password": "password"}
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_for_invalid_credentials(self):
        payload = {"email": "testuser4@xyz.com", "password": "password"}
        create_user(**payload)
        res = self.client.post(TOKEN_URL, {"email": "testuser4@xyz.com",
                                           "password": "wrong"})

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """Test no tokens if user not in database"""
        payload = {"email": "testuser4@xyz.com", "password": "password"}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """Test that user email and password are required"""
        payload = {"email": "testuser4@xyz.com", "password": "password"}
        create_user(**payload)
        res = self.client.post(TOKEN_URL, {"email": "testuser4@xyz.com",
                                           "password": ""})

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthorized_profile_access(self):
        """Test that authentication required for users"""
        res = self.client.get(PROFILE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateAPITests(TestCase):
    """Test API for authenticated users"""

    def setUp(self):
        self.user = create_user(
            email="user3@xyz.com",
            password="password",
            name="user3",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrive_profile_access(self):
        """Test profile access after authentication"""
        res = self.client.get(PROFILE_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'email': "user3@xyz.com",
            'name': "user3"
        })

    def test_post_not_allowed(self):
        """Test post method not allowed for logged in users"""
        res = self.client.post(PROFILE_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_user_update_method(self):
        """Test if user can update his details"""
        payload = {"name": "new_name", "email": 'user4@xyz.com',
                   "password": 'new_password'
                   }
        res = self.client.patch(PROFILE_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
