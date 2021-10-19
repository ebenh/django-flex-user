from django.test import TestCase


class TestEmailTokenSerializer(TestCase):
    """
    This class is designed to test django_flex_user.serializers.EmailTokenSerializer
    """

    def setUp(self):
        from django_flex_user.models.user import FlexUser

        self.user = FlexUser.objects.create_user(email='validEmail1@example.com')

    def test_serialize(self):
        from django_flex_user.serializers import EmailTokenSerializer
        from rest_framework.test import APIRequestFactory
        from django.urls import reverse

        # Dummy request for serializer context and building absolute URI's
        request = APIRequestFactory().get('/')

        # Get email token
        email_token = self.user.emailtoken_set.first()

        # Make sure the serializer only exposes the data we want it to
        serializer = EmailTokenSerializer(email_token, context={'request': request})
        self.assertEqual(
            serializer.data,
            {
                'name': 'va*********@ex*****.***',
                'uri': f'{request.build_absolute_uri(reverse("email-token", args=(email_token.id,)))}'
            }
        )
