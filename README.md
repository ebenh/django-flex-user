# django-flex-user

A flexible user model for Django designed to **maximize sign-up conversion**.

Enables users to up with a **username**, **email address**, **phone number** or any combination thereof. Users can also
sign up using an **OAuth** provider like Facebook or Google.

**Batteries included.** Email and phone verification, password reset, and **REST API** included "in the box".

Click [here](https://django-flex-user.herokuapp.com/) to see a **demo**.

## Getting Started

1. Clone the repository

        mkdir django-flex-user
        cd django-flex-user
        git clone https://github.com/ebenh/django-flex-user

2. Install dependencies

        py -m pipenv install --dev

3. Activate the `pipenv` shell

        py -m pipenv shell

4. Initialize database tables

        py manage.py migrate

5. Create an admin user

        py manage.py createsuperuser

6. Run the development server

        py manage.py runserver

7. Run tests

        py manage.py test

8. Build the Python package

        py setup.py sdist