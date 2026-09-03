# 4J — drafted write-up passages (`I-6`)

**Created** 2026-08-21 · **Origin** `IMP/2026-08-21_review-derived-improvements.md` §6, box 8
**Status** drafted, ready to drop into the manuscript when the manuscript exists

🔴 **There is no manuscript file yet** — `writing/` holds only the two figure prompts and their
rendered PNGs. These passages are written here so they are not lost and so box 8 is closable; they
are **drafts of paragraphs, not an outline of the paper**, and each names exactly where it belongs.

🔴 **Provenance firewall (`IMP` §0-bis) applies to every line below.** Everything here is either a
defect found in our own code (category A) or public, independently re-derived literature
(category B). Nothing is taken from the confidential manuscript, and nothing under
`4J_docs_occ/extra/` may be referenced from any of it.

---

## 1. TUS lineage — for Related Work

**The gap.** Paper 1 reported a high-order Markov baseline at 0.691 against our 0.98. That is the
right *family* to compare against, and we never said which family it was. Two review articles cover
the whole time-use-survey-to-occupancy-model lineage in one citation each:

* Osman & Ouf (2021), `10.1016/j.buildenv.2021.107785`
* Vosoughkhosravi, Dixon-Grasso & Jafari (2023), `10.1016/j.enbuild.2023.113245`

**Draft:**

> Occupancy models built from national time-use surveys form a continuous lineage from the
> first-order inhomogeneous Markov chains of Richardson et al. (2008) and Widén and Wäckelgård
> (2010), through the higher-order and semi-Markov variants that followed, to the survey-conditioned
> statistical models reviewed by Osman and Ouf (2021) and Vosoughkhosravi et al. (2023). The
> baseline reported in our earlier work sits in this family. We retain a first-order inhomogeneous
> Markov chain, fitted per fold on the N−1 training countries, as a comparator throughout, and we
> report its margin alongside the raked-donor null rather than in place of it.

⚪ **What the comparator actually shows, and it is worth one sentence in Results**: fitted on `es`
and `uk` and scored against `it`, the chain reproduces the *transition rate* almost exactly
(0.264 transitions/day error, well inside the 1.50 band) and misses the *dwell-time distribution* by
an order of magnitude (W1 119.6 min against a 10.0 min band). Matching a rate while missing the
distribution is the characteristic first-order failure, and it is the single clearest argument for
scoring dwell times at all.

---

## 2. Day bases — a limitation that turns into a contribution

**Verified from the BLS ATUS User's Guide directly, not from a search response:** ATUS oversamples
weekends *by design* — roughly 10 % of the sample on each weekday and 25 % on each weekend day — and
**repairs that imbalance inside the weight**, `TUFINLWGT` (day allocation p. 13; weight
construction p. 37).

**Our own measurement, `FINDING 53`:** the three countries' diary weights target **three different
day bases**, all exactly — `uk` 71.45 / 14.32 / 14.24 (the calendar week), `es` 50 / 25 / 25,
`it` 33 / 33 / 33. **Only the UK is calendar-representative.** Left alone this moves at-home time by
`es` +0.95 pp, `it` +1.30 pp, `uk` −0.003 pp — a **country-correlated** shift on a leave-one-
country-out design, which is the worst possible shape for it to have.

**Draft:**

> Time-use surveys differ in how they allocate diary days, and in whether the supplied weights
> repair that allocation. The American Time Use Survey oversamples weekend days by design and
> corrects for it within its final weight. The three HETUS-derived files used here do not: their
> diary weights target three different day bases, and only one of the three is representative of the
> calendar week. Because the discrepancy is a property of the country, it is confounded with the
> leave-one-country-out split, and we therefore re-base every diary onto the calendar week before
> any statistic is computed (`weight_dia_cal`). We report the size of the correction rather than
> only its existence.

🔴 **One check is still owed before this is submitted:** the Eurostat HETUS 2018/2020 methodological
guidelines have **not** been read directly on the question of day allocation. `RL17` A6 searched
them for a margin-of-error table and returned `NOT FOUND`; that is a different question. Until the
guidelines are read, the paragraph may state what **our three files** do — which is measured — and
must not state what **HETUS as a framework** requires.

---

## 3. Joint fidelity, stated honestly

`RP03`: fine-tuning shifts conditional probabilities toward the empirical distribution but does
**not** certify the joint. Our own `FINDING 63` is that exact failure mode, caught in our own
pipeline: after a marginal re-label, 1,512 employed Italian 13-year-olds were generated off a single
donor diary — the marginal was right and the joint was wrong, because IPF takes each row's shape
from the seed.

**Draft:**

> Conditioning a generative model on demographic marginals does not certify the joint distribution
> those marginals came from. We report a case from our own pipeline: a correction that repaired a
> marginal left the corresponding joint badly wrong, and it was detected only because the joint was
> inspected directly. We therefore score quantities that were never in the prompt — dwell-time
> distributions, transition matrices and co-presence cross-tabulations, conditioned on attribute
> pairs — and treat marginal agreement as a precondition rather than as evidence.

⚪ This is evidence that we inspect joints, not only marginals. It reads as a strength, and it is
one, but it is stated as a defect we found in our own work.

---

## 4. The tier-naming pass — what is the reference, and is it derived from the thing being scored?

Applied to each gate. The outcome is **one rename-free clarification list**, not a renaming:

| Gate | What it is called | What it actually measures | Action |
|---|---|---|---|
| `G5.1` | marginal fit | **convergence of IPF onto its own targets** — not fidelity to anything external | say "convergence" in the text; the gate keeps its name |
| `G5.8` | temperature calibration reported | a *reporting* obligation plus a *sensitivity* obligation; neither is a fidelity threshold | describe as a reporting gate |
| `G6.1` | margin over the raked-donor null | a comparison of two candidates' distance to a **third, external** reference | see the paragraph below |
| `G6.4` | budgets vs published tables | fidelity to an external published source — the one place the word is unqualified | keep |
| `G6.14` | hour-support constancy | a **completeness invariant of the binning**, not of the model | already stated in its own row |

---

## 5. `G6.1` is not circular — the paragraph that says why

The objection is real and someone will make it: the raked-donor null is raked onto **the same
published marginals the model was conditioned on**, so null and model share a reference. That looks
circular. It is not, and the reason is worth one explicit paragraph rather than a rename.

**Draft:**

> The raked-donor null is constructed on the same published marginals supplied to the model: the
> same geography, the same strata, the same tables. This is deliberate. The comparison is not
> between a candidate and its own reference — it is between two candidates' distance to a third
> reference that neither produced, published by the national statistical offices before either was
> built. Giving the null a different or weaker set of marginals would not make the test more
> demanding; it would convert a null into a handicap, and any margin it produced would measure the
> handicap. The construction is enforced in code: the comparison refuses to run if the two sides
> carry different marginal sources, and the margin test is strict, so a null scored against itself
> yields exactly zero and fails.

⚪ **Checked, and it closes an item `IMP` §7 left owed:** we never divide one divergence by another
anywhere. Every margin in the codebase is a **difference** (`score_margin` returns
`null_value − model_value`), every divergence is a JSD **in bits** and therefore bounded, and no
"superiority multiplier" or divergence ratio appears in any of our documents. The `epsilon`
pathology — where moving a smoothing floor from 1e-4 to 1e-15 moves a reported ratio from 461× to
1727× — cannot reach a bounded difference.

---

## 6. What must NOT be written

* 🔴 **Never "reproducible"** about the generation runs. `RP05`: bit-exactness additionally requires
  `batch_size=1`, deterministic algorithms, `CUBLAS_WORKSPACE_CONFIG` and a **fixed GPU
  architecture**; Speed schedules across nodes. The permitted claim is **"pinned base revision +
  pinned adapter + recorded sampling seeds"**.
* 🔴 **Never "the two temperature criteria agree."** They agree on **one fold of three**: `uk`
  (1.10 vs 1.00). On `es` they are six grid steps apart and on `it` four, and the chosen value rests
  on entropy matching alone. `es`'s chosen temperature is additionally **at the grid endpoint**, and
  the grid was not extended to chase it.
* 🔴 **Never quote `G6.8` as evidence against modal collapse.** Measured: a modal-collapse control
  passes its transitions arm, because a modal day is a real day. Collapse is Tier 2's job.
* 🔴 **Never cite a project-chosen threshold to the literature.** `G6.14`'s support invariant, the
  dwell-time W1 band, the transition bands and the diurnal JSD bands are all **project-chosen**.
* 🔴 **Never say `G6.8` cleared its bands at cell level without saying which basis.** At attribute-
  pair granularity the absolute Tier 1 bands are below the finite-sample noise floor — a second real
  sample fails 65 of 68 cells — so per-cell verdicts are taken on the registered sample-size-matched
  real-real floor, and the absolute bands are enforced at population level.
* 🔴 **Nothing from `4J_docs_occ/extra/` may be cited, paraphrased or alluded to** until and unless
  that manuscript is published. ⚪ This is unchanged by the decision to cite BuildOcc — see the
  BuildOcc section at the end: we cite the **public Zenodo software record**, never the reviewed
  manuscript, and citing is not adopting.

---

## BuildOcc — the reference we will give, and the two things that are NOT the same object

**Author instruction, 2026-08-21:** cite this work and support it. Recorded here with the one
distinction that has to survive into the bibliography, because getting it wrong is a confidentiality
breach and a `FINDING 47`-class citation error at the same time.

### 🟢 The software IS public today and can be cited immediately

The platform is openly released, independently of the manuscript, with its own DOI:

> Jung, W. **BuildOcc** [software]. Zenodo. https://doi.org/10.5281/zenodo.21192895 —
> Apache License 2.0, `pip install buildocc`.

This is a **public artefact**. Citing it breaches nothing, needs no permission, and does not depend
on any editorial decision. **This is the citation to use now**, and it is the one that carries the
thing we would actually be pointing readers at: a working, installable implementation.

### ⚪ The SoftwareX article is NOT yet citable, and the journal name in the instruction was wrong

* Journal is **SoftwareX** (Elsevier), *Original software publication*. 🔴 **Not "Energies"** —
  *Energies* is a different (MDPI) journal and is not involved anywhere in this work.
* Status: **`SOFTX-D-26-00798R1`, revised manuscript under review**, preprint submitted 2026-08-12.
  It has **no volume, no issue, no pages and no article DOI**, because it has not been accepted.
* `FINDING 47` is the reason this matters: our own `G9.4` requires a citation to match
  **volume / issue / pages / first author**, after an `RL17` "CrossRef-verified" DOI turned out to
  resolve to an unrelated paper. A manuscript number is **not** any of those fields. Writing
  "SoftwareX, in press" or inventing a placeholder would be exactly the defect `G9.4` exists to catch.

**So:** cite the Zenodo software record now; **add or swap in the SoftwareX article the moment it is
published**, with the real volume/pages resolved through CrossRef like every other citation. Until
then the article reference stays in this notes file and does not enter a manuscript file.

### 🔴 What "support this paper" may and may not mean in our text

**May:** cite the public software, describe what it does from its **public** record (Zenodo page,
README, the released code), and position our work alongside it — both ground an LLM in a national
time-use survey; BuildOcc uses **ATUS** (US, 16,684 respondents) and an agent/memory architecture,
we use **HETUS** (ES/UK/IT) and a fine-tuned sequence model under leave-one-country-out. That
contrast is a genuine and useful paragraph, and it is drawn entirely from public material.

**May not** — and this does not loosen because we now intend to cite it:

* 🔴 **The reviewed manuscript text stays confidential.** No sentence, number, figure, design choice
  or limitation may be taken, paraphrased or alluded to from `4J_docs_occ/extra/`. Citing a paper
  and **adopting** its unpublished design are different acts; the provenance firewall (IMP §0-bis,
  category C) blocks the second and always did. The bullet above this section still stands.
* 🔴 **Never reveal that we reviewed it.** No "as a reviewer", no reference to the review, the
  revision round, the manuscript number, or anything in `extra/`. A normal citation of a public
  Zenodo record is indistinguishable from any other citation, which is precisely why it is the safe
  route.
* 🔴 **Do not describe it in terms our own review contradicted.** Whatever we write about it must be
  something we would write having only read the public release — that is both the honest standard
  and the test that keeps the two roles separate.

⚪ **Ownership — CLOSED by the author, 2026-08-21.** The work is **not ours**. It is a third
party's (sole author Wooyoung Jung, University of Arizona), and that is precisely *why* it gets a
reference rather than a mention: we owe a citation to someone else's contribution, we claim no part
of it, and nothing in our pipeline is presented as derived from it. The `IMP/2026-08-21_review-
derived-improvements.md` items are ours — category **A** (our own code defects, found by us) and
category **B** (public literature). 🔴 **Category C — that manuscript's unpublished design — was
adopted nowhere, which is the whole point of the §0-bis firewall, and "we cite it" must never be
allowed to drift into "we took something from it".**

⚪ **The `Energies` half of the instruction is recorded as a slip, not a second paper.** The
instruction said "SoftwareX-Energies"; the venue is **SoftwareX** alone. If a separate *Energies*
paper was ever meant, it is not in `extra/`, nothing here covers it, and it needs its own entry.

---

## 7. `D-S11-1` directive 2 — the denominator-incompatibility passages (DRAFTED 2026-08-27)

🔴 **This section discharges directive 2 of `D-S11-1` §8.** It is drafted manuscript text, not a
record: the four passages below are meant to be lifted into Methods (7.1), Results (7.2),
Limitations (7.3) and a figure/caption rule (7.4). ⚪ **No band, threshold, verdict or count is
moved by anything here** — every number is quoted from an artefact that already carries it, and each
passage names where it came from so the sentence can be re-derived rather than trusted.

⚪ Sources drawn on: `Step11_docs/docs/2026-08-27_work-item-11.2_G9.7-diagnosis.md` (`FINDING 163`–
`166` and the §8 ruling), `Step10_docs/docs/2026-08-27_OpenUBEM-response-intake_S3-basis-and-
population.md` §3 / §3.1 / §5 (`FINDING 169`–`172`), `Step4_docs/4thJ_04_finetuneLLM.md`
(the two Leg-5 comparison arms).

---

### 7.1 Methods — the DHW denominator, stated once, where the model is described

> Domestic hot-water demand is emitted from the four-event tapping model of Jordan and Vajen
> (IEA SHC Task 26), whose Table 1 specifies a total of **200 litres per dwelling-day** for a
> one-family house, distributed over four categories — short load 28 L, medium load 72 L, bath
> 20 L, shower 80 L (portions 0.14 / 0.36 / 0.10 / 0.40). The source assigns **no temperature to
> any volume**; it states that "for the cold water temperature distribution during the year, a local
> profile should be used", and the only temperature it gives is a 35 K rise inside a worked
> maximum-energy example. The volume is therefore emitted **per dwelling and unweighted by
> temperature**, and it is held constant with respect to household size, because a per-occupant
> scaling is not present in the source and would be ours.
>
> The pre-registered acceptance band for this quantity — **30–50 litres per person-day at 60 °C** —
> comes from a different work: the review of Fuentes, Arce and Salom (2018), *Renewable and
> Sustainable Energy Reviews* **81**, 1530–1547. A per-person review band and an unscaled
> per-dwelling emission do not share a denominator, and the ratio between them is exactly the
> household size. We report this comparison as a **denominator incompatibility** rather than as a
> model failure, and the band is left exactly as pre-registered.

⚪ **Two things this paragraph must keep.** (i) Both papers are named, with their bases attached —
the single-sentence compression of `RL13` row 15 into "the Jordan and Vajen model … at roughly 30 to
50 L/person/day at 60 °C" is the citation collapse that produced the defect (`FINDING 163`), and the
manuscript must not repeat it. (ii) The phrase *"would be ours"* is doing work: it records that the
constant volume is a **ruling** (`D-S9-2` item 5 (a)), not an oversight.

🔴 **Unverified, and it must stay flagged until someone reads the paper.** Fuentes et al. (2018) has
**not been fetched**; its 30–50 L/person-day at 60 °C is taken from a Tier-2 deep-research row, and
`FINDING 47` holds that such a value is unvetted until confirmed at the source. ⚪ The *bibliographic*
record is verified (CrossRef, `FINDING 167`: no issue field — `RL13`'s `81(1)` was the January
part of the print date). **Verified reference ≠ verified content**, and the manuscript may not
imply the second from the first.

---

### 7.2 Results — how the number itself is reported, with the verdict withdrawn and the deviation kept

> The emitted volumes correspond to population medians of **100.16 (ES), 117.65 (UK) and
> 91.06 (IT) litres per person-day**, against a pre-registered band of 30–50. The scored quantity is
> arithmetically `200 ÷ n_members` — over all 300 rows the largest difference between the reported
> per-person volume and this identity is 0.0005 L, i.e. rounding — so the check measures **household
> size**, not hot-water demand: landing inside the band would require mean households of
> **4.00 to 6.67 people**, where the corpus median is **2.0**. The check is therefore reported as a
> diagnostic and carries no pass/fail verdict; the deviation is reported in full.

🔴 **Why the verdict is withdrawn and the numbers are not.** A verdict asserts that the two sides
were comparable; the medians assert only what was emitted. The ruling withdrew the first and kept
the second, and the manuscript must do the same — *reporting the deviation is the point of the
classification, not an exception to it.*

⚪ **A sentence available if a reviewer asks whether temperature explains it.** *"Granting a
temperature assignment the source does not make — the two low-volume categories at 60 °C and bath
and shower at 40 °C, with a 10 °C inlet — the conversion is ×0.800, which moves the Spanish median
from 100.16 to 80.12 and leaves it outside the band. The discrepancy is not a temperature-basis
error."* 🔴 It is offered **only** as a refutation of that hypothesis; it must never be written as
though the project adopted those temperatures.

---

### 7.3 Limitations — four paragraphs that must appear together

**(a) Denominator incompatibility, and what it cost.** As above: the DHW check compares a per-person
band with a per-dwelling model and is reported as a diagnostic. 🔴 **The honest half that is easy to
omit:** the same check was the pipeline's only detector of a hot-water **scale** mutation, so
classifying it as diagnostic removed a detector as well as a verdict. A replacement arm was declared
in its place, scoring the stock mean litres per **dwelling**-day against the emitter's own
200 L/day ±10 % — a scale/regression arm, explicitly **not** an external validation.

**(b) The simulated end-use basis is heating-only, and the models carry two end uses.** 🔴 **Standing
rule: the pooled 66.8677 kWh/m², the min 29.5663 / median 80.3233 / max 222.2945 and the
FR 55.4141 / ES 87.2000 split may not appear in any sentence, table or caption without the words
"heating-only".** The site total of 93.768 kWh/m² is likewise **not** a whole-building EUI: an object
census of a promoted model finds no `Lights`, no `ElectricEquipment`, no `WaterUse*`, no `People` and
no cooling coil, and heating plus interior-equipment electricity account for 100 % of the total
(residual 0.02 kWh over 10.67 GWh). **The models contain exactly two end uses.** Consequently **no
TABULA comparison, no national-EUI comparison and no stock-level energy projection is drawn from
them anywhere in this paper**, and none may be added later without changing the models rather than
the wording.

**(c) The dwelling-level population is 26, and it is a ceiling.** Per-dwelling statistics over the
simulated corpus are bounded by **26 dwellings in 12 buildings**; the remaining buildings are
massing-only. This is below the 30-per-fold minimum the dwelling-level checks were registered
against — the same shape as the stock-side layout population (9 / 5 / 3 against 30). 🔴 **A check can
be green and empty**, and both of these are known empty for the same underlying reason: the layout
contract, not attribute coverage.

**(d) At the zero-sensitivity rung the electricity series is flat by construction.** Across 381
emitted gain series (8,760 hourly values each) every value is exactly 3 W/m² — ≈ 26.3 kWh/m²·yr of
perfectly flat electricity with **zero occupancy signal**. 🔴 **A null occupancy effect on
electricity found at that rung would be an artefact of the input, not a result**, and this paper
draws no such conclusion. Every reported electricity series states its sensitivity level; the
zero rung is never used as the occupancy baseline for an electricity claim. ⚪ Heating, where every
simulated figure quoted in this paper lives, is unaffected.

**(e) Both backbone/capacity comparison arms are single-fold.** The full fine-tune and the
alternative-backbone arm were each run on **one** held-out country (ES) rather than the full
leave-one-country-out rotation. 🔴 **Only their verdicts are comparable, not their band values:** the
worst-band figure of the reference arm (1.568) differs from the full fine-tune's (1.508) by 0.060 and
from the alternative backbone's (1.539) by 0.029, where the single-fold sampling-noise floor for that
country is **0.529** — an order of magnitude larger in both cases — so no ranking may be read from
either difference. What the arms support is the
**negative** statement that the registered band failure is repaired by **neither** more trainable
capacity **nor** a different pre-trained backbone. ⚪ Truncation was measured only on the later arm
(0.0247 % train / 0.0543 % validation, both far under the 1 % contamination bar); the earlier arms
carry **no** measured rate, and equal truncation across arms must not be claimed.

---

### 7.4 The caption and cross-reference rule

🔴 Three tokens may not travel without their qualifier, in any caption, table header or cross
reference: **"heating-only"** on every simulated EUI; **the sensitivity level** on every electricity
series; and **"diagnostic"** — never "passed" or "within band" — on the DHW per-person quantity.
⚪ And a fourth, for correspondence rather than the manuscript: a check ID quoted across a tree
boundary must carry its date, because an ID is exactly the token that goes stale silently
(`FINDING 170` — a letter named a gate by an ID that had been renumbered the same day).

---

### 7.5 What this passage set does NOT do

⚪ It authors **no result**, moves **no band**, and closes **no open item other than directive 2**.
⚪ It does not verify Fuentes et al. (2018); §7.1's flag stands until someone reads the paper.
⚪ It does not reconcile the two archetype populations (102 × 5 = 510 in the European-locations
specification, 88 × 5 = 440 in this pipeline's own injected campaign) — they are different campaigns,
they differ by 14 archetypes, and any figure carried between them must cross that difference
deliberately. ⚪ It adds no manuscript **file**: these are drafted passages in the notes, and the
manuscript itself remains unwritten.

---

## 8. `D-S6-16` (a′) — how the memorisation ceiling is reported (RULED (a′) 2026-08-28)

🟢 **Status.** `D-S6-16` is **RULED (a′)** as of 2026-08-28, the author having delegated the
choice; `IMP/docs/DONE/2026-08-24_D-S6-16_the-ceiling-alarmed-and-may-not-be-a-ceiling.md` §9 carries the
ruling. **(c′) — a body-randomised ceiling, a full 7 B retrain — is declined.** The release question was
never this decision's to settle: it was settled by the registered bar, and `G6.10` **FAILS** it. The
passages below were drafted under (a′) and are now the ruled text — they stand unchanged, and ruling
(a′) neither adds to nor removes from them. 🔴 The ruling moves no threshold, re-scores nothing and
removes no control.

⚪ Sources: `IMP/docs/DONE/2026-08-24_D-S6-16_the-ceiling-alarmed-and-may-not-be-a-ceiling.md` §3 and its
third addendum §8; `Step6_docs/outputs_step6/privacy_audit.md`; `FINDING 112`–`116`.

---

### 8.1 Methods — the control, and what it turned out to measure

> Memorisation was probed with a pre-registered permuted-shard control: an adapter trained on the
> same corpus with the prefix–body pairing destroyed by a derangement (seed `614614`, 73,254 records
> re-paired, zero fixed points), so that nothing generalisable connects a prompt to its diary. Its
> membership-inference AUC was intended as an upper bound on what the reported adapter could have
> memorised.
>
> **Measured, it does not behave as a ceiling of the reported model; it behaves as a property of the
> backbone.** Across the three leave-one-country-out folds at 1.48 B capacity the control returns
> **0.5488, 0.5484 and 0.5466** — a standard deviation of **0.001137**, while the reported AUCs over
> the same folds differ by an order of magnitude more. At 7 B the same control returns **0.6496**,
> **+0.102** above that mean and **89.4×** its between-fold spread. The instrument is therefore
> constant across folds at fixed capacity and strongly responsive to capacity: it discriminates
> backbones, not folds, and it is reported as such.
>
> The comparison it was to license also has no declared tolerance. The standard error of the
> AUC difference at *n* = 2,000 is 0.0128, so the alarms recorded on the pilot folds sit at
> **z = 0.40, 1.16 and 0.12** — inside noise in every case. **No release decision rests on this
> control.** It is reported with its four runs, its z-values and both of the corrections above, and
> it licenses and refuses nothing.

🔴 **Two guards this paragraph carries.** (i) The control is **not removed** from the paper. It was
built, run and found not to do what it was designed to do, and that is a result; deleting a control
after seeing its result is the move this project refuses everywhere else. (ii) The tolerance is
quoted **to explain the alarms, never to re-score them** — adding the tolerance and re-scoring is
option (b), which was declined precisely because it sets a threshold after seeing the number it would
decide.

---

### 8.2 Results and limitations — what actually decided the release

> The release decision is made by the registered bars on the governing run (job `1286976`, Leg 5,
> `Olmo-3-1025-7B`, held-out fold `it`), and **two of the four registered controls fail**:
> `G6.10` = **0.6645** against a pre-registered ≤ 0.65 (z = 1.70 over the bar, on a standard error of
> 0.00852) and the perplexity-gap control = **0.0570** against ≤ 0.05. `G6.11` (0.5594 ≤ 0.75) and
> `G6.12` (0 exact matches over 103 rare records) pass, and the untuned-base floor is clean at
> **0.4886** — which is what makes the 0.6645 readable as membership signal rather than an artefact
> of the split. **Under the pre-registration's own terms this is a refusal: the weights are not
> released.** The `uk` synthetic set is withheld with them; the `es` and `it` sets ship.

🔴 **Three sentences the write-up must not lose.**
**(a)** Never *"the privacy audit passed"* and never *"four of four"* — it ships **two registered
FAILs and one partial** (`G6.13` is 2 PASS / 1 FAIL, on `uk`).
**(b)** The perplexity gap is **not** a second independent confirmation of `G6.10`: it fails for the
**permuted** adapter too, at 0.0511 (`FINDING 116`), so on this corpus at three epochs it measures
train/test overfit of the diary *language*, not membership of the pairing.
**(c)** The Leg-5 coverage clause reads FAIL **for vacuity, not for want of a demonstration** — the
baseline already fails, and the same two injections do fell `G6.10` on all three Leg-4 folds, so the
gate is demonstrated.

⚪ **The limitation, in one sentence.** *The upper bound this design intended to supply was not
obtained: the control that was to provide it is insensitive to the fold and sensitive to the
backbone, so the memorisation claim rests on the registered attacks and their floor alone, and a
ceiling that would genuinely force memorisation — bodies randomised rather than re-paired — was
specified and not built.*

---

### 8.3 The `FINDING 112` sentence, and why it may not be generalised

> On every run the permuted control reaches a training loss indistinguishable from the reported
> model's — last-20-step means differ by −0.0029, +0.0190, +0.0165 and **+0.0045** (z = 0.23 at 7 B).
> At 1.48 B this supported reading the control as a model that learned the diary *language* without
> memorising pairings. **At 7 B that reading fails**: the control reaches an AUC of 0.6496, so it
> memorises substantially while its aggregate loss stays indistinguishable.

🔴 **So the inference is withdrawn for Leg 5 and stands for Leg 4, and the write-up must say which.**
An aggregate loss that matches is **not** evidence that a model did not memorise — that is the
generalisable lesson and it belongs in the methods, not only in the decision record.

⚪ Equally withdrawn: the Leg-4-only reading that `D-S6-14` had been acting as *"an unregistered bar
at ≈ 0.548, 82 % tighter than the registered ≤ 0.65"*. On Leg 5 the implicit bar is 0.6496, which is
**above** the registered one. Quote it as Leg-4-only or not at all.

---

### 8.4 What this passage set does NOT do

⚪ It did not itself rule `D-S6-16` — the ruling (a′) is in the decision record, §9, and these
passages are what it ruled **into** the methods.
⚪ It moves no threshold, re-scores nothing, and removes no control.
⚪ It does not build the body-randomised ceiling, and it does not claim the four registered controls
pass — two of them do not.
⚪ It creates no manuscript **file**: these are drafted passages in the notes, exactly as §7 is.

---

## 9. No-core regime — a limitation for the write-up (added 2026-09-03, `D-IMP-1`)

🔴 **No circulation zone is modelled.** The owner's no-core ruling (`D-EU-79`/`80`/`81` on the OpenUBEM
side, applied to Step 8's IMP plan via `D-IMP-1`) removes the unconditioned stairwell/corridor core
from every dwelling subdivision: a floor plate divides into dwellings only, no core, corridor, access
band or unconditioned zone; every square metre belongs to a flat; one flat = one zone.

**Consequence, stated plainly:** every square metre of every simulated floor plate is conditioned
dwelling. The thermal buffering action a real building's stairwell/corridor core would provide between
neighbouring flats — and the reduced conditioned floor area a core would otherwise subtract — is absent
from the model. Heating demand under no-core is not directly comparable to a core-modelled campaign; it
is a declared simplification, reported as such, not concealed.

**Literature range, cited as literature only:** unconditioned circulation cores are commonly sized at
**6-12 % of gross floor area** in the residential UBEM/TABULA literature synthesised in `DR02`
(floor-to-unit division and staircase buffer methods) and `DR03` (thermal zoning resolution). This range
is **never** to be read as a district-level or per-building number for this project — it is the
literature's own figure, cited to show the order of magnitude of what the no-core simplification omits,
not a correction applied to any result.

See `IMP/docs/2026-09-03_nocore-pipeline-review-improvements.md` I-1, and the SUPERSEDED markers in
`Step8_docs/IMP_step8/4thJ_08_bemSimulation_IMP.md`, `Step8_docs/IMP_step8/outputs/floor_layout_generation_report.md`
and `Step8_docs/IMP_step8/outputs/step8_master_results_dossier.md:217` for the retired core-era plan
this limitation replaces.
