# 5J Step 9b: timing probe for the Model A campaign size (task doc for a fresh employee)

Written 2026-10-01 15:09 EDT by the 5J manager. Parent: `Step9_docs/5thJ_09_modelA.md` (9C, D9-4, 9V item 6).
Inputs already verified: `Step9_docs/impl/2026-10-01_wp9a_inventory.md` (IDF location, weather files, default settings, run times).
State file you keep: `Step9_docs/impl/2026-10-01_wp9b_timing_probe.md` (Ledger, Verified, Decisions, Next, WHAT I DID NOT VERIFY).

## Why
One pass of default runs over the two districts costs about 740 CPU-h (median 397 s per building in Madrid, 1,029 s in
Bologna). Model A needs several runs per building. Before the run count is chosen, we need to know how much faster a run gets
with two standard EnergyPlus settings, how much the pilot settings (cooling, more outputs) cost, and whether the faster settings
change the heating result.

## 🔴 Rules (binding)
* **UK licence:** nothing for London or the UK. Never open, list or copy a path containing `GB`, `LDN`, `London`, `STDUNSTANS`,
  `uk` or `_uk`. Only the two districts `ES-MAD-BERRUGUETE` and `IT-BOL-GALVANI2`.
* **No folder-wide or repo-wide search, no recursive listing, no wildcard that could match a UK file.** Name files in full; list
  only the two `idfs/` folders named below (one level).
* **Do not change any OpenUBEM file.** Copy the chosen IDFs and the two EPW files into a new folder of your own
  (`/speed-scratch/o_iseri/5J/step9b/` on Speed), and edit only the copies.
* **Compute:** Speed via `sbatch` only (never python or EnergyPlus on the login node; `-t 7-00:00:00`, `--exclude=antenna1`,
  at most 24 CPUs for this task). Never wait for a job: submit, write the job id in the state file, end the turn.

## Inputs
* IDFs: `C:/Users/o_iseri/Desktop/OpenUBEM/openubem/outputs/eu_evidence/EU-11/<D>_recut_2026-09-08/idfs/<stem>.idf`, stem from
  `prepared_buildings.csv` in the same recut folder; run times from `EU-11/<D>_merged_2026-09-08/<d>_manifest.csv`
  (`run_seconds`, `building_id`, `heating_kwh`). Take only buildings whose `eui_source` is `recut` (their IDF is in the recut folder).
* Weather: `EU-17/<D>/weather/es_madrid_2009_2010_y2010.epw` and `it_bologna_2013_2014_y2014.epw` (md5 110b3649... and
  9a5e2509...; check the md5 of your copies).
* EnergyPlus 23.1 on Speed: find the install the OpenUBEM or 4J Speed jobs use (their sbatch files; name them in the state file).
  The IDFs use HVACTemplate, so run with ExpandObjects (`energyplus -w <epw> -d <out> -x -r <idf>`).

## What to do
1. Choose **12 buildings**, 6 per district, nocore layout only (`layouts/` scheme `nocore_equal_area`), with a known
   `run_seconds`: 2 small, 2 medium, 2 large by dwelling count within the district (pick near the 20th, 50th and 80th percentile;
   no building above the district's 90th percentile of `run_seconds`). Write the list with dwellings and manifest seconds.
2. Make **4 variants** of each IDF (edit copies only; print one line per edit and check it is present in the file):
   * V0: unchanged.
   * V1: `ShadowCalculation` update frequency 20 days instead of 1 (everything else as V0).
   * V2: V1 plus `SimulationControl` zone, system and plant sizing off.
   * V3: V0 plus cooling on at 26 C (cooling availability schedule always 1, cooling setpoint 26 C) and the extra hourly outputs
     the pilot reads (`Zone Ideal Loads Zone Total Cooling Energy`, `Zone Other Equipment Electricity Energy` or the IDF's
     equivalent gain meter; name what you used).
3. Run the 48 runs on Speed in one sbatch job (or a small array), each run timed by wall clock, at most 24 runs at once.
4. Report per building and variant: wall seconds, EnergyPlus exit and severe-error count, annual heating kWh (sum of the hourly
   heating variable), and for V1 and V2 the heating difference to V0 in %. V0 heating must equal the manifest `heating_kwh`
   within 0.1 % (a check on your copy; report any building where it does not).
5. Summary per district: median speed-up of V1 and V2 against V0, median extra cost of V3, largest heating change of V1 and V2.

## Done means
The job is submitted and its id written; the state file lists the 12 buildings, the edits with their check lines, the EnergyPlus
path, and a `Next` that tells a cold agent which output file to read and what table to fill. Nothing UK opened or listed; no
OpenUBEM file changed. End your turn with "job N submitted, state written to <path>".
