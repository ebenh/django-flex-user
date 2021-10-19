from django.test import TestCase


class TestUserSerializer(TestCase):
    """
    This class is designed to test django_flex_user.serializers.FlexUserSerializer
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

    _phone_values = [{},
                            {'phone': None},
                            {'phone': ''},
                            {'phone': '+12025551234'},
                            {'phone': 'invalidPhoneNumber'}]

    _password_values = [{},
                        {'password': None},
                        {'password': ''},
                        {'password': 'validPassword'},
                        {'password': 'invalid'}]

    def test_create(self):
        from django.db import transaction
        from freezegun import freeze_time

        for i in self._username_values:
            for j in self._email_values:
                for k in self._phone_values:
                    for l in self._password_values:

                        data = {}
                        data.update(i)
                        data.update(j)
                        data.update(k)
                        data.update(l)

                        with self.subTest(**data), transaction.atomic(), freeze_time():
                            from django_flex_user.serializers import FlexUserSerializer
                            from django.utils import timezone

                            serializer = FlexUserSerializer(data=data)

                            if ('username' not in data or data['username'] is None) and \
                                    ('email' not in data or data['email'] is None) and \
                                    ('phone' not in data or data['phone'] is None):
                                """
                                If the supplied username, email, and phone are simultaneously undefined or None,
                                django_flex_user.serializers.FlexUserSerializer.is_valid should return False.

                                At least one of username, email or phone must be defined and not None.
                                """
                                self.assertIs(serializer.is_valid(), False)
                            elif not data.get('password'):
                                """
                                If the supplied password is undefined, None or the empty string,
                                django_flex_user.serializers.FlexUserSerializer.is_valid should return False.
                                """
                                self.assertIs(serializer.is_valid(), False)
                            elif data.get('username') == '' or \
                                    data.get('email') == '' or \
                                    data.get('phone') == '':
                                """
                                If any of the supplied username, email or phone are the empty string
                                django_flex_user.serializers.FlexUserSerializer.is_valid should return False.
                                """
                                self.assertIs(serializer.is_valid(), False)
                            elif (data.get('username') and 'invalid' in data['username']) or \
                                    (data.get('email') and 'invalid' in data['email']) or \
                                    (data.get('phone') and 'invalid' in data['phone']) or \
                                    (data.get('password') and 'invalid' in data['password']):
                                """
                                If any of the supplied username, email, phone or password are defined and
                                invalid,  django_flex_user.serializers.FlexUserSerializer.is_valid should return False.
                                """
                                self.assertIs(serializer.is_valid(), False)
                            else:
                                """
                                This case encompasses all possible permutations of supplied username, email,
                                phone and password for which django_flex_user.serializers.FlexUserSerializer.is_valid return
                                True.
                                """
                                self.assertIs(serializer.is_valid(), True)

                                user = serializer.save()

                                self.assertIsNotNone(user)
                                self.assertIsNotNone(user.id)

                                self.assertEqual(user.username, data.get('username'))
                                self.assertEqual(user.email, data.get('email'))
                                self.assertEqual(user.phone, data.get('phone'))

                                self.assertTrue(user.password)
                                # django_flex_user.serializers.FlexUserSerializer must always return a user with a usable password
                                self.assertTrue(user.has_usable_password())

                                self.assertEqual(user.date_joined, timezone.now())
                                self.assertIsNone(user.last_login)
                                self.assertIs(user.is_active, True)

                                self.assertIs(user.is_superuser, False)
                                self.assertIs(user.is_staff, False)

                            transaction.set_rollback(True)

    def test_update(self):
        from django_flex_user.models.user import FlexUser
        from django.db import transaction
        from freezegun import freeze_time

        freezer = freeze_time()
        freezer.start()

        user = FlexUser.objects.create_user(username='validUsername', password='validPassword')

        for i in self._username_values:
            for j in self._email_values:
                for k in self._phone_values:
                    for l in self._password_values:

                        data = {}
                        data.update(i)
                        data.update(j)
                        data.update(k)
                        data.update(l)

                        with self.subTest(**data), transaction.atomic():
                            from django_flex_user.serializers import FlexUserSerializer
                            from django.utils import timezone

                            serializer = FlexUserSerializer(user, data=data, partial=True)

                            if 'password' in data and not data['password']:
                                """
                                If the supplied password is defined and either None or the empty string,
                                django_flex_user.serializers.FlexUserSerializer.is_valid should return False.
                                """
                                self.assertIs(serializer.is_valid(), False)
                            elif ('username' in data and data['username'] is None) and \
                                    ('email' not in data or data['email'] is None) and \
                                    ('phone' not in data or data['phone'] is None):
                                """
                                If the supplied username is None, and the supplied email and phone are
                                simultaneously undefined or None, django_flex_user.serializers.FlexUserSerializer.is_valid should
                                return False.
                                """
                                self.assertIs(serializer.is_valid(), False)
                            elif data.get('username') == '' or \
                                    data.get('email') == '' or \
                                    data.get('phone') == '':
                                """
                                If any of the supplied username, email or phone are the empty string
                                django_flex_user.serializers.FlexUserSerializer.is_valid should return False.
                                """
                                self.assertIs(serializer.is_valid(), False)
                            elif (data.get('username') and 'invalid' in data['username']) or \
                                    (data.get('email') and 'invalid' in data['email']) or \
                                    (data.get('phone') and 'invalid' in data['phone']) or \
                                    (data.get('password') and 'invalid' in data['password']):
                                """
                                If any of the supplied username, email, phone or password are defined and
                                invalid,  django_flex_user.serializers.FlexUserSerializer.is_valid should return False.
                                """
                                self.assertIs(serializer.is_valid(), False)
                            else:
                                """
                                This case encompasses all possible permutations of supplied username, email,
                                phone and password for which django_flex_user.serializers.FlexUserSerializer.is_valid return
                                True.
                                """
                                self.assertIs(serializer.is_valid(), True)

                                serializer.save()

                                self.assertIsNotNone(user)
                                self.assertIsNotNone(user.id)

                                self.assertEqual(user.username, data.get('username', 'validUsername'))
                                self.assertEqual(user.email, data.get('email'))
                                self.assertEqual(user.phone, data.get('phone'))

                                self.assertTrue(user.password)
                                # django_flex_user.serializers.FlexUserSerializer must always return a user with a usable password
                                self.assertTrue(user.has_usable_password())

                                self.assertEqual(user.date_joined, timezone.now())
                                self.assertIsNone(user.last_login)
                                self.assertIs(user.is_active, True)

                                self.assertIs(user.is_superuser, False)
                                self.assertIs(user.is_staff, False)

                            user.refresh_from_db()
                            transaction.set_rollback(True)
        freezer.stop()

    def test_create_username_case_insensitivity(self):
        from django_flex_user.serializers import FlexUserSerializer

        data = {'username': 'validUsername', 'password': 'validPassword'}
        serializer = FlexUserSerializer(data=data)
        self.assertIs(serializer.is_valid(), True)
        self.assertIsNotNone(serializer.save())

        data = {'username': 'VALIDUSERNAME', 'password': 'validPassword'}
        serializer = FlexUserSerializer(data=data)
        self.assertIs(serializer.is_valid(), False)
        self.assertRaises(AssertionError, serializer.save)

    def test_update_username_case_insensitivity(self):
        from django_flex_user.models.user import FlexUser
        from django_flex_user.serializers import FlexUserSerializer

        user = FlexUser.objects.create_user(username='validUsername', password='validPassword')
        FlexUser.objects.create_user(username='validUsername2', password='validPassword')

        data = {'username': 'VALIDUSERNAME2'}
        serializer = FlexUserSerializer(user, data=data, partial=True)
        self.assertIs(serializer.is_valid(), False)
        self.assertRaises(AssertionError, serializer.save)

    def test_create_duplicate_username(self):
        from django_flex_user.serializers import FlexUserSerializer

        data = {'username': 'validUsername', 'password': 'validPassword'}

        serializer = FlexUserSerializer(data=data)
        self.assertIs(serializer.is_valid(), True)
        self.assertIsNotNone(serializer.save())

        serializer = FlexUserSerializer(data=data)
        self.assertIs(serializer.is_valid(), False)
        self.assertRaises(AssertionError, serializer.save)

    def test_update_duplicate_username(self):
        from django_flex_user.models.user import FlexUser
        from django_flex_user.serializers import FlexUserSerializer

        user = FlexUser.objects.create_user(username='validUsername', password='validPassword')
        FlexUser.objects.create_user(username='validUsername2', password='validPassword')

        data = {'username': 'validUsername2'}
        serializer = FlexUserSerializer(user, data=data, partial=True)
        self.assertIs(serializer.is_valid(), False)
        self.assertRaises(AssertionError, serializer.save)

    def test_create_duplicate_email(self):
        from django_flex_user.serializers import FlexUserSerializer

        data = {'email': 'validEmail@example.com', 'password': 'validPassword'}

        serializer = FlexUserSerializer(data=data)
        self.assertIs(serializer.is_valid(), True)
        self.assertIsNotNone(serializer.save())

        serializer = FlexUserSerializer(data=data)
        self.assertIs(serializer.is_valid(), False)
        self.assertRaises(AssertionError, serializer.save)

    def test_update_duplicate_email(self):
        from django_flex_user.models.user import FlexUser
        from django_flex_user.serializers import FlexUserSerializer

        user = FlexUser.objects.create_user(email='validEmail@example.com', password='validPassword')
        FlexUser.objects.create_user(email='validEmail2@example.com', password='validPassword')

        data = {'email': 'validEmail2@example.com'}
        serializer = FlexUserSerializer(user, data=data, partial=True)
        self.assertIs(serializer.is_valid(), False)
        self.assertRaises(AssertionError, serializer.save)

    def test_create_duplicate_phone(self):
        from django_flex_user.serializers import FlexUserSerializer

        data = {'phone': '+12025551234', 'password': 'validPassword'}

        serializer = FlexUserSerializer(data=data)
        self.assertIs(serializer.is_valid(), True)
        self.assertIsNotNone(serializer.save())

        serializer = FlexUserSerializer(data=data)
        self.assertIs(serializer.is_valid(), False)
        self.assertRaises(AssertionError, serializer.save)

    def test_update_duplicate_phone(self):
        from django_flex_user.models.user import FlexUser
        from django_flex_user.serializers import FlexUserSerializer

        user = FlexUser.objects.create_user(phone='+12025551234', password='validPassword')
        FlexUser.objects.create_user(phone='+12025554321', password='validPassword')

        data = {'phone': '+12025554321'}
        serializer = FlexUserSerializer(user, data=data, partial=True)
        self.assertIs(serializer.is_valid(), False)
        self.assertRaises(AssertionError, serializer.save)

    def test_create_ambiguous_username(self):
        """
        Verify that an email address or phone number cannot form a valid username.

        :return:
        """
        from django_flex_user.serializers import FlexUserSerializer

        data = {'username': 'validEmail@example.com', 'password': 'validPassword'}
        serializer = FlexUserSerializer(data=data)
        self.assertIs(serializer.is_valid(), False)
        self.assertRaises(AssertionError, serializer.save)

        data = {'username': '+12025551234', 'password': 'validPassword'}
        serializer = FlexUserSerializer(data=data)
        self.assertIs(serializer.is_valid(), False)
        self.assertRaises(AssertionError, serializer.save)

    def test_update_ambiguous_username(self):
        """
        Verify that an email address or phone number cannot form a valid username.

        :return:
        """
        from django_flex_user.models.user import FlexUser
        from django_flex_user.serializers import FlexUserSerializer

        user = FlexUser.objects.create_user(username='validUsername', password='validPassword')

        data = {'username': 'validEmail@example.com'}
        serializer = FlexUserSerializer(user, data=data, partial=True)
        self.assertIs(serializer.is_valid(), False)
        self.assertRaises(AssertionError, serializer.save)

        data = {'username': '+12025551234'}
        serializer = FlexUserSerializer(user, data=data, partial=True)
        self.assertIs(serializer.is_valid(), False)
        self.assertRaises(AssertionError, serializer.save)

    def test_create_ambiguous_email(self):
        """
        Verify that a username or phone number cannot form a valid email.

        :return:
        """
        from django_flex_user.serializers import FlexUserSerializer

        data = {'email': 'validUsername', 'password': 'validPassword'}
        serializer = FlexUserSerializer(data=data)
        self.assertIs(serializer.is_valid(), False)
        self.assertRaises(AssertionError, serializer.save)

        data = {'email': '+12025551234', 'password': 'validPassword'}
        serializer = FlexUserSerializer(data=data)
        self.assertIs(serializer.is_valid(), False)
        self.assertRaises(AssertionError, serializer.save)

    def test_update_ambiguous_email(self):
        """
        Verify that a username or phone number cannot form a valid email.

        :return:
        """
        from django_flex_user.models.user import FlexUser
        from django_flex_user.serializers import FlexUserSerializer

        user = FlexUser.objects.create_user(email='validEmail@example.com', password='validPassword')

        data = {'email': 'validUsername'}
        serializer = FlexUserSerializer(user, data=data, partial=True)
        self.assertIs(serializer.is_valid(), False)
        self.assertRaises(AssertionError, serializer.save)

        data = {'email': '+12025551234'}
        serializer = FlexUserSerializer(user, data=data, partial=True)
        self.assertIs(serializer.is_valid(), False)
        self.assertRaises(AssertionError, serializer.save)

    def test_create_ambiguous_phone(self):
        """
        Verify that a username or email address cannot form a valid phone.

        :return:
        """
        from django_flex_user.serializers import FlexUserSerializer

        data = {'phone': 'validUsername', 'password': 'validPassword'}
        serializer = FlexUserSerializer(data=data)
        self.assertIs(serializer.is_valid(), False)
        self.assertRaises(AssertionError, serializer.save)

        data = {'phone': 'validEmail@example.com', 'password': 'validPassword'}
        serializer = FlexUserSerializer(data=data)
        self.assertIs(serializer.is_valid(), False)
        self.assertRaises(AssertionError, serializer.save)

    def test_update_ambiguous_phone(self):
        """
        Verify that a username or email address cannot form a valid phone.

        :return:
        """
        from django_flex_user.models.user import FlexUser
        from django_flex_user.serializers import FlexUserSerializer

        user = FlexUser.objects.create_user(phone='+12025551234', password='validPassword')

        data = {'phone': 'validUsername'}
        serializer = FlexUserSerializer(user, data=data, partial=True)
        self.assertIs(serializer.is_valid(), False)
        self.assertRaises(AssertionError, serializer.save)

        data = {'phone': 'validEmail@example.com'}
        serializer = FlexUserSerializer(user, data=data, partial=True)
        self.assertIs(serializer.is_valid(), False)
        self.assertRaises(AssertionError, serializer.save)

    def test_create_normalize_username(self):
        from django_flex_user.serializers import FlexUserSerializer

        nfd = 'validUsérname'  # é = U+0065 U+0301
        nfkc = 'validUsérname'  # é = U+00e9

        data = {'username': nfd, 'password': 'validPassword'}
        serializer = FlexUserSerializer(data=data)
        self.assertIs(serializer.is_valid(), True)

        user = serializer.save()
        self.assertIsNotNone(user)
        self.assertEqual(user.username, nfkc)

    def test_update_normalize_username(self):
        from django_flex_user.models.user import FlexUser
        from django_flex_user.serializers import FlexUserSerializer

        user = FlexUser.objects.create_user(username='validUsername', password='validPassword')

        nfd = 'validUsérname'  # é = U+0065 U+0301
        nfkc = 'validUsérname'  # é = U+00e9

        data = {'username': nfd}
        serializer = FlexUserSerializer(user, data=data, partial=True)
        self.assertIs(serializer.is_valid(), True)

        user = serializer.save()
        self.assertIsNotNone(user)
        self.assertEqual(user.username, nfkc)

    def test_create_normalize_email(self):
        from django_flex_user.serializers import FlexUserSerializer

        data = {'email': 'validEmail@bücher.example', 'password': 'validPassword'}
        serializer = FlexUserSerializer(data=data)
        self.assertIs(serializer.is_valid(), True)

        user = serializer.save()
        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'validEmail@xn--bcher-kva.example')

    def test_update_normalize_email(self):
        from django_flex_user.models.user import FlexUser
        from django_flex_user.serializers import FlexUserSerializer

        user = FlexUser.objects.create_user(email='validEmail@example.com', password='validPassword')

        data = {'email': 'validEmail@bücher.example'}
        serializer = FlexUserSerializer(user, data=data, partial=True)
        self.assertIs(serializer.is_valid(), True)

        user = serializer.save()
        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'validEmail@xn--bcher-kva.example')

    def test_email_verified(self):
        from django_flex_user.models.user import FlexUser
        from django_flex_user.models.otp import EmailToken
        from django_flex_user.serializers import FlexUserSerializer

        # Create user
        user = FlexUser.objects.create_user(email='validEmail@example.com', password='validPassword')
        # Serialize user
        serializer = FlexUserSerializer(user)

        # Check email_verified and phone_verified
        self.assertFalse(serializer.data['email_verified'])
        self.assertIsNone(serializer.data['phone_verified'])

        # Verify email address
        email_token = user.emailtoken_set.first()
        email_token.generate_password()
        email_token.check_password(email_token.password)

        # Reload data from db
        user.refresh_from_db()
        serializer = FlexUserSerializer(user)

        # Check email_verified and phone_verified
        self.assertTrue(serializer.data['email_verified'])
        self.assertIsNone(serializer.data['phone_verified'])

    def test_phone_verified(self):
        from django_flex_user.models.user import FlexUser
        from django_flex_user.models.otp import PhoneToken
        from django_flex_user.serializers import FlexUserSerializer

        # Create user
        user = FlexUser.objects.create_user(phone='+12025551234', password='validPassword')
        # Serialize user
        serializer = FlexUserSerializer(user)

        # Check email_verified and phone_verified
        self.assertFalse(serializer.data['phone_verified'])
        self.assertIsNone(serializer.data['email_verified'])

        # Verify phone number
        phone_token = PhoneToken.objects.get(user=user)
        phone_token.generate_password()
        phone_token.check_password(phone_token.password)

        # Reload data from db
        user.refresh_from_db()
        serializer = FlexUserSerializer(user)

        # Check email_verified and phone_verified
        self.assertTrue(serializer.data['phone_verified'])
        self.assertIsNone(serializer.data['email_verified'])
