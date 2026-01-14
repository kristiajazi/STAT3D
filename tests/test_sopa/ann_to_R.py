#!/usr/bin/env python

import spatialdata as sd
import zarr
from spatialdata_io import xenium
import matplotlib.pyplot as plt
import seaborn as sns
import scanpy as sc
import squidpy as sq

sdata = sd.read_zarr("C:/Users/Kristi/miniconda3/envs/TC070_STAT3D_all_outputs_GPU/sopa_TC70_directory.zarr")

print(sdata)

sdata.tables

sdata.write(
    "C:/Users/Kristi/miniconda3/envs/TC070_STAT3D_all_outputs_GPU/sopa_TC70_directory_saved.zarr")

#for reloading : sdata = sd.read_zarr(".../sopa_HCP_directory_saved.zarr")

adata = sdata.tables["table"]

adata

adata.write_h5ad(
    "C:/Users/Kristi/miniconda3/envs/TC070_STAT3D_all_outputs_GPU/adata_cells.h5ad"
)



#sdata.tables["cells"].to_csv("cells_metadata.csv")

#sdata.points["transcripts"].to_csv("transcripts.csv")