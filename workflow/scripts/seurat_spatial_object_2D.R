# create_seurat_object.R

#Snakemake script _seurat_object

# Loading libraries quietly
suppressPackageStartupMessages({
  library(Seurat, quietly = TRUE)
  library(dplyr, quietly = TRUE)
  library(Matrix, quietly = TRUE)
  library(readr, quietly = TRUE)
  library(SingleR, quietly = TRUE)
  library(celldex, quietly = TRUE)
  library(tidyverse, quietly = TRUE)
  library(pheatmap, quietly = TRUE)
  library(scuttle, quietly = TRUE)
  library(scRNAseq, quietly = TRUE)
  library(cowplot, quietly = TRUE)
  library(GenomeInfoDbData, quietly = TRUE)
})

#increase Global space
options(future.globals.maxSize = 40 * 1024^3)

# Snakemake I/O
input_dir <- dirname(snakemake@input[["matrix"]])
barcodes_file <- snakemake@input[["barcodes"]]
output_rds <- snakemake@output[["rds"]]
ref_name <- snakemake@params[["ref"]]
label_type <- snakemake@params[["label_column"]]
cat("Output PDF: ", snakemake@output[["pdf"]], "\n")

# Read matrix and metadata
sp_obj <- Read10X(data.dir = input_dir)[["Gene Expression"]]
sp_obj <- CreateSeuratObject(counts = sp_obj, project = "sp_obj.xenium", assay = "RNA")

barcodes_df <- read.table(gzfile(barcodes_file), header = FALSE, sep = "\t", stringsAsFactors = FALSE)
colnames(barcodes_df) <- c("cell_id_sp_obj", "x_sp_obj", "y_sp_obj")
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

sp_obj<-subset(sp_obj, subset = nCount_RNA >0) 

saveRDS(sp_obj, file = snakemake@output[["rds"]])

# Save DimPlot to PDF using Snakemake-defined path

pdf(snakemake@output[["pdf"]], width = 8, height = 6)

print(DimPlot(sp_obj, reduction = 'spatialobj_'))

dev.off()

#QC plot

pdf(snakemake@output[["pdf_qc"]], width = 10, height = 6)

print(VlnPlot(sp_obj, features = c("nFeature_RNA", "nCount_RNA"), ncol = 2, pt.size = 0))

dev.off()

#Analysis and annotation

sp_obj <- SCTransform(sp_obj)

sp_obj<- RunPCA(sp_obj, npcs = 30, features = rownames(sp_obj))

sp_obj<- RunUMAP(sp_obj, dims = 1:30)

sp_obj <- FindNeighbors(sp_obj, reduction = "pca", dims = 1:30)

sp_obj_SingleR<- FindClusters(sp_obj, resolution = 0.3)

#Load references with celldex

ref <- eval(parse(text = paste0("celldex::", ref_name, "()")))

cat("Successfully loaded reference:", ref_name, "\n")

#Get counts number for our object

counts<- GetAssayData(sp_obj_SingleR, layer = 'counts')

#Run SingleR Annotation

if (label_type == "label.main") {
  if (!"label.main" %in% colnames(colData(ref))) {
    stop("This reference does not have 'label.main'. Check available columns.")
  }
  labels <- ref$label.main
  cat("Using main labels (", length(unique(labels)), "unique types)\n")
} else if (label_type == "label.fine") {
  if (!"label.fine" %in% colnames(colData(ref))) {
    stop("This reference does not have 'label.fine'. Try 'label.main'.")
  }
  labels <- ref$label.fine
  cat("Using fine-grained labels (", length(unique(labels)), "unique types)\n")
} else {
  stop(paste("Invalid label:", label_type, ". Use 'label.main' or 'label.fine'"))
}

# Run SingleR
prediction <- SingleR(test = counts, ref = ref, labels = labels)

sp_obj_SingleR$singleR.labels<- prediction$labels[match(rownames(sp_obj_SingleR@meta.data),rownames(prediction))]

sp_obj_UMAP_SingleR<- DimPlot(sp_obj_SingleR, reduction = 'umap', group.by = 'singleR.labels') +
                              theme_classic(base_size = 10)+
                              theme(
                              legend.position = "bottom",
                              legend.key.size = unit(0.5, "lines"),
                              legend.text = element_text(size = 5),
                              axis.text = element_text(size = 5))

spatial_UMAP_SingleR<- DimPlot(sp_obj_SingleR, reduction = 'spatialobj_',group.by = 'singleR.labels') +
                              theme_classic(base_size = 10)+
                              theme(
                              legend.position = "bottom",
                              legend.key.size = unit(0.5, "lines"),
                              legend.text = element_text(size = 5),
                              axis.text = element_text(size = 5))


# Save SingleR-annotated object

saveRDS(sp_obj_SingleR, file = snakemake@output[["rds_singler"]])

# Save SingleR UMAP plot

pdf(snakemake@output[["pdf_umap_singler"]])

print(sp_obj_UMAP_SingleR)

dev.off()

# Save SingleR spatial plot 

pdf(snakemake@output[["pdf_spatial_singler"]])

print(spatial_UMAP_SingleR)

dev.off()

#Save SingleR predictions QC 

pdf(snakemake@output[["pdf_qc_predictions"]], width = 30, height = 15)

plotScoreHeatmap(prediction)

dev.off()

