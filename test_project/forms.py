from django import forms
from django.utils.text import capfirst
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from django_flex_user.models.otp import TimeoutError

UserModel = get_user_model()


class OTPTokensSearchForm(forms.Form):
    user_identifier = forms.CharField(
        label=capfirst(
            '{username}, {email} or {phone}'.format(
                username=UserModel._meta.get_field('username').verbose_name,
                email=UserModel._meta.get_field('email').verbose_name,
                phone=UserModel._meta.get_field('phone').verbose_name,
            )
        )
    )


class VerifyOTPForm(forms.Form):
    password = forms.CharField(label='Password')

    def __init__(self, otp_token=None, *args, **kwargs):
        self.otp_token = otp_token
        super().__init__(*args, **kwargs)

    def clean_password(self):
        password = self.cleaned_data['password']

        try:
            success = self.otp_token.check_password(password)
        except TimeoutError:
            raise ValidationError("You're doing that too much. Please wait before trying again.")
        else:
            if not success:
                raise ValidationError('The password you entered was incorrect.')

        return password
