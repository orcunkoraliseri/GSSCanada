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
