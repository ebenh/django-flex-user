Basic Usage
===========

Create User
-----------
::

    from django.contrib.auth import get_user_model

    user = get_user_model().objects.create_user(...)

.. automethod:: django_flex_user.models.user.FlexUserManager.create_user

Create Super User
-----------------
::

    from django.contrib.auth import get_user_model

    user = get_user_model().objects.create_superuser(...)

.. automethod:: django_flex_user.models.user.FlexUserManager.create_superuser

Authenticate User
-----------------
To authenticate a user call :func:`django.contrib.auth.authenticate`.

It takes credentials as keyword arguments and checks them against each authentication backend in
:setting:`AUTHENTICATION_BACKENDS`. If the credentials are valid for a backend, it returns a \
:class:`~django_flex_user.models.user.FlexUser` object. If the credentials arent valid for any backend or if a backend
raises :class:`~django.core.exceptions.PermissionDenied`, it returns None.

For example::

    from django.contrib.auth import authenticate

    user = authenticate(email='alice@example.com', password='password')

    if user is not None:
        # A backend authenticated the credentials
    else:
        # No backend authenticated the credentials

.. automethod:: django.contrib.auth.authenticate

One-time Passwords (OTP)
------------------------

One-time passwords are based around the concept of a
`security token <https://en.wikipedia.org/w/index.php?title=Security_token&oldid=1049342825>`_. A security token is a
piece of hardware or software which generates one-time passwords in conjunction with a server. One common security
token is `Google Authenticator <https://en.wikipedia.org/w/index.php?title=Google_Authenticator&oldid=1049479885>`_, a
software application which runs on mobile platforms.

An email address or phone number can also act as a security token by generating a random password on the server and
sending it to the email address or phone number respectively. :mod:`django_flex_user` implements
:class:`~django_flex_user.models.otp.EmailToken` and :class:`~django_flex_user.models.otp.PhoneToken` which does just
this.

These modules are used to verify email addresses and phone numbers, as well as to authorize password resets.

EmailToken
++++++++++
Generate One-Time Password
##########################
::

    from django.contrib.auth import get_user_model

    # Create a user with an email address, an EmailToken object will be created for them automatically
    user = get_user_model().objects.create_user(email='alice@example.com', password='password')

    # Get the user's security token
    email_token = user.emailtoken_set.first()
    # Generate a one-time password
    email_token.generate_password()
    # Email the one-time password to alice@example.com
    email_token.send_password()

Check One-Time Password
#######################
::

    from django_flex_user.models.otp import EmailToken, TimeoutError

    ...

    # Get the security token
    email_token = EmailToken.objects.get(id=id)

    try:
        success = email_token.check_password(...)
    except TimeoutError:
        # There have been too many check_password() attempts
    else:
        if success:
            # The password is correct
        else:
            # The password is incorrect or has expired

.. automethod:: django_flex_user.models.otp.EmailToken.check_password

PhoneToken
++++++++++
Generate One-Time Password
##########################
::

    from django.contrib.auth import get_user_model

    # Create a user with a phone number, a PhoneToken object will be created for them automatically
    user = get_user_model().objects.create_user(phone='+12025551234', password='password')

    # Get the user's security token
    phone_token = user.phonetoken_set.first()
    # Generate a one-time password
    phone_token.generate_password()
    # Send the one-time password to +12025551234 via SMS
    phone_token.send_password()

Check One-Time Password
#######################
::

    from django_flex_user.models.otp import PhoneToken, TimeoutError

    ...

    # Get the security token
    phone_token = PhoneToken.objects.get(id=id)

    try:
        success = phone_token.check_password(...)
    except TimeoutError:
        # There have been too many check_password() attempts
    else:
        if success:
            # The password is correct
        else:
            # The password is incorrect or has expired

.. automethod:: django_flex_user.models.otp.PhoneToken.check_password