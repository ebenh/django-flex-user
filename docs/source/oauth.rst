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

#. Configure SOCIAL_AUTH_CLEAN_USERNAME_FUNCTION::

    SOCIAL_AUTH_CLEAN_USERNAME_FUNCTION = 'django_flex_user.validators.flex_user_clean_username'

#. Configure your redirect URLs::

    SOCIAL_AUTH_LOGIN_REDIRECT_URL = ...
    SOCIAL_AUTH_LOGIN_ERROR_URL = ...
    SOCIAL_AUTH_LOGIN_URL = ...
    SOCIAL_AUTH_NEW_USER_REDIRECT_URL = ...
    SOCIAL_AUTH_NEW_ASSOCIATION_REDIRECT_URL = ...
    SOCIAL_AUTH_DISCONNECT_REDIRECT_URL = ...
    SOCIAL_AUTH_INACTIVE_USER_URL = ...

#. Configure the Facebook API::

    SOCIAL_AUTH_FACEBOOK_KEY = ...  # App ID
    SOCIAL_AUTH_FACEBOOK_SECRET = ...  # App Secret

    SOCIAL_AUTH_FACEBOOK_SCOPE = ['email', ]
    SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {
        'fields': 'id, name, email, picture',
    }
    SOCIAL_AUTH_FACEBOOK_EXTRA_DATA = [
        ('name', 'name', True),
        ('email', 'email', True)
    ]

#. Configure the Google API::

    SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = ...  # client_id
    SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = ...  # client_secret

    SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = [
        'https://www.googleapis.com/auth/userinfo.email',
        'https://www.googleapis.com/auth/userinfo.profile',
    ]
    SOCIAL_AUTH_GOOGLE_OAUTH2_EXTRA_DATA = [
        ('name', 'name', True),
        ('email', 'email', True)
    ]

#. Configure SOCIAL_AUTH_PIPELINE::

    # Pipeline configuration
    SOCIAL_AUTH_PIPELINE = (
        # Get the information we can about the user and return it in a simple
        # format to create the user instance later. On some cases the details are
        # already part of the auth response from the provider, but sometimes this
        # could hit a provider API.
        'social_core.pipeline.social_auth.social_details',

        # Get the social uid from whichever service we're authing thru. The uid is
        # the unique identifier of the given user in the provider.
        'social_core.pipeline.social_auth.social_uid',

        # Verifies that the current auth process is valid within the current
        # project, this is where emails and domains whitelists are applied (if
        # defined).
        'social_core.pipeline.social_auth.auth_allowed',

        # Checks if the current social-account is already associated in the site.
        'social_core.pipeline.social_auth.social_user',

        # Make up a username for this person, appends a random string at the end if
        # there's any collision.
        'social_core.pipeline.user.get_username',

        # Send a validation email to the user to verify its email address.
        # 'social_core.pipeline.mail.mail_validation',
        'django_flex_user.verification.mail_validation',

        # Associates the current social details with another user account with
        # a similar email address.
        'social_core.pipeline.social_auth.associate_by_email',

        # Create a user account if we haven't found one yet.
        'social_core.pipeline.user.create_user',

        # Create the record that associated the social account with this user.
        'social_core.pipeline.social_auth.associate_user',

        # Populate the extra_data field in the social record with the values
        # specified by settings (and the default ones like access_token, etc).
        'social_core.pipeline.social_auth.load_extra_data',

        # Update the user record with any changed info from the auth service.
        'social_core.pipeline.user.user_details'  # todo: disable this step
    )

#. Configure email validation::

    SOCIAL_AUTH_EMAIL_VALIDATION_URL = ...
    SOCIAL_AUTH_EMAIL_VALIDATION_FUNCTION = ...
    SOCIAL_AUTH_FACEBOOK_FORCE_EMAIL_VALIDATION = True
