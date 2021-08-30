from django.core import exceptions
from django.core.validators import EmailValidator
from django.contrib.auth import get_user_model, authenticate, password_validation, update_session_auth_hash
from django.contrib.admin.utils import quote

from rest_framework import serializers
from rest_framework.fields import empty
from rest_framework.settings import api_settings

from phonenumber_field.validators import validate_international_phonenumber

from django_otp.plugins.otp_email.models import EmailDevice

from social_django.models import UserSocialAuth

import tldextract, regex as re

from .models import SPUnicodeUsernameValidator

UserModel = get_user_model()


# https://stackoverflow.com/questions/31278418/django-rest-framework-custom-fields-validation
# https://stackoverflow.com/questions/27591574/order-of-serializer-validation-in-django-rest-framework

class SPUserSerializer(serializers.ModelSerializer):
    email_verified = serializers.SerializerMethodField('get_email_verified')
    phone_number_verified = serializers.SerializerMethodField('get_phone_number_verified')

    @staticmethod
    def get_email_verified(obj):
        try:
            return EmailDevice.objects.get(user=obj.id, email=None).confirmed
        except EmailDevice.DoesNotExist:
            return False  # todo: remove this try/catch after resetting database

    @staticmethod
    def get_phone_number_verified(obj):
        return False

    def validate_username(self, value):
        """
        Normalize username and check it for uniqueness.

        :param value:
        :return:
        """
        value = self.Meta.model.normalize_username(value)

        if value is None:
            return value

        query_set = self.Meta.model.objects.all()
        query_set = query_set.filter(username=value)
        query_set = query_set.exclude(pk=self.instance.pk) if self.instance else query_set
        if query_set.exists():
            raise serializers.ValidationError(
                self.Meta.model._meta.get_field('username').error_messages['unique']
            )
        return value

    def validate_email(self, value):
        """
        Normalize email and check it for uniqueness.

        :param value:
        :return:
        """
        value = self.Meta.model.objects.normalize_email(value)

        if value is None:
            return value

        query_set = self.Meta.model.objects.all()
        query_set = query_set.filter(email=value)
        query_set = query_set.exclude(pk=self.instance.pk) if self.instance else query_set
        if query_set.exists():
            raise serializers.ValidationError(
                self.Meta.model._meta.get_field('email').error_messages['unique']
            )
        return value

    def validate(self, attrs):
        # note eben: This method runs only if all field level validation passes

        # https://github.com/encode/django-rest-framework/issues/5521

        # Extract username, email and phone_number from supplied instance and merge it with attrs
        instance = self.instance if self.instance else self.Meta.model()
        serializer = SPUserSerializer(instance=instance)
        data = {**serializer.data, **attrs}

        errors = {}

        # Check that the caller has supplied at least one of username, email or phone_number
        if data.get('username') is None and data.get('email') is None and data.get('phone_number') is None:
            errors[api_settings.NON_FIELD_ERRORS_KEY] = \
                'You must supply at least one of {username}, {email} or {phone_number}.'.format(
                    username=self.Meta.model._meta.get_field('username').verbose_name,
                    email=self.Meta.model._meta.get_field('email').verbose_name,
                    phone_number=self.Meta.model._meta.get_field('phone_number').verbose_name
                )

        # Check password strength
        if 'password' in attrs:
            try:
                # note eben: UserAttributeSimilarityValidator doesn't normalize email before comparing it
                # note eben: Be aware that there may be issues if a password validator expects the user instance to have
                # a valid id and/or have been persisted to the database. For example, issues may occur in a password
                # validator that checks for password reuse.
                filter_keys = ('email_verified', 'phone_number_verified', 'password')
                temp_user = self.Meta.model(**{k: v for k, v in data.items() if k not in filter_keys})
                temp_user.set_unusable_password()
                password_validation.validate_password(attrs['password'], temp_user)
            except exceptions.ValidationError as e:
                errors['password'] = e.messages

        if errors:
            raise serializers.ValidationError(errors)

        return attrs

    def create(self, validated_data):
        # Ordinarily we would call django_flex_user.models.SPUser.objects.create_user to create a new user, but since doing so
        # would re-perform all the validation we already performed in this serializer, we construct a SPUser object
        # manually.
        password = validated_data.pop('password')
        user = self.Meta.model(**validated_data)
        user.set_password(password)
        user.save()
        # todo: should we authenticate the user here?
        return user

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            if attr == 'password':
                instance.set_password(value)
                # Prevent the user from being signed out of their current session upon password change.
                # https://docs.djangoproject.com/en/3.0/topics/auth/default/#session-invalidation-on-password-change
                request = self.context.get('request')
                if request and request.session.session_key:
                    update_session_auth_hash(request, instance)
            else:
                setattr(instance, attr, value)
        instance.save()
        return instance

    class Meta:
        model = UserModel
        fields = ['username', 'email', 'email_verified', 'phone_number', 'phone_number_verified', 'password']
        extra_kwargs = {
            'username': {
                'allow_blank': False,
                'validators': [SPUnicodeUsernameValidator()]  # Remove Unique validator
            },
            'email': {
                'allow_blank': False,
                'validators': [EmailValidator()]  # Remove Unique validator
            },
            'phone_number': {
                'allow_blank': False
            },
            'password': {
                'max_length': None,  # todo: redundant, this is the default value
                'write_only': True,
                'style': {'input_type': 'password'}
            }
        }


class AuthenticationSerializer(serializers.Serializer):
    username = serializers.CharField(
        allow_blank=False,
        allow_null=True,
        max_length=150,
        required=False,
        validators=[SPUnicodeUsernameValidator()]
    )
    email = serializers.EmailField(
        allow_blank=False,
        allow_null=True,
        max_length=254,
        required=False
    )
    email_verified = serializers.SerializerMethodField('get_email_verified')
    phone_number = serializers.CharField(
        allow_blank=False,
        allow_null=True,
        max_length=128,
        required=False,
        validators=[validate_international_phonenumber]
    )
    phone_number_verified = serializers.SerializerMethodField('get_phone_number_verified')
    password = serializers.CharField(
        allow_blank=False,
        allow_null=False,
        max_length=None,
        required=True,
        style={'input_type': 'password'},
        write_only=True
    )

    @staticmethod
    def get_email_verified(obj):
        return EmailDevice.objects.get(user=obj.id, email=None).confirmed

    @staticmethod
    def get_phone_number_verified(obj):
        return False

    @staticmethod
    def _english_join(items):
        return ', '.join(
            items[:-2] + [' and '.join(items[-2:])]
        )

    @staticmethod
    def validate_username(value):
        return UserModel.normalize_username(value)

    @staticmethod
    def validate_email(value):
        return UserModel.objects.normalize_email(value)

    def __init__(self, instance=None, data=empty, **kwargs):
        assert not instance, 'This serializer is not designed to work with instances.'

        assert 'partial' not in kwargs, 'This serializer is not designed to perform partial updates.'

        assert 'many' not in kwargs, 'This serializer is not designed to work with multiple objects.'

        super(AuthenticationSerializer, self).__init__(instance, data, **kwargs)
        self.user = None

    def validate(self, attrs):
        # Check that the caller has supplied at least one of username, email or phone_number
        if attrs.get('username') is None and attrs.get('email') is None and attrs.get('phone_number') is None:
            raise serializers.ValidationError(
                'You must supply at least one of {username}, {email} or {phone_number}.'.format(
                    username=UserModel._meta.get_field('username').verbose_name,
                    email=UserModel._meta.get_field('email').verbose_name,
                    phone_number=UserModel._meta.get_field('phone_number').verbose_name
                )
            )

        # Check that the supplied username, email and phone_number match an existing user
        query = {k: v for k, v in attrs.items() if k is not 'password' and v is not None}
        try:
            user = UserModel.objects.get(**query)
        except UserModel.DoesNotExist:
            if len(query) == 1:
                k = next(iter(query))
                raise serializers.ValidationError(
                    {k: f"Couldn't find a user with that {UserModel._meta.get_field(k).verbose_name}."}
                )
            else:
                verbose_names = [str(UserModel._meta.get_field(k).verbose_name) for k in query.keys()]
                raise serializers.ValidationError(
                    f"Couldn't find a user with that {self._english_join(verbose_names)}."
                )

        # Check that the user has a password set
        if not user.has_usable_password():
            raise serializers.ValidationError(
                {'password': "You can't sign in using this method. Try signing in using Facebook or Google."}
            )

        # Check that the supplied password is correct
        self.user = authenticate(self.context.get('request'), **attrs)

        if self.user is None:
            raise serializers.ValidationError({'password': 'The password you entered is invalid.'})

        # Populate the serializer with the authenticated user's username, email and phone_number
        attrs['username'] = self.user.username
        attrs['email'] = self.user.email
        attrs['phone_number'] = self.user.phone_number

        return attrs

    def create(self, validated_data):
        return self.user

    def update(self, instance, validated_data):
        assert False, 'This serializer is not designed to work with instances.'

        return self.user


class OTPSerializer(serializers.Serializer):
    pin = serializers.CharField(write_only=True)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class EmailDeviceSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField('get_id')
    email = serializers.SerializerMethodField('get_email')

    @staticmethod
    def _obscure_part(part):
        """
        For parts longer than three characters, we reveal the first two characters and obscure the rest.

        Parts up to three characters long are handled as special cases.

        We reveal no more than 50% of the characters for any part.

        :param part:
        :return:
        """
        if not part:
            return part  # part is None or the empty string, nothing to obscure

        length = len(part)
        if length == 1:
            return '*'  # 0% revealed, 100% obscured

        if length == 2:
            return part[:1] + '*'  # 50% revealed, 50% obscured

        if length == 3:
            return part[:1] + '**'  # 33% revealed, 66% obscured

        if length > 3:
            return part[:2] + '*' * (length - 2)  # At most 50% revealed, At least 50% obscured

    @staticmethod
    def get_id(obj):
        return quote(obj.persistent_id)

    def get_email(self, obj):
        email = obj.email or obj.user.email

        if not email:
            return ''

        user, host = email.split('@')
        subdomain, domain, suffix = tldextract.extract(host)

        user = self._obscure_part(user)
        subdomain = self._obscure_part(subdomain)
        domain = self._obscure_part(domain)
        suffix = re.sub('[^.]', '*', suffix)  # always obscure the TLD and SLD

        return f'{user}@{subdomain}{"." if subdomain and domain else ""}{domain}{"." if domain and suffix else ""}{suffix}'

    class Meta:
        model = EmailDevice
        fields = ['id', 'email']


class UserSocialAuthSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField('get_name')
    email = serializers.SerializerMethodField('get_email')

    @staticmethod
    def get_name(obj):
        return obj.extra_data.get('name')

    @staticmethod
    def get_email(obj):
        return obj.extra_data.get('email')

    class Meta:
        model = UserSocialAuth
        fields = ['id', 'uid', 'provider', 'name', 'email']
        extra_kwargs = {
            'id': {'read_only': True},
            'uid': {'read_only': True},
            'provider': {'read_only': True}
        }
