FROM nvidia/cuda:12.2.0-base-ubuntu20.04

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    bzip2 \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install Mambaforge (system-wide)
RUN wget https://github.com/conda-forge/miniforge/releases/download/23.3.1-1/Mambaforge-23.3.1-1-Linux-x86_64.sh -O ~/mambaforge.sh && \
    bash ~/mambaforge.sh -b -p /opt/mambaforge && \
    rm ~/mambaforge.sh
ENV PATH="/opt/mambaforge/bin:$PATH"

# Use mamba to install packages from conda-forge, bioconda, and pytorch channels
RUN mamba install -y -c conda-forge -c bioconda -c pytorch \
    mamba \
    python=3.10 \
    nextflow \
    snakemake \
    pkg-config \
    openjdk=11 \
    r-base \
    r-irkernel \
    r-curl \
    r-ragg \
    quarto \
    r-quarto \
    pytorch \
    torchvision \
    torchaudio \
    opencv \
    cellpose \
    && mamba clean --all --yes

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

# Use pak to install required packages
RUN R -e "options(repos=c(CRAN='https://packagemanager.posit.co/cran/latest')); \
    install.packages('remotes'); \
    install.packages('devtools'); \
    install.packages('Matrix'); \
    devtools::install_github('satijalab/seurat-data'); \
    pak::pkg_install(c('stringr', 'tidyverse', 'Seurat', 'pheatmap', 'ComplexHeatmap', 'IRanges', 'sp', \
    'SummarizedExperiment', 'SeuratObject', 'Biobase', 'S4Vectors', 'patchwork', \
    'ggrepel', 'EnhancedVolcano', 'readxl', 'data.table', 'sctransform', 'geosphere', \
    'plotly', 'viridis', 'rgl'))"

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
    'rgl'); sapply(packages, function(pkg) { library(pkg, character.only = TRUE); \
    cat(pkg, as.character(packageVersion(pkg)), '\\n') })"

# Print a list of packages and versions
RUN conda env export | grep -E "^[^#].*=" > /tools/conda_packages.txt
RUN R -e "write.table(installed.packages()[, c('Package', 'Version')], file='/tools/r_packages.txt', \
    row.names=FALSE, col.names=TRUE, sep='\t', quote=FALSE)"

# CUDA verification
#CMD ["python", "-c", "import torch; print(f'PyTorch {torch.__version__} | CUDA: {torch.cuda.is_available()}')"]

# Default command
CMD ["bash"]