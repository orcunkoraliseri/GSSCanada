# Step 8 — BEM / UBEM simulation. Validation.

### 4J HETUS LLM pipeline. Validation specification.
#### Implementation: `4thJ_08_bemSimulation.md`. Parent: `../4thJ_00_HETUS_LLM_Pipeline.md`

---

## STATUS

**OPEN. 🟢 THE GATES HAVE RUN, ON THE UNINJECTED CONTROL, 2026-08-25 (late).** All thresholds pre-registered and none moved. `G8.0` executed over **88 archetypes × 2 runs**: **1,232 band rows, 0 gate-cell FAILs**, selftest **29 ok / 0 FAILED**, **12 of 12 injections seen felling their target**, baseline clean, coverage clause PASS. `G8.1`–`G8.4` have the reference `D-S8-1`(a) named and read **exactly 0** — tripwires, not accuracy measurements. `G8.13` is **NOT_EVALUABLE** and says so rather than claiming a vacuous pass. 🟢 **`D-S8-5` ruled 2026-08-25 (late) and applied the same day:** `G8.7` is **INFO, permanently** — no numeric band exists anywhere in this project and item 1 (a) rules that none is created; `G8.5`/`G8.6` are **reproducibility gates against the independent re-run**, `D-S8-1`(a) extended verbatim by item 2, thresholds unmoved, with the occupancy peak shift **reported as an empirical result and not gated**. `G8.12`/`G8.16` await 8.5, and `V8.g`'s arm is already armed. 🟢 **2026-08-25 (late), work item 8.4 is DONE: `G8.8` and `G8.9` were each seen PASSING on a correct cell and FAILING on a deliberately broken one** — 6 runs, 0 severe, 10 of 10 checks ok. 🔴 The probing found three defects: `FINDING 126` (`G8.13`'s parser could not see `Interpolate = Yes` on a real 9-field `Schedule:File`; fixed additively, injection `I13` added, battery now **13 of 13**), `FINDING 127` (`G8.10`'s note read "all zero" while the gate closed on 97.99 GJ) and `FINDING 128` (the full sweep is worth **+1.60 %** annual, **+10.84 %** peak — a PEAK channel). 🔴 **`FINDING 121`–`125` and `D-S8-5` are in `docs/2026-08-25_item-8.3_uninjected-control-campaign.md`; `FINDING 126`–`129` are in `docs/2026-08-25_item-8.4_the-two-probes.md`.**

🟢 **2026-08-25 (night) — THE INJECTED CAMPAIGN HAS RUN AND EVERY STEP 8 GATE IS NOW SCORED AND HAS BEEN SEEN FAILING.** 440 scenario-cells, **4,048 EnergyPlus runs, 0 severe**, **28,161 band rows, 0 gate-unit FAILs**, coverage clause **PASS**, battery **33 ok / 0 FAILED, 18 of 18 injections HIT**. **`G8.12` and `G8.16` are evaluated for the FIRST time in this project** — `G8.12` on both its value arm (the multiplier rebuilt from the published Step 7 diary on disk against the series the SAVED `in.idf` points at) and its **assignment arm** (`E_PHI_INT` must still name that `Schedule:File`), `G8.16` by locating each diary **by content** among the three Step 7 bundles and reading the fold out of the bundle's own manifest. Both report **`NOT_EVALUABLE` on the 88 `f = 0` cells** rather than a vacuous pass, and **`V8.h`** separately asserts that the `f = 0` multiplier is identically 1.0 so "no schedule" cannot hide a wrong one. 🔴 **Three defects were caught before anything was quoted, each now guarded and each guard SEEN FIRING on the artefact that was about to ship:** `FINDING 130` the diaries were the **Leg-4 pilot**, stamped `NOT REPORTABLE` in their own records, because the emitter had the leg hard-coded; `FINDING 131` the schedules were emitted on the survey years (`es` 2010, a **Friday** start) and wired into the 8.1 IDFs' **Sunday**-start `RunPeriod` — `FINDING 99` realised, and measured at −0.12 / −0.04 / +0.02 % annual and **+1.27 / +0.37 / −0.39 % on peak, sign differing by fold**; `FINDING 132` the pre-registered "annual mean exactly 3.0 W/m²" held in the generator and not in the artefact (4.01e-07 relative at `%.6f`, now 4.24e-11 against a bound derived from the write format). 🔴 **`FINDING 133`: the occupancy channel is a PEAK channel and the annual channel is empty** — median **+1.82 / −0.04 / +0.06 %** annual against **+6.38 / +4.54 / +3.96 %** peak, which **corrects `FINDING 128`'s magnitudes** while keeping its direction. 🔴 **`FINDING 134`: on annual heating the effect is SMALLER than the between-diary spread in all three folds**, so no annual occupancy claim survives; on peak it is 1.7–2.0× the spread and does. `FINDING 135`: the annual peak's hour of day never moves at any `f` — it is the thermostat recovery hour — while the mean diurnal profile shifts `uk` 5 → 7 and `it` 6 → 7 at `f ≥ 0.50`. 🔴 **`FINDING 130`–`135` are in `docs/2026-08-25_items-8.5-8.6_injected-campaign-and-aggregate.md`.**

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
| **G8.1** | NMBE, monthly | ±**5 %** | ASHRAE Guideline 14 🔴 *(2026-08-20 `FINDING 44`: no reference series is defined, and the parent forbids Guideline 14 as a bar. See `D-S8-1`.)* |
| **G8.2** | NMBE, hourly | ±**10 %** | ASHRAE Guideline 14 🔴 *(2026-08-20 `FINDING 44`: no reference series is defined, and the parent forbids Guideline 14 as a bar. See `D-S8-1`.)* |
| **G8.3** | CV(RMSE), monthly | **15 %** | ASHRAE Guideline 14 🔴 *(2026-08-20 `FINDING 44`: no reference series is defined, and the parent forbids Guideline 14 as a bar. See `D-S8-1`.)* |
| **G8.4** | CV(RMSE), hourly | **30 %** | ASHRAE Guideline 14 🔴 *(2026-08-20 `FINDING 44`: no reference series is defined, and the parent forbids Guideline 14 as a bar. See `D-S8-1`.)* |
| **G8.5** | Peak magnitude | ±**15 %** | inherited from papers 2 and 3 🟢 *(2026-08-25 `D-S8-5` item 2: reference = the independent re-run, `D-S8-1`(a) extended verbatim. Threshold unmoved. The occupancy peak shift is REPORTED, not gated — scoring it here is the `FINDING 44` inversion.)* |
| **G8.6** | Peak timing | ≤ **1 h** | inherited 🟢 *(2026-08-25 `D-S8-5` item 2: same re-pointing as `G8.5`.)* |
| **G8.7** | Per-archetype EUI vs published band | **INFO, permanently — no band** | `RL13` + project 🔴 *(2026-08-25 `D-S8-5` item 1 ruled **(a)**: no numeric band exists anywhere in this project and NONE IS CREATED. `G87_TOLERANCE_PCT` stays `None`; selftest `C16` fails if that ever changes. `FINDING 121` is published as a declared methodological limitation instead.)* |

🔴 **G8.7's split is deliberate.** An as-modelled band is a comparison of like with like. An empirical
band includes occupant behaviour we did not model and equipment we did not represent, so a miss
against it is information, not a failure. **Reporting both and grading only one is the honest form.**

---

## WIRING GATES — WHERE 3J'S DEFECTS ACTUALLY LIVED

| ID | Check | Target |
|---|---|---|
| **G8.8** 🔴 Scenario differentiation | **Byte-identical outputs across two different scenarios is an automatic FAIL.** Compared on the result files, not on the inputs. 🟢 *(2026-08-25 work item 8.4: PASS on `f = 0.00` vs `f = 1.00`, and **SEEN FAILING** on a scenario declared at `f = 0.50` and wired to `f = 1.00`'s schedule file. Scored only over runs that actually executed, so a stale cache fells `G8.9` and leaves this one silent.)* |
| **G8.9** 🔴 Stale-output guard | Any skip-if-done cache is invalidated by a wiring change. Asserted by changing a schedule and confirming the cell **re-runs**. 🟢 *(2026-08-25 work item 8.4: the cache is proved to HIT before anything else — a cache that never hits makes "it re-ran" meaningless — then PASS on an input-complete key, and **SEEN FAILING** on a key over the cell name alone.)* |
| **G8.10** Unmetered end-use tripwire | Σ end-use meters ≈ `Electricity:Facility` per run, within **0.5 %**. 🔴 **This gate was specified in 3J and never implemented, and 53.5 % of site energy read as zero while every scorecard stayed green** |
| **G8.11** Meter-name validity | Every requested meter name exists in this EnergyPlus version's output. An **unrecognised meter is refused, never zero-filled** |
| **G8.12** Schedule ingestion | The presence schedule EnergyPlus actually used, read back from the **saved IDF**, matches the Step 7 file by md5. 🟢 *(2026-08-25 work item 8.5: **first evaluation in this project** — PASS on 7,040 runs, `NOT_EVALUABLE` on the 88 `f = 0` cells where no Step 7 diary exists. **Seen failing on both arms**: the value arm on a schedule that is not the diary at this `f`, the assignment arm on `E_PHI_INT` re-pointed back at the flat schedule.)* |
| **G8.13** Interpolation setting | `Interpolate to Timestep = No` on every schedule object, asserted from the saved IDF. 🔴 *(2026-08-25 `FINDING 126`, found by work item 8.4: the parser read only the LAST comma-field, so the `Yes` was **invisible on a real 9-field `Schedule:File`** and the row read PASS. 8.3's injection `I9` used an 8-field shape, which is why the gate looked as though it had been seen firing. Fixed additively; injection `I13` covers the real shape; both fire.)* |
| **G8.14** Manifest completeness | Every cell has schedule md5, IDF md5, weather md5, EnergyPlus version **and build hash**, and a **measured** platform field |
| **G8.16** 🔴 Fold correctness | Every cell's `fold` field names the fold that **held out that cell's country**. Count of cells simulating a country under another country's fold: **0**. Checked against the Step 7 schedule provenance, not against the cell's own filename. 🟢 *(2026-08-25 work item 8.5: **first evaluation in this project** — PASS on 3,520 runs, `NOT_EVALUABLE` on the 88 `f = 0` cells. The diary is located **by content** (name + md5) among the three bundles on disk and the fold is read out of the bundle's own `manifest.json`; **seen failing** on a cell driven by another country's fold.)* |
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

🔴 **2026-08-25: that limit was not theoretical.** `FINDING 126` is a defect in exactly that reader,
and no gate found it — **a real artefact did**. Work item 8.4 wrote the project's first genuine
`Schedule:File` and the gate that exists to read it stayed silent. The lesson is recorded rather than
patched over: a checker is only as good as the shapes it has actually been shown, and 8.3's synthetic
injection was not one of them.

🔴 **And an assignment check, not only a value check.** A transform that re-points a schedule object at
a *different* schedule leaves no before/after pair to compare, and in 3J that hid a ×3.028 change in
DHW draw across all 56 cells while every value check reported zero violations.

---

## EVERY GATE MUST BE SEEN FAILING

| Perturbation | Must fail | Must stay clean |
|---|---|---|
| Run two scenarios with the same schedule file | **G8.8** | G8.10 — 🟢 **EXECUTED 2026-08-25 (8.4)**: declared `f = 0.50`, wired to `f = 1.00`'s file; byte-identical results, `G8.8` fell, `G8.10` PASS non-vacuously |
| Change a schedule without clearing the cache | **G8.9** | G8.8 — 🟢 **EXECUTED 2026-08-25 (8.4)**: key over the cell name alone; stale directory reused, `G8.9` fell, `G8.8` silent because the second run never executed |
| Request a pre-EnergyPlus-9.4 meter name (`Gas:Facility`) | **G8.11**, and G8.10 must **also** fire — scored as coverage | — |
| Zero one end-use meter | G8.10 | G8.11 |
| Point a `People` object at a different schedule | 🔴 **G8.12's assignment arm** | G8.12's value arm — *which is exactly why the assignment arm exists*. 🟢 **EXECUTED 2026-08-25 (8.5, `I16`)**: `E_PHI_INT` re-pointed back at `SCH_ALWAYS_ON`; the assignment arm fell with no value pair to compare |
| Set `Interpolate to Timestep = Yes` | G8.13 | G8.12 — 🟢 **EXECUTED 2026-08-25 (8.5, `I9`)** on the real 9-field `Schedule:File`; `G8.13` fell, `G8.12`'s value arm stayed clean |
| Copy another cell's manifest wholesale | **G8.14** (platform/timestamp arm) | G8.12 — 🟢 **EXECUTED 2026-08-25 (8.5, `I3`)**: `G8.14` fell alone |
| 🔴 **Drive one country's cells with a fold that did not hold that country out** | **G8.16** | G8.12, G8.14 — *the schedule is a real Step 7 artefact with a correct md5 and a complete manifest; only the fold is wrong, and the energy result would look entirely normal*. 🟢 **EXECUTED 2026-08-25 (8.5, `I17`)**: `G8.16` fell. 🔴 `G8.12` fell too and that is CORRECT rather than a leak — the other fold's diary is not the series the cell's own `in.idf` points at, so the value arm has a real disagreement to report |
| Shift the modelled profile 2 h later | G8.6 | G8.5 |
| Scale annual energy by 1.2 | G8.1, G8.3 — coverage | G8.6 |
| Run with an archetype whose floor area is from a different geometry | G8.7 | G8.1 — *a 1.5× area error survives a read-through; only an explicit geometry assertion catches it* |
| 🔴 **Null perturbation: change nothing** | **nothing** | everything — 🟢 **EXECUTED on both campaigns**: the pristine copy is scored FIRST and must come back with 0 FAILs before any injection below is trusted (8.3 `I0`, 8.5 `I0`) |
| 🔴 **A cache key that ignores an input** | **G8.9** | — 🟢 **EXECUTED 2026-08-25 (8.5, `I13`/`I14`)**: two runs handed the same key, and a saved IDF that no longer hashes to the key's own input |
| 🔴 **A schedule that is not the Step 7 diary at this `f`** | **G8.12's value arm** | — 🟢 **EXECUTED 2026-08-25 (8.5, `I15`)** |
| 🔴 **An `f = 0` multiplier that is not identically 1.0** | **V8.h** | — 🟢 **EXECUTED 2026-08-25 (8.5, `I18`)**: the arm that stops "no schedule" hiding a wrong one |
| 🔴 **A schedule bundle whose calendar is not the model's** | **V8.i** | — 🟢 **EXECUTED 2026-08-25**: seen refusing `leg4_es_independent_seed1` (2010, Friday start) against the IDF's Sunday-start `RunPeriod` |

### 🔴 `V8.i` — the schedule's calendar must be the model's

Added 2026-08-25 (night), after `FINDING 131`. The 8.1 IDFs declare
`RunPeriod ... Sunday, !- Day of Week for Start Day`, chosen before any schedule existed; the
schedule bundles were emitted on the survey years, and `es` 2010 starts on a **Friday**. Wired
together, every synthetic Saturday lands on a Thursday for fifty-two weeks and **the energy result
looks entirely normal** — `FINDING 99` predicted exactly this and nothing was checking it.

**The check reads both sides from artefacts:** the start day out of the IDF, the calendar year out of
the bundle's own `manifest.json`, and it refuses the pair on a mismatch or on a 366-day year. It was
**seen firing** on `leg4_es_independent_seed1`, the bundle the first build of the injected campaign
actually ran on.

⚪ `D-S7-8`(a) had ruled the schedule year to be *"the first calendar year of whatever twelve-month
weather window `D-S8-2` item 6 fixes"*. `D-S8-4` then made that window a **TMYx.2009-2023** composite,
which has no calendar year — so the ruling lost its referent, and the IDF's own `RunPeriod` is the
only calendar left in the model. The bundles are emitted on **2017**, the nearest non-leap year whose
1 January is a Sunday; every such year gives an identical day-type sequence, so the year is a
consequence and not a choice.

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
* **V8.g** — G8.16 FAILs rather than passing if any cell's manifest carries **no** `fold` field. A
  correctness check over a field that does not exist finds zero violations for the wrong reason, and
  reports the same number as a clean campaign.

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

### 2026-08-14 (second entry) — G8.16, fold correctness

* **Seventeen gates plus G8.0, twelve perturbations, none run.**
* 🔴 **A cell driven by the wrong fold passes every other gate in this document.** The schedule is a
  genuine Step 7 artefact, its md5 matches, the manifest is complete, the platform was measured, and
  the EUI is plausible. **Nothing in the energy result can distinguish a transfer schedule from a
  held-in one**, which is the whole reason the check has to read the fold from Step 7's provenance and
  refuse to infer it from the cell's filename.
* **V8.g** guards the usual way a provenance gate passes for the wrong reason: no `fold` field means
  zero violations found.

### 2026-08-20 — 🔴 **`G8.1`–`G8.4` NAME NO REFERENCE SERIES, AND EVERY CANDIDATE EITHER DOES NOT EXIST OR INVERTS THE CLAIM. `FINDING 44`, `D-S8-1`.**

Written as parallel work while Step 4's `it` fold holds the GPU. **Nothing in Step 8 has been run** —
`outputs_step8/` is empty, no archetype IDF exists, no control campaign, no cell. This is a reading of
the gate table against this step's own claim statement and against the parent document.

#### The four gates

| ID | Check | Target | stated provenance |
|---|---|---|---|
| `G8.1` | NMBE, monthly | ±5 % | ASHRAE Guideline 14 |
| `G8.2` | NMBE, hourly | ±10 % | ASHRAE Guideline 14 |
| `G8.3` | CV(RMSE), monthly | 15 % | ASHRAE Guideline 14 |
| `G8.4` | CV(RMSE), hourly | 30 % | ASHRAE Guideline 14 |

**All four are error metrics between a series and a reference: `NMBE = Σ(y − ŷ) / ((N−p)·ȳ)`. Nothing
in this document says what `y` is.** Three candidates exist and none of them works.

#### 🔴 (a) Measured data — does not exist, and this document says so.

*"It does **not** validate the archetypes against measured buildings. We built them from TABULA
parameters; that is limitation F2 and no gate here closes it."* There is no metered dwelling anywhere
in this project. **The one reference Guideline 14 was written for is the one we do not have.**

#### 🔴 (b) The flat 4.0 W/m² foil — this makes the gate pass exactly when the paper fails.

This step's own *"WHAT THIS STEP MUST PROVE"* is *"that the difference between our schedules and the
flat 4.0 W/m² foil is a property of the schedules"*. Published European stock studies put that
difference at **15 to 50 % on annual space heating and 100 to 300 % on dwelling peak electrical
demand** — the implementation doc quotes exactly those figures as *"the size of the effect this paper
is manipulating"*.

**Scored against the foil, `G8.1` demands NMBE within ±5 % — i.e. that our schedules produce
essentially the foil's energy.** A PASS would mean the activity-resolved diaries changed nothing, which
is the null result. **The gate's passing condition is the negation of the claim.** `G8.5`'s ±15 % peak
band has the same problem against an effect sized at 100–300 %.

#### 🔴 (c) The uninjected control — same inversion, and it collides with `G8.0`.

`G8.0` exists to establish where the untreated control sits *relative to every band*, on the 3J lesson
that **a gate no untreated control can pass is measuring the band, not the model.** Scoring the
injected cells *against* that control turns the control into the reference, and then the control scores
a perfect zero on `G8.1`–`G8.4` by construction — a gate the null passes best of all.

#### Provenance contradiction, and it is already written down elsewhere

The parent, `../4thJ_00_HETUS_LLM_Pipeline.md:432`, on ASHRAE Guideline 14:

> *"a **different quantity** — model versus measurement, not convention versus convention — and may be
> quoted only as context, **never as a bar**."*

`../Step7_docs/4thJ_07_constrainedGeneration.md` repeats it: *"Guideline 14's tolerances are
model-versus-measurement, a different quantity, and may be quoted as context but never as our bar."*
🔴 **Four gates in this step use them as the bar, and name Guideline 14 as the provenance for doing
so.** The prohibition and the violation were written eleven days apart and neither document knows
about the other.

#### `D-S8-1` — for the author. This must be ruled before any archetype is built, not after.

| | ruling | consequence |
|---|---|---|
| **(a)** | 🔴 **Recommended. Re-cast `G8.1`–`G8.4` as *reproducibility* gates, not accuracy gates** — reference = **a re-run of the same cell**, so they detect nondeterminism, wiring drift and stale outputs. That is a real defect class (it is `G8.8`/`G8.9`'s neighbourhood) and Guideline 14's tolerances become a **conservative** bound rather than a borrowed one. **The thresholds do not move; the reference is named.** |
| **(b)** | Keep the foil as reference and **inverted** — require the difference to EXCEED a floor. | Honest, but it is a **new** threshold with no provenance, and setting it now while no number exists is the only moment it can be set cleanly. |
| **(c)** | Delete `G8.1`–`G8.4` and report the foil-vs-schedules difference as the **result**, ungated. | Loses four gates but loses nothing real — they cannot currently be evaluated. `G8.7`'s as-modelled/empirical split already carries the honest comparison. |
| **(d)** | Obtain measured data. | Out of scope; no dataset is named anywhere in the project. |

🔴 **Whichever is ruled, `G8.7`'s split is untouched** — *"as-modelled = PASS, empirical = INFO"* is
already the correctly-framed gate in this table, and it is the model for what `G8.1`–`G8.4` should
look like.

#### The one thing in this step that is genuinely buildable today

**Work item 8.1 — the archetype IDFs.** The implementation doc calls this *"three to five days, **on the
critical path**, and it was not in the original scope"*, and it depends on **nothing upstream**: TABULA
parameters → OpenStudio/TEASER needs no model, no adapter, no schedules and no Step 7 output. It is the
longest-lead item in the whole downstream half and it can start now. **It was not started here** — see
below.

#### What was NOT done

No IDF was built, no TABULA table downloaded, no weather file selected, no control campaign, no cell,
nothing submitted to Speed. `outputs_step8/` remains empty. **`../Step6_docs/outputs_step6/prereg.md`
not touched** — md5 `e4243e07cdd80c9c846b91f40e3e8c45`, verified against its sidecar.

---

### 2026-08-20 (evening) — 🟢 **`D-S8-1` RULED (a): `G8.1`-`G8.4` BECOME REPRODUCIBILITY GATES. THE THRESHOLDS DO NOT MOVE; THE REFERENCE IS FINALLY NAMED.**

**Ruled by the author 2026-08-20.** `FINDING 44` established that these four gates named ASHRAE
Guideline 14 tolerances against **no reference series at all**, and that every candidate reference
either does not exist or inverts the claim — a foil-based reference makes them pass **only when our
claim fails**. `RL24` then confirmed there is no library of European residential EnergyPlus models and
no measured dataset for our archetypes, which closed option (d) by evidence.

**The ruling, stated so it cannot be re-read as an accuracy claim:**

| | after the ruling |
|---|---|
| **reference** | 🔴 **a re-run of the same cell.** Named, obtainable, and free. |
| **what they detect** | nondeterminism, wiring drift, stale outputs — a **real** defect class, and the neighbourhood `G8.8`/`G8.9` already occupy. |
| **thresholds** | **unchanged**: NMBE ±5 % monthly / ±10 % hourly, CV(RMSE) 15 % monthly / 30 % hourly. |
| **what Guideline 14 is now** | a **conservative bound**, not a borrowed bar. A re-run should differ by ~0; tolerating 15 % is generous by orders of magnitude, and that is the point — anything that trips these is badly wrong, not marginally inaccurate. |

🔴 **The sentence that must appear wherever these gates are reported:** *"`G8.1`-`G8.4` are
reproducibility gates. They compare a cell against a re-run of itself. They are **not** a validation of
simulated energy against measured energy, and no such validation is claimed anywhere in this paper."*
Without it, four ASHRAE-labelled tolerances in a results table will be read as an accuracy result by
every reader who does not reach the footnote.

**Rejected, and why it is worth recording rather than just dropping:** (b) would have set a brand-new
exceedance floor with no provenance — and now, while no number exists, was the only moment it could be
set cleanly, so it is genuinely foreclosed rather than deferred. (c) would have lost nothing real but
also nothing gained. (d) is out of scope on evidence, not on effort.

🟢 **`G8.7` is untouched and remains the model.** Its as-modelled = PASS / empirical = INFO split was
already the correctly-framed gate in this table, and (a) makes `G8.1`-`G8.4` look like it.

#### 🔴 A measured input for work item 8.1, from the corpus, available today

The Step 3 corpus was fetched and scored locally while ruling `D-S7-1(c)` (retrieval only, no cluster
compute). Two numbers land squarely on the schedule builder and on archetype occupancy:

* **Mean at-home time is `1,028.8` min/day — `71.4 %` of the modelled day**, corpus-wide. Per fold:
  `it` `1,046.8` (72.7 %), `uk` `1,011.8` (70.3 %), `es` `1,006.7` (69.9 %). Tight across countries,
  which is worth knowing before any transfer result is interpreted.
* 🔴 **1,320 diaries — `1.802 %` — have ZERO at-home minutes.** Per fold: `uk` `2.927 %`, `es`
  `1.641 %`, `it` `1.417 %`, a **2.1x spread**. These are dwellings with **nobody home for a full
  modelled day**. That is legitimate and it must be an **explicit branch** in the schedule builder,
  not an emergent accident — an unoccupied-all-day dwelling has no metabolic gain, no appliance
  trigger and, depending on the setback rule, a materially different heating demand.

#### Work item 8.1 remains the longest-lead item and is fully unblocked

`tabula-values.xlsx` is verified (md5 `7347b2cae3c4d9f5ce78221e9d5fb832`, 65 sheets, 22/22
construction-period bands checked against the file), it depends on nothing upstream, and it needs no
further author decision on the source. 🔴 **`GB` is Great Britain — Northern Ireland is outside the
archetype set**, and that stays a declared limitation of the `uk` fold. **Still unverified from
`RL24`:** `tabula-calculator.xlsx` contents (B16), the "what TABULA does not supply" list (B17), and
the licence/redistribution terms (B12) — the last of these **before any derived table is published**,
not before it is used internally.

**Nothing was built or submitted here.** `outputs_step8/` remains empty. **`prereg.md` not touched**,
md5 `e4243e07cdd80c9c846b91f40e3e8c45` verified against its sidecar.

### 2026-08-25 (late) — 🟢 **THE GATES RAN. `G8.0` OVER 88 ARCHETYPES × 2 RUNS: 1,232 BAND ROWS, 0 FAILS, 12 OF 12 PERTURBATIONS SEEN FELLING THEIR TARGET, COVERAGE CLAUSE PASS. 🔴 AND THE CONTROL DOES NOT SIT INSIDE THE ONLY AS-MODELLED BAND THAT EXISTS.**

**Seventeen gates plus `G8.0`; ten scored, four declared not evaluable, three awaiting 8.4 / 8.5.**
Nothing above was written in prose this time — every row was produced by
`tools/4thJ_gates_step8_control.py` reading artefacts off disk, and the perturbation table below was
executed rather than described. Record:
`docs/2026-08-25_item-8.3_uninjected-control-campaign.md`.

#### `G8.0` — the precondition, discharged

| fold | control EUI | TABULA `q_h_nd` | dev | cells above | E+ heating h | TABULA implied h |
|---|---|---|---|---|---|---|
| `es` | 24.92 | 10.91 | **+136.6 %** | 21 of 24 | 2,901 | 539 |
| `uk` | 104.47 | 165.93 | **−29.6 %** | 0 of 32 | 6,117 | 5,832 |
| `it` | 81.00 | 168.49 | **−36.7 %** | 0 of 32 | 4,784 | 4,176 |

🔴 **`FINDING 121`, and `G8.0`'s own instruction now binds**: *"if a band fails on the control, that
band is reported as a band-applicability limitation and its value is NOT moved to make it pass."* No
value was moved. The sign flips by country, so this is a **country-correlated** limitation sitting
inside the LOCO channel — the same class as `FINDING 110`/`117`/`120` and larger than all three.

#### What each gate did

| gate | verdict over 88 cells | reference |
|---|---|---|
| `G8.1` `G8.2` `G8.3` `G8.4` | **PASS 88, all reading exactly 0** | the independent re-run — `D-S8-1`(a). 🔴 Tripwires, **not** accuracy measurements |
| `G8.5` `G8.6` | PASS 88 (0 % / 0 h) | the re-run only. 🔴 Their intended reference is still unnamed — `D-S8-5` item 2 |
| `G8.7` | **`NO_THRESHOLD_PREREGISTERED` 88** | TABULA `q_h_nd`. 🔴 The gate has no numeric band anywhere in this project — `D-S8-5` item 1 |
| `G8.10` | PASS 88 | `eplustbl.csv`. ⚪ The electricity arm is **vacuous** here — the control has no electric end use, declared not hidden |
| `G8.11` | PASS 88 | requested vs **delivered** variables, plus an `invalid`/`not found` scan of every `.err` line |
| `G8.13` | **`NOT_EVALUABLE` 88** | the control uses `Schedule:Constant` only, which carries no interpolate field. Vacuously clean and it says so — `FINDING 95`'s lesson |
| `G8.14` | PASS 88 | manifests, cross-checked against each cell's **own** `.err`, with the platform measured per run |
| `G8.15` | PASS 88 | 0 severe; warnings triaged **by kind** — which is how `FINDING 124` surfaced |
| `V8.d` `V8.x` | PASS 88 | each cell's own `eplusout.eio` / the two E+ heating series |
| `G8.8` `G8.9` | not evaluable **at the control** — one scenario cannot differ from itself and the 8.3 runner has no cache. 🟢 **EVALUATED by work item 8.4**, each seen passing and each **seen failing** | `probes_step8.json` |
| `G8.12` `G8.16` | not evaluable — no Step 7 schedule exists in a control. **Work item 8.5**; `V8.g`'s arm is already armed | |

#### The perturbation table, executed

| perturbation | felled | also felled |
|---|---|---|
| scale the re-run's annual energy by 1.2 | `G8.1` | `G8.2` `G8.3` `G8.4` `G8.5` |
| shift the re-run profile 2 h later | `G8.6` | `G8.4` |
| copy another cell's manifest wholesale | `G8.14` | — |
| delete the `fold` field (`V8.g`) | `G8.14` | — |
| a floor area from a different geometry | `V8.d` | — |
| zero one end-use row, leave the total | `G8.10` | — |
| an `invalid` / `not found` line in `.err` | `G8.11` | — |
| a severe error in `.err` | `G8.15` | — |
| `Schedule:File` with `Interpolate to Timestep = Yes` | `G8.13` | — |
| over-declare the campaign's cell count | `V8.a` | — |
| a manifest claiming an engine its own `.err` denies | `G8.14` | — |
| the two E+ heating series disagree by 5 % | `V8.x` | — |

⚪ Rows 1 and 2 felling more than their registered target is **reported, not tidied away**: a 1.2×
scale puts NMBE at −16.7 % and monthly CV(RMSE) at 16.7 %, so `G8.2` and `G8.3` must fall with
`G8.1`; a 2-hour roll is a large hourly point-difference, so `G8.4` must fall with `G8.6`.
🟢 **No gate that scored PASS was left unfalsified, and there were no no-ops.**

#### The vacuity guards, and what each actually did

`V8.a` 88 declared / 88 read, **and it was seen refusing** when the count was inflated. `V8.b` one
table, path asserted and printed before any delta. `V8.c` every threshold imported from
`tools/4thJ_step8_bands.py`; there is no second copy. `V8.d` areas read from each cell's own
`eplusout.eio` and cross-checked as floor × storeys = `A_C_Ref`. `V8.e` all 1,232 rows carry
`severity=hard`, re-read from the artefact, and the soft-severity literal the guard says to grep for
appears nowhere in `tools/`. `V8.f` triage **by kind**, with `invalid` and `not found` looked for by
name — 88 benign ground-temperature warnings did not bury the 32 Italian ones. `V8.g` every manifest
carries an explicit `fold`.

#### 🔴 What this document must not be read as saying

**`prereg.md` is untouched** — md5 `e4243e07cdd80c9c846b91f40e3e8c45`, verified before and after — and
it contains no Step 8 clause, so nothing here is a pre-registration deviation. **No threshold was
edited and no band was moved.** The four modelling conventions measured in the record
(`FINDING 122`–`125`) were **measured and left alone**: ruling any of them is a basis change that
would invalidate the 88 IDFs, `D-S8-3`'s geometry and this campaign, and none is needed for 8.4 or
8.5.

---

### 2026-08-25 (late, addendum) — 🟢 **`D-S8-5` RULED, BOTH ITEMS. THE TWO GATES THAT NAMED NO REFERENCE AND NO BAND NOW HAVE AN ANSWER, AND NEITHER ANSWER IS A NUMBER CHOSEN AFTER SEEING THE RESULT.**

| item | ruling | what the scorer now does | the invariant it protects |
|---|---|---|---|
| **1** `G8.7` | 🟢 **(a)** | emits **`INFO`**, 88 of 88, with an **empty threshold column** | zero band-fitting. `G87_TOLERANCE_PCT` is `None` **permanently**, and `C16` now fails if the column fills or the `None` leaves the bands module |
| **2** `G8.5` / `G8.6` | 🟢 **approved** | scores against the **independent re-run**, thresholds unmoved (±15 %, ≤ 1 h), note reads *"reproducibility tripwire; peak shift is reported, not gated"* | the `FINDING 44` inversion — a ±15 % peak band on the flat control fails **exactly when the paper's claim succeeds** |

🔴 **Why `G8.7` is INFO rather than a gate with a generous band.** A generous band is still a
band, and it would be chosen with the control values already on the table. The comparison itself is
not a compliance test: EnergyPlus hourly-dynamic against TABULA's monthly quasi-steady-state `q_h_nd`
differs by **method**, and `FINDING 121`'s Spanish +136.6 % is dominated by heating-season definition
(2,901 h against TABULA's 539 h). It is reported — medians, sign, cell counts — as a **declared
methodological limitation**.

#### Re-verified after the change, not before

Scorer: `control_bands.csv` **1,232 rows**, `G8.7` **INFO = 88**, `G8.5` **PASS = 88**, `G8.6`
**PASS = 88**, **0 gate-cell FAILs over 88 cells**. Selftest: **29 ok / 0 FAILED**, **12 of 12
injections HIT**, no no-ops, baseline clean, **coverage clause PASS**. 🟢 **No campaign cell was
re-run and no measured number changed** — the ruling changes how two gates are *reported*, not what
EnergyPlus produced. 🟢 `prereg.md` untouched, md5 `e4243e07cdd80c9c846b91f40e3e8c45`.

⚪ `G8.7` being INFO carries **no coverage obligation** under the coverage clause — the clause binds
gates that scored PASS, and an INFO row makes no claim to falsify. That is stated so the drop from the
injection battery is a declaration rather than a gap.

---

### 2026-08-25 (late, second addendum) — 🟢 **WORK ITEM 8.4: THE LAST TWO UNEVALUATED GATES WERE EACH SEEN FAILING — AND THE PROBING CAUGHT A GATE THAT ONLY LOOKED AS THOUGH IT HAD BEEN.**

| gate | good arm | 🔴 broken arm | verdict |
|---|---|---|---|
| `G8.8` | `f = 0.00` vs `f = 1.00`, properly injected → result files differ (`22677b61…` / `23ab0413…`) | a scenario **declared `f = 0.50`, wired to `f = 1.00`'s schedule file** | 🟢 PASS then 🔴 **FELL** |
| `G8.9` | key over every input that can change the result: MISS → **HIT** → schedule changed → key moved → **re-ran** | key over **the cell name alone** | 🟢 PASS then 🔴 **FELL** |

⚪ **The vacuity guard on `G8.9` is asserted first.** A cache that never hits would make "the cell
re-ran" true of everything, so the HIT is proved before the invalidation is tested. ⚪ **`G8.8` is
scored only over runs that actually executed**, so on the stale arm it reports `NOT_EVALUATED`, not a
pass — which is what keeps the two gates independent, as the perturbation table above requires.

#### 🔴 `FINDING 126` — the gate that was recorded as seen firing, and could not fire

`G8.13`'s parser read **only the last comma-field**. That is where `Interpolate to Timestep` sits on a
`Schedule:File` written *without* the optional `Minutes per Item` — the shape 8.3's injection `I9`
used. On a **real** 9-field object the `Yes` was invisible and the row read PASS.

| IDF shape | before | after |
|---|---|---|
| control, `Schedule:Constant` only | `NOT_EVALUABLE` | unchanged |
| 8.4's injected 9-field object, `No` | PASS | unchanged |
| 🔴 8.4's injected 9-field object, `Yes` | 🔴 **PASS** | 🟢 **FAIL** |
| 8.3's `I9`, 8-field, `Yes` | FAIL | unchanged |

Fixed **additively** — read by position for `Schedule:File`, and strip comments **per line** before
splitting on commas (IDF writes `value,  !- Field Name`, so the comment belongs to the field *before*
the comma). 🟢 **Nothing that used to fire stopped firing**, and a new injection **`I13`** covers the
shape the real injector writes. Battery: **13 of 13 HIT**.

#### `FINDING 127` — `G8.10`'s note said "all zero" while the gate was closing on 97.99 GJ

`worst_fuel` was assigned only when a deviation *exceeded* the running worst, so an exact 0.0 left it
empty and the note read `worst fuel: all zero` on all 88 cells. What was compared on every cell:
**District Heating Water, 97.99 GJ of end uses against a 97.99 GJ total, at 0.0000 %.** The gate was
live; its note was not. It now counts the fuels **actually** compared and reports `VACUOUS` only when
there are none — because "all zero" and "nothing to compare" are precisely the two readings a vacuity
guard exists to keep apart.

#### Re-verified after the change, not before

Probes **PASS, 10 of 10 checks, 6 runs, 7.2 s, 0 severe**. 8.3 re-scored → **1,232 rows, 0 gate-cell
FAILs over 88 cells**. Selftest → **29 ok, 0 FAILED, 13 of 13 injections HIT**, no no-ops, baseline
clean, coverage clause PASS. 🟢 **No campaign cell was re-run and no measured number changed**; the
`G8.10` note text changed on 88 rows, its value, threshold and verdict did not. 🟢 `prereg.md`
untouched, md5 `e4243e07cdd80c9c846b91f40e3e8c45`. Record:
`docs/2026-08-25_item-8.4_the-two-probes.md`.
