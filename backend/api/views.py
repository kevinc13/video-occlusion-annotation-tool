from django.http import HttpResponse
from django.shortcuts import render

from rest_framework import generics, mixins
from rest_framework.permissions import IsAuthenticated

from .models import User, Video, OcclusionAnnotation
from .serializers import (
    BasicVideoSerializer, FullVideoSerializer, FrameSerializer,
    FrameSegmentationSerializer, UserSerializer, OcclusionAnnotationSerializer
)


class VideoList(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = BasicVideoSerializer
    queryset = Video.objects.all()
    pagination_class = None


class VideoDetail(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = FullVideoSerializer
    queryset = Video.objects.all()
    lookup_url_kwarg = "video_id"


class UserList(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer
    queryset = User.objects.all()
    pagination_class = None


class SelfDetail(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer
    
    def get_object(self):
        return self.request.user


class UserDetail(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_url_kwarg = "user_id"


class AnnotationList(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = OcclusionAnnotationSerializer
    queryset = OcclusionAnnotation.objects.all()


class AnnotationDetail(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = OcclusionAnnotationSerializer
    queryset = OcclusionAnnotation.objects.all()
    lookup_url_kwarg = "occlusion_annotation_id"
