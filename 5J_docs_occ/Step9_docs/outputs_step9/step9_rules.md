# 5J Step 9 rules: Model A (Spain + Italy, Madrid Berruguete + Bologna Galvani 2), written BEFORE any campaign run

Status: **SEALED 2026-10-01 20:17 EDT** (manager, from `date`; drafted 18:38). md5 of this file and of every R1 / R2 list and code
file: `/speed-scratch/o_iseri/5J/modelA/step9_rules.md5` (seal job; read its log before trusting the seal). Sealing = a Speed job writes the md5 of this file and of
every list named in R1 into `/speed-scratch/o_iseri/5J/modelA/step9_rules.md5` before the first campaign run. Sealing waits on the manager's read of the final-base checks (task 9k: CLOSED 19:35) and the swap of the 9m runner. The OpenUBEM flat-count ruling is
handled by R1's 10-04 rules (Madrid sealed now; Bologna lists added by a dated amendment before any Bologna run). After sealing, any change is a dated AMENDMENT at the end, never an edit, and says whether any run or training
result had been seen. Design source: `Step9_docs/5thJ_09_modelA.md` (9A-9G, D9-1..D9-6). Frozen scorer and gates: Step 4
(`/speed-scratch/o_iseri/5J/gates_frozen.md5`), no threshold change.

Spain and Italy only. 🔴 No UK file, path or argument (UKDS EUL v16 cl. 5); no folder-wide search, no wildcard that could match a
UK file; never list `EU-11/` itself.

## R1. Data lists (sealed with this file)
* **Base geometry:** OpenUBEM windowed IDFs `EU-11/ES-MAD-BERRUGUETE_win_2026-10-03/idfs/` and
  `EU-11/IT-BOL-GALVANI2_win_2026-10-03/idfs/` (Speed copies `/speed-scratch/o_iseri/fleets/EU11_<D>_win_2026-10-03/idfs`),
  1,172 / 1,179 IDFs; `windows.csv` md5 a3edc82e575be1cbd23e54bf1b3f5c61 (ES), 232134d1f406790bea33d16524facac1 (IT). Tools
  read the base through `MODELA_VINTAGE=win_2026-10-03`. Model A buildings = every zone is one flat (Madrid 1,165, Bologna 1,171).
* **Building split** (seed 9102, class x flat band 1 / 2-8 / 9-24 / 25+, 70 / 15 / 15), `Step9_docs/impl/buildsplit_win3/`:
  Madrid dev 816 d6ada695904d16c81da1a13059dbfc9d, val 176 ddf1cc4b8f62717a4a0773d022210fdd, test 173
  c4b0e46c3915dfa039eec08ef9da4c5c; Bologna dev 820 55410d3538802ee66ef7ea636e008e47, val 176 b9d4f6d9318d5a0e57027ea8120cfd20,
  test 175 71b57e8ee5e3e76ba20288d8bf5eee78.
* **Hold-out (author 2026-10-01 17:39):** a building with any flat under 15 m2 (`static_win3/flats_<D>.csv`, `floor_area_m2`) is
  not run: `Step9_docs/impl/heldout_tinyflats_win3.csv` md5 1a0cd4ad0a4a906f57ec1e52ec0c5c37 (Madrid 29: dev 21 / val 4 / test 4;
  Bologna 83: 56 / 9 / 18). Filtering happens at use; the split lists stay as sealed. Buildings left: Madrid 795 / 172 / 169,
  Bologna 764 / 167 / 157.
* **Later OpenUBEM tag `_win_2026-10-04` (flat count follows floor area; peer message 2026-10-01 18:56):** Madrid changes only
  for the sliver-join and shared-record buildings (list to come); every other Madrid IDF must stay byte-identical, which is
  checked by md5 per building before any of its runs is reused. Rules written before any campaign run: (a) the Madrid building
  split is sealed on the 10-03 lists above; a building whose flat count changes keeps its sealed split (flat bands were for
  balance only) and its 10-03 runs are void and re-run on 10-04; (b) the Madrid hold-out is re-read on the 10-04 static
  tables (same rule, any flat under 15 m2): a building that leaves it joins with its sealed split, one that enters it is held
  out; (c) Bologna is not run on 10-03: its building split and hold-out are derived on 10-04 with the same seed and rule and
  added here as a dated amendment with md5 before any Bologna run; (d) every run stores the md5 of its source IDF, and a
  result is reused only if that md5 equals the current base file; it also stores the md5s of every code file the IDF writer
  and the household builder actually load (listed per result: writer 4 files, households 7) and of its household placement,
  and is reused only if all four keys equal the current ones (task 9m, seen failing on a staged copy); (e) buildings with
  degenerate surfaces (`Step9_docs/impl/wp9k/degenerate_win3.csv`, md5 99cab93216242c432a26ee661cd63bce; Madrid 72 in the
  plan = 585 runs) fall under D9-6 (fix at source): OpenUBEM is asked to remove them in `_win_2026-10-04`; their runs are
  submitted after the other 8,616 Madrid runs, on 10-04 if it arrives first; a building still degenerate is run as
  delivered and its runs are reported not clean by name (G-c5 unchanged, the store refuses them).
* **Household split** (seed 9101, per country, size strata 1 / 2 / 3 / 4 / 5+, 70 / 15 / 15),
  `/speed-scratch/o_iseri/5J/modelA/households/splits/`: es dev 6,678 915952abb6b7060ccab6334616f6e33a, val 1,431
  599f2acdbde37f92d80ed5189e2c7dfa, test 1,432 e0a9706c981c8e0442cc043f69f24136; it dev 12,905 92a729299090e84a9747e71def939ddf,
  val 2,765 f7dead7152420dae4ade3e77c7504ad6, test 2,765 59bd62e8ac85a07b0ef89c767e7f1b65. Corpus: the ES + IT copy only
  (`4J_step3_corpus_es_it.jsonl`, md5 1a5163445291b54114832e192b0d9a05).
* Test runs are read only by the one Step 6-style scoring job, through a split loader that refuses test ids and appends every
  read to an open log (as Step 5 R1).

## R2. Runs (9C, D9-3, D9-5)
* Per building: dev buildings 3 dev + 2 val + 2 test household runs; val buildings 2 dev + 2 val; test buildings 2 dev + 2 test;
  plus one B0 run (average household = mean of 60 dev households drawn with seed 9106, the pilot `<cc>_avg` rule; one series in
  every flat) and one default-schedule run (constant 3 W/m2, no household), all
  under the same settings. Every flat of a run gets a distinct household of the run's split, drawn by survey weight without
  replacement; no flat gets the same household twice within one pool in one building.
* Settings (D9-3): ideal loads, heating 20 C, cooling 26 C, People + ElectricEquipment from the household's Schedule:File series,
  OtherEquipment lump removed, outputs as the pilot plus the zone map; windows as delivered in the base (D9-5). Weather: the
  district file the base ships (Madrid 2010, Bologna 2014). EnergyPlus 23.1.
* Shading, sizing, timestep: as OpenUBEM delivers them (shading PolygonClipping updated daily, sizing Yes / Yes / Yes, the
  delivered timestep); author 2026-10-01 18:55 "follow openUBEM settings for buildings". No fast setting.
* Writer: `tools/5thJ_modelA_idf.py` at its sealed md5; every written IDF passes `schedcheck`.
* Runner (9l + 9m): `tools/speed/a9_campaign_task.py`, `a9_campaign_task.sh`, `a9_campaign_check.sbatch`, plan
  `campaign/manifests/plan_ES-MAD-BERRUGUETE.csv` (9,201 rows, md5 f627f60d92243dc5019014cd30696a8b), all at their sealed md5s.
* Noise floor: 10 inputs x 10 repeats on 10 dev buildings chosen by seed.
* Run plan after the hold-out: Madrid 9,201 runs, Bologna 8,820, total 18,021 (from 18,924 before the hold-out).

## R3. Run integrity (9V items 3, 4, 8, 9)
* Run count equals the plan; zero failed; every zone of every run extracted; a run is clean only if Severe == 0 and no
  "invalid" / "not found" line (G-c5, never relaxed). A not-clean run is reported by name, never silently dropped.
* Household purity read back from the written series: no respondent, household or diary day in two splits.
* Reproduction (G-c1: default edit chain, heating within 0.1 %), windows (G-c2: window area within 1 %), equipment (G-c3),
  cooling (G-c4 / G-c4s) and zone map (G-c6) pass on the campaign base before the campaign; each was seen failing on a planted
  fault.

## R4. Inputs (9D, E3-E5; EnergyPlus inputs only)
* Household drivers per flat and hour: presence fraction, appliance fraction, member count, appliance design level; derived
  people at home and appliance power (Step 5 R2).
* Neighbour drivers: mean people at home and appliance power of flats on the same storey, the storey above and below (OpenUBEM
  `storey_index`), plus a 0/1 flag when none; a flat spanning several storeys counts on each.
* Weather: 7 EPW variables; calendar: hour of day, day of year, day of week of the diary year.
* Static vector (`tools/5thJ_modelA_static.py`, tables `impl/static_win3/`): per flat floor area, outdoor wall and window area in
  N / E / S / W bins by surface azimuth, adiabatic wall area, roof and ground-floor area, storey index, storeys spanned; per
  building class and age band one-hot, storeys, flats, conditioned area, wall / roof / floor / window U, window share and SHGC,
  neighbour shading surface count; country one-hot (dropped in R8). Z-scored on development and clipped to the development
  range. No building, household or run id is ever an input. Any EnergyPlus output is never an input.
* Window: 168 h before + 24 h predicted in, 24 h out, stride 24 h.

## R5. Targets
Hourly heating, cooling and equipment electricity per flat, standardised on development; total electricity computed as
equipment + (heating + cooling) / 3.0 (COP 3.0 ASSUMED), not learned.

## R6. Models, grid, budget (E7)
TCN and Transformer, width {64, 128} x depth {small, large} x pair-loss weight {0, 1} = 16 configurations, seed 1; AdamW, lr 1e-3
cosine, at most 30 epochs of 400,000 windows, patience 4 on validation, at most 4 GPU-h per configuration, at most 8 at once.
Nothing is carried over from the pilot (no weights, no pilot runs, the pilot winner is not assumed).

## R7. Winner, control, seeds, baselines (E8; Step 5 R4, R5, R7, R8 with AMENDMENT 3)
Shortlist 3 per family by validation loss, frozen scorer on validation, winner = most G5J.3 passes. Control C = household and
neighbour drivers shuffled within country. Seeds 1, 2, 3 for S and C. B0 = the average-household run of the same building.
B1 = boosted trees on at most 6 million development flat-hours, predictions clipped at 0.

## R8. Country-out (INFO)
Trained on one district (development, validation for early stopping), scored on the other; reported as new country, city,
weather year and building stock at once.

## R9. Store
`/speed-scratch/o_iseri/5J/modelA/store/`, built only from Model A runs by the 9g store builder (own working folder per run,
targets truncated to the flat rows, heating read by header position); refuses a not-clean run and any test id outside the scoring
job. Measured 0.229 MB per flat-year.

## R10. Compute size (D9-4) — RULED by the author 2026-10-01 18:55
Frame (2026-10-01 15:50): cost = runs x measured seconds per run with windows and pilot settings; budget 3,000 CPU-h; 5J may use
32 Speed CPUs plus up to 10 desktop CPUs. If the full plan fits, every building runs. If not: (i) the fast setting (shading every
20 days, sizing off) only if the windowed check G-c7 passes (heating and cooling change median <= 1 %, worst <= 3 %, equipment
equal); then (ii) sample buildings within each class x flat-band stratum at one common fraction, keeping every building of
classes with fewer than 60 buildings. Measured 2026-10-01 18:42 (log entry of that time): G-c7 PASS (heating median 0.019 %,
worst 0.074 %; cooling median 0.156 %, worst 0.431 %; equipment equal 12/12; both controls fired); slow setting about 5,800 CPU-h
(above budget), fast setting about 350 to 850 CPU-h; disk about 49 GB. Manager recommendation: fast setting for every Model A run
(occupancy, B0, default-schedule, noise floor), every building, no sampling. Ruling (author, 2026-10-01 18:55): "follow openUBEM settings for buildings" = no fast setting (G-c7 kept as a measured, not
adopted, result). Cost at these settings about 5,800 to 6,800 CPU-h. Full plan or sampling: author 2026-10-01 18:55 "keep going handle simulations" after being told the cost = the full
plan, every building, no sampling (manager reading; Speed 32 CPUs, desktop optional).

## AMENDMENTS (after sealing only)
**A1, 2026-10-01 21:30 EDT (manager), Madrid moves to OpenUBEM `_win_2026-10-05`.** Reason: OpenUBEM delivered a corrected Madrid fleet (113 stems with a new floor-area flat rule, 58 stems with degenerate surfaces deleted; 1,001 byte-identical). Sealed lists are NOT changed: (a) every building keeps its sealed `buildsplit_win3` split; the re-run split on the new flat bands (`buildsplit_win5/`) moves 460 of 1,163 stems and is NOT used. (b) The tiny-flat hold-out is re-read on the new base by the sealed rule (any flat under 15 m2): 8 buildings (dev 6, val 2; none entered, 21 left) = `impl/heldout_tinyflats_win5.csv` md5 e3f673d40be7a4412b67a4731aaca2a2; the 20 that left it join the plan. (c) Two sealed stems with no dwelling zones on 10-05 (`bb4d3f44d4fbe5b1`, `bf1fa61d6ffd3b54`, both dev) cannot run: EXCLUDED, listed by name with this reason in the paper's accounting; `88df8e48213666eb` (59 dwelling zones now, in no sealed list) is NOT added. (d) Runs of buildings still degenerate on our counter run as delivered and are reported not clean by name (R1 e). (e) Plan = `impl/wp9o_win5/plan_ES-MAD-BERRUGUETE_win5.csv` md5 a8ec8ebdd587ead2f96a1f60d90aeb98 (9,354 rows); rows identical to the live plan (7,992) keep their live result; the 1,458 other rows are in `resub_ES-MAD-BERRUGUETE_win5.csv` md5 bb65ffea43ed29e5020684e5919978fa and run in `campaign_win5/` (own results folder; the store reads both roots into one ledger with the win5 plan, zone map and `static_win5`). Old results of the 1,209 void run ids are refused by source-md5 and moved to `results_void_win3/` after the live array ends. No run, split or seed was seen before this amendment for the changed rows.
