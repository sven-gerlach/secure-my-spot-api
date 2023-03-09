# https://testdriven.io/blog/deploying-django-to-heroku-with-docker/
# https://testdriven.io/blog/dockerizing-django-with-postgres-gunicorn-and-nginx/

# pull official base image
FROM python:3.8-alpine

# add maintainer / contact details to container in form of key=value metadata
LABEL maintainer_name="Sven Gerlach" \
      maintainer_email="svengerlach@me.com"

# set work directory
# Github Actions recommends not to set WORKDIR
# https://docs.github.com/en/actions/creating-actions/dockerfile-support-for-github-actions#workdir
# not clear at all how else to set the working directory
WORKDIR /app

# install psycopg2 (needs to be installed manually rather than through executing the Pipfile
RUN apk update && apk add \
    gcc \
    libc-dev \
    python3-dev \
    musl-dev \
    postgresql-dev \
    vim \
    # install bash (alpine ships with ash)
    # access bash with "docker exec -it <container-name> /bin/bash"
    bash --no-cache --upgrade

# source: https://jonathanmeier.io/using-pipenv-with-docker/
# install pipenv and install dependencies
RUN pip install \
    pipenv \
    psycopg2
COPY Pipfile Pipfile.lock ./
RUN pipenv install --system --deploy --pre

# copy project
COPY . .

# expose port 8000
EXPOSE 8000

RUN adduser --disabled-password --no-create-home app

USER app