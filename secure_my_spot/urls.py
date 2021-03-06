"""secure_my_spot URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import debug_toolbar
from django.contrib import admin
from django.urls import include, path

# from django.contrib.staticfiles.storage import staticfiles_storage
# from django.views.generic import RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("app.urls")),
    # debug toolbar is currently deactivated
    path("__debug__", include(debug_toolbar.urls)),
    # [the below code does resolve the favicon issue in the browser but als cause some tests ti
    # fail
    # delivers the favicon during dev and prod mode
    # https://www.ordinarycoders.com/blog/article/add-a-custom-favicon-to-your-django-web-app
    # path("favicon.ico", RedirectView.as_view(url=staticfiles_storage.url("image/favicon.ico"))),
]
