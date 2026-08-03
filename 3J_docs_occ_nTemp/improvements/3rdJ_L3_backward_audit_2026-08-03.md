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
| **B-11** | NECB densities and the 0.95 peak fraction are transcribed, never parsed from the IDF | 🔵 Low | Leg-3 Step 7 |

Nothing here says a result is wrong. B-1, B-2 and B-3 say three headline results are **not yet
established to the standard the rest of the project holds itself to**, and a reviewer will find all
three.

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

# 🔵 B-11 — The NECB constants are transcribed, not parsed

Office 25.0 m²/person; retail ~3.7 m²/person; the 0.95 NECB retail peak fraction; hotel guest-room
density. All four appear in the master doc as given values, sourced to the spec rather than to a
parse of the IDF. This is precisely the class of error Défaut 7 turned out to be — a number that
looked plausible, was never checked against the artefact, and was wrong by a factor of three.

Cheap check: parse `People` objects in the injected IDFs, extract `Zone_Floor_Area_per_Person` and
`People_per_Zone_Floor_Area` grouped by Tag 2, and compare. Ten minutes, and it either retires the
concern or finds the next Défaut 7. Given that Step 9's office FAIL has been chased for a week
through injector defects, lighting diversity and DHW specification, a wrong occupant density would be
worth ruling out explicitly.

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

---

# External literature — three deep-research prompts

Three questions in this audit cannot be answered from project material. Prompts are written in
`improvements/deepResearch/`, following the M/V-series convention
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

---

## Progress Log

### 2026-08-03 — Document opened

Backward audit written from the artefacts. Eleven findings (B-1 … B-11), three at high severity.
Every finding carries a falsifier; none has been run. **No number in this document should be treated
as established until its falsifier is executed** — that is the project's own standing rule and it
applies to this document as much as to any other.

Three deep-research prompts written to `improvements/deepResearch/`.

Not done, deliberately: no validator re-run, no artefact opened larger than a report `.txt`, no
`deepResearch/` report read, Steps 8–9 not re-audited.
