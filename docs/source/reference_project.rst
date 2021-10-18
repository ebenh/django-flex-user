Reference Project
=================

For convenience, we provide a reference project which implements all of the conventional user-flows for sign up,
sign in and account management. Feel free to use this project to guide your implementation of :mod:`django_flex_user`.

You can try a live version of the reference project `here <https://django-flex-user.herokuapp.com>`_. Or, you can run
the reference project on your local machine.

Running the reference project locally
+++++++++++++++++++++++++++++++++++++

.. note::
    The instructions below assume you're running a POSIX-compliant shell (i.e. you're running OS X, Linux or you've
    installed the Microsoft POSIX subsystem).

    The commands below need to be modified if you're running the Windows command shell (i.e. cmd.exe).

#. Clone the git repository:

    .. code-block:: console

        $ mkdir django-flex-user
        $ cd django-flex-user
        $ git clone https://github.com/ebenh/django-flex-user

#. Create an ``.env`` file:

    .. code-block:: console

        $ touch .env
        $ echo "DEBUG=1" >> .env
        $ echo "SECRET_KEY=..." >> .env
        $ echo "SENDGRID_API_KEY=..." >> .env
        $ echo "SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET=..." >> .env
        $ echo "SOCIAL_AUTH_FACEBOOK_SECRET=..." >> .env

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
