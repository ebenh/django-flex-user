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
        ('validEmail@xn--bcher-kva.com', 'va********@xn***********.***'),
    )

    def test_obscure_email(self):
        from django_flex_user.util import obscure_email

        for email, email_obscured in self._emails:
            with self.subTest(email):
                self.assertEqual(obscure_email(email), email_obscured)

    def test_obscure_phone_us_number(self):
        import phonenumbers

        phone = phonenumbers.parse('+1 202-555-1234')

        data = (
            ('E164', phonenumbers.PhoneNumberFormat.E164, '+*********34'),
            ('INTERNATIONAL', phonenumbers.PhoneNumberFormat.INTERNATIONAL, '+* ***-***-**34'),
            ('NATIONAL', phonenumbers.PhoneNumberFormat.NATIONAL, '(***) ***-**34'),
            ('RFC3966', phonenumbers.PhoneNumberFormat.RFC3966, 'tel:+*-***-***-**34')
        )

        for test_name, output_format, expected_output in data:
            with self.subTest(test_name):
                from django_flex_user.util import obscure_phone

                self.assertEqual(obscure_phone(phone, output_format), expected_output)

    def test_obscure_phone_et_number(self):
        import phonenumbers

        phone = phonenumbers.parse('+251 91 123 4567')

        data = (
            ('E164', phonenumbers.PhoneNumberFormat.E164, '+**********67'),
            ('INTERNATIONAL', phonenumbers.PhoneNumberFormat.INTERNATIONAL, '+*** ** *** **67'),
            ('NATIONAL', phonenumbers.PhoneNumberFormat.NATIONAL, '*** *** **67'),
            ('RFC3966', phonenumbers.PhoneNumberFormat.RFC3966, 'tel:+***-**-***-**67')
        )

        for test_name, output_format, expected_output in data:
            with self.subTest(test_name):
                from django_flex_user.util import obscure_phone

                self.assertEqual(obscure_phone(phone, output_format), expected_output)

    def test_obscure_phone_gb_number_with_extension(self):
        import phonenumbers

        phone = phonenumbers.parse('+44 7400 123456 x123')

        data = (
            ('E164', phonenumbers.PhoneNumberFormat.E164, '+**********56'),
            ('INTERNATIONAL', phonenumbers.PhoneNumberFormat.INTERNATIONAL, '+** **** ****56 x123'),
            ('NATIONAL', phonenumbers.PhoneNumberFormat.NATIONAL, '***** ****56 x123'),
            ('RFC3966', phonenumbers.PhoneNumberFormat.RFC3966, 'tel:+**-****-****56;ext=123')
        )

        for test_name, output_format, expected_output in data:
            with self.subTest(test_name):
                from django_flex_user.util import obscure_phone

                self.assertEqual(obscure_phone(phone, output_format), expected_output)

    def test_obscure_phone_alphanumeric_vanity_number(self):
        import phonenumbers

        phone = phonenumbers.parse('+1 800-six-flag')

        data = (
            ('E164', phonenumbers.PhoneNumberFormat.E164, '+*********24'),
            ('INTERNATIONAL', phonenumbers.PhoneNumberFormat.INTERNATIONAL, '+* ***-***-**24'),
            ('NATIONAL', phonenumbers.PhoneNumberFormat.NATIONAL, '(***) ***-**24'),
            ('RFC3966', phonenumbers.PhoneNumberFormat.RFC3966, 'tel:+*-***-***-**24')
        )

        for test_name, output_format, expected_output in data:
            with self.subTest(test_name):
                from django_flex_user.util import obscure_phone

                self.assertEqual(obscure_phone(phone, output_format), expected_output)

    def test_obscure_invalid_number(self):
        import phonenumbers
        from django_flex_user.util import obscure_phone

        phone = phonenumbers.parse('+251 191 123 4567')

        self.assertRaises(ValueError, obscure_phone, phone)