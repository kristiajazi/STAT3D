#!/usr/bin/env python3

import os
import subprocess
from datetime import datetime, timezone

image_path = snakemake.input["image"]
seg_npy = snakemake.output["seg_npy"]

image_base = os.path.splitext(os.path.basename(image_path))[0]
segmentation_dir = os.path.dirname(seg_npy)
results_dir = os.path.dirname(segmentation_dir)
benchmark_dir = os.path.join(results_dir, "benchmarks")

# Parameters from Snakemake
diameter = float(snakemake.params["diameter"])
use_gpu = bool(snakemake.config.get("cellpose_use_gpu", False))
do_3d = bool(snakemake.config.get("cellpose_do_3D", False))

# Fixed settings (no dynamic tuning)
batch_size = "8"
tile = False

print(
    f"[cellpose] batch_size={batch_size} "
    f"tile={tile} do_3D={do_3d} "
    f"use_gpu={use_gpu} diameter={diameter}"
)

os.makedirs(benchmark_dir, exist_ok=True)
log_path = os.path.join(benchmark_dir, f"run_cellpose_{image_base}.log")

with open(log_path, "a", encoding="utf-8") as log_file:
    log_file.write(
        f"batch_size={batch_size} tile={tile} "
        f"do_3D={do_3d} use_gpu={use_gpu} "
        f"diameter={diameter}\n"
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
