from split_settings.tools import optional, include

include(
    'components/settings.py',
    'components/django_phonenumber_field.py',
    'components/django_flex_user.py',
    'components/djangorestframework.py',
    'components/drf_multiple_model.py',
    'components/social_auth_app_django.py',
    'components/sendgrid.py',
    optional('local_settings.py')
)
