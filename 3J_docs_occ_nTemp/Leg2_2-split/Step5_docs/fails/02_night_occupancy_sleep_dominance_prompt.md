# Deep-Research Prompt 2 — Overnight Home-Occupancy & Sleep-Dominance Thresholds for Synthetic Occupancy (3J Step-5 night gates)

> Paste everything below this line into a fresh deep-research session (Gemini / Claude / GPT deep research).

---

## Role

You are a methodologist in **time-use survey microdata, shift-work statistics, and occupant-behaviour
modelling for building energy simulation (BEM)**. Produce a rigorously sourced brief that:

1. **establishes the empirically defensible overnight home-occupancy fraction and sleep-activity
   dominance** from published time-use data and shift-work statistics;
2. **judges whether our two night validation gates (≥85% overnight at-home, ≥70% sleep dominance) are
   correct or too strict**, given the real prevalence of night/shift work; and
3. if the gates are right, **identifies methods to correct the synthetic night profile**; if they are too
   strict, **recommends defensible revised thresholds** (low / central / high) with citations.

Every numeric claim must cite a **named, dated source** (Statistics Canada GSS-Time Use and Labour Force
Survey; ATUS / Eurostat HETUS / MTUS; IEA EBC Annex 66/79; ASHRAE / NECB; peer-reviewed occupancy models).
No numbers without a citation; flag analyst estimates.

## Context (the pipeline and the failure)

We generate **synthetic 24-hour time-use diaries** (48 × 30-min slots) from the Canadian GSS-Time Use +
Census to drive **EnergyPlus** occupancy schedules. After a frozen diffusion generator + a
marginal-preserving rake (Step 4), each Census person is linked to a diary donor and the channels are
copied verbatim (Step 5). Validation compares the full linked population (192k-scale) against the
**observed (real-diary) subset**. Two **night gates** fail:

| Gate | Our value | Threshold | Verdict so far |
|---|---|---|---|
| Overnight AT_HOME (validator slots 1–8, the small hours ≈ 00:00–04:00) | **83.13%** | **≥ 85%** | just under |
| Night **sleep dominance** (share of the overnight window whose dominant activity is sleep) | **61.15%** | **≥ 70%** | under |

**Hypothesised cause:** the 192k-scale pool contains genuine **night-shift workers and diverse
night-activity profiles**; the thresholds were inherited from an earlier **residential-only** study that
implicitly assumed an "everyone home and asleep at night" population. We need the literature to confirm or
refute that the thresholds, not the model, are the issue.

## Part 0 — Methodology basis

Provide, with sources:

1. Define **"overnight home occupancy"** and **"sleep dominance"** as the occupancy/time-use literature
   reports them (presence-at-home curves by time of day; share of population asleep by clock time).
2. State the standard **diary-day convention** (e.g. 04:00–04:00 start in many time-use surveys) and why
   the **slot-to-clock mapping** matters when judging a "night" window — flag the risk of comparing the
   wrong hours.
3. Identify the **single biggest source of error** in estimating night occupancy/sleep from diaries
   (under-coverage of shift workers, weighting, secondary-activity sleep, diary-day boundary effects).

## Part A — Empirical benchmark (low / central / high + citation)

1. **Overnight at-home fraction** — share of the population physically at home in the small hours, from
   StatCan GSS-Time Use, ATUS, HETUS, MTUS. Is **83%** within the observed range, or genuinely low?
2. **Sleep dominance / share asleep** overnight — share of the population whose primary activity is sleep
   in the deep-night window; how it varies by hour. Judge **61%** against this.
3. **Night / shift-work prevalence** — fraction of the Canadian workforce on night, evening, rotating, or
   irregular shifts (StatCan Labour Force Survey / work-arrangements data), and the **implied depression**
   of overnight home occupancy and sleep dominance. Translate this into "how far below 100% should night
   occupancy realistically be?"

## Part B — Threshold validity (the central question)

1. Do **BEM occupancy standards and models** assume near-100% night residential occupancy, or do they
   explicitly model a shift-work / awake-at-night tail? Survey ASHRAE / NECB defaults, **IEA EBC Annex
   66/79**, and stochastic occupancy models (**Richardson, Thomson & Infield 2008**; **Widén &
   Wäckelgård**; **Aerts et al.** occupancy archetypes; **CREST / McKenna**).
2. Given the empirical night/shift-work tail, are **≥85% overnight-at-home** and **≥70% sleep-dominance**
   defensible acceptance thresholds for a *population-representative* synthetic dataset, or are they too
   strict (residential-era)?
3. Recommend **defensible revised thresholds** (low / central / high) for each gate, each tied to a
   citation, OR conclude the current ones are correct and the model is at fault.

## Part C — Remediation if the gates are correct

If the literature says the gates are right and the synthetic night profile is genuinely off, enumerate and
assess methods (mechanism + evidence + preserves-marginals + needs-retraining + risk):

- **Conditioning night profiles on shift-work / employment status** (mixture of day-worker vs
  shift-worker night archetypes).
- **Reweighting / raking** the night-occupancy marginal to the observed target (marginal-preserving,
  no re-training).
- **Donor-stratified linkage** (Step-5-compatible) so the night-time mix matches observed.
- Note explicitly which fixes touch the **frozen Step-4 generator** vs which live in Step 5 / post-hoc.

## Output format

- A **methodology note** (Part 0): definitions, diary-day/slot-to-clock caveat, biggest error source.
- A **benchmark table** (Part A): overnight at-home %, sleep-dominance %, night/shift-work prevalence —
  low / central / high + source — with a verdict on our 83.13% and 61.15%.
- A **threshold verdict** (Part B): for each gate, "current threshold OK / revise to X (low/central/high)",
  one line each, each cited; plus how BEM standards treat night occupancy.
- A **remediation table** (Part C), only if the gates are upheld: methods × (mechanism, evidence,
  preserves-marginals, needs-retraining, risk, rank).
- **Worked / cited examples:** 2–4 datasets or studies reporting overnight occupancy and sleep curves,
  ideally Canadian / cold-climate.
- Full **reference list** with dates and URLs.

## Hard requirements

- Anchor every value to a **named, dated source** (prefer StatCan GSS-TU + LFS / ATUS / HETUS / IEA EBC /
  ASHRAE-NECB); flag analyst estimates.
- Prioritise **Canadian** evidence for prevalence and occupancy; international for method, flagged.
- Be explicit about the **diary-day start and the slot→clock mapping** before declaring any hour "night"
  — this is the most likely silent error.
- Give benchmarks and any recommended thresholds as **low / central / high**.
- Adversarially check the headline night/shift-work prevalence and overnight-occupancy figures against
  **≥2 independent sources**; report disagreement rather than averaging silently.
