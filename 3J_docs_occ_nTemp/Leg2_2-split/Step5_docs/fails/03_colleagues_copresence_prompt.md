# Deep-Research Prompt 3 — Workplace Co-Presence ("with colleagues") Channel Sparsity in Synthetic Time-Use Data (3J Step-5 W3)

> Paste everything below this line into a fresh deep-research session (Gemini / Claude / GPT deep research).

---

## Role

You are a methodologist in **time-use "with whom" (social-context) data, multivariate synthetic-data
fidelity, and occupant social-occupancy modelling for internal-gains / building energy simulation**.
Produce a rigorously sourced brief that:

1. **explains how co-presence ("with whom") is recorded in time-use surveys** and **why a secondary,
   relatively rare positive channel gets under-generated** by multivariate / sequence generative models;
2. **benchmarks workplace co-presence rates** (time spent in the company of colleagues) from published
   time-use data; and
3. **identifies and ranks methods to correct the co-presence channel thinness** — **prioritising post-hoc
   / linkage-stage (Step-5-compatible) and marginal-preserving methods**, and flagging which would require
   re-training the frozen generator.

Every numeric claim must cite a **named, dated source** (Statistics Canada GSS-Time Use; ATUS "who" file;
Eurostat HETUS; MTUS; peer-reviewed synthetic-data or occupancy papers). No numbers without a citation.

## Context (the pipeline and the failure)

We generate **synthetic 24-hour time-use diaries** (48 × 30-min slots) from the Canadian GSS-Time Use +
Census for **EnergyPlus**. Alongside the activity track, each diary carries **9 co-presence channels**
(Alone / Spouse / Children / parents / other-in-family / other-household / friends / others /
**colleagues**), each a 48-slot 0/1 series. After a frozen diffusion generator + marginal-preserving rake
(Step 4), Census persons are linked to diary donors (Step 5) and channels are copied verbatim; validation
compares the full linked population against the **observed (real-diary) subset**.

**The failure (W3 — colleagues co-presence).** Important context: the channel had previously **collapsed to
~0** in the synthetic output due to a **join-key coding bug in the linkage, now fixed** — so it is alive
again. The **residual** gap is a **generation-thinness** effect, not a linkage bug:

| Quantity | Value | Notes |
|---|---|---|
| Observed colleagues co-presence (full population) | **14.88%** | empirical target |
| Synthetic colleagues co-presence (full population) | **10.51%** | model output (post-bug-fix) |
| Gap (W3) | **4.37 pp** | gate ≤ 3 pp → still FAIL |
| Per-worker nonzero rate, observed vs synthetic | **≈ 21.2%** vs **≈ 12.4%** | the synthetic channel is thinner |

The synthetic colleagues channel **exists and is carried faithfully** but is **systematically thinner**
than observed for the synthetic sub-population. We want the literature to (a) explain this under-generation,
(b) tell us a plausible target rate, and (c) supply evidenced correction methods — ideally ones that live
in the linkage/post-processing rather than the locked generator.

## Part 0 — Methodology basis

Provide, with sources:

1. How time-use surveys record **"with whom" / co-presence** (simultaneous companions, primary vs all
   present, the "who" file structure), and why co-presence is **harder to synthesise jointly** with
   activity and location than the activity track itself.
2. The distinction between matching the **co-presence marginal** vs the **joint (activity × location ×
   companion)** structure, and which one our ±3 pp gate actually tests.
3. The **single biggest source of error** in synthesising a binary secondary channel (conditional
   independence assumptions; rare-positive smoothing; loss-weighting across many channels).

## Part A — Why multivariate generators under-produce a positive secondary channel (mechanism + evidence)

1. Catalogue the failure modes by which generative models **under-fill rare/secondary positive channels**:
   class imbalance (most slots are "alone"/no-colleague), marginalisation/averaging toward zero,
   conditional-independence shortcuts that drop the companion given the activity, and multi-head loss
   dilution.
2. Evidence from **multivariate / tabular / sequential synthetic-data fidelity literature** (e.g.
   copula-based generators; SDV / synthcity fidelity metrics; deep generative models for activity-travel
   diaries) on under-representation of secondary attributes and the standard diagnostics for it.
3. Whether **explicit conditioning** (colleagues | at-work, employment, occupation) is the usual structural
   fix and what is lost without it.

## Part B — Empirical benchmark (low / central / high + citation)

1. **Workplace co-presence rate** — share of work time / of workers recorded **in the company of
   colleagues / co-workers** in time-use "with whom" data (StatCan GSS-TU, ATUS who-file, HETUS). Use this
   to judge whether **14.88%** (full population) / **≈21%** (per worker) is a plausible target and where a
   good synthetic value should sit. Give **low / central / high**.
2. How co-presence at work varies by **occupation / sector / telework** — relevant because our pipeline
   keys an office archetype on occupation (NOCS) and carries a telework flag.
3. A note on whether a **±3 pp** marginal tolerance is a standard acceptance bar for a secondary
   co-presence channel, or stricter than the literature uses.

## Part C — Solution methods to correct co-presence thinness (the core deliverable)

Enumerate and **assess each candidate** (mechanism + evidence + preserves-marginals + **lives in Step-5
linkage vs needs Step-4 re-training** + risk), and **rank** by feasibility for a **locked generator where
the gap is measured at linkage**:

- **Donor-based imputation / stratified donor draw in the linkage** so employed agents draw co-presence
  from colleague-bearing donors (Step-5-compatible — highest priority to evaluate).
- **Post-hoc raking / calibration of the colleagues marginal** to the observed target (marginal-preserving).
- **Copula coupling** of the colleagues channel to the work (`wrk30`) channel as a post-process.
- **Conditional resampling** of co-presence given (activity, location/at-work, employment, occupation).
- **Joint activity + co-presence modelling** at generation time (flag: requires re-training the frozen
   Step-4 model).
- Explicitly warn which approaches risk **gaming a full-vs-observed validation** (e.g. biasing only toward
   observed donors) and how to avoid it.

## Output format

- A **methodology note** (Part 0): how "with whom" is recorded; marginal vs joint; biggest error source.
- A **mechanism brief** (Part A): ranked under-generation failure modes with citations.
- A **benchmark table** (Part B): workplace colleague co-presence rate (low / central / high + source),
  variation by occupation/sector/telework, and a tolerance norm — with a verdict on 14.88% / 10.51% / ±3 pp.
- A **solutions table** (Part C): methods × (mechanism, evidence, preserves-marginals, Step-5-vs-retrain,
  risk, rank), naming the **single most defensible Step-5-stage fix**.
- **Worked / cited examples:** 2–4 studies where a synthetic secondary/co-presence channel was diagnosed
  thin and corrected, with before/after.
- Full **reference list** with dates and URLs.

## Hard requirements

- Anchor every value to a **named, dated source** (prefer StatCan GSS-TU / ATUS who-file / HETUS /
  peer-reviewed); flag analyst estimates.
- Prioritise **Canadian** time-use evidence for the benchmark; international for method, flagged.
- Be explicit about **basis** (share of work time vs share of workers vs share of all slots; primary vs
  all-present companion) — this is the most common silent factor error here.
- For every solution, state whether it **preserves marginals** and whether it lives in **Step-5 linkage**
  or needs **Step-4 re-training** — these decide feasibility for our locked pipeline.
- Adversarially check the headline co-presence benchmark against **≥2 independent sources**; report
  disagreement rather than averaging silently.
