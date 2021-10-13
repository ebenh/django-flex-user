from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

from social_core.backends.facebook import FacebookOAuth2
from social_core.backends.google import GoogleOAuth2

# Reference: https://docs.djangoproject.com/en/3.0/topics/auth/customizing/

UserModel = get_user_model()


class FlexUserModelBackend(ModelBackend):
    """
    Our implementation of django.contrib.auth.backends.ModelBackend.
    """

    def authenticate(self, request, username=None, email=None, phone=None, password=None):
        """
        Returns a :class:`~django_flex_user.models.user.FlexUser` object for a set of given credentials.

        :param request: HTTP Request object
        :type request: :class:`~django.http.HttpRequest`
        :param username: The user's username, defaults to None.
        :type username: str, optional
        :param email: The user's email address, defaults to None.
        :type email: str, optional
        :param phone: The user's phone number, defaults to None.
        :type phone: str, optional
        :param password: The user's password, defaults to None.
        :type password: str, optional
        :return: The authenticated user.
        :rtype: :class:`~django_flex_user.models.user.FlexUser`, :class:`NoneType`
        """

        try:
            user = UserModel._default_manager.get_by_natural_key(username, email, phone)
        except UserModel.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user (#20760).
            UserModel().set_password(password)
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user


class FlexUserFacebookOAuth2(FacebookOAuth2):
    """
    Our implementation of social_core.backends.facebook.FacebookOAuth2.
    """

    def get_user_details(self, response):
        """
        Return user details from Facebook account.

        Our implementation of this method is identical to the superclass implementation except when the OAuth service
        doesn't return an email address for the user, we set it to be None instead of the empty string. This is because
        django_flex_user.models.FlexUser does not permit email to be the empty string.

        :param response:
        :return:
        """
        fullname, first_name, last_name = self.get_user_names(
            response.get('name', ''),
            response.get('first_name', ''),
            response.get('last_name', '')
        )
        return {'username': response.get('username', response.get('name')),
                # 'email': response.get('email', ''),
                'email': response.get('email', None),  # Set default email to be None
                'fullname': fullname,
                'first_name': first_name,
                'last_name': last_name}


class FlexUserGoogleOAuth2(GoogleOAuth2):
    """
    Our implementation of social_core.backends.facebook.GoogleOAuth2.
    """

    def get_user_details(self, response):
        """
        Return user details from Google API account.

        Our implementation of this method is identical to the superclass implementation except when the OAuth service
        doesn't return an email address for the user, we set it to be None instead of the empty string. This is because
        django_flex_user.models.FlexUser does not permit email to be the empty string.

        :param response:
        :return:
        """
        if 'email' in response:
            email = response['email']
        else:
            # email = ''
            email = None  # Set default email to be None

        name, given_name, family_name = (
            response.get('name', ''),
            response.get('given_name', ''),
            response.get('family_name', ''),
        )

        fullname, first_name, last_name = self.get_user_names(
            name, given_name, family_name
        )
        return {'username': email.split('@', 1)[0],
                'email': email,
                'fullname': fullname,
                'first_name': first_name,
                'last_name': last_name}
