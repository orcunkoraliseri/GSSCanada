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
| **G6.2** Margin over the nearest-neighbour-country model | Geographic proxy | Reported | `RL06` |
| **G6.3** Margin over the pooled all-country average | The weak null | Reported, **secondary** | `RL08`, demoted |
| **G6.4** Level-1 time budgets vs published tables | Gross wrongness | MAPE ≤ **15.0 %** | **project-chosen** |
| **G6.5** 🔴 Pre-registered FAIL criteria | Gate-shopping after the fact | Fails the claim if **any** of: MAE ≥ raked-donor null; MAPE > 20 %; **the sign of the country's divergence from the European mean is inverted** | **project-chosen**, frozen |
| **G6.6** Regression on held-**in** countries | Forgetting | Bounded; small by construction under joint training | `RL05` |

---

## THE THREE ATTACK GATES — WHERE THE CLAIM IS ACTUALLY DEFENDED

| ID | Attack | Requirement |
|---|---|---|
| **G6.7** Fictional-country control | *"It read about the country on the web"* | Generate under a **fictional country token with perturbed marginals**. Output must **follow the conditioning vector**, not a national stereotype. Quantified: the generated time budget must track the perturbation with slope ≥ **0.8** and the residual against any real country's profile must not be the smallest for a country whose token was not used 🟢 **RULED 2026-08-20, decision item 5 (a), APPLIED: `enc_country()` in `tools/encoder.py` now takes `allow_synthetic_controls=False`. A fictional token must BOTH match `^x_[a-z]{2,16}$` — an `x_` prefix no ISO code has and no corpus value can collide with — AND be asked for by keyword, per call. The production whitelist `{es, uk, it}` is unchanged and the default is off, so `4thJ_step3_build.py` and every other caller keep the old behaviour unedited; the builder is checked for the keyword and does not carry it. `FINDING 41` closed: `G6.7` is runnable.** |
| **G6.8** Joint-structure scores | *"It echoes the marginals"* | Score quantities **never in the prompt**: co-presence cross-tabs, transition entropy, dwell-time distributions conditioned on **attribute pairs**. All must clear their Tier 1 and Tier 2 thresholds on the held-out country |
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
