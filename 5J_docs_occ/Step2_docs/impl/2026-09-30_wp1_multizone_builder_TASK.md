# TASK (employee, Sonnet): 5J multi-zone builder (D2-8), tests on Speed

Written 2026-09-30 ~15:45 EDT (stamp corrected from `date`) by the 5J manager. Design: `Step2_docs/impl/2026-09-30_d2-8_multizone_design.md`
(read it first; items 1-9 are the spec). State file: create `Step2_docs/impl/2026-09-30_wp1_multizone_builder.md`
(Task doc / Status / Ledger / Verified / Decisions / Next / WHAT I DID NOT VERIFY), write as you go; run `date`
before any time stamp. Paths below: G = `C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main`.

## Hard rules
* 🔴 ALL compute on Speed (author). Locally ONLY: edit/write files, `ssh`/`scp`, `ls`, read small files. No local
  python, no local EnergyPlus. Never touch a process you did not start.
* Speed: `ssh o_iseri@speed.encs.concordia.ca`, tcsh login, wrap as `ssh ... "bash -c '...'"`. Login node:
  `sbatch`, `squeue`, `sacct`, `scancel`, `scp`, `ls`, single-file `cat`/`tail`/`wc -l`. Everything else inside
  sbatch: `#SBATCH -p ps -t 7-00:00:00 --exclude=antenna1 -c 1 --mem=4G`, python
  `/speed-scratch/o_iseri/envs/step4/bin/python -u` (print python + package versions first). EnergyPlus 23.1:
  `/speed-scratch/o_iseri/4J_step10_nocore/opt/EnergyPlus-23.1.0-87ed9199d4-Linux-Ubuntu20.04-x86_64/energyplus`
  (Linux `-x` makes a link `in.idf` in the work dir: never name your input `in.idf` in the run dir; copy the
  pattern of `tools/speed/5J_pilot_array.sh`). After `sbatch`: at most 6 checks, each ONE ssh call
  `sleep 30; sacct -j <id> -X --format=JobID,State,ExitCode,Elapsed,MaxRSS`. Still running after that: write the
  JobID in the Ledger with "manager to read" and stop. Every JobID in the Ledger.
* 🔴 UK licence: Spain only. Never open or copy any UK diary, UK episode, UK manifest, the POOLED 4J corpus, or any
  schedule/IDF/output built from UK diaries. No repo-wide or folder-wide search, no wildcard that could match a UK
  file: name files in full. `tabula-values.xlsx` is public TABULA (allowed); read only the Spanish (ES) rows.
* Edit nothing under `4J_docs_occ\` or `OpenUBEM\`, nor `tools/5thJ_idf.py`. New files only (below).
* Speed folder: `R=/speed-scratch/o_iseri/5J/multizone/` (create). Read-only: `/speed-scratch/o_iseri/5J/pilot/`.
* Past ~150k tokens: stop, write state, "handoff needed".

## Part A: TABULA dwelling count (one sbatch job)
Stage `G\4J_docs_occ\Step8_docs\outputs_step8\raw\tabula-values.xlsx` and `...\raw\tabula-calculator.xlsx` and
`...\outputs_step8\archetype_parameters_es.csv` to `R/tabula/`. In the job (openpyxl, read_only): md5 both xlsx
(expect 7347b2cae3c4d9f5ce78221e9d5fb832 / c99ddc9ffcb6dc0ae7391273d9619e37); list every column header whose
name or label contains `apart`, `dwell`, `n_App`, `n_Dw` or `unit` in each sheet; then, for the 24 `Code_Building`
values of the ES csv, print that column's value per row. Write `R/tabula/dwelling_count_es.csv`
(`code, class, n_storey, a_c_ref, n_dwellings_tabula, sheet, column`). If no such column exists, write that
verbatim; do NOT pick a number. Copy the csv back to `G\5J_docs_occ\Step2_docs\outputs_step2\`.

## Part B: `tools/5thJ_idf_mz.py` (new, local file)
* Imports `derive`, `opaque_construction`, `wall_vertices`, `inset_window`, `vtx` and the constants it needs from
  `4thJ_step8_idf.py`; find `4J_docs_occ/tools` RELATIVE to the script (`<root>/4J_docs_occ/tools` next to
  `<root>/5J_docs_occ/tools`), so the same file runs on Speed. Read `build_idf` in full and reproduce every
  non-geometry object per zone (schedules, constructions, IdealLoads, thermostat, infiltration, E_PHI_INT,
  RunPeriod, outputs) with the 5J changes of `tools/5thJ_idf.py` (Version 23.1; DualSetpoint 20/26, T_TYPE 4;
  infiltration ACH and north axis from the building row; E_PHI_INT 0 W; People with activity 120 W, radiant 0.3;
  ElectricEquipment radiant 1.0). Read `tools/5thJ_idf.py` for the exact object text.
* API: `build_mz(row, k, placement, infiltration_ach, north_axis_deg, collapse=False) -> (idf_text, meta)`.
  `placement` maps dwelling index j (0..n_dwellings-1, numbered floor by floor, west to east) to a household dict
  as in `5thJ_idf.py` (hid, n_members, presence_csv, appliance_csv, appliance_peak_w). Zones `Z_F<ff>_D<jj>`.
  SFH/TH: k = 1, one dwelling spanning every floor, people and design level split by floor-area share.
* Geometry per the design (items 2-6): write rectangular surfaces directly (no geomeppy). Every interzone surface
  has a partner with the same area and reversed vertex order, naming each other as Outside Boundary Condition
  Object. Interior constructions are written for BOTH sides (reverse layer order). Header lines state k, floors,
  zone count and the two ASSUMED interior R values.
* Outputs: `Output:Variable,*,Zone Ideal Loads Supply Air Total Heating Energy,Hourly;` same for Cooling;
  `Output:Variable,*,Electric Equipment Electricity Energy,Hourly;`; the two facility meters; the annual table.
* Prints (and returns in meta) one line per step, each must be PRESENT in the job output:
  `PATCH mz_geometry OK floors=.. k=.. zones=..`, `PATCH mz_areas OK ...`, `PATCH mz_windows OK ...`,
  `PATCH mz_mass OK ...`, `PATCH mz_pairs OK pairs=..`, `PATCH mz_people OK zones=..`,
  `PATCH mz_appliances OK zones=..`, `PATCH mz_outputs OK`.
* `collapse=True`: one zone, full height, k = 1 (the old box) for the carry-over gate.

## Part C: checks, run on Speed (sbatch; one job builds, one array runs EnergyPlus)
Stage `tools/5thJ_idf_mz.py`, `tools/5thJ_idf.py`, `G\4J_docs_occ\tools\4thJ_step8_idf.py`,
`archetype_parameters_es.csv` into `R/repo/` keeping the `4J_docs_occ/tools` + `5J_docs_occ/tools` layout.
Households: the pilot's Spanish inputs `/speed-scratch/o_iseri/5J/pilot/inputs/<building>__<hid>/`
(`presence_HH_<hid>.csv`, `elec_HH_<hid>.csv`); take n_members and the appliance design level from the People and
ElectricEquipment objects of that folder's `in.idf` (read ONE file per household). Test placement only: the pilot's
10 households assigned round-robin to the dwellings.
1. **Area gates** (no EnergyPlus): for each of the 5 pilot buildings (es_B07, es_B16, es_B21, es_B33, es_B37;
   rows via `Step2_docs/outputs_step2/buildings.csv`), with k = TABULA value if Part A found one, else k = 2 for
   MFH and 4 for AB (TEST ONLY, say so): sum of zone floor areas = A_C_Ref; exterior opaque wall = `a_wall_box`;
   glazing = `win_total`; roof = ground = `a_plate`; total capacity = c_m x A_C_Ref; every interzone surface paired
   (all within 0.01 %). Print `PASS|FAIL <gate> <numbers>`.
2. **EnergyPlus runs** (Madrid EPW `/speed-scratch/o_iseri/5J/pilot/epw/` (ls it, name the file)): the 5 buildings
   multi-zone, plus 5 collapse runs, plus the 5 single-zone `5thJ_idf.build` runs of the same first household.
   Each: 0 Severe, "Completed Successfully", seconds and MaxRSS recorded per run.
3. **Carry-over gate:** collapse vs single-zone wrapper, annual heating and cooling each within 0.5 %.
4. **Sanity (INFO):** per building, annual heating and cooling per m2 per dwelling, top floor vs middle vs ground;
   whole-building multi-zone vs single-zone heating and cooling (report the ratio; no pass band).
5. **Seen failing** (each must print FAIL, on scratch copies): drop one zone's floor surface from the area gate
   input; delete one partner of an interzone pair; scale U_wall by 1.10 in the collapse run only (carry-over).

## Report back (short)
Part A result (column found or not, values); PATCH lines present y/n; gate lines; run seconds (median, max) and
zones per building; carry-over numbers; the three seen-failing lines; JobIDs. Status DONE, Next = "manager
verifies; author answers A and B; then pilot rebuild".

## What the manager will re-derive
One building's zone floor area sum against A_C_Ref; one carry-over pair from the EnergyPlus table; one run's seconds.

## 🔴 AMENDMENT 2026-09-30 ~15:52 EDT (manager; stamp corrected): widen the outputs (author)
Author: "for energy outputs, if necessary get out all possible outputs, perforamnce, heating, cooling, lighting,
equipment, etc." Replace the Part B "Outputs" list with, hourly, `*` key:
`Zone Ideal Loads Supply Air Total/Sensible/Latent Heating Energy`, same three for Cooling,
`Zone Ideal Loads Zone Total Heating Energy`, `Zone Ideal Loads Zone Total Cooling Energy`,
`Electric Equipment Electricity Energy`, `Lights Electricity Energy`, `People Total Heating Energy`,
`Zone Infiltration Sensible Heat Gain Energy`, `Zone Infiltration Sensible Heat Loss Energy`,
`Zone Windows Total Heat Gain Energy`, `Zone Windows Total Heat Loss Energy`,
`Zone Windows Total Transmitted Solar Radiation Energy`, `Zone Mean Air Temperature`,
`Zone Operative Temperature`, `Zone Air Relative Humidity`,
`Zone Heating Setpoint Not Met Time`, `Zone Cooling Setpoint Not Met Time`;
meters hourly `Heating:EnergyTransfer`, `Cooling:EnergyTransfer`, `InteriorEquipment:Electricity`,
`InteriorLights:Electricity`, `Electricity:Facility`; keep `Output:Table:SummaryReports, AllSummary;`.
Lighting: do NOT invent a Lights object. Look (by name, one file at a time, Spain only) whether the pilot inputs or
`tools/5thJ_idf.py` carry a lighting schedule; write what you find in the state file (Decisions). If there is
none, the Lights variable simply reports nothing; say so. In Part C step 2, record per run: output folder size
(`du -sk` of that ONE run folder, inside the job) and eplusout.eso size, so the manager can size the campaign disk.
Add one gate: every variable above appears in `eplusout.rdd` or the .eso of one multi-zone run (PASS/FAIL per
variable; `Lights Electricity Energy` may be INFO if no Lights object).
