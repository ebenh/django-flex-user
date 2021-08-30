from django.test import TestCase


class TestUserManager(TestCase):
    """
    This class is designed to test django_flex_user.models.SPUserManager
    """
    _username_values = [{},
                        {'username': None},
                        {'username': ''},
                        {'username': 'validUsername'},
                        {'username': 'invalidUsername+'}]

    _email_values = [{},
                     {'email': None},
                     {'email': ''},
                     {'email': 'validEmail@example.com'},
                     {'email': 'invalidEmail'}]

    _phone_number_values = [{},
                            {'phone_number': None},
                            {'phone_number': ''},
                            {'phone_number': '+12025551234'},
                            {'phone_number': 'invalidPhoneNumber'}]

    # note eben: Because django_flex_user.models.SPUserManager._create_user deliberately has no password constraints, there is no
    # such invalid password that we can test.
    _password_values = [{},
                        {'password': None},
                        {'password': ''},
                        {'password': 'validPassword'}]

    def test_create_user(self):
        self._test_create_user(superuser=False)

    def test_create_superuser(self):
        self._test_create_user(superuser=True)

    def _test_create_user(self, superuser):
        from django_flex_user.models import SPUser
        from django.db import transaction
        from freezegun import freeze_time

        create_user_method = SPUser.objects.create_user if not superuser else SPUser.objects.create_superuser

        for i in self._username_values:
            for j in self._email_values:
                for k in self._phone_number_values:
                    for l in self._password_values:

                        args = {}
                        args.update(i)
                        args.update(j)
                        args.update(k)
                        args.update(l)

                        with self.subTest(**args), transaction.atomic(), freeze_time():
                            from django.core.exceptions import ValidationError
                            from django.utils import timezone

                            if ('username' not in args or args['username'] is None) and \
                                    ('email' not in args or args['email'] is None) and \
                                    ('phone_number' not in args or args['phone_number'] is None):
                                """
                                If the supplied username, email, and phone_number are simultaneously undefined or None,
                                django_flex_user.models.SPUserManager._create_user should raise ValidationError.

                                At least one of username, email or phone_number must be defined and not None.
                                """
                                self.assertRaises(ValidationError, create_user_method, **args)
                            elif args.get('username') == '' or \
                                    args.get('email') == '' or \
                                    args.get('phone_number') == '':
                                """
                                If any of the supplied username, email or phone_number are the empty string
                                django_flex_user.models.SPUserManager._create_user should raise ValidationError.
                                """
                                self.assertRaises(ValidationError, create_user_method, **args)
                            elif (args.get('username') and 'invalid' in args['username']) or \
                                    (args.get('email') and 'invalid' in args['email']) or \
                                    (args.get('phone_number') and 'invalid' in args['phone_number']):
                                """
                                If any of the supplied username, email or phone_number are defined and invalid,
                                django_flex_user.models.SPUserManager._create_user should raise ValidationError.
                                """
                                self.assertRaises(ValidationError, create_user_method, **args)
                            else:
                                """
                                This case encompasses all possible permutations of supplied username, email,
                                phone_number and password for which django_flex_user.models.SPUserManager._create_user should
                                return a valid SPUser object.
                                """
                                user = create_user_method(**args)

                                self.assertIsNotNone(user)
                                self.assertIsNotNone(user.id)

                                self.assertEqual(user.username, args.get('username'))
                                self.assertEqual(user.email, args.get('email'))
                                self.assertEqual(user.phone_number, args.get('phone_number'))

                                self.assertTrue(user.password)
                                # If the supplied password is undefined or None, ensure that an unusable password is set
                                if args.get('password') is None:
                                    self.assertFalse(user.has_usable_password())
                                else:
                                    self.assertTrue(user.has_usable_password())

                                self.assertEqual(user.date_joined, timezone.now())
                                self.assertIsNone(user.last_login)
                                self.assertIs(user.is_active, True)

                                if not superuser:
                                    self.assertIs(user.is_superuser, False)
                                    self.assertIs(user.is_staff, False)
                                else:
                                    self.assertIs(user.is_superuser, True)
                                    self.assertIs(user.is_staff, True)

                            transaction.set_rollback(True)

    def test_create_user_username_case_insensitivity(self):
        from django_flex_user.models import SPUser
        from django.core.exceptions import ValidationError

        user = SPUser.objects.create_user(username='validUsername')
        # Ensure username was saved exactly as it was entered
        self.assertEqual(user.username, 'validUsername')

        self.assertRaises(ValidationError, SPUser.objects.create_user, username='VALIDUSERNAME')

    def test_create_superuser_username_case_insensitivity(self):
        from django_flex_user.models import SPUser
        from django.core.exceptions import ValidationError

        user = SPUser.objects.create_superuser(username='validUsername')
        # Ensure username was saved exactly as it was entered
        self.assertEqual(user.username, 'validUsername')

        self.assertRaises(ValidationError, SPUser.objects.create_superuser, username='VALIDUSERNAME')

    def test_create_user_duplicate_username(self):
        from django_flex_user.models import SPUser
        from django.core.exceptions import ValidationError

        SPUser.objects.create_user(username='validUsername')
        self.assertRaises(ValidationError, SPUser.objects.create_user, username='validUsername')

    def test_create_superuser_duplicate_username(self):
        from django_flex_user.models import SPUser
        from django.core.exceptions import ValidationError

        SPUser.objects.create_superuser(username='validUsername')
        self.assertRaises(ValidationError, SPUser.objects.create_superuser, username='validUsername')

    def test_create_user_duplicate_email(self):
        from django_flex_user.models import SPUser
        from django.core.exceptions import ValidationError

        SPUser.objects.create_user(email='validEmail@example.com')
        self.assertRaises(ValidationError, SPUser.objects.create_user, email='validEmail@example.com')

    def test_create_superuser_duplicate_email(self):
        from django_flex_user.models import SPUser
        from django.core.exceptions import ValidationError

        SPUser.objects.create_superuser(email='validEmail@example.com')
        self.assertRaises(ValidationError, SPUser.objects.create_superuser, email='validEmail@example.com')

    def test_create_user_duplicate_phone_number(self):
        from django_flex_user.models import SPUser
        from django.core.exceptions import ValidationError

        SPUser.objects.create_user(phone_number='+12025551234')
        self.assertRaises(ValidationError, SPUser.objects.create_user, phone_number='+12025551234')

    def test_create_superuser_duplicate_phone_number(self):
        from django_flex_user.models import SPUser
        from django.core.exceptions import ValidationError

        SPUser.objects.create_superuser(phone_number='+12025551234')
        self.assertRaises(ValidationError, SPUser.objects.create_superuser, phone_number='+12025551234')

    def test_create_user_ambiguous_username(self):
        """
        Verify that an email address or phone number cannot form a valid username.

        :return:
        """
        from django_flex_user.models import SPUser
        from django.core.exceptions import ValidationError

        self.assertRaises(ValidationError, SPUser.objects.create_user, username='validEmail@example.com')
        self.assertRaises(ValidationError, SPUser.objects.create_user, username='+12025551234')

    def test_create_superuser_ambiguous_username(self):
        """
        Verify that an email address or phone number cannot form a valid username.

        :return:
        """
        from django_flex_user.models import SPUser
        from django.core.exceptions import ValidationError

        self.assertRaises(ValidationError, SPUser.objects.create_superuser, username='validEmail@example.com')
        self.assertRaises(ValidationError, SPUser.objects.create_superuser, username='+12025551234')

    def test_create_user_ambiguous_email(self):
        """
        Verify that a username or phone number cannot form a valid email.

        :return:
        """
        from django_flex_user.models import SPUser
        from django.core.exceptions import ValidationError

        self.assertRaises(ValidationError, SPUser.objects.create_user, email='validUsername')
        self.assertRaises(ValidationError, SPUser.objects.create_user, email='+12025551234')

    def test_create_superuser_ambiguous_email(self):
        """
        Verify that a username or phone number cannot form a valid email.

        :return:
        """
        from django_flex_user.models import SPUser
        from django.core.exceptions import ValidationError

        self.assertRaises(ValidationError, SPUser.objects.create_superuser, email='validUsername')
        self.assertRaises(ValidationError, SPUser.objects.create_superuser, email='+12025551234')

    def test_create_user_ambiguous_phone_number(self):
        """
        Verify that a username or email address cannot form a valid phone_number.

        :return:
        """
        from django_flex_user.models import SPUser
        from django.core.exceptions import ValidationError

        self.assertRaises(ValidationError, SPUser.objects.create_user, phone_number='validUsername')
        self.assertRaises(ValidationError, SPUser.objects.create_user, phone_number='validEmail@example.com')

    def test_create_superuser_ambiguous_phone_number(self):
        """
        Verify that a username or email address cannot form a valid phone_number.

        :return:
        """
        from django_flex_user.models import SPUser
        from django.core.exceptions import ValidationError

        self.assertRaises(ValidationError, SPUser.objects.create_superuser, phone_number='validUsername')
        self.assertRaises(ValidationError, SPUser.objects.create_superuser, phone_number='validEmail@example.com')

    def test_create_user_normalize_username(self):
        from django_flex_user.models import SPUser

        nfd = 'validUsérname'  # é = U+0065 U+0301
        nfkc = 'validUsérname'  # é = U+00e9

        user = SPUser.objects.create_user(username=nfd)
        self.assertEqual(user.username, nfkc)

    def test_create_superuser_normalize_username(self):
        from django_flex_user.models import SPUser

        nfd = 'validUsérname'  # é = U+0065 U+0301
        nfkc = 'validUsérname'  # é = U+00e9

        user = SPUser.objects.create_superuser(username=nfd)
        self.assertEqual(user.username, nfkc)

    def test_create_user_normalize_email(self):
        from django_flex_user.models import SPUser

        user = SPUser.objects.create_user(email='validEmail@bücher.example')
        self.assertEqual(user.email, 'validEmail@xn--bcher-kva.example')

    def test_create_superuser_normalize_email(self):
        from django_flex_user.models import SPUser

        user = SPUser.objects.create_superuser(email='validEmail@bücher.example')
        self.assertEqual(user.email, 'validEmail@xn--bcher-kva.example')

    def test_normalize_email(self):
        from django_flex_user.models import SPUserManager

        email = SPUserManager.normalize_email(None)
        self.assertIs(email, None)

        email = SPUserManager.normalize_email('')
        self.assertEqual(email, '')

        email = SPUserManager.normalize_email('validEmail@example.com')
        self.assertEqual(email, 'validEmail@example.com')

        email = SPUserManager.normalize_email('validEmail@EXAMPLE.com')
        self.assertEqual(email, 'validEmail@example.com')

        email = SPUserManager.normalize_email('validEmail@bücher.example')
        self.assertEqual(email, 'validEmail@xn--bcher-kva.example')

        email = SPUserManager.normalize_email('validEmail@bÜcher.example')
        self.assertEqual(email, 'validEmail@xn--bcher-kva.example')

        email = SPUserManager.normalize_email('validEmail@xn--bcher-kva.example')
        self.assertEqual(email, 'validEmail@xn--bcher-kva.example')

        # Invalid IDNA encoding
        email = SPUserManager.normalize_email('invalidEmail@xn--123.example')
        self.assertEqual(email, 'invalidEmail@xn--123.example')

        # Homograph
        latin_a = 'validEmail@example.com'  # Latin "a" in domain part
        cyrillic_a = 'validEmail@exаmple.com'  # Cyrillic "a" in domain part
        self.assertNotEqual(latin_a, cyrillic_a)

        email = SPUserManager.normalize_email(cyrillic_a)
        self.assertEqual(email, 'validEmail@xn--exmple-4nf.com')

        self.assertNotEqual(SPUserManager.normalize_email(latin_a), SPUserManager.normalize_email(cyrillic_a))
