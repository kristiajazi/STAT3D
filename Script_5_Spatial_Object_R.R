#seurat object preparation
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

sp_obj<- Read10X(data.dir = "/stat3d")

print(names(sp_obj))

sp_obj <- sp_obj[["Gene Expression"]]

sp_obj = CreateSeuratObject(counts= sp_obj, project = "sp_obj.xenium", assay="RNA")

barcodes_df <- fread("/stat3d/barcodes_df.tsv")

colnames(barcodes_df) <- c("cell_id_sp_obj", "x_sp_obj", "y_sp_obj","z_sp_obj")

coords_sp_obj <- barcodes_df[, c("x_sp_obj", "y_sp_obj")]

rownames(coords_sp_obj) <- barcodes_df$cell_id_sp_obj

sp_obj  <- AddMetaData(sp_obj , metadata = coords_sp_obj)

#Prepare DimReductObject and add it to sp_obj seurat object

colnames(coords_sp_obj) <- c("spatial_1", "spatial_2")

cell_id_sp_obj <- barcodes_df[, 1]

cell_id_sp_obj <- barcodes_df$cell_id_sp_obj

row.names(coords_sp_obj) <-cell_id_sp_obj

coords_sp_obj<-cbind(cell_id_sp_obj,coords_sp_obj)

colnames(coords_sp_obj) <- c("spatial_0","spatial_1", "spatial_2")

coords_matrix_sp_obj <- as.matrix(coords_sp_obj[, c("spatial_1", "spatial_2")]) #this matrix needs to be list format ! Check global environment

row.names(coords_matrix_sp_obj) <- barcodes_df$cell_id_sp_obj

sp_obj[["spatialspobj_"]] <- CreateDimReducObject(embeddings = as.matrix(coords_matrix_sp_obj),
                                               key = "spatialspobj_",
                                               assay = DefaultAssay(sp_obj))

#Save files CTRL
saveRDS(sp_obj, file= "/stat3d/sp_obj.rds")

#Plot 
DimPlot(sp_obj, reduction = 'spatialspobj_')

