#!/usr/bin/env python3

import csv
import numpy as np
import pandas as pd
import scipy.sparse as sparse
import scipy.io as sio
import scipy.ndimage as ndimage

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

# Extract dimensions
y_size, x_size = mask_array.shape

# Load transcripts
transcripts_df = pd.read_parquet(path=transcripts_path, columns=["feature_name", "x_location", "y_location", "qv"])
features = np.unique(transcripts_df["feature_name"])

#Find the distinct labels in the array (extract cell IDs) and drop first row which is 0
cells = np.unique(mask_array)[1:]

# Map cell_id -> column index in the counts matrix
max_cell_id = int(cells.max()) if len(cells) else 0
cell_id_to_col = np.full(max_cell_id + 1, -1, dtype=np.int32)
cell_id_to_col[cells] = np.arange(len(cells), dtype=np.int32)

# Convert transcript columns to numpy arrays (preserve row order)
feature_names = transcripts_df["feature_name"].to_numpy()
x = transcripts_df["x_location"].to_numpy(dtype=np.float64, copy=False)
y = transcripts_df["y_location"].to_numpy(dtype=np.float64, copy=False)
qv = transcripts_df["qv"].to_numpy(dtype=np.float64, copy=False)

zero_before_search = 0
zero_after_search = 0

# QV filter matches the original behavior (skip < 20)
keep = qv >= 20
if not np.any(keep):
    counts = np.zeros((len(features), len(cells)), dtype=np.int32)
    last_x = np.zeros(max_cell_id + 1, dtype=np.int64)
    last_y = np.zeros(max_cell_id + 1, dtype=np.int64)
    last_seen = np.zeros(max_cell_id + 1, dtype=bool)
else:
    feature_names = feature_names[keep]
    x = x[keep]
    y = y[keep]

    # Convert transcript locations from physical space to image space
    x_pixel = x / PIXEL_SIZE
    y_pixel = y / PIXEL_SIZE

    # Guard rails: clamp to image bounds
    x_pixel = np.clip(x_pixel, 0, x_size - 1)
    y_pixel = np.clip(y_pixel, 0, y_size - 1)

    # Match Python's round() (bankers rounding) via np.rint
    x_round = np.rint(x_pixel).astype(np.int64)
    y_round = np.rint(y_pixel).astype(np.int64)

    # Look up cell_id assigned by Cellpose
    cell_id = mask_array[y_round, x_round].astype(np.int64, copy=False)
    valid = cell_id != 0

    # Neighborhood rescue for unassigned transcripts (vectorized)
    zero_before_search = int(np.count_nonzero(~valid))
    if zero_before_search > 0 and NUC_EXP_PIXEL > 0:
        dist, indices = ndimage.distance_transform_edt(
            mask_array == 0,
            sampling=(1.0, 1.0),
            return_indices=True,
        )
        dist_at = dist[y_round, x_round]
        rescue = (~valid) & (dist_at < NUC_EXP_PIXEL)
        if np.any(rescue):
            y_nn = indices[0][y_round[rescue], x_round[rescue]]
            x_nn = indices[1][y_round[rescue], x_round[rescue]]
            cell_id = cell_id.copy()
            cell_id[rescue] = mask_array[y_nn, x_nn]
            valid = cell_id != 0
    zero_after_search = int(np.count_nonzero(~valid))

    # Counts matrix
    counts = np.zeros((len(features), len(cells)), dtype=np.int32)
    if np.any(valid):
        # Feature index: features is sorted (np.unique), so searchsorted matches it
        feat_idx = np.searchsorted(features, feature_names).astype(np.int64)
        col_idx = cell_id_to_col[cell_id].astype(np.int64)

        feat_idx = feat_idx[valid]
        col_idx = col_idx[valid]
        np.add.at(counts, (feat_idx, col_idx), 1)

    # Barcode coordinates: preserve "last transcript encountered" semantics.
    # (Do not rely on advanced-index assignment with repeated indices.)
    last_x = np.zeros(max_cell_id + 1, dtype=np.int64)
    last_y = np.zeros(max_cell_id + 1, dtype=np.int64)
    last_seen = np.zeros(max_cell_id + 1, dtype=bool)
    if np.any(valid):
        valid_pos = np.nonzero(valid)[0].astype(np.int64)
        valid_cell = cell_id[valid]

        last_pos = np.full(max_cell_id + 1, -1, dtype=np.int64)
        np.maximum.at(last_pos, valid_cell, valid_pos)

        present = last_pos >= 0
        last_seen[present] = True
        present_cells = np.nonzero(present)[0]
        last_x[present_cells] = x_round[last_pos[present_cells]]
        last_y[present_cells] = y_round[last_pos[present_cells]]

if zero_before_search > 0:
    print(f"Points with cell_id == 0 before neighborhood search: {zero_before_search}")
    print(f"Points with cell_id == 0 after neighborhood search: {zero_after_search}")
    print(f"Points rescued by neighborhood search: {zero_before_search - zero_after_search}")

# Write barcodes.tsv
with open(barcodes_out, 'w', newline='') as tsvfile:
    writer = csv.writer(tsvfile, delimiter='\t', lineterminator='\n')
    for cell in cells:
        if last_seen[cell]:
            x = last_x[cell]
            y = last_y[cell]
            writer.writerow([f"cell_{cell}", x, y])
        else:
            writer.writerow([f"cell_{cell}", "NA", "NA"])

# Write sparse matrix
sparse_mat = sparse.coo_matrix(counts)
sio.mmwrite(matrix_out, sparse_mat)

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
