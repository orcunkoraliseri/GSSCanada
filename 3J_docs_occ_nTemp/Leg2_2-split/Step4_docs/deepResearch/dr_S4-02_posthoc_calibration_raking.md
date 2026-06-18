# Deep-Research Prompt — S4-02: Post-Hoc Calibration / Raking of Generative Outputs

**Why this prompt.** The single largest performance lever in our pipeline is **not** the model — it is
the **post-hoc calibration** applied after generation. In Leg-1 (residential), per-(stratum × slot)
raking took the validator from **17 hard FAILs → 0** ("Calibrated J3"). In Leg-2 we apply a **joint
per-stratum rake** (`04L`) that reassigns the binary AT_HOME / AT_WORK labels to hit the observed
marginals while preserving home/work mutual exclusivity, and **carries the activity-category channel
(`act30`) and co-presence forward unchanged**. Because this is the load-bearing step, we need to know
where it sits in the literature (it is essentially iterative proportional fitting / raking from the
survey & population-synthesis world), whether carrying un-raked channels forward is principled, and
what it risks breaking (transition structure, joint dependence).

**Tool.** Run in Gemini Deep Research inside Antigravity (it has direct access to this project's files).

---

## Paste-ready prompt

```
You are a statistical-calibration and synthetic-data methods researcher with direct filesystem access
to this project. Your job has THREE parts: (1) read our actual calibration code, (2) survey the
external literature, (3) write a report file back into this project.

PART 1 — Read our implementation first (do not skip):
  - 3J_docs_occ_nTemp/Leg2_2-split/Step4_docs/3rdJ_04L_joint_rake_2split.py
        (the joint AT_HOME + AT_WORK post-hoc rake: it loads the trained checkpoint, runs
         generate(return_hw_probs=True) to get per-slot home/work probabilities, then greedily
         assigns binary labels per (cycle_year × day-type-stratum × slot) to match observed
         marginals under mutual exclusivity; activity `act30` and co-presence columns are copied
         forward UNCHANGED).
  - 3J_docs_occ_nTemp/Leg2_2-split/Step4_docs/3rdJ_04_augmentationGSS_2split_val.py
        (the gates the rake is judged on: binary-marginal gates G2/OW1 go to ~0 by construction;
         the rake-untouched axes — OW5 ordering, act30 work-category G4, and the S8 distributional
         metrics EMD/KS/MAE/ACF — are what actually discriminate models).
  - 3J_docs_occ_nTemp/Leg2_2-split/Step4_docs/3rdJ_04_augmentationGSS.md
        (progress log: the "rake equalizes binaries" framing and why acceptance is on the RAKED
         scorecard).

OUR AIM (restate at the top of the report): produce synthetic occupancy diaries whose population
marginals match the observed survey EXACTLY where it matters for building-energy loads, without
destroying the within-sequence temporal realism the generative model learned. The rake is our
mechanism for the first half; we need it to not damage the second half.

PART 2 — Literature review (inline citations + a final reference list required). Cover:
1. Raking / iterative proportional fitting (IPF) and its relatives (IPU, GREG calibration, entropy
   balancing, post-stratification) — origins in survey statistics and SPATIAL MICROSIMULATION /
   POPULATION SYNTHESIS. How are these used to force synthetic populations to match known marginals?
2. POST-HOC calibration of GENERATIVE-MODEL outputs specifically: distribution matching, optimal-
   transport / Sinkhorn post-processing, moment matching, probability calibration (Platt / isotonic),
   rejection / importance reweighting, and constrained decoding. Which operate on samples vs on the
   model itself?
3. The KEY RISK in our approach: editing some channels (binary presence) to match marginals while
   leaving others (activity category, co-presence) and the TEMPORAL TRANSITION structure untouched.
   What does the literature say about post-hoc marginal correction BREAKING joint / conditional /
   transition structure ("fixing marginals while breaking dependence")? How is this detected and
   mitigated?
4. Whether carrying an un-calibrated channel forward unchanged (our `act30`) is defensible, or whether
   joint / simultaneous calibration of correlated channels is required. Precedents either way.
5. How calibration quality is reported and defended in synthetic-population and generative-occupancy
   papers (which marginals, what residual error is acceptable, how joint structure is shown to survive).

PART 3 — Connect to OUR design explicitly. In a dedicated section:
  - Name precisely where our joint per-stratum rake sits in the IPF / calibration taxonomy and cite
    the closest precedents (survey calibration AND generative-output calibration).
  - Assess whether our greedy per-(stratum × slot) binary assignment under mutual exclusivity is a
    sound special case of a known method or an ad-hoc variant; suggest a more principled equivalent if
    one exists (e.g. optimal transport to the target marginal).
  - Give a concrete, cheap TEST we can run to prove the rake did NOT damage transition statistics or
    the home/work joint structure (so we can defend it to reviewers).
  - State whether leaving act30 un-raked is publishable as-is or needs a caveat / joint treatment.

OUTPUT: write a single Markdown report and SAVE it to
  3J_docs_occ_nTemp/Leg2_2-split/Step4_docs/deepResearch/dr_S4-02_posthoc_calibration_raking_REPORT.md
Structure: (a) restated aim, (b) taxonomy table (method × what it matches × operates-on-samples-or-
model × preserves-joint? × key refs), (c) the "connect to our 04L rake" section, (d) the
damage-detection test recipe, (e) full reference list.
```

---

*After the report lands:* use the taxonomy to give `04L` a proper named lineage in the paper, add the
recommended "transitions survived raking" check to the validator, and decide whether `act30` needs
joint calibration or a documented caveat.
