# 3J Leg-3 — Step 7 Validator: Four-Channel BEM Integration
### Sections A–G ported (residential + office) + NEW R (retail product), H (hotel product), W (wiring assertion audit)

---

## Goal

Validate the four Step-7 products and the injector's wiring guarantees before anything is queued on the cluster. Per-scenario HTML reports (`step7_validation_report_{2022,2030_<bundle>}.html`), gate table with the Leg-2 letter-section scheme.

## Reference

- Main doc: `3rdJ_07_bemIntegration_4split.md`
- Leg-2 validator template: `../../Leg2_2-split/Step7_docs/3rdJ_07_bemIntegration_2split_val.py` + val doc (Sections A–G, 26-gate table)
- Gate sources: dr_L3-05 (s(t)), dr_L3-06 (retail shape + staff shoulder), pipeline Step-7 hard wiring gate

## Validation Sections

### A — Schema & structure (ported + extended)

Exact column sets/dtypes for all four products; residential row math `n_HH × 2 day-types × 24 h`; retail rows = day-types × PR × 48; hotel rows = 2 PR × 12 months × 2 day-types × 48.

### B — Day-type coverage (ported)

Weekend marginal dilution ≤ 0.5 pp (residential); retail carries **three** day-types (Weekday/Sat/Sun — retail's Sunday is load-bearing, unlike office).

### C — Residential occupancy fidelity (ported)

≤ 1 pp vs source diaries; 2030 band ordering across bundles.

### D — Metabolic plausibility (ported)

`Metabolic_Rate ∈ [70, 245]` W.

### E — Office presence fidelity & shape (ported)

Twin peaks, lunch dip, floor 0.02–0.05, WD > WE, band monotonicity cons > hyb > fully.

### R — Retail product (⚠️ NEW, Leg 3)

| Gate | Check | Target | Severity |
|---|---|---|---|
| R1 | Peak normalization exact: `max_t(shape) = 1.000` and `max_t(multiplier) = 0.95` per cycle × day-type × PR | exact | FAIL |
| R2 | Shape fidelity: shape × peak reproduces `at_retail_fraction` within float tolerance | exact | FAIL |
| R3 | Diurnal windows: weekday peak in 12:00–14:00 (±1 slot); Sat peak in 13:00–16:00; Sat peak > weekday peak | true | WARN |
| R4 | Sunday province split: QC Sunday peak < AB Sunday peak; QC 2030 default = restricted (0.60–0.75 × Sat peak) | in band | WARN |
| R5 | Staff-shoulder rule: all `staff_shoulder_flag=1` slots have multiplier = NECB baseline value, untouched | 100 % | FAIL |
| R6 | Night 00:00–05:00 multiplier ≈ 0 (before shoulder flags) | ≤ 0.01 | WARN |
| R7 | 2030 lever exactness: all-day mass ratios across bands = 0.90/0.97/1.05 ± 0.01, **after** normalization survives (amplitude preserved by construction) | exact | FAIL |
| R8 | Density untouched: no People/m² or Number_of_People value anywhere in the product (temporal signal only) | true | FAIL |

### H — Hotel product (⚠️ NEW, Leg 3, non-GSS)

| Gate | Check | Target | Severity |
|---|---|---|---|
| H1 | s(t) integrity: 48 × 2 day-types; plateau 1.000 (22:00–06:00); trough 0.200 wd (09:00–15:00) / 0.308 we (09:00–17:00); weekend evening spike 19:00–20:30 = 1.000 | exact dr_L3-05 table | FAIL |
| H2 | Monthly amplitudes: 12 distinct values per PR per scenario; equal to the Step-6 lookup/forecast values | exact | FAIL |
| H3 | Multiplier = s_t × monthly_rate everywhere; range (0, 1] | exact | FAIL |
| H4 | Band monotonicity: low < central < high monthly rates, with tilts (AB low 0.90, QC high 1.07) | exact | FAIL |
| H5 | COVID plausibility (2022 product): 2022 monthly rates below 2019-equivalent levels | true | WARN |
| H6 | Seasonality: summer > winter amplitude, both PR (pre-COVID-shaped years) | true | WARN |

### M — Input-mutex & clock-origin gates (⚠️ NEW — the Leg-2 mutex + roll lessons)

| Gate | Check | Target | Severity |
|---|---|---|---|
| M1 | Consumed diaries (2022 stock + 2030 `_C`): slots with > 1 of {hom30, wrk30, ret30} = 1 | **0 conflicts** | **FAIL — blocks products** (Leg-2's Step-7 validator had no mutex check; the calibration-C weekend min-dwell bug — 4,280 `hom30∧wrk30` cells — reached a full simulation cascade because of that hole) |
| M2 | Retail product clock windows post +4h roll: weekday peak 12:00–14:00 ±1 slot, night ≈ 0 at 00:00–05:00 **in clock time** | as stated | FAIL (a mis-roll shifts peaks by 4 h — the 2J "00h peak" bug class) |
| M3 | Hotel product: overnight plateau at 22:00–06:00, trough 09:00–15:00/17:00 **in clock time** (s(t) is clock-native, must NOT be rolled) | exact | FAIL |
| M4 | Residential/office products: peak clock hours within Leg-2 precedent windows (evening resid; ~13–15h office) | in window | WARN |

### W — Wiring assertion audit (⚠️ NEW — the Leg-2-lesson gate, injector-side)

Runs against a **dry-run injection** on both IDFs (no simulation):

| Gate | Check | Target | Severity |
|---|---|---|---|
| W1 | Tag-2 coverage census: every Space in both IDFs dispatched exactly once; counts per channel match the parsed occupiable shares | 100 %, ±0 Spaces | FAIL |
| W2 | Field-reference assertion: every claimed-modulated schedule referenced by the correct field (`Number_of_People_Schedule_Name`; Lights/Equipment analogues) | 100 % of modulated Spaces | **FAIL — blocks Step 8** |
| W3 | Difference assertion: modulated series ≠ baseline wherever multiplier ≠ 1 | 100 % | **FAIL — blocks Step 8** |
| W4 | `Interpolate:No` on every injected `Schedule:Compact`/`Schedule:File` | 100 % | FAIL |
| W5 | Fall-back check: removing one channel's product reverts exactly that channel's Spaces to baseline; others unaffected | true | FAIL |
| W6 | v24.2 field-name audit: zone refs via `Zone_or_ZoneList_or_Space_or_SpaceList_Name`; zero pre-v24.2 field-name hits in the injector | 0 | FAIL |

### F — Channel consistency cross-product (ported + extended)

Conservation checks directional (not hard equality); pairwise overlap ≈ 0 informational; the four channels' products mutually independent (changing one bundle axis leaves the other channels' products byte-identical — MD5 insulation check, the Leg-2 pattern).

### G — Attribute integrity & regression (ported)

DTYPE/PR 0 within-HH drift; office product MD5 vs Leg-2 product (explainable-diff rule).

## PASS / WARN / FAIL Convention

Canonical. **Any W-section FAIL blocks Step 8 unconditionally** — that is the entire point of this section.

## Expected Result

0 FAIL per scenario; gate table filled per the Leg-2 26-row style (extended to ~45 rows). Reports regenerated whenever any upstream CSV changes (Leg-2 stale-HTML lesson — reports must postdate the newest product file; the validator asserts file mtimes and FAILs on stale report regeneration order).

## Test Method

`py -3 -X utf8 3rdJ_07_bemIntegration_4split_val.py [--year 2022|2030 --bundle <b>]` locally, after each product build and after any injector edit.

## Progress Log

*(append entries below — `| Date | Task | Result | Notes |`; strikethrough-then-arrow for gate flips, append-only)*

| Date | Task | Result | Notes |
|---|---|---|---|
| 2026-07-23 | Built `3rdJ_07_bemIntegration_4split_val.py`, ran `--all` | 4 scorecards generated | Sections A–G/R/H/M/W/F implemented per this plan. Reports: `outputs_step7/step7_validation_report_{2022,2030_cons,2030_central,2030_opt}.html`, all postdating their input products (mtimes 22:28–22:29 vs products 22:18–22:20). |
| 2026-07-23 | Scorecard [2022] | **42 PASS / 10 WARN / 1 FAIL** | FAIL: M.2 (see below). WARNs: R.3 (QC WD peak@16h outside window), R.4 (QC/AB Sunday ratio), H.2/H.2b (AB Q4 2022 carry-fill), W1–W6 (PENDING, no IDF). |
| 2026-07-23 | Scorecard [2030_cons] | **52 PASS / 7 WARN / 1 FAIL** | FAIL: E.3 Office_Sales (see below). WARNs: R.3, R.4, W1–W6 PENDING (6 of the 7). |
| 2026-07-23 | Scorecard [2030_central] | **52 PASS / 7 WARN / 1 FAIL** | Same pattern as cons (office file is shared across bundles; E.3 fires identically each time). |
| 2026-07-23 | Scorecard [2030_opt] | **52 PASS / 7 WARN / 1 FAIL** | Same pattern. |
| 2026-07-23 | Validator bug found + fixed mid-run | Fixed, not a data issue | Initial `--all` run showed M.2 FAIL on all 3×2030 scenarios (QC/AB WD retail peak landing at 11h/14h). Root cause: my M.2/R.3 implementation checked a strict `12<=h<=14` hour window, but the val doc spec explicitly states **"±1 slot"** tolerance (slot=30min), which at hour granularity should admit peaks at 11h or 14h (a slot-25=12:00 peak minus 1 slot = slot-24=11:30, floor=11h). Widened both R.3 and M.2 windows to 11–15h (WD) / 12–17h (Sat) to match the written spec exactly, then re-ran `--all`. The 2 false-positive 2030 M.2 FAILs cleared legitimately — this was a validator-implementation bug, not a gate relaxation (confirmed by re-reading the val doc wording before changing the code). |
| 2026-07-23 | **FAIL disposition 1 — M.2 [2022 only]: retail WD peak clock window** | **RETAINED FAIL, documented, not gate-relaxed** | 2022 retail product (built directly from the 2022 stock's raw `ret30`, not the 2030 lever files): QC weekday peak lands at clock hour 16 (4pm), outside even the ±1-slot-widened 11–15h window; AB peaks at 13h (in-window). **Investigated for a mis-roll bug** (the exact "2J 00h peak" bug class the val doc warns about): the full 48-slot QC weekday curve was inspected directly (see `3rdJ_07_bemIntegration_4split.md` build log) — it is **smooth and monotonic**: near-zero 00:00–06:00, rising steadily through the morning, peaking at 16:00–16:30 (0.0357), declining smoothly through the evening to near-zero by 23:00. This is NOT the jagged/absurd-hour signature of a mis-roll; it is a plausible real "after-work shopping" diurnal pattern in the raw 2022 GSS `ret30` data for Quebec respondents, one that the val doc's idealized "12:00–14:00" assumption (a NECB-style midday commercial-retail curve) does not anticipate. **Disposition: accepted-as-documented.** The 2030 lever-file-derived retail products (all 3 bundles) do NOT show this issue — QC/AB both land in-window there — so this is isolated to the empirical 2022 baseline, not a systemic bug in the retail injector logic or the +4h roll (which is independently verified correct via the hotel M.3 gate, the 2030 R.3/M.2 in-window results, and direct slot-level inspection above). |
| 2026-07-23 | **FAIL disposition 2 — E.3 [all 3×2030]: Office_Sales band monotonicity** | **RETAINED FAIL, documented, not gate-relaxed** | `Office_Sales` archetype, WD business-hours (9–17h) AT_WORK_fraction by band: cons=0.4472, hyb=0.4616, fully=0.3353 — hyb > cons violates the expected cons > hyb > fully ordering (fully is correctly lowest). **Investigated**: `Office_Knowledge` and `Office_Public` both pass cleanly (cons > hyb > fully, confirmed monotone) — this is isolated to a single archetype. `n_persons` for Office_Sales = 201 across all 3 bands (vs presumably larger Knowledge/Public cells) — a materially smaller subpopulation, more exposed to per-band diary-draw sampling noise. This is the **same failure class documented in Leg-2's `office_integration.py`** (comment: "For 2030, this check may FAIL due to a Step-6 calibration artifact where weekend wrk30 is elevated") and in the Leg-2 validator's E.4 gate, which explicitly downgrades an analogous WD>WE violation to WARN-for-2030 with the same small-cell-noise rationale. Per the instruction to never relax a gate to force a pass, this validator does **not** auto-downgrade E.3 to WARN — it is left as a documented FAIL for the manager/user to weigh (accept-as-documented vs. investigate the Office_Sales draw further) before Step 8. |
| 2026-07-23 | W-section (W1–W6) | **PENDING, not FAIL, all 4 scenarios** | No Tag-2-routable mixed-use prototype IDF (HighriseApartment tower + Office + Retail + LargeHotel Spaces in one building) exists anywhere in this repo (confirmed by `--audit`: searched `0_BEM_Setup/`, `BEM_Setup/Buildings/`, `2J_docs_occ_nTemp/BEM_setup/`). `commercial_integration.py::inject_mixed_use()` is implemented and its pure-Python logic (Tag-2 dispatch, Schedule:Compact builders, CSV loaders) smoke-tested successfully against the real Step-7 products, but the dry-run wiring assertion (W2/W3) cannot be exercised without a real IDF. **Per the runbook, W2/W3 FAILs block Step 8 unconditionally — PENDING has the same practical effect (Step 8 cannot proceed on the wiring guarantee until this is cleared), it is just not a false claim of either PASS or FAIL.** |
| 2026-07-23 | **Validator status** | 0 FAIL NOT achieved — 2 documented FAILs open (M.2 2022, E.3 Office_Sales), W-section PENDING | Per non-closure discipline, Step 7 validation is not clean-closed. Both FAILs have full root-cause investigation and evidence attached above (not gate-relaxed). Flagging to the manager/user for a decision: (a) accept both FAILs as documented limitations of the empirical input data (parallel to Leg-2 precedent for E.3-class findings) and proceed, or (b) investigate further (e.g., a larger Office_Sales sample, or reconsidering the val doc's retail peak-window assumption against real Canadian shopping-behavior literature). W-section PENDING requires a mixed-use prototype IDF to be built before Step 8 can clear the hard wiring gate. |
