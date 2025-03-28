# Use the official Micromamba base image
FROM continuumio/miniconda3:latest

# Set the working directory
WORKDIR /stat3d

# Install Mamba, Nextflow, Snakemake, R, and R dependencies via Conda
RUN conda install -c conda-forge -c bioconda mamba && \
    mamba install -c conda-forge -c bioconda nextflow snakemake pkg-config openjdk=11 && \
    conda clean --all --yes

# make a folder for tools
RUN mkdir -p /tools
#RUN ls -l /

# Install Quarto CLI
RUN curl -LO https://quarto.org/download/latest/quarto-linux-amd64.deb && \
    dpkg -i quarto-linux-amd64.deb && \
    rm quarto-linux-amd64.deb

# Install Qupath
#ARG QUPATH_VERSION=0.5.1
RUN curl -LO https://github.com/qupath/qupath/releases/download/v0.5.1/QuPath-v0.5.1-Linux.tar.xz && \
    tar -xf QuPath-v0.5.1-Linux.tar.xz && \
    chmod u+x QuPath-v0.5.1-Linux/QuPath/bin/QuPath && \
    mv QuPath-v0.5.1-Linux/QuPath/ /tools && \
    rm QuPath-v0.5.1-Linux.tar.xz

# Add Conda binaries to PATH early in the build process
ENV PATH="/tools/QuPath/bin:/opt/conda/bin:$PATH"

# Verify installations
RUN quarto --version
RUN java -version
RUN nextflow -version
RUN snakemake --version
RUN curl --version
RUN wget --version
RUN QuPath --help

# Default command
CMD ["bash"]