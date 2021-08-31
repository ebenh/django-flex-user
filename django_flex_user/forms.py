from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import AuthenticationForm
from django.utils.text import capfirst

from .validators import FlexUserUnicodeUsernameValidator

UserModel = get_user_model()


class FlexUserAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label=capfirst(
            '{username}, {email} or {phone_number}'.format(
                username=UserModel._meta.get_field('username').verbose_name,
                email=UserModel._meta.get_field('email').verbose_name,
                phone_number=UserModel._meta.get_field('phone_number').verbose_name,
            )
        ),
        widget=forms.TextInput(attrs={'autofocus': True})
    )

    usernameValidator = FlexUserUnicodeUsernameValidator()

    def __init__(self, request=None, *args, **kwargs):
        """
        The 'request' parameter is set for custom auth use by subclasses.
        The form data comes in via the standard 'data' kwarg.
        """
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username is not None and password:
            user_identifier = self.infer_and_normalize_user_identifier(username)
            self.user_cache = authenticate(request=self.request, **user_identifier, password=password)

            if self.user_cache is None:
                raise self.get_invalid_login_error(next(iter(user_identifier)))
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

    def infer_and_normalize_user_identifier(self, value):
        d = {}
        try:
            # See if value is a username
            self.usernameValidator(value)
        except ValidationError:
            # See if value is an email address or phone number
            if '@' in value:
                d = {'email': UserModel.objects.normalize_email(value)}
            else:
                d = {'phone_number': value}
        else:
            d = {'username': UserModel.normalize_username(value)}
        finally:
            return d

    def get_invalid_login_error(self, user_identifier_type):
        return forms.ValidationError(
            self.error_messages['invalid_login'],
            code='invalid_login',
            params={'username': UserModel._meta.get_field(user_identifier_type).verbose_name},
        )


# Set our custom authentication form to be the default authentication form for Django
LoginView.authentication_form = FlexUserAuthenticationForm
