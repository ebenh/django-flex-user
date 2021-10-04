import string, random, importlib
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from phonenumber_field.modelfields import PhoneNumberField

from django_flex_user.util import obscure_email, obscure_phone


def get_module_member(name):
    module_name, member_name = name.rsplit('.', 1)
    module = importlib.import_module(module_name, member_name)
    member = getattr(module, member_name)
    return member


class TimeoutError(Exception):
    def __init__(self, verification_timeout, verification_failure_count, message):
        self.verification_timeout = verification_timeout
        self.verification_failure_count = verification_failure_count
        self.message = message
        super().__init__(self.message)


class TransmissionError(Exception):
    pass


class OTPToken(models.Model):
    user = models.ForeignKey('FlexUser', on_delete=models.CASCADE)
    verified = models.BooleanField(_('verified'), default=False)

    timeout = models.DateTimeField(_('verification timeout'), null=True, blank=True)
    failure_count = models.PositiveIntegerField(_('verification failure count'), default=0)

    def _set_timeout(self):
        self.timeout = timezone.now() + timedelta(seconds=2 ** self.failure_count)
        self.failure_count += 1

    def _reset_timeout(self):
        self.timeout = None
        self.failure_count = 0

    def _is_timed_out(self):
        if self.timeout and timezone.now() < self.timeout:
            raise TimeoutError(self.timeout, self.failure_count,
                               "Too many failed verification attempts. Please try again later.")

    def throttle_reset(fun):
        def inner(self):
            fun(self)
            self._reset_timeout()
            self.save()

        return inner

    def throttle(fun):
        def inner(self, password):
            self._is_timed_out()
            success = fun(self, password)
            if success:
                self._reset_timeout()
            else:
                self._set_timeout()
            self.save()
            return success

        return inner

    def check_password(self, password):
        raise NotImplementedError

    def get_name(self):
        raise NotImplementedError

    def get_obscured_name(self):
        raise NotImplementedError

    def __str__(self):
        return self.get_name()

    class Meta:
        abstract = True


class SideChannelToken(OTPToken):
    password = models.CharField(_('password'), null=True, blank=True, max_length=256)
    expiration = models.DateTimeField(_('expiration'), null=True, blank=True)

    @property
    def password_length(self):
        raise NotImplementedError

    @property
    def password_alphabet(self):
        raise NotImplementedError

    @OTPToken.throttle_reset
    def generate_password(self):
        self.password = ''.join(
            random.SystemRandom().choice(self.password_alphabet) for _ in range(self.password_length)
        )
        self.expiration = timezone.now() + getattr(settings, 'FLEX_USER_OTP_TTL', timedelta(minutes=15))

    @OTPToken.throttle
    def check_password(self, password):
        # Check whether the password has expired
        if self.expiration and self.expiration <= timezone.now():
            return False

        # Check the password
        success = False if self.password is None else self.password == password
        if success:
            self.verified = True
            self.password = None
            self.expiration = None

        return success

    def reset_password(self):
        self.verified = False
        self.password = None
        self.expiration = None

    def send_password(self, **kwargs):
        raise NotImplementedError

    class Meta:
        abstract = True


class EmailToken(SideChannelToken):
    email = models.EmailField(_('email address'))

    password_length = getattr(settings, 'FLEX_USER_OTP_LENGTH_FOR_EMAIL_TOKEN', 64)
    password_alphabet = getattr(settings, 'FLEX_USER_OTP_ALPHABET_FOR_EMAIL_TOKEN', string.printable)

    def get_name(self):
        return self.email

    def get_obscured_name(self):
        return obscure_email(self.email)

    def send_password(self, **kwargs):
        flex_user_email_function = getattr(settings, 'FLEX_USER_OTP_EMAIL_FUNCTION', None)
        if flex_user_email_function is None:
            raise NotImplementedError

        fun = get_module_member(flex_user_email_function)
        fun(self, **kwargs)


class PhoneToken(SideChannelToken):
    phone = PhoneNumberField(_('phone number'))

    password_length = getattr(settings, 'FLEX_USER_OTP_LENGTH_FOR_PHONE_TOKEN', 6)
    password_alphabet = getattr(settings, 'FLEX_USER_OTP_ALPHABET_FOR_PHONE_TOKEN', string.digits)

    def get_name(self):
        return str(self.phone)

    def get_obscured_name(self):
        return obscure_phone(self.phone)

    def send_password(self, **kwargs):
        flex_user_sms_function = getattr(settings, 'FLEX_USER_OTP_SMS_FUNCTION', None)
        if flex_user_sms_function is None:
            raise NotImplementedError

        fun = get_module_member(flex_user_sms_function)
        fun(self, **kwargs)
