from .test_email_token import TestEmailToken


class TestPhoneToken(TestEmailToken):
    """
    This class is designed to test django_flex_user.models.PhoneToken
    """

    def setUp(self):
        from django_flex_user.models.user import FlexUser
        from django_flex_user.models.otp import PhoneToken

        user = FlexUser.objects.create_user(phone='+12025551234')
        self.otp_token = PhoneToken.objects.get(user=user)

    def test_generate_password_update_email_check_password(self):
        pass

    def test_generate_password_update_phone_check_password(self):
        from freezegun import freeze_time
        from django.utils import timezone
        from datetime import timedelta

        with freeze_time():
            self.otp_token.generate_password()
            password = self.otp_token.password

            # Change the user's phone number to a phony one after generating password
            self.otp_token.user.phone = '+12024561111'
            self.otp_token.user.full_clean()
            self.otp_token.user.save()

            # Ensure the generated password fails
            self.otp_token.refresh_from_db()
            self.assertFalse(self.otp_token.check_password(password))
            self.assertFalse(self.otp_token.verified)
            self.assertEqual(self.otp_token.timeout, timezone.now() + timedelta(seconds=1))
            self.assertEqual(self.otp_token.failure_count, 1)
            self.assertIsNone(self.otp_token.expiration)
