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

0.  Download the folder named "Workflow" from STAT3D repository and save it in the same direcotry path which contains the morphology.ome image and transcript.parquet file

1.  Install Docker Desktop through the official webpage: https://docs.docker.com/desktop/

2.  Download STAT3D docker image by running the following command in the docker desktop terminal:\

``` bash
docker run --platform linux/amd64 --gpus all -it -v C:/your/directory/path:/stat3d ghcr.io/kristiajazi/stat3d:latest
```

3.  Enter the workflow directory by running the following command in the docker desktop terminal:

``` bash
cd Workflow
```

4.  Initialize STAT3D pipeline by running the following command in the docker desktop terminal:

``` bash
snakemake --cores 1
```

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
tbl = pq.read_table("transcripts.parquet", columns=["x","y","z","gene"] )
print(tbl.to_pandas().head())
```

## Outputs
STAT3D produces two main output files:

| File | Description
|------------------------|------------------------|
| QC.pdf | Violin plots displaying the distributions of numbers of features and numbers of clunts in the sample of interest. |
| morphology_your_sample.ome_STAT3D.tif | This image is the new size-reduced and sharpness-preserved image. It will be the base for the rest of the STAT3D analysis. |
| sp_obj.rds | file compatible with R studio containing all the STAT3D pre-processed data. This file is the base for the next standard downstram analysis such as QC, PCA etc. |
| spatialobj_plot.pdf | the spatial image of the tissue of interest where each dot represent a cell. |
| Spatial_SingleR.pdf | This file displays the spatial UMAP plot with the clusters labels generated after QC, SCTransform normalization, FindNeighbours, FindClusters functions and automatic annotation with single R. |
| singler.rds | This file represents the Seurat object generated after QC, SCTransform normalization, FindNeighbours, FindClusters and automatic annotation with single R. |
| UMAP_SingleR.pdf |  This file displays the spatial UMAP plot with the SingleR labelled clusters. The data underwent QC, SCTransform normalization, PCA (npcs = 30), UMAP (dims = 1:30), FindNeighbours (dims = 1:30), FindClusters (resolution = 0.3)  and automatic annotation with single R (ref.celldex::HumanPrimaryCellAtlasData). |


## Parameters

STAT3D supports several configuration parameters (defined in `config.yaml`) that control image extraction, filtering, and segmentation. Below is a compact reference table for the most commonly used parameters.

| Parameter | Description | Example / Notes |
|------------------------|------------------------|------------------------|
| Level | determines the level that will be extracted from the pyramydal image (morphology.ome.tif) | Integer (e.g. `0`, `1`) |
| Z_SLICE_A and Z_SLICE_B | determines the two z-stacks that will be extracted from the single pyramidal level | Integer z indices (e.g. `10`, `12`) |
| CELL_EXPANSION | based on detected nucleus objects, define cell size | Integer (pixels) |
| SIGMA | control /reduce the noise effect | Float (e.g. `1.0`) |
| THRESHOLD | intensity parameter | Float or int |
| MIN_AREA | define the range of nucleus size | Integer |
| MAX_AREA | define the range of nucleus size | Integer |
| BACKGROUND_RADIUS | if background subtraction is considered, 0 equals no background subtraction | Integer (pixels) |
| MEDIAN_RADIUS | reduce image texture | Integer (pixels) |
| sample_size | number of nuclei used to calculate all the parameters | Integer (e.g. `100`) |

To change these values, edit `config.yaml` in the `workflow` folder and re-run the pipeline (for example: `snakemake --cores 1`). For most parameters, start with conservative values and adjust based on the visual quality of segmentation on a small test region.

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

Tip: change a few parameters and run the pipeline on a small test region first to visually inspect segmentation quality before processing the full dataset.

## Usage

To run STAT3D, use the following commands:

```bash=
docker run --platform linux/amd64 --gpus all -it -v C:/your/directory/path:/stat3d ghcr.io/kristiajazi/stat3d:latest
cd workflow
snakemake --cores 1
```

To verify the STAT3D installation you can use a test data located in the folder : Test_STAT3D

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
