import os
from pathlib import Path
import glob

in_root = Path("/tmp/text_control_videos")
out_root = Path("/tmp/text_control_videos_stride2")
stride = 2

out_root.mkdir(exist_ok=True)
all_imgs = sorted(glob.glob(str(in_root/"*.png")))
for i, in_imgpath in enumerate(all_imgs[::stride]):
    os.system(f"cp {in_imgpath} {out_root}/{i}.png")

# command to generate gif
# gifski --fps 40 --quality 100 /tmp/text_control_videos_stride2/*.png -o teaser.gif
