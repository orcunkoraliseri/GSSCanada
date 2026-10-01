# 5J Step 2, WP1 pilot report (Spain, Madrid 2010, 50 runs)
Written 2026-09-30 by the pilot-part-2 employee. Numbers come from `tools/5thJ_pilot_check.py`, run on Speed (job 1404021, exit code 1). Raw output: `/speed-scratch/o_iseri/5J/pilot/report/check_main.out` (Speed) and the gate block below. State file: `Step2_docs/impl/2026-09-30_wp1_pilot_report.md`. No recommendation on the CPU share (O-5) or campaign size (O-3): the manager rules those.

## Plain summary
All 50 runs finished cleanly (Completed Successfully, zero severe, 8,760 rows), and the hourly totals match EnergyPlus's own annual tables. Different households do give different results on the same building, and repeats of one input agree to rounding (spread about 1e-7 J). A run takes a median of 2 s (90th percentile 6 s), so the draft campaign of 22,160 runs is about 12 CPU-hours; it would finish the same day on 8, 16 or 32 CPUs, and its extracted output (about 11 GB) is small next to the free disk, but the user quota has only 0.8 TB of headroom. Three physics checks do not pass and need the manager: building B07 has cooling in January, February and December (gate 4.2a FAIL); heating and cooling per m2 are very high for the multi-family and apartment buildings (about 675-745 kWh/m2 heating); and in 17 of 42 inputs the electricity is NOT higher when people are home, which looks like presence and electricity being about 12 hours out of phase (gate 4.3, diagnostic 4.3b). None of these was investigated here.

## 2D list
* Seconds per run (status.txt, EnergyPlus only, whole seconds): median 2.0, 90th percentile 6.0, max 8. time.txt wall: median 1.95, p90 6.15. CPU per run (user+sys): median 1.88 s, p90 6.01 s. Max RSS: median 210 MB, max 211 MB. Whole-task sacct Elapsed (arrays 1403962, 1403963; includes copy and extraction): median 2, p90 6, max 8 s.
* Raw run folder (input copy + eplus_out) median 3.47 MB; extracted csv median 0.505 MB.
* All 50 finished, Completed Successfully, 0 severe, 8,760 rows per target: gates 2.1 to 2.3 PASS.
* Outputs differ between households on the same building: gates 3.1 and 3.2 PASS (156 pairs, 0 identical, for electricity and for heating).
* Replicate spread: gate 3.3 (below). Annual sums equal hourly sums: gate 2.4 PASS (worst relative difference 0.083 %).

## Size arithmetic (5.1 to 5.3)
* CPU-hours = runs x median seconds / 3600 = 22,160 x 2.0 / 3600 = 12.31 (runs from spec 2A: 21,600 paired + 360 average + 200 replicates). Sensitivity with the finer time.txt wall median 1.95 s: 12.00 CPU-hours.
* Wall time = CPU-hours / CPUs: 8 CPUs 1.54 h; 16 CPUs 0.77 h; 32 CPUs 0.38 h. Start date 2026-09-30, so all three finish 2026-09-30, all before 11 Oct 2026. The 2E cut order is not needed. Not included: queue wait, array start-up, repeats of failed runs, and building the campaign inputs (the pilot inputs were built locally in part 1; the per-run input build cost for 22,160 runs is not measured here).
* Disk: (runs in flight x median raw 3.47 MB) + (all runs x median extracted 0.505 MB = 11.20 GB). 8 in flight 11.22 GB, 16 in flight 11.25 GB, 32 in flight 11.31 GB. Free space read by the preflight job (1401744, 2026-09-29 21:51): filesystem 43.0 TB free; user quota 9.2 TB used of 10.0 TB = 0.80 TB headroom. The plan is under both. Caveat: the extracted size is a csv; the campaign parquet will differ.

## Gate lines (checker output, job 1404021)
```
python 3.10.20 root /speed-scratch/o_iseri/5J/pilot
PASS 2.1 manifest_rows=50 files_expected=100 files_missing=0 (extracted csv + status.txt per run) []
PASS 2.2 runs_parsed=50 err_files_completed_and_0_severe=50 severe_lines_total=0 bad=[]
INFO 2.2b status.txt_vs_err_file_disagreements=0 []
PASS 2.3 runs=50 target_series_checked=200 rows_each=8760 bad=[]
PASS 2.4 runs=50 targets=4 fails=0 [] | heating_J worst_abs_diff_GJ=0.0049 (P027 hourly 578.2651 annual 578.27 rel 0.0009%); cooling_J worst_abs_diff_GJ=0.0047 (P011 hourly 42.4647 annual 42.46 rel 0.0110%); appliance_J worst_abs_diff_GJ=0.0049 (P006 hourly 5.9049 annual 5.90 rel 0.0827%); facility_elec_J worst_abs_diff_GJ=0.0049 (P006 hourly 5.9049 annual 5.90 rel 0.0827%)
PASS 2.5 rows=50 fields=11/11 clock_origin_midnight=50 bad=[]
PASS 2.5b model.idf and schedule md5 re-hashed from the run folder equal the manifest for 50 of 50 runs []
PASS 3.1 buildings=5 pairs_compared=156 identical_pairs=0 [] per_building(households,pairs)={'es_B07': (9, 36), 'es_B16': (9, 36), 'es_B21': (8, 28), 'es_B33': (8, 28), 'es_B37': (8, 28)}
PASS 3.2 identical_pairs/pairs per class (target used): {'AB': '0/56 (heating_J)', 'MFH': '0/28 (heating_J)', 'SFH': '0/36 (heating_J)', 'TH': '0/36 (heating_J)'}
INFO 3.3 es_B07__es_02822 heating_J repeats=5 max_abs_hourly_spread_J=5.96046e-08 annual_spread_rel=0 max_hourly_value_J=2.7781e+07; es_B07__es_02822 cooling_J repeats=5 max_abs_hourly_spread_J=6.70552e-08 annual_spread_rel=3.94e-16 max_hourly_value_J=4.13119e+07; es_B07__es_02822 appliance_J repeats=5 max_abs_hourly_spread_J=0 annual_spread_rel=0 max_hourly_value_J=6.49788e+06; es_B07__es_02822 facility_elec_J repeats=5 max_abs_hourly_spread_J=0 annual_spread_rel=0 max_hourly_value_J=6.49788e+06; es_B16__es_00494 heating_J repeats=5 max_abs_hourly_spread_J=1.56462e-07 annual_spread_rel=0 max_hourly_value_J=5.5096e+07; es_B16__es_00494 cooling_J repeats=5 max_abs_hourly_spread_J=1.86265e-07 annual_spread_rel=5.31e-16 max_hourly_value_J=5.72876e+07; es_B16__es_00494 appliance_J repeats=5 max_abs_hourly_spread_J=0 annual_spread_rel=0 max_hourly_value_J=8.0778e+06; es_B16__es_00494 facility_elec_J repeats=5 max_abs_hourly_spread_J=0 annual_spread_rel=0 max_hourly_value_J=8.0778e+06
PASS 3.4 inputs=42 repeated_inputs=2 bad=[]
WARN 4.1 far (median outside 0.5x..2x of the wrapper values): ['AB', 'MFH'] | wrapper kWh/m2 (55 m2 box): H1 act2 heat 195.5 cool 88.0; H2 act2 heat 190.2 cool 88.8; H1 replicate act2 heat 195.5 cool 88.0; H1 no-act2 heat 195.5 cool 87.2
INFO 4.1d AB n_runs=16 floor_m2=[215.8, 223.8] heating_kWh_m2 median 729.4 [709.2-747.7] cooling_kWh_m2 median 158.9 [120.6-198.2]
INFO 4.1d MFH n_runs=8 floor_m2=[92.6] heating_kWh_m2 median 675.2 [666.5-677.9] cooling_kWh_m2 median 256.3 [255.4-260.7]
INFO 4.1d SFH n_runs=9 floor_m2=[81.4] heating_kWh_m2 median 124.7 [116.7-131.5] cooling_kWh_m2 median 131.5 [126.3-139.0]
INFO 4.1d TH n_runs=9 floor_m2=[125.4] heating_kWh_m2 median 188.9 [182.1-192.8] cooling_kWh_m2 median 96.3 [94.1-100.3]
INFO 4.1e per building (building class floor_m2 heat cool, median over its households): es_B07 SFH 81.4 124.7 131.5; es_B16 TH 125.4 188.9 96.3; es_B21 MFH 92.6 675.2 256.3; es_B33 AB 223.8 712.5 196.8; es_B37 AB 215.8 745.6 121.3
FAIL 4.2a runs_with_cooling_in_Jan_Feb_Dec=13 of 50 max_hourly_kWh=0.285 ['P001', 'P002', 'P003', 'P004', 'P005', 'P006', 'P007', 'P008', 'P046', 'P047', 'P048', 'P049', 'P050']
WARN 4.2b runs_with_heating_in_Jul_Aug=37 of 50 (kWh per run, first 6) {'P009': 0.1, 'P010': 0.2, 'P011': 0.3, 'P012': 0.1, 'P013': 0.1, 'P014': 0.1}
WARN 4.3 inputs_with_presence_and_absence=42 mean_present>mean_absent=25 (59.5%) skipped_always_present_or_absent=0 [] failing=['es_B07__es_00739(921152<=1008684)', 'es_B07__es_01855(655224<=707625)', 'es_B16__es_02822(801938<=827457)', 'es_B16__es_04065(533374<=718899)', 'es_B16__es_01855(655224<=707625)']
INFO 4.3b inputs passing the 4.3 test when presence is shifted by k hours: k=-12:42/42(ratio 1.40) k=-11:42/42(ratio 1.43) k=-10:42/42(ratio 1.56) k=-9:42/42(ratio 1.57) k=-8:42/42(ratio 1.48) k=-7:34/42(ratio 1.31) k=-6:29/42(ratio 1.24) k=-5:29/42(ratio 1.15) k=-4:17/42(ratio 0.93) k=-3:13/42(ratio 0.97) k=-2:13/42(ratio 0.92) k=-1:17/42(ratio 0.97) k=+0:25/42(ratio 1.12) k=+1:12/42(ratio 0.90) k=+2:8/42(ratio 0.80) k=+3:0/42(ratio 0.80) k=+4:0/42(ratio 0.84) k=+5:8/42(ratio 0.83) k=+6:13/42(ratio 0.89) k=+7:17/42(ratio 0.97) k=+8:30/42(ratio 1.10) k=+9:34/42(ratio 1.19) k=+10:33/42(ratio 1.18) k=+11:42/42(ratio 1.29) k=+12:42/42(ratio 1.34)
PASS P.1 build log: inputs_in_log=42 inputs_used=42 patch_names_required=9 PATCH_lines_counted=378 (expected 378) missing_or_duplicate=[]
PASS P.2 array logs with 'PATCH model_idf_rename OK': 50 of 50 (arrays ['1403962', '1403963']) missing_tasks=[]
PASS 5.1 status.txt seconds (whole-second, EnergyPlus only): median=2.0 p90=6.0 max=8 | time.txt wall s: median=1.95 p90=6.15 | CPU s (user+sys): median=1.88 p90=6.01 | max_rss_MB: median=210 max=211 | formula CPU-hours = runs x median_s / 3600 = 22160 x 2.0 / 3600 = 12.31
INFO 5.1b sensitivity with time.txt wall median 1.95 s: 22160 x 1.95 / 3600 = 12.00 CPU-hours
INFO 5.1c sensitivity with whole-task sacct Elapsed (includes copy and extraction; 50 tasks) median=2.0 p90=6.0 max=8 s: 22160 x 2.0 / 3600 = 12.31 CPU-hours
PASS 5.2 median raw run folder 3.47 MB, median extracted 0.505 MB; all runs x extracted = 22160 x 0.505 MB = 11.20 GB | 8 in flight: 8 x 3.47 MB + 11.20 GB = 11.22 GB | 16 in flight: 16 x 3.47 MB + 11.20 GB = 11.25 GB | 32 in flight: 32 x 3.47 MB + 11.20 GB = 11.31 GB | preflight (2026-09-29 21:51): filesystem free 43.0 TB; user quota used 9.2 TB of limit 10.0 TB = headroom 0.80 TB
PASS 5.3 8 CPUs: 12.31 CPU-h / 8 = 1.54 h wall, finish 2026-09-30, MEETS 11 Oct 2026 | 16 CPUs: 12.31 CPU-h / 16 = 0.77 h wall, finish 2026-09-30, MEETS 11 Oct 2026 | 32 CPUs: 12.31 CPU-h / 32 = 0.38 h wall, finish 2026-09-30, MEETS 11 Oct 2026 | (compute time only: no queue wait, no per-task start-up, no failed-run repeats)
SUMMARY PASS=14 FAIL=1 WARN=3 INFO=10 NOT_EVALUABLE=0
FAIL-severity gates not passing: ['4.2a']
```
Exit code 1 (the only FAIL-severity gate not passing is 4.2a).

## Seen failing (val doc Section 6; job 1404021, scratch copies on Speed under `report/scratch/`)
Each case changes one thing in a symlinked copy; the control case (nothing changed) shows only the 4.2a FAIL that is also in the real run, so every other FAIL below is caused by the planted change.
```
=== CASE none: control, nothing changed
FAIL 4.2a runs_with_cooling_in_Jan_Feb_Dec=13 of 50 max_hourly_kWh=0.285 ['P001', 'P002', 'P003', 'P004', 'P005', 'P006', 'P007', 'P008', 'P046', 'P047', 'P048', 'P049', 'P050']
SUMMARY PASS=14 FAIL=1 WARN=3 INFO=9 NOT_EVALUABLE=0
FAIL-severity gates not passing: ['4.2a']
CHECKER EXIT=1
=== CASE 3.1: P001 and P002 are on the same building (es_B07) with different households; P002 extracted file replaced by a copy of P001's
FAIL 2.4 runs=50 targets=4 fails=4 ['P002:heating_J hourly=36.3171 annual=37.50 GJ', 'P002:cooling_J hourly=38.7696 annual=37.84 GJ', 'P002:appliance_J hourly=8.3613 annual=4.11 GJ', 'P002:facility_elec_J hourly=8.3613 annual=4.11 GJ'] | heating_J worst_abs_diff_GJ=1.1829 (P002 hourly 36.3171 annual 37.50 rel 3.1545%); cooling_J worst_abs_diff_GJ=0.9296 (P002 hourly 38.7696 annual 37.84 rel 2.4567
FAIL 3.1 buildings=5 pairs_compared=156 identical_pairs=1 ['es_B07:es_00494==es_00739'] per_building(households,pairs)={'es_B07': (9, 36), 'es_B16': (9, 36), 'es_B21': (8, 28), 'es_B33': (8, 28), 'es_B37': (8, 28)}
FAIL 4.2a runs_with_cooling_in_Jan_Feb_Dec=13 of 50 max_hourly_kWh=0.285 ['P001', 'P002', 'P003', 'P004', 'P005', 'P006', 'P007', 'P008', 'P046', 'P047', 'P048', 'P049', 'P050']
SUMMARY PASS=11 FAIL=3 WARN=4 INFO=9 NOT_EVALUABLE=0
FAIL-severity gates not passing: ['2.4', '3.1', '4.2a']
CHECKER EXIT=1
=== CASE 2.2: one '** Severe  **' line appended to a copy of P001 eplusout.err
FAIL 2.2 runs_parsed=50 err_files_completed_and_0_severe=49 severe_lines_total=1 bad=['P001(completed=True severe=1 fatal=0)']
WARN 2.2b status.txt_vs_err_file_disagreements=1 ['P001(status: ok=yes sev=0; err file: ok=True sev=1)']
FAIL 4.2a runs_with_cooling_in_Jan_Feb_Dec=13 of 50 max_hourly_kWh=0.285 ['P001', 'P002', 'P003', 'P004', 'P005', 'P006', 'P007', 'P008', 'P046', 'P047', 'P048', 'P049', 'P050']
SUMMARY PASS=13 FAIL=2 WARN=4 INFO=8 NOT_EVALUABLE=0
FAIL-severity gates not passing: ['2.2', '4.2a']
CHECKER EXIT=1
=== CASE 2.4: facility_elec_J column of P001 extracted copy x 1.01
FAIL 2.4 runs=50 targets=4 fails=1 ['P001:facility_elec_J hourly=8.4449 annual=8.36 GJ'] | heating_J worst_abs_diff_GJ=0.0049 (P027 hourly 578.2651 annual 578.27 rel 0.0009%); cooling_J worst_abs_diff_GJ=0.0047 (P011 hourly 42.4647 annual 42.46 rel 0.0110%); appliance_J worst_abs_diff_GJ=0.0049 (P006 hourly 5.9049 annual 5.90 rel 0.0827%); facility_elec_J worst_abs_diff_GJ=0.0849 (P001 hourly 8.44
FAIL 4.2a runs_with_cooling_in_Jan_Feb_Dec=13 of 50 max_hourly_kWh=0.285 ['P001', 'P002', 'P003', 'P004', 'P005', 'P006', 'P007', 'P008', 'P046', 'P047', 'P048', 'P049', 'P050']
SUMMARY PASS=13 FAIL=2 WARN=3 INFO=9 NOT_EVALUABLE=0
FAIL-severity gates not passing: ['2.4', '4.2a']
CHECKER EXIT=1
```
Not done: the val doc also lists 1.1 (a planted out-of-range value in `buildings.csv`); that belongs to the design-table check of part 1, not to this task.

## Notes
* Gate 2.4 takes the annual values from the EnergyPlus `eplustbl.csv` End Uses table (GJ, 2 decimals), so the tolerance is 0.1 % of the annual value plus 0.005 GJ (rounding of the printed value). The worst relative difference is 0.083 % (P006 electricity, 5.90 GJ), so the plain 0.1 % rule also holds.
* Heating and cooling are "District Heating" and "District Cooling" in the End Uses table; the hourly targets are the ideal-loads Total heating and Total cooling energy (Total = sensible + latent).
* Gate 4.2b (heating in Jul-Aug) is a WARN of this report (not in the val doc): 37 of 50 runs have a few tenths of a kWh of heating in July or August, tiny against the annual sums.
* The 4.1 comparison uses the four wrapper test values (55 m2 old SFH box: heating 190.2 to 195.5, cooling 87.2 to 88.8 kWh/m2). No TABULA or 4J reference value was opened, so "inside the range 4J reported" (val 4.1) is NOT verified here.
