# 5J campaign design, Spain + Italy (draft for the manager to freeze)

Written 2026-09-30 16:28 EDT by the campaign-design employee. State file: `../impl/2026-09-30_wp1_campaign_design.md`.
Everything below was produced on Speed by `sbatch` jobs (R = `/speed-scratch/o_iseri/5J/campaign_prep/`) and copied here.
Spain and Italy only. The UK waits (see Open items). No recommendation is made in this file.

## 1. Counts per country (from `campaign_runs_es.csv` and `campaign_runs_it.csv`)

3 climates per country, 40 buildings per country (10 SFH, 10 TH, 10 MFH, 10 AB), 60 households per country (40 dev, 10 val, 10 test).

| | Spain | Italy |
|---|---|---|
| SFH runs (10 buildings x 60 households x 3 climates) | 1,800 | 1,800 |
| TH runs (same) | 1,800 | 1,800 |
| MFH runs (every flat tested, P = 3): dev / val / test | 318 / 87 / 87 = 492 | 312 / 84 / 84 = 480 |
| AB runs: dev / val / test | 288 / 84 / 84 = 456 | 123 / 39 / 39 = 201 |
| main runs (replicate 0) | 4,548 | 4,281 |
| B0 (average household), 40 buildings x 3 climates | 120 | 120 |
| replicates (10 inputs x 10 repeats, climate 1 only) | 100 | 100 |
| total runs | 4,768 | 4,501 |
| per climate (replicate 0, B0 included) | 1,556 | 1,467 |

Both countries: 9,269 runs. Formula check (gate C5) printed observed = formula for all 16 class/pool cells per country.
One hand check: Spanish MFH building es_B21 (MFH.01, k = 2, 6 floors, 12 dwellings): dev ceil(40 x 3 / 12) = 10 runs, val ceil(10 x 3 / 12) = 3, test 3 = 16 runs per climate.
The O-3 draft said 200 replicate runs for all countries; the rule as written gives 100 per country (10 inputs x 10 repeats).

Replicate inputs (climate 1 only, 10 repeats each, `replicate` 1..10, run_id ends `_rep<n>`; the original run keeps replicate 0):
* Spain: SFH es_B01..es_B05 (first dev household, run 1 of the dev pool), MFH es_B21, es_B22, AB es_B31, es_B32, and es_B40 (the building with most dwellings, 77); run 1 of the dev pool.
* Italy: SFH it_B01..it_B05, MFH it_B21, it_B22, AB it_B31, it_B32, and it_B37 (most dwellings, 48; it_B38 has the same count, the lowest id was taken).
* Choice made where the task text allowed two readings: "the first 5 buildings by id" of the SFH/TH set are all SFH (B01..B05); the 5 MFH/AB buildings are the max-dwelling one plus the first 2 MFH and the first 2 AB by id.

## 2. Splits and md5

* Households: `split_draft` of `households.csv` as is (40 / 10 / 10 per country). Count by household size (size 1 / 2 / 3 / 4 / 5):
  * Spain dev 13 / 19 / 6 / 2 / 0; val 3 / 5 / 1 / 1 / 0; test 3 / 4 / 2 / 1 / 0.
  * Italy dev 14 / 14 / 7 / 4 / 1; val 3 / 4 / 2 / 1 / 0; test 4 / 4 / 1 / 1 / 0.
* Buildings (per country, `random.Random(7000 + c)`, c = 0 Spain, 1 Italy; one generator per country; classes in the order SFH, TH, MFH, AB; position 0 test, 1 val, rest dev; then one more test and one more val drawn from the dev buildings sorted by id): 30 dev / 5 val / 5 test in each country.
  * Spain: SFH 8/1/1, TH 6/2/2, MFH 8/1/1, AB 8/1/1 (dev/val/test).
  * Italy: SFH 8/1/1, TH 7/1/2, MFH 7/2/1, AB 8/1/1.
  * Every class is in every split in both countries.
* md5 (local copies, equal to the Speed copies):
  * `splits_households.csv` 797a90683e26c42ee90d6bcc02112132
  * `splits_buildings.csv` 7e3bf4edcd187f2b03ebb0f21e5c88d7
  * `campaign_runs_es.csv` b4d5b42eb6220b25daef7f2a7cff18d1 (NEW, distinct-flats repair, 2026-09-30 fix; old v1 table `campaign_runs_es.v1_2026-09-30.csv` 84218a416b241db55617c9533c85d4a8)
  * `campaign_runs_it.csv` e9ddcf105c2aca2958439e70cd8e3dfb (NEW; old v1 table `campaign_runs_it.v1_2026-09-30.csv` 7c517ba1f1f50cb82be4e33978f9b7bc)
  * `k_table_es_it.csv` e07bd57953019001b5aaadcb8f0eb211
  * `dwelling_count_it.csv` a3ebbdc0f4303132e42410abd1c7c4a0
  * input `households.csv` (es + it rows, as staged) e0a3a5e5c83fdca1552036e3f4aeaa2b. The splits were drawn from this version; if the parallel households task rewrites the file, re-check against this md5.

## 3. Placement rule

* Columns: `run_id, country, climate_id, building_id, class, k, n_floors, n_dwellings, pool, building_split, replicate, seed, placement`. `run_id` = `<cc>_<city>_<Bnn>_<pool>_<r>` (+ `_rep<n>`), for example `es_madrid_B21_dev_1`. `placement` = `dwelling:household;...`, dwelling 0..n-1 in the order of the builder (floor by floor), household = the 5-digit `hid`; B0 uses `<cc>_avg` in every slot (built by the households task, not checked here).
* Dwellings per building: SFH/TH one dwelling. MFH/AB: `k = max(1, round_half_up(n_Apartment / n_Storey))` from TABULA, n_dwellings = k x n_Storey (tool `k_from_tabula` of `5thJ_idf_mz.py`; Spain reproduces the re-pilot values).
* SFH/TH: every household of the country (all 60, all splits) one run on every SFH/TH building, placement `0:<hid>`; `pool` = the household's own split; `r` = its position in that pool (households.csv `draw_order`).
* MFH/AB (every flat tested, P = 3): for each building and pool: runs = ceil(|pool| x 3 / n_dwellings); the slots of the runs (run by run, dwelling 0..n-1) are filled with concatenated permutations of the pool, permutation m shuffled with `random.Random(100000*c + 1000*b + 10*pool_idx + m)` (b = building number, pool_idx 0 dev, 1 val, 2 test); `seed` lists the permutation seeds used. A run holds one pool only. If n_dwellings <= |pool| no household appears twice in a run: a clash at a slot is resolved by swapping with the nearest following slot that does not clash. Same placement in the 3 climates of a country (run_ids differ).
* Swap counts (INFO): 136 swaps in total (Spain 70 in 16 buildings, Italy 66 in 10 buildings; per-building list in `design_1404128.out`). DEVIATION from the ruling: in 49 of the 136 swaps no following slot fitted (the clash sat near the end of the last run of a pool), so the nearest PRECEDING slot that fits was used instead. It is counted per building in the log (`fallback_backward`), and every household keeps its number of appearances. Gate C7 confirms no household twice in any run where the rule applies (1,289 runs checked).
* DISTINCT-FLATS REPAIR (fix task 2026-09-30, `../impl/2026-09-30_wp1_campaign_design_fix.md`): the first version gave each household 3 placements per MFH/AB building but some landed twice on the same flat (217 building x household pairs in Spain, 172 in Italy). After the slots of one building and pool are filled, a deterministic repair runs: while a household h has fewer than min(3, n_dwellings) distinct flats, take its first repeated (run a, flat f) and scan runs b and slots g in order for another household h2 such that after swapping (a, f) with (b, g) h gains a distinct flat, h2 keeps at least min(3, n_dwellings) distinct flats, and (when n_dwellings <= pool size) no household appears twice in run a or run b; count the swaps; if none exists print `REPAIR_STUCK`. Repair is done once per building and pool and copied to the 3 climates. Result: 380 repair swaps (Spain 219, Italy 161 over buildings and pools), REPAIR_STUCK 0. Only placements changed: same runs, run_ids, seeds and other columns; every household keeps its slot count per building.
* Every household sits in at least min(3, n_dwellings) DISTINCT dwellings of every MFH/AB building in every climate (gate C1_distinct; the old C1 is kept as C1_slots and counts placements only).
* Italian dwelling counts (TABULA n_Apartment vs modelled k x n_Storey; the difference is recorded, not fixed):

| Code_Building | class | n_Storey | TABULA n_Apartment | k | modelled dwellings | difference |
|---|---|---|---|---|---|---|
| IT.MidClim.MFH.01 | MFH | 2 | 5 | 3 | 6 | +1 |
| IT.MidClim.MFH.02 | MFH | 2 | 16 | 8 | 16 | 0 |
| IT.MidClim.MFH.03 | MFH | 4 | 20 | 5 | 20 | 0 |
| IT.MidClim.MFH.04 | MFH | 3 | 12 | 4 | 12 | 0 |
| IT.MidClim.MFH.05 | MFH | 5 | 10 | 2 | 10 | 0 |
| IT.MidClim.MFH.06 | MFH | 3 | 12 | 4 | 12 | 0 |
| IT.MidClim.MFH.07 | MFH | 3 | 15 | 5 | 15 | 0 |
| IT.MidClim.MFH.08 | MFH | 3 | 13 | 4 | 12 | -1 |
| IT.MidClim.AB.01 | AB | 5 | 16 | 3 | 15 | -1 |
| IT.MidClim.AB.02 | AB | 4 | 40 | 10 | 40 | 0 |
| IT.MidClim.AB.03 | AB | 5 | 30 | 6 | 30 | 0 |
| IT.MidClim.AB.04 | AB | 4 | 24 | 6 | 24 | 0 |
| IT.MidClim.AB.05 | AB | 8 | 40 | 5 | 40 | 0 |
| IT.MidClim.AB.06 | AB | 6 | 48 | 8 | 48 | 0 |
| IT.MidClim.AB.07 | AB | 6 | 36 | 6 | 36 | 0 |
| IT.MidClim.AB.08 | AB | 7 | 31 | 4 | 28 | -3 |

  Full code strings end `.Gen.ReEx.001`. SFH and TH: k = 1, one dwelling (TABULA n_Apartment is 1 for every SFH/TH code). The Italian parameter file holds 42 codes: the 32 used (8 per class) plus 10 combined codes (`SFH-TH`, `MFH-AB`, one row each) that no building uses; the task text said 24.
  Spain (control, same rule): MFH.01 9 -> 12 (+3), MFH.02 8 -> 10 (+2), MFH.03 16 -> 16, MFH.04 12 -> 12, MFH.05 9 -> 8 (-1), MFH.06 15 -> 16 (+1), AB.01 7 -> 7, AB.02 14 -> 14, AB.03 10 -> 12 (+2), AB.04 18 -> 18, AB.05 14 -> 16 (+2), AB.06 78 -> 77 (-1).
* Gates on the written files (v1 tables: job 1404129, superseded). NEW tables, job 1404141: C1_slots, C1_distinct, C2..C7 all PASS in both countries; 8 of 8 seen-failing gates fired. `SUMMARY PASS=16 FAIL=0 NOT_EVALUABLE=0`, `EXIT_CODE 0`. The same gate C1_distinct run on the OLD tables (job 1404140) FAILED: Spain 217, Italy 172 (building, household) pairs below the bar. Position variety of the new tables (INFO, printed in `fix2_1404141.out`): distinct floors and end/middle flats per household per class.

## 4. Targets and outputs (from the design doc 2F / D2-7 / D2-8; not changed here)

* Targets per dwelling, hourly, one year (8,760 rows): heating (Zone Ideal Loads Supply Air Total Heating Energy), cooling (same, Cooling), equipment electricity (Electric Equipment Electricity Energy), total electricity = equipment + heating / 3.0 + cooling / 3.0 with COP 3.0 ASSUMED (manager, pending the author's numbers).
* The other extracted columns (sensible/latent split, zone-side loads, people heat, infiltration and window gains and losses, mean air and operative temperature, relative humidity, unmet hours) are as in `tools/speed/mzp_extract.py` (the widened output list of the D2-8 design).
* Cooling setpoint 26 C, heating 20 C; ideal loads without limit; People + appliances per household; fixed internal gain zeroed (D2-2, D2-7).

## 5. Extraction format and deletion rule

* One file per run, as `tools/speed/mzp_extract.py`: `<run_id>.csv.gz` (long format, 8,760 rows per dwelling, header lines start with `#`, COP 3.0 ASSUMED written in every header) and `<run_id>.dwellings.csv` (side table: household, floor, position, floor area, zones).
* The raw run folder is deleted only after that run's checks pass (EnergyPlus "Completed Successfully", 0 severe, 8,760 rows per target, annual = hourly sum, extracted files written with size and md5 recorded). A run that fails a check keeps its raw folder.

## 6. Arrays

* One array per country x climate: 6 arrays (Spain: Madrid, Valencia, Seville; Italy: Bologna, Turin, Milan), `-p ps -t 7-00:00:00 --exclude=antenna1 -c 1 --mem=4G`, EnergyPlus 23.1 as in `mzp_array.sh`. The 100 replicate runs of a country sit at the end of its climate-1 array.
* Block per task: equal estimated time, not equal run counts, because a run takes 4 s (SFH/TH) to 75 s (77 dwellings). Target about 2,400 s (40 min) of simulation plus extraction per task, which is about 220 runs on average (fewer for blocks that hold many MFH/AB runs). Estimated tasks per array: 7 for each Spanish climate (1,556 runs; Madrid 1,656 with replicates), 7 for Bologna (1,567 with replicates), 6 for Turin and Milan (1,467): 40 tasks in total. The block boundaries are to be computed by the Step 3 tool from the per-class seconds in section 7. Extraction time per run was not timed separately (the whole timing job took 203 s, 120 s of it the two simulations), so the block size is an estimate.
* Throttle: `%5` per array (6 arrays, at most 30 tasks = 30 CPUs at once). The CPU share itself is the author's O-5 number, not set here.

## 7. Timing and disk (job 1404133, real EnergyPlus; Spanish pilot households round robin, TIMING ONLY, not a design run)

* es_B40 (Spain, AB.06, 7 floors x k 11 = 77 dwellings/zones, Madrid 2010): 75 s, MaxRSS 266,208 kB, run folder 345,460 kB (`du -sk`), 0 Severe, Completed Successfully; extracted 31.4 MB.
* it_B37 (Italy, AB.06, 6 floors x k 8 = 48 zones, Bologna 2014): 45 s, MaxRSS 249,576 kB, run folder 214,604 kB, 0 Severe, Completed Successfully; extracted 19.5 MB.
* About 0.97 s and 0.94 s per zone; the re-pilot AB median is 1.06 s per zone (up to 18 zones), so time per zone is roughly linear.
* Re-pilot class medians used (Spanish, 36 runs): SFH 4 s / 12.4 MB raw / 0.44 MB extracted; TH 4 s / 12.4 MB / 0.44 MB; MFH 14 s / 58.1 MB / 5.2 MB; AB 19 s / 84.5 MB / 7.5 MB. For MFH/AB with more than 18 dwellings: per-zone values of that country's big run x dwellings (25 Spanish runs, 245 Italian runs). The MFH/AB medians come from buildings of up to 18 zones and are used for every smaller building too.
* Arithmetic (INFO): Spain 9.34 CPU-hours (0.31 h wall at 30 CPUs), 8.91 GB extracted; Italy 8.49 CPU-hours (0.28 h wall), 7.97 GB extracted; both 17.84 CPU-hours, 0.59 h wall at 30 CPUs (ideal packing, without queue wait, build and extraction time). Raw folders if none were deleted: Spain 130.7 GB, Italy 119.3 GB (not the plan: raw is deleted after each run's check).
* Peak disk = 30 x largest raw folder (353.8 MB) + all extracted (16.88 GB) = 27.49 GB.
* Disk line (raw `df -B1 /speed-scratch/o_iseri`, job 1404133): `filer-speed:/userdata/speed_scratch 133040906960896 86833891835904 46207015124992  66% /nfs/speed-scratch`.
  `PREFLIGHT_DISK free_bytes=46207015124992 used_5J=2691998502` (used_5J = `du -sb /speed-scratch/o_iseri/5J`, 9 s). The free number equals the independent `stat -f` reading; the parser refused three broken inputs (seen failing) and gave the same numbers on a wrapped two-line form.

## 8. Open items

* UK arrays wait on the author's UK household script `tools/5thJ_design_households_uk.py` and on the UKDS 5J project line; nothing UK was opened here.
* Lighting is not modelled (no Lights object exists); asked.
* COP 3.0 is ASSUMED; interior-wall R is ASSUMED (D2-8 design).
* TABULA n_Apartment vs modelled dwellings differ for some codes (table in section 3); recorded, not fixed.
* Madrid cooling per m2 is high in the re-pilot (ideal loads to 26 C, no shading, no night ventilation); a model limitation to check before the paper.
* B0 placement uses the household id `<cc>_avg`; the average households are built by the parallel households task and were not checked here.
* The Italian EPW of climate 1 (Bologna 2014, md5 9a5e25091e7a9585f662e1efdc113629) was used for the Italian timing run; Turin and Milan were not run.
