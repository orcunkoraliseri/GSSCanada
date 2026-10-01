# Step 2 — WP1: campaign design and pilot

### 5J occupancy-aware surrogate. Implementation specification.
#### Parent: `../5thJ_00_Occupancy_Surrogate_Pipeline.md` Step 2. Validation: `5thJ_02_campaignDesignPilot_val.md`

Written 2026-09-28. Every number marked DRAFT is replaced by a measured or chosen value before Step 3.
Facts about 4J tools come from `../Step1_docs/outputs_step1/wp0_inventory.md`; where this doc names a
tool detail before that inventory is read, it says `(check in inventory)`.

---

## STATUS

⬜ NOT STARTED. Step 1 done 2026-09-28 night (UK line still with the author). Needs the design points
in 2F settled (D2-1 needs the author) and O-5 (CPU share with 1J) agreed.

## AIM

Fix the campaign on paper (which climates, which building variants, which households, which outputs,
how many runs) and prove on 50 real runs that it works, how long a run takes and how much disk it needs.
The pilot is the only source for the campaign size (O-3).

## WHAT IS ALREADY DECIDED — DO NOT RELITIGATE

| Decision | Where |
|---|---|
| Frozen frame: building and weather fixed, only the household's occupancy varies inside a pair | Overview, key decisions |
| Same households on every building of a country (clean occupancy contrast) | Parent Step 2 |
| Targets: hourly heating, cooling, electricity per dwelling, one year | Overview, scope |
| Replicate runs set a truth noise floor (lesson 2) | Parent, lessons |
| Electricity schedules use secondary activity (lesson 13); clock rotated to midnight (lesson 1) | Parent, lessons |
| Campaign size set by the measured pilot, not by an estimate | Overview, key decisions |

## 2A. THE DESIGN

### Countries, climates, weather (DRAFT)
About three climates per country, picked from the EPW files that already exist (inventory item D),
spread across heating degree days. Weather = ERA5 actual year matching the diary year (Spain 2009 or
2010, UK 2014 or 2015, Italy 2013 or 2014; the year is the one 4J used, from the inventory).
Candidate list, to be confirmed against the inventory: Spain Madrid, Seville, Bilbao; UK London,
Manchester, Edinburgh; Italy Milan, Rome, Palermo. A climate without an existing EPW is dropped, not
built new in this step.

### Buildings (DRAFT: about 40 variants per country and climate)
* Base: the TABULA residential archetypes per country that the 4J builder already makes (inventory C).
  Keep dwelling classes apart (detached or terraced house, multi-family, apartment block) because only
  geometry-ordered effects survived in 4J (lesson 4).
* Variants: a Latin hypercube over the parameters the 4J builder takes as arguments (inventory C), for
  example wall and roof U-value scale, window share, air change rate, floor area, orientation. Ranges
  stay inside the TABULA ranges for that country and class. A parameter the builder hard-codes is not
  varied in 5J unless the change is one function argument; any such change is logged as a 5J patch that
  prints a line (lesson 6).
* Seed and the full variant table (`building_id`, class, every parameter) written to
  `outputs_step2/buildings.csv` with its md5.

### Households (DRAFT: about 60 per country)
* Drawn from the country's diary households with the survey weights, stratified by household size.
* Each household becomes one household-year of schedules through the 4J path (inventory B): presence,
  activity-driven equipment and lighting, hot water; day-to-year chaining as ruled in 4J.
* **The same 60 households are run on every building of their country.** Household table
  (`household_id`, size, the draw seed) in `outputs_step2/households.csv`; for the UK only the IDs and
  seeds are written by the assistant, the schedules are built by the batch job (UK rule).
* One extra "average schedule" per building (the mean over the 60 households, or the 4J standard
  schedule if it exists) for baseline B0.

### Run count (DRAFT)
3 countries × 3 climates × 40 buildings × 60 households = **21,600** paired annual runs, plus 360 average
runs (one per building), plus replicates: 20 inputs × 10 repeats = 200 runs. Total about 22,160.
Replaced by the pilot-based number in 2E.

### Outputs per run
* Hourly heating, cooling and electricity for the dwelling, from the meters the 4J builder requests
  (inventory C); if a needed meter is missing it is added as one `Output:Meter` line, logged.
* Check that heating and cooling are the energy the system delivers or uses (lesson 9: 2J once counted
  heat recovery as cooling); write down which meter is which.
* Annual sum = sum of the hourly values (within rounding) for every run.
* Extraction: each run's hourly series goes to one row group in a per-array parquet under
  `/speed-scratch/o_iseri/5J/campaign/extracted/`; the raw EnergyPlus output folder is deleted once the
  extraction is checked (lesson 11).

### Inputs recorded per run (the run manifest)
`run_id, country, climate, building_id, household_id, replicate, schedule_md5, idf_md5, epw_md5,
energyplus_version, clock_origin` (lesson 1). The cache key is the hash of all inputs (lesson 7).

## 2B. SPLITS (DRAFT; sealed at Step 3)

Per country: households 60 → 40 development, 10 validation, 10 test; buildings 40 → 30 development,
5 validation, 5 test (drawn per dwelling class so every class is in every split).
* test-new-households = test households on development buildings;
* test-new-buildings = development households on test buildings;
* test-new-country = one country left out entirely (three folds);
* runs that pair a test household with a test building are kept apart and reported as "both new".
Pairs for the occupancy effect are always two households on one building and one weather, both in the
same split.

## 2C. CLUSTER PLAN

* Partition `ps`, `-t 7-00:00:00`, `--exclude=antenna1`, one working directory per run (lesson 8), CPUs
  asked slightly under the agreed share (lesson 11).
* 🔴 **Disk.** `/speed-scratch/o_iseri` was at 9.3 T of 10 T on 2026-09-25 (1J record, not
  re-measured). The pilot measures raw and extracted size per run; the campaign plan must show
  (runs in flight × raw size) + (all runs × extracted size) below the free space read by a disk
  preflight job at submit time.
* **CPU share (O-5).** 1J holds up to 64 CPUs until its last task and scorers finish. 5J asks for a share
  only after `squeue` is read; the manager writes the number agreed in the Progress Log before the
  first 5J submission.

## 2D. PILOT (50 runs)

One country (Spain; not the UK, so the manager can read every file), one climate, 5 buildings (one per
class plus one extra), 10 households, of which 2 inputs are repeated 5 times.
Measured and written to `outputs_step2/pilot_report.md`:
* seconds per run (median, 90th percentile) and CPU per run;
* raw output size and extracted size per run;
* all 50 finished, "EnergyPlus Completed Successfully", 0 severe, 8,760 rows;
* outputs differ between households on the same building (lesson 6), per target;
* replicate spread per target (first look at the noise floor, lesson 2);
* annual sums equal hourly sums.

## 2E. CAMPAIGN SIZE (O-3 closes here)

From the pilot: total CPU-hours = runs × median seconds per run ÷ 3600; wall time at the agreed CPU share;
disk as in 2C. If the campaign does not finish by 11 Oct 2026 at the agreed share, cut in this order:
climates to 2 per country, then buildings to 30, then households to 50; never drop the replicates or
the average-schedule runs. The chosen size and its arithmetic go in the parent Progress Log.

## 2F. WHAT THE INVENTORY CHANGES IN THIS DRAFT (added 2026-09-28 night, from Step 1)

Source for every fact: `../Step1_docs/outputs_step1/wp0_inventory.md` (section and key in brackets).
Recommendations are the manager's; D2-1 changes the design and waits on the author.

* **D2-1 Climates (author).** Only three ERA5 actual-year files exist: Madrid 2009 and 2010, London 2014
  and 2015, Bologna 2013 and 2014 (D). The other six candidate cities in 2A have no file, so under the
  2A rule the design falls to **one climate per country**. Step 8 of 4J also holds TMYx typical years
  for Valencia, Birmingham and Torino (D, `step8_tmyx_epws`), but on a different basis (typical year,
  other station; 4J FINDING 120: the station alone moves heating by 5 to 11 %). Options: (a) make two more
  ERA5 files per country with the existing OpenUBEM ERA5 path (same diary year, same source; a small
  download job on the author's Copernicus account); (b) one city per country, the second ERA5 year as a
  weather variant; (c) add the TMYx cities as second climates. **Recommend (a)**; (b) is the fallback
  if the download is not possible within week 1.
  **Checked 2026-09-28 late night (manager, at the author's request, from the OpenUBEM
  `europeanLocations` docs):**
  * *Can (a) be done? Yes.* OpenUBEM `scripts/acquire_era5_eu_folds.py` (CDS download, one 0.25° grid
    point, 9 variables) and `scripts/convert_era5_eu_folds_to_epw.py` (pvlib, local standard time) take
    coordinates from `openubem/data/weather/weather_registry.json`, so any city works. The CDS key file
    `~/.cdsapirc` exists (Aug 25); `cdsapi`, `ecmwf.datastores`, `pvlib` 0.15.2, `xarray` import in `py`.
    ERA5 covers 1940 to now. Weather is not diary data, so the UK licence rule does not touch it.
  * *Three limits, so 5J needs its own copy of the two scripts (not an edit of the closed OpenUBEM
    project):* (1) the converter keys targets by country (`targets[fold]`), so a second city per
    country would overwrite the first; (2) elevation comes from a per-country table
    (`ELEVATIONS_M`, `convert_era5_eu_folds_to_epw.py:55`), not per city; (3) both scripts read only
    `RULED_NOT_PINNED` entries of the OpenUBEM registry and fetch two years. The 5J copy keeps its own
    registry (`_5J_data/surrogate/weather/weather_registry_5J.json`), fetches only the 4J year per
    country (Spain 2010, UK 2014, Italy 2014; inventory D `diary_year_weather_used_in_4J_step10`),
    and keeps the conversion code unchanged (copied, md5 of the source recorded).
  * *Time:* 13 downloads per city-year (12 months plus the boundary day), one CDS job at a time
    (concurrent jobs were rejected in OpenUBEM). Measured on the OpenUBEM files: Madrid about 6 min per
    file (Aug 26 07:26 to 08:04 for 7 files); Bologna 26 files over about 18 h (Aug 26 14:32 to Aug 27
    08:37, queue waits). So six city-years take between about 8 h and about 2 days. It is a local
    download, not compute; start it first, then build the IDF wrapper while it runs.
  * *Which cities.* The OpenUBEM weather research (`europeanLocations/DeepResearch/DR08_...md` §5)
    lists candidates per country: Spain Barcelona, Valencia, Seville; UK Birmingham, Manchester, Leeds;
    Italy Milan, Turin (Rome rejected: Zone D, outside `IT.MidClim`). The 4J buildings cover one TABULA
    region per country only (`ES.ME`, `GB.ENG`, `IT.MidClim`; OpenUBEM `tabula_archetypes_*.json`), so
    Edinburgh (Scotland), Rome and Palermo from the 2A draft list are **out of the building region and
    dropped**. 4J already scored 44 stations against TABULA's own monthly temperatures
    (`4J_docs_occ/Step8_docs/outputs_step8/weather_selection_report.json`, RMSE in K, lower = closer to
    the building data's climate). Madrid scores 3.57 (worst in Spain) and Bologna 2.82: the existing
    cities are poor fits, which is one more reason to add better-fitting ones.
  * **Recommendation (manager):** per country, the 4J best-fit station plus one large city with a
    different climate:
    Spain: **Valencia** (Viveros, 39.483 N, 0.383 W, 11 m; score 0.62, best; mild coast) and
    **Seville** (hot summer, the cooling end; DR08 candidate; not in the 4J score list, so its score is
    computed from its own ERA5 year with the same rule, and its coordinates and elevation are taken from
    the OneBuilding station record when the registry is written; fallback Barcelona El Prat, 41.293 N,
    2.070 E, 5 m, score 0.93).
    UK: **Birmingham** (AP, 52.454 N, 1.748 W, 100 m; score 0.53, best) and **Manchester** (AP,
    53.354 N, 2.275 W, 78 m; score 0.69; wetter north-west). England's spread is narrow anyway (heating
    days 179 London to 225 Manchester); Leeds Bradford (247 days, score 1.33) is the colder fallback.
    Italy: **Turin** (Venaria, 45.131 N, 7.618 E, 278 m; score 1.04, best; colder) and **Milan** (Linate,
    45.449 N, 9.278 E, 103 m; score 2.44; largest city in Zone E). All Italian choices sit in Zone E, so
    Italy has no hot-summer city by construction (the buildings do not allow one).
    Coordinates and elevations above are the OneBuilding EPW headers in
    `4J_docs_occ/Step8_docs/outputs_step8/weather/` and its `_cache/`; ERA5 uses the nearest 0.25°
    grid point, which the file header records.
  * *Still the author's:* (a) with these six cities, or (b) the fallback. Nothing downloaded yet.
  * **RULED 2026-09-29 (author, "lets go" in reply to "Waiting on you: yes to these six cities"):
    (a) with the six cities above.** Download order puts one new city per country first (Valencia,
    Birmingham, Turin, then Seville, Manchester, Milan), so a slow queue still leaves two climates per
    country early. Task: `impl/2026-09-29_wp1_weather_TASK.md`; state: `impl/2026-09-29_wp1_weather.md`.
* **D2-2 Building builder.** `4thJ_step8_idf.py` takes one dict made from a TABULA row, not one argument
  per parameter (C, `idf_builder_signature`). It is **heating only** (single setpoint 20 °C, no
  cooling), writes **no `Output:Meter`**, and hard-codes infiltration (0.5 ach), north axis (0) and one
  thermal zone (C, `hard_coded_parameters`, `step8_outputs_requested`). 5J needs cooling and
  electricity (Overview, targets). Recommend: a 5J wrapper that calls `derive` and `build_idf` and then
  applies printed patches (lesson 6, class 58): dual heating and cooling setpoints (cooling setpoint from
  a cited standard, chosen and sourced in this step), meters for heating, cooling and electricity,
  infiltration and north axis as variant values, and the Step 9 electricity and hot-water schedules.
  Each patch prints its own line and the pilot checks every line is present.
  **Settled 2026-09-29 (manager; 4J code map: `4thJ_step9_trigger.py:1063-1124`,
  `4thJ_step8_scenario.py:14-53`, `4thJ_step7_schedules.py:398-434`, `4thJ_step8_idf.py:483,596-634`):**
  cooling setpoint **26 °C** with heating 20 °C (`ThermostatSetpoint:DualSetpoint`; EN 16798-1:2019
  Annex B residential default, category II; the author confirms the table from their copy at Step 8);
  the ideal-loads object already has no heating or cooling limit, so only the thermostat changes.
  Targets read as hourly output variables `Zone Ideal Loads Supply Air Total Heating Energy` and
  `... Cooling Energy` (no outdoor air, no heat recovery in the box, so supply = zone load; lesson 9)
  and the hourly meter `InteriorEquipment:Electricity`. Infiltration and north axis become wrapper
  arguments (defaults 0.5 ach and 0, the 4J values).
* **D2-7 Occupant gains (new, manager, settled 2026-09-29).** In 4J the box carried occupancy only as
  one `OtherEquipment` gain held at a fixed yearly mean of 3.0 W/m² (only the timing moved), and Step 10
  had no appliances, lighting or hot water. That is why the 4J heating effect was tiny (lesson 3). 5J
  lets the **household set the level as well as the timing**: (i) a `People` object as in 4J Step 7
  (head-count = household size, presence-fraction schedule, the Step 7 activity level and radiant
  fraction reused, not new numbers); (ii) the Step 9 `ElectricEquipment` appliance object (household peak
  W × fraction schedule; its heat enters the zone, radiant 1.0 as in 4J, logged); (iii) the fixed
  `E_PHI_INT` gain set to zero, so nothing is counted twice. Not modelled, and said so in the paper:
  lighting (no 4J source) and hot-water energy (the 4J `WaterUse:Equipment` has no plant loop in the box;
  hot-water litres stay as a side output only). Electricity target = appliance electricity.
* **D2-3 EnergyPlus version.** Step 8 IDFs declare 24.2; the only installs found are 23.1.0-87ed9199d4
  (local, and two on Speed scratch) (E, F). Recommend 23.1 on Speed (the Step 10 install under
  `4J_step10_nocore/opt/`), `Version, 23.1;` written by the wrapper, and the pilot's 0-severe check as
  the test that no object broke.
* **D2-4 Secondary activity.** The 4J appliance trigger ignores secondary activity by policy (B,
  `secondary_activity_in_electricity_schedules`; 29.8 % of episodes carry one). 5J adds it (lesson 13)
  as a logged change to its own copy of the trigger; the pilot reports electricity with and without it
  on one building.
  **D2-4 detail settled 2026-09-29 (manager):** `act2` is a 2-digit code while the appliance map keys are
  3-digit, so the literal map matches nothing (employee showed the run byte-equal to no-act2). Rule: a
  2-digit `act2` takes the profile shared by all its 3-digit children (prefixes 03, 31, 32, 82 map); an
  **ambiguous prefix (33, care of textiles: laundry, ironing) takes the profile of the child with the most
  primary-episode minutes in that country**, because lesson 13 says laundry lives in the secondary
  activity and leaving 33 unmapped would drop it. To implement in the trigger copy as `--act2-match
  prefix2_major`, with the chosen child printed per country. First test (prefix2, 33 unmapped): annual
  appliance electricity up about 5 % (household 00035: 2,267 to 2,388 kWh).
* **D2-5 Which episode files.** The Spain and Italy episode files on Speed are newer and larger than the
  local ones that match the 4J parse reports (A, `finding_local_vs_speed_parquet_size`). Recommend: one
  `sbatch` job prints row counts and md5 of the Speed copies (Spain, Italy only); 5J uses the local
  copies, copied to `/speed-scratch/o_iseri/5J/inputs/` with md5 checked on both sides.
* **D2-6 Weather on Speed.** Where 4J Step 10 read EPWs on Speed was not found (D, `speed_epw`). 5J
  copies its own EPWs to `/speed-scratch/o_iseri/5J/weather/` and records md5 on both sides.
* **Run time.** The 4J single-zone box took about 2 s of core time per annual run (C/E,
  `time_per_annual_run`: 510 runs, 14 workers, 71.9 s wall), against about 53 to 79 s for a multi-zone
  OpenUBEM cell. If the 5J box stays near that after the D2-2 patches, the whole DRAFT campaign is
  about 12 CPU-hours: **CPU is not the limit, disk and design are.** The pilot measures it.
* **CPU share (O-5), first reading.** `squeue` on 2026-09-28 night: 1J runs one 5-CPU task and has two
  1-CPU scorers waiting on it. A 50-run pilot needs a few CPUs; recommend `--cpus-per-task=8` for the
  pilot, recorded in the parent Progress Log before submission.
* 🔴 `4thJ_step10_weather_year.py` hard-codes the raw UK diary path (D, `epw_tools_note`): never run by
  an AI tool; if 5J needs its logic, the manager writes a copy with the UK path removed.

## OUTPUTS

| File | What |
|---|---|
| `outputs_step2/campaign_design.md` | Final design with every DRAFT replaced |
| `outputs_step2/buildings.csv`, `households.csv`, `climates.csv` | The design tables, md5 in the design doc |
| `outputs_step2/pilot_report.md` | Pilot measurements |
| `impl/<date>_wp1_pilot.md` | Ledger of pilot jobs and state |

## PROGRESS LOG (append-only)
- 2026-09-28 (manager): doc written as a plan. Next: Step 1 inventory, then this design.
- 2026-09-28 night (manager): Step 1 inventory read; section 2F added (six design points D2-1 to D2-6,
  run time, first CPU reading). D2-1 (climates) waits on the author. Next: D2-1 answer, then the design
  tables and the pilot tools (employee).
- 2026-09-28 late night (manager): D2-1 checked against the OpenUBEM `europeanLocations` docs and the
  4J station scores (2F, "Checked"). The ERA5 path works for any city with a small 5J copy of two
  scripts; six city-years take about 8 h to 2 days of download. Recommended: Valencia + Seville, Birmingham
  + Manchester, Turin + Milan. Edinburgh, Rome, Palermo dropped (outside the building regions). Next:
  author says yes to the six cities; then the download starts first.
- 2026-09-30 16:38 EDT (manager): Step 2 CLOSED for Spain + Italy. Multi-zone builder (D2-8), 36-run multi-zone
  re-pilot, households on Speed (Spain reproduced, Italy 60, average households), campaign design with the
  distinct-flat fix, all verified by the manager's own Speed jobs. Frozen design
  `outputs_step2/campaign_design.md` (md5 2594867b0fe6cf24191c00e0c83d91a7): Spain 4,768 + Italy 4,501 runs, about
  18 CPU-hours. UK waits on the author's UK household script. Next: Step 3.
