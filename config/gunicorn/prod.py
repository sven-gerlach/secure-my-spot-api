"""Gunicorn *production* config file"""
import multiprocessing

# Django WSGI application path in pattern MODULE_NAME:VARIABLE_NAME
wsgi_app = "secure_my_spot.wsgi:application"
# The granularity of Error log outputs
loglevel = "error"
# The number of worker processes for handling requests
workers = multiprocessing.cpu_count() * 2
# The socket to bind
bind = "0.0.0.0:3001"
# Restart workers when code changes (development only!)
reload = False
# Write access and error info to /var/log
accesslog = errorlog = "/var/log/gunicorn/dev.log"
# Redirect stdout/stderr to log file
capture_output = True
# PID file so you can easily fetch process ID
pidfile = "/var/run/gunicorn/dev.pid"
# Daemonize the Gunicorn process (detach & enter background)
daemon = False
