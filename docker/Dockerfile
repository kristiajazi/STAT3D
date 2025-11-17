# Dockerfile-pixi: STAT3D using Pixi for dependency management
# This Dockerfile uses Pixi to manage all dependencies (Python, R, system packages, Bioconductor)
# Build: docker build -f docker/Dockerfile-pixi -t stat3d:pixi .
# Run: docker run --platform linux/amd64 --gpus all -it -v /path/to/data:/stat3d stat3d:pixi

FROM nvidia/cuda:12.6.0-base-ubuntu22.04

# Set working directory
WORKDIR /stat3d

# Install system essentials and git
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    curl \
    bzip2 \
    ca-certificates \
    git \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install Pixi
ENV PIXI_VERSION=0.24.2
RUN curl -fsSL https://github.com/prefix-dev/pixi/releases/download/v${PIXI_VERSION}/pixi-x86_64-unknown-linux-musl -o /usr/local/bin/pixi && \
    chmod +x /usr/local/bin/pixi && \
    pixi --version

# Copy pixi configuration
COPY pixi.toml pixi.lock* ./

# Initialize pixi environment and install dependencies
RUN pixi install

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

# Prepare output directory
RUN mkdir -p /tools/logs

# Default command: enter pixi environment and start bash
CMD ["pixi", "run", "bash"]
