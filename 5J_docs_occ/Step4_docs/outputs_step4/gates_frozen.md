# 5J gates, frozen definitions (Step 4)

Written 2026-09-30 by the Step 4 employee (Sonnet) from `Step4_docs/5thJ_04_freezeGates.md` (spec 4A/4B/4C) and the
manager rulings of the task doc `Step4_docs/impl/2026-09-30_freeze_TASK.md`. FROZEN 2026-09-30 by the manager: the G5J.2 band
source is ASHRAE Guideline 14-2002 clause 5.3.2.4 f, p. 18 (read verbatim); the md5 of this file and of the scorer are in
`/speed-scratch/o_iseri/5J/gates_frozen.md5` and the checklist Step 4 box. Any later change is a dated AMENDMENT below, never an edit.
Scorer: `tools/speed/5thJ_04_scorer.py`.

Every numeric threshold is on a line that starts with `THRESHOLD` and carries `| source:` (gate 1.2 reads these lines).

## 0. What is scored

* Runs: Spain and Italy only (Step 3 campaign, 9,269 runs). Runs are read only through `split_loader.load_split`
  and only from `development`, `validation`, `b0_dev`, `b0_val`, `replicates`. The scorer refuses any other run id and logs every file open
  (`openlog_<tag>.tsv`); gate 2.3 counts opens of ids outside those five lists.
* Targets: heating, cooling, equipment electricity, total electricity (= equipment + heating/3 + cooling/3, COP 3.0 ASSUMED, as in the campaign files).
  Scored per dwelling class (SFH, TH, MFH, AB) and per country (es, it); never pooled over classes, countries or end uses. G5J.5 uses total electricity.
* Predictions folder: laid out like the campaign `extracted/` folder: `<climate_id>/<run_id>.csv.gz`, columns `dwelling, hour, heating_kwh, cooling_kwh, equipment_kwh, total_elec_kwh`, 8,760 rows per dwelling.
* File resolution: values are written with `%.8g`.

## 1. The pair rule (ruled by the manager 2026-09-30)

A pair is two households A, B in the SAME flat index of the same building and the same climate, in two different runs, both runs in the
same split, with A not equal to B. Under "every flat tested" (D2-8, ruling A) all such pairs are used: for every (building, climate) group
and every flat index j, every two runs of the group that have different households in flat j. For SFH and TH (one dwelling per run) this is
the pre-registered pair exactly. For MFH and AB the neighbours differ between the two runs, so the difference of energy use contains a
neighbour effect; this is stated as a limitation, it is not removed.
Secondary score, reported and not gated: each flat's effect against the same flat of its B0 run (the average household everywhere): R2 of (S_flat - S_B0flat) against (EP_flat - EP_B0flat).
Code: `toks[ia0] != toks[ib0]` in `_process_group` (scorer line 228).

## 2. Scores work on pair-level sufficient statistics (ruled by the manager 2026-09-30)

Per pair and target, over its n = 8,760 hours, with dEP(t) = EP_A(t) - EP_B(t) and dS(t) = S_A(t) - S_B(t):
n, sum dEP, sum dS, sum dEP^2, sum dS^2, sum dEP*dS, sum (dEP - dS)^2. The annual sum dEP and sum dS are the first two sums (an annual total of the hourly difference).
Hourly pair series are never held in memory together: the sums of all pairs of one flat come from Gram matrices of the centred series (`gram_pair_sums`, scorer line 127).

    R2 = 1 - SSE / SST
    SSE = sum over pairs of sum (dEP - dS)^2
    SST = sum over pairs of sum dEP^2  -  (sum over pairs of sum dEP)^2 / (n * number_of_pairs)

(`r2_from_sums`, scorer line 117). It equals 1 - sum(dEP - dS)^2 / sum(dEP - mean dEP)^2 over the hours of all pairs of the cell.
The equality is tested against a direct computation from the files on 20 random pairs (seed 20260930), 4 targets each, pair by pair and pooled:
must agree to 1e-9 (the scorer option `--selftest 20`, result in `perturbations.md` and the state file).

## 3. Gates (one line per gate, class, country, target; SUMMARY counts lines)

THRESHOLD G5J.1 every run of the split has a prediction file with 8,760 finite rows per dwelling, hour 1..8760 | source: Overview G5J.1 (campaign integrity) applied to the predictions; Step 3 part 2 checks C04
* G5J.1 (per class and country): PASS when no run of the split lacks a readable, complete prediction file. A missing run makes the cell FAIL; the other gates then use the runs that exist.

THRESHOLD G5J.2 hourly CV(RMSE) <= 30 % | source: ASHRAE Guideline 14-2002 (Measurement of Energy and Demand Savings), clause 5.3.2.4 f, p. 18 ("The computer model shall have an NMBE of 5% and a CV(RMSE) of 15% relative to monthly calibration data. If hourly calibration data are used, these requirements shall be 10% and 30%, respectively."), same band in Table 5-1 note 2, p. 17; read verbatim by the manager 2026-09-30 20:01 EDT from a public copy of the 2002 edition (author to check the 2014 edition carries the same clause); a reference only (Guideline 14 is for measured data); band ruled by the manager 2026-09-30
THRESHOLD G5J.2 hourly |NMBE| <= 10 % | source: ASHRAE Guideline 14-2002 (Measurement of Energy and Demand Savings), clause 5.3.2.4 f, p. 18 ("The computer model shall have an NMBE of 5% and a CV(RMSE) of 15% relative to monthly calibration data. If hourly calibration data are used, these requirements shall be 10% and 30%, respectively."), same band in Table 5-1 note 2, p. 17; read verbatim by the manager 2026-09-30 20:01 EDT from a public copy of the 2002 edition (author to check the 2014 edition carries the same clause); a reference only (Guideline 14 is for measured data); band ruled by the manager 2026-09-30
THRESHOLD G5J.2 pass rule: the median run of the cell is inside both bands | source: chosen by the employee on 2026-09-30 because spec 4A says "median and share of runs inside the band" but names no pass rule (CONFIRMED by the manager 2026-09-30 19:37, impl/2026-09-30_freeze.md "Verified (manager)", decision 1)
* G5J.2 load score. Per run and target: CV(RMSE) = RMSE / mean(EP) and NMBE = sum(S - EP) / sum(EP), over all dwelling-hours of the run (hourly). Reported per cell: median CV(RMSE), median |NMBE|, share of runs inside both bands. A run whose EP total is 0 is left out of the medians. The cell passes when the median CV(RMSE) <= 30 % and the median |NMBE| <= 10 %.

THRESHOLD G5J.3 R2 of dS against dEP over the hours of all pairs of the cell >= 0.5 | source: Overview G5J.3 and spec 4A (DRAFT of 2026-09-28, author/manager plan)
THRESHOLD G5J.3 annual sign agreement >= 80 % over pairs above the noise floor | source: Overview G5J.3 and spec 4A (DRAFT of 2026-09-28)
THRESHOLD G5J.3 the 95 % interval of the skill over B1 excludes 0 | source: Overview G5J.3 and spec 4A (DRAFT of 2026-09-28)
THRESHOLD G5J.3 NOT_EVALUABLE when fewer than 30 pairs are above the floor | source: spec 4A (DRAFT of 2026-09-28)
* G5J.3 occupancy effect, per cell: R2 (section 2); annual sign agreement = share of pairs above the floor with sign(sum dS) = sign(sum dEP); skill over B1 = R2(S) - R2(B1), with the 95 % interval (2.5 and 97.5 percentiles) from the two-way cluster bootstrap (section 5). Pass = all three conditions. NOT_EVALUABLE = fewer than 30 pairs above the floor, or R2 undefined (SST = 0).
* Above the floor: |sum dEP| > max(k * sqrt(2) * floor, resolution guard).

THRESHOLD noise floor multiplier k = 2 | source: spec 4A DRAFT k = 2, kept by the manager 2026-09-30
THRESHOLD resolution guard 0.001 kWh per pair and year | source: chosen by the employee on 2026-09-30 (CONFIRMED by the manager 2026-09-30 19:37, decision 2): the files have 8 significant digits, so a sum of 8,760 rounded differences can be wrong by a few 1e-5 kWh; 0.001 kWh makes "above the floor" mean "not zero at the file resolution" (ruling 3) without being fooled by rounding
* Noise floor (ruling 3, plainly): per target and class, the SD of the annual total over the repeats of one input, from the 200 Step 3 replicates (10 repeats x 20 inputs). The campaign measured a spread of 0 kWh on every target and every class (max minus min over the 10 repeats is exactly 0), so the floor is 0 (the printed SD of about 1e-12 kWh is floating-point summation of identical numbers). "Above the floor" therefore means the annual sum dEP is not zero at the file resolution (`%.8g`, guard above). The 4J non-determinism did not reproduce in 5J. The 20 replicate inputs are SFH 10, MFH 4, AB 6: there is no TH input; the TH floor is taken as the largest of the other classes (same, 0 in practice) and this is an assumption (employee, 2026-09-30).
  The "fewer than 30 pairs above the floor is NOT_EVALUABLE" rule is seen failing with a planted high floor (val 5.2). Fix 1 (ruled by the manager 2026-09-30): the first attempt, `sc_highk` (`--k 1e7`), is INERT while the floor is 0, because the threshold is max(k * sqrt(2) * floor, 0.001) and k multiplies 0; it is kept in the record as a failed attempt. The planted high floor is a floors file, `out/floors_PLANTED_HIGH.json` (same layout as `out/floors.json`, every floor = 1.0e6 kWh, md5 printed by its job), given to the scorer with `--floors` on the effgood stand-in (job `sc_highfloor`); expected: G5J.3 NOT_EVALUABLE in all 32 cells, SUMMARY NOT_EVALUABLE > 0, SCORER_EXIT 2.

* G5J.4 blind control. Control C = a predictions folder in which the occupancy information is removed. C is scored exactly like S (same pairs, same B1, same bootstrap). Pass for the paper: C FAILS G5J.3. If C passes, the G5J.4 line says "control passes ... G5J.3 FLAGGED FOR WITHDRAWAL". G5J.4 is NOT_EVALUABLE when G5J.3 of S or of C is NOT_EVALUABLE or when no control is given.

THRESHOLD G5J.5 daily total-electricity peak hour within +-1 h (circular over 24 h) | source: spec 4A (DRAFT of 2026-09-28)
THRESHOLD G5J.5 on >= 70 % of dwelling-days | source: spec 4A (DRAFT of 2026-09-28)
* G5J.5: per dwelling and day (365 days x 24 hours, hour 1..8760 cut into days), the hour of the largest total electricity value (first one if tied) of S and of EP; hit when they differ by at most 1 h (23 and 0 differ by 1). Share over all dwelling-days of the cell.
* G5J.6 (new country) and G5J.7 (speed): reported, not gated; not computed by this step.

## 4. Stand-ins and the perturbation table (validation split, no trained model exists)

THRESHOLD good stand-in noise: Gaussian, SD = 10 % of the run's hourly SD per target, fixed seed | source: ruled by the manager 2026-09-30 (ruling 4: noise at the floor size would be EnergyPlus itself)
THRESHOLD weak B1 stand-in (the reference for the skill score in the perturbation table): EnergyPlus + Gaussian noise, SD = 30 % of the run's hourly SD | source: chosen by the employee on 2026-09-30 (CONFIRMED by the manager 2026-09-30 19:37, decision 4; a stand-in until the real B1 of Step 5): with B1 = good-quality noise the good stand-in cannot beat it, so val 2.0 could never pass; the null test (val 3.2) uses the manager's construction (B1 = the good construction with an independent seed)
* Fix 1 (ruled by the manager 2026-09-30, rulings R1 to R5). Result that led to it: the good stand-in above, now called "ASHRAE-good, effect-blind", passes the absolute-accuracy gate (G5J.2 32/32) and fails the occupancy-effect gate G5J.3 in 15 of 32 cells (every heating and cooling cell except Italy AB heating): independent 10 % noise in each run swamps the small hourly occupancy effect on heating and cooling. This is a result, not a scorer defect (the manager re-derived Italy AB with its own code: equal to the scorer). No gate and no threshold was relaxed. It stays as row 0 of the perturbation table: the paper's premise shown on a second stand-in.
* R1. Two stand-ins. "ASHRAE-good, effect-blind" = `good` (unchanged) is row 0. Val 2.0 ("a good predictor passes every gate") is shown on a new stand-in `effgood`.
* R2. `effgood` definition (validation groups = climate x building; flat index j; m = runs of the group). Per target and hour: mu_j = mean over the m runs of EP_r[j]; D_r,j = EP_r[j] - mu_j; effgood_r[j] = EP_r[j] + 0.10 * SD_h(mu_j) * z_shared + 0.10 * SD_h(D_r,j) * z_r, with SD_h over the 8,760 hours of that flat (ddof=0); z_shared ~ N(0,1) identical for every run of the flat (seed = int(md5("<climate>|<building>|<j>|effgood_shared|20260930")[:15], 16)); z_r per run and flat (seed = int(md5("<run_id>|<j>|effgood|20260930")[:15], 16)). The shared part is the error a surrogate makes on the flat's load level (it cancels inside a pair); the run part is 10 % of the occupancy deviation. m = 1: D = 0, only the shared part. B0 runs: only the shared part with mu = EP of that run. Code: `tools/speed/frz_standins_eff.py`.
THRESHOLD effgood noise: shared part 10 % of SD_h(mu_j), run part 10 % of SD_h(D_r,j), fixed seeds | source: ruled by the manager 2026-09-30 (R2); not changed after seeing results (R5)
* R3. Rows rebuilt on effgood (so each row shows a PASS turning into a FAIL): `effbldmean` = per flat, the mean of effgood over the m runs of the group (occupancy effect exactly zero); `effshift2` = effgood rolled by 2 h (wrap-around); `effdeleted` = symlinks to effgood minus the first validation run in sorted order; row 2 (training mean) is reused as is (it does not depend on the base) and compared against effgood. B1 = `weakb1` (unchanged); control of the main run = `effbldmean`; the old `bldmean` table is kept for the record.
* R4. Planted high floor: see the noise-floor paragraph above.
* R5. If effgood does NOT pass every gate except 1.1, the failing lines are reported and neither 0.10 nor any threshold is changed.
* "Run's hourly SD": standard deviation over all dwelling-hours of the run, per target. Noise is independent per target and per hour (the total electricity column gets its own noise); values are not clipped at 0. Seeds: md5 of run id, label and base 20260930.
* Perturbations as in spec 4B: delete one run (scratch copy, symlinks); training mean per climate, class and hour of year (mean over the development split); building mean per flat index over all runs of the same building and climate in the split (of the good predictions); shift by 2 hours (wrap-around); G5J.4 with the good stand-in as its own control. Base control for the other rows = the building-mean stand-in.

## 5. Bootstrap (val 3.1, 3.3)

THRESHOLD bootstrap resamples = 2,000, 95 % percentile interval | source: spec 4A (2,000 resamples)
THRESHOLD bootstrap seed = 20260930 + 1000 * country index + 100 * class index | source: chosen by the employee on 2026-09-30 (spec says "seed fixed")
* Function `two_way_cluster_bootstrap` (scorer lines 144 to 158). Resampling units: BUILDINGS (unique building ids of the cell, line 156) and HOUSEHOLDS (unique household ids in the cell's pairs, line 157), drawn with replacement, independently of each other; never hours, never runs. A pair keeps the weight (times the building was drawn) x (times household A was drawn) x (times household B was drawn), so it is kept only when its building AND both its households were drawn (line 158). The same building id in several climates is one building unit (conservative).
* Null (val 3.2): S and B1 are two independent copies of the good construction; 200 repetitions; per cell, the share of 95 % intervals of the skill that cover 0; pass = pooled share >= 93 %.

THRESHOLD null coverage >= 93 % of 200 null runs | source: validation plan 3.2 (`5thJ_04_freezeGates_val.md`)

## 6. Exit code and SUMMARY (spec 4C)

* SUMMARY line: `SUMMARY PASS=.. FAIL=.. NOT_EVALUABLE=.. crashed=..` counts gate lines; a FAIL is a verdict, not a crash.
* Exit 0 = every gate computed (PASS or FAIL, none NOT_EVALUABLE). Exit 2 = at least one gate NOT_EVALUABLE. Exit 1 = the scorer crashed somewhere; a crashed section prints one line `VERDICT=NOT_EVALUABLE ... SECTION_CRASHED` and so counts as NOT_EVALUABLE in the SUMMARY too. 1 wins over 2.

## 7. Freeze (manager, not this step)

md5 of this file and of `5thJ_04_scorer.py` (and the loader copy) are written by the manager into the parent checklist and `gates_frozen.md5`; `gates_frozen.md5` was NOT created by this step. The test reader refusal is seen before the freeze (val 4.2 first half); the second half is the manager's.

## 8. Amendments (dated, after the freeze; none at the freeze)

(none)

### AMENDMENT 1 (2026-10-01 02:13 EDT, from `date`; 5J employee, Step 6 part A, task `Step6_docs/impl/2026-09-30_wp4_predict_TASK.md`)
No test prediction, test score or test truth read existed when this was written (the folder `/speed-scratch/o_iseri/5J/test/` held only empty
directories and the staged scorer copy). Nothing above this heading is changed: the frozen text is an unchanged prefix of this file (checked
byte by byte in the lock job) and `/speed-scratch/o_iseri/5J/gates_frozen.md5` is never touched.
* **What.** A new scorer file `5thJ_04_scorer_t.py` = the frozen scorer with ONE added flag, `--test`, and nothing else:
  (1) `--test` refuses to start unless `/speed-scratch/o_iseri/5J/gates_frozen.md5` exists; (2) with `--test`, `--split` must be one of
  `test_new_households`, `test_new_buildings`, `test_both_new`, and the allowed lists are those three + `b0_test` + `b0_dev`; (3) the
  B0 ids used inside are `b0_dev + b0_test` (instead of `b0_dev + b0_val`). Without `--test` the code path is the frozen one: same
  assertion, same allowed lists, same B0 ids.
* **Why.** The frozen scorer refuses every test list (`ALLOWED_SPLITS` and `assert a.split in ("development","validation")`), so the
  one sealed scoring of Step 6 cannot run without it. No gate, threshold, definition or bootstrap line is touched.
* **Diff summary** (`diff -u` of the two files is printed in the check job log `test/logs/s6_scheck_<job>.out` and in the state file):
  +3 lines of constants (`TEST_SPLITS`, `ALLOWED_SPLITS_TEST`, `GATE_LOCK`), +1 argparse line (`--test`), the split assertion becomes an
  if/else (+4 lines, the old assertion kept unchanged in the else branch), the allowed-list loop reads `ALLOWED_SPLITS_TEST if a.test
  else ALLOWED_SPLITS`, and the `b0_ids` line reads `lists["b0_test"] if a.test else lists["b0_val"]`.
* **md5.** Old scorer `5thJ_04_scorer.py` 84d1dafaf6ca38bca3954e2b63720f5a (unchanged, in the original lock). New scorer
  `5thJ_04_scorer_t.py` 4d15df70b60e20f561c8f81197aaf9a8 (locked read-only at `/speed-scratch/o_iseri/5J/freeze/5thJ_04_scorer_t.py`).
  Old `gates_frozen.md` 5a0dae85994acb2aefdb08fb01aab950 (15,958 bytes). The md5 of THIS amended file, of the new scorer and of
  `split_loader.py` (9aad66d5904c0383c85a12f8e17b035b, unchanged) are written by the lock job to
  `/speed-scratch/o_iseri/5J/gates_frozen_amend1.md5` (read-only); the amended text itself is copied to
  `/speed-scratch/o_iseri/5J/test/amend1/gates_frozen.md` (the file in `freeze/` stays as frozen).
* **Seen before the lock** (job `s6_scheck`, same arguments as validation B0 job 1404521): with `--test` absent the amended scorer's
  score file equals the frozen scorer's (diff printed; only the start-time line and the `seconds=` figures may differ); `--test` with a
  validation split is refused; the frozen scorer still refuses a test split; a copy with the lock path changed to a missing file refuses
  `--test`; the comparison itself is shown to report a planted difference.
