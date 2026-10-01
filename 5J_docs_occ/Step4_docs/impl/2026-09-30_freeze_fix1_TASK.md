# TASK (employee, Sonnet): 5J Step 4 fix 1: an effect-good stand-in for val 2.0, a real planted high floor for val 5.2, perturbations.md filled

Written 2026-09-30 19:37 EDT (from `date`) by the 5J manager. Read first, in full: `Step4_docs/impl/2026-09-30_freeze_TASK.md`
(the parent task: its hard rules apply unchanged), `Step4_docs/impl/2026-09-30_freeze.md` (state + ledger, incl. "Verified
(manager)"), `Step4_docs/outputs_step4/gates_frozen.md`, `Step4_docs/outputs_step4/perturbations.md`, `tools/speed/frz_standins.py`,
`tools/speed/frz_chain.sh`, `tools/speed/frz_score.sbatch`, `tools/speed/frz_summarize.py`, and the scorer's G5J.3/G5J.4 block
(`tools/speed/5thJ_04_scorer.py` lines 440-490). State file: create `Step4_docs/impl/2026-09-30_freeze_fix1.md` (same sections as
the parent); `date` before every stamp.

## Hard rules (unchanged from the parent; repeated because they matter)
* 🔴 ALL compute on Speed via sbatch (`-p ps -t 7-00:00:00 --exclude=antenna1`, at most 30 CPUs in total at once, python
  `/speed-scratch/o_iseri/envs/step4/bin/python -u`). Locally ONLY edit/write files, ssh/scp, ls, read small files. Login node:
  sbatch/squeue/sacct/scancel/scp/ls and single-file cat/tail/grep/wc -l only (no `du`, no loops, no python).
  At most 6 sacct checks of 30 s per job; then write "manager to read" and stop.
* 🔴 NO TEST DATA: runs only through `split_loader.load_split`, only `development`, `validation`, `b0_dev`, `b0_val`, `replicates`.
  Never create `gates_frozen.md5`.
* 🔴 UK licence: Spain and Italy only; no UK file; no folder-wide search, no wildcard that could match a UK file.
* Additive only: do not overwrite any existing stand-in folder, score file or log. New names below.
* Past ~150k tokens: stop, write state, "handoff needed".

## What the manager found (2026-09-30 19:35, numbers read from the job outputs)
1. **val 2.0 not met.** The "good" stand-in (EnergyPlus + noise, SD 10 % of the run's hourly SD, independent per run) fails G5J.3 in
   15 of 32 cells: every heating and cooling cell except Italy AB heating (R² from -11.9 to 0.43, e.g. SFH es heating -11.87).
   Its annual sign agreement stays ≥ 0.965 and its G5J.2 passes 32/32. Cause: the hourly occupancy effect on heating/cooling is a
   few % of the run's hourly SD, so independent 10 % noise in each run swamps the pair difference. The manager re-derived Italy AB
   with its own code (job 1404325): pairs 1,032, R² heating 0.537589, cooling 0.427292, equipment 0.989430, total 0.980020 — equal to
   the scorer. This is a RESULT, not a scorer bug: keep it (row 0 below). The gate is NOT relaxed.
2. **val 5.2 never fired.** `sc_highk` used `--k 1e7`, but the threshold is `max(k·√2·floor, 0.001)` and the floor is 0, so k does
   nothing: G5J.3 came out 17 PASS / 15 FAIL / 0 NOT_EVALUABLE, the same as `sc_good`. The planted high floor must be a floor.
3. `frz_misc` (1404320) shows sacct FAILED 2:0 while its output is complete: the last command is the `ls` of the absent
   `gates_frozen.md5` (ls exits 2). Record this; do not rerun.

## Manager rulings (write them into `gates_frozen.md` as "ruled by the manager 2026-09-30")
R1. **Two stand-ins, two jobs.** `good` (unchanged) is renamed in the docs "ASHRAE-good, effect-blind" and stays as row 0 of the
    perturbation table (it passes the absolute-accuracy gate and fails the effect gate on heating and cooling: the paper's premise
    shown on a second stand-in). val 2.0 ("a good predictor passes every gate") is shown with a new stand-in `effgood`.
R2. **`effgood` definition** (validation groups = climate x building, as in `frz_standins.py`). For flat index j of a group with m runs,
    per target and hour: μ_j = mean over the m runs of EP_r[j]; D_r,j = EP_r[j] − μ_j;
    `effgood_r[j] = EP_r[j] + 0.10·SD_h(μ_j)·z_shared + 0.10·SD_h(D_r,j)·z_r`,
    SD_h over the 8,760 hours of that flat (ddof=0); z_shared ~ N(0,1) identical for every run of the flat
    (seed = md5("<climate>|<building>|<j>|effgood_shared|20260930")[:15] as int), z_r per run and flat
    (seed = md5("<run_id>|<j>|effgood|20260930")[:15]). The shared part is the error a surrogate makes on the flat's load level
    (it cancels in a pair); the run part is 10 % of the occupancy deviation. m = 1: D = 0, so only the shared part. B0 runs:
    only the shared part with μ = EP of that run. Write this definition in `gates_frozen.md` and at the top of the new script.
R3. **Rows rebuilt on effgood** (so each row shows a PASS turning into a FAIL): `effbldmean` = per flat, the mean of `effgood` over
    the m runs of the group (occupancy effect exactly zero); `effshift2` = effgood rolled by 2 h (wrap-around); `effdeleted` =
    symlinks to effgood minus the first validation run in sorted order; row 2 (training mean) is reused as is (it does not depend on
    the base) and compared against effgood. B1 = `weakb1` (unchanged), control of the main run = `effbldmean`.
R4. **Planted high floor (val 5.2):** a floors file `out/floors_PLANTED_HIGH.json`, same layout as `out/floors.json`, every floor
    = 1.0e6 kWh; run the scorer on `effgood` with `--floors` that file. Expected: G5J.3 NOT_EVALUABLE in all 32 cells (fewer than 30
    pairs above the floor), SUMMARY NOT_EVALUABLE > 0, SCORER_EXIT 2. Print the file's md5 in the job; state in `gates_frozen.md`
    that `sc_highk` (k only) is inert while the floor is 0.
R5. If `effgood` does NOT pass every gate except 1.1: stop, report the failing lines. Do not change 0.10 or any threshold.

## Parts
A. `tools/speed/frz_standins_eff.py` + sbatch: writes `out/standins/{effgood,effbldmean,effshift2,effdeleted}/` (8 CPUs, as
   `frz_standins.py`; reuse its `write_pred` layout and `%.8g`). Print per folder the file count and, for 3 runs, the median
   over flats of SD(effgood − EP)/SD(D) for the run part in one group with m ≥ 2 (expect about 0.10 + shared term; print both parts).
B. Scorer jobs (6 CPUs each, ≤ 30 in total), new tags: `sc_effgood` (`--pred effgood --b1 weakb1 --control effbldmean --secondary
   --selftest 20`), `sc_effdeleted`, `sc_trainmean_vs_eff` (only if the summary needs a new before; else reuse sc_trainmean and say so),
   `sc_effbldmean`, `sc_effshift2`, `sc_effctrl` (`--pred effgood --control effgood`), `sc_highfloor` (R4). Chain them with
   `--dependency=afterok:<standins job>`.
C. Extend `frz_summarize.py` additively (new function or flag) so `out/perturb_summary_eff.txt` prints the before (effgood) / after
   lines for every eff row, the G5J.2 per class/country/target lines of `effbldmean` (premise, val 2.1b), and the `CHECK 2.3` line
   of EVERY tag (old and new): opens outside the allowed lists must be 0 everywhere.
D. Fill `outputs_step4/perturbations.md`: row 0 = good (ASHRAE-good, effect-blind: its G5J.2 32/32 PASS, G5J.3 15 FAIL, list the
   15 cells with R²), then rows 1-5 on effgood with before/after counts and the cells that changed; the building-mean G5J.2 table
   for BOTH bldmean (old) and effbldmean; the planted crash (`sc_crash`: G5J.5 NOT_EVALUABLE 1, crashed=True, SCORER_EXIT 1);
   the planted high floor (R4); the null (1404311/1404323: 99.98 % of 6,400, min cell 99.5 %, PASS against 93 %). Plain words;
   every number with its source file.
E. Update `gates_frozen.md` (R1-R4, the stand-in definitions, "sc_highk inert while floor 0"); keep the ASHRAE marker. Then one small
   job: md5 of `gates_frozen.md`, the scorer and `split_loader.py` on Speed after you scp them, gate 1.1/1.2 lines again
   (copy `frz_misc.sbatch` to a new file; end it with `ls ... || true` so the job exits 0 and say why).

## Report back (short, plain)
effgood SUMMARY lines and exit; the eff rows before/after; highfloor lines; CHECK 2.3 per tag; md5s; JobIDs; CPU-hours.
Status "DONE except freeze (ASHRAE page pending)"; Next = "manager verifies".

## What the manager will re-derive
With its own code: effgood R² and sign for one heating cell and Italy AB (all 4 targets); the run-part noise ratio; the pair count;
0 locked runs in every open log.
