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
    OcclusionFlag = apps.get_model("api", "OcclusionFlag")
    
    # Read meta.json
    with open(f"{base_dir}/meta.json") as f:
        meta = json.load(f)

    palette = []
    with open(f"{base_dir}/palette.txt") as f:
        for line in f:
            palette.append([int(n) for n in line.split(" ")])
    
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
                    

        for color_index, obj in meta["videos"][video_name]["objects"].items():
            obj_name = obj["category"]
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
                        file=f"YouTube-VOS-Train/frame_segmentations/{video_name}/{color_index}_{obj}/{filename}.png")
                    seg.save()


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
