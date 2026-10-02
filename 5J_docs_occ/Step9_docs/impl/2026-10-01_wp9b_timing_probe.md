# Step 9b timing probe: implementation state

Task doc:   `5J_docs_occ/Step9_docs/impl/2026-10-01_wp9b_timing_probe_TASK.md`
Parent:     `5J_docs_occ/Step9_docs/5thJ_09_modelA.md`; input inventory `Step9_docs/impl/2026-10-01_wp9a_inventory.md`
Stamp:      2026-10-01 15:14 EDT (employee, one turn). Status: IN PROGRESS (job submitted; no result read yet)

## Ledger (cluster jobs)
* 1406898 · 5J_9b_probe array 1-48%24 (1 CPU, 6 G each, ps, 7-day wall, --exclude=antenna1) · SUBMITTED 15:13 · at 15:13 pending (AssocGrpCpuLimit) · exit not yet known · logs `/speed-scratch/o_iseri/5J/step9b/logs/task_1406898_<n>.out`, one result line per task in `/speed-scratch/o_iseri/5J/step9b/results/<n>.tsv`
* 1406899 · 5J_9b_agg (1 CPU, dependency afterany:1406898) · SUBMITTED 15:13 · writes `/speed-scratch/o_iseri/5J/step9b/timing_table.csv` and prints it to `logs/agg_1406899.out`

All Speed work is in `/speed-scratch/o_iseri/5J/step9b/` (my own folder): `idf/<stem>_V0..V3.idf`, `epw/`, `schedules/<stem>/`, `manifest.csv` (48 rows: task, district, cls, building_id, stem, variant, dw, manifest_sec, manifest_heat_kwh, epw), `step9b_task.sh`, `step9b_agg.py`, `step9b_agg.sh`, and `runs/<stem>_<V>/` (made by the job). The local build copy and scripts are in the session scratchpad (`build.py`, `sel.py`, `sel2.py`, `pack/`). The full edit log is `Step9_docs/impl/2026-10-01_wp9b_edit_log.txt`.

## Verified (values read, with source)
* EnergyPlus: `/speed-scratch/o_iseri/4J_step10_nocore/opt/EnergyPlus-23.1.0-87ed9199d4-Linux-Ubuntu20.04-x86_64/energyplus` (native 23.1, build 87ed9199d4, the same hash as the manifest `energyplus_version`). Found by reading line 12 of `/speed-scratch/o_iseri/5J/pilot/5J_pilot_array.sh` (the 5J pilot uses it). Other installs seen and NOT used: `/speed-scratch/o_iseri/EnergyPlus` (24.2) and `ep_wrappers/energyplus` (24.2 container). Call as in the pilot: `energyplus -w <epw> -d <out> -x -r model.idf`. The input is copied to `model.idf`, not `in.idf`, because Linux `-x` makes a link called in.idf and an input of that name aborted the pilot array (rc 134).
* Weather md5 of the copies on Speed (read with `md5sum` on Speed): Madrid 110b364912226ee4d2a5b5411eab81da, Bologna 9a5e25091e7a9585f662e1efdc113629. Both equal the task doc.
* On Speed after the copy: 48 idf files, 12 schedule folders (the one I counted holds 20 files), manifest 49 lines.
* Pool: buildings whose `eui_source` starts with `recut_2026-09-08` (the column value is `recut_2026-09-08`, not `recut`), with a `run_seconds`, and `scheme` `nocore_equal_area` in the layout JSON: Madrid 43, Bologna 134. After the cut at the 90th percentile of `run_seconds` (Madrid cap 2,724 s, Bologna cap 4,413 s). Dwellings are `dwellings_total` from the layout JSON.
* Dwelling percentiles of the pool, 20/50/80: Madrid 10 / 18.5 / 30.2; Bologna 5 / 16 / 16 (degenerate; counts by dwellings: 5 -> 32 buildings, 16 -> 74, 20 -> 9, 40 -> 3, 10 -> 1, 30 -> 1).

### The 12 buildings (6 per district, nocore layout)
| district | class | building_id | stem | dwellings | manifest run_seconds | manifest heating_kwh |
|---|---|---|---|---|---|---|
| ES-MAD-BERRUGUETE | small | way/403642586 | 0275c53572b2ff9f | 10 | 731 | 90937.1 |
| ES-MAD-BERRUGUETE | small | way/435637784 | 7307694dddf93fb6 | 10 | 320 | 9383.8 |
| ES-MAD-BERRUGUETE | medium | relation/13255968 | 805223fc4e4eab99 | 19 | 2234 | 137546.3 |
| ES-MAD-BERRUGUETE | medium | relation/4164892 | 644f3f8ccf35816f | 18 | 89 | 53935.4 |
| ES-MAD-BERRUGUETE | large | relation/12818819 | 919761afea1827b3 | 31 | 1094 | 118496.8 |
| ES-MAD-BERRUGUETE | large | relation/4495685 | 6ffe4aadf739b0cb | 29 | 1217 | 202454.6 |
| IT-BOL-GALVANI2 | small | 30376 | 504fa19567bbc2b7 | 5 | 1168 | 22204.5 |
| IT-BOL-GALVANI2 | small | 32163 | 8ee8de43f018af5c | 5 | 1011 | 21791.9 |
| IT-BOL-GALVANI2 | medium | 29219 | 13c60875a803e164 | 16 | 1422 | 135991.9 |
| IT-BOL-GALVANI2 | medium | 31977 | 77c2655993e8fa5e | 16 | 1326 | 51377.8 |
| IT-BOL-GALVANI2 | large | 32840 | b3f8d90890ff6314 | 20 | 436 | 14246.9 |
| IT-BOL-GALVANI2 | large | 32848 | a14255855ef2c815 | 20 | 389 | 12165.2 |

### Edits (copies only; every edit printed and checked)
For every building the build script asserted that the replacement count equals the expected count, then re-read the written files and asserted the edit is present. All 12 buildings passed all asserts (the script stops otherwise). Example, building 0275c53572b2ff9f (10 zones): V0 schedule path 10 of 10; V1 shadow update 1 of 1; V2 sizing off 3 of 3; V3 cooling availability 10 of 10; V3 cooling setpoint 10 of 10; V3 two Output:Variable added.
* V0: the IDF with ONE change: the File Name of every `Schedule:File` gain schedule was `../../schedules/<stem>/...csv` (relative, does not resolve from my folder) and is now the absolute `/speed-scratch/o_iseri/5J/step9b/schedules/<stem>/...csv`. Schedule CSVs were copied from `<D>_recut_2026-09-08/schedules/<stem>/`; the file count equals the number of Schedule:File objects (asserted). Line endings were also changed from CRLF to LF. Nothing else.
* V1 = V0 + `ShadowCalculation` last field `1` to `20` (method Periodic, so update every 20 days).
* V2 = V1 + `SimulationControl` Do Zone / System / Plant Sizing Calculation `Yes` to `No` (3 fields).
* V3 = V0 + cooling availability schedule of every `HVACTemplate:Zone:IdealLoadsAirSystem` from `EU_CoolingOff` to `EU_AlwaysOn` (always 1) + the constant cooling setpoint of every `HVACTemplate:Thermostat` from 50 to 26 + two added hourly `Output:Variable` (key `*`): `Zone Ideal Loads Zone Total Cooling Energy` and `Zone Other Equipment Electricity Energy`. The IDF gain is an `OtherEquipment` object (fuel Electricity), so this is the variable that carries the gain. No People or Lights objects exist in the file.

## Decisions (not in the task doc, and what I assumed)
* The Bologna percentile rule is degenerate (80th percentile equals the median, 16 dwellings). I took small = 5 dwellings, medium = 16, large = 20 (the next value above the median; 40 dwellings has only 3 buildings, above the 97th percentile). Madrid: the two buildings closest in dwellings to each of the 20/50/80 percentiles. Inside one dwelling value for Bologna, the two buildings are those with `run_seconds` closest to the group median. Madrid medium has a wide spread (2,234 s and 89 s).
* Pool is the recut-wave buildings only (as the task doc says).
* One array of 48 tasks, 1 CPU each, throttle 24 at once. EnergyPlus is single threaded. Timing with 24 runs at once on shared nodes is noisier than on a quiet node; the speed-up is a ratio inside one building. At 15:13 the array was pending (AssocGrpCpuLimit, CPU cap used by other jobs), so it may start late; wall seconds are measured inside the task, so queue time does not count.
* Wall time = `date +%s.%N` before and after the EnergyPlus call. Annual kWh = sum over all zone columns of the hourly variable divided by 3.6e6 (awk on `eplusout.csv`). Run folders keep eplusout.err and stdout; csv, sql, eso and mtr are deleted after the sums.
* Heating change for V1 and V2 is against V0 of the same building (computed in `step9b_agg.py`).

## Next
Cold agent: `sacct -j 1406898 -X` (are all 48 COMPLETED?). For failed tasks read `logs/task_1406898_<n>.out` and `runs/<stem>_<V>/eplus_out/eplusout.err`; resubmit only those with `sbatch --array=<n,...> step9b_task.sh` and then `sbatch step9b_agg.sh`. Then `cat /speed-scratch/o_iseri/5J/step9b/timing_table.csv` (login node, single file; it is also in `logs/agg_1406899.out`). Its first block is one line per building and variant (wall s, exit, completed flag, severe count, heating, cooling, equipment kWh, heating change vs V0 in %, manifest heating, V0 vs manifest in %); its last two lines are the per-district summary (median speed-up of V1 and V2, median V3 / V0, largest absolute heating change of V1 and V2). Fill the per-building table and the district summary into this file under Verified, flag any building where V0 differs from the manifest by more than 0.1 %, set Status to DONE, and give the numbers to the manager for the run-count decision (9C, D9-4, 9V item 6).

## WHAT I DID NOT VERIFY
* Any run result. No task has run yet. The V3 variable names are the standard EnergyPlus 23.1 names, but whether they appear in the output is known only after the run (the awk prints NA for a missing column).
* That all 48 tasks fit in 6 G of memory.
* That `Zone Other Equipment Electricity Energy` is what the pilot reads (the pilot variable list was not opened).
* That V2 (sizing off) runs. Ideal loads with no capacity limit should not need sizing, but only the run shows it.
* That the V0 copy reproduces the manifest heating (the check is in the table after the run).
* UK: nothing UK was opened or listed by me on purpose. Incidental contact: `ls /speed-scratch/o_iseri/` and `ls` of the 5J folder printed the names of other folders and tarballs, including a UK-named tarball; none was opened, copied or touched.
* No OpenUBEM file was changed. I only read (and copied) IDFs, schedules, EPWs, manifests and layout JSONs of the two named districts.
