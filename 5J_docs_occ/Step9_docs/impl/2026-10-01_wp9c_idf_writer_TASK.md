# 5J Step 9c: Model A IDF writer (task doc for a fresh employee)

Written 2026-10-01 15:23 EDT by the 5J manager. Parent: `Step9_docs/5thJ_09_modelA.md` (9A, D9-3 RULED, D9-5 RULED + window data
SETTLED 15:23, 9V). Read those four blocks first; they are the rules. Earlier verified state: `impl/2026-10-01_wp9a_inventory.md`,
`impl/2026-10-01_wp9b_timing_probe_TASK.md` (EnergyPlus path, run command).
State file you keep: `Step9_docs/impl/2026-10-01_wp9c_idf_writer.md` (Ledger, Verified, Decisions, Next, WHAT I DID NOT VERIFY).

## AMENDMENT 2 (2026-10-01 15:45, manager) — the windowed base exists; test on it, not on the fix IDFs
* OpenUBEM's windowed IDFs are built: local `C:/Users/o_iseri/Desktop/OpenUBEM/openubem/outputs/eu_evidence/EU-11/<D>_win_2026-10-01/`
  (idfs/, schedules/, weather/, fleet.lst, prepared_buildings.csv, windows.csv) and on Speed
  `/speed-scratch/o_iseri/fleets/EU11_<D>_win_2026-10-01/`. Manager re-measured at 15:45: windows.csv md5 ES a3edc82e...,
  IT 232134d1...; 1,172 / 1,179 homes; `identity_ok` True for all; 11 / 71 homes without outdoor walls (no windows); 2 / 0
  fallback shares; achieved share within 0.002 of target. Homes come from four source trees (column `source_tree`: fix,
  fix_t06f, fix_t06g, recut_2026-09-08), so zone names and flats must be re-read from these IDFs.
* The first test array (1406998 + 1406999) was CANCELLED by the manager before any task started (it was on the no-window base).
  Keep it in the ledger as cancelled.
* Do now: (1) re-build the zone map and the wall table from the windowed IDFs (new files next to the old ones, suffix `_win`;
  keep the old ones); add per building the window count and window area read from the IDF; (2) re-run the test array on six
  windowed buildings (3 per district, same selection rules, at least one fallback-free building with a triangle wall that got
  a window), runs R0 / R1 / D / O plus P1; (3) G-c2 now evaluable: EnergyPlus's own window area (eplustbl) equals `window_m2`
  in windows.csv within 1 % per building; plant P2 = one building whose IDF copy has one window object removed, which must FAIL
  on that building only. Copies only; never edit the OpenUBEM folders.
* `identity_ok` is OpenUBEM's own check; G-c1 (R1 equals R0) and G-c2 (EnergyPlus window area) are our independent ones.

## AMENDMENT 1 (2026-10-01 15:27, manager) — overrides the window parts below
OpenUBEM is adding windows to its own models (author-ruled method D-EU-140). Model A will use OpenUBEM's windowed IDFs
`EU-11/<D>_win_2026-10-01/idfs/` as its base (not built yet; their `windows.csv` gives target and achieved share, U, SHGC and a
fallback flag per home). So:
* **Do not write window insertion code.** Drop "Windows" from the modes and drop P2. The script must keep any window objects
  already in the base IDF untouched (count them before and after; equal).
* **Window table (item 2) becomes a wall table:** per building, outdoor-wall counts by kind and Adiabatic count only (still
  compared with the peer's counts). No share, U or SHGC computing.
* **Test now on the `fix_2026-10-01` IDFs** (no windows) so the writer is ready; `reproduce`, `default`, `occupancy` modes and
  gates G-c1, G-c3, G-c4, G-c5, G-c6 and timing as written. **G-c2 is re-defined** for later: on the windowed base, the window
  area EnergyPlus reports equals the area implied by `windows.csv` within 1 %. Leave G-c2 NOT_EVALUABLE now and write in `Next`
  that the test array is re-run on the windowed base once the manager says it exists.

## Why
Model A edits copies of the OpenUBEM district IDFs (it does not rebuild them). Each building needs three kinds of run:
an occupancy run (households in the flats), one default-schedule run under the same settings, and a check run that shows the
edit chain itself changes nothing when every edit is switched off. This task writes and tests the script that makes them.

## 🔴 Rules (binding)
* **UK licence:** nothing for London or the UK. Never open, list or copy a path containing `GB`, `LDN`, `London`, `STDUNSTANS`,
  `uk` or `_uk`. Only `ES-MAD-BERRUGUETE` and `IT-BOL-GALVANI2`. In `openubem/data/construction/` open only the two files named
  below, by full name; never list that folder.
* **No folder-wide or repo-wide search, no recursive listing, no wildcard that could match a UK file.** Name files in full; the
  only folders you may list (one level) are the two `fix_2026-10-01/idfs/` folders.
* **Households:** no diary data, no pilot schedule and no pilot generated-day pool may be used (the pilot pools are probably
  built with UK-trained models). Test schedules are synthetic series you write yourself (below).
* **Do not change any OpenUBEM file.** Read from OpenUBEM, write only to `5J_docs_occ/tools/`, your state file, and
  `/speed-scratch/o_iseri/5J/step9c/` on Speed (copies of IDFs and the EPW go there).
* **Compute:** EnergyPlus on Speed via `sbatch` only (never python or EnergyPlus on the login node; `-t 7-00:00:00`,
  `--exclude=antenna1`, **at most 6 CPUs** for this task; the timing probe holds the rest of the cap). Geometry-only parsing of
  the IDFs (no EnergyPlus) may run on the desktop, one process. Never wait for a job: submit, write the job id, end the turn.

## Inputs (all checked to exist by the manager at 15:23)
* IDFs: `C:/Users/o_iseri/Desktop/OpenUBEM/openubem/outputs/eu_evidence/EU-11/<D>_fix_2026-10-01/idfs/<stem>.idf`, list and
  `archetype_id` from `prepared_buildings.csv` in the same folder (columns include `building_id, stem, archetype_id,
  building_type, conditioned_floor_area_m2, fallback_reason`).
* Window data: `C:/Users/o_iseri/Desktop/OpenUBEM/openubem/data/construction/tabula_archetypes_es.json` and
  `tabula_archetypes_it.json`, `records[]` matched on `archetype_id`; fields `geometry.a_window_components_m2`,
  `geometry.a_wall_components_m2`, `u_window_w_m2k`, `g_gl_window`.
* Pilot code to reuse (import, never copy-edit): `5J_docs_occ/tools/5thJ_idf_mz.py` (`inset_window`, `WWR_CAP`, `SHGC`,
  `OUTPUT_VARIABLES`, `OUTPUT_METERS`, the People / ElectricEquipment text at lines 443-475, the glazing text near line 420).
  Check that `inset_window` is correct for walls at any azimuth (the pilot walls were axis-aligned); if it is not, write a
  general version in your script, say so in Decisions, and test it on one rotated wall.
* Weather and EnergyPlus: as in the timing-probe task (same EPW files and md5 check, same EnergyPlus 23.1 path, `-x -r`).

## What to write: `5J_docs_occ/tools/5thJ_modelA_idf.py`
1. **Zone map.** Per building, list the zones; a zone named `<stem>_F<k>_dwelling_<n>` is one flat. A building with any other
   conditioned zone is left out of Model A with reason `not_one_zone_per_dwelling` (D9 rule, 9A). Output per zone: zone, floor
   k, dwelling n, floor area as simulated.
2. **Window table (geometry only, every building in both districts).** Per building: archetype, share (D9-5 formula), window U,
   SHGC used, library g, count of outdoor walls by kind (eligible rectangle, triangle, other shape, too small), Adiabatic wall
   count, eligible wall area, window area, and a flag when the share came from the country median (zero or missing record).
   Totals per district must be compared with the OpenUBEM session's counts (rectangles 36,564 / 58,473, triangles 734 / 1,079,
   other 3 / 10, Adiabatic 19,720 / 44,257); report any difference, do not force agreement.
3. **Modes** (each edit prints one line, and you check each printed edit is PRESENT in the written file):
   * `reproduce`: every edit routine runs but with windows off, the OtherEquipment lump kept, cooling unchanged, only the extra
     Output:Variable / Output:Meter lines added.
   * `default`: windows on, cooling setpoint 26 C and cooling available, OtherEquipment lump kept (3 W/m2), no People or
     ElectricEquipment, pilot outputs added (plus `Zone Ventilation Sensible Heat Loss Energy` and `... Gain Energy`).
   * `occupancy`: as `default`, but the OtherEquipment lump removed and People + ElectricEquipment per zone with Schedule:File,
     object text and split exactly as the pilot (lines 443-475), from a placement CSV: `dwelling_zone, hid, presence_csv,
     appliance_csv, n_members, appliance_peak_w`. Schedule paths must resolve in the run folder on Speed.
   * Windows: one FenestrationSurface:Detailed per eligible wall, inset with the share capped at 0.94, same outward normal
     as its wall, plus one SimpleGlazingSystem construction per building (U, SHGC). Heating setpoint, ventilation,
     InternalMass, timestep, shading settings and geometry stay as simulated.
4. **Test placement.** Synthetic series only: presence 1.0 from 18:00 to 08:00 and 0.2 otherwise; appliance 0.3 at night and
   0.8 from 18:00 to 23:00; 8,760 values; n_members 2, appliance_peak_w 500. Same placement for every flat.

## What to run (one sbatch array, at most 6 at once)
6 buildings, 3 per district, all passing the zone map: one small, one large by dwelling count, and one with at least one
triangle wall. Runs per building: `R0` unedited copy, `R1` reproduce, `D` default, `O` occupancy = 24 runs, plus planted runs:
* P1: in `reproduce`, change one zone's OtherEquipment to 3.3 W/m2 in one building.
* P2: in `default`, force one building's window share to 0.
* P3 (no EnergyPlus): rename one zone in a copy so it no longer matches the pattern.

## Gates (report each as PASS / FAIL / NOT_EVALUABLE, with the exit code meaning written down)
* G-c1 reproduction: annual heating of R1 equals R0 within 0.1 % on every building; P1 must FAIL on exactly its building.
* G-c2 windows, checked by EnergyPlus itself: the window area in the EnergyPlus envelope table of `eplustbl` (window-wall ratio
  / exterior fenestration) equals the writer's window area within 1 % per building for D and O; P2 must FAIL on exactly that
  building and the verdict count of the unplanted run must differ by one.
* G-c3 occupancy edits: in O, People and ElectricEquipment counts equal the flat count, the OtherEquipment lump is gone, the
  hourly equipment electricity sum equals the placement design level times the series within 0.5 %.
* G-c4 cooling: D and O report cooling energy above zero in at least one zone; R0 and R1 report none.
* G-c5 clean runs: exit 0, zero severe errors, and `grep -i "invalid\|not found"` on every `eplusout.err` is empty.
* G-c6 zone map: P3 building is left out with reason `not_one_zone_per_dwelling`.
* Timing: wall seconds of R0, D and O per building (feeds the compute decision, D9-4).

## Done means
Script written; window table and zone-map table written for all buildings (paths in the state file); the array submitted and its
job id written; the state file has the six buildings, every edit line and its presence check, and a `Next` that tells a cold
agent which files to read and which gate table to fill. Nothing UK opened or listed; no OpenUBEM file changed. End your turn with
"job N submitted, state written to <path>".
