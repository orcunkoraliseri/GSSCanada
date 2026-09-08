# Scan: OpenUBEM capabilities (factual digest)

Read-only scan of `C:\Users\o_iseri\Desktop\OpenUBEM` on 2026-09-07. No files in OpenUBEM were modified.
Sources cited by path throughout; project scale is very large (thousands of docs), so this digest is
built from top-level docs, the README, package structure and targeted greps — not an exhaustive read.

---

## A. What OpenUBEM is, and its relationship to GSSCanada / 4J

**What it is.** OpenUBEM is a fully open-source, pip-installable, scriptable Python library that takes a
neighbourhood (address, coordinate, bounding box, or OSM XML) and estimates annual building-level energy
use and carbon emissions via a 5-stage pipeline: OSM ingest → archetype classification/enrichment →
per-building EnergyPlus IDF generation → parallel EnergyPlus 23.1 simulation → results/carbon/validation.
It generalises the probabilistic UBEM methodology of **Iseri et al. (2025, Energy & Buildings 337,
115620)** (the author's own prior work) from a single Istanbul/Bahçelievler case study to a general
pipeline, currently validated on 3 US cities and extended into 4 European districts.
(`README.md:1-10`, `docs/docs_main/OVERVIEW_...md:9-12`, `docs/docs_main/DESIGN_...md:9-11`)

**Relationship to GSSCanada / 4J (the HETUS occupancy work).** OpenUBEM is the **building-energy-simulation
engine** consumed by the 4J project. A dedicated bridge directory,
`docs/docs_ACTIVE/europeanLocations/messages_GSSCanada/`, holds a formal letter exchange between "4J
(GSSCanada)" and "OpenUBEM" (e.g. `2026-08-27_4J_to_OpenUBEM_binding_v2_repinned_and_v1-1_verified.md`,
`2026-08-27_4J_to_OpenUBEM_presence_binding_ruled_and_delivered.md`,
`2026-08-28_4J_to_OpenUBEM_internalmass_fix_verified_campaign_still_not_reproducible.md`). The pattern:
4J issues a **campaign cell spec** (`eu_campaign_cell_spec_v1.x.json`, occupancy/weather/fold bindings
derived from HETUS diaries for `es`/`uk`/`it`) and a **presence binding**; OpenUBEM independently
re-derives every hash/claim read-only against its own tree before accepting it (example: verified
`sha256(v1.1)`, `md5(v1.0)`, per-cell diffs, in the message above) and runs the actual EnergyPlus
simulations that produce the EUI numbers 4J's memory log quotes (e.g. the shared `D-EU-31` /
"reproducibility perimeter" ruling and the `it` fold 108.25 kWh/m² figure trace to this same 12-cell / EU
district campaign machinery). In short: **4J supplies occupancy schedules and campaign specs derived from
HETUS time-use diaries; OpenUBEM supplies geometry, archetypes, IDFs and EnergyPlus runs, and reports
simulated EUI back.** No occupancy-schedule generation, HETUS parsing, or LLM occupancy modelling exists
inside the OpenUBEM codebase itself — that is 4J's side. A design figure explicitly named
"OpenUBEM–GSSCanada integration and validation flow" exists at
`docs/docs_ACTIVE/europeanLocations/content/figure_1_1_integration_pipeline.mmd`
(`docs/docs_ACTIVE/europeanLocations/content/README.md:9`).

Grep for `GSSCanada`/`HETUS`/`4J`/`occupancy`/`schedule` outside this bridge folder returns essentially
nothing — the connection is entirely mediated through `docs_ACTIVE/europeanLocations/` (the arc informally
called "Step 8" inside OpenUBEM) and its `messages_GSSCanada/` sub-folder.

---

## B. Sites / neighbourhoods / countries covered

**United States (original validation matrix, `R5`/Phase-E, 3 cities × 4 density rings = 12 cells,
8,160 buildings):** New York City (ASHRAE 4A), Los Angeles (3B), Austin (2A); rings centre/urban/
suburban/rural. 8,154/8,160 (99.93%) simulated successfully. **Status: validated / adopted baseline**
(`README.md:591-624`, `docs/docs_TODO/wider_validation_matrix.md:33-40`).
- Wider validation matrix (more cities/climate zones) is an explicit **backlog item, not started**,
  deferred by user ruling 2026-08-20 (`docs/docs_TODO/wider_validation_matrix.md:1-8`).

**Europe (the "European locations" arc, arc-internal name Step 8, `EU-01`…`EU-21`+):** four real
residential districts —
- Madrid, Berruguete (Spain, `es`) — 961 buildings
- Lyon, Hauts de Croix-Rousse (France, `fr`) — 297 buildings
- London, St Dunstan's (England, `uk`) — 82→389+ buildings (coverage expansion in progress)
- Bologna, Galvani 2 (Italy, `it`) — 1,204 buildings
(`docs/docs_ACTIVE/europeanLocations/BRIEF_european_locations_v5.md:9-13`, `STATE_european_locations_v5.md`)

**Status as of 2026-09-07 (from `STATE_european_locations_v5.md`, the live-truth doc):**
- The **no-core dwelling-division rule** (`EU-20`/`EU-21`) is written, proven on 550 real test plates,
  and carried into the engine with bit-parity (0 mismatches).
- Four fresh district EUIs were produced 2026-09-06 (London 97.08, Lyon 65.94, Madrid 77.15, Bologna
  54.94 kWh/m²) — **but as of 2026-09-07 these are explicitly marked STALE and not quotable**: three
  parallel decision packages (`D-EU-107` balance-the-cut, `D-EU-108` London coverage recovery, `D-EU-109`
  recover discarded dwelling divisions) are in execution and will force a restatement
  (`STATE_european_locations_v5.md` §1, "no district EUI may be quoted between T05 submission and T06's
  restatement").
- Earlier US-style **US 12-cell matrix numbers remain the only currently quotable OpenUBEM validation
  figures**; no EU district number is currently safe to cite externally.
- `EU-18c` (non-box EnergyPlus sample battery) is **blocked pending the owner's explicit go-ahead
  sentence, `D-EU-55`** (`STATE_european_locations_v5.md:104,749`).

**Not covered / not built:** Canada (NECB) — explicitly out of scope for Phase 1/2, "stubs only" for
Phase 3 (`docs/docs_main/OVERVIEW_...md` Phase Roadmap table). France beyond the one Lyon district is not
otherwise modelled (a 40-archetype TABULA France registry exists and was vetted for licensing, but no
French district beyond Lyon Croix-Rousse is in the built campaign).

---

## C. Data sources

**US pipeline (bundled, `openubem/data/`):**
- OpenStreetMap via `osmnx` (footprints, tags) — canonical geometry input for every location.
- Overture Maps (footprints/heights, offline GeoParquet or live DuckDB) — optional, off by default.
- ASHRAE Standard 169 climate-zone polygons (`climate_zones/*.gpkg`).
- EPW weather from `climate.onebuilding.org`, resolved via a bundled ~2,800-station catalogue
  (`epw_stations.csv`).
- ASHRAE 90.1-2019 envelope/construction tables, IECC 2021, DOE Prototype Buildings loads/schedules,
  CBECS 2018 (validation reference + archetype→PBA crosswalk), EPA eGRID 2022 (carbon factors by US
  state). (`README.md` "Data Assets" table, `openubem/data/` subfolders.)
- LiDAR nDSM and assessor parcel records — supported as **fusion** imputation sources, "enabled, inert
  until sources are configured" (`README.md` Step 2.3 table).

**Europe pipeline (district-specific, vetted via Deep-Research reports in
`docs/docs_ACTIVE/europeanLocations/DeepResearch/`):**
- **TABULA/EPISCOPE** national building-typology workbooks (IWU Darmstadt) — construction-era archetypes
  and envelope data for ES/GB/IT/FR. Licence: open academic use, publication of derived tables and
  redistribution of derived IDFs **permitted with mandatory attribution** ("IEE Projects TABULA +
  EPISCOPE (www.episcope.eu)"); redistribution of unmodified original workbooks permitted non-commercially
  with IWU copyright retained (`DR09_tabula_licence_and_france_registry.md` §2-3). France: 40 `FR.N.*`
  national archetypes usable; 10 `FR.OPHM.*` Montreuil pilot rows excluded as non-standard.
- **Weather (per-fold actual-year windows, matched to each HETUS survey period):** recommended source
  **Copernicus C3S ERA5/ERA5-Land reanalysis** (0.25°/0.1° grid, hourly, 1940–present), converted to EPW;
  cross-validated against national station data — AEMET (Spain), Met Office MIDAS Open (UK), ARPA
  Emilia-Romagna/ISPRA SCIA (Italy). Licence: ERA5 is CC-BY-style "Licence to Use Copernicus Products" —
  **publication-compatible and redistributable with attribution**; MIDAS Open under OGL v3.0, AEMET under
  Spanish reuse law, ARPA/ISPRA under IODL 2.0 — all publication-compatible with attribution. Commercial
  alternatives (Meteonorm, White Box Technologies) permit publishing *derived results* but **forbid
  redistributing the raw/converted EPW files**. (`DR08_actual_year_weather_sources_and_licences.md` §1,
  §3.)
- **European open building/EPC datasets** (surveyed, not necessarily all ingested): Spain — Catastro
  INSPIRE buildings, Comunidad de Madrid EPC (CEE) registry; England — EPC open register (UPRN-keyed),
  Ordnance Survey Open UPRN/Open Map Local; Italy — Emilia-Romagna SACE APE register, Bologna Open Data,
  ISTAT census sections; France — ADEME DPE database, BDNB, IGN BD TOPO
  (`DR10_european_open_building_data_and_dense_neighbourhoods_brief.md` §A "Context").
- District boundary/selection: ruled by residential-building density over open administrative sub-units
  (Madrid *barrios*, London wards/LSOAs, Bologna *quartieri*, France *IRIS*)
  (`DR10_..._brief.md` §"Context").

---

## D. Engine / architecture

**Pipeline (5 stages + optional Step 6), each stage's module and I/O documented in `README.md`
"Pipeline: Step by Step":**
1. **Acquisition** (`openubem/acquisition/`) — OSM fetch/clean → climate zone → EPW.
2. **Semantic enrichment** (`openubem/semantic/`) — rule-based 30-archetype classifier
   (`building_classifier.py`, 17 priority rules) → envelope/loads/schedules from ASHRAE/DOE tables
   (`construction_sets.py`, `loads.py`, `schedules.py`) → tiered imputation & provenance
   (`imputation.py`, `provenance.py`, `spatial_impute.py`, `fusion.py`, `draw_methods.py`, `debias.py`).
3. **IDF generation** (`openubem/geometry/` + `openubem/idf/`) — footprint simplification, thermal
   zoning strategy (single/per-floor/perimeter-core), context shading, real HVAC (10 system families),
   DHW/cooking/refrigeration/elevators as real EnergyPlus objects (`idf/builder.py`, `hvac.py`, `dhw.py`,
   `cooking.py`, `refrigeration.py`, `elevators.py`, `opaque_assembly.py`).
4. **Simulation** (`openubem/simulation/`) — parallel EnergyPlus 23.1 subprocesses via `joblib`/`loky`,
   resumable, per-building isolated work dirs (`runner.py`, `parallel.py`).
5. **Results** (`openubem/results/`) — SQL/CSV parsing, 10 metered end-use EUIs, IOD (overheating),
   per-end-use GWP (`load_referenced_v1` convention), CBECS validation gates, visualisation
   (`parser.py`, `carbon.py`, `aggregator.py`, `visualization.py`).
6. **Step 6, optional, outside the spine** (`openubem/microclimate/`) — outdoor pedestrian-height UTCI
   thermal comfort (sky-view-factor shadows, COST-730 Bröde UTCI polynomial), reads Steps 1–5 read-only,
   never feeds back into `05_results.*`.

**"Arms A–F": not found as OpenUBEM terminology.** No literal "Arm A/B/C/D/E/F" concept exists in this
codebase (checked `grep -rl "Arm A|Arm B|...|Arm F"` — the handful of hits are false positives in
unrelated contexts, not an OpenUBEM taxonomy). The closest analogous concepts inside OpenUBEM are the six
**simulation resolution modes** (`README.md` "Simulation Resolution Modes"): `auto` (adaptive, the
validated default), `building` (1 zone), `floor` (1 zone/floor), `fast_zone` (generic core+perimeter),
`layout_assign` (DOE baseline-IDF substitution, "not certified for fleet-level EUI reporting"), and
`zone` (room-level layout generation, "parked, not a validated baseline"). If "arms A–F" is a term from
the 4J/HETUS side (e.g. platform/host arms for reproducibility), it does not originate in OpenUBEM's own
docs and should be treated as a 4J-side concept, not verified here.

**"No-core" meaning:** in the European Locations arc, "no-core" is the ruling (`D-EU-79`, owner
2026-09-02: *"i have decided with nocore option for all"*) that every floor of a residential building is
divided **directly into dwellings only — no circulation zone, no stair core, no corridor zone** — as
opposed to the earlier "core-era" engine logic that reserved a circulation/core zone per floor.
(`docs/docs_ACTIVE/europeanLocations/STATE_european_locations_v5.md:707`,
`BRIEF_european_locations_v5.md:9-13`.)

**Interactive 3D viewer** (`openubem/viz/`) — self-contained offline HTML per run/district, colours
buildings by simulated EUI, shows per-building provenance and (for EU districts) EU-21 layout-rule
PASS/FAIL badges. Pre-built viewers: `openubem/outputs/3D/` (US) and
`docs/docs_ACTIVE/europeanLocations/outputs_3D/` (EU districts).

---

## E. Validation / reproducibility methodology

- **Gates are report-only, never tuned to pass** (repeated rule throughout `README.md` and
  `docs/PROJECT_CHECKLIST.md`). **Zero fitted parameters** — every constant traces to a cited standard
  (ASHRAE 90.1, DOE prototypes, CBECS, eGRID, IBC).
- **US CBECS gates** (Step 5G): CV(RMSE) < 30%, NMBE < 10%, R² > 0.6 (archetype-level), KS D < 0.10,
  with explicit exclusions (residential apartments, data centres, `OpenUBEMUnknown` from R² only)
  (`README.md` Step 5G table).
- **Four-level validation hierarchy** stated in the design doc: unit tests → DOE prototype round-trip
  (±5% EUI) → Iseri 2025 Bahçelievler replication (±10% per-building heating EUI, 24 buildings) →
  city-scale CBECS/BPD calibration (`docs/docs_main/OVERVIEW_...md` "VALIDATION SUMMARY").
- **Provenance everywhere**: every enriched column carries a provenance column and a composite
  `data_quality_flag` token (observed / imputed / fused / default), enforced in code
  (`README.md` Step 2.3, design principles list).
- **Deterministic & reproducible**: seeded RNG, versioned artifact schemas, resumable Step 4 via
  manifest (`README.md` design principles).
- **Before/after classifier gate**: no archetype-classifier change is adopted until measured on two
  labelled fixtures both before and after, with named accuracy per fixture (`README.md` Step 2.0 note).
- **Cross-project reproducibility protocol with 4J**: the `messages_GSSCanada/` exchanges show OpenUBEM
  independently re-computing every hash/claim in a 4J-issued spec before accepting it (sha256/md5
  cross-checks, cell-by-cell diffs) rather than taking the other side's numbers on trust — the same
  "measure, don't take on word" discipline that recurs throughout `docs/PROJECT_CHECKLIST.md`.
- **No dedicated "prereg"/"digest"/"two-host platform arm" apparatus was found as an OpenUBEM-native
  mechanism** — those terms appear only inside the 4J-authored letters in `messages_GSSCanada/` and one
  EU02 selection-rule pre-registration note
  (`docs/docs_ACTIVE/europeanLocations/outputs/EU02_neighbourhood_selection_2026-08-24/eu02_prereg_selection_rule_v2_amendment.md`),
  which pre-registers the neighbourhood-selection rule before computing the actual counts — a
  4J-borrowed methodology applied once, to district selection.
- **Cluster reproducibility**: OpenUBEM runs city-scale fleets on the Concordia Speed SLURM cluster
  (job-array pattern, generate locally → simulate remotely → harvest back), governed by hard rules in
  `CLAUDE.md` (no compute on login node, always `sbatch --array`, 7-day walltime, 32-wide concurrency cap).

---

## F. Open decisions, roadmap items, stated limitations, future work

**Phase roadmap** (`docs/docs_main/OVERVIEW_...md` "PHASE ROADMAP"):
| Phase | Scope | Status |
|---|---|---|
| Phase 1 | US cities; ASHRAE/IECC/DOE/eGRID; deterministic loads; rule-based classifier | **This design (built)** |
| Phase 2 | Probabilistic Monte-Carlo 4-version sweep; ML imputation (RF/GBM); surrogate models; stochastic (Markov) schedules; Bayesian calibration opt-in | **Architectural hooks present, not built** |
| Phase 3 | NECB Canada; TABULA Europe; CityGML/3DCityDB ingest; ladybug-core solar; Urban Weather Generator climate-morphing; city-scale (≫10⁵) via surrogates | **Stubs only** (Europe/TABULA has since progressed far beyond "stub" via the europeanLocations arc, ahead of this Phase-3 roadmap doc) |

**Explicit Phase-1 non-goals** (`docs/docs_main/DESIGN_...md` §2.2): no native CityGML ingest; no
detailed HVAC plant sizing (ships `IdealLoadsAirSystem`/PTAC only, no chiller plant/VAV optimisation —
**superseded**: 10 real HVAC families are now implemented per README Step 3H, so this DESIGN-doc line is
stale); no grid co-simulation (no OpenDSS/REopt/battery dispatch); **no microclimate/UHI coupling in
Phase 1** (later delivered as the separate, unvalidated Step 6); no embodied carbon/LCA (operational GWP
only); no Bayesian calibration loop; no interactive dashboard/web UI (only the static/offline 3D viewer);
no Rhino/Grasshopper/proprietary CAD path.

**Open design questions still logged** (`docs/docs_main/OVERVIEW_...md` "OPEN QUESTIONS", 14 items,
originally dated 2026-05, largely superseded by later work but never formally closed in this doc):
includes NECB envelope-table sourcing, EnergyPlus version pin policy, default fallback for unknown OSM
tags, Phase-2 stochastic-schedule scope, CMHC/StatCan data for Canada ML imputation.

**Parked/deferred backlog items:**
- **Wider validation matrix** beyond the 12-cell US set — explicitly deferred, "does not block any
  current work" (`docs/docs_TODO/wider_validation_matrix.md`).
- **Mixed-use building classification** — every mixed-use building today silently becomes
  `MidriseApartment` at MEDIUM confidence; user-ruled deferral 2026-08-05, "not a bug fix... a
  modelling-philosophy decision" (`docs/docs_TODO/mixed_use_classification.md`).
- **Room-level `layoutGenerator.py`** — "parked", not a validated baseline
  (`docs/docs_TODO/layoutgenerator/`, `README.md` resolution-modes table).
- **`layout_assign` resolution mode** — usable for zone/HVAC-topology studies but **not certified for
  fleet-level EUI reporting** (storey-matching only reaches 1- or 3-native-storey DOE prototypes; loads
  stay at 2022-code density regardless of real vintage) (`README.md` "Why layout_assign is not used").

**Stated limitations, plainly (`README.md` "Known limitations"):**
- Published US fleet EUI (157.1 kWh/m²) is **not yet end-to-end reproducible from `HEAD`** — provenance
  caveat live pending a confirming third fleet re-run.
- Fleet EUI under-predicts measured benchmarks: NYC −31.3%, LA −3.6%, Austin −30.5% vs. LL84/EBEWE/CBECS
  proxies — attributed to a retired reconstruction overlay being replaced by real physics that exposes a
  previously-absorbed gap (office plug-load intensity), deliberately not closed because fitting to CBECS
  would break the zero-fitted-parameters rule.
- Step 6 (UTCI) has **no measurement validation whatsoever** for any of the twelve cells and is
  deliberately excluded from `05_results.*`.
- Distribution-shape gates (CV(RMSE), KS) are "structural for an archetype-deterministic UBEM" and
  reported for transparency, not as pass/fail.
- License: `README.md` §15 states **"To be specified"** — no license is currently declared, though the
  original DESIGN doc specifies MIT as the intended choice.

**European-locations-arc open items (current as of 2026-09-07):**
- `FINDING 258` — a few dwelling plates split unevenly (tiny units beside one oversized unit) despite
  passing all 7 geometric checks; owner ruled a per-building fix later, not a full re-cut
  (`BRIEF_european_locations_v5.md` §2).
- Three merged decision packages `D-EU-107`/`108`/`109` (balance the cut, London coverage recovery,
  recover discarded divisions) are **in execution**, and until they land **no district EUI may be
  quoted** (`STATE_european_locations_v5.md` §1).
- `EU-18c` non-box EnergyPlus sample battery **blocked** pending an explicit owner go-ahead (`D-EU-55`).
- Corridor/core layout path (the pre-no-core alternative) is **parked with files intact**; "only the
  owner may restart it" (`BRIEF_european_locations_v5.md` §5).

---

## G. Climate change, future weather, heat, adaptation, retrofit, decarbonisation, grid, district energy, policy, health, equity

- **Heat/outdoor thermal comfort**: Step 6 (`openubem/microclimate/`) computes UTCI (universal thermal
  climate index) at pedestrian height, CTSI (cumulative thermal stress) and PHEH (person-hours above
  46°C) per building/parcel, plus **mitigation scenarios**: tree canopy, PV canopy, cool pavement, cool
  roof, high-albedo facade — each modelled as a domain-layer edit (albedo/canopy), not a physics change
  (`README.md` Step 6 table). **Not validated against any real-world measurement** for any site.
- **No future/morphed weather.** OpenUBEM currently simulates only historical/actual-year EPW (TMYx or
  ERA5-derived AMY for specific past HETUS-matched windows). Urban Weather Generator (UWG)
  climate-morphing for future scenarios is explicitly listed as **out of scope for Phase 1**
  (`docs/docs_main/DESIGN_...md` §2.2) with an unresolved open question about pre-wiring a
  `weather/uwg_morph.py` placeholder (`docs/docs_main/DESIGN_...md:547`); no evidence it has been built.
- **Retrofit**: not a modelled capability. No retrofit-scenario, envelope-upgrade, or renovation-pathway
  logic was found in `openubem/`; the DESIGN doc's motivation section only *mentions* retrofit programs
  as one of several downstream UBEM use-cases in general (`docs/docs_main/DESIGN_...md:9`), not as
  something OpenUBEM itself performs.
- **Decarbonisation / carbon accounting**: implemented — per-end-use GWP (`load_referenced_v1`
  convention: 0.181 kg CO₂e/kWh gas; eGRID 2022 state electricity factors) is a first-class Step 5
  output (`README.md` Step 5E). **Operational carbon only — no embodied carbon/LCA** (explicit Phase-1
  non-goal, `docs/docs_main/DESIGN_...md` §2.2).
- **District heating**: present as a real end-use in European fleet buildings (Water Systems / district
  heating metering) — a defect trail exists (`OPEN-61`…`OPEN-64` in `docs/PROJECT_CHECKLIST.md`) around
  district heating being dropped from carbon totals ("no DH emission factor exists in the codebase,
  `carbon.py:106`, `config.py:83`") — logged as an open, deliberately-visible gap, not silently patched.
- **Grid / grid co-simulation**: explicitly **out of scope** — "No OpenDSS, no REopt, no battery
  dispatch (URBANopt handles those)" (`docs/docs_main/DESIGN_...md` §2.2).
- **Policy / health / equity**: no dedicated modules or outputs found. The only policy-adjacent framing
  is the general motivating statement that UBEM is "the analytical foundation for retrofit programs,
  district heating/cooling, photovoltaic siting, and climate-policy formulation"
  (`docs/docs_main/DESIGN_...md:9`) — aspirational framing, not an implemented capability. No equity,
  environmental-justice, health-outcome, or vulnerability-population module found in `openubem/`.

---

## H. LLMs or ML used inside OpenUBEM

- **No LLM is used anywhere in the live `openubem/` pipeline.** Archetype classification is a
  **rule-based** 17-rule engine (`openubem/semantic/building_classifier.py`), not ML/LLM-driven
  (`README.md` Step 2.0).
- **ML imputation tier exists but is opt-in only, never in the default tier list**
  (`IMPUTE_ENABLED_TIERS = ("fusion", "spatial", "statistical")` in `openubem/config.py`, per
  `README.md` "Configuration & Constants"). When enabled, `openubem/semantic/imputation.py` offers
  classical supervised imputers — **MissForest, MICE, kNN, RF (random forest), HistGBM
  (histogram gradient boosting), and linear regression** — plus a quantile-mapping de-bias corrector
  (`debias.py`). No deep learning / transformer / LLM component in this tier.
  (`README.md` Step 2.3 tier table.)
- A **variance-preserving "draw" tier** (KDE, PMM, hot-deck, residual, ABB, categorical-frequency draws)
  is also opt-in-only, not wired into the default call graph (`README.md` Step 2.3).
- **Hard rule enforced in code and tests**: no imputer or fusion source may read an EUI column
  (`_assert_no_eui_leakage`) and no imputation parameter is ever tuned against a simulated-EUI target
  (`README.md` Step 2.3 "Hard rules").
- **`Data Imputation/` folder (top level, outside `openubem/`)** — legacy, standalone Jupyter notebooks
  predating the current package: `local_data_classifier.ipynb` and `u_val_classifier_scaled.ipynb`,
  Turkish-commented, using Keras/TensorFlow (`import keras`, `import tensorflow as tf`, Google Colab
  GPU runtime) to classify construction-date buckets and U-values from `Data Imputation/Datasets/
  merged_data.csv` / `u_val_final.csv`. Pre-trained model artifacts are zipped under
  `Data Imputation/Models/` (`local_data_clas_1_balanced-....zip`,
  `u_val_clas_1_balanced-....zip`). **This is a deep-learning classifier, not an LLM**, and it is
  **not imported or called anywhere in the live `openubem/` package** — it reads as inherited
  research material from the author's earlier (Iseri et al. 2025) methodology, kept for reference,
  not part of the current pipeline. No `README` exists in `Data Imputation/`.
- **Deep-Research reports** (`docs/docs_ACTIVE/europeanLocations/DeepResearch/DR08`–`DR16`) were
  themselves produced by an external "Deep Research Agent" (an LLM-based research tool) to source
  weather/TABULA/validation facts — an LLM was used as a *documentation/research authoring tool* for
  this project, not as a runtime component of the simulation pipeline.
- **`docs/docs_TODO/layoutgenerator/deepResearch/L13_generative_ml_floorplan_prompt.md`** references
  generative/ML floorplan synthesis as explicit **future work**, kept "low-priority/exploratory" and
  out of the core pipeline (`RESULT_L01_interior_zoning_landscape.md:75`); not built.

---

*End of scan. Written to:
`C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\5J_docs_occ\DeepResearch\_scan\scan_openubem_capabilities.md`*
