#
# Configure django-environ
#

from test_project.components import BASE_DIR
from pathlib import Path
import environ

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False),
    SECRET_KEY=(str, 'django-insecure-fyxp5o2zx)=)ou64*)ndz+y9vksix$bq&d!jmnste*p+1w%!*_'),
)

# Read environment variables from .env file (this is part of django-environ config)
environ.Env.read_env(Path(BASE_DIR).joinpath('.env'))
