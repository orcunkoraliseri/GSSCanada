# 5J Step 4: perturbation table (validation split only)

Written 2026-09-30 by the Step 4 employee (fix 1b), numbers read from the finished jobs. Source of every number below: `/speed-scratch/o_iseri/5J/freeze/out/score_<tag>.txt`, `out/perturb_summary.txt` and `out/perturb_summary_eff.txt` (before/after lines), job logs in `/speed-scratch/o_iseri/5J/freeze/logs/`. Definitions: `gates_frozen.md`. Scorer: `tools/speed/5thJ_04_scorer.py`. State: `impl/2026-09-30_freeze.md`, `impl/2026-09-30_freeze_fix1.md`.

Stand-ins (all from EnergyPlus; no trained model exists):
* "ASHRAE-good, effect-blind" (`good`) = EnergyPlus + independent Gaussian noise, SD 10 % of the run's hourly SD per target. It matches the load well but its noise differs in every run, so it hides the occupancy effect.
* `effgood` = EnergyPlus + a noise part shared by all runs of the same flat (the error on the load level, it cancels inside a pair) + 10 % of the run's own occupancy deviation. Definition in `gates_frozen.md` (ruled by the manager 2026-09-30). This is the stand-in that must pass every gate (val 2.0).
* weak B1 = same as `good` with 30 % noise (employee choice). Control of the main run = `effbldmean`.

Manager re-derivation (own code, job 1404408, log `/speed-scratch/o_iseri/5J/mz_pilot/logs/mgr_s4b_1404408.out`): effgood G5J.3 R2 Italy AB heating 0.9947, cooling 0.9942, equipment 0.9937, total 0.9937; Spain MFH 0.9929 / 0.9922 / 0.9918 / 0.9918; pairs 1,032 and 3,570; noise SD per pair / SD of the occupancy difference 0.083 to 0.095; peak share 92.5 % and 93.4 %; 14 open logs, 0 lines naming a locked run. All agree with the scorer.

## Row 0: ASHRAE-good, effect-blind (tag sc_good, `out/score_sc_good.txt`)
SUMMARY PASS=97 FAIL=15 NOT_EVALUABLE=0, exit 0. G5J.2 (absolute load accuracy) passes 32 of 32 cells. G5J.3 (occupancy effect) fails 15 of 32 cells: every heating and cooling cell except Italy AB heating. Annual sign agreement stays at 0.965 or higher. This is a result, not a scorer bug: a predictor that is accurate hour by hour can pass the load band and still miss the small occupancy effect. The gate was not relaxed.

G5J.3 R2 of the 15 failing cells (source: block "G5J.3 lines of sc_good" in `perturb_summary_eff.txt`):

| Class | Country | Heating | Cooling |
|---|---|---|---|
| AB | es | -4.5990 | -3.8123 |
| MFH | es | -1.0028 | -0.8392 |
| SFH | es | -11.8720 | -9.5572 |
| TH | es | -3.2302 | -3.0606 |
| AB | it | 0.5376 (PASS) | 0.4273 (FAIL) |
| MFH | it | -0.1468 | -0.3617 |
| SFH | it | -6.8540 | -3.7518 |
| TH | it | -2.6215 | -1.4595 |

Equipment and total electricity pass in all 16 cells of the `good` run.

## Row "effgood": passes every gate (val 2.0)
Tag sc_effgood: SUMMARY PASS=112 FAIL=0 NOT_EVALUABLE=0 crashed=False, SCORER_EXIT 0; G5J.1 8/8, G5J.2 32/32, G5J.3 32/32, G5J.4 32/32, G5J.5 8/8; self-test max abs difference 2.1e-14; CHECK 2.3 opens outside the allowed lists = 0 (source: `perturb_summary_eff.txt`, first block). Noise check on 3 runs of one group (es_madrid_2010, es_B21, m=13): run part / SD of the occupancy deviation 0.0994 to 0.1005 on every target; shared part / SD of the flat mean about 0.100 (`logs/standins_eff_1404395.out`).

## Rows 1 to 5 on effgood (before = effgood, after = perturbed; source `perturb_summary_eff.txt`)

| Row | Perturbation | Must break | Tag | Before | After | Result |
|---|---|---|---|---|---|---|
| 1 | effgood minus one validation run (es_madrid_B01_val_1 dropped, 2,189 symlinks) | G5J.1 | sc_effdeleted | G5J.1 8 PASS | G5J.1 7 PASS, 1 FAIL (es SFH ALL); G5J.2 to G5J.5 unchanged | caught |
| 2 | training mean per climate, class, hour of year (base-free, reused sc_trainmean) | G5J.2 | sc_trainmean | G5J.2 32 PASS | G5J.2 0 PASS, 32 FAIL; G5J.3 32 to 0 PASS; G5J.5 8 to 0 PASS; G5J.1 and G5J.4 unchanged | caught (other gates also move, see note a) |
| 3 | building mean per flat (occupancy effect exactly zero, load level kept; effbldmean) | G5J.3 | sc_effbldmean | G5J.3 32 PASS | G5J.3 0 PASS, 32 FAIL; G5J.2 32 to 16 PASS; G5J.5 8 to 0 PASS | caught |
| 4 | effgood shifted by 2 h (effshift2) | G5J.5 | sc_effshift2 | G5J.5 8 PASS | G5J.5 0 PASS, 8 FAIL; G5J.2 32 to 0 PASS; G5J.3 32 to 7 PASS (25 FAIL) | caught (other gates also move) |
| 5 | control of G5J.4 = effgood itself | G5J.4 reads "control passes" | sc_effctrl | G5J.4 32 PASS | G5J.4 0 PASS, 32 FAIL; G5J.1, G5J.2, G5J.3, G5J.5 unchanged | caught |

Row 2 changed 32 cells in G5J.2 and G5J.3 (all es and it, AB/MFH/SFH/TH, four targets) and all 8 total-electricity cells in G5J.5. Row 3 changed G5J.2 in 16 cells (see the per-target table below). Row 4 kept G5J.3 PASS in 7 cells (heating in es SFH, es TH, it AB, it MFH, it SFH, it TH, and cooling in es TH). All cell lists are in `perturb_summary_eff.txt`, blocks ROW 1 to ROW 5.

## Premise of the paper: building mean passes the load band, fails the occupancy gate (val 2.1b)
G5J.2 verdict per class, country, target (median CV(RMSE), share of runs in band; source `perturb_summary_eff.txt`, blocks "G5J.2 per class ... under sc_effbldmean" and "... under sc_bldmean").
* Old `bldmean` (building mean of the noisy `good`, tag sc_bldmean): G5J.2 18 PASS, 14 FAIL of 32 cells; SUMMARY PASS=58 FAIL=54.
* `effbldmean` (tag sc_effbldmean): G5J.2 16 PASS, 16 FAIL of 32 cells; G5J.3 0 of 32 PASS; SUMMARY PASS=56 FAIL=56.
* effbldmean G5J.2 FAIL cells (16): equipment in all 8 class-country cells (share of runs in band 0 to 33 %); total electricity in es AB, es MFH, es TH, it AB, it MFH (5 cells); cooling in it AB, it MFH, it TH (3 cells). Heating PASSES in all 8 cells (median CV(RMSE) 13.3 % to 21.0 %); cooling passes in 5 of 8 cells (es AB 25.4 %, es MFH 24.9 %, es SFH 21.5 %, es TH 22.2 %, it SFH 29.4 %).

## Planted crash (tag sc_crash, `logs/score_sc_crash_1404318.out`)
A fault planted in section G5J.5: G5J.5 NOT_EVALUABLE 1 ("SECTION_CRASHED: RuntimeError: planted crash in section G5J.5"), crashed=True, SUMMARY PASS=89 FAIL=15 NOT_EVALUABLE=1, SCORER_EXIT 1. The other sections still ran and reported. CHECK 2.3 = 0 outside opens.

## Planted high floor (val 5.2; tag sc_highfloor, `out/floors_PLANTED_HIGH.json`, every floor 1.0e6 kWh, md5 406c2b6428144df7ef99c220f2840964)
Scorer run on effgood with that floors file: no pair is above the floor (above_floor=0 of 1,497 pairs in es AB), so G5J.3 NOT_EVALUABLE in all 32 cells and G5J.4 NOT_EVALUABLE in 32 cells; G5J.1, G5J.2, G5J.5 unchanged (8, 32, 8 PASS). SUMMARY PASS=48 FAIL=0 NOT_EVALUABLE=64 crashed=False, SCORER_EXIT 2 (= some NOT_EVALUABLE, the intended exit). sacct shows job 1404403 as FAILED 2:0 only because the batch script returns the scorer's exit code 2; that is intended (`logs/score_sc_highfloor_1404403.out`, `perturb_summary_eff.txt`). The earlier `sc_highk` (only k raised to 1e7, floor still 0) changed nothing: SUMMARY PASS=97 FAIL=15, same as sc_good, because the threshold max(k * sqrt(2) * floor, 0.001) ignores k while the floor is 0. It is kept in the record as inert.

## Null (jobs 1404311 / 1404323, `logs/null_1404323.out`)
Bootstrap null: 99.98 % of 6,400 intervals (32 cells x 200 reps) cover zero; lowest cell 99.5 %; cells below 93 %: 0 of 32. Gate 3.2 (at least 93 %) PASS.

## CHECK 2.3 (no locked file opened), every tag
opens_outside_the_5_allowed_lists = 0 for all 14 tags listed in the last block of `perturb_summary_eff.txt`: sc_pipetest, sc_good, sc_deleted, sc_trainmean, sc_bldmean, sc_shift2, sc_ctrlgood, sc_crash, sc_highk, sc_effgood, sc_effdeleted, sc_effbldmean, sc_effshift2, sc_effctrl. sc_highfloor is not in that block; its score file has one CHECK 2.3 line, and the manager's own re-derivation (1404408) found 0 locked runs in 14 open logs. The count for sc_highfloor itself was not read here.

## What this shows
An hourly-accurate stand-in can pass the load band (G5J.2 32 of 32) and still miss the occupancy effect on heating and cooling (row 0: G5J.3 fails 15 of 32 cells). A stand-in that carries the load level but no occupancy effect (effbldmean) passes the load band on 16 of 32 cells (old bldmean: 18) and fails the occupancy gate on all 32. The effect-good stand-in passes every gate (112 of 112), so the gates can be passed. Each planted fault is caught: a dropped run (G5J.1), a training mean (G5J.2 and G5J.3), a zero occupancy effect (G5J.3), a 2 h shift (G5J.5), a control that passes (G5J.4), a crash (exit 1, NOT_EVALUABLE) and a high floor (exit 2, NOT_EVALUABLE in 32 cells). Notes: (a) rows 2 and 4 also move other gates (a prediction that ignores the household or is 2 h late also loses the pair and hourly scores); the spec sentence "the other gates are unchanged" (val 2.1) is reported as it comes out, not forced. (b) The 10 % noise level and all thresholds were not changed to obtain these results.
