# Step 7 — BEM/UBEM Integration: Implementation Plan
### 21CEN22GSS Aug Pipeline: Calibrated Occupancy → EnergyPlus Schedules
#### GSS Occupancy Pipeline — Detailed Implementation Specification

---

## GOAL

Convert the **calibrated-J3 occupancy dataset** (Step 4 model + Phase 8B raking, linked to the
Census 2021 dwelling stock in Step 5 and forecast to 2030 in Step 6) into the **13-column
hourly-per-household BEM schedule** that `eSim_bem_utils/main.py` consumes for EnergyPlus.
One file per scenario year: `BEM_Setup/BEM_Schedules_2022.csv` (current stock) and
`BEM_Setup/BEM_Schedules_2030.csv` (forecast). Each household carries a Weekday and a Weekend
schedule of 24 hourly values for two channels — **occupancy probability** (fraction of members
home) and **metabolic rate** (W/person) — plus dwelling and geography attributes inherited
from the Step 5 linkage.

Script: **`2J_docs_occ_nTemp/07_aug_to_bem.py`** (OP4). Run-from-anywhere, `seed=42`, reversible
(backs up the prior CSV to a `*_CLASSIC_BAK_2026-05-31.csv` before overwriting).

---

## PREREQUISITES & INPUTS

### Input Files

| File | Location | Content | Rows | Key Columns |
|---|---|---|---|---|
| `21CEN22GSS_aug_Full_Aggregated_excl.csv` | `0_Occupancy/Outputs_21CEN22GSS/aug_pipeline/` | **2022 stock** — calibrated (post-link-raked, 8B-5b) linked persons, post-exclusion; one row per person with dwelling vars | 285,367 (post Jul-9 Step-5 refresh; −52 vs prior 285,419) | HH_ID, DDAY_STRATA, act30_001–048, hom30_001–048, HHSIZE, DTYPE, BEDRM, CONDO, ROOM, REPAIR, PR, MATCH_TIER |
| `2030_synthetic_diaries_joint_raked.csv` | `0_Occupancy/Outputs_21CEN22GSS/forecast_2030/` | **2030 forecast** — calibrated structural-break diaries (canonical **joint** rake: act30 + hom30; hom30 WD 78.44 / Sat 79.15 / Sun 81.48; read via `--joint`) | 37,008 (12,231 / 12,406 / 12,371) | DDAY_STRATA, CYCLE_YEAR=2030, act30_001–048, hom30_001–048 |

> The 2030 file carries **occupancy + activity only**; dwelling/geography attributes are taken
> from the 2022 stock via `assemble_2030()` (stratum-matched draw, `seed=42`) so the forecast
> rides on the same 144,465-household frame.

### Confirmed Data Characteristics

| Property | Value |
|---|---|
| Households (both years) | 144,465 |
| Persons (2022 stock, post-exclusion) | 285,367 (~1.98 per HH) |
| act30 range | {1..14}, 0% NaN both files, all strata |
| hom30 range | {0, 1}, hard binary (calibrated) |
| DDAY_STRATA | 1 = Weekday, 2 = Saturday, 3 = Sunday |
| Activity code 5 | Sleep & Naps & Resting (70 W — metabolic anchor) |
| Occupancy calibration | hom30 **raked** (8B-5b for 2022; structural-break for 2030) |
| Activity calibration | act30 **joint-raked (calibrated)** — `05_postlink_rake.py --joint` (see Risk Register) |

---

## BACKGROUND

### Why this converter / the 13-column format

`eSim_bem_utils/main.py` consumes a flat **13-column hourly-per-household** CSV (one row per
`SIM_HH_ID × Day_Type × Hour`). The calibrated occupancy lives in 48-slot (30-min) diary
format. `07_aug_to_bem.py` performs the slot→hourly, per-person→per-household, and
3-stratum→2-day-type reductions in a single pass, emitting exactly the schema the BEM consumer
expects. No EnergyPlus objects are written here — that is the consumer's job downstream.

### Two-day-type reduction (3 strata → Weekday / Weekend)

Per `integration.py`, the BEM layer is **2-day-type**: `Schedule:Compact` carries a Weekday
profile and a Weekend profile. The converter maps `DDAY_STRATA {1,2,3} → {Weekday, Weekend,
Weekend}` — Saturday and Sunday are **pooled** into a single Weekend schedule. This is a
deliberate deviation from the planned 3-type output (see Deviations) and collapses the
calibrated Sat (79.15%) vs Sun (81.48%) distinction (~2.3 pp).

### Metabolic mapping (activity code → W/person)

Each 30-min activity code is mapped to a metabolic heat-output rate via the project's
established `BEMConverter.metabolic_map` (from `21CEN22GSS_occToBEM.py`); unknown codes fall
back to 100 W:

```python
MET = {0:0, 1:125, 2:175, 3:190, 4:195, 5:70, 6:105, 7:170,
       8:110, 9:90, 10:85, 11:245, 12:105, 13:140, 14:135}   # watts/person
```

Code 5 (Sleep) = 70 W anchors the overnight slots. The full code→activity legend is the Step 4
14-category crosswalk. **The W/person values are now sourced and verified** against the *2024
Adult Compendium of Physical Activities*: the map is Compendium MET values scaled by a constant
**70 W/MET** (recovered exactly from Sleeping 1.0→70 W and Eating 1.5→105 W). Full crosswalk,
the 70 W/MET (~60 kg reference) basis, and three minor flags → **`07_metabolicMap_verification.md`**.

### Day-type completion (donor-draw, `seed=42`)

GSS assigns **one diary day per respondent**, so most households appear in only one
`DDAY_STRATA`. `integration.py` rejects any household lacking either day-type. `complete_day_types()`
fills the missing day by a **donor-draw**: for a Weekday-only HH it draws a *genuine* Weekend
diary from the in-frame weekend pool (Sat+Sun), per member, keeping the HH's own dwelling
attributes; symmetrically for Weekend-only HHs. This preserves the calibrated weekend marginal
(an earlier *copy-day* completion diluted it by −2.76 pp). The imputed day's within-HH
co-presence is synthetic, but BEM consumes only the occupancy fraction + metabolic rate (not
pairwise co-presence), so the approximation is harmless to the energy model.

---

## OUTPUT FORMAT

13 columns, one row per `SIM_HH_ID × Day_Type × Hour`:

| Column | Source | Notes |
|---|---|---|
| `SIM_HH_ID` | HH_ID (renamed) | 144,465 unique |
| `Day_Type` | DDAY_STRATA → {Weekday, Weekend} | Sat+Sun pooled |
| `Hour` | 0–23 | 48 half-hour slots averaged in pairs |
| `HHSIZE`, `DTYPE`, `BEDRM`, `CONDO`, `ROOM`, `REPAIR` | Step 5 linkage (`first()` per HH) | dwelling attributes |
| `PR` | province code → region label | Atlantic / Quebec / Ontario / Prairies / Alberta / BC / Northern Canada |
| `MATCH_TIER` | Step 5 linkage | 1_Perfect / 2_Core / 3_Constraints |
| `Occupancy_Schedule` | mean(hom30) over HH members → hourly | fraction of members home, [0,1], 3 dp |
| `Metabolic_Rate` | mean(MET[act30]) over HH members → hourly | W/person, 1 dp |

**Row math:** 144,465 HH × 2 day-types × 24 hours = **6,934,320 rows** per file.
`DTYPE` is relabelled: code 2 (Apartment) → `HighRise` (BEDRM ≤ 1) / `MidRise` (BEDRM ≥ 2);
1 → `SingleD`; 3 → `OtherDwelling`; 8 → `"8"` (matches classic).

---

## HARD GATES

Inline acceptance asserts in `07_aug_to_bem.py` `main()` — all must pass before write-out:

| Gate | Threshold | Rationale |
|---|---|---|
| Day_Type domain | ⊆ {Weekday, Weekend} | integration.py 2-day-type contract |
| Hour range | all ∈ [0, 23] | hourly schedule |
| Occupancy range | all ∈ [0, 1] | probability/fraction |
| Metabolic non-negative | all ≥ 0 | physical |
| Day-type coverage | **every HH has exactly 2 day-types** | integration.py rejects partial HHs |

---

## IMPLEMENTATION SUB-STEPS

### Sub-step 7A — Input audit
Confirm the 2022 stock is the calibrated `_excl` file and the 2030 diaries are the activated
structural-break canonical (WD 78.44 / Sat 79.15 / Sun 81.48); confirm act30/hom30 ranges and 0 NaN.

### Sub-step 7B — Assemble (2030 only)
`assemble_2030()`: copy the 2022 stock frame; for each stratum `k`, overwrite each person's
`act30+hom30` with a `seed=42` stratum-matched draw from the 2030 diary pool. Dwelling/geography
attributes are retained from the stock. (2022 path skips this — reads the stock directly.)

### Sub-step 7C — Day-type completion
`complete_day_types()`: donor-draw the missing day-type per household (see Background).

### Sub-step 7D — Convert
`convert()`: rename HH_ID→SIM_HH_ID; map Day_Type; group by (SIM_HH_ID, Day_Type); mean hom30
→ occupancy, mean MET[act30] → metabolic; reshape 48 → 24 hourly (average each slot pair);
relabel DTYPE/PR; assemble the 13-column frame.

### Sub-step 7E — Acceptance gates + atomic write
Run the 5 asserts; back up any existing target to `*_CLASSIC_BAK_2026-05-31.csv` (gated, once);
write to `.tmp` then `os.replace` → `BEM_Setup/BEM_Schedules_<year>.csv` (float_format `%.3f`).

---

## DEVIATIONS FROM PLANNED STEP 7

The pipeline-overview docs (`00_GSS_Occupancy_Pipeline.md`, `..._Overview.md`) specified a
richer Step 7. What was actually built vs. planned:

| Plan element | Status | Built / Gap |
|---|---|---|
| Occupancy probability 0–1 | ✅ done (hourly) | 48 half-hour slots averaged → 24 hourly; **per-household**, not per-archetype (more granular than planned) |
| Metabolic gains (ASHRAE 55 / ISO 7730) | ✅ done (reused map) | `MET` from BEMConverter; **not re-derived/cited** to ASHRAE — paper-prep check pending |
| Stratify Weekday / Sat / Sun (3) | ⚠️ **2** | Sat+Sun pooled → Weekend (integration.py is 2-day-type); loses Sat/Sun 2.3 pp split |
| Province → ASHRAE climate zone | ⚠️ partial | PR → **region label** only; climate differentiation deferred to the EnergyPlus `.epw` weather-file stage |
| EnergyPlus `Schedule:Compact` objects | ❌ downstream | This step emits the 13-col CSV; `eSim_bem_utils/main.py` builds the IDF schedules |
| CSV lookup × archetype × climate × strata | ⚠️ shape differs | CSV is keyed per-household with dwelling attrs attached, not an archetype×zone lookup |
| UBEM / CityGML-ready | ❌ not done | future work |

---

## OUTPUT FILES

| File | Location | Content |
|---|---|---|
| `BEM_Schedules_2022.csv` | `BEM_Setup/` | 6,934,320 rows; calibrated 2022 stock schedules — EnergyPlus input |
| `BEM_Schedules_2030.csv` | `BEM_Setup/` | 6,934,320 rows; calibrated 2030 forecast schedules — EnergyPlus input |
| `BEM_Schedules_2022_CLASSIC_BAK_2026-05-31.csv` | `BEM_Setup/` | backup of the pre-OP4 (classic-pipeline) 2022 file |
| `BEM_Schedules_2030_CLASSIC_BAK_2026-05-31.csv` | `BEM_Setup/` | backup of the pre-OP4 2030 file |

---

## SCRIPT EXECUTION ORDER

```
Sub-step 7A — Input audit (read-only)
  py -c "..."   # confirm _excl + activated 2030 ranges

Sub-step 7B–7E — Convert + write (one command per year)
  py 2J_docs_occ_nTemp/07_aug_to_bem.py --year 2022
  py 2J_docs_occ_nTemp/07_aug_to_bem.py --year 2030 --joint   # canonical: joint act30+hom30 rake

Validation report (built — runs per year)
  py 2J_docs_occ_nTemp/07_bemIntegrationGSS_val.py            # both years
  py 2J_docs_occ_nTemp/07_bemIntegrationGSS_val.py --year 2030
  # → outputs_step7/step7_validation_report_{2022,2030}_v2.html
```

**Prerequisites:** Step 5 `_excl` aggregated file (calibrated 2022 stock) and Step 6
activated `2030_synthetic_diaries_joint_raked.csv` (canonical, `--joint`) must both exist and pass their own gates.

---

## LOCAL REQUIREMENTS

All sub-steps run locally (CPU only). No GPU, no sbatch. (The downstream EnergyPlus simulation
runs are the first true compute step and may go to the cluster.)

| Sub-step | Runtime | Notes |
|---|---|---|
| 7A — Audit | < 1 min | read-only |
| 7B–7E — Convert (per year) | ~1–3 min | groupby on 285k+ rows; ~6.9M-row write |

**Python deps:** `pandas`, `numpy` — existing environment. No new packages.

---

## RISK REGISTER

| Risk | Impact | Mitigation |
|---|---|---|
| **Metabolic channel now calibrated** — `act30` is joint-raked (`05_postlink_rake.py --joint`, 2026-07-09), alongside `hom30`; `Metabolic_Rate` rides on raked/calibrated activity | Internal-gain inputs to EnergyPlus inherit the calibrated activity distribution | Verified: per-stratum act30 gaps 0.59–1.17 pp vs ~12.3 pp pre-rake; no further mitigation needed |
| Metabolic W/person reference basis (70 W/MET ≈ 60 kg) | Conservative vs ASHRAE 105 / 70 kg 83 W/MET; scales all internal gains | **Verified** vs 2024 Adult Compendium (`07_metabolicMap_verification.md`); document the 70 W/MET basis in Methods; optional ×1.19/×1.5 sensitivity run |
| Sat/Sun pooled → Weekend | Loses calibrated 2.3 pp Sat/Sun distinction | Accept (BEM consumer is 2-day-type); note in paper; a 3-type variant is a small `DAYTYPE` map change if needed |
| Hourly (24) vs planned 30-min (48) | Sub-hourly transitions smoothed | Accept for EnergyPlus timestep; 48-slot data is preserved upstream in the diaries if finer resolution is needed |
| PR → region label, not ASHRAE climate zone | Climate differentiation not in the schedule file | Handle at the `.epw` weather-file selection stage downstream |
| `MATCH_TIER = 3_Constraints` on 52,103 HH (36%) | Looser Step-5 linkage inherited into BEM | Quantify sensitivity; tier is carried in the output for filtering/weighting |

---

## CONNECTION TO DOWNSTREAM STEPS

- **EnergyPlus build (`eSim_bem_utils/main.py`):** consumes `BEM_Schedules_<year>.csv`, builds
  `Schedule:Compact` objects (Weekday/Weekend), injects occupancy + internal gains into the
  IDFs, and runs the simulations. **Not yet executed.**
- **Climate differentiation:** province → ASHRAE climate zone → `.epw` weather file is applied
  at the EnergyPlus stage, not in the schedule CSV.
- **UBEM / CityGML:** optional future work; the per-household schedule + dwelling attributes are
  compatible with building-stock aggregation but no UBEM export is built.

---

## Progress Log

| Date | Task | Result | Notes |
|---|---|---|---|
| 2026-05-31 | OP4 — `07_aug_to_bem.py` build + run (2022 + 2030) | ✅ DONE | Calibrated `BEM_Schedules_{2022,2030}.csv` written, 144,507 HH each; donor-draw day-completion (fixed copy-day −2.76 pp weekend dilution); classic files backed up to `*_CLASSIC_BAK_2026-05-31.csv`. |
| 2026-06-01 | Step 7 documentation created (`07_bemIntegrationGSS.md` + `_val.md`) | ✅ DONE | Mirrors 05/06 doc pair. Documents what `07_aug_to_bem.py` actually does, plan-vs-built deviations, and the verified output stats (see `_val.md` Progress Log). |
| 2026-06-01 | Output re-verification (read-only) | ✅ PASS | Both files: 6,936,336 rows, 144,507 HH, all HH have both day-types, Occ ∈ [0,1], Met ∈ [70,245]. **2022:** WD occ 0.703 / WE occ 0.749 (met 108.5). **2030:** WD occ 0.785 / WE occ 0.803 (met 107.4 / 100.0). 2030 occupancy reproduces the calibrated structural-break marginals to ≤ 0.04 pp. |
| 2026-06-01 | `07_bemIntegrationGSS_val.py` built + run | ✅ 2022 29/0/0 · 2030 28/0/0 | 6-section validator → `outputs_step7/step7_validation_report_{2022,2030}.html`. Confirms schema, day-type coverage (0 partial HH), occupancy calibration (per-HH vs per-person, ≤1 pp; 2030 Δ0.04), metabolic plausibility, attribute integrity (DTYPE/PR 0 within-HH drift; MATCH_TIER varies per-person, BEM-harmless), and regression vs classic. See `07_bemIntegrationGSS_val.md` Progress Log for the three post-run check refinements. |
| 2026-06-01 | Metabolic-map source verification | ✅ SOURCED | Map grounded in the **2024 Adult Compendium of Physical Activities** (user-provided PDF). Recovered the exact basis `W = MET × 70` from two Compendium hits (Sleeping 1.0→70 W, Eating 1.5→105 W); 9/14 categories land on Compendium central values, 2 exact, 3 minor low-impact flags (Socializing low, Active Leisure conservative, Misc high). 70 W/MET ⇒ ~60 kg reference (conservative vs ASHRAE 105 / 70 kg 83). Full crosswalk → `07_metabolicMap_verification.md`. No map value changed (publishable-results guardrail). |
| 2026-07-10 | Doc alignment — `--joint` input + frame refresh + report-label fix | ✅ DONE | Input table now names `2030_synthetic_diaries_joint_raked.csv` (read via `--joint`, canonical joint act30+hom30 rake); frame corrected 144,507→144,465 HH / 285,419→285,367 persons / 6,936,336→6,934,320 rows (Jul-9 Step-5 refresh dropped 42 HH / 52 persons). Validator `07_bemIntegrationGSS_val.py` clock-label fix: removed the obsolete `_clock` (+4h) helper — since the 2026-06-08 +4h roll the BEM `Hour` is real clock time, so §3/§4/§4b chart x-axes and the §4b lighting-peak now read true hours (lighting peak 20h, was mislabelled 00h). Data/gates unchanged; `_v2` reports regenerated. Predecessor → `archive/07_bemIntegrationGSS_val.20260710_pre_clockfix.py`. |
