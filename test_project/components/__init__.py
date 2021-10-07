from pathlib import Path

# When django-split-settings executes each settings file, it sets the __file__ variable to be
# "../django-flex-user/test_project/settings.py". Therefore, we need to set BASE_DIR outside that execution context so
# that the path will be interpreted correctly.

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent
