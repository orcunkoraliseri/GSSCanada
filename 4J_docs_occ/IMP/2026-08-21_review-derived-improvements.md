# Review-derived improvements — implementation document

**Created** 2026-08-21 · **Status** 🟢 **ALL FOUR OPEN DECISIONS RULED BY THE AUTHOR 2026-08-21 (late afternoon). NOTHING APPLIED YET — the next session executes.**
**Origin** Peer review of an external SoftwareX manuscript, plus `RP01`…`RP06`.
**Inputs**
`extra/reviewPaper-softwareX_paper/NOTES_FOR_4J.md` (short) ·
`…/NOTES_FOR_4J_longform.md` · `…/deepResearch/VETTING_RP01-RP06.md`
**Targets** `4thJ_00_HETUS_LLM_Pipeline.md` · `4thJ_00_HETUS_LLM_Pipeline_Overview.md` ·
`Step4_docs` · `Step5_docs` · `Step6_docs`

> **Nothing here is applied.** Every item below is a proposal with its evidence, its cost, and the
> perturbation that must be seen felling it. `feedback_read_the_gates_own_doc`: no item changes a
> registered basis — the one that would (I-1) is written as an additive diagnostic plus a decision
> the author must rule.

---

## 0-ter. 🟢 AUTHOR RULINGS — 2026-08-21 (late afternoon)

All four questions put to the author before implementation began. **No item is open; the next
session executes rather than deliberates.**

| # | Question | Ruling | Consequence |
|---|---|---|---|
| **`D-S5-14`** | How to fix `FINDING 67` | 🟢 **(a) — additive diagnostic, item 5.4 only** | Per-slot denominator **plus** an emitted coverage curve, reported **alongside** the existing `at_home_mae_pp`. Both numbers printed; neither replaces the other. **Nothing registered moves**, so `G4.1` and Step 6 are untouched and no scored gate re-opens. Unblocks `D-S5-13`. |
| **Scope** | How much to do before resuming step progress | 🟢 **ALL improvement items first** — *"appliquer toutes des etapes dans l'amelioration en avant de continuer avec de la progress des steps"* | 🔴 **`I-1` through `I-6` all execute before any further Step work.** Step-by-step progress resumes only when this document is closed. |
| **`I-2`** | `G6.14` as a gate or a diagnostic | 🟢 **Register it as a real gate `G6.14`** | Gets a row in the Step 6 gate table, a threshold, a **project-chosen** provenance label, and a perturbation that must be **seen felling it**. Covered by the "every gate seen failing" discipline. `G6.1`–`G6.13` and the frozen `G6.5` untouched. |
| **`I-4`** | Markov comparator in or out | 🟢 **Add it, reported not thresholded** | Fitted per fold on the N−1 training countries, margin reported **alongside `G6.1`**. 🔴 **Never a FAIL criterion — `G6.5` is frozen.** |

🔴 **The scope ruling is the one with teeth.** It converts this document from a list of proposals
into the **whole of the next session's work**. Do not start Step 6/7/8/9 progress, do not open a new
step doc, and do not treat any item here as optional because it looks like Step 6 machinery. When
every item is applied and this document's §8 checklist is complete, then step progress resumes.

### The `D-S5-14` implementation, as ruled

```python
num = [0.0]*N_SLOTS ; den = [0]*N_SLOTS          # den becomes a VECTOR
...
covered = min(slot, N_SLOTS)
for k in range(covered):
    den[k] += 1 ; num[k] += home[k]
```

Emit **three** things, not one:

* `at_home_mae_pp` — **existing, unchanged**, so every number already recorded stays comparable
* `at_home_mae_pp_covered` — **new**, computed over slots where both curves are defined
* `coverage_curve` — **new**, 144 values, the diagnostic that makes the confound visible

**Perturbation that must be seen felling it:** feed diaries truncated at 1000 minutes. The coverage
curve must fall to zero after slot 100 **and** the two MAEs must diverge. If they do not, the
per-slot denominator is not wired in and the result must not be reported.

🔴 **Still rejected, do not re-propose:** filtering to `sum == 1440`. It keeps 6–13 % of generated
diaries and keeps precisely the ones the model got right — one bias traded for a worse one.

---

## 0-bis. 🔴 PROVENANCE FIREWALL — read before acting on any item

**The author's instruction, 2026-08-21: we are not going to adopt the reviewed paper's pipeline.
That would be plagiarism. We improve the pipeline we already have.** This section exists so that
constraint is enforceable rather than merely understood, and so any item can be defended later.

**Three categories, and only the first two are ours to use.**

| Category | Status | Why |
|---|---|---|
| **A. Defects found in *our own* code** | ✅ **Ours outright** | `FINDING 67` is in `tools/4thJ_step5_temperature.py`. Nobody else's work is involved. Reading the manuscript is what prompted me to look; the bug, the evidence and the fix are entirely ours. |
| **B. Public literature and public method** | ✅ **Usable, cite the source** | The finite-sample floor, dwell-time W1, first-order Markov baselines, the ATUS User's Guide. All published, all independently re-derived, all citable. We reached them through `RP01`…`RP06`, whose prompts never mentioned the manuscript. |
| **C. The manuscript's own design** | 🔴 **OFF LIMITS** | Its architecture, its four ATUS strata, its three-layer interface, its tier structure, its DR scenario typology, its choice of metrics and thresholds, its wording. Not to be adopted, adapted, paraphrased, or cited — it is unpublished and confidential. |

**Provenance of every item in this document:**

| Item | Source | Category | Does it copy anything from the manuscript? |
|---|---|---|---|
| **I-1** `FINDING 67` | Audit of our own `at_home_profile()` | **A** | **No.** The bug is ours, in our file. The manuscript has a different bug in different code. |
| **I-2** `G6.14` | A generic completeness principle: a conditional distribution must have a constant denominator | **B** | **No — and note the direction.** The manuscript **fails** this check. We are adding a check it lacked, not copying one it had. |
| **I-3** `G6.8` checkers | 🔴 **Our own pre-registered spec**, `4thJ_06_transfer_val.md:44`, written long before this review | **A** | **No.** Nothing new is being designed; a checker is being written for a gate we already registered ourselves. |
| **I-4** Markov comparator | Richardson 2008, Widén & Wäckelgård 2010, Wilke 2013 — public, DOI-verified | **B** | **No.** The manuscript's baseline is a *fixed hour-of-day schedule*, which is the thing we criticised. We take the comparator from the literature it failed to cite, not from it. |
| **I-5** `FINDING 66` | Audit of our own script; `RP05` on determinism | **A + B** | **No.** |
| **I-6** Write-up | Public lineage; BLS ATUS User's Guide read directly; our own `FINDING 53` and `FINDING 63` | **B** | **No.** |

🔴 **The test to apply to any future item:** *could I have arrived at this by auditing our own code,
or by reading a published source?* If yes, it is ours. If the honest answer is *"only by having
read that manuscript"*, it is category C — **drop it, and do not record why.**

⚪ **Two further constraints that outlast this document.** (1) The manuscript stays confidential
**even after publication** as regards the review process itself. (2) It **may not be cited at all
until it is published**; if it later is, it becomes an ordinary citable paper like any other, and
`NOTES_FOR_4J.md` may then be used normally. Until then, nothing in `4J_docs_occ/extra/` may be
referenced from a manuscript file, a prompt, or a figure caption.

---

## 0. Summary

Reviewing someone else's ATUS pipeline found a **coverage defect**: a table that had to total 100
per hour did not, because a 04:00–04:00 diary had been binned on a 00:00–24:00 clock. Applying the
same check to our own code found the same *class* of defect in `at_home_profile()`, and it is
**contaminating the statistic item 5.4 is currently using to choose the decoding temperature.**

That is `FINDING 67` below and it is the only urgent item. The rest is a short list of small,
mostly additive improvements, and one pleasant surprise: **most of what the external literature
says is mandatory, we already pre-registered.**

🔴 **All six are now mandatory** — the author ruled that the whole improvement plan is executed
before step progress resumes. The "Blocking?" column below records *why* each matters, not whether
it is optional; none is.

| # | Item | Where | Effort | Status | Why it matters |
|---|---|---|---|---|---|
| **I-1** | 🔴 `FINDING 67` — per-slot denominator in `at_home_profile()` | `tools/4thJ_step5_temperature.py:130` | S | 🟢 **ruled `D-S5-14`(a)** | 🔴 **blocks `D-S5-13`** |
| I-2 | Hour-support constancy gate | Step 6 (new `G6.14`) | S | 🟢 **ruled: register as a gate** | the one boundary error nothing of ours would catch |
| I-3 | Implement `G6.8`'s dwell-time and transition checkers | Step 6, spec already written | M | ⚪ no decision needed | the gate is already registered; only the checker is missing |
| I-4 | First-order Markov comparator alongside the raked-donor null | Step 6 | M | 🟢 **ruled: add, reported not thresholded** | the default comparator a reviewer will name |
| I-5 | `FINDING 66` — seed the generation | `tools/4thJ_step5_temperature.py:239` | S | ⚪ no decision needed | gates the reproducibility sentence |
| I-6 | Write-up: TUS lineage, day bases, honest tier naming | `writing/` | S | ⚪ no decision needed | closes the citation and naming gaps |

---

## 1. 🔴 `FINDING 67` — the at-home profile counts missing diary tails as "away from home", and the error shrinks as temperature rises

### What the code does

`tools/4thJ_step5_temperature.py:130` `at_home_profile()` builds the 144-slot at-home curve:

```python
home = [0] * N_SLOTS                      # line 144 — initialised to NOT-at-home
for e in eps:
    n = dur // SLOT_MINUTES
    for k in range(slot, min(slot + n, N_SLOTS)):
        home[k] = 1 if loc == TH.LOC_AT_HOME else 0
    slot += n
if not ok or slot == 0:                   # line 154 — rejects only non-multiples of 10
    continue
den += 1                                  # line 156 — counts the diary for ALL 144 slots
for k in range(N_SLOTS):
    num[k] += home[k]
```

A diary whose episodes total less than 1440 minutes stops filling at `slot < 144`. **The remaining
slots keep their initial value `0`, and the diary is still counted in the denominator for every one
of them.** The tail is silently scored as "away from home".

There is a `sum == 1440` test in the file — `structural()` at line 201 — but `at_home_profile()`
does not use it. The two functions disagree about what a usable diary is.

### Why it matters here specifically

Every one of the 73,254 **real** diaries sums to exactly 1440, so the reference curve is clean.
**Generated** diaries almost never do: `sum_1440_frac` runs **0.050–0.135**. So the bias is
one-sided — it depresses the generated at-home curve in the late slots only — and its size is set
by how often the model fails to fill the day.

🔴 **And that failure rate moves along the temperature axis being swept.** The `uk` fold finished
while this document was being written (job `1285585`, COMPLETED 0:0), so the **full nine-point grid**
is available rather than the five partial points the impl doc carries:

| `uk` T | 0.50 | 0.60 | 0.70 | 0.80 | 0.90 | **1.00** | 1.10 | 1.20 | 1.30 |
|---|---|---|---|---|---|---|---|---|---|
| at-home MAE pp | 11.150 | 5.917 | 4.858 | 4.344 | 3.216 | **2.566** | 3.277 | 4.830 | 7.033 |
| `sum=1440` | 0.087 | 0.092 | 0.120 | 0.127 | **0.135** | 0.092 | 0.085 | 0.077 | 0.062 |
| `term` | 0.465 | 0.785 | 0.942 | 0.998 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |

🔴 **This corrects what the five partial points suggested.** `sum_1440_frac` is **not** monotone
across the grid — it peaks at T = 0.90 and then falls. Over all nine points
Spearman(MAE, `sum=1440`) = **−0.483**, which on its own would be weak evidence.

**But split the grid at the point where `term` saturates and the picture is much cleaner:**

* **Rising limb, T ≤ 0.90** — Spearman(MAE, `sum=1440`) = **−1.000**, and Spearman(MAE, `term`) =
  **−1.000** as well. Perfectly confounded; this limb proves nothing on its own.
* 🔴 **Falling limb, T ≥ 0.90, where `term` is pinned at exactly 1.000** — Spearman(MAE,
  `sum=1440`) = **−0.900**. Termination is constant, every diary ends properly, and yet the
  at-home MAE still tracks the 1440 fraction almost perfectly: as diaries fill less of the day
  (0.135 → 0.062), the MAE rises (2.566 → 7.033).

That second limb is the evidence. With the one competing explanation held fixed by the data itself,
the phantom away-from-home tail grows and the fidelity statistic worsens in step.

**Consequence:** an unknown share of the at-home MAE curve — including the position of its
minimum at T = 1.00 — is the artefact moving, not the model. `T_fidelity` is selected on a
statistic contaminated by a defect that varies along the swept axis.

⚪ **The `uk` fold happens to survive this.** `T_entropy` = 1.10 (|dH| = 0.0072 nats),
`T_fidelity` = 1.00, the two agree within tolerance, `T_chosen` = **1.10 on entropy matching**, and
neither is an endpoint. **Entropy matching does not use the at-home profile at all**, so `uk`'s
chosen value does not depend on `FINDING 67`. The fix is still owed: `es` and `it` are unread, the
agreement test consumes `T_fidelity`, and `G5.8` is scored on the curve.

### The fix, and why the obvious one is wrong

**Rejected — filter to `sum == 1440`.** That keeps 5–13 % of generated diaries, and keeps
*precisely the ones the model got right*. Small n and a selected subsample: a second bias traded
for the first.

**Proposed — per-slot denominator.** Count each slot only over the diaries that actually reach it:

```python
num = [0.0]*N_SLOTS ; den = [0]*N_SLOTS      # den becomes a vector
...
covered = min(slot, N_SLOTS)
for k in range(covered):
    den[k] += 1 ; num[k] += home[k]
return [num[k]/den[k] if den[k] else None for k in range(N_SLOTS)], den
```

and **report `den` as a coverage curve** beside the profile. `profile_mae_pp` then averages over
slots where both curves are defined. This is exactly the check that caught the external defect,
turned into a routine output.

### 🔴 `D-S5-14` — for the author

`at_home_profile`'s docstring states it is *"the same statistic `G4.1` scores"* and *"the same
family Step 6 scores its time-of-day cells on"*. So changing its denominator is **not local to item
5.4** — it is a basis change that reaches `G4.1` and Step 6. Options:

* **(a) Recommended.** Apply the per-slot denominator **and** emit the coverage curve, in item 5.4
  only, as a **new additive diagnostic reported alongside** the existing `at_home_mae_pp`. Both
  numbers are printed; neither replaces the other; nothing registered moves. The size of the
  confound becomes measurable, and `D-S5-13` can then be ruled on a clean number.
* (b) Change the statistic everywhere at once — `G4.1`, item 5.4, Step 6. Correct, but it is a
  basis change to a gate that has already been run and is out of scope for an open item.
* (c) Leave it and declare it. Cheapest, but `T_fidelity` stays contaminated and `D-S5-13` cannot
  be ruled honestly.

**Perturbation that must fell the new diagnostic:** feed it diaries truncated at 1000 minutes. The
coverage curve must drop to zero after slot 100 and the two MAEs must diverge. If they do not, the
per-slot denominator is not wired in.

**Cost:** about 20 lines, no re-run of anything already finished, no cluster time.

---

## 2. I-2 — Hour-support constancy gate (new, small)

**The gap.** Our batteries are episode-based: durations sum to 1440, round-trips exact, codes legal.
**A wall-clock-binned table passes every one of them**, because the error is in support per hour,
not in totals. `D-S2-5` already set origin 04:00 cyclic, so we do not have the bug — but nothing we
run would tell us if we reintroduced it.

**Proposal — `G6.14`.** Wherever episodes are binned into a time-of-day profile, assert that the
number of contributing diaries is **constant across all slots** within a conditioning cell (or, once
I-1 lands, that the coverage curve is flat).

* **Perturbation that must fell it:** bin one fold on a 00:00 origin instead of 04:00. Support must
  collapse in the first four hours and the gate must FAIL.
* **Where:** `Step6_docs/4thJ_06_transfer_val.md`, appended to the gate table; checker beside the
  existing Step 6 tooling.
* **Note:** this is a *new* gate, so it needs a row, a threshold, a provenance label
  (**project-chosen**) and a perturbation before it counts. It does not modify `G6.1`–`G6.13`.
* **Cost:** one function plus one perturbation.

## 3. I-3 — Implement `G6.8`; the specification already exists

I recorded in the first draft of the notes that we had no episode-length gate. **That was wrong.**
`Step6_docs/4thJ_06_transfer_val.md:44` already defines:

> **G6.8** Joint-structure scores — Score quantities **never in the prompt**: co-presence
> cross-tabs, transition entropy, **dwell-time distributions** conditioned on **attribute pairs**.
> All must clear their Tier 1 and Tier 2 thresholds on the held-out country.

and the Overview's Tier 1 table supplies the numbers it inherits:

| Quantity | Threshold | Provenance |
|---|---|---|
| Dwell-time distribution, Wasserstein-1 per activity | ≤ **10.0 min** (= one slot width) | project-chosen |
| Transitions per day | ≤ **1.50** absolute error | project-chosen |
| Transition-matrix TVD | ≤ **0.050** | project-chosen |
| Diurnal marginal divergence | JSD in **bits** — no `epsilon`, bounded | project-chosen |

The Overview also already pre-registers the null discipline the external literature calls mandatory:
*"a sample-size-matched bootstrap, where the synthetic-to-real divergence must not exceed the
real-to-real split-half divergence"*, and the **shuffled-diary control** that must PASS marginals and
FAIL transitions and dwell.

🔴 **So there is no gate to design — only a checker to write.** `grep` of `tools/` finds no
dwell-time or transition-count implementation; Steps 2/3/5 did not need one, Step 6 does.

* **Reference is already on disk:** 2,024,068 real episodes, all summing to 1440.
* **Perturbations, both already specified:** the shuffled diary (must fail dwell and transitions,
  pass marginals) and the modal-collapse generator.
* **Cost:** medium. This is the largest item and the most valuable after I-1.

## 4. I-4 — A first-order Markov comparator (small addition, not a replacement)

`RP01` is unambiguous that the field's accepted comparator for a generative occupancy model is a
**first-order inhomogeneous Markov chain fitted to the same microdata**. In our docs "Markov"
appears only as the Step 8 **day-chaining** rule, never as a generation baseline.

* Our nulls — the raked-donor null (`G6.1`, built, 34 selftests green) and the pooled average
  (`G6.3`) — are **stronger** than what the literature asks for. Nothing is wrong.
* **But the comparator a reviewer will name by default is absent**, and adding it makes the
  raked-donor null read as deliberate rather than idiosyncratic.
* **Proposal:** fit a first-order inhomogeneous Markov chain per fold on the N−1 training
  countries; report its margin **alongside** `G6.1`, as a *reported* quantity, not a new bar.
  🔴 It must not become a FAIL criterion — `G6.5` is frozen and this does not touch it.
* **Cost:** medium; it reuses the Step 6 scoring path.

## 5. I-5 — `FINDING 66`, and the reproducibility sentence that depends on it

`tools/4thJ_step5_temperature.py:239` calls `model.generate(..., do_sample=True, ...)` with **no
`torch.manual_seed` anywhere in the file**, while the result JSON writes `seed: 42` — which scopes
only the prompt draw at line 326.

`RP05` confirms bit-exact local reproducibility needs `batch_size=1`,
`torch.use_deterministic_algorithms(True)`, `CUBLAS_WORKSPACE_CONFIG=:4096:8` **and a fixed GPU
architecture**. 🔴 Speed jobs can land on different physical nodes, so **we cannot claim
bit-reproducibility at all**.

* **Fix (additive):** `torch.manual_seed(s)` before each `generate_at`, `s` recorded per row, and
  rename the JSON key `seed` → `prompt_seed`.
* **Do not apply while the three sweep jobs are running** — the script on Speed must not move under
  them.
* **The claim we may then make:** *"pinned base revision + pinned adapter + recorded seeds"*, never
  "reproducible". **Do not write the reproducibility sentence before the seeding is in.**

## 6. I-6 — Write-up items (no code)

* **TUS lineage paragraph** in Related Work. Our Paper-1 high-order Markov baseline at 0.691 vs 0.98
  is the right *family*; we never said which family. Two reviews cover the lineage in one citation
  each — Osman & Ouf (2021) `10.1016/j.buildenv.2021.107785`; Vosoughkhosravi et al. (2023)
  `10.1016/j.enbuild.2023.113245`. Full verified list in `NOTES_FOR_4J.md` §7.
* **Day bases.** ATUS oversamples weekends *by design* (10 % per weekday, 25 % per weekend day) and
  repairs it *inside* `TUFINLWGT` — both verified verbatim from the BLS User's Guide. Our three
  folds sit on three different day bases and only the UK is calendar-representative (`FINDING 53`).
  🔴 The framing improves: not "HETUS leaves this open" but **"ATUS repairs this in the weight; our
  files do not, and we repaired it ourselves in `weight_dia_cal`"** — a limitation turned into a
  contribution. Needs one check against the Eurostat 2018 guidelines first.
* **Joint fidelity, stated honestly.** `RP03`: fine-tuning shifts conditional probabilities toward
  the empirical distribution but does **not** certify the joint. Our `FINDING 63` (1,512 employed
  Italian 13-year-olds off one donor diary) is that exact failure mode, caught in our own pipeline.
  Say so — it is evidence we inspect joints, not only marginals.
* **Tier naming pass.** Ask of each gate: *what is the reference, and is it derived from the thing
  being scored?* `G5.1` is convergence, not fidelity. `G6.1`'s null and the model share a reference
  by deliberate design (`score_margin` Guard 1) — that needs **one written paragraph** saying why it
  is not circular, not a rename.

---

## 7. What does NOT change

* **The two figure prompts.** `4thJ_pipeline_steps_figure.md` §5 uses generic tier labels
  (`distributional fidelity` → Step 6). Implementing `G6.8` or adding `G6.14` changes **no permitted
  text string** in §6. `4thJ_graphical_abstract.md` is unaffected. 🔴 **No image needs regenerating**
  — which also respects `feedback_never_create_images`.
* **Secondary activity.** Already ruled: §3B-bis records Spain at 12.2 % of slots, `act2_raw` carried
  through Steps 1–2 but deliberately **not serialised** (a field only one country can emit leaks
  country identity into LOCO), and `D-S9-1` dropped `act2`. **Do not re-open.** One sentence in the
  limitations, phrased as a design choice.
* **`G6.1`–`G6.13`, `G6.5`'s frozen FAIL criteria, and `prereg.md`** (md5
  `e4243e07cdd80c9c846b91f40e3e8c45`). Nothing here edits any of them.
* **Our divergence metric.** Tier 1 already uses JSD in bits, so the `epsilon` pathology
  (`epsilon` 1e-4 → 1e-15 moves a "superiority multiplier" 461× → 1727×) does not reach us. One
  check owed: **confirm we never divide two divergences anywhere in the write-up.**

---

## 8. Order of work — 🔴 ALL SIX, before any further step progress (author ruling)

Tick each box only when the item is applied **and** its perturbation has been **seen felling** the
check it guards. An item that has never been seen to fail has not been shown to work.

- [x] 🟢 **0.** Poll `1285584` (`es`) and `1285586` (`it`); read their **full nine-point grids**; append
      both to `Step5_docs/impl/2026-08-21_item5.4-temperature.md`.
      🔴 **Do not rule anything on partial curves** — `uk`'s five partial points suggested a monotone
      confound that the full grid then corrected.
- [x] 🟢 **1. I-1** — apply `D-S5-14`(a): per-slot denominator, coverage curve, three emitted values.
      Perturbation: diaries truncated at 1000 min. Then re-derive the item 5.4 curves.
- [x] 🟢 **2.** Rule **`D-S5-13`** on the clean numbers. Then `scp` the three JSONs back, write
      `outputs_step5/temperature_calibration.md` and `generation_config.json`.
- [x] 🟢 **3. I-5** — `FINDING 66`: `torch.manual_seed(s)` before each `generate_at`, `s` recorded per
      row, JSON key `seed` → `prompt_seed`. 🔴 **Only after `es`/`it` have landed** — the script on
      Speed must not move under running jobs.
- [x] 🟢 **4.** Write the real **`G5.8`** / **`G5.9`** checkers with their perturbations
      ("report only the fidelity curve" fells `G5.8`; `top_p = 0.9` fells `G5.9`).
      🔴 **`G5.9`'s antecedent is false** — we do not use top-p, the config carries `top_p: 1.0`, so
      the gate is **vacuously satisfied** and must be written that way. A checker that reads
      `1.0 > 0.98` and FAILs would be wrong. Re-run `tools/4thJ_gates_step5.py`. **Close Step 5.**
- [x] 🟢 **5. I-3** — write the `G6.8` dwell-time and transition checkers against the thresholds
      already registered in the Overview's Tier 1 table. Perturbations already specified: the
      shuffled diary (must PASS marginals, FAIL dwell and transitions) and the modal-collapse
      generator.
- [x] 🟢 **6. I-2** — add **`G6.14`** to the Step 6 gate table: row, threshold, **project-chosen**
      provenance label, and the perturbation (bin one fold on a 00:00 origin) seen felling it.
- [x] 🟢 **7. I-4** — the first-order inhomogeneous Markov comparator, fitted per fold on the N−1
      training countries, **reported alongside `G6.1`, never as a FAIL criterion**.
- [x] 🟢 **8. I-6** — write-up: TUS lineage paragraph, the day-bases framing, joint-fidelity honesty,
      the tier-naming pass, and the `G6.1` non-circularity paragraph.
- [x] 🟢 **9.** Close this document. **Only then does step progress resume.** — 🟢 **CLOSED 2026-08-22, see §16.**

## 9. Ledger

| Date | Action | Result |
|---|---|---|
| 2026-08-21 | Audited `at_home_profile()` against the item 5.4 result tables | `FINDING 67` recorded; `D-S5-14` raised |
| 2026-08-21 | Grepped `tools/` for dwell-time / transition checkers | none exist; `G6.8` is spec-only |
| 2026-08-21 | Re-read Overview Tier 1 table and `4thJ_06_transfer_val.md:44` | thresholds and null discipline already registered — no gate design needed |
| 2026-08-21 | Checked both figure prompts against every proposal | no permitted string changes; no image work |

## 10. Verified

* `at_home_profile()` has no `sum == 1440` guard; `structural()` at line 201 does. Read from source.
* The full nine-point `uk` grid was read from `/speed-scratch/o_iseri/4J_step5_temp_1285585.out` and
  the Spearman coefficients in §1 (−0.483 all points; −1.000 rising limb; **−0.900 falling limb with
  `term` pinned at 1.000**) were computed from it, not quoted.
* `uk` job `1285585` COMPLETED, exit `0:0`, elapsed `03:44:37`; artefact
  `temperature_calibration_uk.json`, md5 `e2401535d61f4783021bbb0f4325afb3`; `T_chosen` = 1.10 on
  entropy matching, `agree` = true, neither endpoint flag set.
* `G6.8` names dwell-time distributions; Overview Tier 1 supplies W1 ≤ 10.0 min, transitions ≤ 1.50,
  TVD ≤ 0.050, JSD in bits, the split-half bootstrap and the shuffled-diary control.
* No dwell/transition checker in `tools/`.
* Figure prompt §5 tier labels are generic; §6 permitted strings unaffected.
* BLS ATUS User's Guide quotes (day allocation p. 13; weight construction p. 37; secondary
  activities p. 57) read from the PDF, not from a response.

## 11. WHAT I DID NOT VERIFY

* **`es` and `it` are still running** (`1285584`, `1285586`, both RUNNING on `speed-39` at
  `3:59:43`). Only `uk` is read back. The `es`/`it` rows in §1's earlier partial tables are still
  three points each and their full grids may change the picture, as `uk`'s did.
* **I did not re-derive `uk`'s at-home MAE under the corrected denominator** — that number does not
  exist yet and is exactly what I-1(a) produces.
* **I did not quantify how much of the at-home MAE movement is the artefact.** That is precisely
  what I-1(a) is for — the number does not exist yet, and no claim here depends on its size.
* **I did not confirm `G4.1` and Step 6 use the identical function.** The docstring says "the same
  statistic" and "the same family"; I did not trace either call site. `D-S5-14`'s scope depends on
  this and it should be checked before option (b) is ever considered.
* **I did not check whether the write-up divides two divergences anywhere.** Listed as owed in §7.
* **I did not verify the HETUS secondary-activity claim** in `RP06` (that HETUS carries a full second
  column). Irrelevant while `D-S9-1` stands, but the notes flag it.
* **I did not read Step 0, 1, 2, 3, 7, 8 or 9 docs in full** — only targeted greps. No item above
  touches those steps; if one is thought to, it needs its own read first.

---

## 12. 🟢 EXECUTION PASS — 2026-08-21 (evening). SEVEN OF NINE BOXES CLOSED.

**What is done, and what each was seen doing.**

| Box | Item | State | The evidence, not the intention |
|---|---|---|---|
| **0** | poll `es`/`it`, full grids | 🟢 **DONE** | both COMPLETED `0:0`; full nine-point grids appended to the item ledger; **two of three folds DISAGREE and `es` sits on the grid endpoint** |
| **1** | `I-1` = `D-S5-14`(a) | 🟢 **DONE** | 14/14 selftest green; legacy curve **bit-identical** to a verbatim copy of the old function; truncation perturbation **seen felling it**, coverage 10 → 0 exactly at slot 100, MAEs separated by **25.000 pp** |
| **2** | rule `D-S5-13`, write the two artefacts | 🟢 **DONE — see §14** | jobs `1285712`/`1285713`/`1285714` RUNNING; `temperature_calibration.md` and `generation_config.json` wait on them — ⚪ *superseded:* 🟢 **ALL THREE landed** (`1285712`/`1285713`/`1285714`, all `0:0`); artefacts + 45 generation files pulled; **`generation_config_{es,uk,it}.json` written** and **`outputs_step5/temperature_calibration.md` written (352 lines, GENERATED from the artefacts — regenerate, never edit)**. 🔴 Produced `FINDING 74` (the trap fired; `T_chosen` argmin STABLE 5/5 on all three folds, but the FIDELITY argmin MOVES on `es` and `uk` — both ship as BANDS) and `FINDING 75` (the 1440 error is TWO-SIDED; §1 of this document is corrected in place). |
| **3** | `I-5` = `FINDING 66` | 🟢 **DONE** | `torch.manual_seed` per `generate_at`, `gen_seed` per row, `seed` → `prompt_seed`, `reproducibility_claim` string; **confirmed running on GPU** (`--- T = 1.00  seed 101`) |
| **4** | `G5.8`/`G5.9` checkers | 🟢 **DONE — NO GATE IS BLOCKED ANY MORE** | both have real checkers and both report **BLOCKED**, not PASS, until their artefacts exist; battery now **36 verdicts: 30 PASS, 0 FAIL, 6 BLOCKED**, coverage clause clean. 🟢 **+ selftest 17/17** (`4thJ_step5_g58_g59_selftest.py`): both registered perturbations demonstrated felling their gate on constructed state, and `FINDING 69` shown as a measurement — the as-written reading rejects `top_p` 0.99 and admits 0.50. ⚪ *superseded:* Board **36 verdicts: 34 PASS, 2 FAIL, 0 BLOCKED**, coverage clause clean. 🟢 `G5.9` scores on all three folds and its registered perturbation fells all three — impossible under the superseded reading, so `FINDING 69`’s ruling is DEMONSTRATED. 🟢 `G5.8` PASSES on `it` and its perturbation fells it. 🔴 **`G5.8` FAILS on `es` (0.51×) and `uk` (0.99×) and is LEFT FAILING** — `D-S5-16` is open on whether that is the terminal verdict, and it is the ONLY thing Step 5 still waits on. |
| **5** | `I-3` = `G6.8` checkers | 🟢 **DONE** | 17/17 green; **seen failing** under the registered control on all three sequence arms while the marginal arm passes to machine zero |
| **6** | `I-2` = `G6.14` | 🟢 **DONE** | registered with a row, a band, a **project-chosen** label; 9/9 green; **seen failing**, support 0 in slots 0–23 exactly |
| **7** | `I-4` = Markov comparator | 🟢 **DONE** | fitted `es`+`uk` → scored on `it`; refuses to emit any verdict at all |
| **8** | `I-6` = write-up | 🟢 **DONE** | `writing/4thJ_writeup_notes.md`; the owed §7 check is closed — **we never divide two divergences anywhere** |
| **9** | close the document | ⚪ **OPEN** | closes when boxes 2 and 4 close, which is when `1285712`–`1285714` land. 🔴 **`D-S5-15` (from `FINDING 71`) is now owed to the author and does NOT block this document** — it is additive and changes no `T_chosen`. 🟢 **2026-08-21 night: `D-S5-15` and `FINDING 69`, plus the two RESIDUES of the already-ruled `D-S6-4`/`D-S6-5`, are written up with every option's consequence at `IMP/docs/2026-08-21_questions-for-the-author.md`** — 🟢 **AND ALL FOUR CAME BACK RULED THE SAME NIGHT AND ARE APPLIED, §13: `FINDING 69` closed (selftest 17/17, the perturbation now fells the gate), `G6.8` wired to `weight_dia_cal` (byte-identical additivity + `FINDING 72`), the `tus_00age` subset written down (`FINDING 73`), and `D-S5-15`(a) submitted as jobs `1285777`/`1285778`/`1285779`** |

---

### 🔴 `FINDING 68` — the Tier 1 bands are not evaluable at cell level, and a perfect model fails them

Found by writing `G6.8`'s checker and running it on **real data first**, which is the only reason it
was found at all. Applied per attribute-pair cell (n ≥ 100 both sides), the absolute Tier 1 bands
fail on a **second real sample** of the same country in **65 of 68 cells**. Per-cell real-vs-real
distributions, Italy: dwell-time W1 **median 9.80 min** against a **10.0 min** band; diurnal JSD
fails 65 of 68; transition TVD median 0.032 against 0.050. Only transitions/day is evaluable at cell
granularity (median 0.15 against 1.50, 1 of 68 cells failing).

The bands are **population-level** and correct there — real-vs-real reads dwell 2.03 min,
transitions 0.076, TVD 0.0087, JSD mean 0.00044 bits, comfortably inside every one.

🟢 **RULED (a) by the author, 2026-08-21.** The per-cell verdict is taken on the **already-registered
sample-size-matched comparison**, not on the absolute band — Overview, statistical discipline: *"a
sample-size-matched bootstrap, where the synthetic-to-real divergence must not exceed the
real-to-real split-half divergence. That last comparison is the honest one."* **This designs
nothing**: it implements a comparison that was pre-registered and never implemented.

**Calibrated rather than asserted.** The floor is the worst of 20 real-real draws, every comparison
at matched sample size m vs m, and the family-level null is printed with the result because under
the null each metric exceeds all R floors with probability exactly 1/(R+1):

| candidate | cells with ≥1 exceedance, of 68 | metric exceedances, of 408 |
|---|---|---|
| a second REAL sample | **18** (null expects **17.3**) | 28 (null expects 19.4) |
| the shuffled control | **68** | **317** |

🔴 **The absolute bands are not dropped** — they are enforced at population level and reported
per cell alongside. Both numbers are printed; neither replaces the other.

---

### 🔴 `FINDING 69` — `G5.9`'s registered text and its registered perturbation contradict each other

`G5.9` reads *"if top-p is used at all, **p ≤ 0.98**"*. The perturbation table says *"set
`top_p = 0.9`"* must fell it. **Both cannot hold: 0.9 satisfies p ≤ 0.98.**

In nucleus sampling a **smaller** p truncates **more**. As written the gate admits p = 0.5 — half the
tail deleted — and rejects p = 1.0, no truncation at all: the exact opposite of a gate named "no
truncation creep", and the opposite of what its own perturbation expects. The coherent reading is
**p ≥ 0.98**, under which our `top_p = 1.0` is vacuously satisfied (top-p not used) **and** the
registered perturbation fells the gate.

The checker **evaluates and prints both readings** and takes its verdict on the coherent one,
because it is the only one under which the registered perturbation does what the register says it
does. 🔴 **This is a discrepancy in a registered gate and is flagged, not quietly resolved** — it is
recorded here and in the checker's docstring, and one line of the val doc closes it whichever way it
is ruled. It changes nothing about our configuration, which carries `top_p = 1.0` either way.

---

### ⚪ Two smaller things established by running the controls, both recorded so they are not re-litigated

1. **"Shuffled diary (slots permuted, totals preserved)" is ambiguous, and only one reading works.**
   Permuting a diary against **itself** preserves its own budget and **destroys the population
   day-shape** (diurnal JSD 0.178 bits), so it cannot satisfy "must PASS Tier 1 marginals".
   Permuting **across diaries at a fixed slot index** preserves both marginals to machine zero
   (budget error 0.000000000 min, JSD 0.000000000000 bits) and destroys every within-diary sequence.
   The second is the registered control; both are built and both are reported.
2. **A rotation is not the binning defect.** Reading the diary's minute 0 as wall-clock 00:00 puts
   every profile four hours out of place and `G6.14` **correctly passes it** (38260/38260). The
   defect is the **frame** error — the diary runs 04:00 → 28:00, is placed at true wall-clock time,
   and the past-midnight part is dropped rather than wrapped. The first construction tried did not
   fell the gate, and that is why perturbations get run instead of described.

---

### 🔴 What `I-1` could not do, and the line that has to be in the ledger

**The 27 finished generation passes did not save their text.** So `at_home_mae_pp_covered` and the
coverage curve **do not exist for any point on the three primary grids** and cannot be recovered
without generating again. §1 estimated "no re-run of anything already finished, no cluster time";
that is true of the **fix** and false of the **numbers**. The clean numbers arrive with the
`D-S5-13`(a) replicates, inside work already scheduled, at no additional GPU cost — and the
replicate run **persists its generations**, so this cannot happen a third time.
🔴 **This paragraph is over-stated and is corrected by `FINDING 71` below**: the replicate
windows sit around `T_chosen` (the *entropy* optimum), so on `es` and `it` they exclude
`T_fidelity` entirely and the covered-basis curve arrives as a three-point stub on the wrong side
of the optimum. See `D-S5-15`.

---

### ⚪ Scope check that `D-S5-14` left open is now closed

`at_home_profile` is defined **once** and called **twice**, both in
`tools/4thJ_step5_temperature.py`. `G4.1` uses a **different function** — `at_home_share()` at
`4thJ_step4_train.py:150`, a per-diary scalar normalised by that diary's own total minutes, which
grows no phantom tail. `G4.1` never had `FINDING 67`. Option (a)'s scope claim holds **by
construction**, and option (b) would have had nothing to change.

---

### WHAT THIS PASS DID NOT VERIFY

* **`G6.8` and `G6.14` were run on fold `it` only.** Nothing in either is Italy-specific, but no
  number here transfers to `es` or `uk` and none may be quoted for them.
* **No generated diaries were scored by anything in Step 6.** There is no Step 6 generation. `G6.8`
  has been exercised against real data and constructed controls only; its verdict on the model does
  not exist.
* **The Markov comparator has not been compared to the raked-donor null** — that is a Step 6 run,
  and the ruling defers Step progress until this document closes.
* **The Eurostat 2018/2020 HETUS guidelines were not read** for the day-allocation question. The
  write-up paragraph states what our three files do, which is measured, and not what the framework
  requires.
* **`G5.8`/`G5.9` have never been seen PASSING or FAILING ON THE REAL ARTEFACT** — only BLOCKED.
  🟢 **Superseded in part**: their perturbations are now demonstrated felling them on CONSTRUCTED
  state (selftest 17/17, see the box-4 section below), so they are known to fire. The **real**
  verdict still cannot exist until `1285712`–`1285714` land, and only that counts for the record.

---

### 🔴 `FINDING 71` — the covered-basis curve `D-S5-14`(a) was ruled to produce will NOT exist where it is needed, and §12's promise above is over-stated on two of three folds

§12 says of `I-1`: *"The clean numbers arrive with the `D-S5-13`(a) replicates, inside work already
scheduled, at no additional GPU cost."* That sentence was written without checking **where** the
replicate windows sit relative to the thing the covered basis exists to test. Checked now, from the
two files themselves and not from memory:

| fold | primary grid | `T_fidelity` (legacy basis) | replicate WINDOW | is `T_fidelity` inside the window? |
|---|---|---|---|---|
| `es` | 0.50 … 1.30 (9 pts) | **0.70** | 1.10, 1.20, 1.30 | 🔴 **NO** — four grid steps outside |
| `uk` | 0.50 … 1.30 (9 pts) | **1.00** | 1.00, 1.10, 1.20 | ⚪ yes, but **at the window edge** |
| `it` | 0.50 … 1.30 (9 pts) | **0.80** | 1.10, 1.20, 1.30 | 🔴 **NO** — three grid steps outside |

Sources: `tools/4thJ_step5_temperature_replicates.sh:58-60` (windows, pre-registered before the run)
and `temperature_calibration_{es,uk,it}.json` (`grid`, `T_fidelity`). The windows are correct for the
job they were pre-registered to do — `D-S5-13`(a) reads *"a narrow window around each fold's
`T_chosen`"*, and `T_chosen` is the **entropy** optimum. Nothing about them is a mistake. The
mistake is §12's claim that they also discharge `I-1`.

**Consequence, stated exactly.** After `1285712`–`1285714` land we will hold
`at_home_mae_pp_covered` at **3 of 9 grid points per fold**, and on `es` and `it` those three points
lie **entirely on the far side of the legacy fidelity optimum**. So:

* the **coverage curve** `D-S5-14`(a) obliges us to report exists only as a three-point stub;
* `fidelity_argmin_moved_under_D_S5_14` — the single quantity that would confirm or refute
  `FINDING 67`'s claim that the fidelity criterion is distorted by uncovered tails — is
  **not evaluable on `es` or `it`**, because the candidate it would have to move *from* was never
  generated on the covered basis;
* and in replicate mode the script does not compute that key at all, correctly: the covered argmin
  lives in the `elif usable` branch (`4thJ_step5_temperature.py:612-625`), which a replicate run
  deliberately skips so that it cannot choose. ⚪ **This is not a bug** — it is `D-S5-13`(a) working
  — but it means the comparison has to be read off the rows by hand, on the folds where it exists.

🔴 **This does not block Step 5 and must not be used to re-open a temperature.** `T_chosen` is
frozen by the primary run, `G5.8` scores the reporting obligation and the sensitivity clause, and
neither reads the covered basis. What it blocks is the sentence in §12, which is corrected here.

### ⚪ `D-S5-15` — for the author, one yes/no

**Does `D-S5-14`(a)'s coverage curve get generated on the full grid, or is it declared a stub?**

* **(a) — recommended.** One additional job per fold: single seed, the **full nine-point grid**,
  `--save-gen`, same GPU class, queued behind the replicates. ≈ 2.5 h per fold, no new code — the
  script already computes and stores `at_home_mae_pp_covered` per row and already persists
  generations. This is what makes `FINDING 67` a **measured** claim on all three folds instead of an
  argued one, and `FINDING 67` is the origin of the whole `D-S5-14` ruling.
* **(b)** Declare the coverage curve a three-point stub, report it as such in
  `outputs_step5/temperature_calibration.md` §4, and record that `FINDING 67` stays an **argument
  from the code path plus a `uk`-only measurement**, never a cross-fold measurement.

🔴 Whichever is ruled, the fix is **additive** and touches no threshold, no `T_chosen`, and not
`prereg.md`.

---

### 🟢 BOX 4, PARTIAL — `G5.8`/`G5.9` NOW HAVE A SELFTEST, AND `FINDING 69` IS DEMONSTRATED RATHER THAN ARGUED

`G5.8` and `G5.9` were the **only two checkers in this project with no `_selftest.py`**, and §12's
*"WHAT THIS PASS DID NOT VERIFY"* said so: they had never been seen doing anything but BLOCKED.
That gap needed no GPU and no artefact, so it is closed while `1285712`–`1285714` run.

`tools/4thJ_step5_g58_g59_selftest.py`, **17 of 17 green**, drives both checkers through PASS / FAIL
/ BLOCKED on constructed state whose row keys are the ones `4thJ_step5_temperature.py` actually
writes. What it establishes:

* **Both registered perturbations fell their gate.** *"Report only the fidelity curve"* → `G5.8`
  FAIL (`not reported: entropy curve, one of T_entropy/T_fidelity`). *"Set `top_p = 0.9`"* → `G5.9`
  FAIL. Neither was previously known to fire.
* **`G5.8` cannot be carried by either half alone.** A calibration with a perfect sensitivity block
  but no agreement statement still FAILs; a perfect reporting block with 4 seeds still FAILs; and
  `NOISE DOMINATES` (step 0.05 against a re-run range of 0.10) FAILs with the val doc's own
  consequence in the message — *the deliverable is the BAND*.
* **BLOCKED is returned only when the artefact is absent**, on both gates, which is the property that
  stopped BLOCKED from being a thing a human forgets to revisit.

🔴 **`FINDING 69` is now demonstrated in two lines of output, not argued from the text:**

| `top_p` | what it does | coherent reading `p >= 0.98` | **as-written reading `p <= 0.98`** |
|---|---|---|---|
| 0.99 | deletes almost nothing | PASS | 🔴 **FAIL** |
| 0.50 | deletes half the tail | FAIL | 🔴 **PASS** |

The as-written reading **rejects the harmless configuration and admits the destructive one**, in a
gate named *"no truncation creep"*. That is the contradiction stated as a measurement. ⚪ Our own
`top_p = 1.0` reads PASS as vacuously satisfied either way, so nothing about the configuration turns
on the ruling — one line of the val doc closes it.

⚪ **This is not the real verdict and is not claimed as one.** A gate is *seen failing* for the
record when its registered perturbation fells it on the **real** artefact. Box 4 still closes on
`1285712`–`1285714`; what changed is that we now know the perturbations fire, instead of finding out
at the last step.

---

## 13. 🟢 2026-08-21 (night) — THE AUTHOR RULED ALL FOUR OPEN QUESTIONS AND ALL FOUR ARE APPLIED

The four items written up at `IMP/docs/2026-08-21_questions-for-the-author.md` came back ruled the
same night. Three are closed in code and documentation; the fourth is on the GPU. The rulings and
their full rationale are recorded inside that document; what follows is only what was *done*, and the
two findings the doing produced.

| # | item | ruling | state |
|---|---|---|---|
| Q1 | `D-S5-15` | **(a)** six missing grid points at seed `101` per fold, spliced | 🟡 jobs `1285777`/`1285778`/`1285779` submitted |
| Q2 | `FINDING 69` | **(1)** coherent reading `p ≥ 0.98`, declared erratum | 🟢 applied, selftest 17/17 |
| Q3 | `D-S6-4` residue | **(a)** wire `weight_dia_cal` into `G6.8` now | 🟢 applied, selftest byte-identical + 5 new checks |
| Q4 | `D-S6-5` residue | **(a)** write the `tus_00age` subset down now | 🟢 applied, and it forced two corrections |

### Q1 — the coverage curve gets measured instead of declared

`FINDING 71` said the `D-S5-14`(a) coverage diagnostic would arrive at **3 of 9** grid points and that
`fidelity_argmin_moved_under_D_S5_14` — the one quantity that would *measure* `FINDING 67` — would not
be evaluable on `es` or `it`. The ruling runs the complement of each replicate window at seed `101`
only, so each fold ends with a complete nine-point single-seed curve for two thirds of the cost of a
clean re-run, and the splice is legal because every row records its own `gen_seed`.

🔴 **It chooses nothing.** `--gen-seeds` forces replicate mode, in which the script refuses to
recompute the choice; `T_chosen` and `at_home_mae_pp` are untouched. Launcher:
`tools/4thJ_step5_temperature_coverage101.sh`. The splice will be **declared** in
`outputs_step5/temperature_calibration.md`, per the author's directive.

### Q2 — `G5.9` can now be seen failing at all

Under the registered text (`p ≤ 0.98`) the registered perturbation (`top_p = 0.9`) *satisfied* the
gate, so `G5.9` could never have been seen failing — a gate that cannot fail is not a gate. The ruled
reading `p ≥ 0.98` is written into the three places the register states the clause, each marked as a
post-registration erratum, and the checker prints the superseded reading beside the ruled one.
Selftest **17/17**: `0.9` FAIL, `0.99` PASS, `0.5` FAIL, boundary `0.98` PASS. ⚪ `TOP_P = 1.0` is
unchanged; our configuration was never at issue under either reading.

### Q3 — and 🔴 `FINDING 72`, which says the residue was not cosmetic

`G6.8` now defaults to `weight_dia_cal` and joins it from `harmonised.parquet` on
`(country, pid, diary_day)` — necessary because 🔴 **the Step 3 corpus carries no weight column at
all**. Weights re-weight every distribution and **no count**. Additivity is a `diff`: the selftest is
byte-identical before and after with the weight left off.

Then the three bases were **measured** rather than assumed close:

| fold | `weight_dia` → `weight_dia_cal` | vs the `G6.8` band |
|---|---|---|
| es | **27.14** min/day, TVD 0.0279 | 3.4× the 8.0 min band |
| uk | **0.03** min/day, TVD 0.0000 | nil |
| it | **43.87** min/day, TVD 0.0356 | 5.5× the band, 71 % of the TVD band |

🔴 The basis choice is **larger than the tolerance the gate scores against**, and it is
**country-correlated by construction** — the UK weights already hit the calendar week
(`FINDING 53`), so `weight_dia_cal` has nothing to do there while ES and IT move a great deal. Left
open, it would have moved two folds of a LOCO design and left the third alone, and the difference
would have been read as a transfer result. This is a second, independent argument for the ruling, and
it was not available when the ruling was made. ⚪ Reported, never thresholded.

### Q4 — and 🔴 `FINDING 73`, in two parts

**(i) `Y65-74` is not absent from Eurostat.** Counting `tus_00age` cells split by the `time`
dimension: `Y65-74` is populated in **504 of 504** cells in the **2000** wave and **0** in **2010**,
identically in ES, UK and IT; `Y15-20`, `Y20-74` and `Y_GE65` are the mirror image. The classification
changed between waves. The ruled subset is exactly the 2010 wave's own band set minus `TOTAL` and the
composite `Y20-74` — the right subset, but the reason has to be written as *"the band does not exist
in the wave we score against"*. `FINDING 55`'s second half is corrected in place at
`Step6_docs/4thJ_06_transfer.md`.

**(ii) Two of the five ruled bands are unscorable on our side.** Our finest age class is the
eight-band prefix scheme — all a generated diary can ever carry. `Y25-44`, `Y45-64` and `Y_GE65` map
exactly; `Y15-20` and `Y20-24` do not, because our band is a single `15-24`, and they cannot be merged
from the published side either (rates and times, no band population to weight them). **`tus_00age` is
scorable on three bands covering 84.7 % of the corpus**; `15-24` (10.8 %) and `11-14` (4.4 %) are
declared unscorable, the latter never in scope since the table starts at 15.

### What this section does NOT do

⚪ It does not close boxes 2, 4 or 9. Those still close on `1285712`–`1285714`. ⚪ It does not touch
`prereg.md`, whose md5 is unchanged. ⚪ `FINDING 72` and `FINDING 73` are **reported**, not gates:
neither introduces a threshold, and neither is quoted as a result.

---

## 14. 🟡 2026-08-21 (night) — BOXES 2 AND 4 ARE ALL BUT CLOSED. TWO GATES SCORE FOR THE FIRST TIME, ONE OF THEM FAILS, AND TWO NEW FINDINGS CAME OUT OF THE ARTEFACTS

`1285713` (`uk`) and `1285714` (`it`) COMPLETED; `1285712` (`es`) is on its last realisation. Both
landed replicate artefacts and all 30 generation files are in `Step5_docs/outputs_step5/`.

| box | was | now |
|---|---|---|
| **2** | 🟡 ruled (a), submitted | 🟡 **2 of 3 folds landed and pulled; `temperature_calibration.md` WRITTEN (331 lines), `generation_config_{es,uk,it}.json` WRITTEN.** Closes when `1285712` lands. |
| **4** | 🟡 written, BLOCKED | 🟡 **`G5.9` scores on all three folds and its perturbation fells all three; `G5.8` PASSES `it`, FAILS `uk`, BLOCKED on `es`.** Closes when `es` lands **and** `D-S5-16` is ruled. |
| **9** | ⚪ open | ⚪ **open** — unchanged; it closes on 2 and 4. |

**Battery: 30 PASS / 0 FAIL / 6 BLOCKED → 34 PASS / 1 FAIL / 1 BLOCKED**, coverage clause clean,
populations md5-unchanged.

### 🟢 `FINDING 69`'s ruling is now demonstrated on the real artefact, not argued on paper

`G5.9` scores on all three folds for the first time. `top_p = 1.0` → *"top-p is NOT USED, the
antecedent is false, VACUOUSLY SATISFIED"*; the registered perturbation `top_p = 0.9` → **FAIL on all
three folds**. Under the superseded as-written reading `p ≤ 0.98` this was impossible **in both
directions**: baseline would have FAILED and the perturbation would have PASSED. The erratum earned
its place.

### 🔴 `FINDING 74` — the sensitivity trap fired, and the split runs along the criterion

The `D-S5-13`(a) trap fires **only on `uk`**, and only on the statistics that carry **no part of the
decision**. `T_chosen` rests on **entropy matching**, and `dH` clears the trap on both landed folds.

🟢 **Stronger than the spread block, which only compares magnitudes:** re-applying each selection rule
**inside each of the five realisations** gives `argmin|dH|` = **1.10 on 5/5 `uk` seeds** and **1.20 on
5/5 `it` seeds**. `T_chosen` is a **seed-independent decision**.

🔴 **`T_fidelity` on `uk` is a coin flip** — 1.00 on seeds 101/103/105, 1.10 on 102/104. **It ships as
the band `{1.00, 1.10}`.** 🔴 **`uk`'s `agree = True` holds by `0.0001`** (`|1.10 − 1.00| = 0.1` vs
`agree_tol = 0.1001`) — write *"agree to within one grid step"*, never *"the curves agree"*. 🔴 **`es`
carries `endpoint_entropy = True`**: `T_chosen = 1.30` is the top of the pre-registered grid and the
grid is **not** extended.

### 🔴 `G5.8` FAILS on `uk`, and `D-S5-16` is open on whether that is the terminal verdict

*"The re-run spread (1.4072) is not smaller than the step-to-step difference (1.3994) — the sweep is
uninformative and the deliverable is the BAND."* First substantive real-artefact FAIL in Step 5.
**Left failing.** The registered clause says the step must exceed the spread *"else the deliverable is
the **BAND**, not a value"* — which reads as a **remedy**; the checker implements only the failure
half. Both readings are defensible and give different verdicts on `uk`. 🔴 **Not resolved here:** the
ambiguity surfaced by seeing the gate fail, so amending the checker in the direction that clears the
board would be selecting the test on the outcome. **(a) recommended** — leave it, `uk` FAILS in the
paper, Step 5 closes with one declared FAIL. **(b)** additive erratum branch. **(c) rejected** —
re-running for better statistics is re-selecting on the same criterion.

### 🔴 `FINDING 75` — the 1440-minute error is TWO-SIDED, and this document's own §1 said otherwise

§1 above is built on undershoot: *a diary whose episodes total **less than** 1440 stops filling at
`slot < 144`*. Recounting all 30 persisted generation files says the **majority overshoot**: at
`T_chosen`, `uk` **65.5 % over** vs 24.4 % under; `it` 49.5 % over vs 44.4 % under.

Verified in the code rather than assumed — `at_home_profile()` clamps with `min(slot + n, 144)` and
records `covered = min(slot, 144)`:

- **UNDER** → the phantom tail. 🟢 `FINDING 67`, and `I-1`/`D-S5-14`(a)'s covered basis removes exactly
  it.
- **OVER** → the excess minutes are **silently discarded and the diary reports FULL coverage**. 🔴 No
  phantom tail, and **the covered basis cannot see it**.

⚪ **`I-1` is correct and is not weakened** — but its *scope* was overstated: it addresses the
**minority** of `uk` diaries, and a second distortion exists that **no Step 5 diagnostic measures**.
`FINDING 67` itself survives: its confound rests on the undershoot rate moving along the swept axis,
and it does. The offending sentence is **corrected in place** in the impl doc.

🔴 **`sum_1440_frac ≈ 0.06` is not "the day is barely filled".** Median total is **1,460** (`uk`) /
**1,440** (`it`), median absolute deviation **30** / **50** min, aggregate day-fill **101.6 %** /
**100.4 %**. The error is small and roughly centred; the model just never lands *exactly*.

⚪ **Cross-checked:** the recount reproduces the artefacts' own `coverage_last_slot_frac` row by row
across all 30 realisations — worst disagreement **0.0253**, always positive, growing with `T`, exactly
as the stricter `parse_episodes` denominator predicts.

🟢 **Step 7 does NOT inherit a design gap — the grammar is ALREADY TWO-SIDED BY CONSTRUCTION. Corrected here after checking the code rather than asserting from the finding.** `tally_automaton()` (`tools/4thJ_step7_grammar.py:169`) has 145 states and a **single** accepting state `{144}`, and `tally_step` returns `None` whenever `state + dur/10 > 144`. Run directly: `tally_step(143, 10) → 144` (accept), `tally_step(144, 10) → None`, `tally_step(140, 60) → None`, and from state 140 the only legal durations are **10–40 min**. **Overshoot has no transition; undershoot never reaches the accepting state.** Nothing needs adding to item 7.1.

🔴 **What `FINDING 75` actually supplies is the MAGNITUDE of the work that mask does.** Unmasked, **90–94 %** of generated diaries miss the budget, and **the majority miss it by OVERSHOOTING** — so the constraint the mask most often has to enforce is the **upper** one. A "pad the short tail" mental model of the grammar would have predicted the opposite, and §1 of the improvements document was written on exactly that model. ⚪ `G7.10` (the XGrammar back-end that would apply this during decoding) has **still never been run**, so the grammar remains a specification plus a hand-written oracle, not something demonstrated inside the generation loop.

🔴 **Episodes/diary at `T_chosen` vs the real reference measured in the same run**: `es` **0.68×**,
`it` **0.76×**, `uk` **0.95×** — **country-correlated in the LOCO-dangerous shape**, the same shape as
`FINDING 53` and `FINDING 72`. Reading: fewer, longer episodes filling the same day. A **Step 6
input**, since `G6.8` scores transitions per day and dwell-time distributions.

### What this section does NOT do

⚪ It does not close boxes 2, 4 or 9 — `1285712` and `D-S5-16` are what remain. ⚪ It does not
re-choose any temperature. ⚪ It does not touch `prereg.md`, md5 unchanged. ⚪ `FINDING 74` and
`FINDING 75` introduce **no threshold** and are quoted as **no result**.

---

## 2026-08-21 (night) — 🟢 `1285712` (`es`) COMPLETED. ALL THREE FOLDS ARE IN, NO GATE IS BLOCKED ANY MORE, AND `G5.8` FAILS ON **TWO** FOLDS

`temperature_calibration_es_replicates.json` md5 `6d14b493b03fd37b8af917338f7d6776`; the 15
`generations_es/` files are local. (⚪ The directory also shows `gen_es_T0.50_s101.jsonl` — that is
`1285777`, the coverage-101 job, writing in live. It is outside the replicate grid and no statistic
here reads it.)

### `es` clears the trap on the choice basis and fails it everywhere else

| statistic | step | re-run spread | verdict |
|---|---|---|---|
| `H_gen` / `dH` | 0.0584 | 0.0318 | 🟢 **step > noise** |
| `at_home_mae_pp` | 0.9315 | **1.8127** | 🔴 **NOISE DOMINATES — noise is 1.95× the step** |
| `at_home_mae_pp_covered` | 0.6631 | **1.7613** | 🔴 **NOISE DOMINATES — 2.66×** |
| `act_tvd_pp` | 0.2890 | **1.8034** | 🔴 **NOISE DOMINATES — 6.24×** |
| `sum_1440_frac` | 0.0057 | **0.0283** | 🔴 **NOISE DOMINATES** |
| `terminated_frac` | 0.0003 | **0.0017** | 🔴 **NOISE DOMINATES** |

🟢 **The pattern established on `uk` and `it` holds on `es`, and it is now three for three: the only
statistic that clears the trap on every fold is the one the choice was actually made on.** `dH`
passes everywhere; every statistic carrying no part of the decision is noise-dominated somewhere.

🟢 **`argmin |dH|` = 1.30 on 5/5 `es` seeds.** `T_chosen` is a seed-independent decision on **all
three folds**.

⚪ **One asymmetry that must be stated rather than glossed.** `uk` (1.10 in 1.00–1.20) and `it` (1.20
in 1.10–1.30) choose an **interior** point of their replicate window, so their argmin had two
directions it could have moved in and moved in neither. `es` chooses **1.30, the top of its window
and of the whole grid**, so its argmin could only have moved *inward*. Stability on `es` is a
**one-sided** test and is weaker evidence than on the other two folds. It compounds
`endpoint_entropy = True` and both belong in the same sentence of the write-up.

🔴 **`es`'s fidelity argmin MOVES too:** `at_home_mae_pp` picks 1.10 on three seeds and 1.20 on two;
the covered basis picks 1.20 on four and 1.10 on one. **The `es` fidelity result is the band
`{1.10, 1.20}`.** Two folds of three now have an unstable fidelity argmin.

### The final Step 5 board

**36 gate-fold verdicts: 34 PASS, 2 FAIL, 0 BLOCKED.** Coverage clause clean — *"every passing gate
was made to fall"*. Shipped populations md5-verified unchanged before and after.

| gate | `es` | `uk` | `it` |
|---|---|---|---|
| `G5.8` | 🔴 **FAIL** (step 0.9315 vs spread 1.8127, **0.51×**) | 🔴 **FAIL** (1.3994 vs 1.4072, **0.99×**) | 🟢 PASS (4.1114 vs 3.1993, 1.29×) |
| `G5.9` | 🟢 PASS, perturbation fells it | 🟢 PASS, perturbation fells it | 🟢 PASS, perturbation fells it |

⚪ **No gate is BLOCKED any more.** Every Step 5 gate now scores on a real artefact — which is what
box 4 was for. ⚪ `G5.6` still FAILs 12 of 36 marginal rows, informational, superseded by
`D-S5-12`(a), not counted in the board.

### 🔴 `D-S5-16` now decides TWO folds, and the two are not alike

The decision written up above was framed on `uk` alone. With `es` in, it governs **two folds of
three**, and the two fail very differently:

- **`es` is decisively noise-dominated** — the re-run spread is nearly **twice** the step. No amount
  of re-reading makes this curve informative; it simply is not.
- **`uk` is marginal** — spread `1.4072` against step `1.3994`, a ratio of `0.994`. It fails by
  **0.6 %**. 🔴 **This is precisely the situation in which the temptation to re-run is strongest and
  must be refused**: option (c) would move `uk` across a line it sits within a rounding error of, and
  that is re-selecting on the same criterion with better statistics — which the val doc forbids by
  name. The recommendation is unchanged: **(a)**.

⚪ The `es` failure also makes option (b) less attractive than it looked on `uk` alone: an amendment
that accepts a delivered band would clear a fold whose curve carries **no usable signal at all**, not
merely one that missed by a rounding error. That is an argument the author did not have when the
options were drafted.

⚪ `T_chosen` is untouched on all three folds under every option. `prereg.md` untouched, md5
`e4243e07cdd80c9c846b91f40e3e8c45`.

---

## §15 — 🟢 2026-08-21 (night): the `D-S5-15`(a) coverage jobs landed. Step 5 is deliverable-complete. `FINDING 76`

`1285777` / `1285778` / `1285779` all COMPLETED, exit `0:0` (03:34 / 03:02 / 03:48 elapsed). The
nine-point covered-basis curve now exists on **all three folds**, assembled from the seed-`101` rows
of the replicate artefact plus the six coverage points. 63 generation files local.

🟢 **The gate board did not move — 36 verdicts, 34 PASS, 2 FAIL, 0 BLOCKED**, coverage clause still
*"every passing gate was made to fall"*, populations md5-verified unchanged. Correct: the coverage
jobs run in replicate mode and choose nothing. `temperature_calibration.md` regenerated from the
artefacts, **352 → 530 lines**, md5 `cf8f441e37e124fb68fbad47c7c49b5f`.

🔴 **`fidelity_argmin_moved_under_D_S5_14` fires on `uk` and nowhere else** (0.90 → 1.00). ⚪ Read the
magnitude before the flag: the two competing `uk` minima are **0.0437 pp** apart against a re-run
spread of **1.4072 pp**, a factor of **32**. The argmin moved because the curve is flat there.

🔴 **The coverage jobs bought an independent noise estimate nobody designed them to buy.** Their six
points are a *second realisation* of six grid points the primary sweep measured at seed `42`, at six
temperatures the replicate window never reaches. Point-by-point disagreement: `es` mean **0.5840 pp**
/ max **1.7176 pp**, `uk` 0.6100 / 1.2025, `it` 0.8407 / 1.2418. **On `es` the `G5.8` step the gate
is asked to call meaningful is 0.9315 pp — smaller than two runs of the same configuration disagree
at other temperatures.** This corroborates both `G5.8` failures **from outside the window that
produced them**, and it is evidence `D-S5-16` did not have when it was drafted. Recommendation
unchanged: **(a)**.

🔴 **The fidelity argmin moves under a seed change on all three folds over the full grid** — `es`
0.70 → 0.60, `uk` 1.00 → 0.90, `it` 0.80 → 0.90. One step each, two down and one up. **The fidelity
temperature is a BAND on every fold:** `es` {0.60, 0.70}, `uk` {0.90, 1.00}, `it` {0.80, 0.90}.
⚪ The confound is stated not glossed: no cell shares both `T` and `gen_seed`, so a seed change and an
engine change cannot be separated by exact reproduction; the reference side is byte-identical and the
per-fold mean *signed* differences have inconsistent signs (−0.36 / −0.59 / **+0.71**), which is what
noise looks like. Evidence, not proof.

🟢 **`T_chosen` survives the strongest test yet run.** `argmin |dH|` over **all nine** grid points at
a seed that played no part in the selection: `es` **1.30**, `uk` **1.10**, `it` **1.20** — identical
to `T_chosen` three folds for three. ⚪ `es` still chooses the **top of the grid**, so its stability
is a one-sided test; that sentence and `endpoint_entropy = True` travel together.

### 🔴 `FINDING 76` — `uk`'s `agree = True` does not survive a seed change

`agree` is `True` on exactly one fold of three, by a margin of `0.0001` (`0.1000` vs
`agree_tol = 0.1001`). At seed `101` the `uk` fidelity argmin moves one further grid step away, the
gap becomes `0.2000`, and **`agree` reads `False`**. The single `True` on the whole board does not
replicate. 🟢 `T_chosen` is unaffected — entropy wins on disagreement by pre-registration
(`4thJ_step5_temperature.py:607`), so `uk` selects `1.10` either way. 🔴 **The claim must change, not
the number:** *"on the UK fold the entropy and fidelity criteria agree"* is a property of one
realisation and must never be written as corroboration that the two criteria converge.

⚪ **Third independent measurement pointing the same way** — `FINDING 74` (the sensitivity trap), the
full-grid argmin walk, and `FINDING 76`: **the fidelity curve carries no seed-stable signal on `es`
or `uk`.** Exactly what `G5.8` reports and what `D-S5-16`(a) proposes to let stand.

⚪ **§14 above is superseded on one point.** It records the `uk` fidelity band as `{1.00, 1.10}` and
`agree = True` without qualification. Both were computed **inside the three-point replicate window**;
the nine-point values above replace them. The *conclusions* of §14 are unchanged.

⚪ `prereg.md` untouched, md5 `e4243e07cdd80c9c846b91f40e3e8c45`. 🔴 **Box 9 stays open: it cannot be
ticked until Step 5 closes, and Step 5 closes on `D-S5-16` alone.**


---

## §16 — 2026-08-22: 🟢 **BOXES 2, 4 AND 9 CLOSED. THIS DOCUMENT IS CLOSED. STEP PROGRESS RESUMES.**

| box | closes because |
|---|---|
| **2** | `D-S5-13` was ruled (a) and executed; all three replicate jobs landed `0:0`, the artefacts and 63 generation files are local, `generation_config_{es,uk,it}.json` are written with every field copied from the calibration artefact, and `outputs_step5/temperature_calibration.md` is **generated** from those artefacts — now by `tools/4thJ_step5_mk_calibration_doc.py`, 540 lines, md5 `b76d34558db5bd93c86cb47709ddd5a0`. |
| **4** | `G5.8` and `G5.9` have real checkers, both score on real artefacts on all three folds, and **no gate is BLOCKED**. Board **36 verdicts: 34 PASS, 2 FAIL, 0 BLOCKED**, coverage clause clean. `D-S5-16` — the last thing box 4 waited on — is **RULED (a)**: `G5.8` stands as written and its FAIL on `es` and `uk` is the terminal verdict. |
| **9** | 2 and 4 are closed, so this document is. |

🔴 **The one thing that must travel out of this document unchanged:** Step 5 closes at
**DoD 4 of 5, with item 5 by declared exception**, because item 5 requires *all* gates to pass and
`G5.8` does not pass on `es` or `uk`. **Never 5 of 5. Never 36 of 36.** Every gate on the board,
including both failures, was seen failing; the coverage clause is clean; the two FAILs go into the
paper as the result.

⚪ `prereg.md` untouched, md5 `e4243e07cdd80c9c846b91f40e3e8c45`. Nothing is running on Speed.
🟢 **Step 6/7/8/9 progress resumes**, carrying the `FINDING 75` episode-deficit numbers
(`es` 19.17 vs 28.38 = 0.68x, `it` 21.86 vs 28.62 = 0.76x, `uk` 23.99 vs 25.18 = 0.95x) into `G6.8`.
