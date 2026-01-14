#!/usr/bin/env python

import tifffile, os

dirpath = r"C:\Users\Kristi\miniconda3\envs\TC070_STAT3D_all_outputs_GPU"

print("Files found:")
for f in os.listdir(dirpath):
    print(repr(f))   # repr reveals hidden characters

path = next(
    os.path.join(dirpath, f)
    for f in os.listdir(dirpath)
    if f.lower().endswith(".ome.tif") and "cropped" in f.lower()
)

with tifffile.TiffFile(path) as tif:
    series = tif.series[0]
    print("\nFile :", os.path.basename(path))
    print("Shape:", series.shape)
    print("Axes :", series.axes)

    if 'Z' in series.axes:
        z_index = series.axes.index('Z')
        print("Number of Z planes:", series.shape[z_index])
    else:
        print("No Z dimension found")


with tifffile.TiffFile("TC70_cropped.ome.tif") as tif:
    print("Number of levels:", len(tif.series[0].levels))