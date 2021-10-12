Overview
========

`django-flex-user` is a Django application designed to **maximize sign-up conversion**.

The main components of the Django application are as follows:

User Model
##########

We provide a replacement for Django's default user model.

Our user model enables users to sign up using a **username**, **email address**, **phone number**, or any combination
thereof.

OAuth
#####

We interoperate with `django-social-auth <https://pypi.org/project/django-social-auth/>`_ to enable users to sign up
using an OAuth provider like Facebook or Google.

One-Time Passwords
##################

We provide a common system for one-time passwords. One-time passwords are used to verify email addresses and phone
numbers, as well as to perform password resets.

REST API
########

In addition to conventional Python-Django APIs, we provide a REST API suitable for things like singe-page apps (SPAs).