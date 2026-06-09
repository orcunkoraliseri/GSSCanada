# Deep-research prompts — methodology & technique literature (Steps 1–9)

**Purpose.** Each prompt below pulls the **peer-reviewed precedent and justification** for one
methodological choice in the pipeline, to back the Methods section and sharpen the Introduction's
gap statement of the 2nd journal paper. These target *method justification* — not numeric anchors
(those were covered by `Step9_docs/prompts/DR_prompt_SHEU_regional_anchors.md` and
`..._activity_appliance_mapping.md`).

**How to use.**
- Paste **one fenced block at a time** into a web-based deep-research tool (Gemini / ChatGPT / Claude
  with web/Deep Research). Each block is **self-contained** — the tool needs no access to our repo.
- Save each returned report into `writing/litReview/` (e.g. `litReview/S4_generative_models.md`).
- **Verify every DOI and quote** the tools return — deep-research LLMs hallucinate citations. Each
  prompt explicitly asks the tool to verify DOIs and flag anything it cannot substantiate.
- Seed sources are **starting points** ("verify and expand"), chosen because they are well-established;
  do not treat them as the full set, and confirm they exist before citing.

**Prompt → claim → manuscript section map.**

| Prompt | Defends the claim that… | Feeds § |
|---|---|---|
| DR-S1 | national time-use surveys are a valid empirical basis for building occupancy | Intro, Methods (Data) |
| DR-S2 | pooling/harmonizing multi-wave surveys (incl. mode change) is sound | Methods (Harmonization) |
| DR-S3 | the 10-/30-min tiling + diary-day convention is appropriate for BEM | Methods (Temporal) |
| DR-S4 | a deep generative model is a defensible way to synthesize unobserved diaries | Methods (Augmentation) |
| DR-S5 | statistical matching can link time-use to the dwelling stock | Methods (Linkage) |
| DR-S6 | forecasting occupancy to a future year (with a COVID break) is methodologically grounded | Methods (Forecast), Discussion |
| DR-S7 | diary-driven occupancy + metabolic schedules beat standard fixed schedules in BEM | Methods (BEM integration), Intro (gap) |
| DR-S8 | Monte-Carlo occupancy ensembles + load-shape/peak metrics are the right analysis | Methods (Simulation), Results |
| DR-S9 | activity-based bottom-up load modelling calibrated to national totals is established | Methods (Activity loads, SI) |
| DR-X1 | the *forward-looking, calibrated, activity-resolved load-shape* framing is a genuine gap | Intro (novelty/contribution) |

---

## DR-S1 — Time-use surveys as a basis for building occupancy & activity modelling

**Purpose.** Backs Step 1: using national GSS Time-Use episode microdata (activity, home/away location,
co-presence) as the empirical basis for occupancy schedules, instead of fixed/standard schedules.

```
You are doing deep research for a peer-reviewed building-energy paper. I need the scholarly precedent
and justification for using NATIONAL TIME-USE SURVEY (TUS) microdata as the empirical basis for
building occupancy and activity schedules. WHAT WE DO: from Canada's General Social Survey – Time Use
(GSS-TUS), we use the episode file — activity code, location (home vs away → a presence flag), and
co-presence (who else is present) — as the raw material for residential occupancy schedules feeding
EnergyPlus, in place of deterministic ASHRAE/NECB schedules.

FIND, from peer-reviewed literature (seminal + recent, last ~5 yr):
1. Studies that derive realistic occupancy/activity profiles for building energy from time-use
   surveys (HETUS, ATUS, national TUS), and the argument that diary-based occupancy is more realistic
   than standard fixed schedules.
2. How "location = home" in a diary is used as an occupancy/presence proxy, and its known limitations.
3. The representativeness, strengths, and biases of TUS for occupancy modelling (sample size, single
   diary day per respondent, self-report).
4. The HETUS harmonised standard and its role in this literature.

SEED SOURCES (verify and expand — do NOT fabricate): Widén et al. (2009) and Widén & Wäckelgård
(2010, Applied Energy); Aerts et al. (2014, Building & Environment) on identifying/modelling realistic
domestic occupancy from TUS; Wilke et al. (2013); Tanimoto / Yamaguchi & Shimoda; Eurostat HETUS
guidelines.

DELIVER: an annotated bibliography — for each source: full citation (authors, year, title, venue,
verified DOI/URL), a 2–3 sentence summary, and one line "How it supports our claim." Then a short
synthesis paragraph, and a list of any CONTRADICTING evidence or documented pitfalls of TUS-based
occupancy. Verify every DOI; flag anything you cannot substantiate.
```

---

## DR-S2 — Harmonizing repeated cross-sectional surveys (incl. collection-mode change)

**Purpose.** Backs Step 2: pooling four GSS cycles (2005/2010/2015/2022) across questionnaire
redesigns, recoding categories, crosswalking activity codes to a common 14-category scheme, and
treating collection-mode (CATI → web) and income-regime changes as covariates.

```
You are doing deep research for a peer-reviewed paper. I need the methodological literature on
HARMONIZING repeated cross-sectional / multi-wave surveys for pooled longitudinal analysis. WHAT WE
DO: we pool four cycles of a national time-use survey spanning 2005–2022 onto one schema — renaming
variables, recoding category systems, crosswalking ~60+ raw activity codes to a common 14-category
scheme, enforcing a common missing-value convention, and flagging the data-collection MODE change
(telephone CATI → self-administered web) and an income-measurement regime change as model covariates
rather than dropping the affected cycles.

FIND (seminal + recent peer-reviewed):
1. Ex-ante vs ex-post harmonization of cross-national / multi-wave surveys (frameworks, best practice).
2. Survey MODE EFFECTS (interviewer-administered vs self-administered/web) on time-use and behavioural
   reporting — measurement error, and the practice of controlling for mode as a covariate.
3. Activity-classification harmonization across survey generations (HETUS / ICATUS crosswalks) and the
   risk of pooling raw, uncrosswalked codes.
4. Comparability and known artefacts when pooling repeated cross-sections over long spans.

SEED SOURCES (verify/expand): CESSDA / IPUMS / DDI harmonization guidance; literature on web-vs-CATI
mode effects in surveys; ICATUS and HETUS activity-coding documentation; methodological texts on
pooling repeated cross-sectional data.

DELIVER: annotated bibliography (full citation + verified DOI/URL, 2–3 sentence summary, "How it
supports our claim" line), a synthesis paragraph, and any contradicting/cautionary findings (e.g.
when mode effects cannot be controlled by a covariate). Verify all DOIs; flag unsubstantiated items.
```

---

## DR-S3 — Temporal representation: slot tiling, resolution choice, diary-day convention

**Purpose.** Backs Step 3: tiling episodes to 144 ten-minute HETUS slots, downsampling to 48
thirty-minute slots by majority vote, the 4 AM diary-day origin, and the 1440-minute closure QA.

```
You are doing deep research for a peer-reviewed building-energy paper. I need literature justifying
the TEMPORAL REPRESENTATION of time-use-derived occupancy schedules. WHAT WE DO: we tile variable
episodes into 144 fixed 10-minute slots (HETUS), then downsample to 48 thirty-minute slots by
majority vote (with presence-priority tie-breaking), for input to EnergyPlus. The diary day starts
at 04:00 (4 AM-origin), and we enforce a quality check that each respondent's episode durations sum
to exactly 1440 minutes.

FIND (peer-reviewed):
1. The HETUS 10-minute slot convention and its use in occupancy/load modelling.
2. The EFFECT of occupancy-schedule temporal resolution (1-min vs 10-min vs 30-min vs hourly) on
   simulated building energy and especially PEAK demand — i.e. what resolution is "enough" and what is
   lost by coarsening. (This directly supports our choice of 30-min/hourly for annual BEM.)
3. The 4 AM (or similar) diary-day START-TIME convention in time-use surveys and correct handling when
   mapping a diary onto a real 24-h clock.
4. Time-use data-quality conventions, including the 1440-minute closure constraint.

SEED SOURCES (verify/expand): Eurostat HETUS guidelines; Widén, Aerts, Wilke on occupancy resolution;
building-simulation studies on schedule resolution vs peak accuracy.

DELIVER: annotated bibliography (citation + verified DOI/URL, summary, "How it supports our claim"),
a synthesis paragraph stating the consensus on adequate resolution for annual energy vs sub-hourly
peak, and any contradicting evidence. Verify DOIs; flag anything unverifiable.
```

---

## DR-S4 — Deep generative models for synthetic activity/occupancy sequences

**Purpose.** Backs Step 4: a conditional Transformer + masked discrete-diffusion (MDLM) model that
synthesizes each respondent's 2 unobserved day-types, conditioned on demographics, validated by
Jensen-Shannon divergence.

```
You are doing deep research for a peer-reviewed paper. I need the literature placing DEEP GENERATIVE
MODELS as a defensible method for synthesizing human activity/occupancy SEQUENCES. WHAT WE DO: each
time-use respondent reports only one diary day (Weekday, Saturday, or Sunday). We train a conditional
Transformer encoder–decoder with a MASKED DISCRETE-DIFFUSION objective to generate the 2 UNOBSERVED
day-types per respondent (48 half-hour slots × categorical activity + binary presence + co-presence),
conditioned on demographics and cycle-year. We validate generated vs observed distributions with
Jensen–Shannon divergence, and we are aware of exposure bias (teacher-forced training loss ≠ inference
quality).

FIND (seminal + recent peer-reviewed and major-venue ML):
1. Generative models for occupancy / activity / human-mobility SEQUENCE synthesis in the energy and
   mobility literatures; the shift from Markov-chain generators to neural sequence models (RNN/
   Transformer) and their reported gains.
2. DISCRETE / MASKED DIFFUSION models for categorical sequences — the methodological basis we use.
3. CONDITIONAL generation on covariates; data augmentation for occupancy/behaviour where each subject
   is under-observed.
4. VALIDATION practice for synthetic behavioural sequences (distributional metrics incl. JS
   divergence) and the exposure-bias / teacher-forcing pitfall.

SEED SOURCES (verify/expand — do NOT fabricate): Austin et al. (2021) Structured Denoising Diffusion
in Discrete State-Spaces (D3PM); Lou, Meng & Ermon (2023/24) score-entropy discrete diffusion (SEDD);
Sahoo et al. (2024) Simple & Effective Masked Diffusion Language Models (MDLM); neural occupancy/
activity generators (e.g. Pang, Kazmi, Lu, Chuang and similar) — search for the actual recent papers.

DELIVER: annotated bibliography (citation + verified DOI/URL, summary, "How it supports our claim"),
a synthesis paragraph contrasting Markov vs neural vs diffusion generators for activity sequences,
and any evidence on limits/failure modes of generative occupancy models. Verify DOIs; flag any you
cannot confirm.
```

---

## DR-S5 — Statistical matching / data fusion of surveys with no common identifier

**Purpose.** Backs Step 5: probabilistically linking GSS occupants to the Census dwelling stock via
shared sociodemographics (clustering + classifier → per-archetype building-attribute distributions),
with no shared respondent ID.

```
You are doing deep research for a peer-reviewed paper. I need the methodological literature on
STATISTICAL MATCHING / DATA FUSION of two independent surveys that share NO common record identifier.
WHAT WE DO: the time-use survey lacks dwelling/building variables; the Census provides them but shares
no ID with the time-use survey. We link them probabilistically on shared sociodemographic attributes
(province, age, sex, marital status, household size, labour force, income, occupation) — clustering
time-use respondents into occupant archetypes and using a classifier to assign each Census record an
archetype, then aggregating Census building attributes (dwelling type, bedrooms, year built, etc.)
into per-archetype distributions for building-energy modelling.

FIND (seminal + recent peer-reviewed):
1. Statistical matching / data fusion theory and practice, including the conditional-independence
   assumption and its risks, and how matching quality/uncertainty is assessed.
2. Synthetic population generation for building/urban energy and transport (IPF / iterative
   proportional fitting, combinatorial optimization, sample-free methods) as the adjacent toolkit.
3. Studies that link time-use or behavioural surveys to HOUSING/BUILDING stock or assign dwelling
   archetypes to occupant types.

SEED SOURCES (verify/expand): Rässler (2002) "Statistical Matching" (Springer); D'Orazio, Di Zio &
Scanu (2006) "Statistical Matching: Theory and Practice" (Wiley); Beckman, Baggerly & McKay (1996) on
synthetic populations / IPF; synthetic-population reviews in urban energy/transport modelling.

DELIVER: annotated bibliography (citation + verified DOI/URL, summary, "How it supports our claim"),
a synthesis paragraph on when statistical matching is valid and how to report its uncertainty, and any
contradicting/cautionary findings (e.g. bias under violated conditional independence). Verify DOIs.
```

---

## DR-S6 — Forecasting occupancy/behaviour across survey waves (with a COVID structural break)

**Purpose.** Backs Step 6: progressive fine-tuning with weight inheritance across cycles, recency
weighting, a "predict the next unseen wave" (True-Future-Test) validation, drift quantification, and a
2030 forecast with scenario features capturing post-COVID telework persistence.

```
You are doing deep research for a peer-reviewed paper. I need literature grounding the FORECASTING of
human time-use/occupancy behaviour to a FUTURE year from successive survey waves. WHAT WE DO: using
four time-use waves (2005–2022) we forecast occupancy to 2030 by progressive fine-tuning with weight
inheritance (each wave's model initialised from the prior), recency-weighting recent waves more, and
validating by a "true future test" — a model trained up to wave T is evaluated on the next unseen wave
T+5. We quantify behavioural DRIFT between waves and inject 2030 scenario features (work-from-home
rates, population aging). The 2015→2022 wave shows a COVID structural break (a large rise in at-home
time) that we model as persisting to 2030.

FIND (peer-reviewed, seminal + recent):
1. Forecasting / projecting human behaviour or time-use trends over years/decades, and how such
   forecasts are validated (e.g. backtesting on held-out future periods).
2. Transfer / continual learning under TEMPORAL DISTRIBUTION SHIFT and CONCEPT DRIFT — methods and
   evaluation.
3. COVID-19 impact on TIME USE, telework adoption and its PERSISTENCE, and on RESIDENTIAL energy
   demand — evidence for a durable structural break.
4. Demographic / behavioural scenario projection practice (national statistics agency / UN style).

SEED SOURCES (verify/expand): Gama et al. (2014) survey on concept-drift adaptation; literature on
telework persistence post-COVID and pandemic residential-energy increases; Statistics Canada / UN
population & labour projections; continual-learning surveys.

DELIVER: annotated bibliography (citation + verified DOI/URL, summary, "How it supports our claim"),
a synthesis paragraph on the credibility of multi-year behavioural forecasts and the value of the
next-wave validation design, and any contradicting evidence (e.g. studies finding telework reverting).
Verify DOIs; flag unverifiable claims.
```

---

## DR-S7 — Occupancy → BEM schedules, metabolic gains, and the standard-schedule gap

**Purpose.** Backs Step 7: converting diaries to EnergyPlus `Schedule:Compact` (Weekday/Weekend),
mapping activity → metabolic heat (MET → W), and the argument that diary-driven occupancy/internal
gains improve on standard fixed schedules.

```
You are doing deep research for a peer-reviewed building-energy paper. I need the literature on
turning occupancy/activity data into BUILDING-ENERGY-MODEL inputs and on the value of doing so. WHAT
WE DO: we convert per-household occupancy + activity diaries into EnergyPlus Schedule:Compact objects
(Weekday/Weekend), and map each activity to a METABOLIC heat-output rate (MET → W/person) to drive the
People object's internal gains — replacing the deterministic occupancy/gain schedules in standards
(ASHRAE 90.1 / NECB).

FIND (seminal + recent peer-reviewed):
1. The "performance gap" / discrepancy between standard fixed occupancy schedules and real occupancy,
   and the energy impact of using realistic vs standard schedules in simulation.
2. Stochastic / measured / data-driven occupancy schedules in EnergyPlus and similar engines (and
   tools/frameworks for generating them, e.g. obFMU, DNAS).
3. METABOLIC rate standards and sources for activity-to-heat mapping: ASHRAE Standard 55, ISO 7730,
   and the Compendium of Physical Activities (MET values) — and how internal-gain assumptions affect
   simulated energy.
4. The IEA EBC Annex 66 / Annex 79 framing of occupant behaviour in building performance simulation.

SEED SOURCES (verify/expand): de Wilde (2014) on the predicted-vs-measured performance gap; Yan et al.
(2015, Energy & Buildings) occupant-behaviour modelling for BPS; Hong et al. DNAS / obFMU; ASHRAE 55;
ISO 7730; Ainsworth et al. Compendium of Physical Activities.

DELIVER: annotated bibliography (citation + verified DOI/URL, summary, "How it supports our claim"),
a synthesis paragraph quantifying (where literature allows) the energy sensitivity to occupancy/gain
schedule realism, and any contradicting findings (cases where schedule realism barely moves annual
energy — relevant to our own phase-invariance observation). Verify DOIs.
```

---

## DR-S8 — Monte-Carlo occupancy ensembles, diversity factors, and load-shape/peak analysis

**Purpose.** Backs Step 8: paired Monte-Carlo over household occupancy ensembles (single archetype →
stock), frozen-frame attribution, and load-shape metrics (load factor, peak-to-average, coincidence/
diversity factor, peak timing).

```
You are doing deep research for a peer-reviewed building-energy paper. I need the literature behind a
MONTE-CARLO OCCUPANCY-ENSEMBLE simulation design and LOAD-SHAPE analysis. WHAT WE DO: we run one
archetype building model many times, each with a different household's occupancy time-series sampled
from a calibrated population; the ENSEMBLE is the stock-scale result (occupant diversity without
simulating every dwelling). We use a PAIRED design — the same households simulated across years with
building and weather held fixed — so cross-year deltas isolate the occupancy effect. We report
LOAD-SHAPE metrics: diurnal profile, load factor, peak-to-average ratio, daily ramp, ensemble
coincidence/diversity factor, and peak magnitude + timing.

FIND (seminal + recent peer-reviewed):
1. OCCUPANT BEHAVIOUR as a driver of building energy and the performance gap (IEA EBC Annex 53/66/79).
2. MONTE-CARLO / stochastic occupancy and the resulting VARIANCE in energy predictions; how ensemble
   size / convergence is handled.
3. DIVERSITY and COINCIDENCE factors in residential electricity load, and load-shape / peak-demand
   metrics relevant to grids and demand response.
4. ARCHETYPE-based building-stock / urban building energy modelling (UBEM) — single-building →
   stock-scale inference.
5. Paired / differencing / within-sample designs for clean attribution of an intervention or driver.

SEED SOURCES (verify/expand): IEA EBC Annex 66 outputs and Yan et al. (2017); Reinhart & Cerezo Davila
(2016, Building & Environment) UBEM review; literature on residential diversity/coincidence factors and
peak-demand load shapes; stochastic-occupancy energy-variance studies.

DELIVER: annotated bibliography (citation + verified DOI/URL, summary, "How it supports our claim"),
a synthesis paragraph on why ensemble + paired design is sound for stock-scale occupancy attribution,
and any contradicting/limiting findings. Verify DOIs; flag unverifiable items.
```

---

## DR-S9 — Activity-based bottom-up load modelling, calibration to national totals, co-presence

**Purpose.** Backs Step 9: activity→appliance crosswalk, two-tier baseload/activity split, per-end-use
calibration to NRCan SHEU totals, sub-linear "effective-occupancy" co-presence for shared devices, and
activity-shaped lighting — validated against measured Canadian load. (DR-1/DR-2 pulled the *numbers*;
this prompt targets the *method justification* and how peers validated.)

```
You are doing deep research for a peer-reviewed paper. I need the METHODOLOGICAL literature (not raw
numbers) establishing ACTIVITY-BASED BOTTOM-UP residential electricity load modelling and how such
models are validated. WHAT WE DO: we split each home's electricity into a flat always-on BASELOAD
(fridge/freezer/standby) and an ACTIVITY-DRIVEN part; we shape the activity-driven part with our
predicted time-use activities via an activity→end-use crosswalk; we apply CO-PRESENCE scaling
(sub-linear "effective occupancy" for shared devices like TV/cooking; ~linear for personal devices);
and we CALIBRATE each end use's annual total to national survey statistics with a single per-end-use
scalar. Crucially, we already PREDICT the activities, so we do NOT generate them stochastically
(no Markov chains / switch-on probabilities).

FIND (seminal + recent peer-reviewed):
1. Bottom-up STOCHASTIC residential electricity demand models and the activity→appliance principle.
2. The TWO-TIER (baseload vs activity-driven) decomposition and the EFFECTIVE-OCCUPANCY / shared-vs-
   personal device scaling — exact methodological basis.
3. CALIBRATION of bottom-up load models to NATIONAL survey totals (per-end-use scaling) and why it is
   accepted practice.
4. VALIDATION of such models against HIGH-RESOLUTION MEASURED end-use data — which metrics (load
   shape, peak timing, diversity factor) and which datasets, especially Canadian.
5. Whether using an EXTERNALLY PREDICTED activity sequence (instead of a stochastically generated one)
   to drive the load model is supported / precedented.

SEED SOURCES (verify/expand): Richardson, Thomson, Infield & Clifford (2010, Energy & Buildings 42(10),
DOI 10.1016/j.enbuild.2010.05.023); McKenna & Thomson (2016, Applied Energy 165, CREST); Widén &
Wäckelgård (2010, Applied Energy 87(6)); Armstrong et al. (2009, J. Building Performance Simulation
2(1)); the 2023 "Stochastic bottom-up load profile generator for Canadian households" (Building &
Environment, DOI 10.1016/j.buildenv.2023.110466); validation data Saldanha & Beausoleil-Morrison
(2012, Energy & Buildings 49, DOI 10.1016/j.enbuild.2012.02.013) and Johnson & Beausoleil-Morrison
(2017, Applied Thermal Engineering 114).

DELIVER: annotated bibliography (citation + verified DOI/URL, summary, "How it supports our claim"),
a synthesis paragraph on the standing of activity-based bottom-up calibrated load models, and any
contradicting/cautionary findings (e.g. on 30-min resolution flattening appliance peaks). Verify DOIs.
```

---

## DR-X1 (cross-cutting, optional) — Novelty positioning & research gap

**Purpose.** Sharpens the Introduction's contribution claim: a *forward-looking, calibrated,
activity-resolved behavioural occupancy time-series → BEM load shape & peak timing* (vs prior work's
non-time-series diversity factors → annual energy). Use this to find the closest competing works and
differentiate.

```
You are doing deep research for the INTRODUCTION of a peer-reviewed building-energy paper. I need to
locate and characterise the RESEARCH GAP our work fills, and the closest competing studies to
differentiate from. OUR CONTRIBUTION: prior building-energy work largely drives simulations with
NON-time-series occupancy (demographic diversity factors → annual energy). We instead predict
occupancy as a CALIBRATED BEHAVIOURAL TIME-SERIES (presence + co-presence + activity from national
time-use data), FORECAST it to a future year (2030, incl. a COVID structural break), resolve it to
END-USE loads (equipment, lighting), and drive EnergyPlus to study the LOAD SHAPE, PEAK MAGNITUDE and
PEAK TIMING at stock scale — i.e. the contribution is "when" energy is used, not just "how much."

FIND (recent reviews + key primary studies):
1. State-of-the-art reviews of OCCUPANT BEHAVIOUR in building performance simulation (IEA EBC Annex
   66/79) and of occupancy-schedule generation methods.
2. Studies that FORECAST occupancy/behaviour to future years for energy (rare — find the closest).
3. Studies linking time-use → residential LOAD SHAPE & PEAK (and demand-response relevance).
4. Where the gap is: forward-looking + calibrated + activity-resolved + stock-scale + load-shape-
   focused — identify which of these dimensions prior work covers and which it omits.

SEED SOURCES (verify/expand): Yan et al. (2015/2017) occupant-behaviour BPS reviews; Hong et al.
occupant-behaviour framework papers; de Wilde (2014) performance gap; Reinhart & Cerezo Davila (2016)
UBEM review; recent (≤5 yr) occupancy-forecasting and time-use-to-load papers.

DELIVER: (a) annotated bibliography (citation + verified DOI/URL, summary, relevance), (b) a GAP TABLE
— rows = the closest 8–12 studies, columns = [uses time-series occupancy? calibrated? forecast to
future? activity/end-use resolved? stock-scale? load-shape/peak focus?] with ✓/✗ — so the gap our
paper fills is visually obvious, and (c) a 1-paragraph draft "contribution vs prior work" statement.
Verify every DOI; flag anything you cannot confirm and note where our claimed novelty may already be
partially covered.
```
