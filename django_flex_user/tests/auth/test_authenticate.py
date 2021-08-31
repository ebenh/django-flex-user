from django.test import TestCase


class TestAuthenticate(TestCase):
    """
    This class is designed to test django_flex_user.backends.SPModelBackend.authenticate

    To make it the active authentication backend, set the following in settings.py:

    AUTHENTICATION_BACKENDS = ['django_flex_user.backends.SPModelBackend']
    """
    _username_values = [{},
                        {'username': None},
                        {'username': ''},
                        {'username': 'validUsername'},
                        {'username': 'invalidUsername'}]

    _email_values = [{},
                     {'email': None},
                     {'email': ''},
                     {'email': 'validEmail@example.com'},
                     {'email': 'invalidEmail@example.com'}]

    _phone_number_values = [{},
                            {'phone_number': None},
                            {'phone_number': ''},
                            {'phone_number': '+12025551234'},
                            {'phone_number': 'invalidPhoneNumber'}]

    _password_values = [{},
                        {'password': None},
                        {'password': ''},
                        {'password': 'validPassword'},
                        {'password': 'invalidPassword'}]

    def test_authenticate(self):
        from django_flex_user.models import FlexUser
        from django.db import transaction

        FlexUser.objects.create_user(
            username='validUsername',
            email='validEmail@example.com',
            phone_number='+12025551234',
            password='validPassword'
        )

        for i in self._username_values:
            for j in self._email_values:
                for k in self._phone_number_values:
                    for l in self._password_values:

                        args = {}
                        args.update(i)
                        args.update(j)
                        args.update(k)
                        args.update(l)

                        with self.subTest(**args), transaction.atomic():
                            from django.contrib.auth import authenticate

                            if args.get('username') is None and \
                                    args.get('email') is None and \
                                    args.get('phone_number') is None:
                                """
                                If the supplied username, email, and phone_number are simultaneously undefined or None,
                                django_flex_user.backends.SPModelBackend.authenticate should raise ValueError.
                                
                                At least one of username, email or phone_number must be defined and not None.
                                """
                                self.assertRaises(ValueError, authenticate, **args)
                            elif args.get('password') is None:
                                """
                                If the supplied password is undefined or None,
                                django_flex_user.backends.SPModelBackend.authenticate should return None.
                                """
                                self.assertIsNone(authenticate(**args))
                            elif args.get('password') == '':
                                """
                                If the supplied password is the empty string,
                                django_flex_user.backends.SPModelBackend.authenticate should attempt to authenticate it normally.
                                
                                django_flex_user.models.FlexUserManager._create_user deliberately puts no restriction on password
                                complexity, therefore any password is valid. It's worth pointing out that for users
                                created with None passwords, their passwords are stored as an unusable password. An
                                unusable password is one for which django_flex_user.backends.SPModelBackend.authenticate should
                                always return None. Unusable passwords are random strings prefixed with the unusable
                                password prefix "!".                              
                                
                                In this test case, empty string does not match the stored password of our test user,
                                therefore django_flex_user.backends.SPModelBackend.authenticate should return None.
                                """
                                self.assertIsNone(authenticate(**args))
                            elif args.get('username') == '' or \
                                    args.get('email') == '' or \
                                    args.get('phone_number') == '':
                                """
                                If any of the supplied username, email or phone_number are the empty string,
                                django_flex_user.backends.SPModelBackend.authenticate should return None. This is because empty
                                string does not form a valid username, email or phone_number.
                                """
                                self.assertIsNone(authenticate(**args))
                            elif (args.get('username') and 'invalid' in args['username']) or \
                                    (args.get('email') and 'invalid' in args['email']) or \
                                    (args.get('phone_number') and 'invalid' in args['phone_number']) or \
                                    (args.get('password') and 'invalid' in args['password']):
                                """
                                If any of the supplied username, email, phone_number or password are defined and
                                invalid, django_flex_user.backends.SPModelBackend.authenticate should return None.
                                """
                                self.assertIsNone(authenticate(**args))
                            else:
                                """
                                This case encompasses all possible permutations of supplied username, email,
                                phone_number and password for which django_flex_user.backends.SPModelBackend.authenticate should
                                return a valid (i.e. not None) FlexUser object.
                                """
                                self.assertIsNotNone(authenticate(**args))

                            transaction.set_rollback(True)

    def test_authenticate_with_unusable_password(self):
        from django_flex_user.models import FlexUser
        from django.contrib.auth import authenticate

        FlexUser.objects.create_user(username='validUsername')

        self.assertIsNone(authenticate(username='validUsername'))
        self.assertIsNone(authenticate(username='validUsername', password=None))
        self.assertIsNone(authenticate(username='validUsername', password=''))
        self.assertIsNone(authenticate(username='validUsername', password='invalidPassword'))

        FlexUser.objects.create_user(email='validEmail@example.com', password=None)

        self.assertIsNone(authenticate(email='validEmail@example.com'))
        self.assertIsNone(authenticate(email='validEmail@example.com', password=None))
        self.assertIsNone(authenticate(email='validEmail@example.com', password=''))
        self.assertIsNone(authenticate(email='validEmail@example.com', password='invalidPassword'))

    def test_authenticate_inactive_user(self):
        from django_flex_user.models import FlexUser
        from django.contrib.auth import authenticate

        user = FlexUser.objects.create_user(username='validUsername', password='validPassword', is_active=False)

        self.assertIsNone(authenticate(username='validUsername'))
        self.assertIsNone(authenticate(username='validUsername', password=None))
        self.assertIsNone(authenticate(username='validUsername', password=''))
        self.assertIsNone(authenticate(username='validUsername', password='validPassword'))

    def test_authenticate_username_case_insensitivity(self):
        from django_flex_user.models import FlexUser
        from django.contrib.auth import authenticate

        user1 = FlexUser.objects.create_user(username='validUsername', password='validPassword')
        self.assertIsNotNone(authenticate(username='VALIDUSERNAME', password='validPassword'))

    def test_authenticate_non_normalized_username(self):
        """
        django_flex_user.backends.SPModelBackend.authenticate deliberately does not normalize input. It is the callers
        responsibility to normalize username by calling django_flex_user.models.FlexUser.normalize_username before passing it to
        authenticate.

        :return:
        """
        from django_flex_user.models import FlexUser
        from django.contrib.auth import authenticate

        nfd = 'validUsérname'  # é = U+0065 U+0301
        nfkc = 'validUsérname'  # é = U+00e9

        user1 = FlexUser.objects.create_user(username=nfd, password='validPassword')
        self.assertEqual(user1.username, nfkc)

        # This call to authenticate should fail (i.e. return None) because username has not been normalized
        self.assertIsNone(authenticate(username=nfd, password='validPassword'))

        # This call to authenticate succeeds because we normalize username
        user2 = authenticate(username=FlexUser.normalize_username(nfd), password='validPassword')
        self.assertEqual(user1, user2)

    def test_authenticate_non_normalized_email(self):
        """
        django_flex_user.backends.SPModelBackend.authenticate deliberately does not normalize input. It is the caller's
        responsibility to normalize email by calling django_flex_user.models.FlexUserManager.normalize_email before passing it to
        authenticate.

        :return:
        """
        from django_flex_user.models import FlexUser
        from django.contrib.auth import authenticate

        user1 = FlexUser.objects.create_user(email='validEmail@bücher.example', password='validPassword')
        self.assertEqual(user1.email, 'validEmail@xn--bcher-kva.example')

        # This call to authenticate should fail (i.e. return None) because email has not been normalized
        self.assertIsNone(authenticate(email='validEmail@bücher.example', password='validPassword'))

        # This call to authenticate succeeds because we normalize email
        user2 = authenticate(
            email=FlexUser.objects.normalize_email('validEmail@bücher.example'),
            password='validPassword'
        )
        self.assertEqual(user1, user2)
