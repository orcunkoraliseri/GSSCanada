# 3rdJ Step 3 Validator — Merge & Tiling (Leg-2 Two-Channel Split)

## Goal

Validate the Step-3 merged and tiled outputs for both the Residential (Leg-1
verbatim) and Office (AT_WORK) channels. Emit `outputs_step3/step3_validation_report.html`
+ `.txt` in the same dark-theme visual style as the Step-2 validator.

## Reference

- **Leg-1 validator template:** `2J_docs_occ_nTemp/03_mergingGSS_val.py` (1818 lines)
- **Step-2 Leg-2 validator style:** `Step2_docs/3rdJ_02_harmonizeGSS_2split_val.py`
- **Merged outputs to validate:** `Step3_docs/outputs_step3/`
- **Step-2 outputs (reference):** `Step2_docs/outputs_step2/`

## Validation Methods

| # | Method | Source | Notes |
|---|--------|--------|-------|
| 1 | Row Count Preservation | Leg 1 | Step-2 vs. post-filter; exclusion rate per cycle |
| 2 | Merge Key Integrity | Leg 1 | Orphan episodes, duplicate occID check |
| 3 | Derived Feature Verification | Leg 1 | DAYTYPE, HOUR_OF_DAY, DDAY_STRATA |
| 4 | HETUS 144-Slot Integrity | Leg 1 | slot_* completeness, values 1–14, home_* |
| 5 | Cross-Cycle Consistency | Leg 1 | Weighted act dist, AT_HOME rate, eps/respondent |
| 6 | Summary Statistics Table | Leg 1 | Per-cycle: resp count, excl rate, HETUS rows |
| 7 | 30-Min Downsampling | Leg 1 | Activity dist 10-min vs 30-min; AT_HOME rhythm |
| 8 | Co-Presence Validation | Leg 1 | Completeness heatmap, 9 co-presence cols |
| 9 | AT_WORK 30-min Channel | **NEW** | Shape, alignment, values, diurnal curve (headline) |
| 10 | Office Conditioning Vars | **NEW** | NOCS / NAICS / TELEWORK coverage in hetus_30min |

## Section 9 — AT_WORK Channel Checks (Leg-2 NEW)

### 9.1 — Shape
`work_30min.csv` must be (N, 49): N respondents × [occID + WORK30_001..048].

### 9.2 — occID Alignment
Row-by-row occID match between `work_30min` and `hetus_30min`. Must be exact (same
sort order as hetus_wide → carried through all tiling functions).

### 9.3 — Binary Values
All non-NaN cells in WORK30_* must be in {0, 1}. Any other value = FAIL.
NaN count reported (acceptable for respondents with no resolvable slots).

### 9.4 — Weighted AT_WORK Presence Rate per Cycle
Uses WGHT_PER from hetus_30min joined on occID.
Expected range: 1–25%. WARN if outside range.
Plausible per-cycle values: 2005≈7-12%, 2010≈6-10%, 2015≈4-9%, 2022≈3-8%
(lower than merged_episodes AT_WORK rate due to majority-vote suppression).

### 9.5 — Night-Slot Near-Zero Sanity
WORK30_001..008 (04:00–07:59) mean AT_WORK rate must be <5%. WARN if exceeded.

### 9.6 — AT_HOME vs AT_WORK Overlap
Cells where hom30_* = 1 AND WORK30_* = 1 simultaneously.
Acceptable: small WFH signal (<5% of all cells). WARN if >5%.

### 9.7 — Headline Chart: Mean Diurnal AT_WORK Presence Curve per Cycle
Line chart: 4 coloured lines (one per cycle), x-axis = 48 30-min slots (04:00 AM
origin), y-axis = mean AT_WORK rate (%).
Expected shape: near-zero 04:00–06:00, rising to daytime hump (~09:30–16:30),
lunch dip optional, declining after ~17:00, near-zero after ~20:00.
This is the headline new figure for Step 3.

## Section 10 — Office Conditioning Variables in hetus_30min (Leg-2 NEW)

For NOCS, NAICS, TELEWORK:
- Report non-NaN coverage % per cycle.
- Report distinct value count per cycle.
- TELEWORK 2005: expected all NaN → PASS with note.
- WARN if coverage = 0 on any non-2005 cycle.

## PASS / WARN / FAIL Convention

Follows Step-2 convention:
- **PASS** — clean check / within expected range.
- **WARN** — plausible but needs attention (e.g. AT_WORK rate slightly outside range,
  WFH overlap above 5%, TELEWORK 2005 all NaN, NAICS/NOCS coverage low).
- **FAIL** — concrete data integrity problem (missing output file, wrong shape,
  non-binary WORK30 values, occID mismatch between tiled outputs).

## Expected Result

- 0 FAIL on a clean merged run.
- WARNs acceptable for: night-slot near-zero check if shift workers present, AT_HOME/AT_WORK overlap if 2022 WFH captures some diary-day workers.
- HTML report: dark-theme, base64 embedded charts, scorecard header, 13 charts total.
- TXT report: same PASS/WARN/FAIL lines for cluster log review.
- Section 9a diurnal curve: characteristic daytime hump with near-zero overnight.

## Test Method

```
cd Step3_docs
py -3 -X utf8 3rdJ_03_mergingGSS_2split_val.py
```
Opens `outputs_step3/step3_validation_report.html` in browser to inspect:
- Scorecard: 0 FAIL target.
- Section 9a chart: daytime hump present, all 4 cycles visible.
- Section 10 chart: NOCS/NAICS coverage > 0 for 2005–2022; TELEWORK 2005 = 0%.

---

## Progress Log

### 2026-06-14 — Validator Built

**Deliverable:** `3rdJ_03_mergingGSS_2split_val.py` created with 10 sections
(8 ported from Leg-1 + Sections 9/10 new for Leg-2 AT_WORK office channel).

**New charts added (Leg-2):**
- Chart 9a: Mean diurnal AT_WORK presence curve per cycle (headline new figure —
  low overnight, daytime hump, 4-cycle overlay).
- Chart 9b: Weighted AT_WORK presence rate per cycle (bar chart).
- Chart 10: NOCS / NAICS / TELEWORK coverage % per cycle (3-panel bar).

**All paths resolved via platform-detection block:**
- Windows: `C:\Users\o_iseri\Desktop\GSSCanada\...\Step3_docs\outputs_step3`
- Speed cluster: `/speed-scratch/o_iseri/GSSCanada/.../Step3_docs/outputs_step3`
- Mac: `~/GSSCanada/.../Step3_docs/outputs_step3`

**Run confirmed locally (`py -3 -X utf8 3rdJ_03_mergingGSS_2split_val.py`).**

**PASS/WARN/FAIL tally: 91 PASS / 1 WARN / 0 FAIL.**

Single WARN: Section 9.5 — night-slot AT_WORK rate = 5.03% (threshold <5%). Marginal; early-morning
shift workers. Documented and accepted, not a data integrity issue.

**Section 9 (AT_WORK) results:**
- 9.1 PASS: shape (64,061, 49)
- 9.2 PASS: occID order matches hetus_30min exactly
- 9.3 PASS: all values in {0, 1}, 0 NaN cells
- 9.4 PASS: weighted AT_WORK rates — 2005: 14.96%, 2010: 13.78%, 2015: 13.96%, 2022: 12.53%
- 9.5 WARN: night-slot rate 5.03% (just above 5% threshold)
- 9.6 PASS: AT_HOME AND AT_WORK overlap = 0 cells (0.000%)
- 9.7 PASS: diurnal curve chart generated (Section 9a in HTML)

**Section 10 (office conditioning) results:**
- NOCS: coverage 65.9 / 64.8 / 60.4 / 56.8%, 10 distinct buckets each cycle
- NAICS: coverage 65.9 / 64.7 / 57.7 / 54.5%, 16–19 distinct codes per cycle
- TELEWORK: 2005 = 0% (expected NaN), 2010 = 65.0%, 2015 = 100.0%, 2022 = 41.1%
  (2015 TELEWORK 100% = diary-day instrument WTI_130; documented in Step 2)

**Reports emitted:**
- `outputs_step3/step3_validation_report.html` — dark-theme, 13 charts, base64 embedded
- `outputs_step3/step3_validation_report.txt` — PASS/WARN/FAIL tally for log review

**No blockers.**
