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

    def test_generate_challenge(self):
        from django_flex_user.models.flex_user import FlexUser
        from django_flex_user.models.otp import PhoneDevice

        user = FlexUser.objects.create_user(phone='+12025551234')
        phone_device = PhoneDevice.objects.get(user_id=user.id)
        phone_device.generate_challenge()

        self.assertIsNotNone(phone_device.challenge)
        self.assertNotEqual(phone_device.challenge, '')
        self.assertEqual(len(phone_device.challenge), phone_device.challenge_length)

    def test_verify_challenge_none(self):
        from django_flex_user.models.flex_user import FlexUser
        from django_flex_user.models.otp import PhoneDevice

        user = FlexUser.objects.create_user(phone='+12025551234')
        phone_device = PhoneDevice.objects.get(user_id=user.id)
        phone_device.generate_challenge()

        self.assertFalse(phone_device.verify_challenge(None))

    def test_verify_challenge_empty_string(self):
        from django_flex_user.models.flex_user import FlexUser
        from django_flex_user.models.otp import PhoneDevice

        user = FlexUser.objects.create_user(phone='+12025551234')
        phone_device = PhoneDevice.objects.get(user_id=user.id)
        phone_device.generate_challenge()

        self.assertFalse(phone_device.verify_challenge(''))

    def test_verify_challenge_invalid_challenge(self):
        from django_flex_user.models.flex_user import FlexUser
        from django_flex_user.models.otp import PhoneDevice

        user = FlexUser.objects.create_user(phone='+12025551234')
        phone_device = PhoneDevice.objects.get(user_id=user.id)
        phone_device.generate_challenge()

        self.assertFalse(phone_device.verify_challenge('INVALID_CHALLENGE'))

    def test_verify_challenge_valid_challenge(self):
        from django_flex_user.models.flex_user import FlexUser
        from django_flex_user.models.otp import PhoneDevice

        user = FlexUser.objects.create_user(phone='+12025551234')
        phone_device = PhoneDevice.objects.get(user_id=user.id)
        phone_device.generate_challenge()

        self.assertTrue(phone_device.verify_challenge(phone_device.challenge))
