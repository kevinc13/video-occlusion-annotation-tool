from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
import os

from .storage import OverwriteStorage


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

    name = models.CharField(max_length=100)
    dataset = models.CharField(max_length=100)
    

class VideoFlag(models.Model):
    class Meta:
        db_table = "video_flags"
        verbose_name = "video_flag"
        verbose_name_plural = "video_flags"

    video = models.ForeignKey(Video,
                              related_name="video_flags",
                              related_query_name="video_flag",
                              on_delete=models.CASCADE)
    user = models.ForeignKey(User,
                             related_name="video_flags",
                             related_query_name="video_flags",
                             on_delete=models.CASCADE)
    FLAG_CHOICES = (
        ('NO', 'No occlusions in video'),
        ('UN', 'Unsure')
    )

    flag = models.CharField(
        max_length=2,
        choices=FLAG_CHOICES
    )


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


class SegmentedObject(models.Model):
    class Meta:
        db_table = "segmented_objects"
        verbose_name = "segmented_object"
        verbose_name_plural = "segmented_objects"

    # category = models.ForeignKey(SegmentedObjectCategory,
    #                              on_delete=models.CASCADE,
    #                              related_name="segmented_objects",
    #                              related_query_name="segmented_object")
    # frame_segmentation = models.ForeignKey(FrameSegmentation,
    #                                        on_delete=models.CASCADE,
    #                                        related_name="segmented_objects",
    #                                        related_query_name="segmented_object")
    name = models.CharField(max_length=30)
    color = models.CharField(max_length=30)
    color_index = models.IntegerField()
    video = models.ForeignKey(Video,
                              on_delete=models.CASCADE,
                              related_name="segmented_objects",
                              related_query_name="segmented_object")


class FrameSegmentation(models.Model):
    class Meta:
        db_table = "frame_segmentations"
        verbose_name = "frame_segmentations"
        verbose_name_plural = "frame_segmentation"

    frame = models.ForeignKey(Frame,
                              on_delete=models.CASCADE,
                              related_name="frame_segmentations",
                              related_query_name="frame_segmentation")
    segmented_object = models.ForeignKey(
        SegmentedObject,
        on_delete=models.CASCADE,
        related_name="frame_segmentations",
        related_query_name="frame_segmentation")
    file = models.CharField(max_length=300)


def annotation_directory_path(instance, orig_filename):
    ext = orig_filename.split(".")[-1]
    return "{}/occlusion_annotations/{}/{}_{}/{}_{}.{}".format(
        instance.frame.video.dataset,
        instance.frame.video.name,
        instance.segmented_object.color_index,
        instance.segmented_object.name,
        instance.frame.sequence_number,
        instance.user.username,
        ext
    )


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
    segmented_object = models.ForeignKey(
        SegmentedObject,
        on_delete=models.CASCADE,
        related_name="occlusion_annotations",
        related_query_name="occlusion_annotation",
        blank=True,
        null=True,
        default=None
    )

    def save(self, *args, **kwargs):
        try:
            this = OcclusionAnnotation.objects.get(
                user=self.user,
                frame=self.frame,
                segmented_object=self.segmented_object)
            this.delete()
        except: pass
        super(OcclusionAnnotation, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        path = os.path.join(settings.MEDIA_ROOT, self.file.name)
        if os.path.exists(path):
            os.remove(path)
        super(OcclusionAnnotation, self).delete(*args,**kwargs)
    


# class OcclusionFlag(models.Model):
#     class Meta:
#         db_table = "occlusion_flags"
#         verbose_name = "occlusion_flag"
#         verbose_name_plural = "occlusion_flags"
    
#     frame = models.ForeignKey(Frame,
#                               on_delete=models.CASCADE,
#                               related_name="occlusion_flags",
#                               related_query_name="occlusion_flag")
#     segmented_object = models.ForeignKey(
#         SegmentedObject,
#         on_delete=models.CASCADE,
#         related_name="occlusion_flags",
#         related_query_name="occlusion_flag"
#     )
#     user = models.ForeignKey(User,
#                              on_delete=models.CASCADE,
#                              related_name="occlusion_flags",
#                              related_query_name="occlusion_flag")
#     occluded = models.PositiveSmallIntegerField()
    # 0 = not occluded, 1 = partially occluded, 2 = occluded
