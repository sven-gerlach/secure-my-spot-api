"""Gunicorn *development* config file"""

# Django WSGI application path in pattern MODULE_NAME:VARIABLE_NAME
wsgi_app = "secure_my_spot.wsgi:application"
# The granularity of Error log outputs
loglevel = "debug"
# The number of worker processes for handling requests
workers = 2
# The socket to bind
bind = "0.0.0.0:3001"
# Restart workers when code changes (development only!)
reload = True
# Daemonize the Gunicorn process (detach & enter background)
daemon = False
