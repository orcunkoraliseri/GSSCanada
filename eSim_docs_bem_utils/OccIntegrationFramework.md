# Occupancy → BEM Integration Framework: SWOT Investigation Plan

**Scope.** This document audits how GSS-derived household occupancy (cycles 19/24/28/33 and the 2025 CVAE forecast) is integrated into EnergyPlus single-building and neighbourhood BEM simulations. It compares the *documented* methodology in `eSim_docs_bem_utils/DONE/` against the *actual* code in `eSim_bem_utils/` and `eSim_occ_utils/`, identifies gaps, and proposes a prioritized investigation plan in SWOT form.

**Date created.** 2026-04-07 | **Last updated.** 2026-04-08
**Audience.** Postdoctoral research team — eSim 2026 paper "Longitudinal Occupancy-Driven Energy Demand in Canadian Residential Buildings".

---

## 1. Methodology Snapshot (as actually implemented)

### 1.1 Occupancy data path

All five pipelines (`06CEN05GSS`, `11CEN10GSS`, `16CEN15GSS`, `21CEN22GSS`, `25CEN22GSS_classification`) terminate in an `*_occToBEM.py` step that produces a CSV with the same schema:

| Column | Meaning |
|--------|---------|
| `SIM_HH_ID` | Synthetic household identifier |
| `Day_Type` | `Weekday` or `Weekend` |
| `Hour` | 0–23 |
| `HHSIZE`, `DTYPE`, `BEDRM`, `CONDO`, `ROOM`, `PR` | Census-derived household attributes |
| `Occupancy_Schedule` | Fractional 0–1 (estimated concurrent occupants ÷ HHSIZE) |
| `Metabolic_Rate` | Average W/person at that hour from 14-class activity → MET map |

Generation formula (e.g., `06CEN05GSS_occToBEM.py:174-177`):

```python
estimated_count   = hourly['occPre'] * (hourly['occDensity'] + 1)
occupancy_sched   = (estimated_count / hh_size).clip(upper=1.0)
```

`occPre` is a binary "≥1 person home" mask at 5-min resolution, mean-resampled to hourly. `occDensity` is a 5-min social-density count (additional people present). `Metabolic_Rate` is the mean W/person across the activity codes recorded in the diary (`metabolic_map`, `06CEN05GSS_occToBEM.py:58-74`).

### 1.2 BEM injection path

Entry point: `run_bem.py` → `eSim_bem_utils/main.py` (menu) → either `inject_schedules()` (single building) or `inject_neighbourhood_schedules()` (batch).

Sequence per scenario:

1. **Standardize baseline** — `idf_optimizer.standardize_residential_schedules()` overwrites People/Lights/ElectricEquipment/GasEquipment/WaterUse:Equipment schedules with DOE MidRise Apartment profiles parsed from `0_BEM_Setup/Templates/schedule.json` (`idf_optimizer.py:931-1139`).
2. **Override People** — `inject_schedules` sets `Number_of_People = HHSIZE` and clears `People_per_Zone_Floor_Area` / `Floor_Area_per_Person` so EnergyPlus uses absolute counts (`integration.py:817-836`).
3. **Build TUS schedules** — `Occ_Sch_HH_<id>` (Schedule:Compact, Fraction) and `Met_Sch_HH_<id>` (Schedule:Compact, Any Number) are constructed from the per-household CSV rows and assigned to all `PEOPLE` objects.
4. **Apply load filters**:
   - **Lights** → `LightingGenerator.generate_monthly()` produces 12 monthly Schedule:Compact blocks combining the presence filter with a daylight factor (`schedule_generator.py:239-322`, `integration.py:914-964`).
   - **ElectricEquipment, GasEquipment, WaterUse:Equipment** → `PresenceFilter.apply()` (`schedule_generator.py:325-400`):

     ```python
     if presence > 1e-3:
         result = presence * default_val + (1.0 - presence) * base_load   # blended
     else:
         result = base_load                                                 # absent hours unchanged
     ```

     Partial occupancy (e.g., 1 of 5 members home, `presence = 0.20`) now produces 20% of the peak default load rather than the full DOE value. Absent hours are unaffected by TUS injection.

4b. **Thermostat setback** — `inject_setpoint_schedules()` (`integration.py`) creates per-household `HeatSP_HH_<id>` / `CoolSP_HH_<id>` schedules. Active setpoints are read from the existing IDF thermostat (typically 22.2°C / 23.9°C); setback temperatures apply during absent hours (18°C heating / 27°C cooling). Replaces `heating_sch` and `cooling_sch` references in every `ThermostatSetpoint:DualSetpoint` object.

5. **Rescale water peak flow** — `idf_optimizer.scale_water_use_peak_flow()` adjusts `Peak_Flow_Rate` so daily DHW volume converges on 220 L (`idf_optimizer.py:869-928`).
6. **Optimize / save** — `optimize_idf()`, `apply_speed_optimizations()`, `configure_run_period()`, then `idf.saveas()`.

### 1.3 Documentation vs. code — material divergences

| # | Source | What the docs say | What the code does | Severity |
|---|--------|-------------------|--------------------|----------|
| 1 | `BEM_Methodology_Paper.md §5.4` | `result = occ × MAX(default, floor) + (1−occ) × baseload` (weighted blend) | ~~Binary toggle on `presence > 1e-3`~~ → **FIXED 2026-04-08**: Code now implements blended formula `occ × default + (1−occ) × baseload` when occupied, `baseload` when absent (`schedule_generator.py:376-400`). Paper §5.4 updated to match. | ✅ Resolved |
| 2 | `BEM_Methodology_Paper.md §5.5.1` | Solar/`.stat` data is "for visualization overlays only and does not influence schedule generation" | ~~Paper text contradicted the code~~ → **FIXED 2026-04-08**: Paper §5.5.1 rewritten to correctly describe the Daylight Threshold Method (150 Wh/m² threshold, monthly scaling, floor 0.3). | ✅ Resolved |
| 3 | `Default Schedule Standardization.md` | DOE MidRise Apartment JSON (`0_BEM_Setup/Templates/schedule.json`) is the parsed baseline | ~~File absent, falling back to hardcode~~ → **FIXED 2026-04-08**: `0_BEM_Setup/Templates/schedule.json` created in OpenStudio Standards format. `load_standard_residential_schedules()` now reads from file successfully. | ✅ Resolved |
| 4 | `Default Schedule Standardization.md` | MidRise Apartment is the unaltered baseline | Lighting override branch at `idf_optimizer.py:743-751` can silently replace MidRise lighting. **DORMANT** — `DEFAULT_LIGHTING_SOURCE_IDF = "US+SF+CZ5A+elecres+slab+IECC_2024.idf"` does not exist in `Templates/`; `load_lighting_override_from_idf()` returns `None` and override is skipped at runtime (`idf_optimizer.py:556-631`). Risk: if the file is added later, override activates silently. | **Medium** — silent override pathway exists but is currently inactive |
| 5 | `OccIntegPlan_lightEquipDHW.md` | Standard schedules differ for Weekday vs Weekend | `standardize_residential_schedules()` writes `For: AllDays` using only the Weekday profile (`idf_optimizer.py:1004-1021`) | **Low** — DOE MidRise uses identical Wd/We anyway, but documentation overstates the implementation |
| 6 | `BEM_integration_plan.md` | "Inject specific household profiles" — implies per-occupant heterogeneity | Single People object updated with HH-aggregate fraction; no per-occupant disaggregation | **Low** — design choice, but worth disclosing |

---

## 2. SWOT Analysis

### 2.1 Strengths

**S1. End-to-end longitudinal pipeline.** Five GSS cycles (2005, 2010, 2015, 2022, 2025-CVAE) all converge on a single BEM CSV schema, enabling consistent cross-year comparison without per-cycle special-casing in the BEM layer (`integration.load_schedules()` accepts any cycle).

**S2. Standardized baseline before integration.** `idf_optimizer.standardize_residential_schedules()` rewrites every IDF (single building or neighbourhood) to the same DOE MidRise Apartment baseline *before* TUS injection. This makes "Default vs 2005/15/25" comparisons physics-consistent and is a prerequisite for the comparative claim. The fallback parser of `0_BEM_Setup/Buildings/*.idf` on neighbourhood runs is a thoughtful bridge for IDFs that lack residential schedules.

**S3. Real metabolic schedules from TUS activity codes.** The 14-class `metabolic_map` (`06CEN05GSS_occToBEM.py:58-74`) is grounded in the 2024 Compendium of Physical Activities. The per-hour W/person feeds `Activity_Level_Schedule_Name`, which means the People object's heat gain is *both* presence- and activity-modulated — a noticeably better representation than the constant 95 W in the MidRise default.

**S4. Absolute headcount via `Number_of_People = HHSIZE`.** `integration.py:822-836` clears `People_per_Zone_Floor_Area` / `Floor_Area_per_Person` and sets explicit People counts. Combined with the fractional schedule, EnergyPlus computes `effective_people = HHSIZE × frac × W/person`, which is dimensionally correct and avoids the "people-density" trap of generic templates.

**S5. Dynamic per-household baseload.** `PresenceFilter.__init__()` computes the baseload from the *minimum DOE schedule value during this household's absent hours* (`schedule_generator.py:355-374`), with a 9 AM–5 PM fallback when the household is never absent. This avoids hard-coded constants and makes the absent-hour load shape a property of the household, not the analyst.

**S6. Comparative-mode household matching for like-for-like Default vs Year deltas.** `find_best_match_household()` SSE-matches GSS households against `TARGET_WORKING_PROFILE`, ensuring that the Default scenario's implicit 9-to-5 working day is paired with TUS households whose gross presence shape is similar. Cross-year deltas then reflect *behavioural and technological* drift rather than gross schedule mismatch.

**S7. Parallel batch execution + reproducible IDF preparation.** `simulation.py` uses `concurrent.futures` for the four scenario IDFs; `idf_optimizer` is deterministic (cached `_STANDARD_SCHEDULES_CACHE`), version-pins to E+ 24.2, and injects a consistent set of 7 output variables for end-use breakdowns.

**S8. Daily DHW volume re-anchoring.** `scale_water_use_peak_flow()` rescales `Peak_Flow_Rate` so that the integral of the schedule equals a 220 L/day target. This prevents the prior "100×" DHW spike issue and ensures cross-scenario DHW comparisons are normalized to the same physical reference.

**S9. Seasonal lighting via 12 monthly Compact blocks.** `create_monthly_compact_schedule()` and `LightingGenerator.generate_monthly()` write proper EnergyPlus `Through:` blocks (`Through: 1/31`, `Through: 2/28`, …) so lighting demand naturally tracks Canadian winter/summer daylight asymmetry.

**S10. Modular, low-coupling architecture.** `integration.py` orchestrates, `schedule_generator.py` owns the per-end-use logic, `idf_optimizer.py` owns IDF mutation, `simulation.py` owns the runner, `plotting.py` owns reporting. This makes the framework testable end-use by end-use.

---

### 2.2 Weaknesses

**W1. Binary presence threshold discards fractional information for all loads except People.**
`PresenceFilter.apply()` only checks `presence > 1e-3`. So a household with `Occupancy_Schedule = 0.20` at 14:00 (one of five members briefly home) gets *exactly* the same lighting/equipment/DHW load as a household at full capacity. The People object correctly scales heat gain by the fraction, but every other end-use is binary. The result is an inconsistent treatment of partial occupancy across end-uses within the same simulation.
**Where:** `schedule_generator.py:376-400`, `integration.py:957-1010`.

**W2. The published "weighted" formula is not implemented.** `BEM_Methodology_Paper.md §5.4` claims `result = occ × MAX(default, floor) + (1−occ) × baseload`. The only formula in code is the binary toggle from W1. If the paper text is published as-is, reviewers running the code will not reproduce it.

**W3. Lighting "solar is visualization-only" claim is wrong.** The methodology paper §5.5.1 explicitly states lighting is filtered the same way as Equipment/DHW and that solar data is for visualization only. The code uses `generate_monthly()` everywhere lighting is injected (`integration.py:915, 1224`), which actively modulates the schedule by daylight factor. The newer paper text overrides what the older `OccIntegPlan_lightEquipDHW.md` describes — and the older one matches the code.

**W4. Silent lighting override pathway (dormant but hazardous).** `load_standard_residential_schedules()` ends with an "OVERRIDE" branch (`idf_optimizer.py:743-751`) that would swap the MidRise lighting profile with a "Single Family High-Usage Lighting Schedule" parsed from `DEFAULT_LIGHTING_SOURCE_IDF`. **Verified dormant**: the referenced IDF (`US+SF+CZ5A+elecres+slab+IECC_2024.idf`) and its parent `Templates/` folder do not exist on disk; `load_lighting_override_from_idf()` returns `None` and the branch is skipped. However, if that file is added (e.g., after pulling a new model release), the override will activate silently without any code change. None of the methodology docs mention this pathway.

**W5. `For: AllDays` collapses Weekday/Weekend in standardization.** `_get_or_create_schedule()` only writes the Weekday vector. For DOE MidRise this is harmless because Weekday and Weekend are identical in the source JSON, but it makes the standardization step *structurally* unable to express weekend variation. The TUS-injection step does write separate Weekday/Weekend blocks, so the asymmetry only matters for the Default scenario.

**W6. Dead code and incomplete refactors.**
- `inject_presence_projected_schedules()` (`integration.py:741-758`) is a stub that returns immediately — it is referenced nowhere but reads as a real function.
- `idf.saveas(output_path)` orphaned at `integration.py:359` after `create_monthly_compact_schedule()` returns — unreachable but confusing.
- `_get_single_building_fallback_profiles()` has a duplicate `return` (`integration.py:679, 681`).
- `inject_neighbourhood_schedules()` contains an `if False and ...` block (`integration.py:1399-1441`) that duplicates `_update_power_densities_from_original` logic.

**W7. Comparative matching is single-building only.** `inject_neighbourhood_schedules()` does not call `find_best_match_household()`. So in neighbourhood mode, every building can be paired with an arbitrary GSS household whose gross presence shape may differ from the Default 9-to-5 baseline. This makes "Neighbourhood Default vs Neighbourhood Year" deltas systematically less interpretable than the equivalent single-building deltas.

**W8. `TARGET_WORKING_PROFILE` selection bias in single-building mode.** SSE-matching to a stereotyped 9-to-5 profile is defensible for cross-year *technology* comparisons, but it actively excludes retirees, shift workers, students, and unemployed — exactly the demographic shifts the longitudinal study is meant to capture. The methodology paper acknowledges this as a feature, but a reviewer may read it as cherry-picking.

**W9. CVAE-forecast 2025 inherits no per-row uncertainty.** `25CEN22GSS_classification` produces a single synthetic population per run. Downstream BEM consumes the CSV as if it were ground truth. There is no Monte Carlo wrapper around the CVAE outputs for sensitivity propagation.

**W10. No coupling between presence and HVAC setpoints.** Heating/cooling demand is unaffected by occupancy except through People-object internal gains (sensible heat, ~95–250 W per occupant). In a Canadian winter at -15 °C, internal gain differences are dwarfed by infiltration and conduction. Without setback-when-away logic, the longitudinal "occupancy → HVAC EUI" signal is mechanically small.

**W11. Single-building DTYPE coupling is unenforced.** `inject_schedules()` filters CSVs by `dwelling_type='SingleD'` but does not verify that the IDF geometry actually represents a single detached home. A neighbourhood IDF accidentally passed to single-building mode would silently produce nonsense.

**W12. Activity_Level fallback to 120 W when missing.** `integration.py:815` fills missing metabolic data with `120.0` W. Combined with `Number_of_People = HHSIZE`, this can leak heat gain when the schedule fraction is non-zero but the activity is undefined. Worth confirming whether `_calculate_watts` ever returns missing values for the 25CEN22GSS pipeline.

**W13. No automated regression tests for the integration layer.** `eSim_tests/` exists but there is no `test_schedule_generator.py` or `test_integration.py` referenced from the current implementation. `eSim_tests/test_integration_logic.py` (111 lines, modified 2026-04-02) is stale: it hard-codes `equipment=0.15` and `lights=0.0` as expected baseloads, which no longer match the dynamic-baseload logic introduced in `PresenceFilter.__init__()`. This test would **fail** against current code. Refactors silently change EUI without a valid tripwire.

**W14. Hardcoded baseline schedules are invisible to external audit.** `0_BEM_Setup/Templates/schedule.json` does not exist. `load_standard_residential_schedules()` falls silently to `_get_fallback_schedules()` (hardcoded 24-value Python lists in `idf_optimizer.py:757-796`). The methodology paper implies an external, auditable JSON file is the baseline source. Any reviewer who tries to reproduce the baseline from the stated source will fail — the actual values live only inside the source code.

**W15. `ClusterMomentumModel` ignores the 2021 latent centroid in velocity calculation.** In `eSim_dynamicML_mHead.py:440-443`, velocity vectors are computed only from `2006→2011` and `2011→2016` centroids. The 2021 latent population (`latent_history[2021]`) is used only to seed the forward projection (`last_population_z = latent_history[2021]`), but the 2016→2021 trajectory is never incorporated into the cluster velocities. The most recent 5-year demographic shift is therefore absent from the forecast. A corrected implementation should include a `v_newest = (centroids[2021] - centroids[2016]) / 5.0` term in the weighted momentum.

**W16. 2025 building stock distribution frozen at 2021.** `generate_future_population()` (`eSim_dynamicML_mHead.py:537-541`) explicitly samples building conditions (`bldg_conditions`) from the 2021 dataset only, with a code comment acknowledging this: *"Currently assuming 2021 building stock distribution persists."* New construction, densification (MidRise → HighRise), and retrofits between 2021 and 2025 are invisible to the forecast. This assumption is not stated in the methodology paper.

---

### 2.3 Opportunities

**O1. Replace the binary filter with the documented weighted blend.** Implementing
`load = occ × max(default, floor) + (1 − occ) × baseload`
in `PresenceFilter.apply()` would (a) make the code match the published methodology in one line, (b) finally use the fractional information already in `Occupancy_Schedule`, and (c) eliminate the discontinuity at `presence ≈ 1e-3`. Floor value can be a per-end-use constant (e.g., 0.05 for lighting, 0.10 for equipment) or per-household analogue of the existing baseload.

**O2. Continuous DHW scaling.** For DHW specifically, multiplying the DOE shape by `presence_fraction` (rather than binary) would let partial-occupancy hours produce partial demand — physically correct for showers/sinks. The peak-flow rescaler in `scale_water_use_peak_flow` already protects daily volume.

**O3. Presence-gated thermostat setback.** Add a `HVACTemplate:Thermostat`-level setback schedule constructed from the same presence vector (e.g., −2 °C heating setback when `presence < 0.2`). This is the single change most likely to amplify the longitudinal HVAC signal.

**O4. Neighbourhood-mode comparative matching.** Reuse `find_best_match_household()` inside `inject_neighbourhood_schedules()` for the comparative mode (Options 6/7). Optionally allow a *distribution* of target profiles (not a single 9-to-5 stereotype) so the neighbourhood retains demographic diversity.

**O5. Schedule:File for 8760-resolution per HH.** Instead of weekday/weekend Schedule:Compact, write 8760-row CSVs per household and reference them via `Schedule:File`. This unlocks day-of-year variation, holidays, and weather-coupled occupancy without inflating IDF size.

**O6. Per-end-use validation against measured data.** NRCan SHEU-2017, BC Hydro residential disaggregation studies, or Hydro-Québec smart-meter datasets can serve as reference EUI envelopes by end-use. The framework already produces disaggregated kWh/m²; comparing it to public benchmarks would close the validation gap.

**O7. CVAE Monte Carlo wrapper.** Run `25CEN22GSS_classification/run_step1.py:run_forecasting` N times with different RNG seeds to produce N synthetic populations, simulate each, and report EUI confidence intervals rather than point estimates. The parallel runner already supports this.

**O8. Deterministic test harness for `PresenceFilter` and `LightingGenerator`.** A `eSim_tests/test_schedule_generator.py` with fixtures for (a) always-home, (b) always-away, (c) fractional, (d) single-hour absence would catch any future regression of the documented behaviour.

**O9. Document the lighting override (or remove it).** Either delete the override branch in `load_standard_residential_schedules()` and document MidRise as the only baseline, or document the override file path, why it exists, and which scenario it activates in.

**O10. Multi-region weather sweep.** Extend the current Montreal/Toronto pair to Vancouver, Calgary, Halifax, Yellowknife. The PR column in the BEM CSV already encodes region; matching the EPW to the household's PR closes the climate-zone loop and dramatically increases external validity.

**O11. Per-occupant disaggregation.** Each GSS respondent has their own activity diary and metabolic profile. EnergyPlus supports multiple People objects per zone. Splitting one HH-aggregate People object into N per-member objects with their own activity schedule would let the paper claim "true individual heterogeneity" rather than "household-aggregate."

**O12. Tier 4 fallback flagging.** Profile matching uses Tier 1–4. Today the BEM CSV does not record which tier produced each household. Adding a `MATCH_TIER` column would let the BEM layer down-weight Tier 4 fallbacks in aggregated EUI summaries.

---

### 2.4 Threats

**T1. Methodology-paper / code drift undermines reproducibility.** The two highest-severity discrepancies (W2, W3) mean that anyone reproducing the paper from the code will get different numbers than the paper claims. For an eSim 2026 submission this is a publication-blocking issue, not a stylistic one.

**T2. Selection bias in `TARGET_WORKING_PROFILE`.** A reviewer noticing that comparative households are SSE-matched against a single 9-to-5 stereotype may flag this as cherry-picking. Mitigate by either (a) reporting the SSE distribution and demonstrating the matched subset is representative, or (b) running a sensitivity analysis with the unrestricted population.

**T3. Internal-gain-dominated HVAC delta.** Without presence-coupled setpoints (W10/O3), the cross-year HVAC EUI difference could be dominated by ~50 W per occupant of internal-gain noise. The "longitudinal occupancy-driven" headline result could be statistically weak.

**T4. DOE MidRise Apartment ≠ detached house.** Reviewers familiar with residential building energy will challenge the use of an apartment archetype as the proxy schedule for SingleD geometry. The methodology paper acknowledges this but does not quantify the bias. A robustness check (e.g., comparing MidRise vs the IECC SF Detached schedules) would defuse this.

**T5. Lighting override pathway (W4) is a paper-integrity latent risk.** The override is currently dormant (template file absent). If `US+SF+CZ5A+elecres+slab+IECC_2024.idf` is added to `Templates/` in any future model update, the override silently activates and all lighting baseline numbers change without any code edit. Either permanently remove the override branch or guard it behind an explicit flag.

**T6. Single weather file per region locks in TMYx assumptions.** Future-climate or extreme-weather sensitivity is not captured.

**T7. CVAE forecast uncertainty (W9) is hidden.** A single synthetic population for 2025 could over- or under-state behavioural change relative to 2015 just by sampling variance. Without Monte Carlo, this is invisible to the reader.

**T8. Dead code (W6) hides silent failures.** `inject_presence_projected_schedules()` looking like a real function makes future maintenance error-prone. Someone may reach for it expecting the documented behaviour.

**T9. EnergyPlus version drift via `IDD_FILE` env var.** The IDD lookup falls back to a bare `Energy+.idd` string (`integration.py:793, 1116`). If the user's environment has the wrong IDD, eppy will silently parse fields with the wrong types and produce simulations that look fine but use the wrong schedule semantics.

**T10. Neighbourhood-vs-single-building methodology asymmetry (W7) may break the neighbourhood result chapter.** If the paper presents neighbourhood EUI alongside single-building EUI as comparable, but the matching logic differs, the comparison is not apples-to-apples.

**T11. Hardcoded baseline with no external file breaks reproducibility claim (W14).** The paper's stated source (`schedule.json`) for the energy model baseline does not exist in the repository. Any attempt to independently reproduce the baseline schedules from the paper will fail. For eSim 2026 peer review, the baseline must be (a) recoverable from the repo, or (b) unambiguously described numerically in the methods section.

**T12. ClusterMomentumModel 2021 centroid omission biases the 2025 forecast (W15).** The 2016→2021 demographic shift is the most recent and most relevant signal for a 2025 projection. Excluding it means the model extrapolates from the 2006–2016 trend — a 10-year-old velocity. If demographic patterns accelerated or reversed between 2016 and 2021 (e.g., COVID-era household size shifts), the 2025 forecast will systematically miss the direction.

---

## 3. Investigation Plan

Each task uses the template from `CLAUDE.md § Task List Format`.

### ✅ Task 1 — Reconcile the documented formula with the code (W1, W2, T1)

- **Aim:** Eliminate the highest-severity doc/code drift before any 2025 results are published.
- **What to do:** Decide whether to (a) update `PresenceFilter.apply()` to implement the weighted blend `occ × max(default, floor) + (1−occ) × baseload`, or (b) update `BEM_Methodology_Paper.md §5.4` to describe the binary toggle that is actually implemented.
- **How to do:** If (a), modify `schedule_generator.py:376-400` to remove the `presence > 1e-3` branch and compute the blend per hour. Add a `floor_value` argument with end-use-specific defaults. If (b), rewrite §5.4 to drop the MAX/floor language and explicitly state the binary semantics, then re-render the methodology paper PDF.
- **Why:** A reviewer running the code from the paper must get the paper's numbers. Today they will not.
- **What it impacts:** Every Lights/Equipment/DHW/GasEquipment number in the comparative result chapter, plus the methodology section of the eSim 2026 paper.
- **Steps:**
  1. Decide direction (a) vs (b) with the supervisor.
  2. Implement the chosen path.
  3. Re-run the canonical 4-scenario comparative for households 2402 and 4270.
  4. Diff EUI deltas against the previous run.
  5. Update `BEM_Methodology_Paper.md` § 5.4 (and § 5.5.1 if path (a) extends to lighting).
- **Expected result:** Code and paper text describe the same operation; diffed EUI shows the magnitude of the change (likely small for lighting, possibly larger for equipment).
- **Test:** Add `eSim_tests/test_schedule_generator.py::test_presence_filter_blend` with a hand-checked 24-hour vector.

### ✅ Task 2 — Document or remove the lighting override (W4, T5)

- **Aim:** Restore baseline integrity before any production runs.
- **What to do:** Trace `load_lighting_override_from_idf()` and `DEFAULT_LIGHTING_SOURCE_IDF`. Confirm whether the override is active in current sims.
- **How to do:** `Grep` for `DEFAULT_LIGHTING_SOURCE_IDF` in `idf_optimizer.py`, follow the IDF path, parse the schedule it loads, compare against MidRise. Decide: keep with documentation, gate behind a flag, or delete.
- **Why:** Undisclosed baseline mutation is the kind of finding that retracts papers.
- **What it impacts:** Lighting EUI in every scenario (Default and Year), and the paper's "baseline" claim.
- **Steps:**
  1. Read `idf_optimizer.py:743-751` and `load_lighting_override_from_idf` definition.
  2. Run Option 3 (Comparative single-building) once with override active and once with `override_lighting = None` patched in; compare lighting EUI.
  3. Decide direction with supervisor.
  4. Update `Default Schedule Standardization.md` accordingly.
- **Expected result:** A clear, single-source-of-truth statement of which lighting profile is the baseline, written into both code comments and the methodology paper.
- **Test:** `eSim_tests/test_idf_optimizer.py::test_baseline_lighting_matches_midrise`.

### ✅ Task 3 — Resolve the lighting "solar visualization-only" claim (W3, T1)

- **Aim:** Make `BEM_Methodology_Paper.md § 5.5.1` factually correct.
- **What to do:** Either keep the existing daylight scaling and rewrite §5.5.1 to describe it (matching `OccIntegPlan_lightEquipDHW.md §2`), or strip daylight scaling from `LightingGenerator.generate_monthly()` and use the plain presence filter for lighting.
- **How to do:** Read `schedule_generator.py:239-322`. If keeping: rewrite §5.5.1 to describe threshold 150 Wh/m², floor 0.3, monthly Compact blocks. If stripping: revert lighting to `PresenceFilter.apply()`.
- **Why:** Two methodology docs in the repo currently disagree about how lighting is generated; the code matches the older one.
- **What it impacts:** Lighting EUI and the seasonal lighting story in the paper.
- **Steps:**
  1. Decide direction with supervisor.
  2. Update code or text accordingly.
  3. Re-run lighting comparative.
- **Expected result:** A single, correct lighting methodology section.

### ✅ Task 4 — Add presence-gated thermostat setback (O3, T3)

- **Aim:** Make the longitudinal HVAC EUI signal large enough to discriminate cycles.
- **What to do:** Construct a heating/cooling setback schedule from each household's presence vector and inject it as the `Heating_Setpoint_Schedule_Name` / `Cooling_Setpoint_Schedule_Name` of the existing `HVACTemplate:Thermostat` (or `ThermostatSetpoint:DualSetpoint`).
- **How to do:** Add `inject_setpoint_schedules()` in `integration.py`. For each hour: setpoint = home_setpoint when `presence > 0.5`, else setback (e.g., 18 °C heating / 27 °C cooling). Read the existing thermostat object, replace its schedule references, save.
- **Why:** Without this, internal gain alone determines the HVAC delta — physically small in Canadian climates.
- **What it impacts:** Heating and Cooling EUI in every scenario; magnifies the longitudinal signal.
- **Steps:**
  1. Inspect existing thermostat objects in a representative IDF.
  2. Implement the new helper.
  3. Run a single building 4-scenario comparative.
  4. Quantify ΔHVAC vs the no-setback baseline.
- **Expected result:** Heating EUI Default-vs-Year delta increases; cooling possibly too.
- **Test:** `test_inject_setpoint_schedules` confirming setpoint vector matches presence vector.

### Task 5 — Extend comparative matching to neighbourhood mode (W7, T10)

- **Aim:** Make Neighbourhood and Single Building comparatives methodologically identical.
- **What to do:** Reuse `find_best_match_household()` in `inject_neighbourhood_schedules()`, applying it per-building during the schedules-list construction step in `main.py`.
- **How to do:** Locate where `schedules_list` is built for Option 6/7. For each building, run SSE matching against `TARGET_WORKING_PROFILE` (or per-building target) and replace the chosen household.
- **Why:** Reviewers will compare single-building and neighbourhood EUI side by side; the paper needs them to be apples-to-apples.
- **What it impacts:** All neighbourhood comparative results.
- **Steps:**
  1. Identify schedules_list construction site in `main.py`.
  2. Insert matching call.
  3. Re-run a small neighbourhood (3–5 buildings).
  4. Confirm households differ from before.
- **Expected result:** Neighbourhood Default vs Year deltas now follow the same selection logic as single-building.

### Task 6 — Deterministic regression tests for `PresenceFilter` and `LightingGenerator` (O8, W13)

- **Aim:** Tripwire for future refactors.
- **What to do:** Write `eSim_tests/test_schedule_generator.py` with fixtures: always-home, always-away, half-day, single-hour-absence.
- **How to do:** Use plain `pytest`. Compute expected outputs by hand from `idf_optimizer._get_fallback_schedules()` so tests run without `schedule.json`.
- **Why:** Without this, tasks 1/3 can silently regress lighting or equipment.
- **What it impacts:** CI confidence for any future change in this layer.
- **Steps:** 1. Write fixtures. 2. Write 6–8 assertions. 3. Add to README testing section.
- **Expected result:** Green run; red on regression.

### Task 7 — Validate against external residential EUI benchmarks (O6)

- **Aim:** Anchor the framework to measured data.
- **What to do:** Compare per-end-use EUI for the Default and 2025 scenarios against NRCan SHEU-2017 Quebec/Ontario averages by dwelling type.
- **How to do:** Pull SHEU-2017 single-detached EUI by region. Extract scenario EUI from `eplusout.sql` per Option 3 run. Compute % difference per end-use.
- **Why:** Reviewers will ask "do your numbers match measured residential EUI?" The framework currently has no external anchor.
- **What it impacts:** Strengthens the validation chapter.
- **Steps:** 1. Source SHEU table. 2. Run Option 3 default. 3. Build comparison table. 4. Iterate on baseline (lighting density, equipment density, infiltration) if EUI is off by more than ±20 %.
- **Expected result:** Per-end-use EUI within ±20 % of SHEU averages, or a documented justification for the gap.

### Task 8 — Multi-region weather sweep (O10, T6) — partially done

- **Aim:** Generalize beyond Montreal/Toronto.
- **What to do:** Wire the existing 6-city EPW catalog into a `PR → EPW` lookup so each household routes to the climate file matching its province.
- **How to do:** Extend `eSim_bem_utils/config.py` weather selection logic. Use the BEM CSV's `PR` column as the routing key.
- **Why:** Closes the geographic loop and increases external validity.
- **What it impacts:** Result chapter; possibly amplifies the regional dimension of the longitudinal story.
- **Steps:**
  1. ✅ Collect EPW + STAT files for representative cities. Done — 6 cities present in `0_BEM_Setup/WeatherFile/`:
     - **5A** Toronto (`CAN_ON_Toronto.City-Univ.of.Toronto.715080_TMYx`)
     - **5B** Kelowna (`CAN_BC_Kelowna.Intl.AP.712030_TMYx`)
     - **5C** Vancouver (`CAN_BC_Vancouver.Harbour.CS.712010_TMYx`)
     - **6A** Montreal (`CAN_QC_Montreal.Center-Jean.Brebeuf-McGill.Univ-McTavish.716120_TMYx`)
     - **6B** Calgary (`CAN_AB_Calgary-Canadian.Olympic.Park.Upper.712350_TMYx`)
     - **7A** Winnipeg (`CAN_MB_Winnipeg.The.Forks.715790_TMYx`)
  2. Build a `PR → EPW` lookup dict in `eSim_bem_utils/config.py` (e.g., `'10' → Montreal`, `'35' → Toronto`, `'48' → Calgary`, `'59' → Vancouver`, `'46' → Winnipeg`, etc.). Decide a default for PRs not in the catalog.
  3. Update `simulation.py` / `main.py` so the EPW path is selected per-household (or per-batch) from the lookup instead of a single hard-coded weather file.
  4. Re-run Option 3 default + Option 6/7 comparative for a small cohort to confirm the runner picks the right EPW per PR.
  5. Decide whether multi-region results are reported per-PR or pooled.
- **Expected result:** Per-region EUI distributions, not just Quebec/Ontario; simulation log prints the EPW used per household.

### Task 9 — Clean up dead code (W6)

- **Aim:** Reduce maintenance risk.
- **What to do:** Remove `inject_presence_projected_schedules()` stub, the orphan `idf.saveas` at line 359, the duplicate `return` at lines 679/681, and the `if False and ...` block at lines 1399-1441.
- **How to do:** Edit `integration.py`. No behavioural change expected.
- **Why:** Dead code distracts and risks accidental reactivation.
- **Steps:** 1. Edit. 2. Run a sanity simulation to confirm no break.
- **Expected result:** Same EUI numbers; lighter file.

### Task 10 — Document Tier 4 fallback rate per cycle (O12)

- **Aim:** Quantify how often the profile matcher falls back to its lowest tier.
- **What to do:** Add a `MATCH_TIER` column in each `*_occToBEM.py` step. In the BEM layer, log the distribution.
- **How to do:** Trace where the tier label exists in the `ProfileMatcher` step and propagate it through `HH_aggregation` to `occToBEM`. Update `integration.load_schedules()` to read it.
- **Why:** A claim "Tier 4 < 0.5 %" exists in CLAUDE.md but is not visible at the BEM layer. Surfacing it lets us down-weight low-confidence households in the EUI summaries.
- **Steps:** 1. Add column at each step. 2. Test propagation. 3. Add summary log in `inject_schedules()`.
- **Expected result:** A per-cycle Tier 4 % visible in the run logs and reproducible in the paper.

---

### ✅ Task 11 — Fix ClusterMomentumModel velocity to include 2021 centroid (W15, T12)

- **Aim:** Correct the temporal velocity so the 2025 forecast incorporates the most recent demographic drift.
- **What to do:** In `ClusterMomentumModel.fit()` (`eSim_dynamicML_mHead.py:440-447`), add the 2016→2021 velocity term and update the weighted momentum to include three intervals.
- **How to do:** Add `v_newest = (centroids[2021] - centroids[2016]) / 5.0` and revise the blending weights (e.g., `α₁·v_newest + α₂·v_recent + α₃·v_old` with `α₁ > α₂ > α₃`).
- **Why:** The 2016→2021 period includes COVID-era household changes; ignoring it understates or overstates 2025 demographic projections.
- **What it impacts:** `forecasted_population_2025.csv`, all downstream 2025 BEM schedules, the headline 2025 EUI figures.
- **Steps:** 1. Edit `ClusterMomentumModel.fit()`. 2. Re-run `run_step1.py run_forecasting()`. 3. Re-run Steps 2–3. 4. Re-generate `BEM_Schedules_2025.csv`. 5. Compare 2025 EUI before/after.
- **Expected result:** Corrected 2025 forecast that reflects all four census cycles.

### ✅ Task 12 — Provide auditable baseline schedule source (W14, T11)

- **Aim:** Make the DOE MidRise schedule baseline reproducible from the repository.
- **What to do:** Either (a) create `0_BEM_Setup/Templates/schedule.json` populated with the hardcoded values currently in `_get_fallback_schedules()`, or (b) replace that function with a docstring table in the methods section giving all 24 values per end-use.
- **How to do:** Extract the 24-value arrays from `idf_optimizer.py:757-796` into a JSON file; update `load_standard_residential_schedules()` to load that file (the parse path already exists).
- **Why:** Peer reviewers cannot reproduce the baseline from the methods section alone. The JSON file closes this gap.
- **What it impacts:** Reproducibility of all Default and Year scenarios.
- **Steps:** 1. Write `schedule.json` from hardcoded values. 2. Commit to repo. 3. Confirm `load_standard_residential_schedules()` loads it successfully. 4. Mention file in the methods section.
- **Expected result:** EUI unchanged (same values, different source); `schedule.json` present in repo.

---

### Task 13 — Permanently disable the lighting override pathway (W4, T5)

- **Aim:** Remove the dormant lighting override branch entirely so it can never silently activate, even if `US+SF+CZ5A+elecres+slab+IECC_2024.idf` ever appears in `Templates/`.
- **What to do:** Delete the override branch in `load_standard_residential_schedules()` and the helper function `load_lighting_override_from_idf()` itself.
- **How to do:** In `idf_optimizer.py:743-751`, remove the `# [OVERRIDE] Apply Single Family High-Usage Lighting Schedule` block. Then delete `load_lighting_override_from_idf()` (`idf_optimizer.py:556-631`) and the `DEFAULT_LIGHTING_SOURCE_IDF` / `DEFAULT_LIGHTING_SCHEDULE_NAME` constants. Add a one-line comment in `load_standard_residential_schedules()` saying "Baseline is DOE MidRise from schedule.json — no overrides applied."
- **Why:** Defence in depth. Even with the file absent today, if anyone later drops it into `Templates/`, the override would silently change the lighting baseline. Removing the code path eliminates the risk completely.
- **What it impacts:** No EUI change today (override is dormant). Future-proofs the baseline against accidental activation.
- **Steps:** 1. Delete branch in `load_standard_residential_schedules()`. 2. Delete `load_lighting_override_from_idf()`. 3. Delete unused constants. 4. Run Option 3 once to confirm no behavioural change. 5. Update `Default Schedule Standardization.md` to remove the override mention.
- **Expected result:** Same EUI numbers; smaller, safer codebase.

### Task 14 — Split Weekday and Weekend in baseline standardization (W5)

- **Aim:** Make the standardization step structurally able to express weekend variation, not just rely on `For: AllDays`.
- **What to do:** Update `standardize_residential_schedules()` (`idf_optimizer.py:931-1139`) to write `For: Weekdays` and `For: Weekends Holidays` blocks separately, using the Weekday and Weekend arrays from `schedule.json`.
- **How to do:** Locate the `_get_or_create_schedule()` helper inside `standardize_residential_schedules()`. Replace the `For: AllDays` field with two consecutive blocks: one for Weekdays (using `data['Weekday']`) and one for Weekends (using `data['Weekend']`). The `schedule.json` file already has both keys populated.
- **Why:** Today's DOE MidRise has identical Weekday and Weekend, so this is harmless cosmetically — but the standardization step currently *cannot* express weekend variation if a future baseline (e.g., a residential template with real weekend differences) is introduced. Fixing it now removes a structural blocker.
- **What it impacts:** No EUI change with current baseline; unlocks future ability to use Weekday/Weekend-differentiated baselines.
- **Steps:** 1. Edit `_get_or_create_schedule()`. 2. Re-run Option 3. 3. Confirm EUI unchanged. 4. Inspect a saved IDF to verify Weekday/Weekend blocks are now present.
- **Expected result:** Same EUI numbers; standardized schedules in IDF now use Weekday/Weekend blocks.

### Task 15 — Multi-archetype household matching + illogical-row filter (W8)

- **Aim:** Eliminate the 9-to-5 worker selection bias by sampling from all occupancy archetypes (workers, students, retirees, shift workers), and add a sanity-check filter that drops physically impossible household rows before they enter the BEM stage.
- **What to do:**
  1. **Multi-archetype matching.** Replace the single `TARGET_WORKING_PROFILE` with a small set of stereotype profiles:
     - **Worker** — away 8–16, home otherwise (current target)
     - **Student** — away 9–15, home with afternoon return
     - **Retiree / At-home** — home most of the day, brief out-trips
     - **Shift worker** — away nights, home days
     For comparative runs, randomly draw a household from each archetype rather than locking to a single working-day stereotype.
  2. **Illogical-row detector.** Add `validate_household_schedule()` in `integration.py` that flags and removes households where:
     - Any hour value is outside `[0, 1]`
     - All 24 hours are exactly 0 (everyone "out" all day every day — likely a data error)
     - All 24 hours are exactly 1 (no one ever leaves — physically possible only for retirees, allowed for that archetype only)
     - More than 4 isolated 1-hour spikes (impossible flicker pattern)
     - Total daily presence-hours outside `[2, 24]` for any day
- **How to do:** Add `ARCHETYPE_PROFILES` dict in `integration.py:18-22` next to `TARGET_WORKING_PROFILE`. Add `find_archetype_household(schedules, archetype)` calling `find_best_match_household()` per profile. Add `validate_household_schedule(data) -> bool` and call it inside `load_schedules()` to filter the dict before returning.
- **Why:** The current design systematically excludes the demographic groups whose changes the longitudinal study is trying to capture. Multi-archetype sampling restores demographic diversity. The illogical filter prevents bad rows from contaminating the EUI distribution.
- **What it impacts:** Single-building comparative runs (richer demographic mix); also prevents bad-data EUI outliers.
- **Steps:** 1. Define 4 archetype profiles. 2. Implement `find_archetype_household()`. 3. Implement `validate_household_schedule()`. 4. Add unit tests with 5 fixture households (1 per archetype + 1 illogical). 5. Re-run Option 3 with archetype mode enabled. 6. Compare EUI distribution to single-stereotype run.
- **Expected result:** EUI distribution widens (captures real demographic diversity); a small fraction of input households (~0.5%) are dropped as illogical.

### Task 16 — Monte Carlo at BEM level (W9, T7)

- **Aim:** Replace single-point EUI estimates with mean ± std confidence intervals so that household selection uncertainty is visible to the reader.
- **What to do:** Extend the existing `option_kfold_comparative_simulation()` runner in `main.py:1382` to: (a) sample N=20–30 different random households per scenario instead of one, (b) run all N × 6 simulations in parallel, (c) report `mean(EUI) ± std(EUI)` per scenario per end-use, and (d) plot results as bar charts with error bars instead of single bars.
- **How to do:**
  1. In the k-fold runner, change the household selection loop to draw N samples per scenario (with replacement OK) using `random.sample()` or `np.random.choice()` against the matching pool.
  2. Aggregate per-scenario EUI across the N runs into `(mean, std)` tuples.
  3. Update `plotting.plot_comparative_eui()` to accept `(mean, std)` tuples and add error bars (`yerr=std`).
  4. Save raw per-iteration EUI to CSV so the user can compute additional statistics later.
- **Why:** A single random household is one draw from a wide distribution. Without uncertainty bars, reviewers cannot tell whether a 5 kWh/m² difference between 2005 and 2025 is real or noise. Monte Carlo at the BEM level captures the dominant uncertainty source (household selection) without re-running the CVAE.
- **What it impacts:** All comparative result figures gain error bars; runtime increases by ~N×.
- **Steps:** 1. Modify the k-fold runner. 2. Add aggregation helpers. 3. Update plotting. 4. Run with N=10 first (sanity), then N=30 for production. 5. Compare error bars across scenarios.
- **Expected result:** Comparative bar charts with error bars; honest uncertainty quantification.
- **Note:** CVAE-level Monte Carlo (re-rolling the CVAE seed) is the deeper alternative but ~N× more expensive. Defer until reviewers ask.

### Task 17 — IDF / dwelling-type compatibility check (W11)

- **Aim:** Prevent silent failures when a neighbourhood IDF is loaded in single-building mode (or vice versa), or when the selected dwelling type does not match the IDF geometry.
- **What to do:** Add `validate_idf_compatibility(idf_path, mode, dwelling_type)` in `integration.py` that runs *before* schedule injection. It should:
  1. **Detect mode mismatch** — count `SpaceList` objects with `Neighbourhood_*` prefix. If found in single-building mode → error. If absent in neighbourhood mode → error.
  2. **Detect dwelling-type mismatch** — parse the IDF filename for `SF` (Single Family), `MF` (MultiFamily), `MidRise`, `HighRise` codes. Compare to the user-selected `dwelling_type`. Mismatch → warning + confirmation prompt.
- **How to do:** New helper in `integration.py`. Called from the top of `inject_schedules()` and `inject_neighbourhood_schedules()`. Raises `ValueError` on hard mismatches; prints a yellow warning on filename ambiguity.
- **Why:** Today, if you accidentally select a neighbourhood IDF in Option 3, the simulation runs to completion and produces nonsense numbers without any error. A pre-injection check catches this in seconds instead of after a 2-minute simulation.
- **What it impacts:** Run-time safety; no EUI change for correct selections.
- **Steps:** 1. Implement the helper. 2. Wire it into both inject functions. 3. Test with deliberately mismatched IDF/dtype combinations. 4. Confirm correct selections still pass.
- **Expected result:** Hard error before simulation when IDF and selected mode/dtype disagree.

### ✅ Task 18 — Activity_Level fallback (W12) — Resolved by design

- **Aim:** Confirm that the `120 W` fallback for missing metabolic data is a deliberate design choice consistent with the user's PresenceFilter design intent.
- **Decision:** The `120 W` fallback only takes effect when an occupant is recorded as present at that hour but no metabolic activity code is available. `120 W` corresponds to sedentary work (sitting / light activity) and is the IECC residential default. This is consistent with the user's stated design intent: *"modify the values when occupants exist in the home, keep as is when they are not."*
- **Status:** Resolved by design. No code change needed. The fallback is intentional and physically reasonable.

### Task 20 — Continuous DHW scaling for partial-occupancy hours (O2)

- **Aim:** Make the Domestic Hot Water (DHW) demand reflect *how many* people are home, not just *whether* anyone is home.
- **What to do:** In the DHW path of `PresenceFilter`, multiply the DOE shape by the actual presence fraction (0.0–1.0) instead of routing through the binary occupied/absent branch. The water-end-use already has its own daily-volume rescaler downstream, so the total annual volume is bounded.
- **How to do:**
  1. Either add a `mode='binary'|'continuous'` parameter to `PresenceFilter.apply()`, or call DHW with a dedicated continuous helper. For DHW:
     `result[h] = presence[h] × default_schedule[h] + (1 - presence[h]) × base_load`
     evaluated for *every* hour, with no binary gate on absent hours (presence = 0 already gives `base_load`).
  2. Update `inject_schedules()` so DHW uses the continuous path while Equipment/Lighting keep the existing blended-with-gate behaviour.
  3. Confirm `scale_water_use_peak_flow()` still rescales the daily total to the OpenStudio reference volume so the annual hot-water energy stays plausible.
- **Why:** A household with 1 of 5 people home should not produce the same shower demand as a household with all 5 home. Continuous scaling reflects this without changing the daily total.
- **What it impacts:** DHW energy curves (smoother midday demand), peak-flow rescaler input. Total annual DHW volume should not change because of the rescaler.
- **Steps:**
  1. Add the continuous branch in `schedule_generator.py`.
  2. Wire it into `inject_schedules()` for the `dhw` end-use only.
  3. Run Option 3 for HH 4893 with the change. Compare DHW kWh and the hourly profile to the previous run.
  4. Confirm `scale_water_use_peak_flow()` adjustment is unchanged or rescaled correctly.
- **Expected result:** Same daily DHW total, smoother hour-to-hour curve, midday demand visibly proportional to the number of people home.

### Task 21 — Schedule:File for 8760-resolution per household (O5)

- **Aim:** Replace the Weekday/Weekend Schedule:Compact pair with a per-household 8760-row CSV referenced via `Schedule:File`, unlocking day-of-year variation, holidays, and weather-coupled occupancy.
- **What to do:** For each household, write one CSV per end-use with 8760 hourly values, store under a per-scenario `schedules/` directory, and update `inject_schedules()` to create `Schedule:File` IDF objects pointing at those CSVs instead of building Compact blocks.
- **How to do:**
  1. Decide CSV layout. Recommended: one folder per scenario (`Year_2022/schedules/HH_4893/`) with one CSV per end-use (`occupancy.csv`, `lighting.csv`, `equipment.csv`, `dhw.csv`, `heating_setpoint.csv`, `cooling_setpoint.csv`). Each CSV is a single column of 8760 values.
  2. Generate the 8760 series from the existing 24-hour Weekday/Weekend templates by stamping them across the calendar year (use Jan-1 day-of-week for the EPW). Holidays can be modelled later as Weekend stamps; for v1, copy Weekend onto Canadian statutory holidays.
  3. Add a `Schedule:File` writer in `idf_optimizer.py` that references the CSV path with `Column Number=1, Rows to Skip=0, Number of Hours=8760`.
  4. Replace the Compact-block creation in `inject_schedules()` (and `inject_setpoint_schedules()`) with the new `Schedule:File` writer when a `use_schedule_file=True` flag is set; keep Compact as the fallback.
  5. Run a Default + 2022 + 2025 comparative for HH 4893 to confirm the simulation reads the CSVs and the EUI matches the Compact-block run within numerical noise.
- **Why:** Compact blocks collapse 365 days into 2 day-types. Schedule:File lets you encode every day individually, which becomes essential for any future weather-coupled or holiday-aware behaviour, and keeps the IDF small (one filename instead of hundreds of nested Compact blocks).
- **What it impacts:** Reproducibility (each household's full year is on disk and inspectable), file size of the simulation directory grows substantially, IDF size shrinks.
- **Steps:** As above. Bench against the existing Compact-block run as a regression check.
- **Expected result:** Same EUI as the Compact-block baseline (within ±1 %); per-household 8760 CSV files on disk; IDF file size noticeably smaller.

### Task 22 — Selection-bias sensitivity analysis on `TARGET_WORKING_PROFILE` (T2)

- **Aim:** Defuse the "you cherry-picked 9-to-5 households" critique a reviewer will almost certainly make.
- **What to do:** Quantify how the SSE-matched comparative cohort differs from the unrestricted GSS-derived population, and either (a) demonstrate the matched subset is representative on the dimensions that matter, or (b) re-run a sensitivity case on the unrestricted population so the headline number is robust to the choice of target.
- **How to do:**
  1. Inside `find_best_match_household()` (`eSim_bem_utils/integration.py:27-74`), already records the SSE distance per HH. Persist that to a CSV alongside the matched cohort: one row per HH with `HH_ID`, `SSE_to_target`, `included (yes/no)`, `EMPLOY`, `HHSIZE`, `LIVED_ALONE`, `KIDS_AT_HOME`.
  2. Compute summary statistics: distribution of SSE distances; demographic distribution of the included cohort vs the full GSS pool; one-line "the matched cohort was X % employed full-time vs Y % in the source population."
  3. Run an alternative comparative scenario with a *different* `TARGET_WORKING_PROFILE` (e.g., shift worker, retiree-at-home, mixed weekday) and report whether the headline 5-year EUI trend changes direction, magnitude, or statistical significance.
  4. Add a methodology-paper paragraph stating: target choice, SSE distribution, demographic representativeness, sensitivity result.
- **Why:** The framework's longitudinal claim relies on like-for-like comparison across years, which means *something* has to be held constant. The current choice (one 9-to-5 stereotype) is defensible only if the reader can see (a) it's representative and (b) the result is robust to perturbing it. Without this, the headline number reads as "we cherry-picked the households that gave us the answer we wanted."
- **What it impacts:** Methodology paper (one new subsection); Discussion section (one robustness paragraph); no production code change beyond the SSE-distance CSV dump.
- **Steps:** As above.
- **Expected result:** A short table in the paper showing matched-cohort vs population demographics, an SSE-distance histogram, and a sensitivity bar chart of headline EUI under 2–3 alternative target profiles. Reviewer cannot accuse cherry-picking.

### Task 23 — Archetype robustness check: MidRise vs IECC SF Detached (T4)

- **Aim:** Quantify the bias introduced by using DOE MidRise Apartment schedules as the proxy for the SingleD geometry, so the paper can either (a) defend the choice numerically or (b) switch baselines.
- **What to do:** Run the Default scenario twice — once with the current MidRise baseline, once with an IECC Single-Family Detached baseline — for the same household and EPW, and report the per-end-use EUI delta.
- **How to do:**
  1. Locate or generate an IECC SF Detached schedule set for the same end-uses (occupancy, lighting, equipment, DHW, activity). Source candidates: OpenStudio Standards `space_types.json` SingleFamilyDetached entry, or a published IECC residential reference.
  2. Add a second `schedule_sf.json` file in `0_BEM_Setup/Templates/` mirroring the format of the existing `schedule.json`.
  3. Add a `--baseline midrise|sf_detached` flag to `load_standard_residential_schedules()` (default: `midrise` so existing runs are unchanged).
  4. Run Option 3 Default for HH 4893 with both baselines. Compare per-end-use EUI in a single table.
  5. If the delta is < ±10 %, the paper can state "MidRise is within 10 % of SF Detached for the dominant end-uses" and keep the current baseline. If > ±10 %, the paper either switches baseline or explicitly reports both as a sensitivity range.
- **Why:** Reviewers familiar with residential building energy will immediately challenge "why use an apartment archetype for a detached house?" The methodology paper acknowledges this but does not quantify the bias. One robustness run defuses the entire critique.
- **What it impacts:** One new template file; one new flag; one comparison table in the paper. No effect on existing runs unless the flag is flipped.
- **Steps:** As above.
- **Expected result:** A per-end-use EUI delta table comparing the two baselines, plus a one-sentence verdict in the methodology paper.

### Task 24 — Defensive IDD-file validation against EnergyPlus version drift (T9)

- **Aim:** Eliminate the silent-bug risk where eppy parses IDF fields with the wrong IDD types and produces simulations that *look* fine but use the wrong schedule semantics.
- **What to do:** Replace the bare `IDD_FILE = 'Energy+.idd'` fallback with an explicit, validated path resolution that fails loudly if the IDD is missing or version-mismatched.
- **How to do:**
  1. In `eSim_bem_utils/config.py`, add a function `resolve_idd_path() -> str` that:
     - First checks `os.environ.get('IDD_FILE')` and verifies the file exists.
     - Otherwise builds the expected path from `ENERGYPLUS_DIR` (e.g., `{ENERGYPLUS_DIR}/Energy+.idd` on Windows, `{ENERGYPLUS_DIR}/Energy+.idd` on macOS).
     - Verifies the file exists. If not, raise `FileNotFoundError` with a clear message: "IDD file not found. Set IDD_FILE env var or install EnergyPlus 24.2 in ENERGYPLUS_DIR."
     - Optionally: open the IDD file, read the first ~10 lines, parse the version string, and assert it matches `'24.2'`. Raise `RuntimeError` on mismatch.
  2. In `eSim_bem_utils/integration.py:793, 1116`, replace the `IDD_FILE` fallback string with `resolve_idd_path()`.
  3. Add a one-line print at the top of `inject_schedules()`: `print(f"  Using IDD: {idd_path}")` so the run log makes the IDD version visible.
- **Why:** Today the IDD lookup is invisible. If a future user has EnergyPlus 23.x or 25.x installed, eppy will silently use that IDD, and schedule field types may be reinterpreted in subtle ways. By the time anyone notices, dozens of runs may have been polluted. The fix is small, the failure mode is loud, and it future-proofs the framework against version churn.
- **What it impacts:** No change to current results (assuming you're already running 24.2). Adds one assertion and one log line.
- **Steps:** As above.
- **Expected result:** Every simulation run prints the IDD path; mismatched or missing IDDs raise a clear error before any IDF is touched.

### ✅ Task 25 — Investigate the 2025 work-duration anomaly (918 vs 542 min/day)

- **Aim:** Determine whether the post-velocity-fix 2025 forecast is producing physically plausible work durations, or whether the corrected `ClusterMomentumModel` has introduced (or merely revealed) a worker-heavy bias that needs to be reported, tuned, or flagged before any 2025 BEM result is published.
- **What to do:** Write a diagnostic script that quantifies the daily work duration in the new `Full_data.csv` and compares it to the historical baseline. Also fix the misleading "✅ Success" message in the Profile Matcher validator, which currently passes 918 min/day as "5–8 hours of work" without raising a flag.
- **How to do:**
  1. **Diagnostic script** — create `eSim_tests/diagnose_work_duration.py` (≈ 30 lines of pandas):
     - Load `0_Occupancy/Outputs_CENSUS/Full_data.csv`.
     - Filter to weekday (`DDAY == 1`), employed agents (use `EMPLOY` or `LFTAG` consistent with the matcher's "Employees" cohort).
     - For each `(SIM_HH_ID, ind_id)` person-day, count time slots where `occActivity` (or `ind_occACT`) indicates working. Multiply by slot duration (5 min) to get minutes/day.
     - Print: mean / median / p10 / p90 / max work-minutes/day across the cohort.
     - Group by `PR`, by `AGEGRP`, by `HHSIZE`, and by 2021-vs-2025 source year if both exist in the file. Print each group's mean.
  2. **Compare against historical baseline.** CLAUDE.md documents the historical baseline as **~542 min/day** for employed agents (2005/2010/2015/2022 cycles). If a backup of `Full_data.csv` from before the velocity fix exists, run the script against both and report the delta. If no backup exists, compare against the same metric computed from `BEM_Schedules_2022.csv` aggregated to person-day work minutes.
  3. **Decide root cause.** Three branches:
     - **(a) Validator bug only.** If the script reports a mean near 542 min/day, then the validator's "5–8 hours" string is just printing wrong text. Fix the validator: change the threshold check in the Profile Matcher validation step (`run_validate_profile_matcher`) to `300 ≤ mean ≤ 600` and raise a clear `WARNING` if outside.
     - **(b) Population shift is real and intentional.** If the script reports a mean significantly higher than 542 (say, > 700) and the `EMPLOY` distribution in the new forecast has shifted toward more full-time workers, this is a *real* signal. Document it in the paper as "the corrected velocity model captures the post-2021 employment recovery." Add a paragraph to `BEM_Methodology_Paper.md` and update Session 5 in this document's Progress Log.
     - **(c) Profile Matcher is retrieving wrong GSS episodes.** If the work-minutes are high but the `EMPLOY` distribution is unchanged from 2022, the matcher is pulling longer-work GSS schedules from the new alignment. Trace `run_profile_matcher` and inspect which GSS rows are being matched to a sample of new agents. Compare against the same agent demographics matched in 2022.
  4. **If branch (b) or (c)** — also tune the `ClusterMomentumModel.recent_weight` (currently 0.5). Try `0.4` and `0.35` and re-run Steps 1c, 2, 3 to see if the work-duration distribution moves back toward 542 min/day. Report the sensitivity in the methodology paper.
  5. **Always** — fix the validator threshold message regardless of which branch is taken, so this anomaly cannot pass silently in the future.
- **Why:** The 2025 EUI numbers depend on the schedules in `BEM_Schedules_2025.csv`. If those schedules encode an implausible amount of work (15.3 hours/day vs the historical 9-hour worker), then HVAC, lighting, and equipment results for 2025 will be biased downward (more "away" hours) and the longitudinal trend story will be artefactual. This is the single biggest pre-publication risk introduced by the velocity-fix re-run.
- **What it impacts:**
  - `BEM_Schedules_2025.csv` validity (and therefore every 2025 EUI in the paper).
  - `run_validate_profile_matcher` validator threshold.
  - Possibly `ClusterMomentumModel.recent_weight` parameter.
  - Methodology paper — one sensitivity paragraph.
  - `OccIntegrationFramework.md` §7 Session 5 Progress Log entry.
- **Steps:**
  1. Write `eSim_tests/diagnose_work_duration.py`.
  2. Run it against current `Full_data.csv`. Save output to `eSim_tests/diagnose_work_duration_2025.txt`.
  3. Identify which branch (a/b/c) the result falls into.
  4. Apply the corresponding fix or documentation update.
  5. Fix the validator threshold message in any case.
  6. If tuning `recent_weight`, re-run Steps 1c, 2, 3 with the new value and re-run the diagnostic.
  7. Update §7 Session 5 in `OccIntegrationFramework.md` with the finding.
- **Expected result:** A clear, written answer to "Is the 918 min/day a validator bug, a real demographic shift, or a Profile Matcher artefact?" plus a fix for the validator threshold and (if needed) a tuned `recent_weight`. The 2025 BEM results can then be trusted or flagged accordingly.
- **How to test:** Re-run the diagnostic after any tuning. Confirm the validator now raises a clear warning when the mean drifts outside `[300, 600]` min/day.

### Task 19 — Document the 2025 building-stock-frozen assumption (W16)

- **Aim:** Make the 2021 → 2025 building stock assumption explicit and defensible in the methodology paper, without adding fragile extrapolation code.
- **What to do:** Add a one-paragraph methodology note to `BEM_Methodology_Paper.md` in the section that describes the CVAE 2025 forecast. Also add a code comment near `eSim_dynamicML_mHead.py:537-541` referencing the methodology paragraph.
- **How to do:** Append to the methodology paper:
  > "Building stock characteristics (DTYPE, BEDRM, ROOM, CONDO) for the 2025 forecast are held at the 2021 distribution. Statistics Canada has not released a comprehensive housing inventory for 2022–2025, and any extrapolation would introduce more uncertainty than it removes. The 2025 results therefore reflect demographic drift only, not changes in housing stock."
- **Why:** Reviewers respect honest limitations far more than fragile extrapolations. Stating the assumption upfront removes the need for code complexity.
- **What it impacts:** No code change; one paragraph in the methodology paper; one comment in the source.
- **Steps:** 1. Add the paragraph to the paper. 2. Add the comment in the source. 3. Cross-reference both.
- **Expected result:** The 2025 forecast assumption is visible to any reader of the paper or the source.

---

## 4. Task Prioritization

| Group | Tasks | Why this group |
|-------|-------|----------------|
| **Must complete before publishing results** | 1 ✅, 2 ✅, 3 ✅, 11 ✅, 12 ✅, 25 ✅ | Doc/code drift, CVAE velocity bug, missing baseline file, and the 2025 work-duration anomaly all directly threaten reproducibility or result validity. All six now done. |
| **Needed for strong headline results** | 4 ✅, 5, 7, 8 (partial), 22 | Without thermostat setback the HVAC signal is weak; without neighbourhood matching the comparison is asymmetric; without external validation there is no anchor; the multi-region sweep needs the routing wired in; selection-bias sensitivity defuses the cherry-picking critique. |
| **Needed to answer reviewer questions** | 6, 10, 13, 14, 15, 16, 17, 23 | Regression tests, Tier 4 fallback rate, dormant override removal, weekday/weekend split, multi-archetype matching, BEM-level Monte Carlo, IDF compatibility check, archetype robustness check. |
| **Physical realism upgrades** | 20, 21 | Continuous DHW scaling and Schedule:File 8760-resolution improve fidelity but are not blockers for the headline numbers. |
| **Hygiene — quick, no EUI impact** | 9, 18 ✅, 19, 24 | Dead code removal; W12 fallback design decision (resolved); W16 frozen-stock documentation; defensive IDD validation. |

---

## 5. Appendix — Code Reference Map

| Concept | File | Lines |
|---------|------|-------|
| Occupancy CSV generation formula | `eSim_occ_utils/06CEN05GSS/06CEN05GSS_occToBEM.py` | 174-188 |
| Activity → W mapping | `eSim_occ_utils/06CEN05GSS/06CEN05GSS_occToBEM.py` | 58-74 |
| `PresenceFilter` (binary toggle) | `eSim_bem_utils/schedule_generator.py` | 325-400 |
| `LightingGenerator.generate_monthly` | `eSim_bem_utils/schedule_generator.py` | 287-322 |
| Daylight factor calculation | `eSim_bem_utils/schedule_generator.py` | 239-285 |
| `inject_schedules` (single building) | `eSim_bem_utils/integration.py` | 765-1079 |
| `inject_neighbourhood_schedules` | `eSim_bem_utils/integration.py` | 1082-1450 |
| Standard residential schedule loader | `eSim_bem_utils/idf_optimizer.py` | 634-754 |
| Lighting override branch | `eSim_bem_utils/idf_optimizer.py` | 743-751 |
| `standardize_residential_schedules` | `eSim_bem_utils/idf_optimizer.py` | 931-1139 |
| `scale_water_use_peak_flow` | `eSim_bem_utils/idf_optimizer.py` | 869-928 |
| `find_best_match_household` (SSE) | `eSim_bem_utils/integration.py` | 27-74 |
| `TARGET_WORKING_PROFILE` constant | `eSim_bem_utils/integration.py` | 18-22 |
| Dead code: `inject_presence_projected_schedules` | `eSim_bem_utils/integration.py` | 741-758 |
| Dead code: orphan `idf.saveas` | `eSim_bem_utils/integration.py` | 359 |
| Dead code: duplicate `return` | `eSim_bem_utils/integration.py` | 679, 681 |
| Dead code: `if False and ...` | `eSim_bem_utils/integration.py` | 1399-1441 |
| Fallback schedule (hardcoded) | `eSim_bem_utils/idf_optimizer.py` | 757-796 |
| Lighting override (dormant) | `eSim_bem_utils/idf_optimizer.py` | 556-631, 743-751 |
| CVAE training entry point | `eSim_occ_utils/25CEN22GSS_classification/run_step1.py` | 54-103 |
| ClusterMomentumModel (velocity bug) | `eSim_occ_utils/25CEN22GSS_classification/previous/eSim_dynamicML_mHead.py` | 392-474 |
| 2025 building stock frozen at 2021 | `eSim_occ_utils/25CEN22GSS_classification/previous/eSim_dynamicML_mHead.py` | 537-541 |
| Neighbourhood hhsize fix | `eSim_bem_utils/integration.py` | 1364-1383 |
| Scenario orchestration (6 scenarios) | `eSim_bem_utils/main.py` | 30-33, 590-847 |
| Stale test (would fail) | `eSim_tests/test_integration_logic.py` | 1-111 |

---

## 6. Verification Status (Post-Audit)

Findings from the code audit conducted 2026-04-07. Each claim from the original SWOT was verified against the actual repository state.

| Claim | Verified Status | Notes |
|-------|----------------|-------|
| 5 years of BEM_Schedules_*.csv exist | ✅ CONFIRMED | 2005, 2010, 2015, 2022, 2025 all present in `BEM_Setup/` |
| CVAE model weights saved | ✅ CONFIRMED | `saved_models_cvae/cvae_encoder.keras`, `cvae_decoder.keras` exist |
| forecasted_population_2025.csv generated | ✅ CONFIRMED | In `Outputs_CENSUS/Generated/` |
| Neighbourhood hhsize uses People/Area only | ❌ CORRECTED | A `[FIX]` block at `integration.py:1364-1383` switches to `People` count = hhsize |
| Monte Carlo not in code (W9) | ❌ CORRECTED | `option_kfold_comparative_simulation()` and `option_batch_comparative_neighbourhood_simulation()` both exist in `main.py` |
| W4 lighting override is active | ❌ CORRECTED — DORMANT | Template file does not exist; override returns None at runtime |
| schedule.json is the baseline source | ❌ WRONG — FILE ABSENT | `_get_fallback_schedules()` hardcoded values are the real baseline (new W14) |
| ClusterMomentumModel uses all 4 census years | ❌ WRONG — 2021 IGNORED | Velocity uses only 2006–2016; 2021 is seeding only (new W15) |
| 2025 building stock reflects 2025 conditions | ❌ WRONG — FROZEN AT 2021 | `generate_future_population()` samples `bldg_conditions` from 2021 only (new W16) |
| test_integration_logic.py is valid | ❌ STALE — WOULD FAIL | Hardcodes baseload values superseded by dynamic `PresenceFilter` (new W13 update) |

---

## 7. Progress Log

This section records what was done, when, and what the outcome was. Add a new entry each working session.

---

### Session 1 — 2026-04-07: Code Audit and SWOT Creation

**What was done:**
- Read and audited `schedule_generator.py`, `integration.py`, `idf_optimizer.py`, `main.py`, `neighbourhood.py`, `06CEN05GSS_occToBEM.py`, `test_integration_logic.py`
- Created this document (`OccIntegrationFramework.md`) with the full SWOT analysis
- Identified 16 weaknesses, 12 opportunities, 12 threats, 12 tasks

**Key findings from this session:**
- The lighting override (`W4`) is dormant — the template file does not exist, so it never activates
- `schedule.json` does not exist — the baseline was hardcoded Python lists invisible to external review (`W14`)
- `ClusterMomentumModel` ignores the 2021 latent centroid when computing velocity — the 2025 forecast extrapolates from a 2006–2016 trend (`W15`)
- Neighbourhood mode was properly injecting hhsize via a `[FIX]` block already in place (W9 assumption corrected)
- Monte Carlo runners already exist in `main.py` (original SWOT assumption corrected)
- `test_integration_logic.py` would fail against current code — stale since `PresenceFilter` was updated

---

### Session 2 — 2026-04-08: Fixes and Simulation Testing

**What was done:**

**Task 12 ✅ — Created `0_BEM_Setup/Templates/schedule.json`**
- Extracted the 24-value DOE MidRise arrays from `idf_optimizer.py:757-796`
- Wrote them into `schedule.json` in OpenStudio Standards format (nested `day_schedules` with `times`/`values`)
- `load_standard_residential_schedules()` now reads from file instead of hardcoded fallback
- EUI unchanged — same numbers, now auditable from a versioned file

**Task 11 ✅ — Fixed `ClusterMomentumModel` velocity calculation**
- `eSim_dynamicML_mHead.py:440-447` edited
- Old code: velocity from 2006→2011 and 2011→2016 only (2021 centroid ignored)
- New code: velocity computed from all consecutive census year pairs (2006→11, 2011→16, 2016→21) with configurable weights (`alpha` for most recent, equal share of `1-alpha` for older intervals)
- The 2025 CVAE forecast needs to be re-run with Steps 1c, 2, 3 to regenerate `BEM_Schedules_2025.csv` from the corrected model

**Task 1 ✅ — Updated `PresenceFilter` formula and paper §5.4**
- `schedule_generator.py:376-400`: occupied branch changed from `result = default_val` to `result = presence × default_val + (1 - presence) × base_load`
- Absent branch unchanged — zero-occupancy hours are not touched by TUS injection
- `BEM_Methodology_Paper.md §5.4`: formula updated to match code; MAX/floor language removed
- Decision rationale: blended formula uses the fractional occupancy information already in the CSV; absent-hour gate preserved as explicit design intent

**Task 3 ✅ — Corrected lighting solar claim in paper §5.5.1**
- `BEM_Methodology_Paper.md §5.5.1` rewritten from "solar is visualization only" to correctly describe the Daylight Threshold Method (150 Wh/m², monthly scaling, floor 0.3, 12 monthly Compact blocks)
- No code change needed — the code was already correct; the paper was wrong

**Task 2 ✅ — Documented lighting override as dormant**
- Verified `DEFAULT_LIGHTING_SOURCE_IDF = "US+SF+CZ5A+elecres+slab+IECC_2024.idf"` does not exist on disk
- `load_lighting_override_from_idf()` returns `None` at runtime; override branch never executes
- W4 and T5 in SWOT updated to reflect dormant status

**Task 4 ✅ — Implemented thermostat setback (`inject_setpoint_schedules()`)**
- New function added to `integration.py` before `inject_schedules()`
- Reads existing `heating_sch` / `cooling_sch` setpoints from the IDF (reads actual constant value)
- Creates per-household `HeatSP_HH_<id>` and `CoolSP_HH_<id>` Schedule:Compact objects
- Occupied hours: original setpoints (22.2°C / 23.9°C for Montreal IDF)
- Absent hours: 18°C heating setback / 27°C cooling setback
- Called automatically from `inject_schedules()` — active for all year scenarios; Default scenario retains the original flat schedule and is therefore warmer/cooler than TUS years
- Called from `inject_schedules()` only (single-building mode); neighbourhood mode not yet updated

**Simulation results (HH 4893, Montreal CZ6A, with setback):**
- Space Heating: dropped ~15–20 kWh/m² for TUS years vs Default; year-to-year longitudinal spread now visible in time series
- Space Cooling: Default clearly higher than TUS years; separation amplified vs no-setback run
- Fans: now clearly differentiated — follow HVAC operation pattern
- DHW / WaterSystems: differentiation maintained from previous run
- Decision: keep setback as primary result; previous (no-setback) run retained for sensitivity comparison in paper

**Remaining tasks (not yet started):**
- Task 5 — neighbourhood comparative matching
- Task 6 — regression tests for `PresenceFilter` and `LightingGenerator`
- Task 7 — validate Default EUI against NRCan SHEU-2017 benchmarks
- Task 8 — multi-region weather sweep (Vancouver, Calgary, Halifax)
- Task 9 — dead code cleanup in `integration.py`
- Task 10 — Tier 4 fallback rate per cycle
- **CVAE re-run** — re-run Steps 1c, 2, 3 of `25CEN22GSS_classification` pipeline to regenerate `BEM_Schedules_2025.csv` using the corrected `ClusterMomentumModel`

---

### Session 3 — 2026-04-08: Opportunities Discussion and New Tasks

**What was done:**
- Walked through opportunities O2, O5, O6, O10, O12 in plain English to confirm scope and feasibility before committing them to tasks.
- Confirmed O6 is already covered by Task 7 (NRCan SHEU-2017 benchmark validation).
- Confirmed O12 is already covered by Task 10 (Tier 4 fallback flagging).
- **O10 marked partially done.** User collected the EPW + STAT files for 6 cities into `0_BEM_Setup/WeatherFile/`:
  - 5A Toronto, 5B Kelowna, 5C Vancouver, 6A Montreal, 6B Calgary, 7A Winnipeg
  - Task 8 updated with the file inventory and a step-by-step plan for the `PR → EPW` lookup wiring that remains.
- **Task 20 created (O2 — Continuous DHW scaling).** Multiply DHW DOE shape by the actual presence fraction instead of the binary gate; rely on `scale_water_use_peak_flow()` to keep the daily total bounded.
- **Task 21 created (O5 — Schedule:File 8760-resolution per household).** Replace the Weekday/Weekend Compact-block pair with per-household 8760-row CSVs referenced via `Schedule:File`, opening the door to day-of-year, holiday, and weather-coupled behaviour.
- Task Prioritization table updated: Task 8 moved into "strong headline results" group as partial-done; new "Physical realism upgrades" group introduced for Tasks 20 and 21.

**Why this session matters:**
The opportunities tracked in §2 were originally a long brainstorm. This session converted the still-actionable ones into concrete tasks with steps and expected results, so they can be picked up in order without re-deriving the rationale.

**Next decision:**
Pick the next concrete task to implement. Easy candidates: Task 19 (W16 doc), Task 13 (W4 dead code), Task 8 step 2 (`PR → EPW` lookup) now that the EPW catalog is in place.

---

### Session 4 — 2026-04-08: Threats Coverage Audit and Executor Handoff

**What was done:**
- Walked through all 12 threats (T1–T12) and mapped each to existing tasks.
- Confirmed 9 of 12 threats are already covered: T1 ✅, T3 ✅(setback), T5 (Tasks 2 ✅ + 13), T6 partial (Task 8), T7 (Task 16), T8 (Tasks 9, 13), T10 (Task 5), T11 ✅, T12 ✅.
- **Identified 3 threats with no task coverage and created new tasks:**
  - **Task 22 (T2)** — Selection-bias sensitivity analysis on `TARGET_WORKING_PROFILE`. Persists SSE distances, demonstrates representativeness of the matched cohort, and re-runs comparative scenarios with alternative target profiles.
  - **Task 23 (T4)** — Archetype robustness check: DOE MidRise vs IECC SF Detached. One Default-scenario comparison run to quantify the apartment-vs-detached schedule bias.
  - **Task 24 (T9)** — Defensive IDD-file validation. Replaces the bare `Energy+.idd` fallback with `resolve_idd_path()` that fails loudly on missing or version-mismatched IDD.
- Task Prioritization table updated: Task 22 added to "strong headline results", Task 23 to "reviewer questions", Task 24 to "hygiene".
- T6 (future-climate / extreme-weather) deliberately *not* promoted to a new task. Task 8 covers TMYx multi-region; future-climate sensitivity is out of scope for the eSim 2026 paper unless explicitly added later.

**Why this session matters:**
The threats SWOT was originally a brainstorming list. This session converted every actionable threat into either a confirmed task link or a new task with concrete steps, so nothing in the SWOT is unowned.

**Handoff:**
The planning phase for the SWOT is complete (24 tasks defined). Execution will move to a Sonnet executor; this document remains the source of truth for what to implement, in what order, and what "done" looks like for each task.

---

### Session 5 — 2026-04-08: CVAE Re-run with Corrected ClusterMomentumModel

**What was done:**
- Ran the full `25CEN22GSS_classification` pipeline end-to-end via `main_classification.py` with all flags `True` (Steps 1a–1d, 2a–2f, 3a).
- Confirmed the velocity fix is active in `eSim_dynamicML_mHead.py:440-462`: 3 consecutive-year intervals computed (2006→11, 2011→16, 2016→21) with weights `[0.25, 0.25, 0.5]`.
- CVAE retrained from scratch (100 epochs, total loss 16.15 → 3.97); training plot looks healthy.
- Forecast base year confirmed as 2021 (4-year projection to 2025, 9-year to 2030).
- Generated new `forecasted_population_2025.csv`, `forecasted_population_2030.csv`, `Full_data.csv`, and `BEM_Schedules_2025.csv`.
- Household assembly: 47,764 households; all member counts validated.
- Profile matcher tier distribution: WD (Perfect 27.0 %, Drivers 70.1 %, Constraints 2.7 %, FailSafe 0.2 %); WE (Perfect 16.6 %, Drivers 77.5 %, Constraints 5.4 %, FailSafe 0.6 %).
- DTYPE refinement applied; distribution shifted toward apartments (Single-detached 62.2 % → 56.9 %; Apt <5 storeys 13.2 % → 19.8 %).

**Issues flagged for Task 25:**
- **Work duration anomaly:** Profile Matcher validator reported 918 min/day for the "Employees" cohort, vs the historical baseline of ~542 min/day. The validator's "✅ Success" message was misleading because 918 min = 15.3 h/day, far outside any plausible range. **Root cause identified and fixed in Task 25 (see below).**
- **WE Tier 4 fallback at 0.6 %**, slightly above the < 0.5 % target. Minor; flagged for Task 10.

**Task 25 finding and fix (root cause = validator filter bug — branch a):**

The 918 min/day anomaly was caused by an over-broad activity filter in `validate_matching_quality()` across three files:
- `previous/eSim_dynamicML_mHead.py` (used by run_step2.py)
- `16CEN15GSS/16CEN15GSS_ProfileMatcher.py`
- `06CEN05GSS/06CEN05GSS_ProfileMatcher.py`

**The bug:** `ep_wd['occACT'].astype(str).str.startswith(('1', '0', '8'))` intended to capture category 1 (paid work) and category 8 (transport/commute), but on the harmonized 1-14 integer scheme, `startswith('1')` also captures categories 10, 11, 12, 13, 14 — effectively 7 of 14 activity categories. This inflates the total to ~918 min/day.

**Two bugs fixed (both in the same duration calculation):**
1. `startswith(('1','0','8'))` → `isin([1, 8])` (filter over-capture)
2. Raw HHMM subtraction (`e - s`) → HHMM-to-minutes conversion (`(e//100)*60 + (e%100)` then subtract) because `start`/`end` are stored as HHMM integers (e.g. 920 = 9:20 AM)

**Validator threshold also fixed:** Three-band check: `<60` WARNING, `300–600` ✅ Success, `>600` WARNING with branch guidance.

**Confirmed results (run 2026-04-08):**

Diagnostic (`eSim_tests/diagnose_work_duration.py`, n=1000 employees, HHMM-corrected):
```
Activity filter     : occACT isin([1, 8])  -- paid work + transport/commute
Duration computation: HHMM-to-minutes conversion (not raw HHMM subtraction)
Keys  : 30,273 rows  | unique occIDs in GSS: 6,850
Employees (COW 1-2) in keys: 30,247 agents

Work+commute duration (real minutes, HHMM-corrected):
  Mean   : 397.0 min/day  (6.62 h)
  Median : 480.0 min/day
  P10    : 0.0 min/day
  P90    : 630.0 min/day
  Zeros  : 19.5% (matched to non-working diary day)

Verdict: OK -- within plausible range [300, 600]
  --> The old 918 min/day was a validator filter bug (branch a).
  --> BEM_Schedules_2025.csv is trusted for publication.

Breakdown by HHSIZE:
  1-person HH: 416 min/day | 2-person: 391 | 3-person: 359 | 4-person: 430 | 5-person: 392
```

Validator (`run_validate_profile_matcher()`, n=500, same fixes):
```
   Average Work+Commute Duration for 'Employees' (n=500): 386 min/day
   (Expected range: 300-600 min/day; historical baseline ~542 min/day)
   ✅ Success: Employees performing 5-10 hours of work+commute (plausible range).
```

**Status of `BEM_Schedules_2025.csv`:** trusted for publication. The validator bug affected only the diagnostic text, not the schedule output CSVs.

**Minor (non-blocking):**
- 3/10 reconstruction samples predicted YEAR=2021 instead of true 2011/2016/2021. Latent space has slight bias toward most recent year. Acceptable.
- DTYPE shift toward apartments may be a real Canadian housing-trend signal or a CVAE quirk; worth one line in the methodology paper.

**Next (post Task 25):**
- Run BEM Option 3 for HH 4893 (2025 scenario) and compare EUI to the pre-velocity-fix run.
