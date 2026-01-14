#baysor test KCP

setwd("C:/Users/Kristi/miniconda3/envs/Kidney_STAT3D_all_outputs_GPU/baysor_segmentation_files")

baysor_KCP<-setwd("C:/Users/Kristi/miniconda3/envs/Kidney_STAT3D_all_outputs_GPU/baysor_segmentation_files")

library(remotes)

remotes::install_github("mojaveazure/loomR", ref = "develop")

library(loomR)

library(SeuratWrappers)

exists("ReadLoom")

getAnywhere("ReadLoom")

library(rhdf5)

h5ls("baysor_segmentation_counts.loom")

h5read(
  "baysor_segmentation_counts.loom",
  "/col_attrs",
  index = list(1:5, 1:5)
)

#Features 

genes <- h5read(
  "baysor_segmentation_counts.loom",
  "/row_attrs/Name"
)

head(genes)

length(genes)

#Cell ID

cells <- h5read(
  "baysor_segmentation_counts.loom",
  "/col_attrs/CellID"
)

head(cells)

length(cells)


#matrix

library(Matrix)

library(rhdf5)

counts <- h5read(
  "baysor_segmentation_counts.loom",
  "//matrix"
)


#transpose and seurat object generation


counts <- h5read("baysor_segmentation_counts.loom", "//matrix")

dim(counts) #cells x genes

genes <- h5read("baysor_segmentation_counts.loom", "//row_attrs/Name")

cells <- h5read("baysor_segmentation_counts.loom", "//col_attrs/CellID")

H5close()

# Check lengths

cat("Counts dimensions:", dim(counts), "\n")
cat("Genes length:", length(genes), "\n")
cat("Cells length:", length(cells), "\n")

# THE FIX: Swap if needed
# Loom format: rows = cells, columns = genes (or vice versa)
if (length(genes) == dim(counts)[2] && length(cells) == dim(counts)[1]) {
  # Correct: rows are cells, columns are genes
  # Need to transpose to get genes × cells for Seurat
  counts <- t(counts)
  
  # Now dimensions are: [541 genes, 64515 cells]
  actual_genes <- genes
  actual_cells <- cells
} else if (length(genes) == dim(counts)[1] && length(cells) == dim(counts)[2]) {
  # Already genes × cells
  actual_genes <- genes
  actual_cells <- cells
} else {
  stop("Dimension mismatch! Check your loom file structure.")
}

cat("After transpose:", dim(counts), "\n")

# Convert to sparse matrix
counts <- Matrix(counts, sparse = TRUE)

# Fix gene names
genes_fixed <- gsub("_", "-", actual_genes)
genes_fixed <- make.unique(genes_fixed)

# Assign rownames and colnames
rownames(counts) <- genes_fixed
colnames(counts) <- as.character(actual_cells)

# Verify
cat("Final matrix: ", nrow(counts), "genes ×", ncol(counts), "cells\n")

# Create Seurat object
seurat_obj <- CreateSeuratObject(
  counts = counts,
  assay = "RNA",
  project = "Baysor"
)

print(seurat_obj)

save (seurat_obj, file = "C:/Users/Kristi/miniconda3/envs/Kidney_STAT3D_all_outputs_GPU/baysor_segmentation_files/seurat_object_bajsor_KCP.rds")

VlnPlot(seurat_obj, features = c("nFeature_RNA", "nCount_RNA"), ncol = 2, pt.size = 0)

sp_obj<-subset(seurat_obj, subset = nCount_RNA >0) 

sp_obj <- SCTransform(sp_obj)

sp_obj<- RunPCA(sp_obj, npcs = 30, features = rownames(sp_obj))

sp_obj<- RunUMAP(sp_obj, dims = 1:30)

sp_obj <- FindNeighbors(sp_obj, reduction = "pca", dims = 1:30)

sp_obj<- FindClusters(sp_obj, resolution = 0.3)

DimPlot(sp_obj, reduction = "umap", label = TRUE)

FeaturePlot(sp_obj , features= "LAMP3", label = TRUE)

save (sp_obj, file = "C:/Users/Kristi/miniconda3/envs/Kidney_STAT3D_all_outputs_GPU/baysor_segmentation_files/sp_obj_baysor_KCP.rds")

