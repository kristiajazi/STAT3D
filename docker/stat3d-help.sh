#!/bin/bash
# STAT3D Pipeline Help

cat << EOF
╔═══════════════════════════════════════════════════════════════════════════╗
║                          STAT3D Pipeline v0.1.0                           ║
║              Spatial Transcriptomics Analysis Tool 3D                     ║
╚═══════════════════════════════════════════════════════════════════════════╝

DESCRIPTION:
    STAT3D is an automated pipeline for processing 3D spatial transcriptomics
    data from Xenium platforms. It performs image processing, cell segmentation,
    transcript assignment, and spatial analysis with SingleR annotation.

BASIC USAGE:
    Run the pipeline directly from outside the container:
    
        docker run --platform linux/amd64 --rm \\
            -v /path/to/test_run:/test \\
            -v /path/to/toy_dataset:/data:ro \\
            -v /path/to/configs/toy_dataset_2D_CPU_config.yaml:/config.yaml:ro \\
            ghcr.io/kristiajazi/stat3d:latest --configfile /config.yaml --cores 4

        Notes:
        - Replace the image tag with your local one if needed (e.g. stat3d:local).
        - Do NOT mount anything on /stat3d inside the container, otherwise you will
            hide the embedded workflow at /stat3d/workflow.

CUSTOM CONFIGURATION:
        Example using repo layout (configs/ + toy_dataset/ + test_run/):

        docker run --platform linux/amd64 --rm \\
            -v \$(pwd)/test_run:/test \\
            -v \$(pwd)/toy_dataset:/data:ro \\
            -v \$(pwd)/configs/toy_dataset_2D_CPU_config.yaml:/config.yaml:ro \\
            ghcr.io/kristiajazi/stat3d:latest --configfile /config.yaml --cores 4
    
        Override parameters:
            
        docker run --rm \\
            -v \$(pwd)/test_run:/test \\
            -v \$(pwd)/toy_dataset:/data:ro \\
            -v \$(pwd)/configs/toy_dataset_2D_CPU_config.yaml:/config.yaml:ro \\
            ghcr.io/kristiajazi/stat3d:latest --configfile /config.yaml \\
            --config Z_SLICES=15 CELLPOSE_DIAMETER=30 --cores 4

CONFIG PARAMETERS:
    Required in config.yaml:
    - INPUT_TIFF: Path to morphology image (OME-TIFF)
    - transcripts_df: Path to transcript data (Parquet)
    - directory: Working directory for outputs
    
    Optional:
    - ref: SingleR reference dataset (see SINGLER REFERENCES below)
    - label_column: "label.main" or "label.fine" for annotation granularity
    - Z_SLICES: Number of focal planes to process
    - CELLPOSE_DIAMETER: Expected cell diameter in pixels

SINGLER REFERENCES:
    STAT3D supports 6 celldex reference datasets for cell type annotation:
    
    Human references:
    - HumanPrimaryCellAtlasData (HPCA) - 713 samples, microarray
    - BlueprintEncodeData - 259 samples, bulk RNA-seq  
    - DatabaseImmuneCellExpressionData (DICE) - 1,561 samples, bulk RNA-seq
    - MonacoImmuneData - 114 samples, bulk RNA-seq
    - NovershternHematopoieticData - 211 samples, microarray
    
    Mouse references:
    - MouseRNAseqData - 358 samples, bulk RNA-seq
    
    Note: References are downloaded on-demand (~10-150 MB each) and cached
          locally for subsequent runs. First run may take 15-90 seconds to
          download the selected reference.

WORKFLOW OUTPUTS:
    Generated in your mounted directory:
    - Laplacian_score.csv          Focal plane sharpness scores
    - QuPath_measurements.csv      Cell detection results
    - matrix.mtx.gz                Gene expression matrix
    - features.tsv.gz              Gene names
    - barcodes.tsv.gz              Cell barcodes with coordinates
    - sp_obj.rds                   Seurat spatial object
    - singler.rds                  SingleR annotated object
    - spatialobj_plot.pdf          Spatial visualization
    - UMAP_SingleR.pdf             UMAP with cell types
    - Spatial_SingleR.pdf          Spatial map with cell types
    - SingleR_predictions_QC.pdf   Annotation quality heatmap

CONTAINER STRUCTURE:
    /etc/stat3d/                   Pixi environment (internal, do not mount)
    /stat3d/workflow/              Pipeline scripts (use yours or default)
    /data/                         Suggested input mount point (read-only)
    /test/                         Suggested output mount point (read-write)
    /tools/                        QuPath and other tools

INTERACTIVE MODE:
    For debugging or development:
    
        docker run --platform linux/amd64 -it --rm \\
            -v \$(pwd)/test_run:/test \\
            -v \$(pwd)/toy_dataset:/data:ro \\
            -v \$(pwd)/configs/toy_dataset_2D_CPU_config.yaml:/config.yaml:ro \\
            ghcr.io/kristiajazi/stat3d:latest bash
    
    Inside container:
    $ cd /stat3d/workflow
        $ snakemake --configfile /config.yaml --cores 4
        $ snakemake --configfile /config.yaml -n              # Dry-run
    $ snakemake --dag | dot     # View workflow graph

GPU SUPPORT:
        GPU is optional but recommended for Cellpose.
        If you set cellpose_use_gpu: true in the config, run on an NVIDIA host with:
            docker run --gpus all ...
        Check GPU access:
            docker run --gpus all --rm ghcr.io/kristiajazi/stat3d:latest bash -c "nvidia-smi"

ENVIRONMENT:
    - Python: 3.10 (PyTorch 2.6.0 + CUDA 12.6, Cellpose, NumPy, Pandas)
    - R: 4.4.3 (Seurat, SingleR, Bioconductor packages)
    - Tools: Snakemake, QuPath 0.5.1, Pixi 0.24.2

ADVANCED USAGE:
    View installed packages and system info:
        docker run --rm stat3d:latest sysinfo

        Optional config via environment variable (advanced):
                docker run --rm -e STAT3D_CONFIG=/config.yaml \\
                    -v \$(pwd)/test_run:/test \\
                    -v \$(pwd)/toy_dataset:/data:ro \\
                    -v \$(pwd)/configs/toy_dataset_2D_CPU_config.yaml:/config.yaml:ro \\
                    stat3d:latest --cores 4
    
    Check workflow status:
                docker run --rm \\
                    -v \$(pwd)/test_run:/test \\
                    -v \$(pwd)/toy_dataset:/data:ro \\
                    -v \$(pwd)/configs/toy_dataset_2D_CPU_config.yaml:/config.yaml:ro \\
                    stat3d:latest --configfile /config.yaml --detailed-summary
    
    Clean up intermediate files:
                docker run --rm \\
                    -v \$(pwd)/test_run:/test \\
                    -v \$(pwd)/toy_dataset:/data:ro \\
                    -v \$(pwd)/configs/toy_dataset_2D_CPU_config.yaml:/config.yaml:ro \\
                    stat3d:latest --configfile /config.yaml --cleanup-all
    
    Run specific rule:
                docker run --rm \\
                    -v \$(pwd)/test_run:/test \\
                    -v \$(pwd)/toy_dataset:/data:ro \\
                    -v \$(pwd)/configs/toy_dataset_2D_CPU_config.yaml:/config.yaml:ro \\
                    stat3d:latest --configfile /config.yaml --forcerun compute_laplacian --cores 1

DOCUMENTATION:
    GitHub: https://github.com/kristiajazi/STAT3D
    Issues: https://github.com/kristiajazi/STAT3D/issues

VERSION INFO:
    Container built: $(date -r /etc/stat3d/pixi.toml +%Y-%m-%d 2>/dev/null || echo "unknown")
    Pixi version: $(pixi --version 2>/dev/null || echo "unavailable")
    
For more help, see README.md or contact the maintainers.
EOF
