from django.test import TestCase


class TestUserModel(TestCase):
    """
    This class is designed to test django_flex_user.models.FlexUser
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

    _password_values = [{},
                        {'password': None},
                        {'password': ''},
                        {'password': 'validPassword'},
                        {'password': 'invalidPassword' + 'x' * 128}]

    def test_full_clean_and_save(self):
        from django.db import transaction
        from freezegun import freeze_time

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
                            from django_flex_user.models import FlexUser
                            from django.core.exceptions import ValidationError
                            from django.utils import timezone

                            user = FlexUser(**args)

                            if ('username' not in args or args['username'] is None) and \
                                    ('email' not in args or args['email'] is None) and \
                                    ('phone_number' not in args or args['phone_number'] is None):
                                """
                                If the supplied username, email, and phone_number are simultaneously undefined or None,
                                django_flex_user.models.FlexUser.full_clean should raise ValidationError.

                                At least one of username, email or phone_number must be defined and not None.
                                """
                                self.assertRaises(ValidationError, user.full_clean)
                            elif not args.get('password'):
                                """
                                If the supplied password is undefined, None or the empty string,
                                django_flex_user.models.FlexUser.full_clean should raise ValidationError.
                                """
                                self.assertRaises(ValidationError, user.full_clean)
                            elif args.get('username') == '' or \
                                    args.get('email') == '' or \
                                    args.get('phone_number') == '':
                                """
                                If any of the supplied username, email or phone_number are the empty string
                                django_flex_user.models.FlexUser.full_clean should raise ValidationError.
                                """
                                self.assertRaises(ValidationError, user.full_clean)
                            elif (args.get('username') and 'invalid' in args['username']) or \
                                    (args.get('email') and 'invalid' in args['email']) or \
                                    (args.get('phone_number') and 'invalid' in args['phone_number']) or \
                                    (args.get('password') and 'invalid' in args['password']):
                                """
                                If any of the supplied username, email, phone_number or password are defined and
                                invalid, django_flex_user.models.FlexUser.full_clean should raise ValidationError.
                                """
                                self.assertRaises(ValidationError, user.full_clean)
                            else:
                                """
                                This case encompasses all possible permutations of supplied username, email,
                                phone_number and password for which django_flex_user.models.FlexUser.full_clean should execute
                                successfully without raising an error.
                                """
                                user.full_clean()

                                self.assertIsNone(user.id)

                                self.assertEqual(user.username, args.get('username'))
                                self.assertEqual(user.email, args.get('email'))
                                self.assertEqual(user.phone_number, args.get('phone_number'))

                                self.assertEqual(user.password, args.get('password'))

                                self.assertEqual(user.date_joined, timezone.now())
                                self.assertIsNone(user.last_login)
                                self.assertIs(user.is_active, True)

                                self.assertIs(user.is_superuser, False)
                                self.assertIs(user.is_staff, False)

                                user.save()

                                self.assertIsNotNone(user.id)

                            transaction.set_rollback(True)

    def test_full_clean_and_save_username_case_insensitivity(self):
        from django_flex_user.models import FlexUser
        from django.core.exceptions import ValidationError

        user1 = FlexUser(username='validUsername')
        user1.set_unusable_password()
        user1.full_clean()
        user1.save()
        # Ensure username was saved exactly as it was entered
        self.assertEqual(user1.username, 'validUsername')

        user2 = FlexUser(username='VALIDUSERNAME')
        user2.set_unusable_password()
        self.assertRaises(ValidationError, user2.full_clean)

    def test_full_clean_and_save_duplicate_username(self):
        from django_flex_user.models import FlexUser
        from django.core.exceptions import ValidationError

        user1 = FlexUser(username='validUsername')
        user1.set_unusable_password()
        user1.full_clean()
        user1.save()

        user2 = FlexUser(username='validUsername')
        user2.set_unusable_password()
        self.assertRaises(ValidationError, user2.full_clean)

    def test_full_clean_and_save_duplicate_email(self):
        from django_flex_user.models import FlexUser
        from django.core.exceptions import ValidationError

        user1 = FlexUser(email='validEmail@example.com')
        user1.set_unusable_password()
        user1.full_clean()
        user1.save()

        user2 = FlexUser(email='validEmail@example.com')
        user2.set_unusable_password()
        self.assertRaises(ValidationError, user2.full_clean)

    def test_full_clean_and_save_duplicate_phone_number(self):
        from django_flex_user.models import FlexUser
        from django.core.exceptions import ValidationError

        user1 = FlexUser(phone_number='+12025551234')
        user1.set_unusable_password()
        user1.full_clean()
        user1.save()

        user2 = FlexUser(phone_number='+12025551234')
        user2.set_unusable_password()
        self.assertRaises(ValidationError, user2.full_clean)

    def test_full_clean_and_save_ambiguous_username(self):
        """
        Verify that an email address or phone number cannot form a valid username.

        :return:
        """
        from django_flex_user.models import FlexUser
        from django.core.exceptions import ValidationError

        user1 = FlexUser(username='validEmail@example.com')
        user1.set_unusable_password()
        self.assertRaises(ValidationError, user1.full_clean)

        user2 = FlexUser(username='+12025551234')
        user2.set_unusable_password()
        self.assertRaises(ValidationError, user2.full_clean)

    def test_full_clean_and_save_ambiguous_email(self):
        """
        Verify that a username or phone number cannot form a valid email.

        :return:
        """
        from django_flex_user.models import FlexUser
        from django.core.exceptions import ValidationError

        user1 = FlexUser(email='validUsername')
        user1.set_unusable_password()
        self.assertRaises(ValidationError, user1.full_clean)

        user2 = FlexUser(email='+12025551234')
        user2.set_unusable_password()
        self.assertRaises(ValidationError, user2.full_clean)

    def test_full_clean_and_save_ambiguous_phone_number(self):
        """
        Verify that a username or email address cannot form a valid phone_number.

        :return:
        """
        from django_flex_user.models import FlexUser
        from django.core.exceptions import ValidationError

        user1 = FlexUser(phone_number='validUsername')
        user1.set_unusable_password()
        self.assertRaises(ValidationError, user1.full_clean)

        user2 = FlexUser(phone_number='validEmail@example.com')
        user2.set_unusable_password()
        self.assertRaises(ValidationError, user2.full_clean)

    def test_full_clean_and_save_normalize_username(self):
        from django_flex_user.models import FlexUser
        from django.core.exceptions import ValidationError

        nfd = 'validUsérname'  # é = U+0065 U+0301
        nfkc = 'validUsérname'  # é = U+00e9

        user1 = FlexUser(username=nfd)
        user1.set_unusable_password()

        # Verify that username is not yet normalized
        self.assertEqual(user1.username, nfd)

        # Verify that username is normalized upon full_clean
        user1.full_clean()
        self.assertEqual(user1.username, nfkc)
        user1.save()

        # Verify that non-normalized duplicate username fails unique constraint
        user2 = FlexUser(username=nfd)
        user2.set_unusable_password()
        self.assertRaises(ValidationError, user2.full_clean)

        # Verify that normalized duplicate username fails unique constraint
        user3 = FlexUser(email=nfkc)
        user3.set_unusable_password()
        self.assertRaises(ValidationError, user3.full_clean)

    def test_full_clean_and_save_normalize_email(self):
        from django_flex_user.models import FlexUser
        from django.core.exceptions import ValidationError

        user = FlexUser(email='validEmail@bücher.example')
        user.set_unusable_password()

        # Verify that email is not yet normalized
        self.assertEqual(user.email, 'validEmail@bücher.example')

        # Verify that email is normalized upon full_clean
        user.full_clean()
        self.assertEqual(user.email, 'validEmail@xn--bcher-kva.example')
        user.save()

    def test_normalize_username(self):
        from django_flex_user.models import FlexUser

        username = FlexUser.normalize_username(None)
        self.assertIs(username, None)

        username = FlexUser.normalize_username('')
        self.assertEqual(username, '')

        username = FlexUser.normalize_username('validUsername')
        self.assertEqual(username, 'validUsername')

        username = FlexUser.normalize_username('invalidUsername+')
        self.assertEqual(username, 'invalidUsername+')

        # Unicode equivalence
        nfd = 'validUsérname'  # é = U+0065 U+0301
        nfkc = 'validUsérname'  # é = U+00e9
        self.assertNotEqual(nfd, nfkc)

        username = FlexUser.normalize_username(nfd)
        self.assertEqual(username, nfkc)

    def test_serialize(self):
        """
        This purpose of this method is to test django_flex_user.models.FlexUser.natural_key and
        django_flex_user.models.FlexUserManager.get_by_natural_key.

        :return:
        """
        from django_flex_user.models import FlexUser
        from django.core import serializers

        # Create a user
        user1 = FlexUser(
            username='validUsername',
            email='validEmail@example.com',
            phone_number='+12025551234'
        )
        user1.set_unusable_password()
        user1.full_clean()
        user1.save()

        # Serialize
        stream = serializers.serialize('json', FlexUser.objects.all(), indent=2, use_natural_primary_keys=True)

        # Clear user table
        FlexUser.objects.all().delete()

        # Deserialize. Calls django_flex_user.models.FlexUser.natural_key and django_flex_user.models.FlexUserManager.get_by_natural_key.
        for obj in serializers.deserialize('json', stream):
            obj.save()

        # Verify that the data has round tripped
        user2 = FlexUser.objects.all().first()
        self.assertEqual(user2.username, 'validUsername')
        self.assertEqual(user2.email, 'validEmail@example.com')
        self.assertEqual(user2.phone_number, '+12025551234')
