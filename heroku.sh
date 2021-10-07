psql $DATABASE_URL -c "CREATE EXTENSION IF NOT EXISTS citext;"
python manage.py migrate