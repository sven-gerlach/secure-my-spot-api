# https://testdriven.io/blog/deploying-django-to-heroku-with-docker/
# https://testdriven.io/blog/dockerizing-django-with-postgres-gunicorn-and-nginx/

# pull official base image
FROM python:3.8-alpine

# add maintainer / contact details to container in form of key=value metadata
LABEL maintainer_name="Sven Gerlach" \
      maintainer_email="svengerlach@me.com"

ENV PYTHONUNBUFFERED=1

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

# expose port 3001
EXPOSE 3001

# create static folder manually such that the ownership can be changed to the "app" user
# failung to do that will result in a permission denied error upon executing the collectstatic command
RUN adduser --disabled-password --no-create-home app && \
    mkdir static && \
    chown -R app:app static

USER app

# adding /scripts to PATH ensures that scripts can be executed without prepending the path to the script
ENV PATH="/scripts:${PATH}"

CMD ["sh", "scripts/run_dev.sh"]