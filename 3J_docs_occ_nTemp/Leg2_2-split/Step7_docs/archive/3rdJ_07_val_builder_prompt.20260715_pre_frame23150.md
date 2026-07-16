# Builder prompt — `3rdJ_07_bemIntegration_2split_val.py` (validator + HTML reports)

> Paste into a fresh Sonnet session. Manager-authored 2026-06-26.

---

You are the **employee**. Build the Step-7 validator, run it for both years, write the two HTML
reports, fill in the val-doc gate table + Progress Log, and append a Progress Log entry. Work
**locally** only (no cluster). `pandas` + `numpy` + `matplotlib` (Agg backend) only — no new
packages. Read-only on all data (the validator never mutates a CSV). Run-from-anywhere (resolve
paths relative to the script). Do NOT modify the Step-7 producer script or any locked file.

## Read first (authoritative)
- **Style/idiom reference — port this:** `2J_docs_occ_nTemp\07_bemIntegrationGSS_val.py`
  (dark theme `_DARK`, `_b64()` base64-embedded matplotlib charts, `_clock()` 04:00-origin hour
  map, scorecard + findings lists + summary table, per-year HTML, `--year {2022,2030,both}` CLI,
  `_rec()`/`_sum()` recorders). Reuse the whole HTML/CSS scaffold and the chart helpers verbatim.
- **Validation plan (the sections to implement):** `…\Step7_docs\3rdJ_07_bemIntegration_2split_val.md`
  — Sections A–G + the gate summary table. Your job is to make that plan executable.
- **Producer script (read its actual output headers + its real gate thresholds, don't assume):**
  `…\Step7_docs\3rdJ_07_aug_to_bem_2split.py`. In particular read the office lunch-dip threshold it
  actually uses (it was relaxed to ~1.02× because real GSS noon dips are only 4–7%, NOT 1.3×) —
  mirror that, do NOT hard-FAIL on the real shallow dip.

## Build `…\Step7_docs\3rdJ_07_bemIntegration_2split_val.py`

### Inputs (all local, in `…\Step7_docs\outputs_step7\`)
- Residential 2022: `BEM_Schedules_2split_2022.csv`
- Residential 2030: `BEM_Schedules_2split_2030_{conservative,hybrid,fullyhybrid}.csv` (3 files)
- Office: `office_presence_multiplier_2022.csv`, `office_presence_multiplier_2030.csv`
### Calibration references (for fidelity checks)
- 2022 source (real stock): `…\Step5_docs\outputs_step5\3rdJ_25CEN_aug_Full_Aggregated_excl.csv`
  (per-person `hom30_001-048`, `act30_001-048`, `wrk30_001-048`, `DDAY_STRATA`).
- 2030 source (calibrated): `…\Step6_docs\outputs_step6\2030_synthetic_diaries_2split_calibrated_mindwell_C.csv`
  (the **_C** file — Step-7 2030 was re-run off this; use it, NOT the pre-_C file). Has `BAND`.
- **Do not hardcode `N_HH` or row counts** — compute from the actual residential file
  (`n_HH × 2 day-types × 24 h`); 2022 ≈ 23,211 HH, each 2030 band copies the same stock frame.

### Sections (map the val-plan A–G; one report per year)
1. **Schema & structure (A)** — residential: exact loaded-column set + dtypes, row math
   `n_HH×2×24`, `Hour ⊆ {0..23}`, `Day_Type ⊆ {Weekday,Weekend}`, 0 NaN, 48 rows/HH. Office:
   columns `{office_archetype,BAND,Day_Type,Hour,AT_WORK_fraction,multiplier,n_persons}`,
   `archetype ⊆ {Office_Knowledge,Office_Public,Office_Sales}`, complete grid (archetype×Day_Type
   ×24h ×bands).
2. **Day-type coverage (B)** — 0 partial HH; weekend marginal preserved: BEM weekend mean
   occupancy vs the source weekend `hom30` marginal ≤ ~0.5 pp dilution (2J copy-day lost −2.76 pp —
   must not recur).
3. **Residential occupancy fidelity (C)** — `Occupancy_Schedule ∈ [0,1]`; BEM per-HH hourly
   occupancy reproduces the source per-person `hom30` marginal within ≤ 1 pp (WD & WE); **2030
   band ordering**: daytime (clock 09–17h) home occupancy `conservative < hybrid < fullyhybrid`.
4. **Metabolic plausibility (D)** — `Metabolic_Rate ∈ [70,245]` W, no NaN; sleep trough (min
   hourly) ≈ 70 W; report **sleep share** (act30 code 5) and **WD mean metabolic** from the source
   reference — post calibration-C these are healthy (sleep ~35%, WD metabolic ~110 W); show
   before-context in the note (pre-_C was 22.8% / ~127 W). Treat as PASS/INFO, not a hard gate.
5. **Office presence fidelity & shape (E)** — `AT_WORK_fraction ∈ [0,1]`; weekday shape sane
   (daytime peak ≫ night floor; report the lunch-dip ratio but mirror the producer's relaxed
   threshold — INFO if shallow, do not FAIL); weekday > weekend per archetype; **band
   monotonicity (2030)**: weekday business-hours (clock 09–17h) office presence
   `conservative > hybrid > fullyhybrid` per archetype (quantify spread); flag any low-`n_persons`
   cell.
6. **Channel consistency (F)** — WFH conservation: across bands the daytime RISE in residential
   home occupancy is directionally matched by the FALL in office presence (directional, not a hard
   equality). Report AT_HOME⊕AT_WORK overlap (informational; Step-6 mutex ~0.5% is fine).
7. **Attribute integrity (G)** — DTYPE/PR 0 within-HH drift; MATCH_TIER per-person variation across
   day-types is informational (BEM-harmless), not a gate.
8. **Summary table** — same 4-col gate table as 2J (`Gate/Check | Threshold | Observed | Status`),
   PASS/WARN/INFO/FAIL coloring.

### 2030 report shape
ONE `step7_validation_report_2030.html` covering all 3 bands together: overlay the 3 residential
occupancy curves (one color per band) and the office band-monotonicity bars in the same charts;
run the band-ordering gates (sections 3 & 5) across the bands.

### Outputs
- `…\outputs_step7\step7_validation_report_2022.html`
- `…\outputs_step7\step7_validation_report_2030.html`
- CLI: `--year {2022,2030,both}` (default both). Console prints `N PASS / N WARN / N FAIL` per year.

## After the run
- Fill the **gate summary table** in `3rdJ_07_bemIntegration_2split_val.md` with the real 2022 &
  2030 observed values, and append a dated Progress Log row there (PASS/WARN/FAIL counts per year,
  the two report paths, any gate that did not run or was relaxed + why).
- Add a one-line note to the main doc Progress Log (`3rdJ_07_bemIntegration_2split.md`) that the
  validator was built + run and both HTML reports emitted.

## Return
Concise report: per-year PASS/WARN/FAIL counts, the two report paths, the band-ordering results
(both channels), the metabolic/sleep numbers (confirming calibration-C health), and any gate that
was relaxed or skipped (be honest).
