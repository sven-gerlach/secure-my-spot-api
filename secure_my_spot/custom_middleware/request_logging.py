"""Custom middleware that logs incoming requests and other detail to the console"""
from datetime import datetime
import json


class RequestLogging:
    """Log incoming requests to the terminal"""
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        dt = datetime.now()

        print("=====================INCOMING REQUEST=====================")
        print(f"Time: {dt: %H:%M}")
        print(f"Method: {request.method}")
        print(f"Body: {request.body}")
        print(f"Params: {request.content_params}")
        print("===========================END============================")

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response
