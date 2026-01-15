#!/usr/bin/env python

import sys
import tifffile
import numpy as np

def main():
    input_tiff = sys.argv[1]
    Z_SLICE_A = int(sys.argv[2])
    Z_SLICE_B = int(sys.argv[3])
    LEVEL = int(sys.argv[4])
    output_filename = sys.argv[5]

    with tifffile.TiffFile(input_tiff) as tif:
        series0 = tif.series[0]
        levels = getattr(series0, "levels", None)

        # Some OME-TIFFs have no pyramid levels; in that case we must read level 0.
        if not levels:
            level_array = series0.asarray()
        else:
            if LEVEL < 0 or LEVEL >= len(levels):
                print(
                    f"Warning: requested LEVEL={LEVEL} but available levels are 0..{len(levels)-1}. "
                    "Falling back to LEVEL=0."
                )
                LEVEL = 0
            level_array = levels[LEVEL].asarray()

        z_slice_A = level_array[Z_SLICE_A, :, :]
        z_slice_B = level_array[Z_SLICE_B, :, :]

    stacked_slices = np.stack([z_slice_A, z_slice_B], axis=0)

    tifffile.imwrite(
        output_filename,
        stacked_slices,
        photometric='minisblack',
        dtype='uint16',
        tile=(1024, 1024),
        compression='JPEG2000',
        metadata={'axes': 'ZYX'}
    )
    print(f"Saved {output_filename}")

if __name__ == "__main__":
    if len(sys.argv) != 6:
        print("Usage: python process_tiff.py input.tif z_SLICE_A Z_SLICE_B LEVEL output.tif")
        sys.exit(1)
    main()
