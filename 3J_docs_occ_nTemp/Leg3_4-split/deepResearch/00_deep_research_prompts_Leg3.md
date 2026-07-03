# Deep-Research Prompt Set — Leg 3 (4-Channel Split: + Retail + Hotel)

### README — roster, shared facts, and run conventions for the `dr_L3-*` prompt files

**Purpose.** Fill the evidence gaps that block Leg-3 design freezes. Each prompt is a **standalone
document** (`dr_L3-0N_<shortname>_prompt.md`, in this folder) written to be fed whole into an external
deep-research tool (Gemini Deep Research / Antigravity, ChatGPT Deep Research / o-series, Perplexity).
Format follows the OpenUBEM prompt-set convention: SCOPE GUARD → What/Role/Why → required output tables
(fill every cell) → Part C synthesis → exact output format → hard requirements.

**Do not re-run the foundational research.** The landscape work (occupancy-modelling paradigms,
empirical diurnal profiles per use, generative model families, TUS reach/limits, validation menus,
office/WFH trends, retail + hotel occupancy fundamentals, standards modulate-vs-replace, mixed-use
failure modes) already ran as Prompts 1–10 of `../../deepResearch_Resources/00_deep_research_prompts.md`
and the reports live in that folder. The `dr_L3` set covers only what those reports left open.

---

## Roster

**Core five (block build steps directly):**

| # | Prompt file | Gap it closes | Blocks |
|---|---|---|---|
| dr_L3-01 | `dr_L3-01_statcan_hotel_data_prompt.md` | Exact StatCan hotel-occupancy tables, QC+AB monthly coverage 2005–2022, access, breaks | Step 1C/2D — `hotel_occupancy_monthly.csv`; OPEN DECISION 3 |
| dr_L3-02 | `dr_L3-02_retail_eui_bands_prompt.md` | Retail EUI bands (as-modelled = PASS, empirical = INFO) | Step 8 — retail EUI gate; OPEN DECISION 5 |
| dr_L3-03 | `dr_L3-03_hotel_eui_bands_prompt.md` | Hotel EUI bands + occupancy-elasticity evidence | Step 8 — hotel EUI gate; OPEN DECISION 5 |
| dr_L3-04 | `dr_L3-04_instore_share_2030_prompt.md` | In-store retail share to 2030 → three named scenario bands | Step 6B — retail lever; OPEN DECISION 2 |
| dr_L3-05 | `dr_L3-05_hotel_diurnal_shape_prompt.md` | Numeric unit-normalized 48-slot guest-room shape `s(t)` | Step 6C — the curve; OPEN DECISION 4 |

**Extended set (harden design decisions, gates, and the paper):**

| # | Prompt file | Gap it closes | Feeds |
|---|---|---|---|
| dr_L3-06 | `dr_L3-06_retail_diurnal_targets_prompt.md` | Numeric per-day-type AT_RETAIL validation targets + the population-fraction → schedule-multiplier normalization | Step 4 gates; Step 7 injector formula; checks our project-chosen 0.06–0.10 midday gate |
| dr_L3-07 | `dr_L3-07_crossuse_lunch_coupling_prompt.md` | Model the office→retail lunch transition or keep channels independent (evidence-based verdict) | OPEN DECISION 7 — freeze before the Step-4 head |
| dr_L3-08 | `dr_L3-08_rare_head_extension_prompt.md` | Training recipe for adding a ~2 %-positive third head to the trained backbone (imbalance, calibration, α, regression gates, metrics that fail an all-zeros head) | Step 4 build; protects shipped AT_HOME/AT_WORK quality |
| dr_L3-09 | `dr_L3-09_hotel_2030_forecast_prompt.md` | Pressure-test SARIMA(1,1,1)(1,1,1,12)+COVID-dummy (pulse vs level shift) + three named 2030 hotel scenarios (business-travel structural change) | Step 6C; gives hotel its scenario lever like office WFH / retail in-store |
| dr_L3-10 | `dr_L3-10_mixeduse_reporting_positioning_prompt.md` | Per-use EUI reporting conventions (area basis, plant attribution, MEP treatment) + novelty matrix for the contribution claim | Step 8/9 output schema; 3rd-Journal introduction / related work |

**Step-4 ML trio (dedicated deep-learning research — run before the training plan freezes):**

| # | Prompt file | Gap it closes | Feeds |
|---|---|---|---|
| dr_L3-11 | `dr_L3-11_architecture_pressure_test_prompt.md` | Backbone keep/augment/replace at 3 GSS heads vs 2023–2026 alternatives (post-MDLM diffusion, decoder-only AR, SSM/Mamba, flow matching), argued against our hard gates + a targeted-upgrade menu | Step 4 architecture freeze; confirms or overturns the Leg-2 MDLM rejection |
| dr_L3-12 | `dr_L3-12_output_representation_prompt.md` | Independent binary heads vs joint mutually-exclusive location token (`occPRE` is one exclusive variable; heads permit impossible `AT_HOME = AT_WORK = 1` slots) + the exclusivity gate | Step 4 head design; interacts with OPEN DECISION 1 (OR-rule gating) |
| dr_L3-13 | `dr_L3-13_training_regimen_prompt.md` | The regimen around the resolved dr_L3-08 recipe: loss balancer at 2–4 tasks, conditioning encoding (CYCLE_YEAR under progressive fine-tuning), survey-weight sampling, calibration-safe regularization, flicker-safe decoding, Pareto selection (≤ 4-run ablation budget) | Step 4 training plan; protects fine-tunability for Step 6 |

Suggested run order: **01 → 05 → 09** (hotel side-track, sequential dependencies), **06 → 04** and
**08 → 07** (retail channel), **11 → 12 → 13** (Step-4 trio — backbone and representation gate the
regimen), **02 / 03 / 10** any time (independent).

---

## Shared facts every prompt assumes (embedded inline in each, repeated here for the record)

- **Project.** GSS-derived 4-channel occupancy pipeline (Leg 3 of 3): Residential (AT_HOME, replaces
  baseline) / Office (AT_WORK, modulates) / Retail (AT_RETAIL, modulates — the one new GSS channel) /
  Hotel (non-GSS, modulates monthly). Drives PNNL Tall (26,750 m²) / SuperTall (40,846 m²) mixed-use
  prototypes, NECB17, Montreal Z6 + Calgary Z7A, EnergyPlus `Schedule` at 30-min / 48 slots, cycles
  2005/2010/2015/2022 + 2030 forecast.
- **Retail signal.** GSS customer presence only (staff are AT_WORK); weighted episode-time share at
  shopping locations ~2.1–2.3 %, roughly stable 2005→2022; planned gate: weekday 12:00–14:00
  population fraction 0.06–0.10 (project-chosen, unverified — `dr_L3-06` checks it).
- **Hotel side-track.** `hotel_multiplier(t, month, PR) = s(t) × StatCan_monthly_rate(month, PR)`;
  2030 via SARIMA(1,1,1)(1,1,1,12) per province + COVID indicator (2020-03…2022-06); target schema
  `YEAR, MONTH, PR, occupancy_rate, ADR_CAD, RevPAR_CAD`.
- **Model.** Shared-encoder Conditional Transformer (6-layer, d_model 384, ~64k diaries), 3 GSS heads
  (resid / AT_WORK / AT_RETAIL), planned α = 1.0 : 0.5 : 0.3, per-head JS < 0.02 per stratum; hotel
  never enters the model.
- **Leg-2 EUI-gate pattern to replicate.** Office locked: as-modelled band (central 135, 100–200)
  kWh/m²/yr = PASS; empirical SCIEU band (central 230, 170–360) = INFO; simulated office median 180 →
  PASS. `dr_L3-02`/`dr_L3-03` produce the retail/hotel analogues.
- **Scenario-lever pattern.** One named 3-band lever per commercial channel: office = WFH
  (conservative / hybrid / fullyhybrid, built in Leg 2); retail = in-store share (`dr_L3-04`);
  hotel = travel-demand recovery (`dr_L3-09`).

## Run conventions

1. Paste the **entire** `_prompt.md` file into the tool — the SCOPE GUARD and pre-filled anchors are
   part of the prompt.
2. Every report must return **inline citations + a full reference list** (each prompt enforces this in
   its hard requirements; reject a report that skips it).
3. Save each report as **`dr_L3-0N_<shortname>_REPORT.md`** in this folder, next to its prompt.
4. Mine the findings into `3rdJ_00_4split_Occupancy_Pipeline.md` / `_Overview.md`, and mark the
   matching OPEN DECISION resolved with a date + report link (the Leg-2 convention, e.g. how
   dr_S4-03 resolved the MDLM decision).

## After the reports come back

- (01) → Step 1C/2D source + schema; (05) → Step 6C `s(t)`; (09) → Step 6C recipe + hotel bands;
  (04) → Step 6B retail bands; (06) → Step 4 gates + Step 7 normalization formula; (08) → Step 4
  training plan + regression gates; (07) → OPEN DECISION 7 verdict; (02)/(03) → Step 8 EUI gates;
  (10) → Step 8/9 reporting schema + paper positioning; (11)/(12)/(13) → the Step-4 design freeze
  (backbone, head representation, training regimen).
- Then freeze the Leg-3 design and start the build with Step 3 (the tiler delta).
