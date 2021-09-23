from django.test import TestCase


class TestPhoneDeviceSerializer(TestCase):
    """
    This class is designed to test django_flex_user.serializers.PhoneDeviceSerializer
    """

    def setUp(self):
        from django_flex_user.models import FlexUser
        from django_flex_user.models import PhoneDevice

        user = FlexUser.objects.create_user(phone='+12025550001')
        self.phone_device = PhoneDevice.objects.get(user=user)

    def test_serialize(self):
        from django_flex_user.serializers import PhoneDeviceSerializer

        # Make sure the serializer only exposes the data we want it to
        serializer = PhoneDeviceSerializer(self.phone_device)
        self.assertEqual(
            serializer.data,
            {
                'id': 1,
                'name': '+*********01'
            }
        )