# 3J Leg-3 — Backward audit of the whole chain, Steps 1 → 9

### Are the *early* steps sound? An independent re-reading of preprocessing, training and linkage, from the artefacts

**Date:** 2026-08-03 · **Scope:** `Leg3_4-split/Step1_docs` … `Step9_docs`, `improvements/`, `Leg2_2-split/`, `2J_docs_occ_nTemp/writing/fullSet/`
**Status:** investigation document. No code changed, no artefact touched, no gate re-run.

---

## Aim

Steps 5 → 9 have been audited hard, repeatedly, and the audit culture on them is genuinely good — ten
named classes of vacuous test, findings retracted when the mechanism turned out wrong, gates
re-specified rather than widened. Steps 1 → 4 have not had that treatment. They were closed between
2026-07-19 and 2026-07-21, in three days, and have been treated as settled ever since: Step 4 is
labelled *"DEFINITIVELY COMPLETE — 0 genuine model defects, PAPER-READY"*.

The question this document answers is the one you asked: **is anything upstream wrong, and are we on
the right road?** Not "does the pipeline run" — it does — but "does the thing it produces mean what
the papers will say it means".

## Method, and its limits

Everything below is read from the artefacts and the code, with file and line references. Where a
claim rests on a document rather than a measurement I say so.

**What I did NOT do, and what that costs:**

- I did not re-run any validator, and I did not open `augmented_diaries.csv` (418 MB) or any
  `eplusout.sql`. Every number I quote is either from a validation report `.txt` on disk, a Progress
  Log entry, or source code. **Per the standing rule, a logged number is not evidence** — so each
  finding below carries an explicit *falsifier*: the one cheap measurement that would confirm or kill
  it. Nothing here should be acted on before its falsifier is run.
- I did not read the 13 `deepResearch/` reports. Findings that turn on what a dr report actually
  says are flagged as such.
- Step 8/9 are covered only where the *upstream* steps determine them. The Step-8/9 improvement logs
  already cover their own ground far better than a re-reading would.

---

## Verdict, up front

**The road is right. The pipeline is not broken. But three things upstream are load-bearing for the
paper and are not yet established — and one of them is already in the submitted 2J manuscript.**

| | Finding | Severity | Touches |
|---|---|---|---|
| **B-1** | Residential People = `HHSIZE × any-member-present`, and intra-household presence diversity is exactly zero | 🔴 **High** | 2J (submitted), Leg-2, Leg-3 |
| **B-2** | Step-5 `MIN_POOL` was chosen by *which value makes gate W1 pass* | 🔴 **High** | Leg-3 Step 5 → 9 |
| **B-3** | The two gates built to catch a dead retail head never read the shipped pool | 🔴 **High** | Leg-3 Step 4 |
| **B-4** | The retail level anchor "≈2.1–2.3 %, stable" is contradicted by the project's own measurement (−25 % drift) | 🟠 Med-high | Leg-3 Steps 2, 4, 6 |
| **B-5** | The retail rate gate measures a quantity the injector deliberately discards | 🟠 Med-high | Leg-3 Steps 3, 4, 7 |
| **B-6** | ISR-raw: spec gate `FAIL @ 0.5 %` re-derived to `never-FAIL @ 1.5 %`, delivered 0.70 %, printed `[PASS]` | 🟡 Med | Leg-3 Step 4 |
| **B-7** | Two frozen design-freeze deliverables never executed: the 4-run ablation, and 5-seed mean ± sd | 🟡 Med | Leg-3 Step 4 |
| **B-8** | Défaut 7's corrected areas fixed the header; the body of the master doc still carries the wrong ones | 🟡 Med | Leg-3 Steps 7–9 docs |
| **B-9** | Step-5 `2.2` and `R1` FAILs are open with no located mechanism, and `R1` is proportionally large | 🟡 Med | Leg-3 Step 5 → 9 |
| **B-10** | Master doc still states QC hotel coverage 2005–2022; the artefact starts 2019 | 🔵 Low | Leg-3 docs |
| **B-11** | NECB densities and the 0.95 peak fraction are transcribed, never parsed from the IDF — **parsed 2026-08-03: two of them are wrong** | 🟠 **Med-high** (was 🔵) | Leg-3 Steps 7–9 |

Nothing here says a result is wrong. B-1, B-2 and B-3 say three headline results are **not yet
established to the standard the rest of the project holds itself to**, and a reviewer will find all
three.

---

## Update 2026-08-03 (evening) — the three literature reports have landed

`deepResearch Prompts/R1`, `R2`, `R3` reports are in. They move four findings. **None of the eleven
falsifiers has been run** — the reports are external evidence about the *literature*, not about this
pipeline's artefacts, so they change what a finding *means*, never whether it is present.

| | Moved to | What changed |
|---|---|---|
| **B-1** | 🔴 High — **confirmed and sharpened** | R1: **0 of 14** reviewed study lines use `any-present × N`; the practice is unattested. But R1 §B.3 also shows that **under perfect synchrony the two rules coincide** — so the audit's two halves are one defect, not two, and the operative one is the *synchrony*, not the max. See the R1 box in B-1 |
| **B-2** | 🔴 High — **confirmed, and now fixable by writing alone** | R3: **7 of 8** authorities give no minimum-donor rule, so no citation determines `MIN_POOL`; but the adjustment-cell floor convention (n ≥ 10–20) **retro-justifies 15 independently of W1**. Non-monotonicity confirmed as draw noise. The shipped value need not change |
| **B-4** | 🟡 Med — **downgraded to a documentation defect** | R2: the −25 % decline is **real and internationally corroborated** (ATUS −20.8 %, UK −34.4 %, HETUS −21.4 %), and the 0.97 lever is defensible *with one stated reconciliation sentence*. The doc line "stable across cycles" is simply wrong and must be corrected |
| **B-5** | 🟠 Med-high — **re-framed, and a second defect found underneath** | R2: no published conversion exists between the two bases because they have **different denominators** — the dr_L3-06 band was never the same quantity as the gated GSS rate. So RW6/11.4 is not only vacuous (#11), it was **specified against the wrong reference**. Against a TUS-basis reference the measured rate **passes**. Shape-vs-level sensitivity ≈ 1.2–2.8 % of retail EUI, so little rides on it either way |
| **B-11** | 🔵 Low → 🟠 **Med-high** | Verifying R2's NECB claim against the IDF found **two constants wrong**: retail density is 25.0 m²/person in the model, not ~3.7 (a 6.8× gap, stated in two master docs as a design property), and the 0.95 is the **office** peak fraction — the retail zones run an office-shaped baseline that dips to 0.5 at midday. See *Verification performed* |
| **B-3, B-6…B-10** | unchanged | Not literature questions; the reports were not asked and do not bear on them |

**Standing caution on all three reports.** They are secondary syntheses. Every citation that enters a
manuscript must be opened and checked first — see *Verification still owed* at the end of the external-literature
section. Two claims in particular are load-bearing and unverified: that IEA Annex 66/79 *explicitly
warn* against binary household scaling (R1), and the NECB table reference for the 0.95 peak fraction
(R2, and B-11 already asks for this from the IDF side).

---

# 🔴 B-1 — The residential channel puts the whole household in the room when one person is home

**And every member of every household has the identical presence profile.**

### The evidence

Three facts, from three different files, that were each recorded as unremarkable and are only
alarming together:

1. **Aggregation is a per-slot maximum over household members.**
   `2J_docs_occ_nTemp/writing/fullSet/readySubmission.md:211` — *"Households are then formed by
   aggregating agents sharing a dwelling unit and taking the per-slot maximum AT_HOME indicator
   across household members, so that a slot is classified as occupied if any member is present."*

2. **The people count is the full household size.**
   `Leg3_4-split/Step7_docs/3rdJ_07_bemIntegration_4split.md:12` and the master pipeline doc's
   routing table — Residential is `REPLACE`, `Number_of_People = HHSIZE`. The office row on the very
   next line says *"NECB density — **never HHSIZE**"*, so the asymmetry is deliberate and known.

3. **The maximum changes nothing, because the members are already identical.**
   `Leg3_4-split/Step5_docs/3rdJ_05_censusLinkage_4split.md:272` — *"`hom30`: byte-identical between
   `Full_Schedules` and `Full_Aggregated` too (HH-max aggregation is a no-op at the byte level for
   this pool — **not a bug**, `[5E]` log confirms HH-max logic ran; every HH's members already agree
   on `hom30` pre-aggregation)."*

### Why it matters

Put (1) and (2) together: the residential People schedule is
`People(t) = HHSIZE × 1[at least one member home at t]`. A four-person household where one teenager
is home at 14:00 is modelled as four people in the apartment. Sensible gains, latent gains, CO₂ and —
since T9-13 — service hot water all scale with that count. The bias is one-sided: it can only
over-state daytime residential gains, never under-state them, and it is largest exactly in the
midday shoulder that the 2J paper's headline finding is about ("midday fill and flattening",
`readySubmission.md:10`).

Now add (3). The byte-identity was logged as reassurance. It is the opposite. With ~23,882 households
over 30,273 persons, Leg-3 has roughly 6,400 multi-person households; for the maximum to be a
byte-level no-op across all of them, **every co-resident pair must share an identical 48-slot
presence vector**. That does not happen by chance. It means the linkage is giving co-residents the
same donor diary, or something equivalent — so the model contains *zero* intra-household occupancy
heterogeneity. The residential channel is one person's diary, replicated and multiplied by household
size.

That is a real modelling position, and it may even be defensible. What it is not is *stated*. And it
sits awkwardly against the four-channel argument itself, which is built on the premise that
conflating distinct populations "smears the longitudinal signal" (`3rdJ_00_4split_Occupancy_Pipeline.md:404`)
— the residential channel conflates the members of a household exactly that way.

### Magnitude, honestly

- **Leg-3 (this paper):** 30,273 persons / 23,882 households = **1.27 persons/HH**. Most households
  are single-occupant, so the over-count is small here. The tower's residential channel is 22.4–22.5 %
  of occupiable area and residential is *not* where the Step-9 FAILs live. Low material risk to Leg-3.
- **2J (submitted):** 286,537 individuals / 144,507 households = **1.98 persons/HH**. Here it is not
  small. The paper's residential energy magnitudes were nonetheless calibrated to SHEU within ±2.7 %
  across 48 of 48 cells (`readySubmission.md:450`) — which means either the bias is absorbed by the
  activity-driven end-use calibration, or it is real and the calibration has silently compensated for
  it elsewhere. **Which of those two is true is the question**, and it is answerable.

### Falsifier — cheap, and it decides the finding

```
1. Read Full_Schedules.csv. Group by SIM_HH_ID, keep groups with >1 member.
   Count groups where the 48 hom30 columns are NOT identical across members.
   Prediction if B-1 holds: 0, or a negligible count.
2. On the same file: compute Σ_t Σ_members hom30  vs  Σ_t HHSIZE × max_members hom30.
   The ratio is the people-hour inflation factor. Report it per HHSIZE bucket.
3. Do both on the 2J frame as well (144,507 HH) — that is where the number bites.
```

If step 1 returns a large count, B-1's second half is wrong and only the `HHSIZE ×` half stands.
If step 2 returns ≈1.0, there is no inflation and the whole finding dies. Either result is worth
having before the 3rd paper describes the residential channel.

### Recommended action

Do not change the model on this. Run the falsifier, then **either** state the semantics explicitly in
the methods of both papers ("household presence is modelled as any-member-present at full household
occupancy, an upper bound on daytime residential gains") **or**, if the inflation factor is material,
carry it as a named limitation with its measured magnitude. Deep-research prompt **R1** below asks
what the TUS-to-BEM literature actually does here, because that determines which of those two is the
honest sentence.

### What R1 returned — and the one correction it forces

`deepResearch Prompts/R1_household_occupancy_aggregation_report.md`.

**The headline is a clean negative, and it is worse than expected for the "it's standard practice"
defence.** Across 14 reviewed study lines and standards:

| Aggregation rule | Studies |
|---|---|
| `Any-present × N` — **the rule under audit** | **0** |
| Sum of present members / direct household Markov state | 8 |
| Single-representative diary or static density | 2 |
| Rule not stated at all | 4 |

R1's reading is that where a binary `any-member-home` indicator *does* appear in the literature, it
drives **HVAC setback logic**, not the People count — nobody multiplies it by N to make internal
gains. Richardson/Thomson/Infield, Widén, Wilke, Flett & Kelly, McKenna, Fischer, Tanimoto and NREL
ResStock all write the count of members actually present. So Option 1 of the two draft methods
sentences ("a standard convention") is not available: **it would be a false claim, and it would cite
Richardson for something Richardson does not do.** R1's verdict is Option 2 — declare it, with a
magnitude.

**Now the correction, and it matters more than the negative.** R1 §B.3 makes a point the audit
missed:

> Under perfect synchrony, $\max_i \mathbf{1}_{\text{home},i}(t) = \mathbf{1}_{\text{home},1}(t)$, so
> `Any-present × N` and `Sum of members` **produce identical schedules**.

Evidence item (3) says this pool *has* perfect synchrony. So B-1's two halves are **not two additive
biases — they are one defect seen twice**, and the max operator is dormant given the data it is fed.
The operative defect is the **synchrony itself**: the household can only ever be at N occupants or 0,
with no intermediate state, because every member carries one shared profile. The `HHSIZE ×` multiplier
is then simply how that shared profile is scaled, and it is *correct* conditional on synchrony.

This changes three things:

1. **The falsifier's step 1 becomes the decisive test, not a supporting one.** If co-residents' `hom30`
   vectors are identical, step 2's inflation ratio is **exactly 1.0 by construction** and measures
   nothing. The real magnitude question is not "max vs sum on this pool" but "what would the sum be
   under *realistic* member diversity" — which needs a counterfactual, not a re-read of the artefact.
2. **The fix is a design change, not a bug fix.** R1's caveat 2 is the reason: the GSS samples **one
   individual per household**, so intra-household diversity cannot be recovered from the survey — it
   has to be *manufactured* by pairing independent respondents into synthetic households. That is a
   Step-5 architecture decision, not a Step-7 injection patch, and it is well outside what this audit
   recommends touching.
3. **The literature offers a name for what the model does.** Perfect-synchrony household presence is a
   recognised simplification in the field (R1 §B.3 cites Widén, Wilke, Flett & Kelly on the cost of
   assuming it). That is a far more comfortable position to defend than "any-present × N", which has
   no precedent at all. **The papers should describe the residential channel in synchrony terms.**

**On the ±2.7 % SHEU calibration.** R1 §B.4 argues annual calibration absorbs a gain bias into
envelope/infiltration parameters and leaves a *diurnal* distortion that annual totals cannot see — the
mechanism the audit flagged as "one of two things is true". Treat this as a hypothesis with a stated
mechanism, not a finding: R1 gives no study that measured it on a calibrated model, and its quantified
figures (+180–260 % midday gain, 8–18 % annual heating reduction) are **assembled from occupant-density
sensitivity analogues, not measured for this rule**. They are order-of-magnitude framing. Do not put
them in a manuscript as though someone had measured them.

**Revised recommended action for B-1:** unchanged in cost, changed in wording. Run falsifier step 1
(it is now the whole test). Then describe the residential channel in both papers as *perfectly
synchronised household presence at full occupancy* — cite the synchrony-simplification line, not an
aggregation-rule line — and carry the absence of intra-household diversity as a named limitation. The
2J paper is submitted; this is a limitations-paragraph amendment, not a results change.

---

# 🔴 B-2 — `MIN_POOL` was selected by which value made a gate pass

### The evidence

`Leg3_4-split/Step5_docs/3rdJ_05_censusLinkage_4split_val.md:320`, verbatim:

> **Goal:** smallest `MIN_POOL` that flips W1 FAIL→PASS (from the MIN_POOL=10 baseline: W1=3.13pp/1
> slot, 0.13pp over the 3.0pp gate) without regressing W3 or introducing a genuine new FAIL.

The sweep that followed:

| MIN_POOL | 2.2 AT_HOME | W1 AT_WORK | W3 Colleagues | R1 AT_RETAIL |
|---|---|---|---|---|
| 10 | 6.10 pp | **3.13 pp — FAIL** | 0.870 — PASS | 4.402 — FAIL |
| 11 | 6.29 pp | 2.97 pp — PASS | 0.751 — PASS | 5.511 — FAIL |
| 12 | 4.37 pp | 2.47 pp — PASS | 0.714 — PASS | 5.292 — FAIL |
| **15 ← shipped** | **3.66 pp** | **2.05 pp — PASS** | 0.888 — PASS | 4.796 — FAIL |
| 20 | 4.86 pp | 2.98 pp — PASS | 0.200 — PASS | 4.815 — FAIL |
| 30 | 5.78 pp | **3.81 pp — FAIL** | n/a | 6.161 — FAIL |

Winner first declared 11 ("smallest passing value"), then switched to 15 the same day because 15
"dominates 11 on 2.2 without losing the W1 crossing". The log states plainly:
**"Publishable results change: donor assignments differ from the MIN_POOL=10 version"** (`:369`).

### Why it matters

Three separate problems, in increasing order of seriousness.

1. **The selection criterion is the gate.** The project's own standing rule is *"never widen a band or
   relax a gate to erase a FAIL"*. `MIN_POOL` selection does not move the threshold — it moves the
   model until the threshold is cleared, and the search was explicitly directed by the threshold.
   Functionally it is the same failure: after this, W1 = PASS is not evidence about the matcher. It
   is evidence that a free parameter was fitted to W1.

2. **W1 is non-monotonic in `MIN_POOL`.** FAIL at 10, PASS at 11–20, FAIL at 30. A real effect of pool
   breadth on presence fidelity would be monotone or at least single-signed. A statistic that crosses
   its gate twice in one sweep, with the crossings 0.13 pp and 0.81 pp deep on a 3.0 pp gate, is
   moving inside donor-draw noise. **The PASS at 15 is very likely a draw, not a property.**

3. **The switch 11 → 15 was made on `2.2`, a gate that still FAILs.** 2.2 went 6.29 → 3.66 pp against
   a ≤3.0 pp gate. Improving a failing gate is a fine reason to prefer a configuration; it is not a
   reason that makes the other gate's PASS meaningful. And it means two different gates each
   contributed to picking the parameter.

There is no independent justification for 15 anywhere in the Step-5 documents — no donor-reuse
argument, no effective-sample-size argument, no citation to the statistical-matching literature. The
number's entire provenance is the sweep table above.

### Falsifier

```
1. Re-run the MIN_POOL sweep under 5 different RNG seeds for run_slot_match().
   Report W1 as mean ± sd per MIN_POOL.
   If the sd across seeds at fixed MIN_POOL is >= ~0.5 pp, the 11-vs-15-vs-20 ordering is noise
   and B-2 point 2 is confirmed.
2. Compute, at each MIN_POOL, a criterion that does NOT look at W1/2.2/R1:
   mean donor-reuse count, share of agents drawing from a pool at exactly the minimum,
   effective donor diversity per cycle x stratum.
   If that criterion has an interior optimum, it can replace the gate as the selection rule.
```

### Recommended action

This is fixable without re-running anything expensive, and the fix is mostly writing:

- **Pre-register the criterion.** Choose `MIN_POOL` on the donor-diversity criterion above, decided
  before looking at W1/2.2/R1. If it lands on 15, the shipped result is unchanged and now defensible.
- **Report the sweep as a sensitivity, not as a search.** The table is genuinely useful — it shows the
  linkage gates are stable in the 11–20 band. Present it that way.
- **State W1's sensitivity.** "AT_WORK per-slot deviation is 2.0–3.8 pp across the plausible donor-pool
  range" is an honest and unembarrassing sentence. "W1 PASS" without it is not.

Deep-research prompt **R3** asks whether the statistical-matching / hot-deck literature gives a
principled minimum-donor-pool rule. If it does, that citation resolves this outright.

### What R3 returned — no rule exists, and that is the good outcome

`deepResearch Prompts/R3_donor_pool_size_criterion_report.md`.

**7 of 8 authorities state no minimum-donor rule.** D'Orazio/Di Zio/Scanu, Rässler, Andridge & Little,
Statistics Canada (BANFF/GEIS/CANCEIS), Eurostat, and the software defaults all treat cell size as an
analyst-chosen bias–variance trade-off. The single numeric rule found — Morris/White/Royston's
*k* ≈ 10 for predictive mean matching — governs a *k*-nearest-neighbour distance pool for a **scalar**,
not a categorical adjustment-cell floor, and R3 flags it as non-transferable here on its own initiative.

So no citation determines `MIN_POOL = 15`, and no citation can. **Three things follow, and together
they close B-2 without changing a single donor assignment:**

1. **The claim "15 is determined" was never available to anyone**, so nothing was lost by not having
   it. What is available is a *convention*: survey adjustment-cell collapsing floors of **n ≥ 10–20**
   (Little & Rubin 2002; Andridge & Little 2010; US Census CPS/ATUS practice, which collapses cells
   below n = 10). `MIN_POOL = 15` sits inside that convention. **The shipped value is retro-justified
   by a criterion that never looks at W1** — which is exactly what B-2 asked for, and it costs a
   citation rather than a re-run.
2. **The non-monotonicity is confirmed as draw noise**, independently, by someone who was told the
   sweep numbers but not the audit's reading of them: *"non-monotonic behaviour of a downstream
   validation metric across increasing pool sizes is a textbook indicator of draw noise, not a
   structural optimum."* The single-seed PASS at 15 is a favourable draw sequence.
3. **Tuning on the gate is named for what it is** — data-peeking, and Goodhart on W1: once selected
   because it satisfied W1, W1 cannot also serve as the independent test. The prescribed remedy is a
   multi-seed sensitivity presentation, not a re-selection.

One point R3 raises that the audit had not: **vector transfer raises the stakes on pool size, not
lowers them.** Every published donor-count rule is for imputing a scalar. Here one draw transfers a
48-slot correlated schedule, so an atypical donor contaminates 48 slots at once and a thin pool can
replicate a whole abnormal daily routine across several agents. That is a mechanism for W1's
sensitivity, and it is worth a sentence in the methods.

**Revised recommended action for B-2** — cheaper than the original, and it changes no result:

- Adopt the **adjustment-cell floor** (n ≥ 10–20) as the stated selection criterion, cite Little &
  Rubin 2002 / Andridge & Little 2010, and note `MIN_POOL = 15` falls within it. **Do not re-select.**
- Still run the falsifier's multi-seed sweep — R3's recommendation to report a mean ± CI band across
  `MIN_POOL ∈ [10, 20]` *requires* it, and it is the evidence that turns the sweep table from a search
  into a sensitivity.
- Say plainly in the methods that no published minimum exists. R3's drafted sentences are usable
  nearly verbatim, and stating the absence is stronger than implying a determination.
- Add the scalar-vs-48-slot-vector caveat as the reason pool size matters here more than the scalar
  literature would suggest.

---

# 🔴 B-3 — The gates built to catch a dead retail head never read the shipped pool

### The evidence

The whole point of `RW1` (PR-AUC ≥ 0.15) and `RW2` (F1 ≥ 0.25) is stated in the val plan
(`3rdJ_04_augmentationGSS_4split_val.md:20`): an all-zeros retail head scores JS = 0.010 bits and
*passes* a bare JS gate, so JS is demoted to secondary and RW1/RW2 become the real test.

What the shipped scorecard actually contains
(`outputs_step4/sweep/seed_3_g3fix_raked3_mindwell_actv/step4_validation_report.txt:100-101`):

```
[PASS] RW1 | PR-AUC (teacher-forced, from step4_training_log.csv): 0.5190
[PASS] RW2 | F1        (teacher-forced, from step4_training_log.csv): 0.3794
```

**Teacher-forced, from the training log.** Both numbers are training-time metrics computed with the
ground truth fed back in at every step. Neither is computed on `augmented_diaries.csv`, and neither
sees the free-running decode — which is where temperature 0.7, nucleus 0.9, the −ln 49 logit shift,
the min-dwell ≥ 2 slots constraint, the exclusivity projection and the post-hoc rake all live. The
val doc is honest about this (`:124`): *"`augmented_diaries.csv` carries no continuous retail score
post-decode, so these are read from `step4_training_log.csv`"*.

Two more of the same class, self-declared in the same place:

- **RW8** (calibration after the −ln 49 shift) — 04E never persists pre-threshold probabilities, so
  RW8 is a post-decode rate-difference proxy, sharing its underlying numbers with `RETM`
  (`report.txt:126`). It cannot detect a mis-applied logit shift, which is the thing it exists for.
- **REG-1 / REG-2** (Head-1/Head-2 drift ≤ 0.002 bits) — no row-identity-matched validation split
  exists across legs, so these are **synthetic-vs-synthetic** JS drift, not paired ΔJS
  (`report.txt:168-169`). The reported 0.00003 / 0.00008 bits are three orders of magnitude inside
  the gate, which is what a comparison of two aggregate distributions from the same generator tends
  to produce.

### Why it matters

Five of the Step-4 gates that carry the most weight in the sentence *"0 genuine model defects,
PAPER-READY"* are measurements of something adjacent to the deliverable. What *does* protect the
shipped pool is real and should be said: `RW4` transitions/day = 0.436 (an all-zeros head gives 0),
`RW3` midday error, the `S9` battery (AT_RETAIL EMD 0.248 slots, KS 0.081, mean-curve MAE 0.36 pp),
and ISR-final = 0 % recomputed from the CSV. Those are aggregate, population-level checks and they
pass on the artefact.

So the correct statement is narrower than the one on record: **the shipped retail channel is
verified at the population level and unverified at the individual level.** Whether the right person
shops at the right time — which is the entire justification for using a per-respondent generative
model instead of a population average — is not measured on the delivered pool anywhere.

For a paper whose novelty claim is a *per-respondent* TUS generator driving four channels, that is
the gap a methods reviewer goes to first.

### Falsifier

```
1. In 04E, persist the post-shift, pre-threshold retail probability per (row, slot) —
   the val doc already names the artefact: retail_prob_summary.json.
2. Recompute PR-AUC and F1 free-running on the held-out split, against observed ret30.
   Prediction: both fall below the teacher-forced 0.5190 / 0.3794. The question is by how much,
   and whether they stay above 0.15 / 0.25.
3. RW8 becomes literal at the same time: mean predicted probability vs observed base rate
   per (cycle x stratum).
```

Cost: one 04E re-run on the existing `seed_3` checkpoint (the same job that produced the g3fix pool,
~37 min GPU per the Step-4 log). No retraining.

### Recommended action

Run the falsifier — this is a genuinely cheap fix for a genuinely load-bearing claim. Until then,
Step 4's scorecard should read *"149 PASS / 16 WARN / 1 FAIL, of which RW1, RW2, RW8, REG-1 and REG-2
are measured off the training log or as cross-leg proxies, not on the delivered pool"*. The three
proxies are already flagged in the doc; the scorecard headline does not carry the flag, and the
headline is what gets quoted.

---

# 🟠 B-4 — "≈2.1–2.3 %, stable across cycles" is contradicted by the project's own measurements

### The evidence

The master pipeline doc states the retail level anchor twice, attributed to "audit §2":

- `3rdJ_00_4split_Occupancy_Pipeline.md:102` — *"Weighted share of episode-time in shopping
  locations: **~2.1–2.3 %**, stable across cycles."*
- `:237` — *"All-day episode-time share | ~2.1–2.3 %, **stable across cycles** | audit §2"*, listed
  as a validation target the synthetic must reproduce.

What Step 2 measured (`3rdJ_02_harmonizeGSS_4split_val.md:77-82`):

| cycle | `occPRE==5` | gated OR-rule | leak |
|---|---|---|---|
| 2005 | 1.71 % | **2.00 %** | 0.180 % |
| 2010 | 1.81 % | **2.14 %** | 0.142 % |
| 2015 | 1.58 % | **1.66 %** | 0.164 % |
| 2022 | 1.48 % | **1.50 %** | 0.067 % |

Step 3 measured the tiled all-day daily mean at **1.51–2.14 %** (`3rdJ_03_..._val.md:78`), below its
own 2–8 % provisional bar.

So: the band is 1.50–2.14 %, not 2.1–2.3 %; only one of four cycles reaches the stated band; and the
series **falls 25 % from 2005 to 2022**. "Stable across cycles" is not what the data says. Gate 1.2
duly WARNed on 2022 (1.48 % vs a 1.5 % floor) — that WARN was read as a band-edge nuisance rather
than as the fourth point of a monotone decline.

### Why it matters

Two live consequences, one benign and one not.

**Benign:** the design parameters keyed to "~2 %" — `α_retail = 0.3`, `pos_weight = 49` (implying a
2 % positive rate), the "rare head" framing — are all fine at 1.5–2.1 %. Nothing needs retraining.

**Not benign:** the paper's longitudinal retail story. The Step-6B lever sets 2030 retail presence
relative to 2022 = 1.00 at 0.90 / 0.97 / 1.05 (dr_L3-04), i.e. it treats the in-store share as
roughly flat to slightly declining over the next eight years. But the *observed* series already fell
25 % over the preceding seventeen. Those two statements are not obviously compatible, and the
project has never reconciled them in one place. Either

- the observed 2005→2022 decline is largely a diary-coding artefact (Step 2's own investigation of
  gate 2.3 found a real 2022 GSSP coding concentration — `occPRE==1` share among `occACT==4` episodes
  dropped 8.47 → 4.44 % while `occPRE==5` rose 75.15 → 90.32 %), in which case the *measured*
  longitudinal retail trend is partly instrumental and should not be presented as behavioural; **or**
- it is real, in which case a 2030 lever centred on 0.97 is markedly more optimistic than the
  project's own trend extrapolation, and that needs saying.

Both are defensible papers. Neither is the paper as currently written, which asserts stability in the
design doc and a near-flat lever in Step 6 while carrying a 25 % decline in its own validation tables.

### Falsifier

```
1. Fit the trend on the four gated shares (2.00 / 2.14 / 1.66 / 1.50) with survey-weighted SEs.
   Is the decline significant against cycle-to-cycle sampling error?
2. Decompose 2015->2022: how much of the drop is the occPRE==5 arm and how much is the
   activity arm collapsing (gated share minus location-only share: 0.29 / 0.33 / 0.08 / 0.02 pp)?
   That second column collapsing by 15x is a coding-regime signal, not a behaviour signal.
3. Compare to an external in-store retail spend/footfall series for QC and AB over the same span.
   If the external series also falls ~25%, it is behaviour. Deep-research prompt R2 covers this.
```

Note point 2 independently: the activity arm contributed 0.29 pp in 2005 and 0.02 pp in 2022. The OR
rule that OD-1 spent a decision on is, by 2022, contributing almost nothing. That is worth one
sentence in the paper and it is currently nowhere.

### Recommended action

Correct the two doc lines to the measured band, and add an explicit reconciliation subsection between
the observed 2005→2022 retail decline and the 2030 lever. This costs no compute.

### What R2 returned — the decline is real, the lever survives, the doc line does not

`deepResearch Prompts/R2_tus_presence_vs_footfall_report.md`.

**The either/or in "Why it matters" resolves to *both*, with the split quantified.** R2 puts the
Canadian series alongside the three long international ones:

| Series | Span | Decline in in-person shopping time |
|---|---|---|
| Canada GSS (this project's own measurement) | 2005 → 2022 | **−25.0 %** |
| US ATUS (annual, continuous) | 2003 → 2022 | −20.8 % |
| UK TUS / CTUR | 2000 → 2022 | −34.4 % |
| Eurostat HETUS | 2000 → 2020 | −21.4 % |

So the decline is **behavioural and internationally corroborated** — it is not a Canadian coding
artefact, and the project should stop treating gate 1.2's 2022 WARN as a band-edge nuisance. R2
attributes roughly **three-quarters of the drop to real behaviour and one-quarter to the 2022
GSS coding concentration** the project found on its own (the `occPRE==1` → `occPRE==5` shift at
`3rdJ_02_..._val.md` gate 2.3). That split is R2's estimate, not a measurement, and should be
reported as such — but the *direction* is settled: the trend is mostly real, so it must be presented
as behavioural with the instrumental component named.

**The level itself is also corroborated.** Episode-time share for shopping is 1.5–2.2 % in every
national series R2 examined. The measured Canadian 1.50–2.14 % is **normal international magnitude**,
not a weak signal. This is worth stating in the paper, because the project has spent three steps
treating its own retail level as suspiciously low.

**And the 0.97 lever survives** — but only with the reconciliation sentence written. R2's argument:
the 2005–2022 decline is the steep phase of e-commerce displacement; post-2022 e-commerce share has
plateaued (~15–19 % of retail sales) and footfall has stabilised at ~88–94 % of 2019, so 0.97 encodes
**saturation of the displacement curve rather than linear extrapolation**. Linear extrapolation of the
historical trend would have given ≈0.88, near the low band edge — which is why the two looked
incompatible. They are not; the model behind the lever was just never written down.

**Revised action for B-4 — it drops to a documentation task, but gains one required sentence:**

1. Correct `3rdJ_00_4split_Occupancy_Pipeline.md:102` and `:237` — the band is **1.50–2.14 %,
   declining ~25 % across cycles**, not "~2.1–2.3 %, stable". "Stable across cycles" is false and is
   listed as a *validation target the synthetic must reproduce*, which makes it worse than a typo.
2. Add the reconciliation subsection, and make it say the saturation argument explicitly. One
   paragraph.
3. Add one sentence that the measured level is internationally normal.
4. Falsifier step 3 is now **answered** — the external series fall by comparable amounts. Steps 1 and 2
   (survey-weighted significance; the 15× collapse of the activity arm) are still worth running and
   are still unrun.

---

# 🟠 B-5 — The retail rate gate measures a quantity the injector throws away

### The evidence

The dr_L3-06 weekday 12:00–14:00 band, 0.06–0.10, is enforced at three stages and fails at all three:

| Stage | Gate | Measured | Verdict |
|---|---|---|---|
| Step 3 | 11.4 | **3.31–4.89 %**, all cycles | WARN, "genuine signal-strength gap; carry to Step 4" |
| Step 4 | RW6 ×12 | **4.53 %** weekday, 8.36 % Sat, 4.98 % AB Sun | WARN ×12, "faithfully reproduces the weak observed signal" |
| Step 6 | 5.20 | `0.06–0.10 × lever` | inherited |

The Step-4 disposition is correct as far as it goes: the synthetic reproduces the observed rate to
within 0.4 pp, so the model is faithful and the gap is in the input. Time-use *presence* is
structurally lower than retail-sector *foot-traffic*; the two are not the same quantity.

### What nobody checked

Step 7 injects `retail_schedule_multiplier(t,c,d) = 0.95 × [ at_retail_fraction(t) / max_t at_retail_fraction(t) ]`
— **peak-normalised** (master doc `:294`, dr_L3-06, with raw-fraction injection explicitly REJECTED).
The denominator is the channel's own maximum. The level cancels.

Which means: **the weekday rate could be 4.5 % or 9 % and not one number in any EnergyPlus input file
would change.** RW6 and 11.4 can fail forever without touching the deliverable, and if they were
fixed nothing downstream would move. This is a new member of the project's vacuous-gate taxonomy,
and it is the mirror image of the ones already catalogued:

> **#11 — the gate that measures a quantity the deliverable discards.** It *can* fail — it does, 12
> times — but its failing carries no information about the product, and its passing would carry none
> either. The tell is a normalisation step downstream of the gate whose denominator is the gated
> quantity itself.

The 2.1–2.3 % level anchor (B-4) is in the same position with one exception: the level *does* re-enter
through the Step-6B lever, which is a multiplier on amplitude applied **before** normalisation
(master doc `:266`). So the level matters for 2030 scenario spread and for nothing else.

Meanwhile the gates that *do* bind on the injected product are the shape ones, and they are treated
as secondary: `RW7` Sat-peak > weekday-peak (0.0836 > 0.0453 — **PASS**, and this is the one that
survives normalisation), the night floor 0.000–0.003 (PASS), peak *timing*, and the QC-vs-AB Sunday
ratio. The project graded the informative gate as a sub-check of RW7 and the uninformative one as
twelve separate WARNs.

### Falsifier

```
Take the retail product for two cycles whose weekday rates differ most (2010: 4.89%, 2022: 3.31%).
Peak-normalise both. Compare the 48-slot vectors.
Prediction if B-5 holds: the difference is pure shape, and the ~32% level gap between them
has vanished entirely. Then confirm the injected Schedule:File values are identical
under a fixed lever.
```

### Recommended action

Re-specify, not re-run:

- **RW6 / 11.4 → INFO**, with the provenance sentence attached ("time-use presence is structurally
  ~half the foot-traffic band; the level is discarded by peak-normalisation and re-enters only
  through the Step-6B amplitude lever").
- **Promote the shape gates to PASS/FAIL:** Sat/weekday peak ratio, peak-slot timing, night floor,
  QC/AB Sunday ratio. Those are what the tower actually sees.
- This *removes* 12 WARNs from the Step-4 scorecard on a principled basis rather than by widening a
  band — the distinction matters and should be spelled out in the Progress Log entry that does it.

Deep-research prompt **R2** asks whether the TUS-vs-footfall factor-of-two is a documented, quantified
property with a published conversion, and whether anyone has validated a peak-normalised TUS retail
schedule against measured retail loads. If yes, the INFO label gets a citation instead of an
assertion.

### What R2 returned — the gate is vacuous *and* was aimed at the wrong quantity

`deepResearch Prompts/R2_tus_presence_vs_footfall_report.md`. Three answers, and one of them is a
new finding rather than a confirmation.

**1. No published conversion exists between the two bases — because they have different denominators.**
R2 finds a complete silo: time-use research measures person-time over the whole population; retail
operations and BEM research measure occupancy relative to *store design capacity* or floor area.

```
Presence_TUS(t)      = (# people in retail at t) / N_population
Presence_footfall(t) = (occupants in stores at t) / (total store design capacity)
```

Since `N_population ≫ total store capacity`, the two are not the same number and were never going to
be. **This is the finding.** The project's working explanation — "presence and foot traffic are
structurally different quantities" — was right, and is now sourced. But it has a sharper consequence
than the audit drew: the dr_L3-06 band **0.06–0.10 is a capacity-denominated rate**, and it was
enforced as a gate on a **population-denominated** rate at three separate stages. That is a category
error in the gate's specification, and it is why RW6/11.4 could never pass.

So B-5 is now **two** defects stacked:

> **#11 — the gate that measures a quantity the deliverable discards** (as originally written: the
> level is cancelled by peak-normalisation, so its pass/fail carries no information about the product).
>
> **And underneath it: the gate's reference was a different quantity than the gate's measurement.**
> Even if the level *had* reached EnergyPlus, the comparison would have been invalid. A gate can be
> vacuous and mis-specified at the same time, and this one is both.

**Against the right reference, the measured rate passes.** R2's international weekday-midday
population presence rates — ATUS 0.041–0.054, UK 0.035–0.048, HETUS 0.034–0.044 — bracket the
measured Canadian 0.033–0.049 cleanly. The channel is not weak; it was being graded against a
building-scale metric.

**2. Nobody has ever validated a TUS-derived retail schedule against metered loads.** A clean negative,
and R2 states it flatly: footfall- and sensor-derived retail schedules have been validated against
measured occupant counts and HVAC loads for individual malls, but no study validates a *TUS-derived*
retail schedule against metered retail energy. The honest claim is therefore *"no schedule of this
class has been empirically validated; we establish the population-level diurnal presence profile"* —
weaker than "validated", and publishable.

R2 also confirms the peak-normalisation decision itself was right: the isolated studies that took
diurnal shapes from time-use data (Tanimoto 2008; Santiago 2014) **also peak-normalised before applying
code densities**, because injecting raw population fractions would under-predict design gains by 10–20×.
dr_L3-06's rejection of raw-fraction injection is thereby corroborated.

**3. Very little rides on any of this.** R2's sensitivity synthesis: changing the retail occupancy
schedule *shape* while holding opening hours and peak density alters annual retail EUI by
**≈1.2–2.8 %**, while operating hours, lighting power density and outdoor-air rates account for
**85–95 %** of retail EUI variance. Combined with peak-normalisation cancelling the level, the whole
retail-rate question is a second-order driver of the deliverable. That is a reason to close the
question cheaply and correctly, not a reason to ignore it.

**Revised action for B-5** — the original three bullets stand, with the labels corrected:

- **RW6 / 11.4 → INFO**, and the provenance sentence is now *"the dr_L3-06 band is denominated on store
  design capacity, not on population; the two are not comparable quantities, and no published
  conversion exists (R2). Against population-denominated international references the measured rate is
  in range."* That is a stronger justification than the original "structurally ~half", which still
  implied the two were commensurable and merely offset.
- **Re-specify the reference, do not just downgrade the gate.** If a rate gate is wanted at all, it
  should read against ATUS/HETUS population midday rates. Note the discipline point: this is *not*
  widening a band to erase a FAIL — it replaces a wrong reference with a right one, and the right one
  happens to pass. That distinction must be spelled out in the Progress Log entry that does it, or it
  will look identical to the thing the project has a standing rule against.
- **Promote the shape gates to PASS/FAIL** — unchanged, and now better supported: shape is what
  survives normalisation, and shape is the only part with any EUI sensitivity at all.
- **dr_L3-06's "CONFIRMED" status needs revisiting.** A deep-research round confirmed a band that was
  the wrong quantity for the use it was put to. That is worth one line in the design-freeze record,
  because "CONFIRMED" is currently doing work it cannot support.

---

# 🟡 B-6 — ISR-raw: the one place the "never relax a gate" rule was not followed

**Spec** (dr_L3-12, master doc `:204`, `:388`): *"Raw model outputs: **ISR ≤ 0.5 %** (hard validation
gate — evidence the encoder learned the negative location correlation)."*

**Delivered** (`report.txt:127`):

```
[PASS] ISR-raw | Raw (pre-projection) ISR: 0.7031% ... WARN-capped per 4-channel re-derivation,
       never a hard FAIL (soft target <= 1.5%)
```

The build log (`val.md:121`) states the re-derivation openly: `_grade_isr_raw` is **never-FAIL**
because the 0.5 % bar was a Leg-2 two-channel threshold and a four-channel model shows more
pre-projection co-activation. That reasoning is sound. What follows from it is not: the band was
widened 3× *and* the severity floor removed *and* the result printed as `[PASS]`.

The measured 0.7031 % is 1.4× the spec bar. The honest line is `[WARN] ISR-raw | 0.7031 % vs a
2-channel-derived 0.5 % spec bar; re-derived soft target 1.5 % for 4 channels; deviation recorded`.
The binding gate — ISR-**final** = 0 %, recomputed from the CSV over 6,149,856 slots — genuinely
passes, and that is the one that matters for physical consistency. So this is a labelling defect, not
a result defect. But it is the project's own rule, and the scorecard currently reads clean where it
should read "deviated, documented".

**Note for context:** the 75.5556 % raw ISR that appears in the Step-4 log (`3rdJ_04_..._4split.md:388`)
is from the 180-row local smoke, not production. I checked; the production number is 0.7031 %. Worth
recording so nobody rediscovers the 75 % figure and panics.

---

# 🟡 B-7 — Two frozen design-freeze deliverables were never executed

`3rdJ_04_augmentationGSS_4split.md:19-20`, both still unchecked:

```
- [ ] Cluster: joint fine-tune (5 seeds) — BLOCKED on warmup .out review
- [ ] Ablation (≤ 4 runs: shared / LoRA / semi-shared / reserve)
```

The first line is **stale** — the project caught this itself (`:351`): array `1127957_0..4` ran all
five seeds to completion on 2026-07-19. So the seeds exist. What does not exist:

1. **The 5-seed mean ± sd table.** `report.txt:25` — `[WARN] 10.SEED | no --seed_summary provided`.
   dr_L3-13 (master doc `:222`) specifies *"Report mean ± sd over 5 seeds (normal: 1–2 % sd on
   F1/PR-AUC, 0.001–0.002 bits on JS)"*. This is a stated method with no corresponding result.
2. **The documented application of the selection rule.** dr_L3-13 requires gate-first filtering →
   lexicographic max retail F1 across candidates. Seed 3 is the pool of record; I found no record of
   the five seeds being gate-filtered and ranked on retail F1. It may have happened — but if it did,
   the evidence is not in the Step-4 documents.
3. **The ablation.** The single ablation dr_L3-13 judged worth its cost — shared vs LoRA vs
   semi-shared backbone — was never run.

### Why it matters

(1) and (2) are reviewer questions with cheap answers, and the material is already on the cluster:
`outputs_step4/seed_0..seed_4/` all exist independently by design (`:353`). Running the validator on
the other four pools and publishing the table costs four CPU jobs. Given B-2's demonstration that
this project's gates sit close enough to their thresholds for a draw to flip them, a seed-spread
table is not a formality — it is the thing that tells you which PASSes are robust.

(3) is defensible to skip, but it should be *stated* as skipped with a reason, not left as an
unticked box in a document that elsewhere says "DEFINITIVELY COMPLETE".

**Recommended action:** run the validator across seeds 0–4, publish mean ± sd for every gated metric,
and record whether seed 3 wins the lexicographic rule or was chosen another way. Declare the ablation
dropped, with the reason.

---

# 🟡 B-8 — Défaut 7 corrected the header and left the body

Défaut 7 (2026-07-31) established, by parsing the IDF and SQL: total areas **135,857.6 m² / 72,623.1 m²**
and Service/MEP **20.64 % / 21.41 %** of gross. The master doc's header block says so at length
(`:18-48`).

The *body* of the same document still says:

- `:320` — *"SuperTall 40,846 m² / Tall 26,750 m² verified identical across cities"* (2.7–3.3× wrong)
- `:325` — *"Service/MEP (~52 % gross): prorated by area…"*
- `:410` — *"Service / MEP / Circulation (~52 % gross) left on NECB baseline"*

and the Overview doc repeats both at `:115`, `:126`, `:198`.

Every one of those is a live instruction to a downstream step. `:325` in particular specifies the
proration rule for the SCIEU comparison using the wrong share — proration at 52 % versus 20.6 %
changes each channel's stock-basis EUI by a factor of about 1.6. Whether any table was actually
generated from the body text rather than from `agg_meta.csv` is worth ten minutes of checking.

The deeper point, which is Défaut 7's own lesson and is worth stating in the paper's methods: the
original Tall column repeated **24.4 % for three different channels** — three identical values to one
decimal are a template, not a measurement. Grep the remaining design documents for other repeated
constants of that shape before the paper is written.

**Recommended action:** a single pass over both master docs replacing every occurrence with the
parsed values and a pointer to `Step8_docs/outputs_step8/agg/agg_meta.csv` as the source of record.
Then confirm no Step-8/9 output used the 52 % figure.

---

# 🟡 B-9 — Step-5's open FAILs have no located mechanism, and R1 is proportionally large

Shipped Step-5 scorecard: **32 PASS / 4 WARN / 3 FAIL** at `MIN_POOL = 15`. The three FAILs:

| Gate | Value | Gate | Status |
|---|---|---|---|
| **2.2** AT_HOME per-slot max deviation | 3.66 pp, 6 slots > 3 pp | ≤ 3.0 pp | FAIL, mechanism not located |
| **R1** AT_RETAIL per-slot max deviation | 4.796 pp | ≤ 3.0 pp | FAIL, mechanism not located |
| **PR** join-key overlap | 83.3 %, missing `[6]` | 100 % | FAIL, **fully explained** (GSS has zero Territories respondents in any cycle — a genuine sample-frame gap, 24/30,273 rows) |

PR is a clean, explained, permanent limitation — nothing to do but state it. The other two are not.

**R1 deserves attention it has not had.** The Step-5 log itself flagged it as the "not smoke noise"
trigger (`3rdJ_05_censusLinkage_4split.md:281`): full-scale 5.548 pp driven by `cycle=2005, dday=2`
with `n_out=1,407 / n_pool=19,221` — a well-populated cell — and **5 of 12 cycle×stratum cells over
gate**. It was recorded as *"a real carry-through/aggregation issue in the retail channel, not
sampling noise — needs manager triage before Step 5 is accepted"*. Step 5 was then accepted with R1
still failing and the triage not on record.

Scale matters here. The retail channel's population mean is **0.014953** — 1.5 %. A per-slot
deviation of 4.8 pp between the matched frame and the source pool is roughly **three times the
channel's entire mean level**. On AT_HOME (mean ~0.65) a 3.66 pp deviation is a 6 % relative error;
on AT_RETAIL a 4.8 pp deviation is not a small perturbation of the signal, it is larger than the
signal. The gate threshold was ported from a dense channel to a sparse one without rescaling, which
is why it reads as "one more inherited FAIL" instead of as the largest relative discrepancy in the
step.

Also note R1 moved with `MIN_POOL` — 4.402 → 5.511 → 4.796 across 10 / 11 / 15 — i.e. it is
draw-sensitive in the same way W1 is (B-2).

**Falsifier:**

```
1. For the driver cell (cycle=2005, dday=2): compare the matched frame's per-slot retail rate
   against the pool's, slot by slot. Is the deviation concentrated in the midday peak slots
   (a level/scale problem) or spread flat (a draw problem)?
2. Re-express R1 as a RELATIVE deviation (pp / channel mean) and set the gate on that basis.
   Prediction: AT_HOME and AT_WORK pass comfortably; AT_RETAIL does not, and that is the
   correct reading.
3. Re-run R1 under 5 match seeds at fixed MIN_POOL=15. If sd >~ 1 pp, R1 is a draw statistic
   and needs a different gate entirely.
```

**Recommended action:** locate R1's mechanism before the paper describes the linkage, or re-specify
the gate on a relative basis and record the decision. "Inherited, documented" is the right
disposition for 2.2; for R1 it is premature.

---

# 🔵 B-10 — The hotel coverage claim in the master doc contradicts the artefact

The master doc says QC is continuous 2005–2022 (`:127`, `:425`). The artefact is not:

```
QC : 2019-01 .. 2022-12   (2005-01..2018-12 blank)
AB : 2011-01 .. 2022-09   (2005-01..2010-12 blank; 2022-10..2022-12 blank)
```
— `Step6_docs/3rdJ_06_hotel_sarima_4split.py:26-28`

**This one is handled well and I want to say so.** The Step-1 validator caught it and reconciled the
gates rather than passing them (`3rdJ_01_..._val.md:90-93`). The Step-2 harmonizer builds a 216-month
*grid* with blanks, explicitly *"NOT imputed"* (`3rdJ_02_hotelHarmonize_4split.py:30`). The SARIMA
script refuses to pretend: gate 8.3 for QC is flagged **PARTIAL** with the message *"QC has no ground
truth for 2015-01..2018-12 … not silently passed as a full 5-year backcast"* (`:466-474`). And Step 9
(T9-6) resolved the consequence by excluding hotel from the epoch axis. That is the correct handling
of a data gap at every stage.

The only defect is documentary: two design-doc lines still assert coverage the project knows it does
not have. Fix the lines. Note also that a 216/216 grid *count* passing in Step 2 while Step 1 reports
48 observed QC months is exactly the kind of number that gets quoted out of context later.

---

# 🟠 B-11 — The NECB constants are transcribed, not parsed — **and two of them are wrong**

> **Upgraded 🔵 Low → 🟠 Med-high on 2026-08-03.** The check below was run. It found the next Défaut 7.

Office 25.0 m²/person; retail ~3.7 m²/person; the 0.95 NECB retail peak fraction; hotel guest-room
density. All four appear in the master doc as given values, sourced to the spec rather than to a
parse of the IDF. This is precisely the class of error Défaut 7 turned out to be — a number that
looked plausible, was never checked against the artefact, and was wrong by a factor of three.

Cheap check: parse `People` objects in the injected IDFs, extract `Zone_Floor_Area_per_Person` and
`People_per_Zone_Floor_Area` grouped by Tag 2, and compare. Ten minutes, and it either retires the
concern or finds the next Défaut 7. Given that Step 9's office FAIL has been chased for a week
through injector defects, lighting diversity and DHW specification, a wrong occupant density would be
worth ruling out explicitly.

### Result — the check was run, read-only, and it did not retire the concern

Full evidence, line references and consequences are in **Verification performed — 2026-08-03** under
the external-literature section. In brief:

| Constant | Doc says | IDF has | Verdict |
|---|---|---|---|
| Office density | 25.0 m²/person | `0.040015 person/m²` = **25.0 m²/person** | ✅ correct |
| **Retail density** | **~3.7 m²/person** | `0.040015 person/m²` = **25.0 m²/person** — bit-identical to office | 🔴 **wrong by 6.8×** |
| **0.95 retail peak fraction** | NECB retail/sales peak | The retail zones run `NECB-A-Occupancy`, peak **0.9**. The file's own `RetailStandalone` schedule peaks at **0.8** and is inert. The only 0.95 in the file is the **office** schedule | 🔴 **not a retail number in this model** |
| Injector formula | `0.95 × shape × lever` | Injected peak **0.9215 = 0.95 × 0.97**, identical on all three day-types | ✅ **implemented exactly as specified** |

Two further facts, one reassuring and one not:

- **Reassuring:** the amplitude effect of the whole retail injection is **+2.4 %** at peak (0.9215 vs a
  0.9 baseline). The constants being wrong barely moves the amplitude.
- **Not:** the baseline the retail channel replaces is `NECB-A-Occupancy`, which **dips to 0.5 at
  12:00–14:00** — a lunch trough. That is an office shape standing in for retail, where midday is the
  peak. The retail channel is therefore a **shape** intervention, and a larger one than documented.

**Revised recommended action:**

1. Correct `3rdJ_00_4split_Occupancy_Pipeline.md:291` and `Overview.md:113` — the retail density in the
   model is 25.0 m²/person, not ~3.7.
2. ~~Decide whether 25.0 m²/person is *intended* for the retail floors.~~ **Answered below: it is not.**
3. Re-source the 0.95, or restate it as what it is — an office-schedule peak fraction reused as a
   retail cap. Note that `dr_L3-06`'s NECB table reference could not be verified from public sources.
4. Add the office-shaped-baseline point to the Step-7 documentation. It strengthens the paper.
5. ~~Still unparsed: hotel guest-room density.~~ **Parsed below: also 0.040015.**

### Is 25.0 m²/person intentional for the retail zones? — **No.** Checked 2026-08-03

Three independent lines of evidence, all read-only from the two source towers and one injected product.

**1. It is a single blanket value across every space type.** Every `PEOPLE` object in *both* the Tall
and SuperTall source IDFs carries `0.040015 person/m²` — to six decimals — and the same
`NECB-A-Occupancy` schedule and `NECB-Activity` activity schedule:

```
Classroom · ClosedOffice · Conference · Corridor · Dining · Elevator
HighriseApartment · LargeHotel · OpenOffice · Restroom · Retail
   → all 0.040015 person/m² , all NECB-A-Occupancy
```

No code assigns one occupant density to a restroom, an elevator shaft lobby, a retail sales floor and
an apartment. Eleven identical values to six decimals is a fill, not a parameterisation.

**2. The same file differentiates retail everywhere else — which is the proof.** The archetype author
*did* treat retail as retail, in every property except the two occupancy ones:

| Property | OpenOffice | Retail sales / Entry / POS | Retail Back_Space | Differentiated? |
|---|---|---|---|---|
| OA per **person** (m³/s·person) | `0.002359737216` (5.0 L/s) | **`0.003539605824`** (7.5 L/s) | `0` | ✅ yes |
| OA per **floor area** (m³/s·m²) | `0.0003048` | **`0.0006096`** | `0.0006096` | ✅ yes |
| Lighting schedule | `OfficeLarge BLDG_LIGHT_SCH_2013` | `RetailStandalone BLDG_LIGHT_BACK_SCH_2013` exists | — | ✅ yes |
| **Occupant density** | `0.040015` | **`0.040015`** | `0.040015` | ❌ **no** |
| **Occupancy schedule** | `NECB-A-Occupancy` | **`NECB-A-Occupancy`** | `NECB-A-Occupancy` | ❌ **no** |

An archetype that knows retail needs 7.5 L/s·person rather than 5.0, and that retail floors need
double the area-based outdoor air, but gives retail the same occupant density as a corridor, is not
expressing a modelling choice. **It is inconsistent with itself**, and the inconsistency is confined
to exactly the two fields nobody parsed.

**3. The project found half of this already, and read it narrowly.** `improvements/3rdJ_L3_improvements_step9.md:2235-2242`
states: *"The same probe found the tower carries **exactly one** PEOPLE schedule for every channel"*,
and correctly calls it *"an office-shaped NECB curve that is zero on Saturdays"*. That is the schedule
half of the same finding. It was handled as a **DHW reference** problem for T9-11 — the reference was
re-specified to `baseline_series` and the matter closed. Nobody asked what one-schedule-for-every-channel
implied about the **densities** sitting next to it. `0.040015` appears nowhere in the repository
before this audit.

> **This is the Défaut-7 tell, second occurrence.** The audit already recorded the rule at B-8: *"three
> identical values to one decimal are a template, not a measurement."* Here it is eleven identical
> values to six decimals, and it went past a probe that was looking directly at it.

### What it costs — and one thing it does not

**Demand-controlled ventilation is `No` on all 11 air loops.** Two consequences, and they point in
opposite directions:

- **Good, and worth stating in the paper:** outdoor air is *not* modulated by the occupancy schedule at
  runtime. So the injected retail / office / hotel schedules move **internal gains only** — sensible,
  latent, CO₂ — and never ventilation. That is independent support for R2's finding that schedule
  *shape* is a second-order EUI driver, and it should be said explicitly rather than left implicit.
- **Bad:** because OA is `Sum` method on the *design* density and is never modulated, the retail
  per-person term is permanently low by the full 6.8×:

| | Current (25.0 m²/person) | At 3.7 m²/person | Ratio |
|---|---|---|---|
| OA per person × density | `0.003539605824 × 0.040015` = 1.416e-4 | `× 0.27027` = 9.567e-4 | |
| OA per floor area | 6.096e-4 | 6.096e-4 | |
| **Total retail OA** | **7.512e-4 m³/s·m²** | **1.566e-3 m³/s·m²** | **2.08×** |

Retail outdoor air would **more than double**. In Montreal and Calgary that is a material heating
load, not a rounding term. Occupant gains are low by the same 6.8×, which *partly offsets* on heating
(less gain → more heating; less OA → less heating) and *reinforces* on cooling. **The net sign is not
predictable from arithmetic — it has to be simulated.**

**Hotel guest rooms are also `0.040015`** — B-11's fourth unparsed constant, now parsed. At ~30 m² per
guest room that is ~1.2 occupants, which is coincidentally plausible; but it is the blanket number,
not a hotel-derived one, and should not be presented as sourced.

**And this confirms B-1 directly at the artefact level.** The injected residential People objects read:

```
PEOPLE, F21 Resi_bot_E_Apartment People, ... ,
    MXU_Residential_Occ_HH76197,  !- Number of People Schedule Name
    People,                       !- Number of People Calculation Method
    4,                            !- Number of People
```

An absolute constant count of 4 — `HHSIZE` — modulated by a single shared household schedule. That is
`People(t) = HHSIZE × household-presence(t)`, written in the IDF, exactly as B-1 describes it.

### Recommended action — the doc is wrong either way; the model is a judgement call

1. **Correct the docs regardless.** `3rdJ_00_4split_Occupancy_Pipeline.md:291` and `Overview.md:113`
   claim ~3.7 m²/person as an implemented design property. It is not implemented. This is free.
2. **Do not silently re-parameterise the tower.** Changing retail density invalidates every Step-8/9
   retail comparison already run, including the 112-cell campaign.
3. **Proportionate middle path, and the recommendation: bound it with one sensitivity cell.** Run a
   single retail-density variant at ~3.7 m²/person against the `Default_NECB` baseline and report the
   ΔEUI. That converts "we don't know what this costs" into a measured number for one cell, at the
   price of one simulation, and it is the evidence needed to decide item 2 rather than guess it.
4. **Then choose, with the number in hand:** either accept the single-density NECB-A archetype and
   declare it as a stated limitation, or re-parameterise and re-run. **Do not choose before step 3** —
   the offsetting OA and internal-gain effects mean intuition is unreliable here.
5. Add the DCV-is-off point to the Step-7/9 documentation: the occupancy channels drive internal gains
   only, not ventilation.

---

# Step-by-step assessment

| Step | What it does | Assessment | Open |
|---|---|---|---|
| **1** Collection | GSS reuse (read-only, 8 files SHA-256'd, exact row counts) + hotel acquisition | **Sound.** Reuse manifest is the right pattern; hotel gates were reconciled honestly rather than passed | B-10 (doc) |
| **2** Harmonization | OR-rule freeze, leak cross-tabs, hotel grid | **Sound mechanically.** Gate 2.5 (rule correctness, 0 violations) is a real test. Gate 2.3's falling-leak WARN was properly investigated | B-4 (the level anchor and the decline) |
| **3** Merge & tiling | `retail_30min.csv` + bit-identity vs Leg-2 | **Strongest step in the chain.** Section 12 (SHA-256 identity of all 5 legacy outputs + parquet) is a genuinely falsifiable additive-safety proof. 120 P / 13 W / 0 F | B-5 (11.4's status) |
| **4** Transformer | 3 heads, warmup → PCGrad joint, projection, rake chain | **Mechanically sound, evidentially thinner than advertised.** Regression protection is real (REG-3/REG-4 on the artefact); ISR-final 0 % over 6.1 M slots is real; the G3/W3 reopen on 2026-07-21 was caught and fixed properly | **B-3, B-6, B-7** |
| **5** Linkage | Census↔GSS 4-tier match, exclusion, BEM frame | **Weakest link in the upstream chain.** Frame counts re-derived from the artefact (good practice, 30,273/23,882/648 reconciled exactly), but parameter selection and two FAILs are unresolved | **B-1, B-2, B-9** |
| **6** Forecast + hotel | Progressive fine-tune, DRIFT, retail lever, SARIMA | **Sound, and well audited already.** The bidirectional Stage-B + weekend-pooling fix took it 66P/15W/5F → 69P/15W/2F. Hotel gap handled honestly | B-4 (lever vs observed trend) |
| **7** Injection | `inject_mixed_use()`, Tag-2 dispatch, wiring gate | **Sound.** The hard wiring gate exists *because* Leg-2's silent failure taught it. Four channel products + validator | B-5 (normalisation), B-11 |
| **8** Simulation | 112-cell campaign, probes, aggregation | Extensively audited. Défaut 7 was found here | B-8 (doc cleanup) |
| **9** End-use loads | T9-9…T9-13, arms A–H | Extensively audited, currently running (arm H, job 1171496) | — |

---

# Cross-leg inheritance — what Leg-3 carries from 2J and Leg-2

| Inherited | From | Status |
|---|---|---|
| 4 AM-origin slot math, `(startMin−240) % 1440`, majority vote `sum ≥ 2` | Leg 1 | Verified; the −4 h injection offset bug was found and fixed, and 2J documents it as *"the single most consequential correctness intervention"* (`readySubmission.md:288`). **This is the model of how a bug should be handled** |
| `hom30` HH-max + `Number_of_People = HHSIZE` | Leg 1 → 2J → Leg 2 → Leg 3 | **B-1 — never audited in any leg** |
| Office People-field wiring (`Number_of_People_Schedule_Name`) | Leg 2 bug | Fixed, now a hard gate in Steps 7–8. Correctly handled |
| ffill/bfill empty-slot policy | Leg 1 | Applied uniformly; not independently checked in Leg 3 |
| Frame constants | Leg 2 | Correctly **not** inherited — Step 5 re-derives (`3rdJ_05_..._4split.md:24` warns explicitly against reusing 23,150/29,538/735). Good discipline |
| Schedule interface | Leg 2 | 2J ships hourly `Schedule:Compact`, 2 day-types (`readySubmission.md:284`); Leg-3 OD-8 says "inherit whatever Leg 2 chose" for `Schedule:File` @ 30 min. **The inherited value is named nowhere I could find.** Worth pinning before the methods section is written |
| SHEU / SCIEU calibration anchoring | Leg 1 / Leg 2 | Carried; SCIEU anchoring for the commercial channels is the Step-9 open work |

**One observation about the 2J manuscript specifically.** It is in good shape and internally
consistent — the 144,507 vs 144,465 two-panel design is disclosed and its consequence for the
longitudinal figure is stated in the limitations (`:432`), the clock bug is disclosed with its
measured energy-invariance (+2.85 % max), and the FailSafe-tier-never-invoked check is a real
falsifiable statement. **B-1 is the only finding in this document that reaches it**, and B-1's
falsifier should be run on the 2J frame before the 3rd paper cites 2J's residential channel.

---

# What is NOT wrong — worth recording so it is not re-audited

- **Step-3 bit-identity.** All five legacy CSVs plus the parquet are SHA-256-identical to Leg-2. The
  "additive on Leg 2" claim is proved, not asserted.
- **ISR-final = 0 %**, recomputed from `augmented_diaries.csv` over 6,149,856 slots, cross-checked
  against `isr_summary.json`. The exclusivity guarantee is real.
- **Diary completeness = exactly 1440 min/day in all four cycles.** No episode-coverage loss.
- **The OR-rule gating works.** Gate 2.5: the activity arm adds 0 weighted time on `occPRE ∈ {1,2}`.
  Step-3 11.10: 0 violations.
- **04T byte-identity guard held** — only `act30` changed, `hom30`/`wrk30`/`ret30` identical.
- **Frame arithmetic reconciles exactly** at Step 5: 30,273 − 648 = 29,625, with set equality
  verified, not just counts. The project learned the "matching count ≠ matching set" lesson and
  applied it.
- **OW5** is genuinely unobservable by construction (one diary-day per respondent) and fails
  identically in Leg-2. Carrying it as a documented non-defect is correct.
- **RW7's Sat > weekday sub-check** passing (0.0836 > 0.0453) is the single most informative retail
  result in Step 4, because it is the one that survives peak-normalisation into the BEM.

---

# Recommended order of work

Ordered by (evidence gained) / (cost), not by severity.

| # | Action | Cost | Resolves |
|---|---|---|---|
| 1 | Run the B-1 falsifier on both the Leg-3 and 2J frames | 1 script, minutes | B-1 — and it touches a submitted paper |
| 2 | Doc pass: Défaut-7 areas in the body, QC hotel coverage, the 2.1–2.3 % anchor | writing only | B-8, B-10, B-4 (part) |
| 3 | Parse `People` objects from the injected IDFs, compare to the 4 quoted densities | 10 min | B-11 |
| 4 | Re-label RW6/11.4 → INFO; promote the shape gates to PASS/FAIL | writing + small code | B-5 |
| 5 | Re-label ISR-raw → WARN with the deviation stated | one line | B-6 |
| 6 | Validator across seeds 0–4; publish mean ± sd; record the seed-3 selection rationale | 4 CPU jobs | B-7 |
| 7 | Persist retail probabilities in 04E; recompute PR-AUC / F1 / RW8 free-running on the pool | 1 GPU job (~40 min) | **B-3** |
| 8 | MIN_POOL: define an independent criterion, re-select, present the sweep as sensitivity | 1 script + writing | **B-2** |
| 9 | Locate R1's mechanism in the `2005 × dday=2` cell; re-specify the gate on a relative basis | analysis | B-9 |
| 10 | Write the retail-decline ↔ 2030-lever reconciliation subsection | writing | B-4 |

Items 1–5 change no result and can run alongside the arm-H campaign. Items 6–9 need cluster time but
no retraining. **Nothing in this document requires re-running Step 4's training.**

## Revised order, after the three reports

The reports made four of these cheaper and added three items that did not exist before. Replaces the
table above where they conflict.

| # | Action | Cost | Resolves | Changed by |
|---|---|---|---|---|
| 1 | B-1 falsifier **step 1 only** — are co-resident `hom30` vectors identical? Leg-3 and 2J frames | 1 script, minutes | B-1 | R1: step 2's ratio is 1.0 by construction if step 1 confirms, so it measures nothing |
| 2 | Doc pass: Défaut-7 areas, QC hotel coverage, **and the "stable across cycles" line → "1.50–2.14 %, −25 %"** | writing only | B-8, B-10, **B-4** | R2 settled the direction |
| 3 | Write the `MIN_POOL` methods justification on the adjustment-cell floor (n ≥ 10–20), citing Little & Rubin 2002 / Andridge & Little 2010. **No re-selection** | writing only | **B-2**, most of it | R3: 15 already sits inside the convention |
| 4 | Re-specify RW6/11.4 against a **population-denominated** reference, → INFO; promote the shape gates | writing + small code | **B-5** | R2: the old reference was the wrong quantity |
| ~~5~~ | ~~Parse `People` objects from the injected IDFs~~ — **DONE 2026-08-03.** Superseded by 5a/5b below | — | **B-11 upgraded** | it found two wrong constants |
| **5a** | Correct the retail density in both master docs (25.0, not ~3.7); restate or re-source the 0.95; document the office-shaped baseline | writing only | **B-11**, and strengthens B-5 | new |
| ~~5b~~ | ~~Decide whether 25.0 m²/person is intended~~ — **ANSWERED 2026-08-03: it is not.** One blanket value across all 11 space types, in a file that differentiates retail ventilation correctly | — | **B-11** | superseded by 5c |
| **5c** | **One sensitivity cell**: retail density ~3.7 m²/person vs `Default_NECB` baseline, report ΔEUI. Retail OA would be **2.08×** current; occupant gains 6.8× — the two offset on heating and reinforce on cooling, so the sign is not predictable | 1 simulation | **B-11**, and bounds the exposure of every Step-8/9 retail number | **decide only after this runs** |
| 6 | Re-label ISR-raw → WARN with the deviation stated | one line | B-6 | — |
| 7 | Rewrite both papers' residential-channel description in **synchrony** terms + limitation paragraph | writing | **B-1**, the part that reaches 2J | R1: synchrony is an attested simplification; `any-present × N` is not |
| 8 | Write the retail reconciliation subsection using the **saturation** argument | writing | B-4 | R2 supplied the argument |
| 9 | Validator across seeds 0–4; mean ± sd; record the seed-3 selection rationale | 4 CPU jobs | B-7 | — |
| 10 | Multi-seed `MIN_POOL` sweep → mean ± CI band over [10, 20]; present as sensitivity | 1 array job | **B-2**, the rest | R3 requires it to call the sweep a sensitivity |
| 11 | Persist retail probabilities in 04E; recompute PR-AUC / F1 / RW8 free-running on the pool | 1 GPU job (~40 min) | **B-3** | untouched — no report bears on it |
| 12 | Locate R1's mechanism in the `2005 × dday=2` cell; re-specify on a relative basis | analysis | B-9 | R3 bears on it: it may be a draw statistic |
| ~~13~~ | ~~Verify the load-bearing citations~~ — **DONE 2026-08-03**, all nine checked | — | see *Verification performed* | 1 contradicted, 1 unsubstantiated, 1 mis-cited, 5 outstanding |
| **13a** | Pull the ATUS / HETUS / UK midday presence rates from the **BLS and Eurostat tables directly** — do not accept them second-hand | 1 h | prerequisite for **B-5**'s re-specified gate | a gate is only as good as its reference |
| **13b** | Open Andridge & Little (2010) and the 4 "not stated" rows of R1's table | 1–2 h reading | **B-1**, **B-2** | the **0** count is what carries B-1 |
| **13c** | Fix the Richardson citation wherever it appears — including `dr_L3-06` and the master doc, which inherit the same conflation | 15 min | B-1, B-5 provenance | see below |

Items 1–8 are now writing or minutes. **B-2 and B-4 are close to closed on paper alone**; B-1's
paper-facing half is a limitations paragraph, not a model change; B-3 remains the one high finding
that still needs compute, and it is a single 40-minute job.

**Still true, and now doubly so: nothing here requires re-running Step 4's training.**

---

# External literature — three deep-research prompts, and what they returned

Three questions in this audit cannot be answered from project material. Prompts are written in
`improvements/investigation/deepResearch Prompts/`, following the M/V-series convention
(`idf_reader/.../v2/deepResearch/`): scope guard first, the deliverable as a table, an explicit
instruction that a finding weakening the paper is reported plainly, and a clean negative counted as a
result.

| Prompt | Question | Resolves |
|---|---|---|
| `R1_household_occupancy_aggregation_prompt.md` | How does the TUS-to-BEM literature aggregate multi-occupant households — any-present × HHSIZE, per-member sum, or something else — and what is the documented energy consequence of the choice? | **B-1** |
| `R2_tus_presence_vs_footfall_prompt.md` | Is the ~2× gap between time-use retail presence and retail foot-traffic a documented, quantified property? Has any study validated a peak-normalised TUS retail schedule against metered retail loads? And do external in-store series show the same 2005→2022 decline? | **B-4, B-5** |
| `R3_donor_pool_size_criterion_prompt.md` | Does the statistical-matching / hot-deck literature give a principled minimum-donor-pool rule, decidable without reference to the downstream validation metric? | **B-2** |

Not proposed, and why: the exclusivity representation (dr_L3-12 covers it), the retail 2030 bands
(dr_L3-04), the hotel diurnal shape (dr_L3-05), multi-seed reporting conventions (a project decision,
not a literature question), and the EUI bands (dr_L3-02/03, already re-litigated in Step 9).

## Results — delivered 2026-08-03

All three reports are in `deepResearch Prompts/`, as `R<n>_<topic>_report.md`. Each is discussed in
full inside its finding; this is the one-line version.

| | Headline | Direction |
|---|---|---|
| **R1** | **0 of 14** study lines use `any-present × N`. But under perfect synchrony it is identical to sum-of-members — so the pipeline's real position is *perfectly synchronised household presence*, which **is** an attested simplification | Confirms B-1, **changes its mechanism**, and makes the fix a limitations paragraph rather than a model change |
| **R2** | No conversion exists between TUS presence and footfall — **different denominators**. GSS level and −25 % decline are both internationally normal. Retail EUI is ≈1.2–2.8 % sensitive to schedule shape. The 0.97 lever holds under a saturation argument | **Downgrades B-4** to documentation; **re-frames B-5** — the gate was mis-specified, not merely vacuous |
| **R3** | **7 of 8** authorities give no minimum-donor rule. Adjustment-cell floors (n ≥ 10–20) retro-justify `MIN_POOL = 15` independently of W1. Non-monotonicity = draw noise, confirmed | **Closes most of B-2 by writing**; the shipped value need not change |

Three of the reports' conclusions are *clean negatives* — no aggregation rule, no conversion, no
minimum-donor rule — and in each case the negative is more useful than a number would have been,
because it converts an unstated assumption into a statable limitation.

## Verification still owed

These are secondary syntheses, produced to a prompt. They are good enough to redirect the audit;
they are **not** good enough to cite. Before any of this reaches a manuscript, open the source and
check it. In descending order of how much weight it carries:

| Claim | Why it must be checked | Where it is used |
|---|---|---|
| IEA Annex 66 / 79 *"explicitly warns against binary household scaling"* | This is the strongest single sentence against the current implementation. If the Annex says no such thing, B-1's literature case rests on absence-of-evidence instead | B-1 |
| Richardson et al. (2010) uses a household Markov state, **not** `any-present × N` | R1 says the "standard convention" sentence would miscite Richardson. That accusation must be right before it is acted on | B-1 |
| The aggregation rule of each of the 14 rows | R1 marks 4 as "not stated" — check at least those 4 and 2 of the 8 "sum of members". The **0** count is what makes the finding | B-1 |
| NECB 0.95 peak fraction, and the table it comes from | Also independently checkable from the injected IDF — **audit item 5 does this**, and it is the cheapest cross-check available | B-5, B-11 |
| ATUS / HETUS / UK midday presence rates and minute-per-day figures | These become the *new* reference for a re-specified gate. A gate is only as good as its reference, which is the whole point of B-5 | B-4, B-5 |
| The 75/25 behavioural-vs-instrumental split of the Canadian decline | R2 gives no derivation. Report it as an estimate or drop the split and state only the direction | B-4 |
| "≈1.2–2.8 % EUI sensitivity to schedule shape" | Sets how much anything in B-5 is worth. If it is wrong by an order of magnitude the priority changes | B-5 |
| The +180–260 % midday gain and 8–18 % heating figures (R1) | Explicitly assembled from analogues, **not measured for this rule**. Order-of-magnitude framing only | B-1 |
| US Census CPS "collapse below n = 10" | The single concrete anchor for the `MIN_POOL` justification | B-2 |

Rule of thumb consistent with the rest of this document: **a citation is not evidence until it has
been opened.** The same standard that says a gate is not validation until it has been seen failing.

## Verification performed — 2026-08-03

All nine claims checked. **One is contradicted by the project's own artefact, one is unsubstantiated,
one has a broken citation attached to a correct claim, and five are unverified.** Verdicts first, then
the one that matters.

| # | Claim | Verdict | Basis |
|---|---|---|---|
| 4 | NECB 0.95 retail peak fraction **and** ~3.7 m²/person retail density | 🔴 **CONTRADICTED by the IDF** | The tower IDF, parsed. See below |
| 1 | IEA Annex 66/79 "explicitly warns against binary household scaling" | ❌ **Not substantiated — do not cite** | Annex 66 Final Report fetched (annex66.org, 5.1 MB); no passage on household aggregation or occupant-count scaling found. The PDF is largely image-based, so this is *not found*, not *proven absent* — either way it cannot be cited on this basis |
| 2 | Richardson does not use `any-present × N` | ✅ **Confirmed** — but R1's **citation is wrong** | See below |
| 9 | US Census CPS "collapse below n = 10" | 🟡 **Mechanism confirmed, threshold not** | CPS hot-deck does classify into adjustment cells and, when no match is found, "searches for a match at a lower level of detail, by omitting some variables and collapsing the categories of others". The specific **n = 10** is not confirmed; a threshold of **5** surfaces in some sources. Andridge & Little (2010) is open-access but returned 403 — still owed |
| 7 | ≈1.2–2.8 % retail EUI sensitivity to schedule shape | 🟡 **Direction supported, number unsourced** | That occupancy schedule is second-order to LPD and operating hours is broadly supported (PNNL-26019 and the sensitivity literature); the specific 1.2–2.8 % traces to no named study. **Use the direction, not the figure** |
| 5 | ATUS / HETUS / UK midday presence rates and minute-per-day values | ⚠️ **Unverified** | BLS confirms only the *direction* — purchasing time has declined since 2003. The specific minute values and the derived midday rates (0.041–0.054 etc.) were not retrievable. **These are the proposed new gate reference for B-5 — they must be pulled from the BLS/HETUS tables directly before any gate is re-specified on them** |
| 6 | 75/25 behavioural-vs-instrumental split | ⚠️ **Unverifiable** | R2 gives no derivation. Report the direction only, drop the split |
| 8 | +180–260 % midday gain, 8–18 % heating | ⚠️ **Confirmed as *not measured*** | R1 self-flags these as sensitivity analogues. Framing only |
| 3 | The aggregation rule of each of the 14 rows | ⚠️ **Outstanding** — 1 of 14 spot-checked | Only Richardson was opened. The **0** count is what carries B-1, so at least the four "not stated" rows still need checking |

### The one that matters — claim 4, parsed from the IDF

Read-only, from the Leg-2 source tower and a Leg-3 injected product:

| What | Value | Where |
|---|---|---|
| Retail zone People density, **source** | `0.040015 person/m²` = **25.0 m²/person** | `Leg2_2-split/.../CAN_MTL/TallBuilding_..._v242.idf:54292` |
| `OpenOffice` People density, same file | `0.040015 person/m²` — **identical** | `:54256` |
| Retail zones' baseline occupancy schedule | `NECB-A-Occupancy`, weekday peak **0.9**, **midday dip to 0.5** | `:96553` |
| `RetailStandalone BLDG_OCC_SCH_2010`, present in the file | weekday peak **0.8**, Sat peak **0.8** | `:1613` |
| …is it referenced by the retail zones? | **No.** It is inert | `:54274`, `:54292`, `:54310` |
| The only **0.95** occupancy peak in the whole file | `OfficeLarge BLDG_OCC_SCH Wkdy Day` | `:1093` |
| Retail zone People density, **injected** | `0.040015` — unchanged | `Leg3_4-split/.../B_central__Tall__MTL/injected.idf:80601` |
| Injected `MXU_Retail_People_B_central__Tall__MTL` peak | **0.9215**, on all three day-types | `injected.idf:12540` |

Four things follow, and they are not all bad news.

**1. The injector is working exactly as specified.** `0.9215 = 0.95 × 0.97` to four decimals, and the
peak is identical across Weekdays / Saturday / Sunday — which is precisely what per-cycle
peak-normalisation followed by the B_central 2030 lever should produce. **B-5's falsifier is
effectively passed in advance**: the level really does cancel, and the amplitude really is the product
of the two constants and nothing else. The formula in `Step7_docs/3rdJ_07_bemIntegration_4split.md:18`
is implemented correctly.

**2. The 0.95 is not a retail number in this model.** It is the *office* peak in the same file. The
retail prototype schedule that does exist peaks at 0.8, and is not connected to anything. Whatever
NECB Table A-8.4.3.2.(1)-A says — and it could not be verified, the NECB is not public — **the model
does not use a retail-specific peak fraction**, because the retail zones run on the generic
`NECB-A-Occupancy` schedule.

**3. The ~3.7 m²/person retail density is not in the model.** Retail runs at **25.0 m²/person**, bit-identical
to the office zones. Two documents assert otherwise as a design property:
`3rdJ_00_4split_Occupancy_Pipeline.md:291` — *"NECB retail density (~3.7 m²/person) — **do not scale
the count**"* — and `Overview.md:113` — *"density ~3.7 m2/person NEVER scaled"*. The instruction *not
to scale* was followed. The **stated density is off by a factor of 6.8**, and the number in the doc
has never been in the file.

**4. The retail baseline carries an office signature, and that is the real finding.** The
`NECB-A-Occupancy` schedule the retail zones inherit has a **midday dip to 0.5 at 12:00–14:00** — a
lunch-break trough, which is an office occupancy shape and the opposite of retail, where midday is the
peak. So the retail channel's *shape* replacement is doing considerably more work than anyone
accounted for: it is not refining a retail schedule, it is **replacing an office schedule that was
standing in for retail**. Meanwhile the amplitude barely moves (0.9215 injected vs 0.9 baseline,
**+2.4 %**).

That inverts the framing of B-5 one more time. The retail channel's contribution to the tower is
almost entirely **shape**, the amplitude constants are nearly a no-op, and the thing being corrected is
an office-shaped baseline — which is a *better* result for the paper than "we adjusted the level",
and it is currently nowhere in the documentation.

**Consequences for the audit:**

- **B-11 upgrades 🔵 Low → 🟠 Med-high.** It was written as "the constants are transcribed, never
  parsed". Parsing them found that **both** are wrong against the artefact, one by a factor of 6.8, and
  both are stated in the master doc as design properties. It is no longer a documentation nit.
- **B-5 gains a fourth item**: state that the retail baseline being replaced is office-shaped, and
  report the +2.4 % amplitude change so the reader knows the channel is a shape intervention.
- **A decision is now owed** that this audit will not make: whether 25.0 m²/person is *correct* for
  these zones. If the tower's retail floors are genuinely modelled at office density, retail occupant
  gains are ~6.8× below a true retail parameterisation, and every retail EUI comparison in Steps 8–9
  inherits that. If it is deliberate — a generic NECB-A archetype used consistently across the tower —
  then the doc simply must stop claiming 3.7. **Read the archetype's provenance before choosing.**

### Claim 2 — right conclusion, broken citation, and the project inherits it

The substance is **confirmed**. The Richardson occupancy model is a non-homogeneous Markov chain fitted
to UK time-use data at 10-minute resolution, and its abstract states the model *"indicates the number
of occupants that are active within a house at a given time"* — an integer count, not a binary
indicator. R1 is right that it does not do `any-present × N`, and right that citing it for that would
be a miscitation.

But R1's own reference is a conflation of two different papers:

| | R1's reference list, item 1 | What is actually true |
|---|---|---|
| Title | *A high-resolution domestic building occupancy model for energy demand simulations* | ✅ that is the **2008** occupancy paper |
| Year / vol / pages | 2010, 42(10), 1878–1884 | ❌ those belong to *Domestic electricity use: a high-resolution energy demand model*, **2010**, 42(10), 1878–1887 |
| DOI | `10.1016/j.enbuild.2010.05.023` | ❌ same — that is the 2010 electricity paper |
| Authors | Richardson, Thomson & Infield | the 2010 paper has a fourth author, **Clifford** |

**Correct citation:** Richardson, I., Thomson, M., & Infield, D. (2008). *A high-resolution domestic
building occupancy model for energy demand simulations.* **Energy and Buildings, 40**(8), 1560–1566.
DOI `10.1016/j.enbuild.2008.02.006`.

**This matters beyond R1**, because the project already carries the same conflation. The master doc
cites *"Richardson et al. 2010"* as authority for the peak-normalisation decision at
`3rdJ_00_4split_Occupancy_Pipeline.md:294` and `:433`, and `dr_L3-06` does the same. Whichever of the
two papers was meant, the year and the claim need checking together — and if the intended support for
peak-normalisation is the **occupancy** paper, the year is wrong in the project's own design record.

### And a circularity worth naming

R2 "confirmed" the 0.95 as the NECB retail peak fraction. That confirmation is **not independent**:
the R2 prompt supplied the value and asked R2 to *confirm* it, and the project's own earlier
`dr_L3-06` had already asserted the same table reference. Two rounds citing one unverifiable table is
not corroboration — it is the same claim twice.

> This is **vacuous-gate class #9 in citation form**: *the check whose reference comes from the same
> source it audits.* A verification prompt that names the answer it wants confirmed cannot fail. The
> IDF could fail, and did.

The lesson generalises to the rest of this table: **claims 5 and 7 must not be verified by asking
another model to confirm them.** Pull claim 5 from the BLS/HETUS tables and claim 7 from a named
sensitivity study, or drop both.

---

## Progress Log

### 2026-08-03 — Document opened

Backward audit written from the artefacts. Eleven findings (B-1 … B-11), three at high severity.
Every finding carries a falsifier; none has been run. **No number in this document should be treated
as established until its falsifier is executed** — that is the project's own standing rule and it
applies to this document as much as to any other.

Three deep-research prompts written to `improvements/investigation/deepResearch Prompts/`.

Not done, deliberately: no validator re-run, no artefact opened larger than a report `.txt`, no
`deepResearch/` report read, Steps 8–9 not re-audited.

### 2026-08-03 — Relocated

This document and its three prompts moved from `improvements/` into
`improvements/investigation/`, so the audit and its literature inputs sit together, separate from the
step-level improvement logs (`3rdJ_L3_improvements_step5_6_7.md`, `3rdJ_L3_improvements_step9.md`)
which remain in `improvements/`. Content unchanged; only the two internal path references above were
updated. Reports come back to `improvements/investigation/deepResearch Prompts/` as
`R<n>_<topic>_report.md`.

### 2026-08-03 (evening) — R1, R2, R3 reports received and folded in

All three literature reports delivered. Integrated at four places: a summary block under *Verdict, up
front*; a "What R*n* returned" subsection inside **B-1**, **B-2**, **B-4** and **B-5**; a revised
order of work; and a *Verification still owed* table.

What moved:

- **B-1 confirmed and sharpened, mechanism corrected.** 0 of 14 study lines use `any-present × N`.
  But under perfect synchrony that rule is identical to sum-of-members, so the audit's two halves are
  one defect, and it is the **synchrony**, not the max operator. The paper-facing fix is a
  limitations paragraph describing perfectly-synchronised household presence — an attested
  simplification — rather than an unattested aggregation rule. Falsifier step 2 is retired: its ratio
  is 1.0 by construction if step 1 confirms.
- **B-2 mostly closes on writing.** No literature minimum exists (7 of 8 sources), but the
  adjustment-cell floor convention n ≥ 10–20 retro-justifies `MIN_POOL = 15` without looking at W1.
  Non-monotonicity independently confirmed as draw noise. Multi-seed sweep still required to present
  the table as a sensitivity.
- **B-4 downgraded to a documentation defect.** The −25 % decline is real and matches ATUS/UK/HETUS;
  the level is internationally normal; the 0.97 lever holds under an e-commerce-saturation argument.
  The doc line "stable across cycles" is simply false and is listed as a validation target.
- **B-5 re-framed, and a second defect found underneath.** The dr_L3-06 band is denominated on store
  design capacity; the gated GSS rate is denominated on population. The gate was **mis-specified**,
  not merely vacuous — and against a population-denominated reference the measured rate is in range.
  Class **#11** stands; a re-specification is warranted and must be logged as *replacing a wrong
  reference*, not as widening a band. `dr_L3-06`'s "CONFIRMED" label needs revisiting.

What did **not** move: B-3, B-6…B-11 — no report bears on them. **B-3 remains the only high finding
still needing compute** (one ~40-minute GPU job).

Still true, and unchanged by any of this: **no falsifier has been run.** The reports are evidence
about the literature, not about this pipeline's artefacts. Added a standing caution — these are
secondary syntheses, and a citation is not evidence until it has been opened; nine specific claims are
listed as owing verification before they enter a manuscript.

### 2026-08-03 (late) — the nine citations verified; B-11 upgraded

All nine claims in *Verification still owed* checked. **The check earned its cost: one claim is
contradicted by the project's own artefact.**

- 🔴 **Claim 4 contradicted, and B-11 upgrades 🔵 Low → 🟠 Med-high.** Parsing the tower IDF (read-only,
  Leg-2 source + a Leg-3 injected product) shows the retail zones run at **25.0 m²/person** — bit-identical
  to the office zones — against **~3.7 m²/person** asserted as a design property in two master docs.
  A **6.8× gap**. And the 0.95 "NECB retail peak fraction" is the **office** schedule's peak: the
  file's own `RetailStandalone` schedule peaks at 0.8 and is inert, while the retail zones inherit
  `NECB-A-Occupancy`, which **dips to 0.5 at midday** — an office lunch trough standing in for retail.
- ✅ **The injector itself is vindicated.** Injected retail peak = **0.9215 = 0.95 × 0.97** exactly, on
  all three day-types. Peak-normalisation, the constant and the 2030 lever all behave as specified.
  **B-5's falsifier is effectively passed in advance.** Amplitude effect of the whole retail injection:
  **+2.4 %** over baseline — so the retail channel is a *shape* intervention, and a bigger one than
  documented, because the shape it replaces is an office shape.
- ❌ **Claim 1 (IEA Annex 66/79 "explicitly warns against binary household scaling") not substantiated.**
  Final report fetched; no such passage found. Do not cite it. B-1's literature case now rests on the
  0-of-14 count, which makes item 13b more important, not less.
- ⚠️ **Claim 2 right, citation broken — and the project inherits the same conflation.** The Richardson
  occupancy paper is **2008**, 40(8), 1560–1566, DOI `10.1016/j.enbuild.2008.02.006`; R1 attached the
  2010 electricity paper's year/volume/DOI to it. `3rdJ_00_4split_Occupancy_Pipeline.md:294`/`:433` and
  `dr_L3-06` cite "Richardson et al. 2010" for peak-normalisation and need the same fix.
- ⚠️ **Five outstanding.** Claims 5 (ATUS/HETUS rates), 3 (the 14 rows), 9 (CPS n = 10 — mechanism
  confirmed, threshold not), 7 (1.2–2.8 % EUI — direction supported, number unsourced), 6 and 8
  (self-flagged estimates). **Claim 5 is a prerequisite for re-specifying the B-5 gate** and must come
  from the BLS/Eurostat tables directly.
- 🔁 **A circularity named:** R2's "confirmation" of the 0.95 was not independent — the prompt supplied
  the value, and `dr_L3-06` had already asserted the same unverifiable table. **Vacuous-gate class #9
  in citation form: the check whose reference comes from the same source it audits.** The IDF could
  fail, and did. Claims 5 and 7 must not be "verified" by asking another model.

New open decision, and it is the user's, not the audit's: **is 25.0 m²/person intended for the retail
floors?** If not, every Step-8/9 retail EUI comparison inherits the gap. Recorded as item **5b**.

### 2026-08-03 (late) — the density question answered: **not intentional**

Checked, read-only. Full evidence in **B-11**. Summary:

- **All 11 space types in both source towers carry `0.040015 person/m²` to six decimals**, plus one
  shared `NECB-A-Occupancy` schedule — Classroom, ClosedOffice, Conference, Corridor, Dining, Elevator,
  HighriseApartment, LargeHotel, OpenOffice, Restroom, Retail. A blanket fill.
- **The same file differentiates retail correctly everywhere else** — OA per person 7.5 L/s for retail
  vs 5.0 L/s for office, OA per area doubled, retail-specific lighting schedules. The archetype knows
  what retail is; it just never got a retail occupancy density. **That internal inconsistency is the
  proof**, and it is confined to exactly the two fields nobody parsed.
- **The project had already found half of it** — `improvements/3rdJ_L3_improvements_step9.md:2235-2242`
  records *"the tower carries exactly one PEOPLE schedule for every channel"* and calls it office-shaped
  — but handled it as a T9-11 DHW-reference problem and never asked what it implied about the densities
  beside it. **Défaut-7's tell, second occurrence**, past a probe that was looking straight at it.
- **DCV is `No` on all 11 air loops.** So the occupancy channels drive **internal gains only, never
  ventilation** — independent support for R2's "shape is second-order", and worth stating in the paper.
  But OA is sized on the un-modulated design density, so retail OA is permanently low: **2.08×** at
  3.7 m²/person. Gains are 6.8× low. The two **offset on heating and reinforce on cooling**, so the
  net sign cannot be derived — it must be simulated.
- **Hotel guest rooms are also `0.040015`** — B-11's fourth constant, now parsed. Coincidentally
  plausible (~1.2 occupants per ~30 m² room) but not hotel-derived; do not present it as sourced.
- **B-1 confirmed in the IDF itself**: residential People objects are `Number of People = 4` (HHSIZE),
  constant, modulated by one shared `MXU_Residential_Occ_HH*` schedule.

**Recommendation, and it replaces item 5b with 5c:** correct the docs now (free), do *not* silently
re-parameterise the tower (it would invalidate the 112-cell campaign), and **run one sensitivity cell
at ~3.7 m²/person to measure ΔEUI before deciding anything.** Intuition is unreliable here because the
OA and internal-gain errors point in opposite directions on heating.
