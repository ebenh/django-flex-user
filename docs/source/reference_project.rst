Reference Project
=================

For convenience, we provide a reference project which implements all of the conventional user-flows for sign up,
sign in and account management. Feel free to use this project to guide your implementation of :mod:`django_flex_user`.

You can try a live version of the reference project `here <https://django-flex-user.herokuapp.com>`_. Or, you can run
the reference project on your local machine.

Running the reference project locally
+++++++++++++++++++++++++++++++++++++

.. note::
    The instructions below assume you're running a POSIX environment (i.e. you're running OS X, Linux or you've
    installed the Microsoft POSIX subsystem).

    The commands below need to be modified if you're running a Windows environment.

#. Clone the git repository:

    .. code-block:: console

        $ mkdir django-flex-user
        $ cd django-flex-user
        $ git clone https://github.com/ebenh/django-flex-user

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
        Replace ellipses with values you obtain by following the instructions below:

        * For Sendgrid, click `here <https://sendgrid.com/>`_ to obtain an API key.

        * For Facebook Login, click `here <https://developers.facebook.com/>`_ to obtain an *"App ID"* and *"Secret Key"*.

        * For Google Sign-In, click `here <https://cloud.google.com/>`_ to obtain an *"OAuth Client ID"* and *"Client Secret"*.

#. Install dependencies:

    .. code-block:: console

        $ python -m pipenv install --dev

#. Activate the ``pipenv`` shell:

    .. code-block:: console

        $ python -m pipenv shell

#. Initialize database tables:

    .. code-block:: console

        $ python manage.py migrate

#. Create a super user:

    .. code-block:: console

        $ python manage.py createsuperuser

#. Run the development server:

    .. code-block:: console

        $ python manage.py runserver

#. Run tests:

    .. code-block:: console

        $ python manage.py test

#. Build the Python package:

    .. code-block:: console

        $ python setup.py sdist

#. Build the docs:

    .. code-block:: console

        $ cd doc
        $ make html
