#!/bin/bash

python manage.py collectstatic --noinput
gunicorn secure_my_spot.wsgi:application --bind 0.0.0.0:$PORT
