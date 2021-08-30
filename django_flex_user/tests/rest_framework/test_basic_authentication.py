from rest_framework.test import APITestCase, URLPatternsTestCase

from rest_framework.decorators import api_view, authentication_classes
from rest_framework.authentication import BasicAuthentication
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from django.contrib.auth.models import AnonymousUser
from django.urls import path

import base64


@api_view(['GET'])
@authentication_classes([BasicAuthentication])
@permission_classes([AllowAny])
def _basic_authentication_view(_request):
    return Response()


class TestBasicAuthentication(APITestCase, URLPatternsTestCase):
    urlpatterns = [
        path('basic-authentication-view', _basic_authentication_view),
    ]

    @classmethod
    def _encode_credentials(cls, username, password):
        concatenated = username.encode('utf-8') + b':' + password.encode('utf-8')
        encoded = base64.b64encode(concatenated)
        return f'basic {encoded.decode("utf-8")}'

    def setUp(self):
        from django_flex_user.models import SPUser

        self.user = SPUser.objects.create_user(username='validUsername', password='validPassword')

    def test_no_authentication(self):
        response = self.client.get('/basic-authentication-view')

        self.assertIsInstance(response.wsgi_request.user, AnonymousUser)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_successful_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION=self._encode_credentials('validUsername', 'validPassword'))
        response = self.client.get('/basic-authentication-view')

        self.assertEqual(response.wsgi_request.user, self.user)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unsuccessful_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION=self._encode_credentials('validUsername', 'invalidPassword'))
        response = self.client.get('/basic-authentication-view')

        self.assertIsInstance(response.wsgi_request.user, AnonymousUser)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
