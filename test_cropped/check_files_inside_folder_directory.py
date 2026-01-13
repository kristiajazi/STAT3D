#!/usr/bin/env python

import tifffile, os

dirpath = r"C:\Users\Kristi\miniconda3\envs\TC070_STAT3D_all_outputs_GPU"

print("Files found:")
for f in os.listdir(dirpath):
    print(repr(f))   # repr reveals hidden characters