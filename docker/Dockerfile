# Use the official NVIDIA CUDA base image
# This image is based on Ubuntu 22.04 and includes CUDA 12.6.0
FROM nvidia/cuda:12.6.0-base-ubuntu22.04

# Set the working directory
WORKDIR /stat3d

# Install minimal system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    bzip2 \
    libgl1 \
    libglib2.0-0 \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Mambaforge
RUN wget https://github.com/conda-forge/miniforge/releases/download/23.3.1-1/Mambaforge-23.3.1-1-Linux-x86_64.sh -O ~/mambaforge.sh && \
    bash ~/mambaforge.sh -b -p /opt/mambaforge && \
    rm ~/mambaforge.sh
ENV PATH="/opt/mambaforge/bin:$PATH"

# Use mamba to install packages from conda-forge and bioconda channels
RUN mamba install -c conda-forge -c bioconda mamba && \
    mamba install -c conda-forge -c bioconda python=3.10 nextflow snakemake pkg-config openjdk=11 && \
    mamba install -c conda-forge -c bioconda r-base r-irkernel r-curl r-ragg && \
    mamba install -c conda-forge -c bioconda quarto r-quarto && \
    mamba install -c conda-forge pyarrow && \
    mamba clean --all --yes

# Install PyTorch packages first with CUDA 12.6
RUN pip install --no-cache-dir \
    torch==2.6.0 \
    torchvision==0.21.0 \
    torchaudio==2.6.0 \
    --index-url https://download.pytorch.org/whl/cu126

# Then install remaining packages from PyPI
RUN pip install --no-cache-dir \
    setuptools \
    pyqtgraph \
    PyQt5 \
    numba \
    scipy \
    numpy \
    natsort \
    cellpose==3.1.0

# Make a folder for additional tools
RUN mkdir -p /tools
#RUN ls -l /

# Install Qupath
ARG QUPATH_VERSION=0.5.1
RUN curl -LO https://github.com/qupath/qupath/releases/download/v${QUPATH_VERSION}/QuPath-v${QUPATH_VERSION}-Linux.tar.xz && \
    tar -xf QuPath-v${QUPATH_VERSION}-Linux.tar.xz && \
    chmod u+x QuPath-v${QUPATH_VERSION}-Linux/QuPath/bin/QuPath && \
    mv QuPath-v${QUPATH_VERSION}-Linux/QuPath/ /tools && \
    rm QuPath-v${QUPATH_VERSION}-Linux.tar.xz

# Add QuPath binaries to PATH
ENV PATH="/tools/QuPath/bin:$PATH"

# Install pak from CRAN or GitHub
RUN R -e "install.packages('pak', repos='https://cran.r-project.org')"

# Install R packages using BiocManager and install.packages (more reliable in Docker)
RUN R -e "if (!require('BiocManager', quietly=TRUE)) install.packages('BiocManager'); \
    install.packages(c('remotes', 'Matrix')); \
    remotes::install_github('satijalab/seurat-data'); \
    install.packages(c('tidyverse', 'Seurat', 'pheatmap', 'ComplexHeatmap', 'ggrepel', 'readxl', 'data.table', 'plotly', 'viridis', 'rgl', 'patchwork'), dependencies=TRUE); \
    BiocManager::install(c('IRanges', 'SummarizedExperiment', 'Biobase', 'S4Vectors', 'EnhancedVolcano', 'sctransform', 'geosphere', 'scuttle', 'SingleR', 'celldex', 'scRNAseq'), ask=FALSE)"

# Verify installations
RUN java -version
RUN QuPath --help
RUN nextflow -version
RUN snakemake --version
RUN quarto --version
RUN R --version
RUN R -e "packages <- c('Seurat', 'pheatmap', 'stringr', 'tidyverse', 'ComplexHeatmap', 'IRanges', 'sp', \
    'SummarizedExperiment', 'SeuratObject', 'SeuratData', 'Biobase', 'S4Vectors', 'Matrix', 'patchwork', \
    'ggrepel', 'EnhancedVolcano', 'readxl', 'data.table', 'sctransform', 'geosphere', 'plotly', 'viridis', \
    'rgl', 'scuttle', 'SingleR', 'celldex', 'scRNAseq'); sapply(packages, function(pkg) { library(pkg, character.only = TRUE); \
    cat(pkg, as.character(packageVersion(pkg)), '\\n') })"

# Print a list of packages and versions
RUN conda env export | grep -E "^[^#].*=" > /tools/conda_packages.txt
RUN R -e "write.table(installed.packages()[, c('Package', 'Version')], file='/tools/r_packages.txt', \
    row.names=FALSE, col.names=TRUE, sep='\t', quote=FALSE)"

# Default command
CMD ["bash"]