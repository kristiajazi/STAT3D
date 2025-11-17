#!/bin/bash

# List of packages to check
packages=(
    "bioconductor-biobase"
    "bioconductor-celldex"
    "bioconductor-complexheatmap"
    "bioconductor-enhancedvolcano"
    "bioconductor-iranges"
    "bioconductor-s4vectors"
    "bioconductor-scrnaseq"
    "bioconductor-scuttle"
    "bioconductor-singler"
    "bioconductor-summarizedexperiment"
    "curl"
    "natsort"
    "numba"
    "pkg-config"
    "pyarrow"
    "r-curl"
    "r-geosphere"
    "r-ggrepel"
    "r-irkernel"
    "r-matrix"
    "r-patchwork"
    "r-pheatmap"
    "r-plotly"
    "r-ragg"
    "r-readxl"
    "r-remotes"
    "r-rgl"
    "r-seurat"
    "r-seuratobject"
    "r-tidyverse"
    "r-viridis"
    "wget"
)

echo "Checking packages..."
echo "=================="

for pkg in "${packages[@]}"; do
    # Check bioconda for bioconductor packages
    if [[ $pkg == bioconductor-* ]]; then
        channel="bioconda"
    else
        channel="conda-forge"
    fi
    
    result=$(curl -s "https://api.anaconda.org/package/$channel/$pkg" | grep -q '"name"' && echo "FOUND" || echo "NOT FOUND")
    printf "%-30s %-12s %s\n" "$pkg" "($channel)" "$result"
done

echo "=================="
echo "Check complete!"
