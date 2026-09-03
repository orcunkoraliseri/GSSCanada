# Step 11 — Activity-driven end-use loads at stock scale. Validation.

### 4J HETUS LLM pipeline. Validation specification.
#### Implementation: `4thJ_11_stockEndUseLoads.md`. Parent: `../4thJ_00_HETUS_LLM_Pipeline.md` Step 11.

---

## STATUS

⚪ **PRE-REGISTERED, 2026-08-26. Nothing scored.**

🟢 **AMENDED 2026-08-27: FOUR GATES ARE NOW SCORED. Work item 11.1, the carry-over
audit, ran and `G11.1`-`G11.4` are `PASS 61 / PASS 192 / PASS 149 / PASS 4` online and
`PASS / PASS / PASS / NOT CHECKED` offline** (`V11.c`). 🔴 **The other fourteen gates
are reported `NOT RUN` BY NAME and no tally is printed** - `V11.g`: a partial run that prints a
tally reads as a complete one, and fourteen absent gates are exactly what a tally hides.
⚪ Runner `tools/4thJ_gates_step11.py`, battery `tools/4thJ_step11_selftest.py`
(**7 HIT / 0 MISS / 0 already-failing**, null perturbation moved nothing, coverage clause PASS),
record `docs/2026-08-27_work-item-11.1_carry-over-audit.md`.

🟢 **RULED 2026-08-27, `D-S11-1` item 2: `G11.7` IS `INFO`, PERMANENTLY, AND IS NOT
SCORED AT STOCK SCALE.** It inherits the classification its Step 9 parent was given the same day,
for the same reason and on the same precedent (`G8.7`, `D-S8-5` item 1 (a)). 🔴 **The
30-50 L/person/day band is inherited UNMOVED, exactly as the paragraph below says** - what changed
is that the comparison is reported, not scored, because `FINDING 165` showed its two sides differ
by the factor `n_members`. 🔴 **Do not run a stock-scale attempt to fit the band.**
Growing `N` cannot move a per-dwelling constant divided by a household size whose mean is ~2.0, so
such a run could only produce a number that looked like evidence and was not.

🔴 **`D-S11-2` IS OPEN AND IS NOT MINE TO CLOSE.** `D-S11-1` item 1 left Step 9 with no
detector at all for `scale_dhw_by_2` - `4thJ_step9_selftest.py` line 204 named `G9.7` as the only
one and declared `G9.8` blind to it, and an `INFO` gate cannot fail. Seen, not inferred: doubling
every `dhw_*` column in a copy of the three per-dwelling tables leaves `G9.7` at `INFO`, medians
`200.31 / 235.30 / 182.13`. ⚪ **The repair that invents nothing** is to score the
per-**dwelling** daily volume against Jordan & Vajen's own **200 l/day**, which is the same
denominator as the model and is the source's own published figure, already in
`4thJ_step9_trigger.py` as `--dhw-l-per-day`'s default. 🔴 **It is not implemented, in
Step 9 or here.** Adding a scored arm is a band decision, and band decisions are the author's.

🟢 **CLOSED 2026-08-27, THE SAME DAY, BY THE AUTHOR: the arm is `200 l/day +/-10 %`, and it is
implemented in Step 9 as `G9.15`.** It scores the stock **mean** litres per dwelling per day - the
basis the source states, *"one-family house => 73 000 litres (= 365 days * 200 l/day)"* - and it was
seen failing before it was trusted: shipped tables **PASS** at 200.79 / 201.01 / 199.47,
every `dhw_*` column doubled **FAIL** at 401.58 / 402.03 / 398.93. ⚪ **It is a scale /
regression arm, never an external validation**: 200 l/day is also the emitter's own
`--dhw-l-per-day` default. 🔴 **The medians (174.97 / 175.79 / 195.13) are printed by the
gate on every run, because the distribution is right-skewed and a median arm at the same tolerance
would fail two folds - the statistic was chosen in the open and the alternative is recorded, not
buried.** 🔴 **`G9.7` and `G11.7` stay `INFO` and the 30-50 band stays exactly where it
was registered; nothing here rehabilitates them.**

🔴 **WHAT THIS OBLIGES STEP 11 TO DO, WRITTEN HERE BECAUSE THE RUNNER DOES NOT EXIST YET.**
`G11.18` is declared below and inherits `G9.15`'s basis and tolerance unchanged. 🔴 **`FINDING 168`, found 2026-08-27 while authoring work item 11.1: this arm was first declared as `G11.15`, an ID section D had already given to the double-count gate on 2026-08-26.** Two rows, one ID, in the document the runner reads to decide what it must score - `V11.g` compares sets, and a set does not count a duplicate twice, so one of the two gates would have gone unscored with the coverage clause still reporting PASS. ⚪ Caught by census, not by a run: nothing has been scored under either ID, so the repair is a renumber and no verdict moves. The newcomer moved because the older ID is referenced in the implementation document, the pipeline master and `V11.d`. When the Step 11
runner is authored (work item 11.1), it must score `G11.18` at stock scale and it must report
`G11.7` as `INFO`. ⚪ **`G11.18` is the one DHW arm at stock scale that is NOT vacuous:**
unlike `200 / n_members`, the per-dwelling mean is a quantity `N` genuinely sharpens, so growing the
sample narrows a confidence interval around something the source actually states.

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
| **`G11.4`** Citation correctness | A DOI that resolves to a different paper | CrossRef match on **volume, issue, page range AND first-author surname** — never the title alone. 🔴 A title-only match is what let our own note pass while wrong on three counts (`FINDING 47`). 🔴 If CrossRef is unreachable, print **`NOT CHECKED`**, never `PASS` (`V11.c`) | `G9.4`. 🔴 **Currently `NOT CHECKED` on the Step 9 board** — `FINDING 149`. 🟢 **AMENDED 2026-08-27 by work item 11.1: that sentence is now true only OFFLINE.** With a resolver reachable, `G11.4` scores **`PASS 4`** - all four citations, `FUENTES-2018` included, match CrossRef on title, volume, issue, page range and first-author surname. Offline it still prints `NOT CHECKED`, and `V11.c` still forbids reading that as a pass. ⚪ The two verdicts are not a contradiction: `NOT CHECKED` says the check did not run, and the whole point of `V11.c` is that this is a third thing, not a soft pass |

### B. The trigger and the loads — inherited from `G9.5`–`G9.11`, `G9.14`

| Gate | What it catches | Threshold | Inheritance |
|---|---|---|---|
| **`G11.5`** Cycle completion | A cycle truncated by the end of its activity episode | An appliance triggered near the end of an episode **still runs its full rated cycle**, asserted on synthetic edge cases, not only on the corpus | `G9.5` (PASS) |
| **`G11.6`** Trigger rate | A saturated trigger | Per-appliance daily activation counts within the source model's reported range, per household size. 🔴 **Band unmoved.** Step 9 verdict **FAIL 60** (`FINDING 139`, saturation; 3 standby-only devices `NOT_EVALUABLE`) | `G9.6` |
| **`G11.18`** 🟢 **DHW volume PER DWELLING** (declared 2026-08-27, `D-S11-2`; **renumbered from `G11.15` the same day, `FINDING 168`** - that ID was already the pre-registered double-count gate, and the newcomer moves) | A scale error in the emitted volume, now that `G11.7` is `INFO` and cannot fail | Stock **mean** litres per dwelling per day against **Jordan & Vajen's own 200 l/day, +/-10 %**, inherited from `G9.15` unchanged. ⚪ **A scale / regression arm, not an external validation** - 200 l/day is the emitter's own input. 🔴 **It exists because `D-S11-1` retired `G9.7`'s verdict and with it the only detector of `scale_dhw_by_2`; a gate scores a quantity AND detects a mutation, and retiring the first retires the second.** Unlike `G11.7` this arm is NOT vacuous at stock scale: the per-dwelling mean is a quantity `N` sharpens. The medians must be printed whatever the verdict . ⚪ **AMENDMENT 2026-08-27 (`FINDING 170`):** the OpenUBEM response of 2026-08-27 addresses this arm as `G11.15`, the ID it held before `FINDING 168` renumbered it the same day - read their §6 item 1 as **`G11.18`**. Their two asks need no change here: this arm's population is the Step 9/10 trigger output over HETUS households, **never the `S3` corpus** (nothing on the 4J side was ever scoped against 95 or 374), and it scores against Jordan & Vajen's own 200 l/day, which is the emitter's input, not an `S3` figure. 🔴 An IDF object census run 2026-08-27 confirms `S3` carries **no DHW term at all** - `WaterUse*` 0, `Lights` 0, `ElectricEquipment` 0 - so `S3` could not have served as a comparison even if this arm had proposed it | `G9.15` |
| **`G11.7`** DHW volume | A magnitude error hiding behind a plausible profile | **30–50 L/person/day at 60 °C**, population median, reported per country. 🔴 **Band unmoved.** Step 9 verdict **FAIL 300** at **100.16 / 117.65 / 91.06** — 2–4× the band. **Work item 11.2 must diagnose this before Step 11 re-measures it** — 🔴 **DIAGNOSED 2026-08-27, THEN RULED THE SAME DAY: `INFO`, PERMANENTLY, AND NOT SCORED.** `FINDING 163`–`166`: the band and the model come from two different papers, and the scored quantity is `200 / n_members`, so this gate measures household size. `D-S11-1` item 2 (2026-08-27) classifies `G11.7` `INFO` on the `G8.7` / `D-S8-5` item 1 (a) precedent and forbids a stock-scale attempt to fit the band: `N` cannot move `200 / n_members` when the mean household is ~2.0. 🔴 **The band is not moved either way, and the deviation is reported in full.** `docs/2026-08-27_work-item-11.2_G9.7-diagnosis.md` §8 | `G9.7` |
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
| **`G11.15`** 🔴 No double-counted service load | An end-use both **reconstructed** by Step 10 and **simulated** by Step 11 | For every building, each end-use is accounted on **exactly one** path, recorded in the manifest. End-uses appearing in both Step 10's Table-4 reconstruction and Step 11's trigger output: **0**. 🔴 The double count is invisible in either artefact read alone, which is why it is gated at the seam. ⚪ **AMENDMENT 2026-08-27:** when this gate is authored, the `S3` per-dwelling population is **26 dwelling zones in 12 buildings**, verified from the manifest here; **374 is a ZONE count** (348 of them massing floors) and **381** is the all-96 total including the fatal building's 7 zones. 🔴 `S3` carries exactly **two** end uses - ideal-loads heating and a constant `OtherEquipment` electricity - so the reconstruction/simulation seam has only those two to double-count, and at `f = 0` the electricity side is **flat at 3 W/m² with zero occupancy signal**. Record: `../Step10_docs/docs/2026-08-27_OpenUBEM-response-intake_S3-basis-and-population.md` |
| **`G11.16`** 🔴 Aggregation-unit declaration | Two incomparable R² values placed side by side | Every stock-scale statistic names its **population**, its **spatial extent** and its **weather file**. A cross-population comparison presented without that declaration is a **FAIL**. 🔴 Step 9's 100 dwellings were drawn across a fold; Step 11's sit in one neighbourhood on one EPW — spatially adjacent and epoch-correlated. Not the same population |
| **`G11.17`** 🔴 Arm label survives aggregation | An Arm F total presented as an estimate, or the two arms silently pooled at stock scale | Every Step 11 aggregate names its Step 10 **arm**. Aggregates mixing Arm D and Arm F: **0**. Arm F aggregates carrying estimate language rather than **lower bound**: **0**. ⚪ The gate checks the **label and the pooling**, never a bias magnitude — `RL29`'s percentages rest on a self-refuting citation and are not registered anywhere in this suite. 🟡 **Added 2026-09-03 (I-8):** Arm F redefined for no-core (check-FAIL or unusable footprint → one box per floor); this row's rule is unchanged. |

---

## VACUITY GUARDS

* **`V11.a`** — **The mutation battery.** Every gate that **passes at baseline** is made to fall by a named
  mutation; the null perturbation moves nothing. Reported as `n HIT / n MISS / n already-failing`, with a
  coverage clause.
* **`V11.b`** 🔴 — **`ALREADY_FAILING_AT_BASELINE` is not a hit.** A gate already failing cannot be seen
  felled by its perturbation, and its perturbation therefore **demonstrates nothing about it**. Inherited
  from Step 9's own disposition of `G9.6`, `G9.7` and `G9.12`; applies to `G11.6`, `G11.7` and `G11.12`
  until the underlying quantity passes at baseline. 🔴 **AMENDED 2026-08-27: `G11.7`
  is not `ALREADY_FAILING_AT_BASELINE`, it is `INFO`, and the difference matters to this guard.** A
  failing gate at least still fires on its mutation once the underlying quantity is repaired; an
  `INFO` gate never fires at all. `G11.7`'s perturbation is therefore not vacuous-for-now but
  vacuous-permanently, and the coverage clause must say so in those words. `D-S11-2` is where the
  missing detector is tracked.
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

> 🟢 **AMENDED 2026-08-27 - `G11.7` CANNOT COME BACK PASS, BECAUSE IT IS NO LONGER
> SCORED.** Work item 11.2 did the diagnosis this paragraph demanded, and the answer was that the
> question was ill-posed: the gate's two sides differ by `n_members`, so a stock-scale flip would
> have measured the stock's household-size distribution, not a scale effect. The paragraph below
> now governs `G11.6` and `G11.12` only, and for those two it stands unchanged.

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

### 2026-08-27 — `G11.7` IS BLOCKED BEFORE IT WAS EVER SCORED, AND NO BAND MOVED

Work item 11.2 diagnosed `G9.7`. Record:
`docs/2026-08-27_work-item-11.2_G9.7-diagnosis.md`; summary in §1.3a of the implementation document.

🔴 **`G11.7` must not be evaluated until `D-S11-1` is ruled.** It inherits the **30–50 L/person/day
at 60 °C** band verbatim, and 11.2 established that the band and the model do not share a
denominator: the band is per person and comes from **Fuentes et al. (2018)** by way of `RL13` row 15
(`FINDING 163`), while the model is per dwelling and comes from Jordan & Vajen's table, which
assigns **no temperature to any volume at all** (`FINDING 164`). The scored quantity reduces to
**`200 / n_members`** to within 0.0005 over all 300 Step 9 rows (`FINDING 165`), so the gate reports
the corpus's household-size distribution and not the DHW model.

🔴 **This is the §1.4 disposition arriving one step earlier than expected.** §1.4 says a failing
gate's perturbation demonstrates nothing. 11.2 adds a stronger case: a gate whose two sides are not
the same quantity demonstrates nothing **even when it passes**. `G11.7` would have been the third
inherited FAIL re-measured on a bigger denominator — the precise outcome §1.3 was written to
prevent, and the reason 11.2 was sequenced ahead of 11.5 in the first place.

🔴 **THE BAND IS NOT MOVED, UNDER ANY OPTION IN `D-S11-1`.** Recommendation is **(d)(ii) → (b)**:
repair the citation (`citations.csv` has only Jordan & Vajen; the band's real source is in no
citation table in this project), then make the gate a permanent `INFO` on the `G8.7` / `D-S8-5`
item 1 precedent, reported as `D-S9-2` item 7 (a) describes. 🔴 Option (d)(i) — keeping the band by
**declaring an occupancy** — would meet a threshold by choosing a parameter, and is listed only so
that it is on the record as refused.

⚪ **No `G11.x` has been scored.** Nothing in Step 11 has run; this entry blocks a gate, it does not
report one. `G11.6` and `G11.12` are untouched and still inherit their Step 9 FAILs unmoved.

⚪ `prereg.md` md5 `e4243e07cdd80c9c846b91f40e3e8c45` untouched. No Step 9 threshold moved, no
Step 9 verdict changed: `G9.7` still **FAILS 300**.


---

### 2026-08-27 (later) - `D-S11-1` RULED BY THE AUTHOR AND EXECUTED; `D-S11-2` OPENED IN ITS WAKE

🟢 **The ruling is (d)(ii) → (b), recorded by the author in §8 of
`docs/2026-08-27_work-item-11.2_G9.7-diagnosis.md`.** `G9.7` and `G11.7` are both `INFO`,
permanently, on the `G8.7` / `D-S8-5` item 1 (a) precedent; the citation is repaired; the band is
left exactly as registered and the deviation is reported as a denominator incompatibility rather
than as a model failure. The entry above this one, which blocked `G11.7` pending a ruling, is
answered - it is left standing because the log is append-only.

🟢 **Executed in Step 9, not here:** `g9_7()` now records `INFO` with
`G9_7_BAND_L_PER_PERSON_DAY` untouched at `(30.0, 50.0)`; `FUENTES-2018` is in `citations.csv` and
`G9.4` **caught it on the first online run** (`FINDING 167` - `RL13`'s `81(1)` carries an issue
number the publisher's record does not have, and the column is now empty to match the record).
Step 9's board reads `15 PASS / 2 FAIL / 1 INFO / 1 NOT CHECKED` offline, `16 PASS / 2 FAIL / 1
INFO` online. See `../Step9_docs/4thJ_09_enduseLoads_val.md`, entry of the same date.

🔴 **Executed here: nothing was scored, and that is deliberate.** No `G11.x` has run.
This entry classifies a gate and forbids a run; it does not report a result. `G11.6` and `G11.12`
still inherit their Step 9 FAILs, unmoved.

🔴 **`D-S11-2`, for the author.** The ruling removed the only detector of
`scale_dhw_by_2` from the Step 9 battery, and the removal was demonstrated rather than assumed.
The repair that invents no number is a per-**dwelling** arm at Jordan & Vajen's own 200 l/day -
same denominator as the model, source's own figure. It is not implemented. ⚪ Note what
it would and would not buy: it restores the mutation detector and it checks the emitter against its
own source, but it **cannot** rehabilitate the per-person band, which stays `INFO` under every
option because Fuentes et al.'s basis and Jordan & Vajen's basis do not become the same quantity by
being checked more carefully.

🟢 **CLOSED THE SAME DAY. `G9.15` is implemented, `G11.18` is declared, and the perturbation
table now names `G9.15` for `scale_dhw_by_2`.** Step 9 reads `16 PASS / 2 FAIL / 1 INFO /
1 NOT CHECKED` offline and `17 PASS / 2 FAIL / 1 INFO` online, over fifteen gates and five guards.
⚪ **Still nothing is scored here**: `G11.18` is a declaration, and Step 11 has no runner.

⚪ `prereg.md` md5 `e4243e07cdd80c9c846b91f40e3e8c45` untouched. No band moved anywhere.


---

### 2026-08-27 (last) 🟢 - `D-S11-2` CLOSED: `G9.15` EXISTS, `G11.18` IS DECLARED

🔴 **The author ruled the repair the same day it was raised: the per-dwelling arm, at Jordan &
Vajen's own 200 l/day, +/-10 %.** Implemented in Step 9 as `G9.15` and seen failing before it was
trusted - shipped `PASS` at 200.79 / 201.01 / 199.47 l/dwelling/day, doubled draws `FAIL` at
401.58 / 402.03 / 398.93. `4thJ_step9_selftest.py`'s registered table now hands
`scale_dhw_by_2` to `G9.15`, and `G9.7` is deliberately NOT listed as must-stay-clean: a
permanently-`INFO` gate staying clean is vacuous, it would pass that row even if the model were
deleted.

🟢 **The registered battery was re-run and agrees: 13 HIT / 0 MISS / 2 already-failing,
null perturbation moved nothing, COVERAGE CLAUSE PASS** (308.1 s, 25 households, fold `es`).
`scale_dhw_by_2` is a HIT on `G9.15`. ⚪ The shipped counts were 12 / 0 / 3; one
already-failing gate became an `INFO` classification and one genuine hit took its place.

⚪ **`G11.18` is declared here and inherits the basis and tolerance unchanged**, so the Step 11
runner cannot be authored without it - this document is what the runner reads. 🔴 **It is
the only DHW arm at stock scale that is not vacuous**, because the per-dwelling mean is a quantity
`N` sharpens and `200 / n_members` is not.

⚪ **What it is not.** A scale / regression check, never an external validation: 200 l/day is
the emitter's own `--dhw-l-per-day` default, so a pass says the pipeline reproduces its own stated
reference through disaggregation, the four-event split and the write-out. `G11.7` stays `INFO`,
the 30-50 band stays registered and unmoved, and the manuscript still reports that comparison as a
denominator incompatibility.

---

### 2026-08-27 (last, later) 🟢 - WORK ITEM 11.1 RAN. FOUR GATES SCORED, AND `FINDING 168` FOUND BEFORE THEY WERE

🟢 **`G11.1`-`G11.4` are scored.** Online `PASS 61 / PASS 192 / PASS 149 / PASS 4`;
offline the first three are unchanged and `G11.4` prints `NOT CHECKED` (`V11.c`). The other
fourteen declared gates are printed `NOT RUN` by name and **no tally is reported** (`V11.g`).
Runner `tools/4thJ_gates_step11.py`; artefacts
`outputs_step11/step11_carryover_audit_online.json` and `..._offline.json`.

🔴 **`FINDING 168`, found by census while authoring the runner: `G11.15` headed TWO
gate-table rows.** Section D's pre-registered double-count gate (2026-08-26) and the DHW
per-dwelling arm `D-S11-2` added on 2026-08-27. The runner reads its suite out of this document
and `V11.g` compares SETS - and a set does not count a duplicate twice, so it would have compared
seventeen declared against seventeen scored, reported a match, and left one of the two gates
unscored forever with a green coverage clause on top. ⚪ **The newcomer moved: the DHW
arm is now `G11.18`.** Nothing had been scored under either ID, so the repair is a renumber and no
verdict moves; the older ID stayed because the implementation document, the pipeline master and
`V11.d` already reference it. 🔴 **The detector is registered, not just the repair**:
`declared_gate_ids()` now censuses row heads and the runner REFUSES to score a document that
declares one ID twice, and `duplicate_gate_id` is a case in the battery.

🟢 **The battery: 7 HIT / 0 MISS / 0 already-failing, null perturbation moved nothing,
COVERAGE CLAUSE PASS** (0.2 s). `blank_source_table` fells `G11.1`, `strip_validation_scale`
`G11.2`, `strip_reasoning_and_citation` `G11.3`, `citation_lose_artefact` `G11.4`, and the
document mutation is refused outright.

🔴 **THE OBJECTION THIS AUDIT HAS TO ANSWER, ANSWERED IN THE OPEN.** Section 2 of the
implementation document says the mapping is **not re-authored**, so `G11.1`-`G11.4` re-score the
same rows with the same code against the same bars, and read carelessly that cannot fail. It can,
and the battery shows exactly where: **`drop_rows_to_20` leaves every gate's own verdict at
`PASS`** - twenty well-formed rows satisfy `G11.1` precisely as 192 do - **and the audit still
FAILS, on the inherited COUNT.** ⚪ That is the whole content of the word *carry-over*:
the audit asserts the rows are the same rows (md5 `640af0d0bdfadd5f10936d878bb0600d` for the
mapping, `f240b78bcbaa9783c0021f147cd2c09c` for the citations), that the bars are the same bars
(the expected verdict and count are parsed out of the INHERITANCE COLUMN of this document, never
from a constant in the runner, which would have been written by the same hand and would agree for
that reason alone), and that the code is the same code (`g9_1`-`g9_4` are IMPORTED from
`4thJ_gates_step9.py`, md5 `5c527ef86ccd87cd17c2c684061882cd`, and re-filed under `G11.x` IDs, so a
second opinion is impossible - a second opinion is not an inheritance).

⚪ **What 11.1 does NOT establish.** Nothing at stock scale. No building is simulated,
no Step 10 artefact is read, nothing is aggregated. The four gates score a mapping table, which is
scale-free - which is precisely why this is the one Step 11 item that can run before a cell exists.
🔴 **Scope note, recorded rather than resolved quietly:** the work-item row says *the
Step 9 mapping, trigger and citation set*, but its gate list is `G11.1`-`G11.4` and the trigger
gate is `G11.14`. `G11.14` asserts the trigger's runtime columns against the **generated diaries**,
and Step 11's diaries are Step 10's per-building `N_u` sets, which do not exist yet. It is
deliberately left to the run that has them; scoring it against Step 9's diaries would have answered
a question about Step 9.

⚪ `V11.f` holds: the board carries no `G9.x` or `G10.x` ID, asserted on the rows AND
on the serialised JSON before it is written. `prereg.md` md5 `e4243e07cdd80c9c846b91f40e3e8c45`
untouched. No band, threshold or tolerance moved anywhere; no Step 9 artefact was regenerated or
edited.

### 2026-08-27 (response intake) — TWO ROWS CARRY A DATED AMENDMENT, AND NO GATE, BAND OR VERDICT MOVED

Record: `../Step10_docs/docs/2026-08-27_OpenUBEM-response-intake_S3-basis-and-population.md`.
Incoming: `../messages_OpenUBEM/2026-08-27_OpenUBEM_to_4J_response_S3_EU-05-06_challenges.md`.

🔴 **`FINDING 170` — the OpenUBEM response addresses the DHW per-dwelling arm as `G11.15`.** That ID
became the pre-registered double-count gate again on 2026-08-27 under `FINDING 168`, the same day their
document was written; the DHW arm is **`G11.18`**. Acting on the letter by ID would have amended the
double-count gate — the one gate here whose subject is the Step 10 / Step 11 seam and not water.
⚪ Nothing had been scored under either ID, so no verdict moves. **Rule taken from it: a cross-tree
message that names a gate must name its date, because the ID is the token that goes stale silently.**

🟢 **Their two asks need no change to `G11.18`.** Its population is the Step 9/10 trigger output over
HETUS households, never the `S3` corpus — `grep` over `4J_docs_occ` finds **no** use of 95 or 374 as a
per-dwelling denominator anywhere on this side — and it scores against **Jordan & Vajen's own
200 l/day ±10 %**, the emitter's own input, not an `S3` figure. 🔴 An IDF object census run from this
machine on 2026-08-27 confirms `S3` carries **no DHW term at all** (`WaterUse*` 0, `Lights` 0,
`ElectricEquipment` 0, cooling coils 0), so `S3` could not have served as a comparison even had the arm
proposed it. `G11.18`'s basis, tolerance and inheritance from `G9.15` are **unchanged**.

⚪ **`G11.15` carries a forward amendment for whoever authors it.** The `S3` per-dwelling population is
**26 dwelling zones in 12 buildings**; **374 is a ZONE count** (348 of them massing floors) and **381**
is the all-96 total including the fatal building's 7 zones. `S3` carries exactly **two** end uses —
ideal-loads heating and a constant `OtherEquipment` electricity — and at `f = 0` that electricity is
**flat at 3 W/m² across all 381 gain CSVs, 8,760 rows each, zero occupancy signal**, verified here.

🔴 **`FINDING 172`, recorded in the Step 10 document and repeated here because it bears on every
`EU-*` number this suite will ever inherit:** the OpenUBEM tree **is** on this machine, at
`C:\Users\o_iseri\Desktop\OpenUBEM`, a **sibling** of `GSSCanada`. The earlier record saying otherwise
came from a `find` bounded to `Desktop\GSSCanada`. Every load-bearing figure in the response was
therefore **re-derived here and matches exactly**, including **96 of 96 recorded `idf_sha256`
recomputed with 0 mismatches**. ⚪ **A negative search result is only as strong as its root.**

⚪ `prereg.md` md5 `e4243e07cdd80c9c846b91f40e3e8c45` untouched. No Step 9 or Step 10 threshold moved,
no gate was scored, no artefact regenerated. The only edits are two dated amendments appended inside
existing table cells and this entry.
