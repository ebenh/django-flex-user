OAuth
=====

#. Configure :setting:`INSTALLED_APPS` in :mod:`settings.py`::

    INSTALLED_APPS = [
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'django_flex_user.apps.DjangoFlexUserConfig',
        ...
        'social_django', # Add me
    ]

#. Configure :setting:`MIDDLEWARE` in :mod:`settings.py`::

    MIDDLEWARE = [
        'social_django.middleware.SocialAuthExceptionMiddleware', # Add me
        ...
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ]

#. Configure :setting:`TEMPLATES-OPTIONS` in :mod:`settings.py`::

    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [],
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    'django.template.context_processors.debug',
                    'django.template.context_processors.request',
                    'django.contrib.auth.context_processors.auth',
                    'django.contrib.messages.context_processors.messages',
                    ...
                    'social_django.context_processors.backends', # Add me
                    'social_django.context_processors.login_redirect', # Add me
                ],
            },
        },
    ]

#. Configure :setting:`AUTHENTICATION_BACKENDS` in :mod:`settings.py`::

    AUTHENTICATION_BACKENDS = [
        'django_flex_user.backends.FlexUserModelBackend',
        ...
        'django_flex_user.backends.FlexUserFacebookOAuth2', # Add me
        'django_flex_user.backends.FlexUserGoogleOAuth2', # Add me
    ]
