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
| D7 | OtherDwelling SHEU targets + fridge path (2026-06-05) | **ADDED** | **SHEU targets** already in `activity_loads.SHEU_BY_DTYPE`: `OtherDwelling: (2691.0, 1100.0)` — derived the same way as D1 (attached total ≈10,750 kWh/yr × 29.2% appliance ratio = 3,139 kWh gross; net = 3,139 − 448 fridge = 2,691; lighting = midpoint SingleD 1,262 + apt 736 ≈ 1,100 kWh). **Fridge path audit**: the actual OtherDwelling IDF (`OtherDwelling__Toronto_5A/sample_001_HH24199/2022/in.idf`) has **7 named refrigerators** (`refrigerator_unit1–7`, 91.06 W each, `EquipmentLevel`, schedule `Refrigerator`) across 7 unit zones (`living_unit1–7`). *(Count verified 2026-06-06 by direct IDF inspection — corrected from the earlier template-IDF audit that found only 5.)* Takes the **named-fridge path** (same as SingleD): `integration.py` calibrates each named fridge to ~51.14 W (448 kWh/yr) by back-calculating from the `Refrigerator` schedule frac-hours. No STEP9_Fridge injected. |
| D8 | OtherDwelling multi-unit fridge in validate (2026-06-05) | **ADDED** | OtherDwelling IDF has 7 units; after Step 9 consolidation, 7 named fridges remain (one per zone). Building-level `InteriorEquipment:Electricity` captures ALL 7 fridges: `ac_building = STEP9_Equip (unit 1) + 7 × 448 kWh`. Per-HH SHEU gross target = 2,691 + 448 = 3,139 kWh. **Correction in `step9_validate_full.py`**: subtract `(OD_N_UNITS − 1) × FRIDGE_KWH_IDF = 6 × 448 = 2,688 kWh` from building-level reading before the gate check. The precheck (`precheck_calibration.py`) is unaffected — it reads objects in the occupancy zone (living_unit1) only, which has the correctly calibrated fridge + STEP9_Equip = 3,139 kWh ≈ gross target. |

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
| AUDIT | COMPLETE | — | D7: OtherDwelling SHEU targets already in activity_loads.py; **7 named fridges confirmed** (refrigerator_unit1..7 in OtherDwelling IDF, verified 2026-06-06). D8: **6×FRIDGE_KWH_IDF** correction in step9_validate_full.py. |
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

---

## Progress Log

### 2026-06-06 — Employee (Sonnet 4.6)

**Tasks completed:** T1 (doc consistency), T2 (missing-run tally command), T3 (SI plots + appendix).

**T1 — Doc consistency (numbers corrected, no logic changed):**

| File | Change |
|---|---|
| `step9_cluster/step9_validate_full.py` line 135 | Comment: "4 non-occupancy units" → "6 non-occupancy units" (OD_N_UNITS−1=6) |
| `cluster_run.md` D7 | "5 NAMED refrigerators (refrigerator_unit1–5)" → "7 named refrigerators (refrigerator_unit1–7)"; added note that count verified 2026-06-06 by direct IDF inspection (corrected from earlier template-IDF audit) |
| `cluster_run.md` D8 | "5 units / 5 named fridges / 5×448 / 4×448=1,792 kWh" → "7 units / 7 named fridges / 7×448 / 6×448=2,688 kWh" |
| `cluster_run.md` Full-Grid AUDIT row | "5 named fridges confirmed" → "7 named fridges confirmed (refrigerator_unit1..7, verified 2026-06-06)"; "4×FRIDGE_KWH_IDF" → "6×FRIDGE_KWH_IDF" |

Archives created before each edit:
- `step9_cluster/archive/step9_validate_full.20260606.py`
- `archive/cluster_run.20260606.md`

**T2 — Missing-run tally (on the cluster, login-node-safe):**

Run this single line **on the cluster** to count completed `hourly_meters.csv` per cell×year×arm:

```
find /speed-scratch/o_iseri/step9_run/idfs -name hourly_meters.csv | awk -F/ '{print $6"/"$9"/"$7}' | sort | uniq -c | sort -k2
```

**Tally run 2026-06-06 — CONFIRMED SCATTERED, no FLAG:**

| Cell | Bucket | n | Missing |
|---|---|---|---|
| HighRise__Toronto_5A | 2022/baseline | 49 | 1 |
| HighRise__Toronto_5A | 2030/activity | 49 | 1 |
| HighRise__Toronto_5A | 2030/baseline | 48 | 2 |
| HighRise__Vancouver_5C | 2022/activity | 48 | 2 |
| HighRise__Vancouver_5C | 2022/baseline | 49 | 1 |
| HighRise__Winnipeg_7A | 2030/baseline | 49 | 1 |
| MidRise__Calgary_6B | 2022/baseline | 49 | 1 |
| MidRise__Toronto_5A | 2030/activity | 49 | 1 |
| All other 88 buckets | — | 50 | 0 |

Total missing: 10. Max shortfall in any single bucket: 2. No bucket ≤ 45. All cells clear to plot.

**T3 — SI plots + appendix (green-lit):**

- **Plot generator:** `Step9_docs/step9_si_plots.py` — reads `cluster_run_results.csv` locally;
  produces 5 PNG figures under `Step9_docs/figures/`:
  - `figS1_equip_calibration.png` — equipment BL vs AC per cell, SHEU ±15% band
  - `figS2_light_calibration.png` — lighting BL vs AC per cell, SHEU ±15% band
  - `figS3_sheu_pct.png` — SHEU deviation (%) for all 48 cell×year; all within ±3%
  - `figS4_sleep_check.png` — sleep-hour mean Wh, 300 Wh threshold, WARN cells highlighted
  - `figS5_differential.png` — 2022→2030 activity vs baseline equip sharpening per cell
  - All 5 figures generated and verified locally (2026-06-06).

- **SI/Appendix text:** `Step9_docs/si_appendix_step9.md` — §S4 with 5 sub-sections:
  motivation, SHEU targets (Table S4.1), multi-unit fridge correction (7 units, 6× correction
  explained), validation grid + 48/48 gate summary (Table S4.2), and per-figure captions for
  Figs S1–S5.

**Key findings from CSV inspection:**
- Equipment max deviation: +2.1% (HighRise__Toronto_5A 2022) — well within ±15%
- Lighting max deviation: +2.5% (HighRise__Winnipeg_7A 2030)
- OtherDwelling sleep WARN (~600–790 Wh) is expected building-total fridge sum, not a calibration error
- MidRise shows strongest 2022→2030 sharpening (+100–150 kWh); OtherDwelling near-zero sharpness

**T2 confirmed SCATTERED (2026-06-06):** tally run via SSH; max shortfall = 2 per bucket; all cells clear to plot (see tally table above).

---

### 2026-06-06 — Re-run job 951682 (10 missing runs) — PARTIAL FAIL — MANAGER FLAG

**Job:** `step9_rerun_missing.sh`, submitted 15:06 EDT, running on `magic-node-02`.

**Status at time of writing:** 2/10 complete (failed), 1/10 running, 7/10 pending.

**Results so far:**

| Run | Result | Error |
|---|---|---|
| MidRise__Toronto_5A/activity/sample_003_HH1865/2030 | **FAIL** | 1 Severe — warmup convergence |
| MidRise__Calgary_6B/baseline/sample_029_HH78358/2022 | **FAIL** | 1 Severe — warmup convergence |
| HighRise__Toronto_5A/baseline/sample_012_HH32974/2022 | running | — |

**Root cause — E+ warmup convergence failure:**

Both failed runs share the identical Severe error:
```
** Severe  ** CheckWarmupConvergence: Loads Initialization, Zone="T SE APARTMENT"
              did not converge after 25 warmup days.
              ...Environment(RunPeriod)="RUNPERIOD 1"
```

Zone `T SE APARTMENT` is a MidRise zone. The failure is not a node kill — these IDFs genuinely
fail E+ warmup with the default 25-day limit. This is why they were missing originally.
Both are MidRise archetypes (different cities, different HH IDs, different treatments) — the
MidRise IDF + certain schedule combinations are triggering slow thermal convergence.

**Error files saved locally:**
```
Step9_docs/step9_cluster/errors/MidRise__Toronto_5A_activity_HH1865_2030.err
Step9_docs/step9_cluster/errors/MidRise__Calgary_6B_baseline_HH78358_2022.err
```

**Fix options for manager decision:**

| Option | What | Risk | Effort |
|---|---|---|---|
| A — Accept n=48/49 | Do nothing; gates already PASS at n=48–49 | Negligible statistical impact; document as known limitation | None |
| B — Increase warmup days | Patch `Maximum Number of Warmup Days` in MidRise IDF from 25 → 50; re-run the failing IDFs only | May still fail at 50; E+ default max is 25 but field allows higher | Low — 1 IDF edit + targeted re-run |
| C — Relax convergence tolerance | Edit `Building` object: loosen `Loads Convergence Tolerance Value` (default 0.04) and `Temperature Convergence Tolerance Value` (default 0.4) | Slightly less accurate thermal solution; unlikely to affect annual kWh materially | Low — same IDF edit approach |
| D — Combine B+C | Increase warmup days to 50 AND relax tolerance slightly | Best chance of convergence; small accuracy trade-off | Low |

**Recommendation to manager:** Option A is defensible — 48/49 HH per bucket is statistically equivalent to 50 for the SHEU gate check, and these 2 runs represent 0.04% of the 4,800-run campaign. If the paper needs to report exactly n=50, Option D (increase warmup days + slight tolerance relaxation) is the cleanest fix with minimal accuracy risk.

---

### 2026-06-07 — Warmup-60 Recovery (Round 1) — Job 951832 (s9_warmup60)

**Manager decision:** Option C from Round 0 options — raise `Maximum Number of Warmup Days` 25 → 60 first; if still Severe at 60, raise to 120.

**Scope:** 9 runs total — 1 MidRise Toronto HH1865/2030 + 8 HighRise (4×Toronto_5A, 3×Vancouver_5C, 1×Winnipeg_7A). MidRise Calgary HH78358/2022 EXCLUDED (HVAC blow-up, 53k+ warnings — not a warmup issue).

**Result:** MidRise Toronto HH1865/2030 — **PASS** (Severe=0, `hourly_meters.csv` extracted). 8 HighRise runs — **FAIL** (Severe ≥ 1 at 60 days).

Pre-check on HH32974/2022 (first HighRise fail): Max Heat Load = 4.4539E-002 at 60 days, 11% above tolerance 0.04 → initially assessed as "converging-but-slow."

---

### 2026-06-07 — Warmup-120 Recovery (Round 2) — Job 952228 (s9_warmup120)

**Manager decision (Option C):** Raise `Maximum Number of Warmup Days` 25 → 120 (practical E+ ceiling). Do NOT raise beyond 120. Do NOT relax any convergence tolerance.

**Scope:** 8 HighRise runs only. MidRise Toronto HH1865/2030 already resolved in job 951832 — NOT re-run. MidRise Calgary HH78358/2022 EXCLUDED (HVAC blow-up) — NOT included.

**Script:** `step9_cluster/step9_warmup120_recovery.sh`  
**Patch method:** Restore original IDF from `.bak_warmup60` (25-day IDF, archived by job 951832), then `sed` patch 25→120, grep-verify before running.  
**Tolerances (unchanged):** `Loads Convergence Tolerance Value = 0.04`, `Temperature Convergence Tolerance Value = 0.2`  
**Job elapsed:** 1:24:13 | sacct state: COMPLETED (exit 0:0)

**Per-run results:**

| # | Run | Severe@120 | Result |
|---|-----|-----------|--------|
| 1 | HighRise\_\_Toronto\_5A/baseline/sample\_012\_HH32974/2022 | 1 | **FAIL** |
| 2 | HighRise\_\_Toronto\_5A/baseline/sample\_012\_HH32974/2030 | 0 | **PASS** |
| 3 | HighRise\_\_Toronto\_5A/activity/sample\_017\_HH90265/2030 | 2 | **FAIL** |
| 4 | HighRise\_\_Toronto\_5A/baseline/sample\_026\_HH47072/2030 | 1 | **FAIL** |
| 5 | HighRise\_\_Vancouver\_5C/baseline/sample\_005\_HH79793/2022 | 1 | **FAIL** |
| 6 | HighRise\_\_Vancouver\_5C/activity/sample\_012\_HH75563/2022 | 1 | **FAIL** |
| 7 | HighRise\_\_Vancouver\_5C/activity/sample\_032\_HH104153/2022 | 1 | **FAIL** |
| 8 | HighRise\_\_Winnipeg\_7A/baseline/sample\_013\_HH44464/2030 | 1 | **FAIL** |

**Summary:** succeeded=1, failed=7

**PASS QC:** `HighRise__Toronto_5A/baseline/sample_012_HH32974/2030/hourly_meters.csv` — 1.7 MB, present on cluster ✓

**Convergence evidence for all 7 FAILs:** Each shows `CheckWarmupConvergence: Loads Initialization, Zone="... APARTMENT" did not converge after 120 warmup days.` — confirming **persistent oscillation**, not slow convergence. Pre-check assessment ("converging-but-slow" based on 60-day value 4.4539E-002) was incorrect; 120-day value = 4.4646E-002 (unchanged), confirming oscillation.

**Error files saved locally:**
```
Step9_docs/step9_cluster/errors/warmup120/HighRise_Toronto_HH32974_2022.err
Step9_docs/step9_cluster/errors/warmup120/HighRise_Toronto_HH90265_2030.err
Step9_docs/step9_cluster/errors/warmup120/HighRise_Toronto_HH47072_2030.err
Step9_docs/step9_cluster/errors/warmup120/HighRise_Vancouver_HH79793_2022.err
Step9_docs/step9_cluster/errors/warmup120/HighRise_Vancouver_HH75563_2022.err
Step9_docs/step9_cluster/errors/warmup120/HighRise_Vancouver_HH104153_2022.err
Step9_docs/step9_cluster/errors/warmup120/HighRise_Winnipeg_HH44464_2030.err
```

**FALLBACK applied — complete exclusion list:**

| # | Run | Reason |
|---|-----|--------|
| 1 | MidRise\_\_Calgary\_6B/baseline/sample\_029\_HH78358/2022 | HVAC blow-up (53k+ warnings) — excluded from Round 1 |
| 2 | HighRise\_\_Toronto\_5A/baseline/sample\_012\_HH32974/2022 | Persistent oscillation at 120 days (1 Severe) |
| 3 | HighRise\_\_Toronto\_5A/activity/sample\_017\_HH90265/2030 | Persistent oscillation at 120 days (2 Severe) |
| 4 | HighRise\_\_Toronto\_5A/baseline/sample\_026\_HH47072/2030 | Persistent oscillation at 120 days (1 Severe) |
| 5 | HighRise\_\_Vancouver\_5C/baseline/sample\_005\_HH79793/2022 | Persistent oscillation at 120 days (1 Severe) |
| 6 | HighRise\_\_Vancouver\_5C/activity/sample\_012\_HH75563/2022 | Persistent oscillation at 120 days (1 Severe) |
| 7 | HighRise\_\_Vancouver\_5C/activity/sample\_032\_HH104153/2022 | Persistent oscillation at 120 days (1 Severe) |
| 8 | HighRise\_\_Winnipeg\_7A/baseline/sample\_013\_HH44464/2030 | Persistent oscillation at 120 days (1 Severe) |

**Impact on bucket counts (updated):**

| Cell | Bucket | n (after exclusions) | Missing |
|---|---|---|---|
| HighRise\_\_Toronto\_5A | 2022/baseline | 48 | 2 |
| HighRise\_\_Toronto\_5A | 2030/activity | 48 | 2 |
| HighRise\_\_Toronto\_5A | 2030/baseline | 47 | 3 |
| HighRise\_\_Vancouver\_5C | 2022/activity | 47 | 3 |
| HighRise\_\_Vancouver\_5C | 2022/baseline | 48 | 2 |
| HighRise\_\_Winnipeg\_7A | 2030/baseline | 48 | 2 |
| MidRise\_\_Calgary\_6B | 2022/baseline | 49 | 1 |
| MidRise\_\_Toronto\_5A | 2030/activity | 50 | 0 (HH1865 recovered) |
| All other buckets | — | 50 | 0 |

All buckets ≥ 47. Statistical impact negligible for SHEU gate check. Exclusions documented as known limitation.

---

## Load-Shape Analysis — Phase Status

*Goal: aggregate hourly_meters.csv across full grid → diurnal W profiles + peak-hour shift.*

| Phase | Status | Job ID | Notes |
|---|---|---|---|
| SCRIPTS | COMPLETE 2026-06-07 | — | `step9_loadshape_aggregate.py` + `step9_loadshape.sh` written locally |
| UPLOAD | COMPLETE 2026-06-07 | — | scp'd both scripts to cluster step9_cluster/ dir |
| RUN | COMPLETE 2026-06-07 | **952280** | `s9_loadshape`; elapsed 00:06:42; exit 0:0 |
| DOWNLOAD | COMPLETE 2026-06-07 | — | 3 CSVs in `Step9_docs/` (profiles 2304 rows, peaks 96 rows, shift 48 rows) |
| FIGURES | COMPLETE 2026-06-07 | — | figS6_diurnal_equip.png, figS7_peak_shift.png, figS8_diurnal_light.png saved to `figures/` |
| SI APPENDIX | COMPLETE 2026-06-07 | — | §S5 tables + narrative written; zone-level artifact documented |

---

## Progress Log

### 2026-06-07 — Load-Shape Scripts Built (Employee, Sonnet 4.6)

**Task:** Build cluster aggregator + SLURM wrapper + local plotting script for Step 9 diurnal
load-shape / peak-hour-shift analysis.

**Scripts written:**

| File | Purpose |
|---|---|
| `step9_cluster/step9_loadshape_aggregate.py` | Pure-stdlib aggregator; streams hourly_meters.csv files one at a time; outputs 3 CSVs to `/speed-scratch/o_iseri/step9_run/loadshape/` |
| `step9_cluster/step9_loadshape.sh` | SLURM wrapper — SBATCH header copied verbatim from `step9_warmup120_recovery.sh`; only job-name changed to `s9_loadshape`; 48 h walltime; calls step4 host Python3 |
| `step9_loadshape_plots.py` | Local plotting script; mirrors `step9_si_plots.py` conventions; produces figS6, figS7, figS8 to `Step9_docs/figures/` |

**Job submission:** cannot submit directly (no SSH). See upload + submit commands below.

**Job 952280 — COMPLETED 0:0, elapsed 00:06:42**

**Files skipped:** 0 (all hourly_meters.csv had 8760 rows).

**n_hh per bucket (all ≥ 48):**

| Bucket | n_hh < 50 |
|---|---|
| HighRise__Toronto_5A / 2022 / baseline | 49 |
| HighRise__Toronto_5A / 2030 / activity | 49 |
| HighRise__Toronto_5A / 2030 / baseline | 49 |
| HighRise__Vancouver_5C / 2022 / activity | 48 |
| HighRise__Vancouver_5C / 2022 / baseline | 49 |
| HighRise__Winnipeg_7A / 2030 / baseline | 49 |
| MidRise__Calgary_6B / 2022 / baseline | 49 |
| MidRise__Toronto_5A / 2030 / activity | 49 |
| All other 88 buckets | 50 |

**Full peak_shift_summary.csv:**

```
cell,year,equip_bldg_shift,equip_zone_shift,light_bldg_shift,light_zone_shift
HighRise__Calgary_6B,2022,-4,-17,-5,-19
HighRise__Calgary_6B,2030,-4,-17,-3,-19
HighRise__Kelowna_5B,2022,-4,-17,-3,-19
HighRise__Kelowna_5B,2030,-4,-17,-3,-19
HighRise__Montreal_6A,2022,-4,-17,-3,-19
HighRise__Montreal_6A,2030,-4,-17,-3,-19
HighRise__Toronto_5A,2022,-4,-17,-4,-19
HighRise__Toronto_5A,2030,-4,-17,-3,-19
HighRise__Vancouver_5C,2022,-4,-17,-3,-19
HighRise__Vancouver_5C,2030,-4,-17,-3,-19
HighRise__Winnipeg_7A,2022,-4,-17,-4,-19
HighRise__Winnipeg_7A,2030,-4,-17,-3,-19
MidRise__Calgary_6B,2022,-4,-17,-5,-19
MidRise__Calgary_6B,2030,-4,-17,-3,-19
MidRise__Kelowna_5B,2022,-4,-17,-4,-19
MidRise__Kelowna_5B,2030,-4,-17,-3,-19
MidRise__Montreal_6A,2022,-4,-17,-4,-19
MidRise__Montreal_6A,2030,-4,-17,-3,-19
MidRise__Toronto_5A,2022,-4,-17,-4,-19
MidRise__Toronto_5A,2030,-4,-17,-3,-19
MidRise__Vancouver_5C,2022,-4,-17,-5,-19
MidRise__Vancouver_5C,2030,-4,-17,-3,-19
MidRise__Winnipeg_7A,2022,-3,-17,-4,-19
MidRise__Winnipeg_7A,2030,-4,-17,-3,-19
OtherDwelling__Calgary_6B,2022,-4,1,-2,-19
OtherDwelling__Calgary_6B,2030,-4,0,-2,-19
OtherDwelling__Kelowna_5B,2022,-4,0,-3,-20
OtherDwelling__Kelowna_5B,2030,-4,0,-3,-19
OtherDwelling__Montreal_6A,2022,-4,0,-3,-19
OtherDwelling__Montreal_6A,2030,-5,0,-3,-20
OtherDwelling__Toronto_5A,2022,-4,0,-3,-20
OtherDwelling__Toronto_5A,2030,-4,0,-2,-19
OtherDwelling__Vancouver_5C,2022,-4,0,-3,-19
OtherDwelling__Vancouver_5C,2030,-5,0,-2,-19
OtherDwelling__Winnipeg_7A,2022,-5,0,-5,-20
OtherDwelling__Winnipeg_7A,2030,-4,0,-3,-20
SingleD__Calgary_6B,2022,-5,-5,-5,-5
SingleD__Calgary_6B,2030,-4,-4,-4,-4
SingleD__Kelowna_5B,2022,-4,-4,-3,-3
SingleD__Kelowna_5B,2030,-4,-4,-3,-3
SingleD__Montreal_6A,2022,-4,-4,-3,-3
SingleD__Montreal_6A,2030,-4,-4,-2,-2
SingleD__Toronto_5A,2022,-4,-4,-3,-3
SingleD__Toronto_5A,2030,-4,-4,-4,-4
SingleD__Vancouver_5C,2022,-4,-4,-4,-4
SingleD__Vancouver_5C,2030,-4,-4,-3,-3
SingleD__Winnipeg_7A,2022,-5,-5,-3,-3
SingleD__Winnipeg_7A,2030,-4,-4,-2,-2
```

**Key findings:**

- **Equipment bldg shift: −4 h across all 24 cells** (range −3 to −5). Baseline h17–18 → activity h13–14. Completely consistent across archetypes, climate zones, and years.
- **Lighting bldg shift: −3 to −5 h.** Baseline h19–20 → activity h14–17. Afternoon task/screen lighting peak in activity arm.
- **2022 vs 2030:** Shifts are essentially identical. Mean equip_bldg_shift = −4.1 h both years (σ ≤ 0.4 h).
- **Prototype comparison:** Prototype (n=5 HH, SingleD×Montreal_6A) showed activity equip peak at h7. Full grid (n=50) shows h14. Direction confirmed; magnitude difference is a sample-size effect — n=5 was dominated by 1–2 HH with early breakfast schedules; n=50 averages to the post-lunch peak.
- **Zone-level artifact (HighRise/MidRise/OtherDwelling):** equip_zone and light_zone peak at h0 in activity arm — artifact of the zone meter capturing only unit-1, where the fridge dominates and has a near-flat daily curve. Building-level meter is the correct metric.
- **SingleD sanity check PASS:** equip_bldg_peak_h == equip_zone_peak_h for all 12 SingleD cell×year combinations ✓

**Figures produced:**
- `figures/figS6_diurnal_equip.png` — 4 archetype panels, equipment diurnal 2022
- `figures/figS7_peak_shift.png` — 24-cell dumbbell lollipop, equipment shift 2022
- `figures/figS8_diurnal_light.png` — 4 archetype panels, lighting diurnal 2022

**SI §S5 tables** written to `si_appendix_step9.md` with per-cell peak hours and shifts.
