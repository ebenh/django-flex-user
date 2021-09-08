from django.test import TestCase


class TestEmailDevice(TestCase):
    def test_create_user_with_username(self):
        from django_flex_user.models.flex_user import FlexUser
        from django_flex_user.models.otp import EmailDevice, PhoneDevice

        user = FlexUser.objects.create_user(username='validUsername')

        self.assertRaises(EmailDevice.DoesNotExist, EmailDevice.objects.get, user_id=user.id)
        self.assertRaises(PhoneDevice.DoesNotExist, PhoneDevice.objects.get, user_id=user.id)

    def test_create_user_with_email(self):
        from django_flex_user.models.flex_user import FlexUser
        from django_flex_user.models.otp import EmailDevice, PhoneDevice

        user = FlexUser.objects.create_user(email='validEmail@example.com')

        self.assertRaises(PhoneDevice.DoesNotExist, PhoneDevice.objects.get, user_id=user.id)
        email_device = EmailDevice.objects.get(user_id=user.id)
        self.assertEqual(email_device.email, user.email)
        self.assertFalse(email_device.confirmed)
        self.assertIsNone(email_device.challenge)

    def test_add_email(self):
        from django_flex_user.models.flex_user import FlexUser
        from django_flex_user.models.otp import EmailDevice, PhoneDevice

        user = FlexUser.objects.create_user(username='validUsername')
        user.email = 'validEmail@example.com'
        user.save()

        self.assertRaises(PhoneDevice.DoesNotExist, PhoneDevice.objects.get, user_id=user.id)
        email_device = EmailDevice.objects.get(user_id=user.id)
        self.assertEqual(email_device.email, user.email)
        self.assertFalse(email_device.confirmed)
        self.assertIsNone(email_device.challenge)

    def test_remove_email(self):
        from django_flex_user.models.flex_user import FlexUser
        from django_flex_user.models.otp import EmailDevice

        user = FlexUser.objects.create_user(username='validUsername', email='validEmail@example.com')
        user.email = None
        user.save()

        self.assertRaises(EmailDevice.DoesNotExist, EmailDevice.objects.get, user_id=user.id)

    def test_update_email(self):
        from django_flex_user.models.flex_user import FlexUser
        from django_flex_user.models.otp import EmailDevice

        user = FlexUser.objects.create_user(username='validUsername', email='validEmail@example.com')
        user.email = 'validEmail2@example.com'
        user.save()

        email_device = EmailDevice.objects.get(user_id=user.id)
        self.assertEqual(email_device.email, user.email)
        self.assertFalse(email_device.confirmed)
        self.assertIsNone(email_device.challenge)

    def test_generate_challenge(self):
        from django_flex_user.models.flex_user import FlexUser
        from django_flex_user.models.otp import EmailDevice

        user = FlexUser.objects.create_user(email='validEmail@example.com')
        email_device = EmailDevice.objects.get(user_id=user.id)
        email_device.generate_challenge()

        self.assertIsNotNone(email_device.challenge)
        self.assertNotEqual(email_device.challenge, '')
        # note eben: Because escape characters are inserted into the challenge string, the challenge string's length may
        # be greater than or equal to its configured length
        self.assertGreaterEqual(len(email_device.challenge), email_device.challenge_length)

    def test_verify_challenge_none(self):
        from django_flex_user.models.flex_user import FlexUser
        from django_flex_user.models.otp import EmailDevice

        user = FlexUser.objects.create_user(email='validEmail@example.com')
        email_device = EmailDevice.objects.get(user_id=user.id)
        email_device.generate_challenge()

        self.assertFalse(email_device.verify_challenge(None))

    def test_verify_challenge_empty_string(self):
        from django_flex_user.models.flex_user import FlexUser
        from django_flex_user.models.otp import EmailDevice

        user = FlexUser.objects.create_user(email='validEmail@example.com')
        email_device = EmailDevice.objects.get(user_id=user.id)
        email_device.generate_challenge()

        self.assertFalse(email_device.verify_challenge(''))

    def test_verify_challenge_invalid_challenge(self):
        from django_flex_user.models.flex_user import FlexUser
        from django_flex_user.models.otp import EmailDevice

        user = FlexUser.objects.create_user(email='validEmail@example.com')
        email_device = EmailDevice.objects.get(user_id=user.id)
        email_device.generate_challenge()

        self.assertFalse(email_device.verify_challenge('INVALID_CHALLENGE'))

    def test_verify_challenge_valid_challenge(self):
        from django_flex_user.models.flex_user import FlexUser
        from django_flex_user.models.otp import EmailDevice

        user = FlexUser.objects.create_user(email='validEmail@example.com')
        email_device = EmailDevice.objects.get(user_id=user.id)
        email_device.generate_challenge()

        self.assertTrue(email_device.verify_challenge(email_device.challenge))



