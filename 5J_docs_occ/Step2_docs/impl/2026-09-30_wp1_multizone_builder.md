# WP1 multi-zone builder (D2-8) — implementation state
Task doc:   Step2_docs/impl/2026-09-30_wp1_multizone_builder_TASK.md (design: 2026-09-30_d2-8_multizone_design.md; includes AMENDMENT ~17:00 wide outputs)
Status:     DONE (2026-09-30 ~16:00 EDT); manager verifies; author answers A and B; then pilot rebuild
Files made: tools/5thJ_idf_mz.py; tools/speed/mz_partA_tabula.py, mz_partC_build.py (+.sbatch), mz_partC_array.sh, mz_partC_summary.py (+.sbatch). Speed root R=/speed-scratch/o_iseri/5J/multizone/

## Ledger
- 1404053 · Part A TABULA dwelling-count search (R/logs/partA_1404053.out) · COMPLETED 0:0 29 s · csv R/tabula/dwelling_count_es.csv, copied to outputs_step2/dwelling_count_es.csv
- 1404057 · Part C build job, first try · FAILED 1:0 · 5thJ_idf.build md5s a hard-coded Windows path (FileNotFoundError 'C:\Users\...\4J_docs_occ\tools/4thJ_step8_idf.py') · superseded by 1404059. (No earlier job used the old output list; the amendment arrived before any run job.)
- 1404059 · Part C build: IDFs, area gates, seen-failing 1+2, manifest (R/logs/build_1404059.out) · COMPLETED 0:0 · ALL_AREA_AND_PATCH_GATES PASS
- 1404060 · Part C EnergyPlus array, 16 tasks (5 mz, 5 collapse, 5 single, 1 collapse with U_wall x1.10) · COMPLETED all 16, exit 0:0 · logs R/logs/run_1404060_<n>.out, per-run status R/runs/<run>/status.txt
- 1404061 · Part C summary · COMPLETED · R/logs/summary_1404061.out

## Verified
- Part A: both xlsx md5 match expected (log lines 2-3). ES csv 24 rows. Column FOUND: `n_Apartment` ("number of apartments") in tabula-calculator.xlsx sheet Calc.Set.Building, all 24 codes, 3 identical rows per code. Values: SFH/TH = 1; MFH.01..06 = 9,8,16,12,9,15; AB.01..06 = 7,14,10,18,14,78. Other keyword hits are not per-building dwelling counts (Tab.BuildingStock n_Apartment_Total = stock totals, no Code_Building column; EC_unit; Utilisation).
- Build job 1404059 log, per building (mz): PATCH lines mz_geometry, mz_areas, mz_windows, mz_mass, mz_pairs, mz_people, mz_appliances, mz_outputs ALL PRESENT (8 lines x 5 buildings mz + same for 5 collapse + 1 uwall collapse); PATCHCHECK PASS x5.
- Area gates (rel tolerance 1e-4, parsed from the SAVED IDF text, not from builder variables): all 7 PASS for all 5 buildings; worst rel 5.5e-05 (glazing es_B37); zone floor sum es_B21 555.4993 vs A_C_Ref 555.5000. Layouts: B07 SFH 2 floors 2 zones; B16 TH 2 floors 2 zones; B21 MFH 6 floors k=2 12 zones 32 interzone surfaces (16 pairs); B33 AB 7 floors k=2 14 zones 38 surfaces (19 pairs); B37 AB 9 floors k=2 18 zones 50 surfaces (25 pairs).
- Seen failing (scratch copies on es_B21; files R/seenfail/B21_drop_floor.idf, B21_drop_partner.idf): (1) ground floor of Z_F00_D00 dropped -> FAIL zone_floor_area_sum (509.2080 vs 555.5000), also FAIL ground and FAIL capacity; (2) partner PW_Z_F00_D01_W deleted -> FAIL interzone_surfaces_paired ("PW_Z_F00_D00_E: partner PW_Z_F00_D01_W missing"), also FAIL capacity; control (unmodified) 7 PASS. (3) carry-over with U_wall x1.10 (u_wall 2.6324 -> 2.8957): run in array, result in summary.
- Lighting: `grep -c -i lights` on ONE pilot in.idf (es_B07__es_00050) = 0; 5thJ_idf.py has no lighting text. Decision: no Lights object; `Lights Electricity Energy` and `InteriorLights:Electricity` are requested and will report nothing (INFO in the presence gate).
- Households (read once from each household's first pilot folder): 02822 2 members 1804.97 W; 04065 2, 2228.65; 00739 2, 2342.95; 00494 2, 2243.83; 03043 1, 3735.38; 02288 2, 2148.62; 02419 4, 1770.00; 01855 3, 2440.63; 00050 1, 6018.87; 02065 1, 1882.57. First household (dwelling 0, also the collapse and single-zone household) = 02822.

## Decisions
- k = floor(n_Apartment / n_Storey + 0.5): B21 MFH.01 9/6 = 1.5 -> k=2 (12 dwellings, not 9: rounding adds 3), B33 14/7 -> 2, B37 18/9 -> 2. Not test-only values. SFH/TH k=1.
- Mass: rho computed per building from sum of exterior opaque (walls net of windows, roof, ground) + interior surfaces with each interzone PAIR counted once; every interior surface (both sides) carries that same areal capacity. Consequence: E+ sees each side's full slab, so effective model capacity is above c_m x A_C_Ref by the interior share; the gate checks the design rule (pairs once), as the task says.
- Interior resistive layer R (0.35 floor / 0.50 party) taken as the NoMass layer only (+ capacitive layer R 0.01 + films). Stated in the IDF header.
- Window clamp: same min(frac, 0.94) as 4J (never reached here: max fraction 0.447).
- Gate input for "zone floor area sum" = surfaces of type Floor (ground floor + interzone floor of every zone); in collapse mode the single zone has plate area only, so that gate FAILS for collapse by construction (printed as es_B##_collapse lines, INFO only, not a task gate).
- Outputs: amended list (21 variables, 5 meters, hourly, * key) + `Output:VariableDictionary, Regular;` (added so an .rdd exists for the presence gate) + AllSummary. Dropped vs 4J box: the monthly Zone Ideal Loads Zone Total Heating table (the amended list replaces it).
- 5thJ_idf.build hard-codes TOOLS_4J (Windows path); runner overrides `j5.TOOLS_4J` at run time to R/repo/4J_docs_occ/tools. 5thJ_idf.py itself NOT edited.
- buildings.csv staged to Speed was first copied whole (40 es + 40 it + 40 uk building-attribute rows, no diaries); I overwrote the Speed copy with the es rows only (R/repo/buildings.csv, 40 rows) before job 1404059. The first copy existed on Speed for about 5 minutes (job 1404057 did not read it past the es rows). No UK diary/episode/manifest/IDF was opened.
- Sequencing: array and summary submitted together (dependency afterany) to save poll checks.

## Next
Manager: read R/logs/summary_1404061.out (run table, carry-over lines, SEENFAIL3, sanity INFO, output-presence lines) and copy into Report. If still running, job IDs 1404060 (array), 1404061 (summary).

## WHAT I DID NOT VERIFY
- EnergyPlus results of any run (none read yet at the time of this entry).
- That TABULA `Calc.Set.Building` n_Apartment is a per-building published value rather than a calculator default (only read the numbers).
- That E+ treats pair capacity the way the Decisions note describes (not tested).
- No local syntax check was possible (no local python); the code ran on Speed.

## RESULTS (read from R/logs/summary_1404061.out)
- All 16 runs: rc 0, Completed Successfully, 0 Severe, 8,760 hourly rows. Seconds: mz runs B07 9, B16 4, B21 13, B33 15, B37 19 (median 13, max 19); collapse and single-zone 2 s each. Zones: B07 2, B16 2, B21 12, B33 14, B37 18. MaxRSS about 215-234 MB.
- Disk per run folder (du -sk) / eso bytes: B07 mz 12,396 kB / 6.06 MB; B16 mz 12,472 / 6.09; B21 mz 57,816 / 32.99; B33 mz 66,848 / 38.34; B37 mz 84,460 / 48.82 MB; collapse about 7,950 kB; single about 3,310 kB. (21 variables + 5 meters at hourly, + .csv from readvars about 0.7 x eso.)
- Carry-over collapse vs single-zone (heating, cooling): all 10 PASS, relative difference <= 2e-15 (bit-level identical). Example B21 heating 62,435.539 kWh both; cooling 23,785.247 both.
- Seen failing 3 (B21 collapse, U_wall x1.10): FAIL heating rel 0.0430, FAIL cooling rel 0.0380 (vs single 62,435.539 / 23,785.247; scaled collapse 65,118.368 / 24,688.791).
- Sanity (INFO, kWh/m2 of zone floor area, heating/cooling): B07 SFH ground 55.1/64.5, top 74.8/96.5; B16 TH ground 76.5/38.6, top 130.7/82.6; B21 MFH ground 91.7/42.9, middle 94.4/83.8, top 197.6/127.4; B33 AB ground 88.6/23.0, middle 88.2/54.9, top 188.4/96.7; B37 AB ground 75.3/7.0, middle 72.0/25.3, top 135.5/54.1. Whole building mz/single: heating 1.04, 1.10, 0.99, 1.01, 0.96; cooling 1.22, 1.25, 1.97, 2.00, 1.96 (single zone = 2 people for a whole 555-1942 m2 building, mz = 24-38 people, so not like for like).
- Note: the single-zone wrapper outputs no Electric Equipment variable (meter only), so its elec column in the table is 0; collapse elec = 1967.758 kWh = B07 mz elec (same household, share split).
- Output-presence gate on es_B21__mz: PASS for 20 of 21 variables and 4 of 5 meters (all in .eso dictionary and .rdd); INFO only for `Lights Electricity Energy` and `InteriorLights:Electricity` (no Lights object).

## Verified (manager) 2026-09-30 15:58 EDT: builder ACCEPTED
Re-derived on Speed (login node, single files): `PATCH mz_*` lines in `logs/build_1404059.out` = 88 = 8 names x 11
builds, each name 11 times. es_B21 multi-zone: 12 `Zone,` objects in model.idf; EnergyPlus Total Building Area
555.50 = A_C_Ref 555.5; es_B37 1942.38 = A_C_Ref. Carry-over: es_B21 collapse and single-zone both heating 224.77 GJ
(= 62,436 kWh, the employee's 62,435.539) and cooling 85.63 GJ in eplustbl.csv. Run seconds es_B21 mz 13
(status.txt), collapse 2, single 2; MaxRSS 230 MB.
**Manager rulings:**
* **k (dwellings per floor) = TABULA `n_Apartment` / n_Storey, rounded half up, at least 1**; total dwellings may
  differ from TABULA's count (MFH.01 12 vs 9, AB.06 77 vs 78); the difference is written per building in the
  design table. Source column accepted as TABULA's building data (Calc.Set.Building); whether it is a published or
  default value is recorded as NOT VERIFIED.
* **Mass fix (additive, next task):** EnergyPlus gives BOTH sides of an interzone pair a full construction, so the
  capacity budget must count every interior surface EnergyPlus sees (each side), not each pair once; otherwise the
  modelled capacity exceeds c_m x A_C_Ref. Collapse runs are unaffected (no interior surfaces).
* **Lighting:** no Lights object anywhere in the 5J/4J path (D2-7 said lighting not modelled). The author asked for
  lighting outputs: author asked whether to add a lighting model.
* Cooling in multi-dwelling buildings about 2x the single box: expected (24-38 people vs 2). Top floor heating about
  2x the middle floors: expected (roof).
