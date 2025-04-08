# Use the official Micromamba base image
FROM continuumio/miniconda3:latest

# Set the working directory
WORKDIR /stat3d

# Install Mamba and dependencies via Conda
RUN conda install -c conda-forge -c bioconda mamba && \
    mamba install -c conda-forge -c bioconda python=3.10 nextflow snakemake pkg-config openjdk=11 && \
    mamba install -c conda-forge -c bioconda r-base r-irkernel r-curl r-ragg && \
    mamba install -c conda-forge -c bioconda quarto r-quarto && \
    conda clean --all --yes

# Install Open-ST globally via pip
RUN pip install openst

# Make a folder for tools
RUN mkdir -p /tools
#RUN ls -l /

# Install Qupath
ARG QUPATH_VERSION=0.5.1
RUN curl -LO https://github.com/qupath/qupath/releases/download/v${QUPATH_VERSION}/QuPath-v${QUPATH_VERSION}-Linux.tar.xz && \
    tar -xf QuPath-v${QUPATH_VERSION}-Linux.tar.xz && \
    chmod u+x QuPath-v${QUPATH_VERSION}-Linux/QuPath/bin/QuPath && \
    mv QuPath-v${QUPATH_VERSION}-Linux/QuPath/ /tools && \
    rm QuPath-v${QUPATH_VERSION}-Linux.tar.xz

# Add Conda binaries to PATH early in the build process
ENV PATH="/tools/QuPath/bin:/opt/conda/bin:$PATH"

# Install pak from CRAN or GitHub
RUN R -e "install.packages('pak', repos='https://cran.r-project.org')"

# Use pak to install required packages
RUN R -e "options(repos=c(CRAN='https://packagemanager.posit.co/cran/latest')); \
    install.packages('remotes'); \
    install.packages('Matrix'); \
    remotes::install_github('satijalab/seurat-data'); \
    pak::pkg_install(c('tidyverse', 'Seurat', 'pheatmap', 'ComplexHeatmap', 'IRanges', 'sp', \
    'SummarizedExperiment', 'SeuratObject', 'Biobase', 'S4Vectors', 'patchwork', \
    'ggrepel', 'EnhancedVolcano', 'readxl', 'data.table', 'sctransform', 'geosphere', \
    'plotly', 'viridis', 'rgl'))"

# Verify installations
RUN java -version
RUN QuPath --help
RUN python -m cellpose --help
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

# Default command
CMD ["bash"]