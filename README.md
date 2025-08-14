# STAT3D
Spatial Trancriptomics Analysis Tool 3D


## Known Issues

### Cellpose CUDA out-of-memory (GPU + 3D)
When running Cellpose inside the container with GPU enabled and 3D inference (`--use_gpu --do_3D`), large images may fail with:

```python
torch.OutOfMemoryError: CUDA out of memory. Tried to allocate XX GiB...
GPU has 4.00 GiB; ~2 GiB free. Of the allocated memory 1.20 GiB is allocated by PyTorch...
```

Check GPU availability and whether PyTorch can see and initialize a CUDA-capable GPU with proper drivers:

```bash
nvidia-smi
python -c "import torch; print(torch.cuda.is_available())"
```

PyTorch in this environment/container can see and initialize a CUDA-capable GPU with proper drivers

If the GPU is available but the error persists, consider running without GPU support (or using a machine with more VRAM):

```bash
Inserire il comando (oppure esmpio config file) per eseguire STAT3D senza supporto GPU
```
