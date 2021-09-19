"""
Django settings for secure_my_spot project.

Generated by 'django-admin startproject' using Django 3.2.5.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

import os
from pathlib import Path

import dj_database_url
import django_heroku

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Determine if we are on local dev or production
if os.getenv("ENV") == "development":
    # from the .env file as the database name
    DB = {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.environ.get("DB_HOST"),
        "PORT": os.environ.get("DB_PORT"),
    }
    # Set debug to true
    DEBUG = True
    # Only allow locally running client at port 3000 for CORS
    CORS_ORIGIN_WHITELIST = [
        "http://localhost:3000",
    ]
else:
    # If we are on production, use the dj_database_url package
    # to locate the database based on Heroku setup
    DATABASE_URL = os.environ.get("DATABASE_URL")

    # setting SSL required to True causes the test runner on Gitlab CI to fail
    DB = dj_database_url.config(conn_max_age=500)
    # Set debug to false
    DEBUG = False
    # Only allow the `CLIENT_ORIGIN` for CORS
    CORS_ORIGIN_WHITELIST = [os.getenv("CLIENT_ORIGIN")]


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY", default="foo")

ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django_extensions",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework.authtoken",
    "app",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # Add WhiteNoise package to middleware so that it serves static assets
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "secure_my_spot.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "secure_my_spot.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {"default": DB}

AUTH_USER_MODEL = "app.User"

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Setting the django rest framework authentication scheme
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ]
}


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = "/static/"

# create static root for handling / storing static files
STATIC_ROOT = os.path.join(BASE_DIR, "static")

# Extra places for collectstatic to find static files.
# STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"),)

# add compression and caching support for static files
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# automatically configure DATABASE_URL, ALLOWED_HOSTS, WhiteNoise (for static assets), Logging, and
# Heroku CI
# Source: https://github.com/heroku/django-heroku
# django_heroku.settings(locals(), databases=False)
