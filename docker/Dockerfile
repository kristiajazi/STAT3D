# Use the official Micromamba base image
FROM mambaorg/micromamba:latest

# Set the working directory
WORKDIR /stat3d

# Install all Conda/Mamba dependencies upfront
RUN micromamba install -y -n base -c conda-forge -c bioconda \
    curl \
    wget \
    openjdk=11 \
    nextflow \
    snakemake \
    && micromamba clean -a -y

# Add Conda binaries to PATH early in the build process
ENV PATH="/opt/conda/bin:$PATH"

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

# Add Qupath binaries to PATH
ENV PATH="/usr/local/Qupath/bin:$PATH"

# Verify installations
RUN quarto --version
RUN java -version
RUN nextflow -version
RUN snakemake --version
RUN curl --version
RUN wget --version
RUN java -jar /usr/local/Qupath/Qupath.jar --help

# Default command
CMD ["bash"]