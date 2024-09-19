import os
from pathlib import Path
from tokenize import triple_quoted
import tqdm
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import ffmpeg
import matplotlib.pyplot as plt

ref_img = Image.open("/home/mprinzler/MINIMAL_TRANSFER_FILES/Joker/Code/VIDEO/textcontrol/ref_0_1.png")
control_img = Image.open("/home/mprinzler/MINIMAL_TRANSFER_FILES/Joker/Code/VIDEO/textcontrol/normal_0_1.png")
video_1_path = "/home/mprinzler/MINIMAL_TRANSFER_FILES/Joker/Code/VIDEO/textcontrol/horizontalsweep_0.avi"
video_2_path = "/home/mprinzler/MINIMAL_TRANSFER_FILES/Joker/Code/VIDEO/textcontrol/horizontalsweep_1.avi"
text_1 = "Prompt: \"A woman with her tongue sticking out\""
text_2 = "Prompt: \"A woman with a big smile\""
out_path = "/home/mprinzler/Projects/webpage/malteprinzler.github.io/projects/joker/static/videos/text_control_videos_0_1.mp4"

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

# ref_img = Image.open("/home/mprinzler/MINIMAL_TRANSFER_FILES/Joker/Code/PAPER/FIGURES/Teaser/new_joker_imgs/ref_img.jpg")
# control_img = Image.open("/home/mprinzler/MINIMAL_TRANSFER_FILES/Joker/Code/PAPER/FIGURES/Teaser/new_joker_imgs/cam_190.jpg")
# video_1_path = "/home/mprinzler/MINIMAL_TRANSFER_FILES/Joker/Code/VIDEO/videos/joker_angry_teaser.avi"
# video_2_path = "/home/mprinzler/MINIMAL_TRANSFER_FILES/Joker/Code/VIDEO/videos/joker_tongue_out_teaser.avi"
# text_1 = "Prompt: \"A man with an angry expression\""
# text_2 = "Prompt: \"A man with his tongue sticking out\""
# out_path = "/home/mprinzler/Projects/webpage/malteprinzler.github.io/projects/joker/static/videos/text_control_videos_teaser.mp4"


tmp_out_path = "/tmp/text_control_videos"
fnt = ImageFont.truetype("/home/mprinzler/Downloads/noto-sans/NotoSans-Bold.ttf", size=24)
prompt_fnt = ImageFont.truetype("/home/mprinzler/Downloads/noto-sans/NotoSans-Italic.ttf", size=22)
text_bbx_pad = 4
video_pad = 8

ref_img = ref_img.resize((int((512 - video_pad) / 2), int((512 - video_pad) / 2))).convert("RGBA")
control_img = control_img.resize((int((512 - video_pad) / 2), int((512 - video_pad) / 2))).convert("RGBA")


def draw_textbox_on_img(img, text, font, xy, halign, valign, textfill, bbxfill, bbxpad):
    if isinstance(bbxpad, int) or isinstance(bbxpad, float):
        bbxpad = [bbxpad] * 4
    draw = ImageDraw.Draw(img)
    _, _, w, h = draw.textbbox((0, 0), text, font=font)
    if halign == "left":
        x0 = xy[0]
    elif halign == "right":
        x0 = xy[0] - w
    elif halign == "center":
        x0 = xy[0] - w / 2
    else:
        raise ValueError

    if valign == "top":
        y0 = xy[1]
    elif valign == "bottom":
        y0 = xy[1] - h
    elif valign == "center":
        y0 = xy[1] - h / 2
    else:
        raise ValueError

    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.rectangle([(x0 - bbxpad[0], y0 - bbxpad[1]), (x0 + w + bbxpad[2], y0 + h + bbxpad[3])],
                           fill=bbxfill)
    img = Image.alpha_composite(img.convert("RGBA"), overlay)
    draw = ImageDraw.Draw(img)
    draw.text((x0, y0), text, font=font, fill=textfill)
    return img


# adding labels to images
ref_img = draw_textbox_on_img(ref_img, "Reference Image", font=fnt, xy=(ref_img.width / 2, ref_img.height - 5),
                              halign="center", valign="bottom", textfill="white", bbxfill=(0, 0, 0, 118),
                              bbxpad=4).convert("RGB")
control_img = draw_textbox_on_img(control_img, "3DMM Control", font=fnt, xy=(ref_img.width / 2, ref_img.height - 5),
                                  halign="center", valign="bottom", textfill="white", bbxfill=(0, 0, 0, 118),
                                  bbxpad=4).convert("RGB")

import imageio.v3 as iio

# bulk read all frames
# Warning: large videos will consume a lot of memory (RAM)
frames1 = iio.imread(video_1_path, plugin="pyav")
frames2 = iio.imread(video_2_path, plugin="pyav")
nframes = len(frames1)

out_frames = list()
os.system(f"rm -rf {tmp_out_path}")
os.makedirs(tmp_out_path, exist_ok=True)
for i in tqdm.tqdm(range(nframes)):
    out_canvas = np.zeros(
        (frames1[0].shape[0], ref_img.width + video_pad + frames1[0].shape[1] + video_pad + frames2[0].shape[1], 3),
        dtype=np.uint8) + 255
    canvas_height, canvas_width, _ = out_canvas.shape
    captioned_frame1 = draw_textbox_on_img(Image.fromarray(frames1[i]), text_1, font=prompt_fnt,
                                           xy=(frames1[i].shape[1] / 2, 10), halign="center",
                                           valign="top", textfill="white", bbxfill=(0, 0, 0, 118), bbxpad=4).convert(
        "RGB")
    captioned_frame2 = draw_textbox_on_img(Image.fromarray(frames2[i]), text_2, font=prompt_fnt,
                                           xy=(frames2[i].shape[1] / 2, 10), halign="center",
                                           valign="top", textfill="white", bbxfill=(0, 0, 0, 118), bbxpad=4).convert(
        "RGB")

    out_canvas[:ref_img.height, :ref_img.width] = np.array(ref_img)
    out_canvas[canvas_height - control_img.height:, :control_img.width] = np.array(control_img)
    out_canvas[:, ref_img.width + video_pad:ref_img.width + video_pad + frames1[i].shape[1]] = np.array(
        captioned_frame1)
    out_canvas[:, canvas_width - frames2[i].shape[1]:] = np.array(captioned_frame2)

    Image.fromarray(out_canvas).save(os.path.join(tmp_out_path, f"{i:03d}.png"))
Path(out_path).parent.mkdir(parents=True, exist_ok=True)
os.system(f"/usr/bin/ffmpeg -pattern_type glob -framerate 30 -i '{tmp_out_path}/*.png' -c:v libx264 -crf 23 -profile:v baseline -level 3.0 -pix_fmt yuv420p -c:a aac -ac 2 -b:a 128k -movflags faststart {out_path} -y")