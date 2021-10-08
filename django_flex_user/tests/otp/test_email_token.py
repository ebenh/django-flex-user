from django.test import TestCase
from django.test import override_settings
from datetime import timedelta


class TestEmailToken(TestCase):
    """
    This class is designed to test django_flex_user.models.EmailToken
    """

    def setUp(self):
        from django_flex_user.models.user import FlexUser
        from django_flex_user.models.otp import EmailToken

        user = FlexUser.objects.create_user(email='validEmail@example.com')
        self.otp_token = EmailToken.objects.get(user=user)

    @override_settings(FLEX_USER_OTP_TTL=timedelta(minutes=15))
    def test_generate_password(self):
        from freezegun import freeze_time
        from django.utils import timezone

        with freeze_time():
            self.otp_token.generate_password()

            self.assertFalse(self.otp_token.verified)
            self.assertIsNotNone(self.otp_token.password)
            self.assertNotEqual(self.otp_token.password, '')
            self.assertEqual(len(self.otp_token.password), self.otp_token.password_length)
            self.assertIsNone(self.otp_token.timeout)
            self.assertEqual(self.otp_token.failure_count, 0)
            self.assertEqual(self.otp_token.expiration, timezone.now() + timedelta(minutes=15))

    @override_settings(FLEX_USER_OTP_TTL=timedelta(minutes=15))
    def test_generate_password_check_password_undefined(self):
        from freezegun import freeze_time
        from django.utils import timezone

        with freeze_time():
            self.otp_token.generate_password()

            self.assertRaises(TypeError, self.otp_token.check_password)
            self.assertFalse(self.otp_token.verified)
            self.assertIsNone(self.otp_token.timeout)
            self.assertEqual(self.otp_token.failure_count, 0)
            self.assertEqual(self.otp_token.expiration, timezone.now() + timedelta(minutes=15))

    @override_settings(FLEX_USER_OTP_TTL=timedelta(minutes=15))
    def test_generate_password_check_password_none(self):
        from freezegun import freeze_time
        from django.utils import timezone
        from datetime import timedelta

        with freeze_time():
            self.otp_token.generate_password()

            self.assertFalse(self.otp_token.check_password(None))
            self.assertFalse(self.otp_token.verified)
            self.assertEqual(self.otp_token.timeout, timezone.now() + timedelta(seconds=1))
            self.assertEqual(self.otp_token.failure_count, 1)
            self.assertEqual(self.otp_token.expiration, timezone.now() + timedelta(minutes=15))

    @override_settings(FLEX_USER_OTP_TTL=timedelta(minutes=15))
    def test_generate_password_check_password_empty_string(self):
        from freezegun import freeze_time
        from django.utils import timezone
        from datetime import timedelta

        with freeze_time():
            self.otp_token.generate_password()

            self.assertFalse(self.otp_token.check_password(''))
            self.assertFalse(self.otp_token.verified)
            self.assertEqual(self.otp_token.timeout, timezone.now() + timedelta(seconds=1))
            self.assertEqual(self.otp_token.failure_count, 1)
            self.assertEqual(self.otp_token.expiration, timezone.now() + timedelta(minutes=15))

    def test_generate_password_check_password_valid_password(self):
        from freezegun import freeze_time

        with freeze_time():
            self.otp_token.generate_password()

            self.assertTrue(self.otp_token.check_password(self.otp_token.password))
            self.assertTrue(self.otp_token.verified)
            self.assertIsNone(self.otp_token.timeout)
            self.assertEqual(self.otp_token.failure_count, 0)
            self.assertIsNone(self.otp_token.expiration)

    @override_settings(FLEX_USER_OTP_TTL=timedelta(minutes=15))
    def test_generate_password_check_password_invalid_password(self):
        from freezegun import freeze_time
        from django.utils import timezone
        from datetime import timedelta

        with freeze_time():
            self.otp_token.generate_password()

            self.assertFalse(self.otp_token.check_password('invalidPassword'))
            self.assertFalse(self.otp_token.verified)
            self.assertEqual(self.otp_token.timeout, timezone.now() + timedelta(seconds=1))
            self.assertEqual(self.otp_token.failure_count, 1)
            self.assertEqual(self.otp_token.expiration, timezone.now() + timedelta(minutes=15))

    def test_check_password_undefined(self):
        self.assertRaises(TypeError, self.otp_token.check_password)
        self.assertFalse(self.otp_token.verified)
        self.assertIsNone(self.otp_token.timeout)
        self.assertEqual(self.otp_token.failure_count, 0)
        self.assertIsNone(self.otp_token.expiration)

    def test_check_password_none(self):
        from freezegun import freeze_time
        from django.utils import timezone
        from datetime import timedelta

        with freeze_time():
            self.assertFalse(self.otp_token.check_password(None))
            self.assertFalse(self.otp_token.verified)
            self.assertEqual(self.otp_token.timeout, timezone.now() + timedelta(seconds=1))
            self.assertEqual(self.otp_token.failure_count, 1)
            self.assertIsNone(self.otp_token.expiration)

    def test_check_password_empty_string(self):
        from freezegun import freeze_time
        from django.utils import timezone
        from datetime import timedelta

        with freeze_time():
            self.assertFalse(self.otp_token.check_password(''))
            self.assertFalse(self.otp_token.verified)
            self.assertEqual(self.otp_token.timeout, timezone.now() + timedelta(seconds=1))
            self.assertEqual(self.otp_token.failure_count, 1)
            self.assertIsNone(self.otp_token.expiration)

    def test_check_password_valid_password(self):
        from freezegun import freeze_time
        from django.utils import timezone
        from datetime import timedelta

        with freeze_time():
            self.assertFalse(self.otp_token.check_password(self.otp_token.password))
            self.assertFalse(self.otp_token.verified)
            self.assertEqual(self.otp_token.timeout, timezone.now() + timedelta(seconds=1))
            self.assertEqual(self.otp_token.failure_count, 1)
            self.assertIsNone(self.otp_token.expiration)

    def test_check_password_invalid_password(self):
        from freezegun import freeze_time
        from django.utils import timezone
        from datetime import timedelta

        with freeze_time():
            self.assertFalse(self.otp_token.check_password('invalidPassword'))
            self.assertFalse(self.otp_token.verified)
            self.assertEqual(self.otp_token.timeout, timezone.now() + timedelta(seconds=1))
            self.assertEqual(self.otp_token.failure_count, 1)
            self.assertIsNone(self.otp_token.expiration)

    def test_check_password_throttling(self):
        from django_flex_user.models.otp import TimeoutError
        from freezegun import freeze_time

        self.otp_token.generate_password()

        with freeze_time() as frozen_datetime:
            for i in range(0, 10):
                # Try to verify an invalid password. The method should return false and set the timeout to 2^i seconds
                success = self.otp_token.check_password('invalidPassword')
                self.assertFalse(success)

                # Here we simulate the timeout period. For each second of the timeout period we attempt to verify again.
                # The verification method should raise an exception each time.
                for j in range(0, 2 ** i):
                    # Try to verify again, the method should raise TimeoutError exception
                    self.assertRaises(TimeoutError, self.otp_token.check_password, 'invalidPassword')
                    # The verify method should raise TimeoutError even if we submit the correct password
                    self.assertRaises(TimeoutError, self.otp_token.check_password, self.otp_token.password)
                    # Advance time by 1 second
                    frozen_datetime.tick()

    @override_settings(FLEX_USER_OTP_TTL=timedelta(minutes=15))
    def test_expiration(self):
        from freezegun import freeze_time
        from datetime import timedelta
        from django.utils import timezone

        with freeze_time() as frozen_datetime:
            self.otp_token.generate_password()

            # Advance time to exactly the expiration time
            frozen_datetime.tick(timedelta(minutes=15))

            self.assertFalse(self.otp_token.check_password(self.otp_token.password))
            self.assertFalse(self.otp_token.verified)
            self.assertEqual(self.otp_token.timeout, timezone.now() + timedelta(seconds=1))
            self.assertEqual(self.otp_token.failure_count, 1)
            self.assertEqual(self.otp_token.expiration, timezone.now())

            # Advance time past the expiration
            frozen_datetime.tick(timedelta(minutes=15))

            self.assertFalse(self.otp_token.check_password(self.otp_token.password))
            self.assertFalse(self.otp_token.verified)
            self.assertEqual(self.otp_token.timeout, timezone.now() + timedelta(seconds=2))
            self.assertEqual(self.otp_token.failure_count, 2)
            self.assertEqual(self.otp_token.expiration, timezone.now() - timedelta(minutes=15))

    def test_generate_password_update_email_check_password(self):
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

            # Ensure the generated password fails
            self.otp_token.refresh_from_db()
            self.assertFalse(self.otp_token.check_password(password))
            self.assertFalse(self.otp_token.verified)
            self.assertEqual(self.otp_token.timeout, timezone.now() + timedelta(seconds=1))
            self.assertEqual(self.otp_token.failure_count, 1)
            self.assertIsNone(self.otp_token.expiration)
