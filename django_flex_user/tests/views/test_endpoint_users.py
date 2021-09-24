from rest_framework.test import APITestCase, APIClient
from rest_framework import status


class TestFlexUserCreate(APITestCase):
    """
    This class is designed to test django_flex_user.views.FlexUsers
    """
    _CSRF_TOKENS_PATH = '/account/csrf-tokens/'
    _REST_ENDPOINT_PATH = '/account/users/'

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

            phone_values = [{},
                            {'phone': None},
                            {'phone': ''},
                            {'phone': '+12025551234'},
                            {'phone': 'invalidPhoneNumber'}]

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

            phone_values = [{},
                            {'phone': ''},
                            {'phone': '+12025551234'},
                            {'phone': 'invalidPhoneNumber'}]

            password_values = [{},
                               {'password': ''},
                               {'password': 'validPassword'},
                               {'password': 'invalid'}]

    def setUp(self):
        self.client = APIClient(enforce_csrf_checks=True)
        self.csrf_token = self._get_csrf_token()

    def _get_csrf_token(self):
        response = self.client.get(self._CSRF_TOKENS_PATH)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertIsNotNone(response.cookies.get('csrftoken'))

        return response.cookies['csrftoken'].value

    def test_method_get(self):
        response = self.client.get(self._REST_ENDPOINT_PATH)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_method_post_format_application_json(self):
        from django.db import transaction

        for i in self._ContentType.ApplicationJSON.username_values:
            for j in self._ContentType.ApplicationJSON.email_values:
                for k in self._ContentType.ApplicationJSON.phone_values:
                    for l in self._ContentType.ApplicationJSON.password_values:

                        data = {}
                        data.update(i)
                        data.update(j)
                        data.update(k)
                        data.update(l)

                        with self.subTest(**data), transaction.atomic():

                            response = self.client.post(
                                self._REST_ENDPOINT_PATH,
                                data=data,
                                format='json',
                                HTTP_X_CSRFTOKEN=self.csrf_token
                            )

                            if ('username' not in data or data['username'] is None) and \
                                    ('email' not in data or data['email'] is None) and \
                                    ('phone' not in data or data['phone'] is None):
                                """
                                If the supplied username, email, and phone are simultaneously undefined or None,
                                django_flex_user.views.FlexUsers.post should return HTTP status code HTTP_400_BAD_REQUEST.

                                At least one of username, email or phone must be defined and not None.
                                """
                                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                            elif not data.get('password'):
                                """
                                If the supplied password is undefined, None or the empty string,
                                django_flex_user.views.FlexUsers.post should return HTTP status code HTTP_400_BAD_REQUEST.
                                """
                                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                            elif data.get('username') == '' or \
                                    data.get('email') == '' or \
                                    data.get('phone') == '':
                                """
                                If any of the supplied username, email or phone are the empty string
                                django_flex_user.views.FlexUsers.post should return HTTP status code HTTP_400_BAD_REQUEST.
                                """
                                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                            elif (data.get('username') and 'invalid' in data['username']) or \
                                    (data.get('email') and 'invalid' in data['email']) or \
                                    (data.get('phone') and 'invalid' in data['phone']) or \
                                    (data.get('password') and 'invalid' in data['password']):
                                """
                                If any of the supplied username, email, phone or password are defined and
                                invalid, django_flex_user.views.FlexUsers.post should return HTTP status code
                                HTTP_400_BAD_REQUEST.
                                """
                                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                            else:
                                """
                                This case encompasses all possible permutations of supplied username, email,
                                phone and password for which django_flex_user.views.FlexUsers.post should return HTTP status
                                code HTTP_201_CREATED.
                                """
                                self.assertEqual(response.status_code, status.HTTP_201_CREATED)

                                """
                                When REST parameters are valid, django_flex_user.views.FlexUsers calls django.contrib.auth.login
                                which in turn calls django.middleware.csrf.rotate_token which resets the current CSRF
                                token. Therefore we need to extract the new CSRF token from the response.
                                """
                                self.csrf_token = response.cookies['csrftoken'].value

                                self.assertEqual(
                                    response.data,
                                    {
                                        'username': data.get('username'),
                                        'email': data.get('email'),
                                        'email_verified': False if data.get('email') else None,
                                        'phone': data.get('phone'),
                                        'phone_verified': False if data.get('phone') else None
                                    }
                                )

                            transaction.set_rollback(True)

    def test_method_post_format_multipart_form_data(self):
        from django.db import transaction

        for i in self._ContentType.MultipartFormData.username_values:
            for j in self._ContentType.MultipartFormData.email_values:
                for k in self._ContentType.MultipartFormData.phone_values:
                    for l in self._ContentType.MultipartFormData.password_values:

                        data = {}
                        data.update(i)
                        data.update(j)
                        data.update(k)
                        data.update(l)

                        with self.subTest(**data), transaction.atomic():

                            response = self.client.post(
                                self._REST_ENDPOINT_PATH,
                                data=data,
                                format='multipart',
                                HTTP_X_CSRFTOKEN=self.csrf_token
                            )

                            if ('username' not in data or data['username'] == '') and \
                                    ('email' not in data or data['email'] == '') and \
                                    ('phone' not in data or data['phone'] == ''):
                                """
                                If the supplied username, email, and phone are simultaneously undefined or blank,
                                django_flex_user.views.FlexUsers.post should return HTTP status code HTTP_400_BAD_REQUEST.

                                At least one of username, email or phone must be defined and not blank.
                                """
                                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                            elif 'password' not in data or data['password'] == '':
                                """
                                If the supplied password is undefined or blank, django_flex_user.views.FlexUsers.post should return
                                HTTP status code HTTP_400_BAD_REQUEST.
                                """
                                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                            elif (data.get('username') and 'invalid' in data['username']) or \
                                    (data.get('email') and 'invalid' in data['email']) or \
                                    (data.get('phone') and 'invalid' in data['phone']) or \
                                    (data.get('password') and 'invalid' in data['password']):
                                """
                                If any of the supplied username, email, phone or password are defined and
                                invalid, django_flex_user.views.FlexUsers.post should return HTTP status code HTTP_400_BAD_REQUEST.
                                """
                                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                            else:
                                """
                                This case encompasses all possible permutations of supplied username, email,
                                phone and password for which django_flex_user.views.FlexUsers.post should return HTTP status
                                code HTTP_201_CREATED.
                                """
                                self.assertEqual(response.status_code, status.HTTP_201_CREATED)

                                """
                                When REST parameters are valid, django_flex_user.views.FlexUsers calls django.contrib.auth.login
                                which in turn calls django.middleware.csrf.rotate_token which resets the current CSRF
                                token. Therefore we need to extract the new CSRF token from the response.
                                """
                                self.csrf_token = response.cookies['csrftoken'].value

                                self.assertEqual(
                                    response.data,
                                    {
                                        'username': data.get('username') or None,
                                        'email': data.get('email') or None,
                                        'email_verified': False if data.get('email') else None,
                                        'phone': data.get('phone') or None,
                                        'phone_verified': False if data.get('phone') else None
                                    }
                                )

                            transaction.set_rollback(True)

    def test_method_post_username_case_insensitivity(self):
        data = {'username': 'validUsername', 'password': 'validPassword'}
        response = self.client.post(self._REST_ENDPOINT_PATH, data=data, HTTP_X_CSRFTOKEN=self.csrf_token)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        """
        When REST parameters are valid, django_flex_user.views.FlexUsers calls django.contrib.auth.login which in turn calls
        django.middleware.csrf.rotate_token which resets the current CSRF token. Therefore we need to extract the new
        CSRF token from the response.
        """
        self.csrf_token = response.cookies['csrftoken'].value

        data = {'username': 'VALIDUSERNAME', 'password': 'validPassword'}
        response = self.client.post(self._REST_ENDPOINT_PATH, data=data, HTTP_X_CSRFTOKEN=self.csrf_token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_method_post_duplicate_username(self):
        data = {'username': 'validUsername', 'password': 'validPassword'}

        response = self.client.post(self._REST_ENDPOINT_PATH, data=data, HTTP_X_CSRFTOKEN=self.csrf_token)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        """
        When REST parameters are valid, django_flex_user.views.FlexUsers calls django.contrib.auth.login which in turn calls
        django.middleware.csrf.rotate_token which resets the current CSRF token. Therefore we need to extract the new
        CSRF token from the response.
        """
        self.csrf_token = response.cookies['csrftoken'].value

        response = self.client.post(self._REST_ENDPOINT_PATH, data=data, HTTP_X_CSRFTOKEN=self.csrf_token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_method_post_duplicate_email(self):
        data = {'email': 'validEmail@example.com', 'password': 'validPassword'}

        response = self.client.post(self._REST_ENDPOINT_PATH, data=data, HTTP_X_CSRFTOKEN=self.csrf_token)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        """
        When REST parameters are valid, django_flex_user.views.FlexUsers calls django.contrib.auth.login which in turn calls
        django.middleware.csrf.rotate_token which resets the current CSRF token. Therefore we need to extract the new
        CSRF token from the response.
        """
        self.csrf_token = response.cookies['csrftoken'].value

        response = self.client.post(self._REST_ENDPOINT_PATH, data=data, HTTP_X_CSRFTOKEN=self.csrf_token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_method_post_duplicate_phone(self):
        data = {'phone': '+12025551234', 'password': 'validPassword'}

        response = self.client.post(self._REST_ENDPOINT_PATH, data=data, HTTP_X_CSRFTOKEN=self.csrf_token)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        """
        When REST parameters are valid, django_flex_user.views.FlexUsers calls django.contrib.auth.login which in turn calls
        django.middleware.csrf.rotate_token which resets the current CSRF token. Therefore we need to extract the new
        CSRF token from the response.
        """
        self.csrf_token = response.cookies['csrftoken'].value

        response = self.client.post(self._REST_ENDPOINT_PATH, data=data, HTTP_X_CSRFTOKEN=self.csrf_token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_method_post_ambiguous_username(self):
        """
        Verify that an email address or phone number cannot form a valid username.

        :return:
        """
        data = {'username': 'validEmail@example.com', 'password': 'validPassword'}
        response = self.client.post(self._REST_ENDPOINT_PATH, data=data, HTTP_X_CSRFTOKEN=self.csrf_token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = {'username': '+12025551234', 'password': 'validPassword'}
        response = self.client.post(self._REST_ENDPOINT_PATH, data=data, HTTP_X_CSRFTOKEN=self.csrf_token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_method_post_ambiguous_email(self):
        """
        Verify that a username or phone number cannot form a valid email.

        :return:
        """
        data = {'email': 'validUsername', 'password': 'validPassword'}
        response = self.client.post(self._REST_ENDPOINT_PATH, data=data, HTTP_X_CSRFTOKEN=self.csrf_token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = {'email': '+12025551234', 'password': 'validPassword'}
        response = self.client.post(self._REST_ENDPOINT_PATH, data=data, HTTP_X_CSRFTOKEN=self.csrf_token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_method_post_ambiguous_phone(self):
        """
        Verify that a username or email address cannot form a valid phone.

        :return:
        """
        data = {'phone': 'validUsername', 'password': 'validPassword'}
        response = self.client.post(self._REST_ENDPOINT_PATH, data=data, HTTP_X_CSRFTOKEN=self.csrf_token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = {'phone': 'validEmail@example.com', 'password': 'validPassword'}
        response = self.client.post(self._REST_ENDPOINT_PATH, data=data, HTTP_X_CSRFTOKEN=self.csrf_token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_method_post_normalize_username(self):
        nfd = 'validUsérname'  # é = U+0065 U+0301
        nfkc = 'validUsérname'  # é = U+00e9

        data = {'username': nfd, 'password': 'validPassword'}
        response = self.client.post(self._REST_ENDPOINT_PATH, data=data, HTTP_X_CSRFTOKEN=self.csrf_token)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['username'], nfkc)

    def test_method_post_normalize_email(self):
        data = {'email': 'validEmail@bücher.example', 'password': 'validPassword'}
        response = self.client.post(self._REST_ENDPOINT_PATH, data=data, HTTP_X_CSRFTOKEN=self.csrf_token)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['email'], 'validEmail@xn--bcher-kva.example')

    def test_method_post_no_csrf_token(self):
        response = self.client.post(self._REST_ENDPOINT_PATH)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_method_put(self):
        response = self.client.put(self._REST_ENDPOINT_PATH)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_method_patch(self):
        response = self.client.patch(self._REST_ENDPOINT_PATH)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_method_delete(self):
        response = self.client.delete(self._REST_ENDPOINT_PATH)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_method_options(self):
        response = self.client.options(self._REST_ENDPOINT_PATH)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
