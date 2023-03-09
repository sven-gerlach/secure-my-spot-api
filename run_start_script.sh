#!/usr/bin/env sh

# Waiting for db connection to be established
python manage.py wait_for_db

# Run db migrations
python manage.py migrate

# start development server
python manage.py runserver 0.0.0.0:8000