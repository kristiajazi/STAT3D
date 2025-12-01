# create_seurat_object.R

#Snakemake script _seurat_object

if (!requireNamespace("BiocManager", quietly = TRUE)) {
  install.packages("BiocManager")
}

if (!requireNamespace("GenomeInfoDbData", quietly = TRUE)) {
  BiocManager::install("GenomeInfoDbData", update = FALSE, ask = FALSE)
}


if (!requireNamespace("celldex", quietly = TRUE)) {
  BiocManager::install("celldex", update = FALSE, ask = FALSE)
}

if (!requireNamespace("SingleR", quietly = TRUE)) {
  BiocManager::install("SingleR", update = FALSE, ask = FALSE)
}

if (!requireNamespace("SingleR", quietly = TRUE)) {
  BiocManager::install("SingleR", update = FALSE, ask = FALSE)
}

if (!requireNamespace("scRNAseq", quietly = TRUE)) {
  BiocManager::install("scRNAseq", update = FALSE, ask = FALSE)
}

library(Seurat)
library(dplyr)
library(Matrix)
library(readr)
library(SingleR)  
library(celldex)
library(tidyverse)
library(pheatmap)
library(scuttle)
library(scRNAseq)

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

#Analysis and annotation

VlnPlot(sp_obj, features = c("nFeature_RNA", "nCount_RNA"), ncol = 2, pt.size = 0)

QC<- VlnPlot(sp_obj, features = c("nFeature_RNA", "nCount_RNA"), ncol = 2, pt.size = 0)

sp_obj<- subset(sp_obj , subset = nCount_RNA > 0)

sp_obj

sp_obj <- SCTransform(sp_obj, assay = "SCT")

sp_obj<- RunPCA(sp_obj, npcs = 30, features = rownames(sp_obj))

sp_obj<- RunUMAP(sp_obj, dims = 1:30)

sp_obj <- FindNeighbors(sp_obj, reduction = "pca", dims = 1:30)

sp_obj_SingleR<- FindClusters(sp_obj, resolution = 0.3)

ref<-celldex::HumanPrimaryCellAtlasData()

ref

#get counts number for our object

counts<- GetAssayData(sp_obj_SingleR, layer = 'counts')

counts

#Run singleR on default mode

prediction<-SingleR(test=counts, ref=ref, labels=ref$label.main)

prediction

sp_obj_SingleR$singleR.labels<- prediction$labels[match(rownames(sp_obj_SingleR@meta.data),rownames(prediction))]

DimPlot(sp_obj_SingleR, reduction = 'umap', group.by = 'singleR.labels')

DimPlot(sp_obj_SingleR, reduction = 'spatialobj_',group.by = 'singleR.labels')

sp_obj_UMAP_SingleR<- DimPlot(sp_obj_SingleR, reduction = 'umap', group.by = 'singleR.labels')

spatial_UMAP_SingleR<- DimPlot(sp_obj_SingleR, reduction = 'spatialobj_',group.by = 'singleR.labels')

# Save output

#saveRDS(sp_obj_SingleR, file = output_rds)

# Save SingleR-annotated object

saveRDS(sp_obj_SingleR, file = snakemake@output[["rds_singler"]])

# Save UMAP plot to its own PDF

pdf(snakemake@output[["pdf_umap_singler"]], width = 8, height = 6)

print(sp_obj_UMAP_SingleR)

dev.off()

# Save spatial plot to its own PDF

pdf(snakemake@output[["pdf_spatial_singler"]], width = 8, height = 6)

print(spatial_UMAP_SingleR)

dev.off()

#Save QC plot

pdf(snakemake@output[["pdf_qc"]], width = 8, height = 6)

print(QC)

dev.off()
