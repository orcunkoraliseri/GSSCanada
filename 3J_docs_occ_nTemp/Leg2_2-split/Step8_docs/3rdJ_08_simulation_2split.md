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
