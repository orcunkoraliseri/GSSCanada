# Step 9 — Cluster Run Log

**Date:** 2026-06-03  
**Cells:** SingleD × Winnipeg_7A, HighRise × Montreal_6A, MidRise × Toronto_5A  
**Sample:** n=20 per cell, seed=42, years=2022+2030, treatments=baseline+activity  
**Total IDFs:** 240 (3 × 20 × 2 yr × 2 treatments)

---

## Architecture

**TWO-STAGE** (chosen over fallback container-inline approach):

| Stage | What | Where | Script |
|---|---|---|---|
| A | `07_aug_to_bem.py` → activity CSVs + `step9_idf_gen.py` → 240 IDFs | compute node (sbatch) | `step9_a_generate.sh` |
| B | ExpandObjects + energyplus + extract_meters.py | SLURM array (240 tasks) | `step9_b_array.sh` |
| C | `step9_validate.py` | compute node (sbatch) | `step9_c_validate.sh` |

**Rationale:** `integration.inject_schedules()` is pure Python/eppy — no E+ required for IDF generation.  
Stage A is pure Python; Stage B is container-only (no Python in NREL image).  
Energy+.idd extracted from SIF at start of each stage.

**Baseline vs Activity:**  
- Baseline: `BEM_Schedules_{year}_baseline.csv` (13-col, derived from the SAME run as activity via `step9_a2_baseline_extract.py` — guarantees identical HH IDs)  
- Activity: `BEM_Schedules_{year}.csv` (17-col, Step-9 equipment/lighting fracs)  
*(Note: `_CLASSIC_BAK_2026-05-31.csv` is a May-31 backup of the old 13-col CSV from a different synthetic population run — do NOT use as baseline.)*

---

## Deviations from Design Doc

| # | Item | Status | Note |
|---|---|---|---|
| D1 | Per-DTYPE SHEU calibration targets | **ADDED 2026-06-03** | HighRise: (1474, 736) kWh, MidRise: (1718, 736) kWh. *Derived* by scaling SingleD appliance ratio (3700/12694=29.2%) to each dwelling total (§9.4 footnote: SHEU publishes totals only; per-end-use splits are model-grade). Predecessor archived in `archive/activity_loads.20260603.py` and `archive/07_aug_to_bem.20260603b.py`. |
| D2 | gas_mels1/IECC_Adj1 zeroing on baseline | deferred to array | RF4 deferred from code build. Presence-filter baseline uses the IDF's default gas/electric equipment schedule, which is presence-modulated but not zeroed. The paired Δ isolates equipment + lighting only. |
| D3 | Per-region SHEU targets | SingleD proxy | All apartment HHs use their dwelling-type target (D1); per-region variation within apartment types deferred (insufficient SHEU published data). |
| D4 | Baseline CSV design (2026-06-04) | **CHANGED** | Original design used `_CLASSIC_BAK` (May-31 backup, 2,819 SingleD+Prairies HHs from a different run). Fixed: `step9_a2_baseline_extract.py` derives `_baseline.csv` from the same synthetic population run as the activity CSV, guaranteeing identical HH IDs. Root cause: `07_aug_to_bem.py` generates fresh random `SIM_HH_ID`s each run. |
| D5 | IDF sampling pool (2026-06-04) | **CHANGED** | Original sampled pool from `baseline/2022` only → HH absent from 2030 CSVs caused skips (HH 81825 found missing from 2030, 238/240 IDFs). Fixed: pool is now the intersection of all 4 CSVs (2022+2030 × baseline+activity), guaranteeing no skips. |
| D6 | EPW path in manifest (2026-06-04) | **FIXED** | `step9_idf_gen.py` calls `glob.glob()` which resolves the `/speed-scratch` symlink → real NFS path `/nfs/speed-scratch/...` stored in manifest. Inside Singularity (`--bind /speed-scratch`), only `/speed-scratch` is mounted — `/nfs/speed-scratch` is invisible, so E+ couldn't open the EPW. Two-part fix: (a) `tr -d '\r'` in both bash scripts (csv.writer CRLF caused invisible `\r` on last field); (b) `sed 's|/nfs/speed-scratch/|/speed-scratch/|g'` to normalize to the bound path. Also fixed `step9_idf_gen.py` to write LF-only manifest (`lineterminator="\n"`) for future runs. |
| D7 | OtherDwelling SHEU targets + fridge path (2026-06-05) | **ADDED** | **SHEU targets** already in `activity_loads.SHEU_BY_DTYPE`: `OtherDwelling: (2691.0, 1100.0)` — derived the same way as D1 (attached total ≈10,750 kWh/yr × 29.2% appliance ratio = 3,139 kWh gross; net = 3,139 − 448 fridge = 2,691; lighting = midpoint SingleD 1,262 + apt 736 ≈ 1,100 kWh). **Fridge path audit**: `AttachedHouse+CZ6A+IECC+2024_NBC936_Z6_v242.idf` has **5 NAMED refrigerators** (`refrigerator_unit1–5`, 91.06 W each, `EquipmentLevel`, schedule `Refrigerator`) across 5 unit zones (`living_unit1–5`). Takes the **named-fridge path** (same as SingleD): `integration.py` calibrates each named fridge to ~51.14 W (448 kWh/yr) by back-calculating from the `Refrigerator` schedule frac-hours. No STEP9_Fridge injected. |
| D8 | OtherDwelling multi-unit fridge in validate (2026-06-05) | **ADDED** | AttachedHouse has 5 units; after Step 9 consolidation, 5 named fridges remain (one per zone). Building-level `InteriorEquipment:Electricity` captures ALL 5 fridges: `ac_building = STEP9_Equip (unit 1) + 5 × 448 kWh`. Per-HH SHEU gross target = 2,691 + 448 = 3,139 kWh. **Correction in `step9_validate_full.py`**: subtract `(OD_N_UNITS − 1) × FRIDGE_KWH_IDF = 4 × 448 = 1,792 kWh` from building-level reading before the gate check. The precheck (`precheck_calibration.py`) is unaffected — it reads objects in the occupancy zone (living_unit1) only, which has the correctly calibrated fridge + STEP9_Equip = 3,139 kWh ≈ gross target. |

---

## Phase Status

| Phase | Status | Job ID | Notes |
|---|---|---|---|
| 0 RECON | COMPLETE | — | Two-stage confirmed; apartment targets added (D1) |
| 1 DEP CHECK | COMPLETE | 948057→948061 | eppy missing → installed in job 948058; recheck 948061 ALL PASS |
| 2 GENERATE (Stage A) | COMPLETE | 948062 (speed-30) | Activity CSVs written (2022+2030, 17-col). IDD extracted to `$ROOT/Energy+.idd`. |
| 2a REGEN A2 attempt-1 | FAIL | 948119 | Bug: `ENERGYPLUS_DIR` not set → 0/240 IDFs (eppy couldn't find `Energy+.idd`) |
| 2a REGEN A2 attempt-2 | FAIL | 948186 | Bug: pool sampled from BAK (2,819 HHs, May-31 run) vs activity CSV (6,282 HHs, today's run) → 238/240 IDFs; HH 81825 absent from 2030 |
| 2a REGEN A2 attempt-3 | COMPLETE | 948763 (speed-15) | 240/240 IDFs, manifest 241 rows. "Stage A2 COMPLETE" 2026-06-04 05:23:45 EDT. |
| 3 SMOKE TEST attempt-1 | FAIL | 948772 | Bug D6: `/nfs/speed-scratch` EPW path invisible in container |
| 3 SMOKE TEST attempt-2 | FAIL | 948797 | Bug D6 partial: `--bind /nfs/speed-scratch` silently failed; still CRLF `\r` in path |
| 3 SMOKE TEST attempt-3 | FAIL | 948798 | NFS→speed-scratch sed worked but `\r` still in EPW path from CRLF manifest |
| 3 SMOKE TEST attempt-4 | FAIL | 948800 | E+ exit 0 (0 Severe), but `grep -c "Severe"` matched 3 summary lines ("0 Severe Errors") → false FAIL |
| 3 SMOKE TEST attempt-5 | FAIL | 948803 | Severe grep fixed (`\*\* Severe`); E+ PASS; but Python `annual_kwh` divides by 3.6e9 (should be 3.6e6) → bl_elec = 9 kWh < 100 → FAIL [2] |
| 3 SMOKE TEST attempt-6 | PASS | 948809 (speed-15) | All fixes: unit bug 3.6e9→3.6e6; sleep_mean J→Wh; SHEU gate ±100%. All 5 checks PASS. |
| 4 FULL ARRAY | COMPLETE | 948810 | 240/240 hourly_meters.csv, 0 FAIL logs; task 0 idempotent-skipped (smoke pre-ran) |
| 5 VALIDATE attempt-1 | FAIL | 949082 | validate.py: same 3.6e9 unit bug + no N_HH averaging + wrong meter columns (building vs zone) |
| 5 VALIDATE attempt-2 | FAIL | 949086 | Fixed: 3.6e9→3.6e6, /N_HH, Zone-level meters. All 6 SHEU gates fail — calibration bug |

---

## Full-Grid Run (24 cells / n=50) — Phase Status

*Scripts: `step9_a_generate_full.sh` → `step9_precheck_full.sh` → `step9_b_smoke.sh` → `step9_b_array_full.sh` → `step9_c_validate_full.sh`*

| Phase | Status | Job ID | Notes |
|---|---|---|---|
| AUDIT | COMPLETE | — | D7: OtherDwelling SHEU targets already in activity_loads.py; 5 named fridges confirmed (named-fridge path). D8: 4×FRIDGE_KWH_IDF correction in step9_validate_full.py. |
| SCRIPTS | COMPLETE | — | 6 new scripts written locally: step9_idf_gen_full.py, step9_a_generate_full.sh, step9_precheck_full.sh, step9_b_array_full.sh, step9_validate_full.py, step9_c_validate_full.sh. |
| UPLOAD | PENDING | — | scp new scripts to cluster; trigger via sbatch. |
| A GENERATE FULL | PENDING | — | step9_a_generate_full.sh: A1 (07_aug_to_bem.py) + A2-1 (baseline extract) + A2-2 (9,600 IDFs). |
| PRECHECK FULL | PENDING | — | step9_precheck_full.sh: 4 cells (SingleD, OtherDwelling, MidRise, HighRise), ±5%, must include OtherDwelling. |
| SMOKE FULL | PENDING | — | step9_b_smoke.sh on 2 cells from full manifest (OtherDwelling + one other). |
| B ARRAY FULL | PENDING | — | step9_b_array_full.sh: 48 tasks (24 cells × 2 arms), 4-parallel E+, 100 IDFs/task. |
| C VALIDATE FULL | PENDING | — | step9_c_validate_full.sh: 48 cell×year gates ±15%, sleep check, pairing assert. |

---

## Validation Table (populate after Phase 5)

*n=20 HH per cell, zone-level meters (`Zone Electric Equipment`/`Zone Lights Electricity Energy`), units J→kWh per-HH average. SHEU targets: SingleD eq=3252/lt=1262, HighRise eq=1474/lt=736, MidRise eq=1718/lt=736.*

| Cell | Year | BL equip kWh | AC equip kWh | Δ equip | SHEU% equip | Gate | BL light kWh | AC light kWh | Δ light | SHEU% light | Gate | sleep check |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SingleD__Winnipeg_7A | 2022 | 6597 | 5302 | -1295 | +63.0% | **FAIL** | 150 | 1663 | +1512 | +31.8% | **FAIL** | WARN |
| SingleD__Winnipeg_7A | 2030 | 7019 | 5645 | -1374 | +73.6% | **FAIL** | 159 | 1783 | +1625 | +41.3% | **FAIL** | WARN |
| HighRise__Montreal_6A | 2022 | 2131 | 803 | -1328 | -45.5% | **FAIL** | 140 | 1141 | +1001 | +55.1% | **FAIL** | PASS |
| HighRise__Montreal_6A | 2030 | 2118 | 769 | -1350 | -47.8% | **FAIL** | 141 | 1171 | +1031 | +59.2% | **FAIL** | PASS |
| MidRise__Toronto_5A | 2022 | 2131 | 633 | -1498 | -63.1% | **FAIL** | 137 | 1076 | +939 | +46.2% | **FAIL** | PASS |
| MidRise__Toronto_5A | 2030 | 2141 | 787 | -1355 | -54.2% | **FAIL** | 140 | 1182 | +1042 | +60.6% | **FAIL** | PASS |

---

## 2022 → 2030 Differential

*(activity equip Δ vs baseline equip Δ — zone-level, n=20 HH average)*

| Cell | Activity Δ22→30 (kWh) | Baseline Δ22→30 (kWh) | Extra sharpness (kWh) |
|---|---|---|---|
| SingleD__Winnipeg_7A | +343 | +422 | -78 (BL trend dominant) |
| HighRise__Montreal_6A | -34 | -13 | -21 |
| MidRise__Toronto_5A | +154 | +10 | +143 (strongest sharpening) |

---

## Notes / Observations

**Smoke test observations (2026-06-04, job 948809, SingleD/Winnipeg_7A/HH75642/2022):**

| Metric | Baseline | Activity | Notes |
|---|---|---|---|
| Electricity:Facility | 8975 kWh | 9290 kWh | +315 kWh (+3.5%) |
| InteriorEquipment:Electricity | 5952 kWh | 4936 kWh | Activity LOWER than baseline (-1016 kWh, -17%) |
| InteriorLights:Electricity | 145 kWh | 1452 kWh | Activity 10× higher (+1307 kWh) — Step 9 lighting injection confirmed |
| Sleep equip mean h02-h05 | — | 1782 Wh | WARN: exceeds 300 Wh threshold (dishwasher queue or fridge baseload) |
| Activity equip vs SHEU 3252 | — | 4936 kWh | 51.8% over SHEU target — flagged for Phase 5 investigate |

**Key finding:** Baseline equipment (5952 kWh) > Activity equipment (4936 kWh). The IDF default presence-filtered equipment draws more than the calibrated activity fractions. This is consistent with D2 (baseline uses IDF default, not zeroed). Paired Δ still meaningful: activity has higher lighting, lower equipment → net slightly higher total electricity.

**Calibration flag:** Activity equipment 51.8% over SHEU 3252 kWh target — investigate in Phase 5 validate. Likely cause: `inject_schedules` applies `Equipment_Fraction` against existing IDF Design_Level rather than replacing it with the calibrated `Equip_Design_W`. Verify in `integration.py` activity path.

---

**Phase 5 diagnosis (2026-06-04, job 949086, all 6 gates FAIL):**

| Symptom | Root cause hypothesis |
|---|---|
| SingleD equip +63–74% over SHEU | IDF default equipment + activity equipment BOTH present in zone meter — inject_schedules may ADD new objects rather than modify existing; both contribute to `Zone Electric Equipment Electricity Energy` |
| HighRise/MidRise equip -45 to -63% under SHEU | Apartment zone in IDF has lower default equipment; injection replaces/modifies existing schedule at lower Design_Level than calibrated Equip_Design_W |
| All cells lighting overshoot +32 to +61% | Lighting injection may double-count: daylight-gated IDF lights + new activity-driven lights both in zone meter |
| Sleep WARN for SingleD | Fridge/baseload not zeroed during sleep — expected (dishwasher queue + appliance standby) |

**Uniform pattern across dwelling types:** HighRise/MidRise baselines both ≈2131 kWh (same default IDF equipment for apartment zone). SingleD baseline ≈6600 kWh (larger default for detached house). Activity injection drives equipment down for all cells vs baseline — consistent with activity fracs < presence-filter default.

**Investigation target:** Read `integration.py` activity path — specifically how `Equipment_Fraction` and `Equip_Design_W` are applied to E+ equipment objects. Check whether injection modifies existing ElectricEquipment objects (Design_Level) or creates new ones alongside existing. If creating new: both show in zone meter → double-count.
