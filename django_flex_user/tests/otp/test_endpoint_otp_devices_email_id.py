from rest_framework.test import APITestCase
from rest_framework import status


class TestOTPDeviceRetrieve(APITestCase):
    """
    This class is designed to test django_flex_user.views.OTPDevice
    """
    _REST_ENDPOINT_PATH = '/account/otp-devices/email/{id}'

    def setUp(self):
        from django_flex_user.models import FlexUser
        from django_flex_user.models import EmailDevice

        user1 = FlexUser.objects.create_user(username='validUsername1',
                                             email='validEmail1@example.com',
                                             phone='+12025550001')
        user2 = FlexUser.objects.create_user(username='validUsername2',
                                             email='validEmail2@example.com',
                                             phone='+12025550002')

        self.email_device1 = EmailDevice.objects.get(user=user1)
        self.email_device2 = EmailDevice.objects.get(user=user2)

    def test_method_get(self):
        response = self.client.get(self._REST_ENDPOINT_PATH.format(id=self.email_device1.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_method_post(self):
        response = self.client.post(self._REST_ENDPOINT_PATH.format(id=self.email_device1.id),
                                    data={'challenge': self.email_device1.challenge},
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_method_put(self):
        response = self.client.put(self._REST_ENDPOINT_PATH.format(id=self.email_device1.id))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_method_patch(self):
        response = self.client.patch(self._REST_ENDPOINT_PATH.format(id=self.email_device1.id))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_method_delete(self):
        response = self.client.delete(self._REST_ENDPOINT_PATH.format(id=self.email_device1.id))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_method_options(self):
        response = self.client.options(self._REST_ENDPOINT_PATH.format(id=self.email_device1.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
