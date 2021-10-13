Usage
=====

Creating a user
---------------
::

    from django_flex_user.models.user import FlexUser

    user = FlexUser.objects.create_user(...)

.. automethod:: django_flex_user.models.user.FlexUserManager.create_user

Creating a super user
---------------------
::

    from django_flex_user.models.user import FlexUser

    user = FlexUser.objects.create_superuser(...)

.. automethod:: django_flex_user.models.user.FlexUserManager.create_superuser

Authenticating a user
---------------------
To authenticate a user call :func:`django.contrib.auth.authenticate`.

It takes credentials as keyword arguments and checks them against each authentication backend in
:setting:`AUTHENTICATION_BACKENDS`. If the credentials are valid for a backend, it returns a \
:class:`~django_flex_user.models.user.FlexUser` object. If the credentials arent valid for any backend or if a backend
raises :class:`~django.core.exceptions.PermissionDenied`, it returns None.

For example::

    from django.contrib.auth import authenticate

    user = authenticate(...)

    if user is not None:
        # A backend authenticated the credentials
    else:
        # No backend authenticated the credentials

.. automethod:: django_flex_user.backends.FlexUserModelBackend.authenticate

One-time passwords
------------------
Email
+++++
Generate a one-time password
############################
::

    from django_flex_user.modes.user import FlexUser
    from django_flex_user.models.otp import EmailToken

    # Create a user with an email address, an EmailToken object will be created for them automatically
    user = FlexUser.objects.create_user(email='alice@example.com', password='password')

    email_token = EmailToken.objects.get(user=user)
    # Generate a one-time password
    email_token.generate_password()
    # Email the one-time password to alice@example.com
    email_token.send_password()

Check one-time password
#######################
::

    from django_flex_user.models.otp import EmailToken, TimeoutError

    ...

    email_token = EmailToken.objects.get(user=user)

    try:
        success = email_token.check_password(...)
    except TimeoutError:
        ...
    else:
        if success:
            ...

Phone
+++++
Generate a one-time password
############################
::

    from django_flex_user.modes.user import FlexUser
    from django_flex_user.models.otp import PhoneToken

    # Create a user with a phone number, a PhoneToken object will be created for them automatically
    user = FlexUser.objects.create_user(phone='+12025551234', password='password')

    phone_token = PhoneToken.objects.get(user=user)
    # Generate a one-time password
    phone_token.generate_password()
    # Send the one-time password to +12025551234 via SMS
    phone_token.send_password()

Check one-time password
#######################
::

    from django_flex_user.models.otp import PhoneToken, TimeoutError

    ...

    phone_token = PhoneToken.objects.get(user=user)

    try:
        success = phone_token.check_password(...)
    except TimeoutError:
        ...
    else:
        if success:
            ...
