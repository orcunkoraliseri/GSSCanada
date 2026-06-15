# Research Synthesis — Evidence Base for the 3rd Occupancy Journal (Split Models)

### Distilled from 10 deep-research reports · Planning starting-point, not yet a plan

**What this is.** A single consolidated reading of the ten deep-research reports in
`deepResearch_Resources/`, organised by the decisions we actually have to make for the
2-channel and 4-channel split pipelines. Every section ends with **→ implication** lines.
Numbers are reproduced from the reports; where a report stored a value as an image we flag it
`[image-locked]` (must be OCR'd from the original before quoting in the paper).

**This document does not decide the plan.** It assembles the evidence so the plan
(`2-channel_split.md` → `4-channel_split.md`) can be written without re-opening vicious cycles.

---

## The three legs (recap)

| Leg | Scope | Status |
|---|---|---|
| **Leg 1 — Residential** | Single AT_HOME channel, full 9-step GSS→BEM pipeline + 2030 forecast | **COMPLETE** (2nd Journal) |
| **Leg 2 — 2-channel** | Add Office (AT_WORK) on shared backbone; learn the split process | **NEXT** |
| **Leg 3 — 4-channel** | Add Retail (AT_RETAIL) + Hotel (StatCan, non-GSS); drive mixed-use Tall/SuperTall | **TARGET** (3rd Journal) |

---

## Report → topic map

| # | Report file | Feeds |
|---|---|---|
| 1 | Occupancy Modelling for Building Energy | Lit landscape, paradigms, datasets, open problems |
| 2 | Empirical Occupancy Profile Analysis | Diurnal s(t) shapes + peak/trough table (all uses) |
| 3 | Occupancy Time-Series Generation Models | Model-family decision, multi-head loss strategy |
| 4 | Time Use Surveys for Building Occupancy | What GSS can/can't deliver per channel |
| 5 | Validating Synthetic Occupancy Schedules | Gate menu + thresholds |
| 6 | Office Occupancy vs WFH Trends (2019–2030) | Office s(t), WFH lever, 2030 scenarios |
| 7 | Retail Occupancy for Energy Modelling | Retail customer/staff s(t), data sources |
| 8 | Hotel Occupancy Data for Energy Modeling | Hotel s(t), StatCan tables, SARIMA forecast |
| 9 | Building Energy Modeling Occupancy Standards | Modulate-vs-replace, coupling, resolution |
| 10 | Mixed-Use Building Occupancy Modeling | Cross-use correlation, shared-backbone, failure modes |

---

# PART A — Empirical daily rhythms (the s(t) curves per channel)

The single most reusable output: per-use, day-typed diurnal shapes we can use both as **validation
targets** and as **fixed s(t) shapes** for the non-GSS / modulated channels. All values are
*fraction of peak* unless noted. Source: Report 2 (peak/trough table), with channel detail from
Reports 6/7/8.

### Master peak/trough table (Report 2, reproduced)

| Use | Day | Peak hours | Peak frac | Trough hours | Trough frac |
|---|---|---|---|---|---|
| **Residential** | Weekday | 22:00–05:00 | 0.90–1.00 | 11:00–16:00 | 0.15–0.40 |
| | Saturday | 23:00–07:00 | 0.95–1.00 | 12:00–17:00 | 0.40–0.60 |
| | Sunday | 22:00–07:00 | 0.95–1.00 | 13:00–17:00 | 0.50–0.70 |
| **Office** | Weekday | 09:30–11:30 & 14:30–16:30 | 0.50–0.55 (private) / 0.75–0.80 (open-plan) | 12:00–13:30 lunch dip 0.25–0.35; night 0.02–0.05 | — |
| | Saturday | 10:00–14:00 | 0.05–0.10 | else <0.02 | — |
| | Sunday | 11:00–13:00 | <0.05 | else <0.01 | — |
| **Retail (customers)** | Weekday | 12:00–13:30 & 17:30–19:30 | 0.40–0.60 | 15:00–16:30 mid-dip 0.15–0.30 | — |
| | Saturday | 13:00–16:00 | 0.80–0.95 | closed hours 0.00 | — |
| | Sunday | 14:00–16:00 | 0.60–0.75 | closed hours 0.00 | — |
| **Retail (staff)** | Weekday | 10:00–19:00 | 0.50–0.70 (flat shifts) | night 0.00–0.05 | — |
| | Saturday | 10:00–19:00 | 0.80–1.00 | night 0.00–0.05 | — |
| **Hotel (guest rooms)** | Weekday | 23:00–06:00 | 0.75–0.90 (business) / 0.40–0.50 (leisure) | 09:00–17:00 | 0.10–0.20 |
| | Saturday | 23:00–08:00 | 0.90–1.00 (leisure) | 10:00–16:00 | 0.15–0.25 |
| **Hotel (lobby)** | Weekday | 11:00–12:00 & 16:00–19:00 | 0.60–0.75 | 01:00–06:00 | <0.05 |

### Channel-specific shape notes

**Residential (Leg 1, already shipped — validation cross-check):** overnight plateau ~1.0, decline
after 05:00, weekday midday trough **0.15–0.40**, evening ramp 17:00–20:00. Weekend: delayed/shallower
morning decline, higher daytime floor **0.40–0.70**, bi-modal lunch+dinner meal spikes. Demographics
load-bearing: over-65 ≈ flat weekday/weekend with high daytime presence; students/hybrid ≈ **2×** the
reference midday presence. DOE/BEopt static residential schedules deviate up to **41%** from 12–14 yr
ATUS data — our model should beat that.

**Office (Report 6):** bi-modal weekday — arrivals from 07:00, morning plateau by 09:30, lunch dip
**−30% to −50%** at 12:00–13:30, *true* peak ~15:00, fast decline after 17:00. **Actual peak never
hits design**: private offices **0.50–0.55**, open-plan plateau ~**0.80**; ASHRAE Schedule AA assumes
95–100% → over-prediction of **46%** (private) / **12%** (open-plan). Post-COVID weekly shape: strong
Tue–Thu peak, Mon/Fri light. Kastle peak-day **~62%** of Feb-2020, weekly avg **~52–55%**; XY Sense
global **~40%** of capacity. ~25% of desks never used.

**Retail (Report 7) — customers ≠ staff, must be two curves:**
- Customers peaky: weekday lunch + evening peaks; **Saturday single afternoon peak 13:00–14:00 ≈ 1.0**;
  **Sunday single midday spike 11:00–12:00 ≈ 0.90 then decays to ~0 by 19:00** (no Sunday late peak).
- Staff wider & flatter: arrive **1–2 h before** opening, leave **1–2 h after** closing; peak 0.90–1.00
  across the working day. Report 7 includes a full decoded 24×6 (hour × {wkdy/Sat/Sun}×{cust/staff})
  multiplier table — **directly usable as EnergyPlus fractional schedules**.
- Grocery/big-box: weekday dual peak (11:00–13:00 & 15:00–16:00, ~16% of daily shoppers each); weekend
  single 11:00–13:00 spike (~20%/hr). Specialty "50/20 rule": ~50% of weekly traffic in 20 peak hours.

**Hotel (Report 8) — inverted vs office, decoupled guest-room vs lobby:** guest rooms peak overnight
(weekday business 0.75–0.90), deep daytime trough **0.10–0.20** at 09:00–17:00; lobby peaks at
check-in 15:00–19:00. Report 8 includes weekday/weekend diurnal fraction tables for occupancy /
lighting / receptacle. Guest rooms unoccupied ~**70%** of the day yet drive up to **80%** of hotel
energy. Business hotels peak mid-week; leisure/resort peak Fri/Sat (~100%) vs weekday ≤50%.

> **→ implication.** We get publishable, citable s(t) shapes for all four channels *today*. Residential
> and Office come from GSS (Legs 1–2). Retail-customer can be GSS-shaped but Retail-staff and Hotel
> cannot (Parts B/G). Saturday≠Sunday asymmetry and the office 15:00 (not 17:00) peak are concrete
> validation targets. Per-format retail curves differ — don't ship one generic retail schedule.

---

# PART B — Data sources & what GSS can actually deliver per channel

Report 4 (TUS reach/limits) + Report 7/8 (retail/hotel sources). The central finding: **GSS quality
degrades as you move away from "the respondent's own home."**

| Channel | GSS / TUS evidence quality | Gap | Required supplement |
|---|---|---|---|
| Residential (AT_HOME) | **High** | minor recall/rounding | none (smart-meter optional) |
| Office (AT_WORK) | **Moderate** | misses hybrid/telework volatility, visitors | StatCan LFS WFH rates; badge/Wi-Fi for calibration |
| Retail customers (AT_RETAIL) | **Low** | shopper-centric, no store density, no floor area | mobility data (SafeGraph/Placer/Esri CA); SCIEU hours |
| Retail staff | **Insufficient (erased)** | staff logged as "work", not "shopping" | NRCan **SCIEU** worker density (1.624 avg, 4.347 peak /100 m²) |
| Hotel guests | **Insufficient (out of frame)** | tourists/non-residents not sampled | **STR / Tourism Data Collective** + StatCan tourism tables |

**GSS location vs activity codes (Report 4):** GSS evolved to a 3-digit location scheme — `300` home,
`301` work/school, `306` stores/mall, `309` restaurant/bar, `311` clinic. **Use *location* codes, not
activity codes, for any commercial presence** because the **2015 redesign collapsed activity codes
264→64** ("light diary"), making them too aggregated to distinguish commercial use types.

**Three hard longitudinal breaks in GSS** (must be handled exactly as Leg 1 already does):
1. **2015 redesign** — 264→64 activity codes, CATI→multi-mode EQ; workplace/retail coding break.
2. **2022 GSSP** — dwelling-based frame (DUF), admin-data integration, online-dominant + COVID/hybrid.
3. Weekend oversampling (ATUS-style ~25% Sat / 25% Sun) → **apply design survey weights**.

**Retail data ranking for Canada (Report 7):** ① NRCan SCIEU (baseline archetypes, no hourly) →
② NECB/ASHRAE schedules → ③ mobility/mobile-location (SafeGraph CA, Placer.ai, Esri CA — best for
hourly + post-pandemic) → ④ POS proxies → ⑤ people-counters (gold standard, low access) → ⑥ GSS TUS
(low; customer-shape only).

**Hotel data (Report 8) — exact StatCan tables:** `33-10-0102-01` (accommodation financials — **NOT
physical occupancy**), `24-10-0055-01` (monthly international arrivals), `36-10-0230-01` (national
tourism indicators, quarterly), `33-10-0270-01` (active tourism businesses, monthly). **Physical
occupancy rate needs STR/CoStar or Tourism Data Collective** — submarket resolution (downtown vs
airport) matters. Revenue recovered to 2019 by 2022 but **physical occupancy only by 2024** — do not
proxy occupancy from revenue/RevPAR.

> **→ implication.** Confirms the architecture already drafted: Residential + Office + Retail-customer
> go through the GSS Transformer; **Retail-staff and Hotel are separate non-GSS tracks** (SCIEU + STR).
> The 4-channel doc's decision to source Hotel from StatCan (not GSS) is *validated*. Add: Retail needs
> a **staff** sub-channel from SCIEU, and Retail-customer needs floor-area conversion to become density.

---

# PART C — Model family & multi-head architecture

Report 3 (generative model survey) + Report 1 (paradigm landscape) + Report 10 (mixed-use MTL).

### Ranked recommendation (Report 3)

| Rank | Family | Verdict |
|---|---|---|
| **1 — safest default** | **Multi-head Transformer + dynamic loss weighting** | builds directly on our existing Conditional Transformer; lowest risk |
| 2 — best practical alt | Conditional Action VAE (ActVAE) | fastest train+inference, sample-efficient; watch posterior collapse |
| 3 — promising upside | Discrete masked diffusion (MDLM/SEDD) | global denoising, no exposure bias, CFG/GILC levers; needs sampling speed-up (block-wise → ~3×) |
| 4 | Hierarchical semi-Markov (hazard/Weibull dwell) | interpretable, great dwell times; parameter explosion under covariates |
| 5–6 — avoid | TimeGAN/RTSGAN; agent-based/econometric | unstable on discrete / no end-to-end multi-head gradient training |

**This confirms our plan**: shared encoder + per-channel binary output heads (AT_HOME / AT_WORK /
AT_RETAIL) off one Transformer is *exactly* the report's Rank-1 pattern.

### The one mandatory change for multi-head (Report 3 + Report 10)

Equal-weight loss summation will **fail**: the easy binary presence channels converge fast and
**dominate the gradient**, suppressing the 14-category activity head. Fixes, in priority:

1. **Replace equal weighting with dynamic weighting** — **SLAW** (O(1), scales to many heads) or
   **homoscedastic uncertainty weighting**. *Not optional.*
2. **Add PCGrad (gradient surgery)** to neutralise gradient conflict / negative transfer between heads.
3. Consider **task-private capacity + orthogonality regularizer** (Report 10's shared+private
   state-space split) so added channels don't collapse into each other — echoes our own
   "capacity is the bottleneck" finding.
4. **Diversity-preserving loss, not MSE-only** — Report 10 confirms MSE multi-head training collapses
   to a smoothed mean and kills peaks. **This is our COP failure mode named in the literature.**

> **→ implication.** Keep the multi-head Transformer (validated #1). Treat **loss weighting (SLAW/UW)
> + PCGrad** as required Leg-2 work, not a tuning afterthought. MDLM stays the documented upside path
> (consistent with prior MDLM HPT memory); ActVAE is worth a cheap side-eval for inference cost at
> 144k-HH scale. Exposure bias in our AR arm is the named mechanism behind inference-time COP drift.

---

# PART D — Injection into BEM: modulate vs replace, coupling, resolution

Report 9 (standards). *Caveat: peak densities (people/m², LPD, plug W/m²) and equations are
image-locked in Report 9 — recover before quoting absolute W/m² values.*

**Modulate vs Replace — the core asymmetry our split docs already use:**
- **Replace** (full 8760-h overwrite, remove code diversity factors): right for our data-driven
  synthetic populations, calibration, UBEM. This is the **Residential** semantic.
- **Modulate** (keep code peak density + shape, multiply by presence multiplier): right for
  compliance, and the correct semantic for **Office/Retail/Hotel** so code peak densities (W/m²,
  people/m²) survive for regulatory comparability. Canadian BEM roadmap runs 0.75/1.0/1.25 triple-runs.
- Cited evidence replacement matters: data-mined office schedules ran **36.67–50.53% lower** occupancy
  than DOE baselines → standard profiles over-state loads.

**Inter-schedule coupling (enforce, don't let loads track occupancy linearly to zero):**
- **Lighting:** `L(t) = max(Lmin, η·O(t)·D(t))`; **Lmin ≈ 0.10–0.20** of peak (egress/safety); D(t) =
  daylight dimming 0–1. ASHRAE 90.1-2022: office auto-off **20 min** after vacancy; hotel bath **30 min**.
- **Plug loads:** `P(t) = Pbase + (1−Pbase)·O(t)`; **Pbase ≈ 0.15–0.30** for offices; unoccupied
  overnight/weekend can exceed **50%** of peak draw. Never zero.
- **HVAC:** VAV min airflow 30–50% of design; occupancy-sensor "occupied standby" drops to zero +
  widens deadband.

**Resolution (matches our 30-min convention):** inject via **Schedule:File** (8760/8784-line CSV),
**not** Schedule:Compact. `Minutes per Item` ∈ {1,5,10,15,30,60} → use 30. Decide `Interpolate to
Timestep` deliberately (`Yes` averages = compounds peak loss; `No` preserves block). Down-sampling
10-min→30-min acts as a low-pass filter: dampens transient sensible peaks (meeting rooms, checkout,
lobby check-in), can over-ventilate (dampers stay open), and separates coincident peak solar +
occupant gains. Document the trade-off.

> **→ implication.** The split docs' "Residential replaces, Office/Retail/Hotel modulate" rule is
> textbook-correct. Hard-code coupling constants (Lmin 0.10–0.20, Pbase 0.15–0.30) into the BEM
> integration step. Use Schedule:File @ 30-min. **Action: OCR the image-locked NECB/ASHRAE peak
> densities** from Report 9 before writing any absolute-density numbers.

---

# PART E — Validation framework (hardening our gates)

Report 5. Our current gates (JS per day-type + presence-rate RMS pp + hard gates) are "a solid start"
but blind to temporal/joint realism. *Many thresholds in Report 5 are image-locked; 0.05-class values
are standards-anchored reconstructions — verify before publishing.*

**Tiered checklist (sequential — fail Tier 1/2 before spending EnergyPlus runs):**

| Tier | Metric | Threshold (verify image-locked) |
|---|---|---|
| 1 Distributional | KL (arrival/departure) | < 0.05 |
| 1 | 1-Wasserstein / EMD on hourly presence CDF | < 0.05 |
| 1 | Presence-rate RMS error | ≤ 5 pp per day-type |
| 2 Structural | Transition-matrix Frobenius/MAE (run-level) | < 0.05 |
| 2 | Dwell-time KS test | fail to reject H₀ (p > 0.05) |
| 2 | Autocorrelation MAE, lags 1–24 h | < 0.05 |
| 3 Downstream | NMBE (ASHRAE G14) | monthly ±5%, hourly ±10% |
| 3 | CV(RMSE) | monthly 15%, hourly 30% |
| 3 | Peak demand + **timing shift** | magnitude ±15%; **timing ≤ 1 h** |

**New gates we should add (not in current pipeline):**
- **EMD/Wasserstein** alongside JS — JS *saturates* on disjoint supports (exactly where a bad model
  hides); Wasserstein is sensitive to timing offsets JS misses.
- **Transition-matrix + dwell-time KS** — catches "right marginals, impossible flips" (the HVAC
  over-cycling failure).
- **C2ST** (XGBoost real-vs-synth, target ≈50% accuracy) — single cheap dual-scale gate catching both
  marginal and temporal breakage without one masking the other.
- **Simultaneity/coincidence factor** at aggregate scale — so we don't pass population marginals while
  synchronising peaks (relevant to UBEM aggregation).

**Two pitfalls the reports name that we've personally hit:**
- **Model selection by training loss / composite** is unsafe — select on a **Pareto frontier**
  (Wasserstein + ACF-MAE + downstream peak). (This is exactly why J6_HC beat J3 on composite but
  failed COP.)
- **Teacher-forcing illusion / exposure bias** — evaluate **strictly open-loop, long-horizon**; our AR
  arm is the mechanism behind inference-time COP failures.
- **Compensating-error trap** — validate schedule distributions *independently* of envelope
  calibration (our backcast-2022/forecast-2030 split already mirrors the recommended design).

> **→ implication.** Promote peak-timing ≤1 h to a hard gate (we already measure it: Step-8 h17,
> Step-9 0±1 h). Add EMD + transition/dwell + C2ST to the per-channel gate set. Bake the COVID-break
> handling and open-loop evaluation in from the start of Leg 2.

---

# PART F — Mixed-use & cross-use (Leg 3 specifics)

Report 10. Central thesis: **occupancy across uses is correlated, and treating channels independently
is a named fallacy** ("the fallacy of decoupled schedules"). The same person is an office worker at
10:00 and a food-court customer at 12:30; independent schedules cause **occupant duplication →
coincident-peak overprediction → oversized HVAC**.

- **Shared-backbone MTL beats fully separate per-use models** for stacked towers — but only with
  **task-private capacity + orthogonality regularizer** (anti-negative-transfer) and
  diversity-preserving losses. Naive one-encoder-many-heads risks representation collapse.
- Decoupled/over-simplified geometry underestimates annual heating+cooling demand by **14–26%**.
- **Failure modes to design against:** occupant duplication; diversity decay from MSE-only training;
  parameter unidentifiability (diagnose via Fisher Information Matrix); sequential-ECM and feedstock
  double-counting; negative transfer; ground-level weather on supertall floors.
- **Service/MEP/core** is energetically material (elevators 5–15% of tower electricity); high-fidelity
  work models it as active zones, but it's **out of scope** for our occupancy-schedule layer — leave on
  NECB baseline (as the 4-channel doc already says).
- **Caveat for our paper:** Report 10's MTL-superiority evidence is **cross-domain (not a tower-specific
  bake-off)** — a reviewer can push on that; cite carefully.

> **→ implication.** Our shared-encoder choice is right for cross-use correlation, but Leg 3 must add
> orthogonality/PCGrad to stop the 4 heads degrading each other. The cross-use lunch-transition
> (office→retail) is a real signal GSS time-use *can* capture (an occupant's diary moves 301→306) —
> potential novelty. Keep service/MEP on baseline. Don't over-claim shared-backbone superiority.

---

# PART G — Forecasting to 2030

**Office WFH (Report 6) — single dominant lever:** Canada WFH ~7% (2019) → ~40% (Apr 2020) → ~30%
(Jan 2022) → ~20% (Nov 2023) → ~16–20% (2024). McKinsey: office demand **0–13% lower** by 2030 in the
median city. Three named scenarios to run as sensitivity bands:
- **Conservative Return (low):** WFH 15–20% (offices 80–85% filled).
- **Hybrid Equilibrium (central):** WFH ~30% (70% in office).
- **Fully Hybrid (high):** WFH ~40% (60% in office).
Energy is **non-linear**: 20–50% occupancy cut → only ~10–30% energy savings (fixed HVAC/vent + plug
baseload). EU lags NA (~12% WFH 2021) — our scenarios are NA-appropriate.

**Hotel (Report 8) — classical TS, not the Transformer:** SARIMA/ETS/structural with explicit
**COVID intervention**. Recommended recipe: (1) intervention term (Mar-2020 step + decaying recovery),
(2) STL de-noising of crisis-year seasonality, (3) **SARIMAX/MIDAS** with exogenous proxies (airport
traffic, Google-Trends travel), (4) rolling-origin validation on 2023–2026 (min MAPE/RMSE), (5)
logistic cap at 100%. Canadian seasonality: summer (Jul–Aug) peak, winter (Jan–Feb) trough.

**Coupling shape × amplitude (Report 8) — important pitfall:** multiplicative `Occ = s(t)·O(m)`
"liquefies" guests (50% occupancy ≠ every room at half load) and **suppresses peak HVAC loads**.
Prefer **spatial allocation**: occupy `round(N·O(m))` rooms fully (rotate the subset monthly), set
vacant rooms to standby + setback. Verify the aggregate identity `(1/N)Σ Occ_i = s(t)·O(m)`.

> **→ implication.** Office 2030 = reuse Model-2 progressive fine-tuning + WFH scalar with 3 sensitivity
> bands. Hotel 2030 = separate SARIMAX track (reuses our Step-6 COVID-indicator philosophy). For hotel
> BEM injection, use **binary per-room spatial allocation**, not multiplicative scaling, where peak/DCV
> matters.

---

# Consolidated design decisions for the 3rd Journal

| # | Decision | Evidence | Confidence |
|---|---|---|---|
| 1 | Keep shared-encoder multi-head Transformer | R3 Rank-1; R1; R10 | **High** |
| 2 | **SLAW/UW loss weighting + PCGrad** mandatory for multi-head | R3; R10 | **High** |
| 3 | Add task-private capacity + orthogonality regularizer for 4-head | R10 | Medium |
| 4 | Residential **replaces**; Office/Retail/Hotel **modulate** code baseline | R9 | **High** |
| 5 | Retail = **two** channels (customer GSS-shaped + staff from SCIEU) | R7; R4 | **High** |
| 6 | Hotel = **non-GSS** track (STR/Tourism Data Collective + SARIMAX), binary room allocation | R8; R4 | **High** |
| 7 | Use GSS **location** codes (300/301/306/309) not activity codes for presence | R4 | **High** |
| 8 | Handle 2015 + 2022 GSS breaks; apply survey weights | R4 | **High** |
| 9 | Inject via Schedule:File @30-min; enforce Lmin 0.10–0.20, Pbase 0.15–0.30 | R9 | **High** |
| 10 | Office 2030 via WFH scalar, 3 sensitivity bands (15–20 / 30 / 40%) | R6 | **High** |
| 11 | Harden gates: EMD + transition/dwell-KS + C2ST + peak-timing ≤1 h | R5 | **High** |
| 12 | Select models on Pareto frontier, never composite/training loss; eval open-loop | R5 | **High** |
| 13 | Per-format retail s(t) + Saturday≠Sunday; office peak ~15:00 not 17:00 | R2; R7; R6 | **High** |
| 14 | Service/MEP/core left on NECB baseline | R10 | **High** |

---

# Open questions / risks to resolve before/while planning

1. **Image-locked numbers.** OCR the peak densities/LPD/plug (R9) and the exact validation thresholds
   (R5) from the originals before any absolute value enters the paper.
2. **Retail-staff data acquisition.** SCIEU gives density but no hourly shape; we still need a staff
   *shape* — derive from operating hours, or accept the flat-shift schedule from R7's decoded table?
3. **Hotel physical occupancy access.** STR/Tourism Data Collective may be licensed — confirm we can
   get monthly provincial physical occupancy, else fall back to Yukon/NS open series + arrivals proxy.
4. **Cross-use transition novelty.** Decide whether to *model* office→retail lunch transitions from GSS
   diaries (potential contribution) or treat channels independently (simpler, but R10 flags duplication).
5. **MDLM vs Transformer for Leg 2.** Stay on the safe Rank-1 default, or pilot the diffusion upside
   given prior MDLM HPT work? (Decide before committing Leg-2 compute.)
6. **Reviewer exposure on shared-backbone claim** — R10's MTL evidence is cross-domain; need a
   defensible framing or a small internal ablation (shared vs separate).

---

# Source index

All in `3J_docs_occ_nTemp/deepResearch_Resources/`. Prompts that generated them:
`deepResearch_Resources/00_deep_research_prompts.md`.

1. `Occupancy Modelling for Building Energy.md` — paradigms, BDG2/Annex 79 datasets, Concordia SGW 32.26% case
2. `Empirical Occupancy Profile Analysis.md` — peak/trough table, ATUS/HETUS, code-deviation %
3. `Occupancy Time-Series Generation Models.md` — model ranking, SLAW/PCGrad, MDLM/ActVAE
4. `Time Use Surveys for Building Occupancy.md` — GSS breaks, location-code mapping, use×quality table
5. `Validating Synthetic Occupancy Schedules.md` — tiered gates, EMD/C2ST, ASHRAE G14 tolerances
6. `deep-research-report_Office Occupancy vs. WFH Trends (2019–2030).md` — WFH timeline, 2030 scenarios
7. `Retail Occupancy for Energy Modelling.md` — 24×6 cust/staff table, SCIEU, mobility data ranking
8. `Hotel Occupancy Data for Energy Modeling.md` — StatCan table IDs, diurnal tables, SARIMAX recipe
9. `Building Energy Modeling Occupancy Standards.md` — modulate/replace, coupling, Schedule:File
10. `Mixed-Use Building Occupancy Modeling.md` — cross-use fallacy, shared-backbone MTL, failure modes

*Note: Reports 5, 7, 8, 9 store key numbers as base64 images; the extraction agents decoded what they
could and flagged the rest `[image-locked]`. Confirm those against the originals before publication.*
