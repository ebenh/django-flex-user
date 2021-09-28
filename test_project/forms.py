from django import forms
from django.utils.text import capfirst
from django.contrib.auth import get_user_model

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
