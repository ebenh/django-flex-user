from django.test import TestCase


class TestEmailDevice(TestCase):
    def test_no_email(self):
        from django_flex_user.models.otp import EmailDevice
        from django.core.exceptions import ValidationError

        email_device = EmailDevice()
        self.assertRaises(ValidationError, email_device.full_clean)

    def test_valid_email(self):
        from django_flex_user.models.otp import EmailDevice

        email_device = EmailDevice(email='validEmail@example.com')
        email_device.full_clean()

    def test_invalid_email(self):
        from django_flex_user.models.otp import EmailDevice
        from django.core.exceptions import ValidationError

        email_device = EmailDevice(email='invalidEmail')
        self.assertRaises(ValidationError, email_device.full_clean)

    def test_generate_challenge(self):
        from django_flex_user.models.otp import EmailDevice

        email_device = EmailDevice(email='validEmail@example.com')
        email_device.generate_challenge()
        email_device.full_clean()
        email_device.save()

        self.assertIsNotNone(email_device.challenge)
        self.assertNotEqual(email_device.challenge, '')
        self.assertEqual(len(email_device.challenge), email_device.challenge_length)

    def test_verify_challenge(self):
        from django_flex_user.models.otp import EmailDevice

        email_device = EmailDevice(email='validEmail@example.com')
        email_device.generate_challenge()
        email_device.full_clean()
        email_device.save()

        self.assertFalse(email_device.verify_challenge(None))
        self.assertFalse(email_device.verify_challenge(''))
        self.assertFalse(email_device.verify_challenge('INVALID_CHALLENGE'))
        self.assertTrue(email_device.verify_challenge(email_device.challenge))