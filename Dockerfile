# https://testdriven.io/blog/deploying-django-to-heroku-with-docker/
# https://testdriven.io/blog/dockerizing-django-with-postgres-gunicorn-and-nginx/

# pull official base image
FROM python:3.8-alpine

# add maintainer / contact details to container in form of key=value metadata
LABEL maintainer="svengerlach@me.com"

# set work directory
WORKDIR /app

# set environment variables
# prevents Python from writing pyc files to disc
ENV PYTHONDONTWRITEBYTECODE 1
# prevents Python from buffering stdout and stderr (
ENV PYTHONUNBUFFERED 1
ENV DEBUG 0

# install psycopg2 (needs to be installed manually rather than through executing the Pipfile
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

# add and run as non-root user
RUN adduser -D svengerlach
USER svengerlach

RUN python manage.py collectstatic --noinput --clear