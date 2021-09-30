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
    password = forms.CharField(label='Verification code')

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
                raise ValidationError('The verification code you entered is incorrect or expired.')

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


class SignUpWithEmailForm(forms.ModelForm):
    class Meta:
        model = UserModel
        fields = ('email', 'password')
        # required = ('username', 'password')
        widgets = {
            'password': forms.PasswordInput()
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Override bank = True set in our model
        self.fields['email'].required = True

    def clean(self):
        # Validate unique
        super().clean()

        # Check password strength
        email = self.cleaned_data['email']
        password = self.cleaned_data['password']

        # note eben: UserAttributeSimilarityValidator doesn't normalize email before comparing it
        # note eben: Be aware that there may be issues if a password validator expects the user instance to have
        # a valid id and/or have been persisted to the database. For example, issues may occur in a password
        # validator that checks for password reuse.
        temp_user = self.Meta.model(email=email)
        temp_user.set_unusable_password()
        password_validation.validate_password(password, temp_user)

        return self.cleaned_data

    def save(self):
        password = self.cleaned_data.pop('password')
        self.instance.set_password(password)
        return super().save()


class SignUpWithPhoneForm(forms.ModelForm):
    class Meta:
        model = UserModel
        fields = ('phone', 'password')
        # required = ('username', 'password')
        widgets = {
            'password': forms.PasswordInput()
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Override bank = True set in our model
        self.fields['phone'].required = True

    def clean(self):
        # Validate unique
        super().clean()

        # Check password strength

        # If phonenumber_field.formfields.PhoneNumberField.to_python can't convert the user's text input into a valid
        # phonenumbers.phonenumber.PhoneNumber object, an exception is raised and no "phone" key is added to
        # self.cleaned_data (It's also worth mentioning that following this error the validator
        # phonenumber_field.validators import validate_international_phonenumber will not run).
        # This results in the following field error:
        #   "Enter a valid phone number (e.g. (201) 555-0123) or a number with an international call prefix."
        # As well as the following (redundant) non-field error:
        #   "You must supply at least one of username, email address or phone number."
        # To suppress the redundant non-field error, provide the user a widget for inputting phone numbers which
        # constrains their input to only values which can form a valid phonenumbers.phonenumber.PhoneNumber object.
        phone = self.cleaned_data.get('phone')
        password = self.cleaned_data['password']

        # note eben: UserAttributeSimilarityValidator doesn't normalize email before comparing it
        # note eben: Be aware that there may be issues if a password validator expects the user instance to have
        # a valid id and/or have been persisted to the database. For example, issues may occur in a password
        # validator that checks for password reuse.
        temp_user = self.Meta.model(phone=phone)
        temp_user.set_unusable_password()
        password_validation.validate_password(password, temp_user)

        return self.cleaned_data

    def save(self):
        password = self.cleaned_data.pop('password')
        self.instance.set_password(password)
        return super().save()


class UserForm(forms.ModelForm):
    class Meta:
        model = UserModel
        fields = ('username', 'email', 'phone')
