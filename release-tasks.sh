# Tasks to be run during the "release phase" of deployment on Heroku ...

# Load the "case-insensitive field" extension on our PostgeSQL database
psql $DATABASE_URL -c "CREATE EXTENSION IF NOT EXISTS citext;"

# Apply our Django project's database migrations
python manage.py migrate