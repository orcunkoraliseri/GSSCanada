# Deep-Research Prompt — S4-01: Per-Person Coupling & Multi-Day Diary Consistency

**Why this prompt.** Our Step-4 generator produces, for each respondent, three day-type diaries
(weekday / Saturday / Sunday) by sampling each day-type **independently** from a shared demographic
conditioning. The population marginals come out right (the AT_WORK presence rate per day-type matches
observed — validator gate **OW1 ≈ 0 pp** after raking), but the **per-person ordering** —
weekday work-rate ≥ Saturday ≥ Sunday — only holds for **57.3 %** of respondents (validator gate
**OW5**, a FAIL on every base we have tried, R7/R8/R10). Post-hoc raking *cannot* fix OW5 because it
operates per-stratum and is blind to the cross-day link within a person. Our candidate fix (**R11**)
injects a **shared per-person latent** reused across that person's three day-types, plus an optional
**soft monotonic penalty**. We want the literature to validate, challenge, or improve this design.

**Tool.** Run in Gemini Deep Research inside Antigravity (it has direct access to this project's files).

---

## Paste-ready prompt

```
You are a machine-learning methods researcher with direct filesystem access to this project. Your
job has THREE parts: (1) read our actual code to understand the concrete problem, (2) survey the
external literature, (3) write a report file back into this project.

PART 1 — Read our implementation first (do not skip):
  - 3J_docs_occ_nTemp/Leg2_2-split/Step4_docs/3rdJ_04B_model_2split.py
        (shared-encoder multi-head Transformer; note the per-person latent `r11_latent` /
         `proj_r11_latent` 4th conditioning token, and `_arm1_decode_tf` / `_arm1_generate`).
  - 3J_docs_occ_nTemp/Leg2_2-split/Step4_docs/3rdJ_04D_train_2split.py
        (training; note `r11_monotonic_penalty()` and the per-epoch per-person latent resampling).
  - 3J_docs_occ_nTemp/Leg2_2-split/Step4_docs/3rdJ_04E_inference_2split.py
        (note: ONE latent per respondent is drawn and REUSED across that person's 3 day-types).
  - 3J_docs_occ_nTemp/Leg2_2-split/Step4_docs/3rdJ_04_augmentationGSS_2split_val.py
        (find the OW5 check: per-respondent weekday>=Sat>=Sun ordering of the AT_WORK rate).
  - 3J_docs_occ_nTemp/Leg2_2-split/Step4_docs/3rdJ_04_augmentationGSS.md
        (progress log: the OW5 diagnosis and the R11 rationale).

OUR AIM (state it back in your own words at the top of the report): generate synthetic multi-day
occupancy diaries (residential AT_HOME + office AT_WORK, per 30-min slot) that are faithful BOTH in
population marginals AND in per-person internal consistency across day-types, conditioned on
demographics / survey-cycle / day-type, to drive building-energy load models. OW5 is the
per-person-consistency axis of that aim.

PART 2 — Literature review (inline citations + a final reference list required). Cover:
1. Generating MULTIPLE correlated instances per entity that must stay mutually consistent: shared /
   hierarchical latent-variable models, person-level (subject) random effects, panel / longitudinal
   generative models, and "amortised" shared-latent conditional generation. How is one latent shared
   across several conditioned draws so the draws stay coherent?
2. Imposing ORDERING / monotonicity between related outputs in deep generative models: soft penalty
   terms (hinge / ReLU on rate differences) vs hard architectural constraints (monotonic networks,
   constrained decoding, isotonic post-processing). Evidence on which actually holds at inference.
3. The specific failure we observe — correct population marginals but broken per-instance ordering
   when instances are sampled independently. Is this a named phenomenon (e.g. "marginal-correct,
   joint-wrong")? How do copula models, structured latents, or joint decoding address it?
4. Time-use / activity-diary and occupancy-modelling papers that enforce within-person consistency
   across days or that model a person's week as a coupled object rather than independent days.
5. Cost/benefit and known failure modes of a shared per-person latent (posterior collapse, the latent
   being ignored, latent-vs-conditioning identifiability) and how to diagnose/prevent them.

PART 3 — Connect to OUR design explicitly. In a dedicated section:
  - Does the R11 shared-latent + soft-monotonic-penalty approach match best practice? Cite the
    closest precedents.
  - Name 2-4 concrete ALTERNATIVES or augmentations we could try (e.g. joint multi-day decoding,
    copula coupling, hard monotone head, hierarchical prior) with their trade-offs for ~64k
    respondents × 3 day-types.
  - Flag any risk that our latent will be ignored (collapse) and the cheapest diagnostic for it.

OUTPUT: write a single Markdown report and SAVE it to
  3J_docs_occ_nTemp/Leg2_2-split/Step4_docs/deepResearch/dr_S4-01_perPerson_coupling_REPORT.md
Structure: (a) restated aim + problem, (b) literature synthesis with a comparison table
(approach × consistency mechanism × inference-time guarantee × cost × key refs), (c) the
"connect to our R11 design" section, (d) a ranked recommendation, (e) full reference list.
```

---

*After the report lands:* mine the recommendation section to decide whether R11 stands as-is, gains a
hard-monotone variant, or is replaced by joint multi-day decoding. Cross-link findings into the R11
entry of `3rdJ_04_augmentationGSS.md`.
