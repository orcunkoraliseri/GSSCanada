# `D-S6-7` — for the author, 2026-08-22

## The three surveys' weights are not on the same scale, so `G6.3`'s "pooled all-country" null is 99.99 % one country on two folds of three

**Scope** one decision, in full. Nothing in this file changes any artefact.
`prereg.md` md5 `e4243e07cdd80c9c846b91f40e3e8c45` is untouched and stays untouched whatever is ruled.

| | |
|---|---|
| **Raised by** | the `D-S6-6` (a) rebuild, 2026-08-22 — building both single-country nulls beside the pooled one is what made it visible |
| **Blocks** | `G6.3` only |
| **Does not block** | `G6.1`, `G6.2`, `G6.9`, the claim, or the FAIL criteria — see §4 |
| **Record** | `Step6_docs/impl/2026-08-22_secondary-nulls.md`, `prereg_addendum_02.md` §5 |
| **Status of the artefact** | `secondary_nulls.json` md5 `5bb023e51a3e5c4eb1a7e97b6d79ed66` reports the composition on every run and **repairs nothing** |

---

## 1. The measurement

`weight_dia_cal`, summed over all 73,252 weighted diaries, by country:

| country | diaries | Σ `weight_dia_cal` | mean weight | max weight |
|---|---:|---:|---:|---:|
| `ES` | 19,140 | **162,500,706.02** | 8,490.11 | 89,052.28 |
| `IT` | 38,260 | **162,800,375.82** | 4,255.11 | 48,422.28 |
| `UK` | 15,852 | 🔴 **15,919.83** | **1.0043** | 7.23 |

🔴 **Spain and Italy carry population-grossing weights. The UK carries a scale-free weight with mean
1.** The ratio of total mass is about **10,000 : 1**. It is the same in every weight column
(`weight_ind`, `weight_dia`, `weight_dia_a`, `weight_dia_b`, `weight_dia_cal`), so it is a property of
the **source microdata**, not of `weight_dia_cal`, not of `D-S6-4`, and not of anything built in this
project.

## 2. What that does to `G6.3`

The pooled null takes every donor at its own survey weight and renormalises. With those totals, the
donor countries' shares of the pooled null are:

| fold | pooled null composition | verdict |
|---|---|---|
| `es` | 🔴 `it` **99.9902 %**, `uk` 0.0098 % | it is the Italian null |
| `uk` | `es` 49.9539 %, `it` 50.0461 % | 🟢 a genuine mixture |
| `it` | 🔴 `es` **99.9902 %**, `uk` 0.0098 % | it is the Spanish null |

And the summary statistics confirm it is not a near-miss — on the `es` fold the pooled null and the
`it`-only null agree to four decimal places:

| `es` fold | worst strata gap | ESS |
|---|---:|---:|
| `G6.3` pooled | 14.7629 pp | 14,868 |
| `G6.2` donor `it` alone | 14.7639 pp | 14,866 |

🔴 **On two folds of three, `G6.3` and one of the `G6.2` nulls are the same object under two names.**
The UK's 15,852 real diaries contribute **0.0098 %** of the mass — arithmetically present, materially
absent.

⚪ Why the `uk` fold escapes: its pool is ES + IT, and those two happen to gross to almost the same
total (1.6250e8 vs 1.6280e8). That is a coincidence of two national populations, not a property of
the method.

## 3. 🔴 Why this was not caught before, and what caught it

Nothing in the pooled null's own output could show it. ESS, the heaviest-diary share and the
strata gaps are all computed on the normalised weights, and every one of them looked ordinary
(`es` ESS 27.5 %, heaviest diary 0.0297 %). The defect is only visible **by comparison** — and the
comparison exists because `D-S6-6` was ruled **(a)**, which built the single-country nulls and put
them on the same page. A single nominated neighbour would have had an even chance of being the *other*
country and hiding it completely.

⚪ This is the second time a null's summary statistics have looked healthy while the null was wrong:
`FINDING 52` had `max_dev_pp` at 5.6e-15 with 16.67 % of the pool silently deleted.

## 4. 🟢 What is NOT affected — checked, not assumed

* **`G6.1`, the pre-registered bar, is untouched.** `tools/4thJ_step6_rakeddonor.py:169` starts from
  `weights = [1.0] * len(donors)` — a **uniform** seed (`D-S5-10` (a)) — and rakes from there. The
  raked null never reads a survey weight, so no number in `prereg_addendum_01.md` or in the
  2026-08-21 `G6.1` build moves.
* **All six `G6.2` nulls are unaffected.** Each is built from one country, and a constant scale factor
  cancels exactly on renormalisation. The six numbers in `prereg_addendum_02.md` §5 stand.
* **`G6.9`, and therefore reviewer attack 3, is unaffected.** It compares generated profiles to
  published tables, not to survey weights.
* **Steps 1–5 are unaffected** in every place that uses weights **within** one country, which is
  every place they are used. The defect appears only when countries are **pooled**.

🔴 **What IS affected:** the three `G6.3` numbers recorded on 2026-08-21 (`es` 14.7629 pp,
`uk` 10.1901 pp, `it` 9.6242 pp) and the ESS figures beside them. They are correct arithmetic on a
pool that is not what its label says. **The `uk` one is sound; the `es` and `it` ones describe a
one-country null.**

## 5. The options

### 🟢 (a) — RECOMMENDED: renormalise each country's weights to sum to 1 before pooling; equal country weight

Each donor country contributes the same total mass, and within a country the survey weights keep
their exact relative values.

* **Why:** the pooled null's role in `prereg.md` §5 is *"pooled all-country average diary"* — the word
  is **all-country**, and equal country mass is the only reading under which it is true on every fold.
  It also makes the null's composition a **property of the design** (three countries, LOCO) rather
  than of whichever national statistical office chose to gross its weights.
* **Cost, stated:** a Spanish diary then counts ~2× a UK diary within the null, because 15,852 UK
  diaries and 19,140 Spanish diaries share the mass equally. That is a *declared* convention, not a
  hidden one.
* **On the `uk` fold it changes almost nothing** (49.95/50.05 → 50/50), so `G6.3 uk` stays comparable
  to what is already recorded.

### ⚪ (b) — Renormalise to each country's population; population-proportional pooling

Scale each country's weights so its total equals its census population.

* **Why:** it is what the ES and IT weights already do, and "the average European diary" is a
  defensible object.
* 🔴 **Cost:** it needs a population figure per country from outside the diary data, on a basis that
  must then be registered (`D-S5-5` restricted everything to **private households**; the census-round
  frame is `D-S5-1`). It re-imports the whole marginals-basis question into a *secondary, reported*
  null. And the result is dominated by the largest country by construction, which is the shape of the
  defect rather than its opposite.

### ⚪ (c) — Weight each country by its number of diaries; pool the raw diaries unweighted

* **Why:** simplest possible statement, and it is what a reader assumes "pooled" means.
* 🔴 **Cost:** it throws away the survey weights entirely, and `FINDING 53` is exactly why that is not
  free here — the three countries' diary weights hit three different day bases (`uk`
  71.45/14.32/14.24, `es` 50/25/25, `it` 33/33/33), so an unweighted pool is a null about **weekends**,
  unequally per fold. This option was already rejected once, when `D-S6-4` chose `weight_dia_cal`.

### ⚪ (d) — Change nothing; report `G6.3` with its composition declared

* **Why:** it is a *reported* secondary null with no threshold, it cannot fail the claim, and the
  composition is now printed on every run and recorded in the JSON.
* 🔴 **Cost:** the paper would carry a null labelled "pooled all-country" that is 99.99 % one country
  on two folds of three, and would be relying on a footnote to prevent the obvious misreading. It also
  makes `G6.3` and one `G6.2` **the same number reported twice**, which inflates the apparent number
  of independent nulls from three to two.

## 6. What each ruling costs to apply

| ruling | work | what has to be re-run |
|---|---|---|
| **(a)** | one function, additive, plus a selftest section | the builder (seconds, local); `G6.3`'s three numbers are replaced; `prereg_addendum_02.md` gains a §, or an addendum 03 |
| **(b)** | (a)'s work, plus a registered population figure per country and its provenance | the same, plus a Step 5-style source note |
| **(c)** | trivial | the same, and `D-S6-4` must be reopened |
| **(d)** | nothing | nothing |

⚪ In every case `prereg.md` is untouched, and `G6.1`, `G6.2`, `G6.9` are unaffected. **Nothing is
scored, so nothing has to be discarded** — which is the only reason this is a decision and not a
retraction.

---

## Answer box

> **`D-S6-7`:**  (a) equal country mass / (b) population-proportional / (c) unweighted /
> (d) declare only  → **(a) Equal country mass — renormalise each country's survey weights to sum to 1 before pooling (50/50 donor mass per fold).**

---

## Author's Ruling & Directives (2026-08-22)

| Decision | Ruled Option | Summary of Decision | Action Required |
|---|---|---|---|
| **`D-S6-7`** | 🟢 **Option (a)** | **Equal country mass per donor country** (renormalise each donor country's survey weights to $\sum w = 1$ prior to pooling, giving 50/50 total mass per fold). | Update `tools/4thJ_step6_secondary_nulls.py` to normalise weights within country before pooling; recompute `G6.3` numbers; document in `prereg_addendum_02.md` §5 (or addendum 03). |

---

### Detailed Rulings and Directives

#### 1. Choice: Option (a) — Equal Country Mass Pooling
* **Specification**:
  Prior to forming the pooled donor pool for `G6.3`, each donor country $c \in \text{Donors}(\text{fold})$ has its diary weights renormalised:
  \[
  w_{i, c}^{\text{pooled}} = \frac{w_{i, c}}{\sum_{j \in c} w_{j, c}}
  \]
  such that $\sum_{i \in c} w_{i, c}^{\text{pooled}} = 1.0$ for each donor country, yielding an exact $50\% / 50\%$ country mass contribution in the 2-donor LOCO setting.
* **Scientific Rationale**:
  1. **Preserves intra-country survey weighting**: Within each country, the relative survey weights (`weight_dia_cal`) that correct for day-of-week sampling imbalances (`FINDING 53`) are strictly preserved.
  2. **Eliminates grossing scale artefact**: Corrects the 10,000:1 scale disparity between grossed population weights (Spain, Italy) and unit-mean weights (UK) that previously resulted in 99.99% single-country dominance on the `es` and `it` folds.
  3. **True to the pre-registered definition**: Restores `G6.3` as a genuine "pooled all-country" baseline rather than an inadvertent duplicate of `G6.2`.
  4. **Preserves `uk` fold stability**: On the `uk` fold (where Spain and Italy grossed to almost identical sums), the balance moves from 49.95/50.05 to 50.00/50.00, keeping existing results stable.

#### 2. Scope & Invariants
* **Untouched**:
  - `G6.1` (the primary raked-donor null) remains untouched (it uses uniform seeds $w=1.0$ and IPF raking).
  - All six `G6.2` single-country nulls remain untouched (scale factors cancel identically in single-country normalisation).
  - `G6.9` remains untouched.
  - `prereg.md` remains frozen (md5 `e4243e07cdd80c9c846b91f40e3e8c45` unchanged).

#### 3. Implementation Steps
1. Update `tools/4thJ_step6_secondary_nulls.py` with country-level weight normalisation in the pooled null builder.
2. Re-run `secondary_nulls.py` and its selftest to update `secondary_nulls.json`.
3. Record the equal-mass pooling rule in `Step6_docs/outputs_step6/prereg_addendum_02.md` §5.

---

⚪ `prereg.md` md5 `e4243e07cdd80c9c846b91f40e3e8c45` is unchanged. Nothing is running on Speed.

---

## EXECUTION RECORD — applied 2026-08-22 (night), all three implementation steps

| # | directive | done |
|---|---|---|
| 1 | country-level normalisation in the pooled builder | `equal_country_mass()` in `tools/4thJ_step6_secondary_nulls.py`, called **unconditionally** in `build_pooled()` |
| 2 | re-run the builder and its selftest | selftest **55 of 55** (was 42); `secondary_nulls.json` rebuilt |
| 3 | record the rule in `prereg_addendum_02.md` | new **§5b**, and the file re-frozen |

**Artefacts:** `tools/4thJ_step6_secondary_nulls.py` md5 `e79918f62e64c836ac6479a4d265da2e`, `_selftest.py` `6a2737f8883ab00d9baea23955565998`, `Step6_docs/outputs_step6/secondary_nulls.json` `d4ce5e2f8345bc147d8d297f8f9606d7`. `prereg_addendum_02.md` re-frozen at
`fa1e4524f52c36ec82f02f825d6ff149` (its `D-S6-6`-only version was `db450b89abbaf8f5480eb2479d50ae2d`); §1–§5 unchanged.
🔴 `prereg.md` md5 `e4243e07cdd80c9c846b91f40e3e8c45` **UNCHANGED**; all three sidecars `md5sum -c`
**OK**.

### What moved

| fold | `G6.3` worst strata gap | ESS | donor mass |
|---|---|---|---|
| `es` | 14.7629 → **14.1839 pp** | 14,868 → 25,514 | `it` 50.0000 %, `uk` 50.0000 % |
| `uk` | 10.1901 → **10.1883 pp** | 25,436 → 25,429 | `es` 50.0000 %, `it` 50.0000 % |
| `it` | 9.6242 → **14.8304 pp** | 11,110 → 22,280 | `es` 50.0000 %, `uk` 50.0000 % |

### The two invariants in §2 were CHECKED against the rebuild, not assumed

* 🟢 **All six `G6.2` nulls are byte-identical to the pre-ruling run** — gaps 14.7639 / 30.7305 /
  9.7688 / 12.1025 / 9.6249 / 31.0235 pp and every ESS unchanged. Single-country, so the scale factor
  cancels exactly. This document predicted it before the rebuild; the rebuild confirms it.
* 🟢 **`uk` moved by 0.0018 pp**, which is the check on the whole story: that fold was already a real
  mixture because ES and IT gross to almost the same national total.
* 🟢 `G6.1` never reads a survey weight (`4thJ_step6_rakeddonor.py:169`), so
  `prereg_addendum_01.md` stands untouched.

### 🟢 The defect is gone, and the count of independent nulls is restored

`G6.3` no longer coincides with any `G6.2`: on `es` it is **14.1839** pp against the `it`-only null's
14.7639; on `it` it is **14.8304** pp against the `es`-only null's 9.6249. `pool_dominated_by` is
`null` on all three folds. **Step 6 ships three independent nulls per fold, not two.**

### Guards, seen firing

1. `equal_country_mass()` **refuses** a donor country carrying zero total weight instead of dividing
   by it — the `FINDING 52` failure mode (a silent zero deleted 16.67 % of a pool and the report
   showed a residual of 5.6e-15).
2. The equalisation is applied **unconditionally**, and the selftest reads the module source to prove
   the dominance flag never triggers it. *A basis that switches itself on when the numbers look bad is
   a basis chosen after the fact.*
3. The `FINDING 78` flag is re-pointed: it now means **"the ruling was not applied — do not quote this
   null"**, and it is seen firing on a constructed 99.99 % pool.
4. The source label carries `EQUAL COUNTRY MASS (D-S6-7 (a))`, and `score_margin`'s Guard 1 refuses to
   compare two nulls whose `marginals_source` differs — so a pre-ruling `G6.3` number cannot be quoted
   against a post-ruling one.

### One number this changed that nobody asked about

The selftest's §6 hand-computed case (a null-weight donor excluded) read `0.2 / 0.8` on the raw survey
weights and now reads `0.5 / 0.5`: after the exclusion the pool is one UK diary and one Italian diary,
so equal country mass makes them equal. It was **left failing first**, then the expectation was
rewritten with the old value recorded beside it. It is the smallest place where the ruling is visible.

### WHAT I DID NOT VERIFY

* Nothing is scored — there is still no model output, so no `G6.2`/`G6.3` **margin** exists for any
  fold. These are constructions and their distances from the target population, nothing more.
* The claim that the ~10,000:1 ratio is a property of the source microdata rests on the five weight
  columns of `harmonised.parquet`; the original national deposits were not re-opened.
