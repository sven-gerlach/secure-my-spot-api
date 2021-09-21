from django.http import JsonResponse
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView

from ..serializers import UserSerializer


class SignUpView(APIView):
    """Sign-up view"""

    def post(self, request):
        """
        Create and save a new user in the database
        """
        # parse JSON data
        data = JSONParser().parse(request)
        data = data["credentials"]

        # validate password == password_confirmation
        if data.get("password") != data.get("password_confirmation"):
            return JsonResponse({"password": ["Passwords don't match."]}, status=400)

        # serialize data provided
        serializer = UserSerializer(data=data)

        # check serializer is valid
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)
