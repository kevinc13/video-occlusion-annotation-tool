"""
Initializes API-specific URLs

Author: Kevin Chen
"""

from django.conf.urls import url
from django.urls import path, re_path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    path("videos/", views.VideoList.as_view(), name="video-list"),
    path("videos/<str:video_id>", views.VideoDetail.as_view(),
         name="video-detail"),
    path("annotations/",
         views.AnnotationList.as_view(), name="annotation-list"),
    path("annotations/<int:occlusion_annotation_id>",
         views.AnnotationDetail.as_view(), name="annotation-detail"),
    path("users/", views.UserList.as_view(), name="user-list"),
    path("users/self/", views.SelfDetail.as_view(), name="self-detail"),
    path("users/<int:user_id>/",
         views.UserDetail.as_view(), name="user-detail")
]

urlpatterns = format_suffix_patterns(urlpatterns)
