#!/usr/bin/env python3

import os
import subprocess
from datetime import datetime, timezone

import pandas as pd

image_path = snakemake.input["image"]
diameter_csv = snakemake.input["diameter_csv"]
seg_npy = snakemake.output["seg_npy"]

attempt = int(os.environ.get("SNAKEMAKE_ATTEMPT", "1"))

image_base = os.path.splitext(os.path.basename(image_path))[0]
preproc_dir = os.path.dirname(image_path)
segmentation_dir = os.path.dirname(seg_npy)
results_dir = os.path.dirname(segmentation_dir)
benchmark_dir = os.path.join(results_dir, "benchmarks")

if "diameter" in snakemake.params:
    diameter = snakemake.params["diameter"]
else:
    diameter = pd.read_csv(diameter_csv)["Average_Diameter"].iloc[0]

use_gpu = bool(snakemake.config.get("cellpose_use_gpu", False))
do_3d = bool(snakemake.config.get("cellpose_do_3D", False))

batch_size = "8"
tile = False
if attempt > 1:
    batch_size = "4"
    tile = True

print(
    f"[cellpose] attempt={attempt} "
    f"batch_size={batch_size} tile={tile} "
    f"do_3D={do_3d} use_gpu={use_gpu}"
)

os.makedirs(benchmark_dir, exist_ok=True)
log_path = os.path.join(benchmark_dir, f"run_cellpose_{image_base}.log")
with open(log_path, "a", encoding="utf-8") as log_file:
    log_file.write(
        f"attempt={attempt} "
        f"batch_size={batch_size} tile={tile} "
        f"do_3D={do_3d} use_gpu={use_gpu}\n"
    )

cmd = [
    "python",
    "-m",
    "cellpose",
    "--image_path",
    image_path,
    "--savedir",
    segmentation_dir,
    "--pretrained_model",
    "nuclei",
    "--chan",
    "0",
    "--chan2",
    "0",
    "--diameter",
    str(diameter),
    "--batch_size",
    batch_size,
    "--save_tif",
    "--verbose",
]

if do_3d:
    cmd.append("--do_3D")
if tile:
    cmd.append("--tile")
if use_gpu:
    cmd.append("--use_gpu")

cmd_str = " ".join(cmd)
start_ts = datetime.now(timezone.utc).isoformat()
with open(log_path, "a", encoding="utf-8") as log_file:
    log_file.write(f"cmd={cmd_str}\n")
    log_file.write(f"start_ts={start_ts}\n")

subprocess.run(cmd, check=True)

end_ts = datetime.now(timezone.utc).isoformat()
with open(log_path, "a", encoding="utf-8") as log_file:
    log_file.write(f"end_ts={end_ts}\n")

expected_seg = os.path.join(segmentation_dir, f"{image_base}_seg.npy")
if not os.path.exists(seg_npy) and os.path.exists(expected_seg):
    os.rename(expected_seg, seg_npy)

fallback_seg = os.path.join(preproc_dir, f"{image_base}_seg.npy")
if not os.path.exists(seg_npy) and os.path.exists(fallback_seg):
    os.rename(fallback_seg, seg_npy)

seg_tif = os.path.join(segmentation_dir, f"{image_base}_cp_out.tif")
preproc_tif = os.path.join(preproc_dir, f"{image_base}_cp_out.tif")
if os.path.exists(preproc_tif) and not os.path.exists(seg_tif):
    os.rename(preproc_tif, seg_tif)
