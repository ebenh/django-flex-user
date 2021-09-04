import string, random

from django.db import models

from phonenumber_field.modelfields import PhoneNumberField

from django_flex_user.util import obscure_email


class Device(models.Model):
    confirmed = models.BooleanField(default=False)

    def get_name(self):
        raise NotImplementedError

    def get_obscured_name(self):
        raise NotImplementedError


class OOBDevice(Device):
    challenge = models.CharField(max_length=256)
    challenge_length = 6
    challenge_alphabet = string.digits

    def generate_challenge(self):
        self.challenge = ''.join(
            random.SystemRandom().choice(self.challenge_alphabet) for _ in range(self.challenge_length))
        return self.challenge

    def verify_challenge(self, challenge):
        return self.challenge == challenge


class EmailDevice(OOBDevice):
    challenge_length = 256
    challenge_alphabet = string.printable

    email = models.EmailField()

    def get_name(self):
        return self.email

    def get_obscured_name(self):
        return obscure_email(self.email)


class PhoneDevice(OOBDevice):
    phone = PhoneNumberField()

    def get_name(self):
        return self.phone

    def get_obscured_name(self):
        raise NotImplementedError
