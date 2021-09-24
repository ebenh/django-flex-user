from .test_email_device import TestEmailDevice


class TestPhoneDevice(TestEmailDevice):
    """
    This class is designed to test django_flex_user.models.PhoneDevice
    """

    def setUp(self):
        from django_flex_user.models import FlexUser
        from django_flex_user.models import PhoneToken

        user = FlexUser.objects.create_user(phone='+12025551234')
        self.otp_device = PhoneToken.objects.get(user=user)
