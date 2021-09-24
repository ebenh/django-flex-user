from django.test import TestCase


class TestPhoneTokenSerializer(TestCase):
    """
    This class is designed to test django_flex_user.serializers.PhoneTokenSerializer
    """

    def setUp(self):
        from django_flex_user.models import FlexUser
        from django_flex_user.models import PhoneToken

        user = FlexUser.objects.create_user(phone='+12025550001')
        self.phone_token = PhoneToken.objects.get(user=user)

    def test_serialize(self):
        from django_flex_user.serializers import PhoneTokenSerializer

        # Make sure the serializer only exposes the data we want it to
        serializer = PhoneTokenSerializer(self.phone_token)
        self.assertEqual(
            serializer.data,
            {
                'id': 1,
                'name': '+*********01'
            }
        )
