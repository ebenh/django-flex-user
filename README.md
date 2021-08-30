# django-flex-user

## Getting Started
1. Clone the repository

        git clone https://github.com/ebenh/django-flex-user

2. Install dependencies

        py -m pipenv install --dev

3. Activate the `pipenv` shell

        py -m pipenv shell

4. Initialize database tables

        py manage.py migrate

5. Create an admin user

        py manage.py createsuperuser

7. Run the development server

        py manage.py runserver

8. Run tests

        py manage.py test