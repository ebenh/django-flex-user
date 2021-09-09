import string, random
from datetime import timedelta

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from phonenumber_field.modelfields import PhoneNumberField

from django_flex_user.util import obscure_email, obscure_phone


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

    def set_timeout(self, save=False):
        self.verification_timeout = timezone.now() + timedelta(seconds=2 ** self.verification_failure_count)
        self.verification_failure_count += 1
        if save:
            self.save(update_fields=['verification_timeout', 'verification_failure_count'])

    def reset_timeout(self, save=False):
        self.verification_timeout = None
        self.verification_failure_count = 0
        if save:
            self.save(update_fields=['verification_timeout', 'verification_failure_count'])

    def is_timed_out(self):
        if self.verification_timeout and timezone.now() < self.verification_timeout:
            raise VerificationTimeout(self.verification_timeout, self.verification_failure_count,
                                      "Too many failed verification attempts. Please try again later.")

    def generate_challenge(self):
        self._generate_challenge()
        self.reset_timeout()
        self.save()

    def _generate_challenge(self):
        raise NotImplementedError

    def verify_challenge(self, challenge):
        self.is_timed_out()
        success = self._verify_challenge(challenge)
        if success:
            self.reset_timeout()
        else:
            self.set_timeout()
        self.save()
        return success

    def _verify_challenge(self, challenge):
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

    def _generate_challenge(self):
        challenge = ''.join(
            random.SystemRandom().choice(self.challenge_alphabet) for _ in range(self.challenge_length))
        self.challenge = challenge.encode('unicode_escape').decode('utf-8')

    def _verify_challenge(self, challenge):
        success = self.challenge == challenge
        if success:
            self.challenge = None
            self.confirmed = True
        return success

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


class PhoneDevice(OOBDevice):
    phone = PhoneNumberField(_('phone number'), )

    def get_name(self):
        return self.phone.as_international

    def get_obscured_name(self):
        return obscure_phone(self.phone.as_international)
