Installation
============

#. Install :mod:`django_flex_user` from the Python Package Index (PyPi):

    .. code-block:: console

        $ pip install django-flex-user

#. Configure :setting:`INSTALLED_APPS` in :mod:`settings.py`:

    .. code-block:: python
        :emphasize-lines: 9-13

        INSTALLED_APPS = [
            'django.contrib.admin',
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.messages',
            'django.contrib.staticfiles',
            ...
            'django_flex_user.apps.DjangoFlexUserConfig', # Add me
            'rest_framework', # Add me
            'rest_framework.authtoken', # Add me
            'drf_multiple_model', # Add me
            'social_django', # Add me
        ]

#. Configure :setting:`AUTHENTICATION_BACKENDS` in :mod:`settings.py`:

    .. code-block:: python

        AUTHENTICATION_BACKENDS = [
            'django_flex_user.backends.FlexUserModelBackend', # Add me
        ]

#. Configure :setting:`AUTH_USER_MODEL` in :mod:`settings.py`:

    .. code-block:: python

        AUTH_USER_MODEL = 'django_flex_user.FlexUser'

#. Configure email callback in :mod:`settings.py`:

    .. code-block:: python

        FLEX_USER_OTP_EMAIL_FUNCTION = ...

    Your callback function should have the following signature:

    .. py:function:: email_otp(email_token, **kwargs)

        Sends one-time password via email.

        :param email_token: The OTP token object.
        :type email_token: :class:`~django_flex_user.models.otp.EmailToken`
        :param kwargs: The named arguments passed to :meth:`~django_flex_user.models.otp.EmailToken.send_password`
        :type kwargs: dict, optional
        :raises TransmissionError: If email fails to send.
        :returns: None
        :rtype: None

#. Configure SMS callback in :mod:`settings.py`:

    .. code-block:: python

        FLEX_USER_OTP_SMS_FUNCTION = ...

    Your callback function should have the following signature:

    .. py:function:: sms_otp(phone_token, **kwargs)

        Sends one-time password via SMS.

        :param email_token: The OTP token object.
        :type email_token: :class:`~django_flex_user.models.otp.PhoneToken`
        :param kwargs: The named arguments passed to :meth:`~django_flex_user.models.otp.PhoneToken.send_password`
        :type kwargs: dict, optional
        :raises TransmissionError: If SMS fails to send.
        :returns: None
        :rtype: None

#. Apply database migrations:

    .. code-block:: console

        $ python mange.py migrate
