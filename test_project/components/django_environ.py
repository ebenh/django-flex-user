#
# Configure django-environ
#

from test_project.components import BASE_DIR
from pathlib import Path
import environ

env = environ.Env()

# Read environment variables from .env file (this is part of django-environ config)
environ.Env.read_env(Path(BASE_DIR).joinpath('.env'))
