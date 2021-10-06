#
# Configure djangorestframework
#

from test_project.components.settings import INSTALLED_APPS

INSTALLED_APPS += (
    'rest_framework',
    'rest_framework.authtoken',
)
