from django.test import TestCase


class TestPhoneDevice(TestCase):
    def test_create_user_with_username(self):
        from django_flex_user.models.flex_user import FlexUser
        from django_flex_user.models.otp import EmailDevice, PhoneDevice

        user = FlexUser.objects.create_user(username='validUsername')

        self.assertRaises(EmailDevice.DoesNotExist, EmailDevice.objects.get, user_id=user.id)
        self.assertRaises(PhoneDevice.DoesNotExist, PhoneDevice.objects.get, user_id=user.id)

    def test_create_user_with_phone(self):
        from django_flex_user.models.flex_user import FlexUser
        from django_flex_user.models.otp import EmailDevice, PhoneDevice

        user = FlexUser.objects.create_user(phone='+12025551234')

        self.assertRaises(EmailDevice.DoesNotExist, EmailDevice.objects.get, user_id=user.id)
        phone_device = PhoneDevice.objects.get(user_id=user.id)
        self.assertEqual(phone_device.phone, user.phone)
        self.assertFalse(phone_device.confirmed)
        self.assertIsNone(phone_device.challenge)
        self.assertIsNone(phone_device.verification_timeout)
        self.assertEqual(phone_device.verification_failure_count, 0)

    def test_add_phone(self):
        from django_flex_user.models.flex_user import FlexUser
        from django_flex_user.models.otp import EmailDevice, PhoneDevice

        user = FlexUser.objects.create_user(username='validUsername')
        user.phone = '+12025551234'
        user.save()

        self.assertRaises(EmailDevice.DoesNotExist, EmailDevice.objects.get, user_id=user.id)
        phone_device = PhoneDevice.objects.get(user_id=user.id)
        self.assertEqual(phone_device.phone, user.phone)
        self.assertFalse(phone_device.confirmed)
        self.assertIsNone(phone_device.challenge)
        self.assertIsNone(phone_device.verification_timeout)
        self.assertEqual(phone_device.verification_failure_count, 0)

    def test_remove_phone(self):
        from django_flex_user.models.flex_user import FlexUser
        from django_flex_user.models.otp import PhoneDevice

        user = FlexUser.objects.create_user(username='validUsername', phone='+12025551234')
        user.phone = None
        user.save()

        self.assertRaises(PhoneDevice.DoesNotExist, PhoneDevice.objects.get, user_id=user.id)

    def test_update_phone(self):
        from django_flex_user.models.flex_user import FlexUser
        from django_flex_user.models.otp import PhoneDevice

        user = FlexUser.objects.create_user(username='validUsername', phone='+12025551234')
        user.email = '+12025556789'
        user.save()

        phone_device = PhoneDevice.objects.get(user_id=user.id)
        self.assertEqual(phone_device.phone, user.phone)
        self.assertFalse(phone_device.confirmed)
        self.assertIsNone(phone_device.challenge)
        self.assertIsNone(phone_device.verification_timeout)
        self.assertEqual(phone_device.verification_failure_count, 0)

    def test_generate_challenge(self):
        from django_flex_user.models.flex_user import FlexUser
        from django_flex_user.models.otp import PhoneDevice

        user = FlexUser.objects.create_user(phone='+12025551234')
        phone_device = PhoneDevice.objects.get(user_id=user.id)
        phone_device.generate_challenge()

        self.assertFalse(phone_device.confirmed)
        self.assertIsNotNone(phone_device.challenge)
        self.assertNotEqual(phone_device.challenge, '')
        self.assertEqual(len(phone_device.challenge), phone_device.challenge_length)
        self.assertIsNone(phone_device.verification_timeout)
        self.assertEqual(phone_device.verification_failure_count, 0)

    def test_generate_challenge_verify_challenge_none(self):
        from django_flex_user.models.flex_user import FlexUser
        from django_flex_user.models.otp import PhoneDevice
        from freezegun import freeze_time
        from django.utils import timezone
        from datetime import timedelta

        user = FlexUser.objects.create_user(phone='+12025551234')
        phone_device = PhoneDevice.objects.get(user_id=user.id)
        phone_device.generate_challenge()

        with freeze_time():
            self.assertFalse(phone_device.verify_challenge(None))
            self.assertFalse(phone_device.confirmed)
            self.assertEqual(phone_device.verification_timeout, timezone.now() + timedelta(seconds=1))
            self.assertEqual(phone_device.verification_failure_count, 1)

    def test_generate_challenge_verify_challenge_empty_string(self):
        from django_flex_user.models.flex_user import FlexUser
        from django_flex_user.models.otp import PhoneDevice
        from freezegun import freeze_time
        from django.utils import timezone
        from datetime import timedelta

        user = FlexUser.objects.create_user(phone='+12025551234')
        phone_device = PhoneDevice.objects.get(user_id=user.id)
        phone_device.generate_challenge()

        with freeze_time():
            self.assertFalse(phone_device.verify_challenge(''))
            self.assertFalse(phone_device.confirmed)
            self.assertEqual(phone_device.verification_timeout, timezone.now() + timedelta(seconds=1))
            self.assertEqual(phone_device.verification_failure_count, 1)

    def test_generate_challenge_verify_challenge_invalid_challenge(self):
        from django_flex_user.models.flex_user import FlexUser
        from django_flex_user.models.otp import PhoneDevice
        from freezegun import freeze_time
        from django.utils import timezone
        from datetime import timedelta

        user = FlexUser.objects.create_user(phone='+12025551234')
        phone_device = PhoneDevice.objects.get(user_id=user.id)
        phone_device.generate_challenge()

        with freeze_time():
            self.assertFalse(phone_device.verify_challenge('INVALID_CHALLENGE'))
            self.assertFalse(phone_device.confirmed)
            self.assertEqual(phone_device.verification_timeout, timezone.now() + timedelta(seconds=1))
            self.assertEqual(phone_device.verification_failure_count, 1)

    def test_generate_challenge_verify_challenge_valid_challenge(self):
        from django_flex_user.models.flex_user import FlexUser
        from django_flex_user.models.otp import PhoneDevice

        user = FlexUser.objects.create_user(phone='+12025551234')
        phone_device = PhoneDevice.objects.get(user_id=user.id)
        phone_device.generate_challenge()

        self.assertTrue(phone_device.verify_challenge(phone_device.challenge))
        self.assertTrue(phone_device.confirmed)
        self.assertIsNone(phone_device.verification_timeout)
        self.assertEqual(phone_device.verification_failure_count, 0)

    def test_throttle(self):
        from django_flex_user.models.flex_user import FlexUser
        from django_flex_user.models.otp import PhoneDevice, VerificationTimeout
        from freezegun import freeze_time

        user = FlexUser.objects.create_user(phone='+12025551234')
        phone_device = PhoneDevice.objects.get(user_id=user.id)
        phone_device.generate_challenge()

        with freeze_time() as frozen_datetime:
            for i in range(0, 10):
                # Try to verify an invalid challenge. The method should return false and set the timeout to 2^i seconds
                success = phone_device.verify_challenge('INVALID_CHALLENGE')
                self.assertFalse(success)

                # Here we simulate the timeout period. For each second of the timeout period we attempt to verify again.
                # The verification method should raise an exception each time.
                for j in range(0, 2 ** i):
                    # Try to verify again, the method should raise VerificationTimeout exception
                    self.assertRaises(VerificationTimeout, phone_device.verify_challenge, 'INVALID_CHALLENGE')
                    # The verify method should raise VerificationTimeout even if we submit the correct challenge
                    self.assertRaises(VerificationTimeout, phone_device.verify_challenge, phone_device.challenge)
                    # Advance time by 1 second
                    frozen_datetime.tick()
