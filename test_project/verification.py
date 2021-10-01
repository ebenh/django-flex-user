try:
    # noinspection PyUnresolvedReferences,PyPackageRequirements
    import simplejson as json
except ModuleNotFoundError:
    import json

from django.core.mail import send_mail
from django.urls import reverse
from smtplib import SMTPException
# noinspection PyPackageRequirements
import requests
import base64

from django_flex_user.models.otp import TransmissionError


def email_otp(email_token, **kwargs):
    request = kwargs.get('request')
    view_name = kwargs.get('view_name')

    if request and view_name:
        password = base64.urlsafe_b64encode(email_token.password.encode("utf-8")).decode("ascii")
        link = request.build_absolute_uri(reverse(view_name, args=('email', email_token.id, password,)))
    else:
        raise ValueError('Missing kwargs')

    try:
        send_mail(
            '[django-flex-user] Verify your account',
            f'Click the link below to verify your account:\n\n{link}',
            None,
            (email_token.email,)
        )
    except (SMTPException, ValueError) as e:
        raise TransmissionError from e


def sms_otp(phone_token, **kwargs):
    # note eben: This API key only allows us to send one free message a day
    resp = requests.post('https://textbelt.com/text', {
        'phone': phone_token.phone.as_e164,
        'message': f'Your verification code:\n\n{phone_token.password}',
        'key': 'textbelt',
    })
    try:
        j = resp.json()
    except (json.JSONDecodeError, ValueError) as e:
        raise TransmissionError from e
    else:
        if not j.get('success'):
            raise TransmissionError(j.get('error'))
