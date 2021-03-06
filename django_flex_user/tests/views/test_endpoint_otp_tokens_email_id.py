from django.test import override_settings

from rest_framework.test import APITestCase
from rest_framework import status

from datetime import timedelta


def _send_password(*args):
    pass


class TestEmailTokenRetrieveUpdate(APITestCase):
    """
    This class is designed to test django_flex_user.views.EmailToken
    """
    _REST_ENDPOINT_PATH = '/api/accounts/otp-tokens/{type}/{id}'

    def setUp(self):
        from django_flex_user.models.user import FlexUser

        user = FlexUser.objects.create_user(email='validEmail@example.com')
        self.otp_token = user.emailtoken_set.first()
        self._REST_ENDPOINT_PATH = TestEmailTokenRetrieveUpdate._REST_ENDPOINT_PATH.format(type='email',
                                                                                           id=self.otp_token.id)

    # Method GET

    @override_settings(
        FLEX_USER_OTP_EMAIL_FUNCTION='django_flex_user.tests.views.test_endpoint_otp_tokens_email_id._send_password'
    )
    @override_settings(
        FLEX_USER_OTP_SMS_FUNCTION='django_flex_user.tests.views.test_endpoint_otp_tokens_email_id._send_password'
    )
    @override_settings(FLEX_USER_OTP_TTL=timedelta(minutes=15))
    def test_method_get(self):
        from freezegun import freeze_time
        from django.utils import timezone
        from datetime import timedelta

        with freeze_time():
            response = self.client.get(self._REST_ENDPOINT_PATH)
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

            self.otp_token.refresh_from_db()
            self.assertFalse(self.otp_token.verified)
            self.assertIsNotNone(self.otp_token.password)
            self.assertNotEqual(self.otp_token.password, '')
            self.assertEqual(len(self.otp_token.password), self.otp_token.password_length)
            self.assertIsNone(self.otp_token.timeout)
            self.assertEqual(self.otp_token.failure_count, 0)
            self.assertEqual(self.otp_token.expiration, timezone.now() + timedelta(minutes=15))

    # Method POST, format application/json, generate password then check password

    @override_settings(FLEX_USER_OTP_TTL=timedelta(minutes=15))
    def test_method_post_format_application_json_generate_password_check_password_undefined(self):
        from freezegun import freeze_time
        from django.utils import timezone
        from datetime import timedelta

        data = {}

        with freeze_time():
            self.otp_token.generate_password()

            response = self.client.post(self._REST_ENDPOINT_PATH, data=data, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

            self.otp_token.refresh_from_db()
            self.assertIsNotNone(self.otp_token.password)
            self.assertFalse(self.otp_token.verified)
            self.assertIsNone(self.otp_token.timeout)
            self.assertEqual(self.otp_token.failure_count, 0)
            self.assertEqual(self.otp_token.expiration, timezone.now() + timedelta(minutes=15))

    @override_settings(FLEX_USER_OTP_TTL=timedelta(minutes=15))
    def test_method_post_format_application_json_generate_password_check_password_none(self):
        from freezegun import freeze_time
        from django.utils import timezone
        from datetime import timedelta

        data = {'password': None}

        with freeze_time():
            self.otp_token.generate_password()

            response = self.client.post(self._REST_ENDPOINT_PATH, data=data, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

            self.otp_token.refresh_from_db()
            self.assertIsNotNone(self.otp_token.password)
            self.assertFalse(self.otp_token.verified)
            self.assertIsNone(self.otp_token.timeout)
            self.assertEqual(self.otp_token.failure_count, 0)
            self.assertEqual(self.otp_token.expiration, timezone.now() + timedelta(minutes=15))

    @override_settings(FLEX_USER_OTP_TTL=timedelta(minutes=15))
    def test_method_post_format_application_json_generate_password_check_password_empty_string(self):
        from freezegun import freeze_time
        from django.utils import timezone
        from datetime import timedelta

        data = {'password': ''}

        with freeze_time():
            self.otp_token.generate_password()

            response = self.client.post(self._REST_ENDPOINT_PATH, data=data, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

            self.otp_token.refresh_from_db()
            self.assertIsNotNone(self.otp_token.password)
            self.assertFalse(self.otp_token.verified)
            self.assertIsNone(self.otp_token.timeout)
            self.assertEqual(self.otp_token.failure_count, 0)
            self.assertEqual(self.otp_token.expiration, timezone.now() + timedelta(minutes=15))

    def test_method_post_format_application_json_generate_password_check_password_valid_password(self):
        from freezegun import freeze_time

        with freeze_time():
            self.otp_token.generate_password()

            data = {'password': self.otp_token.password}

            response = self.client.post(self._REST_ENDPOINT_PATH, data=data, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            self.otp_token.refresh_from_db()
            self.assertIsNone(self.otp_token.password)
            self.assertTrue(self.otp_token.verified)
            self.assertIsNone(self.otp_token.timeout)
            self.assertEqual(self.otp_token.failure_count, 0)
            self.assertIsNone(self.otp_token.expiration)

    @override_settings(FLEX_USER_OTP_TTL=timedelta(minutes=15))
    def test_method_post_format_application_json_generate_password_check_password_invalid_password(self):
        from freezegun import freeze_time
        from django.utils import timezone
        from datetime import timedelta

        data = {'password': 'invalidPassword'}

        with freeze_time():
            self.otp_token.generate_password()

            response = self.client.post(self._REST_ENDPOINT_PATH, data=data, format='json')
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

            self.otp_token.refresh_from_db()
            self.assertIsNotNone(self.otp_token.password)
            self.assertFalse(self.otp_token.verified)
            self.assertEqual(self.otp_token.timeout, timezone.now() + timedelta(seconds=1))
            self.assertEqual(self.otp_token.failure_count, 1)
            self.assertEqual(self.otp_token.expiration, timezone.now() + timedelta(minutes=15))

    @override_settings(FLEX_USER_OTP_TTL=timedelta(minutes=15))
    def test_method_post_format_application_json_generate_password_check_password_expired(self):
        from freezegun import freeze_time
        from datetime import timedelta
        from django.utils import timezone

        with freeze_time() as frozen_datetime:
            self.otp_token.generate_password()

            # Advance time to exactly the expiration time
            frozen_datetime.tick(timedelta(minutes=15))

            response = self.client.post(self._REST_ENDPOINT_PATH, data={'password': self.otp_token.password},
                                        format='json')
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

            self.otp_token.refresh_from_db()
            self.assertFalse(self.otp_token.verified)
            self.assertEqual(self.otp_token.timeout, timezone.now() + timedelta(seconds=1))
            self.assertEqual(self.otp_token.failure_count, 1)
            self.assertEqual(self.otp_token.expiration, timezone.now())

            # Advance time past the expiration time
            frozen_datetime.tick(timedelta(minutes=15))

            response = self.client.post(self._REST_ENDPOINT_PATH, data={'password': self.otp_token.password},
                                        format='json')
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

            self.otp_token.refresh_from_db()
            self.assertFalse(self.otp_token.verified)
            self.assertEqual(self.otp_token.timeout, timezone.now() + timedelta(seconds=2))
            self.assertEqual(self.otp_token.failure_count, 2)
            self.assertEqual(self.otp_token.expiration, timezone.now() - timedelta(minutes=15))

    def test_method_post_format_application_json_generate_password_check_password_throttling(self):
        from freezegun import freeze_time

        self.otp_token.generate_password()

        with freeze_time() as frozen_datetime:
            for i in range(0, 10):
                # Here we try to verify an invalid password. django_flex_user.views.EmailToken.post should return HTTP
                # status code HTTP_401_UNAUTHORIZED and subsequent verification attempts should be timed out for the
                # next 2^i seconds.
                response = self.client.post(self._REST_ENDPOINT_PATH, data={'password': 'invalidPassword'},
                                            format='json')
                self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

                # Here we simulate the verification timeout period. For each second of the timeout period we attempt to
                # verify again. django_flex_user.views.EmailToken.post should return HTTP status code
                # HTTP_429_TOO_MANY_REQUESTS each time.
                for j in range(0, 2 ** i):
                    # Try to verify an invalid password.
                    response = self.client.post(self._REST_ENDPOINT_PATH, data={'password': 'invalidPassword'},
                                                format='json')
                    self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
                    # Try to verify a valid password.
                    response = self.client.post(self._REST_ENDPOINT_PATH, data={'password': self.otp_token.password},
                                                format='json')
                    self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
                    # Advance time by one second.
                    frozen_datetime.tick()

    # Method POST, format application/json, skip generate password, check password

    def test_method_post_format_application_json_check_password_undefined(self):
        data = {}

        response = self.client.post(self._REST_ENDPOINT_PATH, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.otp_token.refresh_from_db()
        self.assertIsNone(self.otp_token.password)
        self.assertFalse(self.otp_token.verified)
        self.assertIsNone(self.otp_token.timeout)
        self.assertEqual(self.otp_token.failure_count, 0)
        self.assertIsNone(self.otp_token.expiration)

    def test_method_post_format_application_json_check_password_none(self):
        data = {'password': None}

        response = self.client.post(self._REST_ENDPOINT_PATH, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.otp_token.refresh_from_db()
        self.assertIsNone(self.otp_token.password)
        self.assertFalse(self.otp_token.verified)
        self.assertIsNone(self.otp_token.timeout)
        self.assertEqual(self.otp_token.failure_count, 0)
        self.assertIsNone(self.otp_token.expiration)

    def test_method_post_format_application_json_check_password_empty_string(self):
        data = {'password': ''}

        response = self.client.post(self._REST_ENDPOINT_PATH, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.otp_token.refresh_from_db()
        self.assertIsNone(self.otp_token.password)
        self.assertFalse(self.otp_token.verified)
        self.assertIsNone(self.otp_token.timeout)
        self.assertEqual(self.otp_token.failure_count, 0)
        self.assertIsNone(self.otp_token.expiration)

    def test_method_post_format_application_json_check_password_valid_password(self):
        data = {'password': self.otp_token.password}

        response = self.client.post(self._REST_ENDPOINT_PATH, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.otp_token.refresh_from_db()
        self.assertIsNone(self.otp_token.password)
        self.assertFalse(self.otp_token.verified)
        self.assertIsNone(self.otp_token.timeout)
        self.assertEqual(self.otp_token.failure_count, 0)
        self.assertIsNone(self.otp_token.expiration)

    @override_settings(FLEX_USER_OTP_TTL=timedelta(minutes=15))
    def test_method_post_format_application_json_check_password_invalid_password(self):
        from freezegun import freeze_time
        from django.utils import timezone
        from datetime import timedelta

        data = {'password': 'invalidPassword'}

        with freeze_time():
            response = self.client.post(self._REST_ENDPOINT_PATH, data=data, format='json')
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

            self.otp_token.refresh_from_db()
            self.assertIsNone(self.otp_token.password)
            self.assertFalse(self.otp_token.verified)
            self.assertEqual(self.otp_token.timeout, timezone.now() + timedelta(seconds=1))
            self.assertEqual(self.otp_token.failure_count, 1)
            self.assertIsNone(self.otp_token.expiration)

    # Method POST, format multipart/form-data, generate password then check password

    @override_settings(FLEX_USER_OTP_TTL=timedelta(minutes=15))
    def test_method_post_format_multipart_form_data_generate_password_check_password_undefined(self):
        from freezegun import freeze_time
        from django.utils import timezone
        from datetime import timedelta

        data = {}

        with freeze_time():
            self.otp_token.generate_password()

            response = self.client.post(self._REST_ENDPOINT_PATH, data=data, format='multipart')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

            self.otp_token.refresh_from_db()
            self.assertIsNotNone(self.otp_token.password)
            self.assertFalse(self.otp_token.verified)
            self.assertIsNone(self.otp_token.timeout)
            self.assertEqual(self.otp_token.failure_count, 0)
            self.assertEqual(self.otp_token.expiration, timezone.now() + timedelta(minutes=15))

    @override_settings(FLEX_USER_OTP_TTL=timedelta(minutes=15))
    def test_method_post_format_multipart_form_data_generate_password_check_password_empty_string(self):
        from freezegun import freeze_time
        from django.utils import timezone
        from datetime import timedelta

        data = {'password': ''}

        with freeze_time():
            self.otp_token.generate_password()

            response = self.client.post(self._REST_ENDPOINT_PATH, data=data, format='multipart')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

            self.otp_token.refresh_from_db()
            self.assertIsNotNone(self.otp_token.password)
            self.assertFalse(self.otp_token.verified)
            self.assertIsNone(self.otp_token.timeout)
            self.assertEqual(self.otp_token.failure_count, 0)
            self.assertEqual(self.otp_token.expiration, timezone.now() + timedelta(minutes=15))

    def test_method_post_format_multipart_form_data_generate_password_check_password_valid_password(self):
        from freezegun import freeze_time

        with freeze_time():
            self.otp_token.generate_password()

            data = {'password': self.otp_token.password}

            response = self.client.post(self._REST_ENDPOINT_PATH, data=data, format='multipart')
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            self.otp_token.refresh_from_db()
            self.assertIsNone(self.otp_token.password)
            self.assertTrue(self.otp_token.verified)
            self.assertIsNone(self.otp_token.timeout)
            self.assertEqual(self.otp_token.failure_count, 0)
            self.assertIsNone(self.otp_token.expiration)

    @override_settings(FLEX_USER_OTP_TTL=timedelta(minutes=15))
    def test_method_post_format_multipart_form_data_generate_password_check_password_invalid_password(self):
        from freezegun import freeze_time
        from django.utils import timezone
        from datetime import timedelta

        data = {'password': 'invalidPassword'}

        with freeze_time():
            self.otp_token.generate_password()

            response = self.client.post(self._REST_ENDPOINT_PATH, data=data, format='multipart')
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

            self.otp_token.refresh_from_db()
            self.assertIsNotNone(self.otp_token.password)
            self.assertFalse(self.otp_token.verified)
            self.assertEqual(self.otp_token.timeout, timezone.now() + timedelta(seconds=1))
            self.assertEqual(self.otp_token.failure_count, 1)
            self.assertEqual(self.otp_token.expiration, timezone.now() + timedelta(minutes=15))

    @override_settings(FLEX_USER_OTP_TTL=timedelta(minutes=15))
    def test_method_post_format_multipart_form_data_generate_password_check_password_expired(self):
        from freezegun import freeze_time
        from datetime import timedelta
        from django.utils import timezone

        with freeze_time() as frozen_datetime:
            self.otp_token.generate_password()

            # Advance time to exactly the expiration time
            frozen_datetime.tick(timedelta(minutes=15))

            response = self.client.post(self._REST_ENDPOINT_PATH, data={'password': self.otp_token.password},
                                        format='multipart')
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

            self.otp_token.refresh_from_db()
            self.assertFalse(self.otp_token.verified)
            self.assertEqual(self.otp_token.timeout, timezone.now() + timedelta(seconds=1))
            self.assertEqual(self.otp_token.failure_count, 1)
            self.assertEqual(self.otp_token.expiration, timezone.now())

            # Advance time past the expiration time
            frozen_datetime.tick(timedelta(minutes=15))

            response = self.client.post(self._REST_ENDPOINT_PATH, data={'password': self.otp_token.password},
                                        format='multipart')
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

            self.otp_token.refresh_from_db()
            self.assertFalse(self.otp_token.verified)
            self.assertEqual(self.otp_token.timeout, timezone.now() + timedelta(seconds=2))
            self.assertEqual(self.otp_token.failure_count, 2)
            self.assertEqual(self.otp_token.expiration, timezone.now() - timedelta(minutes=15))

    def test_method_post_format_multipart_form_data_generate_password_check_password_throttling(self):
        from freezegun import freeze_time

        self.otp_token.generate_password()

        with freeze_time() as frozen_datetime:
            for i in range(0, 10):
                # Here we try to verify an invalid password. django_flex_user.views.EmailToken.post should return HTTP
                # status code HTTP_401_UNAUTHORIZED and subsequent verification attempts should be timed out for the
                # next 2^i seconds.
                response = self.client.post(self._REST_ENDPOINT_PATH, data={'password': 'invalidPassword'},
                                            format='multipart')
                self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

                # Here we simulate the verification timeout period. For each second of the timeout period we attempt to
                # verify again. django_flex_user.views.EmailToken.post should return HTTP status code
                # HTTP_429_TOO_MANY_REQUESTS each time.
                for j in range(0, 2 ** i):
                    # Try to verify an invalid password.
                    response = self.client.post(self._REST_ENDPOINT_PATH, data={'password': 'invalidPassword'},
                                                format='multipart')
                    self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
                    # Try to verify a valid password.
                    response = self.client.post(self._REST_ENDPOINT_PATH, data={'password': self.otp_token.password},
                                                format='multipart')
                    self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
                    # Advance time by one second.
                    frozen_datetime.tick()

    # Method POST, format multipart/form-data, skip generate password, check password

    def test_method_post_format_multipart_form_data_check_password_undefined(self):
        data = {}

        response = self.client.post(self._REST_ENDPOINT_PATH, data=data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.otp_token.refresh_from_db()
        self.assertIsNone(self.otp_token.password)
        self.assertFalse(self.otp_token.verified)
        self.assertIsNone(self.otp_token.timeout)
        self.assertEqual(self.otp_token.failure_count, 0)
        self.assertIsNone(self.otp_token.expiration)

    def test_method_post_format_multipart_form_data_check_password_empty_string(self):
        data = {'password': ''}

        response = self.client.post(self._REST_ENDPOINT_PATH, data=data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.otp_token.refresh_from_db()
        self.assertIsNone(self.otp_token.password)
        self.assertFalse(self.otp_token.verified)
        self.assertIsNone(self.otp_token.timeout)
        self.assertEqual(self.otp_token.failure_count, 0)
        self.assertIsNone(self.otp_token.expiration)

    @override_settings(FLEX_USER_OTP_TTL=timedelta(minutes=15))
    def test_method_post_format_multipart_form_data_check_password_invalid_password(self):
        from freezegun import freeze_time
        from django.utils import timezone
        from datetime import timedelta

        data = {'password': 'invalidPassword'}

        with freeze_time():
            response = self.client.post(self._REST_ENDPOINT_PATH, data=data, format='multipart')
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

            self.otp_token.refresh_from_db()
            self.assertIsNone(self.otp_token.password)
            self.assertFalse(self.otp_token.verified)
            self.assertEqual(self.otp_token.timeout, timezone.now() + timedelta(seconds=1))
            self.assertEqual(self.otp_token.failure_count, 1)
            self.assertIsNone(self.otp_token.expiration)

    # Method PUT

    def test_method_put(self):
        response = self.client.put(self._REST_ENDPOINT_PATH)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    # Method PATCH

    def test_method_patch(self):
        response = self.client.patch(self._REST_ENDPOINT_PATH)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    # Method DELETE

    def test_method_delete(self):
        response = self.client.delete(self._REST_ENDPOINT_PATH)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    # Method OPTIONS

    def test_method_options(self):
        response = self.client.options(self._REST_ENDPOINT_PATH)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestMethodPostGeneratePasswordUpdateEmailCheckPassword(APITestCase):
    """
    This class is designed to test django_flex_user.views.EmailToken
    """

    def test_method_post_generate_password_update_email_check_password(self):
        from django_flex_user.models.user import FlexUser
        from freezegun import freeze_time
        from django.utils import timezone
        from datetime import timedelta

        user = FlexUser.objects.create_user(email='validEmail@example.com')
        email_token = user.emailtoken_set.first()

        with freeze_time():
            email_token.generate_password()
            password = email_token.password

            # Change the user's email address to a phony one after generating password
            email_token.user.email = 'president@whitehouse.gov'
            email_token.user.full_clean()
            email_token.user.save()

            response = self.client.post(f'/api/accounts/otp-tokens/email/{email_token.id}', data={'password': password})
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

            # Ensure the generated password fails
            email_token.refresh_from_db()
            self.assertFalse(email_token.verified)
            self.assertEqual(email_token.timeout, timezone.now() + timedelta(seconds=1))
            self.assertEqual(email_token.failure_count, 1)
            self.assertIsNone(email_token.expiration)
