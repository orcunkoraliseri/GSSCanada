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
| **G5.9** No truncation creep | Tail deletion at generation | If top-p is used at all, **p ≤ 0.98**, asserted in the generation config that Step 7 actually reads, not in a comment | `RL09` |
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
