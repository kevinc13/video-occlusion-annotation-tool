"""
Project URL configuration
"""
from django.urls import path, re_path, include
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # API specific paths are set by the 'urls.py' file in the 'api' directory
    path("",
         auth_views.LoginView.as_view(
             template_name="login.html", 
             redirect_authenticated_user=True,
             extra_context = { "ENV_NAME": settings.ENV_NAME }),
         name="login"),
    path("logout/", auth_views.LogoutView.as_view()),
    path("api/", include("api.urls")),
    path("admin/", admin.site.urls),

    # Path for the Vue Single-Page Application (SPA)
    re_path(r'^app/(.*)$', 
            login_required(TemplateView.as_view(
                template_name="spa.html",
                extra_context={ "ENV_NAME": settings.ENV_NAME })),
            name="app")
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
