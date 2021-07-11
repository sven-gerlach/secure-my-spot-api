# source: https://testdriven.io/blog/deploying-django-to-heroku-with-docker/

# pull official base image
FROM python:3.8-alpine

# add maintainer / contact details to container in form of key=value metadata
LABEL maintainer="svengerlach@me.com"

# set work directory
WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DEBUG 0

# install psycopg2
RUN apk update \
    && apk add gcc libc-dev python3-dev musl-dev \
    && apk add postgresql-dev \
    && pip install psycopg2 \
    # install bash (alpine ships with ash)
    # access bash with "docker exec -it <container-name> /bin/bash"
    && apk add --no-cache --upgrade bash

# source: https://jonathanmeier.io/using-pipenv-with-docker/
# install pipenv and install dependencies
RUN pip install pipenv
COPY Pipfile .
COPY Pipfile.lock .
RUN pipenv install --system --deploy --pre

# copy project
COPY . .

## collect static files
#RUN python manage.py collectstatic --noinput

# add and run as non-root user
RUN adduser -D myuser
USER myuser

## run gunicorn
#CMD gunicorn hello_django.wsgi:application --bind 0.0.0.0:$PORT