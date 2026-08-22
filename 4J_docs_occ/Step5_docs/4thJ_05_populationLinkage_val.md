# Step 5 — Conditioning and population linkage. Validation.

### 4J HETUS LLM pipeline. Validation specification.
#### Implementation: `4thJ_05_populationLinkage.md`. Parent: `../4thJ_00_HETUS_LLM_Pipeline.md`

---

## STATUS

**OPEN.** 🟢 **2026-08-21: item 5.1 is COMPLETE — all three folds have published marginals** (`marginals_{uk,es,it}.csv` + `econ_11plus_{uk,es,it}.csv`), so `G6.1`'s raked-donor null is computable on every fold. 🟢 **2026-08-21 (afternoon): `strat_hh_type` is additionally on a PERSON basis in all three folds** (`hhtype_person_{es,uk,it}.csv`, convention A), which is what the rake must consume — `D-S5-6`, `D-S5-7`, `D-S5-8` closed; 🔴 `FINDING 60` / `D-S5-9` open, Italy's household-basis rows still on convention B. 🟢 **2026-08-21 (evening): THE BATTERY HAS RUN. `tools/4thJ_gates_step5.py`, all three folds, 27 gate-fold verdicts: 25 PASS, 2 FAIL, and the coverage clause is CLEAN --- every gate that passed at baseline was made to fall.** 🟢 **2026-08-21 (night): `D-S5-12` RULED (a) AND APPLIED --- `G5.6` is SPLIT into `G5.6i` (contamination: zero marginals from the held-out country's diaries) and `G5.6ii` (published source: URL + table id), both PASS on all three folds, each SEEN FAILING separately. The battery is now 30 gate-fold verdicts, 30 PASS, coverage clause still CLEAN. The old single gate is still run as `G5.6-as-written`, INFORMATIONAL, and still FAILS `es` 30/36 and `it` 12/36.** 🔴 **`G5.8` and `G5.9` are BLOCKED, not passing** --- item 5.4 has produced no temperature sweep and Step 7 no generation config. Item 5.4 is still unbuilt. All thresholds pre-registered.

---

## WHAT THIS STEP MUST PROVE

That the synthetic people are **right on the demographics** and **clean of the held-out country's
microdata**.

The second is the one that can silently destroy Step 6. If any quantity derived from the held-out
country's diaries reaches its marginals, the transfer experiment is contaminated in a way that
inflates the result and leaves no trace in it.

---

## GATES

| ID | What it detects | Threshold | Provenance |
|---|---|---|---|
| **G5.1** Marginal fit | IPF that did not converge | Every target margin reproduced to within **±0.5 pp**, all cells | **project-chosen** |
| **G5.2** Joint plausibility | IPF matching margins while inventing impossible people | Zero synthetic persons in structurally impossible cells (e.g. age 12 with economic status "retired"), against an explicit impossibility table | **project-chosen** |
| **G5.3** Population size | A silently truncated synthesis | Synthetic population total within **±0.1 %** of the target | **project-chosen** |
| **G5.4** Prefix field completeness | A prefix the model has never seen | 🔴 **100 % of synthetic persons map to a prefix whose every value in the FIVE non-`country` fields — `strat_age_band`, `strat_sex`, `strat_hh_type`, `strat_econ_status`, `strat_day_type` — appears in the training corpus.** The threshold is untouched at 100 %; the FIELD SET is narrowed, and this row is where the narrowing is named. `country` is excluded because an unseen `country` token IS the LOCO design (`G4.13` asserts zero held-out records reached the shard, so the token is absent by construction and on purpose), whereas an unseen `strat_hh_type` is a defect. One gate could not tell those apart, and the one that could not was reading 0 % on every fold | **project-chosen**<br>🟢 **RULED 2026-08-20, decision item 3 (a), from `FINDING 40`. 🔴 The field list is `tools/encoder.py:86` `PREFIX_FIELDS` minus `country` — it is NOT `diary_day`, which is not a prefix field at all and which `FINDING 53` showed means three different things in the three countries. The unseen-`country` behaviour is measured instead by `D5.1` below.** |
| **G5.5** Prefix encoder identity | A second copy of the field order drifting from the first | The prefix string built here is **byte-identical** to what `../tools/encoder.py` 🔴 *(2026-08-20: corrected from `../Step3_docs/outputs_step3/encoder.py`, which does not exist)* produces for the same person. Tested by importing that encoder, never by reimplementing it | **project-chosen** |
| **G5.6i** 🔴 Held-out marginal provenance --- CONTAMINATION | **Contamination** | 🟢 **Count of marginals for the held-out country derived from that country's TIME-USE DIARIES: 0.** This is the condition the paper's headline claim rests on. Detected by scanning every marginal row's full provenance record for diary markers (`hetus`, `diary`, `time-use`, `tus_`, the Step 3 corpus, `harmonised.parquet`) --- deliberately WIDE, so a published Eurostat *time-use* aggregate would also trip it and have to be ruled on explicitly | **derived from the experimental design**<br>🟢 **RULED 2026-08-21, `D-S5-12` (a).** Condition (i) of the split |
| **G5.6ii** 🔴 Held-out marginal provenance --- PUBLISHED SOURCE | A number nobody can check | 🟢 **Count of marginals with no published source: 0.** Every marginal row carries a non-empty URL **and** a non-empty table id | **derived from the experimental design**<br>🟢 **RULED 2026-08-21, `D-S5-12` (a).** Condition (ii) of the split |
| ~~**G5.6** Held-out marginal provenance~~ 🔴 **SUPERSEDED** | --- | ~~Count of marginals with no published source, **or derived from microdata**: 0~~. 🔴 **Superseded by `D-S5-12` (a) on 2026-08-21, after FAILING `es` 30/36 and `it` 12/36 --- 42 rows, ZERO of which failed for "no published source".** Three later rulings (`D-S5-4` (b), `D-S5-5`, `D-S5-9`) put **public-use census microdata** into the marginals on purpose, and this text could not tell that apart from a time-use diary. **It is still RUN and still printed, as `G5.6-as-written`, INFORMATIONAL and never scored** --- a superseded gate is retired in the open. Its FAIL is the evidence for the split | --- |
| **G5.7** Co-presence honesty | Conditioning on a flag a country never recorded | No prefix asserts a flag that `copresence_availability.md` marks "not recorded" for that country | **derived from Step 2** |
| **G5.8** Temperature calibration reported | A knob chosen without evidence | Both the entropy-matching curve and the fidelity curve are reported, and **whether they agree is stated explicitly** | **project-chosen** |
| **G5.9** No truncation creep | Tail deletion at generation | If top-p is used at all, **p ≥ 0.98** (🔴 post-registration erratum, `FINDING 69`, ruled 2026-08-21; registered as ≤, which is the wrong direction — smaller p truncates more), asserted in the generation config that Step 7 actually reads, not in a comment | `RL09` |
| **G5.11** 🔴 Prefix field set is not restated | `G5.4` drifting from the encoder | The five fields `G5.4` scores are read from `tools/encoder.py`'s `PREFIX_FIELDS` with `country` removed, **never written out as a literal list in the checker**. A checker carrying its own copy of the field set would keep passing after the prefix changed | **derived from item 3's ruling — the narrowing is only safe if it cannot go stale** |
| **G5.10** No output raking | Using the trick we are benchmarked against | No raking, calibration or post-hoc reweighting is applied to any generated diary anywhere in the codebase. Asserted by an explicit search over the generation path | `RL09` |

---

## 🔴 THE SENSITIVITY TRAP IN G5.8

The temperature sweep is a sweep of one knob. **If it is run once per temperature level with the
noise source held fixed, the resulting curve is a single realisation presented as a function: it has
no error bar, therefore no way to be wrong, therefore no way to fail — and the sweep always produces
a winner.**

**Requirement: every temperature level is run at least 5 times with different seeds, and the
step-to-step difference along the curve must exceed the spread from re-running one level.** If it
does not, the sweep has told us nothing about temperature and the reported deliverable is the
**band**, not a chosen value.

🔴 **And if the sweep turns out to be uninformative, the correct response is not to re-tune.**
Re-selecting on the same criterion with better statistics is still selecting on that criterion.

---

## EVERY GATE MUST BE SEEN FAILING

Each perturbation must break **exactly one** gate.

| Perturbation | Must fail | Must stay clean |
|---|---|---|
| Stop IPF after 2 iterations | G5.1 | G5.3 |
| Remove one impossibility constraint | G5.2 | G5.1 |
| Drop 5 % of synthetic rows | G5.3 | G5.1 (verify: margins may survive proportional loss — that is the point of separating them) |
| Introduce a household type absent from training | G5.4 | G5.1 |
| 🔴 **Generate the held-out fold's prefixes with the held-out `country` token (i.e. change nothing — run the design as specified)** | **nothing** | **`G5.4`** — *this is the whole point of item 3's ruling: before it, the experiment as designed felled its own gate on every fold. If `G5.4` fails here, the narrowing was not applied* |
| 🔴 **Restate the five field names as a literal list inside the `G5.4` checker, then add a seventh field to `PREFIX_FIELDS`** | **`G5.11`** | `G5.4` — *which is exactly the danger: `G5.4` goes on passing while it no longer scores the prefix that exists* |
| Reorder two prefix fields in a local copy | **G5.5** | G5.4 |
| 🔴 **Substitute one held-out marginal recounted from that country's own TIME-USE DIARIES** | **`G5.6i`** | `G5.1`, `G5.6ii` — *the fit is fine and the row is even published; only the contamination condition can see it* |
| 🔴 **Add a held-out marginal with no URL and no table id** | **`G5.6ii`** | `G5.1`, `G5.6i` — *the two conditions must be felled independently or the split is cosmetic* |
| 🔴 **Substitute one held-out marginal with a value computed from that country's CENSUS microdata** | **nothing** | **everything** — 🟢 *this is `D-S5-12` (a)'s own test. `D-S5-4` (b), `D-S5-5` and `D-S5-9` deliberately admit published-census microdata, so a split that still fells a gate here has not split anything. It DOES still fell `G5.6-as-written`, which is why that gate is kept and printed* |
| Assert an unrecorded co-presence flag | G5.7 | G5.4 |
| Report only the fidelity curve | G5.8 | all others |
| Set `top_p = 0.9` in the generation config | G5.9 | all others |
| Add a rake call to the generation path | G5.10 | all others |
| 🔴 **Null perturbation: change nothing** | **nothing** | everything |

### 🔴 `D5.1` — the unseen-`country` diagnostic (decision item 4 (a), 2026-08-20)

**Reported, never a gate.** Item 3 removes `country` from `G5.4` on the ground that an
unseen country token is the design rather than a defect. That is right, and it leaves a
hole: the model **will** do something with a token it never saw, and before this ruling
nothing in Steps 4-7 measured **what**. `D5.1` fills the hole without inventing a
threshold nobody can justify in advance.

Measured at Step 7 generation time, on the fold's own checkpoint, over the same prefixes
the fold actually generates:

1. **Next-token entropy at the first body position**, conditioned on the held-out
   `country` token, against the same quantity conditioned on each of the two SEEN country
   tokens with the rest of the prefix held identical. Three numbers per prefix.
2. **Output divergence**: the total-variation distance between the first-episode `ACT`
   distribution under the held-out token and under each seen token, same prefixes.
3. **The degenerate case, stated explicitly**: whether the held-out token's readings are
   distinguishable from the seen tokens' at all. 🔴 If they are not, the country token is
   not steering generation and the LOCO claim rests on the other five fields — that is a
   result about the design, and it is reported as one either way.

🔴 **No pass/fail band is pre-registered for `D5.1`, deliberately.** There is no published
number for what an out-of-distribution conditioning token should do to entropy, and a band
invented here would be a threshold chosen after seeing the design. It is a characterisation,
it is reported in full, and the coverage clause below does not apply to it.

---

### Coverage clause

Cross-tab every perturbation against baseline; **FAIL the probe if any passing gate was never made to
fall.**

---

## VACUITY GUARDS

* **V5.a** — G5.2's impossibility table must be **non-empty** and must exclude a non-zero number of
  cells on the real data. A constraint set that never binds is a constraint set that is not wired in.
* **V5.b** — G5.6 FAILs rather than skipping if it found **zero** marginals to check. A provenance
  gate over an empty set passes for the wrong reason.
* **V5.c** — G5.10 is a search over source; it must print **what it scanned** and FAIL if it scanned
  fewer files than the generation path contains. 🔴 A grep that cannot distinguish *found nothing*
  from *could not run* is not a check — read the exit code, and print the file list.
* **V5.d** — G5.5 imports the Step 3 encoder. It must **not** be refactored to compare against a copy
  held in this step, which would reduce it to comparing a thing to itself.

---

## WHAT THIS STEP'S VALIDATION DOES **NOT** COVER

* It does **not** validate that IPF is the right population-synthesis method. That is a choice made
  on the literature, and it is deliberately a conventional one.
* It does **not** validate the diaries. No diary exists yet; Step 7 generates them.
* It does **not** test whether the model respects the prefix. That is Step 4's G4.3, G4.4 and G4.12,
  and a population that is perfect on all ten gates here is worthless if the model ignores it.
* 🔴 **G5.6 checks provenance, not leakage.** A marginal can be published *and* have been computed by
  the statistical office from the same microdata we hold out. That is not contamination in the sense
  that matters — the model still never sees a held-out diary — but the distinction should be stated
  in the methods rather than assumed away, because a reviewer will ask.

---

## PROGRESS LOG

Append-only.

### 2026-08-14 — validation document created

* Ten gates, eleven perturbations, none run.
* 🔴 G5.6 is the gate that protects the paper's headline claim, and it is the only gate in this step
  whose failure would not show up anywhere else. A contaminated marginal makes Step 6 look *better*,
  which is the direction no other check is watching.


### 2026-08-21 (evening) --- 🟢 **THE BATTERY EXISTS AND HAS RUN: 25 OF 27 PASS, COVERAGE CLAUSE CLEAN.** 🔴 **`G5.6` FAILS ON TWO FOLDS BY DESIGN, AND `G5.8`/`G5.9` ARE BLOCKED.**

Runner: `tools/4thJ_gates_step5.py`. Full narrative in the implementation doc's entry of the same date.

**Baseline, per fold.**

| gate | `es` | `uk` | `it` |
|---|---|---|---|
| `G5.1` marginal fit | PASS 0.0120 pp | PASS 0.0112 pp | PASS 0.0099 pp |
| `G5.2` joint plausibility | PASS, 12 cells, 0 persons | PASS, 13 cells, 0 | PASS, 5 cells, 0 |
| `G5.3` population size | PASS 100,000/100,000 | PASS | PASS |
| `G5.4` prefix completeness | PASS 0 of 100,000 unseen | PASS | PASS |
| `G5.5` encoder identity | PASS 100,000 compared | PASS | PASS |
| `G5.6` marginal provenance | 🔴 **FAIL 30 of 36** | PASS 0 of 36 | 🔴 **FAIL 12 of 36** |
| `G5.7` co-presence honesty | PASS | PASS | PASS |
| `G5.10` no output raking | PASS, 6 files scanned | PASS | PASS |
| `G5.11` field set not restated | PASS | PASS | PASS |
| `G5.8`, `G5.9` | 🔴 BLOCKED | BLOCKED | BLOCKED |

**Perturbations.** Eleven per fold, each felling exactly the gate this document names, with two
recorded departures and one gap:

* **the 5 % drop is now every 20th row, not the first 5 %.** A head slice fells `G5.1` too, because the
  population file is ordered by stratum. This document's own "must stay clean" column predicted the
  distinction and it is now demonstrated in both directions.
* **`it` survives "stop IPF after 2 sweeps"** and the perturbation escalates to one sweep, printing
  that it escalated. Italy's marginals are near enough to independent that two sweeps already land
  inside 0.5 pp.
* the `G5.6` perturbation is reported **`n/a`** on `es` and `it`, where the gate is already failing at
  baseline. It fells `G5.6` on `uk`, which is the fold where the gate passes.

**Vacuity guards.** `V5.a` --- the impossibility table is non-empty on all three folds (12/13/5 cells)
and it BINDS: the mask zeroes 22.5 % (`es`), 21.8 % (`uk`) and 8.8 % (`it`) of the joint. `V5.b` ---
`G5.6` FAILs rather than skipping if it checked zero rows; it checked 36 on each fold. `V5.c` ---
`G5.10` prints its file list and FAILs if a file could not be read. `V5.d` --- `G5.5` and the battery
both take the field order from `tools/encoder.py`, never from a copy held here.

🔴 **`G5.6` is the gate this document called "the one whose failure would not show up anywhere
else", and it is now failing.** The measured split is what makes it decidable: **zero rows fail for
"no published source"** --- all 42 failing rows have a URL and a table id, and fail only the "derived
from microdata" clause, on public-use CENSUS files, not on time-use diaries. `D-S5-12` is open on
whether the gate's text should separate those two things. It is not being relaxed in the meantime.


### 2026-08-21 (night) --- 🟢 **`D-S5-12` RULED (a) AND APPLIED. `G5.6` IS TWO GATES. 30 OF 30 PASS, COVERAGE CLAUSE STILL CLEAN.**

Runner unchanged: `tools/4thJ_gates_step5.py` (md5 `0988f1abfb4b9534798271748d1db5fa`). Full
narrative in the implementation doc's entry of the same date.

**The split, and what each half now scores.**

| gate | `es` | `uk` | `it` |
|---|---|---|---|
| `G5.6i` diaries (contamination) | **PASS** 0 of 36 | **PASS** 0 of 36 | **PASS** 0 of 36 |
| `G5.6ii` published source | **PASS** 0 of 36 | **PASS** 0 of 36 | **PASS** 0 of 36 |
| `G5.6-as-written` 🔴 INFORMATIONAL, not scored | **FAIL 30 of 36** | PASS | **FAIL 12 of 36** |

**30 gate-fold verdicts, 0 FAIL, 2 BLOCKED per fold.** The two BLOCKED are unchanged: `G5.8` and
`G5.9` still have no temperature sweep and no generation config to read.

**Both halves were SEEN FAILING, separately, on every fold.**

* *substitute a held-out marginal recounted from the held-out diaries* → fells **`G5.6i`** only. The
  injected row is published, carries a URL and a table id, and fits the margins perfectly. Nothing
  else moves.
* *add a marginal with no URL and no table id* → fells **`G5.6ii`** only.
* 🟢 *substitute a held-out marginal computed from CENSUS microdata* → fells **nothing**, which is the
  ruling's own test and is why the perturbation was kept rather than deleted. It still fells
  `G5.6-as-written`, which is why that gate is still run.

🔴 **The old gate is not deleted.** It runs at every baseline and prints
`[INFORMATIONAL -- superseded by D-S5-12 (a), not counted]`. Its FAIL on `es` and `it` is the
evidence for the split; a project that deletes the failing version of a gate it just relaxed has
destroyed its own audit trail.

⚪ **`V5.b` now applies to both halves** --- each FAILs rather than skipping if it checked zero rows.
Each checked 36 on each fold.

⚪ **`G5.6i`'s marker list is deliberately wide.** `tus_` matches published Eurostat time-use tables,
which are aggregates rather than diaries. No Step 5 marginal matches any marker today, so the width
costs nothing now and makes the gate fail towards caution if one ever does.

### 2026-08-21 (evening, II) — 🟢 **`G5.8` AND `G5.9` HAVE REAL CHECKERS AND ARE NO LONGER A STATIC `BLOCKED` LIST.** 🔴 **`FINDING 69`: `G5.9`'s TEXT AND ITS OWN PERTURBATION CONTRADICT EACH OTHER.**

Battery is now **36 gate-fold verdicts: 30 PASS, 0 FAIL, 6 BLOCKED**, coverage clause still clean,
shipped populations md5-unchanged before and after.

**What changed in the battery.** `BLOCKED` was a hardcoded dictionary of two gate ids. It is now
**empty**, and `G5.8`/`G5.9` are ordinary entries in `GATES` with real checkers that return a third
verdict, `None` = BLOCKED, **only while the artefact they read is absent**. The moment the artefact
exists they score like every other gate, and BLOCKED can never again be a thing a human forgot to
revisit. Both registered perturbations are wired: *"report only the fidelity curve"* → `G5.8`,
*"set `top_p = 0.9`"* → `G5.9`.

**`G5.8` reads two conditions, not one.** The gate row is a reporting obligation — both curves and
an explicit agreement statement — and the val doc's own **sensitivity trap** section adds a second:
*"every temperature level is run at least 5 times with different seeds, and the step-to-step
difference along the curve must exceed the spread from re-running one level"*, else the deliverable
is **the band**. Scoring the first alone would let a single-realisation curve — the exact object
that section exists to reject — carry the gate, so both are scored. Today the reporting condition is
**satisfied on all three folds** (`es` T_ent 1.30 / T_fid 0.70 / agree false; `uk` 1.10 / 1.00 /
true; `it` 1.20 / 0.80 / false) and the sensitivity condition is **BLOCKED pending
`1285712`–`1285714`**, the `D-S5-13`(a) replicate jobs.

🔴 **`FINDING 69` — the `G5.9` contradiction, flagged rather than quietly resolved.** The gate reads
*"if top-p is used at all, **p ≤ 0.98**"*. The perturbation table says *"set `top_p = 0.9`"* must
fell it. **Both cannot hold: 0.9 satisfies p ≤ 0.98.** In nucleus sampling a smaller p truncates
more, so as written the gate **admits p = 0.5** — half the tail deleted — and **rejects p = 1.0**,
no truncation at all: the opposite of a gate named "no truncation creep" and the opposite of what
its own perturbation expects. The coherent reading is **p ≥ 0.98**, under which our `top_p = 1.0` is
**vacuously satisfied** (top-p is not used at all) **and** the registered perturbation fells the
gate. The checker **evaluates and prints both readings** and takes its verdict on the coherent one,
because it is the only one under which the register is self-consistent. ⚪ **Nothing about our
configuration changes either way** — we do not use top-p, and `TOP_P = 1.0` is a pre-registered
constant in `4thJ_step5_temperature.py`. One line closes this whichever way it is ruled.

🟢 **RULED (1) BY THE AUTHOR, 2026-08-21 — the coherent reading `p ≥ 0.98` is adopted, as a declared POST-REGISTRATION ERRATUM.** The erratum is written into the three places the register states the clause — `4thJ_05_populationLinkage.md` line 92 (the `RL09` row) and line 168 (the design text, with the full reasoning), and this document's gate table at line 39 — and into `tools/4thJ_gates_step5.py`, whose `g5_9` docstring now records the ruling and whose message prints the superseded reading beside the ruled one so the correction stays visible rather than being absorbed. The registered perturbation *set `top_p = 0.9`* now **fells** the gate, which is the whole point: under the as-written text `G5.9` could never have been seen failing. Re-run of `4thJ_step5_g58_g59_selftest.py`: **17 of 17 green**, with `0.9` FAIL, `0.99` PASS, `0.5` FAIL and the boundary `0.98` PASS all demonstrated. ⚪ Our configuration is unchanged and was never at issue.

**Still owed before Step 5 closes:** the three replicate jobs must land; then
`outputs_step5/temperature_calibration.md` and `generation_config_<fold>.json` get written, and
`G5.8`/`G5.9` score for the first time. **Step 5 DoD 3 of 5.**

### 2026-08-21 (night) — 🟢 **`D-S5-15` RULED (a) AND SUBMITTED: the `D-S5-14`(a) COVERAGE CURVE WILL BE NINE POINTS ON ALL THREE FOLDS, NOT THREE.**

`FINDING 71` established that the `D-S5-13`(a) replicate windows sit around `T_chosen` — the
**entropy** optimum — and therefore exclude `T_fidelity` on `es` (0.70 vs 1.10–1.30) and `it`
(0.80 vs 1.10–1.30), so the covered-basis curve would have arrived as a **3-of-9 stub** and
`fidelity_argmin_moved_under_D_S5_14` would not have been evaluable on two folds of three. 🔴 The
blind spot sat exactly where the confound is largest: on `es` the fidelity optimum is at `T = 0.70`,
where **14.8 %** of diaries never terminate.

The author ruled **(a)**, refined to run only the **six grid points each window does not cover**, at
seed `101` only, spliced with the replicate seed-`101` rows — a complete nine-point single-seed curve
for two thirds of the cost of a clean re-run. Jobs `1285777` (`es`), `1285778` (`uk`), `1285779`
(`it`); launcher `tools/4thJ_step5_temperature_coverage101.sh`. Prompt seed 42, `n_prompts` 600,
`top_p` 1.0, `top_k` 0, `max_new_tokens` 1200, pinned base revision and per-fold adapter — identical
to both earlier passes. 🔴 **Replicate mode, so it chooses nothing**: `T_chosen` stays 1.30 / 1.10 /
1.20 and `at_home_mae_pp` is not recomputed. ⚪ The splice is **declared** in
`outputs_step5/temperature_calibration.md`, per the author's directive, and
`fidelity_argmin_moved_under_D_S5_14` is derived offline there because the script emits it only in
the non-replicate branch.

⚪ **Blocks nothing.** Boxes 2 and 4 — and Step 5's closure — still turn on `1285712`–`1285714`;
this is additive and lands after them.

### 2026-08-21 (night) — 🔴 **`FINDING 74` + `D-S5-16`: THE REPLICATE JOBS LANDED, THE SENSITIVITY TRAP FIRED, AND `G5.8` FAILS ON `uk`**

`1285713` (`uk`) and `1285714` (`it`) COMPLETED; `1285712` (`es`) is on its last realisation.
Artefacts and all 30 generation files are in `outputs_step5/`
(`temperature_calibration_uk_replicates.json` md5 `62f17f9f580b495d6bf8e86bd8a0b38b`,
`…_it_replicates.json` md5 `eeb1fe2e9dc6fdd273d770e1fcf11e0b`). Full record and every number:
`Step5_docs/impl/2026-08-21_item5.4-temperature.md`.

🟢 **The choice survives, and it survives on the criterion it was actually made on.** `T_chosen`
rests on **entropy matching** (`entropy wins on disagreement`, pre-registered), and `dH` clears the
trap on both landed folds (`uk` step 0.0705 > noise 0.0581; `it` 0.0888 > 0.0594). Stronger still,
the test the spread block does *not* run — re-applying the selection rule **inside each of the five
realisations** — gives `argmin|dH|` = **1.10 on 5/5 `uk` seeds** and **1.20 on 5/5 `it` seeds`**.
`T_chosen` is a seed-independent decision, not a magnitude comparison.

🔴 **`T_fidelity` on `uk` is a coin flip and must ship as a BAND.** `argmin at_home_mae_pp` is
`1.00` on seeds 101/103/105 and `1.10` on 102/104. The `1.00` in
`temperature_calibration_uk.json` is one realisation of a quantity with no stable argmin. **Report
`{1.00, 1.10}`, never `1.00`.** ⚪ On `it` the in-window argmin is stable at 1.10, but the ruled
`T_fidelity` = 0.80 lies **outside** the window and stays untested until `1285779` lands.

> 🔴 **CORRECTED 2026-08-21 (night), after the coverage-101 jobs landed.** The band quoted in this paragraph is an argmin taken **inside the three-point replicate window** — the minimum of a *truncated* curve, and on `es` and `it` the ruled `T_fidelity` was not even in the window. It is **not** the fidelity temperature and must never be quoted as one. On the full nine-point grid the fidelity argmin moves one grid step under a seed change on **all three** folds: `es` **0.70 → 0.60**, `uk` **1.00 → 0.90**, `it` **0.80 → 0.90**, giving the bands `es` {0.60, 0.70}, `uk` {0.90, 1.00}, `it` {0.80, 0.90}. ⚪ The *conclusion* of this paragraph — that the fidelity argmin is not seed-stable — is unchanged and now holds on three folds rather than two. See the closing coverage-101 entry of this document.


🔴 **A margin nobody asked about.** `agree` is abs(`T_ent` − `T_fid`) ≤ `AGREE_TOL = 0.1001`. On
`uk` that is `0.1 ≤ 0.1001` — **`agree = True` by one part in ten thousand**. It is robust in
verdict (5/5 True, since the two moving values are 1.00 and 1.10 and both clear it), but the paper
must say **"the two curves agree to within one grid step"**, never *"the curves agree"*.

> 🔴 **CORRECTED 2026-08-21 (night) — `FINDING 76`. `agree` is NOT robust; this paragraph's “5/5 `True`” is an artefact of the same truncated window.** The 5/5 verdict was computed from the **in-window** fidelity argmin, which on `uk` can only be `1.00`, `1.10` or `1.20` — and the first two both clear `agree_tol` by construction. Over the **full nine-point grid** the seed-101 fidelity argmin is `0.90`, the gap to `T_chosen = 1.10` is `0.2000`, and **`agree` reads `False`.** The single `True` on the whole board does not replicate. 🟢 `T_chosen` is unaffected — entropy wins on disagreement by pre-registration (`4thJ_step5_temperature.py:607`), so `uk` selects `1.10` either way. 🔴 **The claim, not the number, is what must change:** never write that the two criteria agree on `uk` as evidence that they converge.


🔴 **`es` carries `endpoint_entropy = True`.** `T_chosen = 1.30` is the **top of the pre-registered
grid**; the entropy optimum may lie above it and the grid cannot see it. The grid is **not**
extended — extending it now would be choosing the search space on the result. Declared with every
`es` number.

**Battery: 30 PASS / 0 FAIL / 6 BLOCKED → 34 PASS / 1 FAIL / 1 BLOCKED**, coverage clause clean.
🟢 `G5.9` scores on all three folds for the first time and its registered perturbation **fells it on
all three** — impossible under the superseded reading, so `FINDING 69`'s ruling is now *demonstrated*
rather than argued. 🟢 `G5.8` PASSES on `it` and its perturbation fells it. 🔴 **`G5.8` FAILS on
`uk`** — *"the re-run spread (1.4072) is not smaller than the step-to-step difference (1.3994) — the
sweep is uninformative and the deliverable is the BAND"*. **First substantive real-artefact FAIL in
Step 5. It is left failing.** ⚪ `G5.8` on `es` stays BLOCKED; BLOCKED is not a PASS.

🔴 **`D-S5-16` — OPEN, FOR THE AUTHOR.** The registered clause says the step must exceed the spread,
*"else the deliverable is the **BAND**, not a value"* — which reads as a **remedy**, not only a
failure condition. The checker (`tools/4thJ_gates_step5.py:544`) implements the first half only and
never asks whether a band was in fact delivered. Both readings are defensible and they give
**different verdicts on `uk`**, the one fold where it bites. 🔴 **Not resolved here, deliberately:**
the ambiguity surfaced by seeing the gate fail, so amending the checker in the direction that turns
that FAIL into a PASS would be selecting the test on the outcome. **(a) recommended** — leave `G5.8`
as written, `uk` FAILS in the paper, and the `uk` fidelity result ships as the band with the FAIL as
its stated reason; **(b)** additive erratum branch that accepts a delivered band, marked exactly as
`FINDING 69` was; **(c) rejected** — re-running `uk` at more seeds is re-selecting on the same
criterion with better statistics, and the `uk` curve is genuinely flat there (3.142 vs 3.425 pp,
sd 0.56 / 0.47). ⚪ **`T_chosen` is untouched under all three**; `D-S5-16` scores a *reporting* gate,
not the generation temperature.

⚪ `generation_config_{es,uk,it}.json` written — every field **copied** from the calibration artefact,
none freshly chosen: `T` 1.30 / 1.10 / 1.20, `top_p` 1.0, `top_k` 0, `max_new_tokens` 1200, base
`allenai/OLMo-2-0425-1B` @ `a1847dff35000b4271fa70afc5db10fd29fedbdf`, per-fold adapter, prompt seed
42. ⚪ `prereg.md` untouched, md5 unchanged. **Step 5 DoD 4 of 5** — `temperature_calibration.md`
and `D-S5-16` are what remain.

### 2026-08-21 (night) — 🔴 **`FINDING 75`: THE 1440-MINUTE BUDGET ERROR IS TWO-SIDED, AND THIS PROJECT'S OWN RECORD SAID OTHERWISE**

The 30 persisted generation files (`generations_{uk,it}/`, 5 seeds × 3 temperatures × 600 diaries)
made it possible for the first time to ask which **direction** the budget error runs, rather than only
how often it is exact. Measured, not inferred. Full record and every number:
`Step5_docs/impl/2026-08-21_item5.4-temperature.md`.

🔴 **At `T_chosen`, `uk` overshoots in 65.5 % of diaries and undershoots in 24.4 %; `it` is 49.5 %
over and 44.4 % under.** The impl doc's *"the bias is one-sided and depresses the generated at-home
curve in the late slots only"* is **wrong** and is **corrected in place** at line 303. On `uk` the
bias is one-sided **in the opposite direction to the one we wrote down**.

🔴 **The two directions take different code paths and produce different distortions** — verified in
`at_home_profile()`, not assumed. It clamps with `min(slot + n, 144)` and records
`covered = min(slot, 144)` (`4thJ_step5_temperature.py:179,186`):

- **UNDER 1440** — the fill stops early, the untouched tail keeps its `0`, and a *missing* tail is
  scored as *away from home*. 🟢 This is `FINDING 67`, and `D-S5-14`(a)'s covered basis removes
  exactly it.
- **OVER 1440** — the excess minutes are **silently discarded** and the diary reports **full**
  coverage. 🔴 No phantom tail, and **the covered basis cannot see it**, because by its own
  denominator such a diary is complete.

⚪ **The `D-S5-14`(a) remedy is correct and is not weakened.** What was wrong is its *scope*: it
addresses the **minority** of `uk` diaries, and a second distortion exists that **no Step 5 diagnostic
measures at all**. `FINDING 67` itself survives intact — its confound argument rests on the undershoot
rate moving along the swept axis, and it does (`uk` 28.6 → 23.3 %, `it` 46.5 → 39.6 %).

🔴 **`sum_1440_frac ≈ 0.06` must never be read as "the day is barely filled".** Median total minutes
is **1,460** (`uk`) and **1,440** (`it`); median absolute deviation **30** and **50** minutes — 2 %
and 3.5 % of a day; aggregate day-fill **101.6 %** and **100.4 %**. The budget error is **small and
roughly centred**. What the model almost never does is land *exactly* on 1440. Two very different
claims, and only the second is true.

⚪ **Cross-checked, not merely re-parsed.** Counting diaries that reach slot 143 from the independent
recount reproduces the artefacts' own `coverage_last_slot_frac` **row by row across all 30
realisations** — worst absolute disagreement **0.0253**, typically 0.002–0.010, and **always
positive**, as predicted: the artefact counts only diaries surviving `transcoder.parse_episodes`,
which drops malformed trailing episodes, so the gap must be positive and must grow with `T`. It does
(`it` `T=1.10` +0.003 → `T=1.30` +0.019). Two code paths, one quantity, agreement to ≤ 2.5 pp with an
explained residual.

🟢 **Step 7 does NOT inherit a design gap — the grammar is ALREADY TWO-SIDED BY CONSTRUCTION. Corrected here after checking the code rather than asserting from the finding.** `tally_automaton()` (`tools/4thJ_step7_grammar.py:169`) has 145 states and a **single** accepting state `{144}`, and `tally_step` returns `None` whenever `state + dur/10 > 144`. Run directly: `tally_step(143, 10) → 144` (accept), `tally_step(144, 10) → None`, `tally_step(140, 60) → None`, and from state 140 the only legal durations are **10–40 min**. **Overshoot has no transition; undershoot never reaches the accepting state.** Nothing needs adding to item 7.1.

🔴 **What `FINDING 75` actually supplies is the MAGNITUDE of the work that mask does.** Unmasked, **90–94 %** of generated diaries miss the budget, and **the majority miss it by OVERSHOOTING** — so the constraint the mask most often has to enforce is the **upper** one. A "pad the short tail" mental model of the grammar would have predicted the opposite, and §1 of the improvements document was written on exactly that model. ⚪ `G7.10` (the XGrammar back-end that would apply this during decoding) has **still never been run**, so the grammar remains a specification plus a hand-written oracle, not something demonstrated inside the generation loop.

🔴 **Episodes per diary at `T_chosen`, against the real reference measured in the same run on the same
600 prompts**: `es` 19.17 vs 28.38 (**0.68×**), `it` 21.86 vs 28.62 (**0.76×**), `uk` 23.99 vs 25.18
(**0.95×**). **Country-correlated in the LOCO-dangerous shape** — the same shape as `FINDING 53` and
`FINDING 72`: `uk` nearly right, `es` and `it` badly short. Read with the totals above, the reading is
**fewer, longer episodes filling the same day**, not a shorter day. ⚪ Reported, never thresholded —
and a **Step 6 input**, since `G6.8` scores transitions per day and dwell-time distributions, both of
which this moves on two folds of three.

⚪ **One caveat closed.** Earlier entries recorded that the real reference's `sum_1440_frac` was
*"asserted from the corpus measurement, not from this run"*. All three artefacts now carry
`real_structural`, and it reads **1.000 / 1.000 / 1.000** on parse, terminate and sum-to-1440 for
`es`, `uk` and `it`. `FINDING 67` now rests on a **within-run** comparison against an
identically-computed reference.

🟢 **The final Step 5 deliverable exists: `Step5_docs/outputs_step5/temperature_calibration.md`**
(331 lines) — both curves per fold, the explicit agreement statement, the `D-S5-13`(a) spread verdict
per statistic, the per-seed argmin stability table, the two-sided budget error, the declared
`D-S5-15`(a) splice, the frozen generation configuration, and the declared limitations. 🔴 **It is
GENERATED from the artefacts and must be regenerated, never hand-edited**; it fills in `es` and the
coverage-101 points automatically as they land. ⚪ `prereg.md` untouched, md5 unchanged.

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

> 🔴 **CORRECTED 2026-08-21 (night), after the coverage-101 jobs landed.** The band quoted in this paragraph is an argmin taken **inside the three-point replicate window** — the minimum of a *truncated* curve, and on `es` and `it` the ruled `T_fidelity` was not even in the window. It is **not** the fidelity temperature and must never be quoted as one. On the full nine-point grid the fidelity argmin moves one grid step under a seed change on **all three** folds: `es` **0.70 → 0.60**, `uk` **1.00 → 0.90**, `it` **0.80 → 0.90**, giving the bands `es` {0.60, 0.70}, `uk` {0.90, 1.00}, `it` {0.80, 0.90}. ⚪ The *conclusion* of this paragraph — that the fidelity argmin is not seed-stable — is unchanged and now holds on three folds rather than two. See the closing coverage-101 entry of this document.


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

## 2026-08-21 (night) — 🟢 THE `D-S5-15`(a) COVERAGE-101 JOBS LANDED. STEP 5 IS DELIVERABLE-COMPLETE. `FINDING 76`

`1285777` (`es`, 03:34:19), `1285778` (`uk`, 03:02:08), `1285779` (`it`, 03:47:39) all COMPLETED,
exit `0:0`. Artefacts and the 45 → **63** persisted generation files are local:

| fold | coverage artefact | md5 | local generation files |
|---|---|---|---|
| `es` | `temperature_calibration_es_coverage101.json` | `61b7c47782b7ea267591de163ef119b3` | 21 |
| `uk` | `temperature_calibration_uk_coverage101.json` | `d991683f718c81d6ebbcf98476712808` | 21 |
| `it` | `temperature_calibration_it_coverage101.json` | `325d6653d5b30b68ec12d77619632112` | 21 |

`temperature_calibration.md` regenerated from the artefacts — **352 → 530 lines**, md5
`cf8f441e37e124fb68fbad47c7c49b5f`. New §6.1–§6.5. 🔴 **It is generated by `scratchpad/mktc.py`.
Re-run it; never hand-edit it.**

🟢 **The gate board did not move: 36 verdicts, 34 PASS, 2 FAIL, 0 BLOCKED**, coverage clause still
*"every passing gate was made to fall"*, shipped populations md5-verified unchanged. This is the
correct outcome — the coverage jobs run in **replicate mode** and choose nothing.

### The splice is complete: 9 of 9 points on all three folds

Assembled from the seed-`101` rows of the replicate artefact (3 points) plus the coverage artefact
(6 points). No `T` appears in both — asserted in code, not assumed. All 27 points `usable`; lowest
`parseable_frac` anywhere is `0.9983` (`it` at `T = 1.30`). The reference side (`H_real`,
`real_structural`) is **byte-identical** between the primary and coverage artefacts on all three
folds, so the comparisons below differ only on the generated side.

### `fidelity_argmin_moved_under_D_S5_14` — derived offline, as the engine does not emit it here

| fold | argmin `at_home_mae_pp` | argmin `at_home_mae_pp_covered` | moved? | gap to runner-up | `G5.8` spread |
|---|---|---|---|---|---|
| `es` | 0.60 | 0.60 | ⚪ no | 0.4664 pp | 1.8127 pp |
| `uk` | 0.90 | **1.00** | 🔴 **YES** | **0.0437 pp** | 1.4072 pp |
| `it` | 0.90 | 0.90 | ⚪ no | 0.1156 pp | 3.1993 pp |

🔴 **The flag fires on `uk` and nowhere else** — `D-S5-14`(a)'s remedy is doing real work. ⚪ **But
the magnitude matters more than the flag:** the two competing `uk` minima are `0.0437 pp` apart
against a re-run spread of `1.4072 pp`, a factor of **32**. The argmin moved because the curve is
*flat* there, not because the basis change is decisive.

### 🔴 What the coverage jobs bought that nobody designed them to buy

The six coverage-101 points are a **second realisation** of six grid points the primary sweep had
already measured at generation seed `42`, and they sit at **six temperatures the replicate window
never reaches**. That is an independent re-run spread estimate, not derived from the same three
levels `G5.8` scores.

| fold | mean \|diff\| | max \|diff\| | at `T` | mean signed diff | `G5.8` step | `G5.8` spread |
|---|---|---|---|---|---|---|
| `es` | 0.5840 pp | **1.7176 pp** | 0.60 | −0.3579 pp | 0.9315 | 1.8127 |
| `uk` | 0.6100 pp | 1.2025 pp | 0.50 | −0.5884 pp | 1.3994 | 1.4072 |
| `it` | 0.8407 pp | 1.2418 pp | 0.80 | **+0.7076 pp** | 4.1114 | 3.1993 |

🔴 **This corroborates the two `G5.8` failures from outside the window that produced them.** On `es`
the step the gate is asked to call meaningful is `0.9315 pp`; two runs of the same configuration at
six *other* grid points disagree by up to `1.7176 pp`. `uk` is the same story less starkly
(1.3994 vs 1.2025). `it` clears comfortably (4.1114 vs 1.2418). ⚪ **The `D-S5-16` recommendation is
unchanged and is now supported by evidence the decision did not have when it was drafted: (a).**

🔴 **The fidelity argmin moves under a seed change on ALL THREE folds, over the full nine-point
grid:** `es` **0.70 → 0.60**, `uk` **1.00 → 0.90**, `it` **0.80 → 0.90**. One grid step each; two
down, one up, so no systematic direction. ⚪ **The fidelity temperature is therefore a BAND on every
fold** — `es` {0.60, 0.70}, `uk` {0.90, 1.00}, `it` {0.80, 0.90}.

🔴 **Correction to what this document recorded earlier.** The bands `{1.10, 1.20}` (`es`) and
`{1.00, 1.10}` (`uk`) were argmins taken **inside the three-point replicate window** — minima of a
truncated curve, and on `es` and `it` the ruled `T_fidelity` was not even in the window. **Never
quote the in-window argmin as the fidelity temperature.** Quote the nine-point bands above.

⚪ **The confound, stated not glossed.** The primary sweep and the replicate/coverage jobs are
separate engine invocations and **no cell shares both `T` and `gen_seed`**, so seed change and
engine change cannot be separated by exact reproduction. Two bounds: the reference side is
byte-identical, so any difference lives on the generated side; and the per-fold mean *signed*
difference has inconsistent signs (−0.3579 / −0.5884 / **+0.7076**), which is what sampling noise
looks like and not what a systematic engine change looks like. Evidence, not proof.

### 🟢 `T_chosen` survives the strongest test yet run

`argmin |dH|` over **all nine** grid points at a generation seed that played no part in the
selection: `es` **1.30**, `uk` **1.10**, `it` **1.20** — **identical to `T_chosen` on all three
folds**. The earlier 5/5 per-seed stability was measured inside a three-point window; this is the
whole grid. ⚪ The `es` asymmetry still stands and still belongs in the same sentence: `es` chooses
`1.30`, the **top of the grid**, so its argmin could only move inward — a **one-sided** test, and
`endpoint_entropy = True`.

### 🔴 `FINDING 76` — `uk`'s `agree = True` does not survive a seed change

| fold | `T_chosen` | `T_fid` @ seed 42 | gap | `agree` recorded | `T_fid` @ seed 101 | gap | `agree` under 101 |
|---|---|---|---|---|---|---|---|
| `es` | 1.30 | 0.70 | 0.6000 | False | 0.60 | 0.7000 | False |
| `uk` | 1.10 | 1.00 | **0.1000** | 🟢 **True** | 0.90 | **0.2000** | 🔴 **False** |
| `it` | 1.20 | 0.80 | 0.4000 | False | 0.90 | 0.3000 | False |

`agree` is `True` on **exactly one fold of three**, and that single `True` is the only evidence
anywhere in Step 5 that the entropy and fidelity criteria ever point the same way. It rests on a
margin of `0.0001` (`0.1000` against `agree_tol = 0.1001`). **Re-running the same configuration at
seed `101` moves the `uk` fidelity argmin one further grid step away and `agree` reads `False`.**

🟢 **`T_chosen` is unaffected, by pre-registration and not by luck.**
`4thJ_step5_temperature.py:607` fixes that entropy wins on disagreement; `uk` selects `1.10` whether
`agree` reads `True` or `False`.

🔴 **What must change is the claim, not the number.** *"On the UK fold the entropy and fidelity
criteria agree"* is a property of one realisation and does not replicate. It must never be written
as corroboration that the two criteria converge. Write **"agree to within one grid step in the
primary realisation; the agreement does not replicate at another seed"**, or do not write it.

⚪ This is the **third** independent measurement pointing the same way — `FINDING 74` (the
sensitivity trap), the argmin walk above, and `FINDING 76`: **the fidelity curve carries no
seed-stable signal on `es` or `uk`.** That is exactly what `G5.8` reports, and exactly what
`D-S5-16`(a) proposes to let stand in the paper.

⚪ `prereg.md` untouched throughout, md5 `e4243e07cdd80c9c846b91f40e3e8c45`. 🔴 **`D-S5-16` remains
the only thing Step 5 waits on.**


---

### 2026-08-22 — 🟢 **`D-S5-16` RULED (a). THE TWO `G5.8` FAILS ARE THE TERMINAL VERDICT AND STEP 5 IS CLOSED.**

**The gate is not amended.** `tools/4thJ_gates_step5.py` is byte-for-byte as it was when `G5.8`
failed. No fold is re-run and no temperature is re-tuned — the register itself forbids re-tuning an
uninformative sweep, and the ambiguity that made this a decision surfaced *by watching the gate fail*.

**FINAL STEP 5 BOARD — 36 gate-fold verdicts: 34 PASS, 2 FAIL, 0 BLOCKED.** Coverage clause clean
(*every gate on the board, the two failures included, was made to fall*). Shipped populations
md5-verified unchanged.

| gate | `es` | `uk` | `it` |
|---|---|---|---|
| `G5.8` | 🔴 **FAIL** (0.9315 vs 1.8127, **0.51x**) | 🔴 **FAIL** (1.3994 vs 1.4072, **0.99x**) | 🟢 PASS (4.1114 vs 3.1993, 1.29x) |
| `G5.9` | 🟢 PASS, perturbation fells it | 🟢 PASS, perturbation fells it | 🟢 PASS, perturbation fells it |
| all others | 🟢 PASS, each seen failing | 🟢 PASS, each seen failing | 🟢 PASS, each seen failing |

⚪ `G5.6-as-written` still FAILs 12 of 36 marginal rows — informational, superseded by
`D-S5-12`(a), **not counted in the board**.

**The fidelity deliverable is a BAND per fold:** `es` **{0.60, 0.70}**, `uk` **{0.90, 1.00}**,
`it` **{0.80, 0.90}**. 🔴 The FAIL is the *reason* it is a band. Never quote a single fidelity
temperature for `es` or `uk`, and never quote the truncated-window argmins `{1.10,1.20}` /
`{1.00,1.10}`.

🟢 **`T_chosen` is untouched and was never at issue:** `es` **1.30**, `uk` **1.10**, `it` **1.20**,
by entropy matching, reproduced exactly by `argmin |dH|` over all nine grid points at a generation
seed that played no part in the selection. ⚪ `es` carries `endpoint_entropy = True` and that
sentence travels with every `es` number.

🔴 **DEFINITION OF DONE — 4 of 5, PLUS ITEM 5 BY DECLARED EXCEPTION.** Item 5 reads *"all Step 5
gates PASS and each has been seen failing"*; under `D-S5-16`(a), `G5.8` does not pass on two folds,
so item 5 **cannot be ticked as written**. It closes as a declared exception: 10 of 11 gates pass on
all three folds and `G5.8` passes on `it`, every gate including the two failures has been seen
falling, and the two FAILs are carried into the paper as the result. **Never write Step 5 as 5 of 5,
and never write the board as 36 of 36.**

⚪ `prereg.md` untouched, md5 `e4243e07cdd80c9c846b91f40e3e8c45`. Nothing is running on Speed.
