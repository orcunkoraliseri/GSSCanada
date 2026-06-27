# Step 7 — BEM Integration: J2 (single-channel) vs J3 Leg-2 (two-channel)

**Scope:** Factual side-by-side comparison of the BEM schedule-wiring step between Journal 2 (residential-only REPLACE) and Journal 3 Leg-2 (residential REPLACE + office MODULATE). Sources: `2J_docs_occ_nTemp/07_bemIntegrationGSS.md`, `07_bemIntegrationGSS_val.md`, `07_metabolicMap_verification.md`; `3J_docs_occ_nTemp/Leg2_2-split/Step7_docs/3rdJ_07_bemIntegration_2split.md`, `3rdJ_07_bemIntegration_2split_val.md`. HTML scorecard counts confirmed from `outputs_step7/step7_validation_report_{2022,2030}.html` in each journal.

---

## 1. Purpose and Method Delta

| Dimension | J2 (Leg-1) | J3 Leg-2 (two-channel) |
|---|---|---|
| Building use covered | Residential only | Residential **+** office |
| Residential approach | **REPLACE** — per-household hourly schedule directly replaces EnergyPlus People/metabolic baseline; `Number_of_People = HHSIZE`. | Same REPLACE logic (port of J2 converter). |
| Office approach | (none) | **MODULATE** — population-level workforce-presence fraction (`AT_WORK_fraction`) per archetype × day-type × hour replaces the *temporal shape* of NECB/ASHRAE office People/Lights/Equipment schedules while keeping code-compliant peak densities. Does not carry HHSIZE. |
| Script | `2J_docs_occ_nTemp/07_aug_to_bem.py` | `3J_docs_occ_nTemp/Leg2_2-split/Step7_docs/3rdJ_07_aug_to_bem_2split.py` |
| +4 h diary→clock roll | Applied as 2J fix 2026-06-08 (corrects GSS slot-1 = 04:00 to real midnight); documented in J3 main doc. | Explicitly documented and applied (`np.roll(...,4)`). Both years, both channels. |
| 2030 WFH bands | Single scenario (structural-break calibrated). | Three bands: conservative (17.5% WFH) / hybrid (30%) / fullyhybrid (40%) — produces 3 residential files + one office file with a `BAND` column. |
| Calibration-C (2030) | Not applicable. | Post-hoc restore of 2030 act30 activity mix (donor-resample from observed-2022 per slot × state) + weekend home marginal (OUT→HOME flips to match 2022 Sat/Sun target) + Stage-0 weekend wrk30 cap (18.6%→6.6% matching observed). `wrk30` is never modified, so the office channel is unaffected. Deliverable: `2030_synthetic_diaries_2split_calibrated_mindwell_C.csv`. |
| Step-9 activity loads in Step-7 output | **Included** — `Equipment_Fraction, Lighting_Fraction, Equip_Design_W, Light_Design_W` added as backward-compatible extension in J2 v2. | **Deferred** — these columns are not in the J3 Step-7 output; they are the 2-split Step-9 deliverable (decision OD-7D). |

The core Step-7 build delta for J3 is the **office MODULATE channel** (`3rdJ_07_bemIntegration_2split.md`, Deviations table: "Office channel (AT_WORK) — new in Leg 2"). The residential side is the same wiring in both journals.

---

## 2. Inputs

### J2 inputs (`07_bemIntegrationGSS.md`, Prerequisites table)

| File | Population | Key columns used |
|---|---|---|
| `0_Occupancy/Outputs_21CEN22GSS/aug_pipeline/21CEN22GSS_aug_Full_Aggregated_excl.csv` | 285,419 persons / 144,507 HH (2022 stock, post-exclusion, calibrated 8B-5b) | `HH_ID, DDAY_STRATA, act30_001–048, hom30_001–048, HHSIZE, DTYPE, BEDRM, CONDO, ROOM, REPAIR, PR, MATCH_TIER` |
| `0_Occupancy/Outputs_21CEN22GSS/forecast_2030/2030_synthetic_diaries.csv` | 37,008 rows (12,231 WD / 12,406 Sat / 12,371 Sun; structural-break canonical) | `DDAY_STRATA, act30_001–048, hom30_001–048` |

2030 dwelling attributes are drawn from the 2022 stock via `assemble_2030()` (stratum-matched, `seed=42`); the 2030 forecast rides on the same 144,507-HH frame.

### J3 inputs (`3rdJ_07_bemIntegration_2split.md`, Prerequisites table)

| File | Population | Key columns used |
|---|---|---|
| `Step5_docs/outputs_step5/3rdJ_25CEN_aug_Full_Aggregated_excl.csv` | ~29,599 linked persons / 23,211 HH (2022, post AT_HOME<0.30 exclusion, employed-enriched 2-split stock) | All J2 columns **plus** `wrk30_001–048, office_archetype_ID, HH_hom30_001–048, N_HH_MEMBERS, NOCS, NAICS_donor, HRSWRK, TELEWORK, WORK_SCHEDULE, CMA, LFTAG` |
| `Step6_docs/outputs_step6/2030_synthetic_diaries_2split_calibrated_mindwell_C.csv` (**calibration-C deliverable**) | 111,024 rows = 3 bands × ~37,008 (BAND column: conservative / hybrid / fullyhybrid) | `act30_001–048, hom30_001–048, wrk30_001–048, BAND, DDAY_STRATA, IS_SYNTHETIC, LFTAG, NOCS, NAICS, PR, CMA` |
| `0_Occupancy/processed/office_archetype_lookup.csv` | NOCS → archetype mapping | `NOCS, archetype_label, is_office` |

2030 dwelling attributes again drawn from the 2022 2-split stock via stratum-matched `assemble_2030()`. Office archetype for 2030 re-derived from 2030 `NOCS` via the lookup (does not need the stock frame).

**Office archetype mapping** (`3rdJ_07_bemIntegration_2split.md`, office_archetype_lookup table):

| NOCS groups | Archetype | is_office |
|---|---|---|
| 0, 1, 2 | Office_Knowledge | Yes |
| 3, 4, 5 | Office_Public | Yes |
| 6 | Office_Sales | Yes |
| 7, 8, 9 | NonOffice | No |
| 10 / 99 / NaN | Unknown_NOCS | No |

Office channel uses `is_office = True` rows only (Knowledge / Public / Sales), restricted to employed persons (`LFTAG` = 1 Paid employee or 2 Self-employed; OD-7C locked).

---

## 3. Outputs

### 3a. J2 output files (`07_bemIntegrationGSS.md`, Output Files table)

| File | Location | Rows | Content |
|---|---|---|---|
| `BEM_Schedules_2022.csv` | `BEM_Setup/` | 6,936,336 | 144,507 HH × 2 day-types × 24 h; calibrated 2022 stock |
| `BEM_Schedules_2030.csv` | `BEM_Setup/` | 6,936,336 | 144,507 HH × 2 day-types × 24 h; calibrated 2030 forecast |

**J2 residential schema** (17 columns — confirmed from `BEM_Setup/BEM_Schedules_2022.csv` header; includes Step-9 activity-load extension):

`SIM_HH_ID, Day_Type, Hour, HHSIZE, DTYPE, BEDRM, CONDO, ROOM, REPAIR, PR, MATCH_TIER, Occupancy_Schedule, Metabolic_Rate, Equipment_Fraction, Lighting_Fraction, Equip_Design_W, Light_Design_W`

> Note: the J2 main doc describes a 13-column format; the 4 Step-9 activity-load columns were added as a backward-compatible v2 extension after the Step-9 work. The J3 Step-7 output does not include them (deferred to 2-split Step 9).

### 3b. J3 output files (`3rdJ_07_bemIntegration_2split.md`, Output Files table)

#### Residential REPLACE (5 files)

| File | Location | Rows | Content |
|---|---|---|---|
| `BEM_Schedules_2split_2022.csv` | `Step7_docs/outputs_step7/` | 1,114,128 | 23,211 HH × 2 day-types × 24 h; 2022 stock |
| `BEM_Schedules_2split_2030_conservative.csv` | same | 1,114,128 | 2030, conservative WFH band (17.5%) |
| `BEM_Schedules_2split_2030_hybrid.csv` | same | 1,114,128 | 2030, hybrid WFH band (30%) |
| `BEM_Schedules_2split_2030_fullyhybrid.csv` | same | 1,114,128 | 2030, fullyhybrid WFH band (40%) |

**J3 residential schema** (13 columns — confirmed from `BEM_Schedules_2split_2022.csv` and `BEM_Schedules_2split_2030_hybrid.csv` headers):

`SIM_HH_ID, Day_Type, Hour, HHSIZE, DTYPE, BEDRM, CONDO, ROOM, REPAIR, PR, MATCH_TIER, Occupancy_Schedule, Metabolic_Rate`

#### Office MODULATE (2 files, new in J3)

| File | Location | Rows | Content |
|---|---|---|---|
| `office_presence_multiplier_2022.csv` | `Step7_docs/outputs_step7/` | 144 | 3 archetypes × 2 day-types × 24 h; BAND = "observed" |
| `office_presence_multiplier_2030.csv` | same | 432 | 3 archetypes × 3 WFH bands × 2 day-types × 24 h |

**Office schema** (7 columns — confirmed from both office CSV headers):

`office_archetype, BAND, Day_Type, Hour, AT_WORK_fraction, multiplier, n_persons`

- `AT_WORK_fraction` [0,1], 4 dp: raw absolute population fraction of employed office workers physically present (primary column used downstream, per OD-7B locked).
- `multiplier`: peak-normalized variant (also emitted for flexibility, not the default consumer input).
- `n_persons`: sample size per cell (for small-cell diagnostics).

#### Key occupancy and metabolic values

| Metric | J2 2022 | J2 2030 | J3 2022 | J3 2030 (post-calib-C) |
|---|---|---|---|---|
| Residential WD mean occ | 0.703 | 0.785 | 0.646 | cons 0.683 / hyb 0.701 / fully 0.711 |
| Residential WE mean occ | 0.749 | 0.803 | 0.732 | cons 0.659 / hyb 0.681 / fully 0.701 |
| WD mean metabolic (W/person) | 108.5 | 107.4 | 109.8 | ~109.9 all bands |
| WE mean metabolic (W/person) | 108.5 | 100.0 | 109.7 | ~110 (sleep 34.8%) |
| Office WD peak AT_WORK_fraction | — | — | Knowledge 0.602 / Public 0.608 / Sales 0.592 | cons Knowledge 0.588, Public 0.591, Sales 0.606; fully ~0.46–0.51 |

Sources: J2 `07_bemIntegrationGSS_val.md` Section 7 table; J3 main doc Progress Log entries 2026-06-26.

---

## 4. Metabolic Mapping

### J2 (`07_metabolicMap_verification.md`, `07_bemIntegrationGSS.md` Background)

The 14-category activity → W/person map is:

```python
MET = {0:0, 1:125, 2:175, 3:190, 4:195, 5:70, 6:105, 7:170,
       8:110, 9:90, 10:85, 11:245, 12:105, 13:140, 14:135}
```

Source verification (2026-06-01, `07_metabolicMap_verification.md`): map is **2024 Adult Compendium of Physical Activities MET values × 70 W/MET**. Recovery: Sleeping (1.0 MET → 70 W) and Eating (1.5 MET → 105 W) are exact anchor hits. Implies a ~60 kg reference adult — conservative vs ASHRAE 55 (105 W/MET, 70 kg 83 W/MET). 9/14 categories land on Compendium central values; 2 exact; 3 minor low-impact flags (Socializing slightly low, Active Leisure conservative for vigorous tail, Misc/Idle slightly high). No map values were changed; the 70 W/MET basis must be cited in Methods.

- `act30` channel is **un-raked** in J2 (only `hom30` was raked); `Metabolic_Rate` rides the raw J3 model activity output. This is documented as a limitation (`07_bemIntegrationGSS_val.md`, Section 4.4 INFO, Risk Register).

### J3 (`3rdJ_07_bemIntegration_2split.md` Background — Residential channel)

The identical map is **reused verbatim** (cited from `21CEN22GSS_occToBEM.py:57`, verified in `07_metabolicMap_verification.md`):

```python
MET = {0:0, 1:125, 2:175, 3:190, 4:195, 5:70, 6:105, 7:170,
       8:110, 9:90, 10:85, 11:245, 12:105, 13:140, 14:135}
```

Same 70 W/MET basis, same Compendium citation. The map was **not re-derived or re-verified** for J3; it is carried over.

**Calibration-C (J3 only):** Before Step 7 runs on the 2030 deliverable, Stage 2 of calibration-C resamples `act30` from observed 2022 stock pools conditional on (slot × state), restoring sleep share from 22.8% → 35.0% and WD metabolic from ~127 → ~110 W. This closes the main un-raked-activity risk for J3 2030 (the 2022 stock `act30` is still un-raked, as in J2).

---

## 5. Validation

### Gate structure comparison

| Aspect | J2 | J3 |
|---|---|---|
| Validator script | `07_bemIntegrationGSS_val.py` | `3rdJ_07_bemIntegration_2split_val.py` |
| Sections | 6 (Schema, Day-Type, Occupancy, Metabolic, Attributes, Regression) | 7 (A Schema — both products, B Day-Type, C Residential occ, D Metabolic, E Office shape, F Channel consistency, G Attributes/regression) |
| Total gates checked | ~17 (2022) / ~16 (2030) | 32 (2022) / 43 (2030) |
| Office-specific gates | (none) | archetype domain, AT_WORK_fraction range, grid completeness, weekday shape (peak > floor, lunch-dip ≥ 1.02×), WD > WE presence, band monotonicity (conservative > hybrid > fullyhybrid on WD 9–17 h) |
| Channel consistency | (none) | WFH conservation cross-channel (home ↑ & office ↓, cons→fully): +6.8 pp home, −12.3 pp office (2030) |

### Scorecard side-by-side (confirmed from HTML reports)

| Journal | Year | PASS | WARN | FAIL |
|---|---|---|---|---|
| **J2** | 2022 | **29** | 0 | 0 |
| **J2** | 2030 | **28** | 0 | 0 |
| **J3** | 2022 | **32** | 0 | 0 |
| **J3** | 2030 | **43** | 0 | 0 |

> J3 had intermediate states during 2026-06-26 development: first run 2022 = 30/0/2, 2030 = 40/1/11; all FAILs cleared by fix bundle A/B/C (see below). Final confirmed scores are from the HTML reports and J3 `_val.md` Progress Log.

### Key gate values — J2 (from `07_bemIntegrationGSS_val.md` Section 7 table)

| Gate | 2022 | 2030 |
|---|---|---|
| Row count | 6,936,336 | 6,936,336 |
| HH count | 144,507 | 144,507 |
| Partial-coverage HH | 0 | 0 |
| WD calibration match (≤ 1 pp) | 70.27% (Δ0.50 pp) | 78.48% (Δ0.04 pp) |
| WE calibration match (≤ 1 pp) | 74.92% (Δ0.15 pp) | 80.33% (Δ0.02 pp) |
| Population AT_HOME vs 72.3% (≤ ±2 pp) | 71.20% (Δ1.10 pp) | — (no future anchor) |
| Peak hourly occupancy (≥ 0.85) | 0.950 | 0.958 |
| Metabolic range [0, 245] | 70.0–245.0 W | 70.0–245.0 W |
| DTYPE/PR within-HH drift | 0 | 0 |

### Key gate values — J3 (from `3rdJ_07_bemIntegration_2split_val.md` gate summary table)

| Gate | 2022 | 2030 |
|---|---|---|
| Residential row count | 1,114,128 | 1,114,128 (per band) |
| HH count | 23,211 | 23,211 |
| Partial-coverage HH | 0 | 0 |
| Weekend marginal dilution (≤ 0.5 pp) | Δ+0.118 pp | Δ+0.103 pp (cons band vs cons diary) |
| WD residential occ fidelity (≤ 1 pp) | Δ0.174 pp | ≤ 0.335 pp all bands |
| WE residential occ fidelity (≤ 1 pp) | Δ0.118 pp | ≤ 0.131 pp all bands |
| 2030 band ordering daytime home | n/a | cons 0.407 < hyb 0.449 < fully 0.475 PASS |
| Sleep trough (≤ 85 W) | 73.2 W | 74.9 W |
| WD metabolic (post-calib-C, INFO) | 109.8 W (sleep 33.9%) | 109.9 W (sleep 34.8%) |
| Office fraction range [0,1] | [0.008, 0.608] | [0.030, 0.701] |
| Office WD > WE presence | PASS | PASS (after Fix C weekend work cap) |
| Band monotonicity office WD 9–17 h | n/a | K: 0.588>0.502>0.462; P: 0.591>0.514>0.445; S: 0.606>0.537>0.508 — all PASS |
| WFH cross-channel direction | n/a (2022 INFO) | +6.8 pp home, −12.3 pp office cons→fully — PASS |
| DTYPE/PR within-HH drift | 0 (after Fix B) | 0 (after Fix B) |

### Fixes required in J3 before clean scorecard (not needed in J2)

| Fix | Issue found | Resolution |
|---|---|---|
| Fix A — PR labels | `PR_LBL` in producer mapped census codes (10, 24, 35…) instead of region codes (1–6) used in the 2-split AUG file | Remapped to `_PROVINCE_TO_REGION` scheme from `3rdJ_05_censusLinkage_2split.py`; `PR_VALID` updated (Alberta merged into Prairies region 4) |
| Fix B — donor-draw attrs | Within-HH DTYPE/PR drift in 2,086 HH (donor metadata bleeding + native within-HH variation in 1,741/1,297 HH) | `complete_day_types()` adds explicit STAT overwrite; `convert()` adds `groupby("SIM_HH_ID").first()` STAT canonicalization |
| Fix C — weekend work cap (calibration-C Stage 0) | 2030 office WE 24-h mean > WD for all 9 archetype/band combos (WE night wrk30 inflated ~22% — Step-6 calibration artifact) | Stage 0 added to `3rdJ_06_calibrate_C_activity_weekend_2split.py`: trims per-slot WE wrk30 to observed-2022 WE mean (trim-only 1→0 flips, seed=42); Sat 18.7%→7.1%, Sun 18.5%→6.1% |

---

## 6. What Is Genuinely New in J3 vs Carried Over from J2

| Element | Status in J3 | Notes |
|---|---|---|
| **Office MODULATE channel** | NEW | The only substantive Step-7 build delta. New archetype lookup, `wrk30` aggregation, AT_WORK_fraction computation, new hard gates (archetype domain, shape, band monotonicity), new validator sections E/F, 2 new output files. |
| **Three 2030 WFH bands** | NEW | Conservative / hybrid / fullyhybrid residential band files + BAND column in office multiplier. |
| **Calibration-C** | NEW | 2030-only; restores act30 activity mix and weekend home marginal post-Step-6 forecast drift. `wrk30` preserved → office channel unaffected. |
| **Channel-consistency validation (Section F)** | NEW | WFH cross-channel direction check (home ↑ & office ↓). |
| Residential REPLACE logic | CARRIED OVER | `hom30` mean → occupancy, `MET[act30]` → metabolic, 48→24 hourly, donor-draw day-type completion, 3→2 day-type pool (Sat+Sun), DTYPE/PR relabelling — all from J2. |
| +4 h diary→clock roll | CARRIED OVER | Applied as 2J bug fix 2026-06-08; kept in J3. |
| Metabolic map | CARRIED OVER | Identical dict, same 70 W/MET Compendium basis, not re-derived. |
| Donor-draw day-type completion | CARRIED OVER | Same `complete_day_types()` design (genuine opposite-day diary from pool, `seed=42`); J3 adds recipient-overwrite to prevent donor metadata bleeding (Fix B). |
| 2-day-type reduction (Sat+Sun pooled) | CARRIED OVER | Same ~2.3 pp Sat/Sun distinction lost; consumer is 2-day-type in both journals. |
| `assemble_2030()` stratum-matched draw | CARRIED OVER | Same `seed=42` mechanism; J3 extends it to also overwrite `wrk30`. |
| PR → region label | CARRIED OVER | Same 7 region labels (J3 needed Fix A to correct the key mismatch). |

---

## 7. Caveats and Risks for the Paper

| Item | Applies to | Description | Mitigation / Status |
|---|---|---|---|
| **Office MODULATE design choice (OD-7B)** | J3 | Raw absolute `AT_WORK_fraction` (peak < 1) is the primary schedule column — it keeps the NECB density and replaces only the temporal shape. A peak-normalized `multiplier` is also emitted. The distinction matters: normalizing erases the WFH level signal (peak falling 0.5→0.4 cons→fully). Must be stated clearly in Methods. | Locked decision in `3rdJ_07_bemIntegration_2split.md`, OD-7B. |
| **Calibration-C weekend work cap modifies weekend wrk30** | J3 | Stage 0 trims weekend `wrk30` to match observed-2022 per-slot means. While `wrk30` was not the Step-6 calibration focus, this is a post-hoc edit to the 2030 diaries. The assumption (weekend work behaviour unchanged 2022→2030) is defensible but must be documented. | Documented as assumption in calibration-C section of main doc and Progress Log. |
| **Metabolic channel un-raked (act30)** | Both | `act30` was never raked to an external activity target in Step 4; `Metabolic_Rate` rides the J3 model's raw activity output (J2) or the calibration-C conditional resample (J3 2030). J2 2022 metabolic is un-raked. | J3 2030 largely fixed by calib-C (sleep 22.8%→35%, WD met 127→110 W). J2 2022 documented as INFO gate; J3 2022 `act30` also un-raked. Document in paper; optional metabolic sensitivity run (×1.19 or ×1.5 reference body factor). |
| **70 W/MET reference basis** | Both | ~60 kg reference adult — conservative vs ASHRAE 55 (105 W/MET) and 70 kg physiological basis (83 W/MET); all internal gains scale linearly. | Verified vs 2024 Adult Compendium (`07_metabolicMap_verification.md`); must be cited + noted in Methods. One-line sensitivity run available. |
| **Sat/Sun pooled → Weekend** | Both | ~2.3 pp Sat/Sun occupancy distinction lost (2022: observed Sat 79.15% vs Sun 81.48% home for J2). | Consumer is 2-day-type; accepted. Note in paper. 3-type variant possible with minor DAYTYPE map change. |
| **`wrk30` not raked to an external office benchmark** | J3 | Office presence rides Step-4/6 calibration; no commercial office survey benchmark applied. | Document; Step 9 can calibrate magnitude vs NRCan SCIEU / NECB. |
| **Small office cells (Office_Sales, weekend)** | J3 | n_persons = 388 for Office_Sales in 2022; weekend sub-bands may be noisy. | `n_persons` column carried in output for filtering; Sat+Sun pooled mitigates. Flag in paper. |
| **MATCH_TIER = 3_Constraints (~52k HH in J2, share in J3)** | Both | Looser Step-5 census linkage inherited into BEM schedules. | Tier carried in output for sensitivity filtering. |
| **Hourly (24 h) vs 30-min (48 slot)** | Both | Sub-hourly transitions smoothed by averaging each slot pair. | 48-slot data preserved upstream; IDF Interpolate-to-Timestep is a downstream choice. Accept for EnergyPlus timestep. |
| **No ASHRAE climate zone in schedule file** | Both | PR → region label only; climate differentiation handled at EPW stage. | By design; handled downstream. |
| **EnergyPlus simulations not yet run** | Both (Step 8) | Step 7 emits data products only; IDFs and simulations are Step 8. | Not a Step-7 issue; note scope boundary. |
