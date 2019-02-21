from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
import os


class User(AbstractUser):
    class Meta:
        db_table = "users"
        verbose_name = "user"
        verbose_name_plural = "users"


class Video(models.Model):
    class Meta:
        db_table = "videos"
        verbose_name = "video"
        verbose_name_plural = "videos"

    id = models.CharField(max_length=30, primary_key=True)
    dataset = models.CharField(max_length=100)


class Frame(models.Model):
    class Meta:
        db_table = "frames"
        verbose_name = "frame"
        verbose_name_plural = "frames"

    video = models.ForeignKey(Video,
                              related_name="frames",
                              related_query_name="frame",
                              on_delete=models.CASCADE)
    sequence_number = models.IntegerField()
    file = models.CharField(max_length=300)


class FrameSegmentation(models.Model):
    class Meta:
        db_table = "frame_segmentations"
        verbose_name = "frame_segmentations"
        verbose_name_plural = "frame_segmentation"

    frame = models.OneToOneField(Frame, on_delete=models.CASCADE,
                                 related_name="frame_segmentation")
    file = models.CharField(max_length=300)


class SegmentedObjectCategory(models.Model):
    class Meta:
        db_table = "segmented_object_categories"
        verbose_name = "segmented_object_category"
        verbose_name_plural = "segmented_object_categories"

    name = models.CharField(max_length=30)


class SegmentedObject(models.Model):
    class Meta:
        db_table = "segmented_objects"
        verbose_name = "segmented_object"
        verbose_name_plural = "segmented_objects"

    category = models.ForeignKey(SegmentedObjectCategory,
                                 on_delete=models.CASCADE,
                                 related_name="segmented_objects",
                                 related_query_name="segmented_object")
    frame_segmentation = models.ForeignKey(FrameSegmentation,
                                           on_delete=models.CASCADE,
                                           related_name="segmented_objects",
                                           related_query_name="segmented_object")


def annotation_directory_path(instance, orig_filename):
    ext = orig_filename.split(".")[-1]
    filename = f"{instance.frame.video.id}_{instance.frame.sequence_number}_{instance.user.username}.{ext}"
    return f"{instance.frame.video.dataset}/occlusion_annotations/{instance.frame.video.id}/{filename}"


class OcclusionAnnotation(models.Model):
    class Meta:
        db_table = "occlusion_annotations"
        verbose_name = "occlusion_annotation"
        verbose_name_plural = "occlusion_annotations"

    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name="occlusion_annotations",
                             related_query_name="occlusion_annotation")
    frame = models.ForeignKey(Frame,
                              on_delete=models.CASCADE,
                              related_name="occlusion_annotations",
                              related_query_name="occlusion_annotation")
    file = models.ImageField(upload_to=annotation_directory_path,
                             max_length=300)

    def delete(self, *args, **kwargs):
        os.remove(os.path.join(settings.MEDIA_ROOT, self.file.name))
        super(OcclusionAnnotation, self).delete(*args,**kwargs)
    

