from django.http import HttpResponse


def signup_view(request):
    """Sign-up view"""
    html = "<h1>Sign-Up</h1>"
    return HttpResponse(html)
