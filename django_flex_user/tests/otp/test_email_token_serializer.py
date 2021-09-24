from django.test import TestCase


class TestEmailTokenSerializer(TestCase):
    """
    This class is designed to test django_flex_user.serializers.EmailTokenSerializer
    """

    def setUp(self):
        from django_flex_user.models import FlexUser
        from django_flex_user.models import EmailToken

        user = FlexUser.objects.create_user(email='validEmail1@example.com')
        self.email_token = EmailToken.objects.get(user=user)

    def test_serialize(self):
        from django_flex_user.serializers import EmailTokenSerializer

        # Make sure the serializer only exposes the data we want it to
        serializer = EmailTokenSerializer(self.email_token)
        self.assertEqual(
            serializer.data,
            {
                'id': 1,
                'name': 'va*********@ex*****.***'
            }
        )
