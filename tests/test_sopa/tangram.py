#!/usr/bin/env python

import pandas as pd
import anndata as ad

print("Loading CSV files...")

# Read data
X = pd.read_csv("ref_expression_cells_x_genes.csv", index_col=0)
obs = pd.read_csv("ref_metadata.csv", index_col=0)
genes = pd.read_csv("ref_genes.csv")

# Create var dataframe
var = pd.DataFrame(index=genes['gene'])

print(f"Expression shape: {X.shape}")
print(f"Metadata shape: {obs.shape}")

# Create AnnData
adata_reference = ad.AnnData(
    X=X.values,
    obs=obs,
    var=var
)

print("\nAnnData object:")
print(adata_reference)
print(f"\nobs columns: {list(adata_reference.obs.columns)}")

# Verify cell_type column
if 'cell_type' in adata_reference.obs.columns:
    print("\n✓ 'cell_type' column found")
    print(adata_reference.obs['cell_type'].value_counts())
else:
    print("\n⚠ Warning: 'cell_type' column not found")
    print(f"Available columns: {list(adata_reference.obs.columns)}")

# Save
adata_reference.write_h5ad("adata_reference.h5ad")
print("\n✓ Saved adata_reference.h5ad")