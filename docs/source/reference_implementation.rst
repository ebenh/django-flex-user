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

        py -m pipenv install --dev

3. Activate the `pipenv` shell::

        py -m pipenv shell

4. Initialize database tables::

        py manage.py migrate

5. Create an admin user::

        py manage.py createsuperuser

6. Run the development server::

        py manage.py runserver

7. Run tests::

        py manage.py test

8. Build the Python package::

        py setup.py sdist
