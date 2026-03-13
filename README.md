# STAT3D

Spatial Trancriptomics Analysis Tool in 3D

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

Create a folder called `test` in a location of your choice.
Example:

```
C:/Users/test
```

---

## 2. Obtain the workflow files

### Option A – Clone the STAT3D repository

Clone the STAT3D repository into the `test` folder and copy the `workflow` directory into `test`.

### Option B – Download manually

Download the files from the STAT3D repository manually.

Then:

1. Create a folder called `scripts` containing all downloaded scripts.
2. Create a directory called `workflow`.
3. Place the `scripts` folder and the `Snakefile` file inside the `workflow` directory.

The `workflow` directory must follow this structure:

```
workflow/
├── Snakefile
└── scripts/
```

---

## 3. Add the configuration file

### Option A

From the cloned repository, copy a configuration file from the `configs` folder and paste it into the `test` directory.

### Option B

Download a configuration file manually from the `configs` folder and store it in the `test` directory.

**Note**

The configuration file can:

* keep its original name (e.g. `config_2D_GPU.yaml`)
* or be renamed to a simpler name such as `config.yaml`.

See the **Running the pipeline** section below for how the command may change depending on the configuration filename.

---

## 4. Add Xenium input files

The Xenium input files must be placed inside the `test` directory, for example:

* `morphology.ome.tiff`
* `transcripts.parquet`

---

## 5. Final folder structure before running STAT3D

Your directory should look like this:

```
test/
├── morphology.ome.tiff
├── transcripts.parquet
├── config.yaml
└── workflow/
    ├── Snakefile
    └── scripts/
```


## Running the pipeline

To run the pipeline with a configuration file called "config":

``` bash
docker run --platform linux/amd64 --gpus all --rm -v C:/Users/test:/stat3d ghcr.io/kristiajazi/stat3d:latest --configfile /stat3d/config.yaml --cores 4
```

To run the pipeline with a configuration file called "config_2D_GPU":

``` bash
docker run --platform linux/amd64 --gpus all --rm -v C:/Users/test:/stat3d ghcr.io/kristiajazi/stat3d:latest --configfile /stat3d/config_2D_GPU.yaml --cores 4
```

Notes:
- The variables that the users can change in this command are only the path "C:/Users/test", the folder name ("test") and the configuration file name ("config".yaml) 
- The workflow is embedded in the container. You only need to mount your input/output folder (e.g. "test") and pass a config via `--configfile`.


## Test on toy dataset

From the repository root:

```bash
docker run --platform linux/amd64 --rm \
  -v $(pwd)/test_run:/test \
  -v $(pwd)/toy_dataset:/data:ro \
  -v $(pwd)/configs/config_toy_dataset_2D_CPU.yaml:/config.yaml:ro \
  ghcr.io/kristiajazi/stat3d:latest \
  --configfile /config.yaml --cores 4
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
| `export` | `preprocessing/` | This folder contains images of every z-stack in the `morphology.ome.tif` image. The images can be inspected with software such as QuPath and help the user choose the most accurate two z-stacks to consider as `Z_stack_A` and `Z_stack_B`. The image resolution quantification is provided in `Laplacian_score.csv`. |
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
| `Z_1 to `Z_6` | determine the  z-slices of the z-stack that will be extracted from the single pyramidal level | Integer z indices (e.g. `4`, `5`). The optimal z_top1 and z_top2 are automatically calculated by STAT3D, dispalyed as message in the Docker terminal and inputed in the wrokflow. However, they can be overwritten with this parameter |
| `CELL_EXPANSION` | define cell size, based on detected nucleus objects  | Integer (pixels) |
| `SIGMA` | control /reduce the noise effect | Float (e.g. `1.0`) |
| `THRESHOLD` | intensity parameter | Float or int |
| `MIN_AREA` | define the range of nucleus size | Integer |
| `MAX_AREA` | define the range of nucleus size | Integer |
| `BACKGROUND_RADIUS` | if background subtraction is considered, 0 equals no background subtraction | Integer (pixels) |
| `MEDIAN_RADIUS` | reduce image texture | Integer (pixels) |
| `sample_size` | number of nuclei used to calculate all the parameters | Integer (e.g. `2000`) / Recommended number : 15000 |
| `cellpose_use_gpu` | enable of GPU during 3D Cellpose segmentation. If set as flase the segmentation runs in CPU | Boolean (e.g. ´true´ or ´false´) / Recommended : ´true´ for morphology.ome.tiff images smaller than 3 GB |
| `cellpose_do_3D` |enable 3D or 2D Cellpose segmentation. If set as flase the segmentation is  performed in 2D| Boolean (e.g. ´true´ or ´false´) |
| `nuclei_diameter` |  integer or decimal number ( in microns) to set as customized nuclei diameter . It overwrites STAT3D measurement  |
| `transcripts_df` | name of the transcripts.parquet file provided by 10x. This name must be written before the pipeline starts. | e.g. ´/stat3d/transcripts.parquet´ |
| `ref` | Name of the "celldex" reference dataset  | e.g. ´HumanPrimaryCellAtlasData´ / Datasets supported : HumanPrimaryCellAtlasData, BlueprintEncodeData, DatabaseImmuneCellExpressionData, MonacoImmuneData, NovershternHematopoieticData, MouseRNAseqData |
| `label_column` | Granularity of SingleR annotation it can be set as label.main or label.fine | label.main annotates the main cells function and phenotypes (e.g. CD8 T cells); label.fine defines specifically cells functions and phenotypes (e.g. Ehxausted CD8 T cells) |
| `PIXEL_SIZE` | pixel size at various levels of the image pyramid | Integer (e.g. `0.85` for level 2)/ Recommended pixel sizes by 10x are listed in Table 1 |
| `Z_SLICE_MICRON` | spacing size between each z-slice | Integer (e.g. `3` )/ 10x uses 3 microns. Do not change it if 10x hasn't released a new image format |
| `memory_mb` | Optional memory floor (MB) applied to all rules. Set to 0 to use automatic sizing. | Example: `memory_mb: 32000` | Cap for RAM usage in Megabytes (e.g. `28000` on 32GB RAM). Prevents system freeze on local machines. Set to `0` for auto-scaling on clusters. |
| `fallback_to_cpu` | If true, switches to CPU inference if GPU fails with "Out Of Memory" (OOM) error. | Recommended value: `true` |

To change these values, edit your own YAML config file (start from one of the examples in `./configs/`) and re-run the pipeline with `--configfile /path/to/your_config.yaml`. For most parameters, start with conservative values and adjust based on the visual quality of segmentation on a small test region.

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
docker run --platform linux/amd64 --rm \
  -v /path/to/my_data:/data \
  ghcr.io/kristiajazi/stat3d:latest \
  --configfile /data/config.yaml --cores 4
```

## Benchmarking and Reports

STAT3D writes per-rule benchmarks to `results/benchmarks/` for computationally intensive steps (e.g., Cellpose, QuPath, and Seurat). To generate a full HTML report with runtime summaries, run:

```bash
# ensure the folder exists
mkdir -p /path/to/workdir/results/benchmarks

# use an absolute path for the report
snakemake --cores 4 --report /path/to/workdir/results/benchmarks/stat3d-report.html
```

The HTML report includes execution times, rule graphs, and the benchmark tables for profiling and reproducibility.

## STAT3D validation datasets
The datsets used for the validation of STAT3D piepline can be found in the webpages listed below.

| Dataset | Link/DOI
|------------------------|------------------------|
| HCP | https://www.10xgenomics.com/datasets/pancreatic-cancer-with-xenium-human-multi-tissue-and-cancer-panel-1-standard |
| KCP | https://www.10xgenomics.com/datasets/human-kidney-preview-data-xenium-human-multi-tissue-and-cancer-panel-1-standard |
| TC70 (Toy dataset) | doi: 10.5281/zenodo.18377027 |


## Memory Management & Performance

STAT3D implements an **adaptive memory system** designed to work efficiently on both personal laptops and HPC clusters.

### Smart Retry Strategy

The pipeline automatically adjusts its strategy if a job fails due to memory constraints:

1. **Attempt 1 (Fast Mode):** Tries to process the full image in memory. Fastest, but high RAM/VRAM usage.
2. **Attempt 2 (Safe Mode):** If Attempt 1 fails, it retries using a **Tiled** approach (significantly lower memory footprint).
3. **Attempt 3 (CPU Fallback):** If GPU memory is insufficient even with tiling, the pipeline can automatically switch to **CPU inference** (if `fallback_to_cpu: true`), guaranteeing that your analysis finishes regardless of GPU limitations.

*Note: You can track exact memory usage and execution time for each rule in the `results/benchmarks/` folder (TSV files).*

### Configuration Guide
To prevent system instability (especially on laptops), you can define a hard memory limit in your configuration file.

* **On Laptops:** Set `memory_mb` in `config.yaml` to ~85% of your physical RAM (e.g., `28000` for a 32GB machine) to prevent system instability.
* **On Clusters (Slurm):** Set `memory_mb: 0`. The pipeline will calculate requirements dynamically based on image size.

**Note:** It is normal to see a "Job failed" message in the logs during the first attempt. Snakemake will automatically display `(retry 1)` and proceed with the tiled method.


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
