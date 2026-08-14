# Step 8 — BEM / UBEM simulation. Validation.

### 4J HETUS LLM pipeline. Validation specification.
#### Implementation: `4thJ_08_bemSimulation.md`. Parent: `../4thJ_00_HETUS_LLM_Pipeline.md`

---

## STATUS

**OPEN. Nothing run.** All thresholds pre-registered.

---

## WHAT THIS STEP MUST PROVE

That the difference between our schedules and the flat 4.0 W/m² foil is **a property of the
schedules**, and not of the archetype we built, the band we chose, or the wiring between Step 7 and
EnergyPlus.

3J's history says the wiring is where the money goes.

---

## 🔴 GATE ZERO: THE UNINJECTED CONTROL, READ BEFORE ANYTHING ELSE

**G8.0.** For every archetype × climate, run with **no schedules applied**, and record where the
result sits relative to every band.

* **If a band fails on the control, that band is reported as a band-applicability limitation and its
  value is NOT moved to make it pass.**
* 🔴 **No injected result may be quoted before the control's value for the same band has been read.**
  A gate that no untreated control can pass is measuring the band, not the model — and in 3J that cost
  eight campaigns.

This is not a threshold. It is a precondition on reading every other number in this step.

---

## TIER 5 GATES — DOWNSTREAM ENERGY (ASHRAE Guideline 14 lineage)

| ID | Check | Target | Provenance |
|---|---|---|---|
| **G8.1** | NMBE, monthly | ±**5 %** | ASHRAE Guideline 14 |
| **G8.2** | NMBE, hourly | ±**10 %** | ASHRAE Guideline 14 |
| **G8.3** | CV(RMSE), monthly | **15 %** | ASHRAE Guideline 14 |
| **G8.4** | CV(RMSE), hourly | **30 %** | ASHRAE Guideline 14 |
| **G8.5** | Peak magnitude | ±**15 %** | inherited from papers 2 and 3 |
| **G8.6** | Peak timing | ≤ **1 h** | inherited |
| **G8.7** | Per-archetype EUI vs published band | **as-modelled = PASS, empirical = INFO** | `RL13` + project |

🔴 **G8.7's split is deliberate.** An as-modelled band is a comparison of like with like. An empirical
band includes occupant behaviour we did not model and equipment we did not represent, so a miss
against it is information, not a failure. **Reporting both and grading only one is the honest form.**

---

## WIRING GATES — WHERE 3J'S DEFECTS ACTUALLY LIVED

| ID | Check | Target |
|---|---|---|
| **G8.8** 🔴 Scenario differentiation | **Byte-identical outputs across two different scenarios is an automatic FAIL.** Compared on the result files, not on the inputs |
| **G8.9** 🔴 Stale-output guard | Any skip-if-done cache is invalidated by a wiring change. Asserted by changing a schedule and confirming the cell **re-runs** |
| **G8.10** Unmetered end-use tripwire | Σ end-use meters ≈ `Electricity:Facility` per run, within **0.5 %**. 🔴 **This gate was specified in 3J and never implemented, and 53.5 % of site energy read as zero while every scorecard stayed green** |
| **G8.11** Meter-name validity | Every requested meter name exists in this EnergyPlus version's output. An **unrecognised meter is refused, never zero-filled** |
| **G8.12** Schedule ingestion | The presence schedule EnergyPlus actually used, read back from the **saved IDF**, matches the Step 7 file by md5 |
| **G8.13** Interpolation setting | `Interpolate to Timestep = No` on every schedule object, asserted from the saved IDF |
| **G8.14** Manifest completeness | Every cell has schedule md5, IDF md5, weather md5, EnergyPlus version **and build hash**, and a **measured** platform field |
| **G8.15** Convergence and warnings | Zero severe errors; warning classes itemised and triaged **by kind, not by frequency** |

---

## 🔴 THE GATE WHOSE REFERENCE MUST NOT SHARE AN ANCESTOR

G8.12 compares the schedule EnergyPlus used against the Step 7 file. **If it reads the schedule from
the same in-memory object the injector wrote, it is comparing the injector's numbers against the
injector's own reading and cannot fail.**

**Requirement: re-open the SAVED IDF from disk, resolve the schedule reference, and compare against
the Step 7 artefact on disk.** Neither side is a number the transform reported about itself.

**Stated limit, kept in the code:** G8.12 and G8.13 both use the same IDF reader, so neither can catch
a defect *in that reader*. The independent guard for that is a separate script with its own parser,
and until it exists this limit is written in the methods rather than assumed away.

🔴 **And an assignment check, not only a value check.** A transform that re-points a schedule object at
a *different* schedule leaves no before/after pair to compare, and in 3J that hid a ×3.028 change in
DHW draw across all 56 cells while every value check reported zero violations.

---

## EVERY GATE MUST BE SEEN FAILING

| Perturbation | Must fail | Must stay clean |
|---|---|---|
| Run two scenarios with the same schedule file | **G8.8** | G8.10 |
| Change a schedule without clearing the cache | **G8.9** | G8.8 |
| Request a pre-EnergyPlus-9.4 meter name (`Gas:Facility`) | **G8.11**, and G8.10 must **also** fire — scored as coverage | — |
| Zero one end-use meter | G8.10 | G8.11 |
| Point a `People` object at a different schedule | 🔴 **G8.12's assignment arm** | G8.12's value arm — *which is exactly why the assignment arm exists* |
| Set `Interpolate to Timestep = Yes` | G8.13 | G8.12 |
| Copy another cell's manifest wholesale | **G8.14** (platform/timestamp arm) | G8.12 |
| Shift the modelled profile 2 h later | G8.6 | G8.5 |
| Scale annual energy by 1.2 | G8.1, G8.3 — coverage | G8.6 |
| Run with an archetype whose floor area is from a different geometry | G8.7 | G8.1 — *a 1.5× area error survives a read-through; only an explicit geometry assertion catches it* |
| 🔴 **Null perturbation: change nothing** | **nothing** | everything |

### Coverage clause

Cross-tab every perturbation against baseline; **FAIL the probe if any passing gate was never made to
fall.** 🔴 **Report which END each band gate fails at.** A gate reading "28 of 56 in band" before and
after, with all 28 having turned over from below-floor to above-ceiling, is an inversion that a
count-only diff calls "no change".

---

## VACUITY GUARDS

* **V8.a** — the scorer FAILs if it read fewer cells than the campaign manifest declares.
* **V8.b** — 🔴 **the scorer and the gate must consume the same table.** Assert the file path before
  scoring any delta. In 3J two adjacent sources for the same quantity differed by 26.5 % and
  disagreed about which of heating and cooling was larger, which inverted a pre-registered sign
  argument.
* **V8.c** — the scorer **imports** its bands from a single module. A second copy drifts, and the copy
  that drifts is the one being quoted.
* **V8.d** — areas, floor counts and volumes are read **per archetype from that archetype's own IDF**,
  never carried across geometries.
* **V8.e** — every gate's severity is **hard**. Grep for `hard=False` before trusting a PASS count.
* **V8.f** — warnings are triaged by **kind**. 🔴 Ranking them by frequency buries the single
  occurrence of "invalid" or "not found" under ten thousand benign repeats.

---

## WHAT THIS STEP'S VALIDATION DOES **NOT** COVER

* It does **not** validate the archetypes against measured buildings. We built them from TABULA
  parameters; that is limitation F2 and no gate here closes it.
* It does **not** validate end-use disaggregation. Step 9.
* It does **not** validate the transfer claim. Step 6. A cell can be perfect here on a country whose
  diaries were wrong.
* 🔴 It does **not** separate the schedule's effect from the **chaining rule's** effect. If open
  decision 14's sensitivity experiment shows more than 25 % peak-demand spread between chaining
  rules, **every number in this step is partly a measurement of that convention**, and the gates here
  cannot tell the two apart.
* 🔴 It does **not** cover a defect in the IDF reader itself. G8.12 and G8.13 share one, and that
  limit is stated in the code rather than discovered later.

---

## PROGRESS LOG

Append-only.

### 2026-08-14 — validation document created

* Sixteen gates plus G8.0, eleven perturbations, none run.
* 🔴 **G8.10 is in this document because in 3J it existed only in prose.** It was specified after a
  2J bug, never written into code, and the slot it occupied convinced everyone downstream that the
  property was covered. **A gate that exists only in a document is worse than a missing one.** When
  auditing this step, grep the code for every gate this document claims, not just the gates the code
  runs.
