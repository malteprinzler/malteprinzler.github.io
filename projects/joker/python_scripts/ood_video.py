import os
from pathlib import Path
from tokenize import triple_quoted
import tqdm
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import ffmpeg
import matplotlib.pyplot as plt

from projects.joker.python_scripts.change_raw_img_framerate import stride
from projects.joker.python_scripts.teaser_video import ref_img

# ref_img = Image.open("/home/mprinzler/MINIMAL_TRANSFER_FILES/Joker/Code/VIDEO/textcontrol/ref_0_1.png")
# control_img = Image.open("/home/mprinzler/MINIMAL_TRANSFER_FILES/Joker/Code/VIDEO/textcontrol/normal_0_1.png")
# video_1_path = "/home/mprinzler/MINIMAL_TRANSFER_FILES/Joker/Code/VIDEO/textcontrol/horizontalsweep_0.avi"
# video_2_path = "/home/mprinzler/MINIMAL_TRANSFER_FILES/Joker/Code/VIDEO/textcontrol/horizontalsweep_1.avi"
# text_1 = "Prompt: \"A woman with her tongue sticking out\""
# text_2 = "Prompt: \"A woman with a big smile\""
# out_path = "/home/mprinzler/Projects/webpage/malteprinzler.github.io/projects/joker/static/videos/text_control_videos_0_1.mp4"

# ref_img = Image.open("/home/mprinzler/MINIMAL_TRANSFER_FILES/Joker/Code/VIDEO/textcontrol/ref_13_15.png")
# control_img = Image.open("/home/mprinzler/MINIMAL_TRANSFER_FILES/Joker/Code/VIDEO/textcontrol/normal_13_15.png")
# video_1_path = "/home/mprinzler/MINIMAL_TRANSFER_FILES/Joker/Code/VIDEO/textcontrol/horizontalsweep_13.avi"
# video_2_path = "/home/mprinzler/MINIMAL_TRANSFER_FILES/Joker/Code/VIDEO/textcontrol/horizontalsweep_15.avi"
# text_1 = "Prompt: \"A man with an angry face\""
# text_2 = "Prompt: \"A man looking very sad\""
# out_path = "/home/mprinzler/Projects/webpage/malteprinzler.github.io/projects/joker/static/videos/text_control_videos_13_15.mp4"

# ref_img = Image.open("/home/mprinzler/MINIMAL_TRANSFER_FILES/Joker/Code/VIDEO/textcontrol/ref_24_25.png")
# control_img = Image.open("/home/mprinzler/MINIMAL_TRANSFER_FILES/Joker/Code/VIDEO/textcontrol/normal_24_25.png")
# video_1_path = "/home/mprinzler/MINIMAL_TRANSFER_FILES/Joker/Code/VIDEO/textcontrol/horizontalsweep_24.avi"
# video_2_path = "/home/mprinzler/MINIMAL_TRANSFER_FILES/Joker/Code/VIDEO/textcontrol/horizontalsweep_25.avi"
# text_1 = "Prompt: \"A man with a shocked expression\""
# text_2 = "Prompt: \"A man with an angry face\""
# out_path = "/home/mprinzler/Projects/webpage/malteprinzler.github.io/projects/joker/static/videos/text_control_videos_24_25.mp4"

ref_imgs = [
    Image.open("/home/mprinzler/Projects/webpage/malteprinzler.github.io/projects/joker/static/videos/more_results/ood_14.jpg"),
    Image.open("/home/mprinzler/Projects/webpage/malteprinzler.github.io/projects/joker/static/videos/more_results/ood_17.jpg"),
    Image.open("/home/mprinzler/Projects/webpage/malteprinzler.github.io/projects/joker/static/videos/more_results/ood_24.jpg"),
]
video_paths = [
    "/home/mprinzler/Projects/webpage/malteprinzler.github.io/projects/joker/static/videos/more_results/ood_smallslowspiral_14.avi.mp4",
    "/home/mprinzler/Projects/webpage/malteprinzler.github.io/projects/joker/static/videos/more_results/ood_smallslowspiral_17.avi.mp4",
    "/home/mprinzler/Projects/webpage/malteprinzler.github.io/projects/joker/static/videos/more_results/ood_smallslowspiral_24.avi.mp4",
]
out_path = "./more_results.mp4"

stride = 2
tmp_out_path = "/tmp/text_control_videos_ood"
text_bbx_pad = 4
video_pad = 8
fps = 30

ref_imgs = [i.convert("RGB") for i in ref_imgs]

import imageio.v3 as iio

# bulk read all frames
# Warning: large videos will consume a lot of memory (RAM)
all_frames = []
for path in video_paths:
    all_frames.append(list(iio.imread(path, plugin="pyav"))[::stride])
nframes = len(all_frames[0])
nvideos = len(video_paths)
tile_height, tile_width = ref_imgs[0].height, ref_imgs[0].width
out_frames = list()
os.system(f"rm -rf {tmp_out_path}")
os.makedirs(tmp_out_path, exist_ok=True)
for i in tqdm.tqdm(range(nframes)):
    out_canvas = np.zeros(
        (tile_height*2 + video_pad, tile_width*nvideos + video_pad*(nvideos-1) , 3),
        dtype=np.uint8) + 255
    canvas_height, canvas_width, _ = out_canvas.shape

    for j in range(nvideos):
        # drawing reference image
        x_ref, y_ref = j * ref_imgs[0].width + j*video_pad, 0
        x_vid, y_vid = x_ref, y_ref + video_pad + ref_imgs[0].height
        out_canvas[y_ref:y_ref+tile_height, x_ref:x_ref+tile_width] = np.array(ref_imgs[j])
        out_canvas[y_vid:y_vid+tile_height, x_vid:x_vid+tile_width] = np.array(all_frames[j][i])


    Image.fromarray(out_canvas).save(os.path.join(tmp_out_path, f"{i:03d}.png"))
Path(out_path).parent.mkdir(parents=True, exist_ok=True)
os.system(
    f"/usr/bin/ffmpeg -pattern_type glob -framerate {fps} -i '{tmp_out_path}/*.png' -c:v libx264 -crf 23 -profile:v baseline -level 3.0 -pix_fmt yuv420p -c:a aac -ac 2 -b:a 128k -movflags faststart {out_path} -y")
