Installation
============
1. Install the Python package from the Python Package Index (PyPi)::

    pip install django-flex-user

2. Modify your settings.py as follows::

    INSTALLED_APPS += (
        'django_flex_user.apps.DjangoFlexUserConfig',
    )

    AUTHENTICATION_BACKENDS += (
        'django_flex_user.backends.FlexUserModelBackend',
    )

    AUTH_USER_MODEL = 'django_flex_user.FlexUser'

3. Register callbacks::

    FLEX_USER_OTP_EMAIL_FUNCTION = 'test_project.verification.email_otp'
    FLEX_USER_OTP_SMS_FUNCTION = 'test_project.verification.sms_otp'

4. Apply database migrations::

    python mange.py migrate
