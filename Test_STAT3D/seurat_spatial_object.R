# create_seurat_object.R

#Snakemake script _seurat_object

library(Seurat)
library(dplyr)
library(Matrix)
library(readr)

# Snakemake I/O
input_dir <- snakemake@input[["input_dir"]]
barcodes_file <- snakemake@input[["barcodes"]]
output_rds <- snakemake@output[["rds"]]
cat("Output PDF: ", snakemake@output[["pdf"]], "\n")

# Read matrix and metadata
sp_obj <- Read10X(data.dir = input_dir)[["Gene Expression"]]
sp_obj <- CreateSeuratObject(counts = sp_obj, project = "sp_obj.xenium", assay = "RNA")

barcodes_df <- read.table(gzfile(barcodes_file), header = FALSE, sep = "\t", stringsAsFactors = FALSE)
colnames(barcodes_df) <- c("cell_id_sp_obj", "x_sp_obj", "y_sp_obj", "z_sp_obj")

coords_sp_obj <- barcodes_df[, c("x_sp_obj", "y_sp_obj")]
rownames(coords_sp_obj) <- barcodes_df$cell_id_sp_obj
sp_obj <- AddMetaData(sp_obj, metadata = coords_sp_obj)

# Create DimReducObject
colnames(coords_sp_obj) <- c("spatial_1", "spatial_2")
row.names(coords_sp_obj) <- barcodes_df$cell_id_sp_obj
coords_matrix_sp_obj <- as.matrix(coords_sp_obj)

sp_obj[["spatialobj_"]] <- CreateDimReducObject(
  embeddings = coords_matrix_sp_obj,
  key = "spatialobj_",
  assay = DefaultAssay(sp_obj)
)

# Save output
saveRDS(sp_obj, file = output_rds)

# Save DimPlot to PDF using Snakemake-defined path
pdf(snakemake@output[["pdf"]], width = 8, height = 6)
print(DimPlot(sp_obj, reduction = 'spatialobj_'))
dev.off()
