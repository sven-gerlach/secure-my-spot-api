#!/bin/bash

python manage.py collectstatic --noinput
python manage.py makemigrations --noinput
python manage.py migrate --noinput
gunicorn secure_my_spot.wsgi:application --bind 0.0.0.0:$PORT