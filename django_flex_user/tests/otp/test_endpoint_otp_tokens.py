from rest_framework.test import APITestCase
from rest_framework import status


class TestOTPTokensRetrieve(APITestCase):
    """
    This class is designed to test django_flex_user.views.OTPTokens
    """
    _REST_ENDPOINT_PATH = '/account/otp-tokens/'

    _search_values = (
        ('', False),  # Empty string
        ('validUsername3', False),  # Non-existent username
        ('validEmail3@example.com', False),  # Non-existent email
        ('+12025550003', False),  # Non-existent phone
        ('validUsername', False),  # Partial match username
        ('validEmail1@', False),  # Partial match email
        ('+1202', False),  # Partial match phone
        ('validUsername1', True),  # Matching username
        ('validEmail1@example.com', True),  # Matching email
        ('+12025550001', True)  # Matching phone
    )

    def setUp(self):
        from django_flex_user.models.user import FlexUser

        FlexUser.objects.create_user(username='validUsername1', email='validEmail1@example.com', phone='+12025550001')
        FlexUser.objects.create_user(username='validUsername2', email='validEmail2@example.com', phone='+12025550002')

    def test_method_get(self):
        response = self.client.get(self._REST_ENDPOINT_PATH)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            {
                'email': [],
                'phone': []
            }
        )

    def test_method_get_with_query_string(self):
        for value, expect_match in self._search_values:
            with self.subTest(search_value=value):
                from rest_framework.test import APIRequestFactory
                from django.urls import reverse

                response = self.client.get(self._REST_ENDPOINT_PATH, {'search': value})
                self.assertEqual(response.status_code, status.HTTP_200_OK)

                # Dummy request for building absolute URI's
                request = APIRequestFactory().get('/')

                if expect_match:
                    self.assertEqual(
                        response.data,
                        {
                            'email': [
                                {
                                    'name': 'va*********@ex*****.***',
                                    'uri': f'{request.build_absolute_uri(reverse("email-token", args=(1,)))}'
                                }
                            ],
                            'phone': [
                                {
                                    'name': '+*********01',
                                    'uri': f'{request.build_absolute_uri(reverse("phone-token", args=(1,)))}'
                                }
                            ]
                        }
                    )
                else:
                    self.assertEqual(
                        response.data,
                        {
                            'email': [],
                            'phone': []
                        }
                    )

    def test_method_post(self):
        response = self.client.post(self._REST_ENDPOINT_PATH)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_method_put(self):
        response = self.client.put(self._REST_ENDPOINT_PATH)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_method_patch(self):
        response = self.client.patch(self._REST_ENDPOINT_PATH)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_method_delete(self):
        response = self.client.delete(self._REST_ENDPOINT_PATH)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_method_options(self):
        response = self.client.options(self._REST_ENDPOINT_PATH)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
