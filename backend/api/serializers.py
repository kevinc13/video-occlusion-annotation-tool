from django.contrib.auth import get_user_model
from rest_framework import serializers
from api.models import (
    User, Video, Frame, FrameSegmentation, OcclusionAnnotation
)
from .fields import Base64ImageField


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id", "first_name", "last_name", "username", "email"
        )


class OcclusionAnnotationSerializer(serializers.ModelSerializer):
    class Meta:
        model = OcclusionAnnotation
        fields = ("id", "user", "frame", "file", "path")
    
    user = UserSerializer(default=serializers.CurrentUserDefault())
    file = Base64ImageField(max_length=None, use_url=True, write_only=True)
    path = serializers.SerializerMethodField()

    def get_path(self, obj):
        return f"/media/{obj.file}"


class BasicVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ("id", "dataset")


class FrameSegmentationSerializer(serializers.ModelSerializer):
    class Meta:
        model = FrameSegmentation
        fields = ("id", "path")

    path = serializers.SerializerMethodField()

    def get_path(self, obj):
        return f"/media/{obj.file}"


class FrameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Frame
        fields = (
            "id", "path", "sequence_number",
            "frame_segmentation", "occlusion_annotations"
        )

    path = serializers.SerializerMethodField()
    frame_segmentation = FrameSegmentationSerializer(read_only=True)
    occlusion_annotations = OcclusionAnnotationSerializer(read_only=True, many=True)

    def get_path(self, obj):
        return f"/media/{obj.file}"


class FullVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ("id", "dataset", "frames")
    
    frames = FrameSerializer(many=True, read_only=True)
