# Deep-Research Prompt dr_L3-12 — STEP-4 OUTPUT REPRESENTATION: independent binary heads vs a joint mutually-exclusive location token

> SCOPE GUARD — READ FIRST. This is the **output-representation** task of the Step-4 ML trio
> (`dr_L3-11` architecture, `dr_L3-12` representation, `dr_L3-13` regimen). The question: should the
> three GSS presence channels stay **independent binary heads** (AT_HOME, AT_WORK, AT_RETAIL — the
> incumbent design, extended per the resolved `dr_L3-08` recipe), or be restructured as **one joint
> categorical "location" head** whose classes are mutually exclusive by construction? Do NOT
> re-litigate the backbone (`dr_L3-11`) and do NOT cover loss balancing / optimization (`dr_L3-13`).
> See `00_deep_research_prompts_Leg3.md` for shared facts and conventions.

---

## What this document is

A representation-choice brief. The ground truth behind all three presence channels is **one**
episode-level variable: the harmonized 18-category GSS location code `occPRE`, which is mutually
exclusive by construction (a person is in exactly one place per episode). Our channels are binary
projections of it: AT_HOME = (occPRE==1), AT_WORK = (occPRE==2), AT_RETAIL = (occPRE==5, plus a gated
activity arm). Independent binary heads discard the exclusivity: nothing in the incumbent prevents a
generated slot with AT_HOME = AT_WORK = 1, a physically impossible state that also corrupts the
population fractions BEM consumes. A joint categorical head (e.g., classes {home, work, retail,
other-out-of-home, travel}) restores exclusivity for free — but changes the loss geometry, the rare-
class handling (retail ~2 %), and the interface to the shipped composite Head 1 (which already emits
AT_HOME inside a validated multi-output head).

> **Known project facts to respect (pre-filled).** (a) Leg 2 deliberately did NOT enforce
> AT_HOME ⊕ AT_WORK exclusion — but that decision addressed the *both-zero* case (commute, errands,
> third places are legitimately neither), never the *both-one* case, which the data itself forbids.
> (b) The OR-rule's activity arm can create true AT_HOME ∧ AT_RETAIL overlaps (online shopping) unless
> gated — the gating is OPEN DECISION 1 and interacts with this choice. (c) The `dr_L3-08` recipe
> (pos_weight = 49 + logit correction, PR-AUC/F1 gates) was derived for a *binary* rare head; a
> categorical representation changes what "rare class handling" means. (d) Head 1 (activity + AT_HOME
> + 9 co-presence) is shipped and validated; any representation change must state its migration path.

## Role

Machine-learning methods researcher (structured prediction / multi-label vs multi-class modelling).
Ground answers in: multi-label vs multi-class literature for mutually exclusive targets; structured
output prediction over sequences (per-slot softmax vs per-channel sigmoids, CRF-style slot coupling);
constraint-enforcement mechanisms (architectural softmax, loss penalties, post-hoc projection) and
their calibration effects; and — most valuable — generative models of human location/activity
trajectories that faced exactly this choice (location as categorical state vs stacked binary
indicators). Note evidence scale and transferability throughout.

## Why this matters (so you scope correctly)

This decision is upstream of everything in Step 4: the head architecture, the `dr_L3-08` recipe's
applicability, the gate set, and the Step-7 population fractions. It is cheap to change now and
expensive after training. The failure modes are asymmetric: binary heads risk impossible states and
mutually inconsistent marginals (each head individually calibrated, their sum > 1 in peak slots);
a categorical head risks worse rare-class fidelity (softmax competition against a ~65 % home class)
and a disruptive migration of the shipped Head 1. The literature has fought this exact fight in other
domains — we want its scars, not our own.

---

## REQUIRED OUTPUT TABLES — fill every cell

### Table 1 — Representation options

| Option | Mechanics | Exclusivity guaranteed? | Rare-class behaviour (2 % retail vs 65 % home) | Migration impact on shipped Head 1 | Citation |
|---|---|---|---|---|---|
| Independent binary heads (**incumbent + dr_L3-08 recipe**) |  | no — impossible states possible |  | none |  |
| Single categorical location head {home, work, retail, other-out, travel} per slot |  | yes |  |  |  |
| Hierarchical: binary "out-of-home?" then categorical destination |  |  |  |  |  |
| Binary heads + exclusion constraint (loss penalty or projection) |  | soft / at decode time |  |  |  |
| Structured per-slot output (CRF / autoregressive across channels within a slot) |  |  |  |  |  |

### Table 2 — Constraint-enforcement mechanics (for any non-softmax option)

| Mechanism | How it enforces ¬(two places at once) | Effect on probability calibration (we need unbiased population fractions) | Evidence | Citation |
|---|---|---|---|---|
| Loss penalty on co-activation |  |  |  |  |
| Post-hoc projection / argmax-style decode |  |  |  |  |
| Architectural (grouped softmax over location channels) |  |  |  |  |
| None — accept and measure violations |  |  |  |  |

### Table 3 — Evidence from location/trajectory generation (the decisive table)

| Study | Task | Representation chosen (categorical state vs stacked binaries) | Stated reason / observed consequence | Citation |
|---|---|---|---|---|
|  |  |  |  |  |
|  |  |  |  |  |
|  |  |  |  |  |

### Table 4 — Consequences for our gates and downstream

| Question | Answer under binary heads | Answer under categorical head | Citation |
|---|---|---|---|
| How is the impossible-state rate measured and bounded? |  |  |  |
| Do per-channel marginals stay individually calibrated? |  |  |  |
| Does the dr_L3-08 rare-head recipe (pos_weight, PR-AUC/F1 gates) carry over? |  |  |  |
| How does the OR-rule's activity arm (retail without a retail location code) fit the class set? |  |  |  |

### Table 5 — VERDICT MATRIX (the deliverable)

| Option | Fidelity expectation (marginals + transitions + exclusivity) | Migration cost / risk to shipped heads | Verdict (recommend / viable / reject) |
|---|---|---|---|
| Keep independent binary heads (+ violation monitoring) |  |  |  |
| Keep binaries + explicit exclusion mechanism (name it) |  |  |  |
| Categorical location head (full migration) |  |  |  |
| Hierarchical two-stage |  |  |  |

---

## Part C — Synthesis (the representation verdict)

Give: (1) a single recommended option with its two strongest citations; (2) if binaries are kept, the
exact **exclusivity gate** to add to Step-4 validation (metric + threshold for the impossible-state
rate, and whether to enforce at decode time); (3) if the categorical head is recommended, the exact
class set (including where `travel` and `other` land), how the OR-rule's activity-arm retail episodes
are labelled, and the migration path that leaves shipped AT_HOME behaviour bit-compatible for Leg-1/2
reproduction; (4) an explicit statement of how the choice interacts with OPEN DECISION 1 (the
online-shopping gating) — which order to decide them in; (5) the reviewer-facing sentence: why the
chosen representation preserves both individual-channel calibration and physical consistency.

## Output format (follow exactly)

1. **Lead with Tables 1–5 fully populated.**
2. Then Part C synthesis.
3. Inline citations; note evidence scale/domain per claim.
4. **"Confidence and caveats":** where domain transfer is weakest.
5. **Reference list** — full citations, dates, URLs/DOIs.

## Hard requirements

- **Calibration is the ruling criterion** — population fractions feed physical simulations; any
  mechanism that fixes exclusivity but biases marginals must say so in its cell.
- **Table 3 must contain real location/trajectory-generation precedents** — if none exist, that GAP is
  itself a finding (we default to the lower-migration option).
- **Every option's row must state the migration impact on the shipped Head 1.**
- **No fabricated precision;** flag GAPs. **Stay on topic** — representation only; backbone is
  `dr_L3-11`, regimen is `dr_L3-13`.
