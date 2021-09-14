from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt


@method_decorator(csrf_exempt, name="dispatch")
class SignUp(View):
    def post(self, request):
        response = request.body
        return JsonResponse({"response": response})

