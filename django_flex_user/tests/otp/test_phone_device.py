from django.test import TestCase


class TestPhoneDevice(TestCase):
    def test_no_phone(self):
        from django_flex_user.models.otp import PhoneDevice
        from django.core.exceptions import ValidationError

        phone_device = PhoneDevice()
        self.assertRaises(ValidationError, phone_device.full_clean)

    def test_valid_phone(self):
        from django_flex_user.models.otp import PhoneDevice

        phone_device = PhoneDevice(phone='+12025551234')
        phone_device.full_clean()

    def test_invalid_phone(self):
        from django_flex_user.models.otp import PhoneDevice
        from django.core.exceptions import ValidationError

        phone_device = PhoneDevice(phone='invalidPhoneNumber')
        self.assertRaises(ValidationError, phone_device.full_clean)

    def test_generate_challenge(self):
        from django_flex_user.models.otp import PhoneDevice

        phone_device = PhoneDevice(phone='+12025551234')
        phone_device.generate_challenge()
        phone_device.full_clean()
        phone_device.save()

        self.assertIsNotNone(phone_device.challenge)
        self.assertNotEqual(phone_device.challenge, '')
        self.assertEqual(len(phone_device.challenge), phone_device.challenge_length)

    def test_verify_challenge(self):
        from django_flex_user.models.otp import PhoneDevice

        phone_device = PhoneDevice(phone='+12025551234')
        phone_device.generate_challenge()
        phone_device.full_clean()
        phone_device.save()

        self.assertFalse(phone_device.verify_challenge(None))
        self.assertFalse(phone_device.verify_challenge(''))
        self.assertFalse(phone_device.verify_challenge('INVALID_CHALLENGE'))
        self.assertTrue(phone_device.verify_challenge(phone_device.challenge))