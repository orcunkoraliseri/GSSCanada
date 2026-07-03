# Deep-Research Prompt dr_L3-11 — STEP-4 ARCHITECTURE PRESSURE-TEST: is the multi-head Transformer still the right backbone at 3 GSS heads? (2023–2026 evidence)

> SCOPE GUARD — READ FIRST. This is the **architecture** task of the Step-4 ML trio (`dr_L3-11`
> architecture, `dr_L3-12` output representation, `dr_L3-13` training regimen). The incumbent won a
> real bake-off in Leg 2: a hybrid conditional Transformer ("J3": shared 6-layer encoder, d_model 384,
> autoregressive activity decoder + parallel non-autoregressive binary heads, ~29M params) beat an
> MDLM/SEDD discrete-diffusion branch that had the best composite score but **failed 2 of 4 hard
> validation gates** and cost 32–64 forward passes per respondent at inference (decision closed
> 2026-06-18). Your job is NOT to re-run a generic survey (the foundational Prompt-3 report covers
> model families) — it is to pressure-test the incumbent **for the 3-head Leg-3 task with 2023–2026
> evidence**, and end with a keep / augment / replace verdict. Do NOT cover head-output representation
> (`dr_L3-12`) or the training recipe (`dr_L3-08`, resolved, and `dr_L3-13`). See
> `00_deep_research_prompts_Leg3.md` for shared facts and conventions.

---

## What this document is

An incumbent-vs-field check before committing Leg 3's training budget. The task: conditional
generation of 48-slot half-hour diaries — a 14-category activity token plus binary presence channels
(AT_HOME, AT_WORK, and now AT_RETAIL at ~2 % positive) plus 9 co-presence channels — conditioned on
demographics, day-type stratum, and survey-cycle year; ~64k real diaries across four cycles
(2005/2010/2015/2022); downstream use is population-level schedule fractions for building-energy
simulation, so **marginal calibration and transition realism outrank sample-level sharpness**. The
incumbent is validated, shipped, and wired into a progressive fine-tuning forecast stack — replacement
carries a re-validation cost measured in weeks. The bar for "replace" is therefore high and must be
evidence-based, not novelty-based.

## Role

Machine-learning methods researcher (generative sequence models). Ground claims in 2023–2026
literature: post-MDLM discrete diffusion developments (and whether its known calibration/gate problems
were since fixed), decoder-only autoregressive approaches to structured/tabular sequences, state-space
models (Mamba-family) for short categorical sequences, discrete flow matching, and — most importantly —
**applications to tasks like ours**: occupancy-schedule generation, human activity/mobility trajectory
synthesis, time-use-diary modelling, load-profile generation. Prefer evidence at our scale (10⁴–10⁵
training sequences, sequence length ~48, ~10⁷–10⁸ params); say explicitly when a cited result comes
from web-scale settings and may not transfer.

## Why this matters (so you scope correctly)

Three heads change the calculus that closed the Leg-2 decision: more heads mean more gradient
interference on the shared encoder, the new head is rare-positive (a regime where AR factorizations
and diffusion models behave differently), and the Leg-1 lesson says composite scores mislead — the
verdict must be argued against our **hard gates** (per-head JS < 0.02 per stratum, presence-rate RMS,
transition/dwell realism, and rare-state metrics from `dr_L3-08`: PR-AUC ≥ 0.15, F1 ≥ 0.25). A wrong
"keep" costs us a better model; a wrong "replace" costs weeks and risks the shipped AT_HOME/AT_WORK
quality. The asymmetry favours the incumbent — the report must quantify whether any challenger clears
it.

---

## REQUIRED OUTPUT TABLES — fill every cell

### Table 1 — Candidate backbones for this task, 2023–2026 state

| Architecture | Fit to categorical+binary 48-slot conditional generation | Data appetite vs our ~64k sequences | Inference cost per sample | Maturity / implementation risk on an existing validated codebase | Citation |
|---|---|---|---|---|---|
| Multi-head Transformer enc-dec, AR activity arm + parallel binary heads (**incumbent**) | (pre-filled: shipped, passes all Leg-2 gates) | (pre-filled: proven at this scale) | 1 AR pass | (pre-filled: zero — exists) | project-internal |
| Decoder-only AR Transformer (LLM-style, joint token stream) |  |  |  |  |  |
| Discrete diffusion, post-MDLM/SEDD generation (2024–2026 variants) |  |  |  |  |  |
| SSM / Mamba-family sequence models |  |  |  |  |  |
| Discrete flow matching |  |  |  |  |  |
| Hybrid (Transformer encoder + non-AR iterative decoder) |  |  |  |  |  |

### Table 2 — Task-match evidence (the decisive table)

Applications of these architectures to occupancy schedules, activity/mobility trajectories, time-use
diaries, or load profiles — the closer to our task, the more weight.

| Study | Task + data scale | Architecture | Reported marginal calibration / transition realism (not just likelihood) | Transferable to our setting? (YES/partial/NO + why) | Citation |
|---|---|---|---|---|---|
|  |  |  |  |  |  |
|  |  |  |  |  |  |
|  |  |  |  |  |  |
|  |  |  |  |  |  |

### Table 3 — Incumbent weaknesses at 3 heads: do challengers actually fix them?

| Known incumbent risk | Evidence it worsens at 3+ heads | Which challenger demonstrably fixes it | New failure mode the challenger introduces | Citation |
|---|---|---|---|---|
| Exposure bias in the AR activity arm |  |  |  |  |
| Peak collapse / over-smoothing in multi-head training |  |  |  |  |
| Gradient interference on the shared encoder |  |  |  |  |
| Rare-state (~2 %) channel fidelity |  |  |  |  |

### Table 4 — Targeted upgrades that keep the backbone (the "augment" menu)

Low-risk improvements grafted onto the incumbent rather than replacing it.

| Upgrade | Mechanics | Evidence of benefit on similar tasks | Risk to shipped heads | Citation |
|---|---|---|---|---|
| Improved decoding for the AR arm (scheduled sampling, constrained/beam decoding for flicker control) |  |  |  |  |
| Classifier-free-guidance-style conditioning strengthening |  |  |  |  |
| Encoder capacity/width bump vs depth bump (capacity was the Leg-2 bottleneck finding) |  |  |  |  |
| Auxiliary consistency losses across heads |  |  |  |  |
| (any other 2023–2026 upgrade the literature supports) |  |  |  |  |

### Table 5 — VERDICT MATRIX (the deliverable)

| Option | Expected gate performance (argued vs our hard gates) | Cost (implementation + re-validation) | Verdict (recommend / viable / reject) |
|---|---|---|---|
| Keep incumbent unchanged |  |  |  |
| Keep + targeted upgrades from Table 4 (name them) |  |  |  |
| Replace with the strongest challenger (name it) |  |  |  |

---

## Part C — Synthesis (the keep/augment/replace verdict)

Give: (1) a single verdict from Table 5 with its two strongest citations; (2) if "augment", the ranked
shortlist of Table-4 upgrades with an explicit do-first item; (3) the **evidence threshold for
replacement** stated as a falsifiable condition (e.g., "a challenger shown to beat an AR-hybrid on
marginal calibration AND transition realism at ≤10⁵ sequences on a mobility/occupancy task — as of
this search, found / not found"); (4) a one-paragraph answer to the reviewer question "why not an
LLM?" — sourced, not dismissive; (5) explicit confirmation or refutation that the Leg-2 MDLM rejection
still stands given 2024–2026 discrete-diffusion progress.

## Output format (follow exactly)

1. **Lead with Tables 1–5 fully populated.**
2. Then Part C synthesis.
3. Inline citations; flag every claim that comes from web-scale settings.
4. **"Confidence and caveats":** where the task-match evidence is thinnest.
5. **Reference list** — full citations, dates, URLs/DOIs.

## Hard requirements

- **Argue against OUR gates** (JS/stratum, presence-rate RMS, transitions, rare-state PR-AUC/F1) —
  likelihood or FID-style scores alone do not count.
- **Table 2 is decisive** — if no near-task evidence exists for a challenger, its verdict cannot be
  "recommend".
- **Respect the asymmetry** — the incumbent is validated and shipped; replacement must clear a
  materially higher bar than parity.
- **No fabricated precision;** flag GAPs. **Stay on topic** — backbone choice only; representation is
  `dr_L3-12`, regimen is `dr_L3-13`.
