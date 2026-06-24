# Deep-Research Prompt 4 — Marginal Calibration vs Joint/Temporal Structure in Synthetic Time-Use Data (cross-cutting methodology)

> Paste everything below this line into a fresh deep-research session (Gemini / Claude / GPT deep research).

---

## Role

You are a methodologist in **synthetic population / microdata calibration** (iterative proportional fitting,
raking, reweighting, combinatorial optimisation), **copula and deep generative methods**, and
**occupant-behaviour modelling for building energy simulation**. Produce a rigorously sourced,
**cross-cutting methodology brief** that underpins three downstream parameter problems (work-peak under-fill,
night occupancy/sleep dominance, co-presence thinness). It must:

1. **formalise why marginal calibration (IPF / raking) preserves marginals exactly but cannot correct
   joint / temporal / cross-channel structure**, and name the standard results;
2. **catalogue and compare methods that *do* control joint / multi-way structure while still respecting the
   1-D marginals** the pipeline must keep exact;
3. give a **principled framework for choosing the minimal set of joint "control margins"** that would
   simultaneously improve all three failing metrics;
4. specify **diagnostics for joint fidelity** (not just marginal fit); and
5. map every method onto a **feasibility ladder** for our pipeline (pure post-hoc / re-rake without
   re-training / full re-train).

Every methodological claim and any benchmark must cite a **named, dated source** (peer-reviewed
synthetic-population, microsimulation, survey-calibration, copula, or generative-model literature; IEA EBC
annexes; StatCan methodology where relevant). No assertions without a citation; flag analyst opinion.

## Context (why this prompt exists)

We build **synthetic 48×30-min time-use diaries** from the Canadian **GSS-Time Use + Census** for
**EnergyPlus**. Step 4 = a **frozen diffusion generator** → a **"joint rake"** (IPF/raking that forces the
synthetic marginals to match observed **exactly**) → a min-dwell smoother. **Step 4 is locked.** Step 5 =
demographic **census linkage**, validated against the **observed (real-diary) subset**.

Three validation failures share **one root mechanism**: the rake matches 1-D marginals exactly, but each
failing metric is a **joint / temporal / cross-channel property the rake never constrained**:

| Failing metric (see prompts 01–03) | The marginal that IS matched | The joint structure that is NOT |
|---|---|---|
| Work-peak under-fill (G4) | per-slot and per-activity activity marginals | **time × activity** mass in the midday work window |
| Night occupancy / sleep dominance | per-slot occupancy / activity marginals | **time × (at-home, sleep)** concentration overnight |
| Colleagues co-presence thinness (W3) | the colleagues marginal (per channel) | **activity/location × companion** coupling (colleague ∧ at-work) |

We want the literature to tell us, generally and with evidence, **how to fix joint structure of this kind
without giving up the exact 1-D marginals** — and which fixes are post-hoc vs require touching the generator.

## Part 0 — Formal basis

Provide, with sources:

1. State precisely why **IPF / raking** converges to the **maximum-entropy / minimum-discrimination
   distribution consistent with the supplied margins**, and therefore **leaves all higher-order
   association not encoded in the control set at its seed (pre-rake) value**. Name the result (Deming–Stephan;
   maximum-entropy interpretation; I-projection) and its practical corollary: *raking cannot create
   association the seed lacks.*
2. Make explicit the distinction between **calibrating weights** (reweighting fixed records) vs
   **editing records** (changing the diaries) vs **generating** records, and what each can and cannot move.
3. Identify the **single biggest conceptual error** practitioners make here (assuming exact marginals imply
   a faithful joint distribution).

## Part A — Methods that control joint structure while preserving marginals (compare with evidence)

Catalogue and compare; for each: mechanism, what association it can fix, whether it **keeps the 1-D
marginals exact**, data/compute cost, convergence/zero-cell risks, and published evidence of use in
microsimulation or time-use/occupancy synthesis:

- **Raking to multi-way control tables** (add 2-way / 3-way margins, e.g. time×activity) — IPF on a
  higher-dimensional target.
- **Iterative Proportional Updating (IPU)** and **combinatorial optimisation / simulated annealing** for
  joint household–person consistency.
- **Entropy balancing / calibration weighting (GREG)** with interaction moments.
- **Copula-based coupling** (impose a dependence structure between channels post-hoc).
- **Optimal-transport reweighting / record editing** toward a 2-D target subject to 1-D constraints.
- **Conditional / joint generative modelling** (the structure is learned, not raked) — flag as
  generator-side.
- **Gibbs / conditional resampling** and **rejection / guided sampling** as post-processes.

## Part B — Control-set design (which joint margins to add)

1. Give a **principled procedure** for selecting the **minimal set of interaction margins** to add to a
   rake so that it repairs a target joint metric without over-constraining (bias–variance, zero-cell
   proliferation, non-convergence). Reference practice in synthetic-population calibration.
2. Apply it to our three metrics: which **specific 2-way (or temporal) margins** (e.g. time×activity in the
   work window; time×at-home and time×sleep overnight; at-work×colleague) would most efficiently move all
   three — and whether one shared control set can serve all three or they conflict.
3. State how adding such margins interacts with **record editing vs reweighting** (does our "edit the
   diaries" rake admit joint margins, or must they enter as a reweight?).

## Part C — Diagnostics & feasibility ladder

1. **Joint-fidelity diagnostics:** the metrics the literature uses to score *association* preservation in
   synthetic microdata (e.g. SRMSE on multi-way tables, total-variation / Cramér's V preservation,
   pairwise-correlation difference, propensity/discriminator scores, SDV/synthcity multivariate metrics) —
   so we can measure joint structure, not just marginal fit.
2. **Feasibility ladder** for our locked pipeline — classify each Part-A method into:
   **(i) pure post-hoc / Step-5 linkage** (no Step-4 touch);
   **(ii) re-run the rake with an expanded control set** (modifies the calibration stage, **no neural
   re-training**);
   **(iii) re-train the generator** (full Step-4 re-open).
   Recommend the **lowest rung** that can credibly fix each metric, with the trade-off.

## Output format

- A **theory note** (Part 0): the max-entropy/I-projection argument, the reweight-vs-edit-vs-generate
  distinction, the key fallacy — each cited.
- A **methods comparison table** (Part A): rows = methods; columns = association fixed,
  preserves-marginals (Y/N), cost, convergence/zero-cell risk, evidence, suitability.
- A **control-set recommendation** (Part B): the minimal interaction margins for each of the three metrics
  and whether a shared set works.
- A **diagnostics list + feasibility ladder** (Part C): the joint-fidelity metrics to adopt, and each
  candidate fix tagged (i)/(ii)/(iii) with the recommended lowest viable rung per metric.
- **Worked / cited examples:** 2–4 microsimulation or synthetic-population studies that added joint margins
  (or used copula/OT/conditional generation) to repair association while keeping marginals — with the
  measured improvement.
- Full **reference list** with dates and URLs.

## Hard requirements

- Anchor every methodological claim and benchmark to a **named, dated source** (prefer peer-reviewed
  synthetic-population / microsimulation / survey-calibration / generative-model literature); flag opinion.
- Be explicit, for every method, about **(a) whether it keeps the 1-D marginals exact** and **(b) where it
  sits on the feasibility ladder (post-hoc / re-rake / re-train)** — these decide what we can actually use.
- Keep **units / basis** explicit when citing any benchmark (per-slot vs daily; reweight vs edit).
- Prefer methods demonstrated on **time-use, activity-travel, or occupancy** data; use general
  synthetic-data sources for theory, flagged as such.
- Adversarially check headline methodological claims (especially "this preserves marginals") against
  **≥2 independent sources**; report disagreement rather than asserting.
