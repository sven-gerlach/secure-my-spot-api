# https://testdriven.io/blog/deploying-django-to-heroku-with-docker/
# https://testdriven.io/blog/dockerizing-django-with-postgres-gunicorn-and-nginx/

# pull official base image
FROM python:3.9

# add maintainer / contact details to container in form of key=value metadata
LABEL maintainer_name="Sven Gerlach" \
      maintainer_email="svengerlach@me.com"

ENV PYTHONUNBUFFERED=1

# set work directory
# Github Actions recommends not to set WORKDIR
# https://docs.github.com/en/actions/creating-actions/dockerfile-support-for-github-actions#workdir
# not clear at all how else to set the working directory
WORKDIR /app

# install poetry
RUN pip install poetry

# copy poetry files
COPY ../pyproject.toml ../poetry.lock ./

# Project initialization:
# --no-root: Do not install the root package (the project itself).
# --no-dev: Do not install the dev dependencies.
# --no-interaction: Do not ask any interactive question.
RUN poetry config virtualenvs.create false \
    && poetry install --only main --no-interaction --no-ansi

# copy project
COPY .. .

# create static folder manually such that the ownership can be changed to the "app" user
# failing to do that will result in a permission denied error upon executing the collectstatic command
RUN adduser --disabled-password --no-create-home app && \
    mkdir static && \
    chown -R app:app static

# create log and pid file directories
RUN mkdir -pv /var/log/gunicorn && \
    mkdir -pv /var/run/gunicorn && \
    touch /var/log/gunicorn/dev.log && \
    touch /var/run/gunicorn/dev.pid && \
    chown -cR app:app /var/log/gunicorn && \
    chown -cR app:app /var/run/gunicorn

USER app

# adding /scripts to PATH ensures that scripts can be executed without prepending the path to the script
ENV PATH="/scripts:${PATH}"

CMD ["sh", "scripts/run_prod.sh"]