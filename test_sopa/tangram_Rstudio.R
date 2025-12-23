#Tangram -Anndata file generation

library(tidyverse)
library(pheatmap)
library(scuttle)
library(SingleR)
library(celldex)
library(scRNAseq)
library(SummarizedExperiment)
library(Seurat)

ref<-celldex::HumanPrimaryCellAtlasData()

ref

###TANGRAM PRE PROCESSING SCRIPT

# Extract the column metadata (sample annotations)

ref_metadata <- as.data.frame(colData(ref))

colnames(ref_metadata)[colnames(ref_metadata) == "label.main"] <- "cell_type"

if (!require("BiocManager", quietly = TRUE))
  install.packages("BiocManager")

BiocManager::install("zellkonverter")

library(zellkonverter)

# Get expression matrix

ref_expression <- assay(ref, "logcounts")

# Create a new SummarizedExperiment with renamed metadata

ref_renamed <- SummarizedExperiment(
  assays = list(logcounts = ref_expression),
  colData = DataFrame(ref_metadata)
)

saveRDS(ref_renamed, file= "C:/Users/Kristi/miniconda3/envs/ref_renamed.rds")

# Extract components
ref_expression <- assay(ref_renamed, "logcounts")
ref_metadata <- as.data.frame(colData(ref_renamed))
gene_names <- rownames(ref_renamed)

# Save as CSV
write.csv(t(ref_expression), "ref_expression_cells_x_genes.csv", row.names = TRUE)
write.csv(ref_metadata, "ref_metadata.csv", row.names = TRUE)
write.csv(data.frame(gene = gene_names), "ref_genes.csv", row.names = FALSE)

print("Exported to CSV files")