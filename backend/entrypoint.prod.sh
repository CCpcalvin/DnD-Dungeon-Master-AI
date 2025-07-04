#!/bin/sh

# Change to the backend directory
cd /backend

# Run migrations automatically
if [ ! -f "db.sqlite3" ]; then
    echo "Database not found. Creating new database..."
    python manage.py makemigrations
    python manage.py migrate
fi

# Collect static files
python manage.py collectstatic --noinput

# Execute gunicorn
gunicorn backend.wsgi:application --bind 0.0.0.0:8001
