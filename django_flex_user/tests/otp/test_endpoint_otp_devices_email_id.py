from rest_framework.test import APITestCase
from rest_framework import status


class TestOTPDeviceRetrieve(APITestCase):
    """
    This class is designed to test django_flex_user.views.OTPDevice
    """
    _REST_ENDPOINT_PATH = '/account/otp-devices/email/{id}'

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
        self.email_device = EmailDevice.objects.get(user=user)

    def test_method_get(self):
        response = self.client.get(self._REST_ENDPOINT_PATH.format(id=self.email_device.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.email_device.refresh_from_db()
        self.assertFalse(self.email_device.confirmed)
        self.assertIsNotNone(self.email_device.challenge)
        self.assertNotEqual(self.email_device.challenge, '')
        # note eben: Because escape characters are inserted into the challenge string, the challenge string's length may
        # be greater than or equal to its configured length
        self.assertGreaterEqual(len(self.email_device.challenge), self.email_device.challenge_length)
        self.assertIsNone(self.email_device.verification_timeout)
        self.assertEqual(self.email_device.verification_failure_count, 0)

    def test_method_post_format_application_json(self):
        from django.db import transaction
        from freezegun import freeze_time
        from django.utils import timezone
        from datetime import timedelta

        self.email_device.generate_challenge()

        for data in self._ContentType.ApplicationJSON.challenge_values:
            with self.subTest(**data), freeze_time(), transaction.atomic():

                # Replace the challenge string with the actual challenge
                if data.get('challenge') == 'validChallenge':
                    data['challenge'] = self.email_device.challenge

                response = self.client.post(self._REST_ENDPOINT_PATH.format(id=self.email_device.id),
                                            data=data,
                                            format='json')
                if not data.get('challenge'):
                    """
                    If the supplied challenge is either undefined, None or the empty string,
                    django_flex_user.views.EmailDevice.post should return HTTP status code HTTP_400_BAD_REQUEST.
                    """
                    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

                    self.email_device.refresh_from_db()
                    self.assertIsNotNone(self.email_device.challenge)
                    self.assertFalse(self.email_device.confirmed)
                    self.assertIsNone(self.email_device.verification_timeout)
                    self.assertEqual(self.email_device.verification_failure_count, 0)
                elif data.get('challenge') == 'invalidChallenge':
                    """
                    If the supplied challenge is defined and invalid, django_flex_user.views.EmailDevice.post
                    should return HTTP status code HTTP_401_UNAUTHORIZED.
                    """
                    self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

                    self.email_device.refresh_from_db()
                    self.assertIsNotNone(self.email_device.challenge)
                    self.assertFalse(self.email_device.confirmed)
                    self.assertEqual(self.email_device.verification_timeout, timezone.now() + timedelta(seconds=1))
                    self.assertEqual(self.email_device.verification_failure_count, 1)
                else:
                    """
                    If the supplied challenge is defined and valid, django_flex_user.views.EmailDevice.post should
                    return HTTP status code HTTP_200_OK.
                    """
                    self.assertEqual(response.status_code, status.HTTP_200_OK)

                    self.email_device.refresh_from_db()
                    self.assertIsNone(self.email_device.challenge)
                    self.assertTrue(self.email_device.confirmed)
                    self.assertIsNone(self.email_device.verification_timeout)
                    self.assertEqual(self.email_device.verification_failure_count, 0)

                transaction.set_rollback(True)

    def test_method_post_format_multipart_form_data(self):
        from django.db import transaction
        from freezegun import freeze_time
        from django.utils import timezone
        from datetime import timedelta

        self.email_device.generate_challenge()

        for data in self._ContentType.MultipartFormData.challenge_values:
            with self.subTest(**data), freeze_time(), transaction.atomic():

                # Replace the challenge string with the actual challenge
                if data.get('challenge') == 'validChallenge':
                    data['challenge'] = self.email_device.challenge

                response = self.client.post(self._REST_ENDPOINT_PATH.format(id=self.email_device.id),
                                            data=data,
                                            format='multipart')
                if not data.get('challenge'):
                    """
                    If the supplied challenge is either undefined or the empty string,
                    django_flex_user.views.EmailDevice.post should return HTTP status code HTTP_400_BAD_REQUEST.
                    """
                    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

                    self.email_device.refresh_from_db()
                    self.assertIsNotNone(self.email_device.challenge)
                    self.assertFalse(self.email_device.confirmed)
                    self.assertIsNone(self.email_device.verification_timeout)
                    self.assertEqual(self.email_device.verification_failure_count, 0)
                elif data.get('challenge') == 'validChallenge':
                    """
                    If the supplied challenge is defined and valid, django_flex_user.views.EmailDevice.post should
                    return HTTP status code HTTP_200_OK.
                    """
                    self.assertEqual(response.status_code, status.HTTP_200_OK)

                    self.email_device.refresh_from_db()
                    self.assertIsNone(self.email_device.challenge)
                    self.assertTrue(self.email_device.confirmed)
                    self.assertIsNone(self.email_device.verification_timeout)
                    self.assertEqual(self.email_device.verification_failure_count, 0)
                elif data.get('challenge') == 'invalidChallenge':
                    """
                    If the supplied challenge is defined and invalid, django_flex_user.views.EmailDevice.post
                    should return HTTP status code HTTP_401_UNAUTHORIZED.
                    """
                    self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

                    self.email_device.refresh_from_db()
                    self.assertIsNotNone(self.email_device.challenge)
                    self.assertFalse(self.email_device.confirmed)
                    self.assertEqual(self.email_device.verification_timeout, timezone.now() + timedelta(seconds=1))
                    self.assertEqual(self.email_device.verification_failure_count, 1)
                else:
                    """
                    If the supplied challenge is defined and valid, django_flex_user.views.EmailDevice.post should
                    return HTTP status code HTTP_200_OK.
                    """
                    self.assertEqual(response.status_code, status.HTTP_200_OK)

                    self.email_device.refresh_from_db()
                    self.assertIsNone(self.email_device.challenge)
                    self.assertTrue(self.email_device.confirmed)
                    self.assertIsNone(self.email_device.verification_timeout)
                    self.assertEqual(self.email_device.verification_failure_count, 0)

                transaction.set_rollback(True)

    def test_method_post_format_application_json2(self):
        from django.db import transaction
        from freezegun import freeze_time
        from django.utils import timezone
        from datetime import timedelta

        for data in self._ContentType.ApplicationJSON.challenge_values:
            with self.subTest(**data), freeze_time(), transaction.atomic():

                # Replace the challenge string with the actual challenge
                if data.get('challenge') == 'validChallenge':
                    data['challenge'] = self.email_device.challenge

                response = self.client.post(self._REST_ENDPOINT_PATH.format(id=self.email_device.id),
                                            data=data,
                                            format='json')
                if not data.get('challenge'):
                    """
                    If the supplied challenge is either undefined, None or the empty string,
                    django_flex_user.views.EmailDevice.post should return HTTP status code HTTP_400_BAD_REQUEST.
                    """
                    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

                    self.email_device.refresh_from_db()
                    self.assertIsNone(self.email_device.challenge)
                    self.assertFalse(self.email_device.confirmed)
                    self.assertIsNone(self.email_device.verification_timeout)
                    self.assertEqual(self.email_device.verification_failure_count, 0)
                elif data.get('challenge') == 'invalidChallenge':
                    """
                    If the supplied challenge is defined and invalid, django_flex_user.views.EmailDevice.post
                    should return HTTP status code HTTP_401_UNAUTHORIZED.
                    """
                    self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

                    self.email_device.refresh_from_db()
                    self.assertIsNone(self.email_device.challenge)
                    self.assertFalse(self.email_device.confirmed)
                    self.assertEqual(self.email_device.verification_timeout, timezone.now() + timedelta(seconds=1))
                    self.assertEqual(self.email_device.verification_failure_count, 1)
                else:
                    """
                    If the supplied challenge is defined and valid, django_flex_user.views.EmailDevice.post should
                    return HTTP status code HTTP_401_UNAUTHORIZED.
                    """
                    self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

                    self.email_device.refresh_from_db()
                    self.assertIsNone(self.email_device.challenge)
                    self.assertFalse(self.email_device.confirmed)
                    self.assertEqual(self.email_device.verification_timeout, timezone.now() + timedelta(seconds=1))
                    self.assertEqual(self.email_device.verification_failure_count, 1)

                transaction.set_rollback(True)

    def test_method_post_format_multipart_form_data2(self):
        from django.db import transaction
        from freezegun import freeze_time
        from django.utils import timezone
        from datetime import timedelta

        for data in self._ContentType.MultipartFormData.challenge_values:
            with self.subTest(**data), freeze_time(), transaction.atomic():

                # Replace the challenge string with the actual challenge
                if data.get('challenge') == 'validChallenge':
                    data['challenge'] = self.email_device.challenge

                response = self.client.post(self._REST_ENDPOINT_PATH.format(id=self.email_device.id),
                                            data=data,
                                            format='multipart')
                if not data.get('challenge'):
                    """
                    If the supplied challenge is either undefined or the empty string,
                    django_flex_user.views.EmailDevice.post should return HTTP status code HTTP_400_BAD_REQUEST.
                    """
                    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

                    self.email_device.refresh_from_db()
                    self.assertIsNone(self.email_device.challenge)
                    self.assertFalse(self.email_device.confirmed)
                    self.assertIsNone(self.email_device.verification_timeout)
                    self.assertEqual(self.email_device.verification_failure_count, 0)
                elif data.get('challenge') == 'invalidChallenge':
                    """
                    If the supplied challenge is defined and invalid, django_flex_user.views.EmailDevice.post
                    should return HTTP status code HTTP_401_UNAUTHORIZED.
                    """
                    self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

                    self.email_device.refresh_from_db()
                    self.assertIsNone(self.email_device.challenge)
                    self.assertFalse(self.email_device.confirmed)
                    self.assertEqual(self.email_device.verification_timeout, timezone.now() + timedelta(seconds=1))
                    self.assertEqual(self.email_device.verification_failure_count, 1)
                else:
                    """
                    If the supplied challenge is defined and valid, django_flex_user.views.EmailDevice.post should
                    return HTTP status code HTTP_401_UNAUTHORIZED.
                    """
                    self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

                    self.email_device.refresh_from_db()
                    self.assertIsNone(self.email_device.challenge)
                    self.assertFalse(self.email_device.confirmed)
                    self.assertEqual(self.email_device.verification_timeout, timezone.now() + timedelta(seconds=1))
                    self.assertEqual(self.email_device.verification_failure_count, 1)

                transaction.set_rollback(True)

    def test_method_put(self):
        response = self.client.put(self._REST_ENDPOINT_PATH.format(id=self.email_device.id))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_method_patch(self):
        response = self.client.patch(self._REST_ENDPOINT_PATH.format(id=self.email_device.id))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_method_delete(self):
        response = self.client.delete(self._REST_ENDPOINT_PATH.format(id=self.email_device.id))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_method_options(self):
        response = self.client.options(self._REST_ENDPOINT_PATH.format(id=self.email_device.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
