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
        uri = request.build_absolute_uri(reverse(view_name, args=('email', email_token.id, password,)))
    else:
        raise ValueError('Missing kwargs')

    try:
        send_mail(
            '[django-flex-user] Verify your account',
            f'Click the link below to verify your django-flex-user account:\n\n{uri}',
            None,
            (email_token.email,)
        )
    except (SMTPException, ValueError) as e:
        raise TransmissionError from e


def sms_otp(phone_token, **kwargs):
    # note eben: This API key only allows us to send one free message a day
    resp = requests.post('https://textbelt.com/text', {
        'phone': phone_token.phone.as_e164,
        'message': f'Your django-flex-user verification code:\n\n{phone_token.password}',
        'key': 'textbelt',
    })
    try:
        j = resp.json()
    except (json.JSONDecodeError, ValueError) as e:
        raise TransmissionError from e
    else:
        if not j.get('success'):
            raise TransmissionError(j.get('error'))


def email_validation_link(strategy, backend, code, partial_token):
    """
    Our email verification function for social-auth-app-django. It's called by the mail_validation partial pipeline
    function to send verification emails.

    See SOCIAL_AUTH_EMAIL_VALIDATION_FUNCTION.

    :param strategy:
    :param backend:
    :param code:
    :param partial_token:
    :return:
    """
    uri_prefix = strategy.build_absolute_uri(
        reverse('social:complete', args=(backend.name,))
    )

    uri_postfix = f'?verification_code={code.code}&partial_token={partial_token}'

    uri = f'{uri_prefix}{uri_postfix}'

    try:
        send_mail(
            '[django-flex-user] Verify your account',
            f'Click the link below to verify your django-flex-user account:\n\n{uri}',
            None,
            (code.email,)
        )
    except (SMTPException, ValueError):
        pass
