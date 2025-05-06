#!/usr/bin/env python


import tifffile
import numpy as np

# Parameters
LEVEL = 2
Z_SLICE_4 = 4
Z_SLICE_5 = 5

with tifffile.TiffFile('C:/Users/Kristi/Desktop/STAT3D/test/morphologyTC070.ome.tif') as tif:
    # Access the specified level
    level_series = tif.series[0].levels[LEVEL]
    
    # Convert the entire level to a numpy array
    level_array = level_series.asarray()
    
    # Check the shape to confirm axes (e.g., Z, Y, X)
    print("Shape of level {}: {}".format(LEVEL, level_array.shape))
    
    # Extract slices 6 and 7
    z_slice_4 = level_array[Z_SLICE_4, :, :]
    z_slice_5 = level_array[Z_SLICE_5, :, :]

# Stack slices into a 3D array
stacked_slices = np.stack([z_slice_4, z_slice_5], axis=0)  # shape: (2, height, width)

# Save as a multi-page TIFF
tifffile.imwrite(
    'z{}_and_{}_level{}_morphology.tif'.format(Z_SLICE_4, Z_SLICE_5, LEVEL),
    stacked_slices,
    photometric='minisblack',
    dtype='uint16',
    tile=(1024, 1024),
    compression='JPEG2000',  # or compression='none'
    metadata={'axes': 'ZYCX'},  # multiple pages
)