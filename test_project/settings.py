"""
Django settings for test_project project.

Generated by 'django-admin startproject' using Django 3.2.6.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-fyxp5o2zx)=)ou64*)ndz+y9vksix$bq&d!jmnste*p+1w%!*_'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    'rest_framework',  # djangorestframework
    'rest_framework.authtoken',  # djangorestframework
    'social_django',  # social-auth-app-django
    'django_otp',  # django-otp
    'django_otp.plugins.otp_email',  # django-otp
    'django_flex_user.apps.DjangoFlexUserConfig',  # django-flex-user
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'social_django.middleware.SocialAuthExceptionMiddleware',  # social-auth-app-django
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_otp.middleware.OTPMiddleware',  # django-otp
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'test_project.urls'

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
                'social_django.context_processors.backends',  # social-auth-app-django
                'social_django.context_processors.login_redirect',  # social-auth-app-django
            ],
        },
    },
]

WSGI_APPLICATION = 'test_project.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    # Added UserAttributeSimilarityValidator
    # todo: add phone_number to user_attributes
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
        'OPTIONS': {
            'user_attributes': ('username', 'email'),
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Tell Django to use our new user model

AUTH_USER_MODEL = 'django_flex_user.SPUser'

# Tell Django to use our authentication backend

AUTHENTICATION_BACKENDS = [
    'django_flex_user.backends.SPModelBackend',
    'django_flex_user.backends.SPFacebookOAuth2',
    'django_flex_user.backends.SPGoogleOAuth2',
]  # default: ['django.contrib.auth.backends.ModelBackend',]

# Tell Django to use our login template

LOGIN_URL = '/account/log-in/'

# Configure django-phonenumber-field

PHONENUMBER_DEFAULT_REGION = 'US'

# Configure social-auth-app-django

# SOCIAL_AUTH_POSTGRES_JSONFIELD = True  # social-auth-app-django ... deprecated
# SOCIAL_AUTH_JSONFIELD_ENABLED = True  # social-auth-app-django ... todo: enable this when using pgsql
# SOCIAL_AUTH_URL_NAMESPACE = 'social'  # social-auth-app-django

SOCIAL_AUTH_ALLOWED_REDIRECT_HOSTS = ['localhost:4200', 'cnn.com', 'yahoo.com',
                                      'cbc.ca']  # note eben: no need to include 'localhost:8000', it's added implicitly

SOCIAL_AUTH_NEW_USER_REDIRECT_URL = 'http://localhost:4200/sign-in/oauth/complete/'
SOCIAL_AUTH_NEW_ASSOCIATION_REDIRECT_URL = 'http://localhost:4200/sign-in/oauth/complete/'
SOCIAL_AUTH_LOGIN_REDIRECT_URL = 'http://localhost:4200/sign-in/oauth/complete/'
SOCIAL_AUTH_LOGIN_ERROR_URL = 'http://localhost:4200/sign-in/oauth/complete/'
SOCIAL_AUTH_DISCONNECT_REDIRECT_URL = 'http://localhost:4200/account/'

# Facebook configuration
SOCIAL_AUTH_FACEBOOK_KEY = '222626885799264'  # App ID
SOCIAL_AUTH_FACEBOOK_SECRET = '148d517f78170127b46167a87c878848'  # App Secret

SOCIAL_AUTH_FACEBOOK_SCOPE = ['email', ]  # It seems email scope is now included by default
SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {
    'fields': 'id, name, email, picture',
}
SOCIAL_AUTH_FACEBOOK_EXTRA_DATA = [
    ('name', 'name', True),
    ('email', 'email', True)
]

# Google configuration
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = '87036211763-394ep44eajp4i8b0347fl44lgpdc0c44.apps.googleusercontent.com'  # client_id
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = 'SPhA2RPJ1GXQrM8LqIPj02dn'  # client_secret

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
    'account.verification.mail_validation',

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
SOCIAL_AUTH_EMAIL_VALIDATION_FUNCTION = 'account.verification.email_validation_link'
SOCIAL_AUTH_FACEBOOK_FORCE_EMAIL_VALIDATION = True

SOCIAL_AUTH_CLEAN_USERNAME_FUNCTION = 'account.validators.clean_username'