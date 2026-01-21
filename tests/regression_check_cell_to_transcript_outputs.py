#!/usr/bin/env python3

import argparse
import hashlib
import tempfile
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass(frozen=True)
class _SnakemakeStub:
    input: dict
    output: dict
    params: dict


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _read_average_nuclear_expansion_px(
    average_nuclear_expansion_csv: Path, pixel_size: float, z_slice_micron: float
) -> tuple[float, float]:
    df = pd.read_csv(average_nuclear_expansion_csv)
    if "Average_Nuclear_Expansion" not in df.columns:
        raise KeyError(
            f"Expected column 'Average_Nuclear_Expansion' in {average_nuclear_expansion_csv}"
        )
    avg = float(df["Average_Nuclear_Expansion"].iloc[0])
    return avg / pixel_size, avg / z_slice_micron


def _exec_snakemake_script(script_path: Path, snakemake_stub: _SnakemakeStub) -> None:
    code = script_path.read_text(encoding="utf-8")
    globals_dict = {"__name__": "__main__", "snakemake": snakemake_stub}
    exec(compile(code, str(script_path), "exec"), globals_dict)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Regression check: re-run cell_to_transcript (2D) on toy inputs and verify "
            "matrix.mtx/features.tsv/barcodes.tsv are byte-identical to test_run outputs."
        )
    )
    parser.add_argument(
        "--repo-root",
        default=str(Path(__file__).resolve().parents[1]),
        help="Path to STAT3D repo root (default: inferred from this file location).",
    )
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()

    # Known-good outputs (golden)
    golden_dir = repo_root / "test_run" / "results" / "counts"
    golden_matrix = golden_dir / "matrix.mtx"
    golden_features = golden_dir / "features.tsv"
    golden_barcodes = golden_dir / "barcodes.tsv"

    for p in (golden_matrix, golden_features, golden_barcodes):
        if not p.exists():
            raise FileNotFoundError(f"Missing golden output: {p}")

    # Inputs for the rule
    seg_npy = repo_root / "test_run" / "results" / "segmentation" / "TC70_cropped.ome_STAT3D_seg.npy"
    average_nuclear_expansion_csv = (
        repo_root / "test_run" / "results" / "segmentation" / "average_nuclear_expansion.csv"
    )
    transcripts_parquet = repo_root / "toy_dataset" / "transcriptsTC070.parquet"

    for p in (seg_npy, average_nuclear_expansion_csv, transcripts_parquet):
        if not p.exists():
            raise FileNotFoundError(f"Missing input: {p}")

    # Parameters (must match the config used to generate test_run)
    pixel_size = 0.85
    z_slice_micron = 3.0
    nuc_exp_pixel, nuc_exp_slice = _read_average_nuclear_expansion_px(
        average_nuclear_expansion_csv=average_nuclear_expansion_csv,
        pixel_size=pixel_size,
        z_slice_micron=z_slice_micron,
    )

    script_path = repo_root / "workflow" / "scripts" / "cell_to_transcript_2D.py"
    if not script_path.exists():
        raise FileNotFoundError(f"Missing script: {script_path}")

    with tempfile.TemporaryDirectory(prefix="stat3d-regression-") as tmpdir:
        tmpdir_path = Path(tmpdir)
        out_matrix = tmpdir_path / "matrix.mtx"
        out_features = tmpdir_path / "features.tsv"
        out_barcodes = tmpdir_path / "barcodes.tsv"

        snakemake_stub = _SnakemakeStub(
            input={
                "seg_data": str(seg_npy),
                "transcripts": str(transcripts_parquet),
                "average_nuclear_expansion_csv": str(average_nuclear_expansion_csv),
            },
            output={
                "matrix": str(out_matrix),
                "features": str(out_features),
                "barcodes": str(out_barcodes),
            },
            params={
                "pixel_size": pixel_size,
                "z_slice_micron": z_slice_micron,
                "nuc_exp_pixel": nuc_exp_pixel,
                "nuc_exp_slice": nuc_exp_slice,
            },
        )

        _exec_snakemake_script(script_path=script_path, snakemake_stub=snakemake_stub)

        # Byte-identical checks against the golden outputs.
        expected = {
            "matrix.mtx": golden_matrix,
            "features.tsv": golden_features,
            "barcodes.tsv": golden_barcodes,
        }
        produced = {
            "matrix.mtx": out_matrix,
            "features.tsv": out_features,
            "barcodes.tsv": out_barcodes,
        }

        failed = False
        for name in ("matrix.mtx", "features.tsv", "barcodes.tsv"):
            exp = expected[name]
            got = produced[name]

            exp_hash = _sha256(exp)
            got_hash = _sha256(got)

            if exp_hash != got_hash:
                failed = True
                print(f"FAIL: {name} differs")
                print(f"  expected: {exp} ({exp_hash})")
                print(f"  got:      {got} ({got_hash})")
            else:
                print(f"OK: {name} matches ({exp_hash})")

        if failed:
            print("\nOne or more outputs differ from the golden files.")
            print("If you are mid-refactor: ensure you preserve the exact coordinate policy and ordering.")
            return 1

    print("\nAll outputs match the golden files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
