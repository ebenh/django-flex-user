from django.test import TestCase


# "A valid vanity number will start with at least 3 digits and will have three or more alpha characters."
# https://github.com/google/libphonenumber/blob/a395b4fef3caf57c4bc5f082e1152a4d2bd0ba4c/cpp/src/phonenumbers/phonenumberutil.h

# Examples of various alpha-numeric (i.e. vanity) numbers accepted by libphonenumber
# https://github.com/google/libphonenumber/blob/master/java/libphonenumber/test/com/google/i18n/phonenumbers/PhoneNumberUtilTest.java

# Regex libphonenumber uses to match phone numbers:
#   kDigits[] = "\\p{Nd}";
#   kValidAlpha[] = "a-z";
# https://github.com/google/libphonenumber/blob/f52af239997c35335894206a4a45f44558ee71a0/cpp/src/phonenumbers/phonenumberutil.cc

# "Why does the library treat some non-digit characters as digits?"
# https://github.com/google/libphonenumber/blob/master/FAQ.md

# "Falsehoods Programmers Believe About Phone Numbers":
# https://github.com/google/libphonenumber/blob/272b7f1866fbea072dbe6ad2865aca5393fc0eb5/FALSEHOODS.md

class TestUsernameValidator(TestCase):
    _valid_usernames = [
        # Separators
        'valid.username',  # Period
        'valid-username',  # Dash
        'valid_username',  # Underscore

        # Character ranges
        'validUsername',  # ASCII
        'validUsérname',  # ASCII Latin-1 character "é" (U+00e9)
        'validUsérname',  # ASCII character with Unicode combining mark "é" (U+0065 U+0301)
        'ትክክለኛ-የተጠቃሚ-ስም',  # Unicode non-Latin characters

        # Numbers

        # Non-decimal number in first position
        'ⅠvalidUsername',  # Unicode category "Letter Number", Roman Numeral One
        '፩validUsername',  # Unicode category "Other Number", Ethiopic Digit One

        # Number not in first position
        'validUsername0',  # Unicode category "Decimal Number", Digit Zero
        'validUsername０',  # Unicode category "Decimal Number", Fullwidth Digit Zero
        'validUsername٠',  # Unicode category "Decimal Number", Arabic-Indic Digit Zero
        'validUsernameⅠ',  # Unicode category "Letter Number", Roman Numeral One
        'validUsername፩',  # Unicode category "Other Number", Ethiopic Digit One
    ]

    _invalid_usernames = [
        # Separators

        # Separator in first position
        ' invalidUsername',  # Space
        '.invalidUsername',  # Period
        '-invalidUsername',  # Dash
        '_invalidUsername',  # Underscore

        # Separator not in first position
        'invalid Username',  # Space

        # Character ranges

        'validUsername@example'
        'validUsername@example.com',
        '+invalidUsername',

        # Number

        # Decimal number in first position
        '0invalidUsername',  # Unicode category "Decimal Number", Digit Zero
        '０invalidUsername',  # Unicode category "Decimal Number", Fullwidth Digit Zero
        '٠invalidUsername',  # Unicode category "Decimal Number", Arabic-Indic Digit Zero

        # US phone number
        '2025551234',
        '(202)555-1234',  # National format
        '+12025551234',  # E164 format
        '+1202-555-1234',  # International format
        '1(202)555-1234',  # Out-of-country format from US
        '001202-555-1234',  # Out-of-country format from CH

        # ET phone Number
        '0911234567',  # National format
        '+251911234567',  # E164 format
        '+251911234567',  # International format
        '011251911234567',  # Out-of-country format from US
        '00251911234567',  # Out-of-country format from CH

        # GB phone number with extension
        '07400123456x123',  # National format
        '+447400123456',  # E164 format
        '+447400123456x123',  # International format
        '011447400123456 x123',  # Out-of-country format from US
        '00447400123456x123',  # Out-of-country format from CH

        # Alpha-numeric/vanity phone number
        '800sixflag',
        '(800)six-flag',  # National format
        '+18007493524',  # E164 format
        '+1800-six-flag',  # International format
        '1(800)six-flag',  # Out-of-country format from US
        '001800-six-flag',  # Out-of-country format from CH
    ]

    def test_valid_usernames(self):
        from django_flex_user.validators import FlexUserUnicodeUsernameValidator

        username_validator = FlexUserUnicodeUsernameValidator()

        for username in self._valid_usernames:
            with self.subTest(username):
                username_validator(username)

    def test_invalid_usernames(self):
        from django_flex_user.validators import FlexUserUnicodeUsernameValidator
        from django.core.exceptions import ValidationError

        username_validator = FlexUserUnicodeUsernameValidator()

        for username in self._invalid_usernames:
            with self.subTest(username):
                self.assertRaises(ValidationError, username_validator, username)
