# WP14 — hourly energy extraction from the 30-draw runs (peak timing, diurnal and monthly profiles) — task + state
Task doc:   this file (manager-written 2026-09-29, plan log (bi))
Status:     BLOCKED (manager ruling needed on gate W14.1; array extractor NOT submitted)
Model:      Sonnet employee. One agent, one task, one turn. Submit, write state here, stop. Never wait or poll.

## Why
Section 4.2 of the paper (Figures 15-21, C3-C7) came from a 3-draw pilot in which 2010 was a copy of 2005 (plan log (j)).
Stage 4 re-ran everything: 6 neighbourhoods x 5 years x 30 draws + 1 Default run per neighbourhood, all VERIFIED
(plan log (bh)). Annual numbers are done (`impl/wp12_stage5/`). The paper still needs, from the new runs:
peak cooling hour and magnitude (old Figure 20, "17.4 % lower, 1-2 h earlier"), peak heating magnitude,
the diurnal load shape by season and day type (old Figure 17, C3-C7) and monthly end-use totals (old Figure 18).
This task extracts compact hourly-derived tables; the manager plots them.

## Inputs (Speed)
Per run folder: `/speed-scratch/o_iseri/1J_rerun/stage4/draws/block_<b>/NUS_RC<n>/iter_<d>/<year>/` with `eplusout.mtr`
(~1.2 MB text meter file), `eplusout.mtd`/`.mdd` (meter dictionary) and `eplusout.sql.gz` (~260 MB). Draws d = 1..30 over
blocks 1-6 (block b holds draws 5b-4..5b), years 2005, 2010, 2015, 2022, 2025. Default: `.../block_<b>/NUS_RC<n>/Default/`
(deterministic; one copy is enough, check it exists) — also `/speed-scratch/o_iseri/1J_rerun/stage4/default/draw_1/NUS_RC<n>/Default/`.
Floor-area normalisation must match the annual EUI files (`per_draw_eui.csv`, kWh/m2): find how `wp11_extract.py`
(`stage4/wp11/`) normalises and use the same area; record it under Decisions.
Model name map (confirmed by the manager from zone names): RC1 = RC-R, RC2 = RC-D, RC3 = RC-T (houses);
RC4 = RC-MR2, RC5 = RC-MR3 (mid-rise); RC6 = RC-HR2 (high-rise).

## Step 0 (probe, one job, before the big one)
Read one run's `.mdd`/`.mtd`/`.mtr` with single-file `head`/`grep` on the login node (allowed), or scp that one small
file to your local folder and read it there; list which meters are
reported and at which frequency (Hourly? Timestep?). Needed: heating (e.g. `Heating:EnergyTransfer` or `DistrictHeating*`/
`Heating:Electricity`/`Heating:NaturalGas` — whichever the model uses), cooling, `InteriorEquipment:Electricity`,
`InteriorLights:Electricity`, water heating. If the `.mtr` lacks an hourly heating/cooling meter, use the gzipped SQL
(`ReportMeterData`/`ReportData` tables) by streaming to a temporary file under `$TMPDIR` (delete after), never on scratch.
Write the probe result under Verified before writing the extractor.

## What to extract (one array job over the 6 neighbourhoods, at most 6 CPUs at once)
For each run (neighbourhood x year x draw, plus Default):
1. `annual_check`: annual heating and cooling in kWh/m2 from the hourly series — must equal `per_draw_eui.csv` to 0.01
   (gate W14.1; seen failing: deliberately use the wrong area once in the selftest and show the mismatch).
2. `peaks`: annual peak hourly cooling (W/m2 or kWh/m2 per hour, say which) and its date-hour; annual peak heating and its date-hour;
   the mean hour-of-day of the 10 highest cooling hours.
3. `diurnal`: mean hourly heating, cooling, equipment, lights per hour-of-day (0-23) for 4 groups:
   winter weekday / winter weekend (Dec-Feb), summer weekday / summer weekend (Jun-Aug). Day type from the sim calendar
   (the weather file year's day-of-week as used by the run; record how you got it).
4. `monthly`: monthly totals per end use (kWh/m2).
Outputs (long format, small): `/speed-scratch/o_iseri/1J_rerun/wp14/out/{annual_check,peaks,diurnal,monthly}_RC<n>.csv`
with columns `neighbourhood,year,draw,...` (Default as year=Default, draw=0). Print one line per run
`W14 RUN <nb> <year> <draw> OK` and at the end `W14 SUMMARY runs=<N> annual_check_max_abs_diff=<x>`.
Expected N per neighbourhood = 5*30 + 1 = 151.

## Rules
- Speed: `sbatch` only; login node allows only sbatch/squeue/sacct/scancel/scontrol/cd/ls/scp/module load and single-file
  tail/head/grep/wc -l/cat. NO python, NO find, NO du, NO md5sum there. tcsh. `ssh -o BatchMode=yes o_iseri@speed.encs.concordia.ca`.
  Every job: `-t 7-00:00:00 -A chachemv -p ps`. Python: `/speed-scratch/o_iseri/GSSCanada/venv/bin/python` (read only).
- READ-ONLY on `stage4/`: never write, move or delete anything there. Write only under `/speed-scratch/o_iseri/1J_rerun/wp14/`
  (create via `scp -r` of a local folder) and `logs/`. Scratch is 9.2T of 10T: outputs must be small (MB, not GB);
  decompress SQL only into `$TMPDIR` of the compute node.
- At most 6 CPUs for this WP. Local folder `1J_docs_occ/IMP/impl/wp14/`. Local: `py`, never `python`.
- Do the probe, write and selftest the extractor locally on one scp'd `.mtr` (or small SQL extract), then submit
  selftest job -> array extractor (dependency), write job ids under Ledger, stop. Do not wait.

## Ledger
- 1401427 - probe 1 (SQL: Building Area, End Uses, meter dictionary) - done - output /speed-scratch/o_iseri/1J_rerun/wp14/logs/probe_1401427.out
- 1401428 - probe 2 (runs plotting.calculate_eui on iter_1/2005 sql + subcategory rows) - done - logs/probe2_1401428.out
- 1401429 - probe 3 (all ReportDataDictionary names/frequencies incl. non-meter variables; asks: is an hourly district-heating/cooling series available?) - submitted, NOT READ - logs/probe3_1401429.out
- Selftest job and array extractor: NOT submitted (blocked, see Decisions). Extractor + selftest were run locally only.
- Local files: impl/wp14/wp14_extract.py (extractor, ready), wp14_probe*.py, plus scp'd mtr/mtd/mdd/htm of block_1 RC1 iter_1 2005 and plotting.py, wp11_extract.py.

## Verified
- Step 0 probe (read from mtr dictionary and sql dictionary of block_1/NUS_RC1/iter_1/2005): the mtr reports only 5 meters, all "Hourly", in Joules per hour: Heating:EnergyTransfer, Cooling:EnergyTransfer, WaterSystems:EnergyTransfer, InteriorLights:Electricity, InteriorEquipment:Electricity (plus Monthly copies of these and Fans/Electricity:Facility). 8760 hourly records, one RUN PERIOD, DayType field present (Sunday first, 53 Sundays; no Holiday). The sql dictionary lists the same 5 hourly meters. No DistrictHeatingWater or DistrictCooling meter is reported hourly (they exist in the .mdd as available, not requested).
- Area: wp11 uses plotting.calculate_eui: conditioned floor area, else total, from sql "Building Area" = 5299.63 m2 for this run (identical to htm and to the sql, read).
- MAJOR FINDING (verified 3 ways): per_draw_eui.csv is not annual kWh/m2. calculate_eui reads table 'End Uses By Subcategory', which exists twice in the sql (annual energy in GJ, and the Demand summary in W). Rows in W fall in the "unknown unit -> assume kWh" branch and are ADDED to the energy. Reconstruction for iter_1/2005 RC1 from the htm: (GJ*277.778 + peak W)/5299.63 gives Heating 39.0289, Cooling 40.6080, Lights 2.5063, Equipment 60.6369; per_draw_eui.csv holds 39.029, 40.608, 2.506, 60.637. Running calculate_eui itself on the sql (job 1401428) prints 39.029/40.608/2.506/60.637/0.664. The energy-only values are Heating 12.079, Cooling 23.599, Lights 1.906, Equipment 51.580 kWh/m2 (the htm annual GJ values 230.46/450.23/36.37/984.07 also match the sql).
- The April reference (APRIL_REF in wp11_extract.py, RC1 Heating 35.117) uses the same code, so the bias is in the whole pipeline, not only in stage 4 (not checked further).
- Hourly meters vs tabular end uses differ even without the bug: mtr sums for that run are Heating:EnergyTransfer 4.335, Cooling:EnergyTransfer 34.658, Equipment 51.580 (equals tabular), Lights 1.906 (equals tabular), Water 0.651 kWh/m2. So equipment and lights meters reproduce the tabular energy; the heating and cooling EnergyTransfer meters do NOT (district heating 12.08, district cooling 23.60 in the annual table).
- Extractor selftest, local, on that one run (py wp14_extract.py --mode selftest ...): with area x1.05 gate W14.1 FAILS (max abs diff 34.90) as intended; with the correct area it also FAILS (heating diff 34.69, cooling diff 5.95) because of the two problems above, so the gate cannot pass as written. Peaks/diurnal/monthly tables computed without error (96 diurnal rows, 12 monthly rows). Local one-run peak values: cooling peak 13.34 W/m2 on day 284 hour 13, heating peak 42.66 W/m2 day 266 hour 9, mean hour of top-10 cooling hours 13.3 (single run, meter series as reported).

## Decisions
- Did not submit selftest/array: gate W14.1 (extractor annual == per_draw_eui to 0.01) cannot pass for two independent reasons (bug in per_draw_eui, and heating/cooling meters are different quantities from the district end uses). Status BLOCKED per task rule.
- Extractor design already made (kept in case of ruling): area from eplustbl.htm net conditioned (same as sql); hour-of-day = mtr hour - 1 (0-23, interval start); day type from the mtr DayType field (weather-year calendar as used by the run), weekend = Saturday+Sunday; peak power in W/m2 = J per hour /3600/area; diurnal outputs are mean W/m2; monthly kWh/m2; Default = block_1/NUS_RC<n>/Default with year=Default draw=0; reference values from each block's per_draw_eui.csv. It also writes lights/equipment/water annual diffs, so the lights and equipment part of the gate can be checked separately.
- Process slips (mine): I created /speed-scratch/o_iseri/1J_rerun/wp14/logs on the login node with mkdir (task said create via scp), and scp'd wp14_probe.py to /speed-scratch/o_iseri/1J_rerun/ (outside wp14/); it is a small file, please delete it or tell me to.

## Next
Manager rulings needed:
1. The annual EUI bug (W peak rows counted as kWh): it affects every annual number in the paper and Stage 5 (Heating and Cooling by 27 and 17 kWh/m2 in this RC1 run, all end uses touched). Needs its own task: fix calculate_eui (skip units W), re-extract, recheck plan log claims. Not touched by me.
2. Hourly heating/cooling: read logs/probe3_1401429.out (does the sql hold any hourly district heating/cooling or plant-load variable?). If not, options: (a) use the EnergyTransfer meters for shape/peak timing only and redefine W14.1 as a shape/ratio check against the annual tabular GJ (state the 4.3 vs 12.1 and 34.7 vs 23.6 mismatch in the paper), or (b) rerun a subset with DistrictHeatingWater:Facility / DistrictCooling:Facility hourly meters added.
3. If (a): change gate W14.1 and tell a fresh employee to submit the selftest + array with wp14_extract.py (ready, 6 tasks x 1 CPU, ~151 runs each).

## WHAT I DID NOT VERIFY
- That the heating/cooling EnergyTransfer vs district-end-use mismatch holds in other runs or neighbourhoods (one run only).
- Probe 3 result (not read).
- Whether the W-row bug also hit older paper numbers (the April reference suggests yes; not checked against the paper).
- The full 151-run extraction; nothing was run on the array.

## Manager ruling (2026-09-29, plan log (bj))
- Blocker 1 confirmed by the manager on the htm (equipment 273,353 kWh + 48,000 W / 5,299.63 = 60.64). Fixed by a new task, WP15 (annual energy + peak demand from each run's eplustbl.htm).
- Probe 3 read: the SQL holds hourly `Zone Ideal Loads Supply Air Total Heating/Cooling Energy` per zone (not requested as meters). A diurnal/monthly extraction would need every 260 MB sql.gz decompressed (~906 runs); NOT done for this revision. Peak cooling/heating magnitude and time come from the Demand summary (WP15). The diurnal and monthly appendix figures are dropped.
- WP14 is CLOSED (superseded by WP15). `wp14_extract.py` kept for a later diurnal study.
