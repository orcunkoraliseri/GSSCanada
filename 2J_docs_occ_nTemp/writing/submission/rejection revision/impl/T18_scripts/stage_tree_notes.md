# T18 stage_tree layout notes

Task doc: `2026-09-15_T18_wp1_rebuild_2022_build.md`. Speed root:
`/speed-scratch/o_iseri/2J_revision/T18/`.

```
T18/
  T18_scripts/                 -- this directory's files (scp'd verbatim)
    t18_filter.py
    t18_pipeline.py
    t18_metrics.py
    t18_chain.sh
  input/
    augmented_diaries.csv      -- full 192,183-row pool (Arm C's own input;
                                   also t18_filter.py's input for Arm N)
    Aligned_Census_2022.csv    -- identical for both arms
  arm_C/repo/
    scripts/                   -- copies (not symlinks) of:
      05_census_linkage.py
      05_postlink_rake.py
      07_aug_to_bem.py
      activity_loads.py        -- co-located: 07_aug_to_bem.py does
                                   sys.path.insert(0, str(HERE)); import
                                   activity_loads at MODULE-IMPORT time, before
                                   t18_pipeline.py gets a chance to patch
                                   anything, so this file MUST sit next to
                                   07_aug_to_bem.py on disk.
      07_bemIntegrationGSS_val.py
    outputs/aug_pipeline/      -- OUT_DIR equivalent; created by the chain
    outputs/BEM_Setup/         -- BEMS equivalent; created by the chain
    (no inputs/ -- Arm C reads T18/input/augmented_diaries.csv and
     T18/input/Aligned_Census_2022.csv directly; no per-arm duplicate needed
     since t18_pipeline.py monkeypatches AUGMENTED_DIARIES/CENSUS_FILE anyway)
  arm_N/repo/
    scripts/                   -- same 5 files, second copy
    inputs/
      augmented_diaries.csv    -- CYCLE_YEAR==2022 only (written by
                                   t18_filter.py ON Speed, NOT scp'd from local)
    outputs/aug_pipeline/
    outputs/BEM_Setup/
    (Aligned_Census_2022.csv also read directly from T18/input/ -- identical
     for both arms, not duplicated)
  reference/                   -- READ-ONLY copies of the CURRENT on-disk
                                   production files, for R0 (never written to
                                   by any job; N3's "local-origin files" whose
                                   md5 must stay unchanged before/after):
    21CEN22GSS_aug_Full_Schedules.csv        (573,177,990 B)
    21CEN22GSS_aug_Matched_Keys.csv          (10,809,829 B)
    21CEN22GSS_aug_Full_Aggregated_excl.csv  (598,812,455 B)
    BEM_Schedules_2022.csv                   (673,929,104 B)
  logs/                        -- #SBATCH --output target directory
  out/                         -- t18_metrics.py's output CSVs land here:
    t18_metrics_C.csv, t18_metrics_N.csv, t18_r0_C.csv
```

Why no directory-depth mirroring of the real repo (unlike T17's precedent,
which had to replicate `<ROOT>/BEM_Setup/WeatherFile/` etc. because
`main.py`'s `BASE_DIR` was not CLI-overridable): `t18_pipeline.py` monkeypatches
every path constant each of the four scripts uses (`AUGMENTED_DIARIES`,
`CENSUS_FILE`, `OUT_DIR`, `_FULL_SCHED_PATH`, `_MATCHED_KEYS_PATH`, `AUG`,
`BEMS`) directly on the imported module object before calling any function, so
the physical staging depth is irrelevant to those scripts' behaviour. See
`t18_pipeline.py`'s own docstring (Decision 1) for the BASE-path bug this
finding surfaced in `05_census_linkage.py` itself, on the live repo, unrelated
to staging.
