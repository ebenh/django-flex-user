from .test_endpoint_otpdevices_email_id import TestEmailDeviceUpdate


class TestPhoneDeviceUpdate(TestEmailDeviceUpdate):
    """
    This class is designed to test django_flex_user.views.OTPPhoneDevice
    """

    def setUp(self):
        from django_flex_user.models import FlexUser
        from django_flex_user.models import PhoneDevice

        user = FlexUser.objects.create_user(username='validUsername',
                                            email='validEmail@example.com',
                                            phone='+12025551234')
        self.otp_device = PhoneDevice.objects.get(user=user)

        self._REST_ENDPOINT_PATH = TestEmailDeviceUpdate._REST_ENDPOINT_PATH.format(type='phone', id=self.otp_device.id)
