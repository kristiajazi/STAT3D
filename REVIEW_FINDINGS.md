# STAT3D Pipeline Review - Detailed Findings
## Comprehensive Analysis for Nature Computational Science Submission

**Date:** January 15, 2026  
**Reviewer:** GitHub Copilot Agent  
**Scope:** Full pipeline review for publication readiness

---

## Executive Summary

**Overall Publication Readiness Score: 5.5/10** ❌ Below Standards

The STAT3D pipeline demonstrates solid scientific methodology and well-designed workflow architecture. However, it contains **critical reproducibility and robustness issues** that must be addressed before submission to Nature Computational Science. The primary concerns are:

1. **Lack of automated testing and validation**
2. **Critical memory efficiency problems with large 3D datasets**
3. **Missing error handling throughout the pipeline**
4. **Incomplete reproducibility guarantees**
5. **Insufficient benchmarking data**

**Estimated remediation time: 2-3 weeks**

---

## 1. Workflow Robustness Analysis

### 1.1 Error Handling ❌ CRITICAL

**Issues Found:**
- Most shell commands in Snakefile lack error checking
- External tool failures (QuPath, Cellpose, R scripts) fail silently
- No validation of intermediate outputs before downstream processing
- Python scripts lack try-catch blocks for file I/O and data processing

**Impact:** Pipeline can proceed with corrupted/missing data, producing invalid results

**Example Problems:**
```python
# workflow/Snakefile line 142
rule run_zslice_script:
    shell: "QuPath script --image {input.image} {input.script}"
    # No error checking - QuPath failure not caught
```

**Recommendations:**
1. Add `set -euo pipefail` to all shell rules
2. Wrap critical operations in try-catch blocks
3. Validate outputs exist and are non-empty before continuing
4. Add schema validation for CSV/parquet files

### 1.2 Checkpointing and Resumability ⚠️ INADEQUATE

**Issues Found:**
- No Snakemake checkpoints defined
- Failed pipelines require full re-run
- No intermediate state validation
- Large outputs (segmentation, matrices) not protected

**Impact:** Wasted compute time on partial failures; cannot resume long-running jobs

**Recommendations:**
1. Add checkpoints after expensive operations (segmentation, matrix generation)
2. Implement output validation steps
3. Use Snakemake's `--rerun-incomplete` properly
4. Add file integrity checks (checksums)

### 1.3 Resource Management 🚨 MISSING

**Critical Issue:** No resource declarations in any rules

**Problems:**
- GPU jobs don't request GPU resources (line 229-244 of Snakefile)
- No memory limits - cellpose can consume all RAM
- No timeout handling for long-running tasks
- Cluster schedulers can't allocate properly

**Example Fix Needed:**
```python
rule run_cellpose:
    resources:
        gpus=1 if config["cellpose_use_gpu"] else 0,
        mem_mb=lambda wildcards, attempt: 32000 * attempt,
        runtime=lambda wildcards, attempt: 240 * attempt
    threads: 4
    retries: 2
```

---

## 2. Environment Configuration and Reproducibility

### 2.1 Dependency Management ⚠️ LOOSE PINNING

**Critical Findings:**

**pixi.toml Issues:**
- 30+ dependencies use wildcard versions (`*`)
- No `pixi.lock` file committed to repository
- Platform lock-in: only `linux-64` supported
- Python minor version not pinned (3.10 vs 3.10.13)

**Impact:** Different users get different dependency versions → non-reproducible results

**Examples:**
```toml
# pixi.toml - TOO LOOSE
pyarrow = "*"           # Should be: ">=15.0.0,<16.0.0"
r-tidyverse = "*"       # Should be: ">=2.0.0,<3.0.0"
python = "3.10"         # Should be: "3.10.13"
```

**Recommendations:**
1. **CRITICAL:** Commit `pixi.lock` to version control
2. Replace all `*` with version ranges
3. Add macOS support: `platforms = ["linux-64", "osx-64", "osx-arm64"]`
4. Pin Python to specific minor version

### 2.2 Docker Configuration ✓ MOSTLY GOOD

**Strengths:**
- Specific CUDA version (12.6.0-base)
- QuPath and Pixi versions pinned
- Cellpose model pre-downloaded

**Issues:**
- Manual R package installation suggests conda can't resolve them
- PyTorch installed via pip instead of conda (line 46-49 of Dockerfile)
- No ARM64 support for Apple Silicon

---

## 3. Core Script Analysis

### 3.1 cell_to_transcript.py 🚨 SEVERE ISSUES

**Critical Memory Problem:**

Line 47 creates dense DataFrame: `pd.DataFrame(0, index=..., columns=cells, dtype=np.int32)`

**Impact:** With 20,000 genes × 100,000 cells:
- Dense matrix: **8 GB RAM**
- Should use sparse: **~200 MB RAM** (40x reduction)

**Performance Bottlenecks:**
1. `.iterrows()` on line 52-88 (slowest pandas iteration)
2. `.at[]` accessor in hot loop (line 88)
3. Redundant coordinate dictionary rebuild (line 101)

**Recommended Refactor:**
```python
from scipy.sparse import lil_matrix

# Use sparse from the start
matrix = lil_matrix((len(features), len(cells)), dtype=np.int32)

# Vectorize main loop - 10-100x faster
data = transcripts_df[['feature_name', 'x_location', 'y_location', 'z_location']].values
for feature, x, y, z in data:
    # Direct numpy operations
    x_idx, y_idx, z_idx = int(round(x)), int(round(y)), int(round(z))
    cell_id = mask_array[z_idx, y_idx, x_idx]
    if cell_id > 0:
        feature_idx = feature_to_index[feature.encode('utf-8')]
        matrix[feature_idx, cell_id] += 1
```

### 3.2 Error Handling in Scripts ❌ MISSING

**Problems:**
- No validation that Snakemake inputs exist
- No try-catch for file I/O operations
- No bounds checking on array indexing
- `allow_pickle=True` security risk without validation

**Examples of Missing Checks:**
```python
# cell_to_transcript.py line 29 - NO ERROR HANDLING
seg_data = np.load(seg_data_path, allow_pickle=True).item()
# Should be:
try:
    if not os.path.exists(seg_data_path):
        raise FileNotFoundError(f"Segmentation file not found: {seg_data_path}")
    seg_data = np.load(seg_data_path, allow_pickle=True).item()
    if 'masks' not in seg_data:
        raise ValueError("Segmentation data missing 'masks' key")
except Exception as e:
    logging.error(f"Failed to load segmentation: {e}")
    raise
```

---

## 4. Documentation and Testing

### 4.1 README Quality: 7/10 ⚠️ GAPS

**Strengths:**
- Clear Docker installation steps
- Comprehensive parameter table
- Good output descriptions

**Critical Gaps:**
1. **Git LFS not mentioned** - users will download corrupt .tif files
2. No end-to-end quick start example
3. Missing troubleshooting section
4. Hardcoded Windows paths in usage examples

**Fix Needed:**
```markdown
## Prerequisites

1. **Git LFS**: Large files (images, parquet) require Git LFS
   ```bash
   git lfs install
   git clone https://github.com/kristiajazi/STAT3D.git
   git lfs pull  # Download actual data files
   ```

2. **Docker Desktop**: Install from https://docs.docker.com/desktop/
```

### 4.2 Testing Infrastructure: 3/10 ❌ INADEQUATE

**Critical Problems:**
- **No automated tests** - all "tests" are manual scripts
- **No CI/CD pipeline** - no GitHub Actions workflows
- **Test scripts have hardcoded Windows paths:**
  ```R
  # tests/test_sopa/sopa_analysis.R line 5
  source("C:\\Users\\Kristi\\miniconda3\\...\\seurat_object_preprocessing.R")
  ```
- **No unit tests** for Python scripts
- **No integration tests** for full pipeline

**Publication Standard Requirement:**
Nature Computational Science requires automated validation of reproducibility

**Recommended Testing Structure:**
```
tests/
├── unit/
│   ├── test_cell_to_transcript.py
│   ├── test_process_tiff.py
│   └── test_laplacian_score.py
├── integration/
│   ├── test_toy_dataset_2D.sh
│   ├── test_toy_dataset_3D.sh
│   └── test_full_pipeline.sh
└── fixtures/
    ├── sample_config.yaml
    └── expected_outputs/
```

### 4.3 Toy Dataset Issues ❌ BROKEN

**Problems:**
1. Config files reference wrong filenames:
   - `config_toy_dataset_3D_GPU.yaml`: `/stat3d/TC70_cropped.ome.tif` ✓
   - `config_3D_GPU.yaml`: `/stat3d/morphology_K.ome.tif` ❌ (doesn't exist)

2. Git LFS required but not documented

3. No validation script to verify dataset integrity

**User Experience:**
```bash
# What happens now:
git clone https://github.com/kristiajazi/stat3d.git
# Downloads 125-byte LFS pointer file instead of 56MB .tif
docker run ... snakemake
# FAILS: "morphology file not found"
```

---

## 5. Configuration Consistency

### 5.1 Coverage Matrix ✓ COMPLETE

All valid CPU/GPU × 2D/3D permutations exist:

| Config | 2D CPU | 2D GPU | 3D CPU | 3D GPU |
|--------|--------|--------|--------|--------|
| **Generic** | ✓ | ✓ | ✓ | ✓ |
| **HCP Dataset** | ✓ | ❌ | ✓ | ❌ |
| **Toy Dataset** | ✓ | ❌ | ❌ | ✓ |

**Gap:** Missing GPU configs for HCP and incomplete toy dataset variants

### 5.2 Parameter Validation ❌ NOT IMPLEMENTED

**Risk:** Invalid configs accepted silently

**No runtime checks for:**
- File existence (`INPUT_TIFF`, `transcripts_df`)
- LEVEL/PIXEL_SIZE alignment
- MIN_AREA < MAX_AREA
- CPU + 3D + large dataset = likely to fail

**Recommendation:**
Add config validation rule at pipeline start:
```python
rule validate_config:
    run:
        if not os.path.exists(config["INPUT_TIFF"]):
            raise FileNotFoundError(f"INPUT_TIFF not found: {config['INPUT_TIFF']}")
        if config["MIN_AREA"] >= config["MAX_AREA"]:
            raise ValueError("MIN_AREA must be less than MAX_AREA")
        # ... more validations
```

---

## 6. Publication-Specific Requirements

### 6.1 Benchmarking Data ❌ MISSING

**Nature Computational Science Requirement:**
Performance comparison against existing tools/methods

**Missing Comparisons:**
- STAT3D vs standard 2D Seurat workflow
- Runtime analysis (CPU vs GPU, 2D vs 3D)
- Memory usage profiling
- Accuracy metrics vs manual annotation

**Recommendation:**
Add `benchmarks/` directory with:
1. Timing results for toy/HCP datasets
2. Comparison with 2D-only analysis
3. Resource usage plots
4. Validation against manual segmentation

### 6.2 Code Style ⚠️ INCONSISTENT

**Python (PEP8):**
- No linting enforced
- Inconsistent naming (camelCase vs snake_case)
- Missing docstrings
- Line length violations

**R (tidyverse):**
- Not checked
- Test scripts use base R syntax

**Recommendation:**
1. Add `.pre-commit-config.yaml` with black, flake8, isort
2. Run `black workflow/scripts/` to auto-format
3. Add R linting with `lintr` package

---

## Priority Action Items

### Must-Fix Before Submission (2-3 weeks)

1. **Add automated testing** (Highest Priority)
   - Create GitHub Actions CI workflow
   - Write integration tests for toy dataset
   - Validate all 8 config permutations pass

2. **Fix memory efficiency** (Critical for 3D)
   - Refactor cell_to_transcript.py to use sparse matrices
   - Add memory profiling to verify improvements

3. **Improve reproducibility**
   - Commit pixi.lock file
   - Pin all wildcard dependencies
   - Document Git LFS requirement

4. **Add error handling**
   - Wrap shell commands with error checking
   - Add try-catch to Python scripts
   - Validate intermediate outputs

5. **Create benchmarking data**
   - Run timing comparisons
   - Document resource requirements
   - Compare against 2D workflows

6. **Fix documentation gaps**
   - Add Git LFS to README
   - Create end-to-end quick start
   - Remove hardcoded paths from tests

### Should-Fix (1 week)

7. Add resource management to Snakefile
8. Implement checkpointing
9. Add config validation
10. Expand platform support (macOS)
11. Add code linting

### Nice-to-Have (Optional)

12. Parameter sensitivity analysis
13. Troubleshooting guide
14. Video tutorial
15. Jupyter notebook examples

---

## Conclusion

STAT3D is a **well-designed scientific pipeline with strong potential**, but requires significant hardening before publication in Nature Computational Science. The core scientific methodology appears sound, but **reproducibility, testing, and robustness must be dramatically improved**.

**Primary blockers for publication:**
1. No automated testing or CI/CD
2. Critical memory issues with large datasets
3. Missing reproducibility guarantees (pixi.lock, version pinning)
4. Insufficient benchmarking data
5. Broken toy dataset workflow

**Recommendation:** Allocate 2-3 weeks for focused remediation work before submission. Prioritize automated testing infrastructure first, as this will catch many other issues during development.

**Contact:** For questions about this review, please open an issue on the GitHub repository.
