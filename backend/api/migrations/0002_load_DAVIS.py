from django.db import migrations
from django.db.models import Q
from django.db.models import ObjectDoesNotExist
import os, json


def load_davis(apps, schema_editor):
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__)))))) + "/media/DAVIS"

    Video = apps.get_model("api", "Video")
    Frame = apps.get_model("api", "Frame")
    FrameSegmentation = apps.get_model("api", "FrameSegmentation")
    SegmentedObject = apps.get_model("api", "SegmentedObject")

    skipped_videos = ["hike","mallard-fly","upside-down","mallard-water","dance-twirl","stroller","dog","bear","rollerblade","camel","drift-chicane","parkour","goat","breakdance","car-roundabout","drift-turn","breakdance-flare","drift-straight","paragliding","rallye","flamingo","car-turn","lab-coat","car-shadow","blackswan","elephant"]

    # Read semantics file
    with open(f"{base_dir}/davis_semantics.json") as f:
        objects = json.load(f)
    
    video_names = [d.name for d in os.scandir(
        f"{base_dir}/frames") if d.is_dir()]
    for video_name in video_names:
        video = Video(name=video_name, dataset="DAVIS")
        if video_name in skipped_videos:
            video.skip = True
        video.save()

        for file in os.listdir(f"{base_dir}/frames/{video_name}"):
            if file.endswith(".jpg") or file.endswith(".png"):
                filename = file.split(".")[0]
                frame = Frame(video=video, sequence_number=int(filename),
                              file=f"DAVIS/frames/{video_name}/{file}")
                frame.save()

                if os.path.exists(f"{base_dir}/frame_segmentations/{video_name}/{filename}.png"):
                    seg = FrameSegmentation(
                        frame=frame, file=f"DAVIS/frame_segmentations/{video_name}/{filename}.png")
                    seg.save()

        if video_name in objects.keys():
            for color_number, obj in objects[video_name].items():
                segmentedObject = SegmentedObject(
                    name=obj, video=video, color_number=int(color_number))
                segmentedObject.save()


def remove_davis(apps, schema_editor):
    Video = apps.get_model("api", "Video")
    Video.objects.filter(dataset="DAVIS").delete()


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(load_davis, remove_davis)
    ]
