# 3rd Journal — Step 8 (EnergyPlus Simulation, Two-Channel) — VALIDATION SPEC

**Status: validation spec, 2026-06-28. Companion to `3rdJ_08_simulation_2split.md`.**

> Ports the J2 `08_simulation_val.md` 8-section structure, adds a new **§0 (historical schedule generation)** gate block for sub-step 8A, and extends every section with office-channel gates. Implemented by `3rdJ_08_simulation_2split_val.py` → `outputs_step8/step8_validation_report.html` (PASS / WARN / INFO / FAIL scorecard, same HTML format as J2).
>
> **Threshold provenance (audited 2026-06-13, carry forward):** NMBE ±5%/±10% and CV(RMSE) 15%/30% = **ASHRAE Guideline 14** — cite the standard. The `< 0.05` / ±15% / ≤1 h gates are **project-chosen**, not literature — do not cite them to any source.

---

## §0 — Historical Schedule Generation (sub-step 8A) — NEW, gates the campaign

8A must pass before any EnergyPlus run launches. These gates confirm the generated 2005/2010/2015 schedules are schema-valid and physically continuous with the existing 2022 file.

| Gate | Channel | Threshold |
|---|---|---|
| 0.1 Schema match | Both | Generated `BEM_Schedules_2split_{2005,2010,2015}.csv` = 13-col schema; `office_presence_multiplier_{2005,2010,2015}.csv` = 7-col schema, byte-identical headers to 2022 |
| 0.2 Row counts | Resid | Each historical residential file = N_HH × 2 day-types × 24 h (N_HH per that cycle's stock; report the count) |
| 0.3 Calibration applied | Both | 04L/04M raking applied per cycle (provenance log present); occupancy marginals match each cycle's observed targets within the locked Step-4 tolerance |
| 0.4 Longitudinal continuity | Both | 2005→2010→2015→2022 occupancy levels move monotonically toward the observed COVID break; no discontinuity from a generation bug (e.g., 2015 ≈ 2022 would flag a leakage error) |
| 0.5 Office historical caveat | Office | The AT_WORK gating-var difference across cycles (2005/2010 PLACE=02 vs 2015/2022 LOCATION) is documented; INFO gate, not FAIL |
| 0.6 No NaN / no empty | Both | Zero NaN in schedule columns; zero header-only files |

---

## §1 — EnergyPlus Run Integrity

| Gate | Threshold | Notes |
|---|---|---|
| 1.1 Completeness | 8,400 resid + 252 office runs complete; 0 skipped cells | report any with-replacement cells (OD-8F) |
| 1.2 No fatal errors | 0 fatals (`eplusout.end` = "Completed Successfully") | |
| 1.3 Sizing converged | No unconverged design-day warnings | as J2 §1.3 |
| 1.4 Output completeness | Each run yields an 8760-row `hourly_meters.csv` | header-only = FAIL (J2 sub-step 8G lesson) |
| 1.5 Office IDF transition | All 4 office IDFs transitioned v22.1→v24.2 with 0 transition errors | precondition for 1.2 |

---

## §2 — Schedule Injection Fidelity

| Gate | Channel | Threshold |
|---|---|---|
| 2.1 People round-trip (resid) | Resid | Injected WD/WE daily mean = source `Occupancy_Schedule` ± 0.5% |
| 2.2 Hour alignment | Both | Clock midnight matches EPW; no off-by-origin (the J2 +4 h bug is fixed in Step 7) |
| 2.3 People-count basis (resid) | Resid | `HHSIZE × schedule ≈ expected headcount` |
| 2.4 Office density preserved | Office | `Number_of_People` in modified IDF = NECB 0.040 ppl/m² × zone area — NOT HHSIZE |
| 2.5 AT_WORK round-trip | Office | Injected People schedule hourly mean = source `AT_WORK_fraction` ± 0.5% |
| 2.6 Lights coupling | Both | Injected Lights schedule = `max(Lmin, η·O·D)` within ± 0.5%; floor `Lmin` never violated (min value ≥ Lmin) |
| 2.7 Equipment coupling | Both | Injected Equipment schedule = `Pbase + (1−Pbase)·O` within ± 0.5%; floor `Pbase` never violated |
| 2.8 Code densities untouched | Office | LPD / plug W/m² and `Number_of_People` unchanged from code baseline (only temporal shape modified) |
| 2.9 Interpolate setting | Both | `Interpolate to Timestep = No` on all injected `Schedule:Compact` (OD-8H) |

---

## §3 — Monte-Carlo Convergence (residential only)

| Gate | Threshold |
|---|---|
| 3.1 Mean stability | Running cell mean stabilises by N = 50 |
| 3.2 CI half-width | 95% CI half-width of cell mean < 2% |
| 3.3 Pool adequacy | All 24 (DTYPE × PR) residential cells have ≥ 50 HH in the 3J stock; any cell < 50 documented + with-replacement (OD-8F) |
| 3.4 Pairing integrity | Same N=50 `SIM_HH_ID`s used across all 7 scenarios within a cell (paired design intact) |

---

## §4 — Physical Plausibility

| Gate | Channel | Reference |
|---|---|---|
| 4.1 Residential EUI range | Resid | Within NRCan **SHEU** residential bands per archetype × CZ (as J2 §4) |
| 4.2 Office EUI range | Office | Within NRCan **SCIEU** commercial bands / NECB reference-schedule implied EUI (OD-8G) |
| 4.3 Heating dominance | Both | Heating share rises with CZ severity (5C → 7A) |
| 4.4 Archetype ordering (resid) | Resid | EUI/area: SingleD > MidRise > OtherDwelling > HighRise (carried from J2) |
| 4.5 Office envelope ordering | Office | SuperTall vs Tall EUI ordering physically consistent (taller → higher façade exposure / different core:perimeter) |

---

## §5 — Load-Shape Sanity

Same structure as J2 §5, both channels:
- 5.1 Peak–occupancy coupling: peak hour tracks the occupancy schedule peak.
- 5.2 Diurnal shape plausibility: office weekday daytime hump + lunch dip; residential evening peak.
- 5.3 Coincidence factor < 1 (residential MC ensemble).
- 5.4 Office weekend < weekday daytime load (presence collapses on weekends).

---

## §6 — Longitudinal, COVID-Break, and WFH-Band Effects (the headline)

| Gate | Channel | Threshold |
|---|---|---|
| 6.1 Resid paired Δ separability | Resid | Per-HH paired Δ CI excludes 0 where expected (midday daytime load) |
| 6.2 Resid direction | Resid | Higher WFH bands → higher daytime residential load, lower evening peak |
| 6.3 Office band ordering (energy) | Office | 2030 weekday daytime energy: conservative > hybrid > fullyhybrid |
| 6.4 COVID break visible | Both | 2015→2022 shows the occupancy-driven load-shape break (office daytime drop; residential daytime rise) |
| 6.5 Cross-channel consistency | Both | Residential daytime load rises as office daytime load falls across WFH bands (directionally matched) |
| 6.6 Peak-hour shift | Both | Reported and explained per scenario (direction depends on WFH magnitude) |
| 6.7 Longitudinal monotonicity | Both | 2005→2015 pre-COVID trend physically smooth; 2022 is the break, not noise |

---

## §7 — Scenario Plausibility

- 7.1 2022 baseline energy-physically reasonable vs Step-7 occupancy levels.
- 7.2 2030 conservative→hybrid→fullyhybrid spans a plausible **non-linear** office energy range (20–50% occupancy cut → only ~10–30% energy savings, per fixed HVAC/plug baseload).
- 7.3 Residential 2030 all bands show higher occupancy than 2022 (WFH persistence) → higher residential internal gains.
- 7.4 Historical office (2005–2015) reconstruction uncertainty stated in the report (INFO), traceable to the §0.5 gating-var caveat.

---

## §8 — Summary Scorecard

PASS / WARN / INFO / FAIL per gate, HTML report `step8_validation_report.html`, same format as J2. A FAIL on any §0, §1, or §2 gate blocks the campaign sign-off; §4–§7 FAILs are investigated and either fixed or documented as a known limitation. Report the scorecard tally (e.g. "n PASS / n WARN / n INFO / n FAIL") in the Progress Log.

---

*End of validation spec.*

---

## Progress Log

- 2026-07-02 — §7.2 gate reworded direction-agnostic, §8E re-validated (job 1062194): 46P/1W/13I/0F — 2-split closed out.
