from rest_framework.test import APITestCase
from rest_framework import status


class TestOTPDevicesRetrieve(APITestCase):
    """
    This class is designed to test django_flex_user.views.OTPDevices
    """
    _REST_ENDPOINT_PATH = '/account/otp-devices/'

    def setUp(self):
        from django_flex_user.models import FlexUser

        FlexUser.objects.create_user(username='validUsername1', email='validEmail1@example.com', phone='+12025550001')
        FlexUser.objects.create_user(username='validUsername2', email='validEmail2@example.com', phone='+12025550002')

    def test_method_get(self):
        response = self.client.get(self._REST_ENDPOINT_PATH)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_method_get_no_matches(self):
        query_values = (
            '',                         # Empty string
            'validUsername3',           # Non-existent username
            'validEmail3@example.com',  # Non-existent email
            '+12025550003',             # Non-existent phone
            'validUsername',            # Partial match username
            'validEmail1@'              # Partial match email
            '+1202'                     # Partial match phone
        )

        for v in query_values:
            with self.subTest(search_value=v):
                response = self.client.get(self._REST_ENDPOINT_PATH, {'search': v})
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertEqual(
                    response.data,
                    {
                        'EmailDevice': [],
                        'PhoneDevice': []
                    }
                )

    def test_method_get_match_found(self):
        query_values = (
            'validUsername1',
            'validEmail1@example.com',
            '+12025550001'
        )

        for v in query_values:
            with self.subTest(search_value=v):
                response = self.client.get(self._REST_ENDPOINT_PATH, {'search': v})
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertEqual(
                    response.data,
                    {
                        'EmailDevice': [
                            {
                                'id': 1,
                                'name': 'va*********@ex*****.***'
                            }
                        ],
                        'PhoneDevice': [
                            {
                                'id': 1,
                                'name': '+*********01'
                            }
                        ]
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
