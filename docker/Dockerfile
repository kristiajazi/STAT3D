# Use the official Micromamba base image
FROM mambaorg/micromamba:latest

# Set the working directory
WORKDIR /stat3d

# Install system dependencies for Quarto CLI, Qupath, Nextflow, and Snakemake
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    openjdk-11-jre \
    libglib2.0-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Quarto CLI
RUN curl -LO https://quarto.org/download/latest/quarto-linux-amd64.deb && \
    dpkg -i quarto-linux-amd64.deb && \
    rm quarto-linux-amd64.deb

# Install Qupath
ARG QUPATH_VERSION=0.5.1
RUN curl -LO https://github.com/qupath/qupath/releases/download/v${QUPATH_VERSION}/Qupath-${QUPATH_VERSION}-linux-x64.tar.gz && \
    tar -xvf Qupath-${QUPATH_VERSION}-linux-x64.tar.gz && \
    mv Qupath /usr/local/Qupath && \
    rm Qupath-${QUPATH_VERSION}-linux-x64.tar.gz

# Set up and install Nextflow and Snakemake via Micromamba
RUN micromamba install -y -n base -c conda-forge -c bioconda nextflow snakemake && \
    micromamba clean -a -y

# Add binaries to PATH
ENV PATH="/usr/local/Qupath/bin:/opt/conda/bin:$PATH"

# Verify installations
RUN quarto --version
RUN java -jar /usr/local/Qupath/Qupath.jar --version
RUN nextflow -version
RUN snakemake --version

# Default command to keep the container running or drop into a shell
CMD ["bash"]