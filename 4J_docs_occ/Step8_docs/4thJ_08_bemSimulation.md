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
