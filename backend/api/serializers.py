from django.contrib.auth import get_user_model
from rest_framework import serializers
from api.models import (
    User, Video, Frame, FrameSegmentation, OcclusionAnnotation,
    SegmentedObject, OcclusionFlag
)
from .fields import Base64ImageField


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id", "first_name", "last_name", "username", "email"
        )


class SegmentedObjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = SegmentedObject
        fields = ("id", "name", "color", "color_index")


class OcclusionAnnotationSerializer(serializers.ModelSerializer):
    class Meta:
        model = OcclusionAnnotation
        fields = (
            "id", "user", "frame", "file", "path", "segmented_object",
            "segmented_object_id"
        )
    
    user = UserSerializer(default=serializers.CurrentUserDefault())
    file = Base64ImageField(max_length=None, use_url=True, write_only=True)
    path = serializers.SerializerMethodField()
    segmented_object = SegmentedObjectSerializer(read_only=True)
    segmented_object_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        queryset=SegmentedObject.objects.all(),
        required=False)

    def get_path(self, obj):
        return f"/media/{obj.file}"

    def create(self, validated_data):
        if "segmented_object_id" in validated_data:
            segmented_object_id = validated_data.pop("segmented_object_id")
            validated_data["segmented_object"] = segmented_object_id
        return self.Meta.model.objects.create(**validated_data)


class BasicOcclusionAnnotationSerializer(serializers.ModelSerializer):
    class Meta:
        model = OcclusionAnnotation
        fields = (
            "id", "file", "path", "segmented_object", "segmented_object_id"
        )

    file = Base64ImageField(max_length=None, use_url=True, write_only=True)
    path = serializers.SerializerMethodField()
    segmented_object = SegmentedObjectSerializer(read_only=True)
    segmented_object_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        queryset=SegmentedObject.objects.all(),
        required=False)

    def get_path(self, obj):
        return f"/media/{obj.file}"


class OcclusionFlagSerializer(serializers.ModelSerializer):
    class Meta:
        model = OcclusionFlag
        fields = ("id", "frame", "segmented_object_id", "user", "occluded")
    
    user = UserSerializer(default=serializers.CurrentUserDefault())
    segmented_object_id = serializers.PrimaryKeyRelatedField(
        queryset=SegmentedObject.objects.all(),
        required=False)

    def create(self, validated_data):
        if "segmented_object_id" in validated_data:
            segmented_object_id = validated_data.pop("segmented_object_id")
            validated_data["segmented_object"] = segmented_object_id
        return self.Meta.model.objects.create(**validated_data)


class BasicOcclusionFlagSerializer(serializers.ModelSerializer):
    class Meta:
        model = OcclusionFlag
        fields = ("id", "segmented_object_id", "occluded")


class BasicVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = (
            "id", "name", "dataset", "skip",
            "n_annotations", "n_user_annotations",
            "n_objects"
        )
    
    n_annotations = serializers.SerializerMethodField()
    n_user_annotations = serializers.SerializerMethodField()
    n_objects = serializers.SerializerMethodField()

    def get_n_annotations(self, obj):
        return OcclusionAnnotation.objects.filter(
            frame__video=obj.id).count()
    
    def get_n_user_annotations(self, obj):
        return OcclusionAnnotation.objects.filter(
            frame__video=obj.id,
            user=self.context['request'].user).count()

    def get_n_objects(self, obj):
        return SegmentedObject.objects.filter(video_id=obj.id).count()


class FrameSegmentationSerializer(serializers.ModelSerializer):
    class Meta:
        model = FrameSegmentation
        fields = ("id", "path", "segmented_object_id")

    path = serializers.SerializerMethodField()

    def get_path(self, obj):
        return f"/media/{obj.file}"


class FrameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Frame
        fields = (
            "id", "path", "sequence_number", "frame_segmentations",
            "user_occlusion_annotations", "user_occlusion_flags"
        )

    path = serializers.SerializerMethodField()
    frame_segmentations = FrameSegmentationSerializer(read_only=True, many=True)
    user_occlusion_annotations = serializers.SerializerMethodField()
    user_occlusion_flags = serializers.SerializerMethodField()

    def get_path(self, obj):
        return f"/media/{obj.file}"

    def get_user_occlusion_annotations(self, obj):
        queryset = OcclusionAnnotation.objects.filter(
            frame=obj, user=self.context["request"].user)
        serializer = BasicOcclusionAnnotationSerializer(queryset, many=True)
        return serializer.data
    
    def get_user_occlusion_flags(self, obj):
        queryset = OcclusionFlag.objects.filter(
            frame=obj, user=self.context["request"].user)
        serializer = BasicOcclusionFlagSerializer(queryset, many=True)
        return serializer.data



class FullVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ("id", "name", "dataset", "skip", "frames", "segmented_objects")
    
    segmented_objects = SegmentedObjectSerializer(many=True, read_only=True)
    frames = FrameSerializer(many=True, read_only=True)
