# 3J Leg-3 — Backward audit of the whole chain, Steps 1 → 9

### Are the *early* steps sound? An independent re-reading of preprocessing, training and linkage, from the artefacts

**Opened:** 2026-08-03 · **Last updated:** 2026-08-04 (evening) · **Scope:** `Leg3_4-split/Step1_docs` … `Step9_docs`, `improvements/`, `Leg2_2-split/`, `2J_docs_occ_nTemp/writing/fullSet/`
**Status:** investigation document. No code changed, no artefact touched, no gate re-run.
**13 findings (B-1 … B-13), 3 at high severity.** B-11, B-12 and B-13 are read directly from the
artefact and are established as *present* without a falsifier. **B-1's falsifier has now been run and
B-1's stated mechanism did not survive it** (see the correction at the head of B-1). The remaining
nine are argued, not yet tested. See *Is this document ready?* at the end before citing any of it.

**Two independent blind audits reported on 2026-08-04** — Codex (`C-1 … C-5`) and Gemini (`G-1 … G-6`),
in `investigationPrompts/`. They are **not merged into this document**; the three-way comparison is in
*Update 2026-08-04 (evening)* below, and `C-`/`G-` numbering stays separate permanently.

---

## Aim

Steps 5 → 9 have been audited hard, repeatedly, and the audit culture on them is genuinely good — ten
named classes of vacuous test at the time this was written (**twelve as of 2026-08-04**), findings
retracted when the mechanism turned out wrong, gates re-specified rather than widened. Steps 1 → 4 have not had that treatment. They were closed between
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
| **B-1** | ~~Residential People = `HHSIZE × any-member-present`, and intra-household presence diversity is exactly zero~~ → **CORRECTED 2026-08-04**: Leg-3 uses `HHSIZE × mean(member AT_HOME)`, and intra-household diversity is **partial, not zero** (≥ 21.38 % of multi-person households measured non-identical). The surviving defect is that **Step 5 computes the household maximum and Step 7 never reads it** | 🔴 **High** (mechanism changed, severity held) | Leg-3 Steps 5, 7 — **no longer 2J** |
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
| **B-12** | Equipment power density is a single blanket `7.5028 W/m²` on every space type in both towers — while lighting *is* differentiated per space type. Occupancy and plug load are the two internal-gain fields that were never parameterised, and they are the two the paper's claim runs through | 🟠 Med-high | Leg-3 Steps 7–9 |
| **B-13** | The **2J** converter multiplies presence by `(occDensity + 1)` and then `.clip(upper=1.0)`. Neither operation appears in the submitted manuscript; `occDensity` is a **sum of per-member companion counts**, which double-counts co-resident co-presence, and the clip silently truncates the over-count | 🟠 **Med-high** | **2J (submitted)**, Leg-1 |

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

## Update 2026-08-04 — read against the Step-9 log (§0.18–§0.21) and its Reader's Guide

Three documents were re-read against this audit: `improvements/3rdJ_L3_improvements_step9.md`, its
byte-identical snapshot `..._BACKUP_2026-08-04.md` (md5 `40cbba0d…` on both — the backup carries no
divergence to fold), and the new `improvements/3rdJ_L3_step9_READER_GUIDE.md`.

The relationship between the two documents has inverted. On 2026-08-03 this audit was a side
investigation into steps nobody had revisited. On 2026-08-04 **Step 9 promoted two of its findings into
its own critical path** — `§0.21.4 Q2` recruits B-11, `Q8` is a backward-audit item — and its
recommended programme (`§0.21.6`) puts the IDF audit *first*, ahead of everything else, because it is
the cheapest thing that could explain the office deficit. So this audit is now load-bearing for
unblocking Step 9, and its own accuracy matters more than it did yesterday.

Four things follow.

### 1. Step 9 cites this audit by the wrong finding number — in the document written for cold reviewers

`§0.21.4 Q8` and `READER_GUIDE §1.4 Q8` both read: *"Backward-audit item **B-3**, still open. The
residential occupancy model uses `HHSIZE × any-present` with zero intra-household diversity, and this
reaches the already-submitted 2J paper. It is the only high-severity backward-audit finding still
needing compute."*

That is **B-1's content under B-3's number**, and the two have opposite cost profiles:

| | What it is | Reaches 2J? | Cost to resolve |
|---|---|---|---|
| **B-1** | `HHSIZE × any-present`, zero intra-household diversity | **Yes — submitted manuscript** | Falsifier **step 1 only** (R1 retired step 2), ~minutes; then a limitations paragraph. **No compute** |
| **B-3** | RW1/RW2 read teacher-forced numbers from `step4_training_log.csv`, not the shipped pool | No — Leg-3 Step 4 gates only | **One ~40-min GPU job** (04E persisting retail probabilities) |

The sentence fuses them, and the Reader's Guide table then answers *"needs simulation? **yes — the only
one**"*. That is correct for B-3 and **wrong for B-1**. As written, it tells an external reviewer that
the finding touching the submitted paper is blocked on cluster time. It is not — B-1's surviving work
is one script and a paragraph.

**Fix in the Step-9 documents** (this audit does not edit them): split Q8 into
**Q8a = B-1** (reaches 2J, desk work + one script, no simulation) and **Q8b = B-3** (Leg-3 Step-4
gates, one GPU job, the only backward-audit item needing compute).

### 2. A second, smaller number to fix in the same paragraph

`Q2` states office is *"19 % below its floor **even uninjected**"*. The uninjected `Default_NECB`
office is **85.45** against a floor of 100 — **14.55 % below**, needing **+17.0 %**. The 18.7 % figure
belongs to the *injected* `B_central` at 81.27. `§0.21.3` states the uninjected shortfall correctly at
15 %; only `Q2` carries the injected number under the uninjected label.

It is a small error in an important place: the entire force of `§0.21.3` is that the **uninjected**
control is the evidence, so the one paragraph that recruits this audit should not quote the injected
figure for it.

### 3. 🔴 Q2 is now ANSWERED — and the answer runs against what Q2 expected

`Q2` asks whether the office channel is mis-specified, and asks for *"an audit of office (and retail)
occupant density, lighting power density and equipment power density against NECB 2020 tables"*,
noting it is cheap because it only reads the IDF.

The occupant-density third was done here on 2026-08-03. **The remaining two thirds were parsed
2026-08-04** — see the new sweep in B-11 and the new finding **B-12**. Result, in one line:

> **Lighting is differentiated per space type. Occupancy and plug load are not — both are a single
> blanket value, and both blanket values are the *office* values.**

The consequence for `Q2` is the opposite of its premise. Office is the one channel for which these
constants are plausibly right; retail, hotel and residential are the channels wearing office's
clothes. **Correcting them moves retail, hotel and residential EUI. It cannot move office.**

So `Q2` resolves to **no — the office deficit is not an occupant-density or power-density
mis-specification**, and `§0.21.3`'s conclusion is *strengthened*: the office channel's 14.55 %
uninjected shortfall against its band has now survived the cheapest available explanation, which was
the one `§0.21.6` ranked first. What remains is `Q1` — band applicability — exactly as `§0.21.3` said.

*Scope of that claim:* what is established is the **internal** inconsistency (lighting parameterised,
occupancy and equipment blanket) plus the fact that the blanket values coincide with the office space
types. That needs no external reference. Whether `7.5028 W/m²` and `25.0 m²/person` are correct *for
office* still needs the NECB 2020 tables opened — new item **5e**.

### 4. B-11/B-12 now bear on a *blocking* Step-9 gate, and the sign is not obvious

`S9-EUI-retail` FAILs on two cells short of the 80.00 floor by **0.23 %** and **0.06 %** — and both are
`SuperTall__CLG`. B-11 and B-12 both change retail internal gains, which is the same quantity those two
cells are marginally short on, and the change is of order **6.8×** on occupant gains, not 0.2 %.

But the direction is genuinely undetermined, and Calgary makes it worse rather than clearer:

| effect | on retail EUI in a heating-dominated climate |
|---|---|
| occupant gains ×6.8 | **down** — internal gains displace heating |
| outdoor air ×2.08 (per-person term on the design density, DCV off) | **up** |
| equipment density, if it is wrong for retail | sign depends on which way, unknown until the tables are opened |

**This raises item 5c from exposure-bounding to decision-relevant.** It was written as "bound how much
of Step-8/9 retail is exposed"; it now also bears on whether `S9-EUI-retail` is measuring the retail
channel at all.

🔴 **And the standing rule applies with force.** 5c must be pre-registered and read as a *measurement of
exposure*, never as an attempt to make retail pass. If the corrected density happens to lift the two
cells into band, that is an incidental consequence of a specification fix and must be reported as one.
Writing the prediction before the cell runs is what keeps the two apart.

For the record against `§0.21.6`'s "stop running campaign arms": **5c is not the ninth arm.** It is one
cell, it changes a channel *specification* rather than trying to move a gate through the occupancy
channel, and its output is a ΔEUI, not a gate verdict.

### 5. The audit's diagnosis is not confined to Steps 1–4 — §0.21.5 reproduces it independently

This audit opened on the premise that Steps 1–4 were closed in three days and never revisited, while
Steps 5–9 had been audited hard. `§0.21.5` — written without reference to this document — reports the
same three structural failures at the *other* end of the pipeline:

| `§0.21.5` says | This audit found | Same failure mode |
|---|---|---|
| #1 *"`S9-EUI-*` gates are used as if they validate the occupancy model. They do not"* | **B-5** — RW6/11.4 measures a rate the injector's peak-normalisation discards | **vacuous-gate class #11**, at Step 4 and again at Step 9 |
| #3 *"no arm was launched with a pre-registered numeric prediction until arm E"* | **B-2** (`MIN_POOL` chosen by which value made W1 pass), **B-6** (ISR-raw band re-derived after the result) | the threshold decided with the answer visible |
| `Q7` — scorer's `BENCH["hotel"]` is `[180,300]`, decision #3 put it at `[240,300]` | **B-8**, **B-10** — the doc and the artefact disagree | the artefact wins silently, and no gate notices |

That changes how the audit should be presented. These are not *early-work* defects that later
discipline caught — the same habits ran through the middle of the campaign, in a period the project
regards as its most rigorous. For the methods paper that is the more interesting and more honest
framing.

### 6. Catalogue reconciliation, and what does NOT change

- **The vacuous-gate catalogue is now 12, not ten** (`READER_GUIDE §4`). This audit's **#11 — the gate
  measuring a quantity the deliverable discards** has been adopted into the canonical numbering. The
  circularity named on 2026-08-03 (R2 "confirming" a value my own prompt supplied) is an instance of
  the pre-existing **#9**, not a new class — recorded that way here. **#12** (a gate's count stable
  while its membership turns over completely — `S9-EUI-hotel` read 28/56 in both arms H and R, a
  *different* 28) is new from `§0.20.1` and bears on no B-finding.
- **Reversal #8** in the Reader's Guide (`prototype_people` not viable as the T9-13 reference: one
  PEOPLE schedule for all channels, `mean_we = 0.0000`) is the schedule half of B-11, now recorded in
  Step 9 as a reversal. Consistent with this audit; nothing to change.
- **Nothing else in §0.18–§0.21 bears on this audit.** Arms A–R, the DHW saga, the K sweep and the
  hotel plant work are all downstream of Step-7 injection. No Step-9 result touches B-1, B-2, B-3,
  B-4, B-6, B-7, B-9 or B-10, and none of the eleven original falsifiers has been run.

---

## Update 2026-08-04 (evening) — two blind auditors reported, and three of my claims moved

Two independent audits of the same pipeline were commissioned on 2026-08-04 and delivered the same
day, each blind to this document and to the other:

| Report | Auditor | Axis | Findings |
|---|---|---|---|
| `investigationPrompts/REPORT_codex_backward_audit.md` | Codex | code and artefacts | `C-1 … C-5` |
| `investigationPrompts/REPORT_gemini_backward_audit.md` | Gemini | claims and provenance | `G-1 … G-6` |

Both filed a clean blindness declaration. Gemini also left its working notes in
`investigationPrompts/gemini-docs/` (`implementation_plan.md`, `walkthrough.md`); nothing in them
contradicts its report.

**Per this folder's own reconciliation rule, the reports are not merged in.** What follows is the
comparison, and — where the three of us disagreed on a *value* — the artefact's answer, because rule 4
says settle those from the artefact and never by majority.

### The replication paid for itself, and not in the way it was meant to

It was run to see whether a second pair of eyes would find what I missed. It did — but the larger
return was that following **C-1 into the code falsified my own B-1**, and then falsified C-1's and
G-4's versions of the same claim as well. All three of us had the residential aggregation rule wrong,
in three different ways, and the artefact settled it in about twenty minutes of `awk`.

### The three-way reconciliation

| Their finding | Maps to | Verdict after checking the artefact |
|---|---|---|
| **C-1** Step-7 uses a per-member *mean*; Step-5's household *max* is computed and never read | **new** — B-1 did not state this | ✅ **CONFIRMED, and it is the best single finding either auditor produced.** Verified below. Its "reaches 2J: **yes**" attribute is ❌ **rejected** — cross-leg category error, verified below |
| **C-2** REG-1/REG-2 are synthetic-vs-synthetic, not row-matched; the validator says so itself | **new** | ✅ **CONFIRMED from the artefact's own text.** An instance of catalogue class **#9** — the gate whose reference comes from the same source it audits |
| **C-3** RW6 calls `_grade_band(hard=False)`; an out-of-band numeric value returns `warn`, never `fail` | **new** | ✅ **CONFIRMED.** New catalogue candidate, class **#13** — see below |
| **C-4** RW1/RW2 are teacher-forced numbers read from the training log, not the shipped pool | **B-3** | ✅ **INDEPENDENT CONFIRMATION of a high finding, found blind.** This is the strongest evidential event in the whole exercise |
| **C-5** The canonical Step-4 directory has no checkpoint and no `rake3ch_provenance.json` | **new**, adjacent to B-7 | ✅ **CONFIRMED as stated.** Reproducibility, not correctness |
| **G-1** Body text still says 40,846 m² / 26,750 m²; parsed areas are 135,857.6 / 72,623.1 | **B-8** | ✅ **INDEPENDENT CONFIRMATION**, same document, same lines (`:320`, Overview `:125`) |
| **G-2** The hotel As-Modelled PASS band `180–300` is contradicted by the PNNL rows in the report that defines it | **new** | ✅ **CONFIRMED, and it bears on a blocking gate.** Verified below. Overstated in one respect — see the caveat |
| **G-3** StatCan Table `24-10-0048-01` does not exist | — | ⚠️ **Self-refuting as evidence.** Its only source is `dr_L3-01`, the report that *found* the table missing. The finding is "a corrected error was corrected". Residual value: grep for surviving mentions |
| **G-4** `Number_of_People = HHSIZE × AT_HOME`, zero intra-household diversity, reaches 2J | **B-1** | ❌ **REJECTED as stated.** No code in either leg does this. G-4 is read from the manuscript only; Gemini never opened the 2J converter. It is my own B-1 error, reproduced from the same document |
| **G-5** Diagrams say "4-head Transformer"; implementation is 3 heads + SARIMA | — | ⚠️ **Self-refuting.** Its cited evidence is the master doc line that already states the diagram is a simplification and that §3.5 is authoritative |
| **G-6** Service/MEP prorated by floor area distorts tenant timing | — | ⚠️ **Weak.** Its own recommended action is "already planned" in `dr_L3-10`. Related to B-8's `:325` proration point, but B-8's version is sharper because it names a *wrong number* rather than a debatable convention |

### The four questions I settled from the artefact

**1. Does Step 7 use the household maximum? No — C-1 is right.**
`Step5_docs/3rdJ_05_censusLinkage_4split.py:1037` computes `hh_occ = df.groupby("SIM_HH_ID")[hom_cols].max()`
into `HH_hom30_*`, with the docstring *"HH occupied = max across members per slot"*.
`Step7_docs/3rdJ_07_aug_to_bem_4split.py:309` then computes `occ48 = df.groupby(["SIM_HH_ID","Day_Type"])[HOM].mean()`
— over the **raw** `hom30_*` columns. `HH_hom30_*` is never referenced in Step 7.

This is an independent instance of the class this audit itself contributed to the catalogue:
**#11, the quantity the deliverable discards.** B-5 found it for a gate; C-1 found it for the
household aggregation rule the submitted paper's §3.3 describes. Found blind, by a different auditor,
on a different object. That is about as good as corroboration of a *class* gets.

**2. Are co-resident presence vectors identical? No — my B-1 was wrong.**
If every co-resident carried the same vector, the only fractional values reachable in the hourly
output would be `{0, 0.5, 1}` — 0.5 arising from the half-hour pair averaging at
`3rdJ_07_aug_to_bem_4split.py:320`. Measured over all 785,616 multi-person rows of
`Step7_docs/outputs_step7/BEM_Schedules_4split_2022.csv`:

| | Rows | Share |
|---|---:|---:|
| `Occupancy_Schedule ∈ {0, 0.5, 1}` | 763,928 | 97.24 % |
| **outside that set** (0.25, 0.333, 0.667, 0.75, 0.833, 0.875, …) | **21,688** | **2.76 %** |

and by household:

| | Households | Share |
|---|---:|---:|
| multi-person `SIM_HH_ID` | 16,367 | — |
| **with ≥ 1 value outside `{0, 0.5, 1}`** | **3,499** | **21.38 %** |

A value of 0.75 or 0.667 is unreachable from identical member vectors. So **at least 21.38 % of
multi-person households carry non-identical co-resident vectors** — and that is a *lower bound*,
because two members disagreeing across a whole hour produce exactly 0.5 and hide inside the
"identical" column. **B-1's "exactly zero intra-household diversity" is falsified.**

The sign matters and it runs against what all three of us assumed. B-1 and G-4 both argued the rule
*over-concentrates* peaks. `HHSIZE × mean(member AT_HOME)` is a fractional expectation — it
**smooths**. Whatever the energy consequence is, it is the opposite direction from what this document
claimed for a day.

**3. Does C-1 reach the submitted 2J paper? No.**
Codex compared the **Leg-3** Step-7 converter against the **2J** manuscript. They are different
programs. The 2J converter is `eSim_occ_utils/21CEN22GSS/21CEN22GSS_HH_aggregation.py:174-176`, and
it *does* implement the maximum: `hh_df["occPre"] = (occupancy_count >= 1).astype(int)`, matching
`readySubmission.md:211` — *"taking the per-slot maximum AT_HOME indicator across household members"* —
exactly. C-1 is a **Leg-3** finding. Its highest-stakes attribute is wrong.

**4. Does the 2J converter match the 2J paper? Only partly — and that is B-13.**
`eSim_occ_utils/21CEN22GSS/21CEN22GSS_occToBEM.py:144-145` reads:

```python
estimated_count = hourly["occPre"] * (hourly["occDensity"] + 1)
occupancy_sched  = (estimated_count / hh_size).clip(upper=1.0)
```

Neither the `(occDensity + 1)` factor nor the `.clip(upper=1.0)` appears anywhere in the submitted
manuscript. Full finding at **B-13** below.

### What the two auditors found that I missed

Four things, and I would not have got to any of them on the road I was on:

- **C-2** — the legacy-head non-regression claim rests on a synthetic-vs-synthetic comparison, and the
  validator's own comment says the frozen split and respondent identities were never persisted. I had
  looked at Step-4's gates and not at this one.
- **C-3** — a gate that is *severity*-vacuous rather than *reference*-vacuous. I had ten classes of
  vacuous test in this document and none of them was this one.
- **C-5** — the canonical Step-4 output cannot be traced to the checkpoint that produced it. B-7 says
  two deliverables were never executed; C-5 says the one that *was* executed cannot be reproduced.
- **G-2** — and this one touches a blocking gate, so it gets its own paragraph.

### G-2 — the hotel PASS ceiling is contradicted by the table that defines it

`dr_L3-03_hotel_eui_bands_REPORT.md:13` recommends **As-Modelled Pass 180.0 – 300.0 kWh/m²·yr**.
Table 2 of the *same report*, at `:58-68`, lists:

| Prototype | Standard | CZ | EUI |
|---|---|---|---:|
| PNNL Large Hotel | 90.1-2004 | 6A | 286.4 |
| PNNL Large Hotel | 90.1-2004 | 7 | **302.2** |
| PNNL Large Hotel | 90.1-2016 | 6A | **484.0** |
| PNNL Large Hotel | 90.1-2016 | 7 | **521.2** |
| PNNL Large Hotel | 90.1-2019 | 6A | **441.6** |
| PNNL Large Hotel | 90.1-2019 | 7 | **479.5** |
| PNNL Small Hotel | 90.1-2019 | 6A/7 | 135 – 175 |
| NECB 2017 archetype | NECB 2017 | 6 (MTL) | 140 – 220 |
| NECB 2017 archetype | NECB 2017 | 7 (CLG) | 160 – 240 |

Six of the eleven reference rows sit **above** the ceiling the same report recommends. Every Large
Hotel row does.

**The caveat Gemini did not state.** The band is evidently derived from the two NECB 2017 rows
(140–240 → 180/240/300), and the modelled object *is* NECB-based (`…NECB17_Z6_v242`), so choosing NECB
over PNNL is defensible. G-2's "any code-compliant Large Hotel will automatically FAIL" overstates it:
the tower's hotel channel is a podium inside a mixed-use NECB tower, not a standalone PNNL Large Hotel.

**What survives the caveat is still serious**, and it is the same shape as the office problem
§0.21.3 established: the band's reference population is not the object being scored, and the report
that defines the band contains the evidence against it. `S9-EUI-hotel` fails against the **300**
ceiling specifically — the number in dispute — and Step 9's own resized campaign found hotel DHW was
undersized by a factor of ~2, so correcting it pushes hotel EUI *further* above 300.

🔴 **This is not licence to widen the band.** The project's rule stands. What it licenses is exactly
what Step-9 decisions #2/#3 already authorised on 2026-08-02 and never executed: a **re-derivation**
of the hotel band from a stated, archetype-matched reference, pre-registered before any cell is
re-read. G-2 supplies the citation that makes that re-derivation defensible rather than convenient —
it is an internal contradiction in the source, not a gate that became inconvenient.

### What neither auditor reproduced

B-2, B-4, B-5, B-6, B-7, B-9, B-10, B-11 and B-12. Per rule 3 this is **not refutation** — both
auditors worked a single pass on a nine-step pipeline and neither claimed coverage; Codex says
explicitly it did not inspect every gate, and Gemini ran no code at all. But it does mean nine of my
thirteen findings still rest on one reading by one auditor, and it says precisely which ones most need
their falsifier run. B-11 and B-12 are exempt — they are parsed from the IDF, and Codex did not parse
LPD/EPD.

### The two auditors were not of equal value, and the reason is instructive

**Codex found five things and measured four of them.** It streamed a 74 MB CSV, re-summed 56 rows of
`agg_meta.csv` to a residual of 1.46 × 10⁻¹¹ m², quoted the line numbers of the code it was
characterising, and — in the one place its own evidence was ambiguous — said so. Its `magnitude,
honestly` sections repeatedly refuse to infer what it did not measure. Its one real error (C-1
reaching 2J) came from comparing code in one leg to prose in another.

**Gemini found six things and read all six.** Three of them (G-3, G-5, G-6) cite as evidence the very
document that already contains the correction — the finding is that a fixed error was fixed. One
(G-4) reproduces my own B-1 mistake from the same manuscript paragraph, which is what happens when a
claim is traced to a *document* rather than to the *program*. Two (G-1, G-2) are real, and G-2 is the
single most consequential thing either auditor produced.

The pattern is worth writing into the methods paper, because it is the same lesson as §0.21.5 and
this document's own class #11: **document-tracing finds what the documents disagree about;
artefact-tracing finds what the documents never said.** The 2J `(occDensity + 1)` factor is invisible
to any amount of careful reading of the manuscript. It took opening the file.

### Catalogue candidate — class #13, the severity-vacuous gate

C-3 is a mechanism the existing twelve classes do not cover. `_grade_band` is called with
`hard=False` at `Step4_docs/3rdJ_04_augmentationGSS_4split_val.py:1293-1297`; under that flag an
out-of-band non-NaN value returns `warn` no matter how far outside the band it lies (`:1267-1285`,
whose own comments state that no FAIL column applies). RW6's delivered weekday retail rate is 0.0453
against a 0.06–0.10 target — 24.5 % below the floor — and is reported WARN in every cycle. A rate of
0.0000 or 1.0000 would report WARN too.

The distinction from the existing classes: the gate has a real reference, a real discriminator, and a
real measured quantity. It reads a genuine failure and then **declines to call it one**. Class #5
("the gate declared but never coded") never runs; class #13 runs, computes the right answer, and
downgrades it.

Proposed for the canonical catalogue in `3rdJ_L3_step9_READER_GUIDE.md §4`. Note it interacts with
B-5: RW6 is the same retail rate gate B-5 found to be measuring a discarded quantity. B-5 says the
number does not matter downstream; C-3 says that even if it did, the gate could not act on it.

---

# 🔴 B-1 — The residential channel puts the whole household in the room when one person is home

> 🔴 **CORRECTED 2026-08-04 (evening) — falsifier run, mechanism did not survive.** The heading and
> the analysis below are kept, not deleted, per the project's method rule. What is now known:
>
> 1. **The rule is not `HHSIZE × any-member-present`.** Leg-3 Step 7 computes
>    `HHSIZE × mean(member AT_HOME)` — `3rdJ_07_aug_to_bem_4split.py:309`.
> 2. **Intra-household diversity is not zero.** At least **21.38 %** of multi-person households carry
>    non-identical co-resident vectors (3,499 / 16,367, measured; lower bound).
> 3. **The error sign is inverted.** A fractional expectation smooths peaks; this section argued it
>    sharpens them.
> 4. **It does not reach the submitted 2J manuscript.** 2J is a different converter and it *does*
>    implement the per-slot maximum that `readySubmission.md:211` describes.
>
> **What survives, and why the severity is held at 🔴 High:** Step 5 computes the household maximum
> into `HH_hom30_*` (`3rdJ_05_censusLinkage_4split.py:1037`) — the quantity the submitted paper's §3.3
> describes — and **Step 7 never reads it**. The paper's stated aggregation rule and the executed one
> are different rules, and the discrepancy is undocumented. Independently found as **C-1**.
>
> The 2J-facing content of this finding has moved to **B-13**, which is a different defect.
>
> Read everything below as the 2026-08-03 argument, now superseded on mechanism.


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

# ~~🟠 B-11~~ — ⚫ **RETIRED 2026-08-05.** The NECB constants are transcribed, not parsed — ~~**and two of them are wrong**~~

> **Upgraded 🔵 Low → 🟠 Med-high on 2026-08-03.** The check below was run. It found the next Défaut 7.
>
> 🔴🔴 **RETIRED 2026-08-05 by V2-C3 / V2-F8. The density half of this finding was a unit-label error
> in our own documentation, not a defect in the model.** NECB states occupancy as **occupants per
> 1000 ft²**. Office = **3.72 occ/1000 ft²**, and `(1000 / 10.7639) / 3.72 = ` **24.97 m²/person** —
> the value the IDF carries. **The "6.8× gap" this finding reported IS the conversion factor**
> (`25.0 / 3.7 = 6.76`). The two numbers were never in conflict; the doc lost the unit. Verified
> against NECB's own table, `improvements/v2/f8_necb_schedule_evidence/space_types_NECB2011.json`
> (md5 `b2cb54a8`).
>
> **Why it survived three rounds of checking:** both numbers were individually correct, so every
> consistency check passed. **A unit-label error cannot be caught by comparing values** — only by
> asking what each value is denominated in. Logged as a method rule.
>
> **What survives, as a new and smaller finding:** retail runs the **office** density 24.97 where NECB
> gives **3.10 occ/1000 ft² = 29.97 m²/person** for `Retail - sales` — ~20 % over-crowded — and NECB's
> retail **schedule type C** is never loaded (`grep -c "NECB-C-" injected.idf` = 0) → **V2-D9**.
> The blanket-constant observation (occupancy + plug blanket, lighting per-space-type) is **unaffected
> and still stands**, as does its consequence for V2-B1: correcting these cannot move office.

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

### The full internal-gains sweep — completed 2026-08-04, at Step-9 `Q2`'s request

On 2026-08-03 only the `PEOPLE` objects were parsed. `§0.21.4 Q2` asked for the other two — lighting
and equipment power density — as the cheapest thing that could explain the office deficit. Both were
parsed 2026-08-04 from the same two read-only source towers. **The result splits cleanly in half.**

| Internal-gain specification | Office (`OpenOffice`) | Retail | Hotel | Apartment | Per-space-type? |
|---|---|---|---|---|---|
| Occupant density (person/m²) | `0.040015` | `0.040015` | `0.040015` | `0.040015` | ❌ **blanket** |
| Occupancy schedule | `NECB-A-Occupancy` | `NECB-A-Occupancy` | `NECB-A-Occupancy` | `NECB-A-Occupancy` | ❌ **blanket** |
| **Lighting W/m²** | `6.566` | `4.090 / 9.042 / 9.500` | 7 distinct, `4.090 … 11.733` | 4 distinct, `2.906 … 7.965` | ✅ **yes** |
| **Lighting schedule** | `OfficeLarge BLDG_LIGHT_SCH*` | `RetailStandalone BLDG_LIGHT*` | `HotelLarge …` | `ApartmentHighRise …` | ✅ **yes** |
| **Equipment W/m²** | `7.5028` | `7.5028` | `7.5028` | `7.5028` | ❌ **blanket** |
| Equipment schedule | `NECB-A-Electric-Equipment` | same | same | same | ❌ **blanket** |
| OA per person | `5.0 L/s` | `7.5 L/s` | — | — | ✅ yes |
| OA per floor area | `3.048e-4` | `6.096e-4` | — | — | ✅ yes |

Identical in `TallBuilding_…_v242.idf` and `SuperTallBuilding_…_v242.idf`. Every non-zero
`ElectricEquipment` object in both files carries `7.5028 W/m²` across all 17 space-type entries; the
zero-valued rows are plenum and shaft zones. Lighting, by contrast, resolves to **seventeen distinct
W/m² values on four distinct schedule families**.

**This is a much stronger version of the 2026-08-03 proof.** Yesterday's argument was that the file
differentiates retail *ventilation* but not retail *occupancy*. The sweep shows the same author
differentiated retail **lighting** too — four schedule families, retail-specific wattages — and left
occupancy and plug load at one number each. An archetype cannot be said to have *chosen* a single
occupant density and a single plug density while carefully assigning nine different lighting
densities in the same file.

> **The split is not random, and it is worth stating in the paper.** The two fields that *were*
> parameterised are the two NECB regulates by explicit tabulated LPD. The two that were **not** are
> occupancy and plug load — **the two the scientific claim of this project runs through.**

**What the blanket values actually are.** `25.0 m²/person`, `7.5028 W/m²`, and an occupancy curve
peaking at 0.9 with a **midday dip to 0.5** — a lunch trough. All three are office quantities. So the
model does not fail to specify the channels symmetrically; **it specifies every channel as an office**,
and office is the one channel for which that is plausibly correct.

*Not established here:* whether `7.5028` and `0.040015` are the right *office* values. That needs the
NECB 2020 tables opened, and it is the only part of `Q2` still outstanding — item **5e**.

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

# 🟠 B-12 — Every channel runs the same plug load, and the pipeline modulates it

**Raised by Step-9 `§0.21.4 Q2`, not by this audit.** Q2 asked for the power-density half of the IDF
check; this is what it returned. Parsed 2026-08-04, read-only, from both source towers.

### The evidence

Every `ElectricEquipment` object in `TallBuilding_…_v242.idf` and `SuperTallBuilding_…_v242.idf`
carries the same two values:

```
Watts per Floor Area : 7.5028 W/m²        (all 17 space-type entries, both towers)
Schedule Name        : NECB-A-Electric-Equipment   (all of them)
```

Classroom, ClosedOffice, Conference, Corridor, Dining, Elec/MechRoom, Elevator, HighriseApartment,
LargeHotel, Main, OpenOffice, Restroom, Retail — one number, one schedule. The only variation is
zero, on plenum and shaft zones.

The same file assigns **nine distinct lighting densities on four schedule families**
(`OfficeLarge` / `RetailStandalone` / `HotelLarge` / `ApartmentHighRise`). See the sweep table in
B-11.

### Why it matters — and why it is not simply a duplicate of B-11

B-11 is about a *documented* constant being wrong. B-12 is about a constant that was never documented
at all, and it is worse in one specific respect: **the pipeline actively modulates plug load.**

The injector writes `MXU_<Channel>_Load_f200_*` schedules over `ELECTRICEQUIPMENT`, and the T9-9 work
exists precisely because an earlier version of the injector destroyed the **22 % plug standby floor**
by writing the occupancy schedule over the equipment schedule. Step 9 measured that defect, fixed it,
and validated the fix — an entire arm (`A`) was spent on it, moving office EUI `71.08 → 80.03`.

All of that careful work modulates a **base density that is one office number applied to a hotel guest
room, an apartment and a retail sales floor.** A 22 % standby floor on the wrong design level is a
precisely-corrected fraction of a wrong quantity.

Plausibility of the blanket value by channel, as an order-of-magnitude sanity check only — **the NECB
2020 tables have not been opened, and this must not be cited until they are** (item 5e):

| channel | `7.5028 W/m²` is | direction of the likely error |
|---|---|---|
| office | plausible | — |
| retail | high — prototype retail plug loads are typically a fraction of office | retail gains **over**-stated |
| hotel guest room | high | hotel gains **over**-stated |
| apartment | high | residential gains **over**-stated |

Note the sign is **opposite** to B-11's. B-11 under-states retail occupant gains by 6.8×; B-12 plausibly
over-states retail plug gains. **They partially cancel**, which is a further reason the net EUI effect
of correcting the archetype is not derivable on paper and must be measured — item 5c.

### Falsifier

Not needed for *presence* — the constant is read directly from the artefact and is not in dispute. What
needs establishing is *whether it is wrong*, which is item **5e**: open NECB 2020 Table A-8.4.3.2 (or
the 90.1-2019 prototype equivalent the file's `90.1-2019` name implies) and compare the four channel
values. One hour, no compute.

### Recommended action

1. **Do not re-parameterise** ahead of 5e and 5c, for the same reason as B-11: it invalidates every
   Step-8/9 comparison already run.
2. **Fold into item 5c.** If the retail-density sensitivity cell runs, run the plug density in the same
   cell — they act on the same zone through the same mechanism and the campaign cost is identical.
3. **State it as a limitation regardless of the outcome.** "Per-channel plug and occupant loads inherit
   a single archetype value; only lighting is space-type-specific" is a one-sentence limitation that is
   true today and cheap to write. It is also directly relevant to how much of the paper's per-channel
   EUI decomposition should be leaned on.
4. **Re-read the T9-9 result in this light.** The standby-floor fix is still correct and still worth
   having; but its per-channel magnitudes are conditioned on a base density that is uniform across
   channels, and any statement of the form "restoring the plug floor moved the *hotel* channel by X"
   inherits that.

---

# 🟠 B-13 — The submitted 2J converter runs two operations the manuscript never mentions

**Raised 2026-08-04 (evening), while checking whether C-1 reaches the 2J paper. It does not — but
this does.** Neither Codex nor Gemini found it: Codex read Leg-3's converter, Gemini read the
manuscript, and this lives only in the 2J code.

### What the manuscript says

`readySubmission.md:211` (§3.3): households are formed *"taking the per-slot maximum AT_HOME indicator
across household members, so that a slot is classified as occupied if any member is present."*
`:229` (§3.5): *"occupancy (AT_HOME fraction) and metabolic heat gain together load the EnergyPlus
`People` object."*

That is the complete description of the residential occupancy quantity in the submitted paper.

### What the code does

`eSim_occ_utils/21CEN22GSS/21CEN22GSS_HH_aggregation.py:174-178` — the max is genuinely there, and
so is a second channel the paper never names:

```python
presence_binary  = (loc_stack == 1).astype(int)
occupancy_count  = presence_binary.sum(axis=0)
hh_df["occPre"]  = (occupancy_count >= 1).astype(int)      # <- §3.3's maximum. Correct.

dens_stack           = np.vstack([p["ind_density"].values for p in people_grids])
hh_df["occDensity"]  = dens_stack.sum(axis=0)              # <- never mentioned in the paper
```

`eSim_occ_utils/21CEN22GSS/21CEN22GSS_occToBEM.py:144-145`:

```python
estimated_count = hourly["occPre"] * (hourly["occDensity"] + 1)
occupancy_sched = (estimated_count / hh_size).clip(upper=1.0)
```

### The three problems, in order of confidence

**(a) The paper's description is incomplete, and this one is certain.** The delivered schedule is not
the AT_HOME fraction. It is `any-present × (companions + 1) / HHSIZE`, saturated at 1. A reader
reproducing §3.3 and §3.5 as written cannot reproduce the shipped schedules. This needs no falsifier —
the two files say it.

**(b) `occDensity` is a sum of per-member companion counts, which double-counts co-presence.**
`ind_density` is `row["social_sum"]` (`21CEN22GSS_HH_aggregation.py:141`) — the GSS "who were you
with" companion count for **that respondent**. Summing it across household members counts each
co-resident pairing once per member. Two members of the same household at home together each report
the other: `sum = 2`, then `+1` for a single respondent gives an estimated 3 people in a 2-person
household. The `+1` is correct for one respondent and wrong for a household of grids.

This is the one genuinely good news in the finding: **2J is not a zero-diversity model at all.** It
reads real co-presence off the GSS social fields — which is *better* than what B-1 accused it of, and
better than the literature R1 surveyed. The defect is the aggregation of that channel, not its
absence.

**(c) The `.clip(upper=1.0)` silently absorbs (b).** Any household whose estimated present count
exceeds `HHSIZE` is truncated to full occupancy rather than flagged. The clip is exactly where the
over-count of (b) would have shown up as an out-of-range value, and it is doing the job of hiding it.
An over-count that saturates is indistinguishable in the output from a genuinely fully-occupied hour.

### Why it matters

`readySubmission.md` is **submitted**. Problem (a) is a methods-section defect in a paper under
review, of the same kind as C-1's, and it is fixable with a paragraph. Problems (b) and (c) would
bias the residential schedule *upward* — toward saturation — in multi-person households, which is the
opposite of the smoothing B-1's correction identified in Leg-3 and could partly offset it in
cross-leg comparisons.

Note this is the second time in two days that a `.clip()` has turned out to be load-bearing: it is
the same failure shape as class #12 (*the count that is stable while its membership turns over*) —
a saturating transform makes two different states report the same number.

### Falsifier

One pass over the 2J BEM schedule file, no simulation:

1. Count rows where `estimated_count / hh_size > 1.0` before the clip — i.e. how often the clip fires,
   by `HHSIZE`. If it is ~0 %, (b) and (c) are immaterial and only (a) survives.
2. For a sample of multi-person households, compare `occDensity + 1` against `HHSIZE`. If
   `occDensity + 1 ≤ HHSIZE` throughout, the double-count does not bind and (b) is false.
3. Confirm `social_sum`'s definition in the GSS codebook — specifically whether it counts *household*
   companions only or all companions including non-residents. If it includes non-residents, the
   over-count is worse than (b) states and the direction is unchanged.

Cost: minutes, local, one script. **Run this before the 2J manuscript is revised**, since (a)'s
correction should describe whatever (b) turns out to be.

### Recommended action

Whatever (1)–(3) return, §3.5 needs one sentence stating the actual transform. If the clip fires
materially, the limitations section needs a second one. No re-simulation is implied by (a); (b) and
(c) would imply one only if the clip fires often, which step 1 measures.

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
| **7** Injection | `inject_mixed_use()`, Tag-2 dispatch, wiring gate | **Sound.** The hard wiring gate exists *because* Leg-2's silent failure taught it. Four channel products + validator | B-5 (normalisation), **B-11, B-12** |
| **8** Simulation | 112-cell campaign, probes, aggregation | Extensively audited. Défaut 7 was found here | B-8 (doc cleanup), **B-11/B-12 (the archetype the campaign was run on)** |
| **9** End-use loads | T9-9…T9-13, arms A–R | Extensively audited. *Updated 2026-08-04:* arm H closed 56/56, arm R closed and scored; 17P/0W/3F/10I unchanged across both. `§0.21` concludes none of the 3 blocking gates is an occupancy problem | **This audit is now on its critical path** — `§0.21.4 Q2` → B-11/B-12 (answered), `Q8a` → B-1, `Q8b` → B-3 |

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
| **5c** | **One sensitivity cell**, pre-registered: retail density ~3.7 m²/person **and the corrected retail plug density**, vs `Default_NECB` baseline, report ΔEUI. Retail OA would be **2.08×** current; occupant gains 6.8× **up**; plug gains plausibly **down** — three effects, two signs, no derivable net | 1 simulation | **B-11**, **B-12**; bounds every Step-8/9 retail number — **and now bears on the blocking `S9-EUI-retail` gate**, whose two failing cells are short by 0.06 % / 0.23 % | **raised in priority 2026-08-04.** 🔴 Read as exposure, never as a fix — write the prediction first |
| ~~5d~~ | ~~Parse lighting and equipment power density~~ — **DONE 2026-08-04**, at Step-9 `Q2`'s request. Lighting **is** per-space-type; equipment is a blanket `7.5028 W/m²` | — | **new finding B-12**; answers 2 of `Q2`'s 3 parts | it found a third blanket constant |
| **5e** | Open **NECB 2020 / 90.1-2019 prototype tables** and check the four channel values for occupant density and plug density. The only part of Step-9 `Q2` still outstanding | 1 h reading | **B-11**, **B-12** — establishes *whether* the blanket values are wrong, not just that they are blanket | **prerequisite for 5c's magnitudes** |
| **5f** | Correct the two citation defects in the Step-9 documents: `Q8`'s **B-3 ↔ B-1** conflation (split into Q8a/Q8b), and `Q2`'s *"19 % below its floor even uninjected"* (uninjected is **14.55 %**) | 10 min | neither is an audit finding — but both are in the document written for external cold review | new |
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

*Amended 2026-08-04:* items **5d/5e/5f** are new, and **5c is the highest-value simulation in the
document** — it is now the only item that bears on a currently-blocking Step-9 gate. It remains one
cell, not an arm.

## Revised again, 2026-08-04 (evening), after the two blind audits

Item 1 has been **executed**, and it changed the list more than the three literature reports did.
Replaces the table above where they conflict.

| # | Action | Cost | Resolves | Changed by |
|---|---|---|---|---|
| ~~1~~ | ~~B-1 falsifier step 1 — are co-resident vectors identical?~~ — **DONE 2026-08-04. No.** ≥ 21.38 % of multi-person households differ. B-1's mechanism is corrected, its severity held, its 2J reach withdrawn | — | **B-1 corrected**, spawned **B-13** | this was the top item for two days; it took twenty minutes |
| **1a** | **Run the B-13 falsifier** — how often does `.clip(upper=1.0)` fire in the 2J frame, and is `occDensity + 1 > HHSIZE`? | 1 script, minutes | **B-13** — and it is the only finding in this document that reaches a **submitted** paper | new. Inherits item 1's priority |
| **1b** | Decide the Leg-3 aggregation question C-1 opens: should Step 7 read `HH_hom30_*` (the paper's max) or keep the mean? **State which, in writing, with the reason** — the defect is that no one chose | writing, then possibly 1 re-run | **B-1**'s surviving half, **C-1** | new. A deliberate mean is defensible; an accidental one is not |
| **4a** | Re-label RW6's severity, or specify a real FAIL condition. It calls `_grade_band(hard=False)`; an out-of-band value can only WARN | small code | **C-3** / class #13 — and it compounds **B-5** on the same gate | new, from Codex. 🔴 Do **not** widen the band |
| **5g** | **Re-derive the hotel As-Modelled band** from an archetype-matched reference, pre-registered. `dr_L3-03:13` recommends 180–300; its own Table 2 at `:58-68` lists 6 of 11 reference rows above 300, and every Large Hotel row | 2 h reading + writing | **G-2** — and it is the only item here that bears directly on the blocking `S9-EUI-hotel` gate | new, from Gemini. This is Step-9 decision #2/#3, authorised 2026-08-02, still unexecuted |
| **9a** | Persist the Step-4 validation respondent IDs and a run manifest (checkpoint / input / code / rake hashes) alongside the canonical CSV | hours, if the artefacts still exist | **C-5**, and it is a precondition for **11** and for C-2's real gate | new, from Codex. Folds naturally into item 9 |
| **11a** | On the persisted IDs from 9a, run the **row-matched** Leg-2 ↔ Leg-3 regression comparison the REG-1/REG-2 gates claim to be | 1 inference job, no retraining | **C-2** | new, from Codex. Same job as item 11 — do them together |

**What moved to the top.** `1a` and `5g`, for opposite reasons. `1a` because it is the only open
item touching a paper that is already under review, and it is minutes. `5g` because it is the only
item in this document that could unblock a Step-9 gate by desk work — which is precisely the
direction §0.21 said all remaining unblocking work lies in.

**What did not move.** B-3 (item 11) is still the one high finding needing compute, still one
~40-minute job, and it is now the one finding an independent auditor reproduced blind (**C-4**). That
raises its priority relative to everything except `1a`.

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

# Is this document ready? — self-assessment, 2026-08-04

Asked directly, so answered directly. **The document is ready to be read and acted on. It is not ready
to be cited.** Those are different thresholds and the difference is the whole point of the rule this
project runs on.

### Ready — as an instrument

- **Complete.** Twelve findings, each with evidence, file-and-line references, a severity, a stated
  mechanism, a falsifier, and a recommended action. Per-step assessment of Steps 1–9, cross-leg
  inheritance, an explicit *what is NOT wrong* section so settled ground is not re-audited.
- **Correctly prioritised, and the priorities have survived contact.** The revised order of work is
  ordered by evidence-per-cost, not by severity. Three external reports and one IDF parse have already
  moved five findings without breaking the ordering.
- **Its two strongest findings are established.** B-11 and B-12 are read directly from the artefact.
  They do not need a falsifier — the constants are in the file, in both towers, and they are not in
  dispute. B-11 has already been acted on by Step 9.
- **It is being used.** Step-9 `§0.21.4` recruited it into the campaign's critical path, and answering
  its `Q2` closed a question that `§0.21.6` had ranked first among all unblocking actions.
- **It reports against itself.** Findings were downgraded (B-4), re-framed (B-5), mechanism-corrected
  (B-1), and one of its own verification rounds was declared circular (class #9). That is the behaviour
  that makes the rest of it worth reading.

### Not ready — as evidence

🔴 **Ten of twelve falsifiers have not been run.** By this project's own standing rule — *a gate is not
validation until it has been seen failing* — B-1 through B-10 are well-argued claims that have not yet
been measured. The document says so in its own Method section and should keep saying so. Specifically:

| Gap | Cost to close | Why it blocks citation |
|---|---|---|
| **B-1's falsifier step 1** — are co-resident `hom30` vectors actually identical? | **one script, minutes** | This is the finding that reaches the **submitted** 2J manuscript. It is the cheapest item in the document and the highest-stakes. **Nothing else should be written up before this runs** |
| **B-2, B-3, B-9** falsifiers | 1 GPU job + 2 scripts | B-3 is the only one needing real compute |
| **5 of 9 citations still unverified** (items 13a, 13b) | ~3 h reading | ATUS/HETUS midday rates are the *proposed new reference* for a re-specified gate — a gate is only as good as its reference. Andridge & Little returned 403; the 14-row aggregation table is 1/14 spot-checked, and the **0** count is what carries B-1 |
| **5e** — are the blanket office values themselves right? | 1 h, NECB 2020 tables | B-11/B-12 establish the values are *blanket*. Whether they are *wrong* needs the tables |
| **5c** — the retail sensitivity cell | 1 simulation | Converts "we cannot predict the sign" into a number, and it now bears on a blocking gate |

### The honest summary

**Nothing in this document is known to be wrong. Almost nothing in it is yet known to be right** —
which is exactly the state a backward audit should be in one day after it opens, and exactly the state
it must not stay in.

**The single next action is B-1's falsifier step 1.** Minutes of work, it touches a submitted paper,
and it is the one item where continuing to write before measuring would repeat the mistake the audit
was opened to find.

## Re-assessed 2026-08-04 (evening), after running that falsifier

**It was run. The answer was no, and B-1's stated mechanism did not survive it.**

That changes this section more than it changes the finding, so the change is worth stating plainly:

- The line above — *"nothing is known to be wrong"* — **is no longer true, and the thing now known to
  be wrong is this document's own headline finding.** B-1 claimed zero intra-household diversity; at
  least 21.38 % of multi-person households have it. B-1 claimed the defect reaches the submitted 2J
  manuscript; it does not.
- **This is the best outcome the exercise could have had.** A falsifier that only ever confirms is
  class #9 wearing a different hat. The first one run killed a high-severity claim in twenty minutes,
  which is a much stronger argument for the method than another confirmation would have been.
- **And it did not cost the finding.** B-1 stays 🔴 High on a *different, verified* mechanism —
  Step 5 computes the household maximum, Step 7 never reads it — independently found as C-1. The
  audit's *conclusion* was right; its *reason* was wrong. Those are separable, and pretending
  otherwise is how documents become unfalsifiable.

**Revised verdict.** Still ready to act on, still not ready to cite — but the numerator moved:
**three of thirteen findings are now established** (B-11, B-12 from the IDF; B-1's surviving half from
the code), and one is established-as-corrected. Ten remain argued.

Two things also got *harder* to cite, not easier:

- 🔴 **B-13 now reaches the submitted 2J manuscript, and B-1 no longer does.** The stake did not
  disappear when B-1 lost its 2J reach — it moved to a finding with its own unrun falsifier. Item
  **1a** inherits the "nothing else should be written up before this runs" status B-1 held.
- ⚠️ **Nine of thirteen findings were not reproduced by either blind auditor.** Not refutation — the
  coverage was not there — but it identifies exactly which claims are still single-sourced.

**The single next action is now B-13's falsifier**, for the same reason B-1's was: minutes of work,
and it is the only open item touching a paper already under review.

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

### 2026-08-04 — re-read against the Step-9 log, its backup and the new Reader's Guide

Three documents re-analysed against this audit at the user's request:
`improvements/3rdJ_L3_improvements_step9.md`, `..._BACKUP_2026-08-04.md` and
`improvements/3rdJ_L3_step9_READER_GUIDE.md`.

**First, a non-result worth recording:** the log and its backup are **byte-identical**, md5
`40cbba0d8f621e5c59bf845d403aec4d` on both, 7,694 lines each. The backup carries no divergence, so
there was nothing to reconcile between them; all new material is what the log itself gained on
2026-08-04 — `§0.18` (local aggregation), `§0.19`/`§0.20` (arm-R predictions and re-score) and `§0.21`
(the cold-review state-of-play) — plus the Reader's Guide, which is new.

**The relationship between the two documents inverted.** Step 9's `§0.21.4` now recruits this audit
into its own critical path (`Q2` → B-11, `Q8` → a backward-audit item) and `§0.21.6` ranks the IDF
audit **first** among the unblocking actions. Findings written here as a side investigation are now
load-bearing for a blocked campaign.

**What the re-read produced.** Full argument in *Update 2026-08-04* under the verdict table.

1. **Two citation defects in the Step-9 documents** — item 5f. `Q8` states B-1's content under **B-3's
   number**, and the Reader's Guide then answers *"needs simulation? yes — the only one"*, which is
   right for B-3 and wrong for B-1: B-1's surviving falsifier is one script and a paragraph, and it is
   the one that reaches the submitted 2J paper. `Q2` separately quotes **19 %** as the *uninjected*
   office shortfall; the uninjected `Default_NECB` figure is **14.55 %** (85.45 vs a floor of 100), and
   18.7 % is the injected `B_central`. `§0.21.3` has it right; only `Q2` does not.
2. **🔴 Step-9 `Q2` ANSWERED, and against its own premise** — item 5d. Lighting and equipment power
   density parsed from both source towers: **lighting is fully per-space-type** (nine distinct W/m²,
   four schedule families) while **equipment is a blanket `7.5028 W/m²` on all 17 space-type entries**,
   one schedule, both towers. With the 2026-08-03 occupant-density result, the picture is: **two of the
   four internal-gain specifications are parameterised, two are blanket — and the two blanket ones are
   occupancy and plug load, the two the paper's claim runs through.** All three blanket values are
   *office* quantities, so **office is the channel they are plausibly right for.** Correcting them moves
   retail, hotel and residential; it cannot move office. `Q2` therefore resolves **no** — the office
   deficit is not a power-density mis-specification — and `§0.21.3`'s band-applicability conclusion is
   strengthened, having now survived the cheapest available alternative explanation.
3. **New finding B-12** (🟠 Med-high) — the blanket plug density, raised by `Q2` rather than by this
   audit. It is worse than B-11 in one respect: the pipeline **actively modulates** plug load, and an
   entire campaign arm (`A`, office `71.08 → 80.03`) was spent restoring a 22 % standby floor on a base
   density that is one office number applied to hotel rooms, apartments and a sales floor. Its likely
   error sign is **opposite** to B-11's, so the two partially cancel — one more reason the net cannot be
   derived on paper.
4. **Item 5c re-prioritised.** It was written to bound exposure; it now also bears on a **blocking**
   gate. `S9-EUI-retail` FAILs on two `SuperTall__CLG` cells short of the 80.00 floor by 0.23 % and
   0.06 %, and B-11/B-12 move retail internal gains by order 6.8×, not 0.2 %. Three effects with two
   signs (gains ↑, outdoor air ↑, plug ↓) in a heating-dominated climate: undetermined. 🔴 It must be
   pre-registered and read as a measurement of exposure, never as an attempt to make retail pass — and
   for the record against `§0.21.6`, one specification-diagnostic cell is not a ninth arm.
5. **`§0.21.5` independently reproduces this audit's diagnosis at the far end of the pipeline** — the
   gate that does not test the claim (#1 ≡ B-5, class #11), the threshold decided with the answer
   visible (#3 ≡ B-2, B-6), and doc-vs-artefact divergence (`Q7` ≡ B-8, B-10). The audit opened on the
   premise that Steps 1–4 were the un-revisited ones; the same habits ran through the middle of the
   campaign, in the period the project regards as its most rigorous. **That is the better framing for
   the methods paper, and the more honest one.**
6. **Catalogue reconciled.** 12 classes now, not ten. This audit's **#11** has been adopted into the
   canonical numbering; the 2026-08-03 circularity is an instance of the pre-existing **#9**, not a new
   class; **#12** is new from `§0.20.1` and bears on no B-finding.

**Unchanged:** nothing in `§0.18`–`§0.21` touches B-1, B-2, B-3, B-4, B-6, B-7, B-9 or B-10 — arms A–R,
the DHW saga, the K sweep and the hotel plant are all downstream of Step-7 injection. **None of the
original eleven falsifiers has been run.** B-3 remains the only finding needing compute, at one
~40-minute GPU job.

### 2026-08-04 (late) — the two Step-9 citation defects CORRECTED, and a readiness self-assessment added

**Item 5f executed.** Both defects fixed in the live documents, struck in place per the Step-9 log's own
method rule #4 (*struck claims are kept, not deleted*). `..._BACKUP_2026-08-04.md` deliberately left
untouched — it is the frozen snapshot, and editing it would destroy the thing it exists for.

| Where | Was | Now |
|---|---|---|
| `step9.md §0.21.4 Q2` | "office is **19 %** below its floor **even uninjected**" | struck → **14.55 %**, with a boxed correction naming 18.73 % as the *injected* `B_central` figure and 85.45 as the uninjected control |
| `step9.md §0.21.4 Q8` | one question, B-1's content under **B-3's** number, "the only high-severity backward-audit finding still needing compute" | struck → split into **`Q8a` = B-1** (reaches submitted 2J, **no** simulation, one script + a limitations paragraph) and **`Q8b` = B-3** (Leg-3 Step-4 gates only, **yes** — one ~40-min GPU job) |
| `READER_GUIDE §1.4` | same Q8 row, answering *"needs simulation? yes — the only one"* | split into Q8a/Q8b rows; footer now reads *"eight of nine need no simulation"* |
| `READER_GUIDE §1.4 Q2` | open question | struck → **ANSWERED**, with the blanket-vs-parameterised result and the "office is the channel they're right for" consequence |
| `READER_GUIDE §2` | 19 reversals | **21** — rows 20 (the B-1/B-3 fusion) and 21 (the injected-figure-under-uninjected-label) added to the register |

`step9.md §0.21.4 Q2` also received the full answer inline: the four-row sweep table, the
*"correcting them cannot move office"* consequence, the pointer to **B-12** and item **5e**, and the
🔴 note that B-11/B-12 now bear on the blocking `S9-EUI-retail` gate and that item 5c must be
pre-registered and read as exposure, never as a fix.

**Staleness cleared in this document:** header now reads *opened 2026-08-03 / last updated 2026-08-04*
and carries the finding count and the falsifier status up front; the Aim's "ten named classes" annotated
to twelve; the Step-9 row of the step-by-step table updated from *"currently running (arm H, job
1171496)"* to arms A–R closed and scored, and its Open column now records that this audit sits on
Step 9's critical path; B-12 added to the Open column of Steps 7 and 8.

**New section: *Is this document ready?*** — answered plainly, because it was asked plainly. **Ready to
be read and acted on; not ready to be cited.** Complete, correctly prioritised, already load-bearing
for Step 9, and its two strongest findings (B-11, B-12) are established directly from the artefact and
need no falsifier. But **ten of twelve falsifiers have not been run**, and five of nine citations remain
unverified. **Nothing here is known to be wrong; almost nothing here is yet known to be right.**

🔴 **The single next action is B-1's falsifier step 1** — are co-resident `hom30` vectors identical?
One script, minutes, and it is the only finding in the document that reaches an **already-submitted**
manuscript. Writing any of this up before that measurement runs would repeat precisely the habit the
audit was opened to find.

### 2026-08-04 — independent replication commissioned: two blind auditors

Written in direct response to this document's own self-assessment. Ten of twelve falsifiers are unrun,
so most of this audit is argued rather than measured; the cheapest available test of whether its
*framing* missed something is to have the same pipeline audited by people who have never seen it.

Two prompts in `investigationPrompts/`, for **Codex** and **Gemini**, both entering at
`Leg3_4-split/3rdJ_00_4split_Occupancy_Pipeline.md` + `_Overview.md`:

| | Emphasis | Findings numbered |
|---|---|---|
| **Codex** | **Code and artefacts** — read the `.py`, re-derive logged numbers from the data, parse the IDFs, interrogate the validators as programs. Works artefact→prose, the opposite direction from the design docs | `C-1, C-2, …` |
| **Gemini** | **Claims and provenance** — build a register of every load-bearing claim in the design docs, trace each to its source, sweep the corpus for contradiction, check what is inherited across the three legs | `G-1, G-2, …` |

Both carry the same standard of evidence as this document (falsifier per finding, `path:line`
citations, *a citation is not evidence until opened*, *a logged number is not evidence*, clean negatives
count, report plainly what weakens the papers), the same read-only constraints (no cluster, no
EnergyPlus, no retraining, `Leg2_2-split/` frozen), and the same deliverable skeleton. Only the starting
axis differs, so the two sweeps overlap as little as possible — and neither reproduces this audit's.

**Blindness is enforced as a whitelist, not a blacklist**, because the prompts live inside the folder
they must not read: *within `improvements/investigation/`, the only file an auditor may open is its own
prompt.* The prior audit, both READMEs, `deepResearch Prompts/`, and the other auditor's prompt and
report are all off-limits. Two files **outside** that folder are partially contaminated by the
2026-08-04 session — `improvements/3rdJ_L3_improvements_step9.md` (`§0.21.4 Q2`/`Q8a`/`Q8b`) and
`improvements/3rdJ_L3_step9_READER_GUIDE.md` (`§1.4` rows `Q2`/`Q8a`/`Q8b`, `§2` rows 20–21) — so both
prompts name those passages and supply a `grep` that locates them. Each report must open with a filled-in
blindness declaration, and both prompts state explicitly that **admitting an accidental read is better
than hiding it**.

🔴 **The reports are not to be merged into this document on arrival.** The three-way comparison *is* the
result: agreement across all three establishes a finding about as well as desk work can; anything in
`C` or `G` that is absent here is the reason the exercise was run; anything here that neither
reproduces does not refute it, but downgrades confidence and identifies precisely which claims most need
their falsifier run. `B-`, `C-` and `G-` numbering stays separate permanently — renumbering into one
series would destroy the provenance that makes the comparison worth anything.

### 2026-08-04 (evening) — both blind reports returned; B-1 falsified; B-13 raised

**Delivered.** `investigationPrompts/REPORT_codex_backward_audit.md` (C-1 … C-5, code and artefacts)
and `REPORT_gemini_backward_audit.md` (G-1 … G-6, claims and provenance), plus Gemini's working notes
in `investigationPrompts/gemini-docs/`. Both filed clean blindness declarations. Reports **not merged**
— the three-way comparison is in *Update 2026-08-04 (evening)* above, per this folder's rule 4.

**Corroboration (rule 1).** Two findings reproduced blind by an auditor who could not have copied
them: **C-4 ≡ B-3** (RW1/RW2 read teacher-forced numbers from the training log, not the shipped pool)
and **G-1 ≡ B-8** (Défaut 7 fixed the header, the body still says 40,846 / 26,750 — same document,
same lines). B-3 was already the one high finding needing compute; it is now also the one an
independent auditor found without help.

**New, from them (rule 2).** **C-2** REG-1/REG-2 are synthetic-vs-synthetic, not row-matched, and the
validator's own comment says the frozen split was never persisted — an instance of class #9.
**C-3** RW6 calls `_grade_band(hard=False)`, so an out-of-band value can only WARN, never FAIL —
proposed as catalogue class **#13, the severity-vacuous gate**. **C-5** the canonical Step-4 directory
holds no checkpoint and no rake provenance. **G-2** the hotel As-Modelled band `180–300` is
contradicted by Table 2 of `dr_L3-03`, the report that defines it — 6 of 11 reference rows sit above
the ceiling, every PNNL Large Hotel row does, and **300 is the exact number `S9-EUI-hotel` fails
against**. New work items 4a, 5g, 9a, 11a.

**🔴 The main event — B-1 was falsified, by its own falsifier.** Following C-1 into the code and then
into the artefact:

- `3rdJ_05_censusLinkage_4split.py:1037` computes the household maximum into `HH_hom30_*`;
  `3rdJ_07_aug_to_bem_4split.py:309` takes `groupby(...)[HOM].mean()` over the **raw** columns and
  **never reads `HH_hom30_*`**. C-1 confirmed — an independent instance of this audit's own class #11.
- Measured on all 785,616 multi-person rows of `BEM_Schedules_4split_2022.csv`: 21,688 rows (2.76 %)
  carry values outside `{0, 0.5, 1}`, which identical co-resident vectors cannot produce. By household:
  **3,499 / 16,367 = 21.38 %** show proven internal disagreement — a lower bound, since a two-member
  full-hour split reads exactly 0.5. **"Exactly zero intra-household diversity" is false.**
- The **error sign is inverted** from what B-1 and G-4 both argued: a fractional expectation smooths
  peaks, it does not sharpen them.
- **B-1 does not reach the submitted 2J manuscript.** 2J is a different converter
  (`21CEN22GSS_HH_aggregation.py:174-176`) and it *does* implement the per-slot maximum that
  `readySubmission.md:211` describes. C-1's "reaches 2J: yes" is a cross-leg category error; G-4's
  `HHSIZE × AT_HOME` is implemented by no code in either leg and was read from the manuscript alone.
- B-1 stays 🔴 High on the surviving, verified mechanism. Conclusion right, reason wrong; kept in
  place and struck, not deleted.

**New finding B-13, found while checking the above and held by none of the three audits.**
`21CEN22GSS_occToBEM.py:144-145` computes `occPre × (occDensity + 1)`, then `.clip(upper=1.0)`.
Neither operation appears in the submitted manuscript. `occDensity` is a **sum of per-member GSS
companion counts**, which double-counts co-resident co-presence (two members at home together give
`sum=2`, `+1` → 3 people in a 2-person household), and the clip is precisely where that over-count
would have surfaced. Good news inside it: **2J is not a zero-diversity model** — it reads real
co-presence off the GSS social fields, which is better than B-1 accused it of and better than the
literature R1 surveyed. Falsifier: count how often the clip fires, by `HHSIZE`. Minutes, local.

**Method note, for the paper.** Codex measured four of its five findings and erred once, by comparing
code in one leg to prose in another. Gemini read all six, and three (G-3, G-5, G-6) cite as evidence
the very document that already contains the correction — a fixed error, refound. G-4 reproduced this
audit's own B-1 error from the same manuscript paragraph. The generalisable lesson, and it is the same
one as class #11 and §0.21.5: **document-tracing finds what the documents disagree about;
artefact-tracing finds what the documents never said.** The `(occDensity + 1)` factor is invisible to
any amount of careful reading — it took opening the file.

**Status:** 13 findings. Three established (B-11, B-12 from the IDF; B-1's surviving half from the
code), one established-as-corrected, ten still argued. **The next action is B-13's falsifier** — it
inherits B-1's status as the only open item touching a paper already under review.

### 2026-08-04 (night) — G-3, G-5, G-6 closed as verified-no-action (V2-C10)

Three of Gemini's six findings — **G-3** (StatCan hotel table), **G-5** (4-head vs 3-head), **G-6**
(Service/MEP prorating) — cite as evidence the very document that already contains the correction.
They are not defects; recorded here once, with the line opened and checked before writing this entry,
so nobody re-audits them.

- **G-3** — `Pipeline.md:425`: "Verified in [dr_L3-01_statcan_hotel_data_REPORT.md] that Table
  24-10-0048-01 does not exist. No Statistics Canada table provides monthly occupancy rates, ADR, or
  RevPAR by province. Sourced instead from Tourisme Québec / ISQ ... and Travel Alberta / Alberta
  Economic Dashboard...". The non-existence finding and the re-sourcing G-3 asks for are both already
  there. **Verified — no action.**
- **G-5** — `Pipeline.md:226`: "**Heads count, resolved.** The graphical abstract and spec §10 say
  '4 output heads'; spec §3.5 defines **3 GSS heads**. **§3.5 is authoritative: three GSS heads + a
  non-GSS hotel side-track.**"; and `_Overview.md:74`: "\"4 heads\" in the PNG = diagram shorthand;
  3 GSS heads is authoritative". Both sites already carry the resolution G-5 asks for, and agree with
  each other. **Verified — no action.**
- **G-6** — `Pipeline.md:325`: "**Service/MEP (~52 % gross):** prorated by area onto the four tenant
  channels (floor area plus core lighting / elevators / circulation ventilation) whenever comparing to
  SCIEU-style stock EUIs...". The prorating *rule* is stated, so G-6's citation is not itself a defect.
  **Only half self-refuting**: the **52 % share** quoted at that same site is independently wrong —
  the file's own French comparison table (`Pipeline.md:32`) gives measured shares of **20,64 %** and
  **21,41 %** against the quoted *"~52 % du brut"* — and is being corrected separately as **V2-C2**.
  The rule was never missing; the number it is applied to was. **Verified — the rule-statement half is
  no-action; the share-value half stays open under V2-C2.**

No further action on G-3 or G-5.
