# GSSCanada research programme — factual digest for 5J planning

Read-only scan. All numbers below were read directly in the cited files; nothing is inferred or
carried from memory of the project outside these documents. Where a document is itself a Deep
Research report (the `RL*` files), treat its content as vetted-but-external — per project convention
these can still contain fabricated citations, so any citation drawn from an `RL*` file should be
re-verified before use in 5J.

---

## A. The four papers — question, data, method, scale, findings

### CENTUS (paper "1" in the 4J series-position table, PUBLISHED)
Iseri, Gursel Dino, Kalkan — *Occupancy modeling using population statistics and machine learning for
urban residential built environment*, **Energy and Buildings 357 (2026) 117155**. Italy, ISTAT Census +
Time Use Survey, LSTM/Transformer classification, 0.98 multitask accuracy. Made an **explicit but
untested claim** that HETUS standardisation makes the approach globally adaptable — this is the claim
4J was built to test. Source: `4J_docs_occ/4thJ_00_HETUS_LLM_Pipeline_Overview.md:9-16`.

### eSim 2026 conference paper (PUBLISHED)
Proof-of-concept GSS → occupancy schedule → EnergyPlus pipeline, Canadian residential. Validated
activity-based harmonization across 4 GSS cycles (2005/2010/2015/2022); demonstrated AT_HOME rate
2005: 63.5% → 2022: 72.3% (COVID signal). Source: `README.md:150-159`.

### 1J — *Longitudinal Analysis of Occupancy-Driven Energy Demand in Canadian Residentials* (UNDER REVIEW, target *Journal of Building Performance Simulation*)
Expanded Census–GSS pipeline + HPC BEM campaign (Calcul Québec/Speed) + paired Monte Carlo (frozen
IDF+TMY, occupancy varied) + activity-driven equipment/lighting loads. Source: `README.md:250-260`;
cited as "under review a" in `3J_docs_occ_nTemp/writing/submission/3J_manuscript_submission.md:865`.

### 2J — *From "How Much" to "When": Forecasting the Residential Energy Load Shape...(Canada, 2005-2030)* (SUBMITTED Building Simulation 2026-08-07, under revision)
**Data:** 4 GSS Time-Use cycles (64,061 diaries), 2021 Census PUMF (144,507 households 2005-2015;
144,465 refreshed 2022/2030 frame), NRCan SHEU-2019 as the end-use calibration benchmark.
**Method:** Conditional Transformer ("J3": 6-layer encoder + 6-layer AR decoder + parallel binary
heads, d_model=384, ~29.25M params) augments diaries to ~192,183 diary-days; probabilistic Census
linkage (Tier-1 44.94% / Tier-2 21.39% / Tier-3 33.67% / Tier-4 0.00%); progressive fine-tuning
2030 forecast under a single high-persistence WFH scenario; 6,000 paired frozen-frame EnergyPlus runs
(archetype+TMY+household-panel held constant, only occupancy time-series varied) isolate the pure
occupancy effect; Step 9 activity-driven end-use loads anchored to SHEU.
**Key numbers:** weekday at-home +5.2pp at COVID break, persists +2.2 to +3.9pp to 2030; annual
electricity moves only +1.4-2.6% across the break and +0.6-1.2% to 2030; midday-fill Δ+0.37pp,
Δload factor +0.012 (CIs exclude zero); evening peak fixed ~17:30 (peak-hour shift 0±1h, mean
−0.12h, σ=0.39h); activity-resolved end uses within ±2.7% of SHEU in all 48 dwelling×year cells
(max +2.33% equipment, +2.63% lighting); J3 validation gates: act_JS 0.019, AT_HOME_RMS 4.57pp,
co-presence max ~2.03pp. Source: `2J_docs_occ_nTemp/writing/chapters/Chapter_00_FrontMatter.md`,
`Chapter_08_Conclusion.md`, `README.md:265-283`.

### 3J — *From One Channel to Four...(Canada, 2005-2030)* (IN PREPARATION, manuscript drafted, target *Building and Environment*)
**Data:** same 4 GSS cycles + Census, provincial hotel-occupancy statistics (StatCan Table
24-10-0048-01, ISQ Quebec, CBRE Alberta), PNNL Tall/SuperTall mixed-use prototypes (Montreal
CZ6A, Calgary CZ7A), TMYx weather.
**Method:** shared-encoder three-head conditional Transformer (residential/office/retail) +
SARIMA side-track for hotel (no GSS code exists for hotel guests); Tag-2 per-space dispatch;
residential **replaces** baseline schedules, other 3 channels **modulate** NECB/90.1 code peak
densities; 56-cell campaign (4 channels × 2 prototypes × 2 cities, forecast 2005-2030).
**Key numbers (from the abstract, `3J_docs_occ_nTemp/writing/submission/3J_manuscript_submission.md:5`):**
four channels peak at different hours — hotel 18.91h vs a ~12h midday cluster for the other three;
whole-building coincidence factor <1 in all 4 cells, median 0.941; 3 of 4 channel EUI gates FAIL —
office 85.45 kWh/m²/yr vs floor 100 (fails even in the **uninjected control**, i.e. before any
occupancy signal); hotel gate splits into two prototype-driven clusters 84.64 kWh/m² apart (70.5%
of band width, ceiling sits inside the gap); retail median 5.47% below its floor. Leg2 (2-channel,
COMPLETE, paper-ready per README): 8,400 residential Monte Carlo cells + 252 office runs, Step-8
scorecard 46 PASS/1 WARN/13 INFO/0 FAIL, office median EUI ≈173 kWh/m². Source: `README.md:314-345`.

### 4J — *HETUS-Wide Occupancy Generation with a Fine-Tuned Open-Weight LLM* (IN PREPARATION, mid-build, manuscript text NOT yet written)
**Data:** HETUS, **3 countries only** — Italy 2013-14 (ISTAT), Spain 2009-10 (INE EET), UK 2014-15
(CTUR/NatCen); France excluded 2026-08-15 (no data-access arrival date; `Overview.md:22-31`).
Weather: AMY (actual meteorological year, ERA5 reanalysis) matched to each country's exact fieldwork
window, not TMY (`DeepResearchPrompts/RL27...md:1,34`).
**Method:** one open-weight LLM fine-tuned once (LoRA r=32, rsLoRA, all-linear), tested by strict
3-fold leave-one-country-out (LOCO); pre-named first fold = held-out Spain. Backbone = `allenai/
Olmo-3-1025-7B` (Leg-5, 7.30B params, reported) chosen because the OLMo/dolma2 tokenizer holds each
3-digit activity code as one token (~34% shorter sequences than Qwen); a `Qwen2.5-7B` comparison arm
and a `OLMo-2-0425-1B` (Leg-4, 1.48B) pilot are also run.
**The null the model must beat:** real diaries from the other 2 countries, demographically raked to
the held-out country ("the hard null is the aim, not an obstacle" — `Overview.md:71`).
**Key result — the headline gate FAILS.** `G6.1` (model MAE < raked-donor null, per age band) is
**FAIL 9/9** on Leg-5: the raked pool of real donor diaries reproduces the held-out country's time
budget **2 to 6× better** than the fine-tuned model on every band of every fold (e.g. `es` Y25-44:
model MAE 36.81 vs null 9.94, margin −26.9; `uk` Y_GE65 closest case, model 21.24 vs null 18.54,
margin still −2.70). Scaling the backbone 4.7× (1.48B→7.30B) bought nothing on this gate (mean MAE
42.05→43.14, 4 cells better/5 worse). `G6.4`, `G6.5`, `G6.6`, `G6.7`, `G6.9` also FAIL on Leg-5.
`G6.7` shows the model **does** respond to a conditioning vector, at roughly half the required
amplitude. Source: `4J_docs_occ/Step6_docs/4thJ_06_transfer.md:2898-2999`.
**Privacy audit (also part of the release decision):** membership-inference AUC `G6.10` = 0.6645
against pre-registered ≤0.65 bar → **FAIL**; perplexity-gap control 0.0570 against ≤0.05 → **FAIL**;
untrained-base floor clean at 0.4886 (makes 0.6645 readable as real membership signal); `G6.12`
(exact-match) 0/103 → PASS; `G6.13` 2 PASS / 1 FAIL (`uk` fails the size-matched arm). Verdict:
**weights are NOT released**; `uk` synthetic set withheld; `es`/`it` synthetic sets ship. Source:
`4J_docs_occ/writing/4thJ_writeup_notes.md:425-436`.
**Step 9 (end-use loads, heating-only) numbers, NOT released as a general EUI:** pooled 66.8677
kWh/m², min 29.5663/median 80.3233/max 222.2945, FR 55.4141/ES 87.2000 split — **must always carry
"heating-only"**, models contain exactly two end uses (heating + interior equipment electricity),
no TABULA/national-EUI/stock-level comparison is drawn. Source: `writing/4thJ_writeup_notes.md:315-320`.
**Real-stock campaign (Step 10):** two campaigns exist under one gate namespace convention — `C1`
core-era (410 cells, 18 PASS/2 FAIL/1 INFO/1 OPEN_INHERITED/2 NOT_EVALUABLE, **archived, closed,
NOT reported**) and `C2` no-core (gate series `G10N.x`, **spec only, no cell yet**, waiting on an
external OpenUBEM engine delivery). Source: `4J_docs_occ/4thJ_00_HETUS_LLM_Pipeline.md:3020-3070`.

---

## B. Data assets held

- **StatCan GSS Time-Use** (2005, 2010, 2015, 2022 cycles) — episode-level diaries. `README.md:143`.
- **StatCan Census PUMF** (2006, 2011, 2016, 2021/2025) — demographic frame. `README.md:144`.
- **StatCan Table 24-10-0048-01** — monthly hotel-occupancy series (3J hotel channel). `README.md:145`.
- **PNNL prototype buildings** — Tall/SuperTall mixed-use IDF prototypes, CZ6A/CZ7A. `README.md:146`.
- **HETUS microdata held on disk:** Italy TUS 2013 + 2023 zips (`4J_docs_occ/Datasets/IT TUS/`), UK-TUS
  zip (`4J_docs_occ/Datasets/UK-TUS-...zip`, 21.5MB), FR-TUS zip (**held but excluded from the
  corpus**), a `CensPop2011_1%_2011_IT` folder. Spanish INE EET 2009-10 microdata is used (per
  `DeepResearchPrompts/RL27...md:1`) but its on-disk path was not located in this scan.
- **TABULA/EPISCOPE** parameter workbooks — used to hand-build European EnergyPlus archetypes (no
  official European archetype library exists); licence checked open for academic re-use per
  `DeepResearchPrompts/RL27_hetus_weights_amy_weather_tabula_licence.md:1`.
- **ERA5 reanalysis (Copernicus C3S)** — open (CC-BY 4.0) hourly weather, used to build AMY EPW files
  matched to each country's exact fieldwork window. Same RL27 file.
- **Cluster:** Concordia Speed HPC, `o_iseri@speed.encs.concordia.ca`; sbatch-only, 7-day walltime
  floor, login node compute-forbidden. `CLAUDE.md:1-10, 130-137`.
- **EnergyPlus 24.2.0** (BEM engine, all three later papers); `energyplus_23.1.0.sif` container used
  for the Step-10 real-stock campaign on Speed. `README.md:59-62`; memory note 2026-08-28(last+27).
- **NRCan SHEU-2019** — national household end-use survey, the calibration/plausibility benchmark for
  2J's activity-driven loads. `2J_docs_occ_nTemp/writing/chapters/Chapter_00_FrontMatter.md`.
- Raw Census/GSS microdata and HETUS microdata are treated as **sensitive/restricted** — not
  committed, not redistributed; 4J's weights/adapters likewise withheld (data-agreement constraint,
  not model licence — `Overview.md:52-58`).

---

## C. Tooling / methodology built

- **Two occupancy pipelines**: classical tiered alignment/matching (06/11/16/21 CEN-GSS year pairs,
  4-tier fallback matcher) and the current ML pipeline (`25CEN22GSS_classification/`, Conditional
  Transformer + forecast). `README.md:159-200`.
- **Validation-gate methodology** (`G<step>.<n>` IDs), used identically across 2J/3J/4J: every step
  has a paired implementation doc + `_val.md` validation doc with thresholds, provenance, a
  perturbation/mutation table where **"every gate must be seen failing, and each perturbation must
  break exactly one gate"**, vacuity guards, and an explicit statement of what the validation does
  NOT cover. `4J_docs_occ/4thJ_00_HETUS_LLM_Pipeline_Overview.md:701`.
- **Pre-registration (`prereg.md`) practice**: thresholds and the held-out fold are frozen and
  md5-stamped before any scoring run; 4J's Step 6 `prereg.md` states the transfer bar in one sentence
  with "no weaker reading". `4J_docs_occ/Step6_docs/4thJ_06_transfer.md:2941-2943`.
- **3-fold leave-one-country-out (LOCO)** — 4J's core transfer-evaluation design (ES/UK/IT), each
  fold held out entirely from training. `README.md:405-407`.
- **Reversal-tracking documentation style** — decisions are amended in place with dated banners
  rather than rewritten, "so a superseded decision is normal" (4J convention). `README.md:412-414`.
- **Two-agent workflow** (Manager/Opus plans, Employee/Sonnet executes one task, writes an
  append-only Progress Log; no agent waits/polls; state lives on disk in `impl/<date>_<task>.md`
  files). `CLAUDE.md:96-129`.
- **Deep-research-as-external-tool workflow**: literature search/citation verification is never done
  in-repo; a prompt file is authored (`L<NN>_*.md`) and run externally (Gemini Antigravity), returning
  `RL<NN>_*.md`; every prompt requires CrossRef verification and warns fabricated citations are
  expected. `CLAUDE.md:139-141`; `4J_docs_occ/DeepResearchPrompts/README.md` (listing, not read in full).
- **"Never create images" workflow** — the assistant authors an image-generation prompt file,
  never draws; plots computed from frozen data by a script are the one exception. `CLAUDE.md:143-146`.
- **Gate/board artifact**: `4J_docs_occ/4thJ_CHECKLIST.html`, a live HTML gate-tracking board
  (12 groups / 143 items as of the last logged count), republished with `node --check` + a DOM-shim
  smoke test before every publish.

---

## D. Stated limitations / open leads / explicitly deferred or out-of-scope items

**4J-specific, from `Overview.md` LIMITATIONS table (`4J_docs_occ/4thJ_00_HETUS_LLM_Pipeline_Overview.md:652-668`):**
- **A1** — HETUS unit non-response 30-65%, diary non-response 10-25%, not correctable by
  post-stratification.
- **A2** — most cycles are 1-2 diary days/respondent (Spain and 1998-France are single-day); multi-day
  dependence largely unobservable.
- **A3** — hotel guests, institutional populations, homeless are outside every survey frame.
- **B1** — pretrained-model world knowledge is uneven across countries, weakest on the peripheral
  European countries transfer is most interesting for; pre-registered as a confound.
- **B2** — transfer scored against aggregates only, not microdata, for the widened (Track A) set.
- **C4** — corpus is only 3 countries, all Western/Southern European; LOCO trains on 2 only; "a
  reviewer can fairly ask whether transfer across... neighbours demonstrates transfer across a
  framework." A widened Track A corpus (17 countries via Eurostat SUF) is **explicitly the fix**,
  gated on Concordia becoming a Eurostat-recognised research entity (**F3**, filed but unresolved).
- **D1** — constrained decoding renormalisation is not neutral (reported, audited, not corrected).
- **D2** — post-hoc raking is deliberately NOT applied to model output (would weaken the claim).
- **E1** — activity-to-load mappings are validated at 100-500 dwelling aggregate scale, not per
  dwelling.
- **E2** — reproducibility is statistical, not bit-exact (GPU float non-associativity).
- **F1** — trained model/weights are not released (data-agreement, not licence, is the binding
  constraint); only ES/IT synthetic data + code ship.
- **F2** — European EnergyPlus archetypes are the authors' own TABULA-parameter construction (no
  official European archetype library exists).
- **F3** — Concordia is not yet a Eurostat-recognised research entity (blocks the 17-country corpus).

**Explicitly declared OUT OF SCOPE (not a limitation, a decision) — the single most important item
for 5J:** 4J carries **no forecast at all**. *"There is no forecast in this paper. Not deferred, not
attempted, not a limitation. Out of scope."* — the rationale given is that a weakly-supported
projection would hand a reviewer "the easiest possible thing to attack," and the paper's contribution
is the cross-national method itself. `4J_docs_occ/4thJ_00_HETUS_LLM_Pipeline_Overview.md:96,424,641`.
A Deep Research round (`DeepResearchPrompts/L16`/`RL16_longitudinal_and_forecasting_axis.md`) had
proposed a defensible route — Kitagawa-Oaxaca-Blinder shift-share decomposition of observed historical
change plus counterfactual scenario generation conditioned on official Eurostat EUROPOP2023 /
Cedefop / EU-LFS telework projections — but this was **not adopted**; the author ruled forecasting
out of scope entirely rather than build it. This is an unclaimed, previously-researched candidate for
a follow-on paper.

**4J's core transfer claim currently fails** (see §A) — `G6.1` FAIL 9/9, the raked-donor null beats
the fine-tuned model 2-6× on every band/fold, and scaling the backbone 4.7× did not help. The project
frames "the hard null is the aim, not an obstacle," so a failed transfer claim is being written up as
the finding itself, not hidden — but it means 4J's own manuscript will likely report **a negative
result on cross-national transfer with an LLM**, which is a very direct opening for 5J: what design
change (larger/more diverse corpus, different conditioning, different backbone class, hybrid
LLM+Transformer, RAG over exemplar diaries, etc.) would actually close that 2-6× gap.

**4J no-core geometry limitation** (added 2026-09-03, `D-IMP-1`): no circulation zone (stairwell/
corridor core) is modelled in the real-stock building campaign; "every square metre of every
simulated floor plate is conditioned dwelling," so heating demand is not directly comparable to a
core-modelled campaign. Literature range cited (not applied): unconditioned circulation cores are
commonly 6-12% of gross floor area in residential UBEM/TABULA literature.
`4J_docs_occ/writing/4thJ_writeup_notes.md:483-508`.

**3J limitations (16, Table 7 in the manuscript; discussion + conclusion quoted directly,
`3J_docs_occ_nTemp/writing/submission/3J_manuscript_submission.md:773-831`):** hotel guests and retail
staff structurally invisible to the survey frame; residential intra-household diversity partial
(3,499/16,367 multi-person households, 21.38%); office EUI floor "contested and unsourced"; hotel
reference band normalised to a city set the study doesn't share; retail validated on shape not level;
residential channel has no as-modelled EUI band; internal gains never parameterised by use;
ground-level weather file used on a supertall tower with no vertical variation. **Explicitly flagged
as what "a following study would need to build": reference bands constructed for, and validated
against, buildings that stack more than one use** (rather than borrowed from single-use stock) — a
direct, named opening for 5J.

**2J limitations/future work (7, Chapter_07; explicit next-steps list in Chapter_08 Conclusion,
`2J_docs_occ_nTemp/writing/chapters/Chapter_07_Limitations.md`, `Chapter_08_Conclusion.md`):**
metabolic/internal-gain channel not independently calibrated (activity-to-METs mapping only,
bounded but not benchmarked) — "an activity-side raking facility exists and could anchor the
metabolic mix **in future work**"; single Montreal Zone-6 envelope reused across 6 climate cities,
TMY (not future/climate-scenario) weather; single high-persistence WFH scenario only — a
high-reversion counter-scenario is named as "the natural sensitivity analysis... would convert the
point forecast into a bracketed range"; **explicit next-steps in the Conclusion**: "absolute future
demand should be projected with **future weather files and an evolving dwelling stock** rather than
the frozen-frame isolation used for attribution," plus a Saturday/Sunday split, sub-hourly reporting,
and **room-level or multi-zone occupancy** as resolution refinements.

**No "5J" name, no "next paper" language, and no other explicit forward-reference to a 5th paper was
found anywhere in the scanned corpus** (`4J_docs_occ/Prompts/RESUME.md` — 0 hits for "5J" across all
9,291 lines). Everything above is inferred from limitation/future-work language, not from an explicit
roadmap entry.

---

## E. Venue history

| Paper | Venue | Status (as documented) | Source |
|---|---|---|---|
| CENTUS (Italy, precursor) | *Energy and Buildings* 357 (2026) 117155 | **Published** | `Overview.md:14` |
| eSim 2026 conference paper | IBPSA-Canada eSim 2026 | **Published** | `README.md:35` |
| 1J (Canadian residential, HPC/validation) | *Journal of Building Performance Simulation* | Under review/evaluation | `README.md:36`, `3J...manuscript:865` |
| 2J ("How Much to When", load-shape forecast) | *Building Simulation* | **Submitted 2026-08-07**, under revision (per memory index; not independently re-verified in this scan) | `README.md:37`, `3J...manuscript:867` |
| 3J (4-channel mixed-use) | *Building and Environment* (target) | In preparation, manuscript drafted, not submitted | `README.md:38` |
| 4J (HETUS LLM) | *Energy and Buildings* primary / *Building and Environment* co-equal secondary (Deep-Research recommendation, `RL14`) — a paired data-descriptor in *Scientific Data*/*Data in Brief* is also floated | In preparation, pipeline mid-build, **manuscript text not yet written** | `README.md:39`, `DeepResearchPrompts/RL14_venue_positioning_and_novelty.md` §A/§C |

Note: `RL14` is a Deep Research report and its Section H reference list / DOIs were not independently
verified in this scan — per project rule, fabricated citations are expected in such reports until
CrossRef-checked.

---

## F. Climate change / future weather / heat / grid / health / equity / policy

- **No TMY-vs-future-year projection is attempted anywhere in the corpus.** 2J and 3J both use fixed
  Typical Meteorological Year (TMY/TMYx) files, one per city, held constant across all forecast years
  (2005-2030) — the forecast varies occupancy, never weather. 2J's Conclusion explicitly names
  "future weather files and an evolving dwelling stock" as work still to be done to project *absolute*
  future demand (currently out of scope; the paper isolates only the occupancy-attributable delta).
  `2J_docs_occ_nTemp/writing/chapters/Chapter_08_Conclusion.md`.
- **4J uses actual historical weather (AMY, ERA5 reanalysis), not TMY and not any future/climate
  scenario file** — chosen specifically to match each country's real survey fieldwork window
  (e.g. Spain 01/10/2009-30/09/2010), not for any climate-change purpose.
  `4J_docs_occ/DeepResearchPrompts/RL27_hetus_weights_amy_weather_tabula_licence.md:1,34,90`.
- **No heat-wave, decarbonisation, health, or equity content was found** in any file scanned
  (README, CLAUDE.md, RESUME.md, both Overview docs, writeup_notes.md, the 2J/3J manuscripts, or the
  4J Deep Research prompt/report set including L16/RL16 on forecasting and L27/RL27 on weather).
- **Grid/demand-response/code-standards discussion exists, but only in 2J**, §6.4 of
  `2J_docs_occ_nTemp/writing/chapters/Chapter_06_Discussion.md`: a stationary evening peak (~17:30)
  combined with a WFH-filled midday valley "reshapes the ramp into the evening peak and widens the
  midday window available for demand-response and distributed-generation absorption, without
  relieving the capacity constraint set by the evening coincident peak itself"; the paper argues for
  "schedule-shape recalibration synchronized with the national time-use survey cycle" in ASHRAE/NECB
  diversity-schedule practice, extending a prior (1J) proposal for a magnitude-only code-calibration
  factor to shape as well.
- **4J explicitly declined a forecasting/scenario axis** that a Deep Research round had proposed
  building on official EU demographic/labour projections (Eurostat EUROPOP2023, Cedefop Skills
  Forecast 2035, EU-LFS telework rates) — see §D above. This is the closest the corpus comes to a
  policy-projection angle, and it was a road not taken, not a road travelled.

---

**File written to:**
`C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\5J_docs_occ\DeepResearch\_scan\scan_gsscanada_progress.md`
