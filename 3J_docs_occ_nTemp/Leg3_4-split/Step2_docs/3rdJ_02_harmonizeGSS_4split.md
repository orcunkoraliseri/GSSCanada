# 3rdJ Step 2 — Data Harmonization (Leg-3 Four-Channel Split)
### GSS side: reuse Leg-2 outputs read-only + confirm the AT_RETAIL signal · Hotel side: harmonize the ISQ/CBRE series into the canonical monthly CSV

---

## Goal

The Leg-2 harmonizer (`3rdJ_02_harmonizeGSS_2split.py`) already produces everything the retail channel needs: the harmonized 18-category `occPRE` scheme carries **Shopping (code 5)** on every episode row in all four cycles, and the 14-category `occACT` carries **Purchasing Goods & Services (code 4)** (audit §2/§3). **No GSS re-run is required** — Leg-3 consumes `../../Leg2_2-split/Step2_docs/outputs_step2/` read-only, and the AT_RETAIL derivation itself executes inside the Step-3 tiler (frozen rule below).

Step-2 build work is therefore:
1. **Delta A (verification, not build)** — confirm the retail crosswalk and the signal's cross-cycle stability from the Leg-2 harmonized episodes (validator work).
2. **Delta B (rule record)** — the gated OR-rule is FROZEN (OPEN DECISION 1, user-approved 2026-07-02); the per-cycle online-shopping leak cross-tab is **still produced** as a Step-2 validation output.
3. **Delta C (exclusion record)** — restaurant (`occPRE == 7`) is available in all cycles and explicitly out of scope.
4. **Delta D (the one build item)** — harmonize the Step-1 raw hotel assembly into the canonical `0_Occupancy/external/hotel_occupancy_monthly.csv` (splice, units, window).

## Reference

- Pipeline: `../3rdJ_00_4split_Occupancy_Pipeline.md` — STEP 2 (§2A–2D); Overview STEP 2 box
- Spec: `../4-channel_split.md` §2.2–2.3, §3.3
- Deep research: `../deepResearch/dr_L3-01_statcan_hotel_data_REPORT.md` (splice calibration), `../deepResearch/dr_L3-06_retail_diurnal_targets_REPORT.md` (episode-time share context)
- Leg-2 counterpart (template): `../../Leg2_2-split/Step2_docs/3rdJ_02_harmonizeGSS.md` + `3rdJ_02_harmonizeGSS_2split.py`
- Audit: `../../investigation/00_GSS_split_suitability_audit.md` §2 (crosswalk confirmed all cycles)

## Data Source Inventory

| Artifact | Path | Role |
|---|---|---|
| `episode_{2005,2010,2015,2022}.csv` (harmonized: `occPRE`, `occACT`, `AT_WORK`, weights) | `../../Leg2_2-split/Step2_docs/outputs_step2/` | ✅ DONE (Leg 2) — read-only input |
| `main_{cycle}.csv` (harmonized) | 〃 | ✅ DONE (Leg 2) — read-only input |
| `hotel_occupancy_raw_assembled.csv` | `../Step1_docs/outputs_step1/` | ⚠️ Leg-3 Step-1 output — Delta-D input |

## Proposed Changes (Leg-3 Deltas)

### Delta A — AT_RETAIL crosswalk confirmation ⚠️ PLANNED (Leg 3, verification-only)

`occPRE == 5` ("Shopping") is already emitted by the Leg-1/Leg-2 presence crosswalk:

| Unified | 2005 (C19) | 2010 (C24) | 2015 (C29) | 2022 (GSSP) | Status |
|---|---|---|---|---|---|
| `occPRE == 5` Shopping | `PLACE = 06` Grocery + `07` Other store / Mall | `PLACE = 06` + `07` | `LOCATION = 306` | `LOCATION = 3306` | ✅ Confirmed all cycles (audit §2) |
| `occPRE == 7` Restaurant/bar/club | `PLACE = 04` | `PLACE = 04` | `LOCATION = 309` | `LOCATION = 3309` | available — excluded (Delta C) |

> **Granularity note.** 2015/2022 collapse grocery vs general merchandise into one bucket; the harmonization already merges 2005/2010 into the same single "Shopping" category → cross-cycle consistent, but a grocery-vs-merchandise archetype split is impossible from GSS (recorded; drives the Step-5 single-retail-archetype decision). Weighted episode-time share in shopping locations: **~2.1–2.3 %, stable across cycles**.

### Delta B — The FROZEN gated OR-rule + the leak cross-tab ⚠️ PLANNED (Leg 3)

**✅ RULE FROZEN 2026-07-02 (OD-1, user-approved):**

```python
AT_RETAIL = (occPRE == 5) | ((occACT == 4) & occPRE.isin({5, 9}))
```

- The activity arm is **gated** to plausible retail locations {5 Shopping, 9 Other/unspecified-out} — this excludes the online-shopping leak (`occACT == 4 & occPRE == 1` = shopping *from home*), whose growth over 2005→2022 would otherwise corrupt exactly the longitudinal signal we care about.
- Consequences carried forward: (a) `AT_HOME ∧ AT_RETAIL` is **not** a legitimate overlap → the dr_L3-12 exclusivity projection applies to the full {AT_HOME, AT_WORK, AT_RETAIL} set (Step 4); (b) the per-cycle `occACT==4 × occPRE` cross-tab **must still be produced** here as a verification output — the freeze does not skip the verification; (c) gating **adds to, never replaces**, the LOCATION-mapping rate gates and co-presence checks.
- The derivation itself is executed episode-level inside the Step-3 tiler script (one place, no duplicated rule); Step 2 emits the cross-tab from the same frozen expression via the validator.

### Delta C — Restaurant: available but excluded (decision record)

`occPRE == 7` would be one more Step-3 list entry, but the PNNL prototypes route `Dining` to the Office channel and `LargeHotel Cafe` to hotel-amenity baseline — **no Space to drive**. Out of scope for Leg 3 (OD-9); recorded so the exclusion is a decision, not an oversight.

### Delta D — Hotel series harmonization ⚠️ PLANNED (Leg 3, non-GSS) — [NEW] `3rdJ_02_hotelHarmonize_4split.py`

Input: Step-1 raw assembly. Output: **canonical** `0_Occupancy/external/hotel_occupancy_monthly.csv` (`YEAR, MONTH, PR, occupancy_rate, ADR_CAD, RevPAR_CAD` + provenance cols `SOURCE, SPLICED`), plus a copy in `outputs_step2/` for validation.

1. **Geography:** QC + AB (Montreal Z6 / Calgary Z7A); keep any acquired market-level series in a side file `hotel_occupancy_monthly_markets.csv` (validation context only).
2. **Window:** 2005-01…2022-12. **All months kept** — the COVID collapse is signal for the Step-6 SARIMA COVID indicator, never a gap to fill.
3. **AB splice at the Jan-2010 boundary** (dr_L3-01): `Occupancy_Spliced(t) = Occupancy_CBRE(t) × [mean(ABDASH_2010) / mean(CBRE_2010)]` — the dashboard excludes resorts and runs 2–4 pp lower than raw CBRE provincial; splice rows flagged `SPLICED = 1`. If the CBRE archive path failed (Step-1 fallback), emit the truncated 2010–2022 AB series and record the decision (the Step-6 SARIMA doc handles both cases; a splice level-shift dummy `D_splice` is then moot).
4. QC/ISQ needs no splicing (structurally consistent 2005–2022).

## Module Structure Summary

```
3rdJ_02_hotelHarmonize_4split.py
├── load_raw_assembly()          (Step-1 output)
├── splice_ab_2010()             (calibration-factor splice, SPLICED flag)
├── finalize_schema()            (canonical column set + provenance)
└── __main__                     (writes external/ canonical + outputs_step2/ copy)

3rdJ_02_harmonizeGSS_4split_val.py   (validator — GSS retail-signal checks read Leg-2
                                      outputs_step2 read-only; hotel canonical checks;
                                      OR-rule leak cross-tab emission)
```

## Expected Result

- `0_Occupancy/external/hotel_occupancy_monthly.csv` — 216 QC rows + 216 AB rows (or 156 AB + documented fallback), `occupancy_rate ∈ (0,1]`, COVID months intact.
- `outputs_step2/retail_orrule_crosstab_{cycle}.csv` — 4 per-cycle `occACT==4 × occPRE` cross-tabs (weighted episode-time), with the online-shopping leak row highlighted.
- `outputs_step2/step2_validation_report.html` + `.txt` — 0 FAIL.
- **No GSS file is written or modified.**

## Test Method

1. Locally: `py -3 -X utf8 3rdJ_02_hotelHarmonize_4split.py` from `Step2_docs/`.
2. `py -3 -X utf8 3rdJ_02_harmonizeGSS_4split_val.py` → inspect HTML: retail share ~2.1–2.3 % per cycle, leak cross-tab present and rising 2005→2022, AB splice step ≤ noise after calibration.
3. Target **0 FAIL** (see `3rdJ_02_harmonizeGSS_4split_val.md` for the gate table).

## Progress Log

*(append entries below — `### YYYY-MM-DD — <short description>`)*

### 2026-07-19 — Delta D built + run; canonical hotel series written (splice moot)

Built `3rdJ_02_hotelHarmonize_4split.py` (`load_raw_assembly` → `splice_ab_2010` → `finalize_schema` → markets side file). Ran locally, all deltas closed:

- **Delta A/B/C (verification-only)** — handled entirely by the validator (see val doc); no GSS file written or modified. ✅
- **Delta D (the one build)** — canonical `0_Occupancy/external/hotel_occupancy_monthly.csv` written (**432 rows**, schema `YEAR,MONTH,PR,occupancy_rate,ADR_CAD,RevPAR_CAD,SOURCE,SPLICED`) + validation copy in `outputs_step2/`. Full 2005–2022 grid kept (216 rows/PR); GAP months preserved as blank occupancy (Step-6 truncates, never imputes here). **Observed: QC 48 (2019+), AB 140 (2011+).**
- **AB splice = MOOT (documented fallback, Delta-D §3).** `read_cbre_ab_archive()` returned `[]` at Step 1 → AB is single-source Market Monitor (SOURCE=ABMKTMONITOR, starts 2011-01), nothing to splice onto. `splice_ab_2010()` sets `SPLICED=0` on every row and records the decision; the Step-6 SARIMA level-shift dummy `D_splice` is therefore moot. QC (ISQ) needs no splice.
- **Markets side file** (non-gated, validation context): `outputs_step2/hotel_occupancy_monthly_markets.csv` — 415 rows, Calgary/Edmonton/AlbertaResorts monthly occupancy behind the `AlbertaExclResorts` provincial driver.

Real Python: `C:/Users/o_iseri/AppData/Local/Programs/Python/Python313/python.exe`.
