from django.core.validators import RegexValidator
from django.utils.deconstruct import deconstructible
from django.utils.functional import SimpleLazyObject
from django.utils.translation import gettext_lazy as _

import regex as re


def _lazy_re_compile(regex, flags=0):
    """Lazily compile a regex with flags."""

    def _compile():
        # Compile the regex if it was not passed pre-compiled.
        if isinstance(regex, str):
            return re.compile(regex, flags)
        else:
            assert not flags, "flags must be empty if regex is passed pre-compiled"
            return regex

    return SimpleLazyObject(_compile)


@deconstructible
class MyRegexValidator(RegexValidator):
    def __init__(self, regex=None, message=None, code=None, inverse_match=None, flags=None):
        if regex is not None:
            self.regex = regex
        if message is not None:
            self.message = message
        if code is not None:
            self.code = code
        if inverse_match is not None:
            self.inverse_match = inverse_match
        if flags is not None:
            self.flags = flags
        if self.flags and not isinstance(self.regex, str):
            raise TypeError("If the flags are set, regex must be a regular expression string.")

        self.regex = _lazy_re_compile(self.regex, self.flags)


@deconstructible()
class FlexUserUnicodeUsernameValidator(MyRegexValidator):
    """
    Our implementation of django.contrib.auth.validators.UnicodeUsernameValidator.

    In order to not create ambiguity with email addresses and phone numbers, the following key constraints are applied:

    - A username may not begin with a decimal number
    - A username may not begin with a "+"
    - A username may not contain "@"

    see: https://www.compart.com/en/unicode/category
    """
    regex = r'^[\p{L}\p{Mn}\p{Mc}\p{Nl}\p{No}][\p{L}\p{Mn}\p{Mc}\p{N}._-]*$'
    message = _(
        'Enter a valid username. This value must begin with a letter and may contain only letters, numbers, '
        'and ./-/_ characters.'
    )
    flags = 0


NO_SPECIAL_REGEX = re.compile(r'[^\w.-]+', re.UNICODE)


def clean_username(value):
    """
    Our clean username function for social-auth-app-django. Cleans input username by removing unsupported characters.

    See SOCIAL_AUTH_CLEAN_USERNAME_FUNCTION.

    :param value:
    :return:
    """
    value = NO_SPECIAL_REGEX.sub('', value)
    return value
