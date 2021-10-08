from django.test import TestCase


class TestPhoneTokenSerializer(TestCase):
    """
    This class is designed to test django_flex_user.serializers.PhoneTokenSerializer
    """

    def setUp(self):
        from django_flex_user.models.user import FlexUser
        from django_flex_user.models.otp import PhoneToken

        user = FlexUser.objects.create_user(phone='+12025550001')
        self.phone_token = PhoneToken.objects.get(user=user)

    def test_serialize(self):
        from django_flex_user.serializers import PhoneTokenSerializer
        from rest_framework.test import APIRequestFactory
        from django.urls import reverse

        # Dummy request for serializer context and building absolute URI's
        request = APIRequestFactory().get('/')

        # Make sure the serializer only exposes the data we want it to
        serializer = PhoneTokenSerializer(self.phone_token, context={'request': request})
        self.assertEqual(
            serializer.data,
            {
                'name': '+*********01',
                'uri': f'{request.build_absolute_uri(reverse("phone-token", args=(self.phone_token.id,)))}'
            }
        )
