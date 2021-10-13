Reference Implementation
========================

For convenience, we provide a test project which implements :mod:`django_flex_user` as a reference implementation. Feel
free to use the test project to guide your implementation.

You can try a live version of the reference implementation `here <https://django-flex-user.herokuapp.com>`_.

Alternatively, you can run the reference implementation on your local machine.

Running the reference implementation locally
++++++++++++++++++++++++++++++++++++++++++++

1. Clone the git repository::

    mkdir django-flex-user
    cd django-flex-user
    git clone https://github.com/ebenh/django-flex-user

2. Create an ``.env`` file::

    touch .env
    echo "DEBUG=1" >> .env
    echo "SECRET_KEY=..." >> .env
    echo "SENDGRID_API_KEY=..." >> .env
    echo "SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET=..." >> .env
    echo "SOCIAL_AUTH_FACEBOOK_SECRET=..." >> .env

3. Install dependencies::

    python -m pipenv install --dev

4. Activate the `pipenv` shell::

    python -m pipenv shell

5. Initialize database tables::

    python manage.py migrate

6. Create an admin user::

    python manage.py createsuperuser

7. Run the development server::

    python manage.py runserver

8. Run tests::

    python manage.py test

9. Build the Python package::

    python setup.py sdist

10. Build the docs::

    cd doc
    make html
