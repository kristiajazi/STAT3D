#!/usr/bin/env python3

import argparse
import csv
import os
import sys
import numpy as np
import pandas as pd
import re
import scipy.sparse as sparse
import scipy.io as sio
import subprocess
import pyarrow as pa

#Read Cellpose segmentation mask
seg_data = np.load('C:/Users/Kristi/Desktop/My_papers/Xenium_method_paper/test_levels/3D_test_levels/level_2_morphology.ome_seg.npy', allow_pickle=True).item()
mask_array = seg_data['masks']
#Use regular expression to extract dimensions from mask_array.shape
m = re.match("\((?P<z_size>\d+), (?P<y_size>\d+), (?P<x_size>\d+)", str(mask_array.shape))
mask_dims = { key:int(m.groupdict()[key]) for key in m.groupdict() }
# Initialize a list to collect coordinates and cell_ids
coordinates = []
#print(mask_dims)
#Read 5 columns from transcripts Parquet file
transcripts_df = pd.read_parquet(path='C:/Users/Kristi/Desktop/My_papers/Xenium_method_paper/test_levels/transcripts.parquet',columns=["feature_name", "x_location", "y_location", "z_location", "qv"])
features = np.unique(transcripts_df["feature_name"])
#Create lookup dictionary
feature_to_index = dict()
for index, val in enumerate(features):
    feature_to_index[val.encode('utf-8')] = index
cells = np.unique(mask_array)[1:]
#Create a cells x features data frame, initialized with 0
matrix = pd.DataFrame(0, index=range(len(features)), columns=cells, dtype=np.int32)
# Iterate through all transcripts
for index, row in transcripts_df.iterrows():
    if index % 10000 == 0:
        print(index, "transcripts processed.")
    
    feature = str(row['feature_name']).encode('utf-8')
    x = row['x_location']
    y = row['y_location']
    z = row['z_location']
    qv = row['qv']
    # Ignore transcript below user-specified cutoff
    if qv < 20:
        continue
        
    #Convert transcript locations from physical space to image space (LEVEL 2 : 0.85)
    x_pixel = x / 0.85
    y_pixel = y / 0.85
    z_slice = z / 3
    
    # Add guard rails to make sure lookup falls within image boundaries.
    x_pixel = min(max(0, x_pixel), mask_dims["x_size"] - 1)
    y_pixel = min(max(0, y_pixel), mask_dims["y_size"] - 1)
    z_slice = min(max(0, z_slice), mask_dims["z_size"] - 1)
    
    # Look up cell_id assigned by Cellpose. Array is in ZYX order.
    cell_id = mask_array[round(z_slice)] [round(y_pixel)] [round(x_pixel)]
    #print(cell_id)
    # If cell_id is 0, Cellpose did not assign the pixel to a cell. Need to perform
    # neighborhood search. See if nearest nucleus is within user-specified distance.
    if cell_id == 0:
        z_neighborhood_min_slice = max(0, round(z_slice-3.33))
        z_neighborhood_max_slice = min(mask_dims["z_size"], round(z_slice+3.33+1))
        y_neighborhood_min_pixel = max(0, round(y_pixel-11.76))
        y_neighborhood_max_pixel = min(mask_dims["y_size"], round(y_pixel+11.76+1))
        x_neighborhood_min_pixel = max(0, round(x_pixel-11.76))
        x_neighborhood_max_pixel = min(mask_dims["x_size"], round(x_pixel+11.76+1))
        
    #If cell_id is not 0 at this point, it means the transcript is associated with a cell
    if cell_id != 0:
       #print("Cell ID is not 0. Incrementing count in feature-cell matrix.")
       # Increment count in feature-cell matrix
      matrix.at[feature_to_index[feature], cell_id] += 1
      #print(cell_id)
      coordinates.append((round(x_pixel), round(y_pixel), round(z_slice), cell_id))
      
coordinates_df = pd.DataFrame(coordinates, columns=["x", "y", "z", "cell_id"]) 
coordinates_df.to_csv("cell_coordinates_new.tsv.gz", sep='\t', index=False, compression='gzip') 

#Prepp sparse matrix
sparse_mat = sparse.coo_matrix(matrix.values)
sio.mmwrite('C:/Users/Kristi/Desktop/My_papers/Xenium_method_paper/test_levels/Results_test_levels/Results_feature_barcodes_matrix/matrix.mtx', sparse_mat)  
  
# Prepare a dictionary for cell coordinates
cell_coordinates = {row['cell_id']: (row['x'], row['y'], row['z']) for _, row in coordinates_df.iterrows()}  
  
#create Seurat and Scanpy compatible MTX output
with open('C:/Users/Kristi/Desktop/My_papers/Xenium_method_paper/test_levels/Results_test_levels/Results_feature_barcodes_matrix/barcodes.tsv', 'w', newline='') as tsvfile:
    writer = csv.writer(tsvfile, delimiter='\t', lineterminator='\n')
    for cell in cells:
        if cell in cell_coordinates:
            x, y, z = cell_coordinates[cell]
            writer.writerow([f"cell_{cell}", x, y, z])
        else:
            writer.writerow([f"cell_{cell}", "NA", "NA", "NA"])  # Handle missing coordinates
with open('C:/Users/Kristi/Desktop/My_papers/Xenium_method_paper/test_levels/Results_test_levels/Results_feature_barcodes_matrix'+ "/features.tsv", 'w', newline='') as tsvfile:
    writer = csv.writer(tsvfile, delimiter='\t', lineterminator='\n')
    for f in features:
        feature = str(f)
        if feature.startswith("NegControlProbe_") or feature.startswith("antisense_"):
            writer.writerow([feature, feature, "Negative Control Probe"])
        elif feature.startswith("NegControlCodeword_"):
            writer.writerow([feature, feature, "Negative Control Codeword"])
        elif feature.startswith("BLANK_"):
            writer.writerow([feature, feature, "Blank Codeword"])
        else:
            writer.writerow([feature, feature, "Gene Expression"])
            
subprocess.run("gzip -f " + 'C:/Users/Kristi/Desktop/My_papers/Xenium_method_paper/test_levels/Results_test_levels/Results_feature_barcodes_matrix' + "/*", shell=True)
