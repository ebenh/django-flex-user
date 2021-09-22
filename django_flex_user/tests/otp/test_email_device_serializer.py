from django.test import TestCase


class TestEmailDeviceSerializer(TestCase):
    """
    This class is designed to test django_flex_user.serializers.EmailDeviceSerializer
    """

    def setUp(self):
        from django_flex_user.models import FlexUser
        from django_flex_user.models import EmailDevice

        user = FlexUser.objects.create_user(email='validEmail1@example.com')
        self.email_device = EmailDevice.objects.get(user=user)

    def test_serialize(self):
        from django_flex_user.serializers import EmailDeviceSerializer

        # Make sure the serializer only exposes the data we want it to
        serializer = EmailDeviceSerializer(self.email_device)
        self.assertEqual(
            serializer.data,
            {
                'id': 1,
                'name': 'va*********@ex*****.***'
            }
        )
