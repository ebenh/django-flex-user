from django import forms
from django.utils.text import capfirst
from django.contrib.auth import get_user_model, password_validation
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
        super().__init__(*args, **kwargs)
        self.otp_token = otp_token

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


class SignUpWithUsernameForm(forms.ModelForm):
    class Meta:
        model = UserModel
        fields = ('username', 'password')
        # required = ('username', 'password')
        widgets = {
            'password': forms.PasswordInput()
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Override bank = True set in our model
        self.fields['username'].required = True

    def clean_username(self):
        # Normalize username
        username = self.cleaned_data['username']
        return UserModel.normalize_username(username)

    def clean(self):
        # Validate unique
        super().clean()

        # Check password strength
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']

        # note eben: UserAttributeSimilarityValidator doesn't normalize email before comparing it
        # note eben: Be aware that there may be issues if a password validator expects the user instance to have
        # a valid id and/or have been persisted to the database. For example, issues may occur in a password
        # validator that checks for password reuse.
        temp_user = self.Meta.model(username=username)
        temp_user.set_unusable_password()
        password_validation.validate_password(password, temp_user)

        return self.cleaned_data

    def save(self):
        password = self.cleaned_data.pop('password')
        self.instance.set_password(password)
        return super().save()
