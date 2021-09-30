try:
    # noinspection PyUnresolvedReferences,PyPackageRequirements
    import simplejson as json
except ModuleNotFoundError:
    import json

from django.core.mail import send_mail
from smtplib import SMTPException
# noinspection PyPackageRequirements
import requests

from django_flex_user.models.otp import TransmissionError


def email_otp(recipient, password):
    try:
        send_mail('Verify your account', f'Your one-time password:\n\n{password}', None, (recipient,))
    except (SMTPException, ValueError) as e:
        raise TransmissionError from e


def sms_otp(recipient, password):
    # note eben: This API key only allows us to send one free message a day
    resp = requests.post('https://textbelt.com/text', {
        'phone': recipient.as_e164,
        'message': f'Your one-time password:\n\n{password}',
        'key': 'textbelt',
    })
    try:
        j = resp.json()
    except (json.JSONDecodeError, ValueError) as e:
        raise TransmissionError from e
    else:
        if not j.get('success'):
            raise TransmissionError(j.get('error'))
