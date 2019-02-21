from django.db import migrations
from django.db.models import Q
from django.db.models import ObjectDoesNotExist
import os, json


def load_youtube_vos(apps, schema_editor):
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))))) + "/media/YouTube-VOS"

    Video = apps.get_model("api", "Video")
    Frame = apps.get_model("api", "Frame")
    FrameSegmentation = apps.get_model("api", "FrameSegmentation")
    SegmentedObject = apps.get_model("api", "SegmentedObject")
    SegmentedObjectCategory = apps.get_model("api", "SegmentedObjectCategory")
    
    # Read meta.json
    with open(f"{base_dir}/meta.json") as f:
        meta = json.load(f)
    
    video_ids = [d.name for d in os.scandir(
        f"{base_dir}/frames") if d.is_dir()]
    for video_id in video_ids:
        video = Video(id=video_id, dataset="YouTube-VOS")
        video.save()

        for file in os.listdir(f"{base_dir}/frames/{video_id}"):
            if file.endswith(".jpg") or file.endswith(".png"):
                filename = file.split(".")[0]
                frame = Frame(video=video, sequence_number=int(filename),
                              file=f"YouTube-VOS/frames/{video_id}/{file}")
                frame.save()

                if os.path.exists(f"{base_dir}/frame_segmentations/{video_id}/{filename}.png"):
                    seg = FrameSegmentation(
                        frame=frame, file=f"YouTube-VOS/frame_segmentations/{video_id}/{filename}.png")
                    seg.save()

        for obj in meta["videos"][video_id]["objects"].values():
            try:
                objectCategory = SegmentedObjectCategory.objects.get(
                    name=obj["category"])
            except ObjectDoesNotExist:
                objectCategory = SegmentedObjectCategory(name=obj["category"])
                objectCategory.save()
            
            frame_seq_numbers = [int(f) for f in obj["frames"]]
            
            for frame_seq_number in frame_seq_numbers:
                seg = FrameSegmentation.objects.get(
                    frame__video=video,
                    frame__sequence_number=frame_seq_number)
                segmentedObject = SegmentedObject(
                    category=objectCategory, frame_segmentation=seg)
                segmentedObject.save()


def remove_youtube_vos(apps, schema_editor):
    Video = apps.get_model("api", "Video")
    Video.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(load_youtube_vos, remove_youtube_vos)
    ]
