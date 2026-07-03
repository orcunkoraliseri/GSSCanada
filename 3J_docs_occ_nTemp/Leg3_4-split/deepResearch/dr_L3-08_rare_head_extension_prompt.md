# Deep-Research Prompt dr_L3-08 — ADDING A RARE-POSITIVE HEAD to a trained multi-head sequence generator

> SCOPE GUARD — READ FIRST. This is the **ML-methods** task of the Leg-3 set. Its job is to source the
> training recipe for extending our trained two-head Conditional Transformer with a **third binary head
> whose positive rate is ~2 %** (AT_RETAIL), without degrading the existing heads. Do NOT re-survey
> generative model families (the foundational Prompt-3 report covers that; the architecture decision is
> closed — multi-head Transformer, MDLM rejected), and do NOT define the retail validation targets
> (that is `dr_L3-06`). See `00_deep_research_prompts_Leg3.md` for shared facts and conventions.

---

## What this document is

A training-recipe brief. The as-built Leg-2 generator: shared 6-layer Transformer encoder (d_model
384), autoregressive activity decoder + parallel non-autoregressive binary heads, trained on ~64k
diaries × 48 half-hour slots; Head 1 = activity (14-cat) + AT_HOME + 9 co-presence, Head 2 = AT_WORK
(~6–7 % positive slots), with SLAW/homoscedastic loss weighting, PCGrad gradient surgery, and a
diversity-preserving loss (countermeasures to a documented peak-collapse failure). Planned loss weights
for Leg 3: **α_resid : α_work : α_retail = 1.0 : 0.5 : 0.3**, target per-head JS divergence < 0.02 per
stratum. The new head's target, AT_RETAIL, is **rare**: ~2 % of slots positive, concentrated in a
midday band. The question set: how to add such a head safely.

## Role

Machine-learning methods researcher (multi-task sequence modelling). Ground answers in the multi-task
learning literature (loss balancing, gradient surgery, negative transfer, catastrophic forgetting /
continual learning), the class-imbalance literature for sequence labelling / binary sequence outputs
(pos_weight, focal loss, resampling), and any generative-time-series or occupancy-modelling papers that
added output channels to trained models. Prefer evidence at our scale (~10⁴–10⁵ training sequences,
~30M parameters) over web-scale results, and say when scale limits transfer of a finding.

## Why this matters (so you scope correctly)

Two expensive failure modes are on the table. First, the **rare-head failure**: with 2 % positives, a
BCE head can reach 98 % accuracy predicting all-zeros — and JS on near-degenerate marginals may not
catch a head that never fires; if that is the case our < 0.02 JS gate is toothless for this head and we
need to know the right metric before training, not after. Second, the **regression failure**: adding
Head 3 changes the encoder's gradients; if the shared representation drifts, the shipped AT_HOME /
AT_WORK quality (already validated and published-adjacent) silently degrades. Retraining from scratch
vs fine-tuning with a frozen-then-unfrozen encoder is a real fork with days of cluster time behind it.

---

## REQUIRED OUTPUT TABLES — fill every cell

### Table 1 — Strategies for adding a head to a trained multi-head model

| Strategy | Mechanics | Risk to existing heads | Evidence (task, scale) | Citation |
|---|---|---|---|---|
| Full retrain from scratch, 3 heads |  |  |  |  |
| Head-only warmup (freeze encoder), then joint fine-tune |  |  |  |  |
| Joint fine-tune from Leg-2 checkpoint, no freeze |  |  |  |  |
| Adapter / LoRA-style head addition |  |  |  |  |
| Elastic-weight-consolidation-style protection of old heads |  |  |  |  |

### Table 2 — Class-imbalance remedies for a ~2 %-positive binary sequence channel

| Remedy | Mechanics | Known effect on calibration of the positive rate (critical: we need unbiased population fractions, not just detection) | Citation |
|---|---|---|---|
| BCE with pos_weight |  |  |  |
| Focal loss |  |  |  |
| Over/under-sampling of retail-active diaries |  |  |  |
| Threshold/temperature calibration post-hoc |  |  |  |
| None (plain BCE; rarity handled by loss weight α) |  |  |  |

### Table 3 — Loss weighting for the third head

| Question | Literature answer | Citation |
|---|---|---|
| Is a fixed α ratio (1.0 : 0.5 : 0.3) defensible vs letting SLAW/UW set it? |  |  |
| How do dynamic weighters behave when one task is much rarer than the others? |  |  |
| Does PCGrad remain appropriate at 3 heads (any evidence of degradation with head count)? |  |  |

### Table 4 — Protecting the shipped heads (regression gates)

| Question | Literature answer | Citation |
|---|---|---|
| Best-practice regression test when extending a model (metric deltas on frozen validation set) |  |  |
| Acceptable tolerance for old-head metric drift after extension (any precedent) |  |  |
| Evidence on whether joint fine-tuning *improves* old heads (positive transfer) vs degrades them, for correlated channels |  |  |

### Table 5 — Evaluation metrics for a rare binary channel (the gate question)

| Metric | Behaviour at 2 % positive rate (does an all-zeros head pass?) | Recommended for our gate set? | Citation |
|---|---|---|---|
| JS divergence per stratum (our current gate) |  |  |  |
| Presence-rate RMS error (pp) |  |  |  |
| PR-AUC / F1 on positive slots |  |  |  |
| Time-conditional rate error (rate within the 11:00–14:00 band) |  |  |  |
| Transition / dwell-time statistics on the rare state |  |  |  |

---

## Part C — Synthesis (the recipe)

Give: (1) the recommended extension strategy from Table 1 with an explicit training schedule sketch
(what freezes when, for roughly how many epochs relative to the Leg-2 budget); (2) the recommended
imbalance handling from Table 2 with its calibration caveat spelled out — we need the *population
fraction* at each slot to be unbiased, since it becomes a physical multiplier; (3) a verdict on the
planned α = 0.3 (keep / change / let the dynamic weighter decide); (4) the recommended gate set for
AT_RETAIL from Table 5, replacing or augmenting bare JS, including one metric that an all-zeros head
provably fails; (5) the regression-gate specification for the old heads (metrics + tolerance).

## Output format (follow exactly)

1. **Lead with Tables 1–5 fully populated.**
2. Then Part C recipe.
3. Inline citations; note the task/scale of each cited result.
4. **"Confidence and caveats":** which recommendation rests on the least transferable evidence.
5. **Reference list** — full citations, dates, URLs/DOIs.

## Hard requirements

- **Answer the calibration question head-on** — remedies that improve detection but bias the predicted
  positive *rate* are worse than nothing for us; every Table-2 row must address it.
- **At least one recommended gate must provably fail an all-zeros head.**
- **No fabricated precision;** flag GAPs. **Stay on topic** — training recipe and gates only; no
  architecture re-litigating.
