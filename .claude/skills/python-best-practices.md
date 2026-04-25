---
name: python-best-practices
description: Python conventions for the eSim codebase — Python 3.9+, joblib/loky, pandas safety, no hardcoded paths.
scope: builder, reviewer
---

# Python Best Practices (eSim)

These rules are project-specific. They override generic Python style guides where they conflict.

## Version and language features

- **Python 3.9+ only.** Use `dict | None` style (PEP 604) is allowed from 3.10 — for 3.9 compatibility prefer `Optional[dict]`.
- Type hints on public functions in `eSim_occ_utils/` and `eSim_bem_utils/`. Internal helpers may skip them.
- f-strings only — never `%`-formatting or `.format()`.

## Path discipline (non-negotiable)

- **Never hardcode** GSS, Census, IDF, weather, or output paths.
- All occupancy-side paths come from `eSim_occ_utils/occ_config.py` (and optional `GSS_BASE_DIR` env var).
- All BEM-side paths come from `eSim_bem_utils/config.py` (and optional `ENERGYPLUS_DIR` env var).
- New paths added to a script must be added to `occ_config.py` / `config.py` first, then imported.
- A grep for `r"C:\\"`, `/Users/`, `/home/` outside config files is a defect.

## Pandas

- Reset or set the index explicitly at every boundary; do not rely on positional alignment.
- After every join/merge, assert expected row count and check for `NaN` introduction in key columns.
- Use `pd.merge(..., validate="one_to_one"|"one_to_many"|"many_to_one")` whenever the relationship is known.
- Never `inplace=True`. Reassign.
- Convert categorical demographic codes through a single mapping module — not ad-hoc per script.

## Multiprocessing

- Use **joblib with the loky backend**: `Parallel(n_jobs=N, backend="loky")`.
- Never `multiprocessing.Pool` directly — it's incompatible with how the rest of the pipeline starts subprocesses on Windows and on the cluster.
- `n_jobs` should default to `-1` only inside scripts run interactively. Cluster-bound scripts should read `n_jobs` from CLI or config so SLURM can constrain it.

## Numpy / arrays

- EnergyPlus annual schedule arrays must be `len == 8760` and `dtype` numeric. Assert both before writing.
- Prefer vectorized operations over Python loops on >10k-row data.

## I/O

- Use `pathlib.Path`, not `os.path`.
- Open text files with explicit `encoding="utf-8"`.
- Parquet is the default interchange format for processed data; CSV only for human-inspectable summaries.

## Errors and logs

- Raise specific exceptions (`ValueError`, `KeyError`) — not bare `Exception`.
- Use the existing logging conventions in each module; do not introduce a new logger framework.
- Never log raw GSS/Census microdata rows. Aggregate counts and column names only.

## Testing hooks

- New public functions get at least one test in `eSim_tests/`. See `test-writing` skill.
