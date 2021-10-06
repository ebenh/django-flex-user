#
# Configure django-flex-user
#

from test_project.components.settings import INSTALLED_APPS, AUTHENTICATION_BACKENDS

INSTALLED_APPS += (
    'django_flex_user.apps.DjangoFlexUserConfig',
)

AUTHENTICATION_BACKENDS += [
    'django_flex_user.backends.FlexUserModelBackend',
]

AUTH_USER_MODEL = 'django_flex_user.FlexUser'

FLEX_USER_OTP_EMAIL_FUNCTION = 'test_project.verification.email_otp'
FLEX_USER_OTP_SMS_FUNCTION = 'test_project.verification.sms_otp'
