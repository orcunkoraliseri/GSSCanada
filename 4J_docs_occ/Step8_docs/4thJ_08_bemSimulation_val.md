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
| **G8.1** | NMBE, monthly | ±**5 %** | ASHRAE Guideline 14 🔴 *(2026-08-20 `FINDING 44`: no reference series is defined, and the parent forbids Guideline 14 as a bar. See `D-S8-1`.)* |
| **G8.2** | NMBE, hourly | ±**10 %** | ASHRAE Guideline 14 🔴 *(2026-08-20 `FINDING 44`: no reference series is defined, and the parent forbids Guideline 14 as a bar. See `D-S8-1`.)* |
| **G8.3** | CV(RMSE), monthly | **15 %** | ASHRAE Guideline 14 🔴 *(2026-08-20 `FINDING 44`: no reference series is defined, and the parent forbids Guideline 14 as a bar. See `D-S8-1`.)* |
| **G8.4** | CV(RMSE), hourly | **30 %** | ASHRAE Guideline 14 🔴 *(2026-08-20 `FINDING 44`: no reference series is defined, and the parent forbids Guideline 14 as a bar. See `D-S8-1`.)* |
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
| **G8.16** 🔴 Fold correctness | Every cell's `fold` field names the fold that **held out that cell's country**. Count of cells simulating a country under another country's fold: **0**. Checked against the Step 7 schedule provenance, not against the cell's own filename |
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
| 🔴 **Drive one country's cells with a fold that did not hold that country out** | **G8.16** | G8.12, G8.14 — *the schedule is a real Step 7 artefact with a correct md5 and a complete manifest; only the fold is wrong, and the energy result would look entirely normal* |
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
