from django.test import override_settings

from rest_framework.test import APITestCase
from rest_framework import status

from datetime import timedelta


def _send_password(*args):
    pass


class TestEmailTokenUpdate(APITestCase):
    """
    This class is designed to test django_flex_user.views.EmailToken
    """
    _REST_ENDPOINT_PATH = '/account/otp-tokens/{type}/{id}'

    class _ContentType:
        class ApplicationJSON:
            password_values = (
                {},
                {'password': None},
                {'password': ''},
                {'password': 'validPassword'},
                {'password': 'invalidPassword'}
            )

        class MultipartFormData:
            password_values = (
                {},
                {'password': ''},
                {'password': 'validPassword'},
                {'password': 'invalidPassword'}
            )

    def setUp(self):
        from django_flex_user.models.user import FlexUser
        from django_flex_user.models.otp import EmailToken

        user = FlexUser.objects.create_user(email='validEmail@example.com')
        self.otp_token = EmailToken.objects.get(user=user)
        self._REST_ENDPOINT_PATH = TestEmailTokenUpdate._REST_ENDPOINT_PATH.format(type='email', id=self.otp_token.id)

    @override_settings(
        FLEX_USER_OTP_EMAIL_FUNCTION='django_flex_user.tests.otp.test_endpoint_otp_tokens_email_id._send_password'
    )
    @override_settings(
        FLEX_USER_OTP_SMS_FUNCTION='django_flex_user.tests.otp.test_endpoint_otp_tokens_email_id._send_password'
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

    @override_settings(FLEX_USER_OTP_TTL=timedelta(minutes=15))
    def test_method_post_format_application_json_generate_password_check_password(self):
        from django.db import transaction
        from freezegun import freeze_time

        for data in self._ContentType.ApplicationJSON.password_values:
            with self.subTest(**data), freeze_time(), transaction.atomic():
                from django.utils import timezone
                from datetime import timedelta

                self.otp_token.refresh_from_db()
                self.otp_token.generate_password()

                """
                When the value for "password" is "validPassword" we replace it with the actual password stored in
                self.otp_token.password before passing it to the POST method.
                """
                d = {'password': self.otp_token.password} if data.get('password') == 'validPassword' else data

                response = self.client.post(self._REST_ENDPOINT_PATH, data=d, format='json')

                if not data.get('password'):
                    """
                    If the supplied password is either undefined, None or the empty string,
                    django_flex_user.views.EmailToken.post should return HTTP status code HTTP_400_BAD_REQUEST.
                    """
                    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

                    self.otp_token.refresh_from_db()
                    self.assertIsNotNone(self.otp_token.password)
                    self.assertFalse(self.otp_token.verified)
                    self.assertIsNone(self.otp_token.timeout)
                    self.assertEqual(self.otp_token.failure_count, 0)
                    self.assertEqual(self.otp_token.expiration, timezone.now() + timedelta(minutes=15))
                elif data['password'] == 'validPassword':
                    """
                    If the supplied password is defined and valid, django_flex_user.views.EmailToken.post should
                    return HTTP status code HTTP_200_OK.
                    """
                    self.assertEqual(response.status_code, status.HTTP_200_OK)

                    self.otp_token.refresh_from_db()
                    self.assertIsNone(self.otp_token.password)
                    self.assertTrue(self.otp_token.verified)
                    self.assertIsNone(self.otp_token.timeout)
                    self.assertEqual(self.otp_token.failure_count, 0)
                    self.assertIsNone(self.otp_token.expiration)
                elif data['password'] == 'invalidPassword':
                    """
                    If the supplied password is defined and invalid, django_flex_user.views.EmailToken.post
                    should return HTTP status code HTTP_401_UNAUTHORIZED.
                    """
                    self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

                    self.otp_token.refresh_from_db()
                    self.assertIsNotNone(self.otp_token.password)
                    self.assertFalse(self.otp_token.verified)
                    self.assertEqual(self.otp_token.timeout, timezone.now() + timedelta(seconds=1))
                    self.assertEqual(self.otp_token.failure_count, 1)
                    self.assertEqual(self.otp_token.expiration, timezone.now() + timedelta(minutes=15))
                else:
                    self.assertFalse(True)

                transaction.set_rollback(True)

    @override_settings(FLEX_USER_OTP_TTL=timedelta(minutes=15))
    def test_method_post_format_multipart_form_data_generate_password_check_password(self):
        from django.db import transaction
        from freezegun import freeze_time

        self.otp_token.generate_password()

        for data in self._ContentType.MultipartFormData.password_values:
            with self.subTest(**data), freeze_time(), transaction.atomic():
                from django.utils import timezone
                from datetime import timedelta

                self.otp_token.refresh_from_db()
                self.otp_token.generate_password()

                """
                When the value for "password" is "validPassword" we replace it with the actual password stored in
                self.otp_token.password before passing it to the POST method.
                """
                d = {'password': self.otp_token.password} if data.get('password') == 'validPassword' else data

                response = self.client.post(self._REST_ENDPOINT_PATH, data=d, format='multipart')

                if not data.get('password'):
                    """
                    If the supplied password is either undefined or the empty string,
                    django_flex_user.views.EmailToken.post should return HTTP status code HTTP_400_BAD_REQUEST.
                    """
                    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

                    self.otp_token.refresh_from_db()
                    self.assertIsNotNone(self.otp_token.password)
                    self.assertFalse(self.otp_token.verified)
                    self.assertIsNone(self.otp_token.timeout)
                    self.assertEqual(self.otp_token.failure_count, 0)
                    self.assertEqual(self.otp_token.expiration, timezone.now() + timedelta(minutes=15))
                elif data['password'] == 'validPassword':
                    """
                    If the supplied password is defined and valid, django_flex_user.views.EmailToken.post should
                    return HTTP status code HTTP_200_OK.
                    """
                    # todo: this test randomly fails and I don't know why
                    self.assertEqual(response.status_code, status.HTTP_200_OK)

                    self.otp_token.refresh_from_db()
                    self.assertIsNone(self.otp_token.password)
                    self.assertTrue(self.otp_token.verified)
                    self.assertIsNone(self.otp_token.timeout)
                    self.assertEqual(self.otp_token.failure_count, 0)
                    self.assertIsNone(self.otp_token.expiration)
                elif data['password'] == 'invalidPassword':
                    """
                    If the supplied password is defined and invalid, django_flex_user.views.EmailToken.post
                    should return HTTP status code HTTP_401_UNAUTHORIZED.
                    """
                    self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

                    self.otp_token.refresh_from_db()
                    self.assertIsNotNone(self.otp_token.password)
                    self.assertFalse(self.otp_token.verified)
                    self.assertEqual(self.otp_token.timeout, timezone.now() + timedelta(seconds=1))
                    self.assertEqual(self.otp_token.failure_count, 1)
                    self.assertEqual(self.otp_token.expiration, timezone.now() + timedelta(minutes=15))
                else:
                    self.assertFalse(True)

                transaction.set_rollback(True)

    def test_method_post_format_application_json_check_password(self):
        from django.db import transaction
        from freezegun import freeze_time

        for data in self._ContentType.ApplicationJSON.password_values:
            with self.subTest(**data), freeze_time(), transaction.atomic():
                from django.utils import timezone
                from datetime import timedelta

                """
                When the value for "password" is "validPassword" we replace it with the actual password stored in
                self.otp_token.password before passing it to the POST method.
                """
                d = {'password': self.otp_token.password} if data.get('password') == 'validPassword' else data

                response = self.client.post(self._REST_ENDPOINT_PATH, data=d, format='json')

                if not data.get('password') or data['password'] == 'validPassword':
                    """
                    If the supplied password is either undefined, None or the empty string OR if the supplied password
                    is defined and valid the django_flex_user.views.EmailToken.post should return HTTP status code
                    HTTP_400_BAD_REQUEST.
                    """
                    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

                    self.otp_token.refresh_from_db()
                    self.assertIsNone(self.otp_token.password)
                    self.assertFalse(self.otp_token.verified)
                    self.assertIsNone(self.otp_token.timeout)
                    self.assertEqual(self.otp_token.failure_count, 0)
                    self.assertIsNone(self.otp_token.expiration)
                elif data['password'] == 'invalidPassword':
                    """
                    If the supplied password is defined and invalid, or defined and valid,
                    django_flex_user.views.EmailToken.post should return HTTP status code HTTP_401_UNAUTHORIZED.
                    """
                    self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

                    self.otp_token.refresh_from_db()
                    self.assertIsNone(self.otp_token.password)
                    self.assertFalse(self.otp_token.verified)
                    self.assertEqual(self.otp_token.timeout, timezone.now() + timedelta(seconds=1))
                    self.assertEqual(self.otp_token.failure_count, 1)
                    self.assertIsNone(self.otp_token.expiration)
                else:
                    self.assertFalse(True)

                transaction.set_rollback(True)

    def test_method_post_format_multipart_form_data_check_password(self):
        from django.db import transaction
        from freezegun import freeze_time

        for data in self._ContentType.MultipartFormData.password_values:
            with self.subTest(**data), freeze_time(), transaction.atomic():
                from django.utils import timezone
                from datetime import timedelta

                """
                When the value for "password" is "validPassword" we replace it with the actual password stored in
                self.otp_token.password before passing it to the POST method.
                
                Also, because mutlipart/form-data cannot accept None values, we perform an extra step to coerce
                password values which are None to the empty string.
                """
                d = {'password': self.otp_token.password or ''} if data.get('password') == 'validPassword' else data

                response = self.client.post(self._REST_ENDPOINT_PATH, data=d, format='multipart')

                if not data.get('password') or data['password'] == 'validPassword':
                    """
                    If the supplied password is either undefined, None or the empty string OR if the supplied password
                    is defined and valid the django_flex_user.views.EmailToken.post should return HTTP status code
                    HTTP_400_BAD_REQUEST.
                    """
                    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

                    self.otp_token.refresh_from_db()
                    self.assertIsNone(self.otp_token.password)
                    self.assertFalse(self.otp_token.verified)
                    self.assertIsNone(self.otp_token.timeout)
                    self.assertEqual(self.otp_token.failure_count, 0)
                    self.assertIsNone(self.otp_token.expiration)
                elif data['password'] == 'invalidPassword':
                    """
                    If the supplied password is defined and invalid, or defined and valid,
                    django_flex_user.views.EmailToken.post should return HTTP status code HTTP_401_UNAUTHORIZED.
                    """
                    self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

                    self.otp_token.refresh_from_db()
                    self.assertIsNone(self.otp_token.password)
                    self.assertFalse(self.otp_token.verified)
                    self.assertEqual(self.otp_token.timeout, timezone.now() + timedelta(seconds=1))
                    self.assertEqual(self.otp_token.failure_count, 1)
                    self.assertIsNone(self.otp_token.expiration)
                else:
                    self.assertFalse(True)

                transaction.set_rollback(True)

    def test_method_post_throttling(self):
        from freezegun import freeze_time

        self.otp_token.generate_password()

        with freeze_time() as frozen_datetime:
            for i in range(0, 10):
                """
                Here we try to verify an invalid password. django_flex_user.views.EmailToken.post should return HTTP
                status code HTTP_401_UNAUTHORIZED and subsequent verification attempts should be timed out for the next
                2^i seconds.
                """
                response = self.client.post(self._REST_ENDPOINT_PATH, data={'password': 'invalidPassword'})
                self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

                """
                Here we simulate the verification timeout period. For each second of the timeout period we attempt to
                verify again. django_flex_user.views.EmailToken.post should return HTTP status code
                HTTP_429_TOO_MANY_REQUESTS each time.
                """
                for j in range(0, 2 ** i):
                    """
                    Try to verify an invalid password.
                    """
                    response = self.client.post(self._REST_ENDPOINT_PATH, data={'password': 'invalidPassword'})
                    self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
                    """
                    Try to verify a valid password.
                    """
                    response = self.client.post(self._REST_ENDPOINT_PATH, data={'password': self.otp_token.password})
                    self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
                    """
                    Advance time by one second.
                    """
                    frozen_datetime.tick()

    @override_settings(FLEX_USER_OTP_TTL=timedelta(minutes=15))
    def test_method_post_expiration(self):
        from freezegun import freeze_time
        from datetime import timedelta
        from django.utils import timezone

        with freeze_time() as frozen_datetime:
            self.otp_token.generate_password()

            # Advance time to exactly the expiration time
            frozen_datetime.tick(timedelta(minutes=15))

            response = self.client.post(self._REST_ENDPOINT_PATH, data={'password': self.otp_token.password})
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

            self.otp_token.refresh_from_db()
            self.assertFalse(self.otp_token.verified)
            self.assertEqual(self.otp_token.timeout, timezone.now() + timedelta(seconds=1))
            self.assertEqual(self.otp_token.failure_count, 1)
            self.assertEqual(self.otp_token.expiration, timezone.now())

            # Advance time past the expiration
            frozen_datetime.tick(timedelta(minutes=15))

            response = self.client.post(self._REST_ENDPOINT_PATH, data={'password': self.otp_token.password})
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

            self.otp_token.refresh_from_db()
            self.assertFalse(self.otp_token.verified)
            self.assertEqual(self.otp_token.timeout, timezone.now() + timedelta(seconds=2))
            self.assertEqual(self.otp_token.failure_count, 2)
            self.assertEqual(self.otp_token.expiration, timezone.now() - timedelta(minutes=15))

    def test_method_post_generate_password_update_email_check_password(self):
        from freezegun import freeze_time
        from django.utils import timezone
        from datetime import timedelta

        with freeze_time():
            self.otp_token.generate_password()
            password = self.otp_token.password

            # Change the user's email address to a phony one after generating password
            self.otp_token.user.email = 'president@whitehouse.gov'
            self.otp_token.user.full_clean()
            self.otp_token.user.save()

            response = self.client.post(self._REST_ENDPOINT_PATH, data={'password': password})
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

            # Ensure the generated password fails
            self.otp_token.refresh_from_db()
            self.assertFalse(self.otp_token.verified)
            self.assertEqual(self.otp_token.timeout, timezone.now() + timedelta(seconds=1))
            self.assertEqual(self.otp_token.failure_count, 1)
            self.assertIsNone(self.otp_token.expiration)

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
