#!/bin/sh

# Apply Django migrations
python manage.py makemigrations
python manage.py migrate

# Start the Django development server (or your application)
exec "$@"
