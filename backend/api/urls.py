"""
API url patterns
"""
from django.urls import path, re_path, include
from . import views

urlpatterns = [
    path("hello", views.hello_world)
]