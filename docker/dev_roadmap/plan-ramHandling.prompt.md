## Plan: RAM-aware pipeline refactor

Add configurable memory settings to Snakemake, apply rule-level memory heuristics for heavy tools, and enable standard runtime/resource reporting for benchmarking. This will make runs more stable on HPC and reproducible across machines, while keeping configuration simple for end users. We’ll work on a new branch, add config keys, set per-rule `resources` and `benchmark`, and document recommended CLI flags for reporting.

### Steps
1. Create a new branch for RAM handling changes.
2. Add `memory_mb` (and optional per-rule overrides) to configs in configs/.
3. Implement rule `resources: mem_mb=...` in workflow/Snakefile.
4. Add heuristics for memory sizing based on file sizes and modes.
5. Add `benchmark:` outputs for heavy rules and document reporting flags.

### Further Considerations
1. Should memory be global only, or allow per-rule overrides (e.g., `memory_cellpose_mb`)?
2. Report format preference: Snakemake `--report` or per-rule `benchmark` files?
3. Optional: add a small “safe mode” to reduce memory (e.g., tile processing)?

Draft for your review—what should I adjust before proceeding?
