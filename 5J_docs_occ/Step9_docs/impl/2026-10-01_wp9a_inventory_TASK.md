# 5J Step 9a: inventory for the Model A design (task doc for a fresh employee; read-only)

Written 2026-10-01 14:59 EDT by the 5J manager. Parent: `Step9_docs/5thJ_09_modelA.md` (fill every value marked MEASURE).
State file you keep: `Step9_docs/impl/2026-10-01_wp9a_inventory.md` (Ledger, Verified, Decisions, Next, WHAT I DID NOT VERIFY).
You write nothing else. You change no file, start no simulation, and do not touch the author's running default-schedule jobs.

## 🔴 Rules (binding)
* **UK licence:** never open, list or run anything for London or the UK: no path containing `GB`, `LDN`, `London`, `STDUNSTANS`,
  `uk` or `_uk`, in OpenUBEM, 4J or 5J, and no 4J pooled corpus (only `4J_step3_corpus_es_it.jsonl`). Lyon (`FR-LYO`) is not
  needed either. If a listing you asked for shows a UK name, do not open it and do not copy it into your notes.
* **No folder-wide or repo-wide search, no recursive listing, no wildcard that could match a UK file.** List only the named
  directories below (one level), and open only files named in full.
* Compute: local reading with `py -3.13` is allowed (the author allows half the desktop, at most 10 CPUs). On Speed, only
  `sbatch` (never python on the login node; `-t 7-00:00:00`, `--exclude=antenna1`, at most 4 CPUs for this task). Never wait for a
  job: submit, write the job id in the state file, and stop.

## What to find (write each value with the file and line or job it came from)
1. **OpenUBEM district inputs** for `ES-MAD-BERRUGUETE` and `IT-BOL-GALVANI2` (2026-09-08 recut). Start from the head block of
   `C:/Users/o_iseri/Desktop/OpenUBEM/docs/docs_ACTIVE/europeanLocations/STATE_european_locations_v5.md` and the paths it names
   (for example `openubem/outputs/eu_evidence/EU-11/<D>_merged_2026-09-08/summary.json`, `outputs_3D/eu_<D>_data/layouts/`).
   Report: where the per-building IDFs or the builder script live; the weather file used (name, md5); HVAC and setpoints;
   building count and dwelling count per district; class counts; the `nocore_equal_area` vs fallback counts (state block says
   1,151 / 23 Madrid, 1,171 / 40 Bologna; check).
2. **Per-building and per-dwelling metadata** available for a building vector: which columns exist (class, storeys, footprint,
   floor of dwelling, dwelling floor area, facade length, construction period or TABULA code, orientation, neighbours / shading),
   with the file that holds them and the share of missing values.
3. **Run time per building** of the 2026-09-08 recut on Speed (jobs `1314028` Madrid, `1314067` Bologna, read-only `sacct` or
   their logs as named in the OpenUBEM docs): median and 90th percentile seconds per building, and seconds per dwelling.
4. **The 5J side:** how `4J_docs_occ/tools/4thJ_step10_nocore_campaign.py` (Spain fold only) takes household schedules, and
   whether 5J's extractor `5J_docs_occ/tools/speed/mzp_extract.py` can read its outputs (same meter names?). Read code only.
5. **Households and diary days, Spain and Italy only:** from `4J_step3_corpus_es_it.jsonl` (Speed:
   `/speed-scratch/o_iseri/5J/households/repo/4J_step3_corpus_es_it.jsonl`; use a local copy only if a path to it is written in a
   5J doc), count households and respondents per country with a positive weight, by household size; and, for a split of
   households 70 / 15 / 15 (seed 9001, stratified by size), the number of real diary days per bucket of the 4J schedule code
   (`4J_docs_occ/tools/4thJ_step7_schedules.py`, buckets at lines ~198-263: age band, sex, household type, economic status, day
   type) per split, and how many buckets would need back-off. Python on the corpus runs only as an sbatch job (or locally if a
   named local copy exists). Spain and Italy rows only; the file is UK-free.

## Done means
Every item above has a value with its source, or `NOT FOUND` with what you tried; the state file lists every file and job you
read; nothing UK was opened or listed; no file other than the state file was written. End your turn with "state written".
