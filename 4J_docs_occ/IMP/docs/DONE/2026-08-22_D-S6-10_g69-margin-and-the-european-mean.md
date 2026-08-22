# `D-S6-10` — `G6.9`'s margin cannot be met by ground truth, and "the European mean" had to be built

**Date:** 2026-08-22 (night)
**Raised by:** building `G6.5` and `G6.9` (`tools/4thJ_step6_g65_g69.py`) and running both arms.
**Status:** OPEN. Nothing enforced, nothing re-based. `prereg.md` untouched, md5
`e4243e07cdd80c9c846b91f40e3e8c45`.

Evidence: `Step6_docs/outputs_step6/g65_g69_corpus_calibration.json` (the real corpus) and
`g65_g69_leg4.json` (the pilot).

**Both gates are built and both arms are scored.** `G6.5` is an AND over three frozen criteria; two of
them are read out of `G6.1`'s and `G6.4`'s own artefacts by file, so `G6.5` cannot disagree with them
about a number they share. Only the sign arm is new code. On the real corpus `G6.5` scores
**7 PASS / 2 FAIL**; on the Leg-4 pilot **0 PASS / 9 FAIL**. The gate discriminates.

`G6.9` scores **0 PASS / 9 FAIL on the real corpus**, and that is the problem.

---

## Item 1 — 🔴 `FINDING 88`. `G6.9`'s margin clause is unsatisfiable by a PERFECT model.

`G6.9` is specified as: the held-out country's generated profile must be closer to its own published
tables than to any other country's, **"by a margin exceeding the between-country spread"**.

Operationalised literally — margin = (MAE to the runner-up) − (MAE to own); spread = the mean pairwise
MAE between the three published profiles — a model that reproduces the held-out country's published
table **exactly** still fails, because its margin is then one pairwise distance and the bar is the mean
of three. The nearest pair is below the mean by construction.

Measured, not argued. A perfect model's margin against the bar it would face:

| band | pairwise MAE (min/day) | mean spread | perfect `es` | perfect `uk` | perfect `it` |
|---|---|---|---|---|---|
| `Y25-44` | es-it 11.83 · es-uk 13.17 · it-uk 15.67 | 13.56 | 11.83 ❌ | 13.17 ❌ | 11.83 ❌ |
| `Y45-64` | es-it 12.67 · es-uk 16.83 · it-uk 20.50 | 16.67 | 12.67 ❌ | 16.83 ✔ | 12.67 ❌ |
| `Y_GE65` | es-it 15.17 · es-uk 23.33 · it-uk 20.17 | 19.56 | 15.17 ❌ | 20.17 ✔ | 15.17 ❌ |

**A perfect model fails 7 of 9 cells.** The real weighted corpus fails 9 of 9. This is a defect in the
operationalisation, not a result.

🟢 What the corpus arm *does* show is that the discrimination itself works: the nearest published
profile is the country's own in **8 of 9 cells**, and the corpus sits 2–7 min/day from its own table
against 11–18 from the runner-up.

### The options

| | option | consequence |
|---|---|---|
| **(a)** | 🟢 **Recommended. A scale-free margin: `(MAE_runner − MAE_own) / MAE(own_published, runner_published) > 0.5`.** | A perfect model scores 1.0; a model exactly halfway between two countries scores 0. It is a pre-registerable number with a meaning, and the 0.5 is the natural midpoint rather than a tuned constant. **Real corpus: 5 of 9 PASS. Leg-4 pilot: 2 of 9.** The three `es` cells score 0.79 / 0.98 / 0.99 |
| **(b)** | Drop the margin clause; score the argmin alone and report the margin as a number. | Literal-minded and satisfiable, but a model 1 minute nearer its own country than its neighbour's would pass, which is the confusion `G6.9` exists to detect |
| **(c)** | Keep the clause and re-define spread as the **minimum** pairwise distance. | A perfect model then lands *exactly on* the bar and fails a strict `>` — the same `>=` versus `>` knife-edge `G6.1`'s own perturbation demonstrated at margin 0.0 |

🔴 Whichever is chosen, it is **not** in `prereg.md`, which names the quantity and not its arithmetic.

### A second fact the `it` fold has to carry either way — `FINDING 89`

On `Y25-44` the **real Italian corpus** is nearer to **Spain's** published table (MAE 5.01) than to
Italy's own (10.40). That is not a modelling artefact: `D-S6-2` already established that Eurostat's
`2010` column for Italy is the **2008-09** survey while our microdata is **ISTAT 2013-14**, and ISTAT
2013-14 appears in no Eurostat table at all. 🔴 So `G6.9` on the `it` fold compares a 2013-14 corpus
against a 2008-09 table, and the working-age band is where five years of change shows. It is the
second basis asymmetry the `it` fold carries, after `D-S6-3`'s.

---

## Item 2 — "the European mean" is not published, so `G6.5` criterion 3 rests on a construction

`G6.5`'s third frozen criterion is *"the sign of the country's divergence from the European mean is
inverted"*. **Eurostat publishes no EU aggregate for `tus_00age`.** Probed 2026-08-22: the table's
`geo` dimension carries **22 countries and no `EU27`, no `EU28`, no `EA`** — AT BE BG DE EE EL ES FI FR
HU IT LT LU LV NL NO PL RO RS SI TR UK.

**Implemented:** the unweighted mean over every HETUS country with a complete level-1 profile in the
band, from `tus_00age_ALLGEO_2010_TIME_SP_T.json` (md5 `86eeb1b290519d25ab134731e3a813d2`, downloaded
and checksummed), the fold country included.

* **Not population-weighted** — that would make "European" mean Germany and Turkey. The claim is about
  a mean over national daily patterns, one country one vote.
* **Not the two donor countries** — a mean of two makes the sign of a divergence a coin toss.
* **Fold country included** — self-inclusion attenuates a divergence by at most 1/n with n ≈ 20, below
  the rounding floor of the published `h:mm` strings.

An aggregate is scored only where the **published** divergence exceeds `SIGN_FLOOR_MIN = 2.0`
min/day; below that the published value's own rounding swamps the sign. Aggregates under the floor
are reported as `not_scored`, and not scored is not a pass.

**Confirm or replace.** Under the implemented basis the real corpus inverts a sign in 2 of 9 cells
(`es Y45-64` on `AC3`, `it Y25-44` on `AC1_TR` — the same 2008-09 table as `FINDING 89`), and the
Leg-4 pilot inverts in 7 of 9.

---

## 🟢 Both gates have been seen failing, and one perturbation is a declared no-op

Run on the **corpus** arm, because a gate already failing at baseline cannot be seen to fall:

| perturbation | fells | notes |
|---|---|---|
| `null` | nothing | |
| `shift25` (+25 % on `AC3`, mass returned to `AC0`) | `G6.5` in 6 cells, **all 6 by the sign arm alone** | |
| `invert_sign` (reflect the model through the European mean) | `G6.5` in 7 cells, **all 7 by the sign arm alone** | this is the perturbation the val doc names for the sign arm, and it moves `G6.4` not at all — a rigid motion about the mean |
| `neighbour_tables` (score the fold against a donor's tables) | 🔴 **nothing** | it cannot fell `G6.9` while `G6.9` is already failing every cell. It becomes live the moment item 1 is ruled |

🔴 So the coverage clause currently reads **FAIL**, honestly: `G6.5` has been seen failing and
`G6.9` has not. That is reported as a FAIL rather than dressed up, and item 1 is what fixes it.

---

## Answer box

> **`D-S6-10` Item 1 (`G6.9` margin clause):** (a) scale-free margin $> 0.5$ / (b) drop margin clause / (c) minimum pairwise  → **(a) Scale-free relative margin $> 0.5$ — `(MAE_runner - MAE_own) / MAE(own_pub, runner_pub) > 0.5`.**
>
> **`D-S6-10` Item 2 (European mean construction):** (confirm / replace)  → **CONFIRM — Unweighted mean over all complete HETUS countries with `SIGN_FLOOR_MIN = 2.0` min/day.**

---

## Author's Rulings & Directives (2026-08-22)

| # | Item / Decision | Ruled Option | Summary of Decision | Action Required |
|---|---|---|---|---|
| **1** | `G6.9` Margin Clause (`FINDING 88`) | 🟢 **Option (a)** | **Adopt scale-free relative margin with threshold $> 0.5$**: $\frac{\text{MAE}_{\text{runner}} - \text{MAE}_{\text{own}}}{\text{MAE}(\text{own\_pub}, \text{runner\_pub})} > 0.5$. | Implement in `tools/4thJ_step6_g65_g69.py`; resolves the mathematical impossibility where a perfect model failed 7/9 cells; enables `neighbour_tables` perturbation to fell `G6.9`. |
| **2** | `G6.5` European Mean Construction | 🟢 **Confirmed** | **Unweighted mean across all 22 HETUS countries** with complete level-1 profiles in the band, including the fold country, with **`SIGN_FLOOR_MIN = 2.0` min/day**. | Preserves democratic national weighting (1 country, 1 vote) rather than population dominance; protects against sign flipping under rounding noise. |

---

### Detailed Rulings and Directives

#### 1. Item 1 (`G6.9` Nearest-Neighbour Discrimination Margin) — Ruled: Option (a)
* **Choice**: Replace the flawed absolute margin with the scale-free normalized margin:
  \[
  \text{Margin}_{\text{norm}} = \frac{\text{MAE}(\text{gen}, \text{pub}_{\text{runner}}) - \text{MAE}(\text{gen}, \text{pub}_{\text{own}})}{\text{MAE}(\text{pub}_{\text{own}}, \text{pub}_{\text{runner}})} > 0.5
  \]
* **Scientific Rationale**:
  1. Under the literal pairwise mean formulation, a ground-truth model that perfectly replicates its target published table fails 7 of 9 cells because the distance to the closest neighbor is strictly less than the mean distance across all pairs ($11.83 < 13.56$).
  2. The scale-free relative margin is mathematically sound: a perfect model achieves $1.0$, an equidistant model achieves $0.0$, and $0.5$ represents the unambiguous midpoint threshold where the model is at least three times closer to its own country than to the competitor.
  3. Validated on empirical data: real corpus passes 5/9 cells (with Spain at 0.79 / 0.98 / 0.99), while Leg-4 pilot scores only 2/9.
  4. Unblocks the coverage clause: allows the `neighbour_tables` perturbation to execute and demonstrate `G6.9` failing.

#### 2. Item 2 (`G6.5` Sign Inversion vs European Mean) — Confirmed
* **Choice**: Confirm the unweighted mean over all complete HETUS reporting countries from `tus_00age_ALLGEO_2010_TIME_SP_T.json` with a 2.0 min/day noise floor.
* **Scientific Rationale**:
  1. Eurostat publishes no aggregate EU/EA total for `tus_00age`.
  2. An unweighted mean across all available HETUS countries ensures that "European baseline" reflects the distribution of European national time-use patterns without being distorted by large-population outliers.
  3. The `SIGN_FLOOR_MIN = 2.0` min/day threshold ensures robust evaluation by ignoring marginal deviations that fall within Eurostat's rounding grain.

---

⚪ `prereg.md` md5 `e4243e07cdd80c9c846b91f40e3e8c45` remains untouched and verified. Nothing is running on Speed.
