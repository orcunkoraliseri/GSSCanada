# Step 5 — Conditioning and population linkage. Validation.

### 4J HETUS LLM pipeline. Validation specification.
#### Implementation: `4thJ_05_populationLinkage.md`. Parent: `../4thJ_00_HETUS_LLM_Pipeline.md`

---

## STATUS

**OPEN. Nothing built.** All thresholds pre-registered.

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
| **G5.4** Prefix field completeness | A prefix the model has never seen | 100 % of synthetic persons map to a prefix whose every field value **appears in the training corpus**. 🔴 An unseen field value at generation time is out-of-distribution input, and the model will do something confident with it | **project-chosen**<br>🔴 **2026-08-20 — SEE `FINDING 40`: as written this gate reads 0 % where it demands 100 %, because the first prefix field is `country` and under LOCO the held-out country's token appears in training exactly zero times. `D-S5-1 (a)` proposes narrowing the field set, never the threshold.** |
| **G5.5** Prefix encoder identity | A second copy of the field order drifting from the first | The prefix string built here is **byte-identical** to what `../tools/encoder.py` 🔴 *(2026-08-20: corrected from `../Step3_docs/outputs_step3/encoder.py`, which does not exist)* produces for the same person. Tested by importing that encoder, never by reimplementing it | **project-chosen** |
| **G5.6** 🔴 Held-out marginal provenance | **Contamination** | Every marginal used for the held-out country traces to a **published** table with a URL and table ID. Count of marginals with no published source, or derived from microdata: **0** | **derived from the experimental design** |
| **G5.7** Co-presence honesty | Conditioning on a flag a country never recorded | No prefix asserts a flag that `copresence_availability.md` marks "not recorded" for that country | **derived from Step 2** |
| **G5.8** Temperature calibration reported | A knob chosen without evidence | Both the entropy-matching curve and the fidelity curve are reported, and **whether they agree is stated explicitly** | **project-chosen** |
| **G5.9** No truncation creep | Tail deletion at generation | If top-p is used at all, **p ≤ 0.98**, asserted in the generation config that Step 7 actually reads, not in a comment | `RL09` |
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
| Reorder two prefix fields in a local copy | **G5.5** | G5.4 |
| 🔴 **Substitute one held-out marginal with a value computed from that country's microdata** | **G5.6** | G5.1 — *the fit is fine, the provenance is not, and only G5.6 can see it* |
| Assert an unrecorded co-presence flag | G5.7 | G5.4 |
| Report only the fidelity curve | G5.8 | all others |
| Set `top_p = 0.9` in the generation config | G5.9 | all others |
| Add a rake call to the generation path | G5.10 | all others |
| 🔴 **Null perturbation: change nothing** | **nothing** | everything |

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
