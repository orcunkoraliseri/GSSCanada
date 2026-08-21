# Step 5 — Conditioning and population linkage. Validation.

### 4J HETUS LLM pipeline. Validation specification.
#### Implementation: `4thJ_05_populationLinkage.md`. Parent: `../4thJ_00_HETUS_LLM_Pipeline.md`

---

## STATUS

**OPEN.** 🟢 **2026-08-21: item 5.1 is COMPLETE — all three folds have published marginals** (`marginals_{uk,es,it}.csv` + `econ_11plus_{uk,es,it}.csv`), so `G6.1`'s raked-donor null is computable on every fold. 🟢 **2026-08-21 (afternoon): `strat_hh_type` is additionally on a PERSON basis in all three folds** (`hhtype_person_{es,uk,it}.csv`, convention A), which is what the rake must consume — `D-S5-6`, `D-S5-7`, `D-S5-8` closed; 🔴 `FINDING 60` / `D-S5-9` open, Italy's household-basis rows still on convention B. Items 5.2-5.4 are still unbuilt and no Step 5 gate has been run. All thresholds pre-registered.

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
| **G5.6** 🔴 Held-out marginal provenance | **Contamination** | Every marginal used for the held-out country traces to a **published** table with a URL and table ID. Count of marginals with no published source, or derived from microdata: **0** | **derived from the experimental design** |
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
| 🔴 **Substitute one held-out marginal with a value computed from that country's microdata** | **G5.6** | G5.1 — *the fit is fine, the provenance is not, and only G5.6 can see it* |
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
