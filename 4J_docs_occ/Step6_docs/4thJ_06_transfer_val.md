# Step 6 — Transfer. Validation.

### 4J HETUS LLM pipeline. Validation specification.
#### Implementation: `4thJ_06_transfer.md`. Parent: `../4thJ_00_HETUS_LLM_Pipeline.md`

---

## STATUS

**OPEN. Nothing run.** Every threshold below is pre-registered and freezes into
`outputs_step6/prereg.md` before the first fold.

---

## WHAT THIS STEP MUST PROVE

That the model beat the **hard** null on a country it never saw, and that it did so for the right
reason.

The second clause is most of the work. A model can beat the null by echoing the marginals it was
given, by having read about the country during pretraining, or by mapping it onto its neighbour.
Each of those is a way of passing the headline while failing the claim.

---

## TIER 4 GATES — THE HEADLINE

| ID | What it detects | Threshold | Provenance |
|---|---|---|---|
| **G6.1** 🔴 Margin over the **raked-donor null** | The claim itself | **Must be positive.** Pre-registered before the run | `RL06`, author decision 4 |
| **G6.2** Margin over the **single-donor-country nulls** — 🟢 `D-S6-6` (a), ruled 2026-08-22, DROPPED the word *nearest*: **every** donor country in the fold's pool is built and reported (**two per fold, six in all**), none is nominated. `prereg_addendum_02.md` | Geographic proxy | Reported | `RL06` |
| **G6.3** Margin over the pooled all-country average, **EQUAL COUNTRY MASS** — 🟢 `D-S6-7` (a), ruled 2026-08-22: each donor country renormalised to sum 1.0 before pooling, because the three surveys' weights are NOT on one scale (`FINDING 78`) and the raw pool was 99.99 % ONE COUNTRY on the `es` and `it` folds. `prereg_addendum_02.md` §5b. 🔴 NEVER quote the pre-ruling numbers (`es` 14.7629 / `uk` 10.1901 / `it` 9.6242 pp) | The weak null | Reported, **secondary** | `RL08`, demoted |
| **G6.4** Level-1 time budgets vs published tables | Gross wrongness | MAPE ≤ **15.0 %** | **project-chosen** |
| **G6.5** 🔴 Pre-registered FAIL criteria | Gate-shopping after the fact | Fails the claim if **any** of: MAE ≥ raked-donor null; MAPE > 20 %; **the sign of the country's divergence from the European mean is inverted** | **project-chosen**, frozen |
| **G6.6** Regression on held-**in** countries | Forgetting | Bounded; small by construction under joint training | `RL05` |

---

## THE THREE ATTACK GATES — WHERE THE CLAIM IS ACTUALLY DEFENDED

| ID | Attack | Requirement |
|---|---|---|
| **G6.7** Fictional-country control | *"It read about the country on the web"* | Generate under a **fictional country token with perturbed marginals**. Output must **follow the conditioning vector**, not a national stereotype. Quantified: the generated time budget must track the perturbation with slope ≥ **0.8** and the residual against any real country's profile must not be the smallest for a country whose token was not used 🟢 **RULED 2026-08-20, decision item 5 (a), APPLIED: `enc_country()` in `tools/encoder.py` now takes `allow_synthetic_controls=False`. A fictional token must BOTH match `^x_[a-z]{2,16}$` — an `x_` prefix no ISO code has and no corpus value can collide with — AND be asked for by keyword, per call. The production whitelist `{es, uk, it}` is unchanged and the default is off, so `4thJ_step3_build.py` and every other caller keep the old behaviour unedited; the builder is checked for the keyword and does not carry it. `FINDING 41` closed: `G6.7` is runnable.** |
| **G6.8** Joint-structure scores | *"It echoes the marginals"* | Score quantities **never in the prompt**: co-presence cross-tabs, transition entropy, dwell-time distributions conditioned on **attribute pairs**. All must clear their Tier 1 and Tier 2 thresholds on the held-out country 🟢 **CHECKER BUILT 2026-08-21, `tools/4thJ_step6_g68_joint.py` + `_selftest.py`, 17/17 green, SEEN FAILING under the registered shuffled-diary control (dwell W1 111.9 min against a 10.0 band, transitions 64.7/day against 1.50, TVD 0.318 against 0.050) while the marginal arm passes EXACTLY (budget error 0.000 min, diurnal JSD 0.000 bits). No quantity was designed and no band moved — every threshold is read from the Overview's Tier 1 table.** 🔴 **`FINDING 68` + AUTHOR RULING (a), 2026-08-21 — THE PER-CELL VERDICT BASIS.** Applied per attribute-pair cell, the absolute Tier 1 bands fail on REAL data: a second real Italian sample fails **65 of 68 cells** (dwell W1 median **9.80 min** against the 10.0 min band; diurnal JSD fails 65/68). The bands are population-level and the cells are n ≥ 100, so at cell granularity they sit **below the finite-sample noise floor** and a perfect model fails them. **The per-cell verdict is therefore taken on the already-registered sample-size-matched comparison** — Overview, statistical discipline: *"a sample-size-matched bootstrap, where the synthetic-to-real divergence must not exceed the real-to-real split-half divergence. That last comparison is the honest one."* **Calibrated, not asserted:** real-vs-real gives **18 of 68 cells** with ≥ 1 exceedance against an analytic null expectation of **17.3**, and the shuffled control gives **68 of 68** and **317 of 408 metric exceedances** against **19.4**. 🔴 **The absolute Tier 1 bands are NOT dropped** — they are enforced at POPULATION level, where real-vs-real is comfortably inside every one of them (dwell 2.03 min, transitions 0.076, TVD 0.0087, JSD mean 0.00044 bits) |
| **G6.9** Nearest-neighbour discrimination | *"It mapped the country to its neighbour"* | The held-out country's generated profile must be **closer to its own published tables than to any other country's**, by a margin exceeding the between-country spread |

🔴 **G6.8 is the gate that carries the most weight and looks the least like a headline.** Marginals
were handed to the model. Joints were not. A model that matches marginals and fails joints has
learned the prompt, and no amount of G6.1 margin repairs that.

---

## 🔴 THE COUNTERFACTUAL EACH GATE ACTUALLY DISCRIMINATES

Before quoting any gate as evidence, name what it separates the model from — and **check the untreated
control's value, not only the treated one.**

| Gate | Separates the model from | Does **not** separate it from |
|---|---|---|
| G6.1 | reweighted real donors | a model that memorised the marginals |
| G6.4 | a grossly wrong model | the raked-donor null (which also passes G6.4 comfortably) |
| G6.8 | a marginal-echoer | a model contaminated by pretraining |
| G6.7 | a contaminated model | a model that is simply bad |

**No single gate here defends the claim. The set does, and only if each is reported with what it
cannot see.**

---

## PRIVACY GATES, FROM `RL10`

| ID | Attack | Fails if |
|---|---|---|
| **G6.10** | Loss-based MIA | AUC > **0.65**, or TPR at 0.1 % FPR > 5 % |
| **G6.11** | Reference-based MIA vs the public base model | AUC > **0.75** |
| **G6.12** | Prefix-prompted extraction, greedy and sampled | any exact match on a stratum with < 5 training records |
| **G6.13** | DCR and NNDR on the synthetic release | any DCR = 0; median DCR to train significantly below median DCR to test; NNDR < 0.33 in > 0.1 % of records |

**Three controls, and they are what make the numbers readable:** the untuned base model (expect
AUC ≈ 0.50), a random-label-permutation adapter (the floor for pure sequence memorisation), and a
train-vs-test perplexity gap under 5 %.

---

## 🟢 STRUCTURAL-BINNING GATE — `G6.14`, REGISTERED 2026-08-21

**Author ruling, 2026-08-21: `G6.14` is a REAL GATE, not a diagnostic.** It gets a row, a
threshold, a provenance label and a perturbation, and it falls under the "every gate seen failing"
discipline like every other. 🔴 **`G6.1`–`G6.13` and `G6.5`'s frozen FAIL criteria are untouched.**

| ID | What it detects | Threshold | Provenance |
|---|---|---|---|
| **G6.14** Hour-support constancy | A time-of-day table binned on the wrong **frame**: the number of contributing diaries is not the same in every slot, so a "profile" is an average over different populations at different hours | **support_min / support_max = 1.000 EXACTLY**, over diaries whose durations sum to 1440 | 🔴 **project-chosen** — nobody publishes this; it is a completeness invariant we choose to assert, and it must never be cited as literature-derived |

**The gap it fills.** Every battery we run is **episode-based**: durations sum to 1440, round-trips
are exact, codes are legal, the 145-state tally automaton enforces the budget. **A table binned on
the wrong frame passes all of them**, because the error is in support per slot and in no total.
`D-S2-5` set our origin to 04:00 cyclic, so we do not have the bug — but nothing we ran would have
told us if we reintroduced it, and an untested invariant is not an invariant.

**Perturbation, and it was SEEN FELLING IT.** Bin one fold onto a 00:00–24:00 **wall-clock frame**
instead of the cyclic 04:00 one — the diary runs 04:00 → 28:00, is placed at its true wall-clock
time, and the part past midnight is dropped rather than wrapped. Measured on `it`, 38,260 diaries:
support falls to **exactly zero in slots 0–23** (the first four hours) and nowhere else, ratio
**0.0000**, gate **FAILS**. At baseline it reads **38260 / 38260 = 1.0000** in all 144 slots, and
every one of the 16 scored conditioning cells passes at baseline and fails under the perturbation.

🔴 **A ROTATION IS NOT THIS DEFECT, and one run was spent establishing it.** Reading the diary's
minute 0 as wall-clock 00:00 rotates every profile four hours out of place — plainly wrong — and
**`G6.14` correctly passes it**, 38260/38260. The gate scores **support**, not alignment; the
alignment claim rests on `D-S2-5` and not on this gate. Recorded so `G6.14` is never quoted for
more than it detects.

🔴 **It scores the BINNING, not the generator.** Generated diaries routinely stop short
(`sum_1440_frac` 0.05–0.135), so their coverage curve is legitimately ragged — that is `FINDING 67`,
measured by `at_home_mae_pp_covered`. The checker **REFUSES** rather than scores when its input does
not sum to 1440, so it can never fail for the generator's reason.

**Implementation:** `tools/4thJ_step6_g614_hoursupport.py`, selftest
`tools/4thJ_step6_g614_selftest.py`, **9 of 9 green**.

---

## ⚪ FIRST-ORDER MARKOV COMPARATOR — REPORTED ALONGSIDE `G6.1`, NEVER A FAIL CRITERION

**Author ruling, 2026-08-21: add it, reported not thresholded.** 🔴 **It is not a bar, it is not in
`G6.5`, and `G6.5` is frozen.** The module refuses to emit a pass/fail verdict at all.

Our nulls are **stronger** than what the literature asks for — the raked-donor null rakes real N−1
diaries onto the held-out country's own published marginals. Nothing is missing on rigour. But the
comparator a reviewer will name by default was absent: for a generative occupancy model the field's
standard baseline is a **first-order inhomogeneous Markov chain fitted to the same microdata**
(Richardson, Thomson & Infield 2008; Widén & Wäckelgård 2010; Wilke 2013). Adding it makes the
raked-donor null read as a deliberate strengthening rather than an idiosyncratic choice.

**Fitted:** 10 HETUS Level-1 states, inhomogeneous in the 10-minute slot, **one chain per
`strat_day_type`** (weekday/weekend chains are standard in this lineage), unseen transitions backing
off to the slot's own marginal — **no smoothing parameter**, because a baseline whose value is
having no free parameters should not acquire one. It is deliberately **not** given the demographic
prefix the model gets: a baseline handed the same conditioning is a second model, not a baseline.

**Measured, fold `it`** (fitted on `es` + `uk`, 34,994 diaries; sampled 38,260):

| quantity | comparator | Tier 1 band |
|---|---|---|
| diurnal JSD, mean | 0.0248 | ≤ 0.015 |
| time-budget error, max | 36.97 min | ≤ 15.0 stratum / 8.0 population |
| **dwell-time W1, max** | **119.56 min** | ≤ 10.0 |
| transitions/day, error | **0.264** | ≤ 1.50 |
| transition-matrix TVD | 0.0863 | ≤ 0.050 |

⚪ **The shape of that result is the useful part.** The chain reproduces the transition *rate*
almost exactly — it is fitted on slot-to-slot transitions, so it must — and misses the dwell-time
*distribution* by an order of magnitude. That is the classic first-order Markov failure and it is
exactly what `G6.8`'s dwell-time arm exists to see.

🔴 **One asymmetry is stated rather than left implicit:** the sampler emits exactly 1440 minutes by
construction, so the comparator can never lose coverage the way a generated diary can. On any
coverage-sensitive statistic this **favours the comparator**.

**Implementation:** `tools/4thJ_step6_markov_comparator.py`.

---

## EVERY GATE MUST BE SEEN FAILING

| Perturbation | Must fail | Must stay clean |
|---|---|---|
| Score the **raked-donor null against itself** as if it were the model | **G6.1 must report exactly zero margin** — and a `<= 0` comparison would pass it. 🔴 The comparison must be strict `>` | G6.4 |
| Shift the generated time budget by 25 % on one category | G6.4, G6.5 (MAPE arm) | G6.9 |
| Invert the sign of the country's divergence from the European mean | **G6.5 (sign arm)** | G6.4 — *this is exactly why the sign arm exists separately* |
| Generate from a model trained **including** the held-out country | G6.10, G6.11 — and 🔴 **G6.1 will IMPROVE**, which is the point: the headline gate moves the wrong way under contamination | — |
| Replace generated diaries with the country's real diaries | **G6.12, G6.13** | G6.1 (it will pass spectacularly) |
| Feed the fictional country the real country's marginals | **G6.7** | G6.8 |
| Permute co-presence within strata | **G6.8** | G6.1, G6.4 — *marginals are preserved exactly, joints are destroyed* |
| 🟢 **Shuffled diary, ACROSS diaries at a fixed slot** (the registered sequence-destruction control) | **G6.8's sequence arm — all three: dwell W1 111.9 min, transitions 64.7/day, TVD 0.318** | **G6.8's marginal arm, EXACTLY** — *budget error 0.000 min, diurnal JSD 0.000 bits. 🔴 The within-diary variant does NOT qualify: permuting a diary against itself also destroys the population day-shape (JSD 0.178 bits) and so cannot "PASS Tier 1 marginals". "Slots permuted, totals preserved" was ambiguous; the across-diary construction is the one that satisfies the requirement as written* |
| 🟢 **Bin one fold on the 00:00–24:00 wall-clock frame** | **G6.14** — *support 0 in slots 0–23, ratio 0.0000* | everything else — *and note a mere ROTATION (`--origin 0`, cyclic) fells nothing, correctly: G6.14 scores support, not alignment* |
| Score the held-out country against its neighbour's tables | G6.9 | G6.4 |
| Train sequentially by country | G6.6 | G6.1 |
| 🔴 **Null perturbation: change nothing** | **nothing** | everything |

### Coverage clause

Cross-tab every perturbation against baseline; **FAIL the probe if any passing gate was never made to
fall.** 🔴 **Report, per band gate, which END it failed at.** A gate that reads "28 of 56 in band"
before and after, while all 28 turned over from below-floor to above-ceiling, is a gate whose diff
would have said "no change" about an inversion.

---

## STATISTICAL DISCIPLINE, AND IT IS NOT OPTIONAL AT THIS N

At 10⁵ to 10⁶ generated diaries **every two-sample test rejects**: a 1.2 min/day difference in meal
preparation gives p < 10⁻¹⁵ while being practically perfect.

🔴 **No gate in this document is a p-value.** Each is a bounded effect size, and each is additionally
reported as:

* a **TOST equivalence test** against a ±15 min/day margin, and
* a **sample-size-matched bootstrap**, where the synthetic-to-real divergence must not exceed the
  **real-to-real split-half divergence**.

That last comparison is the honest one: it asks whether we are further from the truth than the truth
is from itself.

---

## VACUITY GUARDS

* **V6.a** — the scorer **imports** its thresholds and its band definitions from the frozen
  `prereg.md` module. 🔴 A second copy of a threshold drifts invisibly, and the copy that drifts is
  always the one being quoted.
* **V6.b** — the scorer and the gate must consume the **same table**. Before scoring any delta,
  assert that the file path the scorer reads equals the one the gate reads. In 3J two adjacent
  scorers disagreed by 26.5 % and, fatally, disagreed about which of heating and cooling was larger.
* **V6.c** — G6.1's comparison is strict (`margin > 0`), never `>= 0`. **A prediction of movement
  must not be satisfiable by nothing moving.**
* **V6.d** — the runner FAILs if fewer than **3** folds (🔴 CORRECTED 2026-08-20 from **4** — see progress log; France excluded by decision 16) were scored, or if any fold's held-out
  country appears in its own training set — an assertion, run per fold, not a comment.
* **V6.e** — `prereg.md`'s md5 is checked at scoring time against the value recorded before the first
  fold. **A pre-registration that can be edited after the results are seen is not a pre-registration.**

---

## WHAT THIS STEP'S VALIDATION DOES **NOT** COVER

* It does **not** cover downstream energy. Steps 8 and 9 own that, and a model that passes every gate
  here can still produce schedules that behave badly in a building model.
* It does **not** cover structural validity of generated text — Step 7, and the distinction is sharp:
  100 % validity after masking is a property of the decoder, not the model.
* 🔴 It does **not** establish that transfer generalises beyond four Western and Southern European
  countries. That is limitation C4 and no gate here can close it. **The claim must be written at the
  scale the corpus supports**, and if Track A lands the same gates run again at seventeen.
* 🔴 It does **not** rule out that the model's advantage comes from pretraining exposure to European
  daily life generally, rather than to the specific held-out country. G6.7 tests the country-specific
  version of that confound; the general version is limitation B1 and is pre-registered as a confound
  rather than resolved.

---

## PROGRESS LOG

Append-only.

### 2026-08-14 — validation document created

* Thirteen gates, ten perturbations, none run.
* 🔴 The perturbation worth noticing is *"train including the held-out country"*: **the headline gate
  G6.1 improves.** Every check that could catch it is a privacy gate. That is the shape of the
  failure this step most needs to survive — the one where the number gets better.

### 2026-08-20 — 🔴 **`V6.d` REQUIRES FOUR FOLDS. THE DESIGN HAS THREE. AS WRITTEN, THIS GUARD FAILS EVERY COMPLETE RUN OF STEP 6.**

Found by reading, not by running — no scorer exists yet, so nothing has failed and nothing was
re-scored. Recorded here because the guard is a **runner assertion**, and a runner assertion that can
never be satisfied is indistinguishable, in its own output, from the failure it exists to catch.

**The text, unchanged above at line 136:** *"the runner FAILs if fewer than **4** folds were scored."*

**The design, from the FROZEN `prereg.md`:** three. Author decision 16 (2026-08-15) excluded France;
`prereg.md` §2 line 71 reads *"LOCO trains on TWO, not three"*, §8 is titled *"The reporting clause —
all three folds, including the worst"*, and §11 line 312 records *"rotation over three countries"* with
its provenance. **The frozen file is correct. This validation document is the stale one.**

#### The correction, and its exact scope

| | before | after |
|---|---|---|
| `V6.d` fold-count arm | *fewer than **4** folds* → FAIL | *fewer than **3** folds* → FAIL |
| `V6.d` self-containment arm | *any fold's held-out country appears in its own training set* | **unchanged** |

🔴 **The guard is RE-POINTED, not removed.** Its purpose — catching a run that silently scored fewer
folds than the design has — is intact and still needed; only the count was stale. Deleting it because
it was wrong would trade a guard that always fires for no guard at all, which is the worse of the two.

🔴 **`prereg.md` WAS NOT EDITED.** Verified at the time of writing: md5
`e4243e07cdd80c9c846b91f40e3e8c45`, matching its sidecar. The fold count was never *in* the frozen
file as a guard — see the next paragraph, which is the more serious finding.

#### 🔴 The finding underneath the finding: **none of the `V6.*` guards are frozen**

`V6.a` requires the scorer to *"import its thresholds and its band definitions from the frozen
`prereg.md` module"*, on the argument that **a second copy of a threshold drifts invisibly, and the
copy that drifts is always the one being quoted.** A grep for `V6.`, `vacuity` and `assert` over
`prereg.md` returns **nothing**: the vacuity guards live only in this editable document.

So the guards that protect the pre-registration are themselves outside it. `V6.d` drifting from four
folds to three is the demonstration — it is exactly the drift `V6.a` predicts, one level up, and it
went unnoticed for five days because no document holds the guards to the frozen one.

**This is NOT proposed as a `prereg.md` edit.** The file is frozen and `G4.14` is live; editing it
fails every Step 4 run at once. The guards stay here, and the standing requirement is that **the
scorer, when it is written, asserts each `V6.*` guard's parameters against `prereg.md` at run time**
rather than carrying them as literals — which is `V6.a`'s own rule applied to `V6.a`'s own neighbours.

#### What this does and does not change

* **No threshold moved.** `G6.1`–`G6.13` are untouched; this is a fold **count**, not a bar.
* **No result is affected** — Step 6 has never been run, and its `outputs_step6/` holds only
  `prereg.md`, its sidecar, and the D-S6-1 household re-split report.
* **Still open and unrelated:** the §5 **raked-donor null** — `G6.1`'s actual bar — has never been
  built, and `FINDING 39`/`D-S6-3` (2026-08-20) remain open against §6's `MAPE` arm.

### 2026-08-21 (evening) — 🟢 **`G6.8`'s CHECKERS EXIST AND WERE SEEN FAILING; `G6.14` IS REGISTERED AND WAS SEEN FAILING; THE MARKOV COMPARATOR IS FITTED.** 🔴 **`FINDING 68`: THE TIER 1 BANDS ARE NOT EVALUABLE AT CELL LEVEL, AND THE AUTHOR RULED THE BASIS.**

Executed from `IMP/2026-08-21_review-derived-improvements.md` §8, boxes 5, 6 and 7, under the
author's ruling that the whole improvement plan runs before any further Step progress. Full
implementation state, including every number and every non-verification, is in
**`Step6_docs/impl/2026-08-21_g68-g614-markov.md`** — this entry is the summary, not a replacement.

🔴 **`prereg.md` md5 `e4243e07cdd80c9c846b91f40e3e8c45` is untouched. No `G6.1`–`G6.13` threshold
moved. `G6.5`'s FAIL criteria are frozen and nothing entered them.**

**`I-3` — `G6.8`.** There was no gate to design: `4thJ_06_transfer_val.md:44` registered the gate
and the Overview's Tier 1 table registered every band it inherits. Only the checker was missing, and
`grep` of `tools/` confirmed none existed. Built as `tools/4thJ_step6_g68_joint.py` with
`_selftest.py`, **17 of 17 green**. Fold `it`, 38,260 real diaries:

| comparison | dwell W1 max | transitions/day err | transition TVD | budget err | diurnal JSD mean |
|---|---|---|---|---|---|
| REAL vs REAL split-half | **2.026** | **0.076** | **0.0087** | 2.384 min | 0.00044 bits |
| 🔴 shuffled ACROSS diaries | **111.9** | **64.658** | **0.3180** | **0.000000000** | **0.000000000000** |
| band | ≤ 10.0 | ≤ 1.50 | ≤ 0.050 | ≤ 8.0 | ≤ 0.015 |

The registered control does exactly what the Overview requires: **fells all three sequence arms and
preserves both marginal arms to machine zero.**

🔴 **`FINDING 68`, and it was only found because the checker was run on REAL data first.** Applied
per attribute-pair cell (n ≥ 100 both sides), the absolute Tier 1 bands fail on a **second real
sample** in **65 of 68 cells** — dwell W1 median **9.80 min** against a **10.0 min** band, diurnal
JSD failing 65 of 68. At n ≥ 100 the population-level bands sit **below the finite-sample noise
floor**, so a perfect model fails them. 🟢 **Author ruled (a):** the per-cell verdict is taken on the
**already-registered sample-size-matched real-real comparison**, which the Overview pre-registered
and nobody had implemented; the absolute bands stay and are enforced at **population level**, where
real-vs-real is comfortably inside all of them. **Calibrated:** real-vs-real **18 of 68** cells with
≥ 1 exceedance against an analytic null of **17.3**; the shuffled control **68 of 68** and **317 of
408** metric exceedances against **19.4**.

⚪ **Two readings of the registered controls were settled by running them.** (1) *"Shuffled diary
(slots permuted, totals preserved)"* is ambiguous: permuting a diary against itself also destroys
the population day-shape (JSD 0.178 bits) and so cannot "PASS Tier 1 marginals" — only the
**across-diary** construction does. Both are built; the across-diary one is the control. (2) **Modal
collapse does not fell `G6.8`'s transitions arm** (0.143/day) and must not: a modal day is a real
day. Collapse is **Tier 2**'s job, and `G6.8` may never be quoted against it.

**`I-2` — `G6.14` REGISTERED AS A REAL GATE** (author ruling), with a row, a band
(support_min/support_max = 1.000 exactly), a **project-chosen** provenance label and a perturbation
**seen felling it**: binning fold `it` onto the 00:00–24:00 wall-clock frame drops support to
**exactly zero in slots 0–23 and nowhere else**, ratio 0.0000. Baseline reads **38260/38260 =
1.0000** in all 144 slots and all 16 scored cells. ⚪ A pure **rotation** does *not* fell it, and
correctly so — `G6.14` scores support, not alignment; that rests on `D-S2-5`. Incomplete diaries are
**REFUSED**, so the gate can never fail for the generator's reason instead of the binner's.
`tools/4thJ_step6_g614_hoursupport.py` + `_selftest.py`, **9 of 9 green**.

**`I-4` — the first-order inhomogeneous Markov comparator**, fitted per fold on the N−1 training
countries and **reported alongside `G6.1`, never a FAIL criterion**; the module refuses to emit a
verdict at all. Fold `it`, fitted on `es`+`uk` (34,994 diaries, three day-type chains), 38,260
sampled: diurnal JSD 0.0248 · budget err 36.97 min · **dwell W1 119.56 min** · **transitions err
0.264** · TVD 0.0863. ⚪ It reproduces the transition **rate** almost exactly and misses the
dwell-time **distribution** by an order of magnitude — the classic first-order failure, and the
clearest single argument for scoring dwell times at all. 🔴 Its sampler emits exactly 1440 minutes
by construction, so on any coverage-sensitive statistic the comparison **favours the comparator**;
stated, not left implicit.

🔴 **Not verified:** all of the above is fold `it` only; **no generated diaries were scored by
anything**, because Step 6 generation does not exist; the comparator has not been run against the
raked-donor null; and `G6.8`'s co-presence and transition-entropy quantities are computed and
reported but not scored, because Tier 1 registers no band for either.

---

### 2026-08-26 — `G6.8` IS NO LONGER A GATE WITH AN UNRUN ARM

`G6.8`'s registered spec — *"Score quantities NEVER IN THE PROMPT: co-presence cross-tabs,
transition entropy, dwell-time distributions conditioned on ATTRIBUTE PAIRS. All must clear their
Tier 1 and Tier 2 thresholds on the held-out country"* — had been demonstrated only on its two
negative controls. The arm that scores an actual model against an actual held-out country had
never run on either leg. It has now run on all three Leg-5 folds and on both weight bases.

🔴 **SEQUENCE FAIL and MARGINAL FAIL in every fold.** The verdicts do not move between
`weight_dia_cal` and unweighted. `G6.8` therefore joins `G6.1`, `G6.4`, `G6.5`, `G6.6`, `G6.7` and
`G6.9` on the FAIL side, and the board's Step 6 tally must count it as a scored FAIL, not as an
un-run gate.

🔴 **It is a fourth reading of one failure, not a fourth failure.** `G6.8` was registered to
answer "the model only echoes the marginals". It returns no answer, because the marginal arm fails
too: the model matches neither the structure the prompt withheld nor the structure the prompt
supplied. Reporting it as independent corroboration of `G6.1` would be counting the same
measurement twice.

⚪ The two registered negative controls remain the proof the checker discriminates: split-half
PASS/PASS, `shuffled_across` FAIL sequence / PASS marginal. Without that pair a FAIL here would be
unreadable.

⚪ `D-S3-14`'s UK-fold split report is filed alongside; the model half is reported **un-quantified**
under that decision's own fallback clause, because no diary in the `strat_hh_type = unknown` cell
was ever generated. Record:
`Step6_docs/impl/2026-08-26_g68-model-arm-and-uk-split-report.md`.
