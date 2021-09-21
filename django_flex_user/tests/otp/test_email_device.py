from django.test import TestCase


class TestEmailDevice(TestCase):
    def test_generate_challenge(self):
        from django_flex_user.models.flex_user import FlexUser
        from django_flex_user.models.otp import EmailDevice

        user = FlexUser.objects.create_user(email='validEmail@example.com')
        email_device = EmailDevice.objects.get(user_id=user.id)
        email_device.generate_challenge()

        self.assertFalse(email_device.confirmed)
        self.assertIsNotNone(email_device.challenge)
        self.assertNotEqual(email_device.challenge, '')
        # note eben: Because escape characters are inserted into the challenge string, the challenge string's length may
        # be greater than or equal to its configured length
        self.assertGreaterEqual(len(email_device.challenge), email_device.challenge_length)
        self.assertIsNone(email_device.verification_timeout)
        self.assertEqual(email_device.verification_failure_count, 0)

    def test_generate_challenge_verify_challenge_none(self):
        from django_flex_user.models.flex_user import FlexUser
        from django_flex_user.models.otp import EmailDevice
        from freezegun import freeze_time
        from django.utils import timezone
        from datetime import timedelta

        user = FlexUser.objects.create_user(email='validEmail@example.com')
        email_device = EmailDevice.objects.get(user_id=user.id)
        email_device.generate_challenge()

        with freeze_time():
            self.assertFalse(email_device.verify_challenge(None))
            self.assertFalse(email_device.confirmed)
            self.assertEqual(email_device.verification_timeout, timezone.now() + timedelta(seconds=1))
            self.assertEqual(email_device.verification_failure_count, 1)

    def test_generate_challenge_verify_challenge_empty_string(self):
        from django_flex_user.models.flex_user import FlexUser
        from django_flex_user.models.otp import EmailDevice
        from freezegun import freeze_time
        from django.utils import timezone
        from datetime import timedelta

        user = FlexUser.objects.create_user(email='validEmail@example.com')
        email_device = EmailDevice.objects.get(user_id=user.id)
        email_device.generate_challenge()

        with freeze_time():
            self.assertFalse(email_device.verify_challenge(''))
            self.assertFalse(email_device.confirmed)
            self.assertEqual(email_device.verification_timeout, timezone.now() + timedelta(seconds=1))
            self.assertEqual(email_device.verification_failure_count, 1)

    def test_generate_challenge_verify_challenge_invalid_challenge(self):
        from django_flex_user.models.flex_user import FlexUser
        from django_flex_user.models.otp import EmailDevice
        from freezegun import freeze_time
        from django.utils import timezone
        from datetime import timedelta

        user = FlexUser.objects.create_user(email='validEmail@example.com')
        email_device = EmailDevice.objects.get(user_id=user.id)
        email_device.generate_challenge()

        with freeze_time():
            self.assertFalse(email_device.verify_challenge('INVALID_CHALLENGE'))
            self.assertFalse(email_device.confirmed)
            self.assertEqual(email_device.verification_timeout, timezone.now() + timedelta(seconds=1))
            self.assertEqual(email_device.verification_failure_count, 1)

    def test_generate_challenge_verify_challenge_valid_challenge(self):
        from django_flex_user.models.flex_user import FlexUser
        from django_flex_user.models.otp import EmailDevice

        user = FlexUser.objects.create_user(email='validEmail@example.com')
        email_device = EmailDevice.objects.get(user_id=user.id)
        email_device.generate_challenge()

        self.assertTrue(email_device.verify_challenge(email_device.challenge))
        self.assertTrue(email_device.confirmed)
        self.assertIsNone(email_device.verification_timeout)
        self.assertEqual(email_device.verification_failure_count, 0)

    def test_verify_challenge_none(self):
        from django_flex_user.models.flex_user import FlexUser
        from django_flex_user.models.otp import EmailDevice
        from freezegun import freeze_time
        from django.utils import timezone
        from datetime import timedelta

        user = FlexUser.objects.create_user(email='validEmail@example.com')
        email_device = EmailDevice.objects.get(user_id=user.id)

        with freeze_time():
            self.assertFalse(email_device.verify_challenge(None))
            self.assertFalse(email_device.confirmed)
            self.assertEqual(email_device.verification_timeout, timezone.now() + timedelta(seconds=1))
            self.assertEqual(email_device.verification_failure_count, 1)

    def test_verify_challenge_empty_string(self):
        from django_flex_user.models.flex_user import FlexUser
        from django_flex_user.models.otp import EmailDevice
        from freezegun import freeze_time
        from django.utils import timezone
        from datetime import timedelta

        user = FlexUser.objects.create_user(email='validEmail@example.com')
        email_device = EmailDevice.objects.get(user_id=user.id)

        with freeze_time():
            self.assertFalse(email_device.verify_challenge(''))
            self.assertFalse(email_device.confirmed)
            self.assertEqual(email_device.verification_timeout, timezone.now() + timedelta(seconds=1))
            self.assertEqual(email_device.verification_failure_count, 1)

    def test_verify_challenge_invalid_challenge(self):
        from django_flex_user.models.flex_user import FlexUser
        from django_flex_user.models.otp import EmailDevice
        from freezegun import freeze_time
        from django.utils import timezone
        from datetime import timedelta

        user = FlexUser.objects.create_user(email='validEmail@example.com')
        email_device = EmailDevice.objects.get(user_id=user.id)

        with freeze_time():
            self.assertFalse(email_device.verify_challenge('INVALID_CHALLENGE'))
            self.assertFalse(email_device.confirmed)
            self.assertEqual(email_device.verification_timeout, timezone.now() + timedelta(seconds=1))
            self.assertEqual(email_device.verification_failure_count, 1)

    def test_verify_challenge_valid_challenge(self):
        from django_flex_user.models.flex_user import FlexUser
        from django_flex_user.models.otp import EmailDevice
        from freezegun import freeze_time
        from django.utils import timezone
        from datetime import timedelta

        user = FlexUser.objects.create_user(email='validEmail@example.com')
        email_device = EmailDevice.objects.get(user_id=user.id)

        with freeze_time():
            self.assertFalse(email_device.verify_challenge(email_device.challenge))
            self.assertFalse(email_device.confirmed)
            self.assertEqual(email_device.verification_timeout, timezone.now() + timedelta(seconds=1))
            self.assertEqual(email_device.verification_failure_count, 1)

    def test_throttle(self):
        from django_flex_user.models.flex_user import FlexUser
        from django_flex_user.models.otp import EmailDevice, VerificationTimeout
        from freezegun import freeze_time

        user = FlexUser.objects.create_user(email='validEmail@example.com')
        email_device = EmailDevice.objects.get(user_id=user.id)
        email_device.generate_challenge()

        with freeze_time() as frozen_datetime:
            for i in range(0, 10):
                # Try to verify an invalid challenge. The method should return false and set the timeout to 2^i seconds
                success = email_device.verify_challenge('INVALID_CHALLENGE')
                self.assertFalse(success)

                # Here we simulate the timeout period. For each second of the timeout period we attempt to verify again.
                # The verification method should raise an exception each time.
                for j in range(0, 2 ** i):
                    # Try to verify again, the method should raise VerificationTimeout exception
                    self.assertRaises(VerificationTimeout, email_device.verify_challenge, 'INVALID_CHALLENGE')
                    # The verify method should raise VerificationTimeout even if we submit the correct challenge
                    self.assertRaises(VerificationTimeout, email_device.verify_challenge, email_device.challenge)
                    # Advance time by 1 second
                    frozen_datetime.tick()
