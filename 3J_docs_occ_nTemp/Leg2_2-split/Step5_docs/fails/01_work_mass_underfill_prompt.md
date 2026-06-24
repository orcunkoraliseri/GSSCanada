# Deep-Research Prompt 1 — Work-Activity Peak Under-Representation in Synthetic Time-Use Diaries (3J Step-4 G4 → Step-5 AT_WORK / AT_HOME)

> Paste everything below this line into a fresh deep-research session (Gemini / Claude / GPT deep research).

---

## Role

You are a methodologist in **synthetic population generation, time-use survey microdata, and
occupant-behaviour modelling for building energy simulation (BEM)**. Produce a rigorously sourced brief that:

1. **explains why** a generative model of daily time-use diaries systematically **under-produces daytime
   work activity**, and whether this is a recognised failure mode;
2. **benchmarks** our observed/synthetic work-occupancy numbers and our validation tolerance against
   published time-use statistics; and
3. **identifies and ranks solution methods** to close the work-mass gap — **prioritising methods
   compatible with a marginal-preserving (raked) pipeline in which the upstream generator is frozen**, and
   clearly flagging which methods would require re-training the generator.

Every numeric claim must cite a **named, dated source** (Statistics Canada; ATUS / Eurostat HETUS / MTUS;
IEA EBC Annex 66/79; peer-reviewed methods or BEM occupancy papers). Do not assert numbers without a
citation. Where Canadian time-use evidence is thin, use international sources and say so.

## Context (the pipeline and the failure)

We build **synthetic 24-hour time-use diaries** (48 × 30-min slots) from the Canadian **General Social
Survey – Time Use** plus **Census**, to drive **EnergyPlus** occupancy schedules for a residential +
office study. The relevant stages:

- **Step 4 (generation + calibration):** a **discrete / masked-diffusion sequence model** generates each
  diary's activity track (`act30`) plus two occupancy channels — `hom30` (AT_HOME) and `wrk30` (AT_WORK).
  A subsequent **iterative-proportional-fitting / raking** stage ("joint rake") then **forces the
  synthetic marginals to match the observed marginals exactly**, and a min-dwell smoother enforces minimum
  episode durations. **Step 4 is now frozen/locked.**
- **Step 5 (census linkage):** each Census person is matched to a diary donor (synthetic or observed) by a
  demographic fallback match; the donor's channels are copied verbatim. Validation compares the full
  linked population against the **observed (real-diary) subset**.

**The failure.** A temporal shape metric, "work-peak occupancy" (mean AT_WORK rate over the midday
work-peak window), is far below observed and **the rake cannot fix it** (raking corrects marginals, not the
joint time×activity structure). The numbers to validate and explain:

| Quantity | Value | Role |
|---|---|---|
| Observed midday work-peak occupancy | **28.72%** | empirical target |
| Synthetic midday work-peak occupancy | **18.39%** | model output |
| Gap (Step-4 gate "G4") | **−10.33 pp** (synthetic under-fills) | the root FAIL |
| Step-5 AT_WORK max-slot deviation | **10.18 pp** (gate ≤ 3 pp) | propagated, office channel |
| Step-5 AT_HOME max-slot deviation | **8.59 pp** (gate ≤ 3 pp) | daytime mirror, residential |
| Post-rake intra-day swap remedy | moved the gap only **0.1 pp** | why "just add mass" fails |

We are **not** re-deriving the model from scratch; we want the literature to (a) tell us whether this
under-fill is expected and why, (b) say whether our targets and the ±3 pp tolerance are reasonable, and
(c) supply **defensible, evidenced solution methods**.

## Part 0 — Methodology basis (the calibration backbone)

Provide, with sources:

1. Confirm/critique the principle that **marginal calibration (IPF / raking)** can match per-slot or
   per-activity **marginals exactly yet leave a joint/temporal co-occurrence metric (work mass in a
   specific midday window) uncorrected** — i.e. raking fixes margins, not joint structure. Name the
   general result and the standard remedies (raking to **2-way / multi-way control tables**, entropy
   balancing, calibration to joint margins).
2. Define **"work-peak occupancy"** precisely and state how the occupancy/time-use literature reports
   daytime employment presence (share of population at work by time of day; "activity rhythm" curves).
3. Identify the **single biggest source of error** when a simplified sequence generator reproduces
   structured midday work blocks (e.g. episode fragmentation, regression to the population mean,
   day-type mixing).

## Part A — Why generative models under-produce work episodes (mechanism + evidence)

1. Catalogue the **known failure modes** by which sequence/diffusion/Markov/HMM/deep generative models of
   activity or travel diaries **dilute or under-generate structured, high-amplitude daytime blocks**:
   mode collapse / rare-pattern smoothing, over-smoothing in diffusion, stationarity in Markov chains,
   label/class imbalance (employed vs not-in-labour-force), and averaging of heterogeneous day-types.
2. Pull evidence from the **synthetic activity-/travel-diary generation literature** (e.g. deep generative
   models for travel diaries — Borysov et al.; Badu-Marfo; Garrido et al.; and time-use/occupancy
   sequence generation) on whether work/commute episodes are a commonly under-reproduced pattern and why.
3. State whether **conditioning on employment / labour-force status / day-type** is the usual structural
   fix, and what is lost without it.

## Part B — Empirical benchmark & tolerance validity (low / central / high + citation)

1. **Daytime at-work occupancy fraction** in time-use data — the share of the (working-age / total)
   population recorded "at work / paid work" at the midday peak, from **StatCan GSS-Time Use**, **ATUS**,
   **Eurostat HETUS**, **MTUS**. Use this to judge whether **28.72%** is a plausible target and whether
   **18.39%** is implausibly low. Give **low / central / high**.
2. **Validation tolerance:** what **per-slot occupancy agreement** do synthetic-occupancy / BEM
   occupant-behaviour papers actually report or require (is **±3 pp/slot** standard, strict, or loose)?
   What goodness-of-fit metrics do they use (RMSE of activity-rhythm curves, peak-amplitude error)?
3. A **verdict** on our target/tolerance: is the ~10 pp under-fill a model defect, a day-type-mixing
   artefact, or partly a too-strict gate?

## Part C — Solution methods to close the work-mass gap (the core deliverable)

Enumerate and **assess each candidate**, with: mechanism, published evidence of efficacy, expected gap
reduction, **whether it preserves the exact 1-D marginals**, whether it requires **re-training the frozen
generator**, and risk of breaking other gates. Candidates to cover (add others you find):

- **Condition generation** on labour-force status / employment / day-type (two-stage: assign work-day
  skeleton, then fill).
- **Class-balanced / importance-weighted training** or oversampling of work-day diaries.
- **Add work-occupancy joint margins to the rake's control set** (rake to a time×activity 2-way table) —
  marginal-preserving, no re-training.
- **Post-hoc optimal-transport / reweighting** of the synthetic pool to a 2-D (time × at-work) target
  while preserving 1-D margins.
- **Copula / Gibbs post-processing** or guided/rejection sampling (SMC, classifier guidance) to steer
  toward work mass.
- **Donor-based correction in the linkage step** (Step-5-compatible bias toward work-bearing donors for
  employed agents) — and why this risks gaming a full-vs-observed validation.

Then **rank** the methods by (a) gap-closing efficacy, (b) compatibility with a **frozen generator +
exact 1-D marginals**, (c) risk to other gates — and name the **single most defensible** option for a
locked pipeline.

## Output format

- A **methodology note** (Part 0): why raking can't move this metric; the precise metric definition.
- A **mechanism brief** (Part A): ranked list of failure modes with citations.
- A **benchmark table** (Part B): observed daytime work occupancy (low/central/high + source), and a
  per-slot tolerance norm from the literature, with the verdict on our 28.72% / 18.39% / ±3 pp.
- A **solutions table** (Part C): rows = methods; columns = mechanism, evidence, expected effect,
  preserves-marginals (Y/N), needs-retraining (Y/N), risk, recommendation rank.
- **Worked / cited examples:** 2–4 studies where a synthetic activity model's work/peak deficit was
  diagnosed and corrected, with the before/after improvement.
- Full **reference list** with dates and URLs.

## Hard requirements

- Anchor every value to a **named, dated source** (prefer StatCan / ATUS / HETUS / IEA EBC / peer-reviewed);
  flag analyst estimates.
- Prioritise **Canadian time-use** evidence for the benchmark; use international sources for method, flagged.
- Give benchmarks as **low / central / high**; be explicit about **units and basis** (share of total vs
  working-age population; per-slot vs daily; diary-day start time).
- For every proposed solution, state explicitly whether it **preserves exact marginals** and whether it
  **requires re-training** — these two properties decide feasibility for our locked pipeline.
- Adversarially check each headline benchmark against **≥2 independent sources**; report disagreement
  rather than averaging silently.
