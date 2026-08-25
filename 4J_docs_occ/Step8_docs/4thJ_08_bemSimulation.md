# Step 8 — BEM / UBEM simulation

### 4J HETUS LLM pipeline. Implementation specification.
#### Parent: `../4thJ_00_HETUS_LLM_Pipeline.md` Step 8. Validation: `4thJ_08_bemSimulation_val.md`

---

## STATUS

**OPEN. Scoped by `RL13`.** 🟢 **2026-08-21: work item 8.1 has PARAMETER TABLES for all three folds** — `outputs_step8/archetype_parameters_{es,uk,it}.csv` (24 / 36 / 42 archetypes) with `archetype_parameter_provenance.md`. 🟢 **2026-08-21 (afternoon): `D-S8-2` item 5 RULED (c) and PRE-REGISTERED** — the `phi_int` split is a five-level sensitivity `f ∈ {0.00, 0.15, 0.30, 0.50, 1.00}` with `f = 0` as the control, annual mean held at exactly 3.0 W/m² throughout (§9 of the provenance file). The injected campaign is therefore **five times larger**: 102 archetypes × 5 = 510 archetype-runs per weather specification. 🟢 **2026-08-24 (evening): SECTION 6 IS CLOSED — ALL SIX decisions ruled.** Items 1, 3 and 4 were the last three (the header previously said five, which contradicted this file’s own 2026-08-21 entry) and were ruled `1(a)` equal-facade 1:1.5 box, `3(a)` two-layer equivalent, `4a(a)` prefer `Gen`, `4b(a)` merged rows span their declared periods — brief at `Step8_docs/docs/2026-08-24_D-S8-2_items-1-3-4_geometry-layers-archetype-selection.md`. Three new findings, all from measuring the tables rather than quoting them: `FINDING 107` Italy has **0** empty cells (42 rows, 32 cells, 10 duplicates) so 4b was UK-only; `FINDING 108` the 3 missing GB cells sit inside `AB.04-08`’s declared span; `FINDING 109` **all 36 UK archetypes carry zero South and zero North glazing** while ES/IT use all four faces — a country-correlated convention, which is what forced `1(a)`. 🟢 **2026-08-25: items 8.1 AND 8.2 are DONE.** 88 archetype IDFs exist and run; `D-S8-3`(a) made the box reproduce TABULA's wall area (`FINDING 117`); `D-S8-4` closed the weather on a `TMYx.2009-2023` basis with the station selected by measurement against TABULA's own monthly temperatures (`FINDING 118`, `FINDING 119`, 🔴 `FINDING 120` — the station is worth 5–11 % of heating demand). 🟢 **2026-08-25 (late): WORK ITEM 8.3 IS DONE AND THE STEP 8 GATES HAVE RUN FOR THE FIRST TIME.** 88 archetypes × 2 runs, 0 severe errors, **1,232 band rows, 0 gate-cell FAILs**, selftest **29 ok / 0 FAILED**, **12 of 12 injections seen felling their target**, coverage clause PASS. `G8.1`–`G8.4` finally have the reference `D-S8-1`(a) named — an independent re-run — and they read **exactly 0**, so they are tripwires and not accuracy measurements. 🔴 **The campaign's product is `FINDING 121`, not a green board: the uninjected control sits +136.6 % above TABULA's own published `q_h_nd` in Spain and −29.6 % / −36.7 % below it in the UK and Italy — the sign flips by country, 21 of 24 `es` cells above, 32 of 32 `uk` and `it` cells below.** 🔴 `FINDING 122` the simulation timestep is worth −4.1 / +5.6 / −3.7 % and its sign differs by fold; `FINDING 123` EnergyPlus's unruled 18 °C ground default is worth +33.5 / +1.7 / +15.7 %; `FINDING 124` one psychrometric warning belongs to the Torino EPW alone, in all 32 Italian cells and no others; **`FINDING 125` switching `phi_int` off entirely moves heating only +40.5 / +19.7 / +20.1 %, which CAPS the whole occupancy channel below the 15–50 % this document quotes.** 🟢 **2026-08-25 (late, addendum): `D-S8-5` RULED BY THE AUTHOR, both items, and APPLIED.** Item 1 = **(a)**: `G8.7` is reported as **INFO permanently**, with no pass/fail band ever created — EnergyPlus hourly-dynamic against TABULA monthly quasi-steady-state is a model-to-model structural comparison, not a compliance test, so `FINDING 121` is published as a declared methodological limitation instead. Item 2 = **approved**: `D-S8-1`(a) extends **verbatim** to `G8.5` and `G8.6` — reference = the independent re-run, thresholds unmoved at ±15 % and ≤1 h, and the occupancy-driven peak shift 8.5 exists to measure is **reported as an empirical result, not gated against the flat control** (that was the `FINDING 44` inversion). Applied in `tools/4thJ_step8_bands.py`, `tools/4thJ_gates_step8_control.py` and the selftest; scorer re-run gives **`G8.7` INFO = 88, 0 gate-cell FAILs over 88 cells**, selftest **29 ok / 0 FAILED, 12 of 12 injections HIT**. 🟢 **2026-08-25 (late): WORK ITEM 8.4 IS DONE — `G8.8` AND `G8.9` WERE EACH SEEN FAILING.** 6 runs on one archetype, 0 severe, **10 of 10 checks ok**; `G8.8` fell on a scenario declared at `f = 0.50` and wired to `f = 1.00`'s schedule file, `G8.9` fell on a cache key over the cell name alone. The scenario path and cache key are `tools/4thJ_step8_scenario.py`, which 8.5 imports. 🔴 **The probing found three defects the green board was hiding.** `FINDING 126`: `G8.13`'s parser read only the LAST comma-field, so `Interpolate to Timestep = Yes` was **invisible on a real 9-field `Schedule:File`** — 8.3's `I9` used an 8-field shape, which is why the gate looked as though it had been seen firing; fixed additively, new injection `I13` uses the real shape, battery now **13 of 13**. `FINDING 127`: `G8.10`'s note read "worst fuel: all zero" on all 88 cells while the gate was in fact closing District Heating Water at 97.99 GJ vs 97.99 GJ — the note, not the gate, and it now counts the fuels actually compared. `FINDING 128`: the full pre-registered sweep is worth **+1.60 % on annual heating and +10.84 % on peak** with the peak hour one hour earlier — **the occupancy channel is a PEAK channel**, which sharpens `FINDING 125` from a ceiling into a measurement. `FINDING 129`: `f = 0` reproduces the 8.3 control **byte-for-byte**, so `D-S8-2` item 5 (c) held. **8.5, the injected campaign, is next.** 🔴 **Decision 14 (chaining) is still open** and still closes here, on a watt. 🟢 **2026-08-25 (night): WORK ITEMS 8.5 AND 8.6 ARE DONE, AND SO IS DECISION 14's MEASUREMENT. STEP 8's DEFINITION OF DONE IS CLOSED, ALL SIX ITEMS.** The injected campaign is **440 scenario-cells / 4,048 EnergyPlus runs / 0 severe**, scored at **28,161 band rows, 0 gate-unit FAILs**, coverage clause PASS, battery **33 ok / 18 of 18 injections HIT**; **`G8.12` and `G8.16` were evaluated for the first time in this project**, both arms of `G8.12` included, all seen failing. 🔴 **The campaign was built twice.** `FINDING 130`: the diaries were the **Leg-4 pilot**, stamped `NOT REPORTABLE` in their own records, because the schedule emitter had the leg hard-coded and the Leg-5 pools were unreachable. `FINDING 131`: the schedules were emitted on the survey years and wired into a **Sunday**-start `RunPeriod` — `FINDING 99` realised, worth −0.12/−0.04/+0.02 % annual and **+1.27/+0.37/−0.39 % on peak with the sign differing by fold**. `FINDING 132`: the pre-registered “exactly 3.0 W/m²” held in the generator and not in the artefact. All three now have guards (`V8.i` among them) that were **seen firing on the exact artefact that was about to ship**. 🔴 **`FINDING 133`: the occupancy channel is a PEAK channel and the annual channel is empty** — median **+1.82 / −0.04 / +0.06 %** annual against **+6.38 / +4.54 / +3.96 %** peak, which corrects `FINDING 128`'s magnitudes. 🔴 **`FINDING 134`: on annual heating the effect is SMALLER than the between-diary spread in all three folds**, so no annual occupancy claim survives; on peak it is 1.7–2.0× the spread and does. `FINDING 135`: the annual peak's hour of day never moves — it is the thermostat recovery hour — while the mean diurnal profile shifts `uk` 5 → 7 and `it` 6 → 7 at `f ≥ 0.50`; the effect is monotone in dwelling class in all three folds (`AB` +10.13/+8.69/+5.82 % against `TH` +4.29/+3.06/+2.51 %). 🟢 **`FINDING 136`: decision 14's trigger is not approached.** 9,000 more runs: the whole chaining convention moves peak demand **0.178 / 0.075 / 0.239 %** against `G7.18`'s **25 %**, the seed spread beats the rule spread on every metric in every fold, and the occupancy effect is **17–60×** the convention's entire range — so this campaign is **not** measuring the chaining convention. 🟢 **AND THE AUTHOR RULED IT THE SAME NIGHT: DECISION 14 IS CLOSED — `independent`, seed 1, adopted as the standard convention for every published Step 8 and Step 9 dataset, with the empirical null itself as the deliverable. It was the last open decision in the project. No re-run, no pipeline change.** ⚪ `prereg.md` md5 `e4243e07cdd80c9c846b91f40e3e8c45` untouched.

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

🔴 **Country means the country's OWN fold, and this is THREE populations rather than nine.** Decision
11 as amended by decision 16 (2026-08-15, France excluded) produces **three** adapters, and each
country's schedules come from **the fold that held that country out** — that is the whole point: the
diaries driving Italy's buildings must come from the model that never saw Italy. Simulating every
country under every fold would be a 3× larger campaign whose extra cells answer no question the paper
asks, and mixing folds within one country's cells would quietly turn a transfer result into a held-in
one. *(Was four populations rather than sixteen. **`G8.16`'s threshold is unchanged** — it asserts each
cell was driven by the fold that held its country out, which is a per-cell identity and does not depend
on how many folds there are.)*

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

✅ **DONE 2026-08-24, REBUILT 2026-08-25 under `D-S8-3`(a).** 88 IDFs, 26 of 26 selftest checks pass,
all 88 run in EnergyPlus with zero severe errors. 🔴 The aspect ratio is **no longer 1 : 1.5** — it is
solved per archetype from TABULA's wall area, and **38 of 88 fall back** to 1 : 1.5 for two recorded
reasons. Read `FINDING 117` before quoting any envelope or `H_transmission` number: the
country-correlated artefact of `FINDING 110` is reduced from 19.1 pp to 6.1 pp, **not removed**, and
what survives sits entirely in the fallbacks (`it`/`AB` 0.656, `uk`/`AB` 1.137).

From TABULA parameters, per country, per construction period, via OpenStudio or TEASER.

* Every parameter carries its TABULA table reference.
* 🔴 **Record what TABULA does not give us and what we assumed instead.** An assumed value that is not
  written down becomes a fact the moment someone reads the code.

**Output:** `outputs_step8/archetypes/*.idf` + `archetype_parameter_provenance.md`.

### 8.2 — Weather

✅ **DONE 2026-08-25 under `D-S8-4`.** TMY files per country, per climate zone. Recorded by name
and source. 🔴 **The weather file is part of the result**, and 2J shipped a table that had lost its
weather-file column — so it is recorded in `outputs_step8/weather_manifest.csv` with the station,
WMO number, coordinates, source URL, zip md5 and EPW md5, and a gate re-reads all of it from the
bytes.

`TMYx.2009-2023` for all three folds — the one published window containing every original
fieldwork period. One EPW per fold, one climate region per fold, the station **selected by scoring 44
candidates against TABULA's own published monthly temperatures**: `es` Valencia.Viveros 082850,
`uk` Birmingham.AP 035340, `it` Torino.Venaria 160600. 🔴 **`FINDING 120`: the station is worth
5 to 11 % of heating demand and the UK margin that picked it is 0.002 K**, so no cross-fold
comparison of absolute demand is safe to ±10 % and the within-fold reporting rule is what stands
between the paper and that error.

### 8.3 — The uninjected control campaign

✅ **DONE 2026-08-25 (late).** First, before any injected cell, as the order requires. **88
archetypes × 176 EnergyPlus runs**, every cell on its own fold's `D-S8-4` EPW, no schedules
applied — `f = 0` is an endpoint of the pre-registered `D-S8-2`(c) sweep, so **no new model was
built and the 88 IDFs ran byte-identically to the 8.1 artefacts**. Zero severe errors. Every cell run
**twice**, in a fresh process and a different directory, because `D-S8-1`(a) made `G8.1`–`G8.4`
reproducibility gates whose reference did not exist until now.

🔴 **Read `FINDING 121` before quoting any Step 8 number.** Against TABULA's own published
`q_h_nd` — an as-modelled reference of the same quantity that `FINDING 44` never examined, and
which covers 86 of 86 archetype codes — the control sits **+136.6 % (`es`), −29.6 %
(`uk`), −36.7 % (`it`)**. The sign flips by country and the split is total. Mechanism measured
for Spain: TABULA counts gains over a **539-hour** heating season, EnergyPlus heats for **2,901**.

🔴 **`FINDING 125` caps what 8.5 may claim on annual heating.** 🟢 `D-S8-5` is **ruled**: `G8.7`
is INFO permanently and no band is created (item 1 (a)); `G8.5`/`G8.6` are reproducibility gates
against the re-run under `D-S8-1`(a) (item 2), and the peak shift is reported rather than gated.

**Output:** `outputs_step8/control/` (88 cells + 88 re-runs), `control_annual.csv`,
`control_monthly.csv`, **`control_bands.csv` (1,232 rows — the table of where the control sits
relative to every band)**, `control_gate_board.json`, `control_diagnostics.json`,
`tabula_reference.csv`. Record:
`Step8_docs/docs/2026-08-25_item-8.3_uninjected-control-campaign.md`.

### 8.4 — The two probes

Scenario differentiation and the stale-output guard, both run before the campaign and both **seen
firing** on a deliberately broken cell.

🟢 **DONE, 2026-08-25 (late).** 6 EnergyPlus runs on one archetype, 0 severe, **10 of 10 checks ok**.
`G8.8` fell on a scenario declared at `f = 0.50` and wired to `f = 1.00`'s schedule file; `G8.9` fell
on a cache key over the cell name alone. The scenario path and its cache key live in
`tools/4thJ_step8_scenario.py`, which **8.5 imports rather than re-implements**. 🔴 The probing found
three defects a green board was hiding — `FINDING 126` (`G8.13` could not see its own violation on a
real `Schedule:File`), `FINDING 127` (`G8.10`'s note read "all zero" while the gate closed on
97.99 GJ) and `FINDING 128` (the sweep is worth **+1.6 %** on annual heating and **+10.8 %** on peak).
Record: `Step8_docs/docs/2026-08-25_item-8.4_the-two-probes.md`.

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

🟢 **DONE, 2026-08-25 (night).** 88 archetypes × 5 levels of `f` × **10 generated diaries** +
440 independent re-runs = **4,048 EnergyPlus runs, 659 s, 0 severe**. Scorer **28,161 band rows,
0 gate-unit FAILs**, coverage clause PASS; battery **33 ok / 0 FAILED, 18 of 18 injections seen
felling their target**. **`G8.12` and `G8.16` are evaluated for the first time in this project**, both
with an assignment arm as well as a value arm and both seen failing. 🔴 Nothing pre-registers
WHICH diary drives which archetype, so the campaign **measures that free parameter instead of
choosing it** (`FINDING 120`'s precedent): every cell runs an ensemble and every table carries the
between-diary spread beside the effect. Record:
`Step8_docs/docs/2026-08-25_items-8.5-8.6_injected-campaign-and-aggregate.md`.

🔴 **The campaign was built twice, and the first build was wrong in two ways that leave no
trace in the energy.** `FINDING 130`: the diaries were the **Leg-4 pilot**, stamped
`LEG-4 PILOT -- NOT REPORTABLE` in their own records, because the schedule emitter had the leg
hard-coded — the Leg-5 pools had been on disk since 2026-08-24 and no code path could reach them.
`FINDING 131`: the schedules were emitted on the survey years (`es` 2010, a **Friday** start) and
wired into the 8.1 IDFs' **Sunday**-start `RunPeriod`, so every synthetic Saturday landed on a
Thursday for fifty-two weeks — `FINDING 99` realised. Both fixed additively, both now **guarded**,
and both guards **seen firing on the exact artefact that was about to ship**. `FINDING 132`: the
pre-registered "annual mean exactly 3.0 W/m²" was true of the generator and false of the artefact by
4.01e-07 relative, because the multiplier was written at `%.6f`.

### 8.6 — Aggregate

Per-archetype EUI, monthly and hourly profiles, peak magnitude and timing.

🟢 **DONE, 2026-08-25 (night).** `agg_by_fold.csv`, `agg_by_class.csv`, `agg_monthly.csv`,
`agg_diurnal.csv`, `agg_peak_day.csv`, `step8_aggregate.json`. 🔴 The pre-registered reporting
rule is **enforced in code**: every quantity is a mapping over the whole `f` grid, the tool refuses to
write anything if the campaign does not carry all five levels, and no code path in it produces a
single-`f` scalar.

🔴 **`FINDING 133` — the occupancy channel is a PEAK channel and the annual channel is empty.**
Median over cells at `f = 0 → 1`: annual **+1.82 / −0.04 / +0.06 %** (`es`/`uk`/`it`), peak
**+6.38 / +4.54 / +3.96 %**. This **corrects `FINDING 128`**, whose +1.60 % / +10.84 % were measured
on the Leg-4 pilot and the misaligned calendar; the same cell re-reads +0.18 % / +7.70 %.
🔴 **`FINDING 134` — on annual heating the effect is smaller than the between-diary spread in
all three folds** (es 1.82 vs 1.88, uk −0.04 vs 0.36, it 0.06 vs 0.16), and on peak it is 1.7–2.0×
the spread in all three. **No annual occupancy claim survives; the peak claim does, with its spread
attached.** `FINDING 135`: the annual peak's **hour of day never moves** (7 in every fold at every
`f` — it is the thermostat recovery hour) while its **date** moves by up to 7,824 h between diaries;
what does move is the mean **diurnal** profile, `uk` 5 → 7 and `it` 6 → 7 at `f ≥ 0.50`. The effect is
**monotone in dwelling class in all three folds**: `AB` +10.13 / +8.69 / +5.82 % against `TH`
+4.29 / +3.06 / +2.51 %.

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

🟢 **MEASURED, 2026-08-25 (night). `FINDING 136`: it does not, and it is not close.**
`tools/4thJ_step8_chaining.py`, **9,000 EnergyPlus runs, 1,530 s, 0 severe** — three folds × the six
pre-registered rule points (`independent`, `habit` at ρ = 0.25/0.50/0.75/0.90, `static`) × five seeds
× 100 dwellings, one archetype per fold, `f = 1.00` so the number is an **upper bound**. The whole
chaining convention moves aggregate coincident peak power by **0.178 % (`es`) / 0.075 % (`uk`) /
0.239 % (`it`)** against `G7.18`'s **25 %** trigger. 🔴 **And the pre-registered null fired: the
spread across SEEDS within a rule exceeds the spread between RULES on every metric in every fold**
(peak ratios 0.176 / 0.315 / 0.404), which the validation document says in advance means *"the
experiment has told us nothing about chaining, and the deliverable is that finding, not a chosen
rule."* The occupancy sweep this campaign reports is **17–60× larger** than the convention's entire
range, so **the campaign is not measuring the chaining convention**. ⚪ Deciding the rule is still
the author's; the watt the `D-S7-6` ruling said it closes on now exists. Record:
`Step8_docs/docs/2026-08-25_decision-14_chaining-on-a-watt.md`.

🟢 **RULED BY THE AUTHOR 2026-08-25 (night) — DECISION 14 IS CLOSED, and it was the
last open decision in the project.** The convention is **`independent`, seed 1**, adopted as the
standard for every published Step 8 and Step 9 energy dataset. The reason given is the empirical
null itself: the whole rule axis moves peak demand **0.075–0.239 %** against `G7.18`'s **25 %**,
the seed spread beats the rule spread on every metric in every fold, and the occupancy effect is
**17–60×** the convention's entire range. 🔴 **The null is the deliverable and is to be stated
as such in the manuscript** — building thermal and peak response is insensitive to the day-to-year
chaining rule relative to sampling noise. **No re-run, no pipeline change, no recalculation.**
Ruling recorded in §8 of `Step8_docs/docs/2026-08-25_decision-14_chaining-on-a-watt.md`.

⚪ **Nothing in this step is waiting on a person any more.**

**What this step blocks:** Step 9.

---

## DEFINITION OF DONE

1. ✅ **DONE 2026-08-25.** Archetype IDFs built, every parameter traced to TABULA, every
   assumption written down — `outputs_step8/archetypes/*.idf` (88),
   `archetype_parameter_provenance.md`, `archetype_idf_manifest.csv`. 🔴 Built does not mean the
   geometry is faithful: `FINDING 110` is reduced by `D-S8-3`(a), not closed, and `FINDING 117`
   records the 6.1 pp of country-correlated residue that remains inside the LOCO channel.
2. ✅ **DONE 2026-08-25.** Weather acquired, selected by measurement and recorded by name, source and md5 — `outputs_step8/weather/*.epw` (3),
   `weather_manifest.csv`, `weather_selection_report.json` (all 44 candidates, the losing 41 included). 🔴 Acquired does not mean neutral: `FINDING 120` puts ±5–11 % of country-correlated heating demand on the station choice.
3. ✅ **DONE 2026-08-25 (late).** Uninjected control campaign complete and read — 88 cells, 176 runs, `outputs_step8/control/`, band position in `control_bands.csv`. 🔴 Complete does not mean agreeing: `FINDING 121` records a country-correlated, sign-flipping 166 pp gap to TABULA's own answer, and under `G8.0` that is a band-applicability limitation, not a band to move.
4. ✅ **DONE 2026-08-25 (late).** Both probes run and **seen firing** — `G8.8` fell on a scenario
   declared at `f = 0.50` and wired to `f = 1.00`'s schedule file, `G8.9` on a cache key over the
   cell name alone. `Step8_docs/outputs_step8/probes_step8.json`, re-run clean on the corrected
   artefacts.
5. ✅ **DONE 2026-08-25 (night).** Injected campaign complete — 440 scenario-cells, 4,048 runs, every
   cell with a full manifest whose execution fields were measured at run time. 🔴 Complete does not
   mean the campaign the first build would have produced: `FINDING 130` (the diaries were the
   NOT-REPORTABLE Leg-4 pilot) and `FINDING 131` (the schedule calendar was not the model's) were
   both caught before anything was quoted, and both now have a guard that has been seen firing.
6. ✅ **DONE 2026-08-25 (night).** All Step 8 gates PASS and each has been seen failing — 8.3's
   battery 13 of 13, 8.5's battery 18 of 18, coverage clause PASS on both boards. 🔴 A green board
   is not the product: `FINDING 121`, `125`, `130`–`135` are.

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

### 2026-08-20 — 🟢 **`RL24` VETTED. WORK ITEM 8.1 IS UNBLOCKED, AND MY OWN EARLIER CONCLUSION WAS WRONG: TABULA PUBLISHES AN OPEN STATIC WORKBOOK. 22 OF 22 CONSTRUCTION-PERIOD BANDS VERIFIED AGAINST THE FILE.**

Earlier the same day this document recorded that TABULA *"serves its data through an ExtJS back-end,
not a documented export"*, and that scraping it would put unverifiable numbers into a provenance file.
**That was correct about the web tool and wrong about TABULA.** `RL24` found the static master
workbook, which the web tool is merely a front end for.

#### What was verified, by download, not by reading the report

| claim | check run here | verdict |
|---|---|---|
| `tabula-values.xlsx` is downloadable | `curl` → **HTTP 200, 4,028,656 B**, `application/…spreadsheetml.sheet`, md5 `7347b2cae3c4d9f5ce78221e9d5fb832` | ✅ |
| `tabula-calculator.xlsx` is downloadable | **HTTP 200, 34,383,251 B** | ✅ |
| ES / GB / IT national brochures | **HTTP 200**, 10.9 MB / 3.1 MB / 5.0 MB, all `application/pdf` | ✅ |
| the workbook contains sheet `Tab.ConstrYearClass` | opened with `openpyxl`: **65 sheets, the sheet exists** | ✅ |
| Spain has **6** construction periods | read from the file: `ES.01`–`ES.06` | ✅ |
| Great Britain has **8** | `GB.01`–`GB.08` | ✅ |
| Italy has **8** | `IT.01`–`IT.08` | ✅ |
| the period boundaries themselves | **all 22 year-boundaries match `RL24` exactly** | ✅ |

**The verbatim bands, read from `Tab.ConstrYearClass`, which are now the campaign's construction-period
axis and must be quoted from here and not re-typed:**

| Spain | Great Britain | Italy |
|---|---|---|
| `ES.01` ≤1900 *XIX century* | `GB.01` ≤1918 | `IT.01` ≤1900 |
| `ES.02` 1901-1936 *Beginning of the century* | `GB.02` 1919-1944 | `IT.02` 1901-1920 |
| `ES.03` 1937-1959 *Civil war* | `GB.03` 1945-1964 | `IT.03` 1921-1945 |
| `ES.04` 1960-1979 *Improvement in the Spanish economy* | `GB.04` 1965-1980 | `IT.04` 1946-1960 |
| `ES.05` 1980-2006 *CTE-79* | `GB.05` 1981-1990 | `IT.05` 1961-1975 |
| `ES.06` ≥2007 *CTE 2006* | `GB.06` 1991-2003 | `IT.06` 1976-1990 |
| | `GB.07` 2004-2009 | `IT.07` 1991-2005 |
| | `GB.08` ≥2010 | `IT.08` ≥2006 |

🔴 **One small correction to `RL24`, from the file itself.** It gives `ES.05` as
*"1980-2006 (NBE-CT-79)"*. The workbook's own label is **`CTE-79`**. `NBE-CT-79` is the historically
correct name of the Spanish standard and `RL24` is arguably being helpful, but **`archetype_parameter_
provenance.md` must carry the label the file carries**, or a later reader cannot match our table to the
source. Cite `CTE-79`, and note the historical name separately if it is worth saying.

🔴 **`GB` is Great Britain, not the United Kingdom.** TABULA's country code is `GB`. Northern Ireland
is outside it. That is a limitation for a fold labelled `uk`, and it must be stated rather than
absorbed silently — the same class as the D-S6-2 wave gap.

#### What this changes

* **Work item 8.1 is unblocked and needs no author decision on the source.** The route is: download
  `tabula-values.xlsx`, pin its md5, read `Tab.ConstrYearClass`, `Tab.Building.Constr`,
  `Tab.U.Class.Constr`, `Tab.U.Class.Window`, `Tab.System.*`, and cite sheet plus row code per
  parameter. That satisfies *"every parameter carries its TABULA table reference"* by construction.
* **The 65-sheet structure is itself the answer to "what does a row contain".** `RL24`'s B16 named
  `Calc.Set.Building` in `tabula-calculator.xlsx`; the 34 MB calculator was **not** opened here, so
  that specific claim is **UNVERIFIED** and is recorded as such. The 4 MB values file was opened and
  is verified.
* 🔴 **B17 — what TABULA does not supply — was NOT verified** and is the item that matters most for
  `archetype_parameter_provenance.md`'s honesty clause. `RL24` lists sub-hourly occupant schedules,
  appliance draw profiles, DHW tapping series, window-opening behaviour, thermostat setbacks and 3D
  zoning geometry. **Plausible and consistent with a steady-state monthly-balance method, but check it
  against the workbook before writing it down as fact** — the file is on disk now and the check is one
  script.
* **`RL24`'s licence claim (IEE / IWU, redistribution of derived tables permitted with attribution)
  was NOT independently verified.** Quoted terms were not located in this session. 🔴 **Verify before
  any derived parameter table is published**, not before it is used internally.

#### `D-S8-1` is unaffected

`FINDING 44` stands: `G8.1`–`G8.4` still name no reference series, and nothing in `RL24` supplies one.
`RL24` confirms there is no library of European residential EnergyPlus models and no measured dataset
for our archetypes, which **strengthens** the case against Guideline 14 as a bar and therefore against
option (b). The recommendation remains **(a)**, recast as reproducibility gates.

---

### 2026-08-21 — 🟢 **WORK ITEM 8.1 HAS PARAMETER TABLES FOR ALL THREE FOLDS, AND B16 IS VERIFIED.** 🔴 **`FINDING 57`: THE ARCHETYPES USE THE *EU* BOUNDARY CONDITIONS, NOT THE NATIONAL ONES — SO `phi_int` IS 3.0 W/m² IN ALL THREE FOLDS AND THE NIGHT-SETBACK FACTOR IS NOT 1. 🔴 `FINDING 58`: TABULA'S `GB` TYPOLOGY IS *ENGLAND*.**

Full provenance: `outputs_step8/archetype_parameter_provenance.md`. Builder:
`tools/4thJ_step8_tabula.py`. Outputs: `archetype_parameters_{es,uk,it}.csv` — 24 / 36 / 42 archetypes.
Local, no cluster.

#### 🟢 `RL24`'s B16 is VERIFIED, and the route recorded on 2026-08-20 was one workbook short

`tabula-values.xlsx` re-downloaded: md5 `7347b2cae3c4d9f5ce78221e9d5fb832`, **identical to the digest
verified on 2026-08-20**. But every sheet of it was searched for a building-type code
(`<CC>.<region>.<SFH|TH|MFH|AB>.…`) and **ZERO sheets carry one**. `Tab.Building.Constr`, which the
route named, holds wall/roof/ceiling **assemblies** (`ES.Wall.ReEx.01.01`), not archetypes.

The archetypes are only in `tabula-calculator.xlsx` — the 34 MB file the 2026-08-20 entry explicitly
recorded as **NOT opened**, with B16 marked UNVERIFIED. It is opened now, md5
`c99ddc9ffcb6dc0ae7391273d9619e37` pinned for the first time: `Calc.Set.Building`, **3,287 data rows ×
333 columns**, one row per building variant. 🟢 **B16 confirmed.**

#### 🟢 The 22 construction-year bands re-derived independently, and all 22 match

Read from `Tab.ConstrYearClass`. Every boundary equals the table recorded on 2026-08-20.
⚪ **The descriptive labels are SPAIN-ONLY** and live in `Remark_ConstructionYearClass`, not
`Description_…` (which is empty for all 22 rows). GB and IT carry **no label at all**, so there is
nothing to quote for them. `CTE-79` confirmed as the file's own wording for `ES.05`; `NBE-CT-79`
appears nowhere in the workbook.

#### 🔴 `FINDING 57` — the archetypes point at `EU.SUH`/`EU.MUH`, and this reverses the first reading

`Tab.BoundaryCond` publishes national rows AND an EU cross-country pair. Reading the national rows
first suggested "no night setback anywhere, and the three countries differ a lot". **Both halves of
that are wrong for our tables.** `Code_BoundaryCond` on all 102 kept archetype rows takes exactly two
values — `EU.SUH` for `SFH`/`TH`, `EU.MUH` for `MFH`/`AB` — in **all three folds**.

| | `EU.SUH` | `EU.MUH` | `ES.SUH` | `GB.Gen` | `IT.SUH` |
|---|---|---|---|---|---|
| `theta_i` °C | **20** | **20** | 20 | 21 | 20 |
| `F_red_htr1` | **0.9** | **0.95** | 1 | 1 | 1 |
| `F_red_htr4` | **0.8** | **0.85** | 1 | 1 | 1 |
| `n_air_use` 1/h | **0.4** | **0.4** | 0.4 | 0.59 | 0.3 |
| `phi_int` W/m² | **3** | **3** | 3 | 4 | 2.8 |
| `c_m` Wh/(m²K) | **45** | **45** | 45 | 32.79 | 87 |

Three consequences, and none of them is cosmetic:

1. 🔴 **`phi_int` = 3.0 W/m² in every fold.** One number, no split into occupants / appliances /
   lighting, no time profile. **It is the only time-invariant load TABULA has, therefore it is the
   injection point for the whole campaign** — the uninjected control is the run that keeps it, and
   §8.5's injected campaign is the run that replaces it. Nothing else in TABULA can be injected into.
2. 🔴 **There IS an intermittent-heating reduction** (0.9/0.8 and 0.95/0.85), applied as a **scalar on
   the transmission coefficient, not a schedule**, identical across the folds. An EnergyPlus model that
   implements a real night-setback schedule stops computing TABULA's quantity, and its difference from
   TABULA is then partly the setback rather than the occupancy.
3. 🟢 **Keeping the EU set removes a confound.** On it, every non-geometric boundary condition is
   identical across `es`/`uk`/`it`, so cross-country differences come from geometry, U-values and
   weather alone. The national set would add a 1 °C set-point difference and a factor-two air-change
   difference, **both country-correlated, i.e. confounded with the LOCO signal itself**. Switching
   would be a basis change and is **not taken**; it is recorded as an available sensitivity, never a
   mixture. The builder refuses to run if the pointer ever stops being `EU.*`.

⚪ **The honesty clause is now measured, not quoted.** Every sheet header of `tabula-values.xlsx` was
searched for `schedul`, `hourly`, `sub-hour`, `tapping`, `window open`, `thermostat`, `set point`,
`setpoint`, `zoning`, `zone`, `occupan`, `appliance`, `plug`, `lighting`, `draw`, `3d` — **not one
appears anywhere**. `RL24`'s B17 list is CONFIRMED for schedules, appliance profiles, DHW tapping and
3D zoning, and REFINED for setback and window opening: the slots exist, as the two scalars above.

#### 🔴 A published unit that contradicts its own column, in the second official source today

`Tab.BoundaryCond`'s unit row gives `F_red_htr1` and `F_red_htr4` the unit **°C**. They are
dimensionless factors — the EU rows carry `0.9`/`0.8`, the German rows `0.8796296…`/`0.7931034…`.
**Same class as `FINDING 47` and as `FINDING 56` (`P139` in ISTAT's own tracciato).** Two published
label defects, in two different official sources, found in one day, both caught by reading the values
instead of the label. That is now a pattern and not an anecdote.

#### 🔴 `FINDING 58` — TABULA's `GB` typology is ENGLAND, which is worse than the recorded limitation

The standing note was *"`GB` is Great Britain, not the UK; Northern Ireland is outside it"*. The file
is stricter: **every GB archetype code is `GB.ENG.…`, and there is no Scotland or Wales row anywhere**.
So the `uk` fold's diaries are UK-wide while its building stock is English. It belongs in the same
table as `D-S6-2`'s wave gap and `D-S5-1`'s census-year gap.

⚪ ES and IT have one climate region each (`ES.ME`, `IT.MidClim`), so no regional choice arises — but
`IT.MidClim` standing for a country spanning Alpine to Mediterranean is a declared simplification.

#### 🔴 Two contaminants the extraction had to refuse, and one of them is invisible

* **166 refurbishment variants dropped.** Archetypes ship as `.001` (existing), `.002`, `.003`
  (refurbishment levels). Only `.001` is the existing stock; scoring a refurbished variant against a
  real diary compares our occupancy against a building that does not exist.
* 🔴 **4 rows carry NO construction-year class**: `ES.TestRegion.MUH1..MUH4.SyAv.001.001`. They sit
  under `Code_StatusDataset = Typology` and carry real floor areas (1,034.6–1,499.6 m²), so **neither
  the status column nor a non-null check excludes them.** An extraction keyed on the country code alone
  ships them and **Spain then reports seven construction-year classes where the census axis has six**.
  The builder drops them on the construction-year class and refuses if that set ever changes.

#### 🔴 The three folds do not have the same archetype structure — a fourth LOCO asymmetry

| fold | archetypes | type × period cells |
|---|---|---|
| `es` | 24 | **24 of 24 — a complete 4 × 6 grid** |
| `uk` | 36 | 29 of 32, with **two parallel parameterisations** in some cells (`GB.ENG.SFH.01.Gen` *and* `GB.ENG.SFH.01.Detached`) and merged-period codes (`SFH.04-08`) |
| `it` | 42 | 42 of 48, with **composite types** (`MFH-AB`, `SFH-TH`) and **composite periods** (`.01-03`, `.04-05`) |

Reference floor areas: `es` median 747.7 m², `uk` **149.4**, `it` 549.9. 🔴 **The UK median is a fifth
of Spain's**, because the GB set is dominated by single dwellings while ES/IT carry whole apartment
blocks. **Any per-m² comparison across folds must say which.**

#### What was NOT done

* 🔴 **No IDF was written.** Item 8.1 asks for archetype IDFs; what exists is the parameter table they
  must be built from. Six decisions are named in §6 of the provenance file and **none is taken**:
  box geometry and orientation, zoning, layer build-up behind the U-values, which archetype represents
  a `uk`/`it` cell where two exist, what to do with the 3 empty GB and 6 empty IT cells, and **how to
  split `phi_int` = 3.0 W/m² into occupant / appliance / lighting fractions**, which occupancy cannot
  be injected without.
* 🔴 **The licence is STILL unverified.** `RL24`'s IEE/IWU redistribution claim was not checked here
  either. Owed before any derived table is published, not before it is used internally.
* **No gate was run.** `G8.1`–`G8.4` remain as `D-S8-1` (a) left them.
* Item 8.2 (weather) untouched.

---

### 2026-08-21 (afternoon) — 🟢 **`D-S8-2` ITEM 5 RULED (c) BY THE AUTHOR AND PRE-REGISTERED: THE `phi_int` SPLIT IS A FIVE-LEVEL SENSITIVITY, NOT A CHOSEN NUMBER. 🔴 THE CAMPAIGN IS THEREFORE FIVE TIMES LARGER, AND THE SETBACK SCALAR MUST NOT BECOME A SCHEDULE.**

Full text: `outputs_step8/archetype_parameter_provenance.md` **§9**. §6 item 5 is struck through and
marked closed; **items 1–4 and 6 of §6 remain open.**

#### The form

```
phi_int(t) = (1 - f) * 3.0  +  f * 3.0 * g(t) / mean_year(g(t))
```

`g(t)` is the generated presence signal from `G7.13`. Three properties, each a constraint rather than
a convenience:

* 🟢 **Annual mean is exactly 3.0 W/m² at every `f`.** No run adds or removes energy against TABULA's
  own balance, so **every difference between runs is redistribution in TIME** — which is the paper's
  whole claim.
* 🟢 **`f = 0` IS the uninjected control**, an endpoint of the same sweep rather than a separately
  built model. That removes the "the control was constructed differently" objection outright.
* 🟢 **`f = 1` brackets the effect.** If the conclusion holds at both 0.15 and 1.00, the missing split
  does not decide it — a stronger statement than any single chosen split can support.

#### 🔴 The grid, fixed before any run exists

```
f ∈ { 0.00, 0.15, 0.30, 0.50, 1.00 }
```

⚪ Deliberately **not** taken from any literature value — a spanning grid over the admissible
interval, denser at the low end. **Reporting rule, also pre-registered: the headline result is quoted
at every level of `f`, never at one.** A single-`f` number may not appear in the paper.

#### 🔴 What it costs, stated now rather than discovered later

The injected campaign multiplies by **five**: 102 archetypes × 5 = **510 archetype-runs per weather
specification**. ⚪ Cheaper than it looks — the four injected levels share IDF, weather and schedules;
only the gains object changes.

#### 🔴 The interaction the sweep does NOT cover

TABULA applies its intermittent-heating reduction as a **scalar** on the transmission coefficient
(0.9/0.8 SUH, 0.95/0.85 MUH — `FINDING 57`), not a schedule. If the EnergyPlus model implements a
real night-setback schedule **and** an occupancy-driven gains profile, the two stop being separable
and the difference from TABULA is no longer attributable to occupancy. **The campaign must keep the
scalar and must not add a setback schedule.**

⚪ Also outside the sweep: the shape of `g(t)` itself (that is the object under test, not a
parameter), and §6 items 1–4 and 6 — geometry, zoning, layer build-up, archetype selection, weather.

#### 🔴 Unchanged from this morning

No IDF written. TABULA licence still unverified. No Step 8 gate run. Item 8.2 (weather) untouched.


---

### 2026-08-21 (late afternoon) --- 🟢 **SECTION 6 ITEMS 2 AND 6 RULED BY THE AUTHOR: ONE THERMAL ZONE PER DWELLING, AND DIARY-SURVEY-YEAR ACTUAL WEATHER. 🔴 THE WEATHER RULING BUYS INTERNAL CONSISTENCY AT THE PRICE OF A CROSS-FOLD CONFOUND, AND THAT PRICE IS RECORDED BEFORE ANY RUN EXISTS.**

Full text: `outputs_step8/archetype_parameter_provenance.md` **sections 10 and 11** (backup `.bak2`,
247 -> 331 -> 454 lines). Section 6 items 2 and 6 are struck through; **items 1, 3 and 4 remain open.**

#### 🟢 Item 2 --- ONE THERMAL ZONE PER DWELLING

Forced rather than preferred, and by the same shape of argument as `FINDING 60`'s convention A.
TABULA's calculation has no internal partition anywhere: `c_m` is one dwelling-wide capacity,
`theta_i` one set-point, `n_air_use` one air-change rate, `F_red_htr` one scalar on the whole
transmission coefficient. **There is no second zone in the parameter set to give a second zone its
values**, so a multi-zone model would have to be parameterised from an assumption about how dwellings
are divided, and that assumption would then sit between our schedules and our result doing undeclared
work.

🔴 The cost, stated now: the generated diaries carry `LOC == at_home` and nothing finer.
The paper may say that occupancy redistributes internal gains in TIME. It may not say anything about
WHERE in the dwelling they land, and no sentence may imply that it can.

⚪ One zone is not one shoebox. Section 6 item 1 (geometry) is untouched and still owes an
aspect ratio, an orientation and a window-to-face mapping.

#### 🟢 Item 6 --- DIARY-SURVEY-YEAR ACTUAL WEATHER

Each fold runs on the actual meteorological year covering its own fieldwork window: `es` 2009-2010,
`uk` 2014-2015, `it` 2013-2014. Not a typical year, not one shared year.

🔴 **This was not the recommended option, and the reason is a property of the design, not
a preference.** Under a shared weather year the only thing differing across folds is the country and
the transfer to it. Under this ruling **two things differ at once**, and the windows are five years
apart at the extremes. So a cross-fold difference in heating demand can no longer be attributed to the
LOCO transfer: part of it is that Spain's winter and the UK's winter were different winters. It joins
a list of country-correlated asymmetries that is already long enough to need a table in the paper:
`FINDING 53`'s three day bases, `D-S6-2`'s Italian wave gap, `FINDING 51`'s missing Spanish
`homemaker` band, `FINDING 60`'s two household conventions.

🟢 **What contains it, and the containment is real.** `D-S8-2` fixed
`f in {0, 0.15, 0.30, 0.50, 1.00}`, and every level of `f` within one fold runs on the SAME weather
file. So the occupancy effect --- the difference across `f`, within a fold --- is weather-free by
construction, because `f = 0` sees exactly the same year as `f = 1`. 🔴 **Pre-registered
reporting rule, added today: the headline effect is quoted WITHIN fold. Any cross-fold comparison of
absolute demand must name the meteorological year in the same sentence as the country.**

🔴 **The ruling is a decision, not a runnable design.** Item 8.2 stays open and is now a
data-acquisition task of the same kind as 5.1 and 8.1, not attempted blind. It needs (1) the fieldwork
calendars, so "survey year" becomes a definite twelve months --- proposed rule, to be confirmed
against the published methodology: the twelve consecutive months containing the most diaries; (2) an
AMY source whose licence permits publishing derived results, which is a different question from
whether the file downloads; (3) a location, since TABULA's tags are `ES.ME`, `GB.ENG`, `IT.MidClim`
and not coordinates. **Until all three are on disk, no weather-driven number may be quoted at all,
not even a provisional typical-year one** --- a provisional TMY run is exactly the thing that would
later be mistaken for the pre-registered design.

#### 🟢 Item 8.1 re-run and reproducible

`python tools/4thJ_step8_tabula.py Step8_docs/outputs_step8` re-executed end to end from the two
pinned workbooks: 22 of 22 construction-year bands present, all 16 quoted EU boundary-condition values
matching, 166 refurbishment variants dropped, the 4 unclassified ES rows identified by name, and
**24 + 36 + 42 = 102 archetypes** written. `phi_int = 3.0 W/m2` in all three folds, confirmed from the
file rather than quoted.

#### 🟢 The licence question is now a written prompt

Section 7 has owed the TABULA licence verification since 2026-08-20. It is a document-retrieval
question, so the deliverable is a prompt:
`DeepResearchPrompts/L27_hetus_weights_amy_weather_tabula_licence.md`, **Part C**, which also carries
the AMY-weather licence question as **Part B**. 🔴 It states explicitly that a licence may
not be inferred from the absence of a paywall, which is what the earlier unverified claim amounted to.

#### Unchanged

No IDF written. No Step 8 gate run. `G8.1`-`G8.4` are `D-S8-1` (a) reproducibility gates with no run
to reproduce. Section 6 items 1, 3 and 4 open.

---

### 2026-08-24 (evening) — 🟢 **SECTION 6 IS CLOSED. THE LAST THREE OPEN DECISIONS — ITEMS 1, 3 AND 4 — WERE RULED `1(a)`, `3(a)`, `4a(a)`, `4b(a)`, AND THREE OF THE FOUR QUESTIONS CHANGED SHAPE BEFORE THEY WERE PUT, BECAUSE THE PARAMETER TABLES WERE MEASURED RATHER THAN QUOTED.**

Decision brief: `Step8_docs/docs/2026-08-24_D-S8-2_items-1-3-4_geometry-layers-archetype-selection.md`,
status **RULED**, the author's rulings recorded in its own §7. No IDF exists yet; nothing below is a
run.

#### ⚪ First, the docket itself was wrong, and the correction is recorded before the rulings

This document's STATUS line said **five** of six §6 decisions were open. Its own 2026-08-21 entry, 450
lines lower, says items 2 and 6 are struck through and *"items 1, 3 and 4 remain open"*. **Three, not
five.** The header had not been updated when items 2 and 6 were ruled. Fixed above.

#### 🔴 `FINDING 107` — ITALY HAS NO EMPTY CELLS. THE 42 ROWS ARE NOT 42 CELLS.

The tables were read from disk, not from the provenance summary, filtering the three leading `#`
comment lines:

| fold | rows | cells (`types × periods`) | duplicate cells | **empty cells** |
|---|---|---|---|---|
| `es` | 24 | 4 × 6 = **24** | 0 | **0** |
| `uk` | 36 | 4 × 8 = **32** | 7 | **3** — `AB` × `GB.05`, `GB.06`, `GB.08` |
| `it` | 42 | 4 × 8 = **32** | 10 | **0** |

🔴 **This made item 4b a UK-only question.** It had been carried as a general one about "the folds
with more rows than cells", and Italy's ten extra rows are duplicates of cells that are already
filled — they need a *selection* rule (4a), never an *invention* rule. Had the question been put as
written, it would have asked the author to rule on a gap Italy does not have.

#### 🔴 `FINDING 108` — THE THREE MISSING GB CELLS ARE INSIDE A DECLARED SPAN. THE QUESTION WAS NOT "WHAT DO WE INVENT".

Every UK `AB` row and the period its own TABULA code declares:

```
GB.01 -> GB.ENG.AB.01.ApartmentBuildings.SyAv.001     span 01
GB.02 -> GB.ENG.AB.02-03.ApartmentBuildings.SyAv.002  span 02-03
GB.03 -> GB.ENG.AB.03.Gen.ReEx.001                    span 03
GB.04 -> GB.ENG.AB.04-08.ApartmentBuildings.SyAv.005  span 04-08
GB.04 -> GB.ENG.AB.04.Gen.ReEx.001                    span 04
GB.07 -> GB.ENG.AB.07.Gen.ReEx.001                    span 07
```

`GB.05`, `GB.06` and `GB.08` are empty **only because the loader keyed `AB.04-08` to the first period
of its span**. TABULA published one row for five bands and our reader filed it under one. The
question became *may a merged row cover the periods its code declares* — which is a question about
reading the source correctly, not about fabricating an archetype, and that is why the answer could be
`(a)`.

#### 🔴 `FINDING 109` — THE UK ARCHETYPES HAVE ZERO SOUTH AND ZERO NORTH GLAZING, IN ALL 36 ROWS. THIS REVERSED THE RECOMMENDATION ON ITEM 1.

Count of rows carrying a non-zero window area on each face:

| fold | rows | East | **South** | West | **North** | Horizontal |
|---|---|---|---|---|---|---|
| `es` | 24 | 19 | 17 | 17 | 19 | 0 |
| `uk` | 36 | **36** | **0** | 27 | **0** | 0 |
| `it` | 42 | 29 | 38 | 28 | 25 | 0 |

🔴 **The three national TABULA teams did not use the compass columns the same way.** The British
sheet books glazing to East (and partly West) and never to South or North; the Spanish and Italian
sheets spread it over all four. Placing each `A_Window_<dir>` on the face of its own name would
therefore give every UK archetype **an all-East-facing dwelling** and every Spanish and Italian one a
four-sided dwelling — a **country-correlated** solar-gain difference, imposed by a bookkeeping
convention, in a study whose entire design is LOCO. It would land in the same class as
`FINDING 53` (three day bases) and `FINDING 60` (two household conventions): an artefact that is
perfectly deterministic per country and therefore indistinguishable from a country effect.

#### 🟢 The rulings

| item | ruled | what it means |
|---|:---:|---|
| **1** geometry & glazing | **(a)** | One equivalent box per archetype, aspect ratio **1 : 1.5**, long axis **East–West**. Footprint `A_plate = A_C,Ref / n_Storey`, height `n_Storey × h_room`. **Total glazed area split equally over the four vertical facades**, neutralising the British zero-South convention (`FINDING 109`). Where the total-window column is zero the **sum of the compass columns** is used instead — this repairs `ES.ME.MFH.05`. |
| **3** layers & thermal mass | **(a)** | **Two-layer equivalent per surface**: one mass-less resistive layer reproducing the TABULA `U` **exactly**, plus one capacitive layer sized so areal capacity reproduces `c_m = 45 Wh/(m²·K)`. Both normative quantities are met deterministically, and **no external construction assembly is invented** — no brick/EPS/plaster build-up enters the model. |
| **4a** duplicate cells | **(a)** | **Prefer the `Gen` row wherever one exists**; a specific or composite row is used only where no `Gen` row exists. One symmetric rule for all **17** duplicate cells (`uk` 7 + `it` 10), so no country gets its own selection logic. |
| **4b** merged GB rows | **(a)** | **A merged row represents every period its code declares** — `AB.04-08` expands over `GB.04`–`GB.08`, `AB.02-03` over `GB.02`–`GB.03`. The UK matrix closes at **32 / 32** with nothing fabricated. Where the expansion collides with a single-period row, **4a decides** (`Gen` wins). |

⚪ **Where 4a and 4b interact, and the order matters.** `GB.04` is reachable two ways after the
expansion: `AB.04-08.ApartmentBuildings.SyAv.005` by span and `AB.04.Gen.ReEx.001` directly. 4a is
applied after 4b, so `GB.04` takes the `Gen` row and the merged row supplies `GB.05`–`GB.08` only.
The rule is stated in that order deliberately; reversed, it would give `GB.04` a composite row while
a `Gen` row for exactly that band sat unused.

#### 🔴 What this does **not** unblock

* **No IDF exists.** These four rulings are the specification for writing one; none of it has been
  written, and **no Step 8 gate has ever been run** on any leg.
* **Item 8.2 has no weather file.** The diary-survey-year ruling (§6 item 6) is a decision, not an
  acquisition — nothing is on disk and the AMY licence question is still an unanswered Part B of
  `DeepResearchPrompts/L27_...md`. The TABULA licence (Part C) is likewise unverified.
* **`G8.1`–`G8.4` still have no reference series** — `D-S8-1` (a) made them reproducibility gates,
  and there is no run to reproduce.
* 🔴 **Decision 14 (chaining) is still open**, and Step 8 is where it closes, on a watt. Nothing here
  touches it. `FINDING 105` removed one argument that was being made in its support.
* The `f ∈ {0, 0.15, 0.30, 0.50, 1.00}` sensitivity (`D-S8-2` item 5) still multiplies the campaign by
  five: **102 archetypes × 5 = 510 archetype-runs** per weather specification.

⚪ `prereg.md` untouched, md5 `e4243e07cdd80c9c846b91f40e3e8c45`. No threshold moved, no checker
edited, no parameter table rewritten — `archetype_parameters_{es,uk,it}.csv` are byte-identical to
their 2026-08-21 state and the rulings above are instructions to the **builder**, not edits to the
tables.

---

### 2026-08-24 (night) — 🟢 **WORK ITEM 8.1 IS BUILT AND VALIDATED. 88 ARCHETYPE IDFs EXIST, ALL 88 RUN IN ENERGYPLUS WITH ZERO SEVERE ERRORS, AND ENERGYPLUS ITSELF REPRODUCES EVERY TABULA U TO 0.0005 W/(m²·K). 🔴 AND THE VALIDATION FOUND TWO THINGS THE RULINGS DID NOT ANTICIPATE — `FINDING 110` AND `FINDING 111` — BOTH COUNTRY-CORRELATED, ONE OF WHICH NEEDS THE AUTHOR.**

`tools/4thJ_step8_idf.py` + `tools/4thJ_step8_idf_selftest.py`. Local, no Speed job. E+ **24.2.0**,
build hash **`94a887817b`**.

#### 🟢 The archetype set is **88**, not 102 — and that is the rulings working, not a loss

`102` counted **rows in the parameter tables**. `4a(a)` and `4b(a)` turn rows into **cells**, and a
cell is what gets an IDF:

| fold | rows | matrix | resolved | 4b expansions | rows excluded |
|---|---|---|---|---|---|
| `es` | 24 | 4 × 6 = **24** | 24 | 0 | 0 |
| `uk` | 36 | 4 × 8 = **32** | 32 | 6 | 0 |
| `it` | 42 | 4 × 8 = **32** | 32 | 0 | **10** |
| | | | **88** | | |

🔴 **The campaign is therefore `88 × 5 = 440` archetype-runs per weather specification, not
`102 × 5 = 510`.** The 510 figure has been carried since 2026-08-21 and is superseded. ⚪ It is not
in `prereg.md` — checked, the file names no archetype count — so this is a Step 8 figure being
corrected, not a deviation from a frozen registration.

🔴 **Italy's ten extra rows are not duplicates. They are COMBINED-CLASS rows, and `4a(a)` cannot
arbitrate them.** `FINDING 107` called them duplicate cells; reading the codes says otherwise:

```
IT.MidClim.MFH-AB.01-03.Gen.ReEx.001   IT.MidClim.SFH-TH.01-03.Gen.ReEx.001
IT.MidClim.MFH-AB.04-05.Gen.ReEx.001   IT.MidClim.SFH-TH.04-05.Gen.ReEx.001
IT.MidClim.MFH-AB.06.Gen.ReEx.001      IT.MidClim.SFH-TH.06.Gen.ReEx.001
IT.MidClim.MFH-AB.07.Gen.ReEx.001      IT.MidClim.SFH-TH.07.Gen.ReEx.001
IT.MidClim.MFH-AB.08.Gen.ReEx.001      IT.MidClim.SFH-TH.08.Gen.ReEx.001
```

`MFH-AB` names **two** classes. It is TABULA's coarser two-class breakdown published beside the
four-class one — and for periods 06/07/08 the combined row is numerically **identical** to the
single-class row (`SFH-TH.06` `A_C_Ref` = 199.1 = `SFH.06`; `MFH-AB.08` = 829.4 = `MFH.08`). Both
candidates carry `.Gen.`, so **`4a(a)`'s Gen preference cannot choose between them** — it discriminates
on the variant token, and here the difference is in the *class* token. The builder excludes them on
the ground that a row labelled `MFH-AB` is a row for neither `MFH` nor `AB` alone, and the exclusion
is **listed by name** in `archetype_selection_report.json` rather than performed silently. Italy still
closes at 32/32 without them, so nothing is lost — but this is a gap in `4a(a)` as written, and it is
recorded as one.

⚪ Also recorded: **the loader had been filing these under the FIRST class token** (`MFH-AB` → `MFH`),
which is why the earlier count called Italy's 42 rows "10 duplicates". That was the loader's choice,
not TABULA's.

#### 🟢 The four rulings, checked one at a time rather than in aggregate

`4thJ_step8_idf_selftest.py` half A, **17 of 17**:

* `1(a)` — `W/D = 1.5` on all 88; footprint `= A_C_Ref / n_Storey` on all 88; height
  `= n_Storey × h_room` on all 88; glazed area **split into exactly four equal faces** on all 88.
* the compass-sum fallback fires **exactly once**, on `ES.ME.MFH.05` — which is the archetype the
  ruling named. Not asserted from the ruling; measured from the output and compared to it.
* `3(a)` — `c_m × A_C_Ref` conserved over the modelled opaque envelope on all 88, and **no
  construction clamped**.
* `4b(a)` — the UK matrix closes at **32/32**; the four cells served by a merged-span row are
  `AB.02`, `AB.05`, `AB.06`, `AB.08` and no others; the three the table left empty are filled by
  `GB.ENG.AB.04-08.ApartmentBuildings.SyAv.005` specifically.
* `4a` **after** `4b` — `GB.04` is reachable both ways and takes the `.Gen.` row, checked directly.

#### 🟢 Half B is the half that matters, and it is a round-trip through EnergyPlus, not arithmetic

All **88** IDFs were run. **88 / 88 exit 0, zero severe errors.** For every opaque exterior surface
the `U-Factor no Film` E+ computed for itself was read back out of `eplustbl.csv` and compared to
`1 / (1/U_TABULA − R_si − R_se)`:

**worst deviation over 440 surfaces: `0.00050 W/(m²·K)`** (`it_MFH_IT05`, E+ 1.8000 against a
required 1.8005 — a rounding digit).

🔴 **This selftest has been seen failing, four separate times, on defects it found in this build.**
Not one of them was predicted:

| what failed | what it caught |
|---|---|
| `A11` | `ES.ME.SFH.01` has `U_Roof = 5.56 + 0.15`. At the first mass-layer conductivity the capacitive layer's own resistance (0.05) **exceeded the whole available resistance** (0.035) and the construction had to be clamped. Fixed by raising the conductivity to 5.0 — which changes no U and no `c_m`, because conductivity does not enter areal capacity. |
| `A3`/`A4` | The manifest's `period` column carried the **chosen row's** period, not the **cell's**. Six UK files said `GB.04` beside a file named `uk_AB_GB05.idf`. The IDFs were right; the provenance was lying. Now `cell_period` and `row_period` are both written. |
| `B1` | `ScheduleTypeLimits` unit type `ControlMode` is not an EnergyPlus enum value. Every Spanish archetype was fatal on input processing. Caught on the very first run of half B. |
| `B3` | 🔴 **The check itself was wrong** — see `FINDING 111`. |

#### 🔴 `FINDING 110` — THE EQUAL-FACADE BOX CONSERVES FLOOR AREA AND VOLUME. IT DOES NOT CONSERVE ENVELOPE AREA, AND WHAT IT LOSES IS COUNTRY-CORRELATED: ITALY'S TRANSMISSION LOSS IS UNDERSTATED BY 23.5 %, THE UK'S BY 4.4 %.

`1(a)` derives the box from `A_C_Ref` and `n_Storey`. Nothing in that derivation touches
`A_Wall_1..3`, `A_Roof_1..2` or `A_Floor_1..2`, so TABULA's own envelope areas are simply not used —
and the box does not reproduce them. Ratio of modelled to published opaque envelope area, and the
consequence for `H_transmission = Σ U·A`:

| fold | opaque envelope, box / TABULA | `H_transmission`, box / TABULA |
|---|---|---|
| `es` | median **0.889** (0.515 – 1.926) | median **0.924** (0.576 – 1.582) |
| `uk` | median **0.946** (0.699 – 1.552) | median **0.956** (0.802 – 1.213) |
| `it` | median **0.718** (0.361 – 1.322) | median **0.765** (0.576 – 1.240) |

🔴 **The spread across folds is 19 percentage points and it is deterministic per country.** Broken
down by class, the driver is visible:

| class | `es` | `uk` | `it` |
|---|---|---|---|
| `SFH` | 0.873 | 0.871 | 0.792 |
| `TH` | 0.961 | 1.139 | 1.063 |
| `MFH` | 0.906 | 0.934 | **0.703** |
| `AB` | 1.022 | 1.058 | **0.656** |

It is not the class mix — every fold carries the same four classes in equal numbers. It is that the
**Italian TABULA reference buildings for `MFH` and `AB` are shaped nothing like a 1 : 1.5 box.**
`IT.MidClim.AB.02` publishes `A_Wall = 3,257 m²`; the box built from its own `A_C_Ref = 2,448` over
4 storeys has `473 m²` of wall. A factor of **6.9**.

⚪ **This does not make `1(a)` wrong, and it is not a reason to reopen it on its own terms.** `1(a)`
was ruled to neutralise `FINDING 109`, the zero-South British glazing convention, and it does that.
But it was ruled without this number, exactly as `FINDING 109` was discovered after the geometry
question was first drafted. **This is the same class of artefact as `FINDING 53`, `FINDING 60` and
`FINDING 109`: perfectly deterministic per country, and therefore indistinguishable from a country
effect in a design whose entire claim is LOCO.** It goes to the author as **`D-S8-3`**, with the
brief at `Step8_docs/docs/2026-08-24_D-S8-3_the-box-does-not-conserve-envelope-area.md`.

#### 🔴 `FINDING 111` — TABULA'S U AND ENERGYPLUS'S U ARE NOT THE SAME QUANTITY, AND THE GAP GROWS WITH U, SO IT TOO IS PERIOD- AND COUNTRY-CORRELATED.

TABULA publishes a thermal transmittance in the **EN ISO 6946** sense: films included, at the fixed
`R_si = 0.13`, `R_se = 0.04` for a wall. An EnergyPlus `Construction` resistance **excludes** films
and E+ adds its own — dynamically in simulation, and at its own standard values in the tabular
report. The builder therefore gives the resistive layer `1/U − R_si − R_se`, and `B3` confirms E+
computes exactly that back.

But the U **E+ will actually simulate with** is not TABULA's. Over the same 440 surfaces:

```
(U_Eplus_with_film - U_TABULA) / U_TABULA      min -0.00 %   median +2.58 %   max +6.70 %
```

🔴 **The gap grows with U**, because the film resistance is a fixed additive term. A poorly insulated
1960s wall is overstated by ~6 %; a modern one by well under 1 %. Construction period therefore sets
the size of the error, and the period mix differs by fold (median `U_wall + Δ`: `uk` 1.700,
`es` 1.606, `it` 1.305).

⚪ **The alternative convention would have been far worse and in the opposite direction.** Had the
resistive layer been given `1/U` outright — the naive reading of *"a layer matching TABULA U"* — E+
would have added films on top, understating transmittance by **≈ 30 %** at `U = 2.56` and **≈ 5 %** at
`U = 0.30`. That is a five-fold period-dependent bias instead of a six-fold-smaller one. The ISO 6946
subtraction is the right choice and it is now in the code with the reason beside it.

🔴 **`B3` originally tested the wrong quantity** — it compared E+'s with-film U to TABULA's U and
failed, and the temptation was to call the construction broken. It was not; the check was. `B3` now
tests the construction alone, which is what the builder controls, and **`B4` reports the film gap as
a measured number that is deliberately not a pass/fail**, because it does not go away and hiding it
behind a quantity that agrees would be the `FINDING 47` error.

#### ⚪ What the IDFs contain, and what TABULA does not give us

One thermal zone (§6 item 2). Four walls, four windows — one per facade by `1(a)` — a roof, a
ground-coupled floor. `WindowMaterial:SimpleGlazingSystem` at `U_Window_1`. `OtherEquipment` carrying
`phi_int × A_C_Ref` watts on `SCH_ALWAYS_ON`, which is the hook item 8.5 replaces with the Step 7
schedule and the `f ∈ {0, 0.15, 0.30, 0.50, 1.00}` sensitivity. Ideal loads, heating only —
`ThermostatSetpoint:SingleHeating` — because TABULA residential has no cooling demand.

Six quantities are **not** in the 44 columns we hold and are declared in
`archetype_selection_report.json`, every one **uniform across all 88 archetypes and all three folds**
so that it cannot itself manufacture a country difference: `SHGC = 0.70`, infiltration
`0.50 ach`, heating set point `20 °C` (the EU boundary condition, per `FINDING 57`), no cooling, no
ground temperatures, no window frame fraction.

🔴 **The weather is still item 8.2 and is still open.** Half B ran on the Chicago TMY3 file that
ships with EnergyPlus. That is a **validity probe and never a result** — a U-factor round-trip does
not depend on climate, and no energy number from those runs is recorded anywhere. The `RunPeriod`
written into each IDF is a **calendar**, not a weather choice.

#### What this entry does not settle

* **`D-S8-3` is open** and it is on the critical path of any number Step 8 produces.
* **Item 8.2 has no weather file**, so 8.3 cannot start.
* **`G8.1`–`G8.4` still have no reference series** and no Step 8 gate has been run.
* 🔴 **Decision 14 (chaining) is still open** and still closes here, on a watt.
* `prereg.md` untouched, md5 `e4243e07cdd80c9c846b91f40e3e8c45`.

Artefacts: `outputs_step8/archetypes/*.idf` (88 files), `outputs_step8/archetype_idf_manifest.csv`,
`outputs_step8/archetype_selection_report.json`.

### 2026-08-25 — 🟢 **`D-S8-3` RULED (a) BY THE AUTHOR AND IMPLEMENTED. THE 88 IDFs ARE REBUILT, ALL 88 STILL RUN IN ENERGYPLUS WITH ZERO SEVERE ERRORS, AND TABULA'S PUBLISHED WALL AREA IS NOW REPRODUCED EXACTLY ON EVERY ARCHETYPE THAT ADMITS A BOX. 🔴 `FINDING 117`: IT REMOVES TWO THIRDS OF `FINDING 110`, NOT ALL OF IT, AND WHAT SURVIVES IS NOT A REMAINDER — IT LIVES ENTIRELY INSIDE 38 FALLBACKS THAT ARE STRUCTURAL, NOT NUMERICAL.**

#### The ruling, and exactly what was built

`D-S8-3` = **(a)**. The fixed 1 : 1.5 aspect ratio is replaced by an aspect **solved per archetype**
so that the box reproduces TABULA's own wall area. The equal four-facade glazing split — the half of
`1(a)` that was ruled to neutralise `FINDING 109` — is untouched, and so are `A_C_Ref`, the volume,
`c_m`, `phi_int` and the selection.

The solve targets the **gross** facade, not `A_Wall` alone:

```
    2 (W + D) H  =  A_Wall_TABULA + A_Window          W D = A_plate
```

because the builder carves the glazing out of the facade (`a_wall_box = 2(W+D)H − win_total`).
Targeting the gross is what makes the modelled **opaque** wall equal TABULA's published `A_Wall`
exactly; targeting `A_Wall` alone would have conserved nothing and produced *more* fallbacks. `W ≥ D`
always, so `1(a)`'s long-axis-East-West convention survives. Evidence: `tools/4thJ_step8_idf.py`,
module docstring and `derive()`.

#### 🔴 `FINDING 117` — the fix works, it is not complete, and the residue is concentrated

| median, box / TABULA | `es` | `uk` | `it` | spread |
|---|---|---|---|---|
| **wall area**, before | 0.917 | 0.884 | 0.666 | 25.1 pp |
| **wall area**, after | **1.000** | **1.000** | **1.000** | **0.0 pp** |
| `H_transmission`, before | 0.924 | 0.956 | 0.765 | **19.1 pp** |
| `H_transmission`, after | 0.982 | 0.995 | 0.933 | **6.1 pp** |

🟢 The country-correlated artefact `FINDING 110` measured falls by **68 %**, and the quantity the
ruling actually names — the wall area — is conserved to floating-point on every archetype that
admits a box.

🔴 **It does not reach zero, and the 6.1 pp that survives is not spread thinly.** Split by how the
shape was obtained:

| rows | n | `es` | `uk` | `it` | spread |
|---|---|---|---|---|---|
| solved from TABULA | 50 | 0.976 | 0.988 | 0.941 | **4.8 pp** |
| fell back to 1 : 1.5 | 38 | 1.074 | 1.139 | 0.709 | **43.1 pp** |

**The residue is the fallbacks.** Among the 50 archetypes that admit a box the LOCO channel is nearly
clean; among the 38 that do not, the original artefact is not merely intact, it is worse than the
88-row average ever was.

#### 🔴 Why 38 of 88 fall back, and why that is a fact about TABULA rather than about the code

The brief said "a few archetypes". It is **38**, and neither trigger is a rounding accident.

| trigger | n | by fold | by class |
|---|---|---|---|
| `no_real_root` — `S < 2√A_plate`, the published wall is below the minimum perimeter for that footprint, so **no real box exists** | 26 | es 9, uk 10, it 7 | **TH 19**, AB 4, MFH 2, SFH 1 |
| `glazing_does_not_fit` — a real root exists but the box is so elongated that a quarter of the glazing will not fit on the narrow facade (WWR > 0.94) | 12 | es 2, **it 10** | AB 7, MFH 4, SFH 1 |

* **19 of the 26** `no_real_root` rows are **terraced houses**. TABULA's `A_Wall` for a terrace
  excludes the party walls, because a terrace does not have them exposed. A free-standing box must
  have four walls. The equation has no real solution for the same reason the building is not a box.
  This is a **modelling-convention collision, not a data error**, and no aspect ratio can repair it.
* **10 of the 12** `glazing_does_not_fit` rows are **Italian** `AB`/`MFH` — the very class-fold cells
  that drove `FINDING 110`. The solved shapes there are extreme (`IT.MidClim.AB.02` wanted
  186.4 m × 3.3 m, aspect 57 : 1, needing **409 %** of its narrow facade as glass). `1(a)`'s equal
  four-facade split is a strict invariant of the author's directive and outranks the aspect ratio,
  so the **aspect** gives way and the row falls back — the split is never broken.

Consequence, by class and fold, after the change:

| class | `es` | `uk` | `it` |
|---|---|---|---|
| SFH | 1.073 | 0.950 | 0.933 |
| TH | 0.981 | **1.139** | 1.063 |
| MFH | 0.975 | 0.991 | 0.807 |
| AB | 1.027 | **1.137** | **0.656** |

🔴 **`it`/`AB` is still 0.656 and `uk`/`TH`/`AB` now over-state at ≈ 1.14.** The residual artefact has
changed shape: it is no longer a smooth country-wide deficit, it is two opposite-signed cells. Never
quote the 6.1 pp headline without this table — an Italian `AB` result and a British `TH` result are
the two places a LOCO difference is still explainable by geometry.

#### What the aspect ratio actually became

Median **2.05**, min 1.48, p90 10.3, max **22.1** (`ES.ME.MFH.04`, depth 3.8 m). Nine archetypes
exceed 10 : 1. The 57 : 1 case does not appear because it fell back. These are slabs, and they are
slabs on purpose: a Mediterranean apartment block genuinely has far more facade than a compact box
of the same floor area.

#### Verification — 26 checks, 0 failed, and the new ones were seen failing first

Half A now carries five new checks and two regression guards. Half B re-ran all 88 archetypes:

* **B1 every IDF runs, 0 severe errors** — including the 22 : 1 slabs. This was the real risk of (a)
  and it did not materialise.
* **B3 E+'s own construction U reproduces `1/(1/U_TABULA − Rsi − Rse)`**, worst deviation
  **0.0005 W/(m²·K)**. `3(a)` re-conserves automatically as the brief predicted: `A11` still passes,
  `A10` still passes, the areal capacity simply redistributed over the new envelope.
* **B4** the `FINDING 111` film gap is unchanged in character — min −0.00 %, median **+2.58 %**, max
  +6.70 % over 440 surfaces. It is independent of this decision, as the brief said it was.

🔴 **`A5` was a no-op when first written, and the injection battery is what caught it.** It compared
the manifest's stored `a_wall_box` column against `a_wall_tabula` — so reverting an archetype's
geometry to 1 : 1.5 while leaving the stored column alone **passed**. That is precisely the
regression the check exists to catch. `A5` now **re-derives** `2(W+D)H − win_total` from `width`,
`depth`, `height` and `win_total` and cross-checks the stored column against it. Battery result,
baseline clean so the clause is **not vacuous**:

| injection | target | result |
|---|---|---|
| revert a solved row to 1 : 1.5 | `A5` | **seen failing** (was a NO-OP before the fix) |
| relabel a fallback row as solved | `A5` | seen failing |
| drop a fallback's reason | `A5c` | seen failing |
| put the long axis North-South | `A5d` | seen failing |
| let one fallback stop firing | `A13` | seen failing |
| let a facade past the 0.94 cap | `A12` | seen failing |
| inflate a footprint by 5 % | `A6` | seen failing |

`coverage_clause: PASS`, 7 of 7, 0 no-ops. `A13`/`A14`/`A15` pin the fallback census (26 + 12; es 11,
uk 10, it 17; 19 TH) so that a TABULA re-read or a reselection cannot move the numbers `FINDING 117`
is written from without a check going red.

#### What this entry does not settle

* 🔴 **The 6.1 pp residue is real and it is still inside the LOCO channel.** Recovering part of it
  would mean clamping the 12 `glazing_does_not_fit` rows to the most elongated *admissible* aspect
  instead of all the way back to 1 : 1.5 — that is a **new rule**, not an application of `(a)`, and
  it is not taken here. It needs the author.
* **Item 8.2 still has no weather file**, so 8.3 still cannot start. This is now the binding
  constraint on the whole step.
* **`G8.1`–`G8.4` still have no reference series** and no Step 8 gate has ever been run.
* 🔴 **Decision 14 (chaining) is still open** and still closes here, on a watt.
* All 88 IDF md5s changed, including the 38 fallbacks — their geometry is identical but the header
  now records `aspect_source`, so a reader can never mistake a fallback for a solved box.
* `prereg.md` untouched, md5 `e4243e07cdd80c9c846b91f40e3e8c45`.

Artefacts: `tools/4thJ_step8_idf.py` (+77 lines; `.bak_ds83`),
`tools/4thJ_step8_idf_selftest.py` (`.bak_ds83`), `outputs_step8/archetypes/*.idf` (88 rebuilt),
`outputs_step8/archetype_idf_manifest.csv` (4 new columns `aspect`, `aspect_source`,
`aspect_fallback`, `a_wall_gross_target`; `.bak_ds83` holds the pre-ruling manifest),
`outputs_step8/archetype_selection_report.json`.

---

### 2026-08-25 (night) — 🟢 **ITEM 8.2 IS CLOSED. THE AUTHOR REVERSED THE ACTUAL-YEAR WEATHER RULING, AND THE THREE EPWs ARE ON DISK — SELECTED BY MEASURING TABULA'S OWN PUBLISHED MONTHLY TEMPERATURES AGAINST 44 CANDIDATE STATIONS, NOT BY QUOTING A REPORT. 🔴 AND THE STATION TURNS OUT TO BE WORTH 5 TO 11 % OF HEATING DEMAND, CHOSEN ON A MARGIN OF 0.002 K.**

Brief: `Step8_docs/docs/2026-08-25_D-S8-4_weather-basis-and-station-selection.md`.

#### 🟢 The ruling

The author: *"pas nécessaire de choisir de l'année exacte — tu peux choisir des autres années ou TMY
méthode qui constituent plus d'années, ça marche pour nous aussi."* **The exact meteorological year
is not required; a typical year built from many years is acceptable.** This reverses section 6 item 6
(2026-08-21, *diary-survey-year actual weather*). The old entry is left standing with its reasoning
intact; `D-S8-4` is what supersedes it.

🟢 **The reversal is a gain, and the 2026-08-21 entry said so itself**: under the actual-year ruling
"two things differ at once" across folds — the country *and* the meteorological year — so a cross-fold
demand difference could not be attributed to the LOCO transfer. One shared base period removes that
confound. 🟢 `prereg.md` was checked and has no weather clause at all: nothing to deviate from, md5
`e4243e07cdd80c9c846b91f40e3e8c45`, untouched.

#### 🟢 What is on disk

**`TMYx.2009-2023`, the same base period for all three folds** — not an arbitrary vintage among the
five OneBuilding publishes, but the only 15-year window that **contains all three original fieldwork
windows** (`es` 2009-2010, `uk` 2014-2015, `it` 2013-2014). The abandoned years are inside the base
period of the typical year that replaced them.

⚪ Checked before use, and it settles a counterfactual: **climate.onebuilding.org publishes TMYx
only.** All 107 Spanish, 197 British and 148 Italian 2009-2023 files are typical years. Had the old
ruling stood, the source the author pointed at could not have served item 8.2 at all.

One EPW per fold, because the parameter tables carry exactly one climate region per fold — read, not
assumed, and the tool aborts if that stops being true.

#### 🟢 The station was measured, and both planted controls lost

TABULA gives no coordinates, but `Tab.AuxCalc.Climate` gives the twelve monthly mean external
temperatures each region code stands for. That is enough to *select*:
`score = RMSE( EPW monthly mean dry bulb − TABULA theta_e_MM )`, lowest wins. **44 stations
downloaded and scored** (es 11, uk 10, it 23), each shortlist carrying a deliberate control that
should lose.

| fold | region | station | WMO | score | worst candidate |
|---|---|---|---|---|---|
| `es` | `ES.ME` Mediterranean | **Valencia.Viveros** | 082850 | **0.620** | Madrid-Barajas **3.57** |
| `uk` | `GB.Temperate` England | **Birmingham.AP** | 035340 | **0.533** | London St.James **1.69** |
| `it` | `IT.MidClim` Zone E | **Torino.Venaria** | 160600 | **1.043** | Roma-Ciampino **4.58** |

🔴 **`RL27` B12 is falsified and is now marked unusable.** The deep-research response has sat in
`DeepResearchPrompts/` since 2026-08-22 **cited by no document in this project and never vetted**. It
names "Madrid Barajas for `ES.ME`, London Kew/Heathrow for `GB`, Rome/Bologna for `IT.MidClim`".
Measured against TABULA's own numbers those are the **worst** Spanish candidate (3.57 vs 0.62), a
**2.8× worse** English one (Heathrow 1.47 vs 0.53), and the **worst** Italian one (Rome 4.58; Bologna
2.82, vs 1.04). Two of the three name a climate region TABULA does not describe — `ES.ME` is
Mediterranean and Madrid is not; `IT.MidClim` is Zone E and Rome is Zone D. **Nothing else in `RL27`
has been vetted either.**

#### 🔴 `FINDING 120` — the station is a free parameter worth 5 to 11 % of heating demand, and the UK margin that picked it is 0.002 K

Birmingham 0.5333 beat Nottingham-Watnall 0.5351. That is a coin flip, so the coin was made to show
its consequences: **all 88 archetypes were run twice**, on the installed EPW and on the fold's
runner-up — 176 EnergyPlus runs.

| fold | median heating EUI, winner | runner-up | median \|Δ\| | max \|Δ\| |
|---|---|---|---|---|
| `es` | 24.9 kWh/m² | 27.3 | **10.7 %** | 36.6 % |
| `uk` | 104.5 kWh/m² | 110.8 | **5.4 %** | 6.0 % |
| `it` | 81.0 kWh/m² | 74.8 | **8.4 %** | 11.2 % |

🔴 **The sign differs by fold** — Spain's runner-up runs warmer demand, Italy's colder — so this is not
a common offset that divides out of a cross-fold ratio. It is country-correlated, same class as
`FINDING 110`/`117`, and the same order as the 6.1 pp geometry residue `D-S8-3` spent a decision
reducing.

🟢 **What it does not threaten.** `f = 0` and `f = 1` share one EPW inside a fold, so the occupancy
effect — the number the paper is about — is weather-free by construction and the station cancels
exactly. 🔴 **What it does mean: no cross-fold comparison of absolute demand is safe to ±10 %**, and
the 2026-08-21 within-fold reporting rule is kept for that reason. Those EUI figures are a
sensitivity probe with no schedules applied; **none of them is a result.**

⚪ Untaken follow-on, recorded and needing a ruling: run each fold on the mean of its top-`k` stations,
or report a band across them, instead of committing to one station whose margin is 0.002 K. It turns a
hidden ±10 % into a stated interval, and multiplies the campaign by `k`.

#### 🔴 Two smaller findings, both from measuring rather than quoting

* **`FINDING 118`** — one climate region, two spellings, inside one TABULA release: the parameter
  tables carry `GB.Temperate`, `tabula-calculator.xlsx` carries `GB.England-Temperate`. Spain and
  Italy agree across both workbooks; only Great Britain does not. The alias is explicit in the tool
  and the lookup **fails loudly** on a miss — a silent fallback would have scored the British
  stations against nothing.
* **`FINDING 119`** — **TABULA's `HeatingDays` is not the statistic it looks like.** TABULA derives it
  from *monthly* means by a fractional formula (`ES.ME`: `HeatingDays_01 = 21.5`, 22.4 for the year);
  the obvious EPW statistic counts *daily* means below 12 °C. On the same climate the two differ by a
  factor of three — Valencia.Viveros fits the twelve published monthly means to 0.62 K yet shows 72
  "heating days" against TABULA's 22, purely because daily scatter crosses a threshold a monthly mean
  of 11.0 °C never crosses. Scoring on it would have rejected every real Spanish coastal station.
  Measured, recorded per station, **deliberately not scored**. Re-deriving the 22-vs-72 gap is
  re-deriving an artefact.
* ⚪ Annual solar, measured and not scored: all 44 candidates land *above* TABULA's `I_Sol_Year_Hor`.
  The installed files sit at `es` **+9.8 %**, `uk` **+6.7 %**, `it` **+3.0 %** — same sign in all
  three folds, 6.8 pp of spread. In the manifest per fold, not optimised away.

#### 🟢 The gate, and it was seen failing

**`tools/4thJ_step8_weather_selftest.py` — 12 ok, 0 FAILED.** The half that matters is `B2`: one
archetype per fold is run and the `Site:Location` line **EnergyPlus itself writes** into
`eplusout.eio` is read back and matched against the manifest — WMO, latitude, longitude, elevation.
A manifest row saying "this run used Birmingham" is a claim; `WMO#=035340` echoed by E+ is a
measurement. `3J`'s inherited `PLATFORM` field is the precedent.

**Injection battery: 9 of 9 seen felling their target, 0 no-ops, baseline clean** so the coverage
clause is not vacuous — truncate one hour → `W3`; sentinel into a dry bulb → `W4`; corrupt an md5 →
`W2`; mix a second TMYx vintage → `W6`; move a station half a degree → `W7`; overwrite the recorded
score → `W8`; install the runner-up with the manifest made **fully self-consistent** → `W9`; reduce a
candidate set to its winner → `W10`; swap two folds' EPW *content* behind an intact manifest → `B2`,
caught by EnergyPlus.

#### ⚪ The 88 IDFs were rebuilt, for a comment

Every IDF carried `!- NOTE : ... item 8.2 is open.` That is now false, and a false provenance line
stamped into an artefact is a defect class this project already has a precedent for. Three places in
`tools/4thJ_step8_idf.py` corrected, **88 IDFs rebuilt, full 8.1 selftest re-run: 26 ok, 0 FAILED**,
B1 all 88 with zero severe errors, B3 worst deviation 0.00050 W/(m²·K). No geometry, construction or
schedule changed — the diff is comments — but the md5s did, so the manifest was rewritten and
re-checked rather than left to drift.

⚪ The ground-temperature row was corrected in substance too: closing 8.2 does **not** give the model
ground temperatures. E+ ignores the EPW header's ground temperatures unless a `Site:GroundTemperature`
object points at them, and none is written. Still an E+ default, now written down as one.

#### What this entry does not settle

* 🔴 **`FINDING 120`'s ±10 % is live** and no ruling exists on the top-`k` follow-on.
* 🔴 **`G8.1`–`G8.4` still have no reference series.** Item 8.2 was never the reason — they are
  `D-S8-1`(a) reproducibility gates and they need a *run* to reproduce. **8.3, the uninjected control
  campaign, is now unblocked and is the next work item.**
* 🔴 The `D-S8-3` follow-on (clamp the 12 `glazing_does_not_fit` rows) is still open and still needs a
  ruling.
* 🔴 **Decision 14 (chaining) is still open** and still closes here, on a watt.
* ⚪ `RL27` is unvetted in full, not only B12.
* `prereg.md` untouched, md5 `e4243e07cdd80c9c846b91f40e3e8c45`.

Artefacts: `tools/4thJ_step8_weather.py` (new), `tools/4thJ_step8_weather_selftest.py` (new),
`outputs_step8/weather/*.epw` (3), `outputs_step8/weather/_cache/` (44 zips, kept so the md5s stay
checkable), `outputs_step8/weather_manifest.csv` (new), `outputs_step8/weather_selection_report.json`
(new, all 44 candidates including the losing 41), `tools/4thJ_step8_idf.py` (3 comment corrections),
`tools/4thJ_step8_idf_selftest.py` (docstring), `outputs_step8/archetypes/*.idf` (88 rebuilt),
`outputs_step8/archetype_idf_manifest.csv` (`.bak_ds84` holds the pre-rebuild manifest),
`Step8_docs/docs/2026-08-25_D-S8-4_weather-basis-and-station-selection.md` (new).

### 2026-08-25 (late) — 🟢 **WORK ITEM 8.3 IS DONE. `G8.0` HAS RUN, AND THE FIRST STEP 8 GATE BOARD EXISTS. 🔴 ITS PRODUCT IS `FINDING 121`, NOT A GREEN BOARD: THE UNINJECTED CONTROL IS +136.6 % ABOVE TABULA IN SPAIN AND ~30–37 % BELOW IT IN THE UK AND ITALY, AND THE SIGN FLIPS BY COUNTRY.**

Full record: `Step8_docs/docs/2026-08-25_item-8.3_uninjected-control-campaign.md`.

#### What ran

**88 archetypes, 176 EnergyPlus runs, 214.6 s, zero severe errors**, each cell on its own fold's
`D-S8-4` EPW. Engine 24.2.0 build `94a887817b`, read out of **each cell's own** `eplusout.err` and
never copied from a sibling; exe md5 recorded in the campaign header.

🟢 **No new model was built, on purpose.** `D-S8-2` item 5 was ruled (c) precisely so that `f = 0`
would be an **endpoint of the pre-registered sweep** rather than a separately constructed control.
So the 88 IDFs ran **byte-identically** to the 8.1 artefacts, and the selftest re-hashes all 88 on
disk afterwards (`C20`) to prove nothing drifted.

🟢 **Every cell ran twice** — fresh process, different output directory, different working directory,
freshly copied IDF — because `D-S8-1`(a) recast `G8.1`–`G8.4` as reproducibility gates against *a
re-run of the same cell*, and that reference did not exist. It exists now.

#### 🔴 What it measured, and why it is not a defect

The reference `FINDING 44` never examined was already on this laptop: **`tabula-calculator.xlsx`
publishes `q_h_nd`, the annual heating energy need in kWh/(m²·a), for every building variant** —
86 of 86 of our distinct codes, measured not assumed. That is an **as-modelled reference of the same
quantity**, computed from the archetype and never from our schedules, so it cannot invert the way the
flat-4.0 foil and the control itself do.

| fold | n | control | TABULA `q_h_nd` | dev | absolute | above | E+ heating h | TABULA implied h |
|---|---|---|---|---|---|---|---|---|
| `es` | 24 | **24.92** | 10.91 | **+136.6 %** | +17.1 | **21 of 24** | 2,901 | **539** |
| `uk` | 32 | **104.47** | 165.93 | **−29.6 %** | −37.7 | **0 of 32** | 6,117 | 5,832 |
| `it` | 32 | **81.00** | 168.49 | **−36.7 %** | −55.0 | **0 of 32** | 4,784 | 4,176 |

🔴 **`FINDING 121`.** The split is total and it is aligned with country, therefore with the LOCO fold:
a **166-percentage-point spread**, larger than `FINDING 110`, `117` or `120`. Per-cell ranges `es`
−33.8…+791.5 %, `uk` −51.9…−10.0 %, `it` −67.9…−8.9 %; the Spanish outlier is `es_AB_ES06`, where
TABULA's own answer is 2.73 kWh/(m²·a), which is why the absolute column sits beside the percentage.

🟢 **The Spanish mechanism is measured, not hypothesised** — `FINDING 119` from the other end. TABULA
counts gains only inside its own heating season, recoverable as `q_int × 1000 / phi_int`, and for
`ES.ME` that returns **539 h = 22.4 days**, its published `HeatingDays`. EnergyPlus with a 20 °C
set-point heats **2,901 h**, 5.4× as long. The UK (1.05×) and Italy (1.15×) nearly agree on season
length, so season length explains nothing there, and this campaign does not claim to have decomposed
what does.

#### 🔴 Four conventions nobody ruled, each measured, none applied

`tools/4thJ_step8_control_diagnostics.py`, one knob at a time, in temporary directories, **no IDF on
disk modified and no band moved** — `G8.0` forbids exactly that.

| knob | change | `es` | `uk` | `it` |
|---|---|---|---|---|
| `D1` timestep, all 88 cells | `Timestep, 6` → `1` | −4.13 % | **+5.63 %** | −3.66 % |
| `D2` solar | SHGC 0.70 → 0.001 | +60.50 % | +27.62 % | +23.55 % |
| `D3` ground | E+'s 18 °C default → EPW monthly means | **+33.52 %** | +1.72 % | +15.71 % |
| `D4` gains | `phi_int` 3.0 → 0.0 W/m² | +40.54 % | +19.68 % | +20.08 % |

* 🔴 **`FINDING 122`** — the simulation timestep is a free parameter and **its sign differs by fold**
  (the UK moves opposite to Spain and Italy), so it does not divide out of a cross-fold ratio.
  `Timestep, 6` was never ruled; it arrived with the IDF writer.
* 🔴 **`FINDING 123`** — no `Site:GroundTemperature` object is written, so EnergyPlus uses its own
  **constant 18.0 °C** and says so once in every error file. Replacing it with the EPW's monthly means
  is worth **+33.5 / +1.7 / +15.7 %** — a **20× country spread**, and in Spain that single invisible
  default is worth more than switching the entire internal gain off is worth in the UK.
* 🔴 **`FINDING 124`** — `Temperature out of range (PsyPsatFnTemp)`, input −107.10 °C, in **all 32
  Italian cells and no others**. Isolated by measurement: a Spanish IDF on the Torino EPW reproduces
  it, an Italian IDF on the Valencia EPW does not; every field E+ reads in that EPW is in range with
  zero sentinels; at `Timestep, 1` it disappears; the series across that hour is smooth. It is a
  sub-hourly iteration artefact, it does not corrupt the result, and **`D-S8-4`'s 12/12 weather gate
  could not have caught it.** One occurrence against 88 benign ground-temperature warnings — ranking
  by frequency would have buried it, which is the whole of `V8.f`.
* 🔴 **`FINDING 125`** — `D-S8-2` item 5 holds the **annual mean of `phi_int` at exactly 3.0 W/m² at
  every `f`**, so the sweep redistributes gain in time and can never add or remove any. `D4` measures
  what the entire gain is worth: **+40.5 / +19.7 / +20.1 %**. **The whole occupancy channel is
  therefore bounded above by those numbers, and the "15 to 50 % on annual space heating" this document
  quotes as "the size of the effect this paper is manipulating" is unreachable at the top end in two
  folds of three.** ⚪ Says nothing about **peak** demand, a different quantity with no annual-mean
  constraint — that is where the 100–300 % lives.

#### The gates, and the twelve times they were seen failing

**1,232 band rows, 0 gate-cell FAILs over 88 cells.** Selftest **29 ok / 0 FAILED**; injection battery
**12 of 12 HIT, 0 no-ops, baseline scored clean first, coverage clause PASS** — scale the re-run 1.2×
→ `G8.1`(+`G8.2`,`G8.3`,`G8.4`,`G8.5`); roll it 2 h → `G8.6`(+`G8.4`); copy another cell's manifest
→ `G8.14`; delete the `fold` field → `G8.14`; a floor area from another geometry → `V8.d`; zero an
end-use row → `G8.10`; an `invalid`/`not found` line → `G8.11`; a severe error → `G8.15`; a
`Schedule:File` with interpolation on → `G8.13`; over-declare the cell count → `V8.a`; claim an engine
the `.err` denies → `G8.14`; disagree the two heating series → `V8.x`.

🔴 **`G8.1`–`G8.6` all read exactly 0.** EnergyPlus is deterministic and a clean re-run must give that,
so **these are tripwires, not accuracy measurements** — the thresholds sit five to thirty points away
from where any honest re-run lands. Said out loud rather than left for someone to misread as accuracy.

⚪ `G8.13` is **NOT_EVALUABLE**: the control uses `Schedule:Constant` only, which carries no
interpolate field. Vacuously clean, **declared rather than claimed** — `FINDING 95`'s lesson from
Step 7. `G8.8`/`G8.9` await 8.4; `G8.12`/`G8.16` await 8.5, and `V8.g`'s arm is already armed because
every control manifest carries an explicit `fold` field.

#### 🔴 `D-S8-5` is open, and it blocks nothing

1. **`G8.7` has no numeric band anywhere in this project** — measured by grep over every `.md` here,
   over `Prompts/RESUME.md` and over the parent overview; `prereg.md` has no Step 8 clause at all. The
   scorer emits `NO_THRESHOLD_PREREGISTERED` and `tools/4thJ_step8_bands.py` holds
   `G87_TOLERANCE_PCT = None` on purpose: choosing a number now, with the control values in hand, is
   band-fitting. **Recommended (a): report `G8.7` as INFO with no band, permanently**, with §4.2 as a
   stated model-to-model difference and `FINDING 121` as a limitation.
2. **`G8.5` and `G8.6` still name no reference.** `D-S8-1`(a) re-pointed `G8.1`–`G8.4` and left these
   two as they were. 🔴 A ±15 % peak band scored against the control **fails exactly when the paper's
   claim succeeds** — the same inversion `FINDING 44` caught, still live in two gates. Recommended:
   extend `D-S8-1`(a) verbatim to them and report the injected-vs-control peak difference as a result,
   ungated.

#### What was NOT done

No injected cell, no scenario, no schedule — 8.4's two probes come first. No band moved, no threshold
edited, no convention of §5 applied. `Step6_docs/outputs_step6/prereg.md` untouched, md5
`e4243e07cdd80c9c846b91f40e3e8c45` verified before and after. Backups verified non-empty before
editing: `4thJ_08_bemSimulation.md.bak_83`, `4thJ_08_bemSimulation_val.md.bak_83`,
`Prompts/RESUME.md.bak_83`.

⚪ Recorded, not a finding: `Step8_docs/IMP_step8/` is an **unvetted research lane** — its dossier
specifies EnergyPlus 9.2, OpenUBEM and multi-zone geometry, all three of which contradict rulings this
project has already made and built against. It is cited by no governing document. Treat it as `RL27`
is treated.

---

### 2026-08-25 (late, addendum) — 🟢 **`D-S8-5` RULED BY THE AUTHOR, BOTH ITEMS, AND APPLIED IN THE SCORER THE SAME DAY. NO THRESHOLD MOVED, AND THE ONE GATE THAT COULD HAVE HAD A BAND FITTED TO IT IS NOW BARRED FROM EVER HAVING ONE.**

The ruling is recorded by the author in §10 of
`Step8_docs/docs/2026-08-25_item-8.3_uninjected-control-campaign.md`. It is reproduced here because
this file is what a later reader greps.

#### Item 1 — `G8.7`: **(a)**, INFO permanently, no band ever

`G8.7` reads *"per-archetype EUI vs published band — as-modelled = PASS, empirical = INFO"* and
names **no numeric band anywhere in this project**. The author ruled that none is created: the gate
is reported as **INFO**, permanently.

🟢 **The reason is on the record and it is a methodological one, not a convenience.** EnergyPlus
hourly-dynamic simulation against TABULA's monthly quasi-steady-state `q_h_nd` is a **model-to-model
structural comparison, not a pass/fail compliance test** — `FINDING 121`'s +136.6 % / −29.6 % /
−36.7 % is dominated by heating-season definition (Spain: 2,901 h against TABULA's 539 h), which is
a difference of method. It is published as a **declared methodological limitation** in the paper's
methods and limitations sections, with the median discrepancies quoted, rather than scored.

🔴 **What this forecloses.** Picking a tolerance now, with the control numbers already in hand,
is band-fitting — the failure `G8.0` exists to prevent. `G87_TOLERANCE_PCT` therefore stays `None`
permanently, and selftest check `C16` was **strengthened to guard the band itself**: it now fails if
the threshold column ever stops being empty or if `G87_TOLERANCE_PCT = None` ever leaves
`tools/4thJ_step8_bands.py`. A future edit that fits a number to the answer trips a check.

#### Item 2 — `G8.5` / `G8.6`: **approved**, `D-S8-1`(a) extends verbatim

`D-S8-1`(a) re-pointed `G8.1`–`G8.4` at an independent re-run on 2026-08-20 and left `G8.5` and
`G8.6` untouched; the author has now extended it to them **verbatim**. Reference = the independent
re-run of the same cell. **Thresholds unmoved: ±15 % magnitude, ≤ 1 h timing.**

🔴 **This is the `FINDING 44` inversion, closed in the last two gates it was still live in.** A
±15 % peak band scored against the flat control **fails exactly when the paper's claim succeeds** —
the whole point of 8.5 is that occupancy moves the peak. Under the ruling the peak *shift* is a
**primary empirical result, reported and not gated**; the gate stays a reproducibility tripwire on
identical re-runs, where a 15 % deviation means broken wiring and nothing else.

#### Applied, and re-verified rather than asserted

| file | change |
|---|---|
| `tools/4thJ_step8_bands.py` | `EVALUABLE_AT_CONTROL` and `PROVENANCE` for `G8.5`/`G8.6`/`G8.7` re-worded to the ruling; the module docstring's refusal is now a **ruling**, not an open question; `G87_TOLERANCE_PCT = None` marked permanent |
| `tools/4thJ_gates_step8_control.py` | `G8.7` verdict `NO_THRESHOLD_PREREGISTERED` → **`INFO`**; `G8.5`/`G8.6` reference string now names `D-S8-5` item 2 → `D-S8-1`(a) and their note says *"reproducibility tripwire; peak shift is reported, not gated"* |
| `tools/4thJ_step8_control_selftest.py` | `C16` now asserts **INFO, never PASS or FAIL, empty threshold, and `G87_TOLERANCE_PCT = None` still in the bands source** |

Re-run after the change, not before: scorer → `control_bands.csv` **1,232 rows**, `G8.7` **INFO = 88**,
`G8.5`/`G8.6` **PASS = 88**, **RESULT: 0 gate-cell FAILs over 88 cells**. Selftest → **29 ok, 0
FAILED**, **12 of 12 injections HIT**, no no-ops, baseline clean, coverage clause PASS. 🟢 Nothing
about the campaign was re-run and no number changed — only how two gates are *reported*.

⚪ Backups, verified non-empty first: `tools/4thJ_step8_bands.py.bak_ds85`,
`tools/4thJ_gates_step8_control.py.bak_ds85`, `tools/4thJ_step8_control_selftest.py.bak_ds85`.
🟢 `prereg.md` untouched, md5 `e4243e07cdd80c9c846b91f40e3e8c45`.

🔴 **What is still open here:** the `D-S8-3` follow-on (clamp the 12 `glazing_does_not_fit`
rows), the `D-S8-4` follow-on (top-`k` station mean or a reported band), and **decision 14 (chaining),
which still closes in this step, on a watt.** Work item **8.4, the two probes, is next and unblocked.**

---

### 2026-08-25 (late, second addendum) — 🟢 **WORK ITEM 8.4 IS DONE. `G8.8` AND `G8.9` WERE EACH SEEN FAILING, AND THE PROBING FOUND THREE DEFECTS.**

**6 EnergyPlus runs on one archetype (`es_AB_ES01`, its own fold's EPW, real Step 7 presence files
from the fold that held Spain out), 7.2 s, 0 severe errors, 10 of 10 checks ok.**

| probe | good arm | 🔴 broken arm |
|---|---|---|
| `G8.8` scenario differentiation | `f = 0.00` vs `f = 1.00`, injected properly → the result files **differ**; `G8.10` stays clean **non-vacuously** | a third scenario **declared at `f = 0.50` and wired to the `f = 1.00` schedule file** → byte-identical result files, **`G8.8` FELL** |
| `G8.9` stale-output guard | key = every input that can change the result. MISS → **HIT** (the cache is proved to cache *before* anything else) → change the schedule → key moves, cell **re-runs** | key = **the cell name alone** → HIT on the same key, stale directory handed back, results belonging to a schedule no longer wired in, **`G8.9` FELL** |

⚪ `G8.8` is scored only over runs that **actually executed**, so on the stale arm it reports
`NOT_EVALUATED` rather than a pass it did not earn — which is what keeps the two gates independent,
exactly as the validation document's perturbation table requires.

🟢 **The scenario path and its cache key are `tools/4thJ_step8_scenario.py`, and 8.5 imports it
rather than re-implementing it** — so the thing the probes proved is the thing that runs the
campaign. The multiplier `m(t) = (1-f) + f·g(t)/mean(g)` has mean exactly 1.0 **by construction and
by assertion**, so the design level never moves and the annual mean of `phi_int` stays exactly
3.0 W/m² at every `f`, as pre-registered. 🔴 `ScheduleTypeLimits Frac` is 0.0–1.0 and EnergyPlus
**clips** to it; `m(t)` reaches 1.182 on the probe's household, so a separate `PhiMult` limit is
written and the injector **refuses `Frac` by name**.

#### 🔴 What the probing found

* **`FINDING 126` — `G8.13` could not see its own violation on the only shape that matters.** The
  parser read only the LAST comma-field. That is where `Interpolate to Timestep` sits on a
  `Schedule:File` written *without* the optional `Minutes per Item` — the shape 8.3's `I9` used, so
  the gate was recorded as *seen firing*. On a real 9-field object the `Yes` was invisible and the
  row read **PASS**. Two causes, both fixed **additively**: the field is read by position for
  `Schedule:File`, and comments are stripped **per line** first (IDF writes `value,  !- Field Name`,
  so a trailing comment belongs to the field *before* the comma). New injection **`I13`** uses the
  shape the real injector writes; `I9` still fires; battery now **13 of 13**.
* **`FINDING 127` — `G8.10`'s note read "worst fuel: all zero" on all 88 control cells while the gate
  was live.** `worst_fuel` was only assigned when a deviation *exceeded* the running worst, so an
  exact 0.0 left it empty. What was actually compared on every cell: **District Heating Water,
  97.99 GJ of end uses against a 97.99 GJ total, closing at 0.0000 %.** The gate was never broken;
  its note was, and "all zero" and "nothing to compare" are the two readings a vacuity guard exists
  to keep apart. The note now counts the fuels **actually** compared and says `VACUOUS` only when
  there are none.
* 🔴 **`FINDING 128` — the pre-registered sweep is a PEAK channel, not an annual-energy channel.**
  Across the full sweep width (`f = 0.00 → 1.00`) on this archetype: annual heating **+1.60 %**
  (97.99 → 99.56 GJ), peak **+10.84 %**, peak hour 8672 → **8671**. This sharpens `FINDING 125` from
  a ceiling into a measurement — the annual mean is held at 3.0 W/m² by construction, so the sweep
  **redistributes** rather than adds. ⚪ One archetype, one household, one fold — **not a campaign
  result**; 8.5 measures it over 88 × 5. What it does establish is where to look.
* **`FINDING 129` — `f = 0` reproduces the 8.3 control byte-for-byte.** `series_hourly.csv` from the
  injected `f = 0.00` run is byte-identical to `control/es_AB_ES01/series_hourly.csv`. 🟢 That is
  `D-S8-2` item 5 (c)'s whole point, measured: `f = 0` is an **endpoint of the sweep**, not a second
  control, so "the control was built differently" is not available as an objection to 8.5.

#### Re-verified by running, not asserting

Probes → **PASS, 10 of 10, 6 runs, 0 severe**. 8.3 re-scored after the two scorer edits →
**1,232 rows, 0 gate-cell FAILs over 88 cells**. Selftest → **29 ok, 0 FAILED, 13 of 13 injections
HIT**, no no-ops, baseline clean, coverage clause PASS. 🟢 **No campaign cell was re-run and no
measured number changed** — the `G8.10` note text changed on 88 rows; its value, threshold and
verdict did not. ⚪ Backups verified non-empty first: `tools/4thJ_gates_step8_control.py.bak_84`,
`tools/4thJ_step8_control_selftest.py.bak_84`, `tools/4thJ_step8_bands.py.bak_84`.
🟢 `prereg.md` untouched, md5 `e4243e07cdd80c9c846b91f40e3e8c45`, verified before and after.

🔴 **What 8.5 inherits.** Import `tools/4thJ_step8_scenario.py`; **name the multiplier file
deterministically per (cell, schedule, `f`)** — the key includes the injected IDF's md5, which
contains that path, so a churning name turns the cache off (the key is conservative: a false MISS
costs a run, a false HIT costs correctness). `G8.12` and `G8.16` become evaluable there for the first
time. Design the reporting around **peak magnitude and peak timing** (`FINDING 128`). Record:
`Step8_docs/docs/2026-08-25_item-8.4_the-two-probes.md`. **Work item 8.5, the injected campaign, is
next.**

### 2026-08-25 (night) — 🟢 **WORK ITEMS 8.5 AND 8.6 ARE DONE, DECISION 14 IS MEASURED, AND STEP 8'S DEFINITION OF DONE IS CLOSED ON ALL SIX ITEMS**

`tools/4thJ_step8_injected.py`, `tools/4thJ_gates_step8_injected.py`,
`tools/4thJ_step8_injected_selftest.py`, `tools/4thJ_step8_aggregate.py`,
`tools/4thJ_step8_chaining.py`, `tools/4thJ_step8_calendar_probe.py`. Local, no Speed job, no GPU.
**13,108 EnergyPlus runs in total across the three campaigns run tonight, 0 severe errors.**

| | |
|---|---|
| 8.5 injected campaign | 88 cells × 5 `f` × 10 diaries + 440 re-runs = **4,048 runs, 659 s, 0 severe** |
| 8.5 scorer | **28,161 band rows, 0 gate-unit FAILs**, coverage clause **PASS** |
| 8.5 battery | **33 ok / 0 FAILED, 18 of 18 injections HIT**, baseline copy clean first |
| 8.6 aggregate | `agg_by_fold.csv`, `agg_by_class.csv`, `agg_monthly.csv`, `agg_diurnal.csv`, `agg_peak_day.csv`, `step8_aggregate.json` |
| decision 14 | 3 folds × 6 rule points × 5 seeds × 100 dwellings = **9,000 runs, 1,530 s, 0 severe** |
| calendar probe | **60 runs**, what `FINDING 131` was worth |

🔴 **Read `Step8_docs/docs/2026-08-25_items-8.5-8.6_injected-campaign-and-aggregate.md` and
`Step8_docs/docs/2026-08-25_decision-14_chaining-on-a-watt.md` before quoting any of it.** In
particular: `FINDING 134` forbids every annual occupancy claim, and `FINDING 133` supersedes
`FINDING 128`'s magnitudes.

⚪ `prereg.md` untouched, md5 `e4243e07cdd80c9c846b91f40e3e8c45`, verified before and after. No
threshold moved, no checker edited to make a gate pass, no band created. Backups verified non-empty
before every edit: `.bak_85` on the step document, the validation document, `RESUME.md`,
`tools/4thJ_step8_bands.py`, `tools/4thJ_step8_scenario.py`, `tools/4thJ_step7_schedules.py` and
the Step 7 document; `.bak_leg5` on `tools/4thJ_step8_injected.py` and `tools/4thJ_step8_probes.py`.
