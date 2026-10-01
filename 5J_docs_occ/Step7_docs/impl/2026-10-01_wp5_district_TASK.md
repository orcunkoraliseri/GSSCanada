# TASK (employee, Sonnet): 5J Step 7 part A: district twins, household pool, sealed draws, timing pilots

Written 2026-10-01 04:22 EDT by the 5J manager (`date` before every stamp you write). Read first, in full:
`Step7_docs/impl/2026-10-01_step7_design.md` (THE RULING; R7-1 to R7-5), `Step7_docs/impl/2026-10-01_step7_facts.md`,
`Step7_docs/5thJ_07_speedDistrict.md` and `_val.md`, `Step2_docs/outputs_step2/campaign_design.md` (how building rows, run rows
and placements are made), `Step2_docs/impl/2026-09-29_wp1_households_v2.md` (how households were drawn and built),
`tools/speed/camp_plan.py`, `camp_task.py`, `camp_common.py` (campaign run machinery), `tools/speed/s6_store.py`,
`s6_data.py`, `s6_pred_task.py` (how a store and S predictions are built for a new run list; Step 6 part A).
State file: create `Step7_docs/impl/2026-10-01_wp5_district.md` (Ledger / Verified / Decisions / Next / WHAT I DID NOT VERIFY).

## Hard rules
* Speed sbatch only; nothing on the local CPU (no local awk/python either). Login node: sbatch/squeue/sacct/scancel/scontrol/
  scp/ls and single-file cat/tail/grep/wc/head only. All 5J jobs together <= 30 CPUs; GPU at most 4 slices (`-p ps
  --gres=gpu:nvidia_a100_2g.20gb:1 -c 3 --mem=48G -t 7-00:00:00 --exclude=antenna1`). Spain only in this step; never a UK file;
  no folder-wide search or wildcard (open named files; `ls` to find names).
* Write only under a NEW folder `/speed-scratch/o_iseri/5J/district/` (and `Step7_docs/` locally). Never modify `campaign/`,
  `train/`, `test/`, `freeze/`, `splits/`, `households/` outputs of Steps 2-6 (new household builds go under `district/hh/`).
* Test truth of Step 6 is never read. Never wait for jobs: submit chains, write JobIDs, end. At most 6 sacct checks per job.
  Past ~150k tokens: write state, "handoff needed".

## Parts (one dependency chain where possible)
A. **Sample** (CPU job): list the 1,151 eligible Madrid payloads (the preflight list under
   `/speed-scratch/o_iseri/4J_step10_nocore/out/ES-MAD-BERRUGUETE/`), read class + `archetype_id` + real dwellings/storeys from
   each payload, draw 100 stratified by class (R7-1; seed 20261001), write `district/in/sample_buildings.csv` (real id, class,
   code, real dwellings, real storeys) and print the class counts of the 1,151 and of the 100. md5 the file into
   `district/in/SEALS.md5`.
B. **Twins** (same job): one 5J building row per sampled building (`district/in/twins_es.csv`, columns of
   `campaign/in/buildings_es_it.csv`; ids `es_T001..es_T100`), infiltration and north sampled by the campaign's own rule
   (find it in `camp_plan.py` / the design doc; same distributions, seed 20261002). Build each twin's IDF once with the 5J
   builder in a CPU job and record its dwelling count, k, floors (the twin's size) next to the real ones. Seal the file.
C. **Households** (CPU): pilot = 10 new Spanish households (not among the 60; weighted draw as households-v2, seed 6) built with
   `5thJ_step9_trigger_act2.py --hids` + `hh_build.py` into `district/hh/`; print seconds and MB per household; then the full
   set by R7-2 (500, or the largest of 300 / 200 that fits 4 CPU-h; write which and why). Check each built household like
   households-v2 did (8,760 rows, presence in [0,1], design level > 0); the 60 campaign households are REUSED from
   `households/inputs/` (not rebuilt).
D. **Draw seeds** (CPU): the per-draw seeds for up to 1,000 draws and the 20 EnergyPlus-check draw indices (seed 20261003),
   written to `district/in/draws.json` and sealed BEFORE any surrogate or EnergyPlus run (val 3.2). A draw assigns every dwelling
   of every twin one household from the pool by weight, with replacement; write the assignment rule as code
   (`tools/speed/s7_draws.py`) and print 3 example dwellings of draw 0.
E. **District store + surrogate pilot** (GPU, after C and D): store for draws 0-9 (store code path of Step 6 part A, store-dir
   argument, NO targets), S3 predictions (pinned, md5 checked) for those 10 draws; print seconds per dwelling-year (load,
   predict, write separated) and the STATIC_CLIP lines per twin (which twins are out of range). Fix N by R7-3 and write it.
F. **EnergyPlus pilot** (CPU): the 20 check draws' run table (`district/in/district_runs_es.csv`, campaign layout,
   placement = the draw's households) and a 1-draw pilot through the campaign wrapper (100 runs) with G5J.1-style integrity;
   print wall seconds per run and per dwelling. Do NOT launch the other 19 draws.
G. State file: JobIDs, every number above, N chosen, the in-range / out-of-range twin list. Next = "manager verifies part A;
   then part B (full draws, the 19 remaining EnergyPlus draws, comparison, speed)".

## Report back (short, plain)
JobIDs; class counts; twin sizes vs real; household pool size and build time; N and the pilot timings; status.

## What the manager will re-derive
One twin's static vector from its building row; one draw's household assignment from the seed rule; the per-run EnergyPlus
time from the pilot's clock lines.
