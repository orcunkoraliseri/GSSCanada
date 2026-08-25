# Step 8 — BEM / UBEM simulation

### 4J HETUS LLM pipeline. Implementation specification.
#### Parent: `../4thJ_00_HETUS_LLM_Pipeline.md` Step 8. Validation: `4thJ_08_bemSimulation_val.md`

---

## STATUS

**OPEN. Scoped by `RL13`.** 🟢 **2026-08-21: work item 8.1 has PARAMETER TABLES for all three folds** — `outputs_step8/archetype_parameters_{es,uk,it}.csv` (24 / 36 / 42 archetypes) with `archetype_parameter_provenance.md`. 🟢 **2026-08-21 (afternoon): `D-S8-2` item 5 RULED (c) and PRE-REGISTERED** — the `phi_int` split is a five-level sensitivity `f ∈ {0.00, 0.15, 0.30, 0.50, 1.00}` with `f = 0` as the control, annual mean held at exactly 3.0 W/m² throughout (§9 of the provenance file). The injected campaign is therefore **five times larger**: 102 archetypes × 5 = 510 archetype-runs per weather specification. 🟢 **2026-08-24 (evening): SECTION 6 IS CLOSED — ALL SIX decisions ruled.** Items 1, 3 and 4 were the last three (the header previously said five, which contradicted this file’s own 2026-08-21 entry) and were ruled `1(a)` equal-facade 1:1.5 box, `3(a)` two-layer equivalent, `4a(a)` prefer `Gen`, `4b(a)` merged rows span their declared periods — brief at `Step8_docs/docs/2026-08-24_D-S8-2_items-1-3-4_geometry-layers-archetype-selection.md`. Three new findings, all from measuring the tables rather than quoting them: `FINDING 107` Italy has **0** empty cells (42 rows, 32 cells, 10 duplicates) so 4b was UK-only; `FINDING 108` the 3 missing GB cells sit inside `AB.04-08`’s declared span; `FINDING 109` **all 36 UK archetypes carry zero South and zero North glazing** while ES/IT use all four faces — a country-correlated convention, which is what forced `1(a)`. 🔴 **No IDF exists**, **no Step 8 gate has ever been run**, no weather file is on disk, and items 8.2–8.6 are untouched. 🔴 **Decision 14 (chaining) is still open** and still closes here, on a watt.

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
