# TASK (employee, Sonnet): 5J building wrapper + secondary activity + first local test runs (Spain)

Written 2026-09-29 by the 5J manager. Design is settled in `../5thJ_02_campaignDesignPilot.md` §2F:
D2-2 (settled 2026-09-29 block), D2-3, D2-4, D2-7. Do not change any design value; if something does
not fit, write it under Decisions and stop that part.
State file you keep current: `2026-09-29_wp1_wrapper.md` (same folder; CLAUDE.md template: Task doc /
Status / Ledger / Verified / Decisions / Next / WHAT I DID NOT VERIFY). Create it first.

## Hard rules
* **Spain only.** 🔴 Never open UK (or any pooled) diary, episode, schedule, manifest, IDF or output
  file. Italy is not needed here either.
* Never edit anything in `4J_docs_occ/` or `C:\Users\o_iseri\Desktop\OpenUBEM\`. Import or copy only.
* Local runs only, EnergyPlus `C:/EnergyPlusV23-1-0/energyplus.exe`. One working directory per run.
* A weather download (python `acquire_era5_5J.py`) may be running in the background: do not stop it,
  do not touch `_5J_data/surrogate/weather/`.
* Create only the files named here. You do not wait on anything.

## Files
* `5J_docs_occ/tools/5thJ_idf.py` — the wrapper.
* `5J_docs_occ/tools/5thJ_step9_trigger_act2.py` — copy of `4J_docs_occ/tools/4thJ_step9_trigger.py`
  (record source md5) with the one secondary-activity change (and, only if needed, a copy of the
  mapping module the trigger imports; record its md5 too).
* Outputs: `C:\Users\o_iseri\Desktop\GSSCanada\_5J_data\surrogate\wp1_test\` (IDFs, run folders,
  a `test_report.md`).

## Part A — wrapper `5thJ_idf.py`
Import `derive` and `build_idf` from `4J_docs_occ/tools/4thJ_step8_idf.py` (sys.path insert; never
copy-edit it). `build(row, household, infiltration_ach=0.5, north_axis_deg=0.0) -> (idf_text, meta)`.
Apply these patches to the text; **each patch prints one line `PATCH <name> OK <detail>`** and raises if
its anchor text is not found exactly once:
1. `version`: `Version, 24.2;` → `Version, 23.1;`.
2. `dual_setpoint`: replace the `ThermostatSetpoint:SingleHeating` object and the thermostat control
   reference with `ThermostatSetpoint:DualSetpoint` (heating 20 °C, cooling 26 °C, constant schedules),
   control type 4 (`DualSetpoint`), `T_TYPE` constant set to 4.
3. `meters`: add `Output:Variable,*,Zone Ideal Loads Supply Air Total Cooling Energy,Hourly;` (heating
   one exists; keep it), `Output:Meter,InteriorEquipment:Electricity,Hourly;`, and
   `Output:Meter,Electricity:Facility,Hourly;` (a cross-check only).
4. `infiltration`: the ACH value in `ZoneInfiltration:DesignFlowRate` → the argument.
5. `north_axis`: Building object field 2 → the argument.
6. `phi_zero`: `OtherEquipment E_PHI_INT` design level → 0 (keep the object; say so in the line).
7. `people`: add a presence `Schedule:File` + `People` object on the box zone, as
   `4thJ_step7_schedules.py:398-434` writes them (head-count = household size, same activity level
   schedule value, same radiant fraction; copy the numbers from that code and cite line numbers in the
   state file). Presence CSV from Step 7.
8. `appliances`: add the appliance `Schedule:File` + `ElectricEquipment` from
   `4thJ_step9_trigger.py` `idf_objects(...)` (1063-1124), **with the zone name changed to the box
   zone**; do NOT add the `WaterUse:Equipment` or DHW schedule (D2-7). Peak W from the Step 9 outputs
   for that household.
Schedule:File paths must be absolute, `Interpolate to Timestep` = No, rows 8,760 checked before
writing. Write `meta` = every input path + md5, every patch line, the argument values.

## Part B — secondary activity (D2-4)
In the trigger copy, the only change: an episode can switch on an appliance if its **primary or its
secondary** activity (`act2`) maps to it (read how `act` maps today; apply the same map to `act2`;
no new map entries). Mark it `# 5J change (D2-4)` and print `PATCH act2 OK` when it is active; a flag
`--no-act2` gives the 4J behaviour. Run the copy for **Spain only**, **2 households** (the first two
`hid` in sorted order that have Step 7 presence files in
`4J_docs_occ/Step7_docs/outputs_step7/schedules/leg5_es_independent_seed1_cal2010/`), both with and
without act2, output under `wp1_test/step9_act2/` and `wp1_test/step9_no_act2/`. If the trigger
cannot run for 2 named households without the full fold, record why and run what the CLI allows with
the smallest `--n-households`, Spain only, writing only under `wp1_test/`. Check: `--no-act2` output of
a household = the 4J Step 9 file for that household (md5 or max abs difference, if it exists in
`4J_docs_occ/Step9_docs/outputs_step9/enduse_profiles/es/`); act2 output has annual electricity ≥ the
no-act2 value (report both numbers).

## Part C — test runs (local, Spain)
Building: one Spain TABULA row that the 4J builder already makes (the first `ES` single-family row in
`4J_docs_occ/Step8_docs/outputs_step8/archetype_parameters_es.csv`; name it). Weather: the Madrid 2010
ERA5 EPW (path from `5J_docs_occ/Step1_docs/outputs_step1/wp0_inventory.md` section D). Runs:
H1 act2, H2 act2, H1 act2 repeated (replicate), H1 no-act2. Four runs, one folder each.
For each run record in `test_report.md` and the state file: EnergyPlus "Completed Successfully",
severe and warning counts, hourly rows = 8,760 for each target, annual heating, cooling, appliance
electricity (kWh), and annual sum = sum of hourly values.
Re-derivations (write both numbers): annual appliance electricity from EnergyPlus vs peak W × sum of
the hourly fraction column / 1000.
Must hold: heating > 0 and cooling > 0 (Madrid); H1 and H2 differ in all three targets; H1 and its
replicate identical (or say the difference); H1 act2 electricity ≥ H1 no-act2.

## Part D — gate seen failing
A checker function `check_patches(idf_text, printed_lines)` that returns FAIL if any of the 8 patch
lines is absent or any anchor object is missing from the saved IDF. Show it FAILING on (1) a saved IDF
with the `People` object deleted, (2) a printed-lines list with `PATCH dual_setpoint` removed; and
PASSING on the real test IDF. Record the three outputs.

## Report back (short)
Paths, the four runs' annual numbers, the re-derivation pair, the gate outputs, source md5s, anything
you could not do and why.
