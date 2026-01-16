# STAT3D

Spatial Trancriptomics Analysis Tool 3D.

## Table of Contents

-   [Description](#description)
-   [Installation](#installation)
-   [Inputs](#inputs)
-   [Outputs](#outputs)
-   [Parameters](#parameters)
-   [Usage](#usage)
-   [Known Issues](#known-issues)
    -   [Cellpose CUDA out-of-memory (GPU + 3D)](#cellpose-cuda-out-of-memory-gpu--3d)

## Description

STAT3D is a tool designed for the analysis of spatial transcriptomics data in 3D. It provides functionalities for data preprocessing, analysis, and visualization of 3D spatial transcriptomics datasets.

## Installation

0.  Download the folder named "workflow" from STAT3D repository and save it in the same direcotry path which contains the morphology.ome image and transcript.parquet file

1.  Install Docker Desktop through the official webpage: https://docs.docker.com/desktop/

2.  Download STAT3D docker image by running the following command in the docker desktop terminal:\

``` bash
docker pull ghcr.io/kristiajazi/stat3d:latest
```

### Running the pipeline

To run the pipeline with a configuration file:

``` bash
docker run --platform linux/amd64 --gpus all -it \
  -v C:/your/directory/path:/stat3d \
  ghcr.io/kristiajazi/stat3d:latest \
  --configfile workflow/config.yaml
```

### Interactive mode

If you want to enter the container interactively to explore files or run commands manually without a config file, override the entrypoint:

``` bash
docker run --platform linux/amd64 --gpus all -it \
  --entrypoint /bin/bash \
  -v C:/your/directory/path:/stat3d \
  ghcr.io/kristiajazi/stat3d:latest
```

Once inside, you can run `stat3d --help` or navigate to `/stat3d/workflow`.

## Inputs

Required files are:

| File | Description
|------------------------|------------------------|
| morphology.ome.tif | Xenium image : which should be a standard OME-TIFF (pyramidal multi-resolution TIFF). |
| transcripts.parquet | Xenium transcripts : parquet file with numeric x/y coordinates in the same pixel coordinate system as the image |

You can verify the input files using the following commands inside the Docker container:

``` bash
ls -lh /absolute/path/to/my_sample
```

``` python
import pyarrow.parquet as pq
tbl = pq.read_table("transcripts.parquet", columns=["x","y","z","feature_name"] )
print(tbl.to_pandas().head())
```

## Outputs

STAT3D organizes all its outputs in a `results/` folder within your specified working directory.

### Organized Output Structure

| Subfolder | Description |
|-----------|-------------|
| `results/preprocessing/` | Size-reduced images, sharpness scores, and Z-slice metadata. |
| `results/segmentation/`  | Cellpose segmentation masks (`.npy`) and nuclear measurement metrics (`.csv`). |
| `results/counts/`        | Gene expression matrices in 10x-compatible format (`matrix.mtx.gz`, etc.). |
| `results/analysis/`      | Downstream analysis objects (`Seurat` and `SingleR` objects in `.rds` format). |
| `results/plots/`         | All generated QC plots and spatial visualizations in `.pdf` format. |

### Key Output Files

| File | Subfolder | Description |
|------|-----------|-------------|
| `sp_obj.rds` | `analysis/` | File compatible with R studio containing all the STAT3D pre-processed data. This file is the base for the next standard downstram analysis such as QC, PCA etc. |
| `singler.rds` | `analysis/` | This file represents the Seurat object generated after QC, SCTransform normalization, PCA (npcs = 30), UMAP (dims = 1:30), FindNeighbours (dims = 1:30), FindClusters (resolution = 0.3)  and automatic annotation with SingleR. |
| `Spatial_SingleR.pdf` | `plots/` | This file displays the spatial UMAP plot with the clusters labels generated after QC, SCTransform normalization, FindNeighbours, FindClusters functions and automatic annotation with SingleR. |
| `spatialobj_plot.pdf` | `plots/` | The spatial image of the tissue of interest where each dot represent a cell. |
| `SingleR_predictions_QC.pdf` | `plots/` | Heatmap displaying the predictions scores of each cell type assigned to each cluster by SingleR annotation. |
| `UMAP_SingleR.pdf` | `plots/` | This file displays the spatial UMAP plot with the SingleR labelled clusters. |
| `QC.pdf` | `plots/` | Violin plots displaying the distributions of numbers of features and numbers of clunts in the sample of interest. |
| `morphology_your_sample.ome_STAT3D.tif` | `preprocessing/` | This image is the new size-reduced and sharpness-preserved image. It will be the base for the rest of the STAT3D analysis. |
| `..._STAT3D_seg.npy` | `segmentation/` | Segmentation masks produced by Cellpose. |

### Intermediate Files

| File | Subfolder | Description |
|------|-----------|-------------|
| `z_slice_measurement.csv` | `preprocessing/` | This file identifies how many z-stacks are in each level of the image pyramid. |
| `export` | `preprocessing/` | This folder contains images of every z-stack in the `morphology.ome.tif` image. The images can be inspected with software such as QuPath and help the user choose the most accurate two z-stacks to consider as `Z_stack_A` and `Z_stack_B`. The image resolution quantification is provided in `Laplacian_score.csv`. |
| `Laplacian_score.csv` | `preprocessing/` | This file indicates the level of sharpness of the first 10 images (`z0, z1, z2, … z9`) forming the z-stack in the `morphology.ome.tif` image. |
| `QuPath_measurements.csv` | `segmentation/` | This file contains information about the size and area of nuclei detected in the tissue biopsy. It serves as the basis for calculating the nuclei average diameter and average nuclear expansion.|
| `nuclei_diameter.csv` | `segmentation/` | Image-tailored calculation of cell diameters for Cellpose. This file contains the average diameter of nuclei in the tissue biopsy. |
| `average_min_distance.csv` | `segmentation/` | This file contains the average minimum distance between nuclei, used in calculating the average nuclear expansion value. |
| `average_nuclear_expansion.csv` | `segmentation/` | This file represents the expansion of each nucleus to ensure correct transcript assignment and avoid overlap with nearby cells. |
| `features.tsv` | `counts/` | TSV file containing the gene list needed to generate Seurat objects. It is subsequently gzipped (`features.tsv.gz`) by the pipeline for use with the `Read10x` function. |
| `barcodes.tsv` | `counts/` | TSV file containing cell locations (`X, Y, Z`) for every `cell_id`. It is subsequently gzipped (`barcodes.tsv.gz`) by the pipeline for use with the `Read10x` function. |

## Parameters

STAT3D supports several configuration parameters (defined in `config.yaml`) that control image extraction, filtering, and segmentation. Below is a compact reference table for the most commonly used parameters.

| Parameter | Description | Example / Notes |
|------------------------|------------------------|------------------------|
| INPUT_TIFF | name of your image in the stat3d container | e.g. stst3d/name_of_your_morphology.ome.tiff image / Recommended path : ´stat3d/morphology_X.ome.tif´|
| Level | determine the level that will be extracted from the pyramydal image (morphology.ome.tif) | Integer (e.g. `0`, `1`) / Recommended level: 2 |
| Z_SLICE_A and Z_SLICE_B | determine the two z-stacks that will be extracted from the single pyramidal level | Integer z indices (e.g. `4`, `5`). The optimal z_A and z_B are automatically calculated by STAT3D, dispalyed as message in the Docker terminal and inputed in the wrokflow. However, they can be overwritten with this parameter |
| CELL_EXPANSION | define cell size, based on detected nucleus objects  | Integer (pixels) |
| SIGMA | control /reduce the noise effect | Float (e.g. `1.0`) |
| THRESHOLD | intensity parameter | Float or int |
| MIN_AREA | define the range of nucleus size | Integer |
| MAX_AREA | define the range of nucleus size | Integer |
| BACKGROUND_RADIUS | if background subtraction is considered, 0 equals no background subtraction | Integer (pixels) |
| MEDIAN_RADIUS | reduce image texture | Integer (pixels) |
| sample_size | number of nuclei used to calculate all the parameters | Integer (e.g. `2000`) / Recommended number : 15000 |
| cellpose_use_gpu | enable of GPU during 3D Cellpose segmentation. If set as flase the segmentation runs in CPU | Boolean (e.g. ´true´ or ´false´) / Recommended : ´true´ for morphology.ome.tiff images smaller than 3 GB |
| cellpose_img_filter|  name the image processed by Cellpose and produced after z-stack extractions. This name must be written before the pipeline starts. | e.g. ´morphology_X.ome_STAT3D´ / If the INPUT_TIFF is ´morphology_X.ome.tif´, the parameter needed in this slot is ´morphology_X.ome_STAT3D´ |
| transcripts_df | name of the transcripts.parquet file provided by 10x. This name must be written before the pipeline starts. | e.g. ´/stat3d/transcripts.parquet´ |
| PIXEL_SIZE | pixel size at various levels of the image pyramid | Integer (e.g. `0.85` for level 2)/ Recommended pixel sizes by 10x are listed in Table 1 |
| Z_SLICE_MICRON | spacing size between each z-slice | Integer (e.g. `3` )/ 10x uses 3 microns. Do not change it if 10x hasn't released a new image format |
| label_column | Granularity of SingleR annotation it can be set as label.main or label.fine | label.main annotates the main cells function and phenotypes (e.g. CD8 T cells); label.fine defines specifically cells functions and phenotypes (e.g. Ehxausted CD8 T cells) |
| ref | Name of the "celldex" reference dataset  | e.g. ´HumanPrimaryCellAtlasData´ / Datasets supported : HumanPrimaryCellAtlasData, BlueprintEncodeData, DatabaseImmuneCellExpressionData, MonacoImmuneData, NovershternHematopoieticData, MouseRNAseqData |

To change these values, edit `config.yaml` in the `workflow` folder and re-run the pipeline (for example: `snakemake --cores 1`). For most parameters, start with conservative values and adjust based on the visual quality of segmentation on a small test region.

## Table 1. Pixel Size at various level (by 10x Genomics)
The table displays the pixel sizes associated with each pyramidal level in images generated with Xenium platform.

| Pyramidal Level | Pixel size (micron)
|------------------------|------------------------|
0 |	0.2125
1 | 0.425
2 | 0.85
3 | 1.7
4 | 3.4
5 | 6.8

### Example `config.yaml` snippet

Below is a minimal example of `config.yaml` showing the most commonly tuned parameters. Copy this into `workflow/config.yaml` and adjust the values to your dataset and microscope settings.

``` yaml
# workflow/config.yaml (example)
Level: 0
Z_SLICE_A: 10
Z_SLICE_B: 12
CELL_EXPANSION: 5
SIGMA: 1.0
THRESHOLD: 0.1
MIN_AREA: 50
MAX_AREA: 2000
BACKGROUND_RADIUS: 0
MEDIAN_RADIUS: 3
sample_size: 100
```

Tip: change a few parameters and run the pipeline to first to visually inspect segmentation quality before processing the full dataset.

## Usage

To run STAT3D, use the following commands:

```bash=
docker pull ghcr.io/kristiajazi/stat3d:latest # only once when using STAT3D for the first time
docker run --platform linux/amd64 --gpus all -it -v C:/your/directory/path:/stat3d ghcr.io/kristiajazi/stat3d:latest
cd /stat3d/workflow
snakemake --cores 1
```

## STAT3D validation datasets
The datsets used for the validation of STAT3D piepline can be found in the webpages listed below.

| Dataset | Link
|------------------------|------------------------|
| HCP | https://www.10xgenomics.com/datasets/pancreatic-cancer-with-xenium-human-multi-tissue-and-cancer-panel-1-standard |
| KCP | https://www.10xgenomics.com/datasets/human-kidney-preview-data-xenium-human-multi-tissue-and-cancer-panel-1-standard|


## Known Issues

### Cellpose CUDA out-of-memory (GPU + 3D)

When running STAT3D with GPU enabled and 3D inference, large images may fail due to insufficient GPU memory. The error message typically looks like this:

``` python
torch.OutOfMemoryError: CUDA out of memory. Tried to allocate XX GiB...
GPU has 4.00 GiB; ~2 GiB free. Of the allocated memory 1.20 GiB is allocated by PyTorch...
```

First ensure that the NVIDIA drivers are correctly installed and configured. Then check the GPU availability and whether PyTorch can see and initialize a CUDA-capable GPU with proper drivers:

``` bash
# from the container or environment where STAT3D is running
nvidia-smi
python -c "import torch; print(torch.cuda.is_available())"
```

If the GPU is available but the error persists, consider running STAT3D without GPU support (or using a machine with more VRAM):

``` bash
From config.yaml file : "cellpose_use_gpu: false"
```
