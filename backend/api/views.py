import csv

from django.http import StreamingHttpResponse
from django.http import HttpResponse
from django.shortcuts import render

from rest_framework import generics, mixins
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import OrderingFilter

from .models import (
    User, Video, OcclusionAnnotation, SegmentedObject, OcclusionFlag
)
from .serializers import (
    BasicVideoSerializer, FullVideoSerializer, FrameSerializer,
    FrameSegmentationSerializer, UserSerializer, OcclusionAnnotationSerializer,
    SegmentedObjectSerializer, OcclusionFlagSerializer
)


class VideoList(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = BasicVideoSerializer
    queryset = Video.objects.all()
    pagination_class = PageNumberPagination
    filter_backends = (OrderingFilter,)

    def paginate_queryset(self, queryset):
        """
        Return a single page of results, or `None` if pagination is disabled.
        """
        if self.paginator is None:
            return None
        
        limit = self.request.query_params.get("limit", None)
        if limit is not None:
            self.pagination_class.page_size = limit

        return self.paginator.paginate_queryset(queryset, self.request, view=self)


class VideoDetail(generics.RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = FullVideoSerializer
    queryset = Video.objects.all()
    lookup_url_kwarg = "video_id"


class SegmentedObjectDetail(generics.RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = SegmentedObjectSerializer
    queryset = SegmentedObject.objects.all()
    lookup_url_kwarg = "segmented_object_id"


class OcclusionFlagList(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = OcclusionFlagSerializer
    queryset = OcclusionFlag.objects.all()


class OcclusionFlagDetail(generics.RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = OcclusionFlagSerializer
    queryset = OcclusionFlag.objects.all()
    lookup_url_kwarg = "occlusion_flag_id"


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


class AnnotationDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = OcclusionAnnotationSerializer
    queryset = OcclusionAnnotation.objects.all()
    lookup_url_kwarg = "occlusion_annotation_id"


class SummaryView(APIView):
    def get(self, request):
        n_users = User.objects.count()
        n_datasets = Video.objects.values("dataset").distinct().count()
        n_videos = Video.objects.count()
        n_occ_annotations = OcclusionAnnotation.objects.count()

        return Response({
            "n_users": n_users,
            "n_datasets": n_datasets,
            "n_videos": n_videos,
            "n_occlusion_annotations": n_occ_annotations
        })


class Echo:
    def write(self, value):
        return value

def generate_annotation_rows():
    yield ["occlusion_annotation_id", "sequence_number",
           "occlusion_annotation_file", "frame_file", "segmentation_file",
           "object_id", "object_name", "object_color", "object_color_index"
           "user_id", "username", "video_id", "video_name", "dataset"]
    annotations = OcclusionAnnotation.objects.all()
    for annotation in annotations:
        yield [
            annotation.id,
            annotation.frame.sequence_number,
            "/".join(annotation.file.name.split("/")[1:]),
            "/".join(annotation.frame.file.split("/")[1:]),
            "/".join(annotation.frame.frame_segmentation.file.split("/")[1:]),
            annotation.segmented_object.id,
            annotation.segmented_object.name,
            annotation.segmented_object.color,
            annotation.segmented_object.color_index,
            annotation.user.id,
            annotation.user.username,
            annotation.frame.video.id,
            annotation.frame.video.name,
            annotation.frame.video.dataset
        ]

def export_annotations_csv_view(request):
    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    response = StreamingHttpResponse(
        (writer.writerow(row) for row in generate_annotation_rows()),
        content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename="occlusion_annotations.csv"'
    return response
