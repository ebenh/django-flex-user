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


Authenticating a user
---------------------
.. automethod::  django_flex_user.backends.FlexUserModelBackend.authenticate

One-time passwords
------------------
Email
+++++
Generate a one-time password
############################
::

    from django_flex_user.models.otp import EmailToken

    email_token = EmailToken.objects.get(user=user)
    email_token.generate_password()
    email_token.send_password()

Check one-time password
#######################
::

    from django_flex_user.models.otp import EmailToken, TimeoutError

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

    from django_flex_user.models.otp import PhoneToken

    phone_token = PhoneToken.objects.get(user=user)
    phone_token.generate_password()
    phone_token.send_password()

Check one-time password
#######################
::

    from django_flex_user.models.otp import PhoneToken, TimeoutError

    phone_token = PhoneToken.objects.get(user=user)

    try:
        success = phone_token.check_password(...)
    except TimeoutError:
        ...
    else:
        if success:
            ...
