from .test_endpoint_otp_tokens_email_id import TestEmailTokenRetrieveUpdate

from rest_framework.test import APITestCase
from rest_framework import status


class TestPhoneTokenRetrieveUpdate(TestEmailTokenRetrieveUpdate):
    """
    This class is designed to test django_flex_user.views.PhoneToken
    """

    def setUp(self):
        from django_flex_user.models.user import FlexUser

        user = FlexUser.objects.create_user(phone='+12025551234')
        self.otp_token = user.phonetoken_set.first()
        self._REST_ENDPOINT_PATH = TestEmailTokenRetrieveUpdate._REST_ENDPOINT_PATH.format(type='phone',
                                                                                           id=self.otp_token.id)


class TestMethodPostGeneratePasswordUpdatePhoneCheckPassword(APITestCase):
    """
    This class is designed to test django_flex_user.views.PhoneToken
    """

    def test_method_post_generate_password_update_phone_check_password(self):
        from django_flex_user.models.user import FlexUser
        from freezegun import freeze_time
        from django.utils import timezone
        from datetime import timedelta

        user = FlexUser.objects.create_user(phone='+12025551234')
        phone_token = user.phonetoken_set.first()

        with freeze_time():
            phone_token.generate_password()
            password = phone_token.password

            # Change the user's phone number to a phony one after generating password
            phone_token.user.phone = '+12024561111'
            phone_token.user.full_clean()
            phone_token.user.save()

            response = self.client.post(f'/api/accounts/otp-tokens/phone/{phone_token.id}', data={'password': password})
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

            # Ensure the generated password fails
            phone_token.refresh_from_db()
            self.assertFalse(phone_token.verified)
            self.assertEqual(phone_token.timeout, timezone.now() + timedelta(seconds=1))
            self.assertEqual(phone_token.failure_count, 1)
            self.assertIsNone(phone_token.expiration)
