# Step 11 — Activity-driven end-use loads at stock scale. Validation.

### 4J HETUS LLM pipeline. Validation specification.
#### Implementation: `4thJ_11_stockEndUseLoads.md`. Parent: `../4thJ_00_HETUS_LLM_Pipeline.md` Step 11.

---

## STATUS

⚪ **PRE-REGISTERED, 2026-08-26. Nothing scored.**

🔴 **Every band inherited from Step 9 is inherited UNMOVED — including the three that Step 9 failed.**
`G11.6`, `G11.7` and `G11.12` carry `G9.6`, `G9.7` and `G9.12`'s bands exactly. Relaxing a threshold
because the answer came out wrong is the one move this project refuses; Step 9 shipped three FAILs rather
than make it, and Step 11 inherits that posture along with the numbers.

🔴 **Gate-ID rule, same as Step 10's.** Step 11 opens a **new `G11.x` series**. No Step 11 result is filed
under a `G9.x` ID and no `G9.x` ID is scored here. Inheritance is written on each gate's row.

---

## THE GATE TABLE

### A. The mapping — inherited verbatim from `G9.1`–`G9.4`

| Gate | What it catches | Threshold | Inheritance |
|---|---|---|---|
| **`G11.1`** 🔴 Mapping citation completeness | An invented heuristic wearing a citation's clothes | **100 %** of rows in `activity_appliance_map.csv` carry a source model **and** the specific table or figure. A row citing only a paper is not cited | `G9.1` (PASS 61) |
| **`G11.2`** 🔴 VALIDATED labelling | A caveat presented as a method | **100 %** of rows carry VALIDATED or NOT VALIDATED **and** the validation scale. 🔴 **A row labelled VALIDATED with no scale is a FAIL, not a warning.** Keyed on the **structured** field, never on prose (`V11.e`) | `G9.2` (PASS 192) |
| **`G11.3`** Unsourced-row honesty | A plausible number filling a gap | Rows with neither a citation nor written reasoning: **0** | `G9.3` (PASS 149) |
| **`G11.4`** Citation correctness | A DOI that resolves to a different paper | CrossRef match on **volume, issue, page range AND first-author surname** — never the title alone. 🔴 A title-only match is what let our own note pass while wrong on three counts (`FINDING 47`). 🔴 If CrossRef is unreachable, print **`NOT CHECKED`**, never `PASS` (`V11.c`) | `G9.4`. 🔴 **Currently `NOT CHECKED` on the Step 9 board** — `FINDING 149` |

### B. The trigger and the loads — inherited from `G9.5`–`G9.11`, `G9.14`

| Gate | What it catches | Threshold | Inheritance |
|---|---|---|---|
| **`G11.5`** Cycle completion | A cycle truncated by the end of its activity episode | An appliance triggered near the end of an episode **still runs its full rated cycle**, asserted on synthetic edge cases, not only on the corpus | `G9.5` (PASS) |
| **`G11.6`** Trigger rate | A saturated trigger | Per-appliance daily activation counts within the source model's reported range, per household size. 🔴 **Band unmoved.** Step 9 verdict **FAIL 60** (`FINDING 139`, saturation; 3 standby-only devices `NOT_EVALUABLE`) | `G9.6` |
| **`G11.7`** DHW volume | A magnitude error hiding behind a plausible profile | **30–50 L/person/day at 60 °C**, population median, reported per country. 🔴 **Band unmoved.** Step 9 verdict **FAIL 300** at **100.16 / 117.65 / 91.06** — 2–4× the band. **Work item 11.2 must diagnose this before Step 11 re-measures it** | `G9.7` |
| **`G11.8`** DHW event mix | A total that is right for the wrong reasons | Four-event structure (short, medium, bath, shower) with the source model's proportions | `G9.8` (PASS 12, within 3 pp) |
| **`G11.9`** 🔴 DHW **assignment** check | A re-pointed object that a value check cannot see | Re-open the **saved IDF** and assert every `WaterUse:Equipment` object still points at the schedule it was built with. 🔴 In 3J this hid a **×3.028** draw increase across 56 cells with zero violations reported | `G9.9` (PASS 300) |
| **`G11.10`** Energy closure | Loads that do not reconcile with the gain they came from | Σ end-use loads reconciles with the total injected internal gain within **0.5 %**, rebuilt from the saved IDF and the on-disk schedules | `G9.10` (PASS 300) |
| **`G11.11`** 3-digit dependence | A mapping that never needed the corpus decision that preserved 3-digit ACL codes | Distinct ACL codes with distinct appliance rows exceeds the number of distinct 2-digit groups. ⚪ `RULED 2026-08-20` item 11(a): **this gate is allowed to fail** — 0 of 4 published models resolve at 3 digits — and **the band is not relaxed**; the 3-digit corpus decision is re-justified on microdata fidelity instead | `G9.11` (PASS 11, `FINDING 140`) |
| **`G11.14`** 🔴 Trigger inputs exist in the record | A trigger reading a column the diaries do not carry | The columns the trigger reads at runtime are a **subset** of the columns present in the generated diaries, asserted **against the file**, not against a schema constant. 🔴 **`act2` is calibration-only and must not appear in this set** — a trigger reading an absent column does not raise, it silently never fires | `G9.14` (PASS 9) |

### C. The claim — inherited and extended

| Gate | What it catches | Threshold | Inheritance |
|---|---|---|---|
| **`G11.12`** Stock-scale agreement | A load shape that disagrees with its source model | Aggregate load shape over **≥ 100 dwellings** against the source models' published aggregate profiles, **R² ≥ 0.85**. 🔴 **Band unmoved.** Step 9 verdict **FAIL 3** at R² **0.297 / 0.411 / 0.035**, scored on **exactly 100** dwellings per fold — the registered floor | `G9.12` |
| **`G11.13`** 🔴 Per-dwelling non-claim | An aggregate model quoted as a household prediction | **No result in any output, table or figure is a per-dwelling prediction.** Asserted by a search over the results artefacts; negated mentions are counted as denials, not as violations | `G9.13` (PASS 28) |

### D. New to Step 11

| Gate | What it catches | Threshold |
|---|---|---|
| **`G11.15`** 🔴 No double-counted service load | An end-use both **reconstructed** by Step 10 and **simulated** by Step 11 | For every building, each end-use is accounted on **exactly one** path, recorded in the manifest. End-uses appearing in both Step 10's Table-4 reconstruction and Step 11's trigger output: **0**. 🔴 The double count is invisible in either artefact read alone, which is why it is gated at the seam |
| **`G11.16`** 🔴 Aggregation-unit declaration | Two incomparable R² values placed side by side | Every stock-scale statistic names its **population**, its **spatial extent** and its **weather file**. A cross-population comparison presented without that declaration is a **FAIL**. 🔴 Step 9's 100 dwellings were drawn across a fold; Step 11's sit in one neighbourhood on one EPW — spatially adjacent and epoch-correlated. Not the same population |
| **`G11.17`** 🔴 Arm label survives aggregation | An Arm F total presented as an estimate, or the two arms silently pooled at stock scale | Every Step 11 aggregate names its Step 10 **arm**. Aggregates mixing Arm D and Arm F: **0**. Arm F aggregates carrying estimate language rather than **lower bound**: **0**. ⚪ The gate checks the **label and the pooling**, never a bias magnitude — `RL29`'s percentages rest on a self-refuting citation and are not registered anywhere in this suite |

---

## VACUITY GUARDS

* **`V11.a`** — **The mutation battery.** Every gate that **passes at baseline** is made to fall by a named
  mutation; the null perturbation moves nothing. Reported as `n HIT / n MISS / n already-failing`, with a
  coverage clause.
* **`V11.b`** 🔴 — **`ALREADY_FAILING_AT_BASELINE` is not a hit.** A gate already failing cannot be seen
  felled by its perturbation, and its perturbation therefore **demonstrates nothing about it**. Inherited
  from Step 9's own disposition of `G9.6`, `G9.7` and `G9.12`; applies to `G11.6`, `G11.7` and `G11.12`
  until the underlying quantity passes at baseline.
* **`V11.c`** — **`NOT CHECKED` is never a `PASS`.** 🔴 `FINDING 149`: Step 9's runner tallied
  `16 PASS / 3 FAIL` by counting `G9.4`'s `NOT CHECKED` as a pass. The **tally itself** is checked, not
  only the per-gate verdicts.
* **`V11.d`** — **Search gates print their scope.** `G11.13` and `G11.15` print the files they scanned and
  **FAIL if they scanned fewer than the declared artefact set**. 🔴 Step 9's battery found that
  `G9.13`'s scratch-directory exclusion was computed on the **absolute** path, so scoring an output tree
  under a `_`-prefixed directory made the gate skip the very artefacts it was pointed at — and the same
  bug disabled `V9.d`'s self-probe.
* **`V11.e`** — **Labels keyed on the structured field.** `G11.2` reads the structured VALIDATED / scale
  fields, never prose that mentions them.
* **`V11.f`** — **Gate-ID hygiene.** No Step 11 artefact writes a `G9.x` or `G10.x` verdict.
* **`V11.g`** — **The declared suite is the scored suite.** The runner refuses to report a tally if what it
  scored differs from what this document declares. 🔴 A gate that exists only in prose occupies the slot
  of the check that would have caught the defect.

---

## 🔴 WHAT A GREEN BOARD WOULD MEAN HERE, AND WHAT IT WOULD NOT

If `G11.6`, `G11.7` and `G11.12` come back **PASS** at stock scale, the honest reading is **a scale
effect** — and it is only readable that way if work item 11.2 has already diagnosed `G9.7` independently
of the re-measurement (§1.3 of the implementation document). Without that diagnosis, three gates flipping
from FAIL to PASS when the denominator grows is indistinguishable from the denominator having absorbed
the error.

If they come back **FAIL** again, Step 9's failures are confirmed as properties of the mapping, at the
scale its source models were validated at, and **that is the stronger result** — it is a measurement of
where an adapted CREST/Widén/LPG/RAMP mapping stops working on HETUS diaries, which no amount of
threshold movement could have produced.

---

## PROGRESS LOG

### 2026-08-26 — pre-registered

Seventeen gates and seven vacuity guards registered before anything is scored. Fourteen inherit a Step 9
threshold verbatim — three of them **inherit a FAIL** — and two are new, both at seams that did not exist
before Step 10: the reconstruction/simulation double count, and the aggregation-unit declaration.

⚪ `prereg.md` md5 `e4243e07cdd80c9c846b91f40e3e8c45` untouched. No Step 9 threshold moved.
