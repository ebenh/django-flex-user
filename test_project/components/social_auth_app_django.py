#
# Configure social-auth-app-django
#

from test_project.components.settings import env
from test_project.components.settings import INSTALLED_APPS, MIDDLEWARE, TEMPLATES

INSTALLED_APPS += (
    'social_django',
)

MIDDLEWARE = ['social_django.middleware.SocialAuthExceptionMiddleware'] + MIDDLEWARE

TEMPLATES[0]['OPTIONS']['context_processors'] += [
    'social_django.context_processors.backends',
    'social_django.context_processors.login_redirect'
]

# Description of the various settings here:
# https://python-social-auth.readthedocs.io/en/latest/configuration/settings.html

# URLs options
SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/'
SOCIAL_AUTH_LOGIN_ERROR_URL = '/'
SOCIAL_AUTH_LOGIN_URL = '/'
SOCIAL_AUTH_NEW_USER_REDIRECT_URL = '/'
SOCIAL_AUTH_NEW_ASSOCIATION_REDIRECT_URL = '/'
SOCIAL_AUTH_DISCONNECT_REDIRECT_URL = '/'
SOCIAL_AUTH_INACTIVE_USER_URL = '/'

# Facebook configuration
SOCIAL_AUTH_FACEBOOK_KEY = '1018453275609332'  # App ID
SOCIAL_AUTH_FACEBOOK_SECRET = env('SOCIAL_AUTH_FACEBOOK_SECRET')  # App Secret

SOCIAL_AUTH_FACEBOOK_SCOPE = ['email', ]  # It seems email scope is now included by default
SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {
    'fields': 'id, name, email, picture',
}
SOCIAL_AUTH_FACEBOOK_EXTRA_DATA = [
    ('name', 'name', True),
    ('email', 'email', True)
]

# Google configuration
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = '487495415273-m9e0fvsajl1oapfpt9pfcthh1qmbhvs0.apps.googleusercontent.com'  # client_id
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = env('SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET')  # client_secret

SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = [  # These scopes don't seem to be necessary
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
]
SOCIAL_AUTH_GOOGLE_OAUTH2_EXTRA_DATA = [
    ('name', 'name', True),
    ('email', 'email', True)
]

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

SOCIAL_AUTH_EMAIL_VALIDATION_URL = 'http://localhost:4200/verify/email/'
SOCIAL_AUTH_EMAIL_VALIDATION_FUNCTION = 'django_flex_user.verification.email_validation_link'
SOCIAL_AUTH_FACEBOOK_FORCE_EMAIL_VALIDATION = True

SOCIAL_AUTH_CLEAN_USERNAME_FUNCTION = 'django_flex_user.validators.flex_user_clean_username'
