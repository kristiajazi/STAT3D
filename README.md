# STAT3D
Spatial Trancriptomics Analysis Tool 3D

## Table of Contents
- [Description](#description)
- [Installation](#installation)
- [Inputs](#inputs)
- [Outputs](#outputs)
- [Parameters](#parameters)
- [Usage](#usage)
- [Known Issues](#known-issues)
  - [Cellpose CUDA out-of-memory (GPU + 3D)](#cellpose-cuda-out-of-memory-gpu--3d)

## Description
STAT3D is a tool designed for the analysis of spatial transcriptomics data in 3D. It provides functionalities for data preprocessing, analysis, and visualization of 3D spatial transcriptomics datasets.

## Installation

0. Download the folder named "workflow" from STAT3D repository and save it in the same direcotry path which contains the morphology.ome image and transcript.parquet file 

1.Install Docker desktop through the webpage https://docs.docker.com/desktop/ 

2.Download STAT3D docker image by running the following command in the docker desktop terminal:  docker run --platform linux/amd64 --gpus all -it -v C:/your/directory/path:/stat3d ghcr.io/kristiajazi/stat3d:latest

3.Enter the workflow directory by running the following command in the docker desktop terminal: cd workflow

4.Initialize STAT3D pipeline by running the following command in the docker desktop terminal: snakemake --cores 1

## Inputs
Xenium image : morphology.ome.tif 
Xenium transcripts file : transcripts.parquet

## Outputs
One R data serialized ("sp_obj.rds") file compatible with R studio containing all the STAT3D pre-processed. One Portable Document Format ("spatialobj_plot.pdf") file showing the spatial image of the tissue of interest where each dot represent a cell.

## Parameters
STAT3D supports various parameters for customizing the analysis. Below are some of the key parameters:
- Aggiungere i parametri principali con una breve descrizione di cosa fanno
- se non ha senso questa sezione, rimuoverla (ma consiglio almeno di commentare alcuni parametri principali o quelli di che vanno modificati piú spesso o di difficile comprensione di cosa fanno)

## Usage
Si puó trovare un'immagine di esempio (molto leggera) che può essere utilizzata per testare STAT3D?
In tal caso possiamo creare una cartella `test_data` (oppure possiamo mettere il link se é troppo grande per github) con un esempio di immagine e file di configurazione.
Questo permetterebbe agli utenti di testare STAT3D senza dover preparare i propri dati e soprattutto rende la vita del referee facile facile in modo da renderlo meglio predisposto a farci un buon commento :)

To run STAT3D, use the following command:
- Aggioungere il comando principale per eseguire STAT3D, con un esempio di come passare i parametri

## Known Issues
### Cellpose CUDA out-of-memory (GPU + 3D)
When running STAT3D with GPU enabled and 3D inference, large images may fail due to insufficient GPU memory. The error message typically looks like this:

```python
torch.OutOfMemoryError: CUDA out of memory. Tried to allocate XX GiB...
GPU has 4.00 GiB; ~2 GiB free. Of the allocated memory 1.20 GiB is allocated by PyTorch...
```

First ensure that the NVIDIA drivers are correctly installed and configured. Then check the GPU availability and whether PyTorch can see and initialize a CUDA-capable GPU with proper drivers:

```bash
# from the container or environment where STAT3D is running
nvidia-smi
python -c "import torch; print(torch.cuda.is_available())"
```

If the GPU is available but the error persists, consider running STAT3D without GPU support (or using a machine with more VRAM):

```bash
Inserire il comando (oppure esempio config file, solo la parte pertinente) per eseguire STAT3D senza supporto GPU
```
