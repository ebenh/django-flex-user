Installation
============

1. Install :mod:`django_flex_user` from the Python Package Index (PyPi)::

    pip install django-flex-user

2. Configure :setting:`INSTALLED_APPS`::

    INSTALLED_APPS = [
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        ...
        'django_flex_user.apps.DjangoFlexUserConfig', # Add me
    ]

3. Configure :setting:`AUTHENTICATION_BACKENDS`::

    MIDDLEWARE = [
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
        ...
        'django_flex_user.backends.FlexUserModelBackend', # Add me
    ]

4. Configure :setting:`AUTH_USER_MODEL`::

    AUTH_USER_MODEL = 'django_flex_user.FlexUser'

5. Register callbacks::

    FLEX_USER_OTP_EMAIL_FUNCTION = ... # Your callback here
    FLEX_USER_OTP_SMS_FUNCTION = ... # Your callback here

4. Run :djadmin:`migrate`::

    python mange.py migrate django_flex_user
