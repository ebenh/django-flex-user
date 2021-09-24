from django.test import TestCase


class TestEmailToken(TestCase):
    """
    This class is designed to test django_flex_user.models.EmailToken
    """

    def setUp(self):
        from django_flex_user.models import FlexUser
        from django_flex_user.models import EmailToken

        user = FlexUser.objects.create_user(email='validEmail@example.com')
        self.otp_device = EmailToken.objects.get(user=user)

    def test_generate_password(self):
        self.otp_device.generate_password()

        self.assertFalse(self.otp_device.confirmed)
        self.assertIsNotNone(self.otp_device.password)
        self.assertNotEqual(self.otp_device.password, '')
        # note eben: Because escape characters are inserted into the password string, the password string's length may
        # be greater than or equal to its configured length
        self.assertGreaterEqual(len(self.otp_device.password), self.otp_device.password_length)
        self.assertIsNone(self.otp_device.verification_timeout)
        self.assertEqual(self.otp_device.verification_failure_count, 0)

    def test_generate_password_verify_password_none(self):
        from freezegun import freeze_time
        from django.utils import timezone
        from datetime import timedelta

        self.otp_device.generate_password()

        with freeze_time():
            self.assertFalse(self.otp_device.verify_password(None))
            self.assertFalse(self.otp_device.confirmed)
            self.assertEqual(self.otp_device.verification_timeout, timezone.now() + timedelta(seconds=1))
            self.assertEqual(self.otp_device.verification_failure_count, 1)

    def test_generate_password_verify_password_empty_string(self):
        from freezegun import freeze_time
        from django.utils import timezone
        from datetime import timedelta

        self.otp_device.generate_password()

        with freeze_time():
            self.assertFalse(self.otp_device.verify_password(''))
            self.assertFalse(self.otp_device.confirmed)
            self.assertEqual(self.otp_device.verification_timeout, timezone.now() + timedelta(seconds=1))
            self.assertEqual(self.otp_device.verification_failure_count, 1)

    def test_generate_password_verify_password_valid_password(self):
        self.otp_device.generate_password()

        self.assertTrue(self.otp_device.verify_password(self.otp_device.password))
        self.assertTrue(self.otp_device.confirmed)
        self.assertIsNone(self.otp_device.verification_timeout)
        self.assertEqual(self.otp_device.verification_failure_count, 0)

    def test_generate_password_verify_password_invalid_password(self):
        from freezegun import freeze_time
        from django.utils import timezone
        from datetime import timedelta

        self.otp_device.generate_password()

        with freeze_time():
            self.assertFalse(self.otp_device.verify_password('invalidPassword'))
            self.assertFalse(self.otp_device.confirmed)
            self.assertEqual(self.otp_device.verification_timeout, timezone.now() + timedelta(seconds=1))
            self.assertEqual(self.otp_device.verification_failure_count, 1)

    def test_verify_password_none(self):
        from freezegun import freeze_time
        from django.utils import timezone
        from datetime import timedelta

        with freeze_time():
            self.assertFalse(self.otp_device.verify_password(None))
            self.assertFalse(self.otp_device.confirmed)
            self.assertEqual(self.otp_device.verification_timeout, timezone.now() + timedelta(seconds=1))
            self.assertEqual(self.otp_device.verification_failure_count, 1)

    def test_verify_password_empty_string(self):
        from freezegun import freeze_time
        from django.utils import timezone
        from datetime import timedelta

        with freeze_time():
            self.assertFalse(self.otp_device.verify_password(''))
            self.assertFalse(self.otp_device.confirmed)
            self.assertEqual(self.otp_device.verification_timeout, timezone.now() + timedelta(seconds=1))
            self.assertEqual(self.otp_device.verification_failure_count, 1)

    def test_verify_password_valid_password(self):
        from freezegun import freeze_time
        from django.utils import timezone
        from datetime import timedelta

        with freeze_time():
            self.assertFalse(self.otp_device.verify_password(self.otp_device.password))
            self.assertFalse(self.otp_device.confirmed)
            self.assertEqual(self.otp_device.verification_timeout, timezone.now() + timedelta(seconds=1))
            self.assertEqual(self.otp_device.verification_failure_count, 1)

    def test_verify_password_invalid_password(self):
        from freezegun import freeze_time
        from django.utils import timezone
        from datetime import timedelta

        with freeze_time():
            self.assertFalse(self.otp_device.verify_password('invalidPassword'))
            self.assertFalse(self.otp_device.confirmed)
            self.assertEqual(self.otp_device.verification_timeout, timezone.now() + timedelta(seconds=1))
            self.assertEqual(self.otp_device.verification_failure_count, 1)

    def test_verify_password_throttling(self):
        from django_flex_user.models.otp import TimeoutError
        from freezegun import freeze_time

        self.otp_device.generate_password()

        with freeze_time() as frozen_datetime:
            for i in range(0, 10):
                # Try to verify an invalid password. The method should return false and set the timeout to 2^i seconds
                success = self.otp_device.verify_password('invalidPassword')
                self.assertFalse(success)

                # Here we simulate the timeout period. For each second of the timeout period we attempt to verify again.
                # The verification method should raise an exception each time.
                for j in range(0, 2 ** i):
                    # Try to verify again, the method should raise TimeoutError exception
                    self.assertRaises(TimeoutError, self.otp_device.verify_password, 'invalidPassword')
                    # The verify method should raise TimeoutError even if we submit the correct password
                    self.assertRaises(TimeoutError, self.otp_device.verify_password, self.otp_device.password)
                    # Advance time by 1 second
                    frozen_datetime.tick()
