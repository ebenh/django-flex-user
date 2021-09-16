from django.core.mail import send_mail


def email_otp(recipient, challenge):
    send_mail('Verify your account', f'Your one-time password:\n\n{challenge}', 'eben@derso.org', (recipient,))


def sms_otp(recipient, challenge):
    print(recipient)
    print(challenge)
