Reference Project
=================

For convenience, we provide a reference project which implements all of the conventional user-flows for sign up,
sign in and account management. Feel free to use this project to guide your implementation of :mod:`django_flex_user`.

You can try a live version of the reference project `here <https://django-flex-user.herokuapp.com>`__. Or, you can run
the reference project on your local machine.

Running the reference project locally
+++++++++++++++++++++++++++++++++++++

#. Clone the git repository:

    .. code-block:: bash

        $ git clone https://github.com/ebenh/django-flex-user
        $ cd django-flex-user

#. Create an ``.env`` file with the following contents:

    .. code-block:: text

        DEBUG=1
        SECRET_KEY=NOT_FOR_PRODUCTION_x-)pi_7=*sqrnqeo!!p*986207*n4-!4xa&hd(lq&@@p0m=4*(
        SENDGRID_API_KEY=...
        SOCIAL_AUTH_FACEBOOK_KEY=...
        SOCIAL_AUTH_FACEBOOK_SECRET=...
        SOCIAL_AUTH_GOOGLE_OAUTH2_KEY=...
        SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET=...

    .. note::
        Replace ellipses with the values you obtain by following the instructions below:

        * For Sendgrid, click `here <https://sendgrid.com/>`__ to obtain an API key.

        * For Facebook Login, click `here <https://developers.facebook.com/>`__ to obtain an *"App ID"* and *"Secret Key"*.

        * For Google Sign-In, click `here <https://cloud.google.com/>`__ to obtain an *"OAuth Client ID"* and *"Client Secret"*.

#. Install dependencies:

    .. code-block:: bash

        $ python3 -m pipenv install --dev

    .. note::
        On Windows, the command to execute Python is ``py``.

#. Activate the ``pipenv`` shell:

    .. code-block:: bash

        $ python3 -m pipenv shell

#. Initialize database tables:

    .. code-block:: bash

        $ python3 manage.py migrate

#. Create a super user:

    .. code-block:: bash

        $ python3 manage.py createsuperuser

#. Run the development server:

    .. code-block:: bash

        $ python3 manage.py runserver

#. Run tests:

    .. code-block:: bash

        $ python3 manage.py test

    To run tests against multiple versions of Python and Django:

    .. code-block:: bash

        $ python3 tox

    .. note::
        To skip Python interpreters which are not installed run ``tox --skip-missing-interpreters``. To run tests
        against Python 3.8 only for example, run ``tox -e py38``. To run tests against Python 3.8 and Django 3.2 only,
        run ``tox -e py38-django32``.

#. Build the Python package:

    .. code-block:: bash

        $ python3 setup.py sdist

#. Build the docs:

    .. code-block:: bash

        $ cd doc
        $ sphinx-apidoc -o source ../django_flex_user ../django_flex_user/tests ../django_flex_user/migrations
        $ make html

    .. note::
        If you're running Git Bash on Windows, the last command should be ``./make.bat html``
