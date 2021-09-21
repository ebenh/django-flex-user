from django.test import TestCase


class TestEmailDevice(TestCase):
    def setUp(self):
        from django_flex_user.models import FlexUser
        from django_flex_user.models import EmailDevice

        user = FlexUser.objects.create_user(username='validUsername',
                                            email='validEmail@example.com',
                                            phone='+12025551234')
        self.otp_device = EmailDevice.objects.get(user=user)

    def test_generate_challenge(self):
        self.otp_device.generate_challenge()

        self.assertFalse(self.otp_device.confirmed)
        self.assertIsNotNone(self.otp_device.challenge)
        self.assertNotEqual(self.otp_device.challenge, '')
        # note eben: Because escape characters are inserted into the challenge string, the challenge string's length may
        # be greater than or equal to its configured length
        self.assertGreaterEqual(len(self.otp_device.challenge), self.otp_device.challenge_length)
        self.assertIsNone(self.otp_device.verification_timeout)
        self.assertEqual(self.otp_device.verification_failure_count, 0)

    def test_generate_challenge_verify_challenge_none(self):
        from freezegun import freeze_time
        from django.utils import timezone
        from datetime import timedelta

        self.otp_device.generate_challenge()

        with freeze_time():
            self.assertFalse(self.otp_device.verify_challenge(None))
            self.assertFalse(self.otp_device.confirmed)
            self.assertEqual(self.otp_device.verification_timeout, timezone.now() + timedelta(seconds=1))
            self.assertEqual(self.otp_device.verification_failure_count, 1)

    def test_generate_challenge_verify_challenge_empty_string(self):
        from freezegun import freeze_time
        from django.utils import timezone
        from datetime import timedelta

        self.otp_device.generate_challenge()

        with freeze_time():
            self.assertFalse(self.otp_device.verify_challenge(''))
            self.assertFalse(self.otp_device.confirmed)
            self.assertEqual(self.otp_device.verification_timeout, timezone.now() + timedelta(seconds=1))
            self.assertEqual(self.otp_device.verification_failure_count, 1)

    def test_generate_challenge_verify_challenge_valid_challenge(self):
        self.otp_device.generate_challenge()

        self.assertTrue(self.otp_device.verify_challenge(self.otp_device.challenge))
        self.assertTrue(self.otp_device.confirmed)
        self.assertIsNone(self.otp_device.verification_timeout)
        self.assertEqual(self.otp_device.verification_failure_count, 0)

    def test_generate_challenge_verify_challenge_invalid_challenge(self):
        from freezegun import freeze_time
        from django.utils import timezone
        from datetime import timedelta

        self.otp_device.generate_challenge()

        with freeze_time():
            self.assertFalse(self.otp_device.verify_challenge('INVALID_CHALLENGE'))
            self.assertFalse(self.otp_device.confirmed)
            self.assertEqual(self.otp_device.verification_timeout, timezone.now() + timedelta(seconds=1))
            self.assertEqual(self.otp_device.verification_failure_count, 1)

    def test_verify_challenge_none(self):
        from freezegun import freeze_time
        from django.utils import timezone
        from datetime import timedelta

        with freeze_time():
            self.assertFalse(self.otp_device.verify_challenge(None))
            self.assertFalse(self.otp_device.confirmed)
            self.assertEqual(self.otp_device.verification_timeout, timezone.now() + timedelta(seconds=1))
            self.assertEqual(self.otp_device.verification_failure_count, 1)

    def test_verify_challenge_empty_string(self):
        from freezegun import freeze_time
        from django.utils import timezone
        from datetime import timedelta

        with freeze_time():
            self.assertFalse(self.otp_device.verify_challenge(''))
            self.assertFalse(self.otp_device.confirmed)
            self.assertEqual(self.otp_device.verification_timeout, timezone.now() + timedelta(seconds=1))
            self.assertEqual(self.otp_device.verification_failure_count, 1)

    def test_verify_challenge_valid_challenge(self):
        from freezegun import freeze_time
        from django.utils import timezone
        from datetime import timedelta

        with freeze_time():
            self.assertFalse(self.otp_device.verify_challenge(self.otp_device.challenge))
            self.assertFalse(self.otp_device.confirmed)
            self.assertEqual(self.otp_device.verification_timeout, timezone.now() + timedelta(seconds=1))
            self.assertEqual(self.otp_device.verification_failure_count, 1)

    def test_verify_challenge_invalid_challenge(self):
        from freezegun import freeze_time
        from django.utils import timezone
        from datetime import timedelta

        with freeze_time():
            self.assertFalse(self.otp_device.verify_challenge('INVALID_CHALLENGE'))
            self.assertFalse(self.otp_device.confirmed)
            self.assertEqual(self.otp_device.verification_timeout, timezone.now() + timedelta(seconds=1))
            self.assertEqual(self.otp_device.verification_failure_count, 1)

    def test_verify_challenge_throttling(self):
        from django_flex_user.models.otp import VerificationTimeout
        from freezegun import freeze_time

        self.otp_device.generate_challenge()

        with freeze_time() as frozen_datetime:
            for i in range(0, 10):
                # Try to verify an invalid challenge. The method should return false and set the timeout to 2^i seconds
                success = self.otp_device.verify_challenge('INVALID_CHALLENGE')
                self.assertFalse(success)

                # Here we simulate the timeout period. For each second of the timeout period we attempt to verify again.
                # The verification method should raise an exception each time.
                for j in range(0, 2 ** i):
                    # Try to verify again, the method should raise VerificationTimeout exception
                    self.assertRaises(VerificationTimeout, self.otp_device.verify_challenge, 'INVALID_CHALLENGE')
                    # The verify method should raise VerificationTimeout even if we submit the correct challenge
                    self.assertRaises(VerificationTimeout, self.otp_device.verify_challenge, self.otp_device.challenge)
                    # Advance time by 1 second
                    frozen_datetime.tick()
