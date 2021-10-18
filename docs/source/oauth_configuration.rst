OAuth Configuration
===================

OAuth functionality (e.g. sign up using Facebook) is enabled by third-party module :mod:`social_django`.

Below are just the steps needed to make :mod:`social_django` compatible with :mod:`django_flex_user`. For a complete
configuration example refer to the :doc:`reference_project`.

For instructions on how to configure :mod:`social_django`, refer to its documentation
`here <https://python-social-auth.readthedocs.io/en/latest/configuration/django.html>`_

#. Configure :setting:`AUTHENTICATION_BACKENDS` in :mod:`settings.py`:

    .. code-block:: python
        :emphasize-lines: 4-5

        AUTHENTICATION_BACKENDS = [
            'django_flex_user.backends.FlexUserModelBackend',
            ...
            'django_flex_user.backends.FlexUserFacebookOAuth2', # Add me
            'django_flex_user.backends.FlexUserGoogleOAuth2', # Add me
        ]

    .. note::
        At present, the only OAuth providers :mod:`django_flex_user` provides built-in support for are Facebook and
        Google.

        If you want to add support for additional OAuth providers, extend the corresponding backend in
        :mod:`social_core.backends` and override its :meth:`get_user_details` method. (See
        :class:`django_flex_user.backends.FlexUserFacebookOAuth2` for an implementation example.)

        Once done, append the new class to :setting:`AUTHENTICATION_BACKENDS`.

#. Configure ``SOCIAL_AUTH_CLEAN_USERNAME_FUNCTION`` in :mod:`settings.py`:

    .. code-block:: python

        SOCIAL_AUTH_CLEAN_USERNAME_FUNCTION = 'django_flex_user.validators.flex_user_clean_username'

#. Configure ``SOCIAL_AUTH_PIPELINE`` in :mod:`settings.py`:

    .. code-block:: python
        :linenos:

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
            'social_core.pipeline.user.user_details'
        )

    .. note::
        On line 26 we introduce a custom pipeline function.

#. Configure email validation in :mod:`settings.py`:

    .. code-block:: python

        SOCIAL_AUTH_EMAIL_VALIDATION_URL = ...
        SOCIAL_AUTH_EMAIL_VALIDATION_FUNCTION = ...
        SOCIAL_AUTH_FACEBOOK_FORCE_EMAIL_VALIDATION = True
