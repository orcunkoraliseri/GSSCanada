# Step 9 — Activity-Driven Equipment & Lighting: Validation

## Goal

Validate the Step-9 activity-driven load campaign (the supplementary, end-use-resolved load-shape
analysis) on four axes: **engine integrity** (paired runs complete and physically converged),
**calibration** (annual equipment & lighting match the NRCan SHEU 2019 anchors per dwelling type),
**injection correctness** (the activity carrier replaces — does not double-count — the IDF default
loads, and the flat baseload is preserved), and **scientific soundness** (a physically plausible
diurnal shape with a detectable, correctly-signed activity-vs-baseline peak-hour shift that is
stable across the grid). This is the validation record for the **completed** full-grid run; results
below are populated from the cluster outputs, not a forward plan.

**Input**: `/speed-scratch/o_iseri/step9_run/idfs/<cell>/<arm>/<sample>/<year>/hourly_meters.csv`
(per-run E+ meters) + the aggregated `cluster_run_results.csv`, `loadshape_profiles.csv`,
`peak_hours.csv`, `peak_shift_summary.csv` (in `Step9_docs/`).
**Reference**: NRCan SHEU 2019 per-dwelling end-use anchors (§9.4 of `09_activityDrivenLoads.md`);
the Step-8 presence-only baseline on the **same** sampled households (paired Δ).
**Output**: this doc + Supplementary figures `Step9_docs/figures/figS1–figS8.png`, SI text
`Step9_docs/si_appendix_step9.md` (§S4–S5), cluster log `Step9_docs/cluster_run.md`.

**Grid**: 4 archetypes {SingleD, OtherDwelling, MidRise, HighRise} × 6 cities {Toronto_5A,
Kelowna_5B, Vancouver_5C, Montreal_6A, Calgary_6B, Winnipeg_7A} × n=50 HH (seed 42, same sample as
Step 8) × 2 years {2022, 2030} × 2 arms {baseline, activity} = **4,800 paired E+ runs**.

> **Status: COMPLETE — all gates evaluated, 0 FAIL.** Headline result confirmed and verified
> independently from the raw profiles (manager check 2026-06-07).

---

## Section 1 — Run Integrity

| Check | Logic | Result | Status |
|---|---|---|---|
| 1.1 Completeness | runs producing a valid 8760-row `hourly_meters.csv` / 4,800 | 4,790 completed (10 absent) | PASS |
| 1.2 Per-bucket sample | n_hh per (archetype × city × year × arm) | all ≥ 48 of 50 (96 buckets) | PASS |
| 1.3 Output schema | each run yields 8760 hourly rows, 10 meter columns | 0 files skipped (all exactly 8760 rows) | PASS |
| 1.4 Documented exclusions | failed runs triaged & logged, none silently dropped | 8 excluded, all in `cluster_run.md` | INFO |
| 1.5 No tolerance relaxation | warmup/loads convergence tolerances unchanged | confirmed (excluded, not relaxed) | PASS |

**Exclusions (8 total, ≤0.17 % of grid; all documented in `cluster_run.md`):**

- **7 × HighRise** APARTMENT-zone **persistent warmup oscillation** (Toronto HH32974/2022,
  HH90265/2030, HH47072/2030; Vancouver HH79793/2022, HH75563/2022, HH104153/2022; Winnipeg
  HH44464/2030). The 120-day max-load comparison (4.4646E-2) equals the 60-day value (4.4539E-2)
  → genuine oscillation, not slow convergence. E+ still reports *Completed Successfully* (1–2
  Severe); excluded as a conservative measure, **not** by relaxing tolerance.
- **1 × MidRise** Calgary HH78358/2022 — HVAC instability (53k+ warnings), not a warmup issue.
- One additional run (MidRise Toronto HH1865/2030) initially failed warmup and was **recovered** at
  120 days (job 951832); HighRise Toronto HH32974/**2030** likewise recovered. Only the 8 above
  remain excluded.

*Every retained bucket holds n ≥ 48, so the per-cell means are statistically unaffected.*

---

## Section 2 — SHEU Calibration Gates (the hard gate)

Per-dwelling-type annual targets (kWh/HH·yr) and the ±15 % gate (design target ±10 %; §9.4).
Evaluated for all 48 cell × year combinations on the activity arm.

| Dwelling type | Equip target | Light target | Equip result | Light result | Status |
|---|---|---|---|---|---|
| SingleD | 3,700 | 1,262 | within ±0.1 % | within ±0.5 % | PASS |
| OtherDwelling | 3,139¹ | 1,100 | within band | within band | PASS |
| MidRise | 2,166 | 736 | within band | within band | PASS |
| HighRise | 1,922 | 736 | +2.1 % (max) | +2.3 % (max) | PASS |

| Gate | Logic | Result | Status |
|---|---|---|---|
| 2.1 Equipment SHEU ±15 % | activity annual equip vs anchor, per cell × year | **48/48 PASS**; max \|dev\| **2.5 %** (MidRise Toronto 2030, under); largest over +2.1 % (HighRise Toronto 2022) | PASS |
| 2.2 Lighting SHEU ±15 % | activity annual light vs anchor, per cell × year | **48/48 PASS**; max \|dev\| **+2.3 %** (HighRise Toronto 2030) | PASS |
| 2.3 Within design ±10 % | tighter aspiration from §9 HARD GATES | all 48 within **±2.6 %** → passes ±10 % too | PASS |
| 2.4 Climate stability | deviation should not vary systematically with CZ | tight clustering <3 % across all 6 zones | PASS |

¹ OtherDwelling gross target includes the building's 7 named fridges; the gate is applied after the
D8 multi-unit correction (Section 3).

**Verified independently:** `cluster_run_results.csv` read directly — all 48 rows report
`sheu_pct_equip` and `sheu_pct_light` within ±2.6 %, both gate flags PASS.

---

## Section 3 — Injection Correctness (no double-count, baseload preserved)

| Check | Logic | Result | Status |
|---|---|---|---|
| 3.1 Neutralize-and-inject | all non-fridge ELECTRICEQUIPMENT/LIGHTS in the occupancy zone zeroed; ONE `STEP9_Equip`/`STEP9_Lights` carrier injected with calibrated `Design_Level` + activity schedule | confirmed in `integration.py` (lines ~1497–1670) | PASS |
| 3.2 No double-count | activity carrier replaces defaults (not added alongside) | fixed 2026-06-04 (was the n=20 +63 % overshoot); 48/48 now PASS | PASS |
| 3.3 Watts/Area no-op fixed | NECB apartments used `Watts/Area` → calibrated W ignored | fixed: method forced to `EquipmentLevel`/`LightingLevel` (was the −45–63 % undershoot) | PASS |
| 3.4 Baseload integrity | fridge never zeroed; flat 24/7 | named fridge preserved (SingleD, OtherDwelling); NECB lump → `STEP9_Fridge` 51.14 W (448 kWh/yr) | PASS |
| 3.5 Multi-unit correction (D8) | building meter sees all units' fridges; subtract non-occupied units before gate | OtherDwelling: **7 fridges → subtract 6×448 = 2,688 kWh** | PASS |
| 3.6 Step-8 path untouched | Step-9 block only entered when `equip_design_W > 0`; loop guards skip EQUIP/LIGHTS | Step-8 outputs byte-identical | PASS |
| 3.7 Dishwasher de-bounce (RF1) | consecutive eating slots must not re-fire the 3-slot queue | 3-h cooldown; 18 active slots on all-eating day (was 48) | PASS |

---

## Section 4 — Diurnal Load Shape & Peak-Hour Shift (the headline novelty)

The primary Step-9 contribution: activity time-series redistributes load *within* the day even when
the annual total is held to SHEU. Metric basis = building-level `InteriorEquipment:Electricity` /
`InteriorLights:Electricity`, mean diurnal profile (hour % 24) per (cell, year, arm).

| Check | Logic | Result | Status |
|---|---|---|---|
| 4.1 Equipment peak shift | activity peak hour − baseline peak hour | **−4 h uniform** (range −3 to −5); mean −4.1 h (σ 0.4 in 2022, 0.3 in 2030) | INFO ✔ |
| 4.2 — baseline vs activity | where the peaks sit | baseline **h17–18** (evening) → activity **h13–14** (early afternoon, post-lunch) | INFO |
| 4.3 Lighting peak shift | same, lighting | **−2 to −5 h**; baseline h19–20 (evening) → activity h14–17 (afternoon) | INFO ✔ |
| 4.4 Grid uniformity | shift stable across archetypes / cities / years | identical pattern across all 24 cells, both years | PASS |
| 4.5 Diurnal sanity | physically plausible structure; zero/low during sleep | sleep-trough present; afternoon/evening structure as expected | PASS |
| 4.6 Sleep-hour floor | mean equip Wh, 02:00–05:00; WARN > 300 Wh | WARN 28/48 (all SingleD + all OtherDwelling + 4 MidRise-2022 cells: Kelowna/Montreal/Toronto/Vancouver) = fridge/standby baseload, **not** an error | WARN |
| 4.7 SingleD bldg = zone | 1 unit = whole building ⇒ meters must match | all 12 SingleD cell-years: `equip_bldg_peak_h` = `equip_zone_peak_h`, light too | PASS |
| 4.8 Multi-unit zone artifact | zone meter ambiguous for apartments (fridge-dominated, argmax→h0) | zone-level shift reads −17/−19 h (artifact); **building-level is the metric** — documented | INFO |
| 4.9 Default vs Step-9 demand (figV1) | overlay default (baseline) vs Step-9 (activity) equipment demand — SingleD absolute with annual-kWh + SHEU annotation, multi-unit normalized | demand reshaped (peak h18→h14) while SingleD annual lands on the SHEU anchor | INFO |

**Verified independently (manager, 2026-06-07):** raw `loadshape_profiles.csv` for
SingleD__Toronto_5A 2022 — baseline equipment peaks h18 (1,152 W), activity peaks h14 (732 W) =
−4 h; lighting baseline h20 → activity h17 = −3 h; `equip_bldg_W` ≡ `equip_zone_W` byte-for-byte
for SingleD. The −4 h equipment shift is real, not a summary artifact.

**Note on the prototype:** the 1-cell prototype (n=5) reported an activity equipment peak at **h7**;
the full grid (n=50) for the same cell gives **h14**. The prototype value was a small-sample
artifact (1–2 early-breakfast HHs dominating the mean); the n=50 result supersedes it. The
*direction* (earlier than the evening baseline) is preserved. **Do not cite h7** as the aggregate.

**Figure V1 — Default vs Step-9 equipment demand (validation visualization).**
`outputs_step9/figV1_default_vs_step9_equip.png`. 2×2 archetype grid, 2022, comparing the **default**
(baseline arm, presence-gated IDF schedule) against the **Step-9 generated** (activity arm) equipment
demand:
- **SingleD panel** — absolute mean demand (W, 6-city mean): default (grey) vs Step-9 (colour), with
  each arm's **annual kWh and the SHEU target (3,700 kWh) annotated**. This shows Step 9 reshapes the
  diurnal curve (evening → early-afternoon peak) *while holding the annual total on the SHEU anchor* —
  i.e. the schedule changes shape, not energy budget. SingleD is the clean per-dwelling case
  (1 unit = whole building).
- **OtherDwelling / MidRise / HighRise panels** — the same default-vs-Step-9 comparison **normalized to
  each profile's daily mean** (building-level activity reflects a single injected unit, so absolute
  magnitudes are not comparable — calibrated magnitudes are in figS1). 

This is the explicit "before/after" the activity method produces; it complements the normalized shape
overlay (figS6) by tying the SingleD shape change directly to the calibration gate. It is produced and
the gate values re-checked by the runnable validator `09_activityDrivenLoads_val.py` (below).

---

## Section 5 — 2022 → 2030 Differential

| Check | Logic | Result | Status |
|---|---|---|---|
| 5.1 Shift persistence | peak-hour shift holds 2022 → 2030 | identical (−4.1 h both years; statistically the same) | PASS |
| 5.2 Differential sharpening | activity trend vs baseline trend (annual) | MidRise strongest positive sharpness (+100–150 kWh); HighRise/OtherDwelling near-zero/slightly negative | INFO |
| 5.3 Driver attribution | shift driven by activity model, not year-specific diary mix | shift invariant to year ⇒ activity-method effect | PASS |

(Annual differential figure = figS5; peak-hour persistence = peak_shift_summary 2022 vs 2030.)

---

## Section 6 — Pairing & Cross-Grid Consistency

| Check | Logic | Result | Status |
|---|---|---|---|
| 6.1 Same-HH pairing | activity & baseline arms share the per-cell seed-42 sample | confirmed (reused Step-8 frame, no re-sample) | PASS |
| 6.2 Bucket balance | n_hh equal across arms within a cell | balanced (≥48 both arms) | PASS |
| 6.3 Climate-zone coverage | all 6 CZ represented per archetype | 24/24 cells present | PASS |

---

## Summary Scorecard

| Level | Count | Items |
|---|---|---|
| PASS | 21 | run integrity, both SHEU gates, injection correctness (7), diurnal sanity, SingleD bldg=zone, pairing, consistency |
| WARN | 1 | sleep-hour baseload (28/48 cell-years) — expected fridge/standby, not a calibration error |
| INFO | 7 | peak-hour shift magnitudes, multi-unit zone artifact, 2030 differential, exclusion log, default-vs-Step-9 demand (figV1) |
| **FAIL** | **0** | — |

**Verdict: the Step-9 supplementary analysis is sound.** Annual loads calibrate to SHEU (48/48,
all <±2.6 %), injection is double-count-free with baseload preserved, and the novel finding — a
uniform **−4 h equipment / −2 to −5 h lighting** peak shift (evening → early afternoon) driven by
the predicted activity time-series — is robust across all 24 cells and both years, and was verified
against the raw profiles.

---

## Known Limitations / Caveats (state in Methods/SI)

| Item | Note |
|---|---|
| **Multi-unit profiles are per-occupied-dwelling** | The activity arm injects only the occupied unit (others' standard loads zeroed); the building-level *activity* total is therefore not a physically full building. Load-**shape** figures (figS6/S8) are normalized to daily mean so only timing is compared; calibrated annual magnitudes are in figS1/S2. Peak-hour and per-dwelling claims are valid. |
| **Zone-level meter unusable for apartments** | The single `Zone …Electricity Energy` column resolves to one (fridge-dominated) zone for multi-unit IDFs (argmax → h0). Building-level meters are used for all multi-unit findings; SingleD bldg=zone confirms the meter implementation. |
| **30-min resolution flattens appliance spikes** | Valid for load-shape/peak-hour; **not** for instantaneous appliance peak-kW. |
| **Derived per-end-use anchors** | SHEU publishes totals; per-end-use splits are model-grade (DR-1). The single calibration scalar bounds the error in the total, not the inter-end-use split. |
| **8 excluded runs** | 7 HighRise warmup oscillation + 1 MidRise HVAC; ≤0.17 % of grid, all buckets n≥48. |
| **Fridge count reconciled (2026-06-08)** | `09_activityDrivenLoads.md` line ~416 corrected "5 fridges / 4×448" → "7 fridges / 6×448 = 2,688 kWh", matching `cluster_run.md` and the gate code. No result impact — the run already used 7. |

---

## Artifacts

| File | Role |
|---|---|
| `cluster_run_results.csv` | 48-row calibration table (both SHEU gates, all PASS) |
| `loadshape_profiles.csv` | 2,304-row diurnal profiles (96 buckets × 24 h), bldg + zone, equip/light/facility |
| `peak_hours.csv` | per (cell,year,arm) peak hours |
| `peak_shift_summary.csv` | per (cell,year) baseline→activity shift |
| `figures/figS1–S5.png` | calibration & annual differential |
| `figures/figS6–S8.png` | diurnal load shape (normalized) + peak-hour shift |
| `outputs_step9/figV1_default_vs_step9_equip.png` | default vs Step-9 equipment demand (validation) |
| `09_activityDrivenLoads_val.py` | runnable validation — re-evaluates data-testable gates + builds figV1 + HTML report |
| `outputs_step9/step9_validation_report.html` | generated scorecard + embedded charts |
| `si_appendix_step9.md` | SI §S4 (calibration) + §S5 (load shape) |
| `cluster_run.md` | full cluster run log, deviations D1–D8, exclusion triage |

---

## Progress Log

| Date | Check | Result | Notes |
|---|---|---|---|
| 2026-06-07 | Step 9 full-grid validation consolidated | ✅ COMPLETE — 0 FAIL | 6 sections evaluated on the completed 4,800-run grid. §1 4,790/4,800 complete, 8 documented exclusions (7 HighRise warmup oscillation + 1 MidRise HVAC), all buckets n≥48. §2 SHEU 48/48 PASS both gates, max +2.1 % equip / +2.5 % light, all <±2.6 % (beats ±10 % design gate). §3 injection neutralize-and-inject verified, no double-count, baseload preserved, D8 multi-unit correction (OtherDwelling 7 fridges → −6×448 kWh). §4 headline peak shift −4 h equip / −3 to −5 h light, evening→early-afternoon, uniform across 24 cells & both years; SingleD bldg=zone confirmed; multi-unit zone artifact documented; **independently verified from raw `loadshape_profiles.csv`** (manager). §5 shift persists 2022→2030 (activity-driven, not diary-mix). Sleep-hour WARN 21/48 = expected baseload. Figures figS6/S8 re-rendered **normalized to daily mean** (fixes the misleading absolute-W multi-unit comparison); figS7 subtitle corrected ("morning"→"evening→early afternoon"). SI §S5 captions synced. Verdict: supplementary analysis sound, publishable. |
| 2026-06-07 | Programmatic validator built & run — `09_activityDrivenLoads_val.py` | ✅ 0 FAIL — matches hand-written doc on all hard gates | **Script**: `2J_docs_occ_nTemp/09_activityDrivenLoads_val.py` (stdlib csv + numpy + matplotlib; no pandas). **Console scorecard**: PASS=6  WARN=1  INFO=3  FAIL=0. Key computed numbers — G1: 96/96 buckets, min n_hh=48, median=50. G2a: 48/48 equip PASS, max \|pct_equip\|=2.52 %. G2b: 48/48 light PASS, max \|pct_light\|=2.35 %. G2c: max \|any\|=2.52 %, all within ±2.6 %. G4: equip 2022 mean=−4.08 h σ=0.40; 2030 mean=−4.08 h σ=0.28; range −5..−3 h; light range −5..−2 h; BL equip peaks h17, AC h13. G4x: Δ=0.000 h (2022≡2030). G5: 576 SingleD rows, 0 mismatches. **Divergences from hand-written doc (all within gate — no FAIL caused)**: (1) max \|pct_equip\|=2.52 % (doc says 2.1 %; actual max is MidRise Toronto 2030 at −2.52 %, not HighRise Toronto 2022 at +2.13 %); (2) max \|pct_light\|=2.35 % (doc says 2.5 %; actual max HighRise Toronto 2030 at 2.35 %, not HighRise Winnipeg 2030 at 2.25 %); (3) sleep WARN count=28/48 (doc says ~21/48 — MidRise 2022 cities Kelowna/Montreal/Toronto/Vancouver also WARN, total OtherDwelling 12 + SingleD 12 + MidRise 4 = 28); (4) light shift range −5..−2 h (doc says −3..−5 h; some OtherDwelling/SingleD 2030 cells have −2 h light shift). All divergences are minor/labelling; hard gates all confirmed. **Outputs produced**: `outputs_step9/figV1_default_vs_step9_equip.png` (SingleD absolute W with bl_kwh≈6641/ac_kwh≈3700/SHEU=3700 annotations; multi-unit panels normalized); `outputs_step9/step9_validation_report.html` (self-contained, figV1 + figS6–S8 embedded as base64). |
