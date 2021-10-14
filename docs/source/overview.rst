Overview
========

At a high level, the main components of :mod:`django_flex_user` are as follows:

User Model
##########

:class:`django_flex_user.models.user.FlexUser` is a replacement for Django's default user model.

It enables users to sign up using their choice of **username**, **email address**, **phone number**, or any combination
thereof.

OAuth
#####

Sign up using an OAuth (e.g. Facebook, Google) is enabled by third-party package
`django-social-auth <https://pypi.org/project/django-social-auth/>`_.  To lean how to use ``django-social-auth`` with
:mod:`django_flex_user`, refer to the section titled :doc:`oauth`.

One-Time Passwords
##################

:class:`django_flex_user.models.otp.EmailToken` and :class:`django_flex_user.models.otp.PhoneToken` enable email
addresses and phone number verification respectively, as well as password reset.

REST API
########

We provide a REST API suitable for applications like singe-page apps (SPAs).