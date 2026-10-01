# 5J multi-zone re-pilot report (Spain, Madrid 2010, every flat tested)

Written 2026-09-30 by the employee from the checker output `mz_pilot_check_1404086.out` (same folder). Spanish data only; no UK file was opened.
Speed folder `/speed-scratch/o_iseri/5J/mz_pilot/`. Jobs: build 1404083, EnergyPlus array 1404084 (36 tasks), extraction 1404085, checker 1404086.

## What was run
* 36 runs: 10 x es_B07 (SFH, 2 zones), 10 x es_B16 (TH, 2 zones), 2 x es_B21 (MFH, 6 floors x k=2 = 12 flats), 2 x es_B33 (AB, 7 x 2 = 14 flats), 2 x es_B37 (AB, 9 x 2 = 18 flats), plus 5 repeats of es_B07 with household 02822 and 5 repeats of es_B37 run 1. Design: `mz_pilot_runs.csv`.
* Every flat of a multi-flat run has its own household (seeded permutation of the 60; seed 5000 + building number x 10 + r). 51 of the 60 households appear in a multi-flat run; they occupy 22 distinct (building, floor) cells.
* Part A fixes: mass budget now counts every interior surface EnergyPlus sees (both sides): `PATCH mz_mass OK ... interior_sides=32|38|50` for B21|B33|B37; modelled capacity equals c_m x A_C_Ref (relative difference <= 6e-6 on all 36). k = max(1, round_half_up(n_Apartment / n_Storey)) from `dwelling_count_es.csv` (3 rows per code, checked identical): B21 9/6 -> 2 (12 flats, TABULA says 9), B33 14/7 -> 2, B37 18/9 -> 2.
* Build gates (job 1404083): 36/36 IDFs with all 8 builder PATCH lines + `PATCH mz_k` = 324 lines (36 x 9); area and capacity gates 7/7 on all 36; collapse IDFs byte-identical to the builder task's (5/5, same md5). Seen failing: counting pairs once on an all-sides IDF gives FAIL (got 62.08 MJ/K vs 89.99 MJ/K, relative 0.31); the all-sides gate FAILS on an old pairs-once IDF.

## Gate lines (checker, job 1404086)
```
PASS 2.1 extracted 36/36, status files 36/36
PASS 2.2 err files parsed 36, bad=[], status.txt disagrees with err in []
PASS 2.3 dwelling series checked 203 x 4 targets; rows != 8760 or NaN or hour gap in 0 cases
PASS 2.4 facility level: extracted hourly sums vs eplustbl.csv End Uses (tol 0.1 % or the table rounding 0.005 GJ), 36 runs
PASS 2.4b dwelling level: extracted annual vs the sum of the dwelling's own zone columns in eplusout.csv (tol 1e-6), worst rel 3.6e-09 on MZ021
PASS 3.1a_within_run {"AB": [9 runs, 1253 pairs, 0 identical], "MFH": [2, 132, 0]}
PASS 3.1b_across_SFH_TH_runs 90 run pairs with different households, 0 identical
PASS 3.3_replicates_es_B07 and es_B37: 5 repeats each, max absolute hourly spread 0 kWh on all four targets, original run identical
PASS 4.3_equipment_present_vs_absent 100 dwellings evaluated (8 skipped, always present or always absent): 100 % above, ratio median 2.58, min 1.62
```
SUMMARY PASS=10 FAIL=0 WARN=0 NOT_EVALUABLE=0 (INFO=31). Exit code 0.

Seen failing (scratch copies, each printed FAIL):
```
SEENFAIL 2.2 FAIL planted '** Severe  **' in a copy of MZ001 eplusout.err: completed=True severe=1 status_txt_agrees=False (control on the real file: PASS)
SEENFAIL 3.1 FAIL dwelling 1 series copied onto dwelling 0 in a copy of MZ021 (households 01255 vs 07899): identical pairs found 2 of 66 (control on the real data: 0)
SEENFAIL 2.4_facility FAIL heating series of MZ001 (one dwelling) x 1.01 in a copy: heating hourly_sum=40.6239 GJ tbl=40.22 GJ rel=1.00e-02 (control on the real file: PASS)
SEENFAIL 2.4b_dwelling FAIL heating series of one flat of MZ021 x 1.01 in a copy: worst_rel=1.00e-02 dw3 heating_kwh got=4763.3127 ref=4716.1512 rel=1.00e-02 (control on the real file: PASS worst_rel=3.64e-09)
```
Note: a 1 % error on one flat of a 12-flat run moves the facility total by only about 0.08 %, below the 0.1 % facility tolerance, so the facility test alone would miss it; that is why the dwelling-level test 2.4b exists.

## Annual heating and cooling per m2 of dwelling floor area (4.1, INFO; kWh/m2, mean with min-max)
| class, position | flats | heating | cooling |
|---|---|---|---|
| SFH (all floors) | 10 | 68.9 (64.6-72.1) | 85.0 (82.1-89.2) |
| TH (all floors) | 10 | 108.1 (104.8-110.4) | 65.3 (63.8-67.4) |
| MFH ground | 4 | 101.8 (98.5-106.1) | 49.3 (34.4-62.2) |
| MFH middle | 16 | 102.3 (90.0-119.3) | 94.5 (64.1-123.2) |
| MFH top | 4 | 203.6 (196.9-210.3) | 148.8 (136.6-162.1) |
| AB ground | 8 | 86.6 (71.9-101.6) | 18.0 (5.9-37.7) |
| AB middle | 48 | 81.7 (66.8-111.9) | 42.8 (16.8-80.9) |
| AB top | 8 | 171.8 (139.9-206.0) | 88.1 (55.4-128.0) |

## Run seconds and disk (5.1, 5.2)
| class | runs | zones | seconds median / p90 / max | raw run folder MB median (max) | extracted MB median (max) |
|---|---|---|---|---|---|
| SFH | 15 | 2 | 4 / 5 / 6 | 12.1 (12.2) | 0.42 (0.42) |
| TH | 10 | 2 | 4 / 5 / 5 | 12.1 (12.3) | 0.42 (0.43) |
| MFH | 2 | 12 | 14 / 14 / 14 | 56.7 (56.7) | 4.93 (4.94) |
| AB | 9 | 14 or 18 | 19 / 23.4 / 25 | 82.5 (82.7) | 7.16 (7.21) |
All 36 runs: median 4.5 s, p90 19 s, max 25 s; MaxRSS 210-241 MB. By zone count: 2 zones 4 s, 12 zones 14 s, 14 zones 17.5 s, 18 zones 19 s (median). Raw total about 1.1 GB, extracted about 85 MB (nothing raw deleted).

## Draft campaign arithmetic (5.3, INFO; the manager rules O-3)
Per country and climate: 40 buildings (10 per class, Spanish building rows; zones per building SFH 1-3, TH 2-3, MFH 8-16, AB 7-77); SFH and TH 60 runs each (1,200 runs); MFH and AB ceil(60 / n_dwellings) x P runs each (104 runs at P = 1). Seconds and disk use the class medians above. Italy and UK building rows were not opened, so they are assumed to have the same 40-building mix as Spain (proxy). Nine climates = 3 per country x 3 countries. Finish time = CPU-hours / 30.
* P = 1: 1,304 runs and 1.8 CPU-hours per climate; nine climates 11,736 runs, 16.3 CPU-hours, about 0.5 h on 30 CPUs; disk at peak (30 runs in flight x 17 MB raw + all extracted 9.9 GB) 10.4 GB.
* P = 2: 1,408 runs and 2.3 CPU-hours per climate; nine climates 12,672 runs, 20.5 CPU-hours, about 0.7 h; peak disk 16.0 GB.
* P = 3: 1,512 runs and 2.8 CPU-hours per climate; nine climates 13,608 runs, 24.8 CPU-hours, about 0.8 h; peak disk 21.6 GB.
Caveat: the class median seconds come from pilot buildings with at most 18 zones. The largest AB building has 77 zones; EnergyPlus time rose about 1 s per extra zone in this pilot, so the AB share of the CPU-hours is underestimated (it is only 20 of the 40 buildings, and few runs per building).

## Plain summary
All 36 runs finished cleanly and every check passes; the three planted defects were each caught. Each flat in a building now gets its own household, the copy of the building with one big zone still reproduces the old single-zone result exactly, and the thermal mass now adds up to the building total. Flats on the top floor use about twice the heating of the middle floors, cooling is high everywhere (as found before in the single-zone wrapper), and the same household placed in different flats gives different results. Runs are short (4 to 25 seconds) and the files are small, so the campaign size is limited by the number of runs you choose, not by time or disk.
