# Step 9a inventory for Model A: implementation state

Task doc:   `5J_docs_occ/Step9_docs/impl/2026-10-01_wp9a_inventory_TASK.md`
Parent:     `5J_docs_occ/Step9_docs/5thJ_09_modelA.md`
Stamp:      2026-10-01 15:00-15:12 EDT (employee, one turn). Status: IN PROGRESS (item 5 waits on one Speed job; items 1-4 DONE)

OD = `C:/Users/o_iseri/Desktop/OpenUBEM`. EU11 = `OD/openubem/outputs/eu_evidence/EU-11`. L3D = `OD/docs/docs_ACTIVE/europeanLocations/outputs_3D`.
Districts below are only ES-MAD-BERRUGUETE (Madrid) and IT-BOL-GALVANI2 (Bologna).

## Ledger (cluster jobs)
* 1406847 · wp9a_corpus (1 CPU, ps, 7-day wall, --exclude=antenna1) · SUBMITTED 15:06 · exit not yet known · output `/speed-scratch/o_iseri/5J/step9a/corpus.out`
  script `/speed-scratch/o_iseri/5J/step9a/step9a_corpus.py`, input `pos_hids.tsv` (same folder, 27,980 rows = Spain and Italy households with weight > 0, made locally from the weight columns of the two 4J episode parquets).
* Read-only `sacct` on 1314028 (Madrid) and 1314067 (Bologna): these are ARRAYS of chunk tasks (one task = a chunk of buildings, 1 CPU, 6 G, e.g. 1314028_16 COMPLETED 01:15:32, some tasks FAILED after 2-4 s), TotalCPU shows 00:00:00. So `sacct` gives no per-building time; the per-building time comes from the manifest column `run_seconds` (item 3).

## Verified (values read, with source)

### 1. OpenUBEM district inputs (2026-09-08 recut)
* State block: `OD/docs/docs_ACTIVE/europeanLocations/STATE_european_locations_v5.md` lines 1-60 (head block). Its numbers hold: layout side-cars 1,174 (Madrid) and 1,211 (Bologna); `nocore_equal_area` 1,151 and 1,171; fallback 23 and 40.
* CHECKED by counting the layout JSON files myself (`L3D/eu_<D>_data/layouts/`; Madrid files sit in `relation/` 129 and `way/` 1,045; Bologna 1,211 flat): scheme `nocore_equal_area` Madrid 1,151, Bologna 1,171; scheme null (fallback) 23 and 40. EQUAL to the state block.
* Buildings and dwellings of the nocore set (from `dwellings_total` in each layout JSON, own count):
  * Madrid: 1,151 buildings, 11,976 dwellings. SFH 8 (10 dwellings), TH 50 (50), MFH 12 (73), AB 1,081 (11,843). Equals the Step 7 preflight figure.
  * Bologna: 1,171 buildings, 15,705 dwellings. SFH 20 (20), TH 36 (36), MFH 340 (2,085), AB 775 (13,564). (NEW: the design draft says MEASURE.)
  * Storeys per building (nocore): Madrid median 4, max 9; Bologna median 5, max 11.
* Whole prepared population (not only nocore), `EU11/<D>_merged_2026-09-08/<d>_manifest.csv` (1,187 and 1,215 rows): Madrid AB 1,112, TH 54, MFH 12, SFH 9; Bologna AB 798, MFH 361, TH 36, SFH 20. Geometry outcomes Madrid: DWELLING_LAYOUT_EMITTED 1,032, INTERZONE_MISMATCH_REROUTED 73, BEST_EFFORT 44, FALLBACK_PENDING_LAYOUT 22, IMPUTED_COUNT 7, FALLBACK..._MISSING_DWELLING_COUNT 7, BEST_EFFORT_IMPUTED_COUNT 2. Bologna: IMPUTED_COUNT 954, BEST_EFFORT_IMPUTED_COUNT 127, REROUTED 93, FALLBACK_MISSING_DWELLING_COUNT 41.
* Where the IDFs live: one IDF per building, named by the 16-hex `stem` column of `prepared_buildings.csv`: `EU11/<D>_recut_2026-09-08/idfs/<stem>.idf` (1,194 Madrid files, 1,220 Bologna files; more than the 1,187 / 1,215 prepared rows, reason not checked). The recut folder also holds `layouts/`, `schedules/<stem>/`, `prepared_buildings.csv`, `recut_simulate_list.csv`, `excluded_buildings.csv`, `fleet.lst`. The IDF is written by the OpenUBEM campaign code (module `openubem/campaign/`, builder script not opened; not needed because the IDFs exist). Older waves (final, delta, ceiling82) hold the IDFs of buildings that were not re-run in the recut; the merged manifest column `eui_source` says which wave each building comes from (Madrid: delta 630, final 269, ceiling82_carry 215, recut 56, pending 17; Bologna: delta 626, final 234, ceiling82_carry 207, recut 138, pending 10).
* Weather: Madrid `es_madrid_2009_2010_y2010.epw`, sha256 d2563b7dfdd8a78716ce3611c4180bea4e4d217b3779d0f693c607390a17346d, md5 110b364912226ee4d2a5b5411eab81da. Bologna `it_bologna_2013_2014_y2014.epw`, sha256 ab631c6026e3f7cf5cfcff7c6a506eb84b6eeb62f1afa5703fc48ef0897e25fa, md5 9a5e25091e7a9585f662e1efdc113629. Files are in `EU11/../EU-17/<D>/weather/`; sha256 recomputed by me equals the `weather_sha256` in every manifest row (1,187 / 1,215 rows, one value each). THIS IS THE SAME EPW YEAR AS THE PILOT (Madrid 2010, Bologna 2014) and the same as 4J (`FOLD_EPW` in `4J_docs_occ/tools/4thJ_step10_nocore_campaign.py:201-205`). So D9-1 is no longer a choice: the default runs and the pilot use one weather file per district.
* EnergyPlus: Version 23.1.0-87ed9199d4 (manifest column `energyplus_version`); return code 0 on all 1,170 (Madrid) and 1,205 (Bologna) buildings with a result.
* HVAC and setpoints, read from one IDF (`EU11/IT-BOL-GALVANI2_recut_2026-09-08/idfs/02dd9c3e4f745e0b.idf`, building 27410, 16 dwellings): `HVACTemplate:Zone:IdealLoadsAirSystem` per dwelling zone, heating setpoint 20 C (`HVACTemplate:Thermostat`, constant), cooling setpoint 50 C and cooling availability schedule `EU_CoolingOff` = 0 (so heating ONLY, no cooling), no heating or cooling capacity limit, max supply 50 C. Output requested: only `Zone Ideal Loads Zone Total Heating Energy`, hourly (line 8083). Internal gain: one `OtherEquipment` per zone, Watts/Area 1 x a `Schedule:File` of 8,760 hourly values (the `schedules/<stem>/<stem>_F<floor>_dwelling_<n>_f000_gain.csv` files; the one I read holds a constant 3 W/m2); no People, no Lights, no ZoneInfiltration object in the file. `SimulationControl` runs zone, system and plant sizing; shading `PolygonClipping`, `Periodic`, update 1. Neighbours = `Shading:Site:Detailed` (44 polygons in this IDF). Only one IDF read; I did NOT check that all IDFs share these settings.
* Consequence for 9A, 9D, D9-3 (decision for the manager, not taken here): default runs are heating-only with a constant 3 W/m2 gain; the pilot uses 20 / 26 C ideal loads with cooling, people and appliances. A like-for-like level comparison needs the occupancy runs to be read as heating only, or the default runs to be re-run with the pilot's settings (the author re-runs them 10-02; whether the re-run changes the settings is NOT FOUND).
* Later fixes exist and the recut is not the newest state: `EU11/<D>_merged_2026-09-29/summary.json` (fix_2026-09-29 replaced 92 Madrid and 110 Bologna buildings; pooled EUI Madrid 88.244591, Bologna 56.692386, against 81.387738 and 54.671865 in 09-08) and folders `<D>_fix_2026-10-01*` (t06f, t06g, sliver.txt) newer still. I did not open them. The layouts in `L3D` carry the 09-08 vintage. The author's re-run (ready about 10-02) may change layouts and IDFs; counts above must be re-checked then.

### 2. Per-building and per-dwelling metadata
* `L3D/eu_<D>_data/layouts/<building>.json` (nocore buildings; complete for all 1,151 and 1,171, no missing value in the fields below): `building_type` (class), `archetype_id` (country, climate zone, class, age band, e.g. `IT.MidClim.AB.01...`), `storeys`, `dwellings_total`, `units_per_floor`, `observed_max_per_floor`, `floor_to_floor_m`, `gross_footprint_area_m2`, `conditioned_floor_area_m2`, `dwelling_count_provenance`, `construction_period_provenance`, `crs`, and per floor: `storey_index`, `dwelling_count`, `zones[]` with `name` (`<id>_F<floor>_dwelling_<n>`), `coords_m` (polygon, metres), `z_floor`, `z_ceiling`, `storey_span`. Per building also `facade_contact_lengths_m` (one value per dwelling; length equals `dwellings_total` on 100 % of nocore buildings, checked 1,151 + 1,171) and `partition_audit`, `regularization`.
* Dwelling floor area: NOT stored as a number; it is computed from `coords_m` (shoelace). Dwelling floor = `storey_index` of its zone. Dwelling area from polygons: Madrid median 74.1 m2, min 4.6, max 1,081.5; Bologna median 78.4, min 1.8, max 2,281.0. The tiny and huge values are plate-split artefacts (the author's later `sliver` fix task is about this); they need a rule before a building vector is frozen.
* Multi-storey dwellings: a dwelling spanning n storeys is written n times (one per floor row), byte-identical, so zone-row count differs from `dwellings_total` in 233 Madrid and 35 Bologna nocore buildings (distinct zone names = `dwellings_total`, as the 4J code documents; the retracted FINDING 268 was this). Use distinct zone names.
* Construction period: class and age band in `archetype_id` and manifest `age_band` (Madrid ES.01-ES.06 counts 11 / 243 / 188 / 278 / 358 / 109 over 1,187; Bologna IT.01 1,109, IT.03 81, IT.05 25) with 0 % missing; provenance column `construction_period_provenance` (Bologna `IMPUTED_CENSUS_SECTION_CONSTRUCTION_PERIOD` on 1,211 of 1,215, i.e. imputed from the census section; Madrid blank on 1,174 of 1,187 = observed). TABULA envelope values by archetype: 4J `archetype_idf_manifest.csv` (`4J_docs_occ/Step8_docs/outputs_step8/`, named in `5thJ_design_tables.py`, not opened) and the IDF constructions; not read here.
* Footprint, height: `L3D/eu_<D>_data/buildings.csv` (1,398 and 1,257 rows, includes non-residential `excluded` rows; columns building_id, class, building_tag, footprint_area_m2, levels, height_m, height_source, year_built, layout_state, storey_count, dwelling_count, gross_area_m2, conditioned_area_m2, circulation_pct). Missing share: `year_built` 100 % in both; `levels` 25.3 % Madrid and 100 % Bologna; `height_m` 0 % but is an assumed 9.0 m in Bologna (`height_source` "assumed 9.0 m"). Its row counts (1,194 and 1,220 residential) differ from the manifests (1,187 / 1,215): older vintage, not reconciled.
* Neighbour shading: no per-building shading value; only `context_building_count` (`EU11/<D>_recut_2026-09-08/prepared_buildings.csv`, 0 % missing; Madrid median 12, range 3-26; Bologna median 11, range 1-28) and the neighbour polygons inside each IDF (`Shading:Site:Detailed`). A shading factor would have to be computed from the IDF polygons.
* Orientation: not stored (the IDF has `North Axis 0`); derivable from `coords_m` and `facade_contact_lengths_m` only by computing it.
* Not stored anywhere I read: window area or glazing ratio per dwelling (in the IDF only), exposed facade length (only contact length with neighbours per dwelling; exposed length = perimeter minus contact, to compute).

### 3. Run time per building of the 2026-09-08 recut
Source: `run_seconds` in the two merged manifests (1,187 and 1,215 rows), joined to the nocore set (dwellings from the layout JSONs). 229 / 219 rows have no `run_seconds` (carried or pending), so the recut timing alone is only 56 / 138 buildings (43 / 134 nocore).
* Madrid, all nocore buildings with a time (926 of 1,151): median 395 s per building, 90th percentile 1,391 s, mean 645 s, total 166 CPU-h; per dwelling median 52.1 s, 90th 229.3 s, mean 107.5 s.
* Madrid, recut-wave only (43): median 922 s, 90th 2,785 s, mean 1,376 s; per dwelling median 45.0 s, 90th 145.4 s.
* Bologna, all nocore with a time (952 of 1,171): median 998 s, 90th 4,092 s, mean 1,636 s, total 432.7 CPU-h; per dwelling median 83.4 s, 90th 353.2 s, mean 149.5 s.
* Bologna, recut-wave only (134): median 1,432 s, 90th 4,445 s, mean 1,981 s; per dwelling median 100.8 s, 90th 443.0 s.
* Platform in the manifest: Speed nodes, EnergyPlus 23.1, heating-only, hourly output of one variable, sizing on. Occupancy runs add outputs (cooling, equipment) and per-zone people; expect equal or more.
* SIZING CONSEQUENCE (my arithmetic, not a decision): one pass over all nocore buildings costs about 1,151 x 645 s + 1,171 x 1,636 s = about 206 + 532 = about 740 CPU-h. The design draft assumes 79 s per building and 360 CPU-h for about 7 runs per building. At the measured times, 7 runs per building is about 5,200 CPU-h (about 7 days on 30 CPUs, about 22 days on 10 desktop CPUs). The 79 s figure was NOT FOUND in the 4J campaign script; the 4J Italy shakedown cells (`4J_docs_occ/Step10_docs/outputs_step10_nocore/cells/it__*.json`, 1,427 completed cells, field `wall_seconds`) give median 49.1 s, mean 61.3 s, 90th 109.7 s per cell, but those cells are a sample of small buildings on the desktop and not the district distribution. Item 6 of 9V (timing before sizing) is therefore decisive; the frozen design needs either fewer runs per building or a building subset.

### 4. The 5J side (code read only)
* `4J_docs_occ/tools/4thJ_step10_nocore_campaign.py` (1,821 lines). Households enter as: `build_cells` (line 679) takes `paired_mod.build_pairs(rows, by_fold, seed_base=SEED_BASE)` (4J paired-design module, built on `4thJ_step7_schedules` pools) and gives each drawn flat one INDEPENDENT presence series (`unit["presence_path"]`, read by `paired_mod.S.read_presence`, line ~1359). Cells = building x case (A, B) x f level (`F_LEVELS` 0, .15, .30, .50, 1.00, line 316). The presence series is turned into ONE combined `Watts/Area` gain schedule per flat by OpenUBEM `emit_step8_gain_schedule` (called at line 1360; import at 1122, `openubem/semantic/european_schedules.py`); there is no separate People object and no appliance series, f = 0 gives the default gain. One zone per drawn dwelling (zones taken from the layout payload, `zones_for_cell`, line 959); if a building is rerouted to one zone per floor the diaries are area-averaged per floor (`average_units_by_floor`, line 997). Weather: `FOLD_EPW` es/it as above. Engine call: `energyplus -w <epw> -d . -x -r <idf>` (line ~1561, ExpandObjects needed for HVACTemplate). Output: only `Zone Ideal Loads Zone Total Heating Energy` (line 1403). Its district table also lists a UK entry, which I ignored. Spain: the campaign output folder holds only Italian cells (`it__*`, 1,427); NO Spanish cell exists there (Spain not run).
* Can `5J_docs_occ/tools/speed/mzp_extract.py` (134 lines) read those outputs? NOT AS IT STANDS. Differences: (a) it expects the 5J run folder (`R/run_manifest.csv`, `R/runs/<run_id>/meta.json` with `zone_dwelling`, `zone_floor_areas`, `eplus_out/eplusout.csv`), whereas 4J runs write `eplusout.csv` in the cell folder and a cell JSON; (b) its zone-name regex is `(Z_F\d\d_D\d\d)$` (5J builder names), whereas OpenUBEM zones are `<building>_F<floor>_dwelling_<n>` (and for Spain `relation/<n>_...` / `way/<n>_...`, with the slash handled in 4J by a cell slug); (c) it reads 20 variables including cooling and equipment, but 4J/OpenUBEM IDFs output ONLY the heating variable. The variable name `Zone Ideal Loads Zone Total Heating Energy` is in its list (as `zoneside_heating_kwh`), so the heating-only columns would match by name. Needed for Model A: an IDF writer that adds the other output variables and a zone-to-dwelling map for the OpenUBEM names.

### 5. Households and diary days (Spain and Italy)
* Corpus (Speed): `/speed-scratch/o_iseri/5J/households/repo/4J_step3_corpus_es_it.jsonl`, 57,400 lines, 39,651,076 bytes, modified 2026-09-30 16:17. Record fields: country, hid, pid, diary_day, split (4J fold label; not used), text (prefix `country,age_band,sex,household_type,economic_status,day_type|episodes`). No weight and no household size in the record; size = distinct pid per hid (as `5thJ_design_tables.py` `read_household_sizes`); weight from the Spain and Italy episode parquets (`4J_docs_occ/Step1_docs/outputs_step1/episodes_spain.parquet`, `episodes_italy.parquet`; I read only columns hid, pid, weight_ind, no other column). The parquets hold all hids of the survey: Spain 19,295 persons in 9,541 households; Italy 41,229 persons in 18,439 households; EVERY person and every household (lowest-pid rule) has weight > 0, so the positive-weight filter removes nothing (27,980 households, written as `pos_hids.tsv`). Note the corpus has 57,400 rows, 3,124 fewer than the 60,524 parquet persons; the job below counts the corpus rows that are really there.
* The counts by household size, respondents, days per bucket and back-off per split: job 1406847, output `/speed-scratch/o_iseri/5J/step9a/corpus.out`. A cold agent reads that file (single-file `cat` on the login node) and copies the numbers into this section. The job prints: prefix field check, rows per respondent (days per respondent), day types seen, households and respondents by size (1/2/3/4/5+), households with weight > 0, the indicative 70 / 15 / 15 split by household size (python `random.Random(9001)`, sorted hids shuffled per size stratum, round(0.70 n) and round(0.15 n); NOTE this is an indicative split for counting only, NOT the frozen split of the design), and per split: persons, days by day type, full-depth buckets present and how many hold >= 5 and exactly 1 day, then for every person x day type slot the deepest back-off level that still holds >= 1 day (4 = exact bucket, 0 = day type only) and with >= 5 days, and the number of distinct demanded full buckets that need back-off.
* Back-off ladder (code, `4thJ_step7_schedules.py` lines 101-102 and 181-182 and 233-246): fields in order age band, sex, household type, economic status, plus day type always; `draw` falls from depth 4 to depth 0 and records the depth. The corpus holds one diary day per respondent, so a split-aware pool is only as deep as the respondents of that split.

#### Job 1406847 output (2026-10-01 15:46:43 EDT)

```
prefix field counts {6: 57400} bad 0
corpus split field (4J fold labels, not used) {('es', 'train'): 17332, ('es', 'heldout'): 1808, ('it', 'train'): 34366, ('it', 'heldout'): 3894}
== es rows 19140 distinct pid 19140 max rows per pid 1
 day types {'sunday': 3826, 'weekday': 11638, 'saturday': 3676}
 diary_day values {'7': 3826, '2': 1982, '6': 3676, '1': 1968, '5': 3883, '3': 1879, '4': 1926}
 households 9541 by size {'1': 3002, '2': 4401, '3': 1385, '4': 624, '5+': 129}
 households weight>0 (lowest-pid rule, from episodes parquet) 9541 by size {'1': 3002, '2': 4401, '3': 1385, '4': 624, '5+': 129}
 respondents (rows) in weight>0 households 19140
 sizes raw {1: 3002, 2: 4401, 3: 1385, 4: 624, 5: 102, 6: 19, 7: 5, 8: 2, 10: 1}
 split households {'dev': 6678, 'val': 1431, 'test': 1432}
 split dev persons 13393 days by type {'sunday': 2685, 'weekday': 8132, 'saturday': 2576} full buckets present 709 with>=5 days 425 with 1 day 102
   person x daytype slots 40179 deepest level with >=1 day (4 = exact bucket) {3: 376, 4: 39803} | with >=5 days {2: 274, 3: 2851, 4: 37054}
   distinct demanded full buckets 852 needing back-off (0 days) 143 (<5 days) 427
 split val persons 2868 days by type {'sunday': 538, 'weekday': 1760, 'saturday': 570} full buckets present 492 with>=5 days 164 with 1 day 146
   person x daytype slots 8604 deepest level with >=1 day (4 = exact bucket) {2: 52, 3: 461, 4: 8091} | with >=5 days {2: 1096, 3: 1792, 4: 5716}
   distinct demanded full buckets 663 needing back-off (0 days) 171 (<5 days) 499
 split test persons 2879 days by type {'weekday': 1746, 'saturday': 530, 'sunday': 603} full buckets present 491 with>=5 days 164 with 1 day 145
   person x daytype slots 8637 deepest level with >=1 day (4 = exact bucket) {2: 53, 3: 498, 4: 8086} | with >=5 days {2: 960, 3: 1979, 4: 5698}
   distinct demanded full buckets 696 needing back-off (0 days) 205 (<5 days) 532
== it rows 38260 distinct pid 38260 max rows per pid 1
 day types {'saturday': 12733, 'sunday': 12329, 'weekday': 13198}
 diary_day values {'2': 12733, '3': 12329, '1': 13198}
 households 18435 by size {'1': 6504, '2': 6681, '3': 3108, '4': 1746, '5+': 396}
 households weight>0 (lowest-pid rule, from episodes parquet) 18435 by size {'1': 6504, '2': 6681, '3': 3108, '4': 1746, '5+': 396}
 respondents (rows) in weight>0 households 38260
 sizes raw {1: 6504, 2: 6681, 3: 3108, 4: 1746, 5: 322, 6: 55, 7: 10, 8: 5, 9: 4}
 split households {'dev': 12905, 'val': 2765, 'test': 2765}
 split dev persons 26779 days by type {'saturday': 8937, 'sunday': 8728, 'weekday': 9114} full buckets present 819 with>=5 days 547 with 1 day 108
   person x daytype slots 80337 deepest level with >=1 day (4 = exact bucket) {3: 188, 4: 80149} | with >=5 days {2: 75, 3: 2051, 4: 78211}
   distinct demanded full buckets 909 needing back-off (0 days) 90 (<5 days) 362
 split val persons 5737 days by type {'saturday': 1940, 'weekday': 2006, 'sunday': 1791} full buckets present 623 with>=5 days 270 with 1 day 167
   person x daytype slots 17211 deepest level with >=1 day (4 = exact bucket) {2: 15, 3: 303, 4: 16893} | with >=5 days {2: 398, 3: 1899, 4: 14914}
   distinct demanded full buckets 786 needing back-off (0 days) 163 (<5 days) 516
 split test persons 5744 days by type {'saturday': 1856, 'weekday': 2078, 'sunday': 1810} full buckets present 605 with>=5 days 265 with 1 day 155
   person x daytype slots 17232 deepest level with >=1 day (4 = exact bucket) {2: 9, 3: 354, 4: 16869} | with >=5 days {2: 344, 3: 1902, 4: 14986}
   distinct demanded full buckets 777 needing back-off (0 days) 172 (<5 days) 512
```

The corpus holds 57,400 diary records: Spain 19,140 rows (9,541 households) and Italy 38,260 rows (18,435 households). Both countries show a 70/15/15 split into development, validation, and test households; all are weighted positive. The back-off levels show how many person-day-type slots draw from full detail (level 4) versus falling back to coarser bins, with the largest pools (>= 5 days per slot) mostly staying at the full depth and needing 143–205 back-off buckets per split.

Ledger: 1406847 COMPLETED, output pasted 2026-10-01 15:46:43 EDT

## Decisions (not in the task doc, and what I assumed)
* Item 5 weights: the corpus has none, so I read the weight columns of the two episode parquets locally (Spain and Italy only, 3 columns). Assumption: this equals the "positive weight" rule of the task doc; all weights are positive so the result does not depend on it.
* Item 5 counts run on Speed from the Speed corpus copy; no local corpus copy was opened (the local path appears only in code, not in a doc).
* "Per dwelling" run time = per-building `run_seconds` divided by `dwellings_total` (distinct dwellings), only for nocore buildings with a time.
* Wrote scratch scripts only in the session scratchpad and under `/speed-scratch/o_iseri/5J/step9a/` (a new folder, my own); no OpenUBEM, 4J or 5J project file was changed.

## Next
Cold agent: `cat /speed-scratch/o_iseri/5J/step9a/corpus.out` (login node, single file) after `sacct -j 1406847 -X` shows COMPLETED; paste the counts into section 5 above and set Status to DONE. If the job FAILED, read the last lines of `corpus.out` and fix `step9a_corpus.py` in the same folder.
Manager: rule D9-1 (weather: same files, already settled), D9-3 (heating-only default vs 20 / 26 C), and the compute size (about 5,200 CPU-h at measured times, against 360 in the draft) before freezing 9C.

## WHAT I DID NOT VERIFY
* The result of job 1406847 (not waited for).
* That every IDF shares the HVAC, setpoint and gain settings of the one I read; the IDF builder code (`openubem/campaign/`) and the `idf_sha256_matches_ceiling82` column.
* Why the recut IDF folders hold 1,194 / 1,220 files against 1,187 / 1,215 prepared rows; why `buildings.csv` has more residential rows than the manifests.
* Anything in the `_merged_2026-09-29`, `_fix_2026-09-29/30`, `_fix_2026-10-01*` folders beyond the two `summary.json` files; the layouts may have changed since 09-08.
* The 79 s per building of the draft; the Spanish run time of the 4J campaign (no Spanish cell exists).
* TABULA envelope values (4J `archetype_idf_manifest.csv` not opened); window area per dwelling.
* The 4J `paired` module (`build_pairs`) and `emit_step8_gain_schedule` source were not opened; their behaviour is taken from the campaign script's comments and calls.
* UK: nothing UK was opened or listed. Two incidental contacts, both declared: (1) one grep line of the OpenUBEM state file printed a UK folder name inside a path string and was not followed; (2) the `4thJ_step10_nocore_campaign.py` code contains a UK district entry and a UK weather file name, read as part of the file, ignored. A directory listing of `EU11`, `4J Step10 outputs` and `5J tools` returned UK-named entries; they were filtered out of the display where possible and never opened.

## Files and jobs read (full list)
Local: task doc; `5thJ_09_modelA.md`; `STATE_european_locations_v5.md` (head and two greps); `EU11/<D>_merged_2026-09-08/summary.json` and `<d>_manifest.csv` (both districts); `EU11/<D>_merged_2026-09-29/summary.json`; `EU11/<D>_recut_2026-09-08/prepared_buildings.csv`; one IDF (`.../IT-BOL-GALVANI2_recut_2026-09-08/idfs/02dd9c3e4f745e0b.idf`) and one gain csv; `L3D/eu_<D>_data/buildings.csv`, `sources.json`, and all layout JSONs of the two districts (counting); `EU-17/<D>/weather/*.epw` (hash only), `EU-17/<D>/prepared_buildings.csv`; `4thJ_step10_nocore_campaign.py` (grep and ranges); `4thJ_step7_schedules.py` lines 100-275; `5J_docs_occ/tools/speed/mzp_extract.py` lines 1-70; `5thJ_design_tables.py` (greps and lines 140-196); `Step2_docs/outputs_step2/campaign_design.md`, `households.csv`, `Step2_docs/impl/2026-09-30_wp1_it_households.md` (greps); `4J_docs_occ/Step10_docs/outputs_step10_nocore/cells/it__*.json` (wall_seconds); `episodes_spain.parquet`, `episodes_italy.parquet` (3 columns).
Speed: `sacct` 1314028, 1314067; corpus file (`ls`, `wc -l`, `head -c 1800`); `ls` of `/speed-scratch/o_iseri/5J/households/` (and its `ref`, `tools`, `repo`), `.../repo/4J_docs_occ`, `.../5J`; grep of `hh_B.py`, `hh_build.py`; `hh_B.sbatch`; job 1406847 (submitted).
