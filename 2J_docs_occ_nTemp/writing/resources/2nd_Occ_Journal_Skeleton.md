# From "How Much" to "When": Forecasting the Residential Energy Load Shape from a Calibrated Behavioural Occupancy Time-Series (Canada, 2005–2030)

**Document type:** Manuscript skeleton (Journal 2, GSS occupancy line) · **Status:** living draft · **Date:** 2026-06-10
**Departure point:** Iseri & Hachem-Vermette, *Longitudinal Analysis of Occupancy-Driven Energy Demand in Canadian Residentials* (JBPS, under review) + eSim 2026 conference companion + Iseri, Dino & Kalkan (2026, *Energy and Buildings*).
**Structure mirrors** the 1st journal skeleton (Abstract → Keywords → Highlights → §1–§8 → References → Appendices), with two structural upgrades: a standalone **Experimental Design** section (§4) and a standalone **Limitations** section (§7).

> **Trust-tag convention (carried through every section).**
> **✅ PROVEN** = verified on the corrected campaigns — Step-8 v2 (6,000/6,000 runs, validated 2026-06-10) and Step-9 (4,800 paired runs, verified 2026-06-10). All timing numbers are now unlocked.
> ~~**⚠ PENDING-RESIM**~~ → **RESOLVED 2026-06-10.** The Step-9 equipment/lighting re-simulation has landed; the formerly quarantined timing results are now verified and filled in. The historical quarantine is retained only as a methods-integrity note in §6.5 / §7.

> **How figures and tables are handled in this skeleton.** Every figure and table is (1) **cross-referenced in the prose** as `(Figure N)` / `(Table N)`, and (2) given a **standalone caption block** on its own lines — `**Figure N.** *(insert `internal_filename` here)* — full descriptive caption.` — independent of the surrounding paragraph, so you can paste the image directly under that line. **Methods figures (§2–§4) are flow/architecture schematics not yet drawn** — they are tagged *(to create)*. Results figures map to existing assets via the **backtick filename** (`fig01` … `figV1`), the authoritative bridge between a manuscript label (e.g. "Figure 9") and the asset on disk (e.g. `fig01`); these are deliberately *not* one-to-one, so always trust the backtick.

---

## Master figure & table inventory (build-as-you-go checklist)

**Main body figures**

| Label | §  | Internal asset | Full name (short) | Tag |
|---|---|---|---|---|
| **Figure 1** | §1.5 | pipeline overview | End-to-end pipeline, Steps 1–9 | *(to create)* |
| **Figure 2** | §2 | data-prep flow | Dataset preprocessing & harmonization flow | *(to create)* |
| **Figure 3** | §3.2 | J3 architecture | Conditional generator (calibrated J3) architecture | *(to create)* |
| **Figure 4** | §3.5 | schedule integration | Occupancy→EnergyPlus schedule integration | *(to create)* |
| **Figure 5** | §5.1 | `fig01` | Occupancy driver: diurnal at-home shift | ✅ |
| **Figure 6** | §5.2 | `fig10` | Annual EUI by archetype × city | ✅ |
| **Figure 7** | §5.3 | `fig02` | Diurnal electricity load, representative archetype/city (money plot) | ✅ v2 |
| **Figure 8** | §5.3 | `fig04` | Paired within-household Δ load by hour | ✅ v2 |
| **Figure 9** | §5.3 | `fig09` | Longitudinal load-shape trajectory (4 metrics, COVID break) | ✅ v2 |
| **Figure 10** | §5.3 | `fig08` | Stock-weighted ensemble load shape + coincidence factor | ✅ v2 |
| **Figure 11** | §5.4 | `figV1` | Default vs Step-9 activity-driven equipment (energy-conserving validation) | ✅ |
| **Figure 12** | §5.4 | `figS6` | Activity-driven equipment diurnal shape (null peak-shift) | ✅ |

**Main body tables**

| Label | § | Content | Tag |
|---|---|---|---|
| **Table 1** | §1.2 | Six-dimension gap matrix (competitor positioning) | — |
| **Table 2** | §2 | GSS cycle summary (n, exclusions, weighted AT_HOME, collection mode) | ✅ |
| **Table 3** | §4 | Simulation domain: archetype × city × climate zone | — |
| **Table 4** | §4 | Held-vs-varied paired frozen-frame design | — |
| **Table 5** | §5.2 | Annual EUI vs NRCan SHEU bands | ✅ |

**Supplementary figures**

| Label | Internal asset | Full name (short) | Tag |
|---|---|---|---|
| **Figure S1** | architecture-search funnel | Gated generative architecture search (40+ trials) | *(to create)* |
| **Figure S2** | linkage workflow | Census–GSS probabilistic linkage workflow | *(to create)* |
| **Figure S3** | forecasting schematic | Progressive fine-tuning + True-Future-Test | *(to create)* |
| **Figure S4** | end-use crosswalk | Activity-driven end-use load model structure | *(to create)* |
| **Figure S5** | `fig02b` | Diurnal electricity by archetype (4 panels) | ✅ |
| **Figure S6** | `fig03` | Peak-hour shift (histogram + clock plot) | ✅ v2 |
| **Figure S7** | `fig05` | Diurnal load by season × component | ✅ |
| **Figure S8** | `fig06` | Annual electricity carpet (day-of-year × hour) | ✅ |
| **Figure S9** | `fig07` | Paired Δ peak demand by archetype × climate zone | ✅ v2 |
| **Figure S10** | `figS1` | Equipment annual calibration vs SHEU ±15% band | ✅ |
| **Figure S11** | `figS3` | % deviation from SHEU, all 48 cell-years (the gate) | ✅ |
| **Figure S12** | `figS7` | Equipment baseline→activity peak-hour shift, all cells (null result) | ✅ |
| **Figure S13** | `figS8` | Activity-driven lighting diurnal shape | ✅ |
| **Figure S14** | `figS5` | 2022→2030 equipment differential, activity vs baseline | ✅ |
| **Figure S15** | `figS4` | Overnight equipment floor / sleep check | ✅ |

**Supplementary tables:** A1–A3 (loads), B1–B2 (model card / codebook), C1–C2 (validation), D (deviations) — detailed in the Appendices.

> **Calibration figures — resolved 2026-06-10.** The SHEU calibration figures do exist: `figS1` (per-cell annual equipment kWh, baseline vs activity, against the SHEU ±15% band) and `figS3` (% deviation from SHEU across all 48 cell-years, the calibration gate). They are now placed as Figures S10–S11. Together with `figV1` (Figure 11) and the EUI table (Table 5) they carry the magnitude claim. The Step-9 diagnostic figures `figS5` (2022→2030 differential) and `figS4` (overnight sleep-check) are added as Figures S14–S15.

> **Naming caution.** Manuscript supplementary labels ("Figure S10", "Figure S12") are **not** the same as the internal filenames in backticks (`figS1`, `figS7`). The crossing is unavoidable given the on-disk naming — always resolve via the backtick.

---

## Abstract (~150 words, 7 sentences, one per slot)

| # | Slot | Content seed | Tag |
|---|---|---|---|
| 1 | Context + gap | Stock-scale building energy models still run on static, pre-COVID occupancy schedules; what changed is *when* energy is used, not just how much. | — |
| 2 | Aim | Forecast the Canadian residential load shape (2005–2030) from a calibrated behavioural occupancy time-series, through the COVID/WFH structural break. | — |
| 3 | Method (data + model) | Four GSS Time Use cycles (64,061 diaries) harmonized, augmented with a gate-selected hybrid conditional Transformer (calibrated J3), linked to the 2021 Census stock (144,507 households), and forecast with progressive fine-tuning under a True-Future-Test protocol. | ✅ |
| 4 | Method (simulation) | 6,000 paired EnergyPlus runs (the same 50 households across five cycle-years; frozen archetypes and TMY weather) isolate the occupancy effect; activity-resolved end uses anchored to SHEU (48/48 cell-years within ±2.7%). | ✅ |
| 5 | Result, magnitude | Weekday at-home occupancy breaks +5.2 pp at COVID and persists to 2030 (+2.2 to +3.9 pp); annual electricity follows by only +0.6 to +2.6%. | ✅ |
| 6 | Result, timing (the headline) | The load *shape* changes structurally: midday fill and flattening (Δmidday_share +0.37 pp; Δload_factor +0.012; both CIs exclude zero) while the evening peak stays at ~17:30; activity-resolved end uses then restructure the intraday equipment profile without displacing its evening peak (building-level shift 0 ± 1 h). | ✅ |
| 7 | Implication | Time-varying, survey-grounded schedules are feasible at stock scale and materially change ramping and demand-response-relevant load metrics that static schedules cannot see. | — |

**Abstract structure check (skill rule):** Context → Gap → Methodology → Key quantified results → Impact. ✔

## Keywords

Occupancy Modeling; Building Performance Simulation; Time-Use Survey; Load Shape; Peak Demand; Coincidence Factor; Conditional Transformer; Generative Deep Learning; Longitudinal Forecasting; COVID-19 / Work-From-Home; Canadian General Social Survey (GSS); Residential Building Stock; EnergyPlus

## Highlights (5 bullets, ≤85 characters each, every number ✅-verified)

* Gate-selected Transformer augments 64,061 GSS diaries into ~192k calibrated diary-days.
* 2030 occupancy forecast through the COVID/WFH break with a True-Future-Test protocol.
* 6,000 paired EnergyPlus runs isolate the pure occupancy effect at building-stock scale.
* WFH fills the midday valley and flattens load; the ~17:30 evening peak does not move.
* Activity-resolved end uses match SHEU within ±2.7% in all 48 dwelling-by-year cells.

---

# 1 Introduction

**Funnel (six paragraphs):** problem → field split → non-stationarity → our prior line → the four deltas → aim + roadmap. Target ≤1.5 pages. Sections marked **◄prior-pub** are adapted (compressed, citations refreshed) from the 1st journal.

### 1.1 The Performance Gap and Static Occupancy Schedules **◄prior-pub**

Predicted-versus-measured gap (de Wilde 2014); occupant behaviour as the dominant unexplained driver (Yan et al. 2015; IEA EBC Annex 66/79); practice still leans on static ASHRAE/NECB diversity profiles. Reuse the 1st journal's opening case compressed into one subsection: deterministic schedules miss behavioural stochasticity, with discrepancies up to 41%. New emphasis: static schedules are blind not only to *magnitude* error but to *timing* error, the quantity that matters for grids, ramping, and demand response.

### 1.2 Two Tracks That Rarely Meet: High-Fidelity Occupant Models vs Stock-Scale Engines

Track (a): high-fidelity stochastic occupant models, single-building and retrospective (Richardson et al. 2010; Widén & Wäckelgård 2010; Wilke et al. 2013; Aerts et al. 2014; Canadian: Armstrong et al. 2009; Osman et al. 2023; Ferreira et al. 2024). Track (b): stock/urban-scale engines on simplified baseline-year schedules (Reinhart & Cerezo Davila 2016; Chen et al. 2022 as the closest competitor). The two tracks rarely meet, which the six-dimension gap matrix (Table 1) makes explicit. Reading of the matrix: Chen et al. (2022) is closest but retrospective; Yin et al. (2025) is closest on forecasting but stops at statistical probability modelling with no bottom-up simulation. The open cell is forecast-to-2030 through the WFH break plus stock-scale paired BEM simulation of the resulting load shape. *(Write fresh from DR-X1; matrix lists external competitors only.)*

**Table 1.** *(insert six-dimension gap matrix here)* — External competitors scored against six capabilities (time-series occupancy / calibrated behavioural model / forecast to future year / activity- and end-use-resolved / stock-scale / load-shape and peak focus); the all-✓ row "This study" identifies the open cell.

### 1.3 Behaviour Is Non-Stationary and the Field Forecasts off the Wrong Baseline

COVID/WFH is a structural break, not a transient: WFH settled at roughly twice the pre-pandemic norm (Barrero, Bloom & Davis 2021; Guo et al. 2026); weekday smart-meter profiles took on a weekend shape with weather-adjusted +7.9% residential electricity (Cicala 2023); occupancy forecasting through the break is the flagged open problem (Yin et al. 2025; Bielskus et al. 2021). Any 2030 projection from a pre-COVID baseline inherits the break as bias. *(Also motivates the journal choice; keep Cicala's +7.9% as the grid-relevance hook.)*

### 1.4 The Authors' Prior Line: The Departure Point **◄prior-pub**

One paragraph maximum. State the C-VAE pipeline (JBPS under review; eSim 2026; Iseri, Dino & Kalkan 2026) and what it established: time-series GSS occupancy in Canadian BEM, annual heating/cooling effects (+4 to 13% heating, −10 to 27% cooling vs defaults), and first-look diurnal/peak effects. **Do not re-claim its novelty.** Footnote (not body text) the two self-delta cross-checks: (a) the prior journal independently places the equipment peak at 17:00–18:00, the clock-correct anchor this paper's corrected pipeline reproduces; (b) the conference paper's descriptive "−4 h peak-occupancy" argmax difference is unrelated to any converter artefact, keep the two distinct.

### 1.5 Contributions and Aim of the Study

The four deltas over the prior line, one sentence each:

1. **Generator.** C-VAE → a hard-gate-selected hybrid AR/NAT conditional Transformer with post-hoc marginal calibration ("calibrated J3"), the only 4/4-gate model in a 40+ trial search that included masked discrete diffusion (MDLM/SEDD); preserves the sharp activity peaks a VAE smooths.
2. **Loads.** Presence-filtered defaults → an SHEU-calibrated, activity-resolved bottom-up end-use model (presence + co-presence + equipment), 48/48 cell-years within ±2.7% (max +2.33% equipment, +2.63% lighting).
3. **Horizon and validation.** 2025 hindcast → 2030 forecast *through* the structural break, validated with a True-Future-Test.
4. **Attribution.** SSE-matched per-scenario ensembles → a paired within-household Monte-Carlo design (the same 50 households across all five cycle-years; 6,000 runs).

**Aim statement (final paragraph, explicit per skill rule):** *This paper asks whether, and when, forecast behavioural change reshapes the residential load curve at stock scale.* The full pipeline is summarized in Figure 1, with each stage detailed in Sections 2–4. Then the roadmap sentence (§2–§8).

**Figure 1.** *(insert pipeline overview diagram here — to create)* — **End-to-end occupancy-to-energy pipeline (Steps 1–9).** Block schematic from the four GSS Time-Use cycles and Census PUMF through harmonization and 30-min diary construction, generative day-type augmentation, Census linkage, longitudinal forecasting to 2030, BEM schedule conversion, paired Monte-Carlo simulation, and activity-resolved end-use loads; each block labelled with its section number and the key validation gate it passes.

---

# 2 Datasets

The dataset inventory is summarized in Table 2; the preprocessing path from raw microdata to analysis-ready diaries is shown in Figure 2.

| Sub | Content | Key facts to carry | Source |
|---|---|---|---|
| 2.1 | **GSS Time Use cycles 2005/2010/2015/2022** | 64,061 valid diaries post 1,440-min closure filter (19,221 / 15,114 / 17,390 / 12,336); DIARY_VALID exclusions 1.92 / 1.79 / 0.00 / 0.00%; weighted AT_HOME 62.7 / 62.3 / 64.5 / 70.6% (2022 spike = COVID). Footnote: SURVMNTH absent 2005/2010 → DDAY_STRATA (Weekday/Sat/Sun). State the CATI→EQ mode shift here, dispose of it in §7. | Step 1–2 docs |
| 2.2 | **Census PUMF 2021** (2006/2011/2016 context) | Dwelling-stock variables; used only for the Step-5 linkage to the 144,507-household BEM frame. | Step 1C / 5 docs |
| 2.3 | **NRCan SHEU 2019** | End-use calibration anchor: per-dwelling equipment targets (SingleD 3,700 / OtherDwelling 3,139 / MidRise 2,166 / HighRise 1,922 kWh) and lighting targets (1,262 / 1,100 / 736 kWh). | Step 9 docs |
| 2.4 | **Weather and archetypes (pointer to §4)** | TMY EPWs for six cities; Canadian NECB17/NBC936 Z6 code archetypes; EnergyPlus v24.2. | 08_simulation.md |

**Table 2.** *(insert GSS cycle summary here)* — Per-cycle respondent counts, DIARY_VALID exclusion rate, weighted at-home fraction, collection mode (CATI vs electronic questionnaire), and TUI_10 availability across the four GSS Time-Use cycles, with column totals.

**Figure 2.** *(insert dataset preprocessing diagram here — to create)* — **Dataset preprocessing and harmonization flow.** Raw GSS Main and Episode files plus Census PUMF across the four cycles, through cross-cycle schema harmonization to the common 14-category activity scheme, episode-to-HETUS 144×10-min tiling, and presence-priority majority-vote downsampling to the analysis-ready 48×30-min diary; annotated with per-cycle sample sizes, the 1,440-min closure filter, and the 04:00→00:00 clock convention.

*(SI: 14-category activity codebook → Table B2; crosswalk magnitudes 182/264/64/121 raw codes → 14 categories, zero conflicts; co-presence 10 raw → 9 unified columns, `colleagues` not collected 2005/2010.)*

---

# 3 Methods

One condensed subsection per pipeline stage; each carries (i) the design choice, (ii) the precedent, (iii) the validation number. The generator architecture is shown in Figure 3 and the occupancy-to-simulation coupling in Figure 4; supporting workflow schematics for the search, linkage, forecasting, and load model sit in the Appendices (Figures S1–S4).

### 3.1 Harmonization and 30-Minute Diary Construction (Steps 2–3)

Ex-post output harmonization of four cross-sections to a common 14-category activity scheme (Eurostat 2018); 0.00% unmapped all cycles ✅. Episode→HETUS 144×10-min tiling, then presence-priority majority-vote downsampling to **48×30-min slots** (the documented optimal accuracy/cost compromise; a 9× attention-cost reduction); 3-way tie rate 0.82% (the full path is drawn in Figure 2). The mandatory 04:00→00:00 circular shift to the simulation clock is stated here as method (Aerts et al. 2014; HETUS); enforcement is part of the §6.5 validation story. SEASON dropped (JS < 0.001); DDAY_STRATA = {Weekday, Saturday, Sunday}.

### 3.2 Day-Type Augmentation: Gate-Selected Generative Model (Step 4)

Problem: each respondent contributes one observed day-type; the other two are synthesized. The generator architecture is given in Figure 3 and the model card in Table B1: shared 6-layer encoder + 6-layer AR activity decoder + parallel non-autoregressive binary heads behind a detach barrier; d_model 384, ~29.25M parameters; conditioning d_cond = 90 incl. demographics, cycle-year, COLLECT_MODE, ATTSCH/**POWST (work-from-home)**/MODE.

Frame as gate-based model selection over a broad generative search (the funnel is shown in Figure S1): 40+ trials in a progressive 2%→20%→100% data funnel spanning Markov, AR, VAE, GAN-adjacent, cross-attention, and masked discrete diffusion families. Hard gates: activity JS ≤ 0.05, AT_HOME RMS ≤ 5.3 pp, co-presence max ≤ 5.0 pp. **Calibrated J3 was the sole 4/4-gate model** (act_JS 0.0191; AT_HOME RMS 4.57 pp; co-presence max ~2.03 pp) ✅. Reportable negative finding: MDLM produced the best composite (0.559) yet failed 2/4 gates; best-training-loss cross-attention decoders collapsed 20+ pp on co-presence at inference. Post-hoc per-(cycle×stratum×slot) raking (Phase-8B); coherence cost ~1.8–2.1% of slot records, BEM-harmless. Output: **~192,183 diary-days** ✅.

**Figure 3.** *(insert J3 architecture diagram here — to create)* — **Conditional generator (calibrated J3) architecture.** Shared multi-head Transformer encoder over the 48-slot multivariate diary token stream, an autoregressive activity decoder, and parallel non-autoregressive binary heads for AT_HOME and the nine co-presence channels behind a gradient-detach barrier; the conditioning vector (demographics, cycle-year, COLLECT_MODE, ATTSCH/POWST/MODE) injected at both encoder and decoder, and the post-hoc per-(cycle×stratum×slot) marginal raking shown as the terminal calibration block.

### 3.3 Census–GSS Probabilistic Linkage (Step 5)

Slot-native 4-tier hierarchical demographic key-descent match (each of 286,537 Census individuals draws one augmented diary row by descending key specificity) — a probabilistic statistical/hot-deck linkage (Rässler 2002; D'Orazio et al. 2006; Beckman et al. 1996; Putra et al. 2021); the workflow is drawn in Figure S2. **NOTE: this replaces the superseded K-means→Random-Forest archetype scheme of the 1st-journal pipeline — the 2J Step-5 code (`05_census_linkage.py`) uses tiered matching, not clustering.** Report the 7 match keys (AGEGRP, SEX, MARSTH, HHSIZE, LFTAG, PR, CMA + day-type stratum) and the four tiers: Tier-1 Perfect (all 7 + stratum) 44.94% / Tier-2 Core (AGEGRP, SEX, LFTAG, PR + stratum) 21.39% / Tier-3 Constraints (AGEGRP, SEX + stratum) 33.67% / Tier-4 FailSafe (stratum only) 0.00% (never invoked). Dwelling variables carried directly from the matched Census record; HH aggregation = per-slot MAX AT_HOME. Plausibility gate removes 1,082 households → **final frame 144,507 households** ✅. The CIA caveat is stated here in one sentence and disposed of in §7.

### 3.4 Longitudinal Forecasting to 2030 (Step 6)

Progressive fine-tuning with weight inheritance (2005 → +2010 → +2015 → +2022), a DRIFT_MATRIX at each transition, recency-weighted pooling (0.10/0.20/0.30/0.40), and demographic scenario injection for 2030 (StatCan M1; AGEGRP resampling; **37,008 diary-rows**); the protocol is shown in Figure S3. Framing: progressive FT + recency weighting tracks real concept drift P(Y|X); scenario injection handles virtual drift P(X) (Gama et al. 2014). Validation = True-Future-Test: WD JS 0.0630 PASS; the weekend 0.16 ceiling is data-intrinsic (observed-only rows 0.036–0.046) ✅. The single high-persistence scenario (p = 1) is named here, bounded in §7.

### 3.5 Conversion to BEM Schedules (Step 7)

Per-household EnergyPlus `Schedule:Compact` at 30-min resolution for occupancy, metabolic, equipment, lighting; activity→MET per ASHRAE 55 / ISO 7730 / 2024 Compendium; the integration logic is shown in Figure 4. Donor-draw day-completion preserves the calibrated weekend marginal. Per-cycle raking (diary basis 70.4 → 78.4%) makes 2005→2030 one uniform procedure; the standardized series (64.2 / 64.2 / 63.3) is the compositional control quoted in §5.1. The 4-h circular rotation is applied on all four channels (`np.roll(..., 4)`).

**Figure 4.** *(insert schedule-integration diagram here — to create)* — **Occupancy-to-EnergyPlus schedule integration.** The predicted 30-min AT_HOME and 14-category activity sequence mapped to the four EnergyPlus `Schedule:Compact` channels (occupancy, metabolic, equipment, lighting), with the mandatory 04:00→00:00 circular shift aligning the diary origin to the simulation clock, the activity→MET assignment, and the donor-draw day-completion that preserves the calibrated weekend marginal.

### 3.6 Activity-Resolved End-Use Loads (Step 9)

Two-tier structure (flat baseload: fridge 448 + freezer 343 + standby ≈400–430 kWh/yr; transient activity tier via a 9-end-use × 14-activity crosswalk, Tables A1–A3); the model structure is drawn in Figure S4. Co-presence scales shared devices sub-linearly (EFF(N) = 1.0/1.4/1.7/1.9/2.0), personal devices linearly (Richardson et al. 2010; Yamaguchi & Shimoda 2017). Per-end-use SHEU scalar: f_e = SHEU_target_e(dwelling) / simulated_annual_e, baseload held fixed. Lighting as-built: binary occupied-and-awake × SHEU scale, no daylight gate (R1). The Step-9 layer was executed as **4,800 paired baseline-vs-activity runs (4,795 with meters; validation 6 PASS / 1 WARN / 3 INFO / 0 FAIL, verified 2026-06-10)**. Positioning: a precedented *adaptation* driven by externally-predicted activities, not a novel load-modelling method.

---

# 4 Experimental Design

*The paired Monte-Carlo design is a contribution in its own right; standalone section (upgrade vs the 1st journal).*

The simulation domain (archetypes, cities, climate zones) is given in Table 3, and the paired frozen-frame logic in Table 4. The factorial is 4 archetypes (SingleDetached, OtherDwelling/attached, MidRise, HighRise; Canadian NECB17/NBC936 Z6 archetypes, *not* DOE prototypes) × 6 climate-zone cities (Toronto 5A, Kelowna 5B, Vancouver 5C, Montréal 6A, Calgary 6B, Winnipeg 7A; Atlantic mapped to the Montréal EPW, a stated limitation) × 5 years (2005/2010/2015/2022 calibrated + 2030 forecast) × 50 paired households = **6,000 EnergyPlus v24.2 runs** ✅. The held-versus-varied logic (Table 4): hold the IDF, the TMY weather, and the household IDs fixed, and vary only the occupancy time-series. Every SIM_HH_ID exists in all five years, so within-household differencing cancels envelope, climate, and stock turnover, and removes between-household MC sampling variance; the cross-year Δ is purely the predicted behavioural change with tight CIs (Chen et al. 2022; DR-S8). Outputs are 8,760-h load profiles + MC bands, load-shape metrics (load factor, midday share, peak-to-average, coincidence factor), peak-hour statistics, the stock-weighted ensemble, and annual EUI as the secondary plausibility anchor. MC convergence: 95% CI half-width mean 1.80%, worst cell 4.04% at N = 50 ✅. Methods footnote: 1 of 6,000 runs needed a deterministic DX-coil sizing fix (Sub-step 8G); effect ≤0.013 kWh/m².

**Table 3.** *(insert simulation-domain table here)* — The 4 archetypes × 6 cities matrix with each city's ASHRAE climate zone, representative TMY weather file, and the NECB17/NBC936 Z6 code archetype geometry/envelope assumptions; the 24 archetype-by-city cells simulated per year.

**Table 4.** *(insert held-vs-varied table here)* — Factors held constant (archetype IDF, TMY weather file, household IDs) versus the single varied factor (occupancy time-series) across the five cycle-years, with the resulting 6,000-run factorial and the within-household differencing logic.

---

# 5 Results

**Narrative arc = the title promise.** Four sub-questions climbing from "how much" to "when"; each subsection opens with one sentence restating its sub-question, carried by **one primary figure + one headline statistic**. Lead every paired result with the CI.

### 5.1 What Changed in Behaviour? (the driver)

Sub-question: did occupancy itself shift? The COVID break is the dominant behavioural signal, +5.2 pp weekday at-home (WD +6.6 pp) at 2015→2022, persisting +2.2 to +3.9 pp to 2030; the more recent cycles sit visibly higher through the midday "everyone out" trough, the signature of a flattening daytime absence (Figure 5). The gentle pre-COVID drift is shown to be compositional (sample aging) via the AGEGRP×SEX×LFTAG standardization check, not behavioural. ✅

**Figure 5.** *(insert `fig01` here)* — **Occupancy driver: diurnal at-home shift.** Average fraction of households at home across the hours of the day, weekday and weekend panels, one line per survey/forecast cycle (2005–2030), with the work-from-home midday window shaded; the behavioural starting point that the rest of the analysis traces into electricity demand.

### 5.2 How Much Energy Follows? (magnitude + credibility anchor)

Sub-question: does the shift move annual energy, and is the model plausible? Annual electricity follows the behavioural break by only +1.4 to +2.6%, and +0.6 to +1.2% to 2030; the annual EUI lands at 208 / 152 / 128 / 117 kWh/m² (SingleD / MidRise / OtherDwelling / HighRise), every cell inside the NRCan SHEU plausibility bands (Figure 6, Table 5). ✅ Put the EUI evidence early: it buys reader trust before the timing claims.

**Figure 6.** *(insert `fig10` here)* — **Annual energy use intensity by archetype and city.** Grouped bar chart of annual EUI for every archetype-and-city combination, paired bars for the recent observed cycle versus the 2030 forecast with error bars; the annual-total accounting view answering whether the behavioural shift moves total consumption or only redistributes it within the day.

**Table 5.** *(insert annual EUI table here)* — Stock-weighted annual EUI per archetype against the NRCan SHEU plausibility bands, ordered by envelope-to-occupant ratio (colder zones higher).

### 5.3 When Does the Load Move? (the headline)

Sub-question: does behaviour reshape the diurnal curve and peak? The peak hour is stable at 17.5–17.7 h across all five years; the effect is midday fill and flattening, not peak displacement (Figure 7, the representative-dwelling overlay). The paired within-household differential confirms it (Figure 8): Δmidday_share +0.367 pp, CI [+0.208, +0.526]; Δload_factor +0.0117, CI [+0.0085, +0.0150], both excluding zero. The longitudinal trajectory of the four shape metrics places this comparison in its multi-cycle context, with the COVID break marked (Figure 9), and the stock-weighted ensemble carries the same reshaping up to the system level, where the coincidence factor measures how sharply individual peaks coincide (Figure 10). ✅ v2. Report peak-hour *stability* as a finding, not a null: "WFH fills the midday valley without moving the evening peak" is the grid-relevant sentence. Give this subsection the most figure real estate; Figure 7 is the money plot.

**Figure 7.** *(insert `fig02` here)* — **Diurnal electricity load, representative archetype and city.** Average hourly electricity demand over a day for a single representative archetype-and-city combination, most recent observed cycle versus the 2030 forecast, each with a shaded uncertainty band; the "one curve" anchor showing a low overnight base, a gentle daytime rise, and a pronounced evening peak, and whether the projected change is large relative to the household spread.

**Figure 8.** *(insert `fig04` here)* — **Paired within-household Δ load by hour.** Average hour-by-hour difference in electricity demand between the forecast cycle and the recent cycle, computed as a paired within-household change with a confidence band; read against the zero line, the work-from-home midday window highlighted to show where any daytime gain concentrates. The most statistically careful view of which hours are responsible for the change.

**Figure 9.** *(insert `fig09` here)* — **Longitudinal load-shape trajectory.** Four summary load-shape metrics (midday energy share, load factor, peak-to-average ratio, and mean peak hour) across all cycles from the earliest to the forecast year, each in its own panel with error bars and a marked COVID break; frames the recent-to-forecast comparison as one step in a multi-cycle evolution rather than an isolated jump.

**Figure 10.** *(insert `fig08` here)* — **Stock-weighted ensemble load shape and coincidence factor.** Stock-weighted ensemble daily load shape (every archetype and city combined in proportion to its share of the stock) for the recent cycle and the forecast, with the coincidence factor annotated for each; moves the household-level story to the aggregate-system scale a utility or grid planner cares about.

### 5.4 Does Activity Resolution Sharpen the Picture? (end-use)

Sub-question: what does the activity model add over presence-only? On magnitude, the activity-driven reshaping conserves annual energy and the single-detached panel sits on the survey-based annual anchor, confirming the schedules are a faithful, energy-conserving replacement for the defaults rather than an arbitrary rescaling (Figure 11); all 48 dwelling-by-year cells fall within ±2.7% of SHEU (max +2.33% equipment, +2.63% lighting; Figures S10–S11), and the activity model corrects the presence-only baseline's over-prediction of detached/attached plug load (baseline ≈6,550–6,870 kWh vs SHEU 3,139–3,700). ✅ On shape and timing, deriving equipment use from modelled activity produces a different intraday profile than a fixed schedule — a more pronounced morning rise and a sharper evening concentration — but it does *not* move the peak: across all 24 archetype-by-city cells the building-level equipment peak shift is 0 ± 1 h (mean −0.12 h, σ = 0.39), both arms cresting in the evening (equipment h17–18, lighting h18–21; Figure 12). ✅ verified 2026-06-10. **Frame this honestly as a null peak-shift result:** Step-9's contribution is end-use magnitude correction plus behaviourally-timed intraday shape, not peak displacement; the paper's timing headline remains Step-8's WFH midday fill at a stable ~17:30 peak. The earlier "~4 h earlier" equipment peak was the schedule-injection bug, now corrected and gone.

**Figure 11.** *(insert `figV1` here)* — **Default versus Step-9 activity-driven equipment demand (validation).** One panel per archetype: the single-detached panel in absolute terms with the annual total held to the survey-based energy anchor, the remaining archetypes normalized to their daily mean, each overlaying the default curve against the activity-driven curve with peak-hour markers; establishes that the reshaping redistributes *when* energy is used without inflating *how much*.

**Figure 12.** *(insert `figS6` here)* — **Activity-driven equipment diurnal load shape (corrected re-sim).** Daily shape of equipment (plug-load) demand, one panel per archetype, each curve normalized to its own daily mean, baseline shape versus activity-driven shape with a peak-hour marker for each and the baseline-versus-activity peak-hour pair annotated; the activity curve carries a more pronounced morning rise and a sharper evening concentration, yet both curves peak at essentially the same evening hour. Communicates shape and timing, not magnitude. ✅ verified 2026-06-10 (regenerated from the corrected campaign; the pre-fix earlier-peak reading was the injection artefact and is gone).

---

# 6 Discussion

Five-paragraph arc, each with anchor citations:

1. **Principal finding against the gap matrix.** The open cell of Table 1 is filled: a calibrated behavioural forecast, run through paired stock-scale simulation, shows the COVID/WFH break changes load *shape* (Figures 7–10) far more than annual magnitude (Figure 6). Position against Chen et al. (2022, retrospective) and Yin et al. (2025, no bottom-up simulation).
2. **Positioning against literature numbers.** Occupancy-channel-only deltas (+1.4 to 2.6%) are deliberately conservative against Cicala's all-cause +7.9%; the at-home persistence aligns with Barrero-Bloom-Davis and Khalil & Fatmi's ~+12% structural in-home demand.
3. **What activity resolution adds.** Beyond presence: corrects the detached plug-load over-prediction and conserves annual energy (Figure 11), and restructures the intraday equipment profile (sharper morning rise and evening concentration) while leaving the building-level peak hour unchanged — a verified null peak-shift of 0 ± 1 h across all 24 cells (Figure 12). State this plainly rather than spinning it as a positive timing finding; the value is end-use magnitude correction plus behaviourally-timed shape, and co-presence enters as a load-shaping refinement (shared/personal device scaling), claimed honestly as such.
4. **Grid, code, and standards implications.** Stationary evening peak + midday fill, read at the fleet level through the coincidence factor (Figure 10), carries ramping and DR-window consequences; connect to the prior journal's code-calibration-factor proposal and extend it to *schedule-shape* recalibration synchronized with national survey cycles.
5. **Methodological reflection.** The paired within-HH design makes a small signal readable (CIs exclude zero at n = 50/cell; Figure 8). The 4-h phase bug episode is presented as validation rigor: a documented community pitfall (04:00 diary origin; Aerts et al. 2014; HETUS), invisible to annual-energy gates (phase-invariance; Chen et al. 2022), caught by an independent phase check, repaired by full re-simulation. Hand transferability limits to §7.

---

# 7 Limitations

One paragraph each, every limitation paired with its disposition:

1. **Schedule-injection bug (fixed, both campaigns re-simulated).** Step-8 v2 and Step-9 both re-run and verified (2026-06-10); annual/calibration results were never affected (phase-invariant), and the corrected timing is now part of the results.
2. **Metabolic channel un-calibrated** (rides raw J3 activity mix); occupancy, the dominant gain driver, *is* calibrated; ASHRAE 55 / ISO 7730 grounding; activity-side rake available.
3. **Sat+Sun pooled to "Weekend"; hourly E+ reporting.** 30-min is the documented optimal compromise; finer data preserved upstream.
4. **Single MTL Z6 envelope across six climates; frozen 2022 stock; TMY weather.** Deliberate isolation choices; the paired Δ cancels the envelope; Z7A cold-zone EUI sensitivity available.
5. **Statistical-matching CIA risk (Step 5).** Mitigated by a parsimonious predictive match vector and probabilistic carrying; report match tiers.
6. **Survey mode shift (CATI→EQ).** Absorbed by harmonization + per-cycle calibration, conditioned on via COLLECT_MODE; the COVID break dwarfs plausible mode effects.
7. **Single COVID-persistence scenario (p = 1).** Framed as the high-persistence bound; a high-reversion counter-scenario is the natural sensitivity, ideally added before submission, at minimum stated as scope.

---

# 8 Conclusion

One aim-recap paragraph + numbered findings + one future-work paragraph. **No new citations, no new numbers; every figure quoted here must already appear in §5.**

> *Recap seed:* This paper asked whether a calibrated, behaviourally-grounded occupancy time-series, built from four GSS cycles, augmented by a gate-selected conditional Transformer, linked to the Census stock, and forecast through the COVID/WFH structural break, changes *when* Canadian residential energy is used, not just *how much*.

1. An end-to-end national pipeline (64,061 diaries → 144,507 households → 6,000 paired EnergyPlus runs) produces physically plausible energy at stock scale (all EUI cells within SHEU bands; Figure 6, Table 5).
2. The COVID break is the dominant behavioural signal (+5.2 pp weekday at-home; Figure 5), persists to 2030 (+2.2 to +3.9 pp), and is separable from compositional aging.
3. The load-shape consequence is midday fill + flattening with a stationary ~17:30 evening peak (Figures 7–10; CIs exclude zero); annual magnitude moves little (+0.6 to +2.6%; Figure 6).
4. Activity-resolved end uses reproduce SHEU within ±2.7% in all 48 cell-years (max +2.33% equipment, +2.63% lighting) and correct the presence-only baseline's detached plug-load over-prediction while conserving annual energy (Figure 11); the activity arm restructures the intraday shape but leaves the building-level equipment peak hour unchanged — a verified null peak-shift of 0 ± 1 h (Figure 12). The paper's timing headline is Step-8's; Step-9 delivers magnitude calibration and behaviourally-timed shape, not peak displacement.
5. The paired within-household Monte-Carlo design (Table 4) attributes these shifts to occupancy alone, with envelope, weather, and stock held fixed.

> *Future work seed:* bounded persistence scenarios for 2030; future weather files + stock turnover; metabolic-channel calibration; Saturday/Sunday split and sub-hourly resolution; room-level / multi-zone occupancy.

---

## References (anchor groups; full verified list with DOIs lives in the methodology assessment Part 5)

- **Self-citations (the departure point):** Iseri & Hachem-Vermette (JBPS, under review); Iseri & Hachem-Vermette (eSim 2026); Iseri, Dino & Kalkan (2026, *Energy and Buildings*).
- **Performance gap / occupant behaviour in BPS:** de Wilde 2014; Yan et al. 2015, 2017; O'Brien et al. 2020; Hong et al. 2016.
- **TUS-based occupancy (incl. Canadian):** Widén & Wäckelgård 2010; Wilke et al. 2013; Aerts et al. 2014; Armstrong et al. 2009; Osman et al. 2023; Ferreira et al. 2024; Chiou 2009; Eurostat HETUS 2018/2020.
- **Generative models (Step 4):** Austin et al. 2021; Sahoo et al. 2024; Lou et al. 2024; Lamb et al. 2016; Dahlström et al. 2024.
- **Statistical matching (Step 5):** Rässler 2002; D'Orazio et al. 2006; Beckman et al. 1996; Putra et al. 2021.
- **Forecasting / drift / WFH persistence (Step 6):** Gama et al. 2014; Kirkpatrick et al. 2017; Yao et al. 2022; Barrero, Bloom & Davis 2021; Cicala 2023; Guo et al. 2026; Khalil & Fatmi 2022; Yin et al. 2025; Bielskus et al. 2021; Ramirez-Aguilar et al. 2023; StatCan projections / Demosim.
- **Stock-scale / paired MC (Step 8):** Chen et al. 2022; Reinhart & Cerezo Davila 2016; Yoshino et al. 2017.
- **Bottom-up load modelling (Step 9):** Richardson et al. 2010; Widén et al. 2009; McKenna & Thomson 2016; Yamaguchi & Shimoda 2017; Saldanha & Beausoleil-Morrison 2012; Johnson & Beausoleil-Morrison 2017; Fischer et al. 2020; Herrmann et al. 2024.

---

# Appendices / Supplementary Information

**Supplementary methods figures (flow/architecture schematics — to create).**

**Figure S1.** *(insert architecture-search funnel diagram here — to create)* — **Gated generative architecture search.** The progressive 2%→20%→100% data funnel across 40+ trials spanning Markov, autoregressive, VAE, GAN-adjacent, cross-attention, and masked-diffusion families, with the four hard distributional gates (activity JS, AT_HOME RMS, co-presence max) marked, and the outcome that calibrated J3 was the sole 4/4-gate model while MDLM scored best on the composite yet failed two gates.

**Figure S2.** *(insert linkage-workflow diagram here — to create)* — **Census–GSS probabilistic linkage workflow.** A slot-native four-tier hierarchical demographic key-descent match in which each of the 286,537 Census 2021 individuals draws one augmented GSS diary row by descending key specificity (Tier-1 Perfect → Tier-2 Core → Tier-3 Constraints → Tier-4 FailSafe), with the seven match keys, the match-tier distribution, the per-slot-maximum household aggregation, and the plausibility gate that yields the 144,507-household frame.

**Figure S3.** *(insert forecasting-protocol diagram here — to create)* — **Progressive fine-tuning and True-Future-Test forecasting.** The weight-inheritance chain (2005 → +2010 → +2015 → +2022), the next-unseen-cycle holdout evaluated at each phase, the DRIFT_MATRIX computed at every transition, recency-weighted pooling, and demographic-scenario injection producing the 37,008-row 2030 cohort.

**Figure S4.** *(insert end-use-model diagram here — to create)* — **Activity-driven end-use load model structure.** The two-tier split separating the flat 24/7 baseload (refrigeration, freezer, standby) from the transient activity tier, the 9-end-use × 14-activity crosswalk, the co-presence effective-occupancy scaling (shared devices sub-linear, personal devices linear), and the per-end-use SHEU calibration scalar.

**Supplementary results figures (Step-8 occupancy-only).** *(Manuscript labels "Figure S5…S9" are distinct from the internal filenames in backticks — always map via the backtick.)*

**Figure S5.** *(insert `fig02b` here)* — **Diurnal electricity by archetype.** Daily electricity profile in one panel per building archetype (single-detached, other dwelling, mid-rise, high-rise), recent cycle versus forecast with uncertainty bands; shows the load shape and magnitude are strongly archetype-dependent and guards against over-generalising from any one archetype. ✅

**Figure S6.** *(insert `fig03` here)* — **Peak-hour shift.** Histogram of the hour at which each dwelling's daily demand peaks, paired with a circular clock plot of the mean peak hour, recent versus forecast; isolates *when* the maximum occurs and whether the typical peak hour moves, the quantity grid and capacity planning care about. ✅ v2

**Figure S7.** *(insert `fig05` here)* — **Diurnal load by season.** Grid of daily load curves by season (heating, shoulder, cooling) across the columns and by load component (whole-building electricity, heating load, cooling load) down the rows, recent versus forecast; separates behaviour-driven electricity from weather-driven thermal demand. ✅

**Figure S8.** *(insert `fig06` here)* — **Annual electricity carpet.** Heatmap of electricity demand with day-of-year on the horizontal axis and hour-of-day on the vertical axis, recent and forecast panels on a shared colour scale; compresses the full annual hourly series into one image so seasonal and diurnal structure are seen together. ✅

**Figure S9.** *(insert `fig07` here)* — **Paired Δ peak demand by archetype × climate zone.** Heatmap of the paired change in peak demand between forecast and recent cycles, archetypes on one axis and climate zones on the other, diverging colour scale centred on zero; shows *where* the peak-demand change concentrates across the stock-by-geography matrix. ✅ v2 *(strong candidate for promotion into §5.3 if there is room.)*

**Supplementary Step-9 end-use figures (corrected campaign, verified 2026-06-10).**

**Figure S10.** *(insert `figS1` here)* — **Equipment annual calibration against SHEU.** Per-cell annual equipment energy, baseline versus activity, plotted against the NRCan SHEU dwelling targets (SingleD 3,700 / OtherDwelling 3,139 / MidRise 2,166 / HighRise 1,922 kWh) and the ±15% band; shows the activity model hits the target and corrects the over-predicted detached-home baseline. ✅

**Figure S11.** *(insert `figS3` here)* — **Percent deviation from SHEU, all 48 cell-years (the calibration gate).** Per-cell percentage deviation from the SHEU benchmark across every archetype × city × year, with the ±15% gate marked; every cell passes, max +2.33% equipment and +2.63% lighting. ✅

**Figure S12.** *(insert `figS7` here)* — **Equipment baseline→activity peak-hour shift, all cells (null result).** For every archetype-by-city cell, the equipment peak hour under the baseline versus activity-driven schedule, drawn as a stem (open circle = baseline peak hour, filled diamond = activity peak hour), coloured and blocked by archetype; across nearly every cell the markers coincide (0 ± 1 h, mean −0.12 h), so the near-zero stem lengths are themselves the finding — activity scheduling redistributes *when within the day* energy is used without displacing the building-level peak hour. ✅ verified 2026-06-10 (the pre-fix −4 h lollipop was the injection artefact and is superseded — do not cite it).

**Figure S13.** *(insert `figS8` here)* — **Activity-driven lighting diurnal load shape.** Lighting counterpart to Figure 12: one panel per archetype, normalized daily shape, baseline versus activity-driven with peak-hour markers; lighting takes on a more behaviourally plausible intraday profile under modelled activity while peaking at essentially the same evening hour (h18–21). ✅

**Figure S14.** *(insert `figS5` here)* — **2022→2030 equipment differential, activity vs baseline.** Per-archetype change in annual equipment energy from 2022 to 2030, averaged over the six cities, contrasting the SHEU-anchored activity arm (nearly flat: −0.05% to −1.14%) against the baseline arm (+1.0% to +1.7%); the calibration anchor is what stabilises the activity arm (the old single-cell "+35.4% activity" prototype is superseded — do not cite it). ✅

**Figure S15.** *(insert `figS4` here)* — **Overnight equipment floor (sleep check).** Per-cell overnight equipment baseload against a 300 Wh threshold; 12/48 WARN, all OtherDwelling, reflecting the expected D8 multi-unit fridge sum (426–505 Wh floor) rather than a calibration failure; SingleD/MidRise/HighRise all pass. ✅

**Supplementary tables.**

| SI table | Content | Source |
|---|---|---|
| **Table A1** | 9-end-use × 14-activity weight matrix (incl. within-activity sub-splits) | 09 docs |
| **Table A2** | Appliance wattages + sub-30-min prorating rule | 09 docs |
| **Table A3** | Baseload roster (fridge/freezer/standby) | 09 docs |
| **Table B1** | Step-4 generator model card (architecture, conditioning d_cond = 90, training, gates, raking) | 04 docs |
| **Table B2** | 14-category activity codebook; crosswalk magnitudes; co-presence construction | 02 docs |
| **Table C1** | Per-step validation scorecards (Steps 1–9 pass rates) | 00 / step docs |
| **Table C2** | True-Future-Test + backcast tables; DRIFT_MATRIX outputs | 06 docs |
| **Appendix D** | Documented deviations: derived apartment SHEU targets (D1); multi-unit fridge correction (D8); MARSTH/LFTAG NaN handling; lighting R1 + fridge R4 corrections | 05 / 09 docs |

---

## Writing rules carried from the methodology assessment

1. **Framing rule:** magnitude/longitudinal claims carry the headline; Step-8 and Step-9 timing are both verified and unlocked (2026-06-10). The Step-9 timing result is a **null peak-shift** — state it plainly, do not spin it as a positive timing finding; the timing headline belongs to Step-8 (WFH midday fill at a stable ~17:30 peak).
2. **Self-delta rule:** never re-claim the prior papers' novelty; only the four deltas are novelty claims.
3. **One-claim-one-figure rule** in §5; everything else to SI.
4. **CI-first rule** for every paired result.
5. **Number hygiene:** 144,507 households, 64,061 diaries, ~192,183 diary-days, 6,000 runs, 37,008 2030 diary-rows.
6. **Do-not-report list (superseded artefacts):** the pre-fix −4 h equipment peak shift (injection bug, now corrected — the verified result is a 0 ± 1 h null shift); the old single-cell "+35.4% activity vs +0.4% baseline" 2030 differential (superseded by the full-grid Figure S14); raw AT_HOME marginals without the calibrated pair.

## Open dependencies before the full draft

- [ ] Draw the four methods schematics (Figures 1–4) and the four SI methods schematics (Figures S1–S4).
- [x] **Step-9 re-sim landed (2026-06-10)** → §5.4 / Abstract slot 6 / Conclusion item 4 filled; Figures 12, S12, S13 reframed to the null peak-shift result.
- [x] **Calibration-scatter figures confirmed to exist** (`figS1`, `figS3`) → placed as Figures S10–S11; diagnostic `figS5`/`figS4` added as S14–S15.
- [ ] Decide whether to promote Figure S9 (`fig07`, paired Δ peak by archetype × CZ) into §5.3.
- [ ] Decide: add the high-reversion 2030 counter-scenario (caveat 7) or state as scope.
- [ ] Target journal confirmation (affects length, highlight format, SI policy).
- [ ] Harvest ◄prior-pub paragraphs (§1.1, §1.4) from the 1st journal.
