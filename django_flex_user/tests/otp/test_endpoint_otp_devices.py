from rest_framework.test import APITestCase
from rest_framework import status


class TestOTPDevicesRetrieve(APITestCase):
    """
    This class is designed to test django_flex_user.views.OTPDevices
    """
    _REST_ENDPOINT_PATH = '/account/otp-devices/'

    def test_method_get(self):
        response = self.client.get(self._REST_ENDPOINT_PATH)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_method_get_no_matches(self):
        from django_flex_user.models import FlexUser

        FlexUser.objects.create_user(username='validUsername', email='validEmail@example.com', phone='+12025551234')

        for q in ('', 'validUsername2', 'validEmail2@example.com', '+12025554321', 'valid', '+1202'):
            response = self.client.get(self._REST_ENDPOINT_PATH, {'search': q})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(
                response.data,
                {
                    'EmailDevice': [],
                    'PhoneDevice': []
                }
            )

    def test_method_get_match_found(self):
        from django_flex_user.models import FlexUser

        FlexUser.objects.create_user(username='validUsername', email='validEmail@example.com', phone='+12025551234')

        for q in ('validUsername', 'validEmail@example.com', '+12025551234'):
            response = self.client.get(self._REST_ENDPOINT_PATH, {'search': q})
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(
                response.data,
                {
                    'EmailDevice': [
                        {
                            'id': 1,
                            'name': 'va********@ex*****.***'
                        }
                    ],
                    'PhoneDevice': [
                        {
                            'id': 1,
                            'name': '+*********34'
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
