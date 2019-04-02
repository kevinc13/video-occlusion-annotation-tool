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
     path("videos/<int:video_id>", views.VideoDetail.as_view(),
          name="video-detail"),
     path("segmented_objects/<int:segmented_object_id>",
          views.SegmentedObjectDetail.as_view(),
          name="segmented-object-detail"),
     path("occlusion_flags/",
          views.OcclusionFlagList.as_view(),
          name="occlusion-flag-list"),
     path("occlusion_flags/<int:occlusion_flag_id>",
          views.OcclusionFlagDetail.as_view(),
          name="occlusion-flag-detail"),
     path("annotations/",
          views.AnnotationList.as_view(), name="annotation-list"),
     path("annotations/<int:occlusion_annotation_id>",
          views.AnnotationDetail.as_view(), name="annotation-detail"),
     path("users/", views.UserList.as_view(), name="user-list"),
     path("users/self/", views.SelfDetail.as_view(), name="self-detail"),
     path("users/<int:user_id>/",
          views.UserDetail.as_view(), name="user-detail"),
     path("summary/", views.SummaryView.as_view(), name="summary"),
     path("export/",
          views.export_annotations_csv_view, name="export-annotations")
]

urlpatterns = format_suffix_patterns(urlpatterns)
