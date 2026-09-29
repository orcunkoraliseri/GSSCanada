# WP0 Employee B (area truth, StatCan, existing building models) - implementation state
Task doc: 5J_docs_occ/impl/2026-09-22_wp0_task.md
Status:   DONE (B2 EnerGuide redo appended below, 2026-09-26)

## Files kept      <- path, bytes, sha256, URL, time
- `_5J_data\statcan_38100019-eng.zip` — 31912 bytes — sha256 215b5c83e1d92ba8300bdb46c5630aeebbe9444fde2e1bc0637f49de5b93577e — https://www150.statcan.gc.ca/n1/tbl/csv/38100019-eng.zip — 2026-09-22 20:43 local
- `_5J_data\statcan_38100286-eng.zip` — 154495 bytes — sha256 287795d1ae8c9e8dc3005854236423d54b8e47e3eb416e390e7765b7b68abfa1 — https://www150.statcan.gc.ca/n1/tbl/csv/38100286-eng.zip — 2026-09-22 20:43 local
- `_5J_data\statcan_38100019\38100019.csv` (extracted from zip) — sha256 e20f8088c329352c3c5fc7f93e111586f662a4e4d8ed95012e8633ff3e08a126
- `_5J_data\statcan_38100286\38100286.csv` (extracted from zip) — sha256 583cac3e25357d843f3d594970af8583bcf7b0d977bf132905e764a942a67acc
- `_5J_data\statcan_extract_38100019_38100286.csv` — 167115 bytes — sha256 6d9c99ed229b9d6bd01b4a90d5311fc9e043e111c4ae1b3b129d05661d9cd7d6 — built by `statcan_extract.py` (this task) — 2026-09-22 20:44 local
- EnerGuide per-year CSVs: `_5J_data\energuide_<year>.csv` for years 2004-2006 (merged), 2007-2026, downloaded from CKAN resources under dataset `0a7619fd-2ffe-44b5-9027-3dfcec0866fd` (see per-file table below once download completes). Download in progress as of 2026-09-22 20:44 local via background script; log at `_5J_data\download_log.txt`.
- IDFs (read-only, NOT copied, NOT edited, path is inside `GSSCanada-main` as the task allows for existing models): sha256 of the 4 files as found on disk 2026-09-22:
  - `ASHRAE901_ApartmentHighRise_STD2022_Buffalo_NECB17_Z6_v242.idf` — 98cbb291a439f5b7c98d69a52de769a9086bf5906976a13f4e6e61dca24920fe
  - `ASHRAE901_ApartmentMidRise_STD2022_Buffalo_NECB17_Z6_v242.idf` — cfde0ee60cc7f2419f7552bf358571593bc579919bac5daf69a4bab3ed713f1f
  - `AttachedHouse+CZ6A+IECC+2024_NBC936_Z6_v242.idf` — dec64fc31fdc39cae9a047652c7f51563f35d6db56613b04782bb122656cc33f
  - `DetachedHouse+CZ6A+IECC+2024_NBC936_Z6_v242.idf` — 745a06875927473c514534c1ad7b5c42f33fa68b5c31f81c4d9a9cdcfaae8bf6
- `_5J_data\nrcan_open_data_dictionary.xlsx` — 56181 bytes — https://open.canada.ca/data/dataset/0a7619fd-2ffe-44b5-9027-3dfcec0866fd/resource/4b738fc9-80a6-47c9-a442-0f1ae2b57d9c/download/nrcan-open-data-dictionary-dictionnaire-des-donnees-ouvertes-de-rncan.xlsx — 2026-09-22 20:49 local

## EnerGuide licence and dataset identification
- Dataset: "EnerGuide Rating System Open Data", CKAN id `0a7619fd-2ffe-44b5-9027-3dfcec0866fd`, found via `open.canada.ca` search, confirmed via CKAN `package_show` (`https://open.canada.ca/data/api/3/action/package_show?id=0a7619fd-2ffe-44b5-9027-3dfcec0866fd`, fetched 2026-09-22 with a browser User-Agent + Referer header — plain curl with no UA/Referer was rejected by the WAF with an HTML "Request Rejected" page, no HTTP status captured before the switch).
- Licence per `package_show`: `license_id` = "ca-ogl-lgo", `license_title` = "Open Government Licence - Canada", `license_url` = https://open.canada.ca/en/open-government-licence-canada.
- Licence text quoted verbatim from that URL (fetched 2026-09-22): "You are encouraged to use the Information that is available under this licence with only a few conditions. Using Information under this licence Use of any Information indicates your acceptance of the terms below. The Information Provider grants you a worldwide, royalty-free, perpetual, non-exclusive licence to use the Information, including for commercial purposes, subject to the terms below. You are free to: Copy, modify, publish, translate, adapt, distribute or otherwise use the Information in any medium, mode or format for any lawful purpose. You must, where you do any of the above: Acknowledge the source of the Information by including any attribution statement specified by the Information Provider(s) and, where possible, provide a link to this licence. If the Information Provider does not provide a specific attribution statement ... you must use the following attribution statement: Contains information licensed under the Open Government Licence — Canada."
- Per-year CSV resources (23 total): 21 data years as CSV (2004-2006 merged, then one file per year 2007-2026; 2026 is a partial/in-year file, size not listed in the catalog), plus 1 XLSX data dictionary and 1 Power BI dashboard link (not downloaded, not data).
- File-level licence note found directly on file inspection: no separate per-file licence text; only the dataset-level OGL-Canada licence above applies (per `package_show`).

## Verified        <- numbers actually read, with where
### StatCan 38-10-0019-01 (air conditioners) and 38-10-0286-01 (primary heating system)
- Source: CKAN full-table CSV zips at `https://www150.statcan.gc.ca/n1/tbl/csv/38100019-eng.zip` and `.../38100286-eng.zip`, downloaded 2026-09-22.
- 38100019.csv: 2348 data rows total (`wc -l` = 2349 incl. header). Columns: REF_DATE, GEO, DGUID, "Air conditioners", UOM, UOM_ID, SCALAR_FACTOR, SCALAR_ID, VECTOR, COORDINATE, VALUE, STATUS, SYMBOL, TERMINATED, DECIMALS.
- 38100286.csv: 15016 data rows total (`wc -l` = 15017 incl. header). Same column layout with category column "Primary heating system and type of energy".
- GEO values matching Montreal/Toronto/Quebec/Ontario found in both tables (read from the `GEO` column): "Montréal, Quebec" (CMA), "Toronto, Ontario" (CMA), "Quebec" (province), "Ontario" (province). (Other CMAs like Ottawa-Gatineau, Sherbrooke etc. also present but out of scope per task.)
- Extract `_5J_data\statcan_extract_38100019_38100286.csv`: 1380 rows total = 184 rows from 38100019 + 1196 rows from 38100286, filtered to those 4 GEO values, TABLE_ID column added to tell the two tables apart.
- Years present in the extract (both tables, identical set): 2013, 2015, 2017, 2019, 2021, 2023 (read from `REF_DATE` column). This is a biennial series (household energy use survey years), not annual.
- Categories in 38100019 "Air conditioners" column: 13 distinct values — Any/Central/Mini-split/Stand-alone/Other type of air conditioner and Heat pump and Heat-recovery ventilation unit (HRV), each reported both "as a percentage of all households" and "as a percentage of households that had an air conditioner".
- Categories in 38100286 "Primary heating system and type of energy" column: 59 distinct values, spanning fuel types (Electricity, Natural gas, Oil, Propane, Wood, Wood pellets) and system types (Forced air furnace, Boiler with hot water or steam radiators, Heating stove, Heat pump, Mini-split heat pump, Heated floors, Electric baseboard heaters, Centralized HVAC system, combinations of fuel x system, and "All primary heating systems").

### EnerGuide columns (read from the file header, `_5J_data\energuide_2004-2006.csv`, and definitions read from `_5J_data\nrcan_open_data_dictionary.xlsx`, sheet "Open Data-Donnees ouvertes")
- All year files (2004-2006 through 2026) have the identical 433/434-field header (checked by diffing the header row of the oldest file, `energuide_2004-2006.csv`, against the newest, `energuide_2026.csv`: 0 differences).
- Postal-area column: `CLIENTPCODE`, dictionary type `char(7)`, description "Homeowner postal code (where property is located) Only first 3 digits provided." — i.e. this column already IS the FSA (3 characters, e.g. "M1B", "H2X"), not a full postal code.
- Pre/post-retrofit marker: `EVALTYPE`, dictionary description "Type of Evaluation, D, E, P or N" (no letter-to-meaning expansion given anywhere in the dictionary file). Linkage note from the dictionary: "Files can be linked together using the following fields: EVALTYPE, EVALUATIONSID and HOUSEID" and `EVALUATIONSID` = "Identifier representing a unique Pre and post-retrofit evaluation pair (i.e. D and E files for the same house will have the same EvaluationsId)" — confirms D/E is the pre/post-retrofit pair, P and N are the two other evaluation types (new-construction plan/as-built, per the dataset's own description of "existing housing assessments (pre retrofit, post retrofit)" and "evaluations for new homes (plan files and as-built houses)" — but the dictionary does not spell out which of P/N is which). Observed codes in a 14,980-row sample (`energuide_2004-2006.csv`): D, P, N (no E in that sample).
- Heat pump / AC / primary heating columns (dictionary descriptions quoted): `AIRCONDTYPE` "Type of central A/C System (...) or 'Not installed'"; `ASHPHSPF`/`ASHPHSPF2`/`ASHPSEER`/`ASHPSEER2` (air-source heat pump efficiency); `CCASHP` "Indicates the presence of a cold climate heat pump (1 = yes, 0 = no)" with `CCASHPCAP`/`CCASHPCOP`/`CCASHPHSPF`/`CCASHPSEER`; `HPCAP` "Heat pump capacity (Watts)"; `HPEquipType` "Indicates the type of heat pump (...)"; `HPSOURCE` "Heat pump type (air, water, ground or N/A)"; `FURNACEFUEL` "Primary heating equipment fuel type"; `FURNACETYPE` "Primary heating equipment type"; also `INDFURNACEFUEL`/`INDFURNACETYPE` (secondary/induced-draft furnace) and `MURBFURNACEFUEL`/`MURBFURNACETYPE` (MURB-specific). Upgrade-case duplicates of most of these exist with a `UGR` prefix (post-retrofit proposed values).
- Insulation columns (dictionary descriptions quoted, all `decimal(19,10)` RSI values unless noted): `CEILINS` "Ceiling effective insulation RSI value"; `MAINWALLINS` "Main walls effective insulation RSI value"; `FNDWALLINS` "Foundation effective insulation RSI value" (basement/foundation walls); `SLABINSUL` "Indicates basement slab insulation (1 = yes, 0 = no)" (flag, not RSI). `UGR`-prefixed versions of each exist for the upgrade case.
- Evaluation date column: `ENTRYDATE`, dictionary description "Evaluation date (the date when the evaluation was performed). Only the month and year are provided." Sample values are `YYYY-MM-01` (day always 01, confirming month/year-only granularity).

### Existing EnergyPlus models (`2J_docs_occ_nTemp/BEM_setup/Buildings_MTL_v242/`, read-only, never edited)
Parsed with a read-only script (`idf_scan.py`/`idf_scan2.py`, this task, run via `py -3`, never touched the IDFs). Floor area = shoelace-formula area of every `BuildingSurface:Detailed` object with `Surface Type = Floor`, summed per zone (matches EnergyPlus's own zone-floor-area autocalculation rule), then summed across zones x zone Multiplier. This is a "sum of all zone floor areas" total (attic/basement included), not necessarily E+'s "Net Conditioned Building Area" — see Decisions.

**ASHRAE901_ApartmentHighRise_STD2022_Buffalo_NECB17_Z6_v242.idf**
- Zones: 27 (26 apartments/office + corridors on 3 floors: G/M/T). Total floor area (sum over zones): 2350.94 m². Each apartment zone = 88.249 m²; corridor zones = 77.658 m².
- Heating/cooling: per-apartment water-to-air heat pump system — `AirLoopHVAC:UnitaryHeatPump:WaterToAir` (24), fed by `Coil:Heating:WaterToAirHeatPump:EquationFit` (24) and `Coil:Cooling:WaterToAirHeatPump:EquationFit` (24), plus electric backup `Coil:Heating:Electric` (24, supplemental heat) and one central `Boiler:HotWater` ("Central Boiler") on `PlantLoop` "Single Water Plant Loop". Domestic hot water: `WaterHeater:Mixed` ("SWHSys1 Water Heater") on `PlantLoop` "SWHSys1". Ventilation: `ZoneHVAC:EnergyRecoveryVentilator` (23) with controllers (23). 24 `AirLoopHVAC` objects (one per conditioned zone) with splitters/mixers/supply-return paths.
- Wall construction `NECB_Z6_Wall`: layers 1IN Stucco / 8IN CONCRETE HW / NECB Z6 Wall Insulation / 1/2IN Gypsum (interior wall `int_wall`: gypsum board both sides). Roof `NECB_Z6_Roof`: Roof Membrane / NECB Z6 Roof Insulation / Metal Decking. Floor/ceiling `int_slab_ceiling` and `int_slab_floor`: CP02 Carpet Pad / 100mm Normalweight concrete. Ground floors use per-orientation `Construction:FfactorGroundFloor`-style objects named `g*Floor*_Ffactor` (not plain `Construction` objects — layers not applicable, F-factor method).
- Windows: 42 `FenestrationSurface:Detailed` objects, 2 constructions: `ResWindow_U_0.382_SHGC_0.368` (layer "Res Window Glazing Layer") and `NonresWindow_U_0.382_SHGC_0.368` (layer "Nonres Window Glazing Layer").
- Infiltration: 28 `ZoneInfiltration:DesignFlowRate` objects, calc method `Flow/ExteriorWallArea`, value 1.25e-05 (m3/s per m2 exterior wall area) for every zone.

**ASHRAE901_ApartmentMidRise_STD2022_Buffalo_NECB17_Z6_v242.idf**
- Zones: 27 (same layout as high-rise: apartments/office + 3 corridors). Total floor area: 2350.96 m² (same per-zone areas as high-rise, 88.249 / 77.659 m²).
- Heating/cooling: per-apartment split DX system — `AirLoopHVAC:UnitarySystem` (24) with `Coil:Cooling:DX:SingleSpeed` (24) and `Coil:Heating:Fuel` (24, gas furnace coil). No central boiler; `WaterHeater:Mixed` per apartment (23, one per unit) instead of one central unit. Same ERV ventilation pattern (23) as high-rise.
- Same wall/roof/floor constructions as high-rise (`NECB_Z6_Wall`, `NECB_Z6_Roof`, `int_slab_ceiling`), plus `ext_slab_8in_with_carpet` (200mm Normalweight concrete / CP02 Carpet Pad) for ground-contact slab.
- Windows: 39 `FenestrationSurface:Detailed`, same 2 constructions as high-rise.
- Infiltration: 28 `ZoneInfiltration:DesignFlowRate`, same method and value (1.25e-05 Flow/ExteriorWallArea).

**AttachedHouse+CZ6A+IECC+2024_NBC936_Z6_v242.idf**
- Zones: 21 = 7 row-house units x 3 zones each (`living_unitN`, `attic_unitN`, `unheatedbsmt_unitN`). Total floor area: 1890.0 m² (180.0 m² living + 90.0 m² basement per unit x 7; attic zones report 0 m² floor because their only bounding "Floor"-type surface belongs to the living zone below — the attic has no surface of its own tagged `Surface Type = Floor`).
- Heating/cooling: per-unit central system — `AirLoopHVAC:UnitaryHeatCool` (7, name "ACandF_unitN"), fed by `Coil:Heating:Fuel` (7, "Main Fuel heating coil") and `Coil:Cooling:DX:SingleSpeed` (7). Per-unit `WaterHeater:Mixed`+`WaterHeater:Sizing` (7 each) on per-unit `PlantLoop` ("DHW Loop_unitN"). Ventilation: `ZoneHVAC:EnergyRecoveryVentilator` (7) and `ZoneVentilation:DesignFlowRate` (7, all "Flow/Zone" with a 0 base flow — schedule-driven).
- Wall `NBC936_Z6_Wall`: 1IN Stucco / 8IN CONCRETE HW / NBC936 Z6 Wall Insulation / 1/2IN Gypsum. Basement wall `NBC936_Z6_BasementWall`: 8IN CONCRETE HW / NBC936 Z6 Foundation Insulation / 1/2IN Gypsum. Roof `NBC936_Z6_Roof`: 1/2IN Gypsum / NBC936 Z6 Roof Insulation. Slab `NBC936_Z6_SlabOnGrade`: HW Concrete / NBC936 Z6 Slab Insulation / CP02 Carpet Pad. Interior floors ("Exterior Floor"/"Interior Floor" — names as given in the IDF, both used for floors between conditioned zones): Plywood 3/4in / Carpet_n_pad (+ a `floor_consol_layer` on the exterior-facing one).
- Windows: 32 `Window` objects (simple by-ratio type, not `FenestrationSurface:Detailed`), single construction "Exterior Window" (layer "Glass", material is a `WindowMaterial:SimpleGlazingSystem` or `WindowMaterial:Glazing` — 2 of each type present in the file, not individually matched here). 14 `Door` objects, construction "Exterior Door" (layer "door_const").
- Infiltration: modeled via AirflowNetwork, not `ZoneInfiltration:*` (0 `ZoneInfiltration:DesignFlowRate` objects). 7 `AirflowNetwork:MultiZone:Surface:EffectiveLeakageArea` definitions reused across units: ZoneLeak_LongWall (2.361e-3 m2), ZoneLeak_ShortWall (1.771e-3 m2), ZoneLeak_Ceiling (8.291e-3 m2), ZoneLeak_Floor (8.333e-6 m2), ZoneLeak_NonGarageWall (1.175e-3 m2), AtticVent (0.37 m2), CrawlVent (0.37 m2) — all at discharge coefficient 1.15, reference pressure 4 Pa, flow exponent 0.65. 85 `AirflowNetwork:MultiZone:Surface` objects link these leakage areas to specific building surfaces.

**DetachedHouse+CZ6A+IECC+2024_NBC936_Z6_v242.idf**
- Zones: 3 (`living_unit1` 220.818 m², `attic_unit1` 0 m² floor, `unheatedbsmt_unit1` 110.409 m²). Total floor area: 331.23 m². (`living_unit1`'s floor area sums 2 Floor-type surfaces — an adiabatic interior floor plus the floor separating it from the basement — this is how the archetype lumps 2 stories into 1 zone; see Decisions.)
- Heating/cooling, wall/roof/slab constructions, window/door constructions, and the AirflowNetwork infiltration leakage set are identical in structure and values to the Attached House file, just for 1 unit instead of 7 (1 `AirLoopHVAC:UnitaryHeatCool`, 1 `Coil:Heating:Fuel`, 1 `Coil:Cooling:DX:SingleSpeed`, 8 `Window`, 2 `Door`, same 7 AFN leakage-area definitions, 19 `AirflowNetwork:MultiZone:Surface` links).

**What a change would touch (object types only, read from the files above, no values changed):**
- Window swap: the `Window` objects (houses) or `FenestrationSurface:Detailed` objects (apartments) keep their geometry; a window-performance change means editing the `WindowMaterial:SimpleGlazingSystem` / `WindowMaterial:Glazing` object(s) referenced by the window `Construction` (e.g. "Exterior Window" -> "Glass" layer; "ResWindow_U_0.382_SHGC_0.368" -> "Res Window Glazing Layer").
- Insulation change: edit the relevant `Material`/`Material:NoMass` insulation layer object (e.g. "NECB Z6 Wall Insulation", "NBC936 Z6 Wall Insulation", "NBC936 Z6 Foundation Insulation", "NBC936 Z6 Roof Insulation", "NBC936 Z6 Slab Insulation", "NECB Z6 Roof Insulation") — the `Construction` objects that reference them (`NECB_Z6_Wall`, `NBC936_Z6_Wall`, `NBC936_Z6_BasementWall`, `NBC936_Z6_Roof`, `NECB_Z6_Roof`, `NBC936_Z6_SlabOnGrade`) do not need to change, only the material layer inside them.
- Heating system change (baseboard/furnace/heat pump): the `Coil:Heating:*` object type would change (`Coil:Heating:Fuel` <-> `Coil:Heating:Electric` <-> `Coil:Heating:WaterToAirHeatPump:EquationFit`) plus its parent system object (`AirLoopHVAC:UnitaryHeatCool` / `AirLoopHVAC:UnitarySystem` / `AirLoopHVAC:UnitaryHeatPump:WaterToAir`) and, for the apartment high-rise, the central `Boiler:HotWater` + `PlantLoop`.
- Air conditioning change: the `Coil:Cooling:*` object (`Coil:Cooling:DX:SingleSpeed` <-> `Coil:Cooling:WaterToAirHeatPump:EquationFit`) inside the same parent system object as above.

## Decisions       <- open questions for the manager

## Next

## WHAT I DID NOT VERIFY


## B2 EnerGuide (redo)
Employee B2, 2026-09-26. Replaces every EnerGuide number Employee B produced while files were still downloading (those are void). Nothing above this heading is changed except Status.
Scripts (all in `_5J_data\scripts_wp0\`, run with `py -3`, one file at a time, nothing on the cluster): `b2r_stage1_year.py` (per year: size vs log, sha256, csv-parser row count, slim parquet copy), `b2r_stage2a_files.py`, `b2r_stage2b_values.py`, `b2r_stage3_fsa.py`, `b2r_check_item5.py`, `b2r_make_md.py`. Intermediate outputs: `scripts_wp0\b2r_out\` (per-year json + parquet, `ALL.parquet`, `values_out.txt`, `stage3_out.txt`). The older files `b2_energuide_full_scan.py`, `b2_scan_state.json`, `b2_item5_best_rows.csv` in the same folder come from the earlier B2 launch; they were NOT used and NOT trusted.
Columns read (only these 10 of 433): CLIENTPCODE, EVALTYPE, EVALUATIONSID, HOUSEID, ENTRYDATE, AIRCONDTYPE, HPSOURCE, CCASHP, FURNACEFUEL, FURNACETYPE. All read as raw text with `keep_default_na=False` (a first attempt used pandas defaults, which silently turn the text "None"/"N/A" into missing; it was discarded and everything re-run). HOUSEID and EVALUATIONSID are stored as e.g. `298307.0` in the files; the trailing `.0` was removed.

### Item 1. Per file (read by scripts_wp0/b2r_stage1_year.py, output scripts_wp0/b2r_out/YEAR.json, table copy b2r_out/files_table.txt)
Size = last `HTTP 200 bytes` line of `download_log.txt` for every year 2007-2026 (20 of 20 equal). 2004-2006 has no log line (merged locally), so its completeness is NOT checked. `rows(csv)` = records from Python `csv.reader` (handles newlines inside quotes); `rows(wc)` = raw newline count minus 1 header line; they differ only by files with embedded newlines. Dates are the raw min/max of `ENTRYDATE` (placeholders included; see Decisions).

| file | bytes | in log | sha256 | rows(csv) | raw newlines | ENTRYDATE min | ENTRYDATE max | rows with year<1998 |
|---|---|---|---|---|---|---|---|---|
| energuide_2004-2006.csv | 19043811 | n/a (no log line) | 88043946445f8e1197fa0aa5a76cfa9f7c9f2f8948eb9f6f1a3fc705505ca6d3 | 14980 | 14981 | 2000-01-01 | 2011-06-01 | 0 |
| energuide_2007.csv | 124462699 | yes, equal | 7a8357379396fd10ece55a9e1c1f3fe537a76db5c37a26ef0e7a0c6d884d45e6 | 80242 | 80243 | 1980-01-01 | 2011-09-01 | 208 |
| energuide_2008.csv | 397128098 | yes, equal | 552646985891131642872aa99f254939c2a6ed7272688fa5acee135451286bff | 244179 | 244180 | 1970-01-01 | 2016-09-01 | 1 |
| energuide_2009.csv | 777675705 | yes, equal | 3930176cc9fc56f02555cdbe88cd7a5370099ce58873b727d9e6d2614b969565 | 462984 | 462985 | 0002-02-01 | 2011-07-01 | 7 |
| energuide_2010.csv | 738716104 | yes, equal | 98ea0ac62a54016f71e2002671a4b72a650920e3e4845b4f1d870554ed689022 | 438809 | 438810 | 0026-01-01 | 2021-10-01 | 12 |
| energuide_2011.csv | 548702116 | yes, equal | e1c8354000e9ba8a89948ab90444bff769bff3d25b2e1e52958ba400be00c09a | 327057 | 327058 | 2005-06-01 | 2013-04-01 | 0 |
| energuide_2012.csv | 393885858 | yes, equal | a383e0a4d2be9f4d625d15eabcb0c4f44a678be31116d6af4d21468fa6c3f952 | 236880 | 236881 | 2001-06-01 | 2014-10-01 | 0 |
| energuide_2013.csv | 145196356 | yes, equal | 26635e97f01a4a7fd0d577a4bc1e04cb5081835b9e48a8c9fb16bdf8488aabce | 91790 | 91791 | 2007-02-01 | 2015-12-01 | 0 |
| energuide_2014.csv | 149539825 | yes, equal | 367bf4d5f97d48ae10087b67ef4d2538381ca45fb3295301585a67d111293860 | 96305 | 96306 | 2004-09-01 | 2017-04-01 | 0 |
| energuide_2015.csv | 142034262 | yes, equal | a597c13a6fc3cbd814af6465045f68e45f2dd9206cc8e5d9aa1b0252446e3204 | 86435 | 86436 | 2006-04-01 | 2017-09-01 | 0 |
| energuide_2016.csv | 183384650 | yes, equal | cd93c7181fe2d3daad7634af72a4b341d82f373bda106043bb4ca1c3ed298627 | 103379 | 103380 | 2000-08-01 | 2024-04-01 | 0 |
| energuide_2017.csv | 272508010 | yes, equal | 7b6213b5b7d390a368fada19b614ed9f693034a85b539bfabb6ac393aab487dd | 146972 | 146973 | 2010-11-01 | 2020-03-01 | 0 |
| energuide_2018.csv | 338784127 | yes, equal | fb542d4a8d9a2bf1c05c2d4a45908d27109bb3011194c315d7513fa25310afe0 | 174763 | 174764 | 1991-07-01 | 2024-02-01 | 1 |
| energuide_2019.csv | 357854357 | yes, equal | c8fd29052736738c184fa8bc3a8f0cc64bbe769bc9ba17707db001ee6c3eea98 | 181883 | 181884 | 1976-08-01 | 2020-10-01 | 2 |
| energuide_2020.csv | 294014981 | yes, equal | 6c6d74412c3e08b01f2190accd1112cfa74e3e0afe8edf5dbda209aab0b5acb9 | 145975 | 145976 | 2008-11-01 | 2024-08-01 | 0 |
| energuide_2021.csv | 375316911 | yes, equal | 5344e16404cd6f997a68f38551b8433f2cfeef69fb73636da4ef4544697878f9 | 175814 | 175815 | 2007-06-01 | 2024-06-01 | 0 |
| energuide_2022.csv | 740780824 | yes, equal | e0b1fd15d3633836506c49eee07af2f6d2a18852f2d2c405a0c9c49b7945f545 | 334760 | 334764 | 2002-06-01 | 2024-07-01 | 0 |
| energuide_2023.csv | 1043983484 | yes, equal | 9b27fb484c293144da749f6130dde58e5c3c26fc83e890a2867baeeb5bf69697 | 488291 | 488324 | 1998-08-01 | 2025-11-01 | 0 |
| energuide_2024.csv | 895131246 | yes, equal | 3a72c6f7c490e5873edc5260d55be7826bb8db1258d830af4aa26676a1acee86 | 404541 | 404667 | 2003-07-01 | 2026-06-01 | 0 |
| energuide_2025.csv | 534952049 | yes, equal | eea768f445b1d19ac15f9f7757bfe713953a53f85a5ce239e9fa358be2f3d23c | 230609 | 230733 | 2000-01-01 | 2026-06-01 | 0 |
| energuide_2026.csv | 174586231 | yes, equal | 6b7765428ccd4855e92c8807e0187e3b541be34bd576734108c7aa7b659f30ba | 75896 | 75919 | 2000-01-01 | 2026-06-01 | 0 |
| TOTAL | | | | 4542544 | 4542870 | | | 231 |

### Item 3. Distinct values, all 4,542,544 rows, top 30, raw strings (read with `keep_default_na=False`, so no text was silently turned into missing; `<EMPTY>` = empty field)

`AIRCONDTYPE`: 14 distinct values incl. empty; empty = 270608

| value | rows |
|---|---|
| Not installed | 1584267 |
| Conventional A/C | 1133595 |
| Central split system | 1066741 |
| Mini-split ductless | 283019 |
| <EMPTY> | 270608 |
| Ductless Mini- or Multi-split system | 83135 |
| Window A/C | 70255 |
| Central single package system | 25220 |
| A/C with economizer | 7771 |
| Conventional A/C: with vent. cooling | 6550 |
| Window A/C w/vent cooling | 4704 |
| Coils Only | 3616 |
| Compact Ducted Mini- or Multi-split system | 1662 |
| Window A/C w/ economizer | 1401 |

`HPSOURCE`: 6 distinct values incl. empty; empty = 28

| value | rows |
|---|---|
| N/A {no Heat Pump} | 3583264 |
| Air | 918942 |
| Ground | 32101 |
| Water | 8208 |
| <EMPTY> | 28 |
| 0 | 1 |

`CCASHP`: 5 distinct values incl. empty; empty = 2876033

| value | rows |
|---|---|
| <EMPTY> | 2876033 |
| F | 967567 |
| T | 339440 |
| f | 311034 |
| t | 48470 |

`FURNACEFUEL`: 9 distinct values incl. empty; empty = 0

| value | rows |
|---|---|
| Natural Gas | 2674929 |
| Electricity | 1346664 |
| Oil | 428640 |
| Propane | 55522 |
| Mixed Wood | 16847 |
| Mixed wood | 12087 |
| Hardwood | 5762 |
| Wood Pellets | 1859 |
| Softwood | 234 |

`FURNACETYPE`: 59 distinct values incl. empty; empty = 1

| value | rows |
|---|---|
| Condensing furnace | 1776121 |
| Baseboard/Hydronic/Plenum(duct) htrs. | 968810 |
| Furnace with continuous pilot | 441394 |
| Induced draft fan furnace | 297131 |
| Electric furnace | 210763 |
| Furnace with flame retention head | 200006 |
| Forced air furnace | 118765 |
| Boiler  with flame retention head | 84156 |
| Furnace with spark ignition | 47500 |
| Condensing boiler | 44176 |
| Condensing heater | 39193 |
| Furnace | 33695 |
| Boiler  with continuous pilot | 33424 |
| Mid-efficiency furnace (no dil. air) | 33115 |
| Electric boiler | 31768 |
| Furnace with flue vent damper | 28838 |
| Induced draft fan boiler | 18206 |
| Electric Boiler | 15675 |
| Conventional furnace | 15624 |
| Advanced airtight wood stove | 13701 |
| Heater w/ flame ret. head | 12107 |
| Mid-efficiency boiler  (no dil. air) | 10799 |
| Furnace with spark ignit.,vent dmpr | 9024 |
| Boiler | 8825 |
| Boiler  with spark ignition | 8640 |
| Boiler  with flue vent damper | 6073 |
| Boiler  with spark ignit.,vent dmpr | 6066 |
| Direct vent, non-condensing boiler | 3269 |
| Heater w/ Induced draft fan | 3190 |
| Direct vent, non-condensing furnace | 3174 |
| (another 29 values not shown) | 19316 |

`CLIENTPCODE` string length: length 0: 31 rows, length 3: 4542513 rows

### Item 2. EVALTYPE, D/E pairs, houses (read from `b2r_out/values_out.txt`, all 21 files, 4,542,544 rows)
- EVALTYPE rows: D 2,317,385; E 1,770,370; P 231,466; N 223,323 (sum = 4,542,544; no other value, no empty).
- Distinct EVALUATIONSID: 2,549,769 (no empty). No EVALUATIONSID has two rows of the same EVALTYPE (max 1). No fully duplicated row (all 10 columns) in the 21 files.
- EVALUATIONSID that have a D row or an E row: 2,318,289. Of these: both D and E 1,769,466; D only 547,919; E only 904.
- Distinct HOUSEID (non-empty): 2,359,827. 1,489 rows have an EMPTY HOUSEID (kept in row counts, excluded from every per-house step). Rows per HOUSEID: 1 row 482,881 houses; 2 rows 1,722,442; 3 rows 44,576; 4 rows 87,594; up to 14 rows.
- 11,300 of the 2,130,834 houses that have a D or E row show more than one FSA across their rows (side check, printed in the shell only, not saved in a file; reproducible: group D/E rows by HOUSEID, count distinct first 3 characters of CLIENTPCODE).

### Item 3 (continued). What the values look like (facts, read from the raw text)
- `HPSOURCE`: the "no heat pump" string is `N/A {no Heat Pump}` (3,583,264 rows), NOT the string `N/A`. A test "not empty and not `N/A`" therefore counts EVERY row as a heat pump (measured below: share 1.0 everywhere). Real heat-pump values are only `Air`, `Ground`, `Water`. One row has `0`, 28 rows are empty.
- `AIRCONDTYPE`: the "none" string is `Not installed` (1,584,267). The 270,608 empty rows are mostly P/N rows and old files (share empty per file: 2004-2006 0.86, 2007 0.19, 2013-14 0.32-0.37, 2019 onwards 0). Among D/E rows only about 0.2 % (D) and 0.0 % (E) are empty. Window A/C types (`Window A/C`, `Window A/C w/vent cooling`, `Window A/C w/ economizer`) are present, although the dictionary describes the column as central A/C.
- `CCASHP`: values are `T`, `t`, `F`, `f` and empty. There is NO `1` or `0` in the 21 files, although the dictionary says "1 = yes, 0 = no"; a test `CCASHP = 1` would give zero everywhere. Empty in 2,876,033 rows: empty for every row of files 2004-2006 through 2017 (share 1.000), 0.999 in 2018, 0.994 in 2019, 0.948 in 2020, 0.293 in 2021, 0.002 in 2022, and 0.000 in 2023-2026. `T`/`t` occurs with `HPSOURCE` = Air (387,909 rows) and in one row with `N/A {no Heat Pump}`.
- `FURNACEFUEL`: 9 values, no empty; `Mixed Wood` and `Mixed wood` are two spellings of one value. `FURNACETYPE`: 58 values plus 1 empty row (top 30 below).
- `CLIENTPCODE`: 4,542,513 rows have length 3 and pattern letter-digit-letter (already an FSA; no lower-case problem); 31 rows are empty. First letters: L 857,357; N 476,626; V 443,217; J 439,605; T 362,238; G 342,599; M 307,354; K 285,880; B 279,759; E 217,191; H 157,435; S 133,078; P 75,665; R 75,379; C 44,491; A 31,935; Y 8,997; X 3,707 (all provinces).

### Item 4. FSAs H and M (basis: all rows of any EVALTYPE and any date, with non-empty HOUSEID and CLIENTPCODE; 1,520 rows dropped; read from `b2r_out/stage3_out.txt`)
| group | distinct FSAs | houses per FSA min / median / max | FSAs with >= 30 houses | distinct houses |
|---|---|---|---|---|
| H | 113 | 6 / 616 / 2,651 | 111 | 85,625 |
| M | 98 | 5 / 1,353 / 7,715 | 91 | 151,603 |
| H1 | 20 | 183 / 715 / 1,431 | 20 | |
| H2 | 19 | 15 / 513 / 822 | 18 | |
| H3 | 18 | 6 / 292.5 / 908 | 17 | |
| H4 | 17 | 33 / 586 / 944 | 17 | |
| H7 | 19 | 217 / 1,317 / 2,651 | 19 | |
| H8 | 7 | 309 / 762 / 1,272 | 7 | |
| H9 | 13 | 201 / 1,042 / 2,474 | 13 | |

No FSA starts with H0, H5 or H6 in these files (H1..H4 and H7..H9 add up to 113 FSAs).

### Item 5. Per-FSA shares (file `_5J_data\energuide_fsa_shares_2022.csv`, sha256 `0fe77a48223c8512600273d89414b41c1fa8d39063f9eedcf511a201d417bc88`, 204 rows = 200 FSAs + 4 pooled rows; written by `b2r_stage3_fsa.py`)
Selection, counts read from `stage3_out.txt`: D or E rows with non-empty HOUSEID and CLIENTPCODE, all provinces: 4,086,266. Dropped ENTRYDATE before 1998-01-01 (placeholder dates): 224. Dropped ENTRYDATE after 2022-12-31: 1,038,413. Remaining 3,047,629 rows. Per house the LATEST row was chosen over all of the house's rows (ties: E before D, then highest EVALUATIONSID): 1,624,221 houses. THEN only houses whose chosen row has an FSA starting with H or M were kept: 183,720 houses (H 56,814; M 126,906). 457 of them had two rows with the same date and D/E type (different EVALUATIONSID) and the highest EVALUATIONSID was taken. Kept rows: 76.1 % E, 23.9 % D; ENTRYDATE min 2001-01, median 2015-01, max 2022-12. FSAs with at least one kept house: 211; with >= 30 kept houses (rule applied to kept houses, not to item 4's count): 200 (H 109, M 91). By item 4's count the number of FSAs with >= 30 houses is 202.
Independent re-derivation `b2r_check_item5.py` (plain loop, 3,000 random kept houses): 0 disagreements on the FSA of the chosen row. (The first version of stage 3 filtered to H/M BEFORE choosing the latest row and gave 3 of 3,000 disagreements; fixed, everything re-run, numbers above are from the fixed version.)
Definitions in the file: `hp` = HPSOURCE in {Air, Ground, Water}; `hp_taskdef` = HPSOURCE not empty and not exactly `N/A` (the wording in the task, wrong for this data, kept only so nobody uses it); CCASHP share = T or t, given as share of all houses AND as share of houses whose CCASHP is not empty (`n_ccashp_known`); `ac` = AIRCONDTYPE not empty and not `Not installed` (includes window units), and `ac_excl_window` = same without the three window values; empty-AIRCONDTYPE houses count as "no A/C" in the shares, `n_ac_known` says how many are not empty. Fuel counts are per raw FURNACEFUEL value (9 columns; `Mixed_Wood` and `Mixed_wood` kept separate).

Pooled rows (all kept H houses, all kept M houses; the `>= 30` rows use only FSAs with >= 30 houses):

| pool | n houses | share E rows | share heat pump (Air/Ground/Water) | share by task wording | n CCASHP known | CCASHP T (of all) | CCASHP T (of known) | n AC known | A/C any | A/C no window |
|---|---|---|---|---|---|---|---|---|---|---|
| ALL_H | 56,814 | 0.562 | 0.587 | 1.000 | 22,932 | 0.090 | 0.222 | 56,436 | 0.739 | 0.714 |
| ALL_M | 126,906 | 0.849 | 0.012 | 1.000 | 14,720 | 0.004 | 0.032 | 126,883 | 0.868 | 0.842 |
| H, FSAs >= 30 | 56,763 | 0.562 | 0.587 | 1.000 | 22,912 | 0.090 | 0.222 | 56,386 | 0.739 | 0.714 |
| M, FSAs >= 30 | 126,850 | 0.850 | 0.012 | 1.000 | 14,716 | 0.004 | 0.032 | 126,827 | 0.868 | 0.842 |

Furnace fuel, ALL_H: Electricity 44,417; Natural Gas 5,047; Oil 7,257; Propane 88; Hardwood 2; Mixed Wood 3. ALL_M: Natural Gas 124,664; Electricity 1,254; Oil 967; Propane 17; Mixed wood 2; Hardwood 1; Wood Pellets 1.
Across the 200 FSAs the house count per FSA is min 37, median 615.5, max 6,128 (read from the output file). Median ENTRYDATE of kept rows: H 2020-01, M 2011-09 (the two cities are measured in different years).

## Decisions (B2)
1. ENTRYDATE placeholders: raw minimum dates 0002-02-01, 0026-01-01, 0201, 1970-01-01, 1976, 1980-01-01 (208 rows, mostly in the 2007 file) and 1991 exist; 231 rows in all files have a year before 1998. Rule used: only ENTRYDATE from 1998-01-01 counts in item 5 (224 D/E rows dropped). The raw min/max in the item 1 table are NOT cleaned. The 1998 cut is my choice (3 rows in 1998-1999 kept); the manager may prefer 2000.
2. Heat pump = HPSOURCE in {Air, Ground, Water}. The task's "not empty and not N/A" was NOT used as primary because the "none" string is `N/A {no Heat Pump}`; both are in the output file.
3. CCASHP: T and t counted as yes (the dictionary's 1/0 does not occur). The field is empty for all rows before about 2020, so the share among ALL houses is a floor, and the share among KNOWN houses covers mostly houses evaluated 2020-2022. Both are given; neither is a stock estimate without that caveat.
4. A/C: `Not installed` = none; empty counted as none (0.2 % of D and about 0 % of E rows are empty, so it hardly matters for D/E); window units are counted as A/C in the main share and removed in `ac_excl_window`.
5. "Latest" chosen over all provinces first, filtered to H/M afterwards. The 30-house rule applied to the houses kept in item 5.
6. A house counts under the FSA of its chosen row; 11,300 houses show more than one FSA over their history.
7. The 2004-2006 file cannot be checked against the log (no log line); it was analysed as it is (14,980 rows, 19,043,811 bytes).

## Next (B2)
Manager: decide (a) 1998 versus 2000 cut for placeholder dates, (b) whether EnerGuide shares can be used at all given the selection problem in the list below, (c) whether to hand the H/M FSA shares to the design doc. B2 has nothing running.

## WHAT I DID NOT VERIFY (B2)
- That the 2004-2006 file is complete: there is no download-log line for it; I only know it parses (0 ragged records, 14,980 rows).
- That the value strings match the data dictionary: I did not reopen `nrcan_open_data_dictionary.xlsx`; the CCASHP "1/0" and HPSOURCE "N/A" wording come from B's notes above, and the data contradict them.
- That the "latest evaluation" is the current state of the house: D rows are BEFORE a retrofit, E rows AFTER; I did not check whether a heat pump in an E row came from the retrofit, and did not use the UGR columns or any pre/post comparison.
- That EnerGuide houses represent the housing stock. They are program clients (retrofit incentive and new-build labelling); the mix changes by file year and city (H median entry 2020 with 56 % E rows; M median 2011 with 85 % E rows), so H versus M shares are NOT comparable as "Montreal vs Toronto" without a program-history explanation. Not tested; only the counts above are measured.
- The 11,300 multi-FSA houses were counted in a shell session and not saved to a file.
- That ENTRYDATE is the evaluation date and not a data-entry date; the 208 rows of 1980-01-01 may be a placeholder or real; I did not inspect rows one by one.
- I did not read FURNACETYPE beyond the top 30 list, HPEquipType, HPCAP, the UGR columns, or any of the other 423 columns.
- Raw newline counts exceed csv record counts plus one in some files (e.g. 2023: 488,323 lines vs 488,291 records); I did not open a record to see what the extra line breaks are.
- No OpenUBEM process was touched; the design doc was not edited.
