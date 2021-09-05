from django.test import TestCase


class TestUtil(TestCase):
    _emails = (
        # Empty
        (None, ''),
        ('', ''),

        # User part
        ('a@example.com', '*@ex*****.***'),
        ('ab@example.com', 'a*@ex*****.***'),
        ('abc@example.com', 'a**@ex*****.***'),
        ('abcd@example.com', 'ab**@ex*****.***'),

        # Host part with first-level domain
        ('example@a.com', 'ex*****@*.***'),
        ('example@ab.com', 'ex*****@a*.***'),
        ('example@abc.com', 'ex*****@a**.***'),
        ('example@abcd.com', 'ex*****@ab**.***'),

        # Host part with subdomain
        ('example@a.example.com', 'ex*****@*.ex*****.***'),
        ('example@ab.example.com', 'ex*****@a*.ex*****.***'),
        ('example@abc.example.com', 'ex*****@a**.ex*****.***'),
        ('example@abcd.example.com', 'ex*****@ab**.ex*****.***'),

        # Host part with second-level domain
        ('example@example.co.za', 'ex*****@ex*****.**.**'),
        ('example@example.org.uk', 'ex*****@ex*****.***.**'),
        ('example@example.gc.ca', 'ex*****@ex*****.**.**'),

        # Unicode
        ('validEmail@bücher.com', 'va********@bü****.***'),
        ('validEmail@xn--bcher-kva.com', 'va********@bü****.***'),
    )

    _phones = (
        # Empty
        (None, ''),
        ('', ''),

        # US phone number
        ('2025551234', '********34'),
        ('(202)555-1234', '(***)***-**34'),  # National format
        ('+12025551234', '+*********34'),  # E164 format
        ('+1202-555-1234', '+****-***-**34'),  # International format
        ('1(202)555-1234', '*(***)***-**34'),  # Out-of-country format from US
        ('001202-555-1234', '******-***-**34'),  # Out-of-country format from CH

        # ET phone Number
        ('0911234567', '********67'),  # National format
        ('+251911234567', '+**********67'),  # E164 format
        ('+251911234567', '+**********67'),  # International format
        ('011251911234567', '*************67'),  # Out-of-country format from US
        ('00251911234567', '************67'),  # Out-of-country format from CH

        # GB phone number with extension
        ('07400123456x123', '*********56x123'),  # National format
        ('+447400123456', '+**********56'),  # E164 format
        ('+447400123456x123', '+**********56x123'),  # International format
        ('011447400123456 x123', '*************56'),  # Out-of-country format from US
        ('00447400123456x123', '************56x123'),  # Out-of-country format from CH

        # Alpha-numeric/vanity phone number
        ('800sixflag', '********ag'),
        ('(800)six-flag', '(***)***-**ag'),  # National format
        ('+18007493524', '+*********24'),  # E164 format
        ('+1800-six-flag', '+****-***-**ag'),  # International format
        ('1(800)six-flag', '*(***)***-**ag'),  # Out-of-country format from US
        ('001800-six-flag', '******-***-**ag'),  # Out-of-country format from CH
    )

    def test_obscure_email(self):
        from django_flex_user.util import obscure_email

        for email, email_obscured in self._emails:
            with self.subTest(email):
                self.assertEqual(obscure_email(email), email_obscured)

    def test_obscure_phone(self):
        from django_flex_user.util import obscure_phone

        for phone, phone_obscured in self._phones:
            with self.subTest(phone):
                self.assertEqual(obscure_phone(phone), phone_obscured)
