from rest_framework.test import APITestCase, URLPatternsTestCase, APIClient

from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.models import AnonymousUser
from django.urls import path


# https://stackoverflow.com/questions/29749046/test-csrf-verification-with-django-rest-framework

@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@ensure_csrf_cookie
def _get_csrf_token(_request):
    return Response()


@api_view(['GET', 'HEAD', 'OPTIONS', 'TRACE'])
@authentication_classes([SessionAuthentication])
def _csrf_token_exempt(_request):
    return Response()


@api_view(['POST', 'PUT', 'PATCH', 'DELETE'])
@authentication_classes([SessionAuthentication])
def _csrf_token_required(_request):
    return Response()


# CSRF validation in REST framework works slightly differently to standard Django due to the need to support both
# session and non-session based authentication to the same views. This means that only authenticated requests require
# CSRF tokens, and anonymous requests may be sent without CSRF tokens. This behaviour is not suitable for login views,
# which should always have CSRF validation applied.

class TestSessionAuthenticationCSRFToken(APITestCase, URLPatternsTestCase):
    urlpatterns = [
        path('get-csrf-token', _get_csrf_token),
        path('csrf-token-exempt', _csrf_token_exempt),
        path('csrf-token-required', _csrf_token_required)
    ]

    def setUp(self):
        from django_flex_user.models.user import FlexUser

        self.client = APIClient(enforce_csrf_checks=True)

        FlexUser.objects.create_user(username='validUsername', password='validPassword')
        is_authenticated = self.client.login(username='validUsername', password='validPassword')
        self.assertIs(is_authenticated, True)

    def tearDown(self):
        self.client.logout()

    def _get_csrf_token(self):
        response = self.client.get('/get-csrf-token')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.cookies.get('csrftoken'))

        return response.cookies['csrftoken'].value

    def test_csrf_token_exempt_methods(self):
        # GET
        response = self.client.get('/csrf-token-exempt')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # HEAD
        response = self.client.head('/csrf-token-exempt')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # OPTIONS
        response = self.client.options('/csrf-token-exempt')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # TRACE
        response = self.client.trace('/csrf-token-exempt')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_csrf_token_required_methods(self):
        csrf_token = self._get_csrf_token()

        # POST
        response = self.client.post('/csrf-token-required', data={'csrfmiddlewaretoken': csrf_token})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.post('/csrf-token-required', HTTP_X_CSRFTOKEN=csrf_token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.post('/csrf-token-required')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # PUT
        response = self.client.put('/csrf-token-required', HTTP_X_CSRFTOKEN=csrf_token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.put('/csrf-token-required')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # PATCH
        response = self.client.patch('/csrf-token-required', HTTP_X_CSRFTOKEN=csrf_token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.patch('/csrf-token-required')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # DELETE
        response = self.client.delete('/csrf-token-required', HTTP_X_CSRFTOKEN=csrf_token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.delete('/csrf-token-required')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([AllowAny])
def _session_authentication_unrestricted_view(_request):
    return Response()


@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def _session_authentication_restricted_view(_request):
    return Response()


class TestSessionAuthentication(APITestCase, URLPatternsTestCase):
    urlpatterns = [
        path('session-authentication-unrestricted-view', _session_authentication_unrestricted_view),
        path('session-authentication-restricted-view', _session_authentication_restricted_view),
    ]

    def setUp(self):
        from django_flex_user.models.user import FlexUser

        self.user = FlexUser.objects.create_user(username='validUsername', password='validPassword')

    def test_no_authentication_unrestricted_view(self):
        response = self.client.get('/session-authentication-unrestricted-view')

        self.assertIsInstance(response.wsgi_request.user, AnonymousUser)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # Unrestricted view

    def test_successful_authentication_unrestricted_view(self):
        is_authenticated = self.client.login(username='validUsername', password='validPassword')
        self.assertIs(is_authenticated, True)

        response = self.client.get('/session-authentication-unrestricted-view')
        self.assertEqual(response.wsgi_request.user, self.user)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unsuccessful_authentication_unrestricted_view(self):
        is_authenticated = self.client.login(username='validUsername', password='invalidPassword')
        self.assertIs(is_authenticated, False)

        response = self.client.get('/session-authentication-unrestricted-view')
        self.assertIsInstance(response.wsgi_request.user, AnonymousUser)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # Restricted view

    def test_no_authentication_restricted_view(self):
        response = self.client.get('/session-authentication-restricted-view')

        self.assertIsInstance(response.wsgi_request.user, AnonymousUser)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_successful_authentication_restricted_view(self):
        is_authenticated = self.client.login(username='validUsername', password='validPassword')
        self.assertIs(is_authenticated, True)

        response = self.client.get('/session-authentication-restricted-view')
        self.assertEqual(response.wsgi_request.user, self.user)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unsuccessful_authentication_restricted_view(self):
        is_authenticated = self.client.login(username='validUsername', password='invalidPassword')
        self.assertIs(is_authenticated, False)

        response = self.client.get('/session-authentication-restricted-view')
        self.assertIsInstance(response.wsgi_request.user, AnonymousUser)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
