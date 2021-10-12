Installation
============

1. Install :mod:`django_flex_user` from the Python Package Index (PyPi)::

    pip install django-flex-user

2. Configure :setting:`INSTALLED_APPS`::

    INSTALLED_APPS += (
        'django_flex_user.apps.DjangoFlexUserConfig',
    )

3. Configure :setting:`AUTHENTICATION_BACKENDS`::

    AUTHENTICATION_BACKENDS += (
        'django_flex_user.backends.FlexUserModelBackend',
    )

4. Configure :setting:`AUTH_USER_MODEL`::

    AUTH_USER_MODEL = 'django_flex_user.FlexUser'

5. Register callbacks::

    FLEX_USER_OTP_EMAIL_FUNCTION = 'test_project.verification.email_otp'
    FLEX_USER_OTP_SMS_FUNCTION = 'test_project.verification.sms_otp'

4. Run :djadmin:`migrate`::

    python mange.py migrate django_flex_user
