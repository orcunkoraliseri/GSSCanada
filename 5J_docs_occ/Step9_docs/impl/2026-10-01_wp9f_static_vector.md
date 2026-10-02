# Step 9f static-vector reader: implementation state
Task doc:   Step9_docs/impl/2026-10-01_wp9f_static_vector_TASK.md
Status:     DONE (tables written; 2 checks FAIL as findings, see below)
Script:     tools/5thJ_modelA_static.py (md5 229c0645dd12933390cee7472466957b), run `py tools/5thJ_modelA_static.py` (16 s, one process)
Full log:   Step9_docs/impl/static/checks_log.txt (every ORIENT, RANGE, CHECK line)

## Ledger
* Run 2026-10-01 16:0x, desktop, one python process, no job. Four tables rewritten identically on each re-run (flats md5 stable).

## Verified (all numbers read from the script's own output, checks_log.txt)
Table md5s (static/):
* flats_ES-MAD-BERRUGUETE.csv  f0b79946d944fc8f2906bb0ea6c18712 (12,496 rows)
* buildings_ES-MAD-BERRUGUETE.csv 8574a4a9e02f46c0616f870d7b74087b (1,165 rows)
* flats_IT-BOL-GALVANI2.csv 333d45d110bc12f4a054221155c2ee2d (15,683 rows)
* buildings_IT-BOL-GALVANI2.csv 51326fdc56ce79d98cd25a77023cd787 (1,171 rows)

Checks (per district ES / IT unless noted):
* rows = zone map usable rows, buildings = usable buildings (1,165 / 1,171), zone names identical: PASS / PASS
* floor area per flat vs zone map within 0.001 m2: PASS / PASS (0 differ)
* window area over four bins vs wall table `window_area_m2_idf` within 0.01: PASS / PASS (0 of 1,165; 0 of 1,171 differ)
* outdoor wall: surface count = eligible + too_small + triangle + other counts, area of eligible-class walls = `eligible_wall_area_m2` within 0.01, bin sum = total outdoor wall area: PASS / PASS (0 mismatches)
* window U and SHGC vs windows.csv within 0.01: PASS / PASS (0 differ, both)
* north axis: all IDFs have North axis 0 and every zone has origin and relative north 0. Planted in memory (0 vs 90 deg) on the top building of each district: every bin moves one step clockwise: PASS / PASS
* orientation, top 3 window-area buildings per district: in checks_log.txt (ORIENT lines; e.g. ES 4a1b522ef889bf11 N 404.15 E 554.85 S 407.05 W 1224.04, total 2590.09 m2; IT fd4b13e28f1c6f47 N 564.45 E 530.37 S 667.82 W 402.04, total 2164.68)
* planted fault (window U set to 9.9 in memory on c618dfeb21e06f07, 40 ES buildings re-extracted): U check failed on exactly that building: PASS
* no missing values: PASS / PASS (0 cells). Ranges (min, median, max per column per district): in checks_log.txt (RANGE lines)
* window normal agrees with its base wall normal: PASS / PASS (0 disagreements)
* outward normals (vertex-order normal = geometric outward): FAIL / FAIL. ES: walls pointing into the zone floor polygon 35,764 of 35,969 (ambiguous 201, outward 0 after rounding to 4 dp: outward share 0.0001), floors with upward normal 15,565 of 15,566, roofs with downward normal 3,041 of 3,042. IT: walls 54,494 of 54,700 (ambiguous 206), floors 18,901 of 18,910, roofs 2,681 of 2,681.
* vertex order uniformly inverted (outward share <= 0.1% for walls, floors, roofs): PASS / PASS. So the inversion is global, not a random mix.

### 🔴 FINDING (to the manager, not fixed here): the windowed IDFs list every surface clockwise seen from outside
GlobalGeometryRules says CounterClockWise, but floors have normals pointing up, roofs down and outdoor walls into the zone, in 99.5% or more of all surfaces (both districts). Under EnergyPlus's right-hand rule that means it reads each surface facing the other way (azimuth 180 deg off, floor read as a ceiling). I read no EnergyPlus output, so I do not know what EnergyPlus did with it (its .err would say; manager call, also whether the 56-run pilot and the writer test runs share it: same geometry source). Windows share their wall's orientation, so they are inverted too.

## Decisions
* Orientation bins = what EnergyPlus reads: outward normal from the right-hand rule on the vertex order (Newell, `M.newell`), azimuth = atan2(nx, ny) + North axis, N = [315,45), E = [45,135), S = [135,225), W = [225,315). Reason: the labels come from EnergyPlus, which uses the same normal. To get the geometrically true outward bins, swap N<->S and E<->W (exact, because North axis is 0 everywhere). No extra columns written.
* Windows: area from `FENESTRATIONSURFACE:DETAILED` (area x multiplier, as `M` wall-table code `fen_info`), assigned to the zone of the base surface named in the object, bin from the window's own vertices.
* Wall area is gross (windows not subtracted), as in the IDF. Adiabatic walls = outdoor-less walls with boundary condition Adiabatic; walls with boundary `Surface` (partitions) are not counted anywhere.
* Roof area = type Roof with boundary Outdoors. Ground floor area = type Floor with boundary Ground. Floor area as simulated = sum of Floor-type surfaces of the zone (equals the zone map).
* storeys_spanned = the zone Multiplier (1 in every flat). No IDF field shows a flat spanning two storeys.
* Age band: second-to-fourth dot field of `archetype_id`, i.e. `archetype_id.split(".")[3]` (ES.ME.AB.02.Gen... -> 02; IT.MidClim.AB.01.Gen... -> 01). Examples ES: ES.ME.AB.02.Gen.ReEx.001.001 -> 02, ES.ME.AB.03... -> 03, ES.ME.AB.02... -> 02. IT: IT.MidClim.AB.01.Gen.ReEx.001.001 -> 01 (three times in the first rows; bands 01/03/05 exist). Cross-check column `age_band_prepared` (prepared_buildings.csv `age_band`, e.g. ES.02): 0 mismatches. ES bands 01-06, IT bands 01, 03, 05.
* U-values (m2K/W): U = 1 / (sum of layer R + Rsi + Rse); layer R = thickness / conductivity for MATERIAL, R field for MATERIAL:NOMASS / AIRGAP (all envelope layers here are NOMASS). Films: wall 0.13 + 0.04, roof 0.10 + 0.04, ground floor 0.17 + 0 (ground resistance not added, a stated limit). Wall, roof, floor U area-weighted over the building's outdoor walls, outdoor roofs, ground floors. Window U and SHGC: `WindowMaterial:SimpleGlazingSystem` used by the window constructions (area-weighted), no film added.
* Fallbacks (column `u_src`, counts from the log): ES 11 and IT 71 buildings have no outdoor wall, hence no window object. For them wall U comes from the building's wall construction (no surface), and window U and SHGC come from windows.csv (the value that would be inserted; no IDF source exists). Every other U comes from surfaces. All roofs and ground floors have surfaces in the usable buildings (no roof/floor fallback appeared).
* window_share = window area / gross outdoor wall area (0 when no outdoor wall). n_shading = count of all objects whose keyword starts with `SHADING:` (all `Shading:Site:Detailed` here).
* Check "outdoor wall area = eligible + too-small + triangle + other": the wall table holds counts for the last three, not areas, so I compared surface counts, plus eligible-class area and the bin sum.
* Normal-direction test for walls: probe point 0.05 m either side of the wall centroid against the zone's floor polygons (even-odd). Ambiguous (probe on both or neither side, about 0.5%) counted separately.

## Code reused (from tools/5thJ_modelA_idf.py, imported as M, not copied)
`objects` line 88, `newell` line 116, `area3` line 128, `surface_of` line 133, `classify_wall` line 142, `zone_map` line 175, `read_text` line 77, `idf_path` line 71, `read_windows_csv` line 65, `read_prepared` line 201. `VINTAGE` is forced to win_2026-10-01 before the import (the module reads it at import, line 42). The window object field layout is the one in `fen_info` line 53 (not called; same offsets, with the base surface name added).

## Column sources (all EnergyPlus INPUT text of the windowed IDF; no eplusout / eplustbl / sql read)
Flats: district, stem (file name); zone, floor_k (zone name pattern / zone map); storeys_spanned (ZONE multiplier); floor_area_m2 (BuildingSurface:Detailed type Floor); wall_{N,E,S,W}_m2 (type Wall, boundary Outdoors, vertices, Building North axis); win_{N,E,S,W}_m2 (FenestrationSurface:Detailed vertices x multiplier, base surface zone); adiabatic_wall_m2 (Wall, boundary Adiabatic); roof_m2 (Roof, Outdoors); ground_floor_m2 (Floor, Ground); top_flag, ground_flag (derived from roof_m2, ground_floor_m2).
Buildings: district, stem; building_id, class (building_type), age_band_prepared (prepared_buildings.csv, an input of the writer, not an output); age_band (archetype_id text); storeys (distinct floor_k), flats, conditioned_area_m2 (sum of flat floor areas); u_wall, u_roof, u_floor (Construction + Material:NoMass); u_window, shgc_window (WindowMaterial:SimpleGlazingSystem; windows.csv for the 82 window-less buildings); window_share (windows / outdoor wall area); n_shading (Shading:* objects); no_outdoor_wall (0 outdoor wall surfaces); u_src (which source per U).

## Next
Manager: rule on the inside-out vertex order (FINDING above) before any bin is used as a training input; if the geometry is fixed upstream, re-run the script (16 s) and the bins update by themselves.

## WHAT I DID NOT VERIFY
* What EnergyPlus does with the inverted order (no output read; .err not opened).
* That the surfaces of non-dwelling zones carry no window area: only checked in total (window sum per building = wall table; passes).
* Ground resistance in the floor U (not included).
* That the 5-cm probe finds the 0.5% ambiguous walls' true direction (they are counted separately, not as inverted).
* The 7 (ES) and 8 (IT) buildings of prepared_buildings.csv not in the usable list were not read.
* No UK path was opened or listed; no OpenUBEM file changed; wildcards not used.

## Manager check (2026-10-01 16:10)
* Window U and window area per building re-derived by the manager against windows.csv: equal (U exact, area within 0.002 m2). Normal finding confirmed on 3 buildings with a point-in-floor test and the EnergyPlus err log (floors/roofs auto-fixed, walls not); logged as FINDING 5J-5, author decision D9-6 pending. Tables not frozen until D9-6 is ruled.
