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
        self.email_device1.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(self.email_device1.confirmed)
        self.assertIsNotNone(self.email_device1.challenge)
        self.assertNotEqual(self.email_device1.challenge, '')
        # note eben: Because escape characters are inserted into the challenge string, the challenge string's length may
        # be greater than or equal to its configured length
        self.assertGreaterEqual(len(self.email_device1.challenge), self.email_device1.challenge_length)
        self.assertIsNone(self.email_device1.verification_timeout)
        self.assertEqual(self.email_device1.verification_failure_count, 0)

    def test_method_post_format_application_json(self):
        from django_flex_user.models import FlexUser
        from django_flex_user.models import EmailDevice
        from django.db import transaction
        from freezegun import freeze_time
        from django.utils import timezone
        from datetime import timedelta

        user = FlexUser.objects.create_user(username='validUsername',
                                            email='validEmail@example.com',
                                            phone='+12025551234')
        email_device = EmailDevice.objects.get(user=user)
        email_device.challenge = 'validChallenge'
        email_device.save()

        for data in self._ContentType.ApplicationJSON.challenge_values:
            with self.subTest(**data), freeze_time(), transaction.atomic():
                response = self.client.post(self._REST_ENDPOINT_PATH.format(id=email_device.id),
                                            data=data,
                                            format='json')
                if not data.get('challenge'):
                    """
                    If the supplied challenge is either undefined, None or the empty string,
                    django_flex_user.views.EmailDevice.post should return HTTP status code HTTP_400_BAD_REQUEST.
                    """
                    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

                    self.assertIsNotNone(email_device.challenge)
                    self.assertFalse(email_device.confirmed)
                    self.assertIsNone(email_device.verification_timeout)
                    self.assertEqual(email_device.verification_failure_count, 0)
                elif data.get('challenge') == 'validChallenge':
                    """
                    If the supplied challenge is defined and valid, django_flex_user.views.EmailDevice.post should
                    return HTTP status code HTTP_200_OK.
                    """
                    self.assertEqual(response.status_code, status.HTTP_200_OK)

                    email_device.refresh_from_db()
                    self.assertIsNone(email_device.challenge)
                    self.assertTrue(email_device.confirmed)
                    self.assertIsNone(email_device.verification_timeout)
                    self.assertEqual(email_device.verification_failure_count, 0)
                elif data.get('challenge') == 'invalidChallenge':
                    """
                    If the supplied challenge is defined and invalid, django_flex_user.views.EmailDevice.post
                    should return HTTP status code HTTP_401_UNAUTHORIZED.
                    """
                    self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

                    email_device.refresh_from_db()
                    self.assertIsNotNone(email_device.challenge)
                    self.assertFalse(email_device.confirmed)
                    self.assertEqual(email_device.verification_timeout, timezone.now() + timedelta(seconds=1))
                    self.assertEqual(email_device.verification_failure_count, 1)
                else:
                    """
                    If we reach here something is broken.
                    """
                    self.assertFalse(True)

                transaction.set_rollback(True)

    def test_method_post_generate_challenge_verify_challenge_none(self):
        # Generate challenge
        response = self.client.get(self._REST_ENDPOINT_PATH.format(id=self.email_device1.id))
        self.email_device1.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Verify challenge
        response = self.client.post(self._REST_ENDPOINT_PATH.format(id=self.email_device1.id),
                                    data={'challenge': None},
                                    format='json')
        self.email_device1.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsNotNone(self.email_device1.challenge)
        self.assertFalse(self.email_device1.confirmed)
        self.assertIsNone(self.email_device1.verification_timeout)
        self.assertEqual(self.email_device1.verification_failure_count, 0)

    def test_method_post_generate_challenge_verify_challenge_empty_string(self):
        # Generate challenge
        response = self.client.get(self._REST_ENDPOINT_PATH.format(id=self.email_device1.id))
        self.email_device1.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Verify challenge
        response = self.client.post(self._REST_ENDPOINT_PATH.format(id=self.email_device1.id),
                                    data={'challenge': ''},
                                    format='json')
        self.email_device1.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsNotNone(self.email_device1.challenge)
        self.assertFalse(self.email_device1.confirmed)
        self.assertIsNone(self.email_device1.verification_timeout)
        self.assertEqual(self.email_device1.verification_failure_count, 0)

    def test_method_post_generate_challenge_verify_challenge_invalid_challenge(self):
        from freezegun import freeze_time
        from django.utils import timezone
        from datetime import timedelta

        # Generate challenge
        response = self.client.get(self._REST_ENDPOINT_PATH.format(id=self.email_device1.id))
        self.email_device1.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Verify challenge
        with freeze_time():
            response = self.client.post(self._REST_ENDPOINT_PATH.format(id=self.email_device1.id),
                                        data={'challenge': 'INVALID_CHALLENGE'},
                                        format='json')
            self.email_device1.refresh_from_db()
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
            self.assertIsNotNone(self.email_device1.challenge)
            self.assertFalse(self.email_device1.confirmed)
            self.assertEqual(self.email_device1.verification_timeout, timezone.now() + timedelta(seconds=1))
            self.assertEqual(self.email_device1.verification_failure_count, 1)

    def test_method_post_generate_challenge_verify_challenge_valid_challenge(self):
        # Generate challenge
        response = self.client.get(self._REST_ENDPOINT_PATH.format(id=self.email_device1.id))
        self.email_device1.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Verify challenge
        response = self.client.post(self._REST_ENDPOINT_PATH.format(id=self.email_device1.id),
                                    data={'challenge': self.email_device1.challenge},
                                    format='json')
        self.email_device1.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(self.email_device1.challenge)
        self.assertTrue(self.email_device1.confirmed)
        self.assertIsNone(self.email_device1.verification_timeout)
        self.assertEqual(self.email_device1.verification_failure_count, 0)

    def test_method_post_verify_challenge_none(self):
        # Verify challenge
        response = self.client.post(self._REST_ENDPOINT_PATH.format(id=self.email_device1.id),
                                    data={'challenge': None},
                                    format='json')
        self.email_device1.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsNone(self.email_device1.challenge)
        self.assertFalse(self.email_device1.confirmed)
        self.assertIsNone(self.email_device1.verification_timeout)
        self.assertEqual(self.email_device1.verification_failure_count, 0)

    def test_method_post_verify_challenge_empty_string(self):
        # Verify challenge
        response = self.client.post(self._REST_ENDPOINT_PATH.format(id=self.email_device1.id),
                                    data={'challenge': ''},
                                    format='json')
        self.email_device1.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsNone(self.email_device1.challenge)
        self.assertFalse(self.email_device1.confirmed)
        self.assertIsNone(self.email_device1.verification_timeout)
        self.assertEqual(self.email_device1.verification_failure_count, 0)

    def test_method_post_verify_challenge_invalid_challenge(self):
        from freezegun import freeze_time
        from django.utils import timezone
        from datetime import timedelta

        # Verify challenge
        with freeze_time():
            response = self.client.post(self._REST_ENDPOINT_PATH.format(id=self.email_device1.id),
                                        data={'challenge': 'INVALID_CHALLENGE'},
                                        format='json')
            self.email_device1.refresh_from_db()
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
            self.assertIsNone(self.email_device1.challenge)
            self.assertFalse(self.email_device1.confirmed)
            self.assertEqual(self.email_device1.verification_timeout, timezone.now() + timedelta(seconds=1))
            self.assertEqual(self.email_device1.verification_failure_count, 1)

    def test_method_post_verify_challenge_valid_challenge(self):
        # Verify challenge
        response = self.client.post(self._REST_ENDPOINT_PATH.format(id=self.email_device1.id),
                                    data={'challenge': self.email_device1.challenge},
                                    format='json')
        self.email_device1.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsNone(self.email_device1.challenge)
        self.assertFalse(self.email_device1.confirmed)
        self.assertIsNone(self.email_device1.verification_timeout)
        self.assertEqual(self.email_device1.verification_failure_count, 0)

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
