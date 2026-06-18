# Deep-Research Prompt — S4-03: Architecture Choice for Conditional Multi-Channel Occupancy Generation

**Why this prompt.** Our generator is a **shared-encoder, multi-head, autoregressive (AR) conditional
Transformer**: an encoder ingests an observed diary + demographics + survey-cycle + day-type; an AR
decoder emits 48 half-hour slots; separate heads predict the 14-category **activity**, the binary
**AT_HOME** and **AT_WORK** presence channels, and co-presence. Training uses uncertainty / SLAW loss
weighting, PCGrad gradient surgery, and a diversity loss. The standing **open decision #1** from our
research synthesis is whether a **discrete/masked diffusion** model (MDLM / SEDD / D3PM) would be a
better backbone — and more broadly whether the shared-backbone multi-head design is the right way to
keep the channels mutually consistent. We want a literature-grounded justification (or refutation) of
the current architecture, written specifically against **our aim and data scale**.

**Tool.** Run in Gemini Deep Research inside Antigravity (it has direct access to this project's files).

---

## Paste-ready prompt

```
You are a generative-sequence-modelling researcher with direct filesystem access to this project.
Your job has THREE parts: (1) read our actual architecture, (2) survey the external literature,
(3) write a report file back into this project.

PART 1 — Read our implementation first (do not skip):
  - 3J_docs_occ_nTemp/Leg2_2-split/Step4_docs/3rdJ_04B_model_2split.py
        (shared encoder + cross-attention AR decoder; the multiple output heads: activity (14-cat
         softmax), AT_HOME (binary), AT_WORK (binary), co-presence; conditioning tokens from
         demographics / cycle / day-type-strata, plus the optional per-person latent token).
  - 3J_docs_occ_nTemp/Leg2_2-split/Step4_docs/3rdJ_04D_train_2split.py
        (multi-task loss machinery: UncertaintyWeighting / SLAW, PCGrad, diversity loss, component
         losses per head).
  - 3J_docs_occ_nTemp/Leg2_2-split/Step4_docs/3rdJ_04E_inference_2split.py
        (AR generation with temperature sampling + binary decision thresholds).
  - 3J_docs_occ_nTemp/Leg2_2-split/Step4_docs/3rdJ_04_augmentationGSS.md
        (design history: J3 topology lessons, the COP / peak-collapse failure mode, why diversity loss
         matters, the capacity vs wiring findings).

OUR AIM and DATA (restate at the top of the report): from ~64,000 respondents (each one observed
single-day diary) generate, per respondent, the other two day-type diaries — sequences of 48 half-hour
slots carrying a 14-class activity token + binary AT_HOME + binary AT_WORK (+ co-presence) — conditioned
on demographics, survey-cycle year, and target day-type. Outputs must preserve realistic temporal
transition statistics AND population marginals, support multiple correlated channels on ONE backbone,
and later extend from 2 channels to 4 (retail + hotel). Training set ~192k sequences (3 day-types).

PART 2 — Literature review (inline citations + a final reference list required). Cover:
1. Model families for CONDITIONAL generation of multivariate CATEGORICAL + BINARY sequences:
   autoregressive Transformers, discrete / masked diffusion (MDLM, SEDD, D3PM, absorbing-state
   diffusion), conditional VAEs, sequence GANs (TimeGAN etc.), and (semi-)Markov / activity-based
   models. For each: how it conditions on rich covariates, handles long-range temporal dependence,
   rare states, and hard marginal/aggregate constraints.
2. AUTOREGRESSIVE vs DISCRETE-DIFFUSION head-to-head for short discrete sequences (length ~48) at our
   data scale: sample quality, mode coverage / diversity, exposure bias (AR) vs iterative-refinement
   cost (diffusion), controllability, and which better preserves transition matrices and marginals.
3. MULTI-TASK / MULTI-HEAD shared-backbone design for several CORRELATED output channels: when does a
   shared encoder help vs hurt (negative transfer, one head dominating)? Recommended loss-weighting
   (uncertainty weighting, SLAW, GradNorm) and gradient-surgery (PCGrad) practices and their evidence.
   Compare to SEPARATE per-channel models.
4. Evidence from OCCUPANCY / TIME-USE / human-mobility generation specifically: which architectures
   are actually used to synthesize activity diaries or occupancy schedules, and what they report.
5. The known AR failure mode we hit (a co-presence / peak "collapse" where the AR arm degenerates) and
   how the literature prevents it (diversity objectives, scheduled sampling, temperature, etc.).

PART 3 — Connect to OUR design explicitly. In a dedicated section:
  - Is a shared-encoder multi-head AR Transformer a defensible, current choice for this task and scale,
    or does the evidence favour discrete diffusion (MDLM) — and under what conditions would the verdict
    flip? Be specific and cite head-to-head results, not vibes.
  - Assess our specific machinery (UW/SLAW + PCGrad + diversity loss) against best practice; keep,
    drop, or add.
  - Give a concrete recommendation: keep the AR Transformer, or run a bounded MDLM ablation — with the
    minimal experiment that would settle open-decision #1, sized for our data.
  - Note any architecture implication for the upcoming 2->4 channel extension (retail + hotel).

OUTPUT: write a single Markdown report and SAVE it to
  3J_docs_occ_nTemp/Leg2_2-split/Step4_docs/deepResearch/dr_S4-03_architecture_choice_REPORT.md
Structure: (a) restated aim + data, (b) ranked model-family table (family × conditioning × constraint
handling × diversity × compute × occupancy-precedent × key refs), (c) AR-vs-diffusion verdict for our
case, (d) the "connect to our design" section with a keep/drop/add list and the minimal MDLM ablation,
(e) full reference list.
```

---

*After the report lands:* use the AR-vs-diffusion verdict to either close open-decision #1 in favour of
the current Transformer (with citations) or scope a bounded MDLM ablation; fold the keep/drop/add list
into the next training iteration and the paper's methods justification.
