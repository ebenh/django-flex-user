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


class VerificationTimeout(Exception):
    def __init__(self, verification_timeout, verification_failure_count, message):
        self.verification_timeout = verification_timeout
        self.verification_failure_count = verification_failure_count

        super().__init__(message)


class Device(models.Model):
    user = models.ForeignKey('FlexUser', on_delete=models.CASCADE)
    confirmed = models.BooleanField(_('confirmed'), default=False)

    verification_timeout = models.DateTimeField(_('verification timeout'), null=True, blank=True)
    verification_failure_count = models.PositiveIntegerField(_('verification failure count'), default=0)

    def _set_timeout(self, save=False):
        self.verification_timeout = timezone.now() + timedelta(seconds=2 ** self.verification_failure_count)
        self.verification_failure_count += 1
        if save:
            self.save(update_fields=['verification_timeout', 'verification_failure_count'])

    def _reset_timeout(self, save=False):
        self.verification_timeout = None
        self.verification_failure_count = 0
        if save:
            self.save(update_fields=['verification_timeout', 'verification_failure_count'])

    def _is_timed_out(self):
        if self.verification_timeout and timezone.now() < self.verification_timeout:
            raise VerificationTimeout(self.verification_timeout, self.verification_failure_count,
                                      "Too many failed verification attempts. Please try again later.")

    def throttle_reset(fun):
        def inner(self):
            fun(self)
            self._reset_timeout()
            self.save()

        return inner

    def throttle(verify_challenge_fun):
        def inner(self, challenge):
            self._is_timed_out()
            success = verify_challenge_fun(self, challenge)
            if success:
                self._reset_timeout()
            else:
                self._set_timeout()
            self.save()
            return success

        return inner

    def verify_challenge(self, challenge):
        raise NotImplementedError

    def get_name(self):
        raise NotImplementedError

    def get_obscured_name(self):
        raise NotImplementedError

    def __str__(self):
        return self.get_name()

    class Meta:
        abstract = True


class OOBDevice(Device):
    challenge = models.CharField(_('challenge'), blank=True, null=True, max_length=256)
    challenge_length = 6
    challenge_alphabet = string.digits

    @Device.throttle_reset
    def generate_challenge(self):
        challenge = ''.join(
            random.SystemRandom().choice(self.challenge_alphabet) for _ in range(self.challenge_length))
        self.challenge = challenge.encode('unicode_escape').decode('utf-8')

    @Device.throttle
    def verify_challenge(self, challenge):
        success = False if self.challenge is None else self.challenge == challenge
        if success:
            self.challenge = None
            self.confirmed = True
        return success

    def send_challenge(self):
        raise NotImplementedError

    class Meta:
        abstract = True


class EmailDevice(OOBDevice):
    challenge_length = 128
    challenge_alphabet = string.printable

    email = models.EmailField(_('email address'))

    def get_name(self):
        return self.email

    def get_obscured_name(self):
        return obscure_email(self.email)

    def send_challenge(self):
        flex_user_email_function = getattr(settings, 'FLEX_USER_EMAIL_FUNCTION',
                                           'django_flex_user.verification.email_otp')
        fun = get_module_member(flex_user_email_function)
        fun(self.email, self.challenge)


class PhoneDevice(OOBDevice):
    phone = PhoneNumberField(_('phone number'), )

    def get_name(self):
        return str(self.phone)

    def get_obscured_name(self):
        return obscure_phone(str(self.phone))

    def _send_challenge(self):
        pass

    def send_challenge(self):
        flex_user_sms_function = getattr(settings, 'FLEX_USER_SMS_FUNCTION',
                                         'django_flex_user.verification.sms_otp')
        fun = get_module_member(flex_user_sms_function)
        fun(self.phone, self.challenge)
