#!/bin/sh
set -e

# Change to the backend directory
cd /app/backend

# Run migrations automatically
if [ ! -f "db.sqlite3" ]; then
    echo "Database not found. Creating new database..."
    python manage.py makemigrations
    python manage.py migrate
fi

# Execute the command passed to the container
python manage.py runserver 0.0.0.0:8000
