from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models


def sample_user(email="sampleuser@xyz.com", password="password"):
    """create a sample user"""
    return get_user_model().objects.create_user(email=email, password=password)


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """test to create new user with email is successful"""
        email = "abc@xyz.com"
        password = "user1234"

        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_normalize_email(self):
        """test if email of new user is normalized"""
        email = "abc@XYZ.com"
        user = get_user_model().objects.create_user(email=email)
        self.assertEqual(user.email, email.lower())

    def test_user_email_not_null(self):
        """test for error for no email address"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                email=None,
                password="user1234")

    def test_create_super_user(self):
        """test create new super user"""
        email = "123@xyz.com"
        password = "user1234"
        user = get_user_model().objects.create_superuser(
            email=email,
            password=password)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        """Test tag string representation"""
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='vegan'
        )

        self.assertEqual(str(tag), tag.name)
