# 3J Leg-2 — Step 7: Two-Channel BEM Integration — VALIDATION PLAN (companion)

> Companion to `3rdJ_07_bemIntegration_2split.md` (the main design doc). Holds the
> **validation plan + gate definitions + report layout**. Results are appended to the
> Progress Log once the validator `3rdJ_07_bemIntegration_2split_val.py` is built and run.
> Mirrors the 2J `07_bemIntegrationGSS_val.md` (residential) and extends it with the
> office (AT_WORK) section.

- **Validator (to build):** `3rdJ_07_bemIntegration_2split_val.py`
- **Reports:** `outputs_step7/step7_validation_report_{2022,2030}.html`
- **Status:** 📝 PLAN — validator not yet built.

---

## Validation sections

### Section A — Schema & structure (both products)
- Residential: exact column set + dtypes vs the 2J residential schema; row math
  `n_HH × 2 day-types × 24 h`; `Hour ∈ [0,23]`; `Day_Type ⊆ {Weekday, Weekend}`.
- Office: columns `office_archetype, BAND, Day_Type, Hour, AT_WORK_fraction, multiplier,
  n_persons`; `archetype ⊆ {Office_Knowledge, Office_Public, Office_Sales}`; complete grid
  (archetype × Day_Type × 24 h × bands).

### Section B — Day-type coverage (residential)
- 0 households with fewer than 2 day-types (consumer rejects partial HHs).
- Donor-draw preserved the calibrated weekend marginal (Weekend occupancy not diluted vs the
  pre-completion stock by more than ~0.5 pp; 2J copy-day fill lost −2.76 pp — must not recur).

### Section C — Residential occupancy fidelity
- Per-HH hourly occupancy reproduces the per-person `hom30` marginal within ≤ 1 pp.
- 2030 per band reproduces the Step-6 calibrated marginals (≤ ~0.1 pp), and bands ordered:
  daytime home occupancy conservative < hybrid < fullyhybrid (WFH raises daytime home presence).

### Section D — Metabolic plausibility (residential)
- `Metabolic_Rate ∈ [70, 245]` W/person (Sleep 70 floor, Cooking 245 ceiling); no NaN.
- Night slots dominated by 70 W (sleep anchor).

### Section E — Office presence fidelity & shape
- `AT_WORK_fraction ∈ [0,1]`; weekday shape sane: twin peaks ~09:30–11:30 & 14:30–16:30,
  lunch dip ~12–13:30, true peak ~15 h, night floor 0.02–0.05.
- Weekday > Weekend office presence for every archetype.
- **Band monotonicity (2030):** weekday business-hours office presence
  conservative > hybrid > fullyhybrid (WFH lowers office presence). Quantify the spread.
- Small-cell flag: list any (archetype × Day_Type × band) cell with low `n_persons`.

### Section F — Channel consistency (cross-product)
- WFH conservation: across bands, the daytime rise in residential home occupancy is directionally
  matched by the fall in office presence (not a hard equality — mutual exclusion is not enforced;
  commute/3rd-place slots are legitimately neither).
- AT_HOME ⊕ AT_WORK overlap reported (informational; per Step-6 mutex check ~0.5% conflicts is
  acceptable).

### Section G — Attribute integrity & regression
- DTYPE/PR have 0 within-HH drift; MATCH_TIER may vary per person (BEM-harmless, documented).
- Regression vs the 2J residential converter on a shared subset (where comparable): same
  occupancy/metabolic math → values match within rounding.

---

## Gate summary table (filled 2026-06-26)

| # | Gate | Target | 2022 | 2030 |
|---|---|---|---|---|
| A | Residential schema (13 cols) | exact OUT_COLS | PASS (match) | PASS (match) |
| A | Row count (N_HH×2×24) | computed | PASS (23,150 HH / 1,111,200 rows) | PASS (23,150 HH / 1,111,200 rows per band) |
| A | Hour domain {0..23} | {0..23} | PASS | PASS |
| A | Day_Type domain | {Weekday,Weekend} | PASS | PASS |
| A | 0 NaN in occ/metabolic | 0 | PASS | PASS |
| A | Office schema (7 cols) | exact OFFICE_COLS | PASS | PASS |
| A | Office archetype domain | ⊆ {Knowledge,Public,Sales} | PASS | PASS |
| A | Office grid complete | 3×2×24×bands | PASS (144 rows, 1 band) | PASS (432 rows, 3 bands) |
| B | Day-type coverage (res) | 0 partial HH | PASS (0 partial) | PASS (0 partial) |
| B | Weekend marginal preserved | ≤ 0.5 pp dilution | PASS (Δ+0.118 pp) | PASS (Δ+0.103 pp, cons band vs cons diary) |
| C | Residential occ fidelity WD | ≤ 1 pp | PASS (Δ0.174 pp) | PASS (all bands ≤ 0.335 pp) |
| C | Residential occ fidelity WE | ≤ 1 pp | PASS (Δ0.118 pp) | PASS (all bands ≤ 0.131 pp) |
| C | 2030 band ordering (home) | cons < hyb < fully | n/a | PASS (cons=0.407 < hyb=0.449 < fully=0.475) |
| D | Metabolic range | [70,245] W | PASS ([70.0, 245.0]) | PASS ([70.0, 245.0]) |
| D | Sleep trough | ≤ 85 W | PASS (73.2 W) | PASS (74.9 W) |
| D | WD metabolic (post-calib-C) | ~110 W (INFO) | INFO (109.8 W; sleep 33.9%) | INFO (109.9 W; sleep 34.8%) |
| E | Office fraction range | [0,1] | PASS ([0.008, 0.608]) | PASS ([0.030, 0.701]) |
| E | Office weekday shape (peak>floor) | peak > night floor | PASS | PASS |
| E | Office lunch-dip (relaxed 1.02×) | ≥ 1.02× | PASS | PASS |
| E | Office WD > WE presence | WD > WE 24h mean | PASS (2022 all OK) | ~~**FAIL**~~ → **PASS** (Fix C: Stage 0 weekend work cap in calibration-C reduced WE wrk30 18.6%→6.6%, matching obs; all 9 arch/band combos PASS post-fix) |
| E | Band monotonicity (office) | cons > hyb > fully (WD 9–17h) | n/a | PASS (K: 0.588>0.502>0.462; P: 0.591>0.514>0.445; S: 0.606>0.537>0.508) |
| F | WFH cross-channel direction | home↑ & office↓ cons→fully | n/a (2022 INFO: home 34.9%, office 51.1%) | PASS (home +6.8 pp, office −12.3 pp cons→fully) |
| G | DTYPE labels valid | ⊆ valid set | PASS | PASS |
| G | PR labels valid | ⊆ valid label set | ~~**FAIL**~~ → **PASS** (Fix A: PR_LBL remapped to region codes 1–6; PR_VALID updated; labels = Atlantic/Quebec/Ontario/Prairies/BC/Northern Canada) | ~~**FAIL**~~ → **PASS** (same fix) |
| G | DTYPE/PR within-HH drift | 0 drift | ~~**FAIL** (2,086 HH)~~ → **PASS** (Fix B: STAT canonicalization in convert() + recipient overwrite in complete_day_types(); drift = 0 both years) | ~~**FAIL** (2,086 HH)~~ → **PASS** (same fix) |
| G | MATCH_TIER labels/variation | labels valid; variation INFO | PASS (labels 2_Core/3_Constraints; 0 HH variation post-fix-B) | PASS |

---

## Progress Log

| Date | Task | Result | Notes |
|---|---|---|---|
| 2026-06-26 | Validation plan created | ✅ DONE | 7 sections (A–G) + gate summary defined for the two-channel Step 7. Validator script not yet built; results appended here after the first run. |
| 2026-06-26 | Validator built + run; HTML reports generated | ✅ DONE | **2022**: 30 PASS / 0 WARN / 2 FAIL. **2030**: 40 PASS / 1 WARN / 11 FAIL. Reports: `outputs_step7/step7_validation_report_2022.html`, `outputs_step7/step7_validation_report_2030.html`. **Relaxed/noted gates**: (1) Office lunch-dip threshold mirrored from producer at 1.02× (not 1.3×; real GSS dips 4–7%) — PASS both years. (2) Metabolic/sleep treated as INFO post-calibration-C (WD ~110 W, sleep ~35%) — no hard FAIL. **FAILs requiring follow-up**: G.2/G.3 (both years): PR column retains GSS numeric codes 1–6 (producer PR_LBL covers census 10–70 only) + donor-draw causes cross-province drift in 2,086 HH — metadata only, non-simulation-breaking, producer fix needed. E.4 (2030): 2030 office WE 24h mean > WD 24h mean for all 9 arch/band combos — Step-6 calibration artifact (WE night wrk30 inflated ~22%); biz-hrs band monotonicity unaffected (PASS). |
| 2026-06-26 | Fix bundle A/B/C applied — all FAILs cleared; gate table updated | ✅ DONE | **Employee (Sonnet 4.6), LOCAL.** Three-fix bundle cleared all prior FAILs. Fix A: `PR_LBL` remapped to region codes 1–6 (authoritative: `_PROVINCE_TO_REGION` in `3rdJ_05_censusLinkage_2split.py`); `PR_VALID` updated to {Atlantic, Quebec, Ontario, Prairies, BC, Northern Canada} (removed Alberta — merged into Prairies region 4). Fix B: STAT canonicalization in `convert()` via `groupby("SIM_HH_ID").first()` + recipient-overwrite in `complete_day_types()`; within-HH DTYPE/PR drift 2,086 -> 0. Fix C: Stage 0 weekend work cap in calibration-C; WE wrk30 18.6%->6.6% (matching obs); E.4 WD>WE PASS for all 9 arch/band combos. **Final scorecard: 2022 = 32 PASS / 0 WARN / 0 FAIL; 2030 = 43 PASS / 0 WARN / 0 FAIL.** Gate table rows E.4, G.2, G.3 updated to PASS above. |
| 2026-07-18 | 2030 BEM schedules regenerated on mutex-fixed `_C` deliverable — mutex propagation confirmed | ✅ DONE | On 2026-07-17, all three 2030 BEM schedules (`BEM_Schedules_2split_2030_{conservative,hybrid,fullyhybrid}.csv`) were regenerated via `--deliverable` override onto `Step6_docs/outputs_step6/2030_synthetic_diaries_2split_calibrated_mindwell_C.csv` (the mutex-fixed deliverable of record) — run log `run_year2030_20260717.log`, all gates report "ALL PASS" (Residential 5/5 PASS × 3 bands, Office archetype/fraction/shape gates ALL PASS, band monotonicity PASS for Office_Knowledge/Public/Sales). MD5 check confirms the mutex change propagated: the 3 regenerated residential schedule CSVs each have a **different** MD5 from their `_BAK_2026-07-17` pre-regen counterparts (e.g. conservative `d1865bbb...` vs `4e21c6d6...`), while `office_presence_multiplier_2030.csv` MD5 is **identical** pre/post (`3b2f8a2b...` both), confirming the office channel is correctly insulated from the residential-side mutex fix. Row counts unchanged: 1,111,200 data rows / 23,150 HH per residential band; office grid 432 rows (3 archetype × 2 day-type × 24h × 3 bands). This doc's own Gate summary table above (filled 2026-06-26) still holds at the named-gate granularity: **2022 = 22P/2I, 2030 = 25P/1I, 0 WARN / 0 FAIL both years** (re-counted directly from the table's 2022/2030 columns to confirm no gate flipped). Note: the HTML reports (`outputs_step7/step7_validation_report_{2022,2030}.html`) are timestamped 2026-07-15 20:16, i.e. **before** the 2026-07-17 mutex regen — they were not re-rendered as part of this task and reflect the pre-regen CSVs at the individual-check granularity (43 PASS / 0 WARN / 0 FAIL for 2030 there); re-render them before quoting per-check numbers post-mutex-fix. |
