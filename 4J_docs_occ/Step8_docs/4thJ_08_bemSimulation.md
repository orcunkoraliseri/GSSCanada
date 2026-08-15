# Step 8 — BEM / UBEM simulation

### 4J HETUS LLM pipeline. Implementation specification.
#### Parent: `../4thJ_00_HETUS_LLM_Pipeline.md` Step 8. Validation: `4thJ_08_bemSimulation_val.md`

---

## STATUS

**OPEN. Scoped by `RL13`. Nothing built.**

---

## AIM

Carry generated schedules through EnergyPlus on European residential archetypes, so the paper ends in
simulated energy rather than in a metric table.

---

## 🔴 THERE IS NO EUROPEAN DOE PROTOTYPE LIBRARY, AND THAT IS NEW SCOPE

`RL13`'s most consequential finding. Unlike the US, there is **no official library of European
residential EnergyPlus models.** TABULA and EPISCOPE distribute parameter tables, Excel workbooks and
national typology brochures — U-values, geometry parameters, construction periods, HVAC efficiencies.
**Not simulation-ready models.**

**So we build the archetype IDFs ourselves**, from TABULA parameters via OpenStudio, or generated
through TEASER. Three to five days, **on the critical path**, and it was not in the original scope.

It is also limitation F2: the envelope models are our construction and carry our uncertainty.

---

## 🔴 THE BASELINE WE BENCHMARK AGAINST CHANGED, AND FOR A GOOD REASON

The plan was to benchmark against the EN 16798-1 Annex C default residential schedule.
**`RL13` could not open EN 16798-1, said so, and did not reconstruct it.** That is the negative
control working exactly as intended, and it is worth more than a plausible-looking table would have
been: a reconstructed standard schedule would have been undetectable downstream and would have
propagated into the baseline we benchmark against.

So the foil becomes the **open** one that national regulation actually mandates: **ISO 13790 Annex G
Table G.12 and Italy's UNI/TS 11300-1, both specifying a flat continuous 4.0 W/m² internal gain.**

**This is a better foil.** A flat continuous gain is precisely what an activity-resolved diary should
beat, and it is what a practising European energy modeller actually uses. If the standard's own text
is needed later, it is **bought through the library, not reconstructed.**

---

## 🔴 THE UNINJECTED CONTROL RUNS FIRST. ALWAYS.

**The single most expensive lesson of 3J.** The office EUI gate failed, and **eight simulation
campaigns** were spent before it was traced out of the occupancy model entirely: the **uninjected**
control run, with no schedules applied at all, already sat below the band floor — 85.45 against a
floor of 100.

**A gate that no untreated control can pass is measuring the band, not the model.**

So: **run the uninjected control before any injected cell**, in every archetype and every climate, and
record where it sits relative to every band. If a band fails on the control, that band is reported as
a **band-applicability limitation** and its value is **not moved to make it pass.**

---

## THE CAMPAIGN

Axes: **country × construction period × day type × scenario.**

🔴 **Country means the country's OWN fold, and this is four populations rather than sixteen.** Decision
11 produces four adapters, and each country's schedules come from **the fold that held that country
out** — that is the whole point: the diaries driving Italy's buildings must come from the model that
never saw Italy. Simulating every country under every fold would be a 4× larger campaign whose extra
cells answer no question the paper asks, and mixing folds within one country's cells would quietly turn
a transfer result into a held-in one.

**Written into every cell's `manifest.json` as an explicit `fold` field**, so that a schedule file
cannot be read under the wrong fold's name — nothing in the schedule numbers themselves would say.

🔴 **Two mandatory probes before any campaign cell**, both inherited from Leg-2 and Leg-3 at real cost:

1. **Scenario differentiation.** Byte-identical outputs across scenarios is an **automatic FAIL**. The
   Leg-2 People-field bug passed every input-side check and was only visible output-side.
2. **Stale-output guard.** A wiring fix invalidates prior completions, so any skip-if-done logic must
   be invalidated with it.

---

## WHY THE DOWNSTREAM RESULT WILL MATTER

Published European stock studies put the sensitivity at **15 to 50 % on annual space heating demand**
and **100 to 300 % on dwelling peak electrical demand** when static standard schedules are replaced by
stochastic occupant profiles. **That is the size of the effect this paper is manipulating**, and it is
why the building-science half is not decorative.

---

## WORK ITEMS

### 8.1 — Build the archetype IDFs

From TABULA parameters, per country, per construction period, via OpenStudio or TEASER.

* Every parameter carries its TABULA table reference.
* 🔴 **Record what TABULA does not give us and what we assumed instead.** An assumed value that is not
  written down becomes a fact the moment someone reads the code.

**Output:** `outputs_step8/archetypes/*.idf` + `archetype_parameter_provenance.md`.

### 8.2 — Weather

TMY files per country, per climate zone. Recorded by name and source. 🔴 **The weather file is part of
the result**, and 2J shipped a table that had lost its weather-file column.

### 8.3 — The uninjected control campaign

**First. Before any injected cell.** Every archetype, every climate, no schedules applied.

**Output:** `outputs_step8/control/` + a table of where the control sits relative to every band.

### 8.4 — The two probes

Scenario differentiation and the stale-output guard, both run before the campaign and both **seen
firing** on a deliberately broken cell.

### 8.5 — The injected campaign

One cell per (country × period × day type × scenario). Each cell writes a `manifest.json` recording:

* the schedule file md5 and its Step 7 provenance, **including the `fold` the schedule came from**;
* the IDF md5;
* the weather file name and md5;
* the EnergyPlus version **and build hash**;
* 🔴 **the platform, measured at run time, never inherited from another cell's manifest.**

> A provenance field can only be tested by changing the thing it claims to record. In 3J an inherited
> `PLATFORM` field was accidentally correct on the only platform ever run, and 112 manifests claimed a
> value nothing had measured.

### 8.6 — Aggregate

Per-archetype EUI, monthly and hourly profiles, peak magnitude and timing.

---

## OUTPUTS AND INTERFACES

| Artefact | Consumed by |
|---|---|
| `outputs_step8/control/` | Step 8 validation — **read before any injected result is quoted** |
| `outputs_step8/cells/<cell>/manifest.json` | Step 8 validation, reproducibility |
| `outputs_step8/agg_annual.csv` | Step 8 and Step 9 scoring |
| `outputs_step8/archetype_parameter_provenance.md` | Limitation F2; the methods section |

---

## HOW IT RUNS

`sbatch`, `ps`, `-t 7-00:00:00`. EnergyPlus is CPU-bound; no GPU. One cell per task, array jobs.
`/speed-scratch` purges after 90 days — **copy final artefacts off.**

---

## WHAT BLOCKS THIS STEP

Step 7's schedules, and 🔴 **open decision 14**: without a chaining rule there is no annual schedule
to run, and if the chaining sensitivity turns out to exceed 25 % on peak demand, this whole campaign
is measuring the chaining convention.

**What this step blocks:** Step 9.

---

## DEFINITION OF DONE

1. Archetype IDFs built, every parameter traced to TABULA, every assumption written down.
2. Uninjected control campaign complete **and read** before any injected result is quoted.
3. Both probes run and **seen firing**.
4. Injected campaign complete, every cell with a full manifest whose execution fields were measured.
5. All Step 8 gates PASS and each has been seen failing.

---

## PROGRESS LOG

Append-only.

### 2026-08-14 — step document created

* 🔴 The order of items 8.3 and 8.5 is not a preference. Reversing it is what cost 3J eight campaigns.

### 2026-08-14 (second entry) — the campaign is bound to the folds

* **"Country" in the campaign axes now means the country's own fold.** Four populations, not sixteen:
  each country's schedules come from the adapter that **held that country out**, which is the entire
  point of decision 11 and was nowhere in this document.
* 🔴 **The failure it prevents leaves no trace in the energy.** A cell driven by the wrong fold has a
  real schedule file, a correct md5 and a complete manifest, and its EUI looks entirely normal — it has
  simply turned a transfer result into a held-in one. **Gate G8.16** checks it against the Step 7
  provenance rather than against the cell's own filename, with **V8.g** so a missing `fold` field FAILs
  instead of finding zero violations.
