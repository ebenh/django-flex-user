try:
    # noinspection PyUnresolvedReferences,PyPackageRequirements
    import simplejson as json
except ModuleNotFoundError:
    import json

from django.core.mail import send_mail
from smtplib import SMTPException
# noinspection PyPackageRequirements
import requests

from django_flex_user.models.otp import OTPTransmissionError


def email_otp(recipient, challenge):
    try:
        send_mail('Verify your account', f'Your one-time password:\n\n{challenge}', 'eben@derso.org', (recipient,))
    except (SMTPException, ValueError) as e:
        raise OTPTransmissionError from e


def sms_otp(recipient, challenge):
    # note eben: This API key only allows us to send one free message a day
    resp = requests.post('https://textbelt.com/text', {
        'phone': recipient.as_e164,
        'message': f'Your one-time password:\n\n{challenge}',
        'key': 'textbelt',
    })
    try:
        j = resp.json()
    except (json.JSONDecodeError, ValueError) as e:
        raise OTPTransmissionError from e
    else:
        if not j.get('success'):
            raise OTPTransmissionError(j.get('error'))
