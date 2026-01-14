library(IRanges)
library(sp)
library(SummarizedExperiment)
library(SeuratObject)
library(Seurat)
library(SeuratData)
library(Biobase)
library(dplyr)
library(S4Vectors)
library(Matrix)
library(ggplot2)
library(patchwork)
library(ggrepel)
library(EnhancedVolcano)
library(readxl)
library(data.table) 
library(readr)
library(sctransform)
library(geosphere)
library(plotly)
library(viridis)
library(ggplot2)
library(reshape2)
library(tidyverse)

library(zellkonverter)

getwd()

setwd("C:/Users/Kristi/miniconda3/envs/TC070_STAT3D_all_outputs_GPU")

adata <- readH5AD("adata_cells.h5ad")

adata

#The expression data is stored in assay X that is not recognized by standard seurat, the assay is called assay X not Counts

# adata is my SingleCellExperiment

seurat_obj <- CreateSeuratObject(
  counts = assay(adata, "X"),
  meta.data = as.data.frame(colData(adata))
)

spatial_coords <- reducedDim(adata, "spatial")

colnames(spatial_coords) <- c("x_TC70", "y_TC70")

coords_TC70 <- spatial_coords[, c("x_TC70", "y_TC70")]

colnames(coords_TC70) <- c("spatial_1", "spatial_2")

coords_matrix_TC70 <- as.matrix(coords_TC70[, c("spatial_1", "spatial_2")]) #this matrix needs to be list format ! Check global environment

seurat_obj[["spatialTC70_"]] <- CreateDimReducObject(embeddings = as.matrix(coords_matrix_TC70),
                                                 key = "spatialtc70_",
                                                 assay = DefaultAssay(seurat_obj))

saveRDS(seurat_obj, file= "C:/Users/Kristi/miniconda3/envs/TC070_STAT3D_all_outputs_GPU/seurat_obj_TC70_sopa.rds")

DimPlot(seurat_obj, reduction = 'spatialTC70_',group.by = 'cell_type')

#VlnPlot(seurat_obj, features = c("nFeature_RNA", "nCount_RNA"), raster = FALSE) does not work
#pancreas.filter<-subset(pancreas, subset = nCount_RNA > 10 & nFeature_RNA > 10)
#pancreas.filter

TC70_sopa  <- SCTransform(seurat_obj , assay = "RNA")
TC70_sopa  <- RunPCA(TC70_sopa , npcs = 30, features = rownames(HCP_sopa))
TC70_sopa  <- RunUMAP(TC70_sopa  , dims = 1:30)
TC70_sopa  <- FindNeighbors(TC70_sopa  , reduction = "pca", dims = 1:30)
TC70_sopa  <- FindClusters(TC70_sopa  , resolution = 0.3)

saveRDS(TC70_sopa, file= "C:/Users/Kristi/miniconda3/envs/TC070_STAT3D_all_outputs_GPU/TC70_sopa.rds")

FeaturePlot(TC70_sopa , features= c("LAMP3"))
FeaturePlot(singler , features= c("CCR7","CD83","CSF2RA"))
features<- c("LAMP3","CCR7","CD83","MARCO","CD163","MS4A1","CD79A","BANK1")
DotPlot(HCP_sopa, features = features, cols = c("green", "orange"), dot.scale = 15) + RotatedAxis()
DimPlot(TC70_sopa, reduction = "umap", group.by = 'cell_type')

