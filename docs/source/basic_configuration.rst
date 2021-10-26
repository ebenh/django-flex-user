Basic Configuration
===================

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
            'django_flex_user.backends.FlexUserModelBackend',
        ]

#. Configure :setting:`AUTH_USER_MODEL` in :mod:`settings.py`:

    .. code-block:: python

        AUTH_USER_MODEL = 'django_flex_user.FlexUser'

    .. warning::
        You cannot change the AUTH_USER_MODEL setting during the lifetime of a project (i.e. once you have made and
        migrated models that depend on it) without serious effort. It is intended to be set at the project start, and
        the model it refers to must be available in the first migration of the app that it lives in. See
        :ref:`auth-custom-user` for more details.

#. Register a callback function for sending emails in :mod:`settings.py`:

    .. code-block:: python

        FLEX_USER_OTP_EMAIL_FUNCTION = ...

    Your callback function should have the following signature:

    .. py:function:: email_otp(email_token, **kwargs)

        Send one-time password via email.

        :param email_token: The OTP token object.
        :type email_token: :class:`~django_flex_user.models.otp.EmailToken`
        :param kwargs: The named arguments passed to :meth:`~django_flex_user.models.otp.EmailToken.send_password`
        :type kwargs: dict, optional
        :raises TransmissionError: If email fails to send.
        :returns: None
        :rtype: None

#. Register a callback function for sending SMS messages in :mod:`settings.py`:

    .. code-block:: python

        FLEX_USER_OTP_SMS_FUNCTION = ...

    Your callback function should have the following signature:

    .. py:function:: sms_otp(phone_token, **kwargs)

        Send one-time password via SMS.

        :param email_token: The OTP token object.
        :type email_token: :class:`~django_flex_user.models.otp.PhoneToken`
        :param kwargs: The named arguments passed to :meth:`~django_flex_user.models.otp.PhoneToken.send_password`
        :type kwargs: dict, optional
        :raises TransmissionError: If SMS fails to send.
        :returns: None
        :rtype: None

#. Apply database migrations:

    .. code-block:: bash

        $ python mange.py migrate

    .. note::
        On Windows, the command to execute Python is ``py``.

#. Create a superuser:

    .. code-block:: bash

        $ python mange.py createsuperuser

    .. note::
        On Windows, the command to execute Python is ``py``.
