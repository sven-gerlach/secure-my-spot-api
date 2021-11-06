"""Custom middleware that logs incoming requests and other detail to the console"""

from datetime import datetime


class RequestLogging:
    """Log incoming requests to the terminal"""

    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        print("=====================INCOMING REQUEST=====================")
        print(f"Time: {datetime.now(): %H:%M}")
        print(f"Method: {request.method}")
        print(f"Path: {request.path}")
        print(f"Body: {request.body}")
        print(f"Header: {request.headers}")
        print(f"Params: {request.GET}")
        print("===========================END============================")

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        print("====================OUTGOING RESPONSE=====================")
        print(f"Time: {datetime.now(): %H:%M}")
        print(f"Content: {response.content}")
        print(f"Headers: {response.headers}")
        print(f"Status Code: {response.status_code}")
        print("===========================END============================")

        return response
