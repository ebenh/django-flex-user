from django.test import TestCase


class TestEmailTokenSerializer(TestCase):
    """
    This class is designed to test django_flex_user.serializers.EmailTokenSerializer
    """

    def setUp(self):
        from django_flex_user.models.user import FlexUser
        from django_flex_user.models.otp import EmailToken

        user = FlexUser.objects.create_user(email='validEmail1@example.com')
        self.email_token = EmailToken.objects.get(user=user)

    def test_serialize(self):
        from django_flex_user.serializers import EmailTokenSerializer
        from rest_framework.test import APIRequestFactory
        from django.urls import reverse

        # Dummy request for serializer context and building absolute URI's
        request = APIRequestFactory().get('/')

        # Make sure the serializer only exposes the data we want it to
        serializer = EmailTokenSerializer(self.email_token, context={'request': request})
        self.assertEqual(
            serializer.data,
            {
                'name': 'va*********@ex*****.***',
                'uri': f'{request.build_absolute_uri(reverse("email-token", args=(self.email_token.id,)))}'
            }
        )
