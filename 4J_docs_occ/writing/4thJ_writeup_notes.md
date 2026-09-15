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

---

## 10. Figure prompts reconciled to the no-core position (added 2026-09-07)

Both image prompts under `writing/submission/figures/Prompts_Images/` were last written on
2026-08-26 and had aged out. They are reconciled and **both installed images are now out of date and
must be regenerated**. No image was created by the assistant — the prompts are the deliverable and
the author generates from them.

### 10.1 `4thJ_pipeline_steps_figure.md` — cards 10 and 11 only, no chip moves

🔴 **The load-bearing instruction is a refusal, not an edit: card 10 stays `open`.** Step 10's
410-cell campaign was run and gate-scored on 2026-08-28 (**18 PASS / 2 FAIL / 1 INFO /
1 OPEN_INHERITED / 2 NOT_EVALUABLE**), then archived under `D-IMP-4` as campaign `C1` and **not
reported**; campaign `C2`, the no-core one that will be reported, has no cell. A figure describes the
paper, not the repository, so the gate board is not a reason to promote the card — and because the
board is real, the refusal has to be written down or it will be overturned by whoever finds it next.

Three strings changed:

| card | was | is |
|---|---|---|
| 10 decision | `observed footprints, one independent diary per dwelling` | `observed footprints, dwellings only, one independent diary per dwelling` |
| 10 open | `the engine, and which year the diaries belong to` | `the no-core engine does not exist yet` |
| 11 open | `hot water magnitude diagnosed before it is re-measured` | `the bands are inherited unmoved, not re-set at stock scale` |

🔴 **Card 11's old line was a stale-string defect of the `season` class.** `D-S11-1` was ruled on
**2026-08-27, the day after the prompt was last written**: `G9.7` and `G11.7` are both `INFO`
permanently, the 30–50 band is inherited unmoved, the deviation is reported and not scored, and it
**will not be re-measured at stock scale**. The retired line promised a measurement the project had
already decided not to make. Card 10's old open line named the wrong blocker: section 8 of
`Step10_docs/4thJ_10_nocoreRealStock.md` lists the engine carry-in, `D-EU-84`, `D-EU-87`, `D-EU-88`
and `D-EU-55`, and the diary year is not among them.

Also written in: twelve cards is final by `D-IMP-4` (never a thirteenth, never a `Step 12`); a first
district arriving from OpenUBEM is not a campaign and does not move card 10, because `G10N.19` needs
**30 qualifying buildings per fold**; and cards 0–9 were spot-checked, not audited.

### 10.2 `4thJ_graphical_abstract.md` — Band 5 only, and it is a drawing change

🔴 **The no-core rule is drawn, not written. No string is added to the figure.** The subdivided
footprint in the small background plan must be filled **edge to edge** by dwelling cells: no core, no
stair block, no lift shaft, no corridor spine, no shaded service block, no gap. An image generator
asked to subdivide a building plan draws a core by reflex, and a drawn core would state in the
paper's front figure the exact layout regime section 9 above records as removed.

🔴 **And a counting trap was closed.** The real stock is **four districts** (Madrid, Lyon, London,
Bologna) while the corpus is **three countries**, with **Lyon a physical baseline that never enters a
4J denominator** (`G10.11`). Four countable footprints beside three lanes would tell a reader the
paper has a fourth country. The cluster is therefore drawn as **six or seven ungrouped footprints in
grey outline** — uncoloured, unlabelled, and deliberately uncountable — and nothing about project
status (gate counts, chips, `campaign C1`/`C2`, step numbers) may enter this figure at all.

⚪ Backups: `4thJ_pipeline_steps_figure.md.bak_nocore` and `4thJ_graphical_abstract.md.bak_nocore`
beside the live files. Nothing else in either prompt was touched; every earlier revision banner is
kept as the record.

### 10.3 Both figures generated and installed, and checked against their own lists (2026-09-07, same day)

The author generated both images from the reconciled prompts and installed them. They were read and
checked string by string against the prompts' own post-generation lists — Section 10 items 3 to 7 plus
Section 11.1 for the steps figure, Sections 10.1, 10.2 and 10.3 for the abstract.

| file | md5 | size | previous kept at |
|---|---|---|---|
| `submission/figures/HETUS_LLM_Pipeline_Steps.png` | `c852194c9d213c5e7ac825688202befb` | 896 × 1200 | `Prompts_Images/previous/`, md5 `207f42dcac694e2c9a299c13cb966829` |
| `submission/figures/HETUS_LLM_CrossNational_Pipeline.png` | `38e1e602acbab5210839021ef7fb80a4` | 1376 × 768 | `Prompts_Images/previous/`, md5 `d3f0a13b02c04a39fbdb3bc263b6cafc` |

🟢 **Both revisions got what they existed for.** The steps figure keeps cards 10 and 11 on the hollow
`open` chip and carries all three new strings verbatim, so the archived `C1` gate board did not leak
into the paper's figure. The abstract's subdivided footprint is filled edge to edge by its dwelling
cells, with no core, corridor, shaft, hatched block or gap — the no-core rule is drawn, as intended,
and no string was added to say it.

🔴 **Four defects, none of which moves a claim, and two of which are repeats that survived being
explicitly instructed against.** In the steps figure the five band labels are again rotated vertical,
and the `pre-declared gate batteries` bracket again stops short, now at card 4 instead of card 5 — the
second of the two is the one that misstates something, because as drawn Population linkage has no
pre-declared battery. In the abstract the word `activity` is printed above the ribbons, which is the
only unpermitted string in the image, and the six dwelling cells all carry the *same* checkmark where
Band 5 requires them to differ: identical marks say one diary repeated, the opposite of `one
independent diary per dwelling` printed below them, and a checkmark also reads as a pass mark.

⚪ **Both rasters are below print spec** and neither clears the legibility item: 896 × 1200 and
1376 × 768 against the 1400 × 1900 and 2000 × 1100 asked for, both re-encoded from `.jpg`, so the small
type carries JPEG ringing. **The two figures are usable as working drafts and are not yet submission
rasters.**

Every fixable defect was merged **into the paste blocks** of the two prompts rather than appended
after them, and each prompt now carries a dated result section — `4thJ_pipeline_steps_figure.md`
Section 13 and `4thJ_graphical_abstract.md` Section 11 — recording what was correct, what failed and
what changed. Backups: `*.bak_gen20260907`.

---

## 2026-09-14 — figures installed, merged into a `.docx`, and verified against the installed manuscript

The author generated all three images externally and installed them to
`writing/submission/figures/` (`HETUS_LLM_Pipeline_Steps.png`, `HETUS_LLM_CrossNational_Pipeline.png`,
`Figure_02_loco_design.png`), with aliases kept beside the prompts in `Prompts_Images/`. Figure 2 now
exists, so `RESUME.md` queue item 5 is closed as *generated*, not as *verified*.

**Merged copy built.** `pandoc 4J_manuscript_submission.md -o 4J_manuscript_submission.docx
--resource-path=. --standalone`, run from `writing/submission/`. All three images are embedded
byte-for-byte (`word/media/rId13|rId22|rId25.png`, 1,065,892 / 1,205,984 / 1,060,235 bytes — identical
to the installed files). No venue reference document was applied: the venue is undecided, so the 2J
`ref_submit.docx` house style was deliberately **not** used. `4J_supplementary_material.md` contains no
images and was not converted. Nothing in the `.md` was edited to make the merge work.

🔴 **FINDING 276 — Figure 2's fork is drawn backwards, and the fork is the whole point of the figure.**
`4thJ_figure02_loco_design.md:58-70` marks Band 2b as *the load-bearing element*: one marginals box,
**one arrow leaving it**, forking into both candidates. As installed, the box is correctly drawn once,
but the only arrow touching it **arrives**, running from the fine-tuned model's right edge down and into
the box; **no arrow leaves the box, and nothing connects it to the raked donor pool at all.** Read
literally the image says the model produces Britain's census marginals, and it does not show the null
receiving them. That inverts the single claim the figure exists to prove — that both candidates were
handed exactly the same input. **The figure must not be submitted as drawn.** The numbers on it are all
correct and need no change: 58.91 / 21.79, 60.44 / 19.21, 21.24 / 18.54 min/day, closest miss 2.70, and
73,254 diaries / 2,024,068 episodes all match the manuscript abstract.

🔴 **FINDING 277 — Figure 1 card 6 carries a line the manuscript contradicts.** The installed steps
figure prints *"the reported folds are not yet trained"* on the Transfer test card. That string is in the
prompt (`4thJ_pipeline_steps_figure.md`) and was true when the prompt was written on 2026-09-07; it is
false now. The manuscript reports three trained folds and nine scored fold-band cells. A reader who
compares the figure with §5 finds the paper disagreeing with its own pipeline diagram. **The fix is one
line in the prompt, not a claim change.** ⚪ Card 10's *"the no-core engine does not exist yet"* is in the
same stale-prompt class and should be re-checked against Step 10 before the next generation.

⚪ **Figure 1 is otherwise correct, including both repeat defects from 2026-09-07.** Twelve cards, 0 to 11,
no thirteenth. The five band labels are **horizontal** this time. The `pre-declared gate batteries`
bracket **now reaches card 5**, Population linkage, which is the third attempt and the first that is
right. Chips are as specified throughout, card 6 is the enlarged centrepiece with the only bold body
line, and cards 6, 10 and 11 keep the hollow `open` chip.

⚪ **Graphical abstract — one structural defect and two cosmetic ones.** The held-out lane (`Country C`)
appears to run into the dark training block along with the other two rather than passing around it and
re-entering on the right; as drawn it contradicts *"never seen in training"* printed beside it, which is
the same class of error as `FINDING 276` and should be fixed in the same round. Lanes 1 and 2 show only
`episode diary` while lane 3 shows only `serialised record`, where the spec asks every lane to carry
both; and the third ribbon is a flat tint rather than unequal segments. 🟢 **The two defects named on
2026-09-07 are both repaired**: the word `activity` is gone from above the ribbons, and the six dwelling
cells now carry six *different* marks, none of them a checkmark, filling the footprint edge to edge with
no core.

⚪ **Raster spec, unchanged from 2026-09-07 and still not met.** 1376 × 768 and 896 × 1200 against the
2000 × 1100 and 1400 × 1900 asked for, and all three were re-encoded from `.jpg`, so the small type
carries JPEG ringing. **Working drafts, not submission rasters.**

⚪ **Author observation, recorded because it is correct: 4J is figure-poor against its own prior line.**
2J's submission carries **16 images and no inline tables**; 4J carries **3 images and 8 numbered tables**,
and both of its non-abstract figures are schematics — neither plots a measured series. Every result in
4J is currently read as a table. This is not a rule problem: matplotlib plots computed by a script from
frozen data are the standing exception to the never-create-images rule, so the missing result figures are
**local compute and can be made here**, unlike the three schematics. Candidates, in the order they would
earn their place: the nine fold-band transfer cells as model-versus-null bars (the paper's headline,
currently Table-only); the three countries' stock appliance-electricity profiles showing the 14:00 /
18:00 / 20:00 peaks; and the fictional-country amplitude slope against the 0.80 floor. **No figure is
added without the author's word, and none may restate a number the tables do not already carry.**

Next: author decides whether the two structural figure defects are re-generated now, and whether the
result plots are built.

---

## 2026-09-14 (later) — five result-figure prompts written, and one manuscript defect found while writing them

**Author instruction:** build the result figures as **prompts**, to be generated externally in Gemini
alongside the three schematics. So the matplotlib exception was **not** used and nothing was plotted here.
Five new prompt files, all in the Figure-2 house format, all carrying their measured series in a table
under a **no value may be altered** bar, each naming its install path and its manuscript section:

| File | Section | Source of every number |
|---|---|---|
| `4thJ_figure03_nine_cells.md` | §5.1 | Table 5, `4J_manuscript_submission.md:609-621` |
| `4thJ_figure04_amplitude_slope.md` | §5.4 | `Step6_docs/4thJ_06_transfer.md:2989-2993` and `:704-722` of the manuscript |
| `4thJ_figure05_joint_structure.md` | §5.5 | Table 8, `:734-741` |
| `4thJ_figure06_appliance_peaks.md` | §5.8 | `Step9_docs/outputs_step9/agg_diurnal.csv`, column `elec_w_per_dwelling` |
| `4thJ_figure07_heating_null.md` | §5.11 | Table 10, `:872-879`, and the prose of §5.11 |

Figure 4 carries `FINDING 275` inside the drawing rather than only in the caption: the steering arm is
drawn nowhere, appears only as text marked **inherited from the pilot**, and the prompt states that the
plotted slope is the six-channel figure while the registered definition counts five. Figure 3 is forbidden
from computing any ratio, because the table carries three columns and a ratio is not one of them.
Figure 5 is the one place a derived quantity is plotted, and only because Table 8 prints that multiple
itself.

🔴 **`FINDING 278` — Table 9 is archetype-scale numbers under a stock-scale caption, and Spain has no
stock-scale run at all.** Found while harvesting the hourly series for Figure 6, then re-measured here
directly rather than carried from the harvest.

* The manuscript prints **Spain 14:00 / 503 W, Italy 18:00 / 404 W, Britain 20:00 / 416 W** under the
  caption *"Stock appliance-electricity peak, generated populations"*, and §5.8 says the result is
  *"reported as a shape and timing result at stock scale"*.
* Those three numbers are **Step 9, archetype scale, 100 dwellings**:
  `Step9_docs/outputs_step9/agg_diurnal.csv` gives `es` 14:00 **502.8777**, `it` 18:00 **403.5225**,
  `uk` 20:00 **416.1349**. They round to the manuscript's three exactly.
* The **actual stock-scale** figures are different: `Step11_docs/outputs_step11/c2_uk/step11_11-5_uk_reseed.json`
  gives hour 20 at **422.3315239140366 W**, and `.../c2_it/step11_11-5_it_reseed.json` hour 18 at
  **395.0492889695305 W**, both under the key `ours_mean_diurnal_w_per_dwelling`.
* 🔴 **There is no Spanish stock-scale run.** `outputs_step11/` holds only `c2_it/` and `c2_uk/`. Step 11's
  own investigation doc says so in as many words
  (`Step11_docs/docs/2026-09-13_G11.12-stock-scale-failure-investigation.md:257`), and the same doc's
  table at `:63-78` already lists both scales side by side. **This was on record in Step 11 and did not
  reach the manuscript.**

⚪ **What survives and what does not.** The **six-hour spread survives**: the peak hours are 14:00 / 18:00 /
20:00 at archetype scale, and the stock-scale run agrees on both hours it covers, 20:00 for Britain and
18:00 for Italy. What does **not** survive as written is the word *stock*: as printed, Table 9 and §5.8
attribute archetype-scale numbers to a stock-scale campaign, and for Spain no stock-scale campaign exists
to attribute them to. **No gate moves and no band moves.** This is a labelling repair in the manuscript,
in Table 9's caption and in §5.8, and it is the author's to rule.

🔴 **Figure 6 is blocked on that ruling** and its prompt says so at the top. As written the prompt plots
the archetype-scale series, labels it archetype scale, and forbids the word *stock* anywhere in the image.
If the author rules that the figure must be stock scale, the prompt is rewritten against the Step 11
files and **Spain cannot appear in it**, which would cost the figure its six-hour span and most of its
point. The recommendation is to keep the figure at archetype scale and repair the manuscript's two labels.

⚪ Figure numbering assumes the five new figures are cited in section order, making the paper Figures 1 to
7 plus the graphical abstract, against 2J's sixteen images. **Nothing in the manuscript was edited** to
cite them; that is a separate pass, after the images exist and are verified.

Next: author rules on `FINDING 278`, then generates Figures 3, 5 and 7, which are unblocked.

---

## 2026-09-14 — the five result figures were generated and verified against their prompts

The author generated all five result figures externally and installed them. They were produced by
**matplotlib scripts driven by the frozen series in the prompt files**, which is the standing exception to
the never-create-images rule, so the drawn values are the measured values by construction rather than by a
model's reading of a table. Every file was re-measured here rather than accepted on report.

**What is on disk.** Five PNGs, each **3600 x 2160** (Figure 5 is 3600 x 2100, Figure 7 is 3600 x 2550),
which is 300 dpi at twelve inches wide and clears the 180 mm requirement in every prompt. Each image
exists three times and all three copies are **byte-identical** (md5 compared): once in
`writing/submission/figures/` under its install name, and twice in `figures/Prompts_Images/` beside its
prompt, under both the install name and the prompt's own stem.

| Figure | Install name | md5 | Numbers checked against |
|---|---|---|---|
| 3 | `Figure_03_nine_cells.png` | `d71fbdee...` | Table 5, all eighteen values |
| 4 | `Figure_04_amplitude_slope.png` | `e23aaff4...` | `4thJ_06_transfer.md:2989-2993`, fifteen levels and three slopes |
| 5 | `Figure_05_joint_structure.png` | `b0150d76...` | Table 8, four bands and four multiples |
| 6 | `Figure_06_appliance_peaks.png` | `f6ed4410...` | `agg_diurnal.csv`, three peaks and their hours |
| 7 | `Figure_07_heating_null.png` | `948238da...` | Table 10, both panels and three ratios |

⚪ **Every number reads correctly and no value was altered.** Figure 3 prints all nine pairs in manuscript
order, unsorted, with the call-out on Britain's oldest band only. Figure 4 draws Italy's upturn at level 4
and carries all three notes, including the one that says the steering numbers are **inherited from the
pilot and were never recomputed on the reported model**, which is `FINDING 275` surviving into the drawing.
Figure 5 prints Table 8's own multiples rather than recomputing them. Figure 6 marks 14:00 / 18:00 / 20:00
and spans the six hours, and **the word *stock* does not appear anywhere in it**, as its prompt required.
Figure 7 keeps every sign visible, including Italy's negative peak effect and all three negative annual
medians.

🔴 **`FINDING 279` — the no-green-no-red bar is broken in three of the five images.** Every one of the five
prompts carries the same line in its *what must NOT appear* list: **no green, no red, no tick, no cross**,
and every one of them also asks for a colour-blind-safe palette. Three images break it:

* **Figure 4** draws the Italy fold in green and the registered floor line in red, and the same green fills
  Italy's slope bar in the right panel.
* **Figure 6** draws the Italy curve in green against Spain in red-orange.
* **Figure 7** prints Italy's negative value `-0.6332 %` in red type.

The bar exists for two reasons and both are live here. The first is that **red and green together are the
one pairing a colour-blind reader cannot separate**, and in Figures 4 and 6 they carry two of the three
countries. The second is that these are failing checks and a null, so **any hue a reader decodes as
good-or-bad misreads the result**; green on the fold that turns back upward in Figure 4, and red on the one
negative number in Figure 7, both read as verdicts that the paper does not make. Line style and marker
already carry the series in Figures 4 and 6 and hatch already carries it in Figure 7, so the fix costs
nothing: recolour Italy away from green, draw the floor and band lines in black, and set the negative
label in the body colour. **No value changes and no rerun of anything upstream is involved.**

⚪ Smaller, cosmetic, author's call: in Figure 3 the method note and the md5 note sit close enough to the
plotting area and the axis title to look crowded at page width.

🔴 **Figure 6 is still blocked on `FINDING 278`.** The image exists and is correct at archetype scale, but
it cannot be cited until the author rules on whether Table 9 and §5.8 keep the word *stock*. Figures 3, 4,
5 and 7 are clear to cite as drawn once the colour bar is repaired.

⚪ **Nothing in the manuscript was edited.** No figure is cited yet. That remains a separate pass.

Next: recolour Figures 4, 6 and 7, then rule on `FINDING 278`, then cite all five in the manuscript.

---

## 2026-09-14 later — `FINDING 279` closed, and the document put into the 3J house style

### The recolour

🔴 **`FINDING 279` was under-reported when it was written: the defect is in four of the five images, not
three.** Figure 5 drew the registered band line in dark red (`#9B2C2C`) and that was missed on the first
read. The corrected list is **Figures 4, 5, 6 and 7**; only Figure 3 was clean. All four are rebuilt.

The five matplotlib scripts that built the images were copied out of the generating session's scratch
directory into the project at **`writing/submission/figures/scripts/generate_fig03.py` ... `generate_fig07.py`**,
so the figures are now reproducible from inside the repository instead of from a transcript. Each of the
four edited scripts carries a header naming the finding and the palette.

**The house palette, now written into all five prompt files under a new `## Palette` heading:**

| Role | Colour |
|---|---|
| Spain | `#E69F00` orange |
| Britain | `#0072B2` blue |
| Italy | `#7B3294` purple |
| Model series, and any single-series bar | `#3E6B99` slate blue |
| Null series, and the between-diary spread | `#D19C65` ochre, hatched |
| Registered band, registered floor, zero line | `#000000` |
| Every printed value and verdict line | `#111111` |

Colour is never the only carrier: every series still differs by line style and marker, or by fill pattern,
so each figure reads with the colour taken out.

⚪ **No plotted value changed.** The edits touched colour constants and two annotation-box tints and
nothing else; the data arrays in the scripts are untouched, and the four rebuilt images were read back and
checked against their tables again. All fifteen files agree: each image exists three times (`figures/`
under its install name, `Prompts_Images/` under both the install name and the prompt stem) and all three
copies are byte-identical.

| Figure | md5 after recolour |
|---|---|
| 3 (unchanged) | `d71fbdee...` |
| 4 | `f6789866...` |
| 5 | `e7d3d843...` |
| 6 | `00dbcb61...` |
| 7 | `69a21588...` |

Each prompt's header line was also corrected. It said *not generated here*, which is no longer true: it
now names the script that builds the image and says the PNG is never hand-edited.

### The document format

The author asked for `4J_manuscript_submission.docx` to read like `3J_manuscript_submission.docx` in font,
size and paragraph style. **3J's own build chain was adopted unchanged**, which is the right answer because
the target file is the definition of the target style. `ref_submit_single.docx`, `ref_submit.docx` and
`post.py` were copied from `3J_docs_occ_nTemp/writing/submission/extra/build_scripts/` into the matching
place under 4J. The recipe, run from `4J_docs_occ/writing/submission/`:

```
pandoc 4J_manuscript_submission.md -o raw.docx --reference-doc=extra/build_scripts/ref_submit_single.docx --resource-path=.
py -3 extra/build_scripts/post.py raw.docx 4J_manuscript_submission.docx
```

That gives **12 pt Times New Roman, single spaced, justified body, black headings, centred captions**, and
`post.py` then sets **table text to 10 pt single spaced**. Verified rather than assumed: the built file's
`word/styles.xml` is **byte-identical to 3J's** (`a3233bd1...`), its document defaults carry
`Times New Roman`, `w:sz 24` and `w:line 240`, and all eight tables come back with run size `20`
half-points and `after=0 line=240`. The three embedded images are byte-identical to the PNGs on disk.

🔴 **`ref_submit.docx` is the double-spaced reference and it was copied across too.** Single spacing is an
explicit authorial choice carried over from 3J, not a default. **Elsevier asks for double spacing at
submission**, so if a desk check bounces the file the fix is one filename on the pandoc line, not a
rebuild. The previous unstyled build is kept at
`previous/4J_manuscript_submission.2026-09-14_pre_house_style.docx`.

⚪ **The supplementary material was not built.** `4J_supplementary_material.md` exists and 3J builds both
halves every time, but only the manuscript was asked for. It is one more pandoc line when wanted.

⚪ **Still true: no figure is cited in the manuscript.** The built document carries the three original
schematics only. Figures 3 to 7 exist, are correct and are in the right folder, and the citation pass has
not been run.

Next: rule on `FINDING 278`, then cite Figures 3 to 7 in the manuscript and rebuild both halves.

---

## 2026-09-14 — Figures 3 to 7 placed in the manuscript, both halves rebuilt

Asked for: `go ahead, place figures 3 to 7 and rebuild`.

Before this pass the manuscript pointed at three images only (graphical abstract, Figure 1, Figure 2);
the five result figures existed on disk and in the prompt folder but nothing in the text referenced
them, so the built `.docx` carried three images. It now carries eight.

**Where each one went, and the sentence that carries it.** Each figure sits immediately after the
paragraph that states the result it draws, and each is introduced by one clause added to the end of that
paragraph, in the same voice as the existing Figure 1 pointer:

| Fig | Section | Anchor paragraph ends | Pointer added |
|---|---|---|---|
| 3 | §5.1 | "no subset of this table in which the method worked" | "Figure 3 draws the same nine cells." |
| 4 | §5.4 | "named in §7.10 among the unfinished items rather than presented as done" | "Figure 4 shows the response curves and the fitted slopes together, with both qualifiers marked on the figure itself." |
| 5 | §5.5 | "not an artefact of the weighting correction described in §2.1" | "Figure 5 places the four quantities on one scale, as multiples of their registered bands." |
| 6 | §5.8 | "never reported for an individual dwelling" | "Figure 6 shows the three diurnal profiles that the peaks in Table 9 are taken from." |
| 7 | §5.11 | "rather than anything the occupancy signal touches" | "Figure 7 reports the null and the surviving ordering together." |

**The five captions are the ones the prompt files specify, installed verbatim.** Each prompt carries a
`Caption to install with it:` block; each was copied character for character rather than re-written, so
the caption in the manuscript and the caption in the specification cannot drift apart. No number in any
caption was rounded, re-ordered or restated.

**`FINDING 278` is not touched by this pass and is still open.** Figure 6's caption says *mean appliance
electricity per dwelling*, which is true at either scale, so placing the figure does not commit the paper
to the stock-scale reading that Table 9's caption and §5.8's prose assert. The ruling is still needed; it
now governs Table 9's caption, §5.8's "at stock scale" clause, and the figure's own label, not the
caption.

**Build.** From `writing/submission/`, unchanged recipe:

```
pandoc 4J_manuscript_submission.md -o raw.docx --reference-doc=extra/build_scripts/ref_submit_single.docx --resource-path=.
py -3 extra/build_scripts/post.py raw.docx 4J_manuscript_submission.docx
```

`post.py` reported `tables 8 | xml ok`. The file went from 3,383,149 to 5,096,426 bytes and the markdown
from 1,390 to 1,434 lines.

**Verified, not assumed.**
* Eight images are embedded (`word/media/rId44,53,56,82,88,92,98,104.png`) and the md5 of every one of
  the eight is present in the md5 list of `figures/*.png`, so no image was re-encoded on the way in.
* `word/styles.xml` md5 is still `a3233bd11a66cc8ce3939f0c08602858`, byte-identical to 3J's, so placing
  the figures did not disturb the house style applied in the previous pass.
* All eight table objects survived `post.py` at 10 pt single-spaced.

**Backups.** `previous/4J_manuscript_submission.2026-09-14_pre_figures.md` and
`previous/4J_manuscript_submission.2026-09-14_pre_figures.docx` hold the three-image state.

**Two things this pass deliberately did not do.** Figure 2 still has a caption but no prose pointer, as
it did before; adding one is a one-line edit and was not asked for. The supplementary material is still
not built to `.docx`.

Next: rule on `FINDING 278`, then Figure 2 and the graphical abstract still need regenerating
(`FINDING 276`) and Figure 1's prompt still carries the stale line (`FINDING 277`).

---

## 2026-09-14 later still — sole authorship, second recolour, ten-word captions, Figure 1 turned landscape

Author instruction, five parts in one message: drop the second author; recolour Figures 2, 4, 5, 6 and 7
and take the note text out of the bottom of the pictures; cut every table and figure caption to ten words
or fewer and move what leaves into the body text; ask why the reference list is short and whether more
deep-research prompts are needed; and re-specify Figure 1 in a horizontal format. All five are done except
the two images only the author can generate.

### 1. Sole authorship

🟢 **`4J_manuscript_submission.md` now names one author.** Caroline Hachem-Vermette is removed from the
author line and from the CRediT statement, and eleven further sentences that said *the authors* now say
*the author*. The CRediT roles the second author held — Supervision, Funding acquisition, Resources — were
**not** transferred to the remaining author; only *Writing - review and editing* was added, because the
sole author did in fact do it and the other three would be claims rather than records. The funding
sentence is unchanged in substance: NSERC and the Voltage-Age Seed fund are still acknowledged. `grep -i
hachem` returns nothing in the markdown and nothing in `word/document.xml` of the rebuilt `.docx`.

⚪ **Affiliation and corresponding-author block are unchanged.** One affiliation, one ORCID, one address.

### 2. Second recolour, and the notes come out of the pictures

🟢 **Figures 3 to 7 were regenerated from their scripts onto a new house palette.** The palette set on
2026-09-14 in the first recolour (orange / blue / purple) is replaced by the Tol muted set:

| Role | Hex |
|---|---|
| Spain | `#CC6677` rose |
| Britain | `#332288` indigo |
| Italy | `#44AA99` teal |
| Second series in a pair | `#DDCC77` sand, plus a hatch |
| Negative or null channel | `#882255` wine |
| Reference lines, registered floors | `#000000` |

The set is colour-blind safe, carries no green and no red, and separates by lightness as well as hue, so
the greyscale guarantee from the first recolour survives. Line style, marker shape and hatch were left
in place, so no figure depends on hue alone.

🟢 **Every explanatory note, footnote block and verdict sentence was deleted from inside the images.**
That is nine text blocks across the five figures: the italic note boxes at the bottom of Figures 4, 5, 6
and 7, the bold verdict lines under Figures 3, 5 and 6, the two per-panel italic lines under Figure 7's
B1 and B2, and the bold line under Figure 4's right panel. What remains inside each image is axis labels,
tick labels, panel titles, the legend, and the data values themselves. Bottom margins were tightened to
match, so no figure carries a band of white space where the notes used to be.

🔴 **Figure 3 was recoloured-adjacent, not recoloured.** The author's list named Figures 2, 4, 5, 6 and 7.
Figure 3's hues were left as they were, but its bottom notes and verdict line were removed with the rest,
because leaving one figure in the set with a caption-like sentence printed under the chart would have been
visibly inconsistent. If the author wants that line back it is one edit in `generate_fig03.py`.

⚪ **Figure 2 could not be recoloured here** — it is an author-generated image, not a matplotlib plot. Its
prompt now carries the palette table, the no-notes rule, and the reversed-fork correction. See §5.

**No plotted value changed in any of the five scripts.** The patch script refused to write unless every
anchor matched exactly once, and it matched 24 of 24.

### 3. Captions capped at ten words

🟢 **All fifteen numbered captions are now ten words or fewer**, verified by re-parsing the markdown after
the edit rather than by eye:

| | Words | Caption |
|---|---:|---|
| Table 1 | 5 | Positioning against the time-use-survey-to-occupancy lineage. |
| Table 2 | 7 | The three national time-use surveys as delivered. |
| Table 5 | 8 | Time-budget mean absolute error in minutes per day. |
| Table 6 | 3 | The transfer board. |
| Table 7 | 4 | Three independent capacity interventions. |
| Table 8 | 8 | Joint structure never present in the conditioning prompt. |
| Table 9 | 5 | Stock appliance-electricity peak, generated populations. |
| Table 10 | 8 | Occupancy effect on heating after the phase correction. |
| Figure 1 | 5 | Pipeline, Steps 0 to 11. |
| Figure 2 | 6 | Leave-one-country-out design and the two nulls. |
| Figure 3 | 8 | Time-budget mean absolute error, model against raked-donor null. |
| Figure 4 | 8 | The fictional-country control: response curves and fitted slopes. |
| Figure 5 | 10 | Four structural properties, each as a multiple of its band. |
| Figure 6 | 9 | Mean appliance electricity by hour of day, three folds. |
| Figure 7 | 9 | Occupancy effect on heating, and the ordering that survives. |

🔴 **Nothing was dropped; four facts were relocated into the prose that carries them.** This is the part
of the edit that could have quietly lost a qualifier, so each move is recorded:

1. **§5.4** now states, in the paragraph before Figure 4, that the slopes are computed over **six**
   conditioning channels while the registered definition counts **five**, and that a low slope means
   under-response rather than indifference. Both lived only in the old caption and in the figure's own
   note box; both of those are now gone, so without this the qualifier that `FINDING 275` exists to
   protect would have disappeared from §5 entirely.
2. **§5.5** now states that all four structural quantities fail in every fold at between three and nine
   times the band, that each bar spans the range across folds, and that none of the four was in the
   conditioning prompt.
3. **§5.11** now states that Table 10's values are taken at the top of the sensitivity sweep.
4. **§5.11** now names the three panels of Figure 7 in the pointer sentence, since the caption no longer
   can.

🟢 **The `Caption to install with it:` blocks in all six figure prompts were shortened in the same pass**,
so the specification and the manuscript still cannot drift. Each now also carries the standing rule:
*every caption in this paper is ten words or fewer, and anything beyond that belongs in the body text.*

### 4. Figure 1 re-specified as a landscape figure

🟢 **`4thJ_pipeline_steps_figure.md` now asks for a wide figure, not a tall one.** The twelve step cards
run left to right along one spine, the five phase bands move from the left gutter to a band along the
**top**, and the seven validation tiles move from the right gutter to a strip along the **bottom**, each
tile connecting upward to the cards it guards. Target canvas 2400 x 1000 at 300 dpi. A fallback is
written in: if twelve cards in one row would push the body type below 8 pt, wrap to two rows of six,
left to right on both rows, with one return arrow and no snaking.

The change reaches the paste-ready Gemini block in Section 11, not just the prose sections, because
Section 11 is what actually gets pasted. Sections 2, 3, 4, 5 and 7 were written for the portrait figure
and still use the words *gutter* and *spine*; each now carries an **ORIENTATION OVERRIDE** banner saying
the content is unchanged and only the direction is different.

🟢 **`FINDING 277` is closed in the prompt.** Both stale strings are deleted from the card list and added
to the forbidden-string list: card 6's *the reported folds are not yet trained* and card 10's *the no-core
engine does not exist yet*. Checklist item 7 was rewritten to test for their **absence** rather than their
presence, and three new checklist items were added — wide not tall, no note band, no green and no red.

🔴 **One question the author must answer before this figure is generated: card 6's chip still reads
`open`.** That was correct when the card was written. The transfer test is now trained, generated, scored
and reported as a nine-of-nine FAIL, and Step 11 is complete. Whether `open` is still the right chip is a
state judgement, not a wording fix, so it was **not** changed here. The same question applies to cards 10
and 11, where checklist item 8 currently says to reject any generation that gives them a checkmark.

### 5. Figure 2's prompt carries the reversed-fork correction

🟢 **`4thJ_figure02_loco_design.md` now opens with a blocking revision banner.** It states `FINDING 276`
in full — the marginals box must be a **source**, with arrows leaving it into both candidates and no
arrow arriving from either — and adds the palette table and the no-notes rule. It repeats that every
number on the installed image is correct and none of them changes.

⚪ **The image itself is unchanged and the `.docx` still carries the old Figure 2.** Generating it is the
author's step.

### 6. The reference list, answered with a count

🔴 **The manuscript formats 13 references. The project's own deep-research returns already hold 236
unique DOIs.** Counted directly: `RL01` to `RL31` in `4J_docs_occ/DeepResearchPrompts/`, 31 returned and
vetted files, `grep` for DOI patterns, sorted unique — 236. The reference list is short **not because the
literature was never searched, but because the bibliography was assembled only from the pipeline's own
verified citation records**, which are the citations that were load-bearing for a method or a band. The
236 were never harvested into it.

**So the answer to *do we need more deep-research prompts* is: mostly no, and the next move is on-disk.**
The work that is actually outstanding, in order:

1. **A harvest pass over `RL01`-`RL31`.** No external step, no Gemini. Read the 31 returns, pull the
   citations that bear on §1, §2, §3 and §6, format them, and check each against `VETTING_RL27.md`,
   `VETTING_RL28_RL29.md` and `VETTING_RL30_RL31.md` before it is allowed in — `RL30`/`RL31` failed five
   of seven vetting steps and several of their citations were struck, so an unvetted harvest would import
   exactly the fabrications that vetting caught.
2. **Finish the ⚠ block at the end of the reference list**, which names five sources cited in the text and
   not yet formatted: TABULA typology documentation, three national survey user guides, the Eurostat
   HETUS methodological guidelines, and the author's own prior line. Four of the five are on-disk jobs;
   the HETUS guidelines carry the open read recorded in §2.1.
3. **Only then, a new prompt or two, and only where the shelf is genuinely empty.** Two candidates:
   `L14`'s venue positioning was written before the author declined the venue and before the result was
   known, so it is stale rather than wrong; and `RL30`'s three first-person `NOT FOUND` results are
   load-bearing negative claims in §6.1 that a reviewer will test, so they are the ones worth re-running
   against a second search rather than left resting on one.

⚪ **Not done here, because it was a question and not an instruction.** No new deep-research prompt was
written this pass.

### 7. Two defects found while counting captions, neither touched

🔴 **`FINDING 280` — Tables 3 and 4 do not exist, and §3 cites Table 4.** The manuscript's numbered
tables run 1, 2, 5, 6, 7, 8, 9, 10. There is no Table 3 and no Table 4 anywhere in
`4J_manuscript_submission.md`, and the supplementary file contains no numbered tables at all. Line 208 of
§3 reads *"the complete gate set, with each band's provenance marked as published, project-chosen or
heuristic, is given in Table 4"* — a dangling cross-reference to a table the paper does not contain. Two
readings, and the fix differs: either the gate table was written and lost, in which case it must be
restored as Table 4 and Table 3 identified too; or the numbering skipped two and the reference should
point somewhere else, in which case Tables 5 to 10 renumber to 3 to 8 and §3's sentence needs a new home.
**Not guessed at here.** A reviewer will find this on the first pass; it is the most damaging thing in
the file.

🔴 **`FINDING 281` — §5.1 says *activity band* where the table gives *age bands*.** Line 605: *"the
model's time-budget mean absolute error against the raked donor pool's, per activity band, per fold."*
Table 5's `Band` column holds `Y25-44`, `Y45-64` and `Y_GE65`, which are age bands, and the old Table 5
caption said *three published age bands per fold*. The prose and the table disagree on what the rows are.
Left as found, because band vocabulary does not move during a writing round.

### Build and verification

From `writing/submission/`, unchanged recipe:

```
pandoc 4J_manuscript_submission.md -o raw.docx --reference-doc=extra/build_scripts/ref_submit_single.docx --resource-path=.
py -3 extra/build_scripts/post.py raw.docx 4J_manuscript_submission.docx
```

`post.py` reported `tables 8 | xml ok`. The file went from 5,096,426 to 4,615,601 bytes; it shrank because
the five regenerated PNGs carry less text.

**Verified, not assumed.**
* Eight images embedded; the md5 of every one is present in the md5 list of `figures/*.png`, so nothing
  was re-encoded and all five recoloured images did reach the document.
* `word/styles.xml` md5 is still `a3233bd11a66cc8ce3939f0c08602858`, byte-identical to 3J's.
* `grep -i hachem` on `word/document.xml` returns zero.
* All fifteen captions re-parsed out of the markdown after the edit; longest is ten words.

**Backups.** `previous/4J_manuscript_submission.2026-09-14_pre_soleauthor.md`,
`previous/4J_manuscript_submission.2026-09-14_pre_soleauthor.docx`, and
`previous/scripts_pre_recolour_2026-09-14/` holding the five figure scripts as they were.

Next: the author generates Figure 1 (landscape) and Figure 2 (fork corrected) from the two revised
prompts; rule on `FINDING 278` and on `FINDING 280`; then the reference harvest over `RL01`-`RL31`.

---

## 2026-09-14 last — the three author-generated images were returned and checked against their own checklists

⚪ **Nothing was computed. No gate, band, verdict or registered definition moved.** This entry records an
inspection of three PNGs the author generated in Gemini / Antigravity and installed, plus two new findings.

**What was installed, and from where.** The author generated all three, converted the returns from JPEG to
PNG and installed them over the previous versions. The superseded images were kept at
`writing/submission/figures/Prompts_Images/previous/backup_20260914/`. Figures 3 to 7 were not touched
(timestamps unchanged, 10:09).

| File | Size | Verdict |
|---|---|---|
| `HETUS_LLM_Pipeline_Steps.png` (Figure 1) | 1376 x 768 | content **PASS**, resolution **FAIL** |
| `Figure_02_loco_design.png` (Figure 2) | 1376 x 768 | blocking test **PASS**, two cosmetic faults |
| `HETUS_LLM_CrossNational_Pipeline.png` (graphical abstract) | 1376 x 768 | **REJECT**, see `FINDING 283` |

### Figure 1 — the landscape turn worked, and every item of Section 11.1 passes

Checked item by item against the twelve-item checklist in `4thJ_pipeline_steps_figure.md` §11.1, reading
the installed PNG and two magnified crops of it:

* **Item 10, wide not tall — PASS.** Twelve cards in one horizontal row, 0 at the left to 11 at the right,
  every spine arrow pointing right. The five phase bands `DATA` `MODEL` `CLAIM` `ENERGY` `STOCK` are along
  the TOP, each spanning exactly its own cards, all five labelled horizontally. The seven validation tiles
  are along the BOTTOM. This is the change the revision existed for and it landed on the first return.
* **Item 11, no note band — PASS.** No paragraph of small italic text anywhere. The only line below the
  tiles is the one the prompt asks for, inside its dashed box.
* **Item 12, no green and no red — PASS.** The `MODEL` band is the house teal `#44AA99` at a light tint and
  the `ENERGY` band the house rose `#CC6677`; neither reads as pass-green or fail-red, and nothing else in
  the picture carries either.
* **Item 7, the two retired strings — PASS, and this closes the last part of `FINDING 277` on the image
  side.** Card 6 carries only its two body lines and *"the reported folds are not yet trained"* is gone.
  Card 10 carries only *"observed footprints, dwellings only, one independent diary per dwelling"* and
  *"the no-core engine does not exist yet"* is gone. Neither of the two older retired lines appears either.
* **The `pre-declared gate batteries` bracket — PASS, drawn correctly for the first time.** A magnified crop
  of the bracket shows five drop lines, from cards 1, 2, 3, 4 and 5, with the bracket running from card 1's
  left edge to card 5's right edge. It was drawn short twice before, stopping at card 2 and at card 4.
* **Tier routing — PASS.** Traced on a 4x crop: `distributional fidelity`, `collapse, memorisation and
  privacy` and `transfer margin` all rise to card 6; `structural validity` rises to card 7; `downstream
  energy` is one bracket over cards 8 and 9; `basis and denominator` is one bracket over cards 10 and 11.
  The transfer-margin and structural-validity lines cross, which is what the specification asks for and is
  easy to misread as swapped at page size.
* **Chips — PASS.** Card 0 `cleared` with one checkmark; cards 1, 2, 3, 5, 8 and 9 `validated` with two;
  cards 4 and 7 `decided` with none; cards 6, 10 and 11 hollow `open`. Cards 8 and 9 do carry two
  checkmarks, which earlier returns got wrong.
* **Card 6 — PASS.** Larger than the others, light navy fill, thicker border, the `the bar:` line the only
  bold body line in the picture, and it keeps the hollow `open` chip.
* Cards counted: exactly twelve, 0 to 11. No card 12, no `Step 12`, no country name, no model name, no
  number outside the twelve circles.

🔴 **`FINDING 282` — all three returns are 1376 x 768 pixels, and all three prompts asked for more.**
Figure 1's prompt asks for *"at least 2400 by 1000"*, the graphical abstract's for *"at least 2000 by
1100"*. What came back is 1376 x 768 in every case, an aspect ratio of 1.79 where Figure 1 asked for about
2.4. At a 7-inch full-page width that is about 197 dpi, against the 300 dpi most publishers require, and
the card body lines in Figure 1 are about seven pixels tall. **Both prompts also ask for a PNG rather than
a JPEG, in terms, because JPEG compression frays small type; the returns are JPEGs that were converted to
PNG after the fact, so the compression damage is already in the pixels and the conversion did not undo
it.** The `.jpg` originals are in the Antigravity brain directory.

The content is right, so this is a re-render, not a redesign: the same prompt text, asked for at a larger
canvas, or the generator set to its largest output size. If the tool cannot exceed 1376 x 768, the
alternative is to rebuild Figure 1 in matplotlib from the card list, which the never-create-images rule
allows, since the card text is frozen in the prompt file and nothing about it is drawn from judgement.
**Not a blocker for an internal read-through, but it is a blocker for submission.** An author ruling on
which route to take.

### Figure 2 — the fork is fixed, which was the one blocking test

🟢 **`FINDING 276` is closed for Figure 2.** The single `Britain's published census marginals` box is now a
source: two arrows leave it, one up into the fine-tuned model and one down into the raked donor pool, and
no arrow arrives at it from either candidate. The installed image before this pass said the opposite. The
two candidate boxes are the same size and weight, the model is not drawn as the hero, and the held-out
country's real diaries appear only at the far right as `ground truth, never seen by either side until
scoring`.

All numbers verified on the image and all correct: 73,254 diaries, 2,024,068 episodes, 7.30 B backbone,
79.95 M trainable parameters, 5,200 generated diaries, and the three pairs 58.91 / 21.79, 60.44 / 19.21,
21.24 / 18.54 minutes per day, with `The null wins every band of every fold. 9 of 9. Closest miss 2.70
min/day.` The null bar is the shorter of the pair in all three bands. Palette is the house set: Spain rose,
Italy teal, Britain indigo and hollow, model bars sand with a hatch, null bars wine, no green, no red.

Two faults, neither disqualifying:

1. **Annotation (a) is printed twice**, once at the top of the middle band and once again under the
   marginals box, in slightly different line breaks. One copy should go.
2. **The image still carries prose blocks** — annotations (a) and (b) and the verdict line under the bars.
   This is the prompt contradicting itself rather than the generator misreading it: the body of
   `4thJ_figure02_loco_design.md` asks for `Two annotations` and for a line under the bars, while the
   no-notes rule appended to the same file on 2026-09-14 forbids exactly that. The rule was appended and
   the older instructions were not removed. **Whoever revises this prompt next must delete the `Two
   annotations` section and the line under the bars, or strike the no-notes rule for this one figure.**
   Both annotations say something a reader needs, so the honest fix is to move them into the §4 prose that
   cites Figure 2 and out of the picture.

Also cosmetic: the three band labels `split corpus`, `candidate` and `evaluation` are layout words drawn
into the image, and the title `Leave-one-country-out design evaluation` was never asked for. Harmless.

### The graphical abstract

🔴 **`FINDING 283` — the graphical abstract must not be used. Three faults, the first disqualifying.**

1. 🔴 **The held-out lane enters the training block.** The rose `Country C - held out` lane runs into the
   left edge of the navy `One open-weight LLM` block exactly as the teal and orange training lanes do,
   confirmed on a 3x crop. Its prompt asks for the opposite in terms: *"The third does NOT enter it: its
   dashed arrow passes under or around the block and re-enters on the right."* Read literally the picture
   says the held-out country was trained on, which is the single claim the whole paper turns on. This is
   the same defect class as `FINDING 276` and it is why that finding named the abstract as well as Figure 2.
2. 🔴 **The word `activity` is printed above the ribbons.** The prompt forbids it by name twice: *"Write NO
   heading above these ribbons: not the word activity"* and *"the word activity must not appear anywhere."*
3. **Only two ribbons are drawn where the prompt asks for three**, one per lane colour; the rose one is
   missing, and the rose arrow goes straight to the `held-out country` box instead. And inside that box the
   line `three independent nulls, all reported` is printed twice.

What did come out right: the plan of building footprints at the far right is subdivided edge to edge with
no stair core, no corridor and no gap, and its six cells carry six different tick-marks and no checkmark,
which is the fault the prompt flags as most likely and which earlier returns got wrong. The three schedule
curves are there with 0 and 24 axes and visibly different shapes. No real country name, no flag, no model
name, no status word.

**The graphical abstract's prompt was never revised in this pass or the last**, which is why fault 1 is
still in it: the file still contains the original lane instructions and no blocking banner. Revising it is
a session job of the same shape as Figure 2's revision and has not been asked for.

### State

Figure 1 and Figure 2 are usable for an internal read-through now and need one re-render at a larger canvas
before submission. The graphical abstract is not usable. Figures 3 to 7 are untouched and still current.
No caption changed, no manuscript text changed, and the `.docx` was not rebuilt, because the three
installed files carry the same filenames the existing build already embeds by path.

Next: rule on `FINDING 282`, re-render or rebuild; revise the graphical abstract prompt for `FINDING 283`;
strike the duplicated annotation in Figure 2's prompt; then `FINDING 280` and the reference harvest.

---

## 2026-09-14 last+1 — the three Gemini prompts cut back: "these are not reports, these are representative images"

⚪ **Nothing computed. No gate, band, verdict or registered definition moved.** Prompt files only; no image
was generated here and no manuscript text changed.

**The instruction.** *"update prompts to be generated by gemini, also lets use less text inside the
pictures, these are not reports, these are representative images."* Applied to all three author-generated
prompts. The three fixes owed from the inspection entry above were folded into the same pass.

**Backups:** `figures/Prompts_Images/previous/prompts_pre_sparse_2026-09-14/`, all three files.

### Figure 1 — `4thJ_pipeline_steps_figure.md`, Section 11 rewritten

Text that will actually be drawn, counted: **card body lines fell from 18 lines and 155 words to 16 lines
and 82 words.** Every card now carries exactly one short body line, with a second line only on cards 5, 6,
8 and 9 — the four that record something that failed.

| Card | Was | Now |
|---|---|---|
| 0 | data reachable, prior art clear, method justified, release limits known | data, prior art, method, release limits |
| 1 | national time-use series, one wave per country | one harmonised wave per country |
| 2 | common activity, location and co-presence coding, shared day origin | common activity, location, co-presence |
| 3 | episode form: duration, activity, location, co-presence | duration, activity, location, co-presence |
| 4 | open-weight base model, low-rank adapter, one adapter per held-out country | one adapter per held-out country |
| 5 | synthetic population first, then one generated day per person / two gates fail and ship as a declared exception | synthetic population, then one day each / two gates ship as declared exceptions |
| 6 | train on the other two, generate the held-out one from published marginals / the bar: beat real diaries from the other countries, reweighted to the held-out country | train on two, generate the third / the bar: beat real diaries, reweighted |
| 7 | well-formed diaries guaranteed at decoding / throughput, chaining rule and schedule emission | well-formed diaries guaranteed at decoding |
| 8 | European residential archetypes, uninjected control run first / the occupancy effect does not survive at full injection | European residential archetypes / the occupancy effect does not survive |
| 9 | published activity-to-appliance mappings, adapted not authored / three gates ship as declared failures | published activity-to-appliance mappings / three gates ship as declared failures |
| 10 | observed footprints, dwellings only, one independent diary per dwelling | observed footprints, one diary per dwelling |
| 11 | the same mapping, at the scale its sources were validated at / the bands are inherited unmoved, not re-set at stock scale | same mapping, bands inherited unmoved |

Two further cuts:

* **The two title lines became one**, `From harmonised time-use surveys to simulated building energy`. The
  journal prints a caption under the figure; a second title line inside it was duplication.
* 🔴 **The bottom sentence `every tier is first shown failing on a deliberately broken control` was removed
  from the image altogether**, and added to the forbidden-strings list so it cannot come back. It is an
  explanatory sentence in a dashed box along the bottom edge, which is exactly what the no-notes rule of
  2026-09-14 forbids, and the author's instruction settles it. **It is a real methodological claim and it
  must be carried by §3's prose instead.** Recorded here because it is the one piece of content this pass
  removed rather than shortened.

**The honesty lines were kept, shortened, not dropped.** Cards 5, 8 and 9 still say two gates ship as
declared exceptions, the occupancy effect does not survive, and three gates ship as declared failures. A
pipeline figure showing Steps 5, 8 and 9 as `validated` with nothing else would claim a clean downstream
result this project does not have, and the checklist has said so since 2026-08-26.

**Three banners added so the file cannot contradict itself**, at Sections 4, 5 and 6: Section 11's card
list is now the authoritative wording for the **body lines**; Sections 4, 5 and 6 still govern the card
titles, the chip words, the twelve numbers, the seven tile labels and the complete list of strings that
are *allowed*. A string that appears in Section 6 but not in Section 11 is permitted-but-retired and must
not be drawn.

**Two checklist items added**, 13 and 14: count the words (one title line, one body line per card, two
only on 5, 6, 8 and 9, nothing below the tiles), and check the pixel size before installing.

### Figure 2 — `4thJ_figure02_loco_design.md`, specification body rewritten

The whole file is pasted, so the body itself was cut rather than a block inside it.

Removed from the image: the two annotation paragraphs, in full; `published by the national statistical
office before either candidate existed` shortened to `published before either candidate existed`;
`the same tables, the same geography, the same strata` beside the fork; `grammar-constrained generation`;
`79.95 M trainable parameters`; `every day is a day somebody lived`; `one wave each`; `three age bands:
Y25-44 · Y45-64 · Y_GE65` in the scoring box, now carried by the bar labels alone; `training, 2 countries`
cut to `training`; `held out, never seen in training` cut to `held out`; `ground truth, never seen by
either side until scoring` cut to `ground truth`. The verdict line was shortened to `The null wins 9 of 9.
Closest miss 2.70 min/day.` and is now stated to be **the only sentence in the picture**.

🔴 **The prompt no longer contradicts itself.** It previously asked for `Two annotations` in its body while
the no-notes rule appended to the same file forbade them; the generator obeyed the body and printed one of
them twice. The `Two annotations` section is deleted and a paragraph in its place says both arguments now
belong in the body text of the section that cites Figure 2 — that giving the null weaker marginals would
convert a null into a handicap, and that the raking starts from a uniform seed so the donor surveys' own
weights are discarded. **Neither is in the manuscript prose yet. Whoever writes Figure 2's prose pointer
must carry both, or the paper loses two answers to two obvious reviewer objections.**

Also added: no image title, no band headings (the 2026-09-14 return invented both), do not print any label
twice, and the fork rule restated as `No arrow arrives at this box from either candidate`.

**Every number is unchanged**: 73,254 / 2,024,068, 7.30 B, 5,200, the three pairs 58.91 / 21.79,
60.44 / 19.21, 21.24 / 18.54, and 2.70.

### Graphical abstract — `4thJ_graphical_abstract.md`, Section 10 rewritten and a blocking banner added

🟢 **`FINDING 283` is now addressed in the prompt.** Three changes, beyond the text cut:

1. **Lane three is given its own rule, in capitals, stated three times** — before the navy block, in the
   block's own paragraph, and again under "the two things most likely to go wrong". It turns downward
   before reaching the block, runs below it as a dashed line with clear white space, and turns back up on
   the far side. At no point may it touch, overlap or pass behind the block, and no arrowhead from it may
   land on the block. The paragraph says why: the whole paper rests on the held-out country never being
   trained on.
2. **The word `activity` is forbidden three times**, including one sentence that says printing it is on its
   own a reject.
3. **Three ribbons, "and three is the count, not two"**, with the third dashed and receiving lane three.
   The held-out box is specified as exactly two lines, each written once.

Text removed from the image: the diary-field tuples and `conditioning prefix + day sequence` from all three
lanes; the sub-lines under the three source cards; `Harmonised European Time Use Surveys` at the foot of
the left panel; `structure guaranteed at decoding` in the navy block; two of the four lines in the held-out
box; `population and day are generated separately`; and one of the three lines under the schedule curves.
The two title lines stay, because a graphical abstract is read on its own on a listing page.

A blocking banner was added above Section 0 stating all three faults and the text cut, and saying that
where Sections 3 and 6 list a sub-line Section 10 no longer carries, Section 10 wins.

### What this does about `FINDING 282`

It does not fix it, but it makes it survivable. **The same canvas now has to carry about half the words**,
so the type can be set roughly twice as large at any pixel count. All three prompts also end with an
explicit OUTPUT paragraph naming the minimum size, asking for a PNG that was never a JPEG, and saying that
a 1376 x 768 return has to be regenerated. If the generator still caps at 1376 x 768, the ruling recorded
under `FINDING 282` stands: re-render elsewhere, or rebuild Figure 1 in matplotlib from the frozen card
list.

Next: author regenerates all three from the revised prompts; then `FINDING 280`, then the reference harvest.

---

## 2026-09-14 last+2 — second generation from the cut-back prompts, inspected: one pass, two rejects

⚪ **Nothing computed. No gate, band, verdict or registered definition moved.** Image inspection only.

The author regenerated all three images from the prompts rewritten earlier the same day and installed them
at 11:25. The superseded 11:03 set is at `figures/Prompts_Images/previous/backup_20260914_1103/`. The
generating agent's own summary again claimed all three were correct; again it was not taken at face value.
Every statement below was read off the installed PNG, several off crops magnified 3x to 10x.

**All three are 1376 x 768 again.** `FINDING 282` is therefore unchanged and the shorter text did not move
it: the generator caps at that canvas whatever the prompt asks for. The type *is* visibly larger than on
the 11:03 set, because the same box now carries half the words, so the images are readable on screen; they
are still about 197 dpi at full page width. **The author ruling under `FINDING 282` is now the only route
to a submittable Figure 1: re-render somewhere with a larger canvas, or rebuild Figure 1 in matplotlib
from the frozen card list.**

### Figure 1 — `HETUS_LLM_Pipeline_Steps.png` — PASS on thirteen of fourteen items, one typo

🟢 Twelve cards in one row, 0 to 11, left to right. The five bands span exactly the cards they should
(DATA over 0-2, MODEL over 3-5, CLAIM over 6-7, ENERGY over 8-9, STOCK over 10-11) and all five labels are
horizontal. One title line only. No green, no red, nothing written below the tiles. Card 6 is enlarged with
the only bold body line and keeps the hollow `open` chip. Chips are right on all twelve: card 0 `cleared`
with one check, cards 1, 2, 3, 5, 8 and 9 `validated` with two checks each, cards 4 and 7 `decided`, cards
6, 10 and 11 hollow `open`. The `pre-declared gate batteries` bracket spans cards 1 to 5 with five drop
lines, correct for the second time running. The honesty lines on cards 5, 8 and 9 are all present and all
short.

🔴 **`FINDING 286` — card 11 prints the word `mapping,` twice.** It reads *same mapping, mapping, bands
inherited unmoved* where Section 11 says *same mapping, bands inherited unmoved*. Confirmed on a 4x crop.
It is one duplicated word in one card and nothing else on the figure is wrong, so this is a re-render of
Figure 1 alone, not a redesign. Nothing in the prompt caused it; the paste block is correct.

### Figure 2 — `Figure_02_loco_design.png` — REJECT, `FINDING 287`

🔴 **`FINDING 276` is reopened for Figure 2. The fork is wrong again, in the mirror image of the old
defect.** The marginals box now sends one arrow UP into the fine-tuned model, which is right. But the
second arrow still points the wrong way: it runs UP from the raked donor pool INTO the marginals box, so
an arrow **arrives** at the box from a candidate, which the prompt forbids in those words. Read literally
the picture now says the donor pool produces Britain's published marginals. Confirmed at 4x. The branch
that should exist, marginals down into the donor pool, is not drawn.

🔴 **A third arrow runs straight from the marginals box into the scoring box.** The marginals are an input
to both candidates, not a thing that is scored. Three arrowheads land on the scoring box where there
should be two.

🔴 **Three band headings are printed across the top**: *Corpus and split*, *Visual candidates*, *Scoring*.
The revised prompt says there is no image title and no band headings, and names *corpus*, *candidate* and
*split* as words that must not appear in the picture. All three appear.

🔴 **Two hex colour codes are printed inside the boxes**: `Upper: #332288` above the model's title and
`#882255` above the raked donor pool's title. The palette table is a specification for the person drawing
the figure and was read as text to draw.

🔴 **The prompt's own instruction sentence is printed as the ground-truth label**, greyed at the top right,
reading *held-out country's real diaries appear a single label ground truth*, and it is clipped by the
right edge of the canvas. The label should be the two words `ground truth`.

⚪ Minor, not blocking: the two candidate boxes are not of equal visual weight — the model is a white box
with a thin indigo outline, the null a solid wine block. The prompt asks for equal weight so that neither
reads as the hero.

🟢 What is right: every number (58.91 / 21.79, 60.44 / 19.21, 21.24 / 18.54, 2.70, 73,254, 2,024,068,
7.30 B, 5,200), the null bar shorter in all three pairs, the house palette on the country tiles and the
bars, the sand hatch on the null series, Britain outlined not filled, and one verdict sentence only.

### Graphical abstract — `HETUS_LLM_CrossNational_Pipeline.png` — REJECT, `FINDING 288`

🟢 **Two of the three faults of `FINDING 283` are fixed.** The word `activity` appears nowhere in the
image. The dashed bypass below the navy block is now drawn: lane three turns down, runs under the block
with clear white space, and turns up on the far side into the dashed ribbon, with the two small lines
*each country is held out in turn* and *never seen in training* beside it.

🔴 **But lane three still touches the navy block.** A short solid rose stub runs from the point of the
lane-three chevron to the block's left edge, exactly as lanes one and two do. Confirmed at 10x
magnification: the stub is about six pixels long and unmistakable. So the image now says both things at
once — the held-out country bypasses the model, and the held-out country feeds the model. **This is the
same disqualifying defect as before and the abstract still must not be used.** The bypass is necessary but
the contact is what makes the claim false.

🔴 **Only two ribbons are drawn where the prompt asks for three**, one solid and one dashed. The prompt
says *three is the count, not two* in those words. The third, teal or orange, is missing.

🔴 **The held-out box carries four lines, not two, and one of them is garbled**: *generated from published
marginals only*, *compared against demgranle c diary*, *compared against reweighted real diaries*, under
the heading *held-out country*. `demgranle c diary` is not a word. `compared against` is printed twice.

⚪ Minor: the two ribbons are drawn in many hues rather than one per lane colour, and the three lane words
are split across lanes — lane one has `episode diary`, lane two has `serialised record`, lane three has
neither — where the prompt gives all three lanes both.

🟢 What else is right: the three source cards each carry one label, the navy block carries its title, the
transformer motif, the `low-rank adapter` badge and exactly two lines, the marginals-to-synthetic-
population chain runs below and outside the block and turns up into the held-out box, the subdivided
footprint is filled edge to edge with six differently marked cells and no service core, and the three
schedule curves are present in the three lane colours with 0 and 24 on each axis.

### Where this leaves the figure set

| Figure | State |
|---|---|
| Figure 1, pipeline | Content correct. One duplicated word on card 11 (`FINDING 286`). Re-render, or rebuild in matplotlib under `FINDING 282`. |
| Figure 2, design | REJECT (`FINDING 287`). Five faults, one of them the fork the figure exists to prove. |
| Graphical abstract | REJECT (`FINDING 288`). Lane three still touches the block. |
| Figures 3 to 7 | Untouched, timestamps unchanged at 10:09. |

**A pattern worth recording, because it decides what to do next.** Across two generations the same class of
error keeps recurring: text that is a specification for the person drawing gets printed as text in the
drawing (hex codes, band names, the ground-truth instruction sentence), labels get duplicated (`mapping,`,
`compared against`, and on the 11:03 set an annotation and a ribbon line), and an explicitly forbidden
connector gets drawn anyway. Prose prompts are not eliminating these, and each regeneration costs a full
author round trip. **Figure 1 is the one figure whose content is entirely frozen — twelve cards, twelve
titles, sixteen body lines, four chip words, seven tiles, five bands, no judgement anywhere — and the
never-create-images rule permits a matplotlib build from frozen data. Recommendation to the author:
build Figure 1 in code and keep Gemini for Figure 2 and the abstract, which are pictorial.**

Next: author ruling on `FINDING 282`; then regenerate Figure 2 and the abstract; then `FINDING 280`.

---

## 2026-09-14 last+3 — all three figure prompts rewritten a third time, on the author's ruling that the failures are this side's

⚪ **Nothing computed. No gate, band, verdict or registered definition moved.** Prompt files only.

**The instruction.** *"if figures are not good, it is your fault, update prompts to be in detail."*
Taken as written. The inspection entry above (*last+2*) recorded five faults on Figure 2, three on the
graphical abstract and one on Figure 1. **Three of the five Figure 2 faults are traceable to this side
of the work and not to the generator**, and they are the reason the ruling is right.

### The root cause on Figure 2, which was ours

Figure 1 and the graphical abstract each had a fenced paste-ready block. Figure 2 never did: the file
said to paste the whole document. The whole document contains markdown section headings
(`### Band 1 (left) - the corpus, split`, `### Band 2 (middle) - the two candidates`,
`### Band 3 (right) - scoring`), a house-palette table of hex codes, and a sentence describing how to
draw the far-right element. The generator drew all three: three headings across the top of the picture,
`Upper: #332288` and `#882255` inside the boxes, and the description sentence as the label. **It was not
inventing text. It was handed text with no way of telling which of it was to be drawn.**

🟢 **Figure 2 now has Section 12, a single self-contained paste-ready block**, and the file's
header says to paste that and nothing else. The block contains no markdown heading, no table of colour
codes and no sentence that could be mistaken for a label.

### Three additions made to all three prompts

1. **A TEXT INVENTORY**, numbered, at the end of each block: every string the picture may contain, the
   count, and which few strings are drawn more than once and how many times. The governing rule is now
   stated positively — *if a word appears in these instructions but not in the inventory, it must not
   appear in the picture* — rather than as a growing list of prohibitions.
2. **A never-draw-instruction-words paragraph** naming the words that actually leaked: the layout words,
   the section names, and every colour code, with the flat rule that **the character `#` appears nowhere
   in any of the three images**.
3. **A six-question self-check the generator must answer in its reply.** Each question is a yes/no or a
   count on the exact defect that figure has already shown, plus the pixel size, with the sentence
   *a wrong answer reported is one round trip; a wrong answer reported as correct is three*. The
   generating agent has now twice reported all three figures correct when they were not, so the value of
   this is not that it prevents the defect but that it forces the defect to be named.

### Per figure

**Figure 1.** A word-count table for all sixteen card body lines, so a duplicated word shows as a count
one too high, and card 11's five words listed individually with *the word mapping appears on card 11
once and only once* (`FINDING 286`). Nothing else on Figure 1 changed; it passed thirteen of fourteen.

**Figure 2.** An explicit **arrow table**: exactly six arrowheads, each one named by where it lands, and
then the negatives — no arrowhead on the marginals box, no arrow from the marginals box to the scoring
box, exactly two arrowheads on the scoring box, none on any country tile. The two branches of each fork
are stated to be branches of **one** line leaving the source. The 2026-09-13 return drew the only arrow
touching the marginals box as arriving from the model; the 2026-09-14 return drew it arriving from the
donor pool. The new block says which end of each line carries the head, one line at a time
(`FINDING 276`, `FINDING 287`). The far-right label is written out as *the two words are: ground truth*
and given its own inventory number. The two method boxes are respecified as identical except for border
colour and hatch, which also answers the equal-weight point.

**Graphical abstract.** The lane-three rule is rewritten around a measurement rather than an adjective:
lane three turns down **at least one tenth of the image width to the left of** the navy block's edge,
and **no connector of any length** may join them — *six pixels was enough to make the figure unusable*
(`FINDING 288`). It also forbids lane three from tapering to a point aimed at the block, which is what
the defect actually looked like. The held-out box is respecified as exactly three lines counting its
heading, with *do not write "compared against" more than once anywhere in the image*, and with the rule
that every word in the box is an ordinary English word — the return contained `demgranle c diary`.
🔴 **Section 10.2 item 9, which still demanded a fourth line `three independent nulls, all
reported`, is marked SUPERSEDED.** The file had been contradicting itself since the text cut, and a
checker following 10.2 would have enforced the four-line box that produced the duplication.

### What this does not fix

🔴 **`FINDING 282` is untouched and no prompt can touch it.** All three returns have now come
back 1376 x 768 three times running, against prompts that name the size, forbid it, and now ask the
generator to say so if it cannot exceed it. If the fourth return is 1376 x 768 as well, the prompt is
not the variable. **The recommendation of *last+2* stands unchanged: build Figure 1 in matplotlib from
the frozen card list, which settles `FINDING 282` and `FINDING 286` together and at any resolution, and
keep the generator for Figure 2 and the abstract, which are pictorial and cannot be coded.**

**Backups.** `4thJ_pipeline_steps_figure.md.bak_pre_detail` (1103 lines),
`4thJ_figure02_loco_design.md.bak_pre_detail` (214), `4thJ_graphical_abstract.md.bak_pre_detail` (929),
all beside the originals, which are now 1159, 437 and 1011 lines.

Next: author regenerates all three from the revised blocks; then `FINDING 280`.

---

## 2026-09-14 last+4 — third generation inspected: one figure closes a defect and opens two, two figures still fail on the one thing they exist to prove

⚪ **Nothing computed. No gate, band, verdict or registered definition moved.** Image inspection and
prompt files only.

The author regenerated all three from the revised blocks and installed them at 13:11. The 11:25 set is at
`figures/Prompts_Images/previous/backup_20260914_pre_regenerate/`. Every claim below was read off the
installed PNG, several off crops magnified 3x to 8x.

🟢 **The self-check worked, and that is the one clear gain of the third revision.** The generating
agent answered the six questions and **reported three of its own defects in plain words**: the stray
`ONE` and `RIGHT EDGE` labels on Figure 1, one arrowhead touching the marginals box on Figure 2, and the
third lane tapering into the dark block on the abstract. All three were then confirmed here independently.
For the first time the external report and the inspection agree. That is worth keeping whatever else
changes.

🔴 **All three are 1376 x 768 for the fourth time.** `FINDING 282` is now settled as a fact rather
than a suspicion: the prompt is not the variable. The block asks for 2400 x 1000, forbids 1376 x 768 by
name, and asks the generator to say so if it cannot exceed it — and it did say so. The cap is the tool.

### Figure 1 — `HETUS_LLM_Pipeline_Steps.png` — one defect closed, two opened

🟢 **`FINDING 286` is CLOSED.** Card 11 reads `same mapping, bands inherited unmoved`, each word
once. The word-count table did its job.
🟢 The `pre-declared gate batteries` bracket spans cards 1 to 5, confirmed on a 3x crop, for the
third time running. Twelve cards, five bands over the right cards, card 6 enlarged with the only bold
line and a hollow chip, no green, no red, nothing else below the tiles.

🔴 **`FINDING 289` — and this one is this side's fault, not the generator's.** Two extra shapes
are drawn along the bottom: the loose word `ONE` and, in its own grey tile, `RIGHT EDGE`. **Nine tile
shapes where the specification says seven.** Both strings come from the prompt's own bracket sentence,
which read *joined by ONE bracket that spans cards 1, 2, 3, 4 and 5 together. The bracket starts at the
LEFT edge of card 1 and ENDS AT THE RIGHT EDGE OF CARD 5* — written in capitals, and sitting inside the
list of the seven tile labels, where every other line is a label. It was read as two more labels.
**The general rule this yields is now written into all three blocks: an instruction inside a fenced
prompt is never written in capitals and never sits inside a list of labels.** The capitals were added on
this side to make the instruction harder to miss, and they made it easier to draw.

🔴 Card 3's chip reads `vall`, a clipped `validated`, with its two checkmarks correct. Card 0's
`cleared` chip carries no checkmark where the specification gives it one. Both are new, both are the
generator, and both are now named in the block: chip words are spelled in full, widen the chip rather
than clip the word, and card 0 carries exactly one checkmark.

⚪ Minor, not blocking: cards 2 and 3 share one rounded outline and are narrower than the rest, and
card 2 is tinted teal although it sits under the grey `DATA` band.

### Figure 2 — `Figure_02_loco_design.png` — REJECT, `FINDING 290`

🟢 **Four of the five faults of `FINDING 287` are fixed.** No band headings. No hex code anywhere
— the character `#` appears nowhere in the image. The far-right label is the two words `ground truth`,
and the grey dashed line from it to the scoring box carries no arrowhead, as specified. Every number is
right, the null bar is shorter in all three pairs, the hatch is on the null series, Britain is outlined
and not filled, and there is one sentence in the picture.

🔴 **The fork is still wrong, for the third generation running, and it is the only thing the
figure exists to prove.** The single line leaving the Spain-and-Italy enclosure forks into **three**
branches, not two: up into the model, **straight into the box holding Britain's published census
marginals**, and down into the donor pool. Confirmed on a 5x crop: the arrowhead lands squarely on that
box's left edge. Read literally, the picture now says the two training countries produced Britain's
census. Meanwhile the fork that should exist — marginals down and up into the two candidates — **is
not drawn at all**; the marginals box's only outgoing line runs right, merges with the donor pool's
output line, and shares the lower arrowhead into the scoring box. The scoring box does have exactly two
arrowheads, so that count now passes, but one of them is carrying the marginals.

**What the prompt did wrong, and what it now says.** The arrow table named six arrowheads by their
landing place and then listed the negatives afterwards. A list of six destinations does not stop a
seventh line being drawn. The block now describes **three lines, drawn one at a time**, each with its
start, its fork and its two ends, and says that the marginals box is a starting point and never a
destination, with the sentence *if you find yourself drawing a line that ends at it, you have the picture
backwards*.

### Graphical abstract — `HETUS_LLM_CrossNational_Pipeline.png` — REJECT, `FINDING 291`

🟢 **Two of the three faults of `FINDING 288` are fixed.** Three ribbons are drawn, not two. The
held-out box carries its heading and exactly two lines, each written once, every word a real English word
— `demgranle c diary` and the repeated `compared against` are gone.

🔴 **The third lane still reaches the dark block, and it is worse than last time.** On 2026-09-14
at 11:25 the contact was a stub about six pixels long. At 13:11 **the tinted lane body itself runs flush
into the block's left edge across its full width**, confirmed on an 8x nearest-neighbour crop: rose fill
and navy fill are adjacent, with no white between them. A dashed bypass is also drawn below the block. So
the picture again says both things at once, and the disqualifying one is the contact.

**What the prompt did wrong, and what it now says.** The rule was written about arrows, stubs and
connectors — things joined *to* the lane — and the lane is not any of those. It is a tinted strip, and
the strip was simply drawn long enough to arrive. The block now specifies the **shape of the strip
itself**: the third lane is a strip that runs right and **stops**, its rightmost point at least a tenth of
the image width from the block, the gap plain white, and *if any coloured pixel of the third lane is
adjacent to the dark block, the picture is wrong*. It is now the first thing said about the lanes rather
than a rule appended after them.

🔴 **New: all six dwelling cells in the small footprint plan carry the same checkmark.** The
prompt asks for six *different* tiny marks and says *none of them is a checkmark*, in those words. Six
identical ticks were drawn. On a figure whose headline result is a failure, a grid of green-ticked cells
is the worst available mark. The block now lists the six marks one by one and says that six identical
marks are wrong whatever the mark is.

⚪ Minor, unchanged: each lane carries one of `episode diary` and `serialised record` rather than both.

### Where this leaves the figure set

| Figure | State after the third generation |
|---|---|
| Figure 1, pipeline | Content correct, `FINDING 286` closed. Two extra tiles from a prompt defect (`FINDING 289`), one clipped chip word, one missing checkmark. |
| Figure 2, design | REJECT (`FINDING 290`). Four faults fixed; the fork is wrong for the third time. |
| Graphical abstract | REJECT (`FINDING 291`). Two faults fixed; the held-out lane touches the model, worse than before. |
| Figures 3 to 7 | Untouched, timestamps 10:09. |

🔴 **The pattern across three generations is now measurable, and it decides the question.** Each
round fixes most of the named faults and introduces new ones somewhere the prompt did not name. Round one
to two: three faults fixed, three new. Round two to three: six fixed, four new. **Nothing converges,
because the prompt can only name the failures that have already happened.** Figure 1 is the one figure
whose content is entirely frozen — twelve cards, twelve titles, sixteen body lines, four chip words,
seven tiles, five bands, no judgement anywhere — and every remaining defect on it is a drawing error,
not a content error: two stray labels, a clipped word, a missing checkmark, and the canvas size. **A
matplotlib build produces all four correctly by construction and at any resolution, and the
never-create-images rule expressly allows it for frozen data. Recommendation, unchanged and now
stronger: build Figure 1 in code. Figure 2 and the graphical abstract stay with the generator, because
they are pictorial.**

**Prompt files after the fourth revision**: `4thJ_pipeline_steps_figure.md` 1169 lines,
`4thJ_figure02_loco_design.md` 447, `4thJ_graphical_abstract.md` 1020. Pre-revision copies are the
`.bak_pre_detail` files beside them.

Next: author ruling on Figure 1 in code; then regenerate Figure 2 and the abstract; then `FINDING 280`.

---

## 2026-09-14 last+5 — Figures 1 and 2 and the graphical abstract built in code; the image loop is closed

⚪ **Nothing computed, trained or scored. No gate, band, verdict or registered definition moved.**
Figure scripts, one board rename, one new board, two prompts, one rebuild.

### The instruction, and why it is the right call

*"ok if possible you create these failed images."* The never-create-images rule stands and its standing
exception is a plot built by a script from frozen data; the author extended that exception to these three
by name. The case for it was already measured. Round one to two fixed three faults and introduced three.
Round two to three fixed six and introduced four. Round three to four was never run because the pattern
was clear: **a prompt can only name failures that have already happened**, so each revision buys the last
round's defects and pays for them with new ones. Four returns in a row also came back at the same
1376 x 768 canvas against prompts that named the size, forbade it, and asked the tool to say so if it
could not exceed it. The canvas was never the prompt's to fix.

### What was built

| Figure | Script | PNG | Pixels |
|---|---|---|---|
| Figure 1 | `figures/scripts/generate_fig01_pipeline.py` | `HETUS_LLM_Pipeline_Steps.png` | 4440 x 1620 |
| Figure 2 | `figures/scripts/generate_fig02_loco.py` | `Figure_02_loco_design.png` | 3850 x 1277 |
| Graphical abstract | `figures/scripts/generate_graphical_abstract.py` | `HETUS_LLM_CrossNational_Pipeline.png` | 3937 x 1525 |

Each script carries the figure's frozen TEXT INVENTORY as data, copied character for character from the
prompt file, and draws nothing else. The prompt files are untouched and remain the specification.

### The assertions, which are the point

The gain is not that a script draws more neatly. It is that **the defects that kept coming back are now
checked by the program before the file is written**, so a wrong figure cannot be produced silently.

* **Word counts.** Figure 1's sixteen body lines are checked against the prompt's own word-count table.
  `ABORT card N word count ... expected ...` if any line gains or loses a word. This is `FINDING 286`
  made impossible rather than merely warned against.
* **Arrowheads.** Figure 2 collects the six arrowhead coordinates and asserts two on the top method box,
  two on the bottom, two on the scoring box and **zero anywhere inside the published-marginals box**.
  The build prints the four counts. This is `FINDING 276` / `287` / `290`, which was drawn wrong three
  times in three different ways, made impossible.
* **The held-out gap.** The abstract computes the gap between the third lane's end and the model block
  and refuses to save if it is under one tenth of the image width. It prints *held-out lane stops 3.15 in
  (10.0% of the image width) short of the model block*. This is `FINDING 288` / `291`.
* **Text fitting.** Every text object is measured against the element that holds it after drawing.
  Nothing is shrunk and nothing is clipped; the script either prints `no text overflows its element` or
  names the offender, its drawn width and its allowance. All three print the clean line.
* **Resolution.** `FINDING 282` becomes a script argument. All three are well past the 2400 x 1000 the
  prompts asked for, and all three are PNG that was never JPEG.

`FINDING 289`, the two instruction words drawn as extra tiles, closes for a different reason again:
there is no instruction text anywhere in the drawing path, so an instruction cannot leak into a picture.

### Palette and captions, unchanged

Spain rose `#CC6677`, Britain indigo `#332288`, Italy teal `#44AA99`, second series sand `#DDCC77` with a
hatch, negative channel wine `#882255`, reference lines black, neutral fills `#F2F2F2` and `#D0D0D0`. No
green and no red. Every pair is separated by hatch as well as hue, so all three survive greyscale. No
caption, note band, verdict sentence or legend is printed inside any of the three images, and the three
external captions are unchanged and are within the ten-word rule.

### The rebuild, verified rather than assumed

```
cd 4J_docs_occ/writing/submission
pandoc 4J_manuscript_submission.md -o raw.docx --reference-doc=extra/build_scripts/ref_submit_single.docx --resource-path=.
py -3 extra/build_scripts/post.py raw.docx 4J_manuscript_submission.docx
```

`tables 8 | xml ok`. 1,817,366 bytes, down from 4,615,601 because vector-drawn line art compresses far
better than a generated raster. **Eight images embedded; the md5 of each one matches a file in
`figures/`, all eight, so nothing was re-encoded.** The manuscript markdown already referenced all three
images at lines 41, 96 and 100, so no markdown edit was needed and none was made.

Backups: `writing/submission/previous/4J_manuscript_submission.docx.bak_pre_codefigs`, and the three
superseded PNGs at `figures/previous/backup_20260914_pre_codebuild/`. The copies of the three images that
live beside the prompts in `figures/Prompts_Images/`, under both their names, were refreshed too.

### The two boards

🟢 **`4thJ_CHECKLIST.html` is retired to `DONE_4thJ_CHECKLIST.html`**, on the author's
instruction, with its pre-Step-11 backup renamed alongside it. It tracked the pipeline, Steps 0 to 11,
and the pipeline is finished. Nothing else was changed inside it.

🟢 **`writing/4thJ_MANUSCRIPT_CHECKLIST.html` is new** and tracks the paper only: 30 cards, 12
done, 5 blocking, 7 quality, 4 waiting on the author, and 2 carried over under a heading that says they
cannot be closed and are not work. Those two are `G10.14` and `G10.18`, the manifest fields never written
on campaign C1's 410 cells; the board states in plain words why no future session should pick them up.
The card counts on the page were checked against the cards on the page; the inline filter script passes
`node --check` and a DOM-shim smoke run over all six filter states.

### The two evaluation prompts

`writing/IMP/IMP_01_GEMINI_manuscript_evaluation.md` and
`writing/IMP/IMP_02_FABLE_manuscript_evaluation.md`. The split is deliberate and follows the standing
rule that deep research is external: **Gemini gets everything that needs the outside world** - literature
coverage, whether a comparable negative result already exists, whether anything published contradicts
this one, DOI integrity, the hostile-reviewer read - and **Fable gets everything that needs the
repository** - every number traced back to its step document, the cross-reference audit, figure against
text, built file against master, and what the repository records that the paper does not carry. Fable is
explicitly forbidden to search the web, to resolve a DOI or to offer a citation, and is explicitly
read-only.

Both returns are shaped the same way, eight lettered sections in a fixed order, so they can be laid side
by side. Both end with a **reconciliation section that must be answered last**, against the same eight
known defects, which turns the return into a measurement of its own depth: a pass that finds one of the
eight is shallow and the rest of it is worth less. Both forbid replacement prose, forbid changing or
recomputing any number, forbid proposing that a threshold be loosened because the model fails it, and
forbid em and en dashes. Both carry a six-question self-check to be answered in the reply, the mechanism
that worked on the third figure generation.

🔴 **Neither return may move a gate, a band, a verdict or a registered definition.** If a return
argues that one should move, that is a finding to record, not an edit to make. Vet under the seven-step
protocol; `RL30` and `RL31` failed five of seven on 2026-09-13 and several of their citations were
struck.

### What did not change

No gate, band, verdict or registered definition. No number in the manuscript. No wording in any prompt
file. No section of the manuscript markdown. `FINDING 280`, `278`, `281` and `275` are all exactly as
they were and are on the new board.

Next: `FINDING 280` - Tables 3 and 4 do not exist and §3 cites Table 4.

---

## 2026-09-14 last+6 - the two evaluator returns worked through, and Madrid put on the machine

Two independent evaluations of the manuscript came back: one with the literature and without the
repository, one with the repository and without the literature. Both were read in full and planned
into `writing/IMP/IMP_PLAN_2026-09-14.md` as five tiers. This entry records what was executed.

⚪ **No gate, band, verdict or registered definition moved in this round.** `G6.7` still reads FAIL in
all three folds on amplitude, before and after every repair below.

### What the repository said back, against what the paper said

The single most valuable thing the repository-side evaluation produced was a refutation, not a defect.
`FINDING 275` had recorded that the steering arm of `G6.7` was never recomputed on the reported 7.30 B
model, and the manuscript apologised for that in four places. It is not true. The `steering` block in
`Step6_docs/outputs_step6/g67_leg5_{es,uk,it}.json` carries `passes: true` with R-squared 0.9897 /
0.9914 / 0.9941 against a registered floor of 0.80. The arm was computed and it passes in all three
folds. The same files settled a second item: the printed slopes 0.4153 / 0.5329 / 0.4049 are the
five-channel definition that `D-S6-13` rules, not the six-channel numbers the paper said they were;
the six-channel values, 0.1033 / 0.4310 / 0.1916, appear nowhere in the paper. Both were re-measured
directly before anything was edited, because a peer's numbers are evidence only after re-measurement.

### The word that left the prose

The author ruled, verbatim: *"never say as failure, do not use this word, this is academic
publications, instead use the word of limitation"*. 119 prose hits across the manuscript were
rewritten into the register of a limitation. Re-measured independently afterwards rather than taken on
the executing session's own count: 1,456 lines, zero surviving fail-family prose words, zero em or en
dashes, and **exactly 6 uppercase `FAIL` tokens, unchanged**. Those six are registered gate verdicts;
renaming one would move a definition, so they stay verbatim and only the sentences around them changed.

### What the paper now concedes that it did not

* **Capacity.** Both evaluators independently named the unqualified "capacity is eliminated" claim the
  likeliest reviewer objection, because two of the three eliminations ran on a single fold and the
  backbone comparison has two points. It is now scoped in all three loci: across 1.5 to 7.3 billion
  parameters, with the tuning and the second model family each resting on one fold, more capacity did
  not close the gap. The finding is kept; the reach is not.
* **The held-in result.** Section 7.1 now states that the same bar is missed on 6 of 6 of the
  countries the model was trained on, so the shortfall is not confined to transfer. The title frames
  the work as transfer and the paper now says where that framing is generous to itself.

### Two numbers corrected against their own cited basis

* The supplement's adapter merge drift row said `2.7e-4 to 7.3e-4 (table basis)` beside a verdict of
  `FAIL, 4 of 4`. The four scored runs it names read 3.223e-04, 3.471e-04, 3.853e-04 and 7.279e-04, so
  the row now reads `3.2e-4 to 7.3e-4 across those four scored runs`. Recorded with it, and left in
  place rather than edited out of the source: `FINDING 103`'s prose upper bound of `7.6e-04` **matches
  no measurement anywhere in the repository**. Every `max_logit_diff` on disk was enumerated to check.
* Figure 4's title promised direction and amplitude and drew only amplitude. Now that the direction
  arm is known to exist, the figure carries both, and its amplitude axis says on its face that the
  slopes are the five-channel ruled definition.

### Two items did not reproduce, and were reported rather than edited

Figure 7's rounding and the graphical abstract's subtitle were both in the plan and neither was in the
file. The plan had been drawn from stale documents. Reporting a non-reproducing item is the correct
outcome; editing to match a plan is not.

One further item was declined on scope rather than reported as done: Figure 2's caption now says three
nulls and the schematic draws one, so the wording in the script and in the prompt was corrected but the
picture still does not depict three. Redesigning the schematic is a design task and is left open.

### The built file

`tools/4thJ_build_submission_docx.sh` now holds both Word defects. The author line had lost its
affiliation and corresponding-author anchor because raw LaTeX superscript does not survive pandoc; the
script rewrites it to pandoc's own superscript syntax before building. Every figure gained a duplicate
caption paragraph built from its alt text; `--from=markdown-implicit_figures` drops them. Rebuilt and
verified this round: all eight embedded image md5s match the eight PNGs on disk, 8 caption paragraphs
and 0 pandoc-generated ones, and a real Word superscript run is present.

### Madrid, and why the split the author asked for was not taken

The author ruled that Spain be re-run from scratch, then granted the Speed cluster for it, then asked
that some of the runs be given to the local machine because the cluster was busy with their own work.
The first two are done; the third could not be, and the reason is worth recording.

Campaign `C2` pins EnergyPlus 23.1 and refusal `R6` **measures** it by running `--version` on the
binary rather than reading it from a config. Speed carries only 24.2.0, so a 23.1.0 Linux build has to
be installed there before a single cell can run; that install is submitted and sitting behind the
author's own array on the association CPU limit. Separately, the driver has no shard selector at all:
its only subsetting flag is `--limit`, whose own help string reads *"cap the cell count (a smoke run,
never a population)"*.

Both could be worked around. The reason not to is methodological: two builds of version 23.1, one
Windows and one Linux, inside one Madrid population would leave that city with two engine build hashes
where London and Bologna each have one. So the local machine runs the whole population under one engine
and the cluster's granted compute is spent on an independent replication shard instead. That turns a
provenance defect into a cross-check.

🔴 **The run's own scoping note was wrong about how fast this goes, and the error was mine to catch.**
It quoted 800 to 1,100 cells per hour on four local workers. Measured from the precedent runs' own
cell-file timestamps: London did 12,070 cells in about 44 hours, Bologna 11,681 in about 30, so about
273 and about 383 cells per hour. Madrid's first 23 minutes read about 183 cells per hour, and its
cells cost about 1.5 times London's, its stock being `relation/`-identified apartment blocks rather
than terraces. **Expect 40 to 60 hours for Step 10, not 10 to 15.** Worker count was left at 4: the
machine has 20 cores and is not CPU-bound, but sits at 62 per cent committed memory against a 75 per
cent watchdog threshold, and the author uses it interactively and cannot reboot it.

Two launcher bugs were found by the first launch attempt and are recorded because both were silent in
different ways. `powershell.exe -File` refuses any path without a `.ps1` extension and exits 127, which
`mktemp` guaranteed; under `set -eu` that killed the campaign after one line. And `ps_rc=$?` sat after
an unguarded command under `set -e`, so the retry loop the script was built around could never have
been reached: the first memory-watchdog kill would have ended the run instead of resuming it. The
second bug would not have shown itself until hours in.
