#!/usr/bin/env python

import sys

import numpy as np
import tifffile


def _read_level_array(tif: tifffile.TiffFile, level: int) -> tuple[np.ndarray, str | None, int]:
    """Return (array, axes, used_level). Falls back to level 0 if pyramids/level missing."""
    series0 = tif.series[0]
    axes = getattr(series0, "axes", None)
    levels = getattr(series0, "levels", None)

    # Some OME-TIFFs have no pyramid levels; in that case we must read level 0.
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


def _select_first_tc(arr: np.ndarray, axes: str | None) -> tuple[np.ndarray, str | None]:
    """If axes includes T and/or C, select index 0 for them and squeeze singleton dims."""
    if axes:
        axes = axes.strip().upper()

    if axes and len(axes) == arr.ndim:
        index = [slice(None)] * arr.ndim
        for axis_name in ("T", "C"):
            if axis_name in axes:
                index[axes.index(axis_name)] = 0

        arr = arr[tuple(index)]

        # Drop axes that were indexed out
        new_axes = []
        for axis_index, axis_char in enumerate(axes):
            if isinstance(index[axis_index], int):
                continue
            new_axes.append(axis_char)
        axes = "".join(new_axes)

    # Squeeze any remaining singleton dims (e.g. C=1 left behind)
    if arr.ndim > 3:
        singleton_axes = [i for i, s in enumerate(arr.shape) if s == 1]
        if singleton_axes:
            arr = np.squeeze(arr, axis=tuple(singleton_axes))
            if axes and len(axes) == (arr.ndim + len(singleton_axes)):
                axes = "".join(axis_char for i, axis_char in enumerate(axes) if i not in singleton_axes)

    return arr, axes


def _to_zyx(arr: np.ndarray, axes: str | None) -> np.ndarray:
    """Reorder arr to (Z, Y, X) if possible; otherwise assume it already is (Z, Y, X)."""
    if axes:
        axes = axes.strip().upper()

    if arr.ndim == 3 and axes and len(axes) == 3 and all(a in axes for a in "ZYX"):
        z_i, y_i, x_i = axes.index("Z"), axes.index("Y"), axes.index("X")
        return np.moveaxis(arr, (z_i, y_i, x_i), (0, 1, 2))

    if arr.ndim != 3:
        raise ValueError(f"Expected a 3D Z-stack after selecting T/C, got shape={arr.shape}, axes={axes!r}")

    return arr


def main() -> None:
    if len(sys.argv) != 6:
        print("Usage: python process_tiff.py <input.ome.tif> <Z_SLICE_A> <Z_SLICE_B> <LEVEL> <output.tif>")
        sys.exit(1)

    input_tiff = sys.argv[1]
    z_slice_a = int(sys.argv[2])
    z_slice_b = int(sys.argv[3])
    level = int(sys.argv[4])
    output_filename = sys.argv[5]

    with tifffile.TiffFile(input_tiff) as tif:
        level_array, axes, used_level = _read_level_array(tif, level)
        level_array, axes = _select_first_tc(level_array, axes)
        level_array = _to_zyx(level_array, axes)

        if not (0 <= z_slice_a < level_array.shape[0]) or not (0 <= z_slice_b < level_array.shape[0]):
            raise IndexError(
                f"Z slice indices out of range for LEVEL={used_level}: "
                f"Z_SLICE_A={z_slice_a}, Z_SLICE_B={z_slice_b}, available Z=0..{level_array.shape[0] - 1}"
            )

        zA = level_array[z_slice_a, :, :]
        zB = level_array[z_slice_b, :, :]

    stacked_slices = np.stack([zA, zB], axis=0)

    tifffile.imwrite(
        output_filename,
        stacked_slices,
        photometric="minisblack",
        dtype="uint16",
        tile=(1024, 1024),
        compression="JPEG2000",
        metadata={"axes": "ZYX"},
    )
    print(f"Saved {output_filename}")


if __name__ == "__main__":
    main()
