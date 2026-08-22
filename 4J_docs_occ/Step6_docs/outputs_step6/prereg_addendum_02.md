# Pre-registration ADDENDUM 02 — the two secondary nulls, `G6.2` and `G6.3`

**Written 2026-08-22. The author's rulings on `D-S6-6` (a) — §1–§5 — and on `D-S6-7` (a) — §5b:
dated sidecar addenda, not edits.**

⚪ **Re-frozen 2026-08-22 (night) when §5b was added.** The `D-S6-6`-only version of this file had md5
`db450b89abbaf8f5480eb2479d50ae2d`; the current md5 is in the sidecar. §1–§5 are unchanged from that
version. `D-S6-7` was raised *by* the `D-S6-6` rebuild and rules on the same six-plus-three nulls, so
it belongs in this file rather than an addendum 03.

🔴 **`prereg.md` IS NOT EDITED BY THIS DOCUMENT.** It stays frozen at md5
`e4243e07cdd80c9c846b91f40e3e8c45`, its sidecar `prereg.md.md5` is untouched, and `G4.14` is
unaffected — it recomputes `prereg.md`'s hash from disk and keeps matching. This file is the "new
dated document" that `prereg.md`'s own STATUS section requires when something must be added after the
freeze. It is the second such file, beside `prereg_addendum_01.md` (the raking collapses).

🔴 **THIS IS A POST-REGISTRATION REINTERPRETATION AND IS NOT PRESENTED AS PRE-REGISTERED.** What is
reinterpreted is a null's **name**, not its construction, its role or any threshold. The claim made
here is the narrow, checkable one: it is registered **before any fold has been scored**. No Step 6
score exists on disk for any country as of this date, and no synthetic diary has been generated.

---

## 1. What `prereg.md` says, and what it does not say

`prereg.md:110-112`, verbatim:

> | null | strength | role |
> |---|---|---|
> | Pooled all-country average diary | weak | secondary, reported |
> | **Nearest-neighbouring-country model** | **moderate** | **secondary; answers the geographic-proxy objection** |
> | Real diaries from the N−1 pool, raked by IPF onto the held-out country's published marginals | **strongest** | 🔴 **THE PRE-REGISTERED BAR** |

That is the whole of it. **No rule for choosing the neighbour is registered** — not in `prereg.md`,
not in `4thJ_06_transfer.md`, not in the parent overview. The gate row
(`4thJ_06_transfer_val.md:31`) reads *"`G6.2` Margin over the nearest-neighbour-country model |
Geographic proxy | **Reported** | `RL06`"* — a **reported** null with no threshold.

## 2. Why the rule was never written, and why it now cannot be

It did not need to be written. The design at freeze time had **four** countries including **France**,
which shares a land border with **both Spain and Italy**, so every fold had an obvious neighbour.

**Author decision 16 (2026-08-15) excluded France.** The consequences, each measured rather than
asserted:

* **The donor pool per fold is two countries**, and for the `uk` fold neither Spain nor Italy is
  anybody's idea of a nearest neighbour.
* 🔴 **No fold has a land-border neighbour inside its pool.** Spain borders France, Portugal, Andorra,
  Morocco and Gibraltar; the UK borders Ireland; Italy borders France, Switzerland, Austria,
  Slovenia, San Marino and the Vatican. France was the country that made the strict rule work.
* 🔴 **Great-circle distance does not determine an answer either.** Computed on the WGS-84 sphere:

  | basis | `es` fold → | `uk` fold → | `it` fold → |
  |---|---|---|---|
  | capital cities | **`uk`** (1263 vs 1364 km) | `es` (1263 vs 1434) | `es` (1364 vs 1434) |
  | approx. population centroids | 🔴 **`it`** (1331 vs 1409) | `es` (1409 vs 1444) | `es` (1331 vs 1444) |
  | approx. geometric centroids | 🔴 **`it`** (1409 vs 1561) | `es` (1561 vs 1660) | `es` (1409 vs 1660) |

  The `es` fold's neighbour **flips** between bases, and the capital-versus-centroid choice is itself
  unregistered — so the rule does not remove the free choice, it moves it one level down and hides
  it. The three capitals span 1263/1364/1434 km, a spread of 13 %, so the winning margin is 70–170 km
  on ~1,300 km. "Nearest" is not a meaningful relation among these three countries.

* 🔴 **The choice is not cosmetic.** It moves the null's donor base by up to **2.41×**: on the `es`
  fold, `uk` supplies 15,854 diaries and `it` supplies 38,260.

**Choosing a neighbour now — after the corpus, the folds and the populations are all built — would be
choosing a null's strength after the fact**, which is the same class of defect `G6.2` exists to
answer.

## 3. The ruling: (a), report every donor country, nominate none

**`G6.2` is built for EVERY country in the fold's donor pool — two per fold, six in total — and all
six are reported. The word "nearest" is dropped.** The gate is read as *"margin over the
single-donor-country nulls"*.

Why this and not a registered rule:

1. **It removes a degree of freedom instead of registering one.** There is nothing left to choose, so
   the objection this whole decision is about cannot be raised.
2. **It is strictly more informative than any single pick.** If the model merely mapped the held-out
   country onto one donor, the null built from *that* donor is the one that becomes near-unbeatable —
   and reporting both is exactly how a reader sees it. A single nomination can only ever show one.
3. **It is the logic the pre-registration already accepted for this attack.** `G6.9`
   (`4thJ_06_transfer_val.md:47`) requires the held-out country's generated profile to be closer to
   its own published tables than to **any** other country's. Compare against all, nominate none.
4. **It costs nothing.** The machinery was already built and guarded.

⚪ **What is NOT changed by this ruling:** the null's construction (donors at their own survey
weights, **not raked** — `prereg.md` permits raking in exactly one place), its strength label
(*moderate*), its role (*secondary; answers the geographic-proxy objection*), and its threshold
(*Reported*). `G6.1`, `G6.3` and `G6.9` are untouched.

🔴 **Rejected, and recorded as rejected:** choosing the neighbour by **measured similarity of time
use**. It would make `G6.2` the strongest single-country null available and it would be chosen using
the outcome variable, on data, after the fact — selecting the test on the result.

## 4. What is registered, exactly

`tools/4thJ_step6_secondary_nulls.py`, `REGISTERED_NEIGHBOURS`:

| fold | registered donor countries | nulls built |
|---|---|---:|
| `es` | `it`, `uk` | 2 |
| `uk` | `es`, `it` | 2 |
| `it` | `es`, `uk` | 2 |

**Enforced, not asserted.** The module refuses a fold this file does not cover; refuses a donor
country not registered for that fold; refuses a donor country that is the held-out country; and — the
guard that *is* this ruling — **refuses to nominate one donor when a fold registers more than one**,
naming `D-S6-6` (a) and directing the caller to `build_all_neighbours()`. All four are seen refusing
in `tools/4thJ_step6_secondary_nulls_selftest.py` (**42 of 42 green**).

## 5. The result on disk, and what it revealed

`Step6_docs/outputs_step6/secondary_nulls.json`, md5 `5bb023e51a3e5c4eb1a7e97b6d79ed66`. Six `G6.2`
nulls, all built, none scored:

| fold | donor | donors | ESS | worst strata gap vs the target population |
|---|---|---:|---:|---:|
| `es` | `it` | 38,260 | 38.9 % | 14.7639 pp |
| `es` | `uk` | 15,852 | 70.5 % | 🔴 **30.7305 pp** |
| `uk` | `es` | 19,140 | 58.0 % | 9.7688 pp |
| `uk` | `it` | 38,260 | 38.9 % | 12.1025 pp |
| `it` | `es` | 19,140 | 58.0 % | 9.6249 pp |
| `it` | `uk` | 15,852 | 70.5 % | 🔴 **31.0235 pp** |

🔴 **The two nulls of one fold differ by up to 3.2× in distance from the target** (`it` fold: `es`
9.62 pp, `uk` 31.02 pp). Under any single-nomination rule, one of those two numbers would have been
the whole of `G6.2` and the other invisible. That is the concrete case for (a).

🔴 **And reporting both is what exposed `FINDING 78`.** On the `es` fold, the *pooled* null `G6.3`
(14.7629 pp, ESS 14,868) and the *`it`-only* null (14.7639 pp, ESS 14,866) are the same null to four
decimal places — because the three surveys' weights are not on one scale. `weight_dia_cal` sums to
1.625e8 for ES and 1.628e8 for IT (population-grossing) but to **15,919.8 for the UK** (mean 1.0043,
scale-free). The pooled null therefore carries **99.99 %** Italian mass on the `es` fold and **99.99 %**
Spanish mass on the `it` fold. A single nominated neighbour would have had an even chance of hiding
it. **`FINDING 78` is `D-S6-7` and is NOT ruled by this addendum;** it is reported by the builder on
every run and repaired nowhere.

## 5b. 🟢 `D-S6-7` RULED (a), 2026-08-22 (night) — the pooled null's basis is EQUAL COUNTRY MASS

**The ruling, verbatim in effect:** each donor country's `weight_dia_cal` values are renormalised to
sum to **1.0** *before* the pool is formed, so every donor country contributes the same total mass
and, **within** a country, the survey weights keep their exact relative values.

Why: it removes the scale artefact of §5 — the ~**10,000 : 1** ratio between Spain's and Italy's
population-grossing weights and the UK's scale-free ones, which crushed the UK to **0.0098 %** on the
`es` and `it` folds — while preserving the within-country weighting that `D-S6-4` chose and that
`FINDING 53` requires (the three countries' diary weights hit three different day bases). It restores
`G6.3` to a genuine all-country baseline instead of a duplicate of one `G6.2`.

🔴 **This is a basis change, ruled by the author, and it is NOT raking.** Nothing is solved for, no
held-out marginal is read, and no diary's weight is fitted to a target — one arbitrary factor is
removed and nothing else. `prereg.md` still permits raking in exactly one place, `G6.1`.

⚪ **Declared cost:** a Spanish diary now counts ~1.21× a UK diary within the pooled null, because
15,852 UK and 19,140 Spanish diaries share the mass equally. That is a stated convention, not a
hidden one. Options (b) population-proportional, (c) unweighted and (d) declare-only were considered
and rejected; the reasons are in `IMP/docs/2026-08-22_D-S6-7_pooled-null-weight-scale.md` §5.

**What it moved, measured (`secondary_nulls.json`, rebuilt):**

| fold | `G6.3` worst gap, before → after | ESS, before → after | donor mass after |
|---|---|---|---|
| `es` | 14.7629 → **14.1839 pp** | 14,868 → 25,514 | `it` 50.00 %, `uk` 50.00 % |
| `uk` | 10.1901 → **10.1883 pp** | 25,436 → 25,429 | `es` 50.00 %, `it` 50.00 % |
| `it` | 9.6242 → **14.8304 pp** | 11,110 → 22,280 | `es` 50.00 %, `uk` 50.00 % |

🟢 **`G6.3` is no longer a duplicate of a `G6.2`.** On `es` it is 14.1839 pp against the `it`-only
null's 14.7639 pp; on `it` it is 14.8304 pp against the `es`-only null's 9.6249 pp. Before the ruling
those pairs agreed to four decimals. **Step 6 ships three independent nulls per fold, not two.**

🟢 **All six `G6.2` nulls are unchanged to the last decimal** — every one is single-country, so a
constant scale factor cancels exactly on renormalisation. That was predicted in the decision document
before the rebuild and is confirmed by it. **`G6.1` is untouched:** it starts from a uniform seed
(`4thJ_step6_rakeddonor.py:169`, `D-S5-10` (a)) and never reads a survey weight, so
`prereg_addendum_01.md` stands.

⚪ **`uk` moved by 0.0018 pp**, which is the check on the story: that fold was already a real mixture
because ES and IT happen to gross to almost the same national total, so equalising them changes almost
nothing there and a great deal on the other two folds.

**Enforced, not asserted.** `equal_country_mass()` is applied **unconditionally** in `build_pooled()`
— never triggered by the dominance flag, because a basis that switches itself on when the numbers look
bad is a basis chosen after the fact — it refuses a donor country carrying zero total mass, and the
`FINDING 78` flag is now a **check that the ruling was applied** rather than a description of the
defect. All of it is seen firing in `tools/4thJ_step6_secondary_nulls_selftest.py` (**55 of 55
green**, was 42).

## 6. What would invalidate this addendum

* A Step 6 score for any fold found to predate this file.
* **A `G6.2` null built for a fold/donor pair this file does not register.** Enforced by
  `REGISTERED_NEIGHBOURS`; the refusal names the unregistered pair.
* **Any `G6.2` result reported for a fold without its sibling.** Reporting one of the two is the
  nomination this ruling removed, and it is the one failure mode the code cannot catch downstream.
* A `G6.2` null that has been raked. It may not be; only `G6.1` may.
* **A `G6.3` number quoted from before 2026-08-22 (night)** — `es` 14.7629 pp and `it` 9.6242 pp
  describe a one-country pool wearing a pooled label and are superseded by §5b. `uk` 10.1901 pp is
  sound but is superseded too, by 10.1883 pp.
* **A pooled `G6.3` whose donor mass is not 1/k per country.** The builder prints the composition on
  every run and flags it; a flagged pooled null means the ruling was not applied.

---

**Frozen on write. Its md5 lives in the sidecar `prereg_addendum_02.md.md5`, not inside this file,
for the same reason `prereg.md`'s does: a file cannot contain its own hash.**
