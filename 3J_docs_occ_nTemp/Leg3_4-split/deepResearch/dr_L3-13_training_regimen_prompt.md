# Deep-Research Prompt dr_L3-13 — STEP-4 TRAINING REGIMEN PLAYBOOK: loss balancing, conditioning, sampling, selection for the 3-head model

> SCOPE GUARD — READ FIRST. This is the **training-regimen** task of the Step-4 ML trio (`dr_L3-11`
> architecture, `dr_L3-12` representation, `dr_L3-13` regimen). It takes as GIVEN: the multi-head
> Transformer backbone (unless `dr_L3-11` overturns it) and the resolved `dr_L3-08` extension recipe
> (head-only warmup 5 epochs → joint fine-tune 15 epochs with PCGrad; BCE with pos_weight = 49 +
> post-hoc logit correction −ln 49 for calibration; regression gates ΔJS ≤ 0.002 bits on old heads;
> rare-state gates PR-AUC ≥ 0.15, F1 ≥ 0.25). Your job is everything AROUND that recipe: the loss
> balancer, the conditioning encoding, the data sampling, regularization, decoding, and model
> selection. Do NOT re-answer head-addition strategy or imbalance handling (`dr_L3-08`, resolved), the
> backbone (`dr_L3-11`), or the representation (`dr_L3-12`). See `00_deep_research_prompts_Leg3.md`
> for shared facts and conventions.

---

## What this document is

A regimen brief for the full 3-head joint training. Known setup: shared 6-layer encoder (d_model 384,
~29M params), AR activity decoder + parallel binary heads; ~64k diaries across 4 survey cycles
(2005/2010/2015/2022), stratified by cycle × day-type (3 strata: weekday/Saturday/Sunday) with
inverse-frequency stratum weighting already in use; conditioning vector = [demographics, DDAY_STRATA,
CYCLE_YEAR, COLLECT_MODE, NOCS, COW, HRSWRK]; planned per-head loss weights α = 1.0 : 0.5 : 0.3 with
SLAW/homoscedastic-UW weighting and PCGrad carried from Leg 2; a diversity-preserving loss guards a
documented peak-collapse failure mode; downstream, the model is progressively fine-tuned per cycle
(W_2005 → W_2010_ft → W_2015_ft → W_2022_ft), so the regimen must also not break **fine-tunability**.
Known inference-side pathologies from Leg 2 to design against: slot-level flicker (unrealistically
short run-lengths, needed a run-length diagnostic), rake-induced floating states, and the general
lesson that models must be selected open-loop on the Pareto frontier of validation gates — never on
training loss or a single composite.

## Role

Machine-learning practitioner-researcher (multi-task learning + small-data sequence generation).
Ground answers in: the loss-balancing literature (SLAW, homoscedastic uncertainty weighting, GradNorm,
DWA, CAGrad, IMTL, and the "unitary scalarization is enough" counter-evidence) specifically at LOW
task counts (2–4 tasks); gradient-surgery interaction studies (PCGrad combined with dynamic
balancers); conditioning-encoding practice for heterogeneous covariates (embeddings vs FiLM vs
concatenation; encoding an ordinal survey-cycle variable that must support progressive fine-tuning);
survey-data training practice (weighted sampling vs weighted loss for design weights and strata);
regularization and calibration at the ~30M-param / ~64k-sequence regime; and decoding/selection
practice for AR sequence generators (scheduled sampling, temperature, constrained decoding for
run-length realism; multi-objective early stopping). Note evidence scale throughout.

## Why this matters (so you scope correctly)

Leg 2 proved the machinery but tuned it by trial: the balancer, the conditioning encoding, and the
sampling scheme were chosen once and never pressure-tested, and several weeks were lost to failure
modes (peak collapse, flicker, rake-floating) that the literature documents countermeasures for. Leg 3
re-trains everything with a third head and then hands the checkpoint to a 4-stage progressive
fine-tuning chain — a regimen mistake propagates into 26 simulated years. The deliverable is the
regimen we would have wanted written down before Leg 2: what to fix, what to ablate, and in which
order, with citations.

---

## REQUIRED OUTPUT TABLES — fill every cell

### Table 1 — Loss balancers at low task count (2–4 heads)

| Balancer | Evidence at 2–4 tasks (does it beat fixed weights?) | Behaviour when one task is rare/noisy (our retail head) | Interaction with PCGrad (complementary / redundant / harmful) | Citation |
|---|---|---|---|---|
| Fixed weights (α = 1.0 : 0.5 : 0.3, incumbent plan) |  |  |  |  |
| SLAW |  |  |  |  |
| Homoscedastic uncertainty weighting |  |  |  |  |
| GradNorm |  |  |  |  |
| DWA |  |  |  |  |
| CAGrad / IMTL-style |  |  |  |  |
| Unitary scalarization (well-tuned fixed weights, per the counter-literature) |  |  |  |  |

### Table 2 — Conditioning encoding

| Covariate type | Options (embedding / one-hot concat / FiLM / cross-attention) | Best practice + evidence | Special constraint here | Citation |
|---|---|---|---|---|
| Categorical demographics (AGEGRP, SEX, NOCS, COW, …) |  |  |  |  |
| Ordinal-with-meaning CYCLE_YEAR |  |  | must support progressive fine-tuning to unseen 2030 |  |
| Day-type stratum (3-way, drives the whole diurnal shape) |  |  |  |  |
| Mixed-mode flag COLLECT_MODE (confound control, not signal) |  |  |  |  |

### Table 3 — Survey-data sampling and weighting

| Question | Field practice + evidence | Citation |
|---|---|---|
| Design weights (WGHT_PER/WGHT_EPI): weighted loss vs weighted sampling vs post-hoc raking only |  |  |
| Stratum balance: inverse-frequency weighting (incumbent) vs stratified batch composition |  |  |
| Cycle balance during joint pre-training (2022 has fewest diaries) vs leaving it to progressive fine-tuning |  |  |
| Retail-active diary exposure: any resampling despite dr_L3-08's pos_weight already handling rarity (double-correction risk) |  |  |

### Table 4 — Regularization and calibration at ~30M params / ~64k sequences

| Technique | Evidence at this scale | Effect on probability calibration (ruling criterion) | Citation |
|---|---|---|---|
| Dropout level / placement |  |  |  |
| Weight decay |  |  |  |
| Label smoothing (known calibration distortion — quantify) |  |  |  |
| Data augmentation for diaries (slot jitter, cyclic shifts) — legitimate or signal-corrupting? |  |  |  |
| Early stopping criterion (which metric, which patience) |  |  |  |

### Table 5 — Decoding and model selection

| Question | Field practice + evidence | Citation |
|---|---|---|
| AR decoding for realistic run-lengths (temperature / nucleus / constrained decoding / min-duration enforcement) — our flicker countermeasure |  |  |
| Scheduled sampling / exposure-bias mitigation worth it at 48-slot length? |  |  |
| Operationalizing Pareto-frontier selection across ~6 gate metrics (hypervolume, lexicographic, gate-first filtering) |  |  |
| Seed variance: how many seeds to report for a ~30M model on 64k sequences, and what variance is normal |  |  |

---

## Part C — Synthesis (the regimen spec)

Give: (1) a **concrete ordered regimen** — balancer choice (keep SLAW/UW+PCGrad, or change, with the
deciding citation), conditioning encodings per covariate, sampling scheme, regularization settings,
decoding scheme, selection rule — as a checklist the builder can implement top-to-bottom; (2) the
**fix-vs-ablate split**: which choices the evidence settles (fix them, cite them) vs which genuinely
need a small in-house ablation (name the ablation, its metric, and its budget in training runs — keep
it ≤ 4 runs total; the shared-vs-separate-backbone ablation already on our books may be folded in);
(3) explicit confirmation that the recommended regimen preserves **progressive fine-tunability** and
does not fight the dr_L3-08 recipe; (4) the top three regimen mistakes the literature documents for
exactly this setting, phrased as "do not do X because Y (cite)".

## Output format (follow exactly)

1. **Lead with Tables 1–5 fully populated.**
2. Then Part C regimen spec.
3. Inline citations; note task count and scale for every balancer claim.
4. **"Confidence and caveats":** which recommendation rests on the least transferable evidence.
5. **Reference list** — full citations, dates, URLs/DOIs.

## Hard requirements

- **Low-task-count evidence only for Table 1** — balancer results from 10+-task benchmarks do not
  transfer and must not decide the verdict.
- **Calibration is the ruling criterion** wherever a technique touches output probabilities.
- **The ablation budget is hard-capped at 4 runs** — a recommendation demanding a sweep does not close
  this prompt.
- **No fabricated precision;** flag GAPs. **Stay on topic** — regimen only; backbone (`dr_L3-11`),
  representation (`dr_L3-12`), head-addition recipe (`dr_L3-08`, resolved) are out of scope.
