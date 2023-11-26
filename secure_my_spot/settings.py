"""
Django settings for secure_my_spot project.

Generated by 'django-admin startproject' using Django 3.2.5.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

import os
import sys
from pathlib import Path

import dj_database_url
from django.core.management.utils import get_random_secret_key

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
# Determine if we are on local dev or production
environment = os.getenv('DOPPLER_CONFIG')
if environment == "dev":
    # Set debug to true
    DEBUG = True
elif environment == 'prod':
    # Set debug to false
    DEBUG = False
    # Use the X-Forwarded-Proto header to determine if a request is secure
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

    # Set the cookie domains and same-site attribute
    SESSION_COOKIE_DOMAIN = os.getenv('COOKIE_DOMAIN')
    CSRF_COOKIE_DOMAIN = os.getenv('COOKIE_DOMAIN')
    SESSION_COOKIE_SAMESITE = 'Lax'
    CSRF_COOKIE_SAMESITE = 'Lax'

    # Set the Secure attribute for cookies
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
else:
    raise Exception(f'{environment} is not an acceptable value for DOPPLER_CONFIG. It must be either "dev" or "prod".')

# Only allow the `CLIENT_ORIGIN` for CORS
client_origins = os.getenv("CLIENT_ORIGIN")
CORS_ALLOWED_ORIGINS = [origin.strip() for origin in client_origins.split(',')]

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# if env variable is not available during deployment use random secret key
# this work-around allows collectstatic to work during container build when secret key is not yet
# available
# https://stackoverflow.com/questions/59719175/where-to-run-collectstatic-when-deploying-django-app-to-heroku-using-docker
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", default=get_random_secret_key())

allowed_hosts = os.getenv("ALLOWED_HOSTS")
ALLOWED_HOSTS = [host.strip() for host in allowed_hosts.split(',')]

INSTALLED_APPS = [
    "django_extensions",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # [deactivated] add debug toolbar for better debugging
    # "debug_toolbar",
    # rest framework offers additional classes for API support
    "rest_framework",
    "rest_framework.authtoken",
    # adding the main API application of the project
    "app",
    # https://pypi.org/project/django-cors-headers/
    # this is necessary to set up the cors middleware which will respond appropriately to CORS
    # preflight Options requests (see middleware object)
    "corsheaders",
]

# The order of the middleware is very important. In particular, SecurityMiddleware must come first
# immediately followed by WhiteNoiseMiddleware. Violating this restriction will result in static
# assets not being served properly
# https://cheat.readthedocs.io/en/latest/django/static_files.html#the-whitenoise-app
MIDDLEWARE = [
    # https://pypi.org/project/django-cors-headers/
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    # Add WhiteNoise package to middleware so that it serves static assets
    "whitenoise.middleware.WhiteNoiseMiddleware",
    # custom middleware that prints details of incoming http requests to the terminal
    "secure_my_spot.custom_middleware.request_response_logger.RequestLogging",
    # add debug toolbar middleware
    # "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# Normally, if INTERNAL_IP is set (typically 127.0.0.1) and the middleware
# "debug_toolbar.middleware.show_toolbar" is set the debug toolbar shows up automatically when
# DEBUG is set to True. However, containers' ip address changes with every time they are spun up.
# Hence, this manual work-around needs to be applied.
# source: https://stackoverflow.com/questions/26898597/django-debug-toolbar-and-docker
# source: https://django-debug-toolbar.readthedocs.io/en/latest/configuration.html#toolbar-options
def show_toolbar(request):
    return True


if os.getenv("DOPPLER_CONFIG") == "dev":
    DEBUG_TOOLBAR_CONFIG = {
        "SHOW_TOOLBAR_CALLBACK": show_toolbar,
    }

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
DB = {
    "ENGINE": "django.db.backends.postgresql",
    "NAME": os.getenv('DB_NAME'),
    "USER": os.getenv('DB_USER'),
    "PASSWORD": os.getenv('DB_PASSWORD'),
    "HOST": os.getenv('DB_HOST'),
    "PORT": os.getenv('DB_PORT'),
    "OPTIONS": os.getenv('DB_OPTIONS')
}

print(DB)
DATABASES = {"default": DB}

# defines the custom user model
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

REST_FRAMEWORK = {
    # Setting the django rest framework authentication scheme
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.BasicAuthentication",
        # "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ],
    # Only allow requests with valid JSON content (form data not allowed)
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
    ],
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
# https://devcenter.heroku.com/articles/django-assets

STATIC_URL = "/static/"

# create static root for handling / storing static files
STATIC_ROOT = os.path.join(BASE_DIR, "static")

# add compression and caching support for static files
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Custom logger that sends all logs to the console's stdout. This will ensure that print()
# statements and any logging statements are printed to the console and can be read by listening
# to "docker-compose logs -f"
# https://odwyer.software/blog/logging-to-standard-output-with-django
BASE_LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'propagate': True,
        },
        'app': {
            'handlers': ['console'],
            'propagate': True,
        },
    },
}

if environment == "dev":
    LOGGING = BASE_LOGGING
    LOGGING['loggers']['django']['level'] = 'DEBUG'
    LOGGING['loggers']['app']['level'] = 'DEBUG'
elif environment == 'prod':
    LOGGING = BASE_LOGGING
    LOGGING['loggers']['django']['level'] = 'INFO'
    LOGGING['loggers']['app']['level'] = 'INFO'
else:
    raise Exception(f'{environment} is not an acceptable value for DOPPLER_CONFIG. It must be either "dev" or "prod".')

# Celery / RabbitMQ / Redis settings
CELERY_TASK_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ["json", "msgpack"]
if os.getenv("DOPPLER_CONFIG") == "dev":
    # Celery settings
    # broker -> Rabbitmq
    # development RabbitMQ monitor: http://localhost:15672/
    # deployed RabbitMQ monitor: https://jaguar.rmq.cloudamqp.com/#/queues
    rabbit_user = os.getenv("RABBITMQ_DEFAULT_USER")
    rabbit_password = os.getenv("RABBITMQ_DEFAULT_PASS")
    CELERY_BROKER_URL = f"amqp://{rabbit_user}:{rabbit_password}@broker:5672//"

    # backend -> Redis
    redis_password = os.getenv("REDIS_PASSWORD")
    CELERY_RESULT_BACKEND = f"redis://:{redis_password}@redis:6379/0"
else:
    CELERY_BROKER_URL = os.getenv("CLOUDAMQP_URL")
    CELERY_RESULT_BACKEND = os.getenv("REDIS_URL")

    # Set broker pool limit to 1
    # https://devcenter.heroku.com/articles/cloudamqp#celery
    CELERY_BROKER_POOL_LIMIT = 1

# Email client settings
# https://www.sitepoint.com/django-send-email/
EMAIL_HOST = "smtp-relay.sendinblue.com"
EMAIL_PORT = 587
EMAIL_HOST_USER = os.getenv("EMAIL_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_PASSWORD")

# setting up django-redis cache - use the same back-end as Celery
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": CELERY_RESULT_BACKEND,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
        "KEY_PREFIX": "django",
    }
}
