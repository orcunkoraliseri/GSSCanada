# 3rd Journal — Step 8 (EnergyPlus Simulation, Two-Channel) — SCOPING DRAFT

**Status: scoping draft for manager review, 2026-06-26**

> This is a PLANNING document only. No simulation code has been written or run. No cluster jobs have been submitted. All architectural choices are flagged either as carried-over-from-J2 (design-locked) or as [DECISION NEEDED] for manager resolution before the employee build prompt is written.

---

## 1. Aim

Step 8 delivers EnergyPlus energy simulation results for **both channels** of the 3J Leg-2 two-channel occupancy pipeline: the **residential (AT_HOME, REPLACE)** channel and the **office (AT_WORK, MODULATE)** channel. For the residential channel, per-household occupancy and metabolic schedules from Step 7 drive four dwelling archetypes across six Canadian climate zones — mirroring the J2 Step-8 paired Monte-Carlo design but for two scenarios (2022 and 2030 × 3 WFH bands) rather than five historical cycles. For the office channel, a new script `office_integration.py` reads the aggregate workforce-presence multiplier from Step 7 and injects it as the temporal schedule into office-archetype IDFs while preserving NECB/ASHRAE code-compliant peak densities (people/m², LPD, plug). The primary contribution is **load shape** — hourly profiles, peak-hour timing, and the WFH-band energy spread — not annual EUI, which mirrors J2's methodological argument.

---

## 2. Inputs

### 2a. Step-7 deliverables (schema confirmed from CSV headers)

**Residential REPLACE — 4 files in `Step7_docs/outputs_step7/`:**

| File | Rows | Schema (13 cols) |
|---|---|---|
| `BEM_Schedules_2split_2022.csv` | 1,114,128 (23,211 HH × 2 day-types × 24 h) | `SIM_HH_ID, Day_Type, Hour, HHSIZE, DTYPE, BEDRM, CONDO, ROOM, REPAIR, PR, MATCH_TIER, Occupancy_Schedule, Metabolic_Rate` |
| `BEM_Schedules_2split_2030_conservative.csv` | 1,114,128 | same schema |
| `BEM_Schedules_2split_2030_hybrid.csv` | 1,114,128 | same schema |
| `BEM_Schedules_2split_2030_fullyhybrid.csv` | 1,114,128 | same schema |

Key occupancy levels (from Step-7 Progress Log): 2022 WD 0.646; 2030 WD conservative 0.683 < hybrid 0.701 < fullyhybrid 0.711. Metabolic ~110 W/person all scenarios.

**Office MODULATE — 2 files in `Step7_docs/outputs_step7/`:**

| File | Rows | Schema (7 cols) |
|---|---|---|
| `office_presence_multiplier_2022.csv` | 144 (3 archetypes × 1 band × 2 day-types × 24 h) | `office_archetype, BAND, Day_Type, Hour, AT_WORK_fraction, multiplier, n_persons` |
| `office_presence_multiplier_2030.csv` | 432 (3 archetypes × 3 bands × 2 day-types × 24 h) | same schema |

Key values: 2022 weekday peak `AT_WORK_fraction`: Knowledge 0.602 / Public 0.608 / Sales 0.592. 2030 WD business-hours (9–17h): Knowledge conservative 0.588 > hybrid 0.502 > fullyhybrid 0.462; all band-monotonicity gates PASS.

`AT_WORK_fraction` is the primary schedule column (raw absolute fraction, per OD-7B locked). The `multiplier` column (peak-normalized variant) is also emitted but is not the default input.

### 2b. Weather files

**KNOWN — exists locally at `BEM_Setup/WeatherFile/`:** TMYx EPW files for 6 climate zones used in J2: Toronto 5A, Kelowna 5B, Vancouver 5C, Montreal 6A, Calgary 6B, Winnipeg 7A. The `PR_REGION_TO_EPW_CITY` mapping in `eSim_bem_utils/config.py` routes PR (region label) to EPW city for residential. The same mapping is likely reusable for the office archetypes (archetype → climate zone), but the routing logic needs a decision (see Section 9, OD-8E).

### 2c. Building/IDF stock

**Residential archetypes — KNOWN:** 4 dwelling archetypes in `2J_docs_occ_nTemp/BEM_setup/Buildings_MTL_v242/` (EnergyPlus v24.2 after the J2 v22.1→v24.2 transition chain): DetachedHouse (→ SingleD), AttachedHouse (→ OtherDwelling), ApartmentMidRise (→ MidRise), ApartmentHighRise (→ HighRise). Canadian NECB17/NBC936 Z6 construction. These are directly reusable for the J3 residential campaign.

**Office archetypes — [DECISION NEEDED, OD-8A]:** The pipeline planning docs (`3rdJ_00_2split_Occupancy_Pipeline.md` Step 8 panel; `2-channel_split.md` §1) reference **PNNL Tall / SuperTall** as the intended office IDF set, noting office floor-area share of ~30% (SuperTall) / ~24% (Tall). These IDFs exist in `BEM_Setup/Buildings/CAN_CLG` and `CAN_MTL` but their compatibility with E+ 24.2, the zone tagging (Tag-2 routing to office zones), and the NECB/ASHRAE schedule object structure have not been audited for Step 8. Alternatively, standalone NECB17 office archetypes could be sourced. This is the single most important pre-build decision. See Section 9.

---

## 3. The Two-Channel Handling

### Residential REPLACE (rides existing consumer, unchanged from J2)

The J2 `integration.py` (`eSim_bem_utils/integration.py` / versioned copy in `2J_docs_occ_nTemp/Step8_docs/eSim_bem_utils_2J/`) already handles the residential REPLACE path:
- Filters `BEM_Schedules_*.csv` by `DTYPE` to match the target archetype IDF.
- Builds `Schedule:Compact` (Through: end-of-month, For: Weekday/Weekend, hour values) from `Occupancy_Schedule` and `Metabolic_Rate`.
- Injects the schedule into the IDF's `People` object; `Number_of_People = HHSIZE`.
- The +4 h diary→clock roll is already baked into the Step-7 output (applied in `3rdJ_07_aug_to_bem_2split.py`; clock-aligned to EPW midnight).

For J3, the residential runner needs minor adaptation: four scenarios (2022 + 2030×3 bands) instead of five historical cycles, and the 3J stock has 23,211 HH (not 144,507), but the N=50 per cell pool-size check is still safe (smallest cell in J2 was 853 HH; J3's employed-enriched stock may have thinner cells — verify per archetype × region before the full run).

### Office MODULATE (new — `office_integration.py`)

The office channel is architecturally distinct. The Step-7 office multiplier table provides a **population-level aggregate** schedule (not a per-household schedule), so there is no per-HH Monte Carlo sampling for office. For each (office archetype × climate zone × scenario):

1. Read the appropriate rows from `office_presence_multiplier_{year}.csv`, filtered to `office_archetype` and `BAND`.
2. Build a `Schedule:Compact` with `AT_WORK_fraction` values as the hourly Weekday / Weekend values (24 values per day-type, no per-month variation needed beyond the two day-type blocks). The absolute `AT_WORK_fraction` IS the schedule value — it replaces the temporal shape of the NECB/ASHRAE office People schedule while the `Number_of_People` density stays at the code-compliant 25 m²/person (0.040 ppl/m²).
3. Locate and modify the relevant EnergyPlus objects in the office IDF:
   - **People object**: set `Number_of_People = NECB density × zone_area`; replace the schedule reference with the GSS-derived `AT_WORK_fraction` schedule.
   - **[DECISION NEEDED, OD-8B]** Lights and Equipment objects: the coupling formulas `L(t) = max(Lmin, η·O(t)·D(t))` and `P(t) = Pbase + (1−Pbase)·O(t)` are specified in the pipeline docs (`2-channel_split.md` §3.7; `3rdJ_00_2split_Occupancy_Pipeline.md` Step 7 panel) but whether to implement them in Step 8 or defer to Step 9 is unresolved (OD-7D deferred the Step-9 activity-load columns from the residential schema; similarly for office plug/light floors).
4. Apply Tag-2 routing: `apartment*` spaces → residential REPLACE; office-tagged spaces (OpenOffice, ClosedOffice, Conference, Dining, Classroom, Restroom) → office MODULATE; Hotel/Retail → skip (Leg 3); service/MEP/circulation → leave baseline unchanged.
5. Write modified IDF to a per-scenario temp location; run EnergyPlus via the Singularity SIF.

---

## 4. `office_integration.py` Responsibilities — Bullet Spec

- **Inputs:** `office_presence_multiplier_{year}.csv` (Step-7 output); office archetype IDF file(s) (PNNL Tall/SuperTall or NECB standalone — [OD-8A]); EPW path for the climate zone; target `office_archetype` label and `BAND` string; output directory.
- **Schedule construction:** read `AT_WORK_fraction` for the target `(office_archetype, BAND, Day_Type, Hour)` cells; build a `Schedule:Compact` object with `Through: 12/31`, `For: Weekday`, 24 hourly values from the Weekday rows, `For: Weekend`, 24 hourly values from the Weekend rows. No per-month variation (aggregate schedule is day-type only).
- **IDF editing (eppy / geomeppy):** iterate over IDF `PEOPLE` objects; for each office-tagged zone, (a) confirm `Number_of_People_Calculation_Method = People/Area` and peak density = 0.040 ppl/m² (NECB17), (b) replace the existing schedule reference with the new GSS-derived `Schedule:Compact` name, (c) do NOT touch `Number_of_People` — preserve the code-compliant density. [DECISION NEEDED, OD-8B]: whether to also edit `LIGHTS` and `ELECTRICEQUIPMENT` objects using the Lmin/Pbase coupling formulas.
- **Zone routing gate:** assert that only office-tagged zones are modified; apartment/MEP/circulation zones must be unchanged. Flag any zone with ambiguous tags for manager review.
- **Outputs:** modified IDF file (one per archetype × BAND × year combination, written to a temp working dir before the EnergyPlus run); a provenance log (which archetype, which BAND, which rows of the multiplier CSV were consumed, n_persons per cell).
- **Dependencies:** `eppy` (already in the cluster env per `3rdJ_04` precheck history); no new packages needed.

---

## 5. Run Matrix

### Scenario enumeration

| Scenario label | Year | WFH band | Residential file | Office BAND |
|---|---|---|---|---|
| 2022 (baseline) | 2022 | observed | `BEM_Schedules_2split_2022.csv` | "observed" |
| 2030-conservative | 2030 | conservative (17.5% WFH) | `BEM_Schedules_2split_2030_conservative.csv` | "conservative" |
| 2030-hybrid | 2030 | hybrid (30% WFH) | `BEM_Schedules_2split_2030_hybrid.csv` | "hybrid" |
| 2030-fullyhybrid | 2030 | fullyhybrid (40% WFH) | `BEM_Schedules_2split_2030_fullyhybrid.csv` | "fullyhybrid" |

**Total: 4 scenarios.**

### Residential campaign (Monte Carlo, paired design — mirrors J2)

| Dimension | Levels | Count |
|---|---|---|
| Dwelling archetype | SingleD, MidRise, HighRise, OtherDwelling | 4 |
| Climate-zone city | Toronto 5A, Kelowna 5B, Vancouver 5C, Montreal 6A, Calgary 6B, Winnipeg 7A | 6 |
| Scenario | 2022, 2030-conservative, 2030-hybrid, 2030-fullyhybrid | 4 |
| Monte-Carlo households (paired per cell) | N=50, same SIM_HH_IDs across all 4 scenarios | 50 |

**Residential total: 4 × 6 × 4 × 50 = 4,800 EnergyPlus runs.**

Paired design: sample N=50 `SIM_HH_ID`s once per (archetype × climate-zone) cell, then run all 4 scenarios against the same household IDs in the same archetype IDF under the same TMY weather. Per-household 2022→2030 deltas are within-household differences; the WFH band spread is directly attributable to the occupancy multiplier. The 3J residential stock has 23,211 HH; pool sizes by (DTYPE × PR) must be verified to confirm all 24 cells are ≥ 50 before the campaign is launched [OD-8F].

### Office campaign (aggregate schedule — no per-HH MC)

The office multiplier is a population-level aggregate (not per-household), so the office simulation is deterministic per (archetype × climate zone × scenario). One EnergyPlus run per combination:

| Dimension | Levels | Count |
|---|---|---|
| Office archetype IDF | [DECISION NEEDED, OD-8A] — e.g. PNNL Tall, PNNL SuperTall | 2 (if PNNL Tall/SuperTall) or 3 (if per-archetype standalone) |
| Climate-zone city | Same 6 cities as residential [OD-8E] | 6 |
| Scenario | 2022, 2030-conservative, 2030-hybrid, 2030-fullyhybrid | 4 |

**Office total (illustrative): 2 building types × 6 CZ × 4 scenarios = 48 EnergyPlus runs** (or 3 × 6 × 4 = 72 if per-archetype standalone IDFs).

**Grand total estimate: ~4,848–4,872 EnergyPlus runs.**

> **J2 reference:** J2 ran 4 × 6 × 5 × 50 = 6,000 runs. J3 is smaller on the residential side (4 scenarios, not 5 years) and the office side is deterministic (no MC). The cluster effort is comparable or slightly less than J2.

---

## 6. Cluster Execution Plan

**HARD RULES (non-negotiable):**
1. All computation submitted via `sbatch` ONLY. No `srun`, no bare `python` on the login node (`speed-submit2`). This has been flagged three times; a further violation risks account suspension.
2. Every job must request `-t 7-00:00:00` (7-day) minimum walltime. Never 1h / 1day / 48h.
3. Login shell is `tcsh`. All cluster commands must be single-line; no `\` continuation; no `2>&1` (use `>&` or omit).
4. EnergyPlus 24.2 is invoked via the Singularity SIF at `/speed-scratch/o_iseri/step9_spike/energyplus_24.2.0.sif` (`nrel/energyplus:24.2.0`). No local E+ install needed.

**Approach (modelled on J2 MidRise/HighRise cluster port, job 950097):**

- **SLURM array structure:** one task per (residential archetype × climate-zone × scenario) cell = 24 cells × 4 scenarios = 96 array tasks for residential; separate array for office (48–72 tasks depending on OD-8A). Or combine into a single array with a lookup table in the wrapper script.
- **Per-task wrapper:** a bash `.sh` wrapper that (1) extracts the IDD from the SIF at task start, (2) creates a per-task `energyplus`/`ExpandObjects` bash script pointing to the SIF, (3) sets `ESIM_WORKERS=8` (cpus-per-task) and `MPLBACKEND=Agg`, (4) calls the Python runner (`run_paired_mc.py` for residential; the new `office_runner.py` for office) via the cluster Python at `/speed-scratch/o_iseri/envs/step4/bin/python`.
- **Residential runner:** adapt `2J_docs_occ_nTemp/Step8_docs/run_paired_mc.py` — change `COMPARATIVE_YEARS` logic to the 4 scenario labels, point `STEP8_BUILDINGS_DIR` to `Buildings_MTL_v242/`, use the J3 stock (23,211 HH, `BEM_Schedules_2split_*.csv`). Resume-on-restart (check for existing N×scenarios `hourly_meters.csv`).
- **Office runner:** new script that calls `office_integration.py` to produce a modified IDF, then runs EnergyPlus once via the SIF, parses `hourly_meters.csv`.
- **Output landing:** `/speed-scratch/o_iseri/step8_2split/campaign/<cell>/` for residential; `/speed-scratch/o_iseri/step8_2split/office/<archetype>__<city>/` for office.
- **Upload checklist before sbatch:** J3 BEM schedule CSVs (4 files × ~300 MB each), office multiplier CSVs (2 small files), archetype IDFs, 6 EPWs, runner scripts, `office_integration.py`. Bundle all into one `scp -r` upload per cycle (never file-by-file uploads).

**Submission command (locally, after upload):** `sbatch /speed-scratch/o_iseri/step8_2split/run_residential_array.sh` — returns a job ID instantly, leaves nothing on the login node.

---

## 7. Outputs

### Primary outputs (load-shape novelty)

| Output | Channel | Description |
|---|---|---|
| **8760-h hourly load profiles** | Both | Heating / cooling / electricity / total per scenario, with MC bands (residential) or single run (office) |
| **Diurnal-by-season profiles** | Both | 24-h average × heating/cooling season — shows the WFH shape change |
| **Peak demand — magnitude + hour** | Both | Annual and seasonal peak load; **hour-of-peak** shift across WFH bands |
| **WFH band spread** | Office | Conservative vs hybrid vs fullyhybrid office daytime load; expected ordering: conservative > hybrid > fullyhybrid daytime peak load (WFH empties offices) |
| **Paired residential Δ (2022→2030)** | Residential | Within-HH per-scenario energy delta; confidence intervals per (archetype × CZ) |
| **Annual EUI** (secondary) | Both | kWh/m²·yr per archetype × CZ × scenario; plausibility benchmark check |
| **MC ensemble statistics** | Residential | Load factor, peak-to-average ratio, coincidence factor across the N=50 pool |

### Output file locations
- Residential: `Step8_docs/outputs_step8/campaign_N50/<cell>/` (raw) → `outputs_step8/agg/` (aggregated) → `outputs_step8/figures/`
- Office: `Step8_docs/outputs_step8/office/<archetype>__<city>/<scenario>/hourly_meters.csv`
- Validation report: `Step8_docs/outputs_step8/step8_validation_report.html`

### Handoff to Step 9 (deferred per OD-7D)

Step 9 layers activity-driven equipment and lighting loads on top of Step 8's occupancy-driven base energy. It will consume the Step 8 simulation results plus the Step-7 `BEM_Schedules_2split_*.csv` (for the residential activity columns once added) and the office presence multiplier (for office plug/light floors `Pbase`/`Lmin`). Step 8 does NOT implement `Equipment_Fraction`, `Lighting_Fraction`, `Equip_Design_W`, or `Light_Design_W` — these remain the Step-9 deliverable. Step 8 passes through the unmodified Step-7 CSVs and the E+ simulation campaign results to Step 9.

---

## 8. Validation Plan

Port the J2 `08_simulation_val.md` 8-section structure; extend with office-specific gates.

### Section 1 — EnergyPlus Run Integrity

| Gate | Threshold | Notes |
|---|---|---|
| 1.1 Completeness | 4,848–4,872 / total runs complete | 0 skipped cells |
| 1.2 No fatal errors | 0 fatals (`eplusout.end` = "Completed Successfully") | |
| 1.3 Sizing converged | No unconverged design-day warnings | same as J2 §1.3 |
| 1.4 Output completeness | Each run yields 8760-row `hourly_meters.csv` | header-only = FAIL (learned from J2 Sub-step 8G) |

### Section 2 — Schedule Injection Fidelity

| Gate | Channel | Threshold |
|---|---|---|
| 2.1 Daily-mean round-trip (residential) | Residential | Injected WD/WE daily mean = source `Occupancy_Schedule` ± 0.5% |
| 2.2 Hour alignment | Both | No off-by-origin; clock midnight matches EPW (the J2 +4 h bug is already fixed in Step 7) |
| 2.3 People-count basis (residential) | Residential | `HHSIZE × schedule ≈ expected headcount` |
| 2.4 Office density preserved | Office | `Number_of_People` in modified IDF = NECB 0.040 ppl/m² × zone area; not HHSIZE |
| 2.5 AT_WORK_fraction round-trip | Office | Injected office schedule hourly mean = source `AT_WORK_fraction` ± 0.5% |

### Section 3 — Monte-Carlo Convergence (residential only)

| Gate | Threshold |
|---|---|
| 3.1 Mean stability | Running cell mean stabilises by N = 50 |
| 3.2 CI half-width | 95% CI half-width of cell mean < 2% |
| 3.3 Pool adequacy | All 24 residential cells have ≥ 50 HH in the J3 stock |

### Section 4 — Physical Plausibility

| Gate | Channel | Reference |
|---|---|---|
| 4.1 Residential EUI range | Residential | Within NRCan SHEU published residential bands per archetype × CZ (same reference as J2 §4) |
| 4.2 Office EUI range | Office | [DECISION NEEDED, OD-8G] — NRCan SCIEU commercial buildings survey or NECB reference schedules |
| 4.3 Heating dominance | Both | Heating share rises with CZ severity (5C → 7A) |
| 4.4 Archetype ordering | Residential | EUI/area order: SingleD > MidRise > OtherDwelling > HighRise (carried from J2) |

### Section 5 — Load-Shape Sanity

Same structure as J2 §5: peak–occupancy coupling, diurnal shape plausibility, coincidence factor < 1.

### Section 6 — 2022→2030 and WFH Band Effects (the headline)

| Gate | Channel | Threshold |
|---|---|---|
| 6.1 Residential paired Δ separability | Residential | Per-HH paired Δ(2022→2030) CI excludes 0 where expected (daytime midday load) |
| 6.2 Residential direction | Residential | Higher WFH bands → higher daytime residential load, lower evening peak |
| 6.3 Office band ordering (energy) | Office | Weekday daytime energy: conservative > hybrid > fullyhybrid (WFH empties offices) |
| 6.4 Cross-channel consistency | Both | Residential daytime load rises as office load falls across WFH bands (directionally matched) |
| 6.5 Peak-hour shift | Both | Reported and explained (direction depends on WFH magnitude) |

### Section 7 — Longitudinal / Scenario Plausibility

- 7.1 2022 baseline is energy-physically reasonable vs the step-7 occupancy levels.
- 7.2 2030 conservative → hybrid → fullyhybrid spans a plausible energy range for office (non-linear: 20–50% occupancy cut yields only ~10–30% energy savings per the pipeline plan, per the fixed HVAC/plug-load baseload).
- 7.3 Residential 2030 all bands show higher occupancy than 2022 (WFH persistence) → higher residential internal gains.

### Section 8 — Summary table (PASS / WARN / INFO / FAIL per gate)

Same HTML report format as J2 `08_simulation_val.md`, generated by `3rdJ_08_simulation_2split_val.py`.

---

## 9. Open Decisions [DECISION NEEDED]

The following items could NOT be resolved from the existing docs and require explicit manager decisions before the employee build prompt is written. These are listed roughly in priority order.

**OD-8A — Office IDF templates (blocking).** The planning docs reference PNNL Tall / SuperTall as the intended office building archetypes. Are these IDFs available locally (checked: `BEM_Setup/Buildings/CAN_CLG` and `CAN_MTL` mentioned in `2-channel_split.md`)? Are they E+ 24.2 compatible (J2 required a v22.1→v24.2 transition chain for residential IDFs — the same upgrade may be needed here)? Are their Zone objects tagged for Tag-2 routing (apartment vs office vs hotel/retail)? If the PNNL Tall/SuperTall are not usable, what are the alternatives — standalone NECB17 office prototypes, or a different Canadian commercial benchmark IDF? This decision gates all of office_integration.py development.

> **MANAGER VERIFICATION (2026-06-26):** The IDFs EXIST locally — `BEM_Setup/Buildings/CAN_CLG/{Tall,SuperTall}Building_90.1-2019_6A_Buffalo_NECB17_Z7A_v221.idf` (cold-climate Z7A) and `BEM_Setup/Buildings/CAN_MTL/{Tall,SuperTall}Building_…_NECB17_Z6_v221.idf` (Z6). **They are EnergyPlus v22.1 (`_v221`), NOT v24.2** — so a v22.1→v24.2 IDF transition (same chain J2 ran for the residential stock) is required before they can run under the Step-9 SIF (`nrel/energyplus:24.2.0`). Zone tagging for Tag-2 routing still needs auditing. ⇒ OD-8A "availability" half RESOLVED (use PNNL Tall + SuperTall); remaining work = version upgrade + zone-tag audit.

**OD-8B — Lights and Equipment coupling in office (important).** The pipeline docs specify coupling formulas: `L(t) = max(Lmin, η·O(t)·D(t))` (with `Lmin = 0.10–0.20` and daylight dimming `D(t)`) and `P(t) = Pbase + (1−Pbase)·O(t)` (with `Pbase = 0.15–0.30`). Should `office_integration.py` implement these in Step 8, or defer them to Step 9 (analogous to how OD-7D deferred residential equipment/lighting to the 2-split Step 9)? If Step 8 implements them: what values for Lmin and Pbase (per archetype or fixed), and does daylight dimming `D(t)` require EnergyPlus daylighting objects in the IDF?

**OD-8C — Historical cycles for residential (scope).** Should J3 Step 8 simulate the historical cycles (2005, 2010, 2015) to tell the longitudinal COVID-break story, as J2 did? J3 does not have Step-7 BEM schedules for those years (only 2022 + 2030×3 bands). Options: (A) scope J3 Step 8 to only 2022 + 2030×3 bands (4 scenarios, ~4,800 residential runs — the J3 novelty is the office channel, not the longitudinal arc already told by J2); (B) generate 2022-base historical cycles via a J2-style `08_gen_cycle_schedules.py` port on the 3J stock (adds 3 more scenarios and raises the residential run count to 7 × 50 × 24 = 8,400, plus cluster time). Recommendation: Option A is sufficient for J3.

**OD-8D — How office archetype maps to IDF (blocking if OD-8A uses PNNL).** If PNNL Tall/SuperTall are used, all three GSS archetypes (Knowledge/Public/Sales) share the same building envelope — they differ only in the `AT_WORK_fraction` schedule values injected. Are the three archetypes run as three separate simulations with different schedules on the same IDF, or is a single average schedule used? If standalone NECB office IDFs are used, do the three archetypes map to distinct IDF templates?

**OD-8E — Climate zone mapping for office archetypes.** The residential campaign maps `PR` (region label) to EPW city. The office multiplier has no geographic dimension — it is a national aggregate per archetype × BAND × day-type × hour. For office simulations, what EPW cities are used? Same 6 as residential (Toronto 5A, Kelowna 5B, Vancouver 5C, Montreal 6A, Calgary 6B, Winnipeg 7A)? Or a representative subset (e.g., Toronto 5A + Montreal 6A as the two dominant Canadian office markets)? This determines whether office runs 6 CZ or fewer.

**OD-8F — J3 residential pool-size check per (DTYPE × PR) cell.** The J3 residential stock is 23,211 HH (vs J2's 144,507). The smallest J2 cell was 853 HH (HighRise × Prairies). The 3J employed-enriched stock may have thinner cells, especially HighRise × Northern Canada or HighRise × Atlantic. Before the campaign is built, need a pool-size audit: for each of the 24 (DTYPE × PR) cells, confirm at least 50 HH are available. If any cell has < 50, either lower N for that cell (and document), use with-replacement sampling, or exclude the cell.

**OD-8G — Commercial EUI validation benchmark.** J2 used NRCan SHEU for the residential EUI plausibility gate. What is the reference for office EUI? Candidates: NRCan Survey of Commercial and Institutional Energy Use (SCIEU), NECB reference schedules (implied EUI from the code-compliant baseline), or ASHRAE 90.1 prototype building benchmarks. This needs a sourced reference before the validator can be written.

**OD-8H — Interpolate to Timestep setting.** The Step-7 schedules are at 24-hourly resolution (48 half-hour slots averaged to 24). The EnergyPlus `Schedule:Compact` for both channels uses these 24 values. `Interpolate to Timestep = Yes` averages across the simulation timestep (compounds peak loss); `No` holds the block value (preserves the 30-min step as a step function). This open decision (#2 in `3rdJ_00_2split_Occupancy_Pipeline.md`) must be resolved and documented in Methods — it affects the injected schedule shape.

**OD-8I — Office statistical design (MC vs deterministic).** The office multiplier is an aggregate schedule — there is no per-household variability. The current scope assumes each (office archetype × CZ × scenario) cell runs once (deterministic). Is this sufficient for the paper's claims, or should we introduce Monte Carlo uncertainty on building parameters (e.g., floor area, archetype vintage) to generate confidence bands analogous to the residential MC? If MC is desired for office, what are the sampling dimensions?

**OD-8J — `eSim_bem_utils` versioning for J3.** J2 maintained a versioned copy `Step8_docs/eSim_bem_utils_2J/` to isolate J2 from the main engine. Should J3 Step 8 create an analogous versioned copy (`eSim_bem_utils_3J/`), or should it build on top of the J2 copy? Creating a separate versioned copy avoids cross-contamination and is consistent with J2 practice.

---

## 10. References

The following source documents were read to produce this scoping draft:

**J3 Leg-2 primary sources:**
- `3J_docs_occ_nTemp/Leg2_2-split/Step7_docs/3rdJ_07_bemIntegration_2split.md` — Step 7 design doc; OD-7A…E locked decisions; office MODULATE method; output schemas; connection to downstream (Step 8 wiring description)
- `3J_docs_occ_nTemp/Leg2_2-split/Step7_docs/3rdJ_07_bemIntegration_2split_val.md` — validation gates (Sections A–G); Step-7 scorecard 32/43 PASS; confirmed key occupancy/office values
- `3J_docs_occ_nTemp/Leg2_2-split/3rdJ_00_2split_Occupancy_Pipeline.md` — full pipeline plan; Step 8 PLANNED note (PNNL Tall/SuperTall; "extend paired MC to office zones"); NECB/ASHRAE coupling formulas; validation gates (ASHRAE G14 provenance)
- `3J_docs_occ_nTemp/Leg2_2-split/3rdJ_00_2split_Occupancy_Pipeline_Overview.md` — concise flowchart; Step 8 and Step 9 scope boundary; key design decisions table
- `3J_docs_occ_nTemp/Leg2_2-split/2-channel_split.md` — channel definitions; PNNL Tall/SuperTall floor-area shares; `office_integration.py` named and task-scoped; Tag-2 routing definition; NECB/ASHRAE peak density values
- `3J_docs_occ_nTemp/compare/leg2_2-split_vs_leg1/Step7_compare.md` — J2 vs J3 Step-7 comparison; confirmed CSV schemas from headers; gate scorecard cross-reference; caveats for the paper
- `3J_docs_occ_nTemp/compare/leg2_2-split_vs_leg1/README.md` — cross-step summary; green-light statement for Step 8 scope; population-scale gap caveat (23,211 vs 144,507 HH)

**J2 Step-8 reference (ported):**
- `2J_docs_occ_nTemp/08_simulation.md` — full J2 Step-8 design; paired Monte-Carlo design; experimental grid (4 × 6 × 5 × 50 = 6,000 runs); sub-steps 8A–8G; cluster port (SLURM array job 950097 with the nrel E+ 24.2 SIF); campaign runner design; risk register
- `2J_docs_occ_nTemp/08_simulation_val.md` — J2 validator structure (8 sections); gate thresholds (ASHRAE G14 NMBE/CV(RMSE) sourcing); SHEU plausibility benchmark; HTML report format

**Step-7 output CSV headers (confirmed locally):**
- `Step7_docs/outputs_step7/BEM_Schedules_2split_2022.csv` (first 4 rows read)
- `Step7_docs/outputs_step7/office_presence_multiplier_2022.csv` (first 4 rows read)
- `Step7_docs/outputs_step7/office_presence_multiplier_2030.csv` (first 4 rows read)
- `Step7_docs/outputs_step7/BEM_Schedules_2split_2030_conservative.csv` (first 4 rows read)

---

*End of scoping draft. Manager review and resolution of OD-8A through OD-8J required before the employee build prompt for Step 8 is authored.*
