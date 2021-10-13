Reference Implementation
========================

For convenience, we provide a test project which implements :mod:`django_flex_user` as a reference implementation. Feel
free to use this project to guide your implementation.

You can try a live version of the reference implementation `here <https://django-flex-user.herokuapp.com>`_.

Alternatively, you can run the reference implementation on your local machine.

Running the reference implementation on your local machine
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

1. Clone the git repository::

    git clone https://github.com/ebenh/django-flex-user django-flex-user

2. Install dependencies::

    python -m pipenv install --dev

3. Activate the `pipenv` shell::

    python -m pipenv shell

4. Initialize database tables::

    python manage.py migrate

5. Create an admin user::

    python manage.py createsuperuser

6. Run the development server::

    python manage.py runserver

7. Run tests::

    python manage.py test

8. Build the Python package::

    python setup.py sdist
