# Builder prompt — Step 6 Track B: Hotel SARIMA side-track (4-split)

> Paste into a fresh Sonnet session. Manager-authored 2026-07-21. Fully **local** work
> (`py -3 -X utf8`, `statsmodels`) — no cluster, no dependency on Track A, can run any time.

---

You are the **employee**. Execute the task below and append a Progress Log entry on completion.

## Read first

Runbook: `Leg3_4-split/Step6_docs/3rdJ_06_longitudinalForecasting_4split.md`, sections **6I/6J**
(Hotel side-track). Validation plan: `..._4split_val.md`, **Section 8** (hotel gate table). This
track is non-GSS — none of the JS/DRIFT_MATRIX machinery from Track A applies; these are classical
time-series forecast metrics.

## Data inputs

- Hotel canonical monthly series (confirmed present locally):
  `0_Occupancy/external/hotel_occupancy_monthly.csv` (Step-2 Delta-D output, QC + AB monthly
  occupancy rates)
- Hotel diurnal shape (dr_L3-05 48-slot table): **not a file** — it's specified directly in the
  runbook text (6J) and val doc (Section 8, gate H1): weekday + weekend variants, overnight plateau
  1.000 (22:00–06:00), day trough 0.200 weekday (09:00–15:00) / 0.308 weekend (09:00–17:00), weekend
  evening spike 19:00–20:30 = 1.000, evening return ramps in between. Encode this as a hardcoded
  constant table in your script (there is no source CSV to read it from) — cross-check every value
  against the val doc's gate H1 before hardcoding, since the validator will check this table for
  exact equality.
- **First, read `0_Occupancy/external/hotel_occupancy_monthly.csv`'s actual columns/date range
  yourself** (it's ~12.8KB, small enough to read directly) to confirm whether AB has the full
  2005–2022 span or only a truncated 2010–2022 series (OD-2 in the runbook: if AB is truncated, 6I
  fits on 156 obs and the splice dummy `D_splice` is dropped — this changes what you build, so check
  before writing the fitting code, not after).

## File to create

`Leg3_4-split/Step6_docs/3rdJ_06_hotel_sarima_4split.py`

## 6I — Fit + backcast gate

1. **Order selection**: fit SARIMA candidates on the **pre-COVID segment only (2005–2019)** per
   province (QC, AB); select `(p,d,q)(P,D,Q)₁₂` by BIC/AICc (expected result per the runbook:
   `SARIMA(1,1,1)(1,1,1)₁₂` — treat this as an expectation to verify, not a value to hardcode without
   fitting). Verify Ljung-Box residual whiteness on the selected order. **Freeze the orders** — do
   not re-select when you refit on the full series next.
2. **Re-estimate on the full 2005–2022 series** with intervention terms added to the frozen-order
   model: a COVID pulse dummy (2020-03…2022-06) **and** a permanent level-shift term that persists
   past the pulse window (the runbook is explicit that pure-pulse alone is over-optimistic —
   corporate travel stabilized 10–15% below pre-COVID — and pure level-shift alone is
   over-pessimistic; you need both terms, not one or the other). Add the AB splice dummy
   `D_splice` (t ≥ 2010-01) only if you find evidence of a level shift at the splice point in the AB
   series (check this empirically, don't assume).
3. **Backcast gate**: reconstruct 2015–2019 monthly values for QC + AB from the fitted model, compare
   to the historical series — target **MAE < 0.05**. Confirm the 2020-04 COVID dip is recovered
   without overshoot (reconstructed value should not undershoot below the actual historical low).

## 6J — 2030 forecast + multiplier build

- Forecast the monthly path to 2030. Report both the **SARIMA statistical prediction intervals**
  (80%/95%, from the fitted model) and the **three named scenario bands** (a separate, deliberate
  construction — these are physical-state assumptions for the simulation campaign, not statistical
  bands): **Low 0.92 / Central 1.00 / High 1.05** applied to the central forecast path, with
  provincial tilts **AB low = 0.90, QC high = 1.07** (i.e. AB's low band gets an extra downward tilt,
  QC's high band gets an extra upward tilt — apply the tilt only to that one band/province
  combination, not uniformly).
- Sanity-check the central path against known anchors before finalizing: 2023–2025 actuals QC ~0.635
  (Montreal ~0.666 in 2025), AB ~0.615 (Calgary ~0.63). If your central forecast is wildly off these,
  something's wrong with the intervention spec — investigate before shipping.
- Outputs:
  - `0_Occupancy/forecasts/hotel_multiplier_2030.csv` — 12 monthly values × 2 PR × 3 bands
  - `0_Occupancy/processed/hotel_multiplier_lookup.csv` — historical months × PR (for the 2022
    hotel product Step 7 will need)
- **s(t) table**: emit as its own artifact too (CSV or embedded constant, your call, but it must be
  inspectable) — 48 slots × 2 day-types (weekday/weekend), values exactly matching the dr_L3-05 table
  above. Holidays use the weekend shape (dr_L3-05 has no separate holiday variant — this is a
  documented limitation, note it in your Progress Log, don't try to invent a holiday shape).

## Test method — validator gates (Section 8 of the val doc)

Implement or hand off to the Track-A validator session a Section 8 check against these exact gates
(reproduce the table, don't paraphrase it away):

| Gate | Check | Threshold | Severity |
|---|---|---|---|
| 8.1 | Orders frozen on pre-COVID 2005–2019 by BIC/AICc, recorded | documented | FAIL if selected on full series |
| 8.2 | Ljung-Box residual whiteness (full-series refit, with interventions) | p > 0.05 | WARN |
| 8.3 | Backcast 2015–2019 reconstruction, QC + AB | MAE < 0.05 | FAIL |
| 8.4 | COVID 2020-04 dip recovered | no overshoot below historical low | FAIL |
| 8.5 | Intervention spec: pulse + permanent level-shift present, AB splice dummy if applicable | as above | FAIL |
| 8.6 | 2030 central path vs 2023–2025 anchors (QC ~0.635, AB ~0.615) | ±0.05 | WARN |
| 8.7 | Band monotonicity + tilts: low<central<high; AB low 0.90, QC high 1.07 applied | exact | FAIL |
| 8.8 | Seasonality preserved in 2030 path (12-month profile correlation vs pre-COVID mean profile) | r ≥ 0.8 | WARN |
| 8.9 | Output schemas correct; rates ∈ (0,1] | exact | FAIL |
| 8.10 | s(t) table integrity: 48×2 day-types, max=1.000, plateau/trough match dr_L3-05 (0.200/0.308) | exact | FAIL |

Per the val doc: **a hotel FAIL never blocks GSS-channel (Track A) sign-off** (additive-safety
principle), but it does block Step-7 hotel injection specifically — the fall-back guarantee routes
hotel Spaces to NECB baseline if this track isn't clean.

## Progress Log

Append a dated entry to `3rdJ_06_longitudinalForecasting_4split.md`'s Progress Log: which SARIMA
order was selected and for which province, whether AB used the full or truncated series (and
whether the splice dummy was included), the 8.3/8.4 backcast numbers, the 2030 central-path sanity
check against the 2023–2025 anchors, and the full Section-8 gate scorecard.

## Return

Concise report: SARIMA orders (QC/AB), backcast MAE, 2030 central-path values vs anchors, Section-8
scorecard (P/W/F counts), and flag anything that didn't clear a FAIL-severity gate rather than
softening it yourself.
