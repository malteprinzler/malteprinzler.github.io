import os
from pathlib import Path

# joker
ids = [4, 6, 16, 19, 26, 31, 36, 38]
in_root = Path("/fast/mprinzler/TRANSFER_FILES/Joker/data/THE_JOKER_DATASET/CROSSREENACT_SWEEP_NORMALRANGE")
out_root = Path("../static/videos/more_results")
out_prefix = "joker_"

# mixedeval
ids = [11, 19, 25, 26, 27]
in_root = Path("/fast/mprinzler/TRANSFER_FILES/Joker/data/MIXED_DATASET/MIXED_SWEEP_EVAL_CROSSREENACT_NORMALRANGE")
out_root = Path("../static/videos/more_results")
out_prefix = "mixedeval_"

# ood
ids = [2, 3, 8, 9, 14, 17, 19, 21, 22, 24, 27, 28, 30, 32]
in_root = Path("/fast/mprinzler/TRANSFER_FILES/Joker/data/OOD_CROSSREENACT/OOD_CROSSREENACT_SWEEP")
out_root = Path("../static/videos/more_results")
out_prefix = "ood_"

for i in ids:
    in_file = in_root / f"{i:03d}" / "sequences" / "CAM_SWEEP" / "frame_00000" / "ref_img" / "ref_img.jpg"
    out_file = out_root / (out_prefix + f"{i}.jpg")
    os.system(f"cp {in_file} {out_file}")
