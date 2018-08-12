"""
Project URL configuration
"""
from django.urls import path, re_path, include
from django.views.generic import TemplateView
from django.contrib import admin
from django.conf import settings

urlpatterns = [
    # API specific paths are set by the 'urls.py' file in the 'api' directory
    path("api/", include("api.urls")),
    path("admin/", admin.site.urls),

    # Path for the Vue Single-Page Application (SPA)
    re_path(r'^app/(.*)$', 
            TemplateView.as_view(
                template_name="spa.html",
                extra_context={ "ENV_NAME": settings.ENV_NAME }),
            name="app")
]
