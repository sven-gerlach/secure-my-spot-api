#!/usr/bin/env sh

set -e

# Waiting for db connection to be established
python manage.py wait_for_db

# make migrations
python manage.py makemigrations

# Run db migrations
python manage.py migrate

# collect static files
python manage.py collectstatic --noinput

# start production server
# if using an NGINX proxy, use the following command: gunicorn -c config/gunicorn/prod.py
gunicorn secure_my_spot.wsgi:application