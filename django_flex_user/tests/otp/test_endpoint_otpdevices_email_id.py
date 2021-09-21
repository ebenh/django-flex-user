from rest_framework.test import APITestCase
from rest_framework import status


class TestOTPDeviceRetrieve(APITestCase):
    """
    This class is designed to test django_flex_user.views.OTPDevice
    """
    _REST_ENDPOINT_PATH = '/account/otp-devices/{type}/{id}'

    class _ContentType:
        class ApplicationJSON:
            challenge_values = (
                {},
                {'challenge': None},
                {'challenge': ''},
                {'challenge': 'validChallenge'},
                {'challenge': 'invalidChallenge'}
            )

        class MultipartFormData:
            challenge_values = (
                {},
                {'challenge': ''},
                {'challenge': 'validChallenge'},
                {'challenge': 'invalidChallenge'}
            )

    def setUp(self):
        from django_flex_user.models import FlexUser
        from django_flex_user.models import EmailDevice

        user = FlexUser.objects.create_user(username='validUsername',
                                            email='validEmail@example.com',
                                            phone='+12025551234')
        self.otp_device = EmailDevice.objects.get(user=user)

        self._REST_ENDPOINT_PATH = TestOTPDeviceRetrieve._REST_ENDPOINT_PATH.format(type='email', id=self.otp_device.id)

    def test_method_get(self):
        response = self.client.get(self._REST_ENDPOINT_PATH)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.otp_device.refresh_from_db()
        self.assertFalse(self.otp_device.confirmed)
        self.assertIsNotNone(self.otp_device.challenge)
        self.assertNotEqual(self.otp_device.challenge, '')
        # note eben: Because escape characters are inserted into the challenge string, the challenge string's length may
        # be greater than or equal to its configured length
        self.assertGreaterEqual(len(self.otp_device.challenge), self.otp_device.challenge_length)
        self.assertIsNone(self.otp_device.verification_timeout)
        self.assertEqual(self.otp_device.verification_failure_count, 0)

    def test_method_post_format_application_json_generate_challenge_validate_challenge(self):
        from django.db import transaction
        from freezegun import freeze_time
        from django.utils import timezone
        from datetime import timedelta

        self.otp_device.generate_challenge()

        for data in self._ContentType.ApplicationJSON.challenge_values:
            with self.subTest(**data), freeze_time(), transaction.atomic():

                # Replace the challenge string with the actual challenge
                if data.get('challenge') == 'validChallenge':
                    data['challenge'] = self.otp_device.challenge

                response = self.client.post(self._REST_ENDPOINT_PATH, data=data, format='json')

                if not data.get('challenge'):
                    """
                    If the supplied challenge is either undefined, None or the empty string,
                    django_flex_user.views.EmailDevice.post should return HTTP status code HTTP_400_BAD_REQUEST.
                    """
                    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

                    self.otp_device.refresh_from_db()
                    self.assertIsNotNone(self.otp_device.challenge)
                    self.assertFalse(self.otp_device.confirmed)
                    self.assertIsNone(self.otp_device.verification_timeout)
                    self.assertEqual(self.otp_device.verification_failure_count, 0)
                elif data.get('challenge') == 'invalidChallenge':
                    """
                    If the supplied challenge is defined and invalid, django_flex_user.views.EmailDevice.post
                    should return HTTP status code HTTP_401_UNAUTHORIZED.
                    """
                    self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

                    self.otp_device.refresh_from_db()
                    self.assertIsNotNone(self.otp_device.challenge)
                    self.assertFalse(self.otp_device.confirmed)
                    self.assertEqual(self.otp_device.verification_timeout, timezone.now() + timedelta(seconds=1))
                    self.assertEqual(self.otp_device.verification_failure_count, 1)
                else:
                    """
                    If the supplied challenge is defined and valid, django_flex_user.views.EmailDevice.post should
                    return HTTP status code HTTP_200_OK.
                    """
                    self.assertEqual(response.status_code, status.HTTP_200_OK)

                    self.otp_device.refresh_from_db()
                    self.assertIsNone(self.otp_device.challenge)
                    self.assertTrue(self.otp_device.confirmed)
                    self.assertIsNone(self.otp_device.verification_timeout)
                    self.assertEqual(self.otp_device.verification_failure_count, 0)

                transaction.set_rollback(True)

    def test_method_post_format_multipart_form_data_generate_challenge_validate_challenge(self):
        from django.db import transaction
        from freezegun import freeze_time
        from django.utils import timezone
        from datetime import timedelta

        self.otp_device.generate_challenge()

        for data in self._ContentType.MultipartFormData.challenge_values:
            with self.subTest(**data), freeze_time(), transaction.atomic():

                # Replace the challenge string with the actual challenge
                if data.get('challenge') == 'validChallenge':
                    data['challenge'] = self.otp_device.challenge

                response = self.client.post(self._REST_ENDPOINT_PATH, data=data, format='multipart')

                if not data.get('challenge'):
                    """
                    If the supplied challenge is either undefined or the empty string,
                    django_flex_user.views.EmailDevice.post should return HTTP status code HTTP_400_BAD_REQUEST.
                    """
                    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

                    self.otp_device.refresh_from_db()
                    self.assertIsNotNone(self.otp_device.challenge)
                    self.assertFalse(self.otp_device.confirmed)
                    self.assertIsNone(self.otp_device.verification_timeout)
                    self.assertEqual(self.otp_device.verification_failure_count, 0)
                elif data.get('challenge') == 'validChallenge':
                    """
                    If the supplied challenge is defined and valid, django_flex_user.views.EmailDevice.post should
                    return HTTP status code HTTP_200_OK.
                    """
                    self.assertEqual(response.status_code, status.HTTP_200_OK)

                    self.otp_device.refresh_from_db()
                    self.assertIsNone(self.otp_device.challenge)
                    self.assertTrue(self.otp_device.confirmed)
                    self.assertIsNone(self.otp_device.verification_timeout)
                    self.assertEqual(self.otp_device.verification_failure_count, 0)
                elif data.get('challenge') == 'invalidChallenge':
                    """
                    If the supplied challenge is defined and invalid, django_flex_user.views.EmailDevice.post
                    should return HTTP status code HTTP_401_UNAUTHORIZED.
                    """
                    self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

                    self.otp_device.refresh_from_db()
                    self.assertIsNotNone(self.otp_device.challenge)
                    self.assertFalse(self.otp_device.confirmed)
                    self.assertEqual(self.otp_device.verification_timeout, timezone.now() + timedelta(seconds=1))
                    self.assertEqual(self.otp_device.verification_failure_count, 1)
                else:
                    """
                    If the supplied challenge is defined and valid, django_flex_user.views.EmailDevice.post should
                    return HTTP status code HTTP_200_OK.
                    """
                    self.assertEqual(response.status_code, status.HTTP_200_OK)

                    self.otp_device.refresh_from_db()
                    self.assertIsNone(self.otp_device.challenge)
                    self.assertTrue(self.otp_device.confirmed)
                    self.assertIsNone(self.otp_device.verification_timeout)
                    self.assertEqual(self.otp_device.verification_failure_count, 0)

                transaction.set_rollback(True)

    def test_method_post_format_application_json_validate_challenge(self):
        from django.db import transaction
        from freezegun import freeze_time
        from django.utils import timezone
        from datetime import timedelta

        for data in self._ContentType.ApplicationJSON.challenge_values:
            with self.subTest(**data), freeze_time(), transaction.atomic():

                # Replace the challenge string with the actual challenge
                if data.get('challenge') == 'validChallenge':
                    data['challenge'] = self.otp_device.challenge

                response = self.client.post(self._REST_ENDPOINT_PATH, data=data, format='json')

                if not data.get('challenge'):
                    """
                    If the supplied challenge is either undefined, None or the empty string,
                    django_flex_user.views.EmailDevice.post should return HTTP status code HTTP_400_BAD_REQUEST.
                    """
                    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

                    self.otp_device.refresh_from_db()
                    self.assertIsNone(self.otp_device.challenge)
                    self.assertFalse(self.otp_device.confirmed)
                    self.assertIsNone(self.otp_device.verification_timeout)
                    self.assertEqual(self.otp_device.verification_failure_count, 0)
                else:
                    """
                    If the supplied challenge is defined and invalid, or defined and valid,
                    django_flex_user.views.EmailDevice.post should return HTTP status code HTTP_401_UNAUTHORIZED.
                    """
                    self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

                    self.otp_device.refresh_from_db()
                    self.assertIsNone(self.otp_device.challenge)
                    self.assertFalse(self.otp_device.confirmed)
                    self.assertEqual(self.otp_device.verification_timeout, timezone.now() + timedelta(seconds=1))
                    self.assertEqual(self.otp_device.verification_failure_count, 1)

                transaction.set_rollback(True)

    def test_method_post_format_multipart_form_data_validate_challenge(self):
        from django.db import transaction
        from freezegun import freeze_time
        from django.utils import timezone
        from datetime import timedelta

        for data in self._ContentType.MultipartFormData.challenge_values:
            with self.subTest(**data), freeze_time(), transaction.atomic():

                # Replace the challenge string with the actual challenge
                if data.get('challenge') == 'validChallenge':
                    data['challenge'] = self.otp_device.challenge

                response = self.client.post(self._REST_ENDPOINT_PATH, data=data, format='multipart')
                if not data.get('challenge'):
                    """
                    If the supplied challenge is either undefined or the empty string,
                    django_flex_user.views.EmailDevice.post should return HTTP status code HTTP_400_BAD_REQUEST.
                    """
                    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

                    self.otp_device.refresh_from_db()
                    self.assertIsNone(self.otp_device.challenge)
                    self.assertFalse(self.otp_device.confirmed)
                    self.assertIsNone(self.otp_device.verification_timeout)
                    self.assertEqual(self.otp_device.verification_failure_count, 0)
                else:
                    """
                    If the supplied challenge is defined and invalid, or defined and valid,
                    django_flex_user.views.EmailDevice.post should return HTTP status code HTTP_401_UNAUTHORIZED.
                    """
                    self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

                    self.otp_device.refresh_from_db()
                    self.assertIsNone(self.otp_device.challenge)
                    self.assertFalse(self.otp_device.confirmed)
                    self.assertEqual(self.otp_device.verification_timeout, timezone.now() + timedelta(seconds=1))
                    self.assertEqual(self.otp_device.verification_failure_count, 1)

                transaction.set_rollback(True)

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

    def test_throttle(self):
        from freezegun import freeze_time

        self.otp_device.generate_challenge()

        with freeze_time() as frozen_datetime:
            for i in range(0, 10):
                """
                Here we try to verify an invalid challenge. django_flex_user.views.EmailDevice.post should return HTTP
                status code HTTP_401_UNAUTHORIZED and subsequent verification attempts should be timed out for the next
                2^i seconds.
                """
                response = self.client.post(self._REST_ENDPOINT_PATH, data={'challenge': 'invalidChallenge'})
                self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

                """
                Here we simulate the verification timeout period. For each second of the timeout period we attempt to
                verify again. django_flex_user.views.EmailDevice.post should return HTTP status code
                HTTP_429_TOO_MANY_REQUESTS each time.
                """
                for j in range(0, 2 ** i):
                    """
                    Try to verify an invalid challenge.
                    """
                    response = self.client.post(self._REST_ENDPOINT_PATH,
                                                data={'challenge': 'invalidChallenge'})
                    self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
                    """
                    Try to verify a valid challenge.
                    """
                    response = self.client.post(self._REST_ENDPOINT_PATH,
                                                data={'challenge': self.otp_device.challenge})
                    self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
                    """
                    Advance time by one second.
                    """
                    frozen_datetime.tick()
