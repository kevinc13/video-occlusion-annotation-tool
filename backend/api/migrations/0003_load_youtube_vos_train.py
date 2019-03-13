from django.db import migrations
from django.db.models import Q
from django.db.models import ObjectDoesNotExist
import os, json


def load_youtube_vos_train(apps, schema_editor):
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__)))))) + "/media/YouTube-VOS-Train"

    Video = apps.get_model("api", "Video")
    Frame = apps.get_model("api", "Frame")
    FrameSegmentation = apps.get_model("api", "FrameSegmentation")
    SegmentedObject = apps.get_model("api", "SegmentedObject")
    
    # Read meta.json
    with open(f"{base_dir}/meta.json") as f:
        meta = json.load(f)
    
    video_names = [d.name for d in os.scandir(
        f"{base_dir}/frames") if d.is_dir()]
    for video_name in video_names:
        video = Video(name=video_name, dataset="YouTube-VOS-Train")
        video.save()

        for file in os.listdir(f"{base_dir}/frames/{video_name}"):
            if file.endswith(".jpg") or file.endswith(".png"):
                filename = file.split(".")[0]
                frame = Frame(video=video, sequence_number=int(filename),
                              file=f"YouTube-VOS-Train/frames/{video_name}/{file}")
                frame.save()

                if os.path.exists(f"{base_dir}/frame_segmentations/{video_name}/{filename}.png"):
                    seg = FrameSegmentation(
                        frame=frame, file=f"YouTube-VOS-Train/frame_segmentations/{video_name}/{filename}.png")
                    seg.save()

        for obj in meta["videos"][video_name]["objects"].values():
            segmentedObject = SegmentedObject(
                name=obj["category"], video=video)
            segmentedObject.save()


def remove_youtube_vos_train(apps, schema_editor):
    Video = apps.get_model("api", "Video")
    Video.objects.filter(dataset="YouTube-VOS-Train").delete()


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_load_DAVIS'),
    ]

    operations = [
        migrations.RunPython(load_youtube_vos_train, remove_youtube_vos_train)
    ]
