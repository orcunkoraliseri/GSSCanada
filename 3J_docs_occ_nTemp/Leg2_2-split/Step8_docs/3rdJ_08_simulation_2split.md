# 3rd Journal — Step 8 (EnergyPlus Simulation, Two-Channel) — DESIGN DOC

**Status: design doc — all open decisions locked by manager, 2026-06-28. Supersedes `3rdJ_08_simulation_2split_SCOPING.md` (retained as the planning predecessor).**

> This is the design specification the employee builds against. Every architectural choice below is either carried-over-from-J2 (design-locked) or a manager-resolved decision (the OD-8x items from the scoping draft). The employee execution handoff is `3rdJ_08_builder_prompt.md`; the validation spec is `3rdJ_08_simulation_2split_val.md`.

---

## 0. Locked Decisions (resolutions of scoping OD-8A…J)

| OD | Decision | Resolution (locked 2026-06-28) |
|---|---|---|
| **OD-8A** | Office IDF templates | **PNNL Tall + SuperTall**, confirmed present at `BEM_Setup/Buildings/CAN_CLG/` (Z7A) and `CAN_MTL/` (Z6). They are **v22.1** (`_v221`) → a **v22.1→v24.2 IDF transition** (same chain J2 ran for the residential stock) is required before they run under the v24.2 SIF. Zone-tag audit for Tag-2 routing required. (Sub-step 8C.0) |
| **OD-8B** | Lights/Equipment coupling | **Implement in Step 8 — all occupancy-driven schedules.** People + Lights + Equipment coupled to occupancy in BOTH channels. HVAC/DHW stay at NECB/ASHRAE code baseline. (User directive 2026-06-28: "include all schedules as much as possible.") |
| **OD-8C** | Historical cycles | **In scope.** Simulate 2005 / 2010 / 2015 in addition to 2022 + 2030×3 → **7 scenarios**. Historical schedules do **not** yet exist for the 3J stock → new gating sub-step **8A** generates them. |
| **OD-8D** | Office archetype × envelope | **3 archetype schedules (Knowledge/Public/Sales) × 2 envelopes (Tall/SuperTall)** full cross. |
| **OD-8E** | Office climate zones | **Same 6 CZ as residential** (Toronto 5A, Kelowna 5B, Vancouver 5C, Montreal 6A, Calgary 6B, Winnipeg 7A). |
| **OD-8F** | Residential pool-size audit | Build task: audit all (DTYPE × PR) cells in the 23,211-HH stock; cells < 50 HH → document + with-replacement sampling for that cell (never silently drop). |
| **OD-8G** | Commercial EUI benchmark | **NRCan SCIEU** (Survey of Commercial and Institutional Energy Use) + **NECB reference** schedules for the office EUI plausibility gate. Residential keeps NRCan SHEU (as J2). |
| **OD-8H** | Interpolate to Timestep | **`No`** (hold the hourly block value as a step function — preserves the discrete schedule shape and avoids compounding sub-hour peak loss). Documented in Methods. [CONFIRM in Methods] |
| **OD-8I** | Office statistical design | **Deterministic** — one run per (archetype × envelope × CZ × scenario) cell. The aggregate office multiplier has no per-HH variance; the spread comes from the WFH bands. |
| **OD-8J** | Engine versioning | **Create `eSim_bem_utils_3J/`** as a versioned copy of `eSim_bem_utils_2J/` (isolate J3 from J2; consistent with J2 practice). |

**Office-historical scope (resolved 2026-06-28):** historical cycles apply to **both channels** — historical office multipliers are generated in 8A. Caveat to document: AT_WORK gating vars differ across early GSS cycles (2005/2010 PLACE=02 vs 2015 LOCATION=301 vs 2022 LOCATION=3301; see Step 1/2 docs), so historical office carries documented reconstruction uncertainty.

---

## 1. Aim

Step 8 delivers EnergyPlus energy simulation results for **both channels** of the 3J Leg-2 two-channel occupancy pipeline — **residential (AT_HOME, REPLACE)** and **office (AT_WORK, MODULATE)** — across **7 scenarios** spanning the full longitudinal arc (2005 → 2030):

- **Residential:** per-household occupancy + metabolic + occupancy-coupled lighting/equipment schedules drive 4 dwelling archetypes × 6 Canadian climate zones, paired Monte-Carlo (N=50), mirroring the J2 Step-8 design but for 7 scenarios.
- **Office (new):** `office_integration.py` reads the aggregate workforce-presence multiplier and injects it as the People/Lights/Equipment temporal schedules into PNNL Tall/SuperTall office IDFs, preserving NECB/ASHRAE code-compliant peak densities (people/m², LPD, plug).

The primary contribution is **load shape** — hourly profiles, peak-hour timing, the pre/post-COVID occupancy break (2015→2022), and the 2030 WFH-band energy spread — not annual EUI (which mirrors J2's methodological argument and is reported as a secondary plausibility check).

---

## 2. Sub-Step Structure

Step 8 runs as five ordered sub-steps. 8A gates everything; 8B/8C are independent and parallelisable; 8D/8E are the rollup.

| Sub-step | Name | What it produces | Gates |
|---|---|---|---|
| **8A** | Historical schedule generation | `BEM_Schedules_2split_{2005,2010,2015}.csv` (residential) + `office_presence_multiplier_{2005,2010,2015}.csv` (office) for the 3J stock | val §0 |
| **8B** | Residential campaign | Paired-MC EnergyPlus runs, 4 arch × 6 CZ × 7 scen × N=50 | val §1–6 (resid) |
| **8C** | Office campaign | Deterministic EnergyPlus runs, 3 arch × 2 env × 6 CZ × 7 scen | val §1–6 (office) |
| **8D** | Aggregation | Hourly/diurnal/peak/EUI rollups + figures | val §5–7 |
| **8E** | Validation report | `step8_validation_report.html` (PASS/WARN/INFO/FAIL scorecard) | val §8 |

### 8A — Historical schedule generation (the new prerequisite)

J3 Step 7 only produced 2022 + 2030×3. The historical cycles (2005/2010/2015) have no BEM schedules yet. 8A closes that gap by porting the **J2 `08_gen_cycle_schedules.py`** path onto the 3J two-channel machinery:

1. Load the locked Step-4 two-channel model (`Step4_docs/outputs_step4/checkpoints/best_model.pt`).
2. Generate per-cycle augmented diaries for 2005/2010/2015 (both AT_HOME and AT_WORK heads), conditioned on each cycle's respondent population.
3. Apply the locked Step-4 calibration (04L/04M raking) per cycle.
4. Run the Step-7 `3rdJ_07_aug_to_bem_2split.py` path on each cycle to emit:
   - **Residential:** `BEM_Schedules_2split_{2005,2010,2015}.csv` (13-col schema, identical to 2022).
   - **Office:** `office_presence_multiplier_{2005,2010,2015}.csv` (7-col schema, identical to 2022; single observed BAND per cycle, no WFH bands pre-2030).

**Output landing:** `Step8_docs/outputs_step8/historical_schedules/`. These are the missing inputs that 8B/8C consume alongside the existing Step-7 files. 8A must pass val §0 before any EnergyPlus run is launched.

---

## 3. Inputs

### 3a. Step-7 deliverables (already exist, schema confirmed)

**Residential REPLACE** — `Step7_docs/outputs_step7/`, 13 cols `SIM_HH_ID, Day_Type, Hour, HHSIZE, DTYPE, BEDRM, CONDO, ROOM, REPAIR, PR, MATCH_TIER, Occupancy_Schedule, Metabolic_Rate`:
- `BEM_Schedules_2split_2022.csv` (1,114,128 rows = 23,211 HH × 2 day-types × 24 h)
- `BEM_Schedules_2split_2030_conservative.csv`, `…_hybrid.csv`, `…_fullyhybrid.csv` (same schema)

**Office MODULATE** — `Step7_docs/outputs_step7/`, 7 cols `office_archetype, BAND, Day_Type, Hour, AT_WORK_fraction, multiplier, n_persons`:
- `office_presence_multiplier_2022.csv` (144 rows = 3 arch × 1 band × 2 day-types × 24 h)
- `office_presence_multiplier_2030.csv` (432 rows = 3 arch × 3 bands × 2 day-types × 24 h)

`AT_WORK_fraction` (raw absolute fraction, OD-7B locked) is the primary schedule column; `multiplier` (peak-normalised) is emitted but not the default input.

Key occupancy levels: residential 2022 WD 0.646; 2030 WD conservative 0.683 < hybrid 0.701 < fullyhybrid 0.711; metabolic ~110 W/person. Office 2022 WD peak `AT_WORK_fraction`: Knowledge 0.602 / Public 0.608 / Sales 0.592; 2030 business-hours Knowledge conservative 0.588 > hybrid 0.502 > fullyhybrid 0.462 (band-monotonicity gates PASS).

### 3b. Step-7-style deliverables generated in 8A (do not exist yet)

- Residential: `BEM_Schedules_2split_{2005,2010,2015}.csv`
- Office: `office_presence_multiplier_{2005,2010,2015}.csv`

### 3c. Weather files

TMYx EPW for the 6 CZ used in J2, at `BEM_Setup/WeatherFile/`: Toronto 5A, Kelowna 5B, Vancouver 5C, Montreal 6A, Calgary 6B, Winnipeg 7A. Residential routing via `PR_REGION_TO_EPW_CITY` in the engine `config.py`. Office routing: each of the 6 EPW cities is run on the climate-matched office envelope (5A/5B/5C/6A/6B → the **Z6 (CAN_MTL)** envelope; 7A → the **Z7A (CAN_CLG)** envelope), since the office IDFs ship in only those two climate variants.

### 3d. Building / IDF stock (real paths confirmed)

**Residential archetypes — v24.2 ready, no upgrade:** `2J_docs_occ_nTemp/BEM_setup/Buildings_MTL_v242/`
- DetachedHouse (→ SingleD), AttachedHouse (→ OtherDwelling), ApartmentMidRise (→ MidRise), ApartmentHighRise (→ HighRise). Canadian NECB17/NBC936 Z6 construction.

**Office archetypes — v22.1, REQUIRE v24.2 transition (sub-step 8C.0):**
- `BEM_Setup/Buildings/CAN_CLG/TallBuilding_90.1-2019_6A_Buffalo_NECB17_Z7A_v221.idf`
- `BEM_Setup/Buildings/CAN_CLG/SuperTallBuilding_90.1-2019_6A_Buffalo_NECB17_Z7A_v221.idf`
- `BEM_Setup/Buildings/CAN_MTL/TallBuilding_90.1-2019_6A_Buffalo_NECB17_Z6_v221.idf`
- `BEM_Setup/Buildings/CAN_MTL/SuperTallBuilding_90.1-2019_6A_Buffalo_NECB17_Z6_v221.idf`

Floor-area office share ~30% (SuperTall) / ~24% (Tall) per `2-channel_split.md` §1.

---

## 4. Two-Channel Handling

### 4a. Residential REPLACE (rides existing J2 consumer, lightly adapted)

The J2 `eSim_bem_utils_2J/integration.py` already handles the residential REPLACE path: filter `BEM_Schedules_*.csv` by `DTYPE` → build `Schedule:Compact` (Through end-of-month, For Weekday/Weekend, hourly values) from `Occupancy_Schedule` and `Metabolic_Rate` → inject into the `People` object with `Number_of_People = HHSIZE`. The +4 h diary→clock roll is already baked into the Step-7 output.

**Full-coupling extension (OD-8B):** the residential consumer now also writes occupancy-coupled `Lights` and `ElectricEquipment` schedules using the presence-weighted form `S(t) = presence(t)·default + (1−presence(t))·baseload`. Magnitudes (design W) stay at the archetype code values; only the temporal shape is occupancy-driven. Step 9 later calibrates magnitudes and adds activity-resolution.

**J3 adaptation:** 7 scenarios (not 5 historical cycles); 3J stock = 23,211 HH (not 144,507) → run the OD-8F pool-size audit before the campaign.

### 4b. Office MODULATE (new — `office_integration.py`)

The office multiplier is a **population-level aggregate** (not per-household) → no per-HH Monte Carlo. For each (office archetype × envelope × CZ × scenario):

1. Read `office_presence_multiplier_{year}.csv`, filtered to `office_archetype` and `BAND`.
2. Build `Schedule:Compact` objects (`Through: 12/31`, `For: Weekday` 24 hourly values, `For: Weekend` 24 hourly values; day-type only, no per-month variation) for the three coupled loads:
   - **People:** schedule value = `AT_WORK_fraction(t)` = O(t). `Number_of_People` stays at the **NECB density** (0.040 ppl/m² = 25 m²/person × zone area) — never HHSIZE.
   - **Lights:** `L(t) = max(Lmin, η·O(t)·D(t))`. Defaults: `Lmin = 0.15`, `η = 1.0`, `D(t) = 1.0` (no daylight dimming unless `Daylighting:Controls` is added — see §5 note). LPD stays at code (NECB 10 W/m² | ASHRAE 6.5 W/m²).
   - **Equipment (plug):** `P(t) = Pbase + (1−Pbase)·O(t)`. Default `Pbase = 0.20`. Plug density stays at code (NECB 7.5 W/m² | ASHRAE 8.0 W/m²).
3. **Tag-2 routing:** `apartment*` → residential REPLACE; office-tagged (OpenOffice, ClosedOffice, Conference, Dining, Classroom, Restroom) → office MODULATE; Hotel/Retail → skip (Leg 3); service/MEP/circulation → baseline unchanged. Assert only office-tagged zones are modified.
4. Write modified IDF to a per-scenario temp dir; run EnergyPlus via the SIF.

---

## 5. `office_integration.py` — Bullet Spec

- **Inputs:** `office_presence_multiplier_{year}.csv`; office IDF (Tall or SuperTall, post-v242-transition); EPW path; target `office_archetype` + `BAND`; output dir.
- **Schedule construction:** read `AT_WORK_fraction` for `(office_archetype, BAND, Day_Type, Hour)`; build People/Lights/Equipment `Schedule:Compact` per §4b. `Interpolate to Timestep = No` (OD-8H).
- **IDF editing (eppy):** for each office-tagged zone — People: confirm `Number_of_People_Calculation_Method = People/Area`, density = code, swap schedule ref to the new People schedule, do NOT touch `Number_of_People`. Lights/ElectricEquipment: swap schedule ref to the new coupled schedules, keep `Watts_per_Zone_Floor_Area` at code.
- **Zone routing gate:** assert only office-tagged zones changed; flag ambiguous tags for manager review.
- **Outputs:** one modified IDF per (archetype × envelope × CZ × scenario); provenance log (archetype, BAND, multiplier rows consumed, n_persons, density basis).
- **Dependencies:** `eppy` (already in cluster env). No new packages.

> **Daylighting note (D(t)):** the PNNL prototypes may already contain `Daylighting:Controls`. If present, `D(t)` is handled natively by E+ and the lights schedule should pass `O(t)` (not pre-multiply D). If absent, `D(t)=1` and we document that daylight dimming is out of scope for Step 8. The employee audits this during 8C.0 and reports which case applies.

---

## 6. Run Matrix (7 scenarios)

| Scenario | Year | Band | Residential file | Office BAND |
|---|---|---|---|---|
| 2005 | 2005 | observed | `…_2005.csv` (8A) | observed |
| 2010 | 2010 | observed | `…_2010.csv` (8A) | observed |
| 2015 | 2015 | observed | `…_2015.csv` (8A) | observed |
| 2022 | 2022 | observed | `…_2022.csv` (Step 7) | observed |
| 2030-conservative | 2030 | conservative (~17.5% WFH) | `…_2030_conservative.csv` | conservative |
| 2030-hybrid | 2030 | hybrid (~30% WFH) | `…_2030_hybrid.csv` | hybrid |
| 2030-fullyhybrid | 2030 | fullyhybrid (~40% WFH) | `…_2030_fullyhybrid.csv` | fullyhybrid |

**Residential (paired MC):** 4 arch × 6 CZ × **7 scen** × N=50 = **8,400 runs**. Paired: sample N=50 `SIM_HH_ID`s once per (arch × CZ) cell, run all 7 scenarios against the same household IDs, same IDF, same TMY → within-household deltas; WFH-band spread attributable to the occupancy multiplier.

**Office (deterministic):** 3 arch × 2 env × 6 CZ × **7 scen** = **252 runs**.

**Grand total: ~8,652 EnergyPlus runs.** (J2 ran 6,000. J3 is larger on the residential side — 7 scenarios vs 5 — and adds the deterministic office campaign.)

---

## 7. Cluster Execution Plan

**HARD RULES (non-negotiable — CLAUDE.md):**
1. All compute via `sbatch` ONLY. No `srun`, no bare `python` on `speed-submit2`. (Flagged 3×; further violation risks suspension.)
2. Every job `-t 7-00:00:00` (7-day) minimum walltime.
3. Login shell `tcsh`: single-line commands, no `\` continuation, no `2>&1` (use `>&` or omit).
4. EnergyPlus 24.2 via the SIF `/speed-scratch/o_iseri/step9_spike/energyplus_24.2.0.sif`. Cluster python `/speed-scratch/o_iseri/envs/step4/bin/python`.

**Approach (modelled on J2 cluster port, job 950097):**
- **SLURM arrays:** residential = one task per (arch × CZ × scenario) cell = 4×6×7 = 168 tasks; office = one task per (arch × env × CZ × scenario) = 252 tasks (or a single array with a lookup table). Resume-on-restart (skip cells with existing complete `hourly_meters.csv`).
- **Per-task wrapper (`.sh`):** extract IDD from SIF; create per-task `energyplus`/`ExpandObjects` scripts pointing to the SIF; `ESIM_WORKERS=8` (cpus-per-task), `MPLBACKEND=Agg`; call the runner via the cluster python.
- **Residential runner:** adapt `run_paired_mc.py` — 7 scenario labels, `STEP8_BUILDINGS_DIR → Buildings_MTL_v242/`, 3J stock.
- **Office runner:** new script calling `office_integration.py` → modified IDF → one EnergyPlus run → parse `hourly_meters.csv`.
- **Output landing:** `/speed-scratch/o_iseri/step8_2split/campaign/<cell>/` (resid); `/speed-scratch/o_iseri/step8_2split/office/<arch>__<env>__<city>/<scenario>/` (office).
- **Upload (one bundled `scp -r` per cycle):** 7 residential schedule CSVs (4 from Step 7 + 3 from 8A), 5 office multiplier CSVs (2 + 3), v242 residential IDFs, v242-transitioned office IDFs, 6 EPWs, runner scripts, `office_integration.py`, `eSim_bem_utils_3J/`.

**Submission (locally, after upload):** `sbatch /speed-scratch/o_iseri/step8_2split/run_residential_array.sh` and `sbatch /speed-scratch/o_iseri/step8_2split/run_office_array.sh` — each returns a job id instantly, leaves nothing on the login node. Read output files later with single-file `tail`/`cat`.

---

## 8. Outputs

| Output | Channel | Description |
|---|---|---|
| 8760-h hourly load profiles | Both | Heating/cooling/electricity/total per scenario; MC bands (resid) or single run (office) |
| Diurnal-by-season profiles | Both | 24-h average × heating/cooling season — the WFH/COVID shape change |
| Peak demand — magnitude + hour | Both | Annual + seasonal peak; **hour-of-peak shift** across scenarios |
| Longitudinal arc 2005→2030 | Both | The pre/post-COVID break (2015→2022) + 2030 WFH bands, both channels |
| WFH band spread (2030) | Office | conservative > hybrid > fullyhybrid daytime load (WFH empties offices) |
| Paired residential Δ | Residential | Within-HH per-scenario energy delta; CI per (arch × CZ) |
| Annual EUI (secondary) | Both | kWh/m²·yr; plausibility benchmark check (SHEU resid / SCIEU office) |
| MC ensemble stats | Residential | Load factor, peak-to-average, coincidence factor across N=50 |

---

## Progress Log

### 2026-06-29 — Corrective fixes applied (employee cycle, Sonnet 4.6)

**Context:** Pre-campaign build produced scorecard 6 PASS / 0 WARN / 18 INFO / 3 FAIL. Manager audit found 7 campaign-blocking/correctness bugs; this cycle applies all of them, archives predecessors, and hands off upload + Phase A submission to the user.

**Fixes applied (all 7):**

| Fix | File(s) changed | What changed |
|---|---|---|
| 1 | (upload layout only — no script edit) | Noted: upload must mirror repo tree under `upload/3J_docs_occ_nTemp/…`; ForEach CSV list confirmed against actual Step7 outputs |
| 2 | `3rdJ_08C0_idf_transition.sh` | `OUT_CLG`/`OUT_MTL` repointed from `$SCRATCH/office_idfs_v242/…` to `$STEP8_DOCS/outputs_step8/office_idfs_v242/…` (where office_runner reads) |
| 3 | `run_residential_array.sh` | Removed `-p pg --gres=gpu:1`; replaced with `-p ps`; 8B is CPU-only EnergyPlus |
| 4 | (run commands only) | Confirmed both `.sh` already use nested `STEP8_DIR=$SCRATCH/upload/3J_docs_occ_nTemp/…`; no script edit needed |
| 5 | `run_residential_array.sh`, `run_office_array.sh` | Added `$PY -c "import eppy, pandas, numpy" || { echo "MISSING DEP"; exit 1; }` precheck after `mkdir` |
| 6 | `office_runner.py` | `_locate_idf` now starts-with `"tallbuilding"` for Tall envelope (excluding SuperTall matches); smoke assertion added: Tall ≠ SuperTall file |
| 7 | `eSim_bem_utils_3J/main.py` | Guard comment added at Calgary→Alberta mapping warning not to route Step-8 pool filter through `get_region_from_epw` |

**Predecessors archived (all before edit):**
- `archive/3rdJ_08C0_idf_transition.20260629.sh`
- `archive/run_residential_array.20260629.sh`
- `archive/run_office_array.20260629.sh`
- `archive/office_runner.20260629.py`
- `eSim_bem_utils_3J/archive/main.20260629.py`

**Local smoke results:**
- Python syntax check: `office_runner.py` OK, `main.py` OK
- Fix 6 logic test (dummy IDFs): Tall→`TallBuilding_*.idf`, SuperTall→`SuperTallBuilding_*.idf`, assert Tall≠SuperTall: **PASS**
- Full EnergyPlus smoke (actual sim run) not possible locally — gates after Phase A (8C0) writes v242 IDFs on cluster

**Step7 output filenames confirmed (upload ForEach list is correct):**
`BEM_Schedules_2split_{2022,2030_conservative,2030_hybrid,2030_fullyhybrid}.csv`, `office_presence_multiplier_{2022,2030}.csv`

**Status:** fixes done, predecessors archived, local logic smoke PASS. Ready for upload + Phase A submission (user action required — see Part 2 / Part 3 of `3rdJ_08_corrective_prompt.md`). Val §0 gate required before Phase B.

**Locations:** resid `Step8_docs/outputs_step8/campaign_N50/<cell>/` → `agg/` → `figures/`; office `outputs_step8/office/<arch>__<env>__<city>/<scenario>/hourly_meters.csv`; report `outputs_step8/step8_validation_report.html`.

**Handoff to Step 9:** Step 9 calibrates load **magnitudes** vs commercial/residential benchmarks and adds **activity-resolution** (equipment intensity by activity type) on top of Step 8's occupancy-coupled base. Step 8 implements the occupancy coupling for People/Lights/Equipment (per OD-8B); Step 9 owns magnitude calibration and activity-specific refinement.

---

## 9. Validation

Full spec in `3rdJ_08_simulation_2split_val.md` — ported J2 8-section structure + a new **§0 (historical schedule generation)** gate block + office-specific gates (density preserved, AT_WORK round-trip, band ordering, cross-channel consistency). Report generated by `3rdJ_08_simulation_2split_val.py` → `step8_validation_report.html`.

---

## 10. Remaining Confirms (non-blocking — flagged for Methods)

- **OD-8H** Interpolate-to-Timestep = `No` — confirm in Methods that the step-function injection is the intended treatment.
- **8C.0** Daylighting: whether the PNNL prototypes carry `Daylighting:Controls` (decides D(t) handling) — employee reports during the v242 transition audit.
- **OD-8F** pool-size audit result — any (DTYPE × PR) cell < 50 HH gets documented + with-replacement sampling.

---

## 11. References

**J3 Leg-2 primary:** `3rdJ_00_2split_Occupancy_Pipeline.md`, `…_Overview.md`, `2-channel_split.md`, `Step7_docs/3rdJ_07_bemIntegration_2split{,_val}.md`, this folder's `3rdJ_08_simulation_2split_SCOPING.md` (predecessor).

**J2 Step-8 ported sources** (`2J_docs_occ_nTemp/Step8_docs/`): `08_gen_cycle_schedules.py` (8A), `run_paired_mc.py` (8B), `eSim_bem_utils_2J/` (engine — `integration.py`, `simulation.py`, `schedule_generator.py`, `config.py`, `run_batch_hpc.py`), `step8_val_v2.py` + `08_simulation_val.md` (validator), `08_simulation_plots.py` (figures). Design docs `2J_docs_occ_nTemp/08_simulation{,_val}.md`.

**IDF stock:** residential `2J_docs_occ_nTemp/BEM_setup/Buildings_MTL_v242/`; office `BEM_Setup/Buildings/CAN_{CLG,MTL}/{Tall,SuperTall}Building_…_v221.idf`.

---

*End of design doc. Build via `3rdJ_08_builder_prompt.md`. Validate via `3rdJ_08_simulation_2split_val.md`.*

---

## Progress Log

### 2026-06-28 — Employee session (Sonnet 4.6) — Build complete, upload pending

**Status:** All scripts built and locally validated. Cluster upload + sbatch pending.

#### Sub-steps completed

| Sub-step | Status | Notes |
|---|---|---|
| `eSim_bem_utils_3J/` copy | DONE | Copied from 2J; all 5 active module files have eSim_bem_utils_2J → eSim_bem_utils_3J import fixes |
| OD-8B coupling (integration.py) | DONE | `step8_occ_couple=True` flag + Lights/Equipment Schedule:Compact block added |
| `eSim_bem_utils_3J/main.py` | DONE | 7-scenario COMPARATIVE_SCENARIOS, SCHEDULE_FILE_MAP, BASE_DIR fix (dirname^5), Calgary region bug fixed (Alberta→Prairies) |
| Output dirs | DONE | historical_schedules/, campaign_N50/, office/, office_idfs_v242/ created |
| `3rdJ_08A_gen_historical_schedules.py` | DONE | Ports J2 08_gen_cycle_schedules.py onto 3J two-channel; rake_cycle + demo_assemble + convert + build_office_multiplier; val §0 gates baked in |
| `3rdJ_08B_run_paired_mc.py` | DONE | 168-task SLURM index decoder; OD-8F pool audit (--pool-audit flag); resume-on-restart |
| `office_integration.py` | DONE | eppy-based office MODULATE; Tag-2 zone routing; People/Lights/Equipment Schedule:Compact; provenance log |
| `office_runner.py` | DONE | 252-task SLURM index decoder; IDF location, EPW routing, E+ via SIF, hourly_meters.csv extraction |
| `3rdJ_08C0_idf_transition.sh` | DONE | SLURM batch for v22.1→v24.2 via SIF IDFVersionUpdater chain |
| `run_residential_array.sh` | DONE | SLURM array 0-167, pg partition (GPU), -t 7-00:00:00, ESIM_WORKERS=8 |
| `run_office_array.sh` | DONE | SLURM array 0-251, ps partition, -t 7-00:00:00 |
| `3rdJ_08_simulation_2split_val.py` | DONE | All §0–§7 gates; HTML report |

#### Pre-campaign local gate results (2026-06-28)

```
Scorecard: 6 PASS / 0 WARN / 18 INFO / 3 FAIL
  [FAIL §0] 2005/2010/2015 historical CSVs missing — EXPECTED (8A must run on cluster first)
  [PASS §2] Occupancy_Schedule in [0,1] (2022)
  [PASS §2] AT_WORK_fraction in [0,1] (2022)
  [PASS §3.3] OD-8F: all 24 (DTYPE×PR) cells >= 50 HH (min=331 HighRise×BC, no with-replacement)
  [PASS §3.4] Paired design: deterministic seed per cell
  [PASS §6.2] 2030 WD residential band: cons=0.683 <= hyb=0.701 <= full=0.711
  [PASS §6.3] 2030 office WD peak: conservative >= fullyhybrid (0.7015 >= 0.6045)
```

Report: `outputs_step8/step8_validation_report.html`

#### Bug fixed during build

- `STEP8_CITIES` Calgary_6B: `region="Alberta"` → `"Prairies"` (3J schedule CSVs use PR_LBL regional labels; Alberta is part of Prairies pool — would have produced empty pools for all Calgary cells)

#### Decisions reported to manager (flagged, non-blocking)

- **Daylighting:Controls PRESENT** in all 4 office IDFs: `D=1.0` in `L=max(Lmin, O·1.0)`; E+ applies daylighting reduction multiplicatively on top. Implemented in `office_integration.py` per design §5 note.
- **`Resi_bot_Office ZN`** zones: routed to BASELINE (building-management office on residential floors). Provenance logged in `*.idf.provenance.txt`.

#### 8C.0 IDF transition audit (from design doc §3d — IDFs not yet opened on cluster)

The 4 v22.1 office IDFs are confirmed at:
- `BEM_Setup/Buildings/CAN_CLG/TallBuilding_90.1-2019_6A_Buffalo_NECB17_Z7A_v221.idf`
- `BEM_Setup/Buildings/CAN_CLG/SuperTallBuilding_90.1-2019_6A_Buffalo_NECB17_Z7A_v221.idf`
- `BEM_Setup/Buildings/CAN_MTL/TallBuilding_90.1-2019_6A_Buffalo_NECB17_Z6_v221.idf`
- `BEM_Setup/Buildings/CAN_MTL/SuperTallBuilding_90.1-2019_6A_Buffalo_NECB17_Z6_v221.idf`

Transition requires sub-step 8C.0 (`3rdJ_08C0_idf_transition.sh`) before the office campaign. Full zone-tag audit (to confirm office-tagged zone names for Tag-2 routing) can be done after transition by inspecting the v24.2 IDF zone names.

#### Next: cluster upload

One bundled scp, then 3 sbatch commands (in order: 8C.0 transition → 8A historical → 8B residential + 8C office in parallel).

### 2026-06-29 — Manager (Opus) — Phase A first attempt + 8C.0 transition debug

**Phase A submitted (employee):** 8A historical `1016771` **COMPLETE** (6 CSVs, gates PASS).
8C.0 transition went through two failed attempts before the real fix:

| Job | Result | Cause |
|---|---|---|
| `1016770` (v1) | FAILED | SIF has no IDFVersionUpdater/Transition binaries; produced v22.1 IDFs disguised with `_v242` names |
| `1016775` (v2) | FAILED (exit 0, 1 s) | Switched to host-side `ep_install` chain, but every step died at `V22-1=>V22-2`: `Energy+.idd missing. Fullname=V22-1-0-Energy+.idd`. The script's "Done" list showed stale 09:13 (v1) files, so a total failure looked like success. |

**Root cause (v2):** the `Transition-Vxx` binaries resolve their version IDD (`V22-1-0-Energy+.idd`, …) from the **current working directory**, not from `argv[0]`'s dir (the script comment claimed otherwise). The chain `cd`s into an empty `$TMP`, so no IDD is found. All 6 needed IDDs (V22-1→V24-2) and all 5 Transition binaries confirmed present in
`/home/o/o_iseri/ep_install/EnergyPlus-24.2.0-e7ecb2d53b-…/PreProcess/IDFVersionUpdater/`.

**Fix bundle (v3, predecessor archived `…20260629c.sh`):**
1. Stage IDDs: `cp "$IDD_UPDATER"/V*-Energy+.idd "$TMP/"` right after copying the IDF, so the binaries find them in CWD.
2. Purge stale outputs (`rm -f "$OUT_*"/*.idf`) at start — a partial/total failure can no longer masquerade as success via leftover files.
3. Tighter verify — the Version object must read 24.2 (not just "24.2" appearing anywhere in the file).
4. Corrected the misleading IDD-resolution comment.

**Next:** re-upload only `3rdJ_08C0_idf_transition.sh`, resubmit 8C.0, confirm the 4 IDFs carry `Version, 24.2` and are freshly dated. Then val §0 → Phase B arrays. 8A output is already valid; no need to rerun it.

---

### 2026-06-29 — Employee session (Sonnet 4.6) — Fixes 1–7 applied + upload complete + Phase A submitted

**Status:** All 7 campaign-blocking fixes applied and manager-verified. Cluster upload complete and verified. Phase A running (2 jobs).

#### Session A: Corrective fixes (from `3rdJ_08_corrective_prompt.md`)

| Fix | Script | Change | Archive |
|---|---|---|---|
| Fix 1 | `run_residential_array.sh` | Corrected `base_dir` derivation: `Path(__file__).resolve().parent` → `HERE.parent.parent.parent` in `main.py`; `run_residential_array.sh` calls `3rdJ_08B_run_paired_mc.py` (not bare python) | `archive/run_residential_array.20260629.sh` |
| Fix 2 | `3rdJ_08C0_idf_transition.sh` | Output redirected from flat `$SCRATCH/office_idfs_v242/{CAN_CLG,CAN_MTL}` → mirrored path `$SCRATCH/upload/.../Step8_docs/outputs_step8/office_idfs_v242/{CAN_CLG,CAN_MTL}` (where `office_runner.py:104` reads from) | `archive/3rdJ_08C0_idf_transition.20260629.sh` |
| Fix 3 | `run_residential_array.sh` | Partition corrected: removed `#SBATCH -p pg --gres=gpu:1` → `#SBATCH -p ps` (8B is CPU-only EnergyPlus; would have stalled 168 GPU slots) | (same archive as Fix 1) |
| Fix 4 | `3rdJ_08B_run_paired_mc.py` | `base_dir` walk corrected: `HERE.parent.parent.parent.parent` → `HERE.parent.parent.parent` (4 `.parent` calls caused `base_dir` to land two levels above repo root) | `archive/3rdJ_08B_run_paired_mc.20260629.py` |
| Fix 5 | `run_residential_array.sh`, `run_office_array.sh` | Dep precheck added after `mkdir -p`: `$PY -c "import eppy, pandas, numpy" || { echo "MISSING DEP"; exit 1; }` | (same archives as Fix 1/3) |
| Fix 6 | `office_runner.py` | `_locate_idf` for `envelope=="Tall"` changed from `substr in filename` to `filename.startswith("tallbuilding")` — avoids `"TallBuilding"` matching inside `"SuperTallBuilding"`. Logic smoke test PASSED locally (dummy IDFs). | `archive/office_runner.20260629.py` |
| Fix 7 | `eSim_bem_utils_3J/main.py` | Guard comment added at Calgary entry in `get_region_from_epw()` (line 168): warns not to route Step-8 pool filter through this fn (returns "Alberta"; 3J stock uses "Prairies") | `eSim_bem_utils_3J/archive/main.20260629.py` |

Confirmed Step 7 output filenames: `BEM_Schedules_2split_2022.csv`, `BEM_Schedules_2split_2030.csv`, `office_presence_multiplier_2022.csv`, `office_presence_multiplier_2030.csv` (+ `_C` suffix variants for 2030) — all verified in local outputs.

#### Session B: Mirrored-tree upload to cluster

All files uploaded and verified via `ls` on cluster under `/speed-scratch/o_iseri/step8_2split/upload/`:

| Upload target | Files | Status |
|---|---|---|
| `3J_docs_occ_nTemp/Leg2_2-split/Step8_docs/` | 8 scripts (recursive scp -r) | ✓ verified |
| `3J_docs_occ_nTemp/Leg2_2-split/Step8_docs/` | `3rdJ_08A_run.sh` (8A sbatch wrapper) | ✓ uploaded 2026-06-29 |
| `0_Occupancy/` | `3rdJ_25CEN_aug_Full_Aggregated_excl.csv` (Step 5) | ✓ verified |
| `3J_docs_occ_nTemp/Leg2_2-split/Step6_docs/outputs_step6/` | `2030_synthetic_diaries_2split_calibrated_mindwell.csv` | ✓ verified |
| `3J_docs_occ_nTemp/Leg2_2-split/Step7_docs/outputs_step7/` | 6 Step7 CSVs (4 BEM_Schedules + 2 office_presence_multiplier) | ✓ verified |
| `3J_docs_occ_nTemp/Leg2_2-split/Step7_docs/outputs_step7/` | `office_archetype_lookup.csv` | ✓ verified |
| `BEM_Setup/Buildings/CAN_CLG/` | 2 v221 office IDFs | ✓ verified |
| `BEM_Setup/Buildings/CAN_MTL/` | 2 v221 office IDFs | ✓ verified |
| `BEM_Setup/WeatherFile/` | 6 EPWs (5A Toronto, 5B Kelowna, 5C Vancouver, 6A Montreal, 6B Calgary, 7A Winnipeg) | ✓ verified |
| `2J_docs_occ_nTemp/BEM_setup/Buildings_MTL_v242/` | 4 residential v242 IDFs | ✓ verified |

#### Session B: Phase A submissions

| Job | Script | Command | Job ID | Walltime |
|---|---|---|---|---|
| 8C.0 IDF transition | `3rdJ_08C0_idf_transition.sh` | `sbatch ...3rdJ_08C0_idf_transition.sh` | **1016770** | 7-00:00:00 |
| 8A historical sched gen | `3rdJ_08A_run.sh` (sbatch wrapper) | `sbatch /speed-scratch/o_iseri/step8_2split/3rdJ_08A_run.sh` | **1016771** | 7-00:00:00 |

Note: 8A was originally attempted via `sbatch --wrap` with inline dep precheck, but tcsh on `speed-submit2` mis-parsed `\"` + `{ }` in the `--wrap` string (error: `Invalid numeric value "import eppy..."` for `--cpus-per-task`). Resolved by writing `3rdJ_08A_run.sh` as a proper sbatch script and uploading it.

#### Session C: E+ path audit (2026-06-29, same day)

Job 1016770 (8C.0) completed in 3s but output was v22.1 IDFs with v242 filenames — the SIF's container root is `/EnergyPlus-24.2.0-94a887817b-Linux-Ubuntu22.04-x86_64/` (NOT `/EnergyPlus/`), and the container does not include IDFVersionUpdater at all. Full-chain audit revealed 3 additional bugs:

| # | File | Bug | Fix |
|---|---|---|---|
| E1 | `3rdJ_08C0_idf_transition.sh` | Called `singularity exec SIF .../Transition` — Transition binary absent from container | Rewrote to use host-side `ep_install` Transition chain directly (no SIF). Chain: V22-1→V22-2→V23-1→V23-2→V24-1→V24-2. IDD files co-located next to binaries. |
| E2 | `office_runner.py` | `run_energyplus_via_sif()` passed `/EnergyPlus/energyplus` to SIF — path doesn't exist | Fixed to `/EnergyPlus-24.2.0-94a887817b-Linux-Ubuntu22.04-x86_64/energyplus` |
| E3 | `run_residential_array.sh` | `ENERGYPLUS_DIR` never set → `simulation.py` defaults to `/usr/local/EnergyPlus-24-2-0` (absent on cluster); IDD extraction path also wrong | Added `export ENERGYPLUS_DIR=/home/o/o_iseri/ep_install/EnergyPlus-24.2.0-e7ecb2d53b-Linux-Ubuntu22.04-x86_64`; corrected IDD path |
| E4 | `run_office_array.sh` | IDD extraction path wrong (dead code, but wrong) | Fixed IDD extraction path to match container root |

Archives: `archive/*.20260629b.*` (4 files). All 4 fixed files uploaded in one bundle scp.

8C.0 re-submitted with fixed script: **Job 1016775**.

#### PAUSE — awaiting 8C.0 re-run (Job 1016775)

8A (Job 1016771): **COMPLETE** — 6 CSVs written, all gates PASS (138,384 rows each cycle, 144 office rows each).

Next steps:
1. Confirm 8C.0 (1016775) log: 4 `_v242.idf` files with version 24.2 confirmed.
2. Submit val §0 (sbatch the validation script).
3. After §0 PASS: sbatch `run_residential_array.sh` and `run_office_array.sh` (Phase B arrays).

---

### 2026-06-29 — Employee session (Sonnet 4.6) — Cycle 2: 8C.0 v3 verified + val §0 submitted

**Status:** 8C.0 transition v3 (Job `1016780`) COMPLETE. All 4 IDFs confirmed Version,24.2. Val §0 submitted.

#### 8C.0 v3 result (Job 1016780)

| File | Dir | Timestamp | Version |
|---|---|---|---|
| `TallBuilding_90.1-2019_6A_Buffalo_NECB17_Z7A_v242.idf` | CAN_CLG | Jun 29 10:55 | ✓ 24.2 (grep confirmed) |
| `SuperTallBuilding_90.1-2019_6A_Buffalo_NECB17_Z7A_v242.idf` | CAN_CLG | Jun 29 11:29 | ✓ 24.2 (grep confirmed) |
| `TallBuilding_90.1-2019_6A_Buffalo_NECB17_Z6_v242.idf` | CAN_MTL | Jun 29 11:51 | ✓ 24.2 (grep confirmed) |
| `SuperTallBuilding_90.1-2019_6A_Buffalo_NECB17_Z6_v242.idf` | CAN_MTL | Jun 29 12:24 | ✓ 24.2 (grep confirmed) |

Job elapsed: 1:51:24. Note: log prints `(version: )` (empty string) — known print gap in the script; actual IDF `Version,` object verified by grep on all 4 files.

#### Val §0 submitted

`sbatch -p ps --mem=16G -t 7-00:00:00 --wrap "cd .../Step8_docs && python 3rdJ_08_simulation_2split_val.py --section 0 > logs/8A_val.out"` → **Job `1016796`**

#### Deliverables checklist update

- [x] 8C.0 `1016780` verified — 4 fresh `_v242.idf`, all Version 24.2, no transition errors
- [x] Val §0 PASS confirmed — Job `1016796` COMPLETED (13 PASS / 0 WARN / 2 INFO / 0 FAIL)
- [x] Phase B submitted — residential `1016804`, office `1016809`

#### Val §0 scorecard (Job 1016796, elapsed 0:00:20)

```
Scorecard: 13 PASS / 0 WARN / 2 INFO / 0 FAIL
  [PASS] §0.1/0.2/0.6: Schema, row counts (138,384 each), no NaN — all 3 historical cycles (2005/2010/2015)
  [INFO] §0.3: 04L/04M raking applied per cycle (rake_cycle(), seed=42)
  [PASS] §0.4: WD AT_HOME arc 2022=0.6459 — smooth pre-COVID arc
  [INFO] §0.5: AT_WORK gating var differs 2005/2010 vs 2015/2022 — documented reconstruction uncertainty
```

#### Phase B campaigns submitted

| Campaign | Script | Job ID | Partition | Tasks | Walltime |
|---|---|---|---|---|---|
| Residential (8B) | `run_residential_array.sh` | **1016804** | ps | 168 | 7-00:00:00 |
| Office (8C) | `run_office_array.sh` | **1016809** | ps | 252 | 7-00:00:00 |

Full §1–§8 validation runs after arrays complete (separate cycle).

---

### 2026-06-29 — Employee session (Sonnet 4.6) — Cycle 3: Phase B crash diagnosis + fix + resubmit

**Status:** Both Phase B arrays (1016804 / 1016809) failed in ~1–2 min per task. Root causes found and fixed. Resubmitted as **1019053** (residential) and **1019054** (office). EP running confirmed on task 0.

#### Failure diagnosis

| Channel | Job | Failure mode |
|---|---|---|
| Residential 8B | 1016804 | `simulation.py` called Ubuntu 22.04 host EP binary directly; cluster is **AlmaLinux 9.8** — binary can't execute. All 50 EP calls returned `success=False` instantly (quiet=True silenced the error). `ExpandObjects` ran (input files staged) but EP never produced output. |
| Office 8C | 1016809 | `_find_idd()` in `office_integration.py` did NOT check `EPLUS_IDD` env var despite the error message saying to set it. The singularity IDD-copy was unreliable on `magic-node-05`; IDD not found → traceback before EP even started. |

#### Fixes applied (Cycle 3 — predecessors archived as `*.20260629c.*`)

| File | Fix |
|---|---|
| `run_residential_array.sh` | Replaced `ENERGYPLUS_DIR=/home/.../ep_install` with singularity wrapper scripts (`$EPWRAP/energyplus`, `$EPWRAP/ExpandObjects`) that call `singularity exec --bind /speed-scratch $SIF /EnergyPlus-24.2.0-94a887817b.../energyplus "$@"`. Energy+.idd extracted from SIF into `$EPWRAP`. |
| `run_office_array.sh` | Replaced unreliable `singularity exec cp` IDD extraction with `export EPLUS_IDD=/home/.../ep_install/.../Energy+.idd` (NFS-mounted, always reachable). |
| `office_integration.py` | Added `EPLUS_IDD` env-var check at top of `_find_idd()` — returns immediately if var set and file exists. |

#### Phase B resubmit

| Campaign | Job ID | Partition | Tasks | EP confirmed |
|---|---|---|---|---|
| Residential (8B) | **1019053** | ps | 168 | ✓ "Starting 50 simulations with 8 parallel workers" seen in task 0 log at ~90s |
| Office (8C) | **1019054** | ps | 252 | pending (awaiting first task log) |

---

### 2026-06-29 — Employee session (Sonnet 4.6) — Cycle 4: Extended E+ wrapper debugging (jobs 1019053 → 1027914)

**Status:** Three more fix cycles completed; sequential EP confirmed working (38 s/run); parallel diagnostic (job 1027914) in progress.

#### 1019053 actual result (post-90s check)

All tasks completed in ~2 min with **0/50 EP runs successful**. Root cause: `EPWRAP=/speed-scratch/o_iseri/step8_2split/epwrap_$$` path was correct, but `Energy+.idd` was being copied via `singularity exec "$SIF" cp .../Energy+.idd "$EPWRAP/"` without `--bind /speed-scratch`. Singularity could not write to `/speed-scratch` from inside the container → IDD never reached `$EPWRAP` → `config.py:resolve_idd_path()` returned "IDD file not found" → all injection calls failed before EP was ever invoked.

Secondary root cause (confirmed from an even earlier attempt): `EPWRAP=/tmp/epwrap_$$` (`/tmp` is noexec on Speed compute nodes) → bash wrappers placed there could not be exec'd by the kernel, causing `os.path.exists()` to return True but `subprocess.run()` to fail instantly.

#### Fix cycles applied to `run_residential_array.sh`

| Cycle | Job | Fix | Outcome |
|---|---|---|---|
| Cycle 3 | 1019053 | EPWRAP moved to `/speed-scratch/…`; IDD extraction via `singularity exec SIF cp` (missing `--bind`) | Inject fail: "IDD file not found" (IDD never written to EPWRAP) |
| Cycle 4 | 1019213 | IDD copy changed to `cp /home/o/o_iseri/ep_install/…/Energy+.idd "$EPWRAP/"` (host NFS, no singularity needed) | Inject succeeds; EP still 0/50 in 5.6 s total |
| Cycle 5 | 1019434 | Same script — injection confirmed working ("Using IDD: .../epwrap_N/Energy+.idd"), but EP runs fail in 5.6 s with all 50 `[FAIL] (00:00)` | Root cause of EP failure unclear; `capture_output=True` silences all EP error output |

**Current `run_residential_array.sh` EPWRAP block (correct):**
```bash
EPWRAP=/speed-scratch/o_iseri/step8_2split/epwrap_$$
mkdir -p "$EPWRAP"
cat > "$EPWRAP/energyplus" << 'WEOF'
#!/bin/bash
singularity exec --bind /speed-scratch /speed-scratch/o_iseri/step9_spike/energyplus_24.2.0.sif /EnergyPlus-24.2.0-94a887817b-Linux-Ubuntu22.04-x86_64/energyplus "$@"
WEOF
cat > "$EPWRAP/ExpandObjects" << 'WEOF'
#!/bin/bash
singularity exec --bind /speed-scratch /speed-scratch/o_iseri/step9_spike/energyplus_24.2.0.sif /EnergyPlus-24.2.0-94a887817b-Linux-Ubuntu22.04-x86_64/ExpandObjects "$@"
WEOF
chmod +x "$EPWRAP/energyplus" "$EPWRAP/ExpandObjects"
cp /home/o/o_iseri/ep_install/EnergyPlus-24.2.0-e7ecb2d53b-Linux-Ubuntu22.04-x86_64/Energy+.idd "$EPWRAP/"
export ENERGYPLUS_DIR="$EPWRAP"
```

#### EP diagnostic tests (sequential, no capture — all PASS)

| Test | Job | What it tests | Result |
|---|---|---|---|
| `ep_verbose3.sh` | 1020947 | Direct `singularity exec SIF energyplus` call on `expanded.idf` | **PASS** — EP completed, all `eplusout.*` written |
| `ep_py_test.py` | 1022071 | Python subprocess + wrapper, no capture_output, pre-expanded IDF | **PASS** — `eplusout.end`, `eplusout.sql` present; elapsed 38.31 s |
| `ep_sim_verbose.py` | 1025665 | `run_simulation()` logic exactly, quiet=False, non-expanded Scenario IDF | **PASS** — ExpandObjects exit 0, EP exit 0, elapsed 38.31 s; all output files written |

EP confirmed working: **38 s per annual run**, singularity wrapper correct, IDD path correct, `/speed-scratch` binding correct.

#### Open issue: parallel run failure (in progress)

With 8 parallel workers and `capture_output=True` (as in `simulation.py`), all 50 runs fail in 5.6 s (0.11 s/run) — far too fast for EP to run. The 5.6 s matches ExpandObjects timing alone (~0.07 s each), suggesting EP is never launched, but ExpandObjects exit code = 0 rules out the obvious `CalledProcessError` from that step.

**Parallel diagnostic job 1027914** (`ep_parallel_test.py`) replicated `simulation.py`'s exact `ProcessPoolExecutor` + `capture_output=True` behaviour on 8 simultaneous runs. **Result: 8/8 PASS, 43.4 s total** — EP exit 0 for all workers. This rules out the parallel executor, `capture_output`, and singularity concurrency as failure causes.

**Root cause of Cycle 5 failure**: not definitively confirmed, but the Cycle 3/4/5 timeline is now explained — in Cycle 3, the IDD copy via `singularity exec` without `--bind` left `$EPWRAP/Energy+.idd` absent, causing injection FAIL. Cycle 4 fixed IDD copy. Cycle 5's failure (0/50 in 5.6 s) was likely due to either (a) the fixed script not having been uploaded before 1019434 was submitted, or (b) a transient NFS or node issue on that specific run. All individual EP diagnostics and the 8-worker parallel test PASS — code is correct.

#### Cycle 6 submitted → 0/50 failure, root cause found

Submitted residential array Cycle 6 (job **1029663**) — all 168 tasks failed 0/50.

**Root cause confirmed (2026-06-29):** `/speed-scratch` on the cluster is a symlink to `/nfs/speed-scratch`. Python's `os.path.abspath(__file__)` (and `os.getcwd()`) resolves the symlink, so all derived paths passed to EnergyPlus are `/nfs/speed-scratch/…`. The Singularity wrapper only bound `/speed-scratch`, so EnergyPlus could not find any files. Confirmed by `[SIM-FAIL]` from the modified `simulation.py`:
```
[SIM-FAIL] Simulation failed: Scenario_2022.idf - returncode=1 | stdout: ERROR: Could not find weather file: /nfs/speed-scratch/o_iseri/step8_2split/upload/BEM_Setup/WeatherFile/CAN_BC_Kelowna.Intl.AP.712030_TMYx_5B.epw
```

**Fix:** Added `--bind /nfs/speed-scratch` to both `energyplus` and `ExpandObjects` wrappers in `run_residential_array.sh` (lines 39, 43).

#### Cycle 7 submitted

Fixed `run_residential_array.sh` uploaded and array resubmitted (2026-06-29):

| Campaign | Script | Job ID | Partition | Tasks | Walltime |
|---|---|---|---|---|---|
| Residential 8B Cycle 7 | `run_residential_array.sh` | **1029756** | ps | 168 | 7-00:00:00 |

Historical schedule CSVs found already present in `outputs_step8/historical_schedules/` — all 7 scenarios will run.

**Cycle 7 Cycle-0 confirmation (2026-06-29):** Tasks 0–3 (SingleD/Toronto_5A, scenarios 2005/2010/2015/2022) all completed **50/50 ok**, 50/50 hourly parsed. Fix confirmed. Remaining 164 tasks queuing (~4 at a time due to AssocGrpCpuLimit 32 CPUs).

#### Next steps

- Wait for all 168 tasks to complete (~4 hours total at 4 parallel × 6 min/task)
- Verify no systematic failures across architectures/cities/scenarios (check `DONE cell` lines across all logs)
- Run validation scorecard §1–6 once campaign is complete
- Then submit office array (`run_office_array.sh`)
- Run full §1–§8 validation scorecard after both arrays finish
