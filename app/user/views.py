from rest_framework import generics, authentication, permissions

from user.serializers import UserSerialiser, AuthTokenSerializer

from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings


class CreateUserView(generics.CreateAPIView):
    """create a new user"""
    serializer_class = UserSerialiser


class CreateTokenView(ObtainAuthToken):
    """create a new auth token for a user"""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage authenticated user"""
    serializer_class = UserSerialiser
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user

    # https://github.com/encode/django-rest-framework/blob/master/rest_framework/authtoken/views.py
