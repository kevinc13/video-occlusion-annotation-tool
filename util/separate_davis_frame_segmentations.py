import os
from PIL import Image
import cv2
import json
import numpy as np

root_dir = "../media/DAVIS"

def main():
    all_segs_folder = os.path.join(root_dir, "frame_segmentations")
    video_list = os.listdir(all_segs_folder)
    object_data = {}
    with open(os.path.join(root_dir, "objects.json")) as f:
        object_data = json.load(f)

    for video_name in video_list:
        if video_name not in object_data: continue

        seg_folder = os.path.join(all_segs_folder, video_name)
        print("Separating out frame segmentations for " + video_name)

        for obj_color_index, obj_name in object_data[video_name].items():
            obj_seg_dir = os.path.join(seg_folder, "{}_{}".format(obj_color_index, obj_name))
            if not os.path.exists(obj_seg_dir):
                os.mkdir(obj_seg_dir)

        palette = None
        seg_list = sorted([f for f in os.listdir(seg_folder) if os.path.isfile(os.path.join(seg_folder, f))])
        for full_seg_file in seg_list:
            if not full_seg_file[0].isdigit(): continue
            print("Frame: " + full_seg_file)
            full_seg = Image.open(os.path.join(seg_folder, full_seg_file))
            if palette is None:
                palette = full_seg.getpalette()

            for obj_color_index, obj_name in object_data[video_name].items():
                obj_seg_file = os.path.join(
                    seg_folder,
                    "{}_{}".format(obj_color_index, obj_name),
                    full_seg_file
                )

                if os.path.exists(obj_seg_file): continue

                obj_seg_arr = np.array(full_seg)
                if len(obj_seg_arr.shape) == 3:
                    # Convert from RGBA to P
                    full_seg = Image.fromarray(obj_seg_arr).convert("P")
                    full_seg.putpalette(palette)
                    obj_seg_arr = np.array(full_seg)

                obj_seg_arr[obj_seg_arr != int(obj_color_index)] = 0
                obj_seg = Image.fromarray(np.squeeze(obj_seg_arr), mode="P")
                obj_seg.putpalette(palette)
                obj_seg.save(obj_seg_file)

        print("")



if __name__ == "__main__":
    main()