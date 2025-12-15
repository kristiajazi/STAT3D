SOPA WORKING STEPS

With GPU

create a directory called sopa_directory with inside morphology_mip and _focus, transcripts.parquet and xenium.experiment (called experiment .XENIUM File)

enter the folder where the sopa_dir folder is located (cd/---)

pip install sopa[cellpose] (do not create an environment in conda, just enter conda, otherwise sopa does not get installed)

sopa --help # show command names and arguments

sopa convert sopa_directory --technology xenium # read some data

set SOPA_PARALLELIZATION_BACKEND=dask #this step must be run before patching!

sopa patchify image sopa_directory.zarr --patch-width-pixel 6157.16 --patch-overlap-pixel 153.92 # make patches for low-memory segmentation

#sopa patchify image sopa_directory.zarr --patch-width-pixel 1500 --patch-overlap-pixel 50 # make patches for low-memory segmentation

sopa segmentation cellpose sopa_directory.zarr --diameter 60 --channels DAPI --gpu # 

sopa resolve cellpose sopa_directory.zarr # resolve segmentation conflicts at boundaries

sopa aggregate sopa_directory.zarr --average-intensities # transcripts/channels aggregation

sopa explorer write sopa_directory.zarr # convert for interactive vizualisation



SOPA W/O GPU

create a directory called sopa_directory with inside morphology_mip and _focus, transcripts.parquet and xenium.experiment (called experiment .XENIUM File)

enter the folder where the sopa_dir folder is located (cd/---)

pip install sopa[cellpose] (do not create an environment in conda, just enter conda, otherwise sopa does not get installed)

sopa --help # show command names and arguments

sopa convert sopa_directory --technology xenium # read some data

set SOPA_PARALLELIZATION_BACKEND=dask  #this step must be run before patching!

sopa patchify image sopa_directory.zarr # make patches for low-memory segmentation

sopa segmentation cellpose sopa_directory.zarr --diameter 60 --channels DAPI # segmentation

sopa resolve cellpose sopa_directory.zarr # resolve segmentation conflicts at boundaries

sopa aggregate sopa_directory.zarr --average-intensities # transcripts/channels aggregation

sopa explorer write sopa_directory.zarr # convert for interactive vizualisation


Time monitoring $start = Get-Date
sopa segmentation cellpose data.zarr --channels morphology_focus --diameter 50
Write-Host "Processing time: $((Get-Date) - $start)"

Measure-Command { 
    sopa segmentation cellpose data.zarr --channels morphology_focus --diameter 50 
}


