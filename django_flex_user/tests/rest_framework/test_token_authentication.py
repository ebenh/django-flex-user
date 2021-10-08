from rest_framework.test import APITestCase, URLPatternsTestCase

from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from django.contrib.auth.models import AnonymousUser
from django.urls import path


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([AllowAny])
def _token_authentication_unrestricted_view(_request):
    return Response()


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def _token_authentication_restricted_view(_request):
    return Response()


class TestTokenAuthentication(APITestCase, URLPatternsTestCase):
    urlpatterns = [
        path('_token_authentication_unrestricted_view', _token_authentication_unrestricted_view),
        path('_token_authentication_restricted_view', _token_authentication_restricted_view),
    ]

    def test_create_token(self):
        from django_flex_user.models.user import FlexUser
        from django.utils import timezone
        from django.db.utils import IntegrityError
        from freezegun import freeze_time

        with freeze_time():
            user = FlexUser.objects.create_user(username='validUsername', password='validPassword')
            token = Token.objects.create(user=user)

            self.assertIsNotNone(token)
            self.assertIsInstance(token.key, str)
            self.assertTrue(token.key)
            self.assertEqual(token.created, timezone.now())
            self.assertEqual(token.user, user)

            self.assertRaises(IntegrityError, Token.objects.create, user=None)

    # Unrestricted view

    def test_no_authentication_unrestricted_view(self):
        response = self.client.get('/_token_authentication_unrestricted_view')

        self.assertIsInstance(response.wsgi_request.user, AnonymousUser)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_successful_authentication_unrestricted_view(self):
        from django_flex_user.models.user import FlexUser

        user = FlexUser.objects.create_user(username='validUsername', password='validPassword')
        token = Token.objects.create(user=user)

        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        response = self.client.get('/_token_authentication_unrestricted_view')

        self.assertEqual(response.wsgi_request.user, user)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unsuccessful_authentication_unrestricted_view(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token 0123456789')
        response = self.client.get('/_token_authentication_unrestricted_view')

        self.assertIsInstance(response.wsgi_request.user, AnonymousUser)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Restricted view

    def test_no_authentication_restricted_view(self):
        response = self.client.get('/_token_authentication_restricted_view')

        self.assertIsInstance(response.wsgi_request.user, AnonymousUser)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_successful_authentication_restricted_view(self):
        from django_flex_user.models.user import FlexUser

        user = FlexUser.objects.create_user(username='validUsername', password='validPassword')
        token = Token.objects.create(user=user)

        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        response = self.client.get('/_token_authentication_restricted_view')

        self.assertEqual(response.wsgi_request.user, user)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unsuccessful_authentication_restricted_view(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token 0123456789')
        response = self.client.get('/_token_authentication_restricted_view')

        self.assertIsInstance(response.wsgi_request.user, AnonymousUser)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)