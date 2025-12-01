#!/usr/bin/env python

import sys
import tifffile as tiff
import cv2
import numpy as np
import csv

# Load with tifffile
tiff_path = sys.argv[1]
img = tiff.imread(tiff_path)

# Ensure image has multiple Z slices
if img.ndim < 3:
    raise ValueError("Image does not contain Z-slices. Cannot compute slice-wise sharpness.")

# Pick the first 7 Z-slices (or fewer if image has <7 slices)
num_slices = min(7, img.shape[0])

scores = []  # to store results

for z in range(num_slices):
    slice_img = img[z]

    # Convert to grayscale if slice is RGB
    if slice_img.ndim == 3 and slice_img.shape[-1] in [3, 4]:
        slice_img = cv2.cvtColor(slice_img, cv2.COLOR_RGB2GRAY)

    # Compute variance of Laplacian for this Z-slice
    score = cv2.Laplacian(slice_img, cv2.CV_64F).var()
    scores.append((z, score))

    print(f"Sharpness score for slice {z}:", score)

# Write results to CSV using semicolon as delimiter

with open("Laplacian_score.csv", "w", newline="") as f:
    writer = csv.writer(f)#, delimiter=';'
    writer.writerow(["Z_slice", "Sharpness_score"])
    
    # round score to 2 decimals for each row
    for z, sc in scores:
        writer.writerow([z, round(sc, 2)])

print("Saved Laplacian_score.csv")
