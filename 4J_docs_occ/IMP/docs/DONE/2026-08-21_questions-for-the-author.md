# Questions for the author — 2026-08-21

**Written while `1285712` / `1285713` / `1285714` (the `D-S5-13`(a) replicate jobs) run.**
**Scope** the four questions put on 2026-08-21 evening, with the full context and the consequence of
every option. Nothing in this file changes any artefact. `prereg.md` md5
`e4243e07cdd80c9c846b91f40e3e8c45` is untouched.

🔴 **Read this line first: two of the four questions were ALREADY RULED by the author earlier the
same day, and asking them again was my error.** `Prompts/RESUME.md` line 1 still carries a stale
*"STILL OPEN AND UNRULED"* list naming `D-S6-4`, `D-S6-5` and the zero-cell tolerance; the rulings
are recorded in `Step6_docs/4thJ_06_transfer.md:1054-1100`. **Q3 and Q4 below are therefore
confirmations plus the one residue each ruling genuinely left open — not re-openings.** The stale
line is corrected in `RESUME.md`.

| # | Item | Real status | What is actually asked |
|---|---|---|---|
| **Q1** | `D-S5-15` | 🔴 **OPEN — new, found 2026-08-21 while the jobs ran** | a genuine choice, three options |
| **Q2** | `FINDING 69` | 🔴 **OPEN — one line of the Step 5 val doc** | which of two readings the register meant |
| **Q3** | `D-S6-4` | 🟢 **RULED** (score on `weight_dia_cal`) | confirm + rule the residue (`G6.8`'s weight wiring) |
| **Q4** | `D-S6-5` | 🟢 **RULED** (drop `tus_00educ`) | confirm + rule the residue (`tus_00age`'s `Y65-74`) |

⚪ **Also already ruled, listed so it is not asked a third time:** the `D-S6-3` item 1 zero-cell
tolerance is **`< 1.0 %`**, the looser of the two options, and `< 1.0 %` is what must appear
everywhere. It is fixed; any zero-cell hit rate computed against `< 0.5 %` is invalid.

---

## Q1 — `D-S5-15`: the replicate windows exclude the fidelity optimum on two folds of three

### The facts, re-derived from the artefacts and not recalled

The primary temperature grids (`Step5_docs/outputs_step5/temperature_calibration_{es,uk,it}.json`)
and the pre-registered replicate windows (`tools/4thJ_step5_temperature_replicates.sh:58-60`) line up
like this:

| fold | grid | `T_entropy` = `T_chosen` | `T_fidelity` | replicate window | `T_fidelity` inside? | MAE at `T_fidelity` | MAE at `T_chosen` | `terminated_frac` at `T_fidelity` |
|---|---|---|---|---|---|---|---|---|
| `es` | 0.50 … 1.30 | **1.30** | **0.70** | `1.10, 1.20, 1.30` | 🔴 **NO — four grid steps below** | 7.58 pp | 9.40 pp | **0.852** |
| `uk` | 0.50 … 1.30 | **1.10** | **1.00** | `1.00, 1.10, 1.20` | ⚪ yes, on the lower edge | 2.57 pp | 3.28 pp | 1.000 |
| `it` | 0.50 … 1.30 | **1.20** | **0.80** | `1.10, 1.20, 1.30` | 🔴 **NO — three grid steps below** | 3.93 pp | **13.12 pp** | 0.967 |

Two further facts matter and are easy to miss:

* **The primary grids contain no coverage data at all.** `at_home_mae_pp_covered` is `None` in all
  nine rows of all three folds and `real_coverage_curve` is absent — those runs predate `D-S5-14`(a).
  **The replicate jobs are the only source of a coverage curve that will ever exist**, so whatever
  their grid covers is the whole of the curve.
* **The primary curve is not seeded** (`FINDING 66`): its `reproducibility_claim` reads *"NOT SEEDED
  … this curve cannot be reproduced"*. `T_fidelity` was computed off that curve.

### Why this is a defect and not a nuisance

`D-S5-13`(a) asked for a **narrow window around each fold's `T_chosen`**, and the windows do exactly
that — they are **correct for the purpose they were written for**, which is measuring seed spread.
`T_chosen` is the **entropy** optimum. `D-S5-14`(a) then added a second purpose to the same run: the
coverage curve, whose whole point is to test whether the **fidelity** argmin
(`fidelity_argmin_moved_under_D_S5_14`) moves once the truncation confound is removed. **The mistake
is §12 of the improvement document claiming one run discharges both.** It does not.

🔴 **And the confound bites hardest exactly where we cannot see it.** On `es` the fidelity minimum
sits at `T = 0.70`, where **14.8 % of generated diaries never terminate** — the at-home profile there
is computed over truncated days, which is precisely the artefact `FINDING 67` describes. On `it` the
gap between the two criteria costs **9.19 pp of at-home MAE** (3.93 at `T_fidelity` vs 13.12 at
`T_chosen`). Those are the two folds where the curve will be blank.

### 🔴 What this does NOT do — stated so no option can be read as re-opening it

* It **does not change any `T_chosen`**. `D-S5-13`(a) already rules that *a replicate run measures
  spread; it does not choose again*, and re-selecting on the same criterion with better statistics is
  still selecting on it.
* It **does not touch `at_home_mae_pp`**, which `D-S5-14`(a) froze as-is. The coverage curve is an
  **additive diagnostic**; it cannot move a registered basis.
* It **blocks nothing**. Step 5 can close on any of the three options.

### The options

#### 🟢 (a) — RECOMMENDED: run only the six missing grid points, at seed `101`, per fold

Each replicate JSON stores `gen_seed` per row, so the three window points already exist at seed
`101`. Running the six points **outside** the window at the same seed and splicing gives an
**internally consistent nine-point coverage curve at one seed** for the cost of six points, not nine.

* **Cost** ≈ 20–30 min per grid point per fold at the observed rates → **≈ 2–3 h per fold**, three
  folds in parallel on three GPUs, i.e. **one evening of wall-clock**.
* **New code** none. `4thJ_step5_temperature.py` already takes `--grid`, `--gen-seeds`, `--save-gen`
  and `--tag`; this is one `sbatch` per fold with a different `--grid`.
* **What it buys** `fidelity_argmin_moved_under_D_S5_14` becomes evaluable on **all three folds**;
  `FINDING 67` becomes a **measurement on three countries** instead of an argument; the paper can
  state whether the fidelity optimum survives coverage correction, which is the single most
  attackable claim in item 5.4.
* **Risk** the splice joins two jobs. Mitigated because the seed, prompt draw (`prompt_seed = 42`),
  base revision, adapter and `n_prompts = 600` are all identical and pinned; the join must be
  **declared** in `temperature_calibration.md`, not silently concatenated.

#### ⚪ (b) — the same thing as one clean nine-point job per fold

Re-run the whole grid single-seed with `--save-gen`, and use nothing from the replicates for the
curve.

* **Cost** ≈ **4.5 h per fold** (the primary `es` grid took `04:23:37`), so roughly **50 % more GPU**
  than (a) for an identical scientific result.
* **What it buys over (a)** one artefact, no splice to declare, marginally simpler provenance.
* **Verdict** correct but wasteful; take it only if the splice in (a) is judged a reporting hazard.

#### 🔴 (c) — declare the stub and stop

Ship the three-point curve, state in the val doc that the coverage curve covers the entropy side
only, and record `FINDING 67` as a **`uk`-only measurement** plus a code-path argument for `es`/`it`.

* **Cost** zero GPU, zero delay.
* **What it costs instead** the paper carries a declared hole in exactly the place a reviewer will
  press: we introduce a coverage confound, we build the diagnostic for it, and then we do not measure
  it where it is largest. `es` and `it` are also the two folds where the two criteria disagree.
* **Take it only if** GPU time is needed elsewhere, and only with the val doc saying plainly that the
  diagnostic was not evaluated at the fidelity optimum on two folds of three.

---

## Q2 — `FINDING 69`: `G5.9`'s text and its own registered perturbation cannot both hold

### The contradiction, in the register's own words

* **Gate text**, `Step5_docs/4thJ_05_populationLinkage_val.md:39` and
  `4thJ_05_populationLinkage.md:168` — *"If top-p is used at all, **p ≤ 0.98**, asserted in the
  generation config that Step 7 actually reads, not in a comment."*
* **Perturbation table**, `…_val.md:80` — *"Set `top_p = 0.9` in the generation config"* must fell
  `G5.9` and nothing else.

**`0.9` satisfies `p ≤ 0.98`.** The two rows contradict each other outright.

### Which one is wrong is decidable, not a matter of taste

In nucleus sampling a **smaller** `p` truncates **more**. So the gate as written:

| `top_p` | what it actually does | as-written `p ≤ 0.98` | coherent `p ≥ 0.98` |
|---|---|---|---|
| `0.50` | deletes half the probability tail | 🔴 **PASS** | FAIL |
| `0.90` | the registered perturbation | 🔴 **PASS** — so the perturbation cannot fell it | **FAIL** ✅ |
| `0.99` | deletes almost nothing | 🔴 **FAIL** | PASS |
| `1.00` | our configuration, no truncation | not used → vacuous | not used → vacuous |

As written, a gate named **"no truncation creep"** admits the most aggressive truncation and rejects
the mildest. 🟢 **Both readings are already implemented and printed by the checker**
(`tools/4thJ_gates_step5.py`), and both are demonstrated by
`tools/4thJ_step5_g58_g59_selftest.py`, **17/17 green** — this is a measurement, not a reading of the
prose.

### 🔴 What does NOT change under any option

Our configuration. `TOP_P = 1.0` is a pre-registered constant at
`tools/4thJ_step5_temperature.py:85`, we do not use nucleus sampling anywhere, and under **both**
readings our config is vacuously fine. **The decision is about the register's integrity, not about
the model.**

### The options

#### 🟢 (1) — RECOMMENDED: the coherent reading, `p ≥ 0.98`

* **Cost** one line, in three places: the gate row at `…_val.md:39`, the prose at
  `…populationLinkage.md:168`, and the `RL09` row at `…populationLinkage.md:92`.
* **Consequence** the register becomes self-consistent: the registered perturbation `0.9` **fells the
  gate**, so `G5.9` can be **seen failing**, which is the project's hard requirement. The checker
  already takes its verdict on this reading, so no code changes.
* **Reporting duty** the correction must be declared as a **post-registration correction of an
  internal contradiction**, with both readings shown — not quietly rewritten.

#### 🔴 (2) — keep `p ≤ 0.98` and strike the perturbation

* **Consequence** `G5.9` then has **no registered perturbation and can never be seen failing**. Every
  other gate in the project has been seen failing; this one would become the sole exception, and
  `feedback_gates_must_be_seen_failing` forbids trusting a gate nobody has watched fail.
* It also leaves on the books a gate that would **pass a `top_p` of 0.5**.

#### ⚪ (3) — change nothing, declare the contradiction

* **Consequence** a self-contradictory row stays in a register the paper cites. The checker still has
  to pick one reading in order to return a verdict, so the contradiction gets resolved in code and
  left unresolved in the document — the worst of the three.

---

## Q3 — `D-S6-4`: 🟢 ALREADY RULED. What is left is the residue

**The ruling, `Step6_docs/4thJ_06_transfer.md:1059`:** Step 6 scores on **`weight_dia_cal`**, the
calendar-week weight; **`weight_dia` is reported beside it as a declared sensitivity and never mixed
into the headline.**

**Why it was ruled that way** — `FINDING 53`: the three countries' diary weights hit three different
day bases (`uk` 71.45/14.32/14.24 = the calendar week, `es` 50/25/25, `it` 33/33/33, all exact), so
only the UK is calendar-representative. The effect on at-home time is **`es +0.947`, `it +1.300`,
`uk −0.003` pp** — small, but **country-correlated**, which in a leave-one-country-out design is the
one shape of error that lands directly on the held-out fold.

### The two residues

1. ⚪ **External confirmation.** What basis the national institutes were *required* to tabulate on is
   a literature question. It is written as
   `DeepResearchPrompts/L27_hetus_weights_amy_weather_tabula_licence.md` **Part A**, carrying the
   measured day-base table as the thing the guidelines have to explain. **No decision needed** — it
   can only add a declared caveat, never move the basis.
2. 🔴 **`G6.8` refuses `--weight-field`** rather than pick a basis nobody had chosen. Now that a basis
   is chosen, this needs wiring — and that is the question:

| option | consequence |
|---|---|
| 🟢 **(a) RECOMMENDED — wire `weight_dia_cal` into `G6.8` now** | `G6.8` becomes runnable on the ruled basis immediately. `L27` Part A, whenever it returns, can only append a caveat sentence; it cannot invalidate a run, because the basis is ours and declared. Keeps Step 6 off the critical path of an external search. |
| ⚪ **(b) hold the wiring until `L27` Part A returns** | 🔴 Puts a Step 6 gate behind an **external** deep-research task with no return date (`feedback_deep_research_is_external` — we do not control when that lands). Buys nothing, because the ruling already fixed the basis. |

---

## Q4 — `D-S6-5`: 🟢 ALREADY RULED. What is left is `tus_00age`

**The ruling, `Step6_docs/4thJ_06_transfer.md:1074`:** `tus_00educ` is **dropped from the scoring set
and declared**. It is stratified by `isced97` **educational attainment**; the harmonised corpus
carries **no education column at all**, so no mapping exists under any regrouping. It was dropped
rather than back-filled with an invented education proxy.

**The resulting scoring set** — `tus_00startime` + `tus_00selfstat` as the two clean tables,
`tus_00hhstatus` on a **declared regrouping**, and `tus_00age` on a **declared non-overlapping
subset**.

### The residue — the second half of `FINDING 55`

🔴 **`Y65-74` is absent in `0` of `168` cells — in ES, UK and IT alike** — and the published age
dimension is **not a partition**: `Y20-74` contains `Y25-44` and `Y45-64`, and `Y_GE65` contains
`Y65-74`. Summing the published bands therefore double-counts. The ruling says *"declared
non-overlapping subset"*; **which subset** has never been written down.

| option | consequence |
|---|---|
| 🟢 **(a) RECOMMENDED — fix the subset now, in writing** | Name the non-overlapping bands explicitly in the Step 6 doc **before any fold is scored**, so the choice is pre-registered relative to the result rather than made after seeing it. Costs one paragraph. Without it, whoever computes the first age comparison picks the subset silently and the choice becomes post-hoc. |
| ⚪ **(b) leave it to whoever scores `tus_00age` first** | 🔴 A subset chosen while looking at the result is a selection on the outcome. And `Y65-74`'s absence is **identical in all three countries**, so it is not even a fold-specific problem — there is no reason to defer it. |

⚪ Nothing else about `D-S6-5` is open. The drop stands and the declaration is written.

---

## Answer sheet

| # | Item | Recommended | Alternatives |
|---|---|---|---|
| **Q1** | `D-S5-15` | **(a)** six missing grid points at seed `101`, ≈ 2–3 h per fold, run in parallel | (b) full nine-point re-run ≈ 4.5 h/fold · (c) declare the stub |
| **Q2** | `FINDING 69` | **(1)** coherent reading `p ≥ 0.98`, one line in three places | (2) keep `p ≤ 0.98`, lose the perturbation · (3) declare the contradiction |
| **Q3** | `D-S6-4` residue | **(a)** wire `weight_dia_cal` into `G6.8` now | (b) wait for `L27` Part A |
| **Q4** | `D-S6-5` residue | **(a)** fix the `tus_00age` non-overlapping subset in writing now | (b) defer to first use |

🔴 **None of the four blocks Step 5 from closing.** Q1 decides whether the coverage diagnostic is
measured or merely declared; Q2 is one line of prose; Q3 and Q4 are the residues of rulings already
made.

---

## Author's Rulings & Responses (2026-08-21)

| # | Item | Ruled Option | Decision Summary | Action Required |
|---|---|---|---|---|
| **Q1** | `D-S5-15` | 🟢 **Option (a)** | Run only the 6 missing grid points at seed `101` per fold; splice with the replicate seed `101` points to yield a complete 9-point coverage curve | Run 1 sbatch per fold for missing points on `es` (`0.50..1.00`), `it` (`0.50..1.00`), and `uk` (`0.50..0.90, 1.30`); declare splice in `temperature_calibration.md`. |
| **Q2** | `FINDING 69` | 🟢 **Option (1)** | Adopt coherent reading **`p ≥ 0.98`**; declare post-registration erratum for the register's internal contradiction | Update 1 line in 3 places (`4thJ_05_populationLinkage_val.md:39`, `4thJ_05_populationLinkage.md:168`, and `RL09` row at `4thJ_05_populationLinkage.md:92`); ensure perturbation `top_p = 0.9` fells `G5.9`. |
| **Q3** | `D-S6-4` residue | 🟢 **Option (a)** | **Confirm `weight_dia_cal`** headline basis; **wire `weight_dia_cal` into `G6.8` now** | Implement `--weight-field weight_dia_cal` in `G6.8` checker immediately; `L27` Part A remains an additive caveat upon return. |
| **Q4** | `D-S6-5` residue | 🟢 **Option (a)** | **Confirm `tus_00educ` dropped & declared**; **fix `tus_00age` non-overlapping subset in writing now** | Document explicit 5-band partition: `{Y15-20, Y20-24, Y25-44, Y45-64, Y_GE65}`; drop composite `Y20-74` and empty `Y65-74`. |

---

### Detailed Rulings and Directives

#### 1. Q1 (`D-S5-15`) — Ruled: Option (a)
* **Choice**: Run the six missing grid points per fold at seed `101` on Speed in parallel, and splice with the existing seed `101` runs from the replicate jobs.
* **Rationale**: 
  1. Provides a full 9-point coverage curve at seed `101` for all 3 folds at minimal computational expense (~2–3 h per fold in parallel vs ~4.5 h for full re-runs).
  2. Enables evaluability of `fidelity_argmin_moved_under_D_S5_14` on all three folds, transforming `FINDING 67` from an unverified argument / UK-only measurement into a rigorous cross-national empirical evaluation.
  3. Provenance and reproducibility are fully preserved because prompt seed (`42`), base revision, LoRA adapter, and prompt count (`n_prompts = 600`) are identical and pinned across both passes.
* **Directive**: The splice must be explicitly documented and declared in `outputs_step5/temperature_calibration.md`.

#### 2. Q2 (`FINDING 69` / `G5.9`) — Ruled: Option (1)
* **Choice**: Adopt the coherent reading **`p ≥ 0.98`** ("If top-p is used at all, $p \ge 0.98$").
* **Rationale**:
  1. In nucleus sampling, smaller $p$ introduces more aggressive truncation. A gate named "no truncation creep" that allowed $p \le 0.98$ erroneously permitted severe truncation ($p = 0.50$) while forbidding un-truncated distributions.
  2. Under $p \ge 0.98$, the registered perturbation ($top\_p = 0.90$) successfully fells the gate, satisfying the core project invariant (`feedback_gates_must_be_seen_failing`).
  3. Our project configuration ($top\_p = 1.0$) satisfies the condition vacuously without changes.
* **Directive**: Record the post-registration fix in `4thJ_05_populationLinkage_val.md:39`, `4thJ_05_populationLinkage.md:168`, and `4thJ_05_populationLinkage.md:92` (`RL09`), noting the erratum transparently.

#### 3. Q3 (`D-S6-4` Residue / `G6.8`) — Ruled: Option (a)
* **Choice**: Confirm scoring on **`weight_dia_cal`** (calendar-week weight) with `weight_dia` reported alongside as a sensitivity; **wire `weight_dia_cal` into `G6.8` immediately**.
* **Rationale**:
  1. Avoids gating Step 6 execution on external deep-research turnaround (`L27` Part A).
  2. Protects the leave-one-country-out design from country-correlated day-mix bias (`FINDING 53`) by aligning all folds to a common calendar-week basis.
* **Directive**: Update `G6.8` checker to support and default to `weight_dia_cal`.

#### 4. Q4 (`D-S6-5` Residue / `tus_00age`) — Ruled: Option (a)
* **Choice**: Confirm drop of `tus_00educ`; **fix and pre-register the non-overlapping age partition in writing now**.
* **Rationale**:
  1. Eurostat's `tus_00age` table is not an orthogonal partition ($Y20\text{--}74$ and $Y\_\text{GE}65$ contain other published bands), and band $Y65\text{--}74$ contains zero populated cells across all 3 countries ($0/168$ cells).
  2. Pre-registering the partition prevents post-hoc selection bias when computing transfer errors.
* **Partition Specification**:
  The official non-overlapping scoring partition for `tus_00age` is defined as the 5 mutually exclusive, exhaustive published bands for ages 15+:
  1. **`Y15-20`** (15 to 20 years)
  2. **`Y20-24`** (20 to 24 years)
  3. **`Y25-44`** (25 to 44 years)
  4. **`Y45-64`** (45 to 64 years)
  5. **`Y_GE65`** (65 years and over)
  *Excluded from scoring*:
  - **`TOTAL`**: redundant aggregate ($100\%$).
  - **`Y20-74`**: composite band (overlaps with `Y25-44` and `Y45-64`).
  - **`Y65-74`**: dropped due to complete absence ($0/168$ cells across ES, UK, IT); respondents aged 65–74 are captured in `Y_GE65`.

---

## Execution record — all four rulings applied, 2026-08-21 night

| # | Ruled | Applied | Where |
|---|---|---|---|
| **Q1** | `D-S5-15` (a) | 🟡 **submitted, running** | jobs `1285777` `es` · `1285778` `uk` · `1285779` `it`, launcher `tools/4thJ_step5_temperature_coverage101.sh` |
| **Q2** | `FINDING 69` (1) | 🟢 **done** | `4thJ_05_populationLinkage.md` l.92 + l.168, `…_val.md` l.39 + progress log, `tools/4thJ_gates_step5.py` |
| **Q3** | `D-S6-4` residue (a) | 🟢 **done** | `tools/4thJ_step6_g68_joint.py`, `…_selftest.py`, `…_markov_comparator.py`, `Step6_docs/impl/2026-08-21_g68-g614-markov.md` |
| **Q4** | `D-S6-5` residue (a) | 🟢 **done** | `Step6_docs/4thJ_06_transfer.md` — new `D-S6-5` residue section + `FINDING 55` corrected in place |

### Q1 — what was submitted

One job per fold, running **only the six grid points the replicate window does not cover**, at seed
`101` only:

| fold | replicate window (already at seed 101) | this job |
|---|---|---|
| es | 1.10, 1.20, 1.30 | 0.50, 0.60, 0.70, 0.80, 0.90, 1.00 |
| uk | 1.00, 1.10, 1.20 | 0.50, 0.60, 0.70, 0.80, 0.90, 1.30 |
| it | 1.10, 1.20, 1.30 | 0.50, 0.60, 0.70, 0.80, 0.90, 1.00 |

`--gen-seeds 101` puts the script in replicate mode, in which it **refuses to recompute the choice**;
`T_chosen` and `at_home_mae_pp` are untouched. Prompt seed 42, `n_prompts` 600, `top_p` 1.0,
`top_k` 0, same pinned base revision and adapter as both earlier passes. Generations are persisted.
🔴 The splice is **declared** in `outputs_step5/temperature_calibration.md` when it is written, as
directed. ⚪ `fidelity_argmin_moved_under_D_S5_14` is computed only in non-replicate mode, so it is
derived offline from the two JSONs and reported in that document rather than emitted by the run.

### Q2 — what changed, and what did not

The clause now reads **`p ≥ 0.98`** in all three registered places, each carrying the words
*post-registration erratum, `FINDING 69`, ruled 2026-08-21*. The checker prints the superseded
reading beside the ruled one so the correction stays visible instead of being absorbed. Selftest
re-run: **17 of 17**, with `0.9` FAIL (the registered perturbation now fells the gate, which it could
not do before), `0.99` PASS, `0.5` FAIL, boundary `0.98` PASS. ⚪ `TOP_P = 1.0` is unchanged and was
never at issue.

### Q3 — the residue closed, and one thing it turned up

`G6.8` no longer raises on `--weight-field`; it **defaults to `weight_dia_cal`**, joins the weight
from `harmonised.parquet` on `(country, pid, diary_day)` — 73,254 keys, exactly the corpus size,
because 🔴 **the corpus file carries no weight column at all** — and weights every distribution while
weighting **no count** (`MIN_CELL_N`, `MIN_DWELL_N` stay unweighted: sample size decides what is
scorable, weight decides what it represents).

**Additivity is a diff, not a claim:** the selftest was run before and after the refactor with the
weight left off, and the outputs are **byte-identical**. Five new checks then prove the wiring live:
a constant weight moves nothing (6/6 statistics), a non-constant weight moves everything (6/6), the
table keys the whole corpus (73,252 + 2 null excluded), the fold joins with 0 unmatched.

🔴 **`FINDING 72` — the basis was worth more than the band.** Switching `weight_dia` → `weight_dia_cal`
moves a Level-1 population time budget by **27.14 min/day (es)**, **0.03 (uk)** and **43.87 (it)**
against `G6.8`'s **8.0 min/day** band, and consumes up to **71 %** of the transition-TVD band. It is
country-correlated exactly as `FINDING 53` predicts — the UK weights already hit the calendar week, so
`weight_dia_cal` has nothing to do there, while ES and IT move a great deal. Left open, this would
have changed two folds of a leave-one-country-out design and left the third alone. **A second,
independent argument for the ruling, and it was not available when the ruling was made.**

### Q4 — the subset written down, and two corrections it forced

The ruled Eurostat-side subset is recorded: `Y15-20`, `Y20-24`, `Y25-44`, `Y45-64`, `Y_GE65`, with
`TOTAL` and the composite `Y20-74` excluded. Checking it against the downloaded tables produced
🔴 **`FINDING 73`**, in two parts.

1. **`Y65-74` is not absent — the age dimension is wave-dependent.** Split by `time`: `Y65-74` is
   populated in **504 of 504** cells in the **2000** wave and **0** in **2010**, identically in ES, UK
   and IT; `Y15-20`, `Y20-74` and `Y_GE65` are the mirror image. Eurostat replaced the band between
   waves. The ruled subset is therefore exactly the 2010 wave's own band set minus the aggregate and
   the composite — the right subset, for a reason that must be stated correctly: *"the band does not
   exist in the wave we score against"*, never *"Eurostat does not publish it"*. `FINDING 55`'s second
   half is corrected in place.
2. 🔴 **Two of the five ruled bands cannot be scored against our corpus.** Our finest age class is the
   eight-band prefix scheme, which is all a generated diary can ever carry. `Y25-44`, `Y45-64` and
   `Y_GE65` map exactly (two of our bands each); `Y15-20` and `Y20-24` do not, because our band is a
   single `15-24` — and the two cannot be merged from the published side either, since the units are
   rates and times with no band population to weight them. **`tus_00age` is scorable on three bands,
   covering 84.7 % of the corpus** (62,076 of 73,254); the unscorable slices are `15-24` at 10.8 %
   and `11-14` at 4.4 %, the latter never in scope since the table starts at 15. This is a coverage
   limitation of the reference table, fixed before any fold is scored, and it is declared with every
   `tus_00age` number.

⚪ `prereg.md` was not touched by any of the four; its md5 is unchanged.
