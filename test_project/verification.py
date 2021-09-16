from django.core.mail import send_mail
import requests


def email_otp(recipient, challenge):
    send_mail('Verify your account', f'Your one-time password:\n\n{challenge}', 'eben@derso.org', (recipient,))


def sms_otp(recipient, challenge):
    # note eben: This API key only allows us to send one free message a day
    resp = requests.post('https://textbelt.com/text', {
        'phone': recipient.as_e164,
        'message': f'Your one-time password:\n\n{challenge}',
        'key': 'textbelt',
    })
    print(resp.json())
