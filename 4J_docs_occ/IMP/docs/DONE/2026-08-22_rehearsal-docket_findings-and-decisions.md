# The Leg-4 rehearsal docket — everything the rehearsal found, and the five rulings it owes you

**Date:** 2026-08-22 (evening / night)
**Raised by:** executing `D-S7-3` (a) end to end — `envs/step7`, `G7.10`, the Leg-4 pilot rehearsal,
and the Step 6.3–6.5 evaluation path.
**Status:** OPEN. **Nothing has been enforced, rebuilt on a new basis, or frozen.** `prereg.md`
untouched throughout, md5 `e4243e07cdd80c9c846b91f40e3e8c45` re-checked after every job.

**This document is the index.** Each decision already has its own file; this one puts the eight
findings and the five rulings in one place, with the evidence that produced them, so nothing has to be
reconstructed from four separate documents.

| the four decision files this consolidates |
|---|
| `2026-08-22_D-S6-8_level1-crosswalk.md` |
| `2026-08-22_D-S6-9_the-bar-is-not-the-strongest-null.md` |
| `2026-08-22_D-S7-4_D-S7-5_firing-rate-and-copresence.md` |
| `2026-08-22_D-S7-3_generation-leg-and-environment.md` (ruled; execution record appended) |

Full evidence: `Step7_docs/4thJ_07_constrainedGeneration.md` (two entries of 2026-08-22 evening) and
`Step6_docs/4thJ_06_transfer.md` (four entries of the same evening).

---

## 0. Why a rehearsal at all, in one table

The pilot rehearsal generated **600 diaries per fold per arm** from the existing Leg-4 adapters and
pushed them through every downstream script that will ever see Leg-5 output. It was not meant to
produce a result. It was meant to find the things that would have destroyed the real campaign, and it
found eight of them.

| | what it found | what it would have cost if found later |
|---|---|---|
| `FINDING 80` | vLLM was handed the **whole-record** grammar while it masks only the **completion** | 0 of 16 valid. The entire generation campaign |
| `FINDING 81` | `G7.4` is **not enforced** — the household-indexed `COP` grammar variants do not exist | A gate recorded as an enforcement confirmation that was never wired in |
| `FINDING 82` | `G7.6` cannot fall unless `G7.2` has already fallen | A third confirmation counted as an independent measurement |
| `FINDING 83` | The `cop_alone` self-contradiction is **0 in 73,254 real diaries** and 39/23/59 in the pilot | The first clean model-side defect in Step 7, missed |
| `FINDING 84` | Four crosswalk errors, three of them one-directional and country-correlated | `G6.4` reporting a **31 %** travel error that belonged to the crosswalk, not the model |
| `FINDING 85` | The pre-registered *"strongest"* null is the **weakest in 6 of 9 cells** | Discovering it *after* a reportable result existed, where it reads as a reaction |
| `FINDING 86` | `G6.13`'s train-vs-test signal at `p < 1e-9` was a **9× pool-size artefact** | A privacy alarm published on a confound |
| `FINDING 87` | The MIA module generated under **right padding** on a decoder-only model | `G6.12` silently weakened on every short target — a **false negative in a privacy gate** |

🔴 Two of these — `FINDING 84` and `FINDING 86` — are cases where the **first implementation printed a
verdict**. The crosswalk printed a failing corpus; `G6.13` printed PASS on all three folds with one of
its three clauses silently not running. Both are the class this project's gate discipline exists for,
and both were caught by re-deriving rather than by reading a board.

---

## 1. What actually ran, and what it says

### Step 7 — constrained generation

`envs/step7` built (`vllm` 0.27.1, `xgrammar` 0.2.3, `bitsandbytes`), `envs/step4` untouched.
🔴 Three additive fixes were needed before it served a token, and one of them makes every Step 7
throughput number an **eager-mode floor**.

`G7.10` — **PASS, 0 disagreements** between the hand-written oracle and XGrammar over 10,000 strings
(5,000 valid, 5,000 malformed across 19 labels).

| | `es` | `uk` | `it` |
|---|---|---|---|
| constrained, valid | **600/600** | **600/600** | **600/600** |
| unconstrained, valid (`G7.5`, needs ≥ 99.90 %) | **2.67 %** | **7.33 %** | **4.00 %** |
| `<eor>`-terminated, **unconstrained** | 600/600 | 600/600 | 600/600 |
| `G7.13` at-home presence share | 73.11 % | 67.43 % | 69.35 % |

🟢 The unterminated-diary problem does not exist: **every** unconstrained diary ends with `<eor>`
without anything forcing it. The 2.67 % is a *tally* failure — durations that do not sum to 1440 —
not a syntax failure. That is the sharpest single statement the rehearsal produced about what the
grammar is buying.

Board: **12 PASS / 15 FAIL** over scored gates, eleven-run perturbation battery.
🔴 `G7.7`/`G7.8` are among the FAILs **for a sizing reason, not a model reason** — see §3.

### Step 6.4 — the level-1 time budget

`G6.4` and `G6.1` had **no implementation path at all** before this: nothing mapped our 158 activity
codes onto Eurostat's `acl00` aggregates, so neither the headline gate nor prereg §6's FAIL criterion
could be computed. Both now exist (`tools/4thJ_step6_level1.py`, selftest 48/48).

| arm | board | reading |
|---|---|---|
| **real corpus**, weighted by `weight_dia_cal` | 🟢 **9 PASS / 0 FAIL**, MAPE 1.33–4.94 % | the crosswalk is right |
| **Leg-4 pilot**, unweighted | 1 PASS / 8 FAIL | the pilot is wrong |

🔴 The signature is unmistakable and it is not a calibration problem: the pilot gives **106 min/day of
work to Spaniards over 65** (published: 5) and **65 to working-age Italians** (published: 263). A
1.48 B model at pilot settings **is not conditioning on the prefix**. That is the single most useful
number to carry into Leg 5, because it is exactly what Leg 5 has to fix.

`G6.1` null MAE — the bar the model has to beat, min/day, lower = harder:

| fold | `Y25-44` | `Y45-64` | `Y_GE65` |
|---|---|---|---|
| `es` | 9.93 | 8.82 | 11.81 |
| `uk` | 21.79 | 19.21 | 18.54 |
| `it` | 19.51 | 13.85 | 15.51 |

The pilot loses **9 of 9**. Expected, and it is the first time the bar has ever been computable.

### Step 6.5 — the privacy audit

`G6.13` (CPU, no GPU): **PASS 3/3** size-matched. Zero exact matches, zero records with NNDR < 0.33,
minimum DCR **0.0972** — about 14 of 144 ten-minute slots. All three clauses seen failing under
`verbatim` / `nearcopy` / `leak_all`.

`G6.10`–`G6.12`, fold `es`, Leg 4, n = 2,000 per class:

| | value | band | verdict |
|---|---|---|---|
| `G6.10` loss-based MIA, ROC-AUC | **0.5481** | ≤ 0.65 | PASS |
| `G6.10` TPR at 0.1 % FPR | 0.0005 | ≤ 0.05 | PASS |
| control — **untuned base** AUC | **0.4914** | ~0.50 | as expected |
| `G6.11` reference-based MIA, AUC | **0.5204** | ≤ 0.75 | PASS |
| control — train/test perplexity gap | **0.0143** | < 0.05 | PASS |
| `G6.12` extraction, 33 rare strata / 91 records | 0 greedy, 0 sampled | any = FAIL | PASS |

🔴 The **random-label-permutation adapter** control is **NOT RUN** and is written into the artefact as
a named gap. It needs its own training run. **`privacy_audit.md` cannot be written and no release
decision can rest on two of three registered controls.**

🟢 Since these were read, the module has been given its own **perturbation battery** (`FINDING 87`
fixed in the same pass) and **all three folds have been resubmitted**, so that `G6.10`, `G6.11` and
`G6.12` are each *seen failing* — which they had not been. Six injections, scored off one forward
pass: `null`, `g610_memorise`, `g610_tail` (the TPR clause alone, AUC unmoved at 0.4935 while TPR goes
0.0005 → 0.0800), `g611_reference` (confined to the base model's member losses, so only `G6.11` can
move), `pplgap_widen`, `g612_verbatim`.

---

## 2. The five rulings owed

Each is single-recommendation. None can be applied without you.

| # | decision | the choice | recommended |
|---|---|---|---|
| **1** | `D-S6-8` item 1 | `AC9A` = **sum of its seven children** vs the published parent. UK's parent exceeds its children by **48 min** and every other UK parent reconciles exactly | 🟢 **(a) children sum, all three countries** — identical in ES/IT, the only figure that reconciles in the UK |
| **2** | `D-S6-8` item 2 | Score the **three exactly-reproducible age bands** only, vs also scoring `TOTAL` | 🟢 **(a) three bands** — `TOTAL`'s population base is not stated and our floor is age 11. Cost: **ages 11–24 are not covered by `G6.4` at all**, which must be said plainly |
| **3** | `D-S6-9` | `G6.1`'s bar stays the **raked-donor null exactly as pre-registered**, vs the minimum across nulls, vs re-seeding the rake | 🟢 **(a) honour the pre-registration and report `FINDING 85` as a finding** — (b) is choosing the bar after seeing the numbers, (c) is a basis change to `D-S5-10` |
| **4** | `D-S7-4` | Constraint-firing rate **per diary** vs **per token** | 🟢 **(a) per diary** — the only reading the pre-registered 35 % / 2 % are sized for. 🔴 The methods must then say `G7.5` and `G7.7` are one measurement at two granularities |
| **5** | `D-S7-5` | What `G7.4` enforces: **self-contradiction only**, vs also household membership, vs neither | 🟢 **(1) self-contradiction only** — **zero** real diaries rejected, so additive. Household membership rejects **1.49 %** of real diaries at a **14.7× country spread**, which is a basis change |

`D-S6-8` items 3 and 4 are **already implemented as recommended** and need confirmation rather than a
choice: `weight_dia_cal` on the corpus arm and unweighted on the generated arm (a stated asymmetry,
because the synthetic prefixes *are* the fitted marginals and re-weighting would rake twice); and
**`MAE` in minutes reported beside every `MAPE`**, because `AC1_TR` at five published minutes turns a
pilot error into an APE of 2,020 %. 🔴 That second one bears directly on **prereg §6 FAIL criterion
2**, which is `MAPE > 20 %`.

---

## 3. 🔴 The sizing consequence, which binds the Leg-5 campaign

`V7.a` refuses to score `G7.7`/`G7.8` unless **10 strata carry ≥ 100 records each**. From the real
100,000-person prefix pools (228 strata per fold):

| fold | 10th-largest stratum share | minimum `N` |
|---|---|---|
| `es` | 1.96 % | **5,115** |
| `uk` | 1.92 % | **5,203** |
| `it` | 2.06 % | **4,850** |

**The Leg-5 campaign must be sized at `N ≥ ~5,200` per fold** or these two gates cannot be reported at
all. `N = 600` never could have reached it. `G7.9` is harder still — its rejection-sampled control
needs enough *valid unconstrained* diaries to match the constrained batch, ~22,500 draws on `es` at
pilot yields — and becomes affordable exactly to the extent Leg 5 raises `G7.5`.

---

## 4. Where the machine is right now

| job | what | state |
|---|---|---|
| 1286209 | **Leg-5 `es` fold training**, `gpu:nvidia_a100_7g.80gb:1` | PENDING |
| 1286208 | item 7.2 throughput, `Olmo-3-1025-7B` vs `Qwen2.5-7B` (unblocks `G7.12`) | PENDING |
| 1286235 / 1286236 / 1286237 | privacy audit **+ perturbation battery**, folds `es` / `uk` / `it` | PENDING |

🔴 Both 80 GB jobs have been queued for over two hours. Each node advertises **one** `7g.80gb` and
**nine** `2g.20gb` slices of the same physical GPU, so a single 2 GB slice in use blocks the whole
instance. This is a queue fact, not a fault, and it is the critical path.

🔴 **Only fold `es` of Leg 5 is submitted.** `uk` and `it` wait until the `es` fold's Step 4 gates have
been read — `D-S7-3` directive 4's own order: *"train … verify Step 4 gates, and execute the full
generation campaign."*

**Still owed after the rulings:** `G6.5`, `G6.6`, `G6.7` (the fictional-country control) and `G6.9`; a
Step 6 perturbation battery — **no Step 6 gate outside `G6.13` and the MIA module has been seen
failing yet**; the random-label-permutation adapter; and Step 7 items 7.4, 7.6 (chaining, decision 14)
and 7.7.

---

## 5. What is NOT in this document, deliberately

* **No ruling has been anticipated.** Every recommendation above is implemented only where it was
  already the neutral choice (`D-S6-8` items 3–4); `G7.4` enforces nothing, the grammar md5 is
  unchanged, `G6.1`'s bar is the pre-registered one, and `G7.7` is computed per diary only because a
  number had to be printed to size the campaign.
* **No Leg-4 number is reportable.** Every artefact from the rehearsal carries
  `"provenance": "LEG-4 PILOT -- NOT REPORTABLE"` in its own JSON. The pilot is a 1.48 B model at
  pilot settings; the reported model is `allenai/Olmo-3-1025-7B` at revision `a81bae42`.
* **Nothing has been deleted or repaired to make a board look better.** `G6.13`'s raw, un-matched
  train-vs-test comparison is still printed beside the size-matched one and still labelled `NOT THE
  VERDICT`, because removing it would hide `FINDING 86` and using it would be a false alarm.

---

## Author's Rulings & Directives (2026-08-22)

| # | Item / Decision | Ruled Option | Decision Summary | Action Required |
|---|---|---|---|---|
| **1** | `D-S6-8` Item 1 (`AC9A`) | 🟢 **Option (a)** | **`AC9A` = sum of its seven children across all three countries.** | Harmonise `AC9A` calculation in `tools/4thJ_step6_level1.py` as children sum; declare in methods as correction for Eurostat UK parent discrepancy (−48 min). |
| **2** | `D-S6-8` Item 2 (Age Base) | 🟢 **Option (a)** | **Score the 3 exact non-overlapping age bands only (`Y25-44`, `Y45-64`, `Y_GE65`).** Report `TOTAL` as informational context, never as a gate verdict. | Restrict `G6.4` scoring to the 9 exact cells (3 bands × 3 countries); state clearly in methods that ages 11–24 are not covered by `G6.4`. |
| — | `D-S6-8` Items 3 & 4 | 🟢 **Confirmed** | **Item 3**: `weight_dia_cal` on corpus arm, unweighted on generated arm.<br>**Item 4**: Report `MAE` (min/day) beside every `MAPE`; `MAE` carries reading for denominators $< 15$ min. | Declared asymmetry in weights preserved; both MAE and MAPE reported across all level-1 tables. |
| **3** | `D-S6-9` (The Bar / `G6.1`) | 🟢 **Option (a)** | **Honour pre-registration: `G6.1` raked-donor null remains the operative bar.** Report `FINDING 85` (reversal in 6/9 cells) transparently as an empirical finding. | Do not move the bar post-hoc; report full comparative table (`G6.1` raked vs `G6.2` per-donor vs `G6.3` pooled) in paper. |
| **4** | `D-S7-4` (Firing Rate / `G7.7`) | 🟢 **Option (a)** | **Constraint-firing rate measured per DIARY** (share of invalid diaries with mask OFF = $1 - G7.5$). Size Leg-5 campaign at $N \ge 5{,}200$ per fold. | Score `G7.7` per-diary per-stratum; state in methods that `G7.5` and `G7.7` are global and stratum-level views of the same measurement; generate $N \ge 5{,}200$ diaries/fold for Leg-5. |
| **5** | `D-S7-5` (Co-presence / `G7.4`) | 🟢 **Option (1)** | **Enforce self-contradiction only** (`cop_alone` + any other flag). Do NOT enforce household membership. | Filter out the 32 self-contradictory `COP` bit patterns in grammar ($0/73{,}254$ real diaries rejected); report household membership co-presence rates alongside `G7.3` without filtering. |

---

### Detailed Rulings and Directives

#### 1. `D-S6-8` Item 1 (`AC9A` Travel Aggregation) — Ruled: Option (a)
* **Choice**: Take `AC9A` as the sum of its seven child categories for ES, UK, and IT alike.
* **Rationale**:
  - In Spain and Italy, the published parent matches the sum of its children exactly ($70=70$, $79=79$).
  - In the UK, the published parent is $129$ min while its children sum to $81$ min (a $-48$ min discrepancy matching the anomalously high `AC99NSP` of $49$ min).
  - Summing children is uniform across all countries, avoids ad-hoc country-specific branches, and prevents penalising the model for an acknowledged published table flaw.

#### 2. `D-S6-8` Item 2 (`tus_00age` Age Base) — Ruled: Option (a)
* **Choice**: Score only the three exact, non-overlapping age bands (`Y25-44`, `Y45-64`, `Y_GE65`). Report `TOTAL` as informational background only.
* **Rationale**:
  - The Eurostat `TOTAL` row does not specify its lower age boundary, while our microdata begins at age 11.
  - Scoring `TOTAL` would introduce demographic composition distortion rather than evaluate model generative fidelity.
  - Transparently state in the methods that `G6.4` covers adults aged 25+, while youth/young adult validity (ages 11–24) is evaluated via `G6.8` joint structure and `G6.7` fictional-country controls.

#### 3. `D-S6-8` Items 3 & 4 (Weighting & Denominator Sensitivity) — Confirmed
* **Directives**:
  - **Weighting**: Apply `weight_dia_cal` to the empirical corpus arm and evaluate generated diaries unweighted (since generated prompts already sample from fitted marginal distributions). Drop the 2 UK diaries with missing `weight_dia_cal` with explicit notation.
  - **Denominator Stability**: Report absolute `MAE` in minutes/day alongside relative `MAPE`. For low-incidence categories ($< 15$ min/day, e.g. `AC1_TR` for seniors at 5 min), let `MAE` serve as the primary interpretative metric.

#### 4. `D-S6-9` (Operative Benchmark / `G6.1`) — Ruled: Option (a)
* **Choice**: Maintain the pre-registered raked-donor null (`G6.1`) as the official bar.
* **Rationale**:
  - Scientific integrity requires adhering to the frozen pre-registration (`prereg.md` §5).
  - Shifting the bar to the minimum across nulls (Option b) or retroactively altering the rake initialization (Option c) would constitute post-hoc outcome selection.
  - The fact that simpler unraked pooled/single-country nulls achieve lower MAE in 6 of 9 cells (`FINDING 85`) is a scientifically valuable empirical finding that will be reported and discussed transparently in the manuscript.

#### 5. `D-S7-4` (Mask Firing Rate / `G7.7`) — Ruled: Option (a)
* **Choice**: Define constraint-firing rate on a per-diary basis (the proportion of diaries failing structural validity when generated unconstrained).
* **Rationale**:
  - Per-token mask intervention in vLLM is near 100% across the vocabulary at almost every step, rendering token-level counts uninformative.
  - The per-diary metric aligns directly with the pre-registered $>35\%$ (base) and $<2\%$ (fine-tuned) criteria.
  - **Sizing directive**: Sizing the Leg-5 campaign at $N \ge 5{,}200$ per fold is approved and mandated to satisfy the `V7.a` stratum-occupancy threshold (10 strata with $\ge 100$ records).

#### 6. `D-S7-5` (Co-presence Validation / `G7.4`) — Ruled: Option (1)
* **Choice**: Enforce only the strict intra-episode self-contradiction rule (`cop_alone` combined with other co-presence flags).
* **Rationale**:
  - Real human diaries contain exactly $0$ self-contradictions ($0/73{,}254$), whereas the Leg-4 pilot generated dozens. Eliminating these 32 impossible bit combinations in the grammar is a purely structural improvement with zero real data rejection.
  - In contrast, enforcing household-membership consistency would eliminate $1.49\%$ of legitimate real diaries with extreme cross-national skew ($14.7\times$ between UK and IT), representing an un-registered modeling intervention.

---

⚪ `prereg.md` md5 `e4243e07cdd80c9c846b91f40e3e8c45` remains untouched and verified. Nothing is running on Speed.
