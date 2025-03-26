# Use an official lightweight base image
FROM continuumio/miniconda3:latest

# Set the working directory
WORKDIR /stat3d

# Install Mamba, Nextflow, Snakemake, R, and R dependencies via Conda
RUN conda install -c conda-forge -c bioconda mamba && \
    mamba install -c conda-forge -c bioconda nextflow snakemake r-base r-irkernel && \
    mamba install -c conda-forge pkg-config r-curl r-ragg && \
    conda clean --all --yes

# Add Nextflow, Snakemake, and R to PATH (handled automatically by Conda)
ENV PATH="/opt/conda/bin:$PATH"

# Install Quarto CLI for amd64
RUN wget https://github.com/quarto-dev/quarto-cli/releases/download/v1.3.340/quarto-1.3.340-linux-amd64.deb && \
    dpkg -i quarto-1.3.340-linux-amd64.deb && \
    rm quarto-1.3.340-linux-amd64.deb

# Install pak from CRAN or GitHub
RUN R -e "install.packages('pak', repos='https://cran.r-project.org')"

# Use pak to install required packages
RUN R -e "options(repos=c(CRAN='https://packagemanager.posit.co/cran/latest')); pak::pkg_install(c('Seurat', 'pheatmap', 'stringr', 'tidyverse', 'ComplexHeatmap', 'quarto'))"

# Verify the installations in separate steps (avoids single-step failure)
RUN nextflow -version
RUN snakemake --version
RUN quarto --version
RUN R --version
RUN R -e "library(Seurat); packageVersion('Seurat')" && \
    R -e "library(pheatmap); packageVersion('pheatmap')" && \
    R -e "library(stringr); packageVersion('stringr')" && \
    R -e "library(tidyverse); packageVersion('tidyverse')" && \
    R -e "library(ComplexHeatmap); packageVersion('ComplexHeatmap')" && \
    R -e "library(quarto); packageVersion('quarto')"

# Default command to keep the container running or drop into a shell
CMD ["bash"]
