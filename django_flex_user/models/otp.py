import string, random

from django.db import models
from django.utils.translation import gettext_lazy as _

from phonenumber_field.modelfields import PhoneNumberField

from django_flex_user.util import obscure_email, obscure_phone


class Device(models.Model):
    user = models.ForeignKey('FlexUser', on_delete=models.CASCADE)
    challenge = models.CharField(_('challenge'), null=True, blank=True, max_length=256)
    confirmed = models.BooleanField(_('confirmed'), default=False)

    def get_name(self):
        raise NotImplementedError

    def get_obscured_name(self):
        raise NotImplementedError

    def __str__(self):
        return self.get_name()

    class Meta:
        abstract = True


class OOBDevice(Device):
    challenge_length = 6
    challenge_alphabet = string.digits

    def generate_challenge(self):
        challenge = ''.join(
            random.SystemRandom().choice(self.challenge_alphabet) for _ in range(self.challenge_length))
        self.challenge = challenge.encode('unicode_escape').decode('utf-8')
        self.save(update_fields=['challenge'])

    def verify_challenge(self, challenge):
        success = self.challenge == challenge
        if success:
            self.challenge = None
            self.confirmed = True
            self.save(update_fields=['challenge', 'confirmed'])
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
