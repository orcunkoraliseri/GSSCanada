# 5J Step 9f: Model A static-vector reader (task doc for a fresh employee)

Written 2026-10-01 16:01 EDT by the 5J manager. Parent: `Step9_docs/5thJ_09_modelA.md`, blocks "9D FINAL DRAFT" (the rule; read it
first) and "9E detail" item E5 (the 9D FINAL DRAFT overrides E5 where they differ: inputs are read from the windowed IDF, not from the
layout JSONs). Verified inputs: the windowed base (`C:/Users/o_iseri/Desktop/OpenUBEM/openubem/outputs/eu_evidence/EU-11/<D>_win_2026-10-01/`,
`<D>` = `ES-MAD-BERRUGUETE` or `IT-BOL-GALVANI2`; files `idfs/<stem>.idf`, `prepared_buildings.csv`, `windows.csv`), the wall table
`Step9_docs/impl/2026-10-01_wp9c_wall_table_win.csv` and the zone map `Step9_docs/impl/2026-10-01_wp9c_zone_map_win.csv`.
State file you keep: `Step9_docs/impl/2026-10-01_wp9f_static_vector.md` (Ledger, Verified, Decisions, Next, WHAT I DID NOT VERIFY).

## Why
The surrogate gets one fixed description per flat and per building, taken only from what EnergyPlus reads (inputs, never outputs).
This task writes the reader and the two tables for every usable building, before any campaign run exists.

## 🔴 Rules (binding)
* **UK licence:** nothing for London or the UK. Never open, list or pass a path containing `GB`, `LDN`, `London`, `STDUNSTANS`,
  `uk` or `_uk`. Only the two districts named above.
* **No folder-wide or repo-wide search, no recursive listing, and no wildcard of any kind** (a wildcard line count hit a London
  file earlier today, FINDING 5J-4). Get stems from the wall table and open each IDF by its full name.
* **No EnergyPlus output may be read or become a column** (no eplusout, eplustbl, sql). Geometry and construction text only.
* **Do not change any OpenUBEM file.** Write only: `5J_docs_occ/tools/5thJ_modelA_static.py`, your state file, and the folder
  `Step9_docs/impl/static/`.
* **Compute:** desktop, one python process (`py`), geometry parsing only. If it would take more than 30 minutes, stop and write
  the measured rate in the state file.

## Code to reuse (import, never copy-edit; name each function with file:line in the state file)
* `tools/5thJ_modelA_idf.py`: its IDF parsing, zone-map and wall classification code (it already reads these windowed IDFs and
  wrote the wall table). Reuse its parser so both tables read the IDF the same way.

## What to write
1. **Flat table** `static/flats_<district>.csv`, one row per zone of every usable building (zone map rows; usable = wall table
   `zone_map_reason` empty): district, stem, zone, storey index (`floor_k`), storeys spanned (if the IDF shows one), floor area as
   simulated, outdoor wall area in four orientation bins N / E / S / W (outward normal azimuth: N = [315, 45), E = [45, 135),
   S = [135, 225), W = [225, 315), degrees from north, with the IDF's North axis and building rotation applied), window area in the
   same four bins, Adiabatic wall area, roof area (outdoor roof surfaces of the zone), ground-contact floor area, top flag
   (roof area > 0), ground flag (ground floor area > 0).
2. **Building table** `static/buildings_<district>.csv`: district, stem, class (`building_type`), age band (the period field of
   `archetype_id`; write in Decisions how you parsed it, with three examples per district), storeys (distinct `floor_k`), flats,
   conditioned area (sum of flat floor areas), wall / roof / ground-floor / window U-value (from the constructions the surfaces
   use: layer thickness and conductivity, with the film resistances you state; window U and SHGC from the glazing object), window
   share, count of shading surfaces (Shading:* objects) in the IDF, `no_outdoor_wall` flag.
3. **Checks (each PASS / FAIL with what it counted):**
   * rows equal the zone map's usable rows; every usable building has a building row (1,165 / 1,171);
   * per building, the sum of window area over the four bins equals the wall table `window_area_m2_idf` within 0.01 m2, and the
     outdoor wall area equals `eligible_wall_area_m2` plus the too-small, triangle and other walls (state which you compared);
   * the window U and SHGC equal `windows.csv` per building within 0.01;
   * orientation seen working: report, for the 3 buildings with the largest window area per district, the window area per bin,
     and for one building whose IDF has a non-zero North axis or rotation (if any exists), the bins with and without it applied;
   * planted fault: in a copy, swap one building's window U to a wrong value; the U check must FAIL on exactly that building;
   * no column comes from an EnergyPlus output (list every column and its IDF source in the state file);
   * no missing values; ranges printed per column (min, median, max per district).

## Done means
Script written and run; four tables written with md5; every check verdict and the column source list in the state file. Nothing
UK opened or listed; no OpenUBEM file changed; no EnergyPlus output read. End your turn with "done, state written to <path>".
