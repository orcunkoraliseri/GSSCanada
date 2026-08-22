# Step 6 work item 6.2 — the two SECONDARY nulls — implementation state

Task doc:   `Step6_docs/4thJ_06_transfer.md` §6.2 ("Build the three nulls"); the two missing
            ones were recorded as owed at `4thJ_06_transfer.md:881`.
Status:     🟢 **DONE, AND NOTHING IN ITEM 6.2 IS WAITING ON ANYONE.** `D-S6-6` RULED
            (a) 2026-08-22 and APPLIED — `G6.2` builds SIX nulls, two per fold. The
            rebuild exposed `FINDING 78`; `D-S6-7` was RULED (a) the same evening and is
            APPLIED too — `G6.3` now pools at EQUAL COUNTRY MASS. Three nulls of three.

---

## Ledger

| what | where | state |
|---|---|---|
| `tools/4thJ_step6_secondary_nulls.py` | new | 🟢 written |
| `tools/4thJ_step6_secondary_nulls_selftest.py` | new | 🟢 **30 of 30 green**, every guard seen firing |
| `Step6_docs/outputs_step6/secondary_nulls.json` | new | 🟢 written, md5 `bc9f53bb04e0a911649fdb6c552399ca` |
| `G6.3` pooled all-country average null | all three folds | 🟢 **BUILDS** |
| `G6.2` nearest-neighbour-country null | all three folds | 🔴 **REFUSES — `D-S6-6`** |

No cluster job. Everything here is local and reads only files already on disk.

---

## What was built, and why it is this shape

`G6.1` fixed the shape of a null in this project: **a weighting over the real N−1 donor diaries.**
The raked null solves for weights that reproduce the held-out country's strata. The two secondary
nulls do not solve for anything, and that is exactly what makes them weaker on purpose:

* **`G6.3` pooled all-country average** — every donor in the N−1 pool at its **own survey weight**,
  renormalised. No raking. It ignores the held-out country's demographics completely.
* **`G6.2` nearest-neighbour country** — the same, restricted to **one** donor country.

🔴 **Neither is raked, and that is a rule not an omission.** A raked pooled null is the raked-donor
null under a different name; reporting it as a second, independent null would be reporting the same
bar twice. `prereg.md` permits raking in exactly one place.

**Weight basis `weight_dia_cal`**, by `D-S6-4`. `FINDING 53` is why it matters more here than
anywhere else: the three countries' raw diary weights hit three different day bases
(`uk` 71.45/14.32/14.24, `es` 50/25/25, `it` 33/33/33), so an unweighted pooled null would be a null
about weekends, and unequally so per fold.

⚪ **Nothing is scored.** There is no model output yet. Like `4thJ_step6_g61_rake_folds.py` before
it, this answers the question that comes first: can the null be **constructed**, and once built,
**how weak is it?**

---

## Verified — numbers actually read, and where from

Source: `secondary_nulls.json`, written by the run of 2026-08-22.
Weight table: 73,252 keys from `Step2_docs/outputs_step2/harmonised.parquet`.

### `G6.3` builds on all three folds

| fold | donors | ESS | ESS % | heaviest diary | **worst strata gap vs the target population** |
|---|---:|---:|---:|---:|---:|
| `es` | 54,112 of 54,114 | 14,868 | **27.5 %** | 0.0297 % | 🔴 **14.7629 pp** |
| `uk` | 57,400 of 57,400 | 25,436 | **44.3 %** | 0.0274 % | 🔴 **10.1901 pp** |
| `it` | 34,992 of 34,994 | 11,110 | **31.7 %** | 0.0548 % | 🔴 **9.6242 pp** |

🔴 **`G6.1` is ≤ 0.5000 pp on every variable BY CONSTRUCTION.** The pooled null is **19× to 30×**
further from the population it is a null for. That is the first quantification of *how much* weaker
the secondary null is, and it is the number that keeps `G6.3` honestly secondary: beating it is a
much smaller claim than beating `G6.1`, and the paper must not let the two sit in one sentence.

### 🔴 `FINDING 77` — the `es` fold's widest gap is a category the target population does not have

| fold | widest gap | in the null | in the target |
|---|---|---:|---:|
| `es` | `strat_econ_status = homemaker` | **14.76 %** | **0.00 %** |
| `uk` | `strat_econ_status = employed` | 42.89 % | 53.09 % |
| `it` | `strat_econ_status = retired` | 14.14 % | 23.76 % |

`FINDING 51`: the Spanish census `RELA` has no *Labores del hogar*, so `D-S5-4`(b) fitted `population_es.csv`
on **five** economic bands and it contains **no homemakers at all** — while 14.76 % of the `es` fold's
donor pool is homemaker. The raked null met this as an orphan and it is why registered collapse **B**
(`homemaker → other_inactive`) exists. **The pooled null is not raked, so nothing refuses: the
mismatch is simply carried.** It must therefore be *declared* rather than fixed — collapsing it here
would make `G6.3` a partially-raked null, which is the one thing it may not be.

⚪ Note the direction: the widest gap on **all three** folds is an economic-status column, not age or
sex. Economic status is where the three countries' populations actually differ.

### ⚪ A counterintuitive measurement, recorded because it will otherwise be misread

Effective sample size, pooled versus raked, on the same pools:

| fold | `G6.3` pooled ESS | `G6.1` raked ESS |
|---|---:|---:|
| `es` | 27.5 % | 49.5 % |
| `uk` | 44.3 % | 59.4 % |
| `it` | 31.7 % | **76.8 %** |

**Raking *increased* effective sample size on every fold.** The raw survey weights are more dispersed
than the raking factors that reproduce a target from them, so the *stronger* null also rests on
*more* diaries. `FINDING 62`'s warning ("a null can be arithmetically perfect and rest on 68
diaries") points the other way here, and neither number may be quoted as though low ESS made a null
weak on its own.

### The two null-weight diaries

`UK / 12110816_2`, days 1 and 2, carry `NaN` in **every** weight column of `harmonised.parquet`
(`weight_ind`, `weight_dia`, `weight_dia_a`, `weight_dia_b`, `weight_dia_cal`) — checked directly, so
this is a survey gap, **not** a `weight_dia_cal` construction artefact and not basis-dependent. They
are **excluded and counted**, following `G6.8`'s precedent (73,252 scored, 2 null excluded). They are
UK diaries, so they touch only the `es` and `it` folds.

---

## 🔴 `D-S6-6` — OPEN, FOR THE AUTHOR: which country is the "nearest neighbour"?

`prereg.md` §5 names a **"nearest-neighbouring-country model"** and **defines no rule for choosing
the neighbour.** It did not need one when it was written: the design then had **four** countries
including **France**, which borders both Spain and Italy, so every fold had an obvious neighbour.
**Author decision 16 (2026-08-15) excluded France.** The pool per fold is now two countries, and for
the `uk` fold neither Spain nor Italy is anybody's idea of a nearest neighbour.

🔴 **Picking one now — after the corpus, the folds and the populations are all built — is choosing a
null's strength after the fact**, which is the same defect `G6.2` exists to answer. So
`REGISTERED_NEIGHBOURS` ships **empty**, `G6.2` **refuses on all three folds**, and the refusal names
this decision. It is seen refusing in the selftest and in the live run.

**What the ruling must supply: a RULE, not three country codes.** Candidate bases, none chosen here:
shared land border (fails for `uk` outright); great-circle distance between population centroids;
a published cultural/regional grouping (e.g. Eurostat's North/South/West); or **drop `G6.2` and
declare it undeliverable under a three-country design** — which is defensible, because the null it
answers ("the model mapped the country onto its neighbour") is weaker when no fold *has* a neighbour.

⚪ Whatever is ruled goes in a dated sidecar, `Step6_docs/outputs_step6/prereg_addendum_02.md`,
beside `prereg_addendum_01.md`. `prereg.md` is frozen and cannot carry it.

---

## Decisions taken here, and what they were based on

1. **Secondary nulls are not raked.** From `prereg.md` §5's own sentence that raking is permitted in
   exactly one place. Not a judgement call.
2. **Weight basis `weight_dia_cal`.** `D-S6-4`, already ruled.
3. **Null source weight → exclude and count; unkeyed donor → refuse.** The two are different and the
   module keeps them apart. `_g68.load_weights` drops nulls silently, which would make a respondent
   the survey never weighted indistinguishable from a join that missed, so this module reads the
   weight table itself and keeps both sets.
4. **`G6.2` refuses rather than guesses.** See `D-S6-6`.

---

## WHAT I DID NOT VERIFY

* **Nothing is scored, and no gate verdict is produced.** `G6.2` and `G6.3` are *reported* nulls by
  `RL08`/author decision; the gates that read them cannot run until generated diaries exist, which is
  Step 7's deliverable.
* The distance-to-target numbers are computed on the **five prefix strata only**
  (`strat_age_band`, `strat_sex`, `strat_hh_type`, `strat_econ_status`, `strat_day_type`), the same
  five `G6.1` rakes on. Joint structure is not measured here; that is `G6.8`.
* The selftest's arithmetic is checked against hand-computable answers on a four-diary corpus, not
  against the module's own output. It does **not** test the live corpus path beyond the fact that the
  live run completes.

---

## Next

`G6.3` is done. `G6.2` waits on `D-S6-6`. **Everything else in Step 6 — work items 6.3 (run the
folds), 6.4 (score) and 6.5 (privacy audit) — waits on generated diaries, which is Step 7's
deliverable, not Step 6's.** Step 6's Definition of Done moves to **item 2 partially: two nulls of
three built** (raked-donor + pooled), the third blocked on the author.


---

# 🟢 EXECUTION RECORD — `D-S6-6` RULED (a) AND APPLIED, 2026-08-22

**The author ruled `D-S6-6` option (a)** on the strength of
`IMP/docs/2026-08-22_D-S6-6_neighbour-null.md`: build the single-donor-country null for **every**
country in the fold's pool, report them all, and **drop the word "nearest"**. Registered in the dated
sidecar `Step6_docs/outputs_step6/prereg_addendum_02.md` (md5 `db450b89abbaf8f5480eb2479d50ae2d`,
sidecar `prereg_addendum_02.md.md5`). ⚪ `prereg.md` md5 `e4243e07cdd80c9c846b91f40e3e8c45`
**unchanged**, verified before and after; all three sidecars `md5sum -c` **OK**.

## Ledger — what is on disk now

| what | md5 | state |
|---|---|---|
| `tools/4thJ_step6_secondary_nulls.py` | `0e2df0ca8d0fd4a02145b356a9be53bb` | 🟢 registry populated, `build_all_neighbours()` added |
| `tools/4thJ_step6_secondary_nulls_selftest.py` | `1e8a5a3880250af68762368e99f78b11` | 🟢 **42 of 42 green** (was 30) |
| `Step6_docs/outputs_step6/secondary_nulls.json` | `5bb023e51a3e5c4eb1a7e97b6d79ed66` | 🟢 3 pooled + **6** per-donor nulls |
| `Step6_docs/outputs_step6/prereg_addendum_02.md` | `db450b89abbaf8f5480eb2479d50ae2d` | 🟢 written, frozen, sidecar written |
| `Step6_docs/outputs_step6/prereg.md` | `e4243e07cdd80c9c846b91f40e3e8c45` | ⚪ untouched |

No cluster job. Everything local; nothing is scored.

## The six `G6.2` nulls

| fold | donor | donors | ESS | ESS % | worst strata gap vs the target | widest column |
|---|---|---:|---:|---:|---:|---|
| `es` | `it` | 38,260 | 14,866 | 38.9 % | 14.7639 pp | `econ_status = homemaker` (14.76 % vs **0.00 %**) |
| `es` | `uk` | 15,852 | 11,173 | 70.5 % | 🔴 **30.7305 pp** | `hh_type = couple_with_children` (18.72 % vs 49.45 %) |
| `uk` | `es` | 19,140 | 11,108 | 58.0 % | 9.7688 pp | `hh_type = couple_with_children` (51.11 % vs 41.34 %) |
| `uk` | `it` | 38,260 | 14,866 | 38.9 % | 12.1025 pp | `econ_status = employed` (40.98 % vs 53.09 %) |
| `it` | `es` | 19,140 | 11,108 | 58.0 % | 9.6249 pp | `econ_status = retired` (14.14 % vs 23.76 %) |
| `it` | `uk` | 15,852 | 11,173 | 70.5 % | 🔴 **31.0235 pp** | `hh_type = couple_with_children` (18.72 % vs 49.74 %) |

🔴 **The two nulls of one fold differ by up to 3.2x** (`it` fold: `es` 9.62 pp vs `uk` 31.02 pp).
Under any single-nomination rule one of those numbers would have been the whole of `G6.2` and the
other invisible. That is the concrete case for (a), measured rather than argued.

⚪ The `es`-fold `it` null inherits `FINDING 77` intact: `homemaker` is 14.76 % of it and 0.00 %
of `population_es.csv`. Still declared, still not collapsed — collapsing would make it partly raked.

## Guards, all seen firing (selftest §§8, 8b, 9)

1. a fold the ruling does not cover → **refused**;
2. a donor country not registered for that fold → **refused**;
3. a registered donor that IS the held-out country → **refused**;
4. 🔴 **and the guard that IS the ruling** — with two donors registered, `build_neighbour`
   **refuses to nominate one** and directs the caller to `build_all_neighbours()`. Reporting one of
   two is the nomination (a) removed, and this is the only place it can be caught.

## 🔴 `FINDING 78` — what the rebuild exposed, and it is not small

Building both single-country nulls beside the pooled one made this visible; nothing in `G6.3`'s own
output could have.

| country | diaries | Σ `weight_dia_cal` | mean |
|---|---:|---:|---:|
| `ES` | 19,140 | 162,500,706.02 | 8,490.11 |
| `IT` | 38,260 | 162,800,375.82 | 4,255.11 |
| `UK` | 15,852 | 🔴 **15,919.83** | **1.0043** |

🔴 **Spain and Italy carry population-grossing weights; the UK carries a scale-free weight with
mean 1.** ~10,000:1 in total mass, identical in **every** weight column, so it is a property of the
source microdata — not of `weight_dia_cal`, not of `D-S6-4`, not of anything built here.

Consequence for the pooled null:

| fold | pooled composition | |
|---|---|---|
| `es` | 🔴 `it` **99.9902 %**, `uk` 0.0098 % | it IS the Italian null |
| `uk` | `es` 49.9539 %, `it` 50.0461 % | 🟢 a genuine mixture |
| `it` | 🔴 `es` **99.9902 %**, `uk` 0.0098 % | it IS the Spanish null |

On the `es` fold the pooled null (14.7629 pp, ESS 14,868) and the `it`-only null (14.7639 pp, ESS
14,866) agree to four decimals. 🔴 **`G6.3` and one `G6.2` are the same object under two names on
two folds of three**, which also means the paper has **two** independent nulls there, not three.
⚪ The `uk` fold escapes only because ES and IT happen to gross to nearly the same total — a
coincidence of two national populations, not a property of the method.

**Not repaired here.** The pooling basis is a basis choice and belongs to the author:
`IMP/docs/2026-08-22_D-S6-7_pooled-null-weight-scale.md`, recommendation **(a) equal country mass**.
What was added is **additive and diagnostic only**: `country_mass()` plus a
`POOL_DOMINANCE_FLAG_PP = 0.90` line the builder prints on every run and stores in the JSON as
`donor_country_mass` / `pool_dominated_by`. The selftest checks that no rescaling exists anywhere in
the module.

🟢 **Checked, not assumed — what `FINDING 78` does NOT touch:** `G6.1` starts from
`weights = [1.0] * len(donors)` (`4thJ_step6_rakeddonor.py:169`, uniform seed, `D-S5-10` (a)) and
never reads a survey weight, so the pre-registered bar and every number in `prereg_addendum_01.md`
stand. All six `G6.2` nulls are single-country, so a constant scale factor cancels exactly on
renormalisation. `G6.9` reads published tables. Steps 1–5 use weights **within** one country
everywhere, and the defect only appears when countries are pooled.

🔴 **What it does touch:** the three `G6.3` numbers recorded on 2026-08-21. `uk` 10.1901 pp is
sound; `es` 14.7629 pp and `it` 9.6242 pp describe a one-country null and must not be quoted as
"pooled" until `D-S6-7` is ruled.

## ⚪ One defect of my own, fixed and recorded

The first rebuild **built all six nulls and then died** on the last line of `main()` — a
`UnicodeEncodeError` on an emoji under a cp1252 console — **after** the work and **before**
`--json` was written, so a completed run produced no artefact and exit 1. `say()` now falls back to
`encode(enc, 'replace')`. Proved behaviour-neutral: the cp1252 re-run and the UTF-8 run wrote
byte-identical JSON (`e76a4ea2…` both). A second slip — `top = max(mass, ...)` shadowing
`report()`'s `top` parameter — raised `TypeError` and was caught the same way, by the run failing
loudly rather than writing a wrong file.

## Next

`G6.2` and `G6.3` are both built. **Step 6 DoD item 2 is three nulls of three**, with `G6.3`'s
pooling basis open as `D-S6-7`. 🔴 **Everything else in Step 6 — items 6.3 (run the folds),
6.4 (score), 6.5 (privacy audit) — still waits on GENERATED DIARIES, which is Step 7's
deliverable. That is the critical path, not Step 6.**

---

## 🟢 `D-S6-7` RULED (a) AND APPLIED — 2026-08-22 (night)

**The ruling.** Each donor country's `weight_dia_cal` is renormalised to sum to **1.0** before the
pool is formed. Every donor country contributes the same total mass; within a country the survey
weights keep their exact relative values, which is what `D-S6-4` chose and what `FINDING 53` requires.
Registered in `Step6_docs/outputs_step6/prereg_addendum_02.md` **§5b**; decision document
`IMP/docs/2026-08-22_D-S6-7_pooled-null-weight-scale.md`, answer box and directives completed by the
author.

### Ledger

| # | what | result |
|---|---|---|
| 1 | `equal_country_mass()` added, applied **unconditionally** in `build_pooled()` | module md5 `e79918f62e64c836ac6479a4d265da2e` (was `0e2df0ca8d0fd4a02145b356a9be53bb`) |
| 2 | selftest §7b (7 new checks + 1 new refusal) and §9b rewritten | **55 ok, 0 FAILED** (was 42); md5 `6a2737f8883ab00d9baea23955565998` |
| 3 | builder re-run, local, seconds | `secondary_nulls.json` md5 `d4ce5e2f8345bc147d8d297f8f9606d7` (was `5bb023e51a3e5c4eb1a7e97b6d79ed66`) |
| 4 | `prereg_addendum_02.md` §5b + §6, re-frozen | md5 `fa1e4524f52c36ec82f02f825d6ff149` (was `db450b89abbaf8f5480eb2479d50ae2d`), sidecar rewritten, all three `md5sum -c` **OK** |

🔴 `prereg.md` md5 `e4243e07cdd80c9c846b91f40e3e8c45` **UNCHANGED**. Nothing ran on Speed.

### Verified — what moved

| fold | `G6.3` worst strata gap | ESS | donor mass after |
|---|---|---|---|
| `es` | 14.7629 → **14.1839 pp** | 14,868 → 25,514 (27.5 → 47.2 %) | `it` 50.0000 %, `uk` 50.0000 % |
| `uk` | 10.1901 → **10.1883 pp** | 25,436 → 25,429 (44.3 → 44.3 %) | `es` 50.0000 %, `it` 50.0000 % |
| `it` | 9.6242 → **14.8304 pp** | 11,110 → 22,280 (31.7 → 63.7 %) | `es` 50.0000 %, `uk` 50.0000 % |

🟢 **The defect is gone and the count of independent nulls is restored.** `G6.3` no longer
coincides with any `G6.2`: `es` 14.1839 vs the `it`-only null's 14.7639; `it` 14.8304 vs the `es`-only
null's 9.6249. Before the ruling those pairs agreed to four decimal places. `pool_dominated_by` is
`null` on all three folds.

🟢 **Both invariants the decision document asserted were CHECKED against the rebuild, not
assumed.** All six `G6.2` nulls came back byte-identical — 14.7639 / 30.7305 / 9.7688 / 12.1025 /
9.6249 / 31.0235 pp, every ESS unchanged — because each is single-country and a constant scale
factor cancels on renormalisation. And `uk` moved by **0.0018 pp**, which is the check on the whole
story: that fold was already a genuine mixture, because ES and IT gross to almost the same national
total. `G6.1` was re-checked at `tools/4thJ_step6_rakeddonor.py:169` (`weights = [1.0] * len(donors)`)
— it never reads a survey weight, so `prereg_addendum_01.md` stands untouched.

### Guards — all seen firing

1. `equal_country_mass()` **REFUSES** a donor country carrying zero total weight rather than dividing
   by it. That is the `FINDING 52` failure mode exactly: a silent zero deleted 16.67 % of a pool and
   the report showed a residual of 5.6e-15.
2. The equalisation is **UNCONDITIONAL**. The selftest reads the module's own source to prove the
   dominance flag never triggers it — *a basis that switches itself on when the numbers look bad
   is a basis chosen after the fact.*
3. The `FINDING 78` flag is **re-pointed, not deleted**: it can no longer fire by construction, so if
   it ever does it means the ruling was not applied. Still seen firing on a constructed 99.99 % pool.
4. The source label now carries `EQUAL COUNTRY MASS (D-S6-7 (a))`, and `score_margin`'s Guard 1
   refuses to compare two nulls whose `marginals_source` differs — so a pre-ruling `G6.3` number
   cannot be quoted against a post-ruling one.

### 🔴 One expectation this ruling broke, and it was left failing first

The selftest's §6 hand-computed case — a donor whose source weight is NULL is excluded —
read `0.2 / 0.8` and now reads `0.5 / 0.5`: after the exclusion the pool is one UK diary and one
Italian diary, so equal country mass makes them equal. The check **was run and seen failing** before
the expectation was rewritten, and the old value is recorded beside the new one in the file. It is the
smallest place in the project where this ruling is visible.

### Next

Nothing, for item 6.2. 🔴 Items **6.3** (run the folds), **6.4** (score) and **6.5** (privacy
audit) wait on GENERATED DIARIES — Step 7's deliverable, and the critical path.

### WHAT I DID NOT VERIFY

* Nothing is scored. No `G6.2` or `G6.3` **margin** exists for any fold, because there is no model
  output; these are constructions and their distances from the target population.
* That the ~10,000:1 ratio originates upstream rests on the five weight columns of
  `harmonised.parquet` agreeing; the original national deposits were not re-opened.

