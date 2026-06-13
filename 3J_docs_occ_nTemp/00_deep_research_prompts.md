# Deep-Research Prompts — Split Occupancy Modelling (Residential → Office → 4-Channel)

### Pre-build evidence gathering for the 3rd Occupancy Journal

**Purpose.** Before we write a single line of split-channel model code, we want *research data* in hand:
what to learn, which model families are credible, how others validate, what the empirical daily
rhythms of each building use actually look like, and where the literature already solved (or failed
to solve) this. This avoids the vicious build-debug-rebuild cycles we hit on the residential model.

This document is a **collection of paste-ready deep-research prompts**. Each one is written to be
dropped directly into a web-based deep-research tool (Gemini Deep Research, ChatGPT Deep Research /
o-series, Perplexity, etc.). Run them, save the returned reports next to this file, and we mine the
findings to lock design decisions for `2-channel_split.md` and `4-channel_split.md`.

---

## The three legs of the occupancy programme

| Leg | Scope | Status | Doc |
|---|---|---|---|
| **Leg 1 — Residential** | Single AT_HOME channel; GSS time-use → Conditional Transformer → 2030 forecast → BEM. The full 9-step pipeline. | **COMPLETE** (2nd Journal, submission copy built) | `2J_docs_occ_nTemp/00_GSS_Occupancy_Pipeline_Overview.md` |
| **Leg 2 — 2-channel split (middle step)** | Add a parallel **Office (AT_WORK)** channel on the shared Transformer backbone; learn the *split process* on the simplest non-residential case. Injected into PNNL Tall / SuperTall office zones. | **NEXT** (learning step) | `3J_docs_occ_nTemp/2-channel_split.md` |
| **Leg 3 — 4-channel split** | Extend to **Retail (AT_RETAIL)** + **Hotel** (StatCan tourism, non-GSS). Drives the full mixed-use Tall / SuperTall prototypes. | **TARGET** (3rd Journal) | `3J_docs_occ_nTemp/4-channel_split.md` |

> We deliberately walk Leg 2 before Leg 3: prove the multi-head split, the modulate-not-replace
> injection asymmetry, and the validation gates on **one** new channel before adding three.

---

## How to use these prompts

1. Pick a prompt, copy the fenced block verbatim into your deep-research tool.
2. Where a prompt says `[our context]`, the framing is already embedded — you can run it as-is, or
   trim the Canadian-specific clauses if the tool returns too little international literature.
3. Ask the tool for **inline citations + a reference list** every time (each prompt requests this).
4. Save each report as `dr_<NN>_<shortname>.md` in this folder; we cross-reference them in the design docs.
5. Prompts 1–5 are *foundational* (run first). Prompts 6–10 are *channel-* and *method-specific*.

---

## PROMPT 1 — Literature landscape: occupancy modelling for non-residential & mixed-use BEM/UBEM

```
You are a building-energy-modelling research assistant. Produce a structured literature review on
data-driven OCCUPANCY MODELLING for building energy simulation (BEM) and urban building energy
modelling (UBEM), with emphasis on NON-RESIDENTIAL and MIXED-USE buildings (office, retail, hotel)
rather than single-family homes.

Cover, with inline citations and a final reference list:
1. The main modelling paradigms used to generate occupancy SCHEDULES / time-series for BEM:
   deterministic standard schedules (ASHRAE 90.1, DOE prototypes, NECB), stochastic Markov/
   agent-based models, survey/time-use-driven models, sensor/Wi-Fi/CO2-driven data models, and
   recent deep-learning generative approaches.
2. For each paradigm: representative papers (2015–2025), the data they use, the temporal resolution
   (10-min / 30-min / hourly), and how outputs feed EnergyPlus/DOE-2/Modelica.
3. Which studies model MULTIPLE building uses or MIXED-USE towers with a single shared framework,
   and how they keep the uses consistent (shared backbone vs separate models per use).
4. Known benchmark datasets for occupancy (e.g. ASHRAE Great Energy Predictor, Building Data Genome,
   any time-use-derived occupancy sets).
5. Open problems repeatedly named in reviews (transferability across building types, validation,
   data scarcity for commercial occupancy, COVID/WFH structural breaks).

Output as a structured report with a comparison table of paradigms (rows = paradigm,
columns = data source, resolution, strengths, weaknesses, key refs). End with a 5-bullet
"what this implies for a shared multi-channel generative model" section.
```

---

## PROMPT 2 — Empirical daily rhythms (diurnal occupancy profiles) per building use

```
You are a buildings-occupancy data analyst. Compile EMPIRICAL diurnal occupancy profiles (fraction
of design/peak occupancy vs time-of-day, ideally split by weekday / Saturday / Sunday) for each of
these building uses, drawing on measured studies, standards, and survey data:
  (a) Residential dwellings (presence at home),
  (b) Office / workplaces,
  (c) Retail / shopping (customer footfall AND staff presence — distinguish them),
  (d) Hotels (guest-room presence, overnight vs daytime; plus lobby/amenity).

For each use, report and cite:
1. Typical shape of the 24-hour presence curve: peak hour(s), trough hour(s), ramp-up / ramp-down
   timing, and weekday-vs-weekend differences.
2. The numeric peak-fraction and characteristic plateau values where studies give them.
3. The standard reference schedules (ASHRAE 90.1 Appendix G, DOE commercial prototype, NECB) for the
   same use, and how far MEASURED occupancy deviates from those standard schedules.
4. Seasonal / monthly variation, especially for hotels (tourism seasonality) and retail (holiday peaks).
5. How North-American / Canadian patterns differ from European (HETUS) or other regions.

Deliver four labelled diurnal-profile descriptions (one per use), a table of peak/trough hours per
use per day-type, and a short note on which uses are well-captured by a person-level time-use diary
vs which need a population/footfall data source. Inline citations + reference list required.
```

---

## PROMPT 3 — Generative model families for multivariate occupancy time-series

```
You are a machine-learning methods researcher. Survey MODEL ARCHITECTURES suitable for generating
SYNTHETIC, multivariate, categorical+binary OCCUPANCY TIME-SERIES (e.g. a per-30-minute sequence of
an activity category plus several binary presence channels), conditioned on demographic / contextual
covariates.

[Our context: we currently use a Conditional Transformer encoder-decoder that emits 48 half-hour
slots of a 14-category activity token + binary presence channels, conditioned on demographics, day-
type and survey-cycle year. We want to add parallel presence channels (office, retail) as additional
output heads. We need to know the credible alternatives and their trade-offs before committing.]

Cover, with inline citations + reference list:
1. Architecture families for conditional sequence generation of categorical/binary data:
   - autoregressive Transformers,
   - discrete diffusion / masked-diffusion language models (MDLM/SEDD/D3PM),
   - VAEs / conditional VAEs,
   - GANs (incl. TimeGAN, sequence GANs),
   - HMMs / semi-Markov / inhomogeneous Markov chains,
   - agent-based / activity-based scheduling models.
2. MULTI-TASK / MULTI-HEAD designs: how to share an encoder across several correlated output
   channels, recommended loss weighting strategies, and risks (negative transfer, one channel
   dominating).
3. How each family handles: long-range temporal dependencies, hard marginal/aggregate constraints,
   rare states, and conditioning on many covariates.
4. Evidence on which families best preserve realistic transition statistics and population marginals
   for occupancy specifically.
5. Compute cost and data-hunger of each, for ~50k–200k training sequences.

Deliver a ranked recommendation table (model family × suitability for multi-channel occupancy ×
constraint-handling × compute) and a 5-bullet "safest default + most promising upside" summary.
```

---

## PROMPT 4 — Time-use surveys as an occupancy data source: reach and limits

```
You are a time-use-survey methodologist advising a building-energy project. Assess how national
TIME-USE SURVEYS (TUS) — e.g. the Canadian General Social Survey Time Use, American Time Use Survey
(ATUS), the Harmonised European Time Use Survey (HETUS), UK Time Use Survey — can and cannot be used
to derive building-occupancy schedules by building USE TYPE.

Address, with inline citations + reference list:
1. How TUS episode data (activity + location codes) is converted into presence indicators for
   "at home", "at work/workplace", "at retail/shopping/services". What location-code schemes exist
   and how stable they are across survey waves/redesigns.
2. The KNOWN LIMITATIONS of using TUS for NON-residential occupancy:
   - residents are sampled at home, so workplaces/retail are seen only from the visitor/worker side,
   - tourists and out-of-region visitors are out of frame (critical for hotels),
   - one-day diaries, weekday/weekend imbalance, self-report error, COVID-era collection changes.
3. Published precedents that DID derive occupancy or activity schedules from TUS for energy models
   (residential and, if any, commercial). Summarise their method and stated caveats.
4. Recommended corrections / augmentations when TUS under-covers a use (e.g. pairing with footfall,
   employment statistics, or tourism statistics).
5. Specifics for the Canadian GSS Time Use (cycles ~2005/2010/2015/2022): location coding, the 2015
   redesign, and any documented break in workplace/retail coding.

Deliver: a mapping table (building use → TUS evidence quality → recommended supplementary source),
and an explicit list of uses for which TUS is INSUFFICIENT and must be replaced/augmented.
```

---

## PROMPT 5 — Validation & testing of synthetic occupancy schedules

```
You are a validation-methods researcher for synthetic data in building energy modelling. Compile the
methods and METRICS used to validate SYNTHETIC / GENERATED occupancy schedules against observed data,
and to validate their downstream energy impact.

[Our context: we validate generated diaries with Jensen-Shannon divergence per day-type, presence-
rate RMS error in percentage points, and a small set of hard "gates" a model must pass. We want a
complete menu of accepted validation practices, plus how others test the ENERGY-side consequences.]

Cover, with inline citations + reference list:
1. Distributional metrics for occupancy realism: JS/KL divergence, Wasserstein/EMD, marginal-match
   error, transition-matrix / dwell-time comparison, autocorrelation, diversity/coverage metrics for
   generative models.
2. Aggregate-vs-individual validation: how to check population marginals AND per-sequence realism
   without one masking the other.
3. Downstream / energy-side validation: comparing simulated load shapes, peak timing, and EUI from
   synthetic vs reference schedules; what tolerances are considered acceptable.
4. Cross-validation designs for temporal/longitudinal generative models (hold-out future wave,
   "true future test", backcasting).
5. Common validation PITFALLS (selecting models by training loss, teacher-forcing illusion,
   overfitting marginals while breaking transitions) and how papers guard against them.

Deliver a tiered validation checklist (Tier 1 distributional → Tier 2 structural → Tier 3 downstream
energy), with a recommended pass/fail threshold for each metric where the literature gives one.
```

---

## PROMPT 6 — Office occupancy, WFH structural break, and 2030 forecasting

```
You are a workplace-occupancy and labour-trends analyst. Produce an evidence base on OFFICE building
occupancy and the work-from-home (WFH) / hybrid-work structural change, oriented toward forecasting
office occupancy to ~2030 for energy modelling.

Cover, with inline citations + reference list:
1. Measured office occupancy / utilisation rates before COVID-19 vs current (badge, Wi-Fi, sensor,
   and survey-based studies), including the diurnal and weekly shape change (e.g. mid-week peak,
   "Tuesday-Wednesday-Thursday" pattern).
2. WFH / remote-work prevalence trends, Canada-specific where possible (Statistics Canada / Labour
   Force Survey), with numeric rates by year 2019→2024 and any forecast to 2030.
3. How energy-modelling and real-estate studies forecast future office occupancy and the implied
   range of plausible 2030 WFH rates (low / central / high scenarios).
4. The energy-demand consequences reported for reduced/hybrid office occupancy (load shape, peak,
   EUI), and why occupancy reductions don't scale linearly to energy.
5. How to represent WFH as a single tunable scenario lever for sensitivity analysis.

Deliver: a year-by-year table of office occupancy / WFH rate (with sources), three named 2030
scenarios (low/central/high WFH) with justification, and a note on Canadian vs US/EU differences.
```

---

## PROMPT 7 — Retail occupancy & footfall: data sources and diurnal patterns

```
You are a retail-analytics researcher. Produce an evidence base on RETAIL building occupancy —
both CUSTOMER footfall and STAFF presence — for use in building energy modelling.

Cover, with inline citations + reference list:
1. Typical diurnal and weekly footfall curves for retail (malls, high-street, grocery, big-box),
   including weekday vs weekend and seasonal/holiday peaks; give numeric peak hours and shapes.
2. Distinction between customer presence and employee presence (employees arrive before / leave after
   opening hours; staffing is flatter than footfall) and how each drives different end-uses
   (lighting/HVAC follow opening hours; plug loads follow staff).
3. Data sources for retail occupancy: footfall-counter datasets, mobility/mobile-location data,
   point-of-sale proxies, employment statistics, and any open datasets.
4. How standards (ASHRAE 90.1 / NECB / DOE retail prototype) schedule retail occupancy and how that
   compares to measured footfall.
5. Whether time-use surveys' "shopping/services" activity adequately captures the retail-occupancy
   signal, and what biases arise (shoppers counted, not the store-level occupancy).

Deliver: a labelled retail diurnal profile (weekday/Saturday/Sunday), a customer-vs-staff comparison,
and a ranked list of data sources by accessibility and fitness for a Canadian study.
```

---

## PROMPT 8 — Hotel occupancy: data sources, diurnal guest presence, seasonal forecasting

```
You are a hospitality-and-tourism data analyst supporting a building-energy project. Produce an
evidence base on HOTEL occupancy for energy modelling, given that national time-use surveys do NOT
capture hotel guests (residents aren't sampled as guests in their own city; tourists are out of frame).

Cover, with inline citations + reference list:
1. Authoritative hotel-occupancy data sources: Statistics Canada tourism / accommodation series
   (e.g. monthly occupancy rate, ADR, RevPAR; name the current table numbers), STR/CoStar, provincial
   tourism boards, and any open series. Note coverage, frequency, and geography.
2. The typical DIURNAL guest-presence shape inside hotel guest rooms (overnight occupancy high,
   daytime partial for business vs leisure travellers) and how energy models (NECB/ASHRAE hotel
   prototype) schedule guest rooms vs lobby/amenity/back-of-house.
3. Monthly / seasonal occupancy variation and the COVID-19 collapse-and-recovery trajectory in
   Canadian hotel occupancy.
4. Methods to forecast hotel occupancy to ~2030 from a monthly series (SARIMA / ETS / structural
   time-series with a COVID indicator); recommended approach and pitfalls.
5. How to combine a fixed unit-normalised diurnal guest-room shape with a monthly occupancy
   amplitude to produce a defensible per-30-minute schedule.

Deliver: a list of named, citable data sources with table IDs; a typical guest-room diurnal shape
(weekday/weekend); a monthly seasonality summary for Canada; and a recommended forecasting recipe.
```

---

## PROMPT 9 — Standard reference schedules: modulate vs replace, and code-compliant baselines

```
You are a building-energy-codes specialist. Document the STANDARD reference occupancy (and the linked
lighting / plug-load / HVAC) schedules used in building energy modelling, and the correct way to
inject a measured/synthetic occupancy signal on top of them.

Cover, with inline citations + reference list:
1. The standard occupancy schedules and peak densities (people/m², W/m²) for office, retail, and
   hotel in: ASHRAE 90.1 Appendix G, the US DOE commercial prototype building models, and Canada's
   NECB (NECB 2017/2020). Give the canonical weekday/weekend schedule fractions and peak densities.
2. The methodological distinction between (a) REPLACING a baseline schedule with a measured/synthetic
   one, vs (b) MODULATING the baseline by a presence multiplier while keeping code-compliant peak
   densities. When is each appropriate, and what do published studies do?
3. How keeping code-of-record peak densities matters for regulatory comparability, and what breaks if
   you overwrite them.
4. How occupancy interacts with dependent schedules (lighting follows occupancy and daylight; plug
   loads have a non-zero base load; HVAC setback follows occupancy) — recommended coupling rules.
5. Resolution conventions (hourly vs 30-min vs 10-min) in EnergyPlus Schedule:Compact / Schedule:File
   and any loss from down-sampling occupancy to 30-min.

Deliver: a table of standard peak densities + schedule fractions per use per standard, and a decision
rule for "modulate vs replace" per building use, with citations.
```

---

## PROMPT 10 — Mixed-use tall buildings: cross-use interactions, alternatives, and failure modes

```
You are a UBEM / mixed-use-building researcher. Investigate the specific challenges of modelling
occupancy in MIXED-USE TALL / SUPERTALL buildings that stack residential, office, retail, and hotel
uses in one structure, and survey the ALTERNATIVE approaches and documented FAILURE MODES.

Cover, with inline citations + reference list:
1. Studies that model occupancy and energy for vertically mixed-use towers; how they handle the
   coexistence of multiple use schedules, shared cores/services, and inter-zone coupling.
2. Whether and how occupancy in different uses is correlated within one building or city (e.g. office
   workers becoming retail customers at lunch; commuting links residential-empty with office-full)
   and whether any model captures these cross-use dependencies vs treating channels independently.
3. The trade-off between a SHARED-BACKBONE multi-channel generative model (one encoder, several output
   heads) and SEPARATE per-use models: documented pros, cons, and any head-to-head comparisons.
4. Documented failure modes and reviewer criticisms in occupancy-for-energy work: identifiability,
   double-counting people across uses, mismatched data frames, over-fitting marginals, ignoring
   stochastic diversity between identical zones.
5. The treatment of service / MEP / circulation space (often ~50% of gross floor area) — is it left on
   baseline or modelled, and what's the energy materiality?

Deliver: a synthesis of best practices for mixed-use occupancy modelling, an explicit list of pitfalls
to design against, and a recommendation on shared-backbone vs separate-models for a 2→4 channel build.
```

---

## After the reports come back

- Save each as `dr_01_…` … `dr_10_…` in this folder.
- Extract: (a) confirmed diurnal shapes per use → feeds the `s(t)` curves and validation targets;
  (b) the model-family decision → confirms/replaces the multi-head Transformer choice;
  (c) the validation menu → hardens the gates in both split docs;
  (d) the hotel/retail data-source list → fills the `external/` inputs for Leg 3.
- Then, and only then, we freeze the Leg 2 (`2-channel_split.md`) design and start building.
