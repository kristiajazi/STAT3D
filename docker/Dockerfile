# Dockerfile-pixi: STAT3D using Pixi for dependency management
# This Dockerfile uses Pixi to manage all dependencies (Python, R, system packages, Bioconductor)
# Build: docker build -f docker/Dockerfile-pixi -t stat3d:pixi .
# Run: docker run --platform linux/amd64 --gpus all -it -v /path/to/data:/stat3d stat3d:pixi

# Build trigger version: 2026-15-01-001
# Update this version to trigger a new Docker image build in GitHub Actions

FROM nvidia/cuda:12.6.0-base-ubuntu22.04

LABEL maintainer="Kristi Ajazi <kristi.ajazi@immun.lth.se>, Massimiliano Volpe <massimiliano.volpe@scilifelab.se>"
LABEL description="STAT3D: Spatial Transcriptomics Analysis Tool 3D"
LABEL version="0.1.0"

WORKDIR /etc/stat3d

# Ensure the Pixi default environment is always at the front of the PATH
ENV PATH="/etc/stat3d/.pixi/envs/default/bin:$PATH"
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC
ENV PYTHONWARNINGS="ignore"
ENV R_CRAN_WEB="https://cloud.r-project.org"

RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    curl \
    bzip2 \
    xz-utils \
    ca-certificates \
    git \
    libgl1 \
    libglib2.0-0 \
    time \
    tzdata \
    nano \
    && ln -fs /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone \
    && dpkg-reconfigure --frontend noninteractive tzdata \
    && rm -rf /var/lib/apt/lists/*

# Install Pixi
ENV PIXI_VERSION=0.63.1
RUN curl -fsSL https://github.com/prefix-dev/pixi/releases/download/v${PIXI_VERSION}/pixi-x86_64-unknown-linux-musl -o /usr/local/bin/pixi && \
    chmod +x /usr/local/bin/pixi && \
    pixi --version

# Copy pixi configuration to both /etc/stat3d and /stat3d
# Without the wildcard (*), pixi.lock is now mandatory for reproducibility
COPY pixi.toml pixi.lock /etc/stat3d/
COPY pixi.toml pixi.lock /stat3d/

# Initialize pixi environment and install dependencies using the lock file
RUN pixi install --frozen

# Pre-install Bioconductor packages that some workflows try to install at runtime.
# Under pixi/rattler, some Bioconductor "data packages" are shipped as noarch metapackages and
# are not automatically available as regular R libraries, so we install them explicitly here.
RUN /etc/stat3d/.pixi/envs/default/bin/R -q -e 'pkgs <- c("GenomeInfoDbData","celldex","scRNAseq"); if (!requireNamespace("BiocManager", quietly=TRUE)) install.packages("BiocManager", repos="https://cloud.r-project.org"); BiocManager::install(pkgs, update=FALSE, ask=FALSE); stopifnot(all(sapply(pkgs, requireNamespace, quietly=TRUE)))'

# Install PyTorch with CUDA 12.6 support via pip (conda resolves CPU-only versions)
# This matches the working configuration from the original Dockerfile
RUN /etc/stat3d/.pixi/envs/default/bin/pip install --no-cache-dir \
    torch==2.6.0 \
    torchvision==0.21.0 \
    torchaudio==2.6.0 \
    --index-url https://download.pytorch.org/whl/cu126

# Pre-download Cellpose model to avoid runtime downloads.
# Cellpose will otherwise fetch this to ~/.cellpose/models on first run.
ARG CELLPOSE_MODEL_DIR=/root/.cellpose/models
RUN mkdir -p "${CELLPOSE_MODEL_DIR}" && \
    curl -fsSL -o "${CELLPOSE_MODEL_DIR}/nucleitorch_0" "https://www.cellpose.org/models/nucleitorch_0" && \
    test -s "${CELLPOSE_MODEL_DIR}/nucleitorch_0"

# Install QuPath (not available via conda, so install manually)
ARG QUPATH_VERSION=0.5.1
RUN mkdir -p /tools && \
    curl -LO https://github.com/qupath/qupath/releases/download/v${QUPATH_VERSION}/QuPath-v${QUPATH_VERSION}-Linux.tar.xz && \
    tar -xf QuPath-v${QUPATH_VERSION}-Linux.tar.xz && \
    chmod u+x QuPath-v${QUPATH_VERSION}-Linux/QuPath/bin/QuPath && \
    mv QuPath-v${QUPATH_VERSION}-Linux/QuPath/ /tools && \
    rm QuPath-v${QUPATH_VERSION}-Linux.tar.xz

# Add QuPath binaries to PATH
ENV PATH="/tools/QuPath/bin:$PATH"

# Verify key installations using pixi
RUN pixi run verify

# Copy workflow files to /stat3d (must be after pixi install)
COPY workflow/ /stat3d/workflow/

# Copy and install stat3d command wrapper
COPY docker/stat3d-help.sh /usr/local/bin/stat3d-help.sh
COPY docker/stat3d-wrapper.sh /usr/local/bin/stat3d
COPY docker/stat3d-sysinfo.sh /usr/local/bin/stat3d-sysinfo
RUN chmod +x /usr/local/bin/stat3d-help.sh /usr/local/bin/stat3d /usr/local/bin/stat3d-sysinfo

# Default command: run stat3d with arguments or show help
ENTRYPOINT ["/usr/local/bin/stat3d"]
CMD ["--help"]
