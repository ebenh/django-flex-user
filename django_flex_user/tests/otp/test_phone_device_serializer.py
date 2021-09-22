from django.test import TestCase


class TestPhoneDeviceSerializer(TestCase):
    """
    This class is designed to test django_flex_user.serializers.PhoneDeviceSerializer
    """

    def setUp(self):
        from django_flex_user.models import FlexUser

        self.user1 = FlexUser.objects.create_user(username='validUsername1',
                                                  email='validEmail1@example.com',
                                                  phone='+12025550001')
        self.user2 = FlexUser.objects.create_user(username='validUsername2',
                                                  email='validEmail2@example.com',
                                                  phone='+12025550002')

    def test_serialize(self):
        from django_flex_user.models.otp import PhoneDevice
        from django_flex_user.serializers import PhoneDeviceSerializer

        phone_device = PhoneDevice.objects.get(user=self.user1)

        # Make sure the serializer only exposes the data we want it to
        serializer = PhoneDeviceSerializer(phone_device)
        self.assertEqual(
            serializer.data,
            {
                'id': 1,
                'name': '+*********01'
            }
        )

    def test_serialize_many(self):
        from collections import OrderedDict
        from django_flex_user.models.otp import PhoneDevice
        from django_flex_user.serializers import PhoneDeviceSerializer

        phone_devices = PhoneDevice.objects.all()

        # Make sure the serializer only exposes the data we want it to
        serializer = PhoneDeviceSerializer(phone_devices, many=True)
        self.assertEqual(
            serializer.data,
            [
                OrderedDict([('id', 1), ('name', '+*********01')]),
                OrderedDict([('id', 2), ('name', '+*********02')])
            ]
        )
