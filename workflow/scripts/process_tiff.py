#!/usr/bin/env python

import sys
import numpy as np
import tifffile


def _read_level_array(tif: tifffile.TiffFile, level: int):
    """Return (array, axes, used_level). Falls back to level 0 if pyramids missing."""
    series0 = tif.series[0]
    axes = getattr(series0, "axes", None)
    levels = getattr(series0, "levels", None)

    if not levels:
        return series0.asarray(), axes, 0

    if level < 0 or level >= len(levels):
        print(
            f"Warning: requested LEVEL={level} but available levels are 0..{len(levels) - 1}. "
            "Falling back to LEVEL=0.",
            file=sys.stderr,
        )
        level = 0

    return levels[level].asarray(), axes, level


def _select_first_tc(arr: np.ndarray, axes: str | None):
    """Select T=0 and/or C=0 if present, then squeeze singleton dims."""
    if axes:
        axes = axes.upper()

    if axes and len(axes) == arr.ndim:
        index = [slice(None)] * arr.ndim
        for a in ("T", "C"):
            if a in axes:
                index[axes.index(a)] = 0

        arr = arr[tuple(index)]

        new_axes = []
        for i, a in enumerate(axes):
            if isinstance(index[i], int):
                continue
            new_axes.append(a)
        axes = "".join(new_axes)

    if arr.ndim > 3:
        singleton_axes = [i for i, s in enumerate(arr.shape) if s == 1]
        if singleton_axes:
            arr = np.squeeze(arr, axis=tuple(singleton_axes))
            if axes:
                axes = "".join(a for i, a in enumerate(axes) if i not in singleton_axes)

    return arr, axes


def _to_zyx(arr: np.ndarray, axes: str | None) -> np.ndarray:
    """Reorder array to (Z, Y, X)."""
    if axes:
        axes = axes.upper()

    if arr.ndim == 3 and axes and all(a in axes for a in "ZYX"):
        z, y, x = axes.index("Z"), axes.index("Y"), axes.index("X")
        return np.moveaxis(arr, (z, y, x), (0, 1, 2))

    if arr.ndim != 3:
        raise ValueError(f"Expected 3D Z-stack, got shape={arr.shape}, axes={axes}")

    return arr


def main():
    if len(sys.argv) < 6:
        print(
            "Usage: python process_tiff.py "
            "input.tif LEVEL Z_STACK laplacian_mode output.tif [z_slices...]"
        )
        sys.exit(1)

    input_tiff = sys.argv[1]
    level = int(sys.argv[2])
    z_stack_mode = sys.argv[3]          # "ALL" or other
    laplacian_mode = sys.argv[4]        # kept for compatibility
    output_filename = sys.argv[5]
    user_z_slices = [int(z) for z in sys.argv[6:]]

    with tifffile.TiffFile(input_tiff) as tif:
        level_array, axes, used_level = _read_level_array(tif, level)
        level_array, axes = _select_first_tc(level_array, axes)
        level_array = _to_zyx(level_array, axes)  # (Z, Y, X)

    # --------------------------------------------------
    # Z_STACK = ALL → MAX projection
    # --------------------------------------------------
    if z_stack_mode == "ALL":
        print("Z_STACK=ALL: Performing MAX projection over Z")
        output_array = np.max(level_array, axis=0)  # (Y, X)
        out_axes = "YX"

    # --------------------------------------------------
    # Explicit Z slices (Laplacian / user mode)
    # --------------------------------------------------
    elif user_z_slices:
        print(f"Extracting Z-slices: {user_z_slices}")

        for z in user_z_slices:
            if not (0 <= z < level_array.shape[0]):
                raise IndexError(
                    f"Z slice {z} out of range for LEVEL={used_level}: "
                    f"available Z=0..{level_array.shape[0] - 1}"
                )

        z_slices = [level_array[z, :, :] for z in user_z_slices]
        output_array = np.stack(z_slices, axis=0)  # (Z, Y, X)
        out_axes = "ZYX"

    else:
        raise ValueError("No Z-slices specified and Z_STACK is not 'ALL'")

    print(f"Output shape: {output_array.shape}, axes={out_axes}")

    tifffile.imwrite(
        output_filename,
        output_array,
        photometric="minisblack",
        dtype="uint16",
        tile=(1024, 1024),
        compression="JPEG2000",
        metadata={"axes": out_axes},
    )

    print(f"Saved {output_filename}")


if __name__ == "__main__":
    main()
