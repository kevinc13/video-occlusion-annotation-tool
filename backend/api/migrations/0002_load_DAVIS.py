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

    # Read semantics file
    with open(f"{base_dir}/objects.json") as f:
        objects = json.load(f)

    palette = []
    with open(f"{base_dir}/palette.txt") as f:
        for line in f:
            palette.append([int(n) for n in line.split(" ")])

    video_names = [d.name for d in os.scandir(
        f"{base_dir}/frames") if d.is_dir()]
    for video_name in video_names:
        video = Video(name=video_name, dataset="DAVIS")
        video.save()

        for file in os.listdir(f"{base_dir}/frames/{video_name}"):
            if file.endswith(".jpg") or file.endswith(".png"):
                filename = file.split(".")[0]
                frame = Frame(video=video, sequence_number=int(filename),
                              file=f"DAVIS/frames/{video_name}/{file}")
                frame.save()

        if video_name in objects.keys():
            for color_index, obj in objects[video_name].items():
                color_index = int(color_index)
                hex_color = '#%02x%02x%02x' % tuple(palette[color_index])
                segmented_object = SegmentedObject(
                    name=obj, video=video, color_index=color_index,
                    color=hex_color)
                segmented_object.save()

                for file in os.listdir(f"{base_dir}/frame_segmentations/{video_name}/{color_index}_{obj}"):
                    if file.endswith(".jpg") or file.endswith(".png"):
                        filename = file.split(".")[0]
                        frame = Frame.objects.get(video__name=video_name, sequence_number=int(filename))
                        seg = FrameSegmentation(
                            frame=frame,
                            segmented_object=segmented_object,
                            file=f"DAVIS/frame_segmentations/{video_name}/{color_index}_{obj}/{filename}.png")
                        seg.save()



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
