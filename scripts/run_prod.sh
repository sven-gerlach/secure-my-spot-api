#!/usr/bin/env sh

set -e

# Waiting for db connection to be established
python manage.py wait_for_db

# Run db migrations
python manage.py migrate

# collect static files
python manage.py collectstatic --noinput

# start production server
gunicorn secure_my_spot.wsgi:application --bind 0.0.0.0:3001