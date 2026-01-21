#!/usr/bin/env python3

import csv
import numpy as np
import pandas as pd
import re
import scipy.sparse as sparse
import scipy.io as sio
import subprocess
import gzip
import io

# Inputs from Snakemake
seg_data_path = snakemake.input["seg_data"]
transcripts_path = snakemake.input["transcripts"]

# Outputs from Snakemake
matrix_out = snakemake.output["matrix"]
features_out = snakemake.output["features"]
barcodes_out = snakemake.output["barcodes"]

# Parameters from Snakemake
PIXEL_SIZE = snakemake.params["pixel_size"]
Z_SLICE_MICRON = snakemake.params["z_slice_micron"]
NUC_EXP_PIXEL = snakemake.params["nuc_exp_pixel"]
NUC_EXP_SLICE = snakemake.params["nuc_exp_slice"]

# Load Cellpose segmentation mask
seg_data = np.load(seg_data_path, allow_pickle=True).item()
mask_array = seg_data['masks']

# Extract dimensions using regex
m = re.match(r"\((?P<z_size>\d+), (?P<y_size>\d+), (?P<x_size>\d+)", str(mask_array.shape))
mask_dims = {key: int(m.groupdict()[key]) for key in m.groupdict()}

# Load transcripts
transcripts_df = pd.read_parquet(path=transcripts_path, columns=["feature_name", "x_location", "y_location", "z_location", "qv"])
features = np.unique(transcripts_df["feature_name"])

# Create lookup dictionary for feature indices
feature_to_index = {val.encode('utf-8'): idx for idx, val in enumerate(features)}

#Find the distinct labels in the array (extract cell IDs) and drop first row which is 0
cells = np.unique(mask_array)[1:]

#Create a result table with rows for features and cell IDs as columns 
matrix = pd.DataFrame(0, index=range(len(features)), columns=cells, dtype=np.int32)

coordinates = []

# Main loop
for idx, row in transcripts_df.iterrows():
    if idx % 10000 == 0:
        print(f"{idx} transcripts processed.")

    feature = str(row['feature_name']).encode('utf-8')
    x = row['x_location']
    y = row['y_location']
    z = row['z_location']
    qv = row['qv']

    if qv < 20:
        continue

    #Convert transcript locations from physical space to image space
    x_pixel = x / PIXEL_SIZE
    y_pixel = y / PIXEL_SIZE
    z_slice = z / Z_SLICE_MICRON

    #Add guard rails to make sure lookup falls within image boundaries
    x_pixel = min(max(0, x_pixel), mask_dims["x_size"] - 1)
    y_pixel = min(max(0, y_pixel), mask_dims["y_size"] - 1)
    z_slice = min(max(0, z_slice), mask_dims["z_size"] - 1)
    
    # Look up cell_id assigned by Cellpose. Array is in ZYX order
    cell_id = mask_array[round(z_slice)][round(y_pixel)][round(x_pixel)]

    if cell_id == 0:
        # Optionally implement neighborhood search here if desired
        z_neighborhood_min_slice = max(0, round(z_slice-NUC_EXP_SLICE))
        z_neighborhood_max_slice = min(mask_dims["z_size"], round(z_slice+NUC_EXP_SLICE+1))
        y_neighborhood_min_pixel = max(0, round(y_pixel-NUC_EXP_PIXEL))
        y_neighborhood_max_pixel = min(mask_dims["y_size"], round(y_pixel+NUC_EXP_PIXEL+1))
        x_neighborhood_min_pixel = max(0, round(x_pixel-NUC_EXP_PIXEL))
        x_neighborhood_max_pixel = min(mask_dims["x_size"], round(x_pixel+NUC_EXP_PIXEL+1))

    if cell_id != 0:
        matrix.at[feature_to_index[feature], cell_id] += 1
        coordinates.append((round(x_pixel), round(y_pixel), round(z_slice), cell_id))

# Extract coordinates 
coordinates_df = pd.DataFrame(coordinates, columns=["x", "y", "z", "cell_id"])
#coordinates_df.to_csv("cell_coordinates_new.tsv.gz", sep='\t', index=False, compression='gzip')

# Write sparse matrix
sparse_mat = sparse.coo_matrix(matrix.values)
sio.mmwrite(matrix_out, sparse_mat)

# Build coordinate map for barcodes
cell_coordinates = {
    row['cell_id']: (row['x'], row['y'], row['z']) for _, row in coordinates_df.iterrows()
}

# Write barcodes.tsv
with open(barcodes_out, 'w', newline='') as tsvfile:
    writer = csv.writer(tsvfile, delimiter='\t', lineterminator='\n')
    for cell in cells:
        if cell in cell_coordinates:
            x, y, z = cell_coordinates[cell]
            writer.writerow([f"cell_{cell}", x, y, z])
        else:
            writer.writerow([f"cell_{cell}", "NA", "NA", "NA"])

# Write features.tsv
with open(features_out, 'w', newline='') as tsvfile:
    writer = csv.writer(tsvfile, delimiter='\t', lineterminator='\n')
    for f in features:
        feature = str(f)
        if feature.startswith("NegControlProbe_") or feature.startswith("antisense_"):
            category = "Negative Control Probe"
        elif feature.startswith("NegControlCodeword_"):
            category = "Negative Control Codeword"
        elif feature.startswith("BLANK_"):
            category = "Blank Codeword"
        else:
            category = "Gene Expression"
        writer.writerow([feature, feature, category])


