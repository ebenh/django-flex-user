from rest_framework.test import APITestCase
from rest_framework import status


class TestSPUserRetrieveUpdate(APITestCase):
    """
    This class is designed to test django_flex_user.views.SPUser
    """
    _REST_ENDPOINT_PATH = '/account/users/user/'

    def test_method_get(self):
        response = self.client.get(self._REST_ENDPOINT_PATH)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_method_post(self):
        response = self.client.post(self._REST_ENDPOINT_PATH)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_method_put(self):
        response = self.client.put(self._REST_ENDPOINT_PATH)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_method_patch(self):
        response = self.client.patch(self._REST_ENDPOINT_PATH)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_method_delete(self):
        response = self.client.delete(self._REST_ENDPOINT_PATH)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_method_options(self):
        response = self.client.options(self._REST_ENDPOINT_PATH)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestSPUserRetrieveUpdateAuthenticated(APITestCase):
    """
    This class is designed to test django_flex_user.views.SPUser
    """
    _REST_ENDPOINT_PATH = '/account/users/user/'

    class _ContentType:
        class ApplicationJSON:
            username_values = [{},
                               {'username': None},
                               {'username': ''},
                               {'username': 'validUsername'},
                               {'username': 'invalidUsername+'}]

            email_values = [{},
                            {'email': None},
                            {'email': ''},
                            {'email': 'validEmail@example.com'},
                            {'email': 'invalidEmail'}]

            phone_number_values = [{},
                                   {'phone_number': None},
                                   {'phone_number': ''},
                                   {'phone_number': '+12025551234'},
                                   {'phone_number': 'invalidPhoneNumber'}]

            password_values = [{},
                               {'password': None},
                               {'password': ''},
                               {'password': 'validPassword'},
                               {'password': 'invalid'}]

        class MultipartFormData:
            username_values = [{},
                               {'username': ''},
                               {'username': 'validUsername'},
                               {'username': 'invalidUsername+'}]

            email_values = [{},
                            {'email': ''},
                            {'email': 'validEmail@example.com'},
                            {'email': 'invalidEmail'}]

            phone_number_values = [{},
                                   {'phone_number': ''},
                                   {'phone_number': '+12025551234'},
                                   {'phone_number': 'invalidPhoneNumber'}]

            password_values = [{},
                               {'password': ''},
                               {'password': 'validPassword'},
                               {'password': 'invalid'}]

    def setUp(self):
        from django_flex_user.models import SPUser

        self.user = SPUser.objects.create_user(username='validUsername', password='validPassword')

    def test_method_get(self):
        is_authenticated = self.client.login(username='validUsername', password='validPassword')
        self.assertIs(is_authenticated, True)

        response = self.client.get(self._REST_ENDPOINT_PATH)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(
            response.data,
            {
                'username': 'validUsername',
                'email': None,
                'email_verified': False,
                'phone_number': None,
                'phone_number_verified': False
            }
        )

        self.client.logout()

    def test_method_post(self):
        is_authenticated = self.client.login(username='validUsername', password='validPassword')
        self.assertIs(is_authenticated, True)

        response = self.client.post(self._REST_ENDPOINT_PATH)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.logout()

    def test_method_patch_format_application_json(self):
        from django.db import transaction

        for i in self._ContentType.ApplicationJSON.username_values:
            for j in self._ContentType.ApplicationJSON.email_values:
                for k in self._ContentType.ApplicationJSON.phone_number_values:
                    for l in self._ContentType.ApplicationJSON.password_values:

                        data = {}
                        data.update(i)
                        data.update(j)
                        data.update(k)
                        data.update(l)

                        with self.subTest(**data), transaction.atomic():

                            """
                            Special considerations for password changes:

                            By default, updating a user's password invalidates all sessions for the user. To make it so
                            that the user is *not* signed out by a password change, in
                            django_flex_user.serializers.SPUserSerializer.update we call
                            django.contrib.auth.update_session_auth_hash which (1) generates a new session key for the
                            user's current session (2) updates the current session's _auth_user_hash with a value based
                            on the user's new password (because the value of _auth_user_hash for all other sessions are
                            not based on the user's latest password, those sessions are implicitly invalidated). The
                            session key for the newly created session is returned to the client in a 'set-cookie'
                            response header.

                            Because this call is wrapped in a transaction that rolls back all database changes at the
                            end of each iteration, the changes to the user's session will not be persisted to the
                            database. This means that on iterations following a password change, the session key
                            that was returned to the client will not match any session in the django_session table. 

                            Therefore it is insufficient to log in the test client once before the execution of this
                            loop. Instead we have to call django.test.client.Client.force_login on each iteration to
                            ensure the client always has a valid session. We could instead call
                            django.test.client.Client.login, but it significantly impacts execution time. 

                            For good measure/symmetry we also call django.test.client.Client.logout at the end of each
                            iteration.                       
                            """
                            self.client.force_login(self.user, 'django_flex_user.backends.SPModelBackend')

                            response = self.client.patch(self._REST_ENDPOINT_PATH, data=data, format='json')

                            if 'password' in data and not data['password']:
                                """
                                If the supplied password is defined and either None or the empty string,
                                django_flex_user.views.SPUser.put should return HTTP status code HTTP_400_BAD_REQUEST.
                                """
                                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                                self.client.logout()
                            elif ('username' in data and data['username'] is None) and \
                                    ('email' not in data or data['email'] is None) and \
                                    ('phone_number' not in data or data['phone_number'] is None):
                                """
                                If the supplied username is None, and the supplied email and phone_number are
                                simultaneously undefined or None, django_flex_user.views.SPUser.put should return HTTP status
                                code HTTP_400_BAD_REQUEST.
                                """
                                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                                self.client.logout()
                            elif data.get('username') == '' or \
                                    data.get('email') == '' or \
                                    data.get('phone_number') == '':
                                """
                                If any of the supplied username, email or phone_number are the empty string
                                django_flex_user.views.SPUser.put should return HTTP status code HTTP_400_BAD_REQUEST.
                                """
                                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                                self.client.logout()
                            elif (data.get('username') and 'invalid' in data['username']) or \
                                    (data.get('email') and 'invalid' in data['email']) or \
                                    (data.get('phone_number') and 'invalid' in data['phone_number']) or \
                                    (data.get('password') and 'invalid' in data['password']):
                                """
                                If any of the supplied username, email, phone_number or password are defined and
                                invalid, django_flex_user.views.SPUser.put should return HTTP status code
                                HTTP_400_BAD_REQUEST.
                                """
                                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                                self.client.logout()
                            else:
                                """
                                This case encompasses all possible permutations of supplied username, email,
                                phone_number and password for which django_flex_user.views.SPUser.put should return HTTP status
                                code HTTP_200_OK.
                                """
                                self.assertEqual(response.status_code, status.HTTP_200_OK)

                                self.assertEqual(
                                    response.data,
                                    {
                                        'username': data.get('username', 'validUsername'),
                                        'email': data.get('email'),
                                        'email_verified': False,
                                        'phone_number': data.get('phone_number'),
                                        'phone_number_verified': False
                                    }
                                )

                                self.client.logout()
                                transaction.set_rollback(True)

    def test_method_patch_format_multipart_form_data(self):
        from django.db import transaction

        for i in self._ContentType.MultipartFormData.username_values:
            for j in self._ContentType.MultipartFormData.email_values:
                for k in self._ContentType.MultipartFormData.phone_number_values:
                    for l in self._ContentType.MultipartFormData.password_values:

                        data = {}
                        data.update(i)
                        data.update(j)
                        data.update(k)
                        data.update(l)

                        with self.subTest(**data), transaction.atomic():

                            """
                            Special considerations for password changes:

                            By default, updating a user's password invalidates all sessions for the user. To make it so
                            that the user is *not* signed out by a password change, in
                            django_flex_user.serializers.SPUserSerializer.update we call
                            django.contrib.auth.update_session_auth_hash which (1) generates a new session key for the
                            user's current session (2) updates the current session's _auth_user_hash with a value based
                            on the user's new password (because the value of _auth_user_hash for all other sessions are
                            not based on the user's latest password, those sessions are implicitly invalidated). The
                            session key for the newly created session is returned to the client in a 'set-cookie'
                            response header.

                            Because this call is wrapped in a transaction that rolls back all database changes at the
                            end of each iteration, the changes to the user's session will not be persisted to the
                            database. This means that on iterations following a password change, the session key
                            that was returned to the client will not match any session in the django_session table. 

                            Therefore it is insufficient to log in the test client once before the execution of this
                            loop. Instead we have to call django.test.client.Client.force_login on each iteration to
                            ensure the client always has a valid session. We could instead call
                            django.test.client.Client.login, but it significantly impacts execution time. 

                            For good measure/symmetry we also call django.test.client.Client.logout at the end of each
                            iteration.                       
                            """
                            self.client.force_login(self.user, 'django_flex_user.backends.SPModelBackend')

                            response = self.client.patch(self._REST_ENDPOINT_PATH, data=data, format='multipart')

                            if 'password' in data and data['password'] == '':
                                """
                                If the supplied password is defined and blank, django_flex_user.views.SPUser.put should return
                                HTTP status code HTTP_400_BAD_REQUEST.
                                """
                                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                                self.client.logout()
                            elif ('username' in data and data['username'] == '') and \
                                    ('email' not in data or data['email'] == '') and \
                                    ('phone_number' not in data or data['phone_number'] == ''):
                                """
                                If the supplied username is blank, and the supplied email and phone_number are
                                simultaneously undefined or blank, django_flex_user.views.SPUser.put should return HTTP status
                                code HTTP_400_BAD_REQUEST.
                                """
                                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                                self.client.logout()
                            elif (data.get('username') and 'invalid' in data['username']) or \
                                    (data.get('email') and 'invalid' in data['email']) or \
                                    (data.get('phone_number') and 'invalid' in data['phone_number']) or \
                                    (data.get('password') and 'invalid' in data['password']):
                                """
                                If any of the supplied username, email, phone_number or password are defined and
                                invalid, django_flex_user.views.SPUser.put should return HTTP status code HTTP_400_BAD_REQUEST.
                                """
                                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                                self.client.logout()
                            else:
                                """
                                This case encompasses all possible permutations of supplied username, email,
                                phone_number and password for which django_flex_user.views.SPUser.put should return HTTP status
                                code HTTP_200_OK.
                                """
                                self.assertEqual(response.status_code, status.HTTP_200_OK)

                                self.assertEqual(
                                    response.data,
                                    {
                                        'username':
                                            data.get('username', 'validUsername')
                                            if data.get('username') != '' else None,
                                        'email':
                                            data.get('email') if data.get('email') != '' else None,
                                        'email_verified': False,
                                        'phone_number':
                                            data.get('phone_number') if data.get('phone_number') != '' else None,
                                        'phone_number_verified': False
                                    }
                                )

                                self.client.logout()
                                transaction.set_rollback(True)

    def test_method_patch_username_case_insensitivity(self):
        from django_flex_user.models import SPUser

        SPUser.objects.create_user(username='validUsername2', password='validPassword')

        self.client.force_login(self.user, 'django_flex_user.backends.SPModelBackend')

        data = {'username': 'VALIDUSERNAME2'}
        response = self.client.patch(self._REST_ENDPOINT_PATH, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.client.logout()

    def test_method_patch_duplicate_username(self):
        from django_flex_user.models import SPUser

        SPUser.objects.create_user(username='validUsername2', password='validPassword')

        self.client.force_login(self.user, 'django_flex_user.backends.SPModelBackend')

        data = {'username': 'validUsername2'}
        response = self.client.patch(self._REST_ENDPOINT_PATH, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.client.logout()

    def test_method_patch_duplicate_email(self):
        from django_flex_user.models import SPUser

        SPUser.objects.create_user(email='validEmail@example.com', password='validPassword')

        self.client.force_login(self.user, 'django_flex_user.backends.SPModelBackend')

        data = {'email': 'validEmail@example.com'}
        response = self.client.patch(self._REST_ENDPOINT_PATH, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.client.logout()

    def test_method_patch_duplicate_phone_number(self):
        from django_flex_user.models import SPUser

        SPUser.objects.create_user(phone_number='+12025551234', password='validPassword')

        self.client.force_login(self.user, 'django_flex_user.backends.SPModelBackend')

        data = {'phone_number': '+12025551234'}
        response = self.client.patch(self._REST_ENDPOINT_PATH, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.client.logout()

    def test_method_patch_ambiguous_username(self):
        """
        Verify that an email address or phone number cannot form a valid username.

        :return:
        """
        self.client.force_login(self.user, 'django_flex_user.backends.SPModelBackend')

        data = {'username': 'validEmail@example.com'}
        response = self.client.patch(self._REST_ENDPOINT_PATH, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = {'username': '+12025551234'}
        response = self.client.patch(self._REST_ENDPOINT_PATH, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.client.logout()

    def test_method_patch_ambiguous_email(self):
        """
        Verify that a username or phone number cannot form a valid email.

        :return:
        """
        self.client.force_login(self.user, 'django_flex_user.backends.SPModelBackend')

        data = {'email': 'validUsername'}
        response = self.client.patch(self._REST_ENDPOINT_PATH, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = {'email': '+12025551234'}
        response = self.client.patch(self._REST_ENDPOINT_PATH, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.client.logout()

    def test_method_patch_ambiguous_phone_number(self):
        """
        Verify that a username or email address cannot form a valid phone_number.

        :return:
        """
        self.client.force_login(self.user, 'django_flex_user.backends.SPModelBackend')

        data = {'phone_number': 'validUsername'}
        response = self.client.patch(self._REST_ENDPOINT_PATH, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = {'phone_number': 'validEmail@example.com'}
        response = self.client.patch(self._REST_ENDPOINT_PATH, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.client.logout()

    def test_method_patch_normalize_username(self):
        self.client.force_login(self.user, 'django_flex_user.backends.SPModelBackend')

        nfd = 'validUsérname'  # é = U+0065 U+0301
        nfkc = 'validUsérname'  # é = U+00e9

        data = {'username': nfd}
        response = self.client.patch(self._REST_ENDPOINT_PATH, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], nfkc)

        self.client.logout()

    def test_method_patch_normalize_email(self):
        self.client.force_login(self.user, 'django_flex_user.backends.SPModelBackend')

        data = {'email': 'validEmail@bücher.example'}
        response = self.client.patch(self._REST_ENDPOINT_PATH, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'validEmail@xn--bcher-kva.example')

        self.client.logout()

    def test_method_put(self):
        is_authenticated = self.client.login(username='validUsername', password='validPassword')
        self.assertIs(is_authenticated, True)

        response = self.client.put(self._REST_ENDPOINT_PATH)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.logout()

    def test_method_delete(self):
        is_authenticated = self.client.login(username='validUsername', password='validPassword')
        self.assertIs(is_authenticated, True)

        response = self.client.delete(self._REST_ENDPOINT_PATH)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        self.client.logout()

    def test_method_options(self):
        is_authenticated = self.client.login(username='validUsername', password='validPassword')
        self.assertIs(is_authenticated, True)

        response = self.client.options(self._REST_ENDPOINT_PATH)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.logout()
