from .test_endpoint_otpdevices_email_id import TestEmailTokenUpdate


class TestPhoneTokenUpdate(TestEmailTokenUpdate):
    """
    This class is designed to test django_flex_user.views.PhoneToken
    """

    def setUp(self):
        from django_flex_user.models import FlexUser
        from django_flex_user.models import PhoneToken

        user = FlexUser.objects.create_user(phone='+12025551234')
        self.otp_token = PhoneToken.objects.get(user=user)
        self._REST_ENDPOINT_PATH = TestEmailTokenUpdate._REST_ENDPOINT_PATH.format(type='phone', id=self.otp_token.id)
