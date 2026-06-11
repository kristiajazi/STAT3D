<p align="center">
  <img src="docs/stat3d_logo.svg" width="280" style="margin-left:40px;">
</p>

<p align="center">
Spatial Transcriptomics Analysis Tool in 3D
</p>

<p align="center">
  <img src="https://img.shields.io/badge/workflow-Snakemake-brightgreen">
  <img src="https://img.shields.io/badge/container-Docker-blue">
  <img src="https://img.shields.io/badge/container-Apptainer-orange">
</p>


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

STAT3D is a tool designed for the analysis of Xenium-derived spatial transcriptomics data including for the first time automatic and tailored 3D Cellpose segmentation. It provides functionalities for data preprocessing, analysis, and visualization of 3D and 2D spatial transcriptomics datasets.

## Installation

STAT3D is typically run via the Docker container. Provide your own config file (YAML) to run the workflow; example configs are in `./configs/`.

1.  Install Docker Desktop through the official webpage: https://docs.docker.com/desktop/

2.  Download STAT3D docker image by running the following command in the Docker terminal:

``` bash
docker pull ghcr.io/kristiajazi/stat3d:latest
```


# Preparing the Workflow Directory

Follow the steps below to prepare the required directory structure before running **STAT3D**.

---

## 1. Create a working directory

Create a folder called `xenium_stat3d` in a location of your choice.
Example:

```
C:/Users/xenium_stat3d
```

---

## 2. Obtain the workflow files

### Option A (Advanced users) – Clone the STAT3D repository

Clone STAT3D repository into the `xenium_stat3d` folder and copy the `workflow` directory into `xenium_stat3d`.

### Option B (Basic users)  – Download manually

Download the `workflow` files from the STAT3D repository manually.

Then:

1. Create a folder called `scripts` containing all downloaded scripts.
2. Create a directory called `workflow`.
3. Place the `scripts` folder and the `Snakefile` file inside the `workflow` directory.
4. Move `workflow` directory in `xenium_stat3d`

**Note**

The `workflow` directory must follow this structure:

```
workflow/
├── Snakefile
└── scripts/
```

---

## 3. Add the configuration file

### Option A (Advanced users)

From the cloned repository, copy a configuration file from the `configs` folder and paste it into the `xenium_stat3d` directory.

### Option B (Basic users)

Download a configuration file manually from the `configs` folder and store it in the `xenium_stat3d` directory.

**Note**

The configuration file can:

* keep its original name (e.g. `config_2D_GPU.yaml`)
* or be renamed to a simpler name such as `config.yaml`.

See the **Running the pipeline** section below for how the command may change depending on the configuration filename.

---

## 4. Add Xenium input files

The Xenium input files must be placed inside the `xenium_stat3d` directory.
The required files are the following:

* `morphology.ome.tiff`
* `transcripts.parquet`

---

## 5. Final folder structure before running STAT3D

Your `xenium_stat3d` directory should look like this:

```
xenium_stat3d/
├── morphology.ome.tiff
├── transcripts.parquet
├── config.yaml
└── workflow/
    ├── Snakefile
    └── scripts/
```


## Running the pipeline on Docker desktop terminal

To run the pipeline with a configuration file called "config":

``` bash
docker run --platform linux/amd64 --gpus all --rm -v C:/Users/xenium_stat3d:/stat3d ghcr.io/kristiajazi/stat3d:latest --configfile /stat3d/config.yaml --cores 4
```

To run the pipeline with a configuration file called "config_2D_GPU":

``` bash
docker run --platform linux/amd64 --gpus all --rm -v C:/Users/xenium_stat3d:/stat3d ghcr.io/kristiajazi/stat3d:latest --configfile /stat3d/config_2D_GPU.yaml --cores 4
```

Notes:
- The variables that the users can change in this command are only the path "C:/Users/test", the folder name ("xenium_stat3d") and the configuration file name ("config".yaml) 
- The workflow is embedded in the container. You only need to mount your input/output folder (e.g. "xenium_stat3d") and pass a config via `--configfile`.


## Test on toy dataset

Store the `toy_dataset` files in `xenium_data` folder, together with one of the configuration files dedicated for the toy dataset which is located in `configs` directory.
The `workflow` directory remains invariate.

Run the pipeline in 2D with the command:

``` bash
docker run --platform linux/amd64 --gpus all --rm -v C:/Users/xenium_stat3d:/stat3d ghcr.io/kristiajazi/stat3d:latest --configfile /stat3d/config_toy_dataset_2D_CPU.yaml --cores 4
```

Run the pipeline in 3D with the command:

``` bash
docker run --platform linux/amd64 --gpus all --rm -v C:/Users/xenium_stat3d:/stat3d ghcr.io/kristiajazi/stat3d:latest --configfile /stat3d/config_toy_dataset_3D_CPU.yaml --cores 4
```

The layout of `xenium_data` directory must follow this structure:

```
xenium_stat3d/
├── TC70_cropped.ome.tif 
├── transcriptsTC070.parquet 
├── config_toy_dataset_3D_CPU.yaml  # or config_toy_dataset_2D_CPU.yaml
└── workflow/
    ├── Snakefile
    └── scripts/
```


### Interactive mode

If you want to enter the container interactively to explore files or run commands manually without a config file, override the entrypoint:

``` bash
docker run --platform linux/amd64 --gpus all -it --entrypoint /bin/bash -v C:/Users/xenium_data:/stat3d ghcr.io/kristiajazi/stat3d:latest
```

Followed by entering the `workflow` directory:

``` bash
cd /stat3d/workflow
```

Run the pipeline with the configuration file of choice:

``` bash
snakemake --configfile config.yaml --cores 4 
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
| `results/benchmarks/`    | Per-rule runtime/CPU benchmark TSV files and tool logs for profiling. |

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
| `export` | `preprocessing/` | This folder contains images of every z-stack in the `morphology.ome.tif` image. The images can be inspected with software such as QuPath and help the user choose the most accurate z-slice/s to consider. The image resolution quantification is provided in `Laplacian_score.csv`. |
| `Laplacian_score.csv` | `preprocessing/` | This file indicates the level of sharpness of the first 10 images (`z0, z1, z2, … z9`) forming the z-stack in the `morphology.ome.tif` image. |
| `QuPath_measurements.csv` | `segmentation/` | This file contains information about the size and area of nuclei detected in the tissue biopsy. It serves as the basis for calculating the nuclei average diameter and average nuclear expansion.|
| `nuclei_diameter.csv` | `segmentation/` | Image-tailored calculation of cell diameters for Cellpose. This file contains the average diameter of nuclei in the tissue biopsy. |
| `average_min_distance.csv` | `segmentation/` | This file contains the average minimum distance between nuclei, used in calculating the average nuclear expansion value. |
| `average_nuclear_expansion.csv` | `segmentation/` | This file represents the expansion of each nucleus to ensure correct transcript assignment and avoid overlap with nearby cells. |
| `features.tsv` | `counts/` | TSV file containing the gene list needed to generate Seurat objects. It is subsequently gzipped (`features.tsv.gz`) by the pipeline for use with the `Read10x` function. |
| `barcodes.tsv` | `counts/` | TSV file containing cell locations (`X, Y, Z`) for every `cell_id`. It is subsequently gzipped (`barcodes.tsv.gz`) by the pipeline for use with the `Read10x` function. |

### Benchmark Files

| File | Subfolder | Description |
|------|-----------|-------------|
| `compute_laplacian.tsv` | `benchmarks/` | Runtime and CPU usage for Laplacian score computation. |
| `process_tiff.tsv` | `benchmarks/` | Runtime and CPU usage for TIFF downsampling/stacking. |
| `run_qupath_analysis.tsv` | `benchmarks/` | Runtime and CPU usage for QuPath nucleus detection. |
| `image_measurements.tsv` | `benchmarks/` | Runtime and CPU usage for the nuclear measurement summary. |
| `run_cellpose.tsv` | `benchmarks/` | Runtime and CPU usage for Cellpose segmentation. |
| `cell_to_transcript.tsv` | `benchmarks/` | Runtime and CPU usage for matrix generation from transcripts. |
| `seurat_spatial_object.tsv` | `benchmarks/` | Runtime and CPU usage for Seurat/SingleR analysis. |
| `workflow_resource_usage.txt` | `benchmarks/` | End-to-end wall-clock time and peak RAM usage for the full run. |
| `run_cellpose_<image>.log` | `benchmarks/` | Per-image Cellpose settings, command line, and timestamps. |


## Parameters

STAT3D supports several configuration parameters (defined in your user-provided YAML config file) that control image extraction, filtering, and segmentation. Below is a compact reference table for the most commonly used parameters.

| Parameter | Description | Example / Notes |
|------------------------|------------------------|------------------------|
| `INPUT_TIFF` | name of your image in the stat3d container | e.g. stst3d/name_of_your_morphology.ome.tiff image / Recommended path : ´stat3d/morphology_X.ome.tif´|
| `LEVEL` | determine the level that will be extracted from the pyramydal image (morphology.ome.tif) | Integer (e.g. `0`, `1`) / Recommended level: 2 |
| `Z_1` to `Z_6` | determine the  z-slices of the z-stack that will be extracted from the single pyramidal level. Multiple z-slices can be selected as well as only one z-slice. | Integer z indices (e.g. `4`, `5`). The optimal z_top1 and z_top2 are automatically calculated by STAT3D, dispalyed as message in the Docker terminal and inputed in the wrokflow. However, they can be overwritten with this parameter |
| `Z_STACK` | set at "ALL" it considers all the z-slices in the z-stack and performs Maximum Intensity Projection (MIP) returining a 2D flattened OME.TIFF image.The analysis must be carried on with 2D segmentation.  | Boolean |
| `Laplacian` | set to "HIGHEST" it considers the z-slice with the higest LS score.The analysis must be carried on with 2D segmentation. | Boolean |
| `NUCLEAR_EXPANSION_SET` | determine nuclear expansion for each cell nuclei to ensure correct cell-to-transcript assignment  | Integer (microns) |
| `CELL_EXPANSION` | QuPath parameter to define cell size, based on detected nucleus objects  | Integer (pixels) |
| `SIGMA` | QuPath parameter to control /reduce the noise effect | Float (e.g. `1.0`), QuPath parameter |
| `THRESHOLD` | QuPath parameter for intensity parameter | Float or int |
| `MIN_AREA` | QuPath parameter to define the range of nucleus size | Integer |
| `MAX_AREA` | QuPath parameter to define the range of nucleus size | Integer |
| `BACKGROUND_RADIUS` | QuPath parameter. If background subtraction is considered, 0 equals no background subtraction | Integer (pixels) |
| `MEDIAN_RADIUS` | QuPath parameter to reduce image texture | Integer (pixels) |
| `sample_size` | number of nuclei used to calculate all the parameters | Integer (e.g. `2000`) / Recommended number : 15000 |
| `cellpose_use_gpu` | enable of GPU during 3D Cellpose segmentation. If set as flase the segmentation runs in CPU | Boolean (e.g. ´true´ or ´false´) / Recommended : ´true´ for morphology.ome.tiff images smaller than 3 GB |
| `cellpose_do_3D` |enable 3D or 2D Cellpose segmentation. If set as flase the segmentation is  performed in 2D| Boolean (e.g. ´true´ or ´false´). If only one z-slice is choosen, then STAT3D must be run in 2D. |
| `nuclei_diameter` |  integer or decimal number ( in microns) to set as customized nuclei diameter . It overwrites STAT3D measurement  |
| `transcripts_df` | name of the transcripts.parquet file provided by 10x. This name must be written before the pipeline starts. | e.g. ´/stat3d/transcripts.parquet´ |
| `ref` | Name of the "celldex" reference dataset  | e.g. ´HumanPrimaryCellAtlasData´ / Datasets supported : HumanPrimaryCellAtlasData, BlueprintEncodeData, DatabaseImmuneCellExpressionData, MonacoImmuneData, NovershternHematopoieticData, MouseRNAseqData |
| `label_column` | Granularity of SingleR annotation it can be set as label.main or label.fine | label.main annotates the main cells function and phenotypes (e.g. CD8 T cells); label.fine defines specifically cells functions and phenotypes (e.g. Ehxausted CD8 T cells) |
| `PIXEL_SIZE` | pixel size at various levels of the image pyramid | Integer (e.g. `0.85` for level 2)/ Recommended pixel sizes by 10x are listed in Table 1 |
| `Z_SLICE_MICRON` | spacing size between each z-slice | Integer (e.g. `3` )/ 10x uses 3 microns. Do not change it if 10x hasn't released a new image format |

To change these values, edit your own YAML config file (start from one of the examples in `./configs/`) and re-run the pipeline with `--configfile /path/to/your_config.yaml`.
For most parameters, start with conservative values and adjust based on the visual quality of segmentation on a small test region.
It is recommended to test the QuPath parameters with QuPath App at `Analyze >Cell Detection >Cell detection` to achieve optimal tailoring.

**Note**
If Z_1,Z_2,Z_3,Z_4,Z_5,Z_6, Z_STACK and Laplacian parameters are silenced, STAT3D automatically performs the selection of the two most sharp z-slices returning a multi-plane (2-planes) z-stack which can be analysed with 3D Cellpose segmentation.

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

### Example config snippet

Below is a minimal example showing the most commonly tuned parameters. Save it as a new YAML file (for example `my_config.yaml`) and adjust the values to your dataset and microscope settings.

``` yaml
# my_config.yaml (example)
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

```bash
docker pull ghcr.io/kristiajazi/stat3d:latest # only once when using STAT3D for the first time

# Run with an explicit config file

docker run --platform linux/amd64 --gpus all --rm -v C:/Users/xenium_stat3d:/stat3d ghcr.io/kristiajazi/stat3d:latest --configfile /stat3d/config.yaml --cores 4

```

## Benchmarking and Reports

STAT3D writes per-rule benchmarks to `results/benchmarks/` for computationally intensive steps (e.g., Cellpose, QuPath, and Seurat). To generate a full HTML report with runtime summaries, run:

```bash
# ensure the folder exists
mkdir -p C:/Users/xenium_stat3d/results/benchmarks

# use an absolute path for the report
snakemake --cores 4 --report C:/Users/xenium_stat3d/results/benchmarks/stat3d-report.html
```

The HTML report includes execution times, rule graphs, and the benchmark tables for profiling and reproducibility.

## STAT3D validation datasets
The datsets used for the validation of STAT3D piepline can be found in the webpages listed below.

| Dataset | Link/DOI
|------------------------|------------------------|
| HCP | https://www.10xgenomics.com/datasets/pancreatic-cancer-with-xenium-human-multi-tissue-and-cancer-panel-1-standard |
| KCP | https://www.10xgenomics.com/datasets/human-kidney-preview-data-xenium-human-multi-tissue-and-cancer-panel-1-standard |
| TC70 (Toy dataset image) | https://zenodo.org/records/19092042?preview=1&token=eyJhbGciOiJIUzUxMiIsImlhdCI6MTc3MzgzNTg2MCwiZXhwIjoxNzkxNjc2Nzk5fQ.eyJpZCI6ImMwNzViOWNhLTFkMzAtNDNiYS04MmJlLTcwZTE0ZWMzOWEwNyIsImRhdGEiOnt9LCJyYW5kb20iOiJmZjRjYjY0OTY0M2M4YzZkYzZmYjc0MjVmMmJkZWI4YSJ9.O34bHC_pcZjf19IxKHoXSL2Oh2WHd78uSOCsJqGHGK4blkEkvulqovISyljbyJr2-GZgRVfB5h4KASJ4FyFiTw  |


## Apptainer file for High Performance Clusters

| File | Zenodo link
|------------------------|------------------------|
| Simple Interaction File (.sif)  | https://zenodo.org/records/19091773?preview=1&token=eyJhbGciOiJIUzUxMiIsImlhdCI6MTc3MzgzNTI0NCwiZXhwIjoxNzkxNjc2Nzk5fQ.eyJpZCI6ImQ2YzA1MWZjLWRiMGEtNDZhZC1iZDIyLTg2OTE0YjQ3NTFlYSIsImRhdGEiOnt9LCJyYW5kb20iOiIyYjA4OTc3MTc4NmI2ZWY4Mzk1ZDUxYWYwNDEyZjRlNCJ9.JvyBxRoxN_HVwsaFRW8EznWKog6opZaYohg1lTfl0IMTYBcvGDIvhCEqUWdofVi_zkelQ1gY4aQjV_-xoew6fQ  |

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

*Update:* While the pipeline now automatically handles system RAM (CPU) issues via the adaptive tiling strategy described above, GPU VRAM limits may still occur with very large 3D volumes. If CUDA errors persist, the pipeline allows switching to CPU-only mode by setting `cellpose_use_gpu: false` in the config.
