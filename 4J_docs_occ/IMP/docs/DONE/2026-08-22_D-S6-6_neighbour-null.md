# `D-S6-6` — for the author, 2026-08-22

## Which country is the "nearest neighbour"? And is `G6.2` deliverable at all under a three-country design?

**Scope** one decision, in full. Nothing in this file changes any artefact.
`prereg.md` md5 `e4243e07cdd80c9c846b91f40e3e8c45` is untouched and stays untouched whatever is ruled
— it is frozen, so the ruling goes in a **dated sidecar**, `Step6_docs/outputs_step6/prereg_addendum_02.md`,
beside `prereg_addendum_01.md`.

| | |
|---|---|
| **Raised by** | Step 6 work item 6.2, building the two secondary nulls, 2026-08-22 |
| **Blocks** | `G6.2` only. `G6.3` is built on all three folds; `G6.1` was built on 2026-08-21 |
| **Does not block** | the claim, the FAIL criteria, `G6.9`, or Step 6 closing — see §5 |
| **Record** | `Step6_docs/impl/2026-08-22_secondary-nulls.md`, `Step6_docs/4thJ_06_transfer.md` (2026-08-22 entry) |

---

## 1. The problem in one paragraph

`prereg.md` §5 names three nulls. One of them is a **"nearest-neighbouring-country model"** — and the
pre-registration **defines no rule for choosing the neighbour**. It did not need one when it was
written: the design then had **four** countries including **France**, which shares a land border with
both Spain and Italy, so every fold had an obvious neighbour. **Author decision 16 (2026-08-15)
excluded France.** The donor pool per fold is now **two** countries, and for the `uk` fold neither
Spain nor Italy is anybody's idea of a nearest neighbour. 🔴 **Choosing one now — after the corpus,
the folds and the populations are all built — is choosing a null's strength after the fact**, which is
the same class of defect `G6.2` exists to answer. So the code **refuses** rather than guess.

## 2. The registered text, quoted exactly

`Step6_docs/outputs_step6/prereg.md:110-112` (frozen):

> | null | strength | role |
> |---|---|---|
> | Pooled all-country average diary | weak | secondary, reported |
> | **Nearest-neighbouring-country model** | **moderate** | **secondary; answers the geographic-proxy objection** |
> | Real diaries from the N−1 pool, raked by IPF onto the held-out country's published marginals | **strongest** | 🔴 **THE PRE-REGISTERED BAR** |

That is the whole of it. There is no §on how the neighbour is picked, in `prereg.md`, in
`4thJ_06_transfer.md`, or in the parent overview. The gate row is
`4thJ_06_transfer_val.md:31` — **`G6.2` Margin over the nearest-neighbour-country model | Geographic
proxy | Reported | `RL06`** — and note the threshold column reads **Reported**, not a number.

## 3. What is actually on the table, numerically

**Donor pools.** Corpus = 73,254 diaries: `es` 19,140, `it` 38,260, `uk` 15,854.

| fold | donor pool (N−1) | if the neighbour is… | …the null rests on | ratio between the two choices |
|---|---:|---|---:|---:|
| `es` | 54,114 | `uk` | 15,854 | **2.41×** |
| | | `it` | 38,260 | |
| `uk` | 57,400 | `es` | 19,140 | **2.00×** |
| | | `it` | 38,260 | |
| `it` | 34,994 | `uk` | 15,854 | **1.21×** |
| | | `es` | 19,140 | |

🔴 **The choice of neighbour changes the null's donor base by up to 2.4×**, before anything about
similarity is considered. It is not a cosmetic label.

## 4. 🔴 The obvious rule was tested and it does not survive the test

The natural candidate is *"nearest by geographic distance"*. It was computed, not assumed —
great-circle distance on the WGS-84 sphere, three bases:

| basis | `es` fold → | `uk` fold → | `it` fold → |
|---|---|---|---|
| **capital cities** | **`uk`** (1263 vs 1364 km, margin 101) | `es` (1263 vs 1434, margin 170) | `es` (1364 vs 1434, margin 70) |
| **approx. population centroids** | 🔴 **`it`** (1331 vs 1409, margin 78) | `es` (1409 vs 1444, margin 34) | `es` (1331 vs 1444, margin 113) |
| **approx. geometric centroids** | 🔴 **`it`** (1409 vs 1561, margin 152) | `es` (1561 vs 1660, margin 99) | `es` (1409 vs 1660, margin 251) |

Three things this shows, and each of them is fatal on its own:

1. 🔴 **The `es` fold's neighbour FLIPS — `uk` under capitals, `it` under centroids.** The
   capital-versus-centroid choice is itself unregistered, so the rule does not determine an answer; it
   moves the choice one level down and hides it. `es` is also the fold with the widest strata gap
   (14.76 pp), so this is not the fold to be arbitrary on.
2. 🔴 **All three capitals are nearly equidistant** — 1263, 1364 and 1434 km, a spread of **13 %**.
   The winning margin is **70–170 km on ~1,300 km**. "Nearest" is not a meaningful relation among
   these three countries.
3. 🔴 **Under capitals the rule pairs `es` with `uk`** and separates Spain from Italy — the two
   Mediterranean, Romance-language, Southern-Europe countries. Any reader who checks will read that as
   an artefact, and they will be right.

⚪ **Shared land border**, the strictest geographic rule, yields **nothing on any fold**: Spain borders
France, Portugal, Andorra, Morocco and Gibraltar; the UK borders Ireland; Italy borders France,
Switzerland, Austria, Slovenia, San Marino and the Vatican. **No fold has a land-border neighbour
inside its donor pool.** France was the country that made this rule work, and it is gone.

## 5. 🟢 The thing that lowers the stakes, and it was checked rather than assumed

**Reviewer attack 3 is not carried by `G6.2`. It is carried by `G6.9`.**

`4thJ_06_transfer_val.md:47` — **`G6.9` Nearest-neighbour discrimination | *"It mapped the country to
its neighbour"* | The held-out country's generated profile must be closer to its own published tables
than to ANY other country's, by a margin exceeding the between-country spread.**

🟢 **`G6.9` compares against every other country and therefore needs no neighbour rule at all.** It is
a discrimination test with a threshold; `G6.2` is a *reported* secondary null with none. So:

* DoD item 4 — *"All three reviewer attacks answered with an experiment"* — is satisfiable through
  `G6.7` / `G6.8` / `G6.9` **whatever is ruled here**.
* `G6.5`'s FAIL criteria name **only** the raked-donor null. `G6.2` cannot fail the claim.
* What is genuinely at stake is narrower and worth stating plainly: **`prereg.md` §5 promises three
  nulls, and a paper that ships two owes the reader an explanation.**

## 6. The options

### 🟢 (a) — RECOMMENDED: report **both** single-country nulls on every fold, and drop the word "nearest"

Build the single-donor-country null for **each** country in the pool — two per fold, six in total —
and report both beside the headline. `G6.2` becomes *"per-donor-country nulls, both reported"*.

* **Why it is the strongest answer available:** there is **nothing left to choose**, so the objection
  this whole decision is about cannot be raised. It removes a degree of freedom instead of registering
  one.
* **It is strictly more informative than any single pick.** If the model merely mapped `it` onto `es`,
  the `es`-only null is the one that becomes near-unbeatable — and reporting both is exactly how a
  reader sees that. A single "nearest" pick can only ever show one of the two.
* **It is the same logic as `G6.9`**, which the pre-registration already accepted for this attack:
  compare against *all* the others, do not nominate one.
* **Cost: near zero.** The machinery is built and tested; `build_neighbour()` already takes an explicit
  country and refuses an unregistered one. The ruling populates the registry with both, per fold.
* 🔴 **What it is, honestly:** a **post-registration reinterpretation** of a pre-registered null's
  *name* — not of its construction, its role, or any threshold. Declared as such in addendum 02, with
  the reason (France's removal) stated. It must never be presented as what §5 said.

### ⚪ (b) — Register a geographic rule: nearest capital city by great-circle distance

* **Consequence:** `es` → `uk`, `uk` → `es`, `it` → `es`. Three nulls, one per fold.
* 🔴 **Weakened by §4 on three counts:** the `es` answer flips to `it` the moment the basis moves from
  capitals to centroids, and the basis is unregistered; the margins are 5–13 % of the distance; and it
  pairs Spain with the UK rather than Italy. Take it **only** if the author judges a mechanical,
  stated, checkable rule to be worth more than a defensible one — and it must then be written up
  **with the flip disclosed**, not without it.

### ⚪ (c) — Register a published regional grouping (UN M49 / Eurostat)

Spain and Italy are **Southern Europe**; the United Kingdom is **Northern Europe**.

* **Consequence:** `es` → `it` and `it` → `es`, both defensible and both matching the intuition
  §4 offends. 🔴 **And `uk` is undefined** — it has no same-region partner in the pool, so the rule
  determines two folds of three and needs a *second*, ad-hoc rule for the third.
* 🔴 That second rule is the choice this decision is trying to avoid, reintroduced on the one fold
  where it is least defensible. Take it only paired with **(a)** or **(d)** for `uk`, and say so.

### ⚪ (d) — Drop `G6.2`; declare it undeliverable under a three-country design

* **Consequence:** two nulls ship instead of three. The paper states that the nearest-neighbour null
  was pre-registered when the design had four countries including France, that decision 16 removed the
  only country that made "nearest" meaningful, and that no fold in the final design has a neighbour.
* 🟢 **Defensible, because of §5:** attack 3 is answered by **`G6.9`**, which needs no neighbour, and
  `G6.2` can fail nothing. Dropping a *reported* secondary null costs no gate and no criterion.
* 🔴 **Cost:** §5 of the frozen pre-registration promises three nulls and two arrive. A reader who
  reads the pre-registration — which is the point of publishing it — will notice, so the declaration
  has to be prominent, not a footnote. **(a) delivers the same honesty and keeps the promise**, which
  is why it is recommended over this.

### 🔴 (e) — Choose the neighbour by measured similarity of time use. **REJECT.**

Listed only so it is on the record as refused. Picking the donor country whose diaries are closest to
the held-out country's would make `G6.2` the **strongest** single-country null available — and it
would be chosen using the outcome variable, on data, after the fact. That is selecting the test on the
result, the exact move `D-S5-16` was just ruled (a) to avoid.

## 7. What the code does today, and what changes on a ruling

`tools/4thJ_step6_secondary_nulls.py` ships with `REGISTERED_NEIGHBOURS = {}` — **empty**. `G6.2`
refuses on all three folds and the refusal names this decision. It is **seen refusing** in the
selftest (`4thJ_step6_secondary_nulls_selftest.py`, 30 of 30 green) and in the live run, and it also
refuses a neighbour asserted on the command line but not registered, and a "neighbour" that is the
held-out country itself.

| ruling | what changes |
|---|---|
| **(a)** | registry gets both donor countries per fold; the report emits six single-country nulls; addendum 02 records the reinterpretation |
| **(b)** or **(c)** | registry gets one country per fold with the rule and its citation; addendum 02 records the rule, and for **(b)** the capital-vs-centroid flip |
| **(d)** | registry stays empty; `G6.2` is marked **NOT DELIVERED** with its reason in the val doc, the step doc and the paper |

⚪ In every case `prereg.md` is untouched and `G6.1`, `G6.3`, `G6.9` are unaffected.

---

## Answer box

> **`D-S6-6`:**  (a) both single-country nulls / (b) capital distance / (c) regional grouping /
> (d) drop `G6.2`  → **(a) Report both single-country nulls on every fold (drop "nearest") — 6 single-country nulls in total, recorded in `prereg_addendum_02.md`.**

---

## Author's Ruling & Directives (2026-08-22)

| Decision | Ruled Option | Summary of Decision | Action Required |
|---|---|---|---|
| **`D-S6-6`** | 🟢 **Option (a)** | **Report both single-donor-country nulls on every fold** (6 nulls in total); re-interpret `G6.2` as *"per-donor-country nulls, both reported"*; record formally in `prereg_addendum_02.md`. | Populate `REGISTERED_NEIGHBOURS` in `tools/4thJ_step6_secondary_nulls.py` with all donor countries per fold: `es: [it, uk]`, `uk: [es, it]`, `it: [es, uk]`; write `prereg_addendum_02.md` explaining France's removal under Author Decision 16. |

---

### Detailed Rulings and Directives

#### 1. Choice: Option (a) — Report Both Single-Country Nulls
* **Pre-registration reinterpretation**:
  - `G6.2` is re-interpreted as **"Per-donor-country baseline models, both reported"** rather than selecting an artificial single "nearest neighbour".
  - For each held-out fold, two single-country donor nulls are evaluated and reported:
    - **`es` fold**: single-country nulls from **`it`** and **`uk`**
    - **`uk` fold**: single-country nulls from **`es`** and **`it`**
    - **`it` fold**: single-country nulls from **`es`** and **`uk`**
* **Scientific Rationale**:
  1. **Zero degrees of freedom**: Eliminates arbitrary post-hoc geographical/regional definitions (which flip under capitals vs centroids or leave `uk` orphaned).
  2. **Maximum diagnostic transparency**: Directly tests whether transfer on a given fold is trivial or asymmetric (e.g., if Spain simply mirrors Italy).
  3. **Alignment with `G6.9`**: Mirrors the discrimination discipline of `G6.9`, which evaluates discrimination against *all* alternative countries rather than an arbitrary single counterpart.
  4. **Attack 3 is fully protected**: Reviewer Attack 3 (*"It mapped the country to its neighbour"*) is structurally answered by gate `G6.9`, meaning `G6.2` serves as an informative, reported diagnostic without carrying a gate FAIL risk.

#### 2. Implementation Directives
1. **Registry in Code**:
   Update `tools/4thJ_step6_secondary_nulls.py` to register both donors per fold:
   ```python
   REGISTERED_NEIGHBOURS = {
       "es": ("it", "uk"),
       "uk": ("es", "it"),
       "it": ("es", "uk"),
   }
   ```
2. **Dated Addendum**:
   Create `Step6_docs/outputs_step6/prereg_addendum_02.md` documenting:
   - The initial 4-country context (with France).
   - Author Decision 16 (exclusion of France) leaving 3 non-bordering countries.
   - The formal decision to emit both single-country donor nulls per fold under `G6.2`.
3. **Preservation of Core Artifacts**:
   `prereg.md` remains frozen (md5 `e4243e07cdd80c9c846b91f40e3e8c45` untouched).

---

⚪ `prereg.md` md5 `e4243e07cdd80c9c846b91f40e3e8c45` is unchanged. Nothing is running on Speed.
