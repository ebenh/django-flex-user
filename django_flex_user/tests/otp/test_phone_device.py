from .test_email_device import TestEmailDevice


class TestPhoneDevice(TestEmailDevice):
    def setUp(self):
        from django_flex_user.models import FlexUser
        from django_flex_user.models import PhoneDevice

        user = FlexUser.objects.create_user(username='validUsername',
                                            email='validEmail@example.com',
                                            phone='+12025551234')
        self.otp_device = PhoneDevice.objects.get(user=user)
