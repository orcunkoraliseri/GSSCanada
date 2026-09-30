# WP15 — re-extract annual energy and peak demand for every Stage-4 run (fix of the calculate_eui defect) — task + state
Task doc:   this file (manager-written 2026-09-29, plan log (bj))
Status:     SUBMITTED (job 1401448, not read; manager reads the log)
Model:      Sonnet employee. One agent, one task, one turn. Submit, write state here, stop. Never wait or poll.

## Why (verified by the manager, 2026-09-29)
Every `per_draw_eui.csv` of Stage 4 was built by `plotting.calculate_eui()` (staged copy of `eSim/eSim_bem_utils/plotting.py`).
Its SQL query takes table `End Uses By Subcategory` without pinning `ReportName`; EnergyPlus writes that table twice,
under `AnnualBuildingUtilityPerformanceSummary` (GJ) and `DemandEndUseComponentsSummary` (W). The W rows fall into
`else: val_kwh = val` and are ADDED to the annual kWh. Manager check on block_1/NUS_RC1/iter_1/2005 (`impl/wp14/eplustbl.htm`):
equipment 984.07 GJ -> 273,353 kWh + 48,000 W = 321,353 / 5,299.63 m2 = 60.64 (the file's value); energy only = 51.58.
Heating file 39.03 vs energy only 12.08. The same defect was found and fixed in 2J/3J in August (V4-B4); 1J never got the fix.
So every Stage-5 number is contaminated. The runs themselves are fine; only the extraction is wrong.

## Inputs (Speed, READ-ONLY)
Every run folder `/speed-scratch/o_iseri/1J_rerun/stage4/draws/block_<b>/NUS_RC<n>/iter_<d>/<year>/` (b = 1..6, n = 1..6,
d = 5b-4..5b, year in 2005/2010/2015/2022/2025) and each block's `.../block_<b>/NUS_RC<n>/Default/` (deterministic; read
block 1's and also check blocks 2-6 give identical numbers). Each holds `eplustbl.htm` (~4 MB) and `eplusout.sql.gz`.
Use `eplustbl.htm` (no decompression needed). If a run lacks it, fall back to the SQL streamed into `$TMPDIR`; if both
are missing, record the run as MISSING (never fill it).
Also the old per-draw files for the reconstruction gate: local copies `1J_docs_occ/IMP/impl/wp12_stage5/raw/b<b>_RC<n>_per_draw.csv`
(or the same files on Speed).

## What to extract per run (one sbatch job, 1-4 CPUs; ~906 runs)
From the htm (tables are located by the `Report:` heading, then the `<b>table name</b>` heading):
1. `Building Area` (Annual Building Utility Performance Summary): Total and Net Conditioned area, m2. Use NET CONDITIONED
   (same choice as calculate_eui: conditioned if present, else total).
2. `End Uses` table of **Annual Building Utility Performance Summary** only: for every end-use row (Heating, Cooling,
   Interior Lighting, Interior Equipment, Fans, Pumps, Water Systems, ...) and every fuel column with an energy unit
   (GJ, kWh, kBtu...), convert to kWh. Skip any water-volume column (m3, gal) whatever its unit spelling.
   Output per run: kWh and kWh/m2 per end use summed over energy fuel columns, and per fuel column.
3. `Demand End Use Components Summary`: the "Time of Peak" row and the peak value in W for each fuel column
   (especially District Cooling, District Heating Water, Electricity), plus the end-use rows at that time.
   Output: peak W, peak W/m2, and the date/time string of the peak, per fuel.

## Gates (seen failing first in a local selftest on the one htm in `impl/wp14/eplustbl.htm`)
- W15.1 reconstruction: for every run, rebuild the OLD contaminated value as (annual kWh + demand W of the same end use and
  fuel, from the Demand table's `End Uses By Subcategory` rows) / area, exactly as calculate_eui did, and compare with the old
  `per_draw_eui.csv` value (Heating, Cooling, Interior Lighting, Electric Equipment, Water Systems). PASS if max |diff| < 0.002
  for all runs (the old file is rounded to 3 decimals). This proves the defect is the ONLY difference.
  Seen failing: drop the demand term in the selftest and show the gate fails.
- W15.2 independent check the defect cannot reach: for the probe run(s), corrected Interior Equipment and Interior Lights kWh
  vs the sum of the hourly meters `InteriorEquipment:Electricity` and `InteriorLights:Electricity` in `eplusout.mtr` (the WP14
  employee found they agree for block_1/RC1/iter_1/2005). Check at least one run per neighbourhood (6 runs). PASS if within 0.1 %.
- W15.3 counts: runs found per neighbourhood = 5*30 + Default; print `W15 COUNT <nb> runs=<N> missing=<M>`.
- Default identical across the six blocks (print the max spread).
Print one summary line `W15 SUMMARY runs=<N> missing=<M> W15.1=<PASS/FAIL maxdiff> W15.2=<PASS/FAIL maxreldiff>`.

## Outputs
`/speed-scratch/o_iseri/1J_rerun/wp15/out/annual_enduse.csv` (neighbourhood, block, draw, year, end_use, fuel, kwh, kwh_m2, area_m2),
`annual_enduse_totals.csv` (neighbourhood, block, draw, year, end_use, kwh_m2 summed over fuels — same shape as per_draw_eui.csv:
columns `neighbourhood,draw,year,end_use,value`, Default as year=Default draw=0),
`peaks.csv` (neighbourhood, block, draw, year, fuel, peak_w, peak_w_m2, peak_time), and the gate log.
scp them to `1J_docs_occ/IMP/impl/wp15/out/`.

## Rules
- Speed: `sbatch` only; login node allows only sbatch/squeue/sacct/scancel/scontrol/cd/ls/scp/module load and single-file
  tail/head/grep/wc -l/cat. NO python, NO find, NO du, NO md5sum, NO mkdir there (create folders by `scp -r` of a local folder).
  tcsh. `ssh -o BatchMode=yes o_iseri@speed.encs.concordia.ca`. Every job: `-t 7-00:00:00 -A chachemv -p ps`.
  Python: `/speed-scratch/o_iseri/GSSCanada/venv/bin/python` (read only).
- stage4/ is READ-ONLY. Write only under `/speed-scratch/o_iseri/1J_rerun/wp15/` and `logs/`. Outputs small.
- Never edit `eSim/eSim_bem_utils/plotting.py` or any pipeline file. Write a new extractor.
- Local: `py`, never `python`. Local folder `1J_docs_occ/IMP/impl/wp15/`. Never open a multi-MB file in context.
- Submit, write the job id + log path under Ledger, stop. Do not wait. The manager reads the log.

## Ledger
- 1401448 - WP15 extractor, single job, 4 CPUs, 16G, ps/chachemv/7-day - SUBMITTED, not read - log /speed-scratch/o_iseri/1J_rerun/wp15/logs/wp15_1401448.out ; outputs /speed-scratch/o_iseri/1J_rerun/wp15/out/{annual_enduse,annual_enduse_totals,peaks,peaks_enduse}.csv
- Speed files written (all under wp15/): wp15_extract.py, old/ (36 old per_draw csv copies from local wp12_stage5/raw), logs/, out/ (made by scp -r of a local folder; no mkdir on login node).
- Local files: 1J_docs_occ/IMP/impl/wp15/wp15_extract.py (+ old/, logs/, out/ empty). Nothing else touched; stage4 untouched.

## Verified
- Local selftest on impl/wp14/eplustbl.htm + eplusout.mtr (block_1/NUS_RC1/iter_1/2005) against wp12_stage5/raw/b1_RC1_per_draw.csv (draw 1, 2005):
  - Area 5299.63 m2 (Net Conditioned).
  - W15.1 seen failing: without the demand term maxdiff = 26.950 (Heating) -> FAIL. With the demand term maxdiff = 0.00000 over the 5 end uses -> PASS; reconstruction = Heating 39.029, Cooling 40.608, Interior Lighting 2.506, Electric Equipment 60.637, Water Systems 0.664, exactly the known old values.
  - Corrected kWh/m2: Heating 12.079, Cooling 23.599, Interior Lighting 1.906, Electric Equipment 51.580, Water Systems 0.652 (Water Systems old 0.664 = 0.652 + demand term).
  - W15.2 PASS locally: End Uses table Interior Equipment 273353.0 kWh vs hourly meter 273353.9 (rel 3.2e-6); Interior Lighting 10102.8 vs 10102.4 (rel 4.3e-5).
  - Extra check W15.4: End Uses table row totals equal the sums of the By-Subcategory rows (max diff 0.0 kWh) on that run.
  - Peaks (that run): Electricity 51,179.98 W (01-JAN-18:30); District Cooling 90,143.4 W (26-JUL-19:45); District Heating Water 142,885.77 W (30-JUN-00:30). Row counts: 182 end-use-fuel rows, 13 end-use totals, 3 peak rows, 6 peak-end-use rows.
- The job has NOT been read; W15.1 across all runs, W15.2 across 6 neighbourhoods, W15.3 counts and the Default spread are all unverified until the log is read.

## Decisions
- annual_enduse_totals.csv uses the By-Subcategory table with calculate_eui's naming (General/Other -> end use, else subcategory name, e.g. Electric Equipment, Elevators), so it matches per_draw_eui.csv shape. annual_enduse.csv uses the plain End Uses table (Interior Equipment, etc.), kWh per fuel column; energy units GJ/kWh/J/kBtu/Btu/MJ converted, any column with m3 or gal skipped. Zero-valued end uses ARE written (old file dropped them); they are 0.
- Peak = the Demand table 'Total End Uses' row (W) per fuel, time = 'Time of Peak' row; peaks.csv keeps only fuels with non-zero peak in W. peaks_enduse.csv (extra file) has the end-use rows in W at those times. Note District Heating Water peak time on the probe run is 30-JUN-00:30, odd for a Montreal heating peak; reported as read, not interpreted.
- W15.1 compares every end use of the old file plus flags any end use non-zero in my reconstruction but absent in the old file. Tolerance 0.002 as specified.
- W15.3: each neighbourhood is expected to hold 150 draw runs + 6 Defaults (one per block) = 156; the printed expected value is 156, the task text says 5*30+1. The six Defaults are all read, which also gives the spread check.
- Job order: no dependency, single job, multiprocessing pool of 4.
- W15.2 uses block_1/iter_1/2005 of each of the 6 neighbourhoods and reads eplusout.mtr from there.

## Next
Manager: read /speed-scratch/o_iseri/1J_rerun/wp15/logs/wp15_1401448.out (tail for the lines `W15 COUNT`, `W15 DEFAULT`, `W15 SUMMARY`; grep MISSING / DIFF / MISMATCH). If W15.1 and counts pass, scp out/*.csv to 1J_docs_occ/IMP/impl/wp15/out/ and rerun Stage 5 on annual_enduse_totals.csv.

## WHAT I DID NOT VERIFY
- Anything about the full 906-run job: parsing on other run types (RC4-6 mid/high-rise have extra rows such as Elevators, District columns), missing files, gate results.
- That the old per_draw files locally copied equal the ones on Speed (they were copied from wp12_stage5/raw as given).
- Whether every htm has the two "End Uses By Subcategory" tables in the same order (I select by Report heading, so it should).
- The oddity of the District Heating Water peak time (30-JUN).
- The wp14 probe script /speed-scratch/o_iseri/1J_rerun/wp14_probe.py left by the previous employee (not touched).
