#!/usr/bin/env sh

set -e

# Waiting for db connection to be established
python manage.py wait_for_db

# Run db migrations
python manage.py migrate

# start development server
gunicorn -c config/gunicorn/dev.py