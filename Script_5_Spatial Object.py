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


#CTRL seurat object preparation
setwd("C:/Users/Kristi/miniconda3/envs/envs_CTRL/CTRL_updated_241017")
#Spatial object generation
CTRL<-setwd("C:/Users/Kristi/miniconda3/envs/envs_CTRL/CTRL_updated_241017")

CTRL<- Read10X(data.dir = CTRL)

print(names(CTRL))

CTRL <- CTRL[["Gene Expression"]]

CTRL = CreateSeuratObject(counts= CTRL, project = "CTRL.xenium", assay="RNA") #, counts= CTRL$`Gene Expression`)

barcodes_df_CTRL <- fread("C:/Users/Kristi/miniconda3/envs/envs_CTRL/CTRL_updated_241017/barcodes_df_CTRL.tsv")

colnames(barcodes_df_CTRL) <- c("cell_id_CTRL", "x_CTRL", "y_CTRL","z_CTRL")

coords_CTRL <- barcodes_df_CTRL[, c("x_CTRL", "y_CTRL")]

rownames(coords_CTRL) <- barcodes_df_CTRL$cell_id_CTRL

CTRL  <- AddMetaData(CTRL , metadata = coords_CTRL)

#Prepare DimReductObject and add it to ctrl seurat object

colnames(coords_CTRL) <- c("spatial_1", "spatial_2")

cell_id_CTRL <- barcodes_df_CTRL[, 1]

cell_id_CTRL <- barcodes_df_CTRL$cell_id_CTRL

row.names(coords_CTRL) <-cell_id_CTRL

coords_CTRL<-cbind(cell_id_CTRL,coords_CTRL)

colnames(coords_CTRL) <- c("spatial_0","spatial_1", "spatial_2")

coords_matrix_CTRL <- as.matrix(coords_CTRL[, c("spatial_1", "spatial_2")]) #this matrix needs to be list format ! Check global environment

row.names(coords_matrix_CTRL) <- barcodes_df_CTRL$cell_id_CTRL

CTRL[["spatial_CTRL"]] <- CreateDimReducObject(embeddings = as.matrix(coords_matrix_CTRL),
                                                  key = "spatial_CTRL",
                                                  assay = DefaultAssay(CTRL))
#SEPARATE spatial reduction object
spatial_reduction_CTRL<- CreateDimReducObject(embeddings = as.matrix(coords_matrix_CTRL),
                                                key = "spatial_",
                                              assay = DefaultAssay(CTRL))
#Save files CTRL
saveRDS(CTRL, file= "C:/Users/Kristi/miniconda3/envs/envs_CTRL/CTRL_updated_241017/CTRL_spatial.rds")
saveRDS(spatial_reduction_CTRL, file= "C:/Users/Kristi/miniconda3/envs/envs_CTRL/CTRL_updated_241017/CTRL_spatial_red_obj.rds")
DimPlot(CTRL, reduction = 'spatial_CTRL', cols='polychrome', pt.size=2 )