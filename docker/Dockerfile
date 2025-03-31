# Use the official Micromamba base image
FROM continuumio/miniconda3:latest

# Set the working directory
WORKDIR /stat3d

# Install Mamba, Nextflow, Snakemake, R, and R dependencies via Conda
RUN conda install -c conda-forge -c bioconda mamba && \
    mamba install -c conda-forge -c bioconda nextflow snakemake pkg-config openjdk=11 && \
    mamba install -c conda-forge -c bioconda cellpose r-base r-irkernel r-curl r-ragg && \
    mamba install -c conda-forge -c bioconda quarto r-quarto && \
    conda clean --all --yes

# make a folder for tools
RUN mkdir -p /tools
#RUN ls -l /

# Install Qupath
ARG QUPATH_VERSION=0.5.1
#RUN curl -LO https://github.com/qupath/qupath/releases/download/v0.5.1/QuPath-v0.5.1-Linux.tar.xz && \
#    tar -xf QuPath-v0.5.1-Linux.tar.xz && \
#    chmod u+x QuPath-v0.5.1-Linux/QuPath/bin/QuPath && \
#    mv QuPath-v0.5.1-Linux/QuPath/ /tools && \
#    rm QuPath-v0.5.1-Linux.tar.xz

RUN curl -LO https://github.com/qupath/qupath/releases/download/v${QUPATH_VERSION}/QuPath-v${QUPATH_VERSION}-Linux.tar.xz && \
    tar -xf QuPath-v${QUPATH_VERSION}-Linux.tar.xz && \
    chmod u+x QuPath-v${QUPATH_VERSION}-Linux/QuPath/bin/QuPath && \
    mv QuPath-v${QUPATH_VERSION}-Linux/QuPath/ /tools && \
    rm QuPath-v${QUPATH_VERSION}-Linux.tar.xz

# Add Conda binaries to PATH early in the build process
ENV PATH="/tools/QuPath/bin:/opt/conda/bin:$PATH"

# Verify installations
RUN java -version
RUN QuPath --help
RUN python -m cellpose --help
RUN nextflow -version
RUN snakemake --version
RUN quarto --version
RUN R --version

# Default command
CMD ["bash"]