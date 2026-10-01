# 5J Step 6: results of the ONE scoring of the sealed tests (Spain + Italy)

Written 2026-10-01 04:15 EDT by the manager from the job outputs below. Verdicts are copied as the scorer printed them.
Scoring job 1405205 (submitted once; start-up 32/32 checks PASS; 24 locked scorer calls + 3 locked reported-analysis calls),
collect job 1405206. Files: `scores.parquet`, `SUMMARY.txt`, `bootstrap_intervals.csv`, `claims.txt`, `reported_S_<list>.txt`
(this folder). Claim rule = spec 6D, written 2026-09-30 21:25 before any test result.

## Headline (the pinned surrogate S = S3)
| Test list | G5J.3 occupancy effect (cells PASS) | G5J.2 load accuracy (cells PASS) | G5J.5 peaks | G5J.4 (C fails) |
|---|---|---|---|---|
| new households (1,107 runs) | 31 / 32 | 21 / 32 | 8 / 8 | 32 / 32 |
| new buildings (813 runs) | 31 / 32 | 14 / 32 | 8 / 8 | 32 / 32 |
| both new (207 runs) | 26 / 28 (+4 NOT_EVALUABLE: it AB, no pairs) | 14 / 32 | 8 / 8 | 28 / 28 (+4 NOT_EVALUABLE) |

**6D claims (S):** holds in 11 of 12 target x list combinations; "partly" for heating on new households in new buildings
(5/8: es 2/4, it 3/4, it AB not evaluable). Heating holds on new households (7/8) and new buildings (7/8); cooling,
equipment and total electricity hold on all three lists. The blind control never passes (G5J.4 FLAGGED 0 everywhere).

**G5J.3 failures of S:** new households: it AB heating (R² 0.81, skill interval contains 0). New buildings and both new: es SFH
heating (R² 0.42 / 0.38; B1 better, skill interval below 0); both new: es AB heating (interval contains 0).

**G5J.2 (ASHRAE hourly bands) is where S is weak:** on new buildings S misses the bands for heating and cooling in most Spanish
classes (median |NMBE| 28-42 % for SFH/TH/AB) and for Italian MFH/AB cooling (CV(RMSE) 135-252 %). S gets the household
DIFFERENCE right far more often than the absolute load: the paper's premise, now shown on the trained model.

## Baselines and control
* C (household drivers swapped): G5J.3 0 of 32 / 32 / 28; G5J.2 6 / 2 / 2 of 32.
* B1 (trees, clipped at 0): G5J.2 24 / 14 / 14 of 32; its G5J.3 line is scored against itself (`--b1 B1`), so its skill is 0 by
  construction and every cell prints FAIL (design of the call, not a result about B1). B1's own R² sits in S's lines (`r2_B1`).
* B0 (average household): G5J.2 19 / 19 / 18 of 32; G5J.3 0.

## Seed spread (reported only, spec 6D 02:05)
Same configuration, seeds 2 and 3, G5J.3 PASS: new households 17 / 11 of 32, new buildings 23 / 21, both new 14 / 11 of 28
(S seed 1: 31, 31, 26). Under the 6D rule seeds 2/3 would NOT hold heating on any list. **The claim is the pinned model's; the
configuration's success depends strongly on the training seed.** The paper must say this next to every claim.

## New country (G5J.6, reported; only the held-out country's lines count)
* Trained on Spain, scored on Italy (SloES): G5J.3 0 / 3 / 2 of 16 (12 evaluable on both new); G5J.2 2 / 4 / 4 of 16.
* Trained on Italy, scored on Spain (SloIT): G5J.3 9 / 10 / 9 of 16; G5J.2 3 / 4 / 4 of 16.
The surrogate does not transfer to a new country without its data; Italy -> Spain partly does.

## Reported analyses (locked `s6_reported_v2.py`)
* Presence-heating timing lag (like-for-like check, not a building time constant): S's median lag equals EnergyPlus's in most
  cells (12-18 h), 78-99 % of flats within 1 h. One self-check (the +6 h planted shift) could not run on new buildings (the
  chosen flat's lag left no room for +6 h): NOT_EVALUABLE for that list; the reported numbers are unaffected.
* Level versus timing: household size and appliance energy explain 73-98 % of the ANNUAL pair effect (EnergyPlus), and S
  reproduces that share (79-98 %; corrected 2026-10-01 06:07 by the manager, first written as 73-97 %). Most of the occupancy
  effect on annual energy is a level effect.
* Mild-climate cooling: annual cooling pair R² 0.72-0.999 per climate x class (cells with pairs; corrected 2026-10-01 06:07 by the
  manager, first written as 0.86-0.99 from the validation run); annual cooling LEVEL error large in new buildings.

## Manager re-derivation (val section 5; job 1405218, own code)
* Run it_bologna_B05_test_1: hourly total-electricity CV(RMSE) 12.8 %, NMBE -7.4 %.
* Pair it_bologna_B05_test_1 vs _10: annual heating difference EP -109.0 kWh, S -147.9 kWh, same sign.
* G5J.3 it SFH heating on test_both_new: own R² 0.9164, sign 0.9852, 135 pairs = scorer line = scores.parquet row.
